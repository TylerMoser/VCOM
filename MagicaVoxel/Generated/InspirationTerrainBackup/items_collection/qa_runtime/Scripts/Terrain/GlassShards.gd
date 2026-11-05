## Broken glass. Every pane that shatters ([method VoxelTerrain.shatter]) flies
## apart as shards, thin plates of glass, drawn see-through as the pane was
## (GlassShard.gdshader), that tumble, fall and lie where they land for the rest
## of the battle, as the lumps of [VoxelDebris] do.
##
## Only for show, and lean: a shard is no physics body and has no node of its
## own, but is an instance of a few MultiMeshes, moved by this node while it
## falls and never again once it lies still, so a floor strewn with glass costs
## nothing a frame. A shard lands on the first voxel under it
## ([member floor_under]), looked for again each time it falls into a new
## column of voxels, bouncing once or twice and coming to rest lying flat;
## if what it lies on goes, it falls again ([method wake]). Past
## [constant MOST] shards, the oldest is taken up to make each new one, lying
## still long since. One that falls off the map ([member lowest]) is gone.
##
## A shard over something cut away from the view ([Cutaway]) is not drawn while
## it is ([member hides]), as a lump of debris is not: looked at every frame it
## falls and as it lands, and every shard lying still as the view is cut again
## ([method rehide]).
##
## Where it goes, how it turns and how big it is draw on a generator of its own,
## never the global one, which the rules draw on.
class_name GlassShards
extends Node3D

const SHARD_SHADER := preload("res://Scripts/Terrain/GlassShard.gdshader")
const SHINE_SHADER := preload("res://Scripts/Terrain/GlassShardShine.gdshader")
## How big a voxel is, in cells.
const VOXEL := VoxelShape.SCALE
## How many shards each MultiMesh draws, as a power of two, and the most there
## are at once.
const CHUNK_SHIFT := 10
const CHUNK := 1 << CHUNK_SHIFT
const CHUNK_MASK := CHUNK - 1
const MOST := 8192
## About one shard for every so many voxels of glass broken; each between
## these many voxels across, and this thick.
const VOXELS_PER_SHARD := 3.0
const SIZE_MIN := 0.6
const SIZE_MAX := 1.7
const THICKNESS := 0.25
## How much a shard scatters about the way it is sent, in cells a second, and
## how fast it tumbles, in radians a second.
const SCATTER := 0.8
const SPIN_MIN := 6.0
const SPIN_MAX := 18.0
## How much of its speed a shard keeps bouncing off the floor, up and across,
## and how slowly it must be falling, in cells a second, to lie still instead.
const BOUNCE := 0.3
const SLIDE := 0.4
const REST_SPEED := 0.7
## Where a shard no longer drawn is put: shrunk to nothing.
const HIDDEN := Transform3D(Basis(Vector3.ZERO, Vector3.ZERO, Vector3.ZERO), Vector3.ZERO)
## How far the shards can be from the map's origin and still be drawn, in
## cells: the MultiMeshes are never culled.
const REACH := 1000.0

## What a shard is: not there; falling; lying still.
enum State { FREE, FALLING, LYING }

## How high the floor is under a point in the world: the top of the first voxel
## below it, in the world's y, or -INF if there is none. Unset, shards fall
## for ever, until [member lowest].
var floor_under: Callable
## Below this, in the world's y, a falling shard is gone.
var lowest := -INF
## Whether a shard with its middle at a point in the world is hidden, cut away
## from the view with what it lies on; asked only of shards at or above
## [member hide_above], in the world's y. Unset, nothing is hidden ([Cutaway]).
var hides: Callable
var hide_above := INF

var _mesh: BoxMesh
var _material: ShaderMaterial
var _chunks: Array[MultiMesh] = []
## Each shard, by number: its state; where its middle is; how fast it moves,
## the axis it turns about and how fast; how it is turned, as a quaternion; its
## size, across, across and through; its colour and clarity; the floor under
## it; whether it is hidden, cut away from the view; and the cell it is filed
## under while it lies still.
var _state := PackedByteArray()
var _positions := PackedVector3Array()
var _velocities := PackedVector3Array()
var _spins := PackedVector3Array()
var _spin_speeds := PackedFloat32Array()
var _turns := PackedVector4Array()
var _sizes := PackedVector3Array()
var _colors := PackedColorArray()
var _clarities := PackedFloat32Array()
var _floors := PackedFloat32Array()
var _cut := PackedByteArray()
var _cells: Array[Vector3i] = []
## The column of voxels (x and z, a sixteenth of a cell each, in the world)
## each falling shard's floor was last looked for under.
var _columns: Array[Vector2i] = []
## The shards falling, as a set; the shards lying still, filed by the cell
## (a cell a unit across, in the world) they lie in; where the next shard goes,
## and how many have been made in all.
var _falling := {}
var _by_cell := {}
var _next := 0
var _made := 0
var _gravity := 9.8
var _show := RandomNumberGenerator.new()


