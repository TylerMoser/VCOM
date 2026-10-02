## A voxel model loose in the world that wears away a few voxels at a time, as
## a block does ([VoxelDestruction]): one of a crate's pieces, once a round or
## a blast has reached it since the crate broke
## ([method VoxelTerrain.take_on_later]), or any rigid body drawn by a
## MagicaVoxel model that [method VoxelTerrain.take_on_body] has taken on.
##
## It is a node under its body, and goes when the body goes. The body is a
## [RigidBody3D]; the model is drawn by a [MeshInstance3D] among its children,
## whose space is the model's frame, laid out as its [VoxelShape], grown by
## [member scale] for a model drawn bigger than a block's voxels (a prop a
## figure dropped). What is
## left of it is a copy of the shape's voxels, less what rounds and blasts have
## broken off, drawn by that MeshInstance3D, collided as the box round it by
## the body's first [CollisionShape3D], and weighing its share of what the body
## weighed whole.
##
## Like all debris it is only for show: nothing in the rules sees it, and
## rounds tear through it and fly on.
class_name VoxelBody
extends Node

## The kind of model it is, and how it wears away.
var shape: VoxelShape
var destruction: VoxelDestruction
## What is left of it, laid out as [member shape]'s array, and its rows.
var voxels: PackedByteArray
var rows: PackedInt64Array
## How many voxels are left, and how many it had when it came loose or was
## last cut from another: worn below its destruction's
## [member VoxelDestruction.collapse_below] of these, it crumbles.
var count := 0
var whole := 0
## How heavy it was then, in kilograms.
var whole_mass := 1.0
## The body it is, what draws it and what it collides as.
var body: RigidBody3D
var drawn: MeshInstance3D
var collider: CollisionShape3D
## The box round what is left of it, in its frame.
var bounds := AABB()
## The bodies this one passes through: the pieces it was cut to overlap, and
## the models it was cut from or that were cut off it. Kept here, handed over
## by whatever made it ([method ScriptedDestruction._pass_overlaps]), as the
## physics server's own list still holds bodies since freed and fails on them;
## untyped, as this one may too, so each is checked before it is used.
var passes: Array = []
## The blood on it, drawn over its mesh: null until some lands on it
## ([method stained]).
var stains: VoxelStains
## The model's voxel size over [constant VoxelShape.SCALE]: 1 for a block's
## pieces, a shade more for a prop, which is imported at 0.063 a voxel. Its
## mesh's space is the shape's frame grown by this.
var scale := 1.0


## The model [param kind], wearing away as [param how] says, which
## [param mesh], a child of [param rigid], draws. [param left] is what is left
## of it, laid out as the kind's array; left out, it is whole.
func _init(kind: VoxelShape, how: VoxelDestruction, rigid: RigidBody3D, mesh: MeshInstance3D, left := PackedByteArray()) -> void:
	name = &"Voxels"
	shape = kind
	destruction = how
	body = rigid
	drawn = mesh
	# Copies: the kind's arrays are everything's drawn from that model.
	if left.is_empty():
		voxels = kind.voxels.duplicate()
		rows = kind.rows.duplicate()
		count = kind.count
	else:
		voxels = left
		rows = kind.rows_of(voxels)
		count = voxels.size() - voxels.count(0)
	whole = count
	whole_mass = rigid.mass
	for child in rigid.get_children():
		if child is CollisionShape3D:
			collider = child
			break
	bounds = shape.bounds_of(rows)


## Where the model is in the world: its frame, the space its mesh is drawn
## in, shrunk back to the shape's by [member scale].
func frame() -> Transform3D:
	return drawn.global_transform * Transform3D(Basis.from_scale(Vector3.ONE * scale), Vector3.ZERO)


## The box round what is left of it, in the world.
func world_box() -> AABB:
	return frame() * bounds


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


## The blood on it, made the first time it is asked for, and drawn over it.
func stained() -> VoxelStains:
	if stains == null:
		stains = VoxelStains.new(shape, scale)
		stains.voxels = func() -> PackedByteArray: return voxels
		stains.attach(drawn)
	return stains


## Takes [param kept] as its blood: the stains its mesh had before it came
## loose, as a prop a figure carried, already drawn over it.
func adopt_stains(kept: VoxelStains) -> void:
	stains = kept
	stains.voxels = func() -> PackedByteArray: return voxels


## Takes on the blood of [param from], the model it was cut from, laid out as
## its own: a stain shows only where this part has the voxel.
func carry_stains(from: VoxelStains) -> void:
	if from == null or from.is_empty():
		return
	var mine := stained()
	for index: int in from.faces:
		mine.stain(index, from.faces[index])


## Starts counting what it loses afresh from what it has now, as a model cut
## from another does: its share of what it weighed whole then is what it weighs
## whole now.
func restart() -> void:
	whole_mass = whole_mass * count / maxi(whole, 1)
	whole = count


## Draws what is left of it, and collides as the box round it and weighs its
## share, its body woken to fall or tumble as what is left would.
func rebuild() -> void:
	var arrays: Variant = VoxelMesher.surface(shape, voxels, rows)
	if arrays == null:
		drawn.mesh = null
	else:
		if scale != 1.0:
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			for vertex in vertices.size():
				vertices[vertex] *= scale
			arrays[Mesh.ARRAY_VERTEX] = vertices
		var built := ArrayMesh.new()
		built.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		built.surface_set_material(0, shape.material)
		drawn.mesh = built
	if stains != null:
		stains.changed()
	bounds = shape.bounds_of(rows)
	if collider != null and bounds.has_volume():
		var box := collider.shape as BoxShape3D
		if box == null:
			box = BoxShape3D.new()
			collider.shape = box
		# The box sits in the model's frame, wherever the mesh sits in the body
		# and however it is grown there.
		var in_body := body.global_transform.affine_inverse() * frame()
		box.size = bounds.size * in_body.basis.get_scale() * (1.0 - ScriptedDestruction.SLACK)
		collider.transform = Transform3D(in_body.basis.orthonormalized(), in_body * bounds.get_center())
	body.mass = maxf(whole_mass * count / maxi(whole, 1), ScriptedDestruction.MIN_MASS)
	body.sleeping = false
