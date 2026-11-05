## Authors every animation a humanoid character plays, for one rig, and the
## [AnimationNodeBlendTree] that plays them. Run by [code]BakeCharacter.gd[/code].
##
## The animations are written as poses in code rather than keyed by hand. A
## function of time places the feet, the hands and what they hold, and leans
## the body; the limbs between are worked out by inverse kinematics for this
## rig's proportions. So a model with longer legs or shorter arms gets
## animations that fit it, feet on the floor and hands on its rifle, by baking
## again. Each is sampled [constant FPS] times a second into rotation keys, and
## position keys for the root and hips. The result is an ordinary
## [AnimationLibrary] that the editor's animation panel can play and change,
## though the next bake replaces it.
##
## Units are rig voxels throughout: Godot's axes, a voxel a unit, the figure
## facing +z with its left toward +x, as [code]VoxelRig[/code] has them. A
## bone's rotation is relative to its parent, and every bone rests unrotated,
## so on any bone +x tips its +y toward +z (an upright bone leans forward, a
## hanging leg swings back), +y turns +z toward +x (the face turns to the
## figure's left), and +z tips +y toward -x (an upright bone leans to the
## figure's right).
##
## Three stances share every pose but what the hands hold: [code]rifle[/code]
## (the gun two-handed where it can be), [code]melee[/code] (the sword in the
## right hand) and [code]unarmed[/code]. A thrown grenade always leaves the left
## hand, so the right keeps hold of whatever it has.
extends RefCounted

const VoxelRig := preload("res://Scripts/Characters/VoxelRig.gd")

## Samples a second.
const FPS := 30.0
## The speed the run cycles are made for, in tiles a second. A character
## running faster or slower plays them faster or slower to match (see
## [code]CharacterModel[/code]), so its feet keep pace with the ground.
const RUN_SPEED := 5.0
## Tiles a stride of the run covers: one, so a cycle of two strides is two
## tiles.
const STRIDE_TILES := 1.0

## How far along its cover a character steps to lean out round the end of it,
## in voxels: most of the way to the edge of its tile, which is half a tile
## (about 7.9) from where it stood. Shifting its weight and tipping its body
## take its head the rest of the way and past: some 12 voxels out, three
## quarters of a tile, which a head 7 voxels wide needs to show past the edge
## to someone straight in front of the cover.
const LEAN_STEP := 6.5

## The stances, and the base poses (loops) every one of them has. A base pose
## is what a character holds between actions; see [method make_tree].
const STANCES: Array[StringName] = [&"rifle", &"melee", &"unarmed"]
const STANCE_POSES: Array[StringName] = [
	&"stand", &"crouch", &"wall", &"hunker", &"ready_throw", &"cheer",
	&"wall_lean_left", &"wall_lean_right", &"crouch_lean_left", &"crouch_lean_right",
]
## The leans out of cover among them, as [code][name, side][/code]: the side is
## 1 for the character's left and -1 for its right.
const LEANS := [[&"left", 1.0], [&"right", -1.0]]
## Base poses only some stances have.
const RIFLE_POSES: Array[StringName] = [&"aim_rifle", &"overwatch_rifle", &"overwatch_crouch_rifle"]
const MELEE_POSES: Array[StringName] = [&"ready_melee"]
## Played over the base pose, whole: [code]act[/code] in the tree.
const ACTS: Array[StringName] = [
	&"strike_sword", &"throw_rifle", &"throw_melee", &"throw_unarmed", &"draw_sword", &"stow_sword",
]
## Played over the arms and head alone, so the legs and body keep whatever
## pose they hold (standing, kneeling behind cover, hunkered):
## [code]upper[/code] in the tree. These key only [constant ARMS_AND_HEAD].
const UPPER_ACTS: Array[StringName] = [&"reload_rifle"]
## Played over the left arm alone, so everything else keeps whatever it was
## doing, the right hand holding on to its weapon: [code]left[/code] in the
## tree. These key only [constant LEFT_ARM].
const LEFT_ACTS: Array[StringName] = [&"use_medkit", &"use_medkit_self"]
## Added to whatever the base pose is doing, as a change to it:
## [code]react[/code] in the tree. These key only the bones they move.
const REACTS: Array[StringName] = [&"fire_rifle", &"hit_front", &"hit_back", &"dodge", &"land"]
## The bones the additive reactions move, and the bones a hop moves.
const UPPER_BODY: Array[StringName] = [&"Spine", &"Chest", &"Neck", &"Head"]
## The bones an [constant UPPER_ACTS] clip moves: both arms, the neck and the
## head, every one turned from the chest, so the clip rides the body however
## it leans.
const ARMS_AND_HEAD: Array[StringName] = [
	&"LeftUpperArm", &"LeftLowerArm", &"LeftHand", &"RightUpperArm", &"RightLowerArm", &"RightHand",
	&"Neck", &"Head",
]
## The bones a [constant LEFT_ACTS] clip moves: the left arm, turned from the
## chest, so it rides the body however it stands. The head is left to look
## where the figure is told to ([code]CharacterModel[/code]).
const LEFT_ARM: Array[StringName] = [&"LeftUpperArm", &"LeftLowerArm", &"LeftHand"]
## Where the left hand holds a medkit to the figure's own middle, in rig voxels
## from the chest joint: the [code]use_medkit_self[/code] clip.
const SELF_MEDKIT := Vector3(0.4, -2.6, 3.2)
const LEGS: Array[StringName] = [
	&"Hips", &"LeftUpperLeg", &"LeftLowerLeg", &"LeftFoot", &"RightUpperLeg", &"RightLowerLeg", &"RightFoot",
]

var rig: VoxelRig
## Godot units a voxel, from the rig.
var scale := 1.0
## Where the hand holds each prop, as the prop's origin (its grip) in the
## hand bone's own space, in rig voxels. The props stand along +z, up +y.
var rifle_grip := Transform3D.IDENTITY
var sword_grip := Transform3D.IDENTITY
var grenade_grip := Transform3D.IDENTITY
## Where the left hand holds the rifle, in the rifle's own space.
var rifle_foregrip := Vector3(0, 0, 3)

## Bone -> its parent, and its joint's offset from its parent's at rest.
var _parent := {}
var _rest := {}
## Each hand's palm: the middle of its voxels, in its own space.
var _palm := {}
## The middle of the head's voxels, in its own space.
var _head := Vector3.ZERO


func _init(voxel_rig: VoxelRig) -> void:
	rig = voxel_rig
	scale = rig.scale
	for entry: Array in VoxelRig.BONES:
		_parent[entry[0]] = entry[1]
		_rest[entry[0]] = rig.joints[entry[0]] - (rig.joints[entry[1]] if entry[1] != &"" else Vector3.ZERO)
	for side: StringName in [&"Left", &"Right"]:
		var hand := StringName(side + "Hand")
		_palm[side] = rig.bone_box(hand).get_center() / scale
	_head = rig.bone_box(&"Head").get_center() / scale
	# The rifle's barrel runs on from the forearm, as a pistol's does: along the
	# right hand's length (-x), its top up the back of the hand.
	rifle_grip = Transform3D(Basis(Vector3.UP, -PI / 2.0), _palm[&"Right"])
	# The sword stands out of the fist on the thumb side (+z), its edges up and
	# down the hand.
	sword_grip = Transform3D(Basis.IDENTITY, _palm[&"Right"])
	grenade_grip = Transform3D(Basis.IDENTITY, _palm[&"Left"])


## Reads where the left hand holds the rifle from the rifle's scene, its
## [code]Foregrip[/code] marker, so the animations follow the model.
func read_rifle(rifle_scene: PackedScene) -> void:
	var rifle := rifle_scene.instantiate()
	var marker := rifle.get_node_or_null(^"Foregrip") as Node3D
	if marker != null:
		rifle_foregrip = marker.position / scale
	rifle.free()


