## Tile queries and pathfinding over the combat map's level ([VoxelLevel]).
##
## A tile is an empty cell a unit can stand in: solid ground below it and
## [constant UNIT_HEIGHT] empty cells of headroom. Every solid piece in the
## middle of a cell is ground, crates included. From a tile a unit can step to
## any of the eight neighbouring tiles, climbing at most [constant MAX_CLIMB]
## levels and dropping at most [constant MAX_DROP]. Diagonal steps cost the
## same as straight ones but may not cut a corner.
##
## A piece can also stand on the edge between two cells side by side: a fence
## or a wall ([LevelRules]). To the rules it stands across that edge, at its
## own level, until it breaks, and so it is cover to both sides of it
## ([LineOfSight]), it blocks a sight line crossing the edge at its level, and
## it stops a round or a throw there. A unit steps over one a level high or
## less, as it climbs a level, and never over one taller, nor diagonally past
## any.
##
## Paths go over a walking graph, the steps from every tile, worked out once as
## the map loads and kept, rather than at every search. The steps from a tile
## read nothing but the rules close round it, so as a piece leaves the rules
## only the steps round it are worked out again ([method _on_piece_removed]).
class_name CombatGrid
extends Node

## Emitted when a round strikes a solid cell, with the environmental damage
## behind it. What a strike does to the cell is up to the terrain: the grid
## only reports it.
signal terrain_struck(hit: RayHit, damage: int)
## Emitted when a blast goes off at [param origin], with every cell it
## reaches, solid or not, the environmental damage behind it, and how hard it
## throws debris about, as a [Blast] force. As with a strike, what it does to
## the cells is up to the terrain.
signal terrain_blasted(origin: Vector3, cells: Array[Vector3i], damage: int, force: float)
## Emitted as every round lands, hit or miss, with the line it flew along and
## the environmental damage behind it, for what lies along that line that a
## round tears through and flies on past: never terrain, which only
## [signal terrain_struck] reports, but loose voxel models ([VoxelBody]).
signal round_flown(from: Vector3, to: Vector3, damage: int)

const UNIT_HEIGHT := 2
const MAX_CLIMB := 1
const MAX_DROP := 2
## How many levels below a tile's own, and above it, the rules its steps are
## worked out from reach ([method _walkable_from]): down to the ground under
## the lowest tile it can drop to, up to the head of a unit that has climbed as
## high as it can. A change further from a tile than that leaves its steps as
## they were.
const STEP_READS_BELOW := MAX_DROP + 1
const STEP_READS_ABOVE := MAX_CLIMB + UNIT_HEIGHT - 1
## How close two cell boundaries must be for [method is_line_clear] to treat
## a sight line as crossing both at once, rather than one and then the other.
const BOUNDARY_EPSILON := 1e-6
## No voxel: a ray that met a whole cell or a whole edge.
const NO_VOXEL := Vector3i(-2147483648, -2147483648, -2147483648)

const DIRECTIONS: Array[Vector2i] = [
	Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1),
	Vector2i(1, 1), Vector2i(1, -1), Vector2i(-1, 1), Vector2i(-1, -1),
]

@export var level_path: NodePath = ^"../Level"

## The voxels of everything that wears away, kept by the map's
## [TerrainDestruction], which gives it as it is ready.
var voxels: VoxelTerrain
## The level the grid reads.
var level: VoxelLevel

var _rules: LevelRules
var _volume: VoxelVolume
## Whether each of the level's kinds wears away, by its place in the level's
## kinds: what a round is traced through voxel by voxel.
var _wears := PackedByteArray()
## Whether any edge has a piece across it: none, and sight and paths skip
## looking.
var _has_edges := false
## The box, in cells, that every solid cell on the map lies within. Worked
## out once: cells only ever go from the map, so it never needs to grow.
var _bounds_min := Vector3i.ZERO
var _bounds_max := Vector3i.ZERO
## The walking graph: each tile -> the tiles one step from it, in
## [constant DIRECTIONS]' order ([method _walkable_from]). Worked out for every
## tile as the map loads, and kept: only what a piece leaving the rules could
## change is ever worked out again.
var _graph := {}
## The cells round the pieces gone from the rules since, as a set, whose steps
## are to be worked out again: at the end of the frame they went in, or first
## thing in the next search, whichever comes first ([method _catch_up]).
var _stale := {}


