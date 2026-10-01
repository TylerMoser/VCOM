## The voxels of every block on the map that wears away ([VoxelDestruction]):
## what is left of each, drawn and collided with, and the ways they wear - a
## round's bite ([method chip]) and a blast's crater ([method crater]) - or
## break up whole ([method crumble]). [TerrainDestruction] makes it and says
## when.
##
## A block nothing has touched is drawn by the GridMap as any other is, and
## collides as its voxels do. The first time it loses one it becomes a
## [WornBlock], which draws and collides as what is left, and its cell is
## given the block's stand-in: an item of the map's library that draws nothing
## and collides as nothing, but is still a block, so to the rules the cell is
## exactly as solid as before. Sight, cover and paths are read off whole cells
## and never see a voxel.
##
## Rounds are the exception: [method CombatGrid.cast] traces them through these
## blocks voxel by voxel ([method trace]), so a stray round strikes the voxel it
## actually meets, and one that passes beside a thin trunk, or through a hole,
## flies on.
##
## A voxel left joined to nothing that holds it up - the ground under a block
## on the bottom of the map, or a voxel of the next block across - falls away
## with those broken off. A block worn below its share of voxels
## ([member VoxelDestruction.collapse_below]) is worn past standing, and so is
## one holding something up that nothing joins from its bottom to its top any
## more, such as a tree's trunk shot through: [TerrainDestruction] breaks them.
## The bottom of the map never is, and is only ever worn [constant FLOOR_DEPTH]
## voxels deep, since a unit stands on the top of its tile whatever is under
## its feet.
##
## A round's bite is drawn at once. A blast wears many blocks at a time, so
## what it leaves of them is drawn over the next few frames, no more than
## [constant REBUILD_BUDGET] microseconds of each, under its fireball; the
## voxels themselves, and so the rules, have changed at once.
##
## Which voxels go is decided by the global random generator, so seeding it
## replays a fight exactly, which blocks break included. How they fall is
## physics, and only for show.
class_name VoxelTerrain
extends Node3D

const SIZE := VoxelShape.SIZE
const VOXEL := 1.0 / SIZE
const HALF := Vector3(0.5, 0.5, 0.5)
## How deep, in voxels from its top, a block on the bottom of the map can be
## worn. Its tile's floor stays at the top of the block, where a unit stands, so
## a deep crater would leave the unit standing on air.
const FLOOR_DEPTH := 4
## How far from where a round strikes the voxels it breaks off can be, as many
## times as far as its bite would reach into a solid block, and never further
## than [constant BITE_REACH] cells: a round striking a thin trunk takes a
## slice of it, not the whole trunk from top to bottom.
const BITE_SPREAD := 2.0
const BITE_REACH := 0.5
## How far round its edge a bite or a crater wanders in and out, as a share of
## its size, and how many bumps it has across its size: so it is not a perfect
## ball.
const ROUGHNESS := 0.2
const BUMPS := 2.5
## How many voxels across, at most, the pieces a round or a blast breaks off
## are, and the most pieces a blast throws about. The rest of what a blast
## breaks off is blown to dust, or there would be thousands.
const DEBRIS_CLUMP := 2
const CRATER_DEBRIS := 150
## Most time a frame given to drawing what a blast has left of the blocks it
## wore, in microseconds.
const REBUILD_BUDGET := 4000

## How fast a voxel a round breaks off flies out of the face it struck, in cells
## a second, between these; how much it scatters about that; how much it is
## carried on the way the round was going; and how fast it tumbles, in radians
## a second.
const CHIP_SPEED_MIN := 1.0
const CHIP_SPEED_MAX := 2.5
const CHIP_SCATTER := 0.8
const CHIP_CARRY := 0.5
const CHIP_SPIN := 15.0
## How fast a piece a blast breaks off flies away from where it goes off, in
## cells a second, and how much faster upward: this much for one right where
## it goes off, and [constant CRATER_FAR_SHARE] of it for one at the crater's
## edge. And how much it scatters about that. The blast's push
## ([method VoxelDebris.burst]) is added to it.
const CRATER_SPEED := 4.0
const CRATER_LIFT := 4.5
const CRATER_FAR_SHARE := 0.4
const CRATER_SCATTER := 1.0
## How much a voxel cut loose from everything scatters as it drops away.
const LOOSE_SCATTER := 0.3
## How much the pieces a block crumbles into scatter and tumble; how hard the
## round that broke it knocks the piece nearest where it struck on along its
## flight, in cells a second; and how far from there the knock reaches, in
## cells.
const CRUMBLE_SCATTER := 0.6
const CRUMBLE_SPIN := 4.0
const CRUMBLE_PUSH := 1.5
const CRUMBLE_REACH := 1.0

