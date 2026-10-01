## The voxels one kind of block is made of, as its MagicaVoxel model draws
## them: what every block of that kind is before anything wears it away.
##
## They are read from the .vox its MeshLibrary mesh was imported from, with
## the importer's own reader, so each voxel sits exactly where the imported
## mesh draws it. They are kept in the block's own cell, unturned, sixteen to
## a side ([constant SIZE]): voxel (0, 0, 0) is the corner of the cell at its
## least x, y and z, and each is a sixteenth of the cell across. The array has
## an empty voxel all round the cell's own ([constant PADDED] to a side), so a
## voxel's neighbours can be read without minding the edges of the cell.
##
## A voxel holds the place of its colour in [member colors], 0 being no voxel
## at all.
class_name VoxelShape
extends RefCounted

## Voxels to a side of a cell, and to a side of the array that holds them.
const SIZE := 16
const PADDED := SIZE + 2
## How far apart in the array two voxels side by side along x, y and z are.
const STRIDE_X := 1
const STRIDE_Y := PADDED
const STRIDE_Z := PADDED * PADDED
const STRIDES: Array[int] = [STRIDE_X, STRIDE_Y, STRIDE_Z]
## Where voxel (0, 0, 0) is in the array, and how long the array is.
const ORIGIN := STRIDE_X + STRIDE_Y + STRIDE_Z
const LENGTH := PADDED * PADDED * PADDED

## The reader the MagicaVoxel importer uses, and how it turns the model's axes
## (z up) into Godot's (y up).
const VoxReader = preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
const VOX_TO_GODOT := Basis(Vector3.RIGHT, Vector3.FORWARD, Vector3.UP)

## The voxels, as places in [member colors], 0 for none.
var voxels := PackedByteArray()
## The same voxels a row at a time ([method rows_of]).
var rows := PackedInt32Array()
## The model's palette, each colour at the place its voxels hold. The first,
## 0, is no colour.
var colors := PackedColorArray()
## How many voxels the block has whole.
var count := 0
## What the imported mesh is drawn with, for drawing what is left of a block
## the same way.
var material: Material


## The voxels of the block [param mesh] draws, standing in its cell as
## [param mesh_transform] places it there: a MeshLibrary item's. Null, with an
## error, if they cannot be read.
static func read(mesh: Mesh, mesh_transform: Transform3D) -> VoxelShape:
	if mesh == null or not mesh.resource_path.get_extension().to_lower() == "vox":
		push_error("VoxelShape: a block that wears away must be drawn by a mesh imported from a .vox, not '%s'." % (mesh.resource_path if mesh != null else "nothing"))
		return null
	var reader = VoxReader.new()
	var file: Dictionary = reader.read_vox_data(mesh.resource_path)
	if file["error"] != OK:
		push_error("VoxelShape: could not read '%s' (%s)." % [mesh.resource_path, error_string(file["error"])])
		return null
	# The importer draws the first frame of an animated model, so this does.
	var frames: Dictionary = reader.unify_voxels(file["vox"], false)
	var frame: Dictionary = frames[frames.keys().min()]
	var palette: Array = file["vox"].colors

	var shape := VoxelShape.new()
	shape.voxels.resize(LENGTH)
	shape.colors.resize(256)
	for index in mini(palette.size(), 255):
		shape.colors[index + 1] = palette[index]
	shape.material = mesh.surface_get_material(0) if mesh.get_surface_count() > 0 else null

	var outside := 0
	var half := Vector3.ONE * 0.5
	for voxel: Vector3 in frame:
		# Where the importer draws the voxel's middle, then where that is in
		# the cell, counted in voxels from its least corner.
		var middle := mesh_transform * (VOX_TO_GODOT * (voxel + half) / SIZE)
		var at := Vector3i(((middle + half) * SIZE).floor())
		if at.x < 0 or at.y < 0 or at.z < 0 or at.x >= SIZE or at.y >= SIZE or at.z >= SIZE:
			outside += 1
			continue
		shape.voxels[index_of(at)] = int(frame[voxel]) + 1
		shape.count += 1
	if outside > 0:
		push_warning("VoxelShape: %d voxels of '%s' lie outside its cell, and are left out." % [outside, mesh.resource_path])
	shape.rows = rows_of(shape.voxels)
	return shape


## Whether every voxel of the cell is filled.
func is_full() -> bool:
	return count == SIZE * SIZE * SIZE


## The rows of [param voxels]: for each y and z, which of the sixteen voxels
## along x there are, as the bits of one number, bit x for voxel x, at
## [code]y + z * SIZE[/code]. A block's faces can be found from them sixteen
## voxels at a time ([VoxelMesher]).
static func rows_of(voxels: PackedByteArray) -> PackedInt32Array:
	var rows := PackedInt32Array()
	rows.resize(SIZE * SIZE)
	for z in SIZE:
		for y in SIZE:
			var row := 0
			var at := ORIGIN + y * STRIDE_Y + z * STRIDE_Z
			for x in SIZE:
				if voxels[at + x] != 0:
					row |= 1 << x
			rows[y + z * SIZE] = row
	return rows


## Where the voxel [param at], counted from the cell's least corner, is in the
## array.
static func index_of(at: Vector3i) -> int:
	return ORIGIN + at.x * STRIDE_X + at.y * STRIDE_Y + at.z * STRIDE_Z


## The voxel at [param index] in the array, counted from the cell's least
## corner.
@warning_ignore("integer_division")
static func voxel_at(index: int) -> Vector3i:
	var rest := index - ORIGIN
	var z := rest / STRIDE_Z
	rest -= z * STRIDE_Z
	var y := rest / STRIDE_Y
	return Vector3i(rest - y * STRIDE_Y, y, z)


## The middle of the voxel at [param index], in the cell, unturned: a cell
## being one across and centred on its middle.
static func center_of(index: int) -> Vector3:
	return (Vector3(voxel_at(index)) + Vector3.ONE * 0.5) / SIZE - Vector3.ONE * 0.5
