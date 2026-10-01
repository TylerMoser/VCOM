## The voxels of everything on the map that wears away ([VoxelDestruction]):
## the blocks of the grid, and the voxel models loose in the world
## ([VoxelBody]). It keeps what is left of each, draws and collides it, and
## wears it: a round's bite ([method chip], [method tear]), a blast's crater
## ([method crater]), or breaking up whole ([method crumble]).
## [TerrainDestruction] makes it and says when.
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
## A loose model - one of a crate's pieces once the crate has broken, or any
## rigid body drawn by a MagicaVoxel model taken on with
## [method take_on_body] - wears the same way, but is only for show, as all
## debris is: a round tears through it, taking a bite where it goes in, and
## flies on ([method tear]), and a blast craters it as it craters blocks. Once
## part of it is cut off from the rest, that part flies on as a model of its
## own if it has [constant SMALLEST_PART] voxels or more, and crumbles into
## lumps if not; one worn past its share crumbles whole. A crate's pieces are
## only taken on the first time a round or a blast reaches them
## ([method take_on_later]): most never are, and taking one on costs more than
## making it.
##
## A round's bite is drawn at once. A blast wears many blocks at a time, so
## what it leaves of them is drawn over the next few frames, no more than
## [constant REBUILD_BUDGET] microseconds of each, under its fireball; the
## voxels themselves, and so the rules, have changed at once.
##
## Which voxels of a block go is decided by the global random generator - one
## number for each round or blast - so seeding it replays a fight exactly,
## which blocks break included. Everything else here is only for show and
## draws on a generator of its own, so how much debris there is, or what a
## round tears through on its way, never changes what the rules draw next.
class_name VoxelTerrain
extends Node3D

const VOXEL := VoxelShape.SCALE
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
## How many voxels across, at most, the lumps a round or a blast breaks off
## are, and the most lumps a blast throws about. The rest of what a blast
## breaks off is blown to dust, or there would be thousands; which are thrown
## is chosen before any is made ([Batch]), since making a lump costs three
## times what working out which voxels it holds does.
const DEBRIS_CLUMP := 2
const CRATER_DEBRIS := 150
## The fewest voxels a part cut off a loose model can have and fly on as a
## model of its own; and the most loose models a round tears through.
const SMALLEST_PART := 8
const MOST_TORN := 8
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


## What wearing blocks away did: whether any block lost a voxel, the blocks now
## worn past standing, which must break, and the box, in the world, round every
## block that lost voxels.
class Wear:
	var worn := false
	var broken: Array[Vector3i] = []
	var box := AABB()


## Voxels found near a point: the blocks they are in, by cell (none for a loose
## model), and for each voxel which of those it is in, its place in that
## block's array, and how near it is, roughened, as a score. A block's voxels
## come one after another.
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

	## The voxels at [param picks], places in the lists, by their places in
	## their arrays.
	func voxels_at(picks: PackedInt32Array) -> PackedInt32Array:
		var found := PackedInt32Array()
		for pick in picks:
			found.append(indices[pick])
		return found


## The voxels one block lost in one go: where each was in its array and what
## it held, and the same as rows ([method VoxelShape.rows_of]), for finding
## what that cut loose.
class Lost:
	var indices := PackedInt32Array()
	var held := PackedByteArray()
	var rows := PackedInt64Array()

	func _init(shape: VoxelShape) -> void:
		rows.resize(shape.size.y * shape.size.z)

	## Notes the voxel at [param index], which held [param what], at bit
	## [param x] of row [param row].
	func add(index: int, what: int, row: int, x: int) -> void:
		indices.append(index)
		held.append(what)
		rows[row] |= 1 << x


## Where a ray first meets a voxel of a model: the point, in the world; the
## face of the voxel it came in through, in the model's frame and as the way it
## looks out in the world, none if the ray started inside; the voxel's place in
## the model's array; and how far the ray went.
class Met:
	var point := Vector3.ZERO
	var face := Vector3i.ZERO
	var normal := Vector3.ZERO
	var index := -1
	var distance := 0.0


## Voxels broken off one model in one go, grouped into lumps but not made yet:
## the model's kind and frame, which voxels and what each held, what breaks
## them, and how a lump of them sets off once made. A blast breaks off far more
## lumps than are ever made ([method _scatter]).
class Batch:
	var shape: VoxelShape
	var frame: Transform3D
	var indices: PackedInt32Array
	var held: PackedByteArray
	var destruction: VoxelDestruction
	## Sets a lump moving: called with the [VoxelDebris.Piece], standing where
	## it broke off.
	var motion: Callable
	## The lumps, each as the places in [member indices] of its voxels.
	var clumps: Array = []


## A piece waiting to wear away until a round or a blast first reaches it
## ([method take_on_later]): how it wears, the .vox its model is read from,
## and the bodies it passes through.
class Wearable:
	var destruction: VoxelDestruction
	var source := ""
	var passes: Array = []


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
## Every loose model, by its body, and every piece waiting to be taken on as
## one, by its body.
var _loose := {}
var _wearable := {}
## The level of the bottom of the map, in cells.
var _bottom := 0
## What roughens bites and craters, reseeded for each.
var _noise := FastNoiseLite.new()
var _bump_scale := 1.0
var _bump_size := 0.0
## What everything only for show draws on, so the global generator, which the
## rules draw on, is left alone.
var _show := RandomNumberGenerator.new()


func _init(grid: CombatGrid, map: GridMap, debris: VoxelDebris) -> void:
	name = &"VoxelTerrain"
	_grid = grid
	_map = map
	_debris = debris
	_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	_noise.frequency = 1.0
	_show.randomize()


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
			faces.set_faces(VoxelMesher.faces(shape, shape.voxels))
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