## The six ways out of a voxel, along x, y and z and back, and how far it is in
## the array to the voxel each way. Up is first and down last, so a search
## through the voxels pops down first and reaches the ground soonest.
const STEPS: Array[int] = [
	VoxelShape.STRIDE_Y, VoxelShape.STRIDE_X, -VoxelShape.STRIDE_X,
	VoxelShape.STRIDE_Z, -VoxelShape.STRIDE_Z, -VoxelShape.STRIDE_Y,
]


## What wearing blocks away did: whether any block lost a voxel, the blocks now
## worn past standing, which must break, and the box, in the world, round every
## block that lost voxels.
class Wear:
	var worn := false
	var broken: Array[Vector3i] = []
	var box := AABB()


## Voxels found near a point: the blocks they are in, by cell, and for each
## voxel which of those it is in, its place in that block's array, and how
## near it is, roughened, as a score. A block's voxels come one after another.
class Found:
	var cells: Array[Vector3i] = []
	var owners := PackedInt32Array()
	var indices := PackedInt32Array()
	var scores := PackedFloat32Array()

	## The [param count] voxels scoring least, by place in the lists.
	func least(count: int) -> PackedInt32Array:
		var picks := PackedInt32Array()
		if scores.is_empty() or count <= 0:
			return picks
		var sorted := scores.duplicate()
		sorted.sort()
		var limit := sorted[mini(count, sorted.size()) - 1]
		for index in scores.size():
			if scores[index] <= limit and picks.size() < count:
				picks.append(index)
		return picks

	## Every voxel scoring under [param limit], by place in the lists.
	func under(limit: float) -> PackedInt32Array:
		var picks := PackedInt32Array()
		for index in scores.size():
			if scores[index] < limit:
				picks.append(index)
		return picks


## The voxels one block lost in one go: where each was in its array and what
## it held, and the same as rows ([method VoxelShape.rows_of]), for finding
## what that cut loose.
class Lost:
	var indices := PackedInt32Array()
	var held := PackedByteArray()
	var rows := PackedInt32Array()

	func _init() -> void:
		rows.resize(VoxelShape.SIZE * VoxelShape.SIZE)

	## Notes the voxel at [param index], which held [param what], at bit
	## [param x] of row [param row].
	func add(index: int, what: int, row: int, x: int) -> void:
		indices.append(index)
		held.append(what)
		rows[row] |= 1 << x

	## Notes everything [param other] notes too.
	func take_in(other: Lost) -> void:
		indices.append_array(other.indices)
		held.append_array(other.held)
		for row in rows.size():
			rows[row] |= other.rows[row]


var _grid: CombatGrid
var _map: GridMap
var _debris: VoxelDebris
## Every block that wears away, by MeshLibrary item, its own and its
## stand-in's: its kind's voxels, and its destruction.
var _shapes := {}
var _destructions := {}
## The stand-in of each such block, by its own item.
var _stand_ins := {}
## The blocks that have lost voxels, by cell.
var _worn := {}
## Worn blocks still drawn as they were before a blast, as a set.
var _stale := {}
## The level of the bottom of the map, in cells.
var _bottom := 0
## What roughens bites and craters, reseeded for each.
var _noise := FastNoiseLite.new()
var _bump_scale := 1.0
var _bump_size := 0.0


func _init(grid: CombatGrid, map: GridMap, debris: VoxelDebris) -> void:
	name = &"VoxelTerrain"
	_grid = grid
	_map = map
	_debris = debris
	_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	_noise.frequency = 1.0


func _process(_delta: float) -> void:
	if _stale.is_empty():
		return
	var start := Time.get_ticks_usec()
	for block: WornBlock in _stale.keys():
		_stale.erase(block)
		_redraw(block)
		if Time.get_ticks_usec() - start > REBUILD_BUDGET:
			break


## Takes on every block of [param library] that [param destructions] (by item)
## says wears away: reads its voxels, has it collide as them, and gives it a
## stand-in, which is added to [param destructions] with the same destruction.
## A block whose voxels cannot be read is taken out of [param destructions], and
## never breaks. Call it on the map's library before the map is given it.
func take_on(library: MeshLibrary, destructions: Dictionary) -> void:
	var cells := _map.get_used_cells()
	if not cells.is_empty():
		_bottom = cells[0].y
		for cell in cells:
			_bottom = mini(_bottom, cell.y)
	for item: int in destructions.keys():
		var destruction := destructions[item] as VoxelDestruction
		if destruction == null:
			continue
		var shape := VoxelShape.read(library.get_item_mesh(item), library.get_item_mesh_transform(item))
		if shape == null:
			destructions.erase(item)
			continue
		# A block that fills its cell keeps the cube it has; anything else
		# collides as its voxels, so debris lands on the trunk, not round it.
		if not shape.is_full():
			var faces := ConcavePolygonShape3D.new()
			faces.set_faces(VoxelMesher.faces(shape.voxels))
			library.set_item_shapes(item, [faces, Transform3D.IDENTITY])
		var stand_in := library.get_last_unused_item_id()
		library.create_item(stand_in)
		library.set_item_name(stand_in, "%s (worn)" % library.get_item_name(item))
		library.set_item_mesh_transform(stand_in, library.get_item_mesh_transform(item))
		_stand_ins[item] = stand_in
		for each in [item, stand_in]:
			_shapes[each] = shape
			_destructions[each] = destruction
		destructions[stand_in] = destruction


