## A block that wears away ([VoxelDestruction]) once it has lost voxels: what
## is left of it, drawn and collided with as it is now, standing in its cell in
## place of the GridMap's drawing of the whole block.
##
## It stands where the cell does, unturned voxels and all turned with it, so
## its voxels are laid out as its kind's [VoxelShape], in its own frame. It is
## only for show and for debris to land on: to the rules the cell holds the
## block's stand-in, as solid as the block whole (see [VoxelTerrain]).
class_name WornBlock
extends Node3D

## The kind of block it is, and what is left of it: a copy of the kind's
## array, less what has been broken off, and its rows
## ([method VoxelShape.rows_of]).
var shape: VoxelShape
var voxels: PackedByteArray
var rows: PackedInt64Array
## How many voxels are left.
var count := 0

var _drawn: MeshInstance3D
var _collider: CollisionShape3D


func _init(kind: VoxelShape) -> void:
	name = &"WornBlock"
	shape = kind
	# Copies: the kind's arrays are every unworn block's of that kind.
	voxels = kind.voxels.duplicate()
	rows = kind.rows.duplicate()
	count = kind.count
	_drawn = MeshInstance3D.new()
	_drawn.name = &"Mesh"
	add_child(_drawn)
	var body := StaticBody3D.new()
	body.name = &"Body"
	body.collision_layer = TerrainDestruction.TERRAIN_LAYER
	body.collision_mask = 0
	add_child(body)
	_collider = CollisionShape3D.new()
	body.add_child(_collider)


## Takes the voxel at [param index] in [member voxels] away, and returns what
## it held: the place of its colour, 0 if there was none.
func remove(index: int) -> int:
	var held := voxels[index]
	if held != 0:
		voxels[index] = 0
		var at := shape.voxel_at(index)
		rows[at.y + at.z * shape.size.y] &= ~(1 << at.x)
		count -= 1
	return held


## Draws and collides as what is left now.
func rebuild() -> void:
	var arrays: Variant = VoxelMesher.surface(shape, voxels, rows)
	if arrays == null:
		_drawn.mesh = null
		_collider.shape = null
		return
	var built := ArrayMesh.new()
	built.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	built.surface_set_material(0, shape.material)
	_drawn.mesh = built
	var faces := ConcavePolygonShape3D.new()
	faces.set_faces(VoxelMesher.triangles(arrays))
	_collider.shape = faces


## The mesh it is drawn with now.
func get_mesh() -> Mesh:
	return _drawn.mesh
