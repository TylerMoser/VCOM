## Every voxel broken off a block that wears away ([VoxelDestruction]): lumps
## of one voxel or a few, falling, tumbling and coming to rest among the rest of
## the debris, and staying there for the rest of the fight.
##
## There can be many thousands, so they are kept lean. A lump is a rigid body
## made straight on the physics server, with no node of its own, and every
## voxel of every lump is drawn by a few MultiMeshes, a cube in the colour it
## was. A voxel is only moved while its lump moves, which the physics server
## reports each step, so a lump at rest costs nothing a frame.
##
## Otherwise they are debris like a crate's pieces: on the debris layer,
## bumping off the blocks, each other and units, thrown about by blasts
## ([method burst]), and taken away once they fall off the map or turn up
## wedged inside a block ([method tidy]). Nothing in the rules sees them.
##
## A lump is let go a physics step after it is made, as a crate's pieces are:
## the block it broke from may only lose its collision at the end of the frame,
## and until then the lump would start inside it. It is drawn from the start.
##
## The physics can only hold so many bodies (the Jolt limits in the project
## settings), so the lumps' bodies are kept under [constant MOST]. The moment
## they reach it, the lumps lying at rest furthest from the tile the camera is
## looking at ([member focus]) are stilled until fewer than [constant KEEP]
## still have bodies: a stilled lump has no body, and stays drawn exactly where
## it lies, so nothing leaves the board, but the bodies go to the lumps the
## player is watching, and to every lump broken off from then on. A lump still
## moving is never stilled. A stilled lump gets its body back the moment
## anything disturbs it: a blast reaching it ([method burst]), the ground going
## from under it, or a unit walking into it ([method wake]).
class_name VoxelDebris
extends Node3D

## How big a voxel is, in cells.
const VOXEL := 1.0 / VoxelShape.SIZE
## How many voxels each MultiMesh draws.
const CHUNK := 4096
## The most bodies the lumps have at once, well inside the physics' limit on
## bodies, which the map's blocks, units and other debris share; and how many
## they keep once lumps have been stilled to make room.
const MOST := 20000
const KEEP := 5000
## How many physics steps a lump must go without moving to count as at rest,
## and so be stilled if room is needed.
const RESTING_STEPS := 2
## How far a lump's middle can be from the face of whatever it lies on, in
## cells: more than half the widest lump. Waking what lies on a block looks
## this far round it.
const LYING_ON := 0.3
## How much smaller a lump's box is than its voxels, as a share of each side,
## as a crate's pieces are: a voxel exactly as wide as a gap would wedge in it.
const SLACK := ScriptedDestruction.SLACK
## Lightest a lump can be, in kilograms.
const MIN_MASS := 0.01
## Where a voxel no longer drawn is put: shrunk to nothing.
const HIDDEN := Transform3D(Basis(Vector3.ZERO, Vector3.ZERO, Vector3.ZERO), Vector3.ZERO)
## How far the debris can be from the map's origin and still be drawn, in
## cells. The MultiMeshes are never culled, so they never work out their bounds
## as the voxels move.
const REACH := 1000.0

## What a lump is: taken away; made, but held out of the physics until the next
## step; moving with a body in the physics; or stilled, lying where it came to
## rest with no body at all.
enum State { GONE, HELD, LIVE, STILL }


## A lump about to be made: where it is, what it is made of and how it moves.
class Piece:
	## The middle of its box, in the world, turned as its voxels are.
	var transform := Transform3D.IDENTITY
	## The middle of each of its voxels, in the lump's own frame, and the colour
	## of each.
	var voxels := PackedVector3Array([Vector3.ZERO])
	var colors := PackedColorArray([Color.WHITE])
	## The box round its voxels, in the lump's own frame.
	var size := Vector3.ONE * VOXEL
	## How fast it moves, in cells a second, and turns, in radians a second.
	var velocity := Vector3.ZERO
	var spin := Vector3.ZERO