func _init() -> void:
	name = &"GlassShards"
	_show.randomize()
	_gravity = float(ProjectSettings.get_setting("physics/3d/default_gravity", 9.8))
	_mesh = BoxMesh.new()
	_mesh.size = Vector3.ONE
	_material = ShaderMaterial.new()
	_material.shader = SHARD_SHADER
	var shine := ShaderMaterial.new()
	shine.shader = SHINE_SHADER
	shine.render_priority = VoxelModel.SHINE_PRIORITY
	_material.next_pass = shine


## How many shards there are, falling or lying still.
func count() -> int:
	return _falling.size() + _lying_count()


## How many shards lie still.
func _lying_count() -> int:
	var total := 0
	for cell: Vector3i in _by_cell:
		total += (_by_cell[cell] as PackedInt32Array).size()
	return total


## How many are falling.
func falling_count() -> int:
	return _falling.size()


## Breaks the glass voxels whose middles, in the world, are [param points]
## into shards: about one for every [constant VOXELS_PER_SHARD] of them, each
## made where one of them was, in its colour ([param colors], sRGB) and as
## clear as it was ([param clarities], 0 to 1), setting off as [param motion]
## says: called with a shard's middle, in the world, it gives its speed, in
## cells a second, before its scatter.
func burst(points: PackedVector3Array, colors: PackedColorArray, clarities: PackedFloat32Array, motion: Callable) -> void:
	if points.is_empty():
		return
	var shards := maxi(1, ceili(points.size() / VOXELS_PER_SHARD))
	# Which voxels they come from: each once, at random, as far as they go.
	var order := PackedInt32Array()
	order.resize(points.size())
	for at in points.size():
		order[at] = at
	for at in range(points.size() - 1, 0, -1):
		var other := _show.randi_range(0, at)
		var swap := order[at]
		order[at] = order[other]
		order[other] = swap
	for made in shards:
		var from := order[made % order.size()]
		var at := points[from] + Vector3(_show.randf_range(-0.5, 0.5), _show.randf_range(-0.5, 0.5), _show.randf_range(-0.5, 0.5)) * VOXEL
		var velocity: Vector3 = motion.call(at) if motion.is_valid() else Vector3.ZERO
		_add(at, velocity + _random_in_ball() * SCATTER, colors[from], clarities[from])


## Lets every shard lying still within [param box], in the world, fall again if
## what it lay on has gone: called as the level under it is drawn again.
func wake(box: AABB) -> void:
	if _by_cell.is_empty():
		return
	var least := Vector3i(box.position.floor())
	var most := Vector3i(box.end.floor())
	for x in range(least.x, most.x + 1):
		for y in range(least.y, most.y + 1):
			for z in range(least.z, most.z + 1):
				var cell := Vector3i(x, y, z)
				if not _by_cell.has(cell):
					continue
				for shard in (_by_cell[cell] as PackedInt32Array).duplicate():
					if not box.has_point(_positions[shard]):
						continue
					var under := _floor_at(_positions[shard])
					if under < _floors[shard] - 0.001:
						_floors[shard] = under
						_columns[shard] = Vector2i(floori(_positions[shard].x / VOXEL), floori(_positions[shard].z / VOXEL))
						_unfile(shard)
						_state[shard] = State.FALLING
						_velocities[shard] = Vector3.ZERO
						_falling[shard] = true


## Hides, or shows again, every shard lying still by whether it is over
## something cut away from the view ([member hides]): as the view is cut again.
func rehide() -> void:
	for cell: Vector3i in _by_cell:
		for shard in _by_cell[cell] as PackedInt32Array:
			_hide(shard)