## Takes on [param body], a rigid body drawn by a MagicaVoxel model, as a loose
## model wearing away as [param destruction] says. The model is the first of
## its MeshInstance3D children drawn by one: a model of a .vox imported as a
## scene, the .vox being [param source] ([method VoxelShape.source_of]), or a
## mesh imported straight from a .vox, which needs none. [param passes] are the
## bodies it passes through, which it hands on to the parts cut from it
## ([member VoxelBody.passes]). It is made a piece
## ([method TerrainDestruction.make_piece]), if it was not one, for rounds and
## blasts to find it by. Returns its [VoxelBody], or null if no voxel model
## draws it.
func take_on_body(body: RigidBody3D, destruction: VoxelDestruction, source := "", passes: Array = []) -> VoxelBody:
	if _loose.has(body):
		return _loose[body]
	_wearable.erase(body)
	for child in body.get_children():
		var drawn := child as MeshInstance3D
		if drawn == null or drawn.mesh == null:
			continue
		var shape: VoxelShape = null
		if drawn.has_meta(&"magica_voxel_model_id") and not source.is_empty():
			shape = VoxelShape.read_model(source, int(drawn.get_meta(&"magica_voxel_model_id")))
		elif drawn.mesh.resource_path.get_extension().to_lower() == "vox":
			shape = VoxelShape.read_mesh(drawn.mesh)
		if shape == null or shape.count == 0:
			continue
		if shape.material == null and drawn.mesh.get_surface_count() > 0:
			shape.material = drawn.mesh.surface_get_material(0)
		var model := VoxelBody.new(shape, destruction, body, drawn)
		model.passes = passes
		body.add_child(model)
		TerrainDestruction.make_piece(body)
		_keep(body, model)
		return model
	return null


## Lets [param body] wear away as [method take_on_body] would, but takes it on
## only the first time a round or a blast reaches it ([method _model_of]), as a
## crate's pieces are: taking a piece on costs more than making it, and most
## pieces are never hit. Until then it is just a piece
## ([method TerrainDestruction.make_piece]), noted as one that wears.
func take_on_later(body: RigidBody3D, destruction: VoxelDestruction, source := "", passes: Array = []) -> void:
	if _loose.has(body) or _wearable.has(body):
		return
	var waiting := Wearable.new()
	waiting.destruction = destruction
	waiting.source = source
	waiting.passes = passes
	_wearable[body] = waiting
	TerrainDestruction.make_piece(body)
	body.tree_exiting.connect(_forget.bind(body), CONNECT_ONE_SHOT)


## How many loose models there are: pieces taken on, not those still waiting
## to be ([method take_on_later]).
func loose_count() -> int:
	return _loose.size()


## Whether the block in [param cell] is one that wears away.
func wears_away(cell: Vector3i) -> bool:
	return _shapes.has(_map.get_cell_item(cell))


## The kind of block in [param cell], if it wears away; null if not.
func shape_at(cell: Vector3i) -> VoxelShape:
	return _shapes.get(_map.get_cell_item(cell))


## The block in [param cell]'s own frame, in the world: its cell's middle,
## turned as the block is. Its voxels are laid out in it as its
## [VoxelShape]'s.
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
	var shape := shape_at(cell)
	if shape == null:
		return true
	var at := shape.voxel_under(frame_of(cell).affine_inverse() * point).clamp(Vector3i.ZERO, shape.size - Vector3i.ONE)
	return _voxels_in(cell)[shape.index_of(at)] != 0


## Where a ray from [param origin] along [param direction] first meets a voxel
## of the block in [param cell], one that wears away, as a
## [CombatGrid.RayHit]: [member CombatGrid.RayHit.face] is the face of the
## voxel it came in through. Null if it crosses the cell without meeting one,
## or meets one further than [param max_distance] from [param origin].
func trace(cell: Vector3i, origin: Vector3, direction: Vector3, max_distance: float) -> Variant:
	var shape := shape_at(cell)
	if shape == null or direction.is_zero_approx():
		return null
	var heading := direction.normalized()
	var met := _march(shape, _voxels_in(cell), frame_of(cell), origin, heading, max_distance)
	if met == null:
		return null
	var hit := CombatGrid.RayHit.new()
	hit.cell = cell
	hit.point = met.point
	hit.direction = heading
	hit.distance = met.distance
	if met.face != Vector3i.ZERO:
		var turn := _map.get_basis_with_orthogonal_index(_map.get_cell_item_orientation(cell))
		hit.face = Vector3i((turn * Vector3(met.face)).round())
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
	var radius := _bite_radius(budget)
	var reach := minf(radius * BITE_SPREAD, BITE_REACH)
	_roughen(radius, randi())
	var found := Found.new()
	for cell in _cells_round(center, reach):
		_gather(cell, center, reach, 1.0, found)
	var outward := -hit.direction
	if hit.face != Vector3i.ZERO:
		outward = (_map.global_basis * Vector3(hit.face)).normalized()
	var batches: Array = []
	var wear := _wear_away(found, found.least(budget), _chip_motion(outward, hit.direction), true, batches)
	_scatter(batches)
	return wear