## Where a ray cast by [method cast] first runs into something solid.
class RayHit:
	## The cell it ran into, or, meeting a piece across an edge, the cell it
	## was about to enter; for a voxel, the cell the voxel is in.
	var cell: Vector3i
	## Where the ray met it, on the face it came in through: for a ray traced
	## voxel by voxel, where it met the voxel.
	var point: Vector3
	## The face it came in through, as the way that face looks out:
	## [code]Vector3i.UP[/code] for the top. For a voxel, the voxel's face.
	## Zero if the ray started inside.
	var face: Vector3i
	## Which way the ray was travelling, normalised.
	var direction: Vector3
	## How far the ray travelled to get there.
	var distance: float
	## For a ray traced voxel by voxel, the voxel it met, in the level
	## ([VoxelVolume]); [constant NO_VOXEL] for a whole cell or edge.
	var voxel := NO_VOXEL
	## The piece it met, by its index in the level's [LevelData]: the voxel's,
	## or the one standing on top in the cell, or across the edge. -1 if none.
	var piece := -1
	## Whether it met a piece across an edge, as a whole: the edge's slot
	## ([LevelData]) if so, else the cell's.
	var on_edge := false

	## Whether it met a voxel rather than a whole cell or edge.
	func has_voxel() -> bool:
		return voxel != NO_VOXEL


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
	level = get_node_or_null(level_path) as VoxelLevel
	if level == null:
		push_error("CombatGrid: no VoxelLevel at '%s'." % level_path)
		return
	if level.rules == null:
		push_error("CombatGrid: the level at '%s' is scenery, or has no pieces." % level_path)
		return
	# Readied again (a probe taking up rules made afresh), it lets go of the
	# rules it read before.
	if _rules != null and _rules.removed.is_connected(_on_piece_removed):
		_rules.removed.disconnect(_on_piece_removed)
	_rules = level.rules
	_volume = level.volume
	_bounds_min = _rules.bounds_min
	_bounds_max = _rules.bounds_max
	_has_edges = not _rules.edge_slots().is_empty()
	_wears.resize(level.data.kinds.size())
	for kind in level.data.kinds.size():
		var piece_kind := level.library.find(StringName(level.data.kinds[kind]))
		_wears[kind] = 1 if piece_kind != null and piece_kind.destruction is VoxelDestruction else 0
	_build_graph()
	_rules.removed.connect(_on_piece_removed)


func is_solid(cell: Vector3i) -> bool:
	return _rules.is_solid(cell)


## Whether a piece stands across the edge of [param cell] toward
## [param direction], at the cell's own level.
func has_edge(cell: Vector3i, direction: Vector2i) -> bool:
	return _has_edges and _rules.has_edge(cell, direction)


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
	for cell in _rules.solid_cells():
		var above := cell + Vector3i.UP
		if is_tile(above):
			result.append(above)
	return result


## World position of the centre of [param cell].
func cell_center(cell: Vector3i) -> Vector3:
	return level.to_global(Vector3(cell) + Vector3.ONE * 0.5)


## World position of the floor at the centre of [param tile].
func tile_position(tile: Vector3i) -> Vector3:
	return level.to_global(Vector3(tile.x + 0.5, tile.y, tile.z + 0.5))


## The tile whose floor is at, or just below, [param world_position].
func tile_at(world_position: Vector3) -> Vector3i:
	var lifted := level.to_local(world_position) + Vector3(0.0, 0.5, 0.0)
	return Vector3i(lifted.floor())


## The first tile at or below [param cell], straight down: where anything
## falling from there comes to rest. Null if there is no ground below it.
func tile_under(cell: Vector3i) -> Variant:
	for y in range(cell.y, _bounds_min.y, -1):
		var below := Vector3i(cell.x, y, cell.z)
		if is_tile(below):
			return below
	return null


## Tiles standing units occupy, except [param except]'s own, as a set.
func occupied_tiles(except: Unit = null) -> Dictionary:
	var tiles := {}
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		if node != except:
			tiles[tile_at((node as Unit).global_position)] = true
	return tiles


## Tiles one step away from [param tile], from the walking graph. A copy, to
## do with as the caller likes.
func neighbours(tile: Vector3i) -> Array[Vector3i]:
	_catch_up()
	return _links(tile).duplicate()