## The point the camera is looking at, in the world, called when lumps must be
## stilled to make room: the furthest from it go first. Unset, they are
## measured from the map's origin.
var focus: Callable

var _space := RID()
var _cube: BoxMesh
## The MultiMeshes the voxels are drawn by, and how many of each one's are used.
var _chunks: Array[MultiMesh] = []
var _chunk_used := PackedInt32Array()

## Each lump, by number: what it is ([enum State]); its body, while it has one;
## its weight, friction, bounce and the size of its box, to make a body with;
## where its middle was last seen, and how it lay when it was stilled; and the
## last physics step it was seen moving in.
var _state := PackedByteArray()
var _bodies: Array[RID] = []
var _masses := PackedFloat32Array()
var _frictions := PackedFloat32Array()
var _bounces := PackedFloat32Array()
var _sizes := PackedVector3Array()
var _centers := PackedVector3Array()
var _poses: Array[Transform3D] = []
var _moved_at := PackedInt64Array()
## Where each lump's voxels are drawn - which MultiMesh, from where and how
## many - and where in [member _offsets] each one's middles start.
var _chunk_of := PackedInt32Array()
var _first := PackedInt32Array()
var _voxel_count := PackedInt32Array()
var _offset_start := PackedInt32Array()
var _offsets := PackedVector3Array()
## Lumps held but not let go yet, with the physics frame each was made in, and
## how each is to move once it is.
var _waiting := PackedInt32Array()
var _waiting_since := PackedInt64Array()
var _velocities := PackedVector3Array()
var _spins := PackedVector3Array()
## Every lump not gone, filed by the cell (a cell a unit across, in the world)
## its middle was last seen in, and the cell each is filed under.
var _by_cell := {}
var _cells: Array[Vector3i] = []
## Lumps seen moving since [method tidy] last looked, as a set.
var _moved := {}
## How many lumps there are, and how many of them have bodies.
var _living := 0
var _bodied := 0
## A box shape for every size of lump, by size.
var _boxes := {}


func _init() -> void:
	name = &"VoxelDebris"
	_cube = BoxMesh.new()
	_cube.size = Vector3.ONE * VOXEL
	# Drawn as the blocks are, so a voxel is the colour it was on the block.
	var material := StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.vertex_color_is_srgb = true
	material.roughness = 1.0
	_cube.material = material


func _enter_tree() -> void:
	_space = get_world_3d().space
	for piece in _state.size():
		if _state[piece] == State.LIVE:
			PhysicsServer3D.body_set_space(_bodies[piece], _space)


# The world the bodies are in belongs to the window, not to the map, so they
# would stay in it after the map has gone.
func _exit_tree() -> void:
	for piece in _state.size():
		if _state[piece] == State.LIVE:
			PhysicsServer3D.body_set_space(_bodies[piece], RID())


func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE:
		for piece in _state.size():
			if _state[piece] == State.LIVE or _state[piece] == State.HELD:
				PhysicsServer3D.free_rid(_bodies[piece])
		for shape: RID in _boxes.values():
			PhysicsServer3D.free_rid(shape)


func _physics_process(_delta: float) -> void:
	if _waiting.is_empty():
		return
	var frame := Engine.get_physics_frames()
	var still := PackedInt32Array()
	var still_since := PackedInt64Array()
	for index in _waiting.size():
		var piece := _waiting[index]
		if _waiting_since[index] >= frame:
			still.append(piece)
			still_since.append(_waiting_since[index])
		elif _state[piece] == State.HELD:
			_let_go(piece)
	_waiting = still
	_waiting_since = still_since


## How many lumps there are.
func count() -> int:
	return _living


## How many of them have bodies.
func body_count() -> int:
	return _bodied


## Whether any lump has been stilled and lies without a body.
func has_still() -> bool:
	return _living > _bodied


## How many voxels the lumps there are have between them.
func voxel_count() -> int:
	var voxels := 0
	for piece in _state.size():
		if _state[piece] != State.GONE:
			voxels += _voxel_count[piece]
	return voxels