## Every animation, by name.
func make_library() -> AnimationLibrary:
	var library := AnimationLibrary.new()
	for stance in STANCES:
		library.add_animation(StringName("stand_%s" % stance), _loop(2.4, _stand.bind(stance)))
		library.add_animation(StringName("crouch_%s" % stance), _loop(2.8, _crouch.bind(stance, false)))
		library.add_animation(StringName("wall_%s" % stance), _loop(2.6, _wall.bind(stance)))
		library.add_animation(StringName("hunker_%s" % stance), _loop(3.2, _hunker.bind(stance)))
		for lean: Array in LEANS:
			library.add_animation(StringName("wall_lean_%s_%s" % [lean[0], stance]), _lean(2.6, _wall.bind(stance, lean[1])))
			library.add_animation(StringName("crouch_lean_%s_%s" % [lean[0], stance]), _lean(2.8, _crouch.bind(stance, false, lean[1])))
		library.add_animation(StringName("ready_throw_%s" % stance), _loop(2.0, _throw.bind(stance, -1.0)))
		library.add_animation(StringName("cheer_%s" % stance), _loop(1.0, _cheer.bind(stance)))
		var run := _loop(_cycle(), _run.bind(stance))
		run.set_meta(&"speed", RUN_SPEED)
		library.add_animation(StringName("run_%s" % stance), run)
		var throw := _once(0.8, _throw.bind(stance, 1.0))
		throw.set_meta(&"release", 0.36)
		library.add_animation(StringName("throw_%s" % stance), throw)
	library.add_animation(&"aim_rifle", _loop(3.0, _aim.bind(0.0)))
	library.add_animation(&"overwatch_rifle", _loop(4.0, _aim.bind(1.0)))
	library.add_animation(&"overwatch_crouch_rifle", _loop(4.0, _crouch.bind(&"rifle", true)))
	library.add_animation(&"ready_melee", _loop(2.0, _strike.bind(-1.0)))
	library.add_animation(&"back_rifle", _loop(_cycle(), _step.bind(Vector2(0, -1))))
	library.add_animation(&"strafe_left_rifle", _loop(_cycle(), _step.bind(Vector2(1, 0))))
	library.add_animation(&"strafe_right_rifle", _loop(_cycle(), _step.bind(Vector2(-1, 0))))
	library.add_animation(&"hop", _loop(0.5, _hop))
	library.add_animation(&"fall", _loop(0.6, _fall))
	var strike := _once(0.75, _strike.bind(1.0))
	strike.set_meta(&"impact", 0.27)
	library.add_animation(&"strike_sword", strike)
	var draw := _once(0.45, _draw.bind(true))
	draw.set_meta(&"swap", 0.17)
	library.add_animation(&"draw_sword", draw)
	var stow := _once(0.45, _draw.bind(false))
	stow.set_meta(&"swap", 0.2)
	library.add_animation(&"stow_sword", stow)
	var reload := _once(1.2, _reload, ARMS_AND_HEAD)
	reload.set_meta(&"seat", 0.78)
	library.add_animation(&"reload_rifle", reload)
	for on_self in [false, true]:
		var medkit := _once(1.4, _medkit.bind(on_self), LEFT_ARM)
		medkit.set_meta(&"take", 0.24)
		medkit.set_meta(&"apply", 0.58)
		medkit.set_meta(&"stow", 1.18)
		library.add_animation(&"use_medkit_self" if on_self else &"use_medkit", medkit)
	library.add_animation(&"fire_rifle", _once(0.3, _fire, UPPER_BODY))
	library.add_animation(&"hit_front", _once(0.42, _hit.bind(-1.0), UPPER_BODY))
	library.add_animation(&"hit_back", _once(0.42, _hit.bind(1.0), UPPER_BODY))
	library.add_animation(&"dodge", _once(0.4, _dodge, UPPER_BODY))
	library.add_animation(&"land", _once(0.5, _land, UPPER_BODY + LEGS))
	return library


## The tree every character plays its animations through. Its parameters are
## what [code]CharacterModel[/code] sets:
##
## - [code]stance[/code]: which base pose it holds (a [AnimationNodeTransition]
##   over every base loop, by name).
## - [code]run[/code] and [code]run_scale[/code]: which run it runs, and how
##   fast; [code]run_rifle[/code], which way, a blend position across the
##   ground in its own space (forward is +y), since a rifleman stepping out
##   keeps facing his target.
## - [code]move[/code]: from the base pose (0) to running (1).
## - [code]hop[/code]: the legs tucked up, for a step up or down a level.
## - [code]air[/code]: falling.
## - [code]act[/code]: a one-shot played whole over all that, picked by
##   [code]act_pick[/code]: a strike, a throw, drawing or stowing the sword.
## - [code]upper[/code]: a one-shot over the arms and head alone (filtered to
##   [constant ARMS_AND_HEAD]), picked by [code]upper_pick[/code]: a reload.
## - [code]left[/code]: a one-shot over the left arm alone (filtered to
##   [constant LEFT_ARM]), picked by [code]left_pick[/code]: using a medkit.
## - [code]react[/code]: a one-shot added to everything else, picked by
##   [code]react_pick[/code]: firing, a flinch, landing.
func make_tree() -> AnimationNodeBlendTree:
	var tree := AnimationNodeBlendTree.new()

	var stance := AnimationNodeTransition.new()
	stance.xfade_time = 0.22
	var row := 0
	for pose in base_poses():
		stance.add_input(pose)
		stance.set_input_reset(row, false)
		tree.add_node(pose, _animation(pose), Vector2(0.0, row * 70.0))
		row += 1
	tree.add_node(&"stance", stance, Vector2(300.0, 0.0))
	for index in row:
		tree.connect_node(&"stance", index, base_poses()[index])

	var directions := AnimationNodeBlendSpace2D.new()
	directions.sync = true
	directions.min_space = Vector2(-1.0, -1.0)
	directions.max_space = Vector2(1.0, 1.0)
	directions.add_blend_point(_animation(&"run_rifle"), Vector2(0.0, 1.0), -1, &"forward")
	directions.add_blend_point(_animation(&"back_rifle"), Vector2(0.0, -1.0), -1, &"back")
	directions.add_blend_point(_animation(&"strafe_left_rifle"), Vector2(1.0, 0.0), -1, &"left")
	directions.add_blend_point(_animation(&"strafe_right_rifle"), Vector2(-1.0, 0.0), -1, &"right")
	tree.add_node(&"run_rifle", directions, Vector2(0.0, row * 70.0 + 40.0))
	tree.add_node(&"run_melee", _animation(&"run_melee"), Vector2(0.0, row * 70.0 + 110.0))
	tree.add_node(&"run_unarmed", _animation(&"run_unarmed"), Vector2(0.0, row * 70.0 + 180.0))
	var run := AnimationNodeTransition.new()
	run.xfade_time = 0.15
	for name: StringName in [&"run_rifle", &"run_melee", &"run_unarmed"]:
		run.add_input(name)
	tree.add_node(&"run", run, Vector2(300.0, row * 70.0 + 80.0))
	tree.connect_node(&"run", 0, &"run_rifle")
	tree.connect_node(&"run", 1, &"run_melee")
	tree.connect_node(&"run", 2, &"run_unarmed")
	tree.add_node(&"run_scale", AnimationNodeTimeScale.new(), Vector2(500.0, row * 70.0 + 80.0))
	tree.connect_node(&"run_scale", 0, &"run")

	var move := AnimationNodeBlend2.new()
	tree.add_node(&"move", move, Vector2(700.0, 200.0))
	tree.connect_node(&"move", 0, &"stance")
	tree.connect_node(&"move", 1, &"run_scale")

	var hop := AnimationNodeBlend2.new()
	hop.filter_enabled = true
	for bone in LEGS:
		hop.set_filter_path(NodePath("Skeleton3D:" + bone), true)
	tree.add_node(&"hop_pose", _animation(&"hop"), Vector2(700.0, 400.0))
	tree.add_node(&"hop", hop, Vector2(900.0, 200.0))
	tree.connect_node(&"hop", 0, &"move")
	tree.connect_node(&"hop", 1, &"hop_pose")

	tree.add_node(&"fall_pose", _animation(&"fall"), Vector2(900.0, 400.0))
	tree.add_node(&"air", AnimationNodeBlend2.new(), Vector2(1100.0, 200.0))
	tree.connect_node(&"air", 0, &"hop")
	tree.connect_node(&"air", 1, &"fall_pose")

	_picker(tree, &"act_pick", ACTS, Vector2(1100.0, 450.0))
	var act := AnimationNodeOneShot.new()
	act.fadein_time = 0.1
	act.fadeout_time = 0.22
	tree.add_node(&"act", act, Vector2(1500.0, 200.0))
	tree.connect_node(&"act", 0, &"air")
	tree.connect_node(&"act", 1, &"act_pick")

	# Filtered, so the bones it leaves alone come straight from what is under
	# it: the tree blends deterministically, and a clip missing a bone's track
	# would otherwise pull that bone toward its rest.
	_picker(tree, &"upper_pick", UPPER_ACTS, Vector2(1500.0, 650.0))
	var upper := AnimationNodeOneShot.new()
	upper.fadein_time = 0.15
	upper.fadeout_time = 0.25
	upper.filter_enabled = true
	for bone in ARMS_AND_HEAD:
		upper.set_filter_path(NodePath("Skeleton3D:" + bone), true)
	tree.add_node(&"upper", upper, Vector2(1700.0, 200.0))
	tree.connect_node(&"upper", 0, &"act")
	tree.connect_node(&"upper", 1, &"upper_pick")

	# Filtered as the upper one is, to the left arm alone.
	_picker(tree, &"left_pick", LEFT_ACTS, Vector2(1700.0, 850.0))
	var left := AnimationNodeOneShot.new()
	left.fadein_time = 0.15
	left.fadeout_time = 0.25
	left.filter_enabled = true
	for bone in LEFT_ARM:
		left.set_filter_path(NodePath("Skeleton3D:" + bone), true)
	tree.add_node(&"left", left, Vector2(1900.0, 200.0))
	tree.connect_node(&"left", 0, &"upper")
	tree.connect_node(&"left", 1, &"left_pick")

	_picker(tree, &"react_pick", REACTS, Vector2(1500.0, 450.0))
	var react := AnimationNodeOneShot.new()
	react.mix_mode = AnimationNodeOneShot.MIX_MODE_ADD
	react.fadein_time = 0.03
	react.fadeout_time = 0.12
	tree.add_node(&"react", react, Vector2(2100.0, 200.0))
	tree.connect_node(&"react", 0, &"left")
	tree.connect_node(&"react", 1, &"react_pick")

	tree.connect_node(&"output", 0, &"react")
	tree.set_node_position(&"output", Vector2(2300.0, 200.0))
	return tree