## Whether the block in [param cell] is one that wears away.
func wears_away(cell: Vector3i) -> bool:
	return _shapes.has(_map.get_cell_item(cell))


## The kind of block in [param cell], if it wears away; null if not.
func shape_at(cell: Vector3i) -> VoxelShape:
	return _shapes.get(_map.get_cell_item(cell))


## The block in [param cell]'s own frame, in the world: its cell's middle,
## turned as the block is. Its voxels are laid out in it as in a
## [VoxelShape]'s array.
func frame_of(cell: Vector3i) -> Transform3D:
	var turn := _map.get_basis_with_orthogonal_index(_map.get_cell_item_orientation(cell))
	return _map.global_transform * Transform3D(turn, _map.map_to_local(cell))


## How many voxels the block in [param cell] has left.
func count_at(cell: Vector3i) -> int:
	if _worn.has(cell):
		return (_worn[cell] as WornBlock).count
	var shape := shape_at(cell)
	return shape.count if shape != null else 0


## Whether [param point], in the world, is inside a block: inside one of its
## voxels for a block that wears away, anywhere in its cell for any other.
func is_solid_at(point: Vector3) -> bool:
	var cell := _map.local_to_map(_map.to_local(point))
	if not _grid.is_solid(cell):
		return false
	var voxels := _voxels_in(cell)
	if voxels.is_empty():
		return true
	var at := Vector3i(((frame_of(cell).affine_inverse() * point + HALF) * SIZE).floor())
	return voxels[VoxelShape.index_of(at.clamp(Vector3i.ZERO, Vector3i.ONE * (SIZE - 1)))] != 0


## Where a ray from [param origin] along [param direction] first meets a voxel
## of the block in [param cell], one that wears away, as a
## [CombatGrid.RayHit]: [member CombatGrid.RayHit.face] is the face of the
## voxel it came in through. Null if it crosses the cell without meeting one,
## or meets one further than [param max_distance] from [param origin].
func trace(cell: Vector3i, origin: Vector3, direction: Vector3, max_distance: float) -> Variant:
	var voxels := _voxels_in(cell)
	if voxels.is_empty() or direction.is_zero_approx():
		return null
	var frame := frame_of(cell)
	var inverse := frame.affine_inverse()
	var heading := direction.normalized()
	# Counted in voxels from the cell's least corner, along the ray in voxels.
	var from := (inverse * origin + HALF) * SIZE
	var along := (inverse.basis * heading).normalized()

	# Where the ray is inside the cell's box, between enter and leave.
	var enter := -INF
	var leave := INF
	var entered_on := -1
	for axis in 3:
		if is_zero_approx(along[axis]):
			if from[axis] < 0.0 or from[axis] > SIZE:
				return null
			continue
		var near := -from[axis] / along[axis]
		var far := (SIZE - from[axis]) / along[axis]
		if near > far:
			var swap := near
			near = far
			far = swap
		if near > enter:
			enter = near
			entered_on = axis
		leave = minf(leave, far)
	if leave < maxf(enter, 0.0):
		return null
	var t := maxf(enter, 0.0)
	if enter < 0.0:
		entered_on = -1

	# Then voxel by voxel through it, as CombatGrid.cast goes cell by cell.
	var voxel := Vector3i((from + along * (t + 1e-4)).floor()).clamp(Vector3i.ZERO, Vector3i.ONE * (SIZE - 1))
	var step := Vector3i.ZERO
	var next_cross := Vector3(INF, INF, INF)
	var cross_spacing := Vector3(INF, INF, INF)
	for axis in 3:
		if is_zero_approx(along[axis]):
			continue
		step[axis] = int(signf(along[axis]))
		var boundary := voxel[axis] + (1 if step[axis] > 0 else 0)
		next_cross[axis] = (boundary - from[axis]) / along[axis]
		cross_spacing[axis] = absf(1.0 / along[axis])
	while voxels[VoxelShape.index_of(voxel)] == 0:
		var axis := next_cross.min_axis_index()
		t = next_cross[axis]
		voxel[axis] += step[axis]
		if t > leave or voxel[axis] < 0 or voxel[axis] >= SIZE:
			return null
		next_cross[axis] += cross_spacing[axis]
		entered_on = axis

	var hit := CombatGrid.RayHit.new()
	hit.cell = cell
	hit.point = frame * ((from + along * t) / SIZE - HALF)
	hit.direction = heading
	hit.distance = origin.distance_to(hit.point)
	if hit.distance > max_distance:
		return null
	if entered_on >= 0:
		var face := Vector3.ZERO
		face[entered_on] = -step[entered_on]
		var turn := _map.get_basis_with_orthogonal_index(_map.get_cell_item_orientation(cell))
		hit.face = Vector3i((turn * face).round())
	return hit


