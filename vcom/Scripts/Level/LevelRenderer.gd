@tool
## Draws a [VoxelVolume], and gives it collision for debris to land on.
##
## Each chunk is meshed on its own ([ChunkMesher]), and the meshes of the chunks
## in each section - [constant SECTION] chunks a side - are drawn as one, so a
## battlefield is a hundred draw calls rather than five hundred. Every voxel's
## colour lives in one [Texture2DArray], a layer a chunk, which every section's
## material reads (Voxels.gdshader, which draws every voxel model,
## [VoxelModel]); recolouring voxels uploads only their chunks' layers, once a
## frame however many changed.
##
## As voxels wear away, [method refresh] meshes the chunks they were in again,
## and the sections those are in, and their collision: at once, or within a
## budget each frame, the rest the next, as a blast's many chunks are. The
## collision is a trimesh a chunk, on the terrain layer, as exact as what is
## drawn; made only in the game, never in the editor. Making it is most of what
## building a level costs (the physics works each trimesh out as it gets it),
## so a level is drawn at once and given its collision over the frames after,
## a few chunks a frame ([method stream_collision]); anything about to put
## debris somewhere has the chunks round it given theirs first
## ([method ensure_collision]), and a chunk worn away is given its at once.
##
## Pieces can be cut away from the view, to see into buildings ([method cut]):
## the chunks they are in, and those beside them, are meshed again as if those
## pieces' voxels were not there, so what they hid has faces, and those meshes
## are drawn in place of the whole ones. The whole meshes still cast every
## shadow, unseen, so the light is as it was; and the collision is always the
## whole level's.
class_name LevelRenderer
extends Node3D

## Emitted as a chunk is drawn again, and so collides again, as what is left
## of it ([method refresh]): debris lying on what wore away has to fall.
signal chunk_redrawn(key: Vector3i)

## Chunks to a side of a section, as a shift.
const SECTION_SHIFT := 1
const SECTION := 1 << SECTION_SHIFT
## The physics layer debris lands on ([constant TerrainDestruction.TERRAIN_LAYER]).
const TERRAIN_LAYER := 1
## Layers the colour texture keeps spare for chunks made later, in the editor.
const SPARE_LAYERS := 32

## What it draws.
var volume: VoxelVolume
## Whether chunks get collision.
var collides := true
## The material every section is drawn with, and the texture of every voxel's
## colour it reads.
var material: ShaderMaterial
var texture: Texture2DArray

## Each chunk's rectangles and mesh arrays, by key, as last built.
var _quads := {}
var _arrays := {}
## Each section's mesh, by section key, and the sections to build again.
var _sections := {}
var _stale_sections := {}
## Each chunk's collision, by key; the chunks still waiting for theirs, as a
## set; and those whose collision is out of date, worn since it was made, which
## go first.
var _bodies := {}
var _uncollided := {}
var _recollide := {}
var _layers := 0
## How many triangles are drawn, for probes.
var triangles := 0

## The pieces cut away from the view, by their index in the level, as a set
## ([method cut]); empty with nothing cut away.
var _cut := {}
## The rows of each chunk holding voxels of a piece cut away, without them,
## by key: [rows along x, rows along z].
var _cut_rows := {}
## Each chunk drawn otherwise while pieces are cut away, its own voxels cut or
## a neighbour's against it: its rectangles, and its mesh arrays (none for no
## rectangles), as so drawn, by key.
var _cut_quads := {}
var _cut_arrays := {}
## The whole mesh of each section drawn cut away, casting its shadow unseen,
## by section key.
var _shadows := {}


func _init(drawn: VoxelVolume, with_collision := true) -> void:
	name = &"Voxels"
	volume = drawn
	collides = with_collision
	material = ShaderMaterial.new()
	material.shader = VoxelModel.SHADER


