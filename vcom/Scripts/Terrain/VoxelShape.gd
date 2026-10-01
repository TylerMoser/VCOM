## The voxels of one voxel model, as its MagicaVoxel file draws them: what a
## block, or a loose model such as one of a crate's pieces, is before anything
## wears it away.
##
## They are read from the .vox the model was imported from, with the importer's
## own reader, so each voxel sits exactly where the imported mesh draws it, in
## the model's own frame: for a block ([method read]), its cell, a cell across
## and centred on its middle, sixteen voxels to a side; for a model of a .vox
## imported as a scene ([method read_model]), or a mesh imported straight from
## one ([method read_mesh]), the space its mesh is drawn in. Voxel (0, 0, 0) is
## the one at the least x, y and z, its least corner at [member corner], and
## each is [constant SCALE] across, a sixteenth of a cell, as every block and
## prop is imported.
##
## The voxels are kept in an array with an empty voxel all round the model's
## own, so a voxel's neighbours can be read without minding the edges, and a
## voxel holds the place of its colour in [member colors], 0 being no voxel at
## all. Beside them are the same voxels a row at a time ([member rows]): for
## each y and z, which of the voxels along x there are, as the bits of one
## number, bit x for voxel x, so a model can be at most [constant WIDEST]
## voxels along x.
##
## What a model is whole never changes, so each is read once and shared: a
## block or a loose model wearing away changes a copy of the arrays, never
## these.
class_name VoxelShape
extends RefCounted

## Voxels to a side of a block's cell, and how big a voxel is, in cells.
const BLOCK := 16
const SCALE := 1.0 / BLOCK
## The most voxels a model can have along x: a row's bits, less the sign.
const WIDEST := 62

## The reader the MagicaVoxel importer uses, and how it turns the model's axes
## (z up) into Godot's (y up).
const VoxReader = preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
const VOX_TO_GODOT := Basis(Vector3.RIGHT, Vector3.FORWARD, Vector3.UP)

## How many voxels the model has along x, y and z.
var size := Vector3i.ZERO
## How far apart in the array two voxels side by side along y and along z are
## (along x, one), where voxel (0, 0, 0) is in it, and how long it is.
var stride_y := 0
var stride_z := 0
var origin := 0
var length := 0
## The least corner of voxel (0, 0, 0), in the model's own frame.
var corner := Vector3.ZERO
## The voxels, as places in [member colors], 0 for none, and their rows.
var voxels := PackedByteArray()
var rows := PackedInt64Array()
## The model's palette, each colour at the place its voxels hold. The first,
## 0, is no colour.
var colors := PackedColorArray()
## How many voxels the model has whole.
var count := 0
## What the imported mesh is drawn with, for drawing what is left of a model
## the same way.
var material: Material

## Every .vox read so far and the frames it has, by path, and every model's
## shape, by path and model: none of them ever changes.
static var _files := {}
static var _frames := {}
static var _models := {}


## An empty model [param dimensions] voxels across, the least corner of its
## first voxel at [param least_corner] in its frame.
func _init(dimensions: Vector3i, least_corner: Vector3) -> void:
	size = dimensions
	stride_y = size.x + 2
	stride_z = stride_y * (size.y + 2)
	origin = 1 + stride_y + stride_z
	length = stride_z * (size.z + 2)
	corner = least_corner
	voxels.resize(length)
	rows.resize(size.y * size.z)
	colors.resize(256)


## The voxels of the block [param mesh] draws, standing in its cell as
## [param mesh_transform] places it there: a MeshLibrary item's. Null, with an
## error, if they cannot be read.
static func read(mesh: Mesh, mesh_transform: Transform3D) -> VoxelShape:
	var frame: Variant = _first_frame(mesh)
	if frame == null:
		return null
	var shape := VoxelShape.new(Vector3i.ONE * BLOCK, -Vector3.ONE * 0.5)
	shape._paint(_files[mesh.resource_path].colors)
	shape.material = mesh.surface_get_material(0) if mesh.get_surface_count() > 0 else null
	var outside := 0
	var half := Vector3.ONE * 0.5
	for voxel: Vector3 in frame:
		# Where the importer draws the voxel's middle, then where that is in
		# the cell, counted in voxels from its least corner.
		var middle := mesh_transform * (VOX_TO_GODOT * (voxel + half) * SCALE)
		var at := Vector3i(((middle + half) * BLOCK).floor())
		if not shape.holds(at):
			outside += 1
			continue
		shape.voxels[shape.index_of(at)] = int(frame[voxel]) + 1
		shape.count += 1
	if outside > 0:
		push_warning("VoxelShape: %d voxels of '%s' lie outside its cell, and are left out." % [outside, mesh.resource_path])
	shape.rows = shape.rows_of(shape.voxels)
	return shape