## Breaks off the voxels nearest where [param hit] struck a block that wears
## away, so many for each point of [param damage] (its destruction's
## [member VoxelDestruction.voxels_per_damage]), from whichever blocks they
## are in, out to [constant BITE_SPREAD] times as far as the bite would go
## into a solid block. Each flies out of the face the round struck.
func chip(hit: CombatGrid.RayHit, damage: int) -> Wear:
	var destruction: VoxelDestruction = _destructions.get(_map.get_cell_item(hit.cell))
	if destruction == null:
		return Wear.new()
	var budget := roundi(damage * destruction.voxels_per_damage)
	if budget <= 0:
		return Wear.new()
	# Half a voxel in, so the voxel struck is the nearest. Into a solid block the
	# bite would be a half ball of budget voxels, which sets how far it reaches
	# and how much its edge is roughened.
	var center := hit.point + hit.direction * VOXEL * 0.5
	var radius := pow(3.0 * budget / TAU, 1.0 / 3.0) * VOXEL
	var reach := minf(radius * BITE_SPREAD, BITE_REACH)
	_roughen(radius)
	var found := Found.new()
	for cell in _cells_round(center, reach):
		_gather(cell, center, reach, 1.0, found)

	var outward := -hit.direction
	if hit.face != Vector3i.ZERO:
		outward = (_map.global_basis * Vector3(hit.face)).normalized()
	var heading := hit.direction
	var launch := func(_middle: Vector3) -> Vector3:
		return (
			outward * randf_range(CHIP_SPEED_MIN, CHIP_SPEED_MAX)
			+ _random_in_ball() * CHIP_SCATTER
			+ heading * CHIP_CARRY
		)
	return _wear_away(found, found.least(budget), launch, CHIP_SPIN, budget, true)


## Blows a crater round [param origin], where a blast doing [param damage]
## environmental damage goes off, in every block that wears away among
## [param cells], the cells the blast reaches: every voxel within its
## destruction's [method VoxelDestruction.crater_radius] of it, roughened. Up to
## [constant CRATER_DEBRIS] pieces of them fly off as debris.
##
## The bottom of the map, only ever worn [constant FLOOR_DEPTH] deep, is blown
## into a bowl instead: as wide as the ball is where it meets the ground, and
## [constant FLOOR_DEPTH] deep in the middle, under where the blast went off.
func crater(origin: Vector3, cells: Array[Vector3i], damage: int) -> Wear:
	var found := Found.new()
	var largest := 0.0
	for cell in cells:
		var destruction: VoxelDestruction = _destructions.get(_map.get_cell_item(cell))
		if destruction != null:
			largest = maxf(largest, destruction.crater_radius(damage))
	if largest <= 0.0:
		return Wear.new()
	_roughen(largest)
	for cell in cells:
		var destruction: VoxelDestruction = _destructions.get(_map.get_cell_item(cell))
		if destruction == null:
			continue
		var radius := destruction.crater_radius(damage)
		if radius <= 0.0:
			continue
		# Well inside, a voxel goes however its edge is roughened.
		if cell.y != _bottom:
			_gather(cell, origin, radius + _bump_size, radius, found, 1.0, radius - _bump_size)
			continue
		var ground := _grid.cell_center(cell).y + 0.5
		var across := sqrt(maxf(radius * radius - pow(origin.y - ground, 2.0), 0.0))
		if across > 0.0:
			var under := Vector3(origin.x, ground, origin.z)
			_gather(cell, under, across + _bump_size, across, found, across / (FLOOR_DEPTH * VOXEL), across - _bump_size)

	var launch := func(middle: Vector3) -> Vector3:
		var away := middle - origin
		var share := lerpf(1.0, CRATER_FAR_SHARE, clampf(away.length() / largest, 0.0, 1.0))
		# What the blast drives down into the ground, the ground throws back up.
		away.y = absf(away.y)
		return (
			Blast.away_from(away) * CRATER_SPEED * share
			+ Vector3.UP * CRATER_LIFT * share
			+ _random_in_ball() * CRATER_SCATTER
		)
	return _wear_away(found, found.under(1.0), launch, CHIP_SPIN, CRATER_DEBRIS, false)


## Takes what is left of the block in [param cell] out of this: its voxels,
## worn or whole, as a [VoxelShape]'s array. Its worn block, if it had one, is
## gone; the cell itself is the caller's to clear.
func take(cell: Vector3i) -> PackedByteArray:
	if _worn.has(cell):
		var block: WornBlock = _worn[cell]
		var voxels := block.voxels
		_worn.erase(cell)
		_stale.erase(block)
		block.free()
		return voxels
	var shape := shape_at(cell)
	return shape.voxels if shape != null else PackedByteArray()