## Every base pose, as named in the tree's [code]stance[/code].
static func base_poses() -> Array[StringName]:
	var poses: Array[StringName] = []
	for stance in STANCES:
		for pose in STANCE_POSES:
			poses.append(StringName("%s_%s" % [pose, stance]))
	poses.append_array(RIFLE_POSES)
	poses.append_array(MELEE_POSES)
	return poses


## Seconds a run cycle takes at [constant RUN_SPEED]: two strides.
func _cycle() -> float:
	return 2.0 * STRIDE_TILES / RUN_SPEED


func _animation(name: StringName) -> AnimationNodeAnimation:
	var node := AnimationNodeAnimation.new()
	node.animation = name
	return node


## A transition named [param name] over clips of [param names], cut straight
## to whichever is asked for, to feed a one-shot: the one-shot does the fading.
func _picker(tree: AnimationNodeBlendTree, name: StringName, names: Array[StringName], at: Vector2) -> void:
	var picker := AnimationNodeTransition.new()
	picker.xfade_time = 0.0
	for index in names.size():
		picker.add_input(names[index])
		picker.set_input_reset(index, true)
		tree.add_node(StringName("%s_clip" % names[index]), _animation(names[index]), at + Vector2(0.0, index * 70.0))
	tree.add_node(name, picker, at + Vector2(200.0, 0.0))
	for index in names.size():
		tree.connect_node(name, index, StringName("%s_clip" % names[index]))


# --- Sampling ----------------------------------------------------------------

## A looping animation [param length] seconds long, sampled from
## [param pose_at], a function of the time.
func _loop(length: float, pose_at: Callable) -> Animation:
	var animation := _sample(length, pose_at, [])
	animation.loop_mode = Animation.LOOP_LINEAR
	return animation


## A looping lean out of cover, [param length] seconds long, sampled from
## [param pose_at]. How far out of the middle of its tile the lean puts the
## middle of the head, in Godot units, goes on it as [code]reach[/code]: where
## whoever has the character in their sights is seen to aim.
func _lean(length: float, pose_at: Callable) -> Animation:
	var animation := _loop(length, pose_at)
	var head: Transform3D = (pose_at.call(0.0) as Pose).at(&"Head")
	animation.set_meta(&"reach", absf((head * _head).x) * scale)
	return animation


## An animation played once. [param only], if given, are the only bones keyed:
## an animation added to others keys just what it changes.
func _once(length: float, pose_at: Callable, only: Array[StringName] = []) -> Animation:
	return _sample(length, pose_at, only)


func _sample(length: float, pose_at: Callable, only: Array[StringName]) -> Animation:
	var animation := Animation.new()
	animation.length = length
	var bones: Array[StringName] = []
	for entry: Array in VoxelRig.BONES:
		if only.is_empty() or entry[0] in only:
			bones.append(entry[0])
	var tracks := {}
	for bone in bones:
		var track := animation.add_track(Animation.TYPE_ROTATION_3D)
		animation.track_set_path(track, NodePath("Skeleton3D:" + bone))
		tracks[bone] = track
	var moved := {}
	for bone: StringName in [&"Root", &"Hips"]:
		if bone in bones:
			var track := animation.add_track(Animation.TYPE_POSITION_3D)
			animation.track_set_path(track, NodePath("Skeleton3D:" + bone))
			moved[bone] = track
	var frames := maxi(ceili(length * FPS), 1)
	var last := {}
	for frame in frames + 1:
		var time := length * frame / frames
		var pose: Pose = pose_at.call(time)
		for bone in bones:
			var turn: Quaternion = pose.rotations[bone]
			# Keep each key on the same side as the one before, so a key
			# never swings the long way round to the next.
			if last.has(bone) and (last[bone] as Quaternion).dot(turn) < 0.0:
				turn = -turn
			last[bone] = turn
			animation.rotation_track_insert_key(tracks[bone], time, turn)
		for bone: StringName in moved:
			var offset: Vector3 = pose.root if bone == &"Root" else pose.hips
			animation.position_track_insert_key(moved[bone], time, (_rest[bone] + offset) * scale)
	# Drop the keys a straight blend between their neighbours would give anyway.
	animation.optimize(0.005, 0.005)
	return animation


## Where [param keys] are at [param time]: each key is [code][time, value][/code],
## in order, and the value eases from one key to the next. Values are floats
## or vectors.
static func _keyed(keys: Array, time: float) -> Variant:
	if time <= keys[0][0]:
		return keys[0][1]
	for index in range(1, keys.size()):
		if time <= keys[index][0]:
			var from: Array = keys[index - 1]
			var to: Array = keys[index]
			var along := smoothstep(0.0, 1.0, (time - from[0]) / maxf(to[0] - from[0], 0.0001))
			return lerp(from[1], to[1], along)
	return keys[-1][1]


# --- Poses -------------------------------------------------------------------