## The voxels of [param mesh], imported straight from a .vox as a Mesh, in the
## space it is drawn in: as big as the model, however big. Shared by
## everything drawn by that mesh; null, with an error, if they cannot be read.
static func read_mesh(mesh: Mesh) -> VoxelShape:
	if mesh != null and _models.has(mesh.resource_path):
		return _models[mesh.resource_path]
	var frame: Variant = _first_frame(mesh)
	if frame == null:
		return null
	# Where the importer draws each voxel's least corner, in voxels: MagicaVoxel's
	# y runs the other way to Godot's z.
	var least := Vector3i.MAX
	var most := Vector3i.MIN
	for voxel: Vector3 in frame:
		var at := _godot_corner(voxel)
		least = least.min(at)
		most = most.max(at)
	var shape := VoxelShape.new(most - least + Vector3i.ONE, Vector3(least) * SCALE)
	if shape.size.x > WIDEST:
		push_error("VoxelShape: '%s' is %d voxels along x, more than the %d a model can be." % [mesh.resource_path, shape.size.x, WIDEST])
		return null
	shape._paint(_files[mesh.resource_path].colors)
	shape.material = mesh.surface_get_material(0) if mesh.get_surface_count() > 0 else null
	for voxel: Vector3 in frame:
		shape.voxels[shape.index_of(_godot_corner(voxel) - least)] = int(frame[voxel]) + 1
		shape.count += 1
	shape.rows = shape.rows_of(shape.voxels)
	_models[mesh.resource_path] = shape
	return shape


## The voxels of model [param model_id] of the .vox at [param path], imported
## as a scene: in the space the importer draws that model's MeshInstance3D in,
## the model centred on its own middle. The importer marks each such node with
## its model ([code]magica_voxel_model_id[/code]). Shared by everything drawn
## from that model; null if the model is empty, and, with an error, if it
## cannot be read.
static func read_model(path: String, model_id: int) -> VoxelShape:
	var key := "%s#%d" % [path, model_id]
	if _models.has(key):
		return _models[key]
	var vox: Variant = _file(path)
	if vox == null or not vox.models.has(model_id):
		push_error("VoxelShape: '%s' has no model %d." % [path, model_id])
		return null
	var model = vox.models[model_id]
	if model.voxels.is_empty():
		_models[key] = null
		return null
	# The importer centres the model on its middle, rounded down, and turns its
	# axes as for a mesh: MagicaVoxel's y runs the other way to Godot's z. The
	# shape is cut down to the voxels there are: a crate's board is drawn as a
	# whole crate's model with only the board in it.
	var drawn := Vector3i(model.size)
	var middle := Vector3i((model.size / 2.0).floor())
	var least := Vector3i.MAX
	var most := Vector3i.MIN
	for voxel: Vector3 in model.voxels:
		var at := Vector3i(int(voxel.x), int(voxel.z), drawn.y - 1 - int(voxel.y))
		least = least.min(at)
		most = most.max(at)
	var size := most - least + Vector3i.ONE
	if size.x > WIDEST:
		push_error("VoxelShape: model %d of '%s' is %d voxels along x, more than the %d a model can be." % [model_id, path, size.x, WIDEST])
		_models[key] = null
		return null
	var base := Vector3(-middle.x, -middle.z, middle.y - drawn.y)
	var shape := VoxelShape.new(size, (base + Vector3(least)) * SCALE)
	shape._paint(vox.colors)
	for voxel: Vector3 in model.voxels:
		var at := Vector3i(int(voxel.x), int(voxel.z), drawn.y - 1 - int(voxel.y))
		shape.voxels[shape.index_of(at - least)] = int(model.voxels[voxel]) + 1
		shape.count += 1
	shape.rows = shape.rows_of(shape.voxels)
	_models[key] = shape
	return shape


## The .vox [param scene] was imported from, found through the scenes it
## inherits from, as a block's pieces scene inherits its .vox: where its
## models' voxels are read. Empty if it comes from none.
static func source_of(scene: PackedScene) -> String:
	var at := scene
	while at != null:
		if at.resource_path.get_extension().to_lower() == "vox":
			return at.resource_path
		at = at.get_state().get_node_instance(0) if at.get_state().get_node_count() > 0 else null
	return ""


## Whether every voxel of the model is filled.
func is_full() -> bool:
	return count == size.x * size.y * size.z