## Builds everything afresh: every chunk's mesh, collision and layer of
## colours. Returns how long it took, in microseconds.
func build() -> int:
	var start := Time.get_ticks_usec()
	for section: MeshInstance3D in _sections.values():
		section.queue_free()
	_sections.clear()
	for body: StaticBody3D in _bodies.values():
		body.queue_free()
	_bodies.clear()
	for shadow: MeshInstance3D in _shadows.values():
		shadow.queue_free()
	_shadows.clear()
	_cut.clear()
	_cut_rows.clear()
	_cut_quads.clear()
	_cut_arrays.clear()
	_quads.clear()
	_arrays.clear()
	_uncollided.clear()
	_recollide.clear()
	_make_texture()
	set_palette()
	for key: Vector3i in volume.chunks:
		if collides:
			_uncollided[key] = true
		_mesh_chunk(key)
	for key: Vector3i in _stale_sections.keys():
		_build_section(key)
	_stale_sections.clear()
	volume.dirty.clear()
	volume.dirty_colors.clear()
	return Time.get_ticks_usec() - start


## Hands the volume's palette to the material: each place's colour, its flags
## in the alpha.
func set_palette() -> void:
	material.set_shader_parameter(&"palette", palette_of(volume))
	material.set_shader_parameter(&"box_size", Vector3i.ONE * VoxelVolume.SIZE)


## [param of]'s palette as the shader takes it: each place's colour, and its
## flags ([method VoxelModel.palette_entries]).
static func palette_of(of: VoxelVolume) -> PackedVector4Array:
	return VoxelModel.palette_entries(of.palette, of.flags)


## Draws again what has changed in the volume since it was last drawn: chunks
## whose voxels changed are meshed again, with their sections and collision,
## for up to [param budget] microseconds, the rest left for the next call, or
## all of them with a budget below 0; chunks whose colours changed have their
## layers uploaded, all of them. Returns whether anything is left to do.
func refresh(budget := -1) -> bool:
	var start := Time.get_ticks_usec()
	# What wear has laid bare takes its colours before anything is drawn.
	volume.flush_bare()
	if not volume.dirty_colors.is_empty():
		for key: Vector3i in volume.dirty_colors:
			_upload(key)
		volume.dirty_colors.clear()
	if volume.dirty.is_empty():
		return false
	# Every chunk changed loses what it holds of the pieces cut away before any
	# is meshed: a chunk's faces against its neighbour read the neighbour's
	# rows as drawn.
	if not _cut.is_empty():
		for key: Vector3i in volume.dirty:
			_cut_chunk(key)
	var redrawn: Array[Vector3i] = []
	for key: Vector3i in volume.dirty.keys():
		volume.dirty.erase(key)
		if volume.chunks.has(key):
			_mesh_chunk(key)
			if not _cut.is_empty():
				_mesh_cut(key)
			redrawn.append(key)
		elif _quads.has(key):
			_forget(key)
		if budget >= 0 and Time.get_ticks_usec() - start > budget:
			break
	for key: Vector3i in _stale_sections.keys():
		_build_section(key)
	_stale_sections.clear()
	for key in redrawn:
		chunk_redrawn.emit(key)
	return not volume.dirty.is_empty()


## Whether a chunk is waiting to be drawn again.
func is_stale() -> bool:
	return not volume.dirty.is_empty()


## Draws the level with [param pieces], a set of their indices in the level,
## cut away, so as to see past them ([LevelCutaway]); with none, whole again.
## The chunks they are in are meshed again without them, and the chunks beside
## those, whose faces against them now show; the chunks cut away before and
## not now are drawn whole again. Their sections draw what is left, and the
## whole level casts the shadows, unseen. Returns how long it took, in
## microseconds.
func cut(pieces: Dictionary) -> int:
	var start := Time.get_ticks_usec()
	var redraw := {}
	for key: Vector3i in _cut_quads:
		redraw[key] = true
	_cut = pieces.duplicate()
	_cut_rows.clear()
	var reached := {}
	for piece: int in _cut:
		for key in VoxelVolume.keys_of(volume.data.slot_at(piece)):
			reached[key] = true
	for key: Vector3i in reached:
		_cut_chunk(key)
	for key: Vector3i in _cut_rows:
		redraw[key] = true
		for step in VoxelVolume.STEPS:
			redraw[key + step] = true
	for key: Vector3i in redraw:
		_mesh_cut(key)
	for key: Vector3i in _stale_sections.keys():
		_build_section(key)
	_stale_sections.clear()
	return Time.get_ticks_usec() - start