## Breaks [param voxels], what is left of a block of [param shape]'s kind, up
## into pieces at most [member VoxelDestruction.crumble_size] voxels across,
## standing in [param frame] (the block's frame, where it stood or landed), and
## lets them fall. [param hit] is the round that broke it, if one did, which
## knocks the pieces nearest where it struck on along its flight; [param motion]
## is how the block was moving, if it fell whole, which its pieces carry on.
## Returns their bodies.
func crumble(
	voxels: PackedByteArray, shape: VoxelShape, frame: Transform3D, destruction: VoxelDestruction,
	hit: CombatGrid.RayHit = null, motion: Destruction.Motion = null
) -> Array[RID]:
	var indices := PackedInt32Array()
	var held := PackedByteArray()
	for index in VoxelShape.LENGTH:
		if voxels[index] != 0:
			indices.append(index)
			held.append(voxels[index])
	var pieces := _cut(indices, held, shape, frame, destruction.crumble_size)
	for piece in pieces:
		var center := piece.transform.origin
		piece.velocity = _random_in_ball() * CRUMBLE_SCATTER
		piece.spin = _random_in_ball() * CRUMBLE_SPIN
		if hit != null:
			var nearness := 1.0 - clampf(center.distance_to(hit.point) / CRUMBLE_REACH, 0.0, 1.0)
			piece.velocity += hit.direction * CRUMBLE_PUSH * nearness
		if motion != null:
			piece.velocity += motion.at(center)
			piece.spin += motion.angular_velocity
	return _debris.add(pieces, destruction)


## The voxels of the block in [param cell]: what is left of it if it is worn,
## its kind's if not, and none if it does not wear away.
func _voxels_in(cell: Vector3i) -> PackedByteArray:
	if _worn.has(cell):
		return (_worn[cell] as WornBlock).voxels
	var shape := shape_at(cell)
	return shape.voxels if shape != null else PackedByteArray()


## The rows of the voxels of the block in [param cell], as [method _voxels_in].
func _rows_in(cell: Vector3i) -> PackedInt32Array:
	if _worn.has(cell):
		return (_worn[cell] as WornBlock).rows
	var shape := shape_at(cell)
	return shape.rows if shape != null else PackedInt32Array()


## The worn block in [param cell], made the first time it is asked for: from
## then on it draws and collides as what is left, and the cell holds the
## block's stand-in.
func _wear(cell: Vector3i) -> WornBlock:
	if _worn.has(cell):
		return _worn[cell]
	var item := _map.get_cell_item(cell)
	var block := WornBlock.new(_shapes[item])
	add_child(block)
	block.global_transform = frame_of(cell)
	_map.set_cell_item(cell, _stand_ins.get(item, item), _map.get_cell_item_orientation(cell))
	_worn[cell] = block
	return block


## Breaks off the voxels of [param found] at [param picks], then everything
## those leave holding on to nothing, and lets them fall as pieces at most
## [constant DEBRIS_CLUMP] voxels across: up to [param most_pieces] of them, the
## rest blown to dust. Each piece sets off as [param launch] says (called with
## where it was, returning its velocity), or, one cut loose, just drops, and
## tumbles up to [param spin] radians a second. Says which blocks are worn past
## standing, and draws what is left of the rest: at once if [param now], else
## over the next few frames.
func _wear_away(found: Found, picks: PackedInt32Array, launch: Callable, spin: float, most_pieces: int, now: bool) -> Wear:
	# Each block's voxels come one after another, so each block is worn in one
	# go, its arrays worked on here and handed back, with what it lost.
	var losses := {}
	var block: WornBlock = null
	var voxels := PackedByteArray()
	var rows := PackedInt32Array()
	var count := 0
	var lost: Lost = null
	var owner := -1
	for pick in picks.size():
		var place := picks[pick]
		if found.owners[place] != owner:
			if block != null:
				_hand_back(found.cells[owner], block, voxels, rows, count, lost, losses)
			owner = found.owners[place]
			block = _wear(found.cells[owner])
			voxels = block.voxels
			rows = block.rows
			count = block.count
			lost = Lost.new()
		var index := found.indices[place]
		var held := voxels[index]
		if held == 0:
			continue
		voxels[index] = 0
		var at := VoxelShape.voxel_at(index)
		var row := at.y + at.z * SIZE
		rows[row] &= ~(1 << at.x)
		count -= 1
		lost.add(index, held, row, at.x)
	if block != null:
		_hand_back(found.cells[owner], block, voxels, rows, count, lost, losses)

	# What each block lost, and then what that cut loose from it, in pieces.
	var pieces: Array = []
	for cell: Vector3i in losses:
		var worn: WornBlock = _worn[cell]
		var destruction: VoxelDestruction = _destructions[_map.get_cell_item(cell)]
		var lost_here: Lost = losses[cell]
		for piece in _cut(lost_here.indices, lost_here.held, worn.shape, worn.global_transform, DEBRIS_CLUMP):
			piece.velocity = launch.call(piece.transform.origin)
			piece.spin = _random_in_ball() * spin
			pieces.append([piece, destruction])
		var loose := _loose_voxels(cell, worn, lost_here.rows)
		var loose_held := PackedByteArray()
		for index in loose:
			loose_held.append(worn.remove(index))
		for piece in _cut(loose, loose_held, worn.shape, worn.global_transform, DEBRIS_CLUMP):
			piece.velocity = _random_in_ball() * LOOSE_SCATTER
			piece.spin = _random_in_ball() * spin * 0.2
			pieces.append([piece, destruction])
	if pieces.size() > most_pieces:
		pieces.shuffle()
		pieces = pieces.slice(0, most_pieces)
	var by_destruction := {}
	for pair: Array in pieces:
		var list: Array = by_destruction.get_or_add(pair[1], [])
		list.append(pair[0])
	for destruction: VoxelDestruction in by_destruction:
		var made: Array[VoxelDebris.Piece] = []
		made.assign(by_destruction[destruction])
		_debris.add(made, destruction)

	var wear := Wear.new()
	wear.worn = not losses.is_empty()
	var first := true
	for cell: Vector3i in losses:
		var left: WornBlock = _worn[cell]
		var destruction: VoxelDestruction = _destructions[_map.get_cell_item(cell)]
		var box := AABB(_grid.cell_center(cell) - HALF, Vector3.ONE)
		wear.box = box if first else wear.box.merge(box)
		first = false
		# One worn past standing is about to be broken up, as it is now.
		if cell.y != _bottom and (left.count < destruction.collapse_below * left.shape.count or not _holds_up(cell, left)):
			wear.broken.append(cell)
		elif now:
			_redraw(left)
		else:
			_stale[left] = true
	return wear