## Whether [param at], counted from voxel (0, 0, 0), is one of the model's.
func holds(at: Vector3i) -> bool:
	return at.x >= 0 and at.y >= 0 and at.z >= 0 and at.x < size.x and at.y < size.y and at.z < size.z


## Where the voxel [param at] is in the array.
func index_of(at: Vector3i) -> int:
	return origin + at.x + at.y * stride_y + at.z * stride_z


## The voxel at [param index] in the array.
@warning_ignore("integer_division")
func voxel_at(index: int) -> Vector3i:
	var rest := index - origin
	var z := rest / stride_z
	rest -= z * stride_z
	var y := rest / stride_y
	return Vector3i(rest - y * stride_y, y, z)


## The middle of the voxel at [param index], in the model's frame.
func center_of(index: int) -> Vector3:
	return corner + (Vector3(voxel_at(index)) + Vector3.ONE * 0.5) * SCALE


## The voxel a point at [param local], in the model's frame, falls in: perhaps
## one outside the model.
func voxel_under(local: Vector3) -> Vector3i:
	return Vector3i(((local - corner) / SCALE).floor())


## The six ways out of a voxel, and how far it is in the array to the voxel
## each way: up first and down last, so a search pushing them in this order
## pops down first.
func steps() -> Array[int]:
	return [stride_y, 1, -1, stride_z, -stride_z, -stride_y]


## The rows of [param of_voxels], an array laid out as this model's: for each
## y and z, which voxels along x there are, as the bits of one number, bit x
## for voxel x, at [code]y + z * size.y[/code].
func rows_of(of_voxels: PackedByteArray) -> PackedInt64Array:
	var found := PackedInt64Array()
	found.resize(size.y * size.z)
	for z in size.z:
		for y in size.y:
			var row := 0
			var at := origin + y * stride_y + z * stride_z
			for x in size.x:
				if of_voxels[at + x] != 0:
					row |= 1 << x
			found[y + z * size.y] = row
	return found


## The box, in the model's frame, round the voxels [param of_rows] say there
## are. Empty, at the frame's middle, if there are none.
func bounds_of(of_rows: PackedInt64Array) -> AABB:
	var least := Vector3i.MAX
	var most := Vector3i.MIN
	for z in size.z:
		for y in size.y:
			var row := of_rows[y + z * size.y]
			if row == 0:
				continue
			var low := row & -row
			var high := row
			while high & (high - 1):
				high &= high - 1
			least = least.min(Vector3i(VoxelMesher.BIT[low], y, z))
			most = most.max(Vector3i(VoxelMesher.BIT[high], y, z))
	if most.x < 0:
		return AABB(corner + Vector3(size) * SCALE * 0.5, Vector3.ZERO)
	return AABB(corner + Vector3(least) * SCALE, Vector3(most - least + Vector3i.ONE) * SCALE)


## Fills [member colors] from [param palette], a .vox's.
func _paint(palette: Array) -> void:
	for index in mini(palette.size(), 255):
		colors[index + 1] = palette[index]


## Where the importer draws the least corner of [param voxel], a voxel of a
## .vox read whole, in voxels in the mesh's space.
static func _godot_corner(voxel: Vector3) -> Vector3i:
	return Vector3i(int(voxel.x), int(voxel.z), -int(voxel.y) - 1)


## The voxels of the first frame of the .vox [param mesh] was imported from,
## as the importer draws them: by place in the model's own axes, holding the
## places of their colours. Null, with an error, if the mesh is not from one or
## it cannot be read.
static func _first_frame(mesh: Mesh) -> Variant:
	if mesh == null or mesh.resource_path.get_extension().to_lower() != "vox":
		push_error("VoxelShape: a model that wears away must be drawn by a mesh imported from a .vox, not '%s'." % (mesh.resource_path if mesh != null else "nothing"))
		return null
	var vox: Variant = _file(mesh.resource_path)
	if vox == null:
		return null
	# The importer draws the first frame of an animated model, so this does. The
	# reader gathers only the frames it has been told the file has.
	var reader = VoxReader.new()
	reader.fileKeyframeIds = _frames[mesh.resource_path].duplicate()
	var frames: Dictionary = reader.unify_voxels(vox, false)
	return frames[frames.keys().min()]


## The .vox at [param path], read once. Null, with an error, if it cannot be.
static func _file(path: String) -> Variant:
	if _files.has(path):
		return _files[path]
	var file: Dictionary = VoxReader.new().read_vox_data(path)
	if file["error"] != OK:
		push_error("VoxelShape: could not read '%s' (%s)." % [path, error_string(file["error"])])
		return null
	_files[path] = file["vox"]
	_frames[path] = file["keyframe_ids"]
	return file["vox"]