## A pose being built: every bone's rotation from its parent, and how far the
## root and the hips are moved from where they rest.
class Pose:
	var rotations := {}
	var root := Vector3.ZERO
	var hips := Vector3.ZERO
	var _parent: Dictionary
	var _rest: Dictionary
	var _globals := {}

	func _init(parents: Dictionary, rests: Dictionary) -> void:
		_parent = parents
		_rest = rests
		for bone: StringName in parents:
			rotations[bone] = Quaternion.IDENTITY

	## Sets [param bone]'s rotation from its parent, in degrees about x, y, z
	## (yaw first, then pitch, then roll, as [method Basis.from_euler] has it).
	func turn(bone: StringName, degrees: Vector3) -> Pose:
		rotations[bone] = Quaternion.from_euler(degrees * (PI / 180.0))
		_globals.clear()
		return self

	func move(root_offset: Vector3, hips_offset: Vector3) -> Pose:
		root = root_offset
		hips = hips_offset
		_globals.clear()
		return self

	## Where [param bone] is, and how it is turned, in the model's space.
	func at(bone: StringName) -> Transform3D:
		if _globals.has(bone):
			return _globals[bone]
		var offset: Vector3 = _rest[bone]
		if bone == &"Root":
			offset += root
		elif bone == &"Hips":
			offset += hips
		var local := Transform3D(Basis(rotations[bone]), offset)
		var parent: StringName = _parent[bone]
		var global := local if parent == &"" else at(parent) * local
		_globals[bone] = global
		return global

	## Turns [param bone] so it ends up turned [param basis] in the model's space.
	func face(bone: StringName, basis: Basis) -> void:
		var parent := at(_parent[bone]).basis
		rotations[bone] = (parent.inverse() * basis).orthonormalized().get_rotation_quaternion()
		_globals.clear()

	## Bends the limb from [param upper] through [param lower] to [param end] so
	## that [param effector], a point in [param end]'s own space, lands on
	## [param target], with the middle joint pointing toward [param pole]. If
	## [param end_basis] is given, the end bone is turned that way in the
	## model's space; otherwise it carries straight on from [param lower]. A
	## target out of reach leaves the limb straight toward it.
	func reach(upper: StringName, lower: StringName, end: StringName, target: Vector3, pole: Vector3,
			hinge_at_rest: Vector3, effector := Vector3.ZERO, end_basis: Variant = null) -> void:
		var base := at(_parent[upper])
		var start: Vector3 = base * (_rest[upper] as Vector3)
		var upper_dir: Vector3 = (_rest[lower] as Vector3).normalized()
		var length_1: float = (_rest[lower] as Vector3).length()
		var lower_span: Vector3 = _rest[end]
		var goal := target
		if end_basis != null:
			goal = target - (end_basis as Basis) * effector
		else:
			lower_span += effector
		var length_2 := lower_span.length()
		var lower_dir := lower_span.normalized()

		var to_goal := goal - start
		var distance := clampf(to_goal.length(), absf(length_1 - length_2) + 0.001, length_1 + length_2 - 0.001)
		var toward := to_goal.normalized() if not to_goal.is_zero_approx() else Vector3.DOWN
		var along := (length_1 * length_1 - length_2 * length_2 + distance * distance) / (2.0 * distance)
		var out := sqrt(maxf(length_1 * length_1 - along * along, 0.0))
		var side := pole - toward * toward.dot(pole)
		if side.is_zero_approx():
			side = toward.cross(Vector3.RIGHT if absf(toward.x) < 0.9 else Vector3.UP)
		side = side.normalized()
		var middle := start + toward * along + side * out
		var finish := start + toward * distance
		var hinge := (middle - start).cross(finish - middle)
		if hinge.length_squared() < 1e-6:
			hinge = side.cross(toward)
		hinge = hinge.normalized()

		var upper_basis := _frame(middle - start, hinge) * _frame(upper_dir, hinge_at_rest).inverse()
		var lower_basis := _frame(finish - middle, hinge) * _frame(lower_dir, hinge_at_rest).inverse()
		rotations[upper] = (base.basis.inverse() * upper_basis).orthonormalized().get_rotation_quaternion()
		rotations[lower] = (upper_basis.inverse() * lower_basis).orthonormalized().get_rotation_quaternion()
		if end_basis != null:
			rotations[end] = (lower_basis.inverse() * (end_basis as Basis)).orthonormalized().get_rotation_quaternion()
		else:
			rotations[end] = Quaternion.IDENTITY
		_globals.clear()

	## An orthonormal basis whose x is [param along] and whose y is as near
	## [param hinge] as it can be.
	static func _frame(along: Vector3, hinge: Vector3) -> Basis:
		var x := along.normalized()
		var y := (hinge - x * x.dot(hinge)).normalized()
		return Basis(x, y, x.cross(y))


func _pose() -> Pose:
	return Pose.new(_parent, _rest)


## The way each limb's middle joint bends at rest: an elbow brings the forearm
## forward, a knee the shin back. See [method Pose.reach].
const ELBOW_LEFT := Vector3.DOWN
const ELBOW_RIGHT := Vector3.UP
const KNEE := Vector3.RIGHT


## Stands [param side]'s foot with its ankle at [param ankle], turned
## [param yaw] degrees out and pitched [param pitch] degrees toes down, the
## knee over the toes, or toward [param knee] if given (down, to kneel).
func _foot(pose: Pose, side: StringName, ankle: Vector3, yaw := 0.0, pitch := 0.0, knee := Vector3.ZERO) -> void:
	var turn := Basis.from_euler(Vector3(deg_to_rad(pitch), deg_to_rad(yaw), 0.0))
	if knee.is_zero_approx():
		knee = Basis(Vector3.UP, deg_to_rad(yaw)) * Vector3.BACK + Vector3.UP * 0.2
	pose.reach(StringName(side + "UpperLeg"), StringName(side + "LowerLeg"), StringName(side + "Foot"),
		ankle, knee, KNEE, Vector3.ZERO, turn)


## The ankle over a point on the floor, for a flat foot.
func _ankle(on_floor: Vector3) -> Vector3:
	return on_floor + Vector3.UP * rig.joints[&"LeftFoot"].y


## Puts [param side]'s palm on [param palm] with the elbow toward [param pole],
## the hand turned [param basis] in the model's space if given, else carrying
## straight on from the forearm.
func _hand(pose: Pose, side: StringName, palm: Vector3, pole: Vector3, basis: Variant = null) -> void:
	pose.reach(StringName(side + "UpperArm"), StringName(side + "LowerArm"), StringName(side + "Hand"),
		palm, pole, ELBOW_LEFT if side == &"Left" else ELBOW_RIGHT, _palm[side], basis)


## Puts a prop held by [param side]'s hand at [param item] (its grip, turned as
## it stands) in the model's space, through [param grip].
func _hold(pose: Pose, side: StringName, item: Transform3D, grip: Transform3D, pole: Vector3) -> void:
	var hand := item * grip.affine_inverse()
	pose.reach(StringName(side + "UpperArm"), StringName(side + "LowerArm"), StringName(side + "Hand"),
		hand.origin, pole, ELBOW_LEFT if side == &"Left" else ELBOW_RIGHT, Vector3.ZERO, hand.basis)


## A prop's stance: its grip at [param grip], pointing [param forward] with its
## top toward [param up].
static func _item(grip: Vector3, forward: Vector3, up := Vector3.UP) -> Transform3D:
	return Transform3D(Basis.looking_at(forward, up, true), grip)


## The rifle in both hands at [param rifle_in_chest], a stance relative to the
## chest, so it rides the body.
func _rifle(pose: Pose, rifle_in_chest: Transform3D, right_pole := Vector3(-1, -1, -0.3), left_pole := Vector3(1, -1, 0)) -> void:
	var rifle := pose.at(&"Chest") * rifle_in_chest
	_hold(pose, &"Right", rifle, rifle_grip, right_pole)
	_hand(pose, &"Left", rifle * rifle_foregrip, left_pole)


## Carried at the ready: across the body, muzzle down and to the left.
func _low_ready() -> Transform3D:
	return _item(Vector3(-1.5, -0.5, 3.0), Vector3(0.55, -0.35, 0.75))


## At the shoulder, aimed straight ahead, the stock tucked under the chin.
func _shouldered() -> Transform3D:
	return _item(Vector3(0.0, 2.0, 4.3), Vector3(0, 0, 1))


## The torso and head: [param lean] degrees forward, [param turn] degrees to
## the left, [param tilt] to the right, shared out between the spine and chest,
## with the head turned back by [param steady] of it so it looks where it was.
func _torso(pose: Pose, lean: float, turn := 0.0, tilt := 0.0, steady := 0.6) -> void:
	pose.turn(&"Spine", Vector3(lean * 0.45, turn * 0.4, tilt * 0.5))
	pose.turn(&"Chest", Vector3(lean * 0.55, turn * 0.6, tilt * 0.5))
	pose.turn(&"Neck", Vector3(-lean * steady * 0.4, -turn * steady * 0.5, -tilt * steady * 0.5))
	pose.turn(&"Head", Vector3(-lean * steady * 0.6, -turn * steady * 0.5, -tilt * steady * 0.5))


## What the right hand (and the left, when free) does with [param stance]'s
## weapon while standing about: the rifle carried at the ready, the sword low
## at the side, or empty hands hanging.
func _carry(pose: Pose, stance: StringName, sway: float, left_free := false) -> void:
	match stance:
		&"rifle":
			if left_free:
				# One hand, hanging at the side, muzzle down.
				var hip := pose.at(&"Hips")
				var rifle := hip * _item(Vector3(-4.6, 2.5 + sway * 0.2, 2.0), Vector3(-0.1, -0.5, 0.86))
				_hold(pose, &"Right", rifle, rifle_grip, Vector3(-0.6, 0, -1))
			else:
				_rifle(pose, _low_ready().rotated_local(Vector3.RIGHT, deg_to_rad(sway * 2.0)))
		&"melee":
			var hip := pose.at(&"Hips")
			var sword := hip * _item(Vector3(-4.8, 2.0 + sway * 0.2, 2.0), Vector3(0.15, -0.45, 0.88), Vector3(0, 0.6, -0.2))
			_hold(pose, &"Right", sword, sword_grip, Vector3(-0.5, 0, -1))
			if not left_free:
				_hand(pose, &"Left", hip * Vector3(4.6, 1.5 + sway * 0.2, 0.8), Vector3(0.3, 0, -1))
		_:
			var hip := pose.at(&"Hips")
			_hand(pose, &"Right", hip * Vector3(-4.6, 1.8 + sway * 0.2, 1.0), Vector3(-0.3, 0, -1))
			if not left_free:
				_hand(pose, &"Left", hip * Vector3(4.6, 1.8 + sway * 0.2, 1.0), Vector3(0.3, 0, -1))


