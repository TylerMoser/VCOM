## Bakes a voxel character model into the rigged figure every unit wears: a
## [Skeleton3D] the model's voxels are skinned to, its animations, the tree
## that plays them, a ragdoll for when it falls, and the sockets its gear hangs
## from, all under a [CharacterModel]. Run from vcom/:
##
##   godot --headless --path . --script res://Scripts/Characters/BakeCharacter.gd
##   godot --headless --path . --script res://Scripts/Characters/BakeCharacter.gd -- <vox> <scene>
##
## (defaults: res://Characters/BaseCharacter.vox -> res://Scenes/BaseCharacter.tscn).
## Run it again after editing the model in MagicaVoxel, or after changing how
## it is rigged ([code]VoxelRig.gd[/code]) or animated
## ([code]HumanoidAnimations.gd[/code]). It overwrites the scene, and beside
## the model it writes the skinned mesh ([code]<model>Body.res[/code]) and the
## animations ([code]<model>Animations.res[/code]), so changes made to those in
## the editor are lost: change the scripts instead.
##
## A model needs a layout in [constant LAYOUTS]: where its joints are and which
## voxels each bone takes (see [code]VoxelRig.gd[/code]). One drawn to the base
## character's proportions can share its layout.
##
## A script error does not end a --script run: Godot sits idle after it, so
## give the run a timeout when scripting it.
extends SceneTree

const VoxelRig := preload("res://Scripts/Characters/VoxelRig.gd")
const HumanoidAnimations := preload("res://Scripts/Characters/HumanoidAnimations.gd")
const MODEL_SCRIPT := preload("res://Scripts/Characters/CharacterModel.gd")
const AIM_SCRIPT := preload("res://Scripts/Characters/AimModifier.gd")
## The rifle whose foregrip the left hand is posed to hold.
const RIFLE_SCENE := "res://Scenes/Props/Rifle.tscn"

const DEFAULT_VOX := "res://Characters/BaseCharacter.vox"
const DEFAULT_SCENE := "res://Scenes/BaseCharacter.tscn"
## Model -> its layout.
const LAYOUTS := {
	"res://Characters/BaseCharacter.vox": VoxelRig.BASE_CHARACTER,
}

## Where gear is carried when it is not in hand, in rig voxels in the space of
## the bone each hangs from: the gun slung across the back, muzzle up over the
## left shoulder; the sword across it the other way, its hilt over the right
## shoulder for the right hand to draw; grenades tucked into the back of the
## belt by their handles, heads up, the outer two leaning out 25 degrees so
## the three heads stand apart rather than in one block.
## Each is [code][bone, origin, forward (+z of the prop), its left (+x)][/code].
const SLOTS := {
	&"Back/RifleSlot": [&"Chest", Vector3(-1.25, -0.6, -2.6), Vector3(0.5, 0.85, 0.0), Vector3(0, 0, 1)],
	&"Back/SwordSlot": [&"Chest", Vector3(-2.5, 4.0, -2.2), Vector3(0.45, -0.9, 0.0), Vector3(0, 0, 1)],
	&"Belt/Grenade1": [&"Hips", Vector3(2.2, 1.5, -2.1), Vector3(0, 0, 1), Vector3(0.906, -0.423, 0)],
	&"Belt/Grenade2": [&"Hips", Vector3(-2.2, 1.5, -2.1), Vector3(0, 0, 1), Vector3(0.906, 0.423, 0)],
	&"Belt/Grenade3": [&"Hips", Vector3(0.0, 1.5, -2.7), Vector3(0, 0, 1), Vector3(1, 0, 0)],
}
## Grenades on the belt are shown smaller than one in hand, so three fit.
const BELT_SCALE := 0.8


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var vox_path: String = args[0] if args.size() > 0 else DEFAULT_VOX
	var scene_path: String = args[1] if args.size() > 1 else DEFAULT_SCENE
	quit(_bake(vox_path, scene_path))


