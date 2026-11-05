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
##
## Glass is meshed apart ([method ChunkMesher.faces]) and drawn as a second
## surface of its section's mesh, named [constant VoxelModel.GLASS_SURFACE],
## by [member glass_material]: see-through, casting no shadow. It collides as
## the rest does, for debris to lie on until it shatters (Docs/GLASS.md).
##
## The voxels that cast no shadow from a lamp's light (a lamp's bulb, and the
## frame right beside it: [member VoxelVolume.Chunk.shadowless_x]) are meshed
## apart too, and drawn as a third surface, named [constant SHADOWLESS_SURFACE],
## by [member shadowless_material]: the voxel shader as ever, but left out of
## the shadow maps of lamps' lights, though not the sun's (Docs/LIGHTS.md).
## They collide as the rest does.
##
## An area light draws its shadow map in one paraboloid, warping each corner of
## a face, not the face between them: a big face near the light lands in the
## wrong place in the map, and light leaks past walls. So while a battle's
## lamps are area lights ([method use_fine_shadows]), each section within their
## reach has a copy of its faces cut into small pieces, finer the nearer a
## light, drawn only into those lights' shadow maps, on a layer of its own
## ([constant FINE_LAYER]); and the sections, on another ([constant
## SECTION_LAYER]), are left out of them. The sun's and an omni light's
## shadows stay the sections'.
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
## The name of a section's surface of voxels casting no lamp's shadow.
const SHADOWLESS_SURFACE := "shadowless"
## The visual layer every section is drawn on while area lights take their
## shadows from the fine copies ([method use_fine_shadows]), so they can leave
## the sections out: layer 19. Layer 1, as everything else, otherwise.
const SECTION_LAYER := 1 << 18
## The visual layer of the fine copies, which only area lights' shadow maps
## draw: layer 20.
const FINE_LAYER := 1 << 19
## How finely a fine copy is cut: the longest side of its pieces, in voxels, by
## how far the face is from the nearest area light, in cells:
## [code][nearer than, longest side][/code], nearest first; further, its pieces
## are [constant FINE_FURTHEST] long. Small enough that no corner of a piece is
## more than a centimetre or so from where the paraboloid puts it.
const FINE_STEPS := [[1.0, 2], [2.0, 4], [4.5, 8]]
const FINE_FURTHEST := 16

## What it draws.
var volume: VoxelVolume
## Whether chunks get collision.
var collides := true
## The material every section is drawn with, and the texture of every voxel's
## colour it reads; the material its glass is drawn with, which reads the
## same, its shine its next pass ([method VoxelModel.glass_material]); and the
## one its voxels casting no lamp's shadow are, the first's but for that.
var material: ShaderMaterial
var glass_material: ShaderMaterial
var shadowless_material: ShaderMaterial
var texture: Texture2DArray

## Each chunk's rectangles and mesh arrays, by key, as last built, and its
## glass's, for a chunk with glass that shows, and its shadowless voxels', for
## a chunk with those.
var _quads := {}
var _arrays := {}
var _glass_quads := {}
var _glass_arrays := {}
var _shadowless_quads := {}
var _shadowless_arrays := {}
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
## by key: [rows along x, rows along z, glass along x, glass along z,
## shadowless along x, shadowless along z], the glass's and shadowless' empty
## for a chunk with none.
var _cut_rows := {}
## Each chunk drawn otherwise while pieces are cut away, its own voxels cut or
## a neighbour's against it: its rectangles, and its mesh arrays (none for no
## rectangles), as so drawn, by key; and its glass's, and its shadowless'.
var _cut_quads := {}
var _cut_arrays := {}
var _cut_glass_quads := {}
var _cut_glass_arrays := {}
var _cut_shadowless_quads := {}
var _cut_shadowless_arrays := {}
## The whole mesh of each section drawn cut away, casting its shadow unseen,
## by section key.
var _shadows := {}
## The visual layers sections are drawn on: layer 1, or [constant
## SECTION_LAYER] while there are fine copies.
var _section_layers := 1
## The area lights fine copies are cut for, in this node's space:
## [code][where, reach, facing][/code] each.
var _fine_lights: Array = []
## The fine copy of each section within their reach, by section key; and the
## sections whose copy is to be cut again, their chunks meshed again.
var _fine := {}
var _fine_stale := {}
## How many triangles the fine copies have, for probes.
var fine_triangles := 0