## Tears through every loose model a round flying from [param from] to
## [param to] passes through, with [param damage] environmental damage behind
## it, up to [constant MOST_TORN] of them: breaks off so many voxels for each
## point (each model's [member VoxelDestruction.voxels_per_damage]) nearest
## where it goes into the model, which fly out of the face it went in by and
## on the way it was going, and the round flies on. Only for show: nothing the
## rules decide waits on it.
func tear(from: Vector3, to: Vector3, damage: int) -> void:
	if (_loose.is_empty() and _wearable.is_empty()) or from.is_equal_approx(to):
		return
	var heading := from.direction_to(to)
	var length := from.distance_to(to)
	var batches: Array = []
	# Found first and torn after, as tearing one can cut new models from it.
	for model in _models_along(from, to):
		if not is_instance_valid(model):
			continue
		var met := _march(model.shape, model.voxels, model.frame(), from, heading, length)
		if met == null:
			continue
		var budget := roundi(damage * model.destruction.voxels_per_damage)
		if budget <= 0:
			continue
		var center := met.point + heading * VOXEL * 0.5
		var radius := _bite_radius(budget)
		var reach := minf(radius * BITE_SPREAD, BITE_REACH)
		_roughen(radius, _show.randi())
		var found := Found.new()
		_gather_voxels(model.shape, model.voxels, model.rows, model.frame(), center, reach, 1.0, found, 0)
		var outward := met.normal if met.face != Vector3i.ZERO else -heading
		_wear_model(model, found.voxels_at(found.least(budget)), _chip_motion(outward, heading), batches)
	_scatter(batches)


## Blows a crater round [param origin], where a blast doing [param damage]
## environmental damage goes off, in every block that wears away among
## [param cells], the cells the blast reaches: every voxel within its
## destruction's [method VoxelDestruction.crater_radius] of it, roughened. Every
## loose model inside the blast is cratered the same way, inside the blast.
## Up to [constant CRATER_DEBRIS] lumps of what they lose fly off as debris.
##
## The bottom of the map, only ever worn [constant FLOOR_DEPTH] deep, is blown
## into a bowl instead: as wide as the ball is where it meets the ground, and
## [constant FLOOR_DEPTH] deep in the middle, under where the blast went off.
func crater(origin: Vector3, cells: Array[Vector3i], damage: int) -> Wear:
	var wear := Wear.new()
	var batches: Array = []
	var largest := 0.0
	for cell in cells:
		var destruction: VoxelDestruction = _destructions.get(_map.get_cell_item(cell))
		if destruction != null:
			largest = maxf(largest, destruction.crater_radius(damage))
	if largest > 0.0:
		_roughen(largest, randi())
		var found := Found.new()
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
		wear = _wear_away(found, found.under(1.0), _crater_motion(origin, largest), false, batches)

	# Then every loose model the blast reaches: only for show. A piece waiting
	# to wear away is only taken on if the crater reaches its box.
	if not (_loose.is_empty() and _wearable.is_empty()) and not cells.is_empty():
		var box := _box_round(cells)
		for body in TerrainDestruction.pieces_in(get_world_3d().direct_space_state, box):
			var how := _wear_of(body)
			if how == null:
				continue
			var radius := how.crater_radius(damage)
			if radius <= 0.0:
				continue
			var near := TerrainDestruction.debris_box(body)
			if origin.distance_to(origin.clamp(near.position, near.end)) > radius * (1.0 + ROUGHNESS) + VOXEL:
				continue
			var model := _model_of(body)
			if model == null:
				continue
			_roughen(radius, _show.randi())
			var found := Found.new()
			_gather_voxels(model.shape, model.voxels, model.rows, model.frame(), origin, radius + _bump_size, radius, found, 0, 1.0, radius - _bump_size, -INF, box)
			_wear_model(model, found.voxels_at(found.under(1.0)), _crater_motion(origin, radius), batches)
	_scatter(batches, CRATER_DEBRIS)
	return wear


## Takes what is left of the block in [param cell] out of this: its voxels,
## worn or whole, as an array laid out as its [VoxelShape]'s. Its worn block,
## if it had one, is gone; the cell itself is the caller's to clear.
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


## Breaks [param voxels], what is left of a model of [param shape]'s kind, up
## into lumps at most [member VoxelDestruction.crumble_size] voxels across,
## standing in [param frame] (the model's frame, where it stood or landed), and
## lets them fall. [param hit] is the round that broke it, if one did, which
## knocks the lumps nearest where it struck on along its flight; [param motion]
## is how the model was moving, if it fell whole, which its lumps carry on.
## Returns their bodies.
func crumble(
	voxels: PackedByteArray, shape: VoxelShape, frame: Transform3D, destruction: VoxelDestruction,
	hit: CombatGrid.RayHit = null, motion: Destruction.Motion = null
) -> Array[RID]:
	var indices := PackedInt32Array()
	var held := PackedByteArray()
	for index in shape.length:
		if voxels[index] != 0:
			indices.append(index)
			held.append(voxels[index])
	var sets_off := func(piece: VoxelDebris.Piece) -> void:
		var center := piece.transform.origin
		piece.velocity = _random_in_ball() * CRUMBLE_SCATTER
		piece.spin = _random_in_ball() * CRUMBLE_SPIN
		if hit != null:
			var nearness := 1.0 - clampf(center.distance_to(hit.point) / CRUMBLE_REACH, 0.0, 1.0)
			piece.velocity += hit.direction * CRUMBLE_PUSH * nearness
		if motion != null:
			piece.velocity += motion.at(center)
			piece.spin += motion.angular_velocity
	return _scatter([_batch(indices, held, shape, frame, destruction.crumble_size, destruction, sets_off)])


## The voxels of the block in [param cell]: what is left of it if it is worn,
## its kind's if not, and none if it does not wear away.
func _voxels_in(cell: Vector3i) -> PackedByteArray:
	if _worn.has(cell):
		return (_worn[cell] as WornBlock).voxels
	var shape := shape_at(cell)
	return shape.voxels if shape != null else PackedByteArray()


