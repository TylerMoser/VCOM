@tool
## Draws a level that is only scenery: the forest round a battlefield, which
## nothing in the rules sees, nothing breaks and blood never reaches. Each kind
## of piece is meshed once and drawn as many times as it is placed, by a
## [MultiMesh] for each kind in each region of 8 cells square
## ([constant REGION_SHIFT]), so the view culls what it does not see a region at
## a time, as a GridMap's octants did.
##
## A kind is meshed as a chunk of its own ([ChunkMesher]): its faces merged by
## shape alone, its colours read from a texture of every kind's voxels, a layer
## a kind, and the faces looking down left out, since scenery is only ever seen
## from above. It casts no shadow, as the scenery never did: drawn into the
## sun's shadow map the forest cost more than the rest of a frame together.
##
## Further from the [member battlefield] it draws less detail: each kind also
## has a copy twice as coarse (every 2 x 2 x 2 of its voxels made one) and one
## four times as coarse, made from the kind's own voxels as the scenery is built,
## and each piece is drawn with the copy its rows out from the battlefield call
## for ([constant FULL_DETAIL_TO_ROW], [constant COARSE_2X_TO_ROW]), the edges
## between them made ragged ([constant RAGGED_2X_ROWS],
## [constant RAGGED_4X_ROWS]). The camera never leaves the battlefield, so a
## piece's rows from it stand for its distance from the camera, and its copy is
## chosen once, as the scenery is built: nothing changes as the camera moves.
## Docs/LEVELS.md ("Scenery") has the whole of it.
class_name SceneryRenderer
extends Node3D

## Cells to a side of a region, as a shift: 8. Smaller regions follow the
## edge of the view more closely, so less of what is off screen is drawn, but
## each costs a draw call and about 62 KB of video memory.
const REGION_SHIFT := 3

## Where each level of detail is drawn, in rows out from the battlefield's
## edge (a row is a cell; BoundaryMap's ring is 75 deep): every piece to
## FULL_DETAIL_TO_ROW in full detail, then the copies twice as coarse to
## COARSE_2X_TO_ROW, and those four times as coarse beyond it. Zoomed out and
## looking inward from an edge, the camera stands over about row 13; past row
## 20 a voxel in full detail is under a pixel wide, zoomed out. Set
## FULL_DETAIL_TO_ROW past the ring's depth to draw every piece in full, or
## COARSE_2X_TO_ROW past it for no copy four times as coarse.
const FULL_DETAIL_TO_ROW := 15
const COARSE_2X_TO_ROW := 30
## How ragged the edge is where each coarser copy starts: before its copy is
## chosen, each piece's row is moved by up to this many rows either way, by a
## number its slot always gives, so the edge wanders across a band twice this
## wide rather than running straight across the ring. 0 draws a straight edge.
## Keep each under half the rows between the two edges.
const RAGGED_2X_ROWS := 4
const RAGGED_4X_ROWS := 4

## What it draws.
var data: LevelData
var library: PieceLibrary
## The material the full-detail meshes share.
var material: ShaderMaterial
## The battlefield it surrounds, in cells across the ground (x and z), whose
## edge the rows are counted from. With no area, every piece is drawn in full.
var battlefield := Rect2i()
## How many triangles it draws in all, for probes.
var triangles := 0

## Each kind's mesh and its triangles, by how coarse (1 in full detail, 2 or 4)
## and then by the kind's place in the level's kinds; and how many kinds were
## meshed: a level edited to use a kind more is drawn afresh.
var _meshes := {}
var _kinds_meshed := 0
## Each region's instances, by kind, coarseness and region: (kind, coarseness,
## region x, region z).
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
	for key: Vector4i in placed:
		_fill(key, placed[key])
	return Time.get_ticks_usec() - start