## Gives [param block], in [param cell], back what wearing it has left of it -
## [param voxels], their [param rows] and their [param count] - and notes in
## [param losses], by cell, what it [param lost].
func _hand_back(
	cell: Vector3i, block: WornBlock, voxels: PackedByteArray, rows: PackedInt32Array, count: int,
	lost: Lost, losses: Dictionary
) -> void:
	block.voxels = voxels
	block.rows = rows
	block.count = count
	if losses.has(cell):
		(losses[cell] as Lost).take_in(lost)
	else:
		losses[cell] = lost


## Draws and collides [param block] as what is left of it, and wakes the
## debris lying round it, which may have been lying on what has gone.
func _redraw(block: WornBlock) -> void:
	if not is_instance_valid(block):
		return
	block.rebuild()
	_debris.wake(AABB(block.global_position - HALF, Vector3.ONE).grow(VoxelDebris.LYING_ON))


## The voxels at [param indices] in a block of [param shape]'s kind standing
## in [param frame], which held [param held] each, cut into pieces at most
## [param size] voxels across, standing where they were and not yet moving.
## They are cut on a grid set at random, so no two blocks come apart along the
## same lines.
func _cut(indices: PackedInt32Array, held: PackedByteArray, shape: VoxelShape, frame: Transform3D, size: int) -> Array[VoxelDebris.Piece]:
	var pieces: Array[VoxelDebris.Piece] = []
	if indices.is_empty():
		return pieces
	var shift := Vector3i(randi_range(0, size - 1), randi_range(0, size - 1), randi_range(0, size - 1))
	var clumps := {}
	for place in indices.size():
		var key := (VoxelShape.voxel_at(indices[place]) + shift) / size
		var clump: Array = clumps.get_or_add(key, [])
		clump.append(place)
	for clump: Array in clumps.values():
		var least := Vector3i.ONE * SIZE
		var most := -Vector3i.ONE
		for place: int in clump:
			var at := VoxelShape.voxel_at(indices[place])
			least = least.min(at)
			most = most.max(at)
		var middle := (Vector3(least) + Vector3(most + Vector3i.ONE)) * 0.5 / SIZE - HALF
		var piece := VoxelDebris.Piece.new()
		piece.transform = Transform3D(frame.basis, frame * middle)
		piece.size = Vector3(most - least + Vector3i.ONE) * VOXEL
		piece.voxels = PackedVector3Array()
		piece.colors = PackedColorArray()
		for place: int in clump:
			piece.voxels.append(VoxelShape.center_of(indices[place]) - middle)
			piece.colors.append(shape.colors[held[place]])
		pieces.append(piece)
	return pieces