## Makes [param pieces], broken off a block [param destruction] breaks, and
## returns their bodies. With [constant MOST] bodies about, lumps lying still
## are stilled first to make room ([member focus]); should every lump be on the
## move, the rest are blown to dust.
func add(pieces: Array[Piece], destruction: VoxelDestruction) -> Array[RID]:
	var made: Array[RID] = []
	var frame := Engine.get_physics_frames()
	var voxel_mass := destruction.density * VOXEL * VOXEL * VOXEL
	for piece in pieces:
		if piece.voxels.is_empty():
			continue
		if _bodied >= MOST:
			_make_room()
			if _bodied >= MOST:
				break
		var index := _state.size()
		_state.append(State.HELD)
		_bodies.append(RID())
		_masses.append(maxf(voxel_mass * piece.voxels.size(), MIN_MASS))
		_frictions.append(destruction.friction)
		_bounces.append(destruction.bounce)
		_sizes.append(piece.size)
		_centers.append(piece.transform.origin)
		_poses.append(piece.transform)
		_moved_at.append(frame)
		_velocities.append(piece.velocity)
		_spins.append(piece.spin)
		_offset_start.append(_offsets.size())
		_offsets.append_array(piece.voxels)
		_cells.append(Vector3i.ZERO)
		_file(index, Vector3i(piece.transform.origin.floor()))
		_place_voxels(index, piece)
		var body := _make_body(index)
		_bodies[index] = body
		_living += 1
		_bodied += 1
		_waiting.append(index)
		_waiting_since.append(frame)
		made.append(body)
	return made


## Throws every lump whose middle is inside [param box] away from
## [param origin] with a [Blast] of [param force], as a blast throws a crate's
## pieces, a stilled one given its body back first. Lumps are taken as
## unturned boxes: near enough for what they show the blast.
func burst(origin: Vector3, box: AABB, force: float) -> void:
	if force <= 0.0:
		return
	for piece in _within(box):
		if _state[piece] == State.STILL:
			_rebody(piece)
		var center := _centers[piece]
		var half := _sizes[piece] * 0.5
		var away := center - origin
		var direction := Blast.away_from(away)
		var impulse := direction * Blast.strength(away.length(), force) * Blast.box_area(_sizes[piece], Basis.IDENTITY, direction)
		if _state[piece] == State.HELD:
			# Not in the physics yet: it sets off at the speed the push gives it.
			_velocities[piece] += impulse / _masses[piece]
			continue
		var contact := origin.clamp(center - half, center + half)
		PhysicsServer3D.body_apply_impulse(_bodies[piece], impulse, contact - center)


## Wakes every lump with its middle inside [param box], for one left lying on
## something that has gone from under it, or in the way of something on the
## move: a stilled one gets its body back, and, unless [param only_still], one
## asleep is woken.
func wake(box: AABB, only_still := false) -> void:
	for piece in _within(box):
		if _state[piece] == State.STILL:
			_rebody(piece)
		elif _state[piece] == State.LIVE and not only_still:
			PhysicsServer3D.body_set_state(_bodies[piece], PhysicsServer3D.BODY_STATE_SLEEPING, false)


## Takes away every lump seen moving since this was last called that is now
## lower than [param lowest] - fallen off the map - or wedged inside something
## solid, by [param is_solid] (called with a point in the world, returning
## whether it is inside a block). A lump at rest is neither.
func tidy(lowest: float, is_solid: Callable) -> void:
	for piece: int in _moved:
		if _state[piece] != State.LIVE:
			continue
		var center := _centers[piece]
		if center.y < lowest or is_solid.call(center):
			_remove(piece)
	_moved.clear()