## Breadth-first search from [param start], up to [param max_steps] steps,
## over the walking graph. Tiles in [param blocked] (a set of Vector3i keys)
## cannot be entered.
func find_reachable(start: Vector3i, max_steps: int, blocked: Dictionary = {}) -> Reach:
	_catch_up()
	var reach := Reach.new()
	reach.steps[start] = 0
	var frontier: Array[Vector3i] = [start]
	while not frontier.is_empty():
		var tile: Vector3i = frontier.pop_front()
		var steps: int = reach.steps[tile]
		if steps >= max_steps:
			continue
		for next in _links(tile):
			if reach.steps.has(next) or blocked.has(next):
				continue
			reach.steps[next] = steps + 1
			reach.came_from[next] = tile
			frontier.append(next)
	return reach


## How high a unit stepping from [param from] to [param to], straight across
## the ground, has to step over the pieces standing across the edge between
## them: none (0), or a level for a piece a level high, which it climbs over.
## For the figure's hop over it ([method Unit.walk]).
func vault_height(from: Vector3i, to: Vector3i) -> int:
	var direction := Vector2i(to.x - from.x, to.z - from.z)
	if not _has_edges or absi(direction.x) + absi(direction.y) != 1:
		return 0
	return 1 if has_edge(Vector3i(from.x, maxi(from.y, to.y), from.z), direction) else 0


## How high each step of a walk from [param start] along [param path] steps
## over a piece across the edge on the way ([method vault_height]), a step at
## a time: for the figure to hop over a fence ([method Unit.walk]).
func vaults_along(start: Vector3i, path: Array[Vector3i]) -> PackedFloat32Array:
	var vaults := PackedFloat32Array()
	var at := start
	for tile in path:
		vaults.append(vault_height(at, tile))
		at = tile
	return vaults


## Whether nothing solid stands between the centres of cells [param from] and
## [param to]. Neither end is tested, so the cells a unit fills never block
## its own sight line.
##
## Where the line crosses two cell boundaries at once - what a shot straight
## down a diagonal does - it cuts the corner instead of clipping the cells to
## either side. Sight lines are therefore permissive where [method neighbours]
## is strict: a unit can see through a diagonal gap it cannot walk through. A
## piece across an edge blocks a line crossing that edge at its level; one
## crossing at a corner, where it could go either side of the pieces there, is
## blocked only if it would be whichever way round it went, so it slips past
## the end of a wall but not through the joint between two lengths of one.
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
		var before := cell
		var crossed := PackedInt32Array()
		for axis in 3:
			if next_cross[axis] <= crossing + BOUNDARY_EPSILON:
				cell[axis] += step[axis]
				next_cross[axis] += cross_spacing[axis]
				crossed.append(axis)
		if _has_edges and _edges_block(before, crossed, step):
			return false
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
	if not landed.on_edge and landed.face == Vector3i.UP and is_tile(landed.cell + Vector3i.UP):
		return landed.cell + Vector3i.UP
	return null


## The first solid thing a ray from [param origin] along [param direction]
## runs into, as a [RayHit], or null if it leaves the map or goes
## [param max_distance] cells without meeting one: a cell with a solid piece in
## it, or a piece standing across an edge it crosses, at the edge.
##
## The ray is traced cell by cell through the grid. It enters every cell it
## touches, so unlike [method is_line_clear] it never slips between two blocks
## that meet at a corner.
##
## With [param by_voxel], pieces that wear away are traced voxel by voxel
## through the level's voxels ([VoxelVolume]), and only stop the ray where it
## meets one of their voxels: one that crosses a cell beside them, or through a
## hole, goes on, and one passing a fence goes between its rails. Only a
## round's flight is traced so ([Ballistics]). To sight, cover and a throw's arc
## a piece is its whole cell, or its whole edge, however worn. With
## [param every_block] as well, every piece is traced so, a crate's slats and
## gaps included, and pieces that are only decoration too: only for blood
## ([Blood]), which stains the voxel it meets and touches no rule.
func cast(origin: Vector3, direction: Vector3, max_distance := 500.0, by_voxel := false, every_block := false) -> Variant:
	if level == null:
		return null
	# Work in cell units, where cell c spans [c, c + 1) on each axis: the
	# level's own space, a cell a unit across.
	var from := level.to_local(origin)
	var dir := level.global_basis.inverse() * direction
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
		# Crossing an edge with a piece standing across it.
		if _has_edges and entered_axis >= 0 and entered_axis != 1:
			var came := Vector2i.ZERO
			came[0 if entered_axis == 0 else 1] = step[entered_axis]
			var behind := cell
			behind[entered_axis] -= step[entered_axis]
			var across := _rules.pieces_across(LevelData.edge_slot(behind, came))
			if not across.is_empty() and not (by_voxel and (every_block or _all_wear(across))):
				var face := Vector3i.ZERO
				face[entered_axis] = -step[entered_axis]
				return _whole_hit(cell, face, across[across.size() - 1], from + dir * t, direction, origin, true)
		if is_solid(cell):
			var standing := _rules.pieces_in(cell)
			var traced := by_voxel and (every_block or _all_wear(standing))
			if not traced:
				var face := Vector3i.ZERO
				if entered_axis >= 0:
					face[entered_axis] = -step[entered_axis]
				return _whole_hit(cell, face, standing[standing.size() - 1], from + dir * t, direction, origin, false)
		if by_voxel and _volume.cell_has_voxels(cell):
			var leave := minf(t_max.x, minf(t_max.y, t_max.z))
			var met: Variant = _trace_cell(cell, from, dir, t, leave, max_distance, every_block, origin, direction)
			if met != null:
				return met
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
	return level.global_transform * cells