## Works out the rows of the chunk keyed [param key] without the voxels of the
## pieces cut away, into [member _cut_rows], or forgets them if it holds none.
## Only the voxels each such piece still owns are taken out, a row of bits at a
## time across its box: a later piece's voxels over it stay.
func _cut_chunk(key: Vector3i) -> void:
	_cut_rows.erase(key)
	var chunk: VoxelVolume.Chunk = volume.chunks.get(key)
	if chunk == null:
		return
	var size := VoxelVolume.SIZE
	var block := VoxelVolume.BLOCK
	var rows_x := PackedInt64Array()
	var rows_z := PackedInt64Array()
	for at in chunk.owners.size():
		var piece := chunk.owners[at]
		if not _cut.has(piece):
			continue
		var slot_number := at + 1
		var least := LevelData.voxel_origin(volume.data.slot_at(piece)) - chunk.origin
		var x_from := maxi(least.x, 0)
		var x_to := mini(least.x + block, size)
		if x_from >= x_to:
			continue
		var x_bits := ((1 << (x_to - x_from)) - 1) << x_from
		for y in range(maxi(least.y, 0), mini(least.y + block, size)):
			for z in range(maxi(least.z, 0), mini(least.z + block, size)):
				var row := z + y * size
				var bits := chunk.rows_x[row] & x_bits
				while bits != 0:
					var low := bits & -bits
					bits &= bits - 1
					var x: int = ChunkMesher.BIT[low % 67]
					if chunk.slots[x + row * size] != slot_number:
						continue
					if rows_x.is_empty():
						rows_x = chunk.rows_x.duplicate()
						rows_z = chunk.rows_z.duplicate()
					rows_x[row] &= ~low
					rows_z[x + y * size] &= ~(1 << z)
	if not rows_x.is_empty():
		_cut_rows[key] = [rows_x, rows_z]


## Meshes the chunk keyed [param key] as it is drawn with the pieces cut away,
## if it is drawn otherwise so - its own voxels cut, or a neighbour's against
## it - and marks its section to be built again; else forgets how it was.
func _mesh_cut(key: Vector3i) -> void:
	var chunk: VoxelVolume.Chunk = volume.chunks.get(key)
	var affected := chunk != null and _cut_rows.has(key)
	if chunk != null and not affected:
		for step in VoxelVolume.STEPS:
			if _cut_rows.has(key + step):
				affected = true
				break
	if not affected:
		if _cut_quads.erase(key):
			_cut_arrays.erase(key)
			_stale_sections[_section_of(key)] = true
		return
	var near := ChunkMesher.Near.new()
	near.east = _shown_rows(key + Vector3i.RIGHT, false)
	near.west = _shown_rows(key + Vector3i.LEFT, false)
	near.up = _shown_rows(key + Vector3i.UP, true)
	near.down = _shown_rows(key + Vector3i.DOWN, true)
	near.north = _shown_rows(key + Vector3i.BACK, true)
	near.south = _shown_rows(key + Vector3i.FORWARD, true)
	var floor_slice := volume.floor_y - chunk.origin.y
	var quads := ChunkMesher.rectangles(
		VoxelVolume.SIZE, _shown_rows(key, true), _shown_rows(key, false), near, floor_slice
	)
	_cut_quads[key] = quads
	if quads.is_empty():
		_cut_arrays.erase(key)
	else:
		_cut_arrays[key] = ChunkMesher.arrays(quads, chunk.origin, chunk.layer, 1.0 / VoxelVolume.BLOCK)
	_stale_sections[_section_of(key)] = true