## Standing about, breathing.
func _stand(time: float, stance: StringName) -> Pose:
	var pose := _pose()
	var breath := sin(TAU * time / 2.4)
	var drift := sin(TAU * time / 4.8)
	pose.move(Vector3.ZERO, Vector3(0.2 * drift, -0.5 + 0.15 * breath, 0.0))
	pose.turn(&"Hips", Vector3(0, -8.0 + drift * 2.0, 0))
	_torso(pose, 4.0 + breath * 1.2, 8.0 - drift * 2.0, 0.0, 0.5)
	pose.turn(&"Head", Vector3(-2.0, drift * 6.0, 0))
	_foot(pose, &"Left", _ankle(Vector3(2.0, 0, 1.2)), 8.0)
	_foot(pose, &"Right", _ankle(Vector3(-2.0, 0, -0.8)), -14.0)
	_carry(pose, stance, breath)
	return pose


## Down on one knee behind low cover: the right knee on the floor, the left foot
## planted ahead. On overwatch, [param aiming], the rifle is shouldered over it.
##
## With [param side] it is leaning out round the end of that cover instead, to
## its left (1) or its right (-1), as a character does for as long as someone
## has a shot lined up at it that sees it there: shuffled [constant LEAN_STEP]
## along the cover on its knee, its weight over that side and its head and
## shoulders tipped out past the edge, looking round it.
func _crouch(time: float, stance: StringName, aiming: bool, side := 0.0) -> Pose:
	var pose := _pose()
	var breath := sin(TAU * time / 2.8)
	var hips_y: float = 5.0 - rig.joints[&"Hips"].y
	# How far along the cover the knee and the planted foot have shuffled. The
	# hips sit a little toward the kneeling knee, or over the side leaned to.
	var out := side * LEAN_STEP
	pose.move(Vector3.ZERO, Vector3(out + side * 1.2 - 0.4 * (1.0 - absf(side)), hips_y + 0.12 * breath, -1.2))
	pose.turn(&"Hips", Vector3(0, -6.0 + side * 6.0, side * -5.0))
	# The kneeling shin lies along the floor, the foot behind it toes down.
	_foot(pose, &"Right", _ankle(Vector3(out - 2.2, 0.4, -6.2)), -4.0, 55.0, Vector3(0, -1, 0.7))
	_foot(pose, &"Left", _ankle(Vector3(out + 2.0, 0, 2.6)), 6.0)
	if aiming:
		var scan := sin(TAU * time / 4.0)
		_torso(pose, 8.0, scan * 10.0, 0.0, 0.2)
		_rifle(pose, _shouldered().rotated_local(Vector3.RIGHT, deg_to_rad(5.0)))
		pose.turn(&"Head", Vector3(-6.0, scan * 6.0, 0))
	else:
		_torso(pose, 10.0 + breath, 6.0 + side * 8.0, side * -18.0, 0.5)
		if side != 0.0:
			# Round the edge, not at the cover in front.
			pose.turn(&"Head", Vector3(-4.0, side * 16.0, side * 4.0))
		match stance:
			&"rifle":
				_rifle(pose, _item(Vector3(-1.0, -0.5, 3.0), Vector3(0.45, 0.35, 0.8)).rotated_local(Vector3.RIGHT, deg_to_rad(breath)))
			&"melee":
				var hip := pose.at(&"Hips")
				var sword := hip * _item(Vector3(-3.5, 3.0, 4.0), Vector3(0.1, 0.9, 0.35), Vector3(0, 0, 1))
				_hold(pose, &"Right", sword, sword_grip, Vector3(-1, -0.5, -0.5))
				_hand(pose, &"Left", _ankle(Vector3(out + 2.0, 4.6, 3.2)) + Vector3(0, 0.4 * breath, 0), Vector3(1, 0, -0.2))
			_:
				_hand(pose, &"Right", _ankle(Vector3(out + 0.0, 4.4, 3.6)), Vector3(-1, 0, -0.5))
				_hand(pose, &"Left", _ankle(Vector3(out + 2.2, 4.6, 3.0)), Vector3(1, 0, -0.5))
	return pose


## Up close behind high cover, leaning into it, the weapon held upright ready to
## lean out with.
##
## With [param side] it has leaned out with it, round the end of the cover to
## its left (1) or its right (-1), as a character does for as long as someone
## has a shot lined up at it that sees it there: a step of
## [constant LEAN_STEP] along the wall to its edge, the weight over the outside
## foot, and the head and shoulders tipped out past the edge, looking round it.
func _wall(time: float, stance: StringName, side := 0.0) -> Pose:
	var pose := _pose()
	var breath := sin(TAU * time / 2.6)
	# How far along the wall the feet have gone, and how far down the lean
	# takes the hips.
	var out := side * LEAN_STEP
	var sink := absf(side) * 0.6
	pose.move(Vector3.ZERO, Vector3(out + side * 1.8, -1.0 - sink + 0.12 * breath, 0.6))
	pose.turn(&"Hips", Vector3(0, -4.0 + side * 8.0, side * -5.0))
	_torso(pose, 9.0 + breath, 4.0 + side * 8.0, side * -18.0, 0.6)
	pose.turn(&"Head", Vector3(-6.0, side * 16.0, side * 4.0))
	_foot(pose, &"Left", _ankle(Vector3(out + 2.2 + side * 0.6, 0, 0.6)), 6.0 + maxf(side, 0.0) * 12.0)
	_foot(pose, &"Right", _ankle(Vector3(out - 2.2 + side * 0.6, 0, -1.4)), -10.0 + minf(side, 0.0) * 12.0)
	match stance:
		&"rifle":
			_rifle(pose, _item(Vector3(-1.2, 0.2, 3.2), Vector3(0.15, 1.0, 0.25), Vector3(0, 0, 1)), Vector3(-1, -1, 0), Vector3(1, -1, 0))
		&"melee":
			var sword := pose.at(&"Chest") * _item(Vector3(-1.0, 0.0, 3.4), Vector3(0.05, 1.0, 0.15), Vector3(0, 0, 1))
			_hold(pose, &"Right", sword, sword_grip, Vector3(-1, -1, 0))
			_hand(pose, &"Left", pose.at(&"Chest") * Vector3(1.2, 0.4, 3.4), Vector3(1, -1, 0))
		_:
			var chest := pose.at(&"Chest")
			_hand(pose, &"Right", chest * Vector3(-1.4, 1.8 + 0.2 * breath, 3.6), Vector3(-1, -1, 0))
			_hand(pose, &"Left", chest * Vector3(1.4, 1.8 + 0.2 * breath, 3.6), Vector3(1, -1, 0))
	return pose


## Hunkered down behind cover of either height: on one knee as behind low
## cover, but lower, bent well over the knee with the head bowed, and the weapon
## hugged upright to the chest; with nothing in hand, the hands clasped over the
## back of the head.
func _hunker(time: float, stance: StringName) -> Pose:
	var pose := _pose()
	var breath := sin(TAU * time / 3.2)
	var hips_y: float = 3.6 - rig.joints[&"Hips"].y
	pose.move(Vector3.ZERO, Vector3(-0.4, hips_y + 0.1 * breath, -1.8))
	pose.turn(&"Hips", Vector3(0, -6.0, 0))
	# The crouch's legs, the knee on the floor drawn in under the body.
	_foot(pose, &"Right", _ankle(Vector3(-2.2, 0.4, -6.6)), -4.0, 55.0, Vector3(0, -1, 0.7))
	_foot(pose, &"Left", _ankle(Vector3(2.0, 0, 2.0)), 6.0)
	_torso(pose, 36.0 + breath * 1.5, 4.0, 0.0, 0.0)
	pose.turn(&"Neck", Vector3(10.0, 0, 0))
	pose.turn(&"Head", Vector3(14.0, 0, 0))
	match stance:
		&"rifle":
			_rifle(pose, _item(Vector3(-1.0, -0.5, 2.6), Vector3(0.1, 1.0, 0.1), Vector3(0, 0, 1)), Vector3(-1, -1, -0.3), Vector3(1, -1, 0))
		&"melee":
			var chest := pose.at(&"Chest")
			var sword := chest * _item(Vector3(-1.0, -1.0, 2.8), Vector3(0.05, 1.0, 0.1), Vector3(0, 0, 1))
			_hold(pose, &"Right", sword, sword_grip, Vector3(-1, -1, 0))
			_hand(pose, &"Left", chest * Vector3(1.2, -0.4, 2.8), Vector3(1, -1, 0))
		_:
			var head := pose.at(&"Head")
			_hand(pose, &"Right", head * Vector3(-1.6, 4.0, -0.5), Vector3(-1, 0.3, 0.5))
			_hand(pose, &"Left", head * Vector3(1.6, 4.0, -0.5), Vector3(1, 0.3, 0.5))
	return pose