## The rows of the voxels of the block in [param cell], as [method _voxels_in].
func _rows_in(cell: Vector3i) -> PackedInt64Array:
	if _worn.has(cell):
		return (_worn[cell] as WornBlock).rows
	var shape := shape_at(cell)
	return shape.rows if shape != null else PackedInt64Array()


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


## Breaks off the voxels of [param found] at [param picks], blocks', then
## everything those leave holding on to nothing, grouped into lumps at most
## [constant DEBRIS_CLUMP] voxels across added to [param batches]. Each lump
## sets off as [param motion] says, or, one cut loose, just drops. Says which
## blocks are worn past standing, and draws what is left of the rest: at once
## if [param now], else over the next few frames.
func _wear_away(found: Found, picks: PackedInt32Array, motion: Callable, now: bool, batches: Array) -> Wear:
	# Each block's voxels come one after another, so each block is worn in one
	# go, noting what it lost.
	var losses := {}
	var block: WornBlock = null
	var lost: Lost = null
	var owner := -1
	for pick in picks.size():
		var place := picks[pick]
		if found.owners[place] != owner:
			owner = found.owners[place]
			block = _wear(found.cells[owner])
			lost = Lost.new(block.shape)
			losses[found.cells[owner]] = lost
		var index := found.indices[place]
		var held := block.remove(index)
		if held == 0:
			continue
		var at := block.shape.voxel_at(index)
		lost.add(index, held, at.y + at.z * block.shape.size.y, at.x)

	# What each block lost, and then what that cut loose from it, in lumps.
	var dropping := _falling_motion(Vector3.ZERO, Vector3.ZERO, Vector3.ZERO, LOOSE_SCATTER, CHIP_SPIN * 0.2)
	for cell: Vector3i in losses:
		var worn: WornBlock = _worn[cell]
		var destruction: VoxelDestruction = _destructions[_map.get_cell_item(cell)]
		var lost_here: Lost = losses[cell]
		batches.append(_batch(lost_here.indices, lost_here.held, worn.shape, worn.global_transform, DEBRIS_CLUMP, destruction, motion))
		var loose := _loose_voxels(cell, worn, lost_here.rows)
		var loose_held := PackedByteArray()
		for index in loose:
			loose_held.append(worn.remove(index))
		batches.append(_batch(loose, loose_held, worn.shape, worn.global_transform, DEBRIS_CLUMP, destruction, dropping))

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


## Breaks the voxels at [param indices] off the loose model [param model],
## grouped into lumps at most [constant DEBRIS_CLUMP] voxels across added to
## [param batches], each setting off as [param motion] says, carried on as the
## model was moving; then settles what is left of it ([method _settle]).
func _wear_model(model: VoxelBody, indices: PackedInt32Array, motion: Callable, batches: Array) -> void:
	var lost := PackedInt32Array()
	var held := PackedByteArray()
	for index in indices:
		var what := model.remove(index)
		if what != 0:
			lost.append(index)
			held.append(what)
	if lost.is_empty():
		return
	var moving := model.body.linear_velocity
	var carried := func(piece: VoxelDebris.Piece) -> void:
		motion.call(piece)
		piece.velocity += moving
	batches.append(_batch(lost, held, model.shape, model.frame(), DEBRIS_CLUMP, model.destruction, carried))
	_settle(model, batches)


## Settles what is left of [param model] after it has lost voxels: crumbles it
## if it is worn past its share, or too small to stand on its own; else cuts
## every part no longer joined to the rest off it, as a model of its own if it
## is big enough and as lumps added to [param batches] if not, and draws,
## collides and weighs what is left as it is.
func _settle(model: VoxelBody, batches: Array) -> void:
	if model.count < SMALLEST_PART or model.count < model.destruction.collapse_below * model.whole:
		_crumble_model(model, batches)
		return
	var parts := _parts(model)
	if parts.size() > 1:
		var from := model.body
		var dropping := _falling_motion(from.linear_velocity, from.angular_velocity, from.global_position, LOOSE_SCATTER, CHIP_SPIN * 0.2)
		for place in range(1, parts.size()):
			var part := parts[place]
			if part.size() >= SMALLEST_PART:
				_split_off(model, part)
				continue
			var held := PackedByteArray()
			for index in part:
				held.append(model.remove(index))
			batches.append(_batch(part, held, model.shape, model.frame(), DEBRIS_CLUMP, model.destruction, dropping))
		model.restart()
	model.rebuild()


## Breaks what is left of the loose model [param model] up into lumps
## [member VoxelDestruction.crumble_size] voxels across, carrying on as it was
## moving, adds them to [param batches], and takes the model away.
func _crumble_model(model: VoxelBody, batches: Array) -> void:
	var from := model.body
	var indices := PackedInt32Array()
	var held := PackedByteArray()
	for index in model.shape.length:
		if model.voxels[index] != 0:
			indices.append(index)
			held.append(model.voxels[index])
	var falling := _falling_motion(from.linear_velocity, from.angular_velocity, from.global_position, CRUMBLE_SCATTER, CRUMBLE_SPIN)
	batches.append(_batch(indices, held, model.shape, model.frame(), model.destruction.crumble_size, model.destruction, falling))
	_forget(from)
	# Out of the way at once: its lumps are let go at the next physics step.
	from.hide()
	from.collision_layer = 0
	from.collision_mask = 0
	from.queue_free()