func _init(drawn: VoxelVolume, with_collision := true) -> void:
	name = &"Voxels"
	volume = drawn
	collides = with_collision
	material = ShaderMaterial.new()
	material.shader = VoxelModel.SHADER
	glass_material = VoxelModel.glass_material()
	shadowless_material = ShaderMaterial.new()
	shadowless_material.shader = VoxelModel.SHADER
	shadowless_material.set_shader_parameter(&"lamp_shadows", false)


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
	for fine: MeshInstance3D in _fine.values():
		fine.queue_free()
	_fine.clear()
	_fine_stale.clear()
	fine_triangles = 0
	_cut.clear()
	_cut_rows.clear()
	_cut_quads.clear()
	_cut_arrays.clear()
	_cut_glass_quads.clear()
	_cut_glass_arrays.clear()
	_cut_shadowless_quads.clear()
	_cut_shadowless_arrays.clear()
	_quads.clear()
	_arrays.clear()
	_glass_quads.clear()
	_glass_arrays.clear()
	_shadowless_quads.clear()
	_shadowless_arrays.clear()
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


## Hands the volume's palette to the materials: each place's colour, its flags
## in the alpha.
func set_palette() -> void:
	var palette := palette_of(volume)
	for each: ShaderMaterial in [material, glass_material, shadowless_material]:
		VoxelModel.set_parameter(each, &"palette", palette)
		VoxelModel.set_parameter(each, &"box_size", Vector3i.ONE * VoxelVolume.SIZE)


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


## Has [param area_lights] take their shadows from fine copies of the level
## within their reach, cut for them, instead of from the sections, which a
## paraboloid's shadow map puts in the wrong place near the light; and
## [param other_lights] (the sun) leave the copies out of theirs. The copies
## follow the level as it wears and breaks; a light put out later keeps its
## copies, which nothing else sees. With no area lights given, the sections
## cast every shadow again. Returns how long it took, in microseconds.
func use_fine_shadows(area_lights: Array, other_lights: Array) -> int:
	var start := Time.get_ticks_usec()
	_fine_lights.clear()
	var to_local_basis := global_basis.inverse()
	for light: AreaLight3D in area_lights:
		var facing := (to_local_basis * -light.global_basis.z).normalized()
		var reach := light.area_range + light.area_size.length() * 0.5
		_fine_lights.append([to_local(light.global_position), reach, facing])
		light.shadow_caster_mask = 0xFFFFFFFF & ~SECTION_LAYER
	for light: Light3D in other_lights:
		light.shadow_caster_mask = light.shadow_caster_mask & ~FINE_LAYER
	_section_layers = SECTION_LAYER if not _fine_lights.is_empty() else 1
	for section: MeshInstance3D in _sections.values():
		section.layers = _section_layers
	for shadow: MeshInstance3D in _shadows.values():
		shadow.layers = _section_layers
	for fine: MeshInstance3D in _fine.values():
		fine.queue_free()
	_fine.clear()
	_fine_stale.clear()
	fine_triangles = 0
	var keys := {}
	for key: Vector3i in _quads:
		keys[_section_of(key)] = true
	for key: Vector3i in keys:
		_build_fine(key)
	return Time.get_ticks_usec() - start