## Draws again the regions [param slots] are in, as the level editor changes
## the pieces in them: every piece in each of those regions placed again, each
## with the copy its rows call for. A kind the level did not use before is
## drawn afresh with the rest.
func rebuild_slots(slots: Array[Vector3i]) -> void:
	if data.kinds.size() != _kinds_meshed or _meshes.is_empty():
		build()
		return
	var regions := {}
	for slot in slots:
		var cell := LevelData.cell_of(slot)
		regions[Vector2i(cell.x >> REGION_SHIFT, cell.z >> REGION_SHIFT)] = true
	# What was there goes; what is there now comes back.
	for key: Vector4i in _regions.keys():
		if regions.has(Vector2i(key.z, key.w)):
			var drawn: MultiMeshInstance3D = _regions[key]
			triangles -= int(_meshes[key.y][key.x][1]) * drawn.multimesh.instance_count
			drawn.queue_free()
			_regions.erase(key)
	var placed := {}
	for index in data.count():
		var key := _region_of(index)
		if key.x < 0 or not regions.has(Vector2i(key.z, key.w)):
			continue
		var list: Array = placed.get_or_add(key, [])
		list.append(index)
	for key: Vector4i in placed:
		_fill(key, placed[key])


## How many regions are drawn, for probes: a region holds a multimesh for each
## kind and coarseness in it.
func region_count() -> int:
	return _regions.size()


## Meshes each kind the level uses in full detail, twice as coarse and four
## times as coarse, each coarseness with the material its kinds share.
func _make_meshes() -> void:
	# The kinds' voxels and the palette are worked out as a battlefield's are,
	# a kind's own box standing for a chunk.
	var volume := VoxelVolume.new(data, library)
	var stamps := {}
	for kind in data.kinds.size():
		if volume.shapes[kind] == null:
			continue
		var stamp := volume._stamp(kind, 0)
		if stamp.count > 0:
			stamps[kind] = stamp
	_kinds_meshed = data.kinds.size()
	for size in [1, 2, 4]:
		var made := _make_size(size, stamps, volume)
		if not made.is_empty():
			_meshes[size] = made


## Meshes every kind in [param stamps] [param size] times as coarse, and makes
## the material they share, a layer of its texture a kind. Returns each kind's
## mesh and its triangles, by kind.
func _make_size(size: int, stamps: Dictionary, volume: VoxelVolume) -> Dictionary:
	@warning_ignore("integer_division")
	var n := VoxelVolume.BLOCK / size
	var made := {}
	var images: Array[Image] = []
	for kind: int in stamps:
		var stamp: VoxelVolume.Stamp = stamps[kind]
		var rows_x := stamp.rows_x
		var rows_z := stamp.rows_z
		var colors := stamp.colors
		if size > 1:
			var coarse := _coarser(stamp, size)
			rows_x = coarse[0]
			rows_z = coarse[1]
			colors = Image.create_from_data(n, n * n, false, Image.FORMAT_R8, coarse[2])
		var quads := ChunkMesher.rectangles(n, rows_x, rows_z, ChunkMesher.Near.new(), -1, true)
		if quads.is_empty():
			continue
		var arrays := ChunkMesher.arrays(quads, Vector3i.ZERO, images.size(), 1.0 / n)
		@warning_ignore("integer_division")
		var count := quads.size() / ChunkMesher.FIELDS
		arrays[Mesh.ARRAY_INDEX] = ChunkMesher.index_array(count)
		var mesh := ArrayMesh.new()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, [], {}, ChunkMesher.format())
		made[kind] = [mesh, count * 2]
		images.append(colors)
	if images.is_empty():
		return made
	var texture := Texture2DArray.new()
	texture.create_from_images(images)
	var shared := ShaderMaterial.new()
	shared.shader = VoxelModel.SHADER
	shared.set_shader_parameter(&"voxels", texture)
	shared.set_shader_parameter(&"box_size", Vector3i.ONE * n)
	shared.set_shader_parameter(&"voxels_per_unit", float(n))
	shared.set_shader_parameter(&"palette", LevelRenderer.palette_of(volume))
	for entry: Array in made.values():
		(entry[0] as ArrayMesh).surface_set_material(0, shared)
	if size == 1:
		material = shared
	return made