## Cuts the voxels at [param part] off the loose model [param model] as a
## model of its own: a body of its own beside it, drawing, colliding and
## weighing as those voxels, flying on as that part of the model was moving.
## The two start out touching, so they pass through each other, as a crate's
## pieces cut to overlap do, and the part passes through whatever the model
## did, which may be lying through it.
func _split_off(model: VoxelBody, part: PackedInt32Array) -> VoxelBody:
	var from := model.body
	var rigid := RigidBody3D.new()
	rigid.name = from.name
	rigid.collision_layer = from.collision_layer
	rigid.collision_mask = from.collision_mask
	rigid.continuous_cd = from.continuous_cd
	rigid.physics_material_override = from.physics_material_override
	var drawn := MeshInstance3D.new()
	drawn.name = model.drawn.name
	drawn.transform = from.global_transform.affine_inverse() * model.drawn.global_transform
	rigid.add_child(drawn)
	var collider := CollisionShape3D.new()
	collider.shape = BoxShape3D.new()
	rigid.add_child(collider)
	var left := PackedByteArray()
	left.resize(model.shape.length)
	for index in part:
		left[index] = model.remove(index)
	var split := VoxelBody.new(model.shape, model.destruction, rigid, drawn, left)
	split.whole_mass = model.whole_mass * split.count / maxi(model.whole, 1)
	rigid.add_child(split)
	from.get_parent().add_child(rigid)
	rigid.global_transform = from.global_transform
	TerrainDestruction.make_piece(rigid)
	# What either passes through, the other knows of, taken on or not yet.
	var passes: Array = [from]
	for other in model.passes:
		if is_instance_valid(other):
			passes.append(other)
	model.passes = passes.slice(1)
	for other in passes:
		rigid.add_collision_exception_with(other)
		var theirs: VoxelBody = _loose.get(other)
		if theirs != null:
			theirs.passes.append(rigid)
		elif _wearable.has(other):
			(_wearable[other] as Wearable).passes.append(rigid)
	split.passes = passes
	rigid.linear_velocity = _moving_at(from, split.world_box().get_center())
	rigid.angular_velocity = from.angular_velocity
	_keep(rigid, split)
	split.rebuild()
	return split


## The parts of what is left of [param model], each every voxel joined to the
## others face to face, as their places in its array, the biggest first.
func _parts(model: VoxelBody) -> Array[PackedInt32Array]:
	var shape := model.shape
	var voxels := model.voxels
	var steps := shape.steps()
	var seen := PackedByteArray()
	seen.resize(shape.length)
	var parts: Array[PackedInt32Array] = []
	for z in shape.size.z:
		for y in shape.size.y:
			var row := model.rows[y + z * shape.size.y]
			var row_start := shape.origin + y * shape.stride_y + z * shape.stride_z
			while row != 0:
				var low := row & -row
				row ^= low
				var start: int = row_start + VoxelMesher.BIT[low]
				if seen[start] != 0:
					continue
				seen[start] = 1
				var part := PackedInt32Array([start])
				var next := 0
				while next < part.size():
					var at := part[next]
					next += 1
					for step in steps:
						var near := at + step
						if voxels[near] != 0 and seen[near] == 0:
							seen[near] = 1
							part.append(near)
				parts.append(part)
	parts.sort_custom(func(a: PackedInt32Array, b: PackedInt32Array) -> bool: return a.size() > b.size())
	return parts


## How fast the point [param at], in the world, of [param body] is moving.
static func _moving_at(body: RigidBody3D, at: Vector3) -> Vector3:
	return body.linear_velocity + body.angular_velocity.cross(at - body.global_position)


## Notes [param model] as the loose model [param body] is, and forgets it once
## the body goes.
func _keep(body: RigidBody3D, model: VoxelBody) -> void:
	_loose[body] = model
	model.tree_exiting.connect(_forget.bind(body), CONNECT_ONE_SHOT)


## Forgets [param body], a loose model or a piece waiting to be one.
func _forget(body: RigidBody3D) -> void:
	_loose.erase(body)
	_wearable.erase(body)


## The loose model [param body] is, taken on now if it was a piece waiting to
## wear away ([method take_on_later]); null if it does not wear away.
func _model_of(body: Object) -> VoxelBody:
	var model: VoxelBody = _loose.get(body)
	if model != null:
		return model
	var waiting: Wearable = _wearable.get(body)
	if waiting == null:
		return null
	return take_on_body(body as RigidBody3D, waiting.destruction, waiting.source, waiting.passes)


## How [param body] wears away, taken on or still waiting to be; null if it
## does not.
func _wear_of(body: Object) -> VoxelDestruction:
	var model: VoxelBody = _loose.get(body)
	if model != null:
		return model.destruction
	var waiting: Wearable = _wearable.get(body)
	return waiting.destruction if waiting != null else null


## Every loose model whose body a round flying from [param from] to [param to]
## passes through, nearest first, up to [constant MOST_TORN]; a piece waiting
## to wear away is taken on as it is found.
func _models_along(from: Vector3, to: Vector3) -> Array[VoxelBody]:
	var found: Array[VoxelBody] = []
	var query := PhysicsRayQueryParameters3D.create(from, to, TerrainDestruction.PIECE_LAYER)
	query.collide_with_areas = false
	query.hit_from_inside = true
	var passed: Array[RID] = []
	var space := get_world_3d().direct_space_state
	# A few pieces that do not wear away may be passed through on the way.
	for attempt in MOST_TORN * 2:
		query.exclude = passed
		var met := space.intersect_ray(query)
		if met.is_empty():
			break
		passed.append(met.rid)
		var model := _model_of(met.collider)
		if model != null:
			found.append(model)
			if found.size() >= MOST_TORN:
				break
	return found