## The rows of the chunk keyed [param key] as they are drawn, without the
## pieces cut away, along x if [param along_x] else along z; empty if there is
## no chunk there.
func _shown_rows(key: Vector3i, along_x: bool) -> PackedInt64Array:
	var rows: Array = _cut_rows.get(key, [])
	if rows.is_empty():
		return _rows(key, along_x)
	return rows[0] if along_x else rows[1]


## Makes the texture of every voxel's colour, a layer for each chunk, and gives
## each chunk its layer.
func _make_texture() -> void:
	var images: Array[Image] = []
	var layer := 0
	for key: Vector3i in volume.chunks:
		var chunk: VoxelVolume.Chunk = volume.chunks[key]
		chunk.layer = layer
		images.append(_image_of(chunk))
		layer += 1
	_layers = layer + (SPARE_LAYERS if Engine.is_editor_hint() else 0)
	var empty := Image.create(VoxelVolume.SIZE, VoxelVolume.AREA, false, Image.FORMAT_R8)
	while images.size() < maxi(_layers, 1):
		images.append(empty)
	texture = Texture2DArray.new()
	texture.create_from_images(images)
	material.set_shader_parameter(&"voxels", texture)


## The image of [param chunk]'s colours, as its layer holds them.
static func _image_of(chunk: VoxelVolume.Chunk) -> Image:
	return Image.create_from_data(VoxelVolume.SIZE, VoxelVolume.AREA, false, Image.FORMAT_R8, chunk.colors)


## Uploads the colours of the chunk keyed [param key] to its layer, making the
## texture afresh if it is a chunk new since the texture was made and there is
## no spare layer for it.
func _upload(key: Vector3i) -> void:
	var chunk: VoxelVolume.Chunk = volume.chunks.get(key)
	if chunk == null:
		return
	if chunk.layer < 0:
		var used := 0
		for each: VoxelVolume.Chunk in volume.chunks.values():
			used = maxi(used, each.layer + 1)
		if used >= _layers:
			_make_texture()
			for other in volume.chunks:
				_stale_sections[_section_of(other)] = true
			return
		chunk.layer = used
	texture.update_layer(_image_of(chunk), chunk.layer)


## Meshes the chunk keyed [param key] again, with its collision, and marks its
## section to be built again.
func _mesh_chunk(key: Vector3i) -> void:
	var chunk: VoxelVolume.Chunk = volume.chunks[key]
	if chunk.layer < 0:
		_upload(key)
	var near := ChunkMesher.Near.new()
	near.east = _rows(key + Vector3i.RIGHT, false)
	near.west = _rows(key + Vector3i.LEFT, false)
	near.up = _rows(key + Vector3i.UP, true)
	near.down = _rows(key + Vector3i.DOWN, true)
	near.north = _rows(key + Vector3i.BACK, true)
	near.south = _rows(key + Vector3i.FORWARD, true)
	var floor_slice := volume.floor_y - chunk.origin.y
	var quads := ChunkMesher.rectangles(VoxelVolume.SIZE, chunk.rows_x, chunk.rows_z, near, floor_slice)
	_quads[key] = quads
	if quads.is_empty():
		_arrays.erase(key)
	else:
		_arrays[key] = ChunkMesher.arrays(quads, chunk.origin, chunk.layer, 1.0 / VoxelVolume.BLOCK)
	_stale_sections[_section_of(key)] = true
	# The collision is made again ahead of the next physics step
	# (VoxelLevel._physics_process), not here: it is the dearest part of drawing
	# a chunk again, and what wear breaks off is held still until that step.
	if collides and not _uncollided.has(key):
		_recollide[key] = true