## How many sections have a fine copy, for probes.
func fine_count() -> int:
	return _fine.size()


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
	var glass_x := PackedInt64Array()
	var glass_z := PackedInt64Array()
	var shadowless_x := PackedInt64Array()
	var shadowless_z := PackedInt64Array()
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
						if chunk.has_glass():
							glass_x = chunk.glass_x.duplicate()
							glass_z = chunk.glass_z.duplicate()
						if chunk.has_shadowless():
							shadowless_x = chunk.shadowless_x.duplicate()
							shadowless_z = chunk.shadowless_z.duplicate()
					rows_x[row] &= ~low
					rows_z[x + y * size] &= ~(1 << z)
					if not glass_x.is_empty():
						glass_x[row] &= ~low
						glass_z[x + y * size] &= ~(1 << z)
					if not shadowless_x.is_empty():
						shadowless_x[row] &= ~low
						shadowless_z[x + y * size] &= ~(1 << z)
	if not rows_x.is_empty():
		_cut_rows[key] = [rows_x, rows_z, glass_x, glass_z, shadowless_x, shadowless_z]


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
			_cut_glass_quads.erase(key)
			_cut_glass_arrays.erase(key)
			_cut_shadowless_quads.erase(key)
			_cut_shadowless_arrays.erase(key)
			_stale_sections[_section_of(key)] = true
		return
	var near := _near(key, true)
	var floor_slice := volume.floor_y - chunk.origin.y
	var found := ChunkMesher.faces(
		VoxelVolume.SIZE, _shown_rows(key, true), _shown_rows(key, false), _shown_glass(key, true),
		_shown_glass(key, false), near, floor_slice, false, _shown_shadowless(key, true), _shown_shadowless(key, false)
	)
	_keep_quads(key, found, chunk, true)
	_stale_sections[_section_of(key)] = true


## The neighbours of the chunk keyed [param key], for the mesher: their rows
## and glass as drawn, with the pieces cut away if [param cut], else whole.
func _near(key: Vector3i, cut: bool) -> ChunkMesher.Near:
	var near := ChunkMesher.Near.new()
	var sides := {
		&"east": [Vector3i.RIGHT, false], &"west": [Vector3i.LEFT, false],
		&"up": [Vector3i.UP, true], &"down": [Vector3i.DOWN, true],
		&"north": [Vector3i.BACK, true], &"south": [Vector3i.FORWARD, true],
	}
	for side: StringName in sides:
		var at: Vector3i = key + sides[side][0]
		var along_x: bool = sides[side][1]
		near.set(side, _shown_rows(at, along_x) if cut else _rows(at, along_x))
		near.set(StringName(String(side) + "_glass"), _shown_glass(at, along_x) if cut else _glass(at, along_x))
	return near


## Keeps [param found], the chunk keyed [param key]'s rectangles, its glass's
## and its shadowless voxels' ([method ChunkMesher.faces]), and the mesh arrays
## of each, as drawn whole, or as drawn cut away if [param cut]; none of the
## glass's or shadowless' for a chunk with none showing. The first set is kept
## even empty: it says the chunk is drawn so.
func _keep_quads(key: Vector3i, found: Array[PackedInt32Array], chunk: VoxelVolume.Chunk, cut: bool) -> void:
	var sets := _sets(cut)
	for part in 3:
		var quads: Dictionary = sets[part][0]
		var arrays: Dictionary = sets[part][1]
		if found[part].is_empty():
			if part == 0:
				quads[key] = found[part]
			else:
				quads.erase(key)
			arrays.erase(key)
		else:
			quads[key] = found[part]
			arrays[key] = ChunkMesher.arrays(found[part], chunk.origin, chunk.layer, 1.0 / VoxelVolume.BLOCK)


## The rectangles and mesh arrays of each surface, as dictionaries by chunk
## key, drawn whole or, if [param cut], cut away: [code][[rest's quads,
## arrays], [glass's], [shadowless']][/code].
func _sets(cut: bool) -> Array:
	if cut:
		return [[_cut_quads, _cut_arrays], [_cut_glass_quads, _cut_glass_arrays], [_cut_shadowless_quads, _cut_shadowless_arrays]]
	return [[_quads, _arrays], [_glass_quads, _glass_arrays], [_shadowless_quads, _shadowless_arrays]]


## The rows of the chunk keyed [param key] as they are drawn, without the
## pieces cut away, along x if [param along_x] else along z; empty if there is
## no chunk there.
func _shown_rows(key: Vector3i, along_x: bool) -> PackedInt64Array:
	var rows: Array = _cut_rows.get(key, [])
	if rows.is_empty():
		return _rows(key, along_x)
	return rows[0] if along_x else rows[1]