## Shouldering the rifle and looking down its sights. On overwatch
## ([param watch] 1) it is lowered a touch and swept slowly from side to side.
func _aim(time: float, watch: float) -> Pose:
	var pose := _pose()
	var breath := sin(TAU * time / 3.0)
	var scan := sin(TAU * time / 4.0) * watch
	pose.move(Vector3.ZERO, Vector3(0.0, -1.2 + 0.1 * breath, -0.3))
	pose.turn(&"Hips", Vector3(0, -12.0 + scan * 4.0, 0))
	_torso(pose, 6.0 + watch * 6.0 + breath * 0.5, 12.0 + scan * 14.0, 0.0, 0.0)
	pose.turn(&"Neck", Vector3(-2.0, -4.0, 0))
	pose.turn(&"Head", Vector3(-4.0 - watch * 4.0, -6.0 + scan * 6.0, 0))
	_foot(pose, &"Left", _ankle(Vector3(2.2, 0, 2.6)), 4.0)
	_foot(pose, &"Right", _ankle(Vector3(-2.2, 0, -2.6)), -22.0)
	_rifle(pose, _shouldered().rotated_local(Vector3.RIGHT, deg_to_rad(watch * 6.0)), Vector3(-1.2, -1, 0), Vector3(1, -1, 0))
	return pose


## Where a foot is through a run cycle, [param phase] 0 to 1 from the moment it
## touches down, in the model's space: planted and swept back under the body
## as the ground goes by, then kicked up behind and swung forward again.
## Returns [code][ankle, pitch][/code].
func _stride(phase: float, x: float) -> Array:
	var stance := 0.27
	# The ground goes by at the run's speed, so a planted foot sweeps back the
	# share of a cycle's ground that its stance lasts.
	var reach := _cycle() * RUN_SPEED / scale * stance * 0.5
	if phase < stance:
		var along := phase / stance
		var lift := smoothstep(0.65, 1.0, along) * 1.2
		return [_ankle(Vector3(x, lift, lerpf(reach, -reach, along))), smoothstep(0.6, 1.0, along) * 35.0]
	var swing := (phase - stance) / (1.0 - stance)
	var forward := lerpf(-reach, reach * 1.1, smoothstep(0.1, 0.85, swing))
	var height := sin(PI * swing) * 4.2 + sin(PI * minf(swing * 2.0, 1.0)) * 1.2
	return [_ankle(Vector3(x, height, forward)), lerpf(35.0, -15.0, smoothstep(0.0, 0.8, swing))]


## Running, at [constant RUN_SPEED]: a stride a tile, leaning into it.
func _run(time: float, stance: StringName) -> Pose:
	var pose := _pose()
	var phase := fposmod(time / _cycle(), 1.0)
	var bob := -cos(TAU * 2.0 * (phase - 0.135))
	pose.move(Vector3.ZERO, Vector3(0, -1.4 + 0.55 * bob, 0.6))
	var swing := sin(TAU * phase)
	pose.turn(&"Hips", Vector3(4.0, swing * 9.0, 0))
	_torso(pose, 10.0 + bob * 1.5, -swing * 16.0, 0.0, 0.8)
	var right: Array = _stride(phase, -1.6)
	var left: Array = _stride(fposmod(phase + 0.5, 1.0), 1.6)
	_foot(pose, &"Right", right[0], -4.0, right[1])
	_foot(pose, &"Left", left[0], 4.0, left[1])
	var pump := -swing
	match stance:
		&"rifle":
			_rifle(pose, _low_ready().rotated_local(Vector3.RIGHT, deg_to_rad(bob * 2.0)))
		&"melee":
			var hip := pose.at(&"Hips")
			var sword := hip * _item(Vector3(-4.8, 3.0 + pump * 0.6, -1.0 + pump * 1.5), Vector3(0.1, -0.35, -0.93), Vector3(0, 1, 0))
			_hold(pose, &"Right", sword, sword_grip, Vector3(-0.5, -0.3, -1))
			var chest := pose.at(&"Chest")
			_hand(pose, &"Left", chest * Vector3(3.6, -2.0 - pump * 0.8, 3.0 * pump), Vector3(0.6, -0.2, -1))
		_:
			var chest := pose.at(&"Chest")
			_hand(pose, &"Right", chest * Vector3(-3.8, -2.0 + pump * 0.8, -3.0 * pump), Vector3(-0.6, -0.2, -1))
			_hand(pose, &"Left", chest * Vector3(3.8, -2.0 - pump * 0.8, 3.0 * pump), Vector3(0.6, -0.2, -1))
	return pose


## Stepping out or back with the rifle up, still facing the target: shuffled
## steps that never cross, [param way] across the ground in the figure's own
## space (+y forward, +x to its left).
func _step(time: float, way: Vector2) -> Pose:
	var pose := _pose()
	var phase := fposmod(time / _cycle(), 1.0)
	var hop := absf(sin(TAU * phase))
	pose.move(Vector3.ZERO, Vector3(0, -1.6 + 0.5 * hop, -0.3))
	pose.turn(&"Hips", Vector3(0, -12.0, 0))
	_torso(pose, 8.0, 12.0, way.x * -4.0, 0.0)
	for index in 2:
		var side: StringName = [&"Left", &"Right"][index]
		var x: float = [2.4, -2.4][index]
		var z: float = [1.6, -1.6][index]
		var foot_phase := fposmod(phase + index * 0.5, 1.0)
		var shift := sin(TAU * foot_phase) * 2.6
		var lift := maxf(sin(TAU * foot_phase), 0.0) * 2.2
		var ankle := _ankle(Vector3(x + shift * way.x, lift, z + shift * way.y))
		_foot(pose, side, ankle, [4.0, -18.0][index])
	_rifle(pose, _shouldered(), Vector3(-1.2, -1, 0), Vector3(1, -1, 0))
	return pose


## The legs tucked up for a hop on to or off a ledge.
func _hop(time: float) -> Pose:
	var pose := _pose()
	var flutter := sin(TAU * time / 0.5)
	pose.move(Vector3.ZERO, Vector3(0, 0.5, 0))
	pose.turn(&"Hips", Vector3(-6.0, 0, 0))
	_torso(pose, 14.0, 0.0, 0.0, 0.6)
	_foot(pose, &"Left", Vector3(1.8, 5.0 + flutter * 0.3, 3.0), 0.0, -10.0)
	_foot(pose, &"Right", Vector3(-1.8, 4.0 - flutter * 0.3, -2.5), 0.0, 30.0)
	_carry(pose, &"unarmed", 0.0)
	return pose


## Dropping through a floor that gave way: arms flung up, legs kicking.
func _fall(time: float) -> Pose:
	var pose := _pose()
	var kick := sin(TAU * time / 0.6)
	pose.move(Vector3.ZERO, Vector3(0, 0, 0))
	pose.turn(&"Hips", Vector3(-10.0, 0, kick * 4.0))
	_torso(pose, -12.0, kick * 8.0, 0.0, 0.0)
	pose.turn(&"Head", Vector3(-10.0, 0, 0))
	_foot(pose, &"Left", Vector3(2.4, 2.6 + kick * 1.5, 2.0 + kick * 1.5), 10.0, -20.0)
	_foot(pose, &"Right", Vector3(-2.4, 2.6 - kick * 1.5, 2.0 - kick * 1.5), -10.0, -20.0)
	var chest := pose.at(&"Chest")
	_hand(pose, &"Right", chest * Vector3(-6.5, 7.0 + kick, 1.0), Vector3(-1, -0.5, -0.5))
	_hand(pose, &"Left", chest * Vector3(6.5, 7.0 - kick, 1.0), Vector3(1, -0.5, -0.5))
	return pose