## Reports a round striking the solid cell [param hit] ran into, with
## [param damage] environmental damage behind it, as [signal terrain_struck].
func strike(hit: RayHit, damage: int) -> void:
	terrain_struck.emit(hit, damage)


## Reports a blast going off at [param origin] and reaching [param cells],
## with [param damage] environmental damage behind it and [param force] to
## throw debris about with, as [signal terrain_blasted].
func blast(origin: Vector3, cells: Array[Vector3i], damage: int, force: float) -> void:
	terrain_blasted.emit(origin, cells, damage, force)


## Reports a round flying from [param from] to [param to] with [param damage]
## environmental damage behind it, as [signal round_flown].
func fly(from: Vector3, to: Vector3, damage: int) -> void:
	round_flown.emit(from, to, damage)


## Whether every piece in [param pieces] wears away.
func _all_wear(pieces: PackedInt32Array) -> bool:
	for piece in pieces:
		if _wears[level.data.kind_at(piece)] == 0:
			return false
	return true


## A hit on a whole cell or edge: [param cell], entered through [param face],
## met at [param local] in the level's space, struck on [param piece].
func _whole_hit(cell: Vector3i, face: Vector3i, piece: int, local: Vector3, direction: Vector3, origin: Vector3, on_edge: bool) -> RayHit:
	var hit := RayHit.new()
	hit.cell = cell
	hit.face = face
	hit.piece = piece
	hit.on_edge = on_edge
	hit.point = level.to_global(local)
	hit.direction = direction.normalized()
	hit.distance = origin.distance_to(hit.point)
	return hit


## Where the ray from [param from], in the level's space, along [param dir]
## first meets a voxel in [param cell], between [param enter] and
## [param leave] along it, as a [RayHit]; null if it meets none, or one further
## than [param max_distance]. The voxels of a piece that does not wear away,
## and of one that is only decoration, are passed by, unless
## [param every_block]: the first is met whole, at its cell or edge, and the
## second stops nothing.
func _trace_cell(
	cell: Vector3i, from: Vector3, dir: Vector3, enter: float, leave: float, max_distance: float,
	every_block: bool, origin: Vector3, direction: Vector3
) -> Variant:
	var size := float(VoxelVolume.BLOCK)
	# In voxels from here on.
	var start := (from + dir * enter) * size
	var voxel := Vector3i((start + dir * 1e-4).floor())
	var least := cell * VoxelVolume.BLOCK
	voxel = voxel.clamp(least, least + Vector3i.ONE * (VoxelVolume.BLOCK - 1))
	var step := Vector3i.ZERO
	var next_cross := Vector3(INF, INF, INF)
	var cross_spacing := Vector3(INF, INF, INF)
	var t := enter * size
	var end := leave * size
	for axis in 3:
		if is_zero_approx(dir[axis]):
			continue
		step[axis] = int(signf(dir[axis]))
		var boundary := voxel[axis] + (1 if step[axis] > 0 else 0)
		next_cross[axis] = (boundary - from[axis] * size) / dir[axis]
		cross_spacing[axis] = absf(1.0 / dir[axis])
	var entered_on := -1
	# The face the ray came into the cell by, if it did not start inside it.
	if enter > 0.0:
		var nearest := INF
		for axis in 3:
			if step[axis] == 0:
				continue
			var boundary := cell[axis] + (0 if step[axis] > 0 else 1)
			var gap := absf(from[axis] + dir[axis] * enter - boundary)
			if gap < nearest:
				nearest = gap
				entered_on = axis
	while true:
		if _volume.is_solid(voxel):
			var piece := _volume.owner_at(voxel)
			if every_block or _stops_rounds(piece):
				var hit := RayHit.new()
				hit.cell = cell
				hit.voxel = voxel
				hit.piece = piece
				hit.point = level.to_global(from + dir * (t / size))
				hit.direction = direction.normalized()
				hit.distance = origin.distance_to(hit.point)
				if entered_on >= 0:
					hit.face[entered_on] = -step[entered_on]
				if hit.distance > max_distance:
					return null
				return hit
		var axis := next_cross.min_axis_index()
		t = next_cross[axis]
		if t > end + 1e-4:
			return null
		voxel[axis] += step[axis]
		if voxel[axis] < least[axis] or voxel[axis] >= least[axis] + VoxelVolume.BLOCK:
			return null
		next_cross[axis] += cross_spacing[axis]
		entered_on = axis
	return null