## [param stamp]'s voxels [param size] times as coarse: a voxel wherever any of
## the voxels it stands for is one, so a thin piece thickens rather than
## vanishes, in the colour most of them have. Returns its rows along x and
## along z and its colours, laid out as a stamp's are.
static func _coarser(stamp: VoxelVolume.Stamp, size: int) -> Array:
	@warning_ignore("integer_division")
	var n := VoxelVolume.BLOCK / size
	var rows_x := PackedInt64Array()
	var rows_z := PackedInt64Array()
	var places := PackedByteArray()
	rows_x.resize(n * n)
	rows_z.resize(n * n)
	places.resize(n * n * n)
	for y in n:
		for z in n:
			for x in n:
				var tally := {}
				for dy in size:
					for dz in size:
						var row_at := z * size + dz + (y * size + dy) * VoxelVolume.BLOCK
						var row := stamp.rows_x[row_at]
						for dx in size:
							if (row >> (x * size + dx)) & 1:
								var place := stamp.places[x * size + dx + row_at * VoxelVolume.BLOCK]
								tally[place] = int(tally.get(place, 0)) + 1
				if tally.is_empty():
					continue
				rows_x[z + y * n] |= 1 << x
				rows_z[x + y * n] |= 1 << z
				var most := 0
				for place: int in tally:
					if tally[place] > most:
						most = tally[place]
						places[x + (z + y * n) * n] = place
	return [rows_x, rows_z, places]


## The kind, coarseness and region of piece [param index], as (kind,
## coarseness, region x, region z); x below 0 for a piece whose kind has no
## mesh. A kind with no coarser copy (one with no voxels left to mesh at that
## size) is drawn with the finest it has.
func _region_of(index: int) -> Vector4i:
	var kind := data.kind_at(index)
	var slot := data.slot_at(index)
	var size := _size_at(slot)
	while size > 1 and not (_meshes.get(size, {}) as Dictionary).has(kind):
		@warning_ignore("integer_division")
		size /= 2
	if not (_meshes.get(size, {}) as Dictionary).has(kind):
		return Vector4i(-1, 0, 0, 0)
	var cell := LevelData.cell_of(slot)
	return Vector4i(kind, size, cell.x >> REGION_SHIFT, cell.z >> REGION_SHIFT)


## How coarse a piece in [param slot] is drawn: 1 in full detail, 2 or 4 times
## as coarse, by its rows out from the battlefield's edge, moved by up to
## [constant RAGGED_2X_ROWS] or [constant RAGGED_4X_ROWS] at the edge where each
## coarser copy starts. The move comes from the slot alone, so a piece takes
## the same copy at every load and wherever the editor draws it again.
func _size_at(slot: Vector3i) -> int:
	if not battlefield.has_area():
		return 1
	var cell := LevelData.cell_of(slot)
	var last := battlefield.end - Vector2i.ONE
	var row := maxi(
		maxi(battlefield.position.x - cell.x, cell.x - last.x),
		maxi(battlefield.position.y - cell.z, cell.z - last.y))
	var wander := hash(slot)
	if row + _ragged(wander, RAGGED_2X_ROWS) <= FULL_DETAIL_TO_ROW:
		return 1
	if row + _ragged(wander >> 8, RAGGED_4X_ROWS) <= COARSE_2X_TO_ROW:
		return 2
	return 4


## A move of up to [param rows] either way, from [param number].
static func _ragged(number: int, rows: int) -> int:
	return posmod(number, 2 * rows + 1) - rows if rows > 0 else 0


## Draws the pieces [param list], all of one kind and coarseness in one region
## keyed [param key], as one multimesh.
func _fill(key: Vector4i, list: Array) -> void:
	var half := Vector3.ONE * 0.5
	var multimesh := MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.mesh = _meshes[key.y][key.x][0]
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
	triangles += int(_meshes[key.y][key.x][1]) * list.size()