## Makes the lumps of [param batches] and lets them fall: up to [param most]
## of them, chosen at random before any is made, the rest blown to dust; every
## one if [param most] is less than 0. Returns their bodies.
func _scatter(batches: Array, most := -1) -> Array[RID]:
	var total := 0
	for batch: Batch in batches:
		total += batch.clumps.size()
	# Which to make, numbered through each batch's lumps in turn.
	var chosen := PackedByteArray()
	chosen.resize(total)
	if most < 0 or total <= most:
		chosen.fill(1)
	else:
		var numbers := PackedInt32Array()
		numbers.resize(total)
		for number in total:
			numbers[number] = number
		for pick in most:
			var other := _show.randi_range(pick, total - 1)
			var swap := numbers[pick]
			numbers[pick] = numbers[other]
			numbers[other] = swap
			chosen[numbers[pick]] = 1
	var by_destruction := {}
	var number := 0
	for batch: Batch in batches:
		for clump: Array in batch.clumps:
			if chosen[number] != 0:
				var list: Array = by_destruction.get_or_add(batch.destruction, [])
				list.append(_make(batch, clump))
			number += 1
	var made: Array[RID] = []
	for destruction: VoxelDestruction in by_destruction:
		var pieces: Array[VoxelDebris.Piece] = []
		pieces.assign(by_destruction[destruction])
		made.append_array(_debris.add(pieces, destruction))
	return made


## Draws and collides [param block] as what is left of it, and wakes the
## debris lying round it, which may have been lying on what has gone.
func _redraw(block: WornBlock) -> void:
	if not is_instance_valid(block):
		return
	block.rebuild()
	_debris.wake(AABB(block.global_position - HALF, Vector3.ONE).grow(VoxelDebris.LYING_ON))


## The voxels at [param indices] in a model of [param shape]'s kind standing in
## [param frame], which held [param held] each, as a [Batch]: grouped into
## lumps at most [param size] voxels across, broken off as [param destruction]
## breaks them, to set off as [param motion] says once made. They are grouped
## on a grid set at random, so no two models come apart along the same lines.
func _batch(
	indices: PackedInt32Array, held: PackedByteArray, shape: VoxelShape, frame: Transform3D, size: int,
	destruction: VoxelDestruction, motion: Callable
) -> Batch:
	var batch := Batch.new()
	batch.shape = shape
	batch.frame = frame
	batch.indices = indices
	batch.held = held
	batch.destruction = destruction
	batch.motion = motion
	if indices.is_empty():
		return batch
	var shift := Vector3i(_show.randi_range(0, size - 1), _show.randi_range(0, size - 1), _show.randi_range(0, size - 1))
	var clumps := {}
	for place in indices.size():
		var key := (shape.voxel_at(indices[place]) + shift) / size
		var clump: Array = clumps.get_or_add(key, [])
		clump.append(place)
	batch.clumps = clumps.values()
	return batch


## The lump of [param batch] made of the voxels at [param clump], places in
## its lists: standing where they broke off, and set moving as the batch says.
func _make(batch: Batch, clump: Array) -> VoxelDebris.Piece:
	var shape := batch.shape
	var least := Vector3i.MAX
	var most := Vector3i.MIN
	for place: int in clump:
		var at := shape.voxel_at(batch.indices[place])
		least = least.min(at)
		most = most.max(at)
	var middle := shape.corner + (Vector3(least) + Vector3(most + Vector3i.ONE)) * 0.5 * VOXEL
	var piece := VoxelDebris.Piece.new()
	piece.transform = Transform3D(batch.frame.basis, batch.frame * middle)
	piece.size = Vector3(most - least + Vector3i.ONE) * VOXEL
	piece.voxels = PackedVector3Array()
	piece.colors = PackedColorArray()
	for place: int in clump:
		piece.voxels.append(shape.center_of(batch.indices[place]) - middle)
		piece.colors.append(shape.colors[batch.held[place]])
	batch.motion.call(piece)
	return piece


## How the lumps a round breaks off set off: out of [param outward], the face
## it struck, and on along [param heading], the way it was going, tumbling.
func _chip_motion(outward: Vector3, heading: Vector3) -> Callable:
	return func(piece: VoxelDebris.Piece) -> void:
		piece.velocity = (
			outward * _show.randf_range(CHIP_SPEED_MIN, CHIP_SPEED_MAX)
			+ _random_in_ball() * CHIP_SCATTER
			+ heading * CHIP_CARRY
		)
		piece.spin = _random_in_ball() * CHIP_SPIN


## How the lumps a blast going off at [param origin] breaks off set off: away
## from it, the harder the nearer, out to a crater [param radius] across, and
## tumbling; what the blast drives down into the ground, the ground throws back
## up.
func _crater_motion(origin: Vector3, radius: float) -> Callable:
	return func(piece: VoxelDebris.Piece) -> void:
		var away := piece.transform.origin - origin
		var share := lerpf(1.0, CRATER_FAR_SHARE, clampf(away.length() / radius, 0.0, 1.0))
		away.y = absf(away.y)
		piece.velocity = (
			Blast.away_from(away) * CRATER_SPEED * share
			+ Vector3.UP * CRATER_LIFT * share
			+ _random_in_ball() * CRATER_SCATTER
		)
		piece.spin = _random_in_ball() * CHIP_SPIN


## How lumps that drop away from something set off: as the point they broke
## from was moving, on a body moving at [param linear] and turning at
## [param angular] about [param center], give or take [param scatter] cells a
## second, and turning as it turned, give or take [param spin] radians a
## second.
func _falling_motion(linear: Vector3, angular: Vector3, center: Vector3, scatter: float, spin: float) -> Callable:
	return func(piece: VoxelDebris.Piece) -> void:
		piece.velocity = linear + angular.cross(piece.transform.origin - center) + _random_in_ball() * scatter
		piece.spin = angular + _random_in_ball() * spin