## Whether a round stops on a voxel of [param piece]: a solid one that wears
## away. The voxels of one that does not are met whole, at its cell or edge.
func _stops_rounds(piece: int) -> bool:
	if piece < 0:
		return false
	var kind := level.data.kind_at(piece)
	if _wears[kind] == 0:
		return false
	return _rules.is_standing(piece)


## Works out the steps from every tile on the map afresh: the walking graph, as
## the map loads.
func _build_graph() -> void:
	_graph.clear()
	_stale.clear()
	for tile in tiles():
		_graph[tile] = _walkable_from(tile)


## The steps from [param tile], from the walking graph: as they were last
## worked out, or, for a cell it has none for (one that is no tile, such as
## one a falling unit is in), worked out now and kept. The graph's own array,
## never to be changed.
func _links(tile: Vector3i) -> Array[Vector3i]:
	var links: Variant = _graph.get(tile)
	if links == null:
		links = _walkable_from(tile)
		_graph[tile] = links
	return links


## The tiles one step away from [param tile], worked out from the rules as they
## stand: what the walking graph keeps for it. A diagonal needs both of the
## straight steps beside it to be open, so units cannot squeeze between two
## blocks that touch at a corner, and nothing across any edge round the corner
## it passes.
##
## The graph is kept by what this reads: the cells of the nine columns round
## [param tile], its own and the eight beside it, from
## [constant STEP_READS_BELOW] levels below its own to
## [constant STEP_READS_ABOVE] above, and the edges between those columns from
## its own level to [constant STEP_READS_ABOVE] above. Make it read further and
## [method _on_piece_removed] has to forget further round a change.
func _walkable_from(tile: Vector3i) -> Array[Vector3i]:
	# Each step is worked out once, for a diagonal looks again at the straight
	# steps beside it.
	var steps := {}
	for direction in DIRECTIONS:
		steps[direction] = _step(tile, direction)
	var result: Array[Vector3i] = []
	for direction in DIRECTIONS:
		var next: Variant = steps[direction]
		if next == null:
			continue
		if direction.x != 0 and direction.y != 0:
			if steps[Vector2i(direction.x, 0)] == null or steps[Vector2i(0, direction.y)] == null:
				continue
			if _has_edges and _corner_blocked(tile, next, direction):
				continue
		result.append(next)
	return result


## Forgets the steps from every cell whose steps read [param slot], which a
## piece has just left ([signal LevelRules.removed]), to be worked out again
## ([method _catch_up]). While another piece still stands there, nothing has
## changed for them.
func _on_piece_removed(_piece: int, slot: Vector3i) -> void:
	var cell := LevelData.cell_of(slot)
	if LevelData.is_centre(slot):
		if not _rules.is_solid(cell):
			_forget(cell, cell, cell.y - STEP_READS_ABOVE, cell.y + STEP_READS_BELOW)
	elif not _rules.has_edge_slot(slot):
		# An edge is read from the columns round both of its sides, by the tiles
		# at its own level and up to STEP_READS_ABOVE below it.
		_forget(cell, LevelData.other_cell(slot), slot.y - STEP_READS_ABOVE, slot.y)


## Takes the steps from every cell of the columns within one of [param a] or
## [param b], from level [param low] to [param high], out of the walking graph,
## and marks them to be worked out again.
func _forget(a: Vector3i, b: Vector3i, low: int, high: int) -> void:
	if _stale.is_empty():
		_catch_up.call_deferred()
	for x in range(mini(a.x, b.x) - 1, maxi(a.x, b.x) + 2):
		for z in range(mini(a.z, b.z) - 1, maxi(a.z, b.z) + 2):
			for y in range(low, high + 1):
				var cell := Vector3i(x, y, z)
				_graph.erase(cell)
				_stale[cell] = true


