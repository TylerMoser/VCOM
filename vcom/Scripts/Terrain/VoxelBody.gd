## A voxel model loose in the world that wears away a few voxels at a time, as
## a block does ([VoxelDestruction]): one of a crate's pieces, once a round or
## a blast has reached it since the crate broke
## ([method VoxelTerrain.take_on_later]), a prop a dying figure dropped, or any
## rigid body drawn by a MagicaVoxel model that [method VoxelTerrain.take_on_body]
## has taken on.
##
## It is a node under its body, and goes when the body goes. The body is a
## [RigidBody3D]; the model is a [VoxelModel] under one of its children, the
## [MeshInstance3D] that draws it, which holds its voxels, what is left of
## them, and their colours, blood and all. This is the model as a body: it
## collides as the box round what is left by the body's first
## [CollisionShape3D], and weighs its share of what the body weighed whole.
##
## Like all debris it is only for show: nothing in the rules sees it, and
## rounds tear through it and fly on.
class_name VoxelBody
extends Node

## Its voxels, as they are drawn.
var model: VoxelModel
## How it wears away.
var destruction: VoxelDestruction
## How many voxels it had when it came loose or was last cut from another:
## worn below its destruction's [member VoxelDestruction.collapse_below] of
## these, it crumbles. And how heavy it was then, in kilograms.
var whole := 0
var whole_mass := 1.0
## The body it is, and what it collides as.
var body: RigidBody3D
var collider: CollisionShape3D
## The bodies this one passes through: the pieces it was cut to overlap, and
## the models it was cut from or that were cut off it. Kept here, handed over
## by whatever made it ([method ScriptedDestruction._pass_overlaps]), as the
## physics server's own list still holds bodies since freed and fails on them;
## untyped, as this one may too, so each is checked before it is used.
var passes: Array = []


## [param drawing], drawn by a child of [param rigid], as a body wearing away
## as [param how] says.
func _init(drawing: VoxelModel, how: VoxelDestruction, rigid: RigidBody3D) -> void:
	name = &"Voxels"
	model = drawing
	destruction = how
	body = rigid
	whole = model.count
	whole_mass = rigid.mass
	for child in rigid.get_children():
		if child is CollisionShape3D:
			collider = child
			break


## Where its voxels are in the world ([method VoxelModel.frame]).
func frame() -> Transform3D:
	return model.frame()


## The box round what is left of it, in the world.
func world_box() -> AABB:
	return model.world_box()


## Starts counting what it loses afresh from what it has now, as a model cut
## from another does: its share of what it weighed whole then is what it weighs
## whole now.
func restart() -> void:
	whole_mass = whole_mass * model.count / maxi(whole, 1)
	whole = model.count


## Draws what is left of it, and collides as the box round it and weighs its
## share, its body woken to fall or tumble as what is left would.
func rebuild() -> void:
	model.rebuild()
	var bounds := model.bounds
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
	body.mass = maxf(whole_mass * model.count / maxi(whole, 1), ScriptedDestruction.MIN_MASS)
	body.sleeping = false