## Stills the lumps lying at rest furthest from [member focus] until fewer
## than [constant KEEP] lumps have bodies: each loses its body and stays drawn
## where it lies. Lumps still moving, or just made, keep theirs.
func _make_room() -> void:
	var around: Vector3 = focus.call() if focus.is_valid() else Vector3.ZERO
	var frame := Engine.get_physics_frames()
	var resting := PackedInt32Array()
	var distances := PackedFloat32Array()
	for piece in _state.size():
		if _state[piece] == State.LIVE and frame - _moved_at[piece] > RESTING_STEPS:
			resting.append(piece)
			distances.append(_centers[piece].distance_squared_to(around))
	var needed := _bodied - (KEEP - 1)
	if needed <= 0 or resting.is_empty():
		return
	if needed >= resting.size():
		for piece in resting:
			_still(piece)
		return
	# The furthest are those at least as far as the needed-th furthest: every
	# one further than that, then as many as it takes of those just as far.
	var sorted := distances.duplicate()
	sorted.sort()
	var limit := sorted[resting.size() - needed]
	var stilled := 0
	for place in resting.size():
		if distances[place] > limit:
			_still(resting[place])
			stilled += 1
	for place in resting.size():
		if stilled >= needed:
			break
		if distances[place] == limit:
			_still(resting[place])
			stilled += 1


## Takes the body away from the lump [param piece], at rest, leaving it drawn
## where it lies, and notes how it lies, for giving it a body again.
func _still(piece: int) -> void:
	var body := _bodies[piece]
	_poses[piece] = PhysicsServer3D.body_get_state(body, PhysicsServer3D.BODY_STATE_TRANSFORM)
	PhysicsServer3D.free_rid(body)
	_bodies[piece] = RID()
	_state[piece] = State.STILL
	_bodied -= 1
	_moved.erase(piece)


## Gives the stilled lump [param piece] its body back, lying as it lay, and
## puts it into the physics at once: nothing new is in its way. Makes room
## first if the lumps have [constant MOST] bodies already.
func _rebody(piece: int) -> void:
	if _bodied >= MOST:
		_make_room()
	var body := _make_body(piece)
	PhysicsServer3D.body_set_space(body, _space)
	_bodies[piece] = body
	_state[piece] = State.LIVE
	_bodied += 1
	_moved_at[piece] = Engine.get_physics_frames()


## A body for the lump [param piece], lying as [member _poses] says, out of the
## physics.
func _make_body(piece: int) -> RID:
	var body := PhysicsServer3D.body_create()
	PhysicsServer3D.body_set_mode(body, PhysicsServer3D.BODY_MODE_RIGID)
	PhysicsServer3D.body_add_shape(body, _box(_sizes[piece]))
	PhysicsServer3D.body_set_collision_layer(body, TerrainDestruction.DEBRIS_LAYER)
	PhysicsServer3D.body_set_collision_mask(body, TerrainDestruction.DEBRIS_MASK)
	PhysicsServer3D.body_set_param(body, PhysicsServer3D.BODY_PARAM_MASS, _masses[piece])
	PhysicsServer3D.body_set_param(body, PhysicsServer3D.BODY_PARAM_FRICTION, _frictions[piece])
	PhysicsServer3D.body_set_param(body, PhysicsServer3D.BODY_PARAM_BOUNCE, _bounces[piece])
	# Small and quick, they would slip through one another in a step.
	PhysicsServer3D.body_set_enable_continuous_collision_detection(body, true)
	PhysicsServer3D.body_set_state_sync_callback(body, _on_moved.bind(piece))
	PhysicsServer3D.body_set_state(body, PhysicsServer3D.BODY_STATE_TRANSFORM, _poses[piece])
	return body


## Puts a held lump's body into the physics, moving as it was made to.
func _let_go(piece: int) -> void:
	var body := _bodies[piece]
	PhysicsServer3D.body_set_space(body, _space)
	PhysicsServer3D.body_set_state(body, PhysicsServer3D.BODY_STATE_LINEAR_VELOCITY, _velocities[piece])
	PhysicsServer3D.body_set_state(body, PhysicsServer3D.BODY_STATE_ANGULAR_VELOCITY, _spins[piece])
	_state[piece] = State.LIVE