## How far a bite of [param budget] voxels reaches into a solid model, as a
## half ball, in cells.
static func _bite_radius(budget: int) -> float:
	return pow(3.0 * budget / TAU, 1.0 / 3.0) * VOXEL


## Adds to [param found] every voxel of the block in [param cell], if it wears
## away, within [param reach] of [param center] that may be worn, as
## [method _gather_voxels] does. The bottom of the map is only worn
## [constant FLOOR_DEPTH] deep.
func _gather(cell: Vector3i, center: Vector3, reach: float, scale: float, found: Found, squash := 1.0, certain := -INF) -> void:
	var shape := shape_at(cell)
	if shape == null:
		return
	var lowest := -INF
	if cell.y == _bottom:
		lowest = _grid.cell_center(cell).y + 0.5 - FLOOR_DEPTH * VOXEL
	var before := found.indices.size()
	_gather_voxels(shape, _voxels_in(cell), _rows_in(cell), frame_of(cell), center, reach, scale, found, found.cells.size(), squash, certain, lowest)
	if found.indices.size() > before:
		found.cells.append(cell)


## Adds to [param found], as [param owner]'s, every one of [param voxels] -
## laid out as [param shape]'s, with [param rows], standing in [param frame] -
## within [param reach] of [param center], scored by how far it is, roughened,
## over [param scale]. Distance up and down counts [param squash] times over,
## for a crater flatter than a ball. One nearer than [param certain] scores
## nothing at all, however the edge is roughened. One lower than
## [param lowest], in the world, or, if [param inside] has volume, outside it,
## is left out.
##
## Only the voxels inside the ball are looked at: each row of the model is
## cut to the run of it inside the ball, and only the voxels there are visited.
func _gather_voxels(
	shape: VoxelShape, voxels: PackedByteArray, rows: PackedInt64Array, frame: Transform3D, center: Vector3,
	reach: float, scale: float, found: Found, owner: int, squash := 1.0, certain := -INF, lowest := -INF,
	inside := AABB()
) -> void:
	var local := frame.affine_inverse() * center
	var up := (frame.basis.inverse() * Vector3.UP).normalized()
	# In voxels from the least corner of voxel (0, 0, 0) from here on.
	var middle := (local - shape.corner) / VOXEL
	var far := reach / VOXEL
	var last_voxel := shape.size - Vector3i.ONE
	var least := Vector3i((middle - Vector3.ONE * far).floor()).clamp(Vector3i.ZERO, last_voxel)
	var most := Vector3i((middle + Vector3.ONE * far).floor()).clamp(Vector3i.ZERO, last_voxel)
	# Squashed up and down along the model's y only if that is up: otherwise
	# rows are cut to the whole ball, which holds the squashed one.
	var level := absf(up.y) > 0.999
	var flatten := squash * squash if level else 1.0
	var stretch := squash * squash - 1.0
	var limited := inside.has_volume()
	for z in range(least.z, most.z + 1):
		var across_z := z + 0.5 - middle.z
		for y in range(least.y, most.y + 1):
			var row := rows[y + z * shape.size.y]
			if row == 0:
				continue
			# A model standing upright has the whole row at one height.
			if level and lowest > -INF and (frame * (shape.corner + Vector3(0.0, (y + 0.5) * VOXEL, 0.0))).y < lowest:
				continue
			var across_y := y + 0.5 - middle.y
			var left := far * far - across_z * across_z - across_y * across_y * flatten
			if left < 0.0:
				continue
			var half_run := sqrt(left)
			var first := maxi(ceili(middle.x - half_run - 0.5), 0)
			var last := mini(floori(middle.x + half_run - 0.5), last_voxel.x)
			if first > last:
				continue
			var run := row & ((1 << (last + 1)) - 1) & ~((1 << first) - 1)
			var row_start := shape.origin + y * shape.stride_y + z * shape.stride_z
			while run != 0:
				var low := run & -run
				run ^= low
				var x: int = VoxelMesher.BIT[low]
				var offset := Vector3(x + 0.5 - middle.x, across_y, across_z) * VOXEL
				var rise := offset.dot(up)
				var distance := sqrt(offset.length_squared() + rise * rise * stretch)
				if distance > reach:
					continue
				var score := 0.0
				if distance >= certain or not level or limited:
					var world := frame * (shape.corner + (Vector3(x, y, z) + HALF) * VOXEL)
					if world.y < lowest:
						continue
					if limited and not inside.has_point(world):
						continue
					if distance >= certain:
						score = (distance + _bump(world)) / scale
				found.owners.append(owner)
				found.indices.append(row_start + x)
				found.scores.append(score)


