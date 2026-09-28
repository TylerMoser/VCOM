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

## Emitted when a round strikes a solid cell, with the environmental damage
## behind it. What a strike does to the cell is up to the terrain: the grid
## only reports it.
signal terrain_struck(hit: RayHit, damage: int)

const UNIT_HEIGHT := 2
const MAX_CLIMB := 1
const MAX_DROP := 2
## How close two cell boundaries must be for [method is_line_clear] to treat
## a sight line as crossing both at once, rather than one and then the other.
const BOUNDARY_EPSILON := 1e-6

const DIRECTIONS: Array[Vector2i] = [
	Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1),
	Vector2i(1, 1), Vector2i(1, -1), Vector2i(-1, 1), Vector2i(-1, -1),
]

@export var grid_map_path: NodePath = ^"../GridMap"

var _grid: GridMap
## The box, in cells, that every solid cell on the map lies within. Worked
## out once: cells only ever go from the map, so it never needs to grow.
var _bounds_min := Vector3i.ZERO
var _bounds_max := Vector3i.ZERO


## Where a ray cast by [method cast] first runs into a solid cell.
class RayHit:
	## The solid cell the ray ran into.
	var cell: Vector3i
	## Where the ray met the cell, on the face it came in through.
	var point: Vector3
	## The face of [member cell] the ray came in through, as the way that face
	## looks out: [code]Vector3i.UP[/code] for the top. Zero if the ray started
	## inside the cell.
	var face: Vector3i
	## Which way the ray was travelling, normalised.
	var direction: Vector3
	## How far the ray travelled to get there.
	var distance: float


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
	var cells := _grid.get_used_cells()
	if cells.is_empty():
		return
	_bounds_min = cells[0]
	_bounds_max = cells[0]
	for cell in cells:
		_bounds_min = _bounds_min.min(cell)
		_bounds_max = _bounds_max.max(cell)


func is_solid(cell: Vector3i) -> bool:
	return _grid.get_cell_item(cell) != GridMap.INVALID_CELL_ITEM


func is_tile(cell: Vector3i) -> bool:
	if not is_solid(cell + Vector3i.DOWN):
		return false
	for height in UNIT_HEIGHT:
		if is_solid(cell + Vector3i.UP * height):
			return false
	return true


## Every tile on the map.
func tiles() -> Array[Vector3i]:
	var result: Array[Vector3i] = []
	for cell in _grid.get_used_cells():
		var above := cell + Vector3i.UP
		if is_tile(above):
			result.append(above)
	return result


## World position of the centre of [param cell].
func cell_center(cell: Vector3i) -> Vector3:
	return _grid.to_global(_grid.map_to_local(cell))


## World position of the floor at the centre of [param tile].
func tile_position(tile: Vector3i) -> Vector3:
	var floor_center := _grid.map_to_local(tile) - Vector3(0.0, _grid.cell_size.y * 0.5, 0.0)
	return _grid.to_global(floor_center)


## The tile whose floor is at, or just below, [param world_position].
func tile_at(world_position: Vector3) -> Vector3i:
	var lifted := _grid.to_local(world_position) + Vector3(0.0, _grid.cell_size.y * 0.5, 0.0)
	return _grid.local_to_map(lifted)


## Tiles standing units occupy, except [param except]'s own, as a set.
func occupied_tiles(except: Unit = null) -> Dictionary:
	var tiles := {}
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		if node != except:
			tiles[tile_at((node as Unit).global_position)] = true
	return tiles


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


## Whether nothing solid stands between the centres of cells [param from] and
## [param to]. Neither end is tested, so the cells a unit fills never block
## its own sight line.
##
## Where the line crosses two cell boundaries at once - what a shot straight
## down a diagonal does - it cuts the corner instead of clipping the cells to
## either side. Sight lines are therefore permissive where [method neighbours]
## is strict: a unit can see through a diagonal gap it cannot walk through.
func is_line_clear(from: Vector3i, to: Vector3i) -> bool:
	var direction := Vector3(to - from)
	var cell := from
	var step := Vector3i.ZERO
	# Distance along the line, as a fraction of its length, to the next cell
	# boundary on each axis and to every one after that. Both ends sit at a
	# cell centre, so the first boundary is half a cell away.
	var next_cross := Vector3(INF, INF, INF)
	var cross_spacing := Vector3(INF, INF, INF)
	for axis in 3:
		if is_zero_approx(direction[axis]):
			continue
		step[axis] = int(signf(direction[axis]))
		next_cross[axis] = 0.5 / absf(direction[axis])
		cross_spacing[axis] = 1.0 / absf(direction[axis])

	while cell != to:
		var crossing: float = next_cross[next_cross.min_axis_index()]
		if crossing > 1.0:
			break
		for axis in 3:
			if next_cross[axis] <= crossing + BOUNDARY_EPSILON:
				cell[axis] += step[axis]
				next_cross[axis] += cross_spacing[axis]
		if cell != to and is_solid(cell):
			return false
	return true