func _process(delta: float) -> void:
	if _falling.is_empty():
		return
	# The arrays themselves, not copies: a packed array is shared.
	var positions := _positions
	var velocities := _velocities
	var axes := _spins
	var speeds := _spin_speeds
	var turns := _turns
	var sizes := _sizes
	var floors := _floors
	var columns := _columns
	var cut := _cut
	var fall := _gravity * delta
	var across := 1.0 / VOXEL
	for shard: int in _falling.keys():
		var velocity := velocities[shard]
		velocity.y -= fall
		var at := positions[shard] + velocity * delta
		var held := turns[shard]
		var turn := Quaternion(held.x, held.y, held.z, held.w)
		var speed := speeds[shard]
		if speed > 0.0:
			turn = (Quaternion(axes[shard], speed * delta) * turn).normalized()
		# Into a new column, the floor under it is looked for afresh, from where
		# it is now; one with something solid where it would go is a wall, which
		# stops it going across, and it falls on down where it was.
		var column := Vector2i(floori(at.x * across), floori(at.z * across))
		if column != columns[shard]:
			var under := _floor_at(at + Vector3.UP * VOXEL)
			if under > at.y:
				at.x = positions[shard].x
				at.z = positions[shard].z
				velocity.x = 0.0
				velocity.z = 0.0
			else:
				columns[shard] = column
				floors[shard] = under
		var size := sizes[shard]
		var resting := floors[shard] + size.z * 0.5
		if at.y <= resting:
			at.y = resting
			if -velocity.y > REST_SPEED:
				velocity = Vector3(velocity.x * SLIDE, -velocity.y * BOUNCE, velocity.z * SLIDE)
				speeds[shard] = speed * 0.5
			else:
				positions[shard] = at
				_lie(shard)
				continue
		elif at.y < lowest:
			_remove(shard)
			continue
		positions[shard] = at
		velocities[shard] = velocity
		turns[shard] = Vector4(turn.x, turn.y, turn.z, turn.w)
		# Hidden as it falls over something cut away from the view, as it is
		# lying there; only asked at the cut's height or above.
		var hidden := at.y >= hide_above and hides.is_valid() and bool(hides.call(at))
		cut[shard] = 1 if hidden else 0
		_chunks[shard >> CHUNK_SHIFT].set_instance_transform(
			shard & CHUNK_MASK, HIDDEN if hidden else Transform3D(Basis(turn).scaled_local(size), at)
		)


## Makes a shard at [param at], in the world, moving at [param velocity], of
## [param color] and [param clarity]: in the next free place, or the oldest
## shard's past [constant MOST].
func _add(at: Vector3, velocity: Vector3, color: Color, clarity: float) -> void:
	var shard := _next
	_next = (_next + 1) % MOST
	if shard >= _state.size():
		_grow(shard + 1)
	elif _state[shard] != State.FREE:
		_remove(shard)
	_made += 1
	var across := _show.randf_range(SIZE_MIN, SIZE_MAX) * VOXEL
	var along := _show.randf_range(SIZE_MIN, SIZE_MAX) * VOXEL
	_sizes[shard] = Vector3(across, along, THICKNESS * VOXEL)
	var turn := Quaternion.from_euler(Vector3(_show.randf_range(-PI, PI), _show.randf_range(-PI, PI), _show.randf_range(-PI, PI)))
	_turns[shard] = Vector4(turn.x, turn.y, turn.z, turn.w)
	var axis := _random_in_ball()
	if axis.is_zero_approx():
		axis = Vector3.UP
	_spins[shard] = axis.normalized()
	_spin_speeds[shard] = _show.randf_range(SPIN_MIN, SPIN_MAX)
	_positions[shard] = at
	_velocities[shard] = velocity
	_colors[shard] = color
	_clarities[shard] = clarity
	_floors[shard] = _floor_at(at)
	_columns[shard] = Vector2i(floori(at.x / VOXEL), floori(at.z / VOXEL))
	_cut[shard] = 0
	_state[shard] = State.FALLING
	_falling[shard] = true
	var multimesh := _chunks[shard >> CHUNK_SHIFT]
	multimesh.set_instance_color(shard & CHUNK_MASK, color)
	multimesh.set_instance_custom_data(shard & CHUNK_MASK, Color(clarity, 0.0, 0.0, 0.0))
	_draw(shard)