## The glass of the chunk keyed [param key] as it is drawn, as
## [method _shown_rows] has its rows: empty if it has none.
func _shown_glass(key: Vector3i, along_x: bool) -> PackedInt64Array:
	var rows: Array = _cut_rows.get(key, [])
	if rows.is_empty():
		return _glass(key, along_x)
	return rows[2] if along_x else rows[3]


## The voxels casting no lamp's shadow of the chunk keyed [param key] as it is
## drawn, as [method _shown_rows] has its rows: empty if it has none.
func _shown_shadowless(key: Vector3i, along_x: bool) -> PackedInt64Array:
	var rows: Array = _cut_rows.get(key, [])
	if rows.is_empty():
		var chunk: VoxelVolume.Chunk = volume.chunks.get(key)
		if chunk == null:
			return PackedInt64Array()
		return chunk.shadowless_x if along_x else chunk.shadowless_z
	return rows[4] if along_x else rows[5]


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
	VoxelModel.set_parameter(glass_material, &"voxels", texture)
	shadowless_material.set_shader_parameter(&"voxels", texture)


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
	var near := _near(key, false)
	var floor_slice := volume.floor_y - chunk.origin.y
	var found := ChunkMesher.faces(
		VoxelVolume.SIZE, chunk.rows_x, chunk.rows_z, chunk.glass_x, chunk.glass_z, near, floor_slice, false,
		chunk.shadowless_x, chunk.shadowless_z
	)
	_keep_quads(key, found, chunk, false)
	_stale_sections[_section_of(key)] = true
	if not _fine_lights.is_empty():
		_fine_stale[_section_of(key)] = true
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
	_glass_quads.erase(key)
	_glass_arrays.erase(key)
	_shadowless_quads.erase(key)
	_shadowless_arrays.erase(key)
	_cut_rows.erase(key)
	_cut_quads.erase(key)
	_cut_arrays.erase(key)
	_cut_glass_quads.erase(key)
	_cut_glass_arrays.erase(key)
	_cut_shadowless_quads.erase(key)
	_cut_shadowless_arrays.erase(key)
	_uncollided.erase(key)
	_recollide.erase(key)
	_stale_sections[_section_of(key)] = true
	if not _fine_lights.is_empty():
		_fine_stale[_section_of(key)] = true
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


## The glass of the chunk keyed [param key], as [method _rows] has its rows;
## empty if there is no chunk there or it has no glass.
func _glass(key: Vector3i, along_x: bool) -> PackedInt64Array:
	var chunk: VoxelVolume.Chunk = volume.chunks.get(key)
	if chunk == null:
		return PackedInt64Array()
	return chunk.glass_x if along_x else chunk.glass_z


static func _section_of(key: Vector3i) -> Vector3i:
	return Vector3i(key.x >> SECTION_SHIFT, key.y >> SECTION_SHIFT, key.z >> SECTION_SHIFT)


## Builds the mesh of the section keyed [param key] afresh from its chunks':
## as they are drawn, with any pieces cut away, and then, if any chunk of it is
## drawn cut away, its whole mesh as well, casting the shadow in its place.
func _build_section(key: Vector3i) -> void:
	if _fine_stale.erase(key):
		_build_fine(key)
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
			drawn.layers = _section_layers
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
		shadow.layers = _section_layers
		add_child(shadow)
		_shadows[key] = shadow
	shadow.mesh = whole


## The mesh of the section keyed [param key], from its chunks as drawn with the
## pieces cut away if [param cut], else whole, and how many rectangles it has:
## [mesh, rectangles], the mesh null for none. Its glass, if any shows, is a
## surface of its own, named [constant VoxelModel.GLASS_SURFACE], and so are its
## voxels casting no lamp's shadow, named [constant SHADOWLESS_SURFACE], in that
## order after the rest.
func _section_mesh(key: Vector3i, cut: bool) -> Array:
	var mesh: ArrayMesh = null
	var quads := 0
	var materials := [material, glass_material, shadowless_material]
	var names := ["", VoxelModel.GLASS_SURFACE, SHADOWLESS_SURFACE]
	for part_index in 3:
		var part := _section_part(key, cut, part_index)
		var count: int = part[1]
		if count == 0:
			continue
		quads += count
		if mesh == null:
			mesh = ArrayMesh.new()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, part[0], [], {}, ChunkMesher.format())
		var surface := mesh.get_surface_count() - 1
		mesh.surface_set_material(surface, materials[part_index])
		if names[part_index] != "":
			mesh.surface_set_name(surface, names[part_index])
	if quads == 0:
		return [null, 0]
	return [mesh, quads]