## Adds to [param found] every voxel of the block in [param cell], if it wears
## away, within [param reach] of [param center] that may be worn: scored by how
## far it is, roughened, over [param scale]. Distance up and down counts
## [param squash] times over, for a crater flatter than a ball. One nearer than
## [param certain] scores nothing at all, however the edge is roughened.
##
## Only the voxels inside the ball are looked at: each row of the block is
## cut to the run of it inside the ball, and only the voxels there are visited.
func _gather(
	cell: Vector3i, center: Vector3, reach: float, scale: float, found: Found, squash := 1.0, certain := -INF
) -> void:
	var voxels := _voxels_in(cell)
	if voxels.is_empty():
		return
	var rows := _rows_in(cell)
	var frame := frame_of(cell)
	var local := frame.affine_inverse() * center
	var up := frame.basis.inverse() * Vector3.UP
	# In voxels from the cell's least corner from here on.
	var middle := (local + HALF) * SIZE
	var far := reach * SIZE
	var least := Vector3i((middle - Vector3.ONE * far).floor()).clamp(Vector3i.ZERO, Vector3i.ONE * (SIZE - 1))
	var most := Vector3i((middle + Vector3.ONE * far).floor()).clamp(Vector3i.ZERO, Vector3i.ONE * (SIZE - 1))
	# Squashed up and down along the block's y only if that is up: otherwise
	# rows are cut to the whole ball, which holds the squashed one.
	var level := absf(up.y) > 0.999
	var flatten := squash * squash if level else 1.0
	var stretch := squash * squash - 1.0
	var lowest := -INF
	if cell.y == _bottom:
		lowest = _grid.cell_center(cell).y + 0.5 - FLOOR_DEPTH * VOXEL
	var owner := -1
	for z in range(least.z, most.z + 1):
		var across_z := z + 0.5 - middle.z
		for y in range(least.y, most.y + 1):
			var row := rows[y + z * SIZE]
			if row == 0:
				continue
			# A block standing upright has the whole row at one height.
			if level and (frame * Vector3(0.0, (y + 0.5) / SIZE - 0.5, 0.0)).y < lowest:
				continue
			var across_y := y + 0.5 - middle.y
			var left := far * far - across_z * across_z - across_y * across_y * flatten
			if left < 0.0:
				continue
			var half_run := sqrt(left)
			var first := maxi(ceili(middle.x - half_run - 0.5), 0)
			var last := mini(floori(middle.x + half_run - 0.5), SIZE - 1)
			if first > last:
				continue
			var run := row & ((1 << (last + 1)) - 1) & ~((1 << first) - 1)
			var row_start := VoxelShape.ORIGIN + y * VoxelShape.STRIDE_Y + z * VoxelShape.STRIDE_Z
			while run != 0:
				var low := run & -run
				run ^= low
				var x: int = VoxelMesher.BIT[low]
				var offset := Vector3(x + 0.5 - middle.x, across_y, across_z) / SIZE
				var rise := offset.dot(up)
				var distance := sqrt(offset.length_squared() + rise * rise * stretch)
				if distance > reach:
					continue
				var score := 0.0
				if distance >= certain or not level:
					var world := frame * ((Vector3(x, y, z) + HALF) / SIZE - HALF)
					if world.y < lowest:
						continue
					if distance >= certain:
						score = (distance + _bump(world)) / scale
				if owner < 0:
					found.cells.append(cell)
					owner = found.cells.size() - 1
				found.owners.append(owner)
				found.indices.append(row_start + x)
				found.scores.append(score)


## Sets bites and craters roughening afresh for one [param size] cells across.
func _roughen(size: float) -> void:
	_noise.seed = randi()
	_bump_size = size * ROUGHNESS
	_bump_scale = BUMPS / maxf(size, VOXEL)


## How far the edge of the bite or crater being made wanders in or out at
## [param point], in cells.
func _bump(point: Vector3) -> float:
	return _noise.get_noise_3dv(point * _bump_scale) * _bump_size


## Every cell a ball of [param reach] round [param center] reaches into.
func _cells_round(center: Vector3, reach: float) -> Array[Vector3i]:
	var least := _map.local_to_map(_map.to_local(center - Vector3.ONE * reach))
	var most := _map.local_to_map(_map.to_local(center + Vector3.ONE * reach))
	var cells: Array[Vector3i] = []
	for x in range(mini(least.x, most.x), maxi(least.x, most.x) + 1):
		for y in range(mini(least.y, most.y), maxi(least.y, most.y) + 1):
			for z in range(mini(least.z, most.z), maxi(least.z, most.z) + 1):
				cells.append(Vector3i(x, y, z))
	return cells