## Lays [param shard] down where it is, flat on the floor at a turn of its
## own, and files it among those lying still.
func _lie(shard: int) -> void:
	_falling.erase(shard)
	_state[shard] = State.LYING
	_velocities[shard] = Vector3.ZERO
	_spin_speeds[shard] = 0.0
	var at := _positions[shard]
	at.y = _floors[shard] + _sizes[shard].z * 0.5
	_positions[shard] = at
	# Its thin side, its own z, up.
	var flat := Quaternion(Vector3.UP, _show.randf_range(-PI, PI)) * Quaternion(Vector3.RIGHT, -PI * 0.5)
	_turns[shard] = Vector4(flat.x, flat.y, flat.z, flat.w)
	var cell := Vector3i(at.floor())
	_cells[shard] = cell
	var filed: PackedInt32Array = _by_cell.get(cell, PackedInt32Array())
	filed.append(shard)
	_by_cell[cell] = filed
	_hide(shard)
	_draw(shard)


## Takes [param shard] away.
func _remove(shard: int) -> void:
	if _state[shard] == State.LYING:
		_unfile(shard)
	_falling.erase(shard)
	_state[shard] = State.FREE
	_chunks[shard >> CHUNK_SHIFT].set_instance_transform(shard & CHUNK_MASK, HIDDEN)


## Takes [param shard] out of the file of those lying still.
func _unfile(shard: int) -> void:
	var cell := _cells[shard]
	var filed: PackedInt32Array = _by_cell.get(cell, PackedInt32Array())
	var at := filed.find(shard)
	if at >= 0:
		filed.remove_at(at)
	if filed.is_empty():
		_by_cell.erase(cell)
	else:
		_by_cell[cell] = filed


## Whether [param shard], lying still, is hidden with what is cut away, and so
## drawn so.
func _hide(shard: int) -> void:
	var at := _positions[shard]
	var hidden := hides.is_valid() and at.y >= hide_above and bool(hides.call(at))
	if hidden != (_cut[shard] != 0):
		_cut[shard] = 1 if hidden else 0
		_draw(shard)


## Draws [param shard] where it is, as it is turned, or not at all if it is
## hidden or gone.
func _draw(shard: int) -> void:
	var multimesh := _chunks[shard >> CHUNK_SHIFT]
	if _state[shard] == State.FREE or _cut[shard] != 0:
		multimesh.set_instance_transform(shard & CHUNK_MASK, HIDDEN)
		return
	multimesh.set_instance_transform(shard & CHUNK_MASK, Transform3D(Basis(_quaternion(shard)).scaled_local(_sizes[shard]), _positions[shard]))


func _quaternion(shard: int) -> Quaternion:
	var turn := _turns[shard]
	return Quaternion(turn.x, turn.y, turn.z, turn.w)


## The floor under [param at], in the world: [member floor_under]'s, or none.
func _floor_at(at: Vector3) -> float:
	if floor_under.is_valid():
		return float(floor_under.call(at))
	return -INF


## Makes room for [param needed] shards, a MultiMesh of [constant CHUNK] at a
## time.
func _grow(needed: int) -> void:
	while _state.size() < needed:
		var multimesh := MultiMesh.new()
		multimesh.transform_format = MultiMesh.TRANSFORM_3D
		multimesh.use_colors = true
		multimesh.use_custom_data = true
		multimesh.mesh = _mesh
		multimesh.instance_count = CHUNK
		for at in CHUNK:
			multimesh.set_instance_transform(at, HIDDEN)
		_chunks.append(multimesh)
		var drawn := MultiMeshInstance3D.new()
		drawn.multimesh = multimesh
		drawn.material_override = _material
		drawn.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		drawn.custom_aabb = AABB(-Vector3.ONE * REACH, Vector3.ONE * REACH * 2.0)
		add_child(drawn)
		var size := _state.size() + CHUNK
		_state.resize(size)
		_positions.resize(size)
		_velocities.resize(size)
		_spins.resize(size)
		_spin_speeds.resize(size)
		_turns.resize(size)
		_sizes.resize(size)
		_colors.resize(size)
		_clarities.resize(size)
		_floors.resize(size)
		_cut.resize(size)
		_cells.resize(size)
		_columns.resize(size)


## A point picked evenly from inside a ball one across.
func _random_in_ball() -> Vector3:
	var point := Vector3(_show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0))
	while point.length_squared() > 1.0:
		point = Vector3(_show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0))
	return point