## Victory: the weapon thrust overhead, bouncing on the toes.
func _cheer(time: float, stance: StringName) -> Pose:
	var pose := _pose()
	var beat := sin(TAU * time)
	var bounce := maxf(beat, 0.0)
	pose.move(Vector3.ZERO, Vector3(0, -0.8 + bounce * 1.2, 0))
	_torso(pose, 2.0, 6.0 * beat, 0.0, 0.0)
	pose.turn(&"Head", Vector3(-8.0, 0, 0))
	_foot(pose, &"Left", _ankle(Vector3(2.4, bounce * 0.8, 0.8)), 10.0, bounce * 20.0)
	_foot(pose, &"Right", _ankle(Vector3(-2.4, bounce * 0.8, -0.4)), -12.0, bounce * 20.0)
	var chest := pose.at(&"Chest")
	var pump := 0.5 + 0.5 * beat
	match stance:
		&"rifle":
			var rifle := chest * _item(Vector3(-6.5, 8.0 + pump * 1.5, 1.0), Vector3(0.35, 0.8, 0.45), Vector3(-0.5, 0, 1))
			_hold(pose, &"Right", rifle, rifle_grip, Vector3(-1, 0, -0.3))
		&"melee":
			var sword := chest * _item(Vector3(-6.5, 8.0 + pump * 1.5, 1.0), Vector3(0.25, 0.9, 0.35), Vector3(0, 0, 1))
			_hold(pose, &"Right", sword, sword_grip, Vector3(-1, 0, -0.3))
		_:
			_hand(pose, &"Right", chest * Vector3(-6.5, 8.0 + pump * 1.5, 1.5), Vector3(-1, 0, -0.3))
	# Clear of the head, which is wider than the shoulders.
	_hand(pose, &"Left", chest * Vector3(6.5, 7.0 + (1.0 - pump) * 2.0, 1.5), Vector3(1, 0, -0.3))
	return pose


## A thrown grenade, from the left hand. [param progress] below zero is the
## ready pose held while the throw is lined up: the grenade held up by the
## shoulder. Otherwise it is the throw, [param time] into it: wound back, the
## arm whips over the head to let go, and the body follows through.
func _throw(time: float, stance: StringName, progress: float) -> Pose:
	var pose := _pose()
	var ready := progress < 0.0
	var breath := sin(TAU * time / 2.0) if ready else 0.0
	# [time, twist (left shoulder back is +), weight forward, lean, hand x, y, z in the chest's space]
	var keys := [
		[0.00, Vector3(10.0, -0.3, 2.0), Vector3(3.2, 1.5, 3.4)],
		[0.22, Vector3(42.0, -1.6, -6.0), Vector3(5.0, 7.5, -4.2)],
		[0.36, Vector3(-18.0, 1.2, 12.0), Vector3(2.6, 9.5, 4.0)],
		[0.50, Vector3(-30.0, 1.8, 18.0), Vector3(-0.5, -1.5, 6.0)],
		[0.80, Vector3(10.0, -0.3, 2.0), Vector3(3.2, 1.5, 3.4)],
	]
	var body: Vector3 = keys[0][1] if ready else _keyed(keys.map(func(key: Array) -> Array: return [key[0], key[1]]), time)
	var hand: Vector3 = keys[0][2] if ready else _keyed(keys.map(func(key: Array) -> Array: return [key[0], key[2]]), time)
	pose.move(Vector3.ZERO, Vector3(0.0, -1.0 + 0.1 * breath - absf(body.y) * 0.3, body.y))
	pose.turn(&"Hips", Vector3(0, body.x * 0.4, 0))
	_torso(pose, body.z + breath, body.x * 0.6, 0.0, 0.5)
	pose.turn(&"Head", Vector3(-4.0, -body.x * 0.3, 0))
	_foot(pose, &"Right", _ankle(Vector3(-2.2, 0, 2.6)), -6.0)
	_foot(pose, &"Left", _ankle(Vector3(2.4, 0, -2.4)), 18.0)
	_carry(pose, stance, breath, true)
	var chest := pose.at(&"Chest")
	_hand(pose, &"Left", chest * (hand + Vector3(0, breath * 0.2, 0)), Vector3(1, -1, -0.6))
	return pose


## The sword. [param progress] below zero is the guard held while a strike is
## lined up: the blade raised by the right shoulder. Otherwise it is the strike,
## [param time] into it: drawn back, swept down across the body with a lunge
## (the blow lands at 0.27 s), and recovered to the guard.
func _strike(time: float, progress: float) -> Pose:
	var pose := _pose()
	var ready := progress < 0.0
	var breath := sin(TAU * time / 2.0) if ready else 0.0
	# [time, lunge forward, twist (+ left), lean]
	var body_keys := [
		[0.00, Vector3(0.0, 12.0, 6.0)],
		[0.14, Vector3(-1.5, 30.0, 0.0)],
		[0.27, Vector3(5.0, -28.0, 20.0)],
		[0.42, Vector3(5.5, -38.0, 24.0)],
		[0.75, Vector3(0.0, 12.0, 6.0)],
	]
	# [time, grip in the chest's space, blade direction, which way its edge faces]
	var sword_keys := [
		[0.00, Vector3(-4.2, 4.0, 2.5), Vector3(-0.15, 0.85, -0.5), Vector3(0, 0.5, 1)],
		[0.14, Vector3(-5.5, 7.0, -1.5), Vector3(0.1, 0.4, -0.91), Vector3(0, 1, 0.4)],
		[0.27, Vector3(0.0, -0.5, 6.0), Vector3(0.55, -0.45, 0.7), Vector3(0.5, -0.8, -0.1)],
		[0.42, Vector3(1.0, -2.5, 3.5), Vector3(0.75, -0.6, 0.25), Vector3(0.3, -0.6, -0.7)],
		[0.75, Vector3(-4.2, 4.0, 2.5), Vector3(-0.15, 0.85, -0.5), Vector3(0, 0.5, 1)],
	]
	var body: Vector3 = body_keys[0][1] if ready else _keyed(body_keys, time)
	var grip: Vector3 = sword_keys[0][1] if ready else _keyed(sword_keys.map(func(key: Array) -> Array: return [key[0], key[1]]), time)
	var blade: Vector3 = sword_keys[0][2] if ready else _keyed(sword_keys.map(func(key: Array) -> Array: return [key[0], key[2]]), time)
	var edge: Vector3 = sword_keys[0][3] if ready else _keyed(sword_keys.map(func(key: Array) -> Array: return [key[0], key[3]]), time)
	var root := Vector3(0, 0, body.x)
	pose.move(root, Vector3(0.0, -1.6 + 0.12 * breath - maxf(body.x, 0.0) * 0.15, 0.0))
	pose.turn(&"Hips", Vector3(0, body.y * 0.35, 0))
	_torso(pose, body.z + breath, body.y * 0.65, 0.0, 0.5)
	pose.turn(&"Head", Vector3(-4.0, -body.y * 0.25, 0))
	# The feet stay where they were planted while the root lunges over them,
	# but for the front foot, which steps into the blow.
	var step := clampf(body.x, 0.0, 5.0)
	_foot(pose, &"Left", _ankle(Vector3(2.4, 0, 2.6 + step * 0.4)) - root, 8.0)
	_foot(pose, &"Right", _ankle(Vector3(-2.2, 0, -2.4)) - root, -24.0)
	var chest := pose.at(&"Chest")
	var sword := chest * _item(grip + Vector3(0, breath * 0.3, 0), blade.normalized(), edge)
	_hold(pose, &"Right", sword, sword_grip, Vector3(-1, -0.6, -0.4))
	_hand(pose, &"Left", chest * Vector3(3.0, -0.5 + breath * 0.2, 4.5 - body.y * 0.05), Vector3(1, -1, -0.2))
	return pose


## Drawing the sword from the back ([param drawing]), or putting it away: the
## right hand goes up over the right shoulder, the swap happens there (see the
## [code]swap[/code] metadata), and the hand comes down with the other weapon.
func _draw(time: float, drawing: bool) -> Pose:
	var from := _strike(0.0, -1.0) if not drawing else _stand(0.0, &"rifle")
	var to := _stand(0.0, &"rifle") if not drawing else _strike(0.0, -1.0)
	var pose := _pose()
	var up := sin(PI * clampf(time / 0.38, 0.0, 1.0))
	var along := smoothstep(0.0, 1.0, time / 0.45)
	for bone: StringName in pose.rotations:
		pose.rotations[bone] = (from.rotations[bone] as Quaternion).slerp(to.rotations[bone], along)
	pose.move(from.root.lerp(to.root, along), from.hips.lerp(to.hips, along))
	# Reach over the right shoulder for the hilt.
	var chest := pose.at(&"Chest")
	var hilt := chest * Vector3(-2.8, 5.5, -1.5)
	var hand := pose.at(&"RightHand")
	_hand(pose, &"Right", (hand * _palm[&"Right"]).lerp(hilt, up), Vector3(-1, -0.4, -0.3), hand.basis)
	return pose