## The tile whose floor a ray first lands on, or null if the ray hits the side
## of a block or nothing at all.
func pick_tile(origin: Vector3, direction: Vector3, max_distance := 500.0) -> Variant:
	var hit: Variant = cast(origin, direction, max_distance)
	if hit == null:
		return null
	var landed := hit as RayHit
	# Only a hit on the top face counts as clicking the floor above.
	if landed.face == Vector3i.UP and is_tile(landed.cell + Vector3i.UP):
		return landed.cell + Vector3i.UP
	return null


## The first solid cell a ray from [param origin] along [param direction]
## runs into, as a [RayHit], or null if it leaves the map or goes
## [param max_distance] cells without meeting one.
##
## The ray is traced cell by cell through the grid, because the blocks have no
## collision shapes. It enters every cell it touches, so unlike
## [method is_line_clear] it never slips between two blocks that meet at a
## corner.
func cast(origin: Vector3, direction: Vector3, max_distance := 500.0) -> Variant:
	# Work in cell units, where cell c spans [c, c + 1) on each axis.
	var from := _grid.to_local(origin) / _grid.cell_size
	var dir := (_grid.global_basis.inverse() * direction) / _grid.cell_size
	if dir.is_zero_approx():
		return null
	dir = dir.normalized()

	var cell := Vector3i(from.floor())
	var step := Vector3i.ZERO
	var t_max := Vector3(INF, INF, INF)
	var t_delta := Vector3(INF, INF, INF)
	for axis in 3:
		if is_zero_approx(dir[axis]):
			continue
		step[axis] = int(signf(dir[axis]))
		var boundary := cell[axis] + (1 if step[axis] > 0 else 0)
		t_max[axis] = (boundary - from[axis]) / dir[axis]
		t_delta[axis] = absf(1.0 / dir[axis])

	var entered_axis := -1
	var t := 0.0
	while t <= max_distance:
		if is_solid(cell):
			var face := Vector3i.ZERO
			if entered_axis >= 0:
				face[entered_axis] = -step[entered_axis]
			var hit := RayHit.new()
			hit.cell = cell
			hit.face = face
			hit.point = _grid.to_global((from + dir * t) * _grid.cell_size)
			hit.direction = direction.normalized()
			hit.distance = origin.distance_to(hit.point)
			return hit
		if _is_leaving_map(cell, step):
			return null
		entered_axis = t_max.min_axis_index()
		t = t_max[entered_axis]
		cell[entered_axis] += step[entered_axis]
		t_max[entered_axis] += t_delta[entered_axis]
	return null


## The box every cell on the map lies within, in world space.
func map_bounds() -> AABB:
	var cells := AABB(Vector3(_bounds_min), Vector3(_bounds_max - _bounds_min + Vector3i.ONE))
	var local := AABB(cells.position * _grid.cell_size, cells.size * _grid.cell_size)
	return _grid.global_transform * local


## Reports a round striking the solid cell [param hit] ran into, with
## [param damage] environmental damage behind it, as [signal terrain_struck].
func strike(hit: RayHit, damage: int) -> void:
	terrain_struck.emit(hit, damage)


## The tile reached by stepping from [param from] toward [param direction],
## or null if the climb, drop or headroom rules forbid it.
func _step(from: Vector3i, direction: Vector2i) -> Variant:
	for rise in range(MAX_CLIMB, -MAX_DROP - 1, -1):
		var to := from + Vector3i(direction.x, rise, direction.y)
		if is_tile(to) and _is_clear(from, to):
			return to
	return null


## Whether a ray stepping [param step] through the grid from [param cell] is
## outside the map and heading away from it, and so can never meet a block.
func _is_leaving_map(cell: Vector3i, step: Vector3i) -> bool:
	for axis in 3:
		if cell[axis] < _bounds_min[axis] and step[axis] <= 0:
			return true
		if cell[axis] > _bounds_max[axis] and step[axis] >= 0:
			return true
	return false


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