## The arrays of one surface of the section keyed [param key], as
## [method _section_mesh] makes it: its chunks' rest if [param part] is 0,
## glass if 1, voxels casting no lamp's shadow if 2, and how many rectangles
## that is: [arrays, rectangles].
func _section_part(key: Vector3i, cut: bool, part: int) -> Array:
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
				var drawn_as: Array = _sets(is_cut)[part]
				var from_quads: Dictionary = drawn_as[0]
				var from_arrays: Dictionary = drawn_as[1]
				var made: Variant = from_arrays.get(chunk_key)
				if made == null:
					continue
				vertices.append_array(made[Mesh.ARRAY_VERTEX])
				normals.append_array(made[Mesh.ARRAY_NORMAL])
				custom0.append_array(made[Mesh.ARRAY_CUSTOM0])
				custom1.append_array(made[Mesh.ARRAY_CUSTOM1])
				@warning_ignore("integer_division")
				quads += (from_quads[chunk_key] as PackedInt32Array).size() / ChunkMesher.FIELDS
	if quads == 0:
		return [[], 0]
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_CUSTOM0] = custom0
	arrays[Mesh.ARRAY_CUSTOM1] = custom1
	arrays[Mesh.ARRAY_INDEX] = ChunkMesher.index_array(quads)
	return [arrays, quads]


## Cuts the fine copy of the section keyed [param key] afresh from its chunks'
## faces as they are whole (a cut never changes a shadow): those that are
## neither glass, which casts no shadow, nor voxels that cast none from a lamp,
## and within reach of an area light and in front of it ([method
## _fine_pieces]). A section with none has no copy.
func _build_fine(key: Vector3i) -> void:
	var fine: MeshInstance3D = _fine.get(key)
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var custom0 := PackedFloat32Array()
	var custom1 := PackedFloat32Array()
	var quads := 0
	if _in_reach(key):
		var first := key * SECTION
		for x in SECTION:
			for y in SECTION:
				for z in SECTION:
					var chunk_key := first + Vector3i(x, y, z)
					var whole: PackedInt32Array = _quads.get(chunk_key, PackedInt32Array())
					var chunk: VoxelVolume.Chunk = volume.chunks.get(chunk_key)
					if whole.is_empty() or chunk == null:
						continue
					var pieces := _fine_pieces(whole, chunk.origin)
					if pieces.is_empty():
						continue
					var made := ChunkMesher.arrays(pieces, chunk.origin, chunk.layer, 1.0 / VoxelVolume.BLOCK)
					vertices.append_array(made[Mesh.ARRAY_VERTEX])
					normals.append_array(made[Mesh.ARRAY_NORMAL])
					custom0.append_array(made[Mesh.ARRAY_CUSTOM0])
					custom1.append_array(made[Mesh.ARRAY_CUSTOM1])
					@warning_ignore("integer_division")
					quads += pieces.size() / ChunkMesher.FIELDS
	var old_quads := 0
	if fine != null:
		old_quads = fine.get_meta(&"quads", 0)
	fine_triangles += (quads - old_quads) * 2
	if quads == 0:
		if fine != null:
			fine.queue_free()
			_fine.erase(key)
		return
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
	if fine == null:
		fine = MeshInstance3D.new()
		fine.name = &"FineShadow"
		fine.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
		fine.layers = FINE_LAYER
		add_child(fine)
		_fine[key] = fine
	fine.mesh = mesh
	fine.set_meta(&"quads", quads)