## Gives collision to chunks still waiting for it, for up to [param budget]
## microseconds: first those worn since theirs was made, then, unless
## [param worn_only], those that never had any. Returns whether any are still
## waiting.
func stream_collision(budget: int, worn_only := false) -> bool:
	var start := Time.get_ticks_usec()
	var waiting_for: Array[Dictionary] = [_recollide]
	if not worn_only:
		waiting_for.append(_uncollided)
	for waiting in waiting_for:
		for key: Vector3i in waiting.keys():
			waiting.erase(key)
			_collide(key)
			if Time.get_ticks_usec() - start > budget:
				return not is_collided()
	return not is_collided()


## Whether a chunk worn since its collision was made is still waiting for it
## again.
func has_worn_collision() -> bool:
	return not _recollide.is_empty()


## Gives collision now to every chunk waiting for it that the box of voxels
## from [param least] to [param most] reaches, and to those beside them, for
## whatever is about to be broken off there to land on.
func ensure_collision(least: Vector3i, most: Vector3i) -> void:
	if _uncollided.is_empty() and _recollide.is_empty():
		return
	var from := Vector3i(least.x >> VoxelVolume.SHIFT, least.y >> VoxelVolume.SHIFT, least.z >> VoxelVolume.SHIFT) - Vector3i.ONE
	var to := Vector3i(most.x >> VoxelVolume.SHIFT, most.y >> VoxelVolume.SHIFT, most.z >> VoxelVolume.SHIFT) + Vector3i.ONE
	for x in range(from.x, to.x + 1):
		for y in range(from.y, to.y + 1):
			for z in range(from.z, to.z + 1):
				var key := Vector3i(x, y, z)
				if _uncollided.has(key) or _recollide.has(key):
					_uncollided.erase(key)
					_recollide.erase(key)
					_collide(key)


## Whether every chunk has its collision, as it is drawn now.
func is_collided() -> bool:
	return _uncollided.is_empty() and _recollide.is_empty()


## Takes away what was drawn of the chunk keyed [param key], which is gone:
## the level editor erased the last of its voxels.
func _forget(key: Vector3i) -> void:
	_quads.erase(key)
	_arrays.erase(key)
	_cut_rows.erase(key)
	_cut_quads.erase(key)
	_cut_arrays.erase(key)
	_uncollided.erase(key)
	_recollide.erase(key)
	_stale_sections[_section_of(key)] = true
	var body: StaticBody3D = _bodies.get(key)
	if body != null:
		body.queue_free()
		_bodies.erase(key)


## The rows of the chunk keyed [param key], along x if [param along_x] else
## along z; empty if there is no chunk there.
func _rows(key: Vector3i, along_x: bool) -> PackedInt64Array:
	var chunk: VoxelVolume.Chunk = volume.chunks.get(key)
	if chunk == null:
		return PackedInt64Array()
	return chunk.rows_x if along_x else chunk.rows_z


static func _section_of(key: Vector3i) -> Vector3i:
	return Vector3i(key.x >> SECTION_SHIFT, key.y >> SECTION_SHIFT, key.z >> SECTION_SHIFT)