func _bake(vox_path: String, scene_path: String) -> int:
	if not LAYOUTS.has(vox_path):
		push_error("BakeCharacter: no layout for '%s'; add one to LAYOUTS." % vox_path)
		return 1
	var rig := VoxelRig.new()
	if not rig.load_vox(vox_path, LAYOUTS[vox_path]):
		return 1
	var stem := vox_path.get_basename()

	var root := Node3D.new()
	root.name = vox_path.get_file().get_basename()
	root.set_script(MODEL_SCRIPT)

	var skeleton := rig.make_skeleton()
	_add(root, skeleton, root)

	var body := MeshInstance3D.new()
	body.name = &"Body"
	var mesh := rig.make_mesh(skeleton)
	if not _save(mesh, stem + "Body.res"):
		return 1
	body.mesh = mesh
	_add(skeleton, body, root)
	body.skeleton = NodePath("..")
	body.skin = skeleton.create_skin_from_rest_transforms()

	var aim := SkeletonModifier3D.new()
	aim.name = &"Aim"
	aim.set_script(AIM_SCRIPT)
	_add(skeleton, aim, root)

	var ragdoll := rig.make_ragdoll(skeleton, VoxelRig.RAGDOLL_MASS)
	_add(skeleton, ragdoll, root)

	var animations := HumanoidAnimations.new(rig)
	animations.read_rifle(load(RIFLE_SCENE))
	_sockets(skeleton, root, rig, animations)

	var library := animations.make_library()
	if not _save(library, stem + "Animations.res"):
		return 1
	var player := AnimationPlayer.new()
	player.name = &"AnimationPlayer"
	player.add_animation_library(&"", library)
	_add(root, player, root)

	var tree := AnimationTree.new()
	tree.name = &"AnimationTree"
	tree.tree_root = animations.make_tree()
	_add(root, tree, root)
	tree.anim_player = NodePath("../AnimationPlayer")
	tree.active = true

	var bone_count := skeleton.get_bone_count()
	var packed := PackedScene.new()
	var error := packed.pack(root)
	if error == OK:
		error = ResourceSaver.save(packed, scene_path)
	root.free()
	if error != OK:
		push_error("BakeCharacter: could not save '%s' (%s)." % [scene_path, error_string(error)])
		return 1
	var voxels := 0
	for bone: StringName in rig.cells:
		voxels += rig.voxel_count(bone)
	print("BakeCharacter: %s -> %s: %d voxels on %d bones, %d vertices, %d animations." % [
		vox_path, scene_path, voxels, bone_count,
		mesh.surface_get_array_len(0), library.get_animation_list().size(),
	])
	return 0


## The sockets the gear is put in: one in each hand, at the palm, turned as
## the animations hold that kind of item; and the slots of [constant SLOTS].
func _sockets(skeleton: Skeleton3D, root: Node, rig: VoxelRig, animations: HumanoidAnimations) -> void:
	var holders := {}
	for spec: Array in [[&"RightHand", &"RightHand"], [&"LeftHand", &"LeftHand"], [&"Back", &"Chest"], [&"Belt", &"Hips"]]:
		var attachment := BoneAttachment3D.new()
		attachment.name = spec[0]
		attachment.bone_name = spec[1]
		_add(skeleton, attachment, root)
		holders[spec[0]] = attachment
	_socket(holders[&"RightHand"], &"RifleGrip", animations.rifle_grip, rig.scale, root)
	_socket(holders[&"RightHand"], &"SwordGrip", animations.sword_grip, rig.scale, root)
	_socket(holders[&"LeftHand"], &"GrenadeGrip", animations.grenade_grip, rig.scale, root)
	for path: StringName in SLOTS:
		var spec: Array = SLOTS[path]
		var forward: Vector3 = (spec[2] as Vector3).normalized()
		var left: Vector3 = spec[3]
		var up := forward.cross(left).normalized()
		left = up.cross(forward).normalized()
		var slot := Transform3D(Basis(left, up, forward), spec[1])
		if String(path).begins_with("Belt"):
			slot.basis = slot.basis.scaled(Vector3.ONE * BELT_SCALE)
		var holder: Node = holders[StringName(String(path).get_slice("/", 0))]
		_socket(holder, StringName(String(path).get_slice("/", 1)), slot, rig.scale, root)


func _socket(holder: Node, socket_name: StringName, at: Transform3D, scale: float, root: Node) -> void:
	var socket := Node3D.new()
	socket.name = socket_name
	socket.transform = Transform3D(at.basis, at.origin * scale)
	_add(holder, socket, root)


func _add(parent: Node, child: Node, root: Node) -> void:
	parent.add_child(child)
	child.owner = root
	for node in child.find_children("*", "", true, false):
		node.owner = root


func _save(resource: Resource, path: String) -> bool:
	var error := ResourceSaver.save(resource, path)
	if error != OK:
		push_error("BakeCharacter: could not save '%s' (%s)." % [path, error_string(error)])
		return false
	resource.take_over_path(path)
	return true
