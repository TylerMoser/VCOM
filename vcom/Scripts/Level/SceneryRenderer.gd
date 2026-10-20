@tool
## Draws a level that is only scenery: the forest round a battlefield, which
## nothing in the rules sees, nothing breaks and blood never reaches. Each kind
## of piece is meshed once and drawn as many times as it is placed, by a
## [MultiMesh] for each kind in each region of [constant REGION] cells square,
## so the view culls what it does not see a region at a time, as a GridMap's
## octants did.
##
## A kind is meshed as a chunk of its own ([ChunkMesher]): its faces merged by
## shape alone, its colours read from a texture of every kind's voxels, a layer
## a kind, and the faces looking down left out, since scenery is only ever seen
## from above. It casts no shadow, as the scenery never did: drawn into the
## sun's shadow map the forest cost more than the rest of a frame together.
class_name SceneryRenderer
extends Node3D

## Cells to a side of a region, as a shift.
const REGION_SHIFT := 4

## What it draws.
var data: LevelData
var library: PieceLibrary
var material: ShaderMaterial
## How many triangles it draws in all, for probes.
var triangles := 0

## Each kind's mesh and its triangles, by its place in the level's kinds, and
## how many kinds were meshed: a level edited to use a kind more is drawn
## afresh.
var _meshes := {}
var _kinds_meshed := 0
## Each region's instances, by kind and region: (kind, region x, region z).
var _regions := {}


func _init(level: LevelData, pieces: PieceLibrary) -> void:
	name = &"Scenery"
	data = level
	library = pieces


## Builds every region's instances afresh. Returns how long it took, in
## microseconds.
func build() -> int:
	var start := Time.get_ticks_usec()
	for child in get_children():
		child.queue_free()
	_regions.clear()
	_meshes.clear()
	triangles = 0
	if data == null or library == null or data.count() == 0:
		return 0
	_make_meshes()
	if _meshes.is_empty():
		return 0
	var placed := {}
	for index in data.count():
		var key := _region_of(index)
		if key.x < 0:
			continue
		var list: Array = placed.get_or_add(key, [])
		list.append(index)
	for key: Vector3i in placed:
		_fill(key, placed[key])
	return Time.get_ticks_usec() - start


## Draws again the regions [param slots] are in, as the level editor changes
## the pieces in them: every piece in each of those regions placed again. A kind
## the level did not use before is drawn afresh with the rest.
func rebuild_slots(slots: Array[Vector3i]) -> void:
	if data.kinds.size() != _kinds_meshed or _meshes.is_empty():
		build()
		return
	var regions := {}
	for slot in slots:
		var cell := LevelData.cell_of(slot)
		regions[Vector2i(cell.x >> REGION_SHIFT, cell.z >> REGION_SHIFT)] = true
	# What was there goes; what is there now comes back.
	for key: Vector3i in _regions.keys():
		if regions.has(Vector2i(key.y, key.z)):
			var drawn: MultiMeshInstance3D = _regions[key]
			triangles -= int(_meshes.get(key.x, [null, 0])[1]) * drawn.multimesh.instance_count
			drawn.queue_free()
			_regions.erase(key)
	var placed := {}
	for index in data.count():
		var key := _region_of(index)
		if key.x < 0 or not regions.has(Vector2i(key.y, key.z)):
			continue
		var list: Array = placed.get_or_add(key, [])
		list.append(index)
	for key: Vector3i in placed:
		_fill(key, placed[key])


## How many regions are drawn, for probes.
func region_count() -> int:
	return _regions.size()


## Meshes each kind the level uses, and makes the material they share.
func _make_meshes() -> void:
	# The kinds' voxels and the palette are worked out as a battlefield's are,
	# a kind's own box standing for a chunk.
	var volume := VoxelVolume.new(data, library)
	var images: Array[Image] = []
	for kind in data.kinds.size():
		if volume.shapes[kind] == null:
			continue
		var stamp := volume._stamp(kind, 0)
		if stamp.count == 0:
			continue
		var quads := ChunkMesher.rectangles(VoxelVolume.BLOCK, stamp.rows_x, stamp.rows_z, ChunkMesher.Near.new(), -1, true)
		if quads.is_empty():
			continue
		var arrays := ChunkMesher.arrays(quads, Vector3i.ZERO, images.size(), 1.0 / VoxelVolume.BLOCK)
		@warning_ignore("integer_division")
		var count := quads.size() / ChunkMesher.FIELDS
		arrays[Mesh.ARRAY_INDEX] = ChunkMesher.index_array(count)
		var mesh := ArrayMesh.new()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, [], {}, ChunkMesher.format())
		_meshes[kind] = [mesh, count * 2]
		images.append(stamp.colors)
	_kinds_meshed = data.kinds.size()
	if images.is_empty():
		return
	var texture := Texture2DArray.new()
	texture.create_from_images(images)
	material = ShaderMaterial.new()
	material.shader = VoxelModel.SHADER
	material.set_shader_parameter(&"voxels", texture)
	material.set_shader_parameter(&"box_size", Vector3i.ONE * VoxelVolume.BLOCK)
	material.set_shader_parameter(&"palette", LevelRenderer.palette_of(volume))
	for entry: Array in _meshes.values():
		(entry[0] as ArrayMesh).surface_set_material(0, material)


## The kind and region of piece [param index], as (kind, region x, region z);
## x below 0 for a piece whose kind has no mesh.
func _region_of(index: int) -> Vector3i:
	var kind := data.kind_at(index)
	if not _meshes.has(kind):
		return Vector3i(-1, 0, 0)
	var cell := LevelData.cell_of(data.slot_at(index))
	return Vector3i(kind, cell.x >> REGION_SHIFT, cell.z >> REGION_SHIFT)


## Draws the pieces [param list], all of one kind in one region keyed
## [param key], as one multimesh.
func _fill(key: Vector3i, list: Array) -> void:
	var half := Vector3.ONE * 0.5
	var multimesh := MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.mesh = _meshes[key.x][0]
	multimesh.instance_count = list.size()
	for at in list.size():
		var index: int = list[at]
		var turn := Basis(Vector3.UP, data.turn_at(index) * PI * 0.5)
		var middle := LevelData.box_center(data.slot_at(index))
		multimesh.set_instance_transform(at, Transform3D(turn, middle) * Transform3D(Basis.IDENTITY, -half))
	var drawn := MultiMeshInstance3D.new()
	drawn.name = &"Region"
	drawn.multimesh = multimesh
	drawn.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(drawn)
	_regions[key] = drawn
	triangles += int(_meshes[key.x][1]) * list.size()