## Loading a fresh magazine, over the arms and head alone, everything placed
## from the chest so it rides whatever pose the body holds: the rifle comes up
## across the chest, rolled to show its underside to the left hand, which pulls
## the spent magazine from under the receiver, drops it by the hip, takes a
## fresh one from the belt and slaps it home (the [code]seat[/code] metadata,
## 0.78 s, when the gun is loaded), then goes back to the fore-end as the rifle
## returns to the ready. The head looks down at the work. The rifle model has
## no magazine of its own, so the hand mimes one just ahead of the grip.
func _reload(time: float) -> Pose:
	var pose := _pose()
	pose.move(Vector3.ZERO, Vector3(0.0, -0.5, 0.0))
	_torso(pose, 4.0, 8.0, 0.0, 0.5)
	var chest := pose.at(&"Chest")

	# The rifle, chest-relative: from the ready up to the reload hold, a jolt as
	# the magazine is slapped home, and back down.
	var ready := _low_ready()
	var hold := _item(Vector3(-2.4, -0.4, 3.8), Vector3(0.62, 0.48, 0.62), Vector3(-0.6, 0.6, -0.5))
	var up := smoothstep(0.0, 0.22, time) * (1.0 - smoothstep(0.88, 1.15, time))
	var rifle_in_chest := ready.interpolate_with(hold, up)
	var slap := smoothstep(0.74, 0.78, time) * (1.0 - smoothstep(0.78, 0.9, time))
	rifle_in_chest.origin += Vector3(0.0, 0.5, 0.0) * slap
	var rifle := chest * rifle_in_chest
	_hold(pose, &"Right", rifle, rifle_grip, Vector3(-1, -1, -0.3))

	# The left hand: each key a point in the rifle's space (true) or the
	# chest's (false), turned into the chest's as the rifle stands now.
	var well := Vector3(0.0, -1.4, 1.5)
	var keys := [
		[0.00, true, rifle_foregrip],
		[0.24, true, well],
		[0.40, false, Vector3(5.0, -5.0, 2.5)],
		[0.56, false, Vector3(3.6, -6.2, 1.2)],
		[0.72, true, well + Vector3(0.0, -1.8, 0.0)],
		[0.78, true, well + Vector3(0.0, 0.3, 0.0)],
		[0.98, true, rifle_foregrip],
		[1.20, true, rifle_foregrip],
	]
	var in_chest := keys.map(func(key: Array) -> Array:
		return [key[0], rifle_in_chest * (key[2] as Vector3) if key[1] else key[2]])
	_hand(pose, &"Left", chest * (_keyed(in_chest, time) as Vector3), Vector3(1, -1, 0))

	var look := smoothstep(0.1, 0.3, time) * (1.0 - smoothstep(0.85, 1.1, time))
	pose.turn(&"Neck", Vector3(6.0 * look, -4.0 * look, 0))
	pose.turn(&"Head", Vector3(14.0 * look, -10.0 * look, 0))
	return pose


## Using a medkit, over the left arm alone, placed from the chest so it rides
## whatever pose the body holds: the left hand reaches back to the belt for the
## medkit (taken in hand at the [code]take[/code] metadata, 0.24 s), brings it
## round and holds it out at arm's length toward the ally in front, who mends
## as it gets there ([code]apply[/code], 0.58 s), holds it there a moment, then
## hooks it back on the belt ([code]stow[/code], 1.18 s) and lets the arm hang.
## The right hand keeps whatever it held, which is why only the left arm is
## keyed. [param on_self] ([code]use_medkit_self[/code]) brings it to the
## figure's own front instead, pressed to its middle and pressed again, at the
## same moments.
func _medkit(time: float, on_self: bool) -> Pose:
	var pose := _pose()
	pose.move(Vector3.ZERO, Vector3(0.0, -0.5, 0.0))
	_torso(pose, 4.0, 8.0, 0.0, 0.5)
	var chest := pose.at(&"Chest")
	var belt := Vector3(4.2, -6.6, -1.2)
	var out := SELF_MEDKIT if on_self else Vector3(1.6, 1.2, 7.2)
	# Held out, it is pushed a little toward the ally; on itself, pressed in.
	var press := Vector3(0.0, -0.3, -0.5) if on_self else Vector3(0.0, -0.4, 0.3)
	var keys := [
		[0.00, Vector3(4.6, -5.6, 1.0)],
		[0.24, belt],
		[0.42, Vector3(3.6, -3.0, 4.0) if on_self else Vector3(3.4, -1.5, 5.0)],
		[0.58, out],
		[0.80, out + press],
		[0.98, out],
		[1.18, belt],
		[1.40, Vector3(4.6, -5.6, 1.0)],
	]
	_hand(pose, &"Left", chest * (_keyed(keys, time) as Vector3), Vector3(1, -1, -0.4))
	return pose


## The kick of a shot, added to the aim: the chest jolts back and settles.
func _fire(time: float) -> Pose:
	var pose := _pose()
	var kick := (1.0 - smoothstep(0.03, 0.28, time)) * smoothstep(0.0, 0.03, time)
	pose.turn(&"Spine", Vector3(-2.5 * kick, 0, 0))
	pose.turn(&"Chest", Vector3(-7.0 * kick, 1.5 * kick, 0))
	pose.turn(&"Neck", Vector3(-2.0 * kick, 0, 0))
	pose.turn(&"Head", Vector3(-3.0 * kick, 0, 0))
	return pose


## Flinching from a hit, added to whatever the body is doing: thrown back by a
## hit from in front ([param way] -1), forward by one from behind (+1).
func _hit(time: float, way: float) -> Pose:
	var pose := _pose()
	var jolt := (1.0 - smoothstep(0.05, 0.42, time)) * smoothstep(0.0, 0.05, time)
	pose.turn(&"Spine", Vector3(16.0 * way * jolt, 0, 6.0 * jolt))
	pose.turn(&"Chest", Vector3(22.0 * way * jolt, 9.0 * jolt, 0))
	pose.turn(&"Neck", Vector3(12.0 * way * jolt, 0, 0))
	pose.turn(&"Head", Vector3(24.0 * way * jolt, -12.0 * jolt, 9.0 * jolt))
	return pose


## Ducking a round that went wide, added to whatever the body is doing.
func _dodge(time: float) -> Pose:
	var pose := _pose()
	var duck := (1.0 - smoothstep(0.1, 0.4, time)) * smoothstep(0.0, 0.08, time)
	pose.turn(&"Spine", Vector3(10.0 * duck, 0, -10.0 * duck))
	pose.turn(&"Chest", Vector3(10.0 * duck, -6.0 * duck, -6.0 * duck))
	pose.turn(&"Neck", Vector3(6.0 * duck, 0, 0))
	pose.turn(&"Head", Vector3(10.0 * duck, 10.0 * duck, -8.0 * duck))
	return pose


## Landing from a fall, added to the stance it lands in: the knees buckle and
## the body comes back up.
func _land(time: float) -> Pose:
	var pose := _pose()
	var squash := (1.0 - smoothstep(0.08, 0.5, time)) * smoothstep(0.0, 0.06, time)
	pose.move(Vector3.ZERO, Vector3(0, -3.6 * squash, -0.8 * squash))
	pose.turn(&"Hips", Vector3(10.0 * squash, 0, 0))
	pose.turn(&"Spine", Vector3(12.0 * squash, 0, 0))
	pose.turn(&"Chest", Vector3(8.0 * squash, 0, 0))
	pose.turn(&"Head", Vector3(-10.0 * squash, 0, 0))
	pose.turn(&"LeftUpperLeg", Vector3(-48.0 * squash, 0, 0))
	pose.turn(&"RightUpperLeg", Vector3(-48.0 * squash, 0, 0))
	pose.turn(&"LeftLowerLeg", Vector3(80.0 * squash, 0, 0))
	pose.turn(&"RightLowerLeg", Vector3(80.0 * squash, 0, 0))
	pose.turn(&"LeftFoot", Vector3(-38.0 * squash, 0, 0))
	pose.turn(&"RightFoot", Vector3(-38.0 * squash, 0, 0))
	return pose