## Works the steps out again from every tile among the cells forgotten since it
## last ran: at the end of the frame the pieces went in, or as the next search
## begins, so no search reads steps a change has made wrong.
func _catch_up() -> void:
	if _stale.is_empty():
		return
	for cell: Vector3i in _stale:
		if is_tile(cell):
			_graph[cell] = _walkable_from(cell)
	_stale.clear()


## The tile reached by stepping from [param from] toward [param direction],
## or null if the climb, drop, headroom or edge rules forbid it.
func _step(from: Vector3i, direction: Vector2i) -> Variant:
	for rise in range(MAX_CLIMB, -MAX_DROP - 1, -1):
		var to := from + Vector3i(direction.x, rise, direction.y)
		if not is_tile(to):
			continue
		var top: Variant = _crossing_top(from, to, direction)
		if top != null and _is_clear(from, to, top):
			return to
	return null


## The level a unit stepping from [param from] to [param to] crosses the edge
## between their columns at, its feet there: the higher of the two tiles, a
## level higher still to step over a piece a level high standing across the
## edge there, which only one stepping no higher than [constant MAX_CLIMB]
## above where it stands can. Null if the edge is blocked: a piece standing
## anywhere across it from there up to the top of the unit. A diagonal crosses
## no single edge ([method _corner_blocked]).
func _crossing_top(from: Vector3i, to: Vector3i, direction: Vector2i) -> Variant:
	var top := maxi(from.y, to.y)
	if not _has_edges or (direction.x != 0 and direction.y != 0):
		return top
	var column := Vector3i(from.x, 0, from.z)
	if _rules.has_edge(column + Vector3i.UP * top, direction):
		top += 1
		if top - from.y > MAX_CLIMB:
			return null
	for y in range(top, top + UNIT_HEIGHT):
		if _rules.has_edge(column + Vector3i.UP * y, direction):
			return null
	return top


## Whether a diagonal step from [param from] to [param to] toward
## [param direction] would pass a piece standing across any of the four edges
## round the corner it passes through, at any level the unit fills crossing
## it: it never steps over one diagonally.
func _corner_blocked(from: Vector3i, to: Vector3i, direction: Vector2i) -> bool:
	var top := maxi(from.y, to.y)
	var along_x := Vector2i(direction.x, 0)
	var along_z := Vector2i(0, direction.y)
	for y in range(top, top + UNIT_HEIGHT):
		var here := Vector3i(from.x, y, from.z)
		if (
			_rules.has_edge(here, along_x) or _rules.has_edge(here, along_z)
			or _rules.has_edge(here + Vector3i(direction.x, 0, 0), along_z)
			or _rules.has_edge(here + Vector3i(0, 0, direction.y), along_x)
		):
			return true
	return false


## Whether pieces across edges block a sight line crossing the boundaries
## [param crossed] (axes, at once) out of [param before], each toward
## [param step]. Crossing several at once, it could have gone either side of
## the corner or edge it passed exactly through, so it is blocked only if it
## would be whichever order it crossed them in.
func _edges_block(before: Vector3i, crossed: PackedInt32Array, step: Vector3i) -> bool:
	if not (0 in crossed or 2 in crossed):
		return false
	for order in _orders(crossed):
		var cell := before
		var blocked := false
		for axis in order:
			if axis != 1:
				var way := Vector2i(step.x if axis == 0 else 0, step.z if axis == 2 else 0)
				if _rules.has_edge(cell, way):
					blocked = true
					break
			cell[axis] += step[axis]
		if not blocked:
			return false
	return true


## Every order [param axes] can be taken in.
static func _orders(axes: PackedInt32Array) -> Array[PackedInt32Array]:
	var found: Array[PackedInt32Array] = []
	if axes.size() <= 1:
		found.append(axes)
		return found
	for place in axes.size():
		var rest := axes.duplicate()
		rest.remove_at(place)
		for tail in _orders(rest):
			var order := PackedInt32Array([axes[place]])
			order.append_array(tail)
			found.append(order)
	return found


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
## [param from] and [param to], including headroom over [param top], the level
## the unit crosses between them at ([method _crossing_top]).
func _is_clear(from: Vector3i, to: Vector3i, top: int) -> bool:
	var highest := top + UNIT_HEIGHT - 1
	for y in range(from.y, highest + 1):
		if is_solid(Vector3i(from.x, y, from.z)):
			return false
	for y in range(to.y, highest + 1):
		if is_solid(Vector3i(to.x, y, to.z)):
			return false
	return true
