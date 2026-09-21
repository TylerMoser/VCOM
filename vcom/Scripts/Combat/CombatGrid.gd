## Tile queries and pathfinding over the combat map's GridMap.
##
## A tile is an empty cell a unit can stand in: solid ground below it and
## [constant UNIT_HEIGHT] empty cells of headroom. Every block is ground,
## crates included. From a tile a unit can step to any of the eight
## neighbouring tiles, climbing at most [constant MAX_CLIMB] levels and
## dropping at most [constant MAX_DROP]. Diagonal steps cost the same as
## straight ones but may not cut a corner.
class_name CombatGrid
extends Node

const UNIT_HEIGHT := 2
const MAX_CLIMB := 1
const MAX_DROP := 2

const DIRECTIONS: Array[Vector2i] = [
	Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1),
	Vector2i(1, 1), Vector2i(1, -1), Vector2i(-1, 1), Vector2i(-1, -1),
]

@export var grid_map_path: NodePath = ^"../GridMap"

var _grid: GridMap
var _lowest_y := 0


## Result of [method find_reachable]: every reachable tile, how many steps it
## takes, and the route there.
class Reach:
	## Tile -> number of steps from the start. The start itself is 0.
	var steps := {}
	## Tile -> the tile it was reached from.
	var came_from := {}

	## The tiles walked through to reach [param tile], ending with it and not
	## including the start. Empty if [param tile] is unreachable.
	func path_to(tile: Vector3i) -> Array[Vector3i]:
		var path: Array[Vector3i] = []
		while came_from.has(tile):
			path.push_front(tile)
			tile = came_from[tile]
		return path


func _ready() -> void:
	_grid = get_node_or_null(grid_map_path) as GridMap
	if _grid == null:
		push_error("CombatGrid: no GridMap at '%s'." % grid_map_path)
		return
	for cell in _grid.get_used_cells():
		_lowest_y = mini(_lowest_y, cell.y)


func is_solid(cell: Vector3i) -> bool:
	return _grid.get_cell_item(cell) != GridMap.INVALID_CELL_ITEM


func is_tile(cell: Vector3i) -> bool:
	if not is_solid(cell + Vector3i.DOWN):
		return false
	for height in UNIT_HEIGHT:
		if is_solid(cell + Vector3i.UP * height):
			return false
	return true


## World position of the floor at the centre of [param tile].
func tile_position(tile: Vector3i) -> Vector3:
	var floor_center := _grid.map_to_local(tile) - Vector3(0.0, _grid.cell_size.y * 0.5, 0.0)
	return _grid.to_global(floor_center)


## The tile whose floor is at, or just below, [param world_position].
func tile_at(world_position: Vector3) -> Vector3i:
	var lifted := _grid.to_local(world_position) + Vector3(0.0, _grid.cell_size.y * 0.5, 0.0)
	return _grid.local_to_map(lifted)


## Tiles one step away from [param tile].
func neighbours(tile: Vector3i) -> Array[Vector3i]:
	var result: Array[Vector3i] = []
	for direction in DIRECTIONS:
		var next: Variant = _step(tile, direction)
		if next == null:
			continue
		# A diagonal needs both of the straight steps beside it to be open,
		# so units cannot squeeze between two blocks that touch at a corner.
		if direction.x != 0 and direction.y != 0:
			if _step(tile, Vector2i(direction.x, 0)) == null or _step(tile, Vector2i(0, direction.y)) == null:
				continue
		result.append(next)
	return result


## Breadth-first search from [param start], up to [param max_steps] steps.
## Tiles in [param blocked] (a set of Vector3i keys) cannot be entered.
func find_reachable(start: Vector3i, max_steps: int, blocked: Dictionary = {}) -> Reach:
	var reach := Reach.new()
	reach.steps[start] = 0
	var frontier: Array[Vector3i] = [start]
	while not frontier.is_empty():
		var tile: Vector3i = frontier.pop_front()
		var steps: int = reach.steps[tile]
		if steps >= max_steps:
			continue
		for next in neighbours(tile):
			if reach.steps.has(next) or blocked.has(next):
				continue
			reach.steps[next] = steps + 1
			reach.came_from[next] = tile
			frontier.append(next)
	return reach


## The tile whose floor a ray first lands on, or null if the ray hits the side
## of a block or nothing at all. The ray is traced cell by cell through the
## grid, because the blocks have no collision shapes.
func pick_tile(origin: Vector3, direction: Vector3, max_distance := 500.0) -> Variant:
	# Work in cell units, where cell c spans [c, c + 1) on each axis.
	var from := _grid.to_local(origin) / _grid.cell_size
	var dir := (_grid.global_basis.inverse() * direction) / _grid.cell_size
	if dir.is_zero_approx():
		return null
	dir = dir.normalized()

	var cell := Vector3i(from.floor())
	var step := Vector3i(int(signf(dir.x)), int(signf(dir.y)), int(signf(dir.z)))
	var t_max := Vector3.ZERO
	var t_delta := Vector3.ZERO
	for axis in 3:
		if is_zero_approx(dir[axis]):
			t_max[axis] = INF
			t_delta[axis] = INF
		else:
			var boundary := cell[axis] + (1 if step[axis] > 0 else 0)
			t_max[axis] = (boundary - from[axis]) / dir[axis]
			t_delta[axis] = absf(1.0 / dir[axis])

	var entered_axis := -1
	var t := 0.0
	while t <= max_distance:
		if is_solid(cell):
			# Only a hit on the top face counts as clicking the floor above.
			if entered_axis == Vector3.AXIS_Y and step.y < 0 and is_tile(cell + Vector3i.UP):
				return cell + Vector3i.UP
			return null
		if cell.y < _lowest_y and step.y <= 0:
			return null
		entered_axis = t_max.min_axis_index()
		t = t_max[entered_axis]
		cell[entered_axis] += step[entered_axis]
		t_max[entered_axis] += t_delta[entered_axis]
	return null


## The tile reached by stepping from [param from] toward [param direction],
## or null if the climb, drop or headroom rules forbid it.
func _step(from: Vector3i, direction: Vector2i) -> Variant:
	for rise in range(MAX_CLIMB, -MAX_DROP - 1, -1):
		var to := from + Vector3i(direction.x, rise, direction.y)
		if is_tile(to) and _is_clear(from, to):
			return to
	return null


## Whether both columns are open for the whole climb or drop between
## [param from] and [param to], including headroom at the higher end.
func _is_clear(from: Vector3i, to: Vector3i) -> bool:
	var top := maxi(from.y, to.y) + UNIT_HEIGHT - 1
	for y in range(from.y, top + 1):
		if is_solid(Vector3i(from.x, y, from.z)):
			return false
	for y in range(to.y, top + 1):
		if is_solid(Vector3i(to.x, y, to.z)):
			return false
	return true