## The voxels of [param block], in [param cell], left holding on to nothing
## once the voxels in [param gone] (rows of what it has just lost, as
## [method VoxelShape.rows_of]) have gone. Each voxel left next to one gone is
## searched from, until the search reaches a voxel that holds on to something,
## or turns out to be cut off with everything it reaches.
func _loose_voxels(cell: Vector3i, block: WornBlock, gone: PackedInt32Array) -> PackedInt32Array:
	var voxels := block.voxels
	var rows := block.rows
	var frame := frame_of(cell)
	var on_bottom := cell.y == _bottom
	# Every voxel left next to one gone: along its row, or in the rows round it.
	var starts := PackedInt32Array()
	for z in SIZE:
		for y in SIZE:
			var row := rows[y + z * SIZE]
			if row == 0:
				continue
			var near := (gone[y + z * SIZE] << 1) | (gone[y + z * SIZE] >> 1)
			if y > 0:
				near |= gone[y - 1 + z * SIZE]
			if y < SIZE - 1:
				near |= gone[y + 1 + z * SIZE]
			if z > 0:
				near |= gone[y + (z - 1) * SIZE]
			if z < SIZE - 1:
				near |= gone[y + (z + 1) * SIZE]
			var edge := row & near
			var row_start := VoxelShape.ORIGIN + y * VoxelShape.STRIDE_Y + z * VoxelShape.STRIDE_Z
			while edge != 0:
				var low := edge & -edge
				edge ^= low
				starts.append(row_start + VoxelMesher.BIT[low])
	# 0 not yet known, 1 held, 2 being searched, 3 loose.
	var known := PackedByteArray()
	known.resize(VoxelShape.LENGTH)
	var loose := PackedInt32Array()
	var stack := PackedInt32Array()
	var searched := PackedInt32Array()
	for start in starts:
		if known[start] != 0:
			continue
		stack.clear()
		searched.clear()
		stack.append(start)
		searched.append(start)
		known[start] = 2
		var held := false
		while not stack.is_empty() and not held:
			var at := stack[stack.size() - 1]
			stack.resize(stack.size() - 1)
			if _holds_on(frame, at, on_bottom):
				held = true
				break
			for step in STEPS:
				var next := at + step
				if voxels[next] == 0:
					continue
				if known[next] == 1:
					held = true
					break
				if known[next] == 0:
					known[next] = 2
					stack.append(next)
					searched.append(next)
		for index in searched:
			known[index] = 1 if held else 3
		if not held:
			loose.append_array(searched)
	return loose


## Whether what is left of [param block], in [param cell], can still hold up
## whatever stands on it: nothing does, or some run of its voxels still joins
## the bottom of its cell to the top. A tree's trunk shot through holds up its
## crown no longer, however much of the rest of it is left. Searched from every
## voxel along the bottom, upward first, until one reaches the top. A block
## lying on its side is taken to hold up what is on it.
func _holds_up(cell: Vector3i, block: WornBlock) -> bool:
	if not _grid.is_solid(cell + Vector3i.UP):
		return true
	var up := frame_of(cell).basis.inverse() * Vector3.UP
	if absf(up.y) < 0.999:
		return true
	var voxels := block.voxels
	var rising := VoxelShape.STRIDE_Y if up.y > 0.0 else -VoxelShape.STRIDE_Y
	var bottom := 0 if up.y > 0.0 else SIZE - 1
	var top := SIZE - 1 - bottom
	# Up is pushed last, so it is searched first.
	var steps: Array[int] = [-rising, VoxelShape.STRIDE_X, -VoxelShape.STRIDE_X, VoxelShape.STRIDE_Z, -VoxelShape.STRIDE_Z, rising]
	var seen := PackedByteArray()
	seen.resize(VoxelShape.LENGTH)
	var stack := PackedInt32Array()
	for z in SIZE:
		for x in SIZE:
			var index := VoxelShape.ORIGIN + x * VoxelShape.STRIDE_X + bottom * VoxelShape.STRIDE_Y + z * VoxelShape.STRIDE_Z
			if voxels[index] != 0:
				stack.append(index)
				seen[index] = 1
	while not stack.is_empty():
		var at := stack[stack.size() - 1]
		stack.resize(stack.size() - 1)
		if VoxelShape.voxel_at(at).y == top:
			return true
		for step in steps:
			var next := at + step
			if voxels[next] != 0 and seen[next] == 0:
				seen[next] = 1
				stack.append(next)
	return false


## Whether the voxel at [param index], of a block standing in [param frame],
## holds on to something outside its cell: a voxel, or any other block, across
## a face of the cell it is on, or the ground under the bottom of the map,
## [param on_bottom] saying the block is there.
func _holds_on(frame: Transform3D, index: int, on_bottom: bool) -> bool:
	var at := VoxelShape.voxel_at(index)
	for axis in 3:
		var side := 0
		if at[axis] == 0:
			side = -1
		elif at[axis] == SIZE - 1:
			side = 1
		else:
			continue
		var out := Vector3.ZERO
		out[axis] = side
		if on_bottom and (frame.basis * out).y < -0.5:
			return true
		if is_solid_at(frame * (VoxelShape.center_of(index) + out * VOXEL)):
			return true
	return false


## A point drawn at random from the ball of radius one.
static func _random_in_ball() -> Vector3:
	var point := Vector3(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0), randf_range(-1.0, 1.0))
	while point.length_squared() > 1.0:
		point = Vector3(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0), randf_range(-1.0, 1.0))
	return point