## Whether any area light fine copies are cut for reaches into the section
## keyed [param key]: none, and it needs no copy.
func _in_reach(key: Vector3i) -> bool:
	var low := Vector3(key * SECTION * VoxelVolume.SIZE) / VoxelVolume.BLOCK
	var high := low + Vector3.ONE * float(SECTION * VoxelVolume.SIZE) / VoxelVolume.BLOCK
	for light: Array in _fine_lights:
		var from: Vector3 = light[0]
		if from.clamp(low, high).distance_to(from) <= light[1]:
			return true
	return false


## The rectangles [param quads] of the chunk at [param origin] (in voxels), as
## the mesher packs them, each cut into pieces as [constant FINE_STEPS] has it
## for the nearest area light it is within reach of, faces and is not wholly
## behind; a rectangle no light reaches so is left out.
func _fine_pieces(quads: PackedInt32Array, origin: Vector3i) -> PackedInt32Array:
	var pieces := PackedInt32Array()
	var base := Vector3(origin)
	var to_cells := 1.0 / VoxelVolume.BLOCK
	for at in range(0, quads.size(), ChunkMesher.FIELDS):
		var axis := quads[at + ChunkMesher.AXIS]
		var side := quads[at + ChunkMesher.SIDE]
		var slice := quads[at + ChunkMesher.SLICE]
		var a0 := quads[at + ChunkMesher.ALONG]
		var b0 := quads[at + ChunkMesher.DOWN]
		var a1 := a0 + quads[at + ChunkMesher.WIDTH]
		var b1 := b0 + quads[at + ChunkMesher.HEIGHT]
		# Its box, flat across its axis, in cells, as ChunkMesher.arrays() lays
		# its corners out.
		var plane := float(slice + (1 if side > 0 else 0))
		var low: Vector3
		var high: Vector3
		if axis == 0:
			low = Vector3(plane, b0, a0)
			high = Vector3(plane, b1, a1)
		elif axis == 1:
			low = Vector3(a0, plane, b0)
			high = Vector3(a1, plane, b1)
		else:
			low = Vector3(a0, b0, plane)
			high = Vector3(a1, b1, plane)
		low = (base + low) * to_cells
		high = (base + high) * to_cells
		var nearest := INF
		for light: Array in _fine_lights:
			var from: Vector3 = light[0]
			var reach: float = light[1]
			var facing: Vector3 = light[2]
			var distance := from.clamp(low, high).distance_to(from)
			if distance > reach:
				continue
			# A face turned away from the light: a shadow map is drawn with back
			# faces culled, as the section is, so it would draw nothing.
			if (from[axis] - low[axis]) * side <= 0.0:
				continue
			# Its corner furthest out in front of the light: none in front, and
			# it is behind the light's paraboloid, which leaves it out.
			var ahead := (
				maxf(low.x * facing.x, high.x * facing.x)
				+ maxf(low.y * facing.y, high.y * facing.y)
				+ maxf(low.z * facing.z, high.z * facing.z)
				- from.dot(facing)
			)
			if ahead <= 0.0:
				continue
			nearest = minf(nearest, distance)
		if nearest == INF:
			continue
		var longest: int = FINE_FURTHEST
		for step: Array in FINE_STEPS:
			if nearest < step[0]:
				longest = step[1]
				break
		for a in range(a0, a1, longest):
			for b in range(b0, b1, longest):
				pieces.append_array([axis, side, slice, a, b, mini(longest, a1 - a), mini(longest, b1 - b)])
	return pieces


## Gives the chunk keyed [param key] collision as its faces are now: a trimesh
## of the same rectangles it is drawn with, its glass's and its shadowless
## voxels' among them.
func _collide(key: Vector3i) -> void:
	var body: StaticBody3D = _bodies.get(key)
	var vertices := PackedVector3Array()
	var quads := 0
	for drawn_as: Array in _sets(false):
		var made: Variant = (drawn_as[1] as Dictionary).get(key)
		if made == null:
			continue
		vertices.append_array(made[Mesh.ARRAY_VERTEX])
		@warning_ignore("integer_division")
		quads += ((drawn_as[0] as Dictionary)[key] as PackedInt32Array).size() / ChunkMesher.FIELDS
	if quads == 0:
		if body != null:
			body.queue_free()
			_bodies.erase(key)
		return
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
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