func _remove(piece: int) -> void:
	PhysicsServer3D.free_rid(_bodies[piece])
	_bodies[piece] = RID()
	_state[piece] = State.GONE
	_living -= 1
	_bodied -= 1
	_unfile(piece)
	var multimesh := _chunks[_chunk_of[piece]]
	for voxel in _voxel_count[piece]:
		multimesh.set_instance_transform(_first[piece] + voxel, HIDDEN)


## Every lump not gone whose middle is inside [param box].
func _within(box: AABB) -> PackedInt32Array:
	var found := PackedInt32Array()
	var least := Vector3i(box.position.floor())
	var most := Vector3i(box.end.floor())
	for x in range(least.x, most.x + 1):
		for y in range(least.y, most.y + 1):
			for z in range(least.z, most.z + 1):
				var cell := Vector3i(x, y, z)
				if not _by_cell.has(cell):
					continue
				for piece: int in _by_cell[cell]:
					if box.has_point(_centers[piece]):
						found.append(piece)
	return found


## Files the lump [param piece] under [param cell].
func _file(piece: int, cell: Vector3i) -> void:
	_cells[piece] = cell
	var filed: Array = _by_cell.get_or_add(cell, [])
	filed.append(piece)


## Takes the lump [param piece] out of the cell it is filed under.
func _unfile(piece: int) -> void:
	var cell := _cells[piece]
	var filed: Array = _by_cell.get(cell, [])
	filed.erase(piece)
	if filed.is_empty():
		_by_cell.erase(cell)


## Called by the physics server for each lump that moved in a step.
func _on_moved(state: PhysicsDirectBodyState3D, piece: int) -> void:
	var placed := state.transform
	_centers[piece] = placed.origin
	_moved[piece] = true
	_moved_at[piece] = Engine.get_physics_frames()
	var cell := Vector3i(placed.origin.floor())
	if cell != _cells[piece]:
		_unfile(piece)
		_file(piece, cell)
	var multimesh := _chunks[_chunk_of[piece]]
	var first := _first[piece]
	var start := _offset_start[piece]
	for voxel in _voxel_count[piece]:
		multimesh.set_instance_transform(first + voxel, Transform3D(placed.basis, placed * _offsets[start + voxel]))


## Draws the voxels of [param piece], numbered [param index], where it is made,
## in the first MultiMesh with room for them all.
func _place_voxels(index: int, piece: Piece) -> void:
	var count := piece.voxels.size()
	var chunk := _chunks.size() - 1
	if chunk < 0 or _chunk_used[chunk] + count > CHUNK:
		chunk = _add_chunk()
	var multimesh := _chunks[chunk]
	var first := _chunk_used[chunk]
	for voxel in count:
		multimesh.set_instance_transform(first + voxel, Transform3D(piece.transform.basis, piece.transform * piece.voxels[voxel]))
		multimesh.set_instance_color(first + voxel, piece.colors[voxel])
	_chunk_used[chunk] = first + count
	multimesh.visible_instance_count = first + count
	_chunk_of.append(chunk)
	_first.append(first)
	_voxel_count.append(count)


func _add_chunk() -> int:
	var multimesh := MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.use_colors = true
	multimesh.mesh = _cube
	multimesh.instance_count = CHUNK
	multimesh.visible_instance_count = 0
	var drawn := MultiMeshInstance3D.new()
	drawn.name = &"Voxels"
	drawn.multimesh = multimesh
	drawn.custom_aabb = AABB(-Vector3.ONE * REACH, Vector3.ONE * REACH * 2.0)
	add_child(drawn)
	_chunks.append(multimesh)
	_chunk_used.append(0)
	return _chunks.size() - 1


## A box shape [param size] across, a shade smaller, shared by every lump of
## that size.
func _box(size: Vector3) -> RID:
	var key := Vector3i((size / VOXEL).round())
	if not _boxes.has(key):
		var shape := PhysicsServer3D.box_shape_create()
		PhysicsServer3D.shape_set_data(shape, size * (1.0 - SLACK) * 0.5)
		_boxes[key] = shape
	return _boxes[key]