## Builds the mesh of the section keyed [param key] afresh from its chunks':
## as they are drawn, with any pieces cut away, and then, if any chunk of it is
## drawn cut away, its whole mesh as well, casting the shadow in its place.
func _build_section(key: Vector3i) -> void:
	var cut := false
	var first := key * SECTION
	for x in SECTION:
		for y in SECTION:
			for z in SECTION:
				if _cut_quads.has(first + Vector3i(x, y, z)):
					cut = true
	var drawn: MeshInstance3D = _sections.get(key)
	var old_quads := 0
	if drawn != null and drawn.mesh != null:
		old_quads = drawn.get_meta(&"quads", 0)
	var made := _section_mesh(key, cut)
	var quads: int = made[1]
	triangles += (quads - old_quads) * 2
	if quads == 0:
		if drawn != null:
			drawn.queue_free()
			_sections.erase(key)
	else:
		if drawn == null:
			drawn = MeshInstance3D.new()
			drawn.name = &"Section"
			add_child(drawn)
			_sections[key] = drawn
		drawn.mesh = made[0]
		drawn.set_meta(&"quads", quads)
		drawn.cast_shadow = (
			GeometryInstance3D.SHADOW_CASTING_SETTING_OFF if cut else GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		)
	var shadow: MeshInstance3D = _shadows.get(key)
	var whole: Mesh = _section_mesh(key, false)[0] if cut else null
	if whole == null:
		if shadow != null:
			shadow.queue_free()
			_shadows.erase(key)
		return
	if shadow == null:
		shadow = MeshInstance3D.new()
		shadow.name = &"Shadow"
		shadow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
		add_child(shadow)
		_shadows[key] = shadow
	shadow.mesh = whole


## The mesh of the section keyed [param key], from its chunks as drawn with the
## pieces cut away if [param cut], else whole, and how many rectangles it has:
## [mesh, rectangles], the mesh null for none.
func _section_mesh(key: Vector3i, cut: bool) -> Array:
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var custom0 := PackedFloat32Array()
	var custom1 := PackedFloat32Array()
	var quads := 0
	var first := key * SECTION
	for x in SECTION:
		for y in SECTION:
			for z in SECTION:
				var chunk_key := first + Vector3i(x, y, z)
				var is_cut := cut and _cut_quads.has(chunk_key)
				var made: Variant = (_cut_arrays if is_cut else _arrays).get(chunk_key)
				if made == null:
					continue
				vertices.append_array(made[Mesh.ARRAY_VERTEX])
				normals.append_array(made[Mesh.ARRAY_NORMAL])
				custom0.append_array(made[Mesh.ARRAY_CUSTOM0])
				custom1.append_array(made[Mesh.ARRAY_CUSTOM1])
				@warning_ignore("integer_division")
				quads += ((_cut_quads if is_cut else _quads)[chunk_key] as PackedInt32Array).size() / ChunkMesher.FIELDS
	if quads == 0:
		return [null, 0]
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_CUSTOM0] = custom0
	arrays[Mesh.ARRAY_CUSTOM1] = custom1
	arrays[Mesh.ARRAY_INDEX] = ChunkMesher.index_array(quads)
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, [], {}, ChunkMesher.format())
	mesh.surface_set_material(0, material)
	return [mesh, quads]


## Gives the chunk keyed [param key] collision as its faces are now: a trimesh
## of the same rectangles it is drawn with.
func _collide(key: Vector3i) -> void:
	var made: Variant = _arrays.get(key)
	var body: StaticBody3D = _bodies.get(key)
	if made == null:
		if body != null:
			body.queue_free()
			_bodies.erase(key)
		return
	@warning_ignore("integer_division")
	var quads := (_quads[key] as PackedInt32Array).size() / ChunkMesher.FIELDS
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = made[Mesh.ARRAY_VERTEX]
	arrays[Mesh.ARRAY_INDEX] = ChunkMesher.index_array(quads)
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var shape := mesh.create_trimesh_shape()
	if body == null:
		body = StaticBody3D.new()
		body.name = &"Collision"
		body.collision_layer = TERRAIN_LAYER
		body.collision_mask = 0
		var collider := CollisionShape3D.new()
		body.add_child(collider)
		add_child(body)
		_bodies[key] = body
	(body.get_child(0) as CollisionShape3D).shape = shape


## How many sections are drawn, for probes.
func section_count() -> int:
	return _sections.size()


## How many chunks are drawn cut away, and how many sections cast their shadow
## from a whole mesh drawn unseen, for probes.
func cut_counts() -> Vector2i:
	return Vector2i(_cut_quads.size(), _shadows.size())