## Where a ray from [param origin] along [param heading], normalised, first
## meets one of [param voxels] - laid out as [param shape]'s, standing in
## [param frame] - within [param max_distance] of [param origin], as a [Met];
## null if it meets none. Traced voxel by voxel through the model's box, as
## [method CombatGrid.cast] goes cell by cell.
func _march(shape: VoxelShape, voxels: PackedByteArray, frame: Transform3D, origin: Vector3, heading: Vector3, max_distance: float) -> Met:
	var inverse := frame.affine_inverse()
	# Counted in voxels from the least corner of voxel (0, 0, 0), along the ray
	# in voxels.
	var from := (inverse * origin - shape.corner) / VOXEL
	var along := (inverse.basis * heading).normalized()
	var bounds := Vector3(shape.size)

	# Where the ray is inside the model's box, between enter and leave.
	var enter := -INF
	var leave := INF
	var entered_on := -1
	for axis in 3:
		if is_zero_approx(along[axis]):
			if from[axis] < 0.0 or from[axis] > bounds[axis]:
				return null
			continue
		var near := -from[axis] / along[axis]
		var far := (bounds[axis] - from[axis]) / along[axis]
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

	var voxel := Vector3i((from + along * (t + 1e-4)).floor()).clamp(Vector3i.ZERO, shape.size - Vector3i.ONE)
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
	while voxels[shape.index_of(voxel)] == 0:
		var axis := next_cross.min_axis_index()
		t = next_cross[axis]
		voxel[axis] += step[axis]
		if t > leave or voxel[axis] < 0 or voxel[axis] >= shape.size[axis]:
			return null
		next_cross[axis] += cross_spacing[axis]
		entered_on = axis

	var met := Met.new()
	met.point = frame * (shape.corner + (from + along * t) * VOXEL)
	met.distance = origin.distance_to(met.point)
	if met.distance > max_distance:
		return null
	met.index = shape.index_of(voxel)
	if entered_on >= 0:
		met.face[entered_on] = -step[entered_on]
		met.normal = (frame.basis * Vector3(met.face)).normalized()
	return met


## Sets bites and craters roughening afresh, from [param seed], for one
## [param size] cells across.
func _roughen(size: float, seed: int) -> void:
	_noise.seed = seed
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


## The box, in the world, that [param cells] fill.
func _box_round(cells: Array[Vector3i]) -> AABB:
	var box := AABB(_grid.cell_center(cells[0]), Vector3.ZERO)
	for cell in cells:
		box = box.expand(_grid.cell_center(cell))
	return box.grow(0.5)


## The voxels of [param block], in [param cell], left holding on to nothing
## once the voxels in [param gone] (rows of what it has just lost, as
## [method VoxelShape.rows_of]) have gone. Each voxel left next to one gone is
## searched from, until the search reaches a voxel that holds on to something,
## or turns out to be cut off with everything it reaches.
func _loose_voxels(cell: Vector3i, block: WornBlock, gone: PackedInt64Array) -> PackedInt32Array:
	var shape := block.shape
	var voxels := block.voxels
	var rows := block.rows
	var size := shape.size
	var frame := frame_of(cell)
	var on_bottom := cell.y == _bottom
	# Every voxel left next to one gone: along its row, or in the rows round it.
	var starts := PackedInt32Array()
	for z in size.z:
		for y in size.y:
			var row := rows[y + z * size.y]
			if row == 0:
				continue
			var near := (gone[y + z * size.y] << 1) | (gone[y + z * size.y] >> 1)
			if y > 0:
				near |= gone[y - 1 + z * size.y]
			if y < size.y - 1:
				near |= gone[y + 1 + z * size.y]
			if z > 0:
				near |= gone[y + (z - 1) * size.y]
			if z < size.z - 1:
				near |= gone[y + (z + 1) * size.y]
			var edge := row & near
			var row_start := shape.origin + y * shape.stride_y + z * shape.stride_z
			while edge != 0:
				var low := edge & -edge
				edge ^= low
				starts.append(row_start + VoxelMesher.BIT[low])
	var steps := shape.steps()
	# 0 not yet known, 1 held, 2 being searched, 3 loose.
	var known := PackedByteArray()
	known.resize(shape.length)
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
			if _holds_on(shape, frame, at, on_bottom):
				held = true
				break
			for step in steps:
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
	var shape := block.shape
	var voxels := block.voxels
	var rising := shape.stride_y if up.y > 0.0 else -shape.stride_y
	var bottom := 0 if up.y > 0.0 else shape.size.y - 1
	var top := shape.size.y - 1 - bottom
	# Up is pushed last, so it is searched first.
	var steps: Array[int] = [-rising, 1, -1, shape.stride_z, -shape.stride_z, rising]
	var seen := PackedByteArray()
	seen.resize(shape.length)
	var stack := PackedInt32Array()
	for z in shape.size.z:
		for x in shape.size.x:
			var index := shape.index_of(Vector3i(x, bottom, z))
			if voxels[index] != 0:
				stack.append(index)
				seen[index] = 1
	while not stack.is_empty():
		var at := stack[stack.size() - 1]
		stack.resize(stack.size() - 1)
		if shape.voxel_at(at).y == top:
			return true
		for step in steps:
			var next := at + step
			if voxels[next] != 0 and seen[next] == 0:
				seen[next] = 1
				stack.append(next)
	return false


## Whether the voxel at [param index], of a block of [param shape]'s kind
## standing in [param frame], holds on to something outside its cell: a voxel,
## or any other block, across a face of the cell it is on, or the ground under
## the bottom of the map, [param on_bottom] saying the block is there.
func _holds_on(shape: VoxelShape, frame: Transform3D, index: int, on_bottom: bool) -> bool:
	var at := shape.voxel_at(index)
	for axis in 3:
		var side := 0
		if at[axis] == 0:
			side = -1
		elif at[axis] == shape.size[axis] - 1:
			side = 1
		else:
			continue
		var out := Vector3.ZERO
		out[axis] = side
		if on_bottom and (frame.basis * out).y < -0.5:
			return true
		if is_solid_at(frame * (shape.center_of(index) + out * VOXEL)):
			return true
	return false


## A point drawn at random from the ball of radius one.
func _random_in_ball() -> Vector3:
	var point := Vector3(_show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0))
	while point.length_squared() > 1.0:
		point = Vector3(_show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0))
	return point
