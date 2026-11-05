## Bends a character's upper body to aim above or below level, and turns its
## head toward what it is looking at, over whatever its animation is doing. A
## [SkeletonModifier3D], so it works on the pose the animations leave each
## frame and never builds up. [CharacterModel] sets it.
##
## The animations aim level. Up or down, the spine and chest share the bend
## between them, so the arms and the gun in them come with the body.
extends SkeletonModifier3D

## The most the head turns toward what it looks at, side to side and up or
## down, in degrees.
const LOOK_YAW_LIMIT := 70.0
const LOOK_PITCH_LIMIT := 35.0
## How far above the head's joint its eyes are, in Godot units: where a look
## is measured from.
const EYE_RISE := 0.2

## How far the body is bent toward [member aim_pitch], 0 to 1.
var aim_weight := 0.0
## How far above level the body aims, in radians; below is negative.
var aim_pitch := 0.0
## How far the head is turned toward [member look_point], 0 to 1.
var look_weight := 0.0
## What the head looks at, in the world.
var look_point := Vector3.ZERO

var _spine := -1
var _chest := -1
var _head := -1


func _skeleton_changed(_old: Skeleton3D, new: Skeleton3D) -> void:
	_spine = -1
	if new != null:
		_spine = new.find_bone(&"Spine")
		_chest = new.find_bone(&"Chest")
		_head = new.find_bone(&"Head")


func _process_modification_with_delta(_delta: float) -> void:
	var skeleton := get_skeleton()
	if skeleton == null:
		return
	if _spine < 0:
		_skeleton_changed(null, skeleton)
		if _spine < 0:
			return
	if aim_weight > 0.001 and absf(aim_pitch) > 0.001:
		# Up tips the front (+z) toward +y, which is a turn the negative way
		# about the figure's side axis.
		var angle := -aim_pitch * aim_weight
		_turn(skeleton, _spine, Basis(Vector3.RIGHT, angle * 0.4))
		_turn(skeleton, _chest, Basis(Vector3.RIGHT, angle * 0.6))
	if look_weight > 0.001:
		var head := skeleton.get_bone_global_pose(_head)
		var target := skeleton.global_transform.affine_inverse() * look_point
		var toward := target - (head.origin + head.basis.y.normalized() * EYE_RISE)
		if toward.length_squared() > 1e-6:
			# Measured from the body's own front, not the head's, so a look
			# never winds the head round past what a neck allows.
			var chest := skeleton.get_bone_global_pose(_chest).basis.orthonormalized()
			var local := chest.inverse() * toward.normalized()
			var yaw := clampf(rad_to_deg(atan2(local.x, local.z)), -LOOK_YAW_LIMIT, LOOK_YAW_LIMIT)
			var pitch := clampf(rad_to_deg(atan2(local.y, Vector2(local.x, local.z).length())), -LOOK_PITCH_LIMIT, LOOK_PITCH_LIMIT)
			var wanted := chest * Basis.from_euler(Vector3(deg_to_rad(-pitch), deg_to_rad(yaw), 0.0))
			var now := Quaternion(head.basis.orthonormalized())
			var turned := now.slerp(Quaternion(wanted.orthonormalized()), look_weight)
			skeleton.set_bone_global_pose(_head, Transform3D(Basis(turned), head.origin))


## Turns [param bone] by [param turn] about its own joint, in the skeleton's
## space, taking everything below it along.
func _turn(skeleton: Skeleton3D, bone: int, turn: Basis) -> void:
	var pose := skeleton.get_bone_global_pose(bone)
	skeleton.set_bone_global_pose(bone, Transform3D(turn * pose.basis, pose.origin))
