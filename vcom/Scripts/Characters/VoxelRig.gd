## How a voxel character model becomes a rigged one: the humanoid skeleton every
## character shares, where its joints sit in one particular model, and which
## bone each of the model's voxels moves with.
##
## Every voxel follows exactly one bone, all the way, so a limb moves as a solid
## block and never bends or stretches: the action-figure look of segmented
## voxel characters. Each bone is meshed on its own, keeping the faces where it
## meets another bone, so a joint that bends shows the ends of the blocks it
## joins rather than a hole.
##
## A model's [i]layout[/i] says, for each bone, the joint it turns about and the
## voxels that are its. Joints are in rig voxels: Godot's axes, one unit a
## voxel, x across (the figure's left is +x), y up from the floor, z forward,
## with the origin under the middle of the figure. Regions are boxes in the
## model's own voxel coordinates, as MagicaVoxel counts them; the first bone
## whose box holds a voxel takes it. Bone names are Godot's
## [SkeletonProfileHumanoid] names, so the rig retargets like any humanoid.
##
## The rest pose is the model as drawn (a T-pose), and every bone rests
## unrotated, lined up with the model's axes, so an animation's rotations mean
## the same thing on every bone.
extends RefCounted

const VoxImporter := preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")

## Every bone, parent before child, as [code][name, parent][/code].
const BONES := [
	[&"Root", &""],
	[&"Hips", &"Root"],
	[&"Spine", &"Hips"],
	[&"Chest", &"Spine"],
	[&"Neck", &"Chest"],
	[&"Head", &"Neck"],
	[&"LeftUpperArm", &"Chest"],
	[&"LeftLowerArm", &"LeftUpperArm"],
	[&"LeftHand", &"LeftLowerArm"],
	[&"RightUpperArm", &"Chest"],
	[&"RightLowerArm", &"RightUpperArm"],
	[&"RightHand", &"RightLowerArm"],
	[&"LeftUpperLeg", &"Hips"],
	[&"LeftLowerLeg", &"LeftUpperLeg"],
	[&"LeftFoot", &"LeftLowerLeg"],
	[&"RightUpperLeg", &"Hips"],
	[&"RightLowerLeg", &"RightUpperLeg"],
	[&"RightFoot", &"RightLowerLeg"],
]

## [code]Characters/BaseCharacter.vox[/code]: the grey mannequin every unit
## wears for now, 25 voxels across its outstretched arms and 27 tall.
const BASE_CHARACTER := {
	## Godot units a voxel: what the plain import of the model used, so the
	## figure stands 1.7 cells tall.
	"scale": 0.063,
	"joints": {
		&"Root": Vector3(0, 0, 0),
		&"Hips": Vector3(0, 9, 0),
		&"Spine": Vector3(0, 12, 0),
		&"Chest": Vector3(0, 15, 0),
		&"Neck": Vector3(0, 19, 0),
		&"Head": Vector3(0, 20, 0),
		# A voxel in from where the arm meets the body, so that a lowered arm
		# hangs flush beside it instead of sinking into it.
		&"LeftUpperArm": Vector3(3.5, 18, 0),
		&"LeftLowerArm": Vector3(7.5, 18, 0),
		&"LeftHand": Vector3(10.5, 18, 0),
		&"RightUpperArm": Vector3(-3.5, 18, 0),
		&"RightLowerArm": Vector3(-7.5, 18, 0),
		&"RightHand": Vector3(-10.5, 18, 0),
		&"LeftUpperLeg": Vector3(1.5, 9, 0),
		&"LeftLowerLeg": Vector3(1.5, 5, 0),
		&"LeftFoot": Vector3(1.5, 1, 0),
		&"RightUpperLeg": Vector3(-1.5, 9, 0),
		&"RightLowerLeg": Vector3(-1.5, 5, 0),
		&"RightFoot": Vector3(-1.5, 1, 0),
	},
	## [code][bone, lowest corner, highest corner][/code], inclusive, in the
	## model's voxel coordinates (z up, the face toward -y).
	"regions": [
		[&"Head", Vector3i(0, 0, 20), Vector3i(255, 255, 255)],
		[&"Neck", Vector3i(0, 0, 19), Vector3i(255, 255, 19)],
		[&"RightHand", Vector3i(0, 0, 17), Vector3i(5, 255, 18)],
		[&"RightLowerArm", Vector3i(6, 0, 17), Vector3i(8, 255, 18)],
		[&"RightUpperArm", Vector3i(9, 0, 17), Vector3i(13, 255, 18)],
		[&"LeftHand", Vector3i(27, 0, 17), Vector3i(255, 255, 18)],
		[&"LeftLowerArm", Vector3i(24, 0, 17), Vector3i(26, 255, 18)],
		[&"LeftUpperArm", Vector3i(19, 0, 17), Vector3i(23, 255, 18)],
		[&"Chest", Vector3i(0, 0, 15), Vector3i(255, 255, 18)],
		[&"Spine", Vector3i(0, 0, 12), Vector3i(255, 255, 14)],
		[&"Hips", Vector3i(0, 0, 9), Vector3i(255, 255, 11)],
		[&"RightUpperLeg", Vector3i(0, 0, 5), Vector3i(16, 255, 8)],
		[&"LeftUpperLeg", Vector3i(17, 0, 5), Vector3i(255, 255, 8)],
		[&"RightLowerLeg", Vector3i(0, 0, 1), Vector3i(16, 255, 4)],
		[&"LeftLowerLeg", Vector3i(17, 0, 1), Vector3i(255, 255, 4)],
		[&"RightFoot", Vector3i(0, 0, 0), Vector3i(16, 255, 0)],
		[&"LeftFoot", Vector3i(17, 0, 0), Vector3i(255, 255, 0)],
	],
}

## The bones that get a body of their own when the character goes limp, as
## [code][bone, carried, twist axis, swing, twist, share][/code]: the bones
## riding along with it whose voxels its box takes in too, the way along the
## limb its joint twists about (in the bone's own space at rest), how far the
## joint swings off that axis and twists about it, in degrees, and its share of
## the weight. The first has no joint: it is what the rest hang from. Hands,
## feet and the head ride on the bones above them, which keeps the chain short
## enough for the solver to hold together.
const RAGDOLL := [
	[&"Hips", [], Vector3.UP, 0.0, 0.0, 0.16],
	[&"Spine", [], Vector3.UP, 20.0, 15.0, 0.12],
	[&"Chest", [], Vector3.UP, 20.0, 15.0, 0.14],
	[&"Neck", [&"Head"], Vector3.UP, 35.0, 30.0, 0.18],
	[&"LeftUpperArm", [], Vector3.RIGHT, 75.0, 30.0, 0.05],
	[&"LeftLowerArm", [&"LeftHand"], Vector3.RIGHT, 70.0, 20.0, 0.04],
	[&"RightUpperArm", [], Vector3.LEFT, 75.0, 30.0, 0.05],
	[&"RightLowerArm", [&"RightHand"], Vector3.LEFT, 70.0, 20.0, 0.04],
	[&"LeftUpperLeg", [], Vector3.DOWN, 55.0, 20.0, 0.055],
	[&"LeftLowerLeg", [&"LeftFoot"], Vector3.DOWN, 65.0, 10.0, 0.045],
	[&"RightUpperLeg", [], Vector3.DOWN, 55.0, 20.0, 0.055],
	[&"RightLowerLeg", [&"RightFoot"], Vector3.DOWN, 65.0, 10.0, 0.045],
]

## What a fallen body weighs, in kilograms, shared out by [constant RAGDOLL].
const RAGDOLL_MASS := 40.0

## The six faces of a cell, as the way each looks out.
const FACES: Array[Vector3i] = [
	Vector3i.RIGHT, Vector3i.LEFT, Vector3i.UP, Vector3i.DOWN, Vector3i.BACK, Vector3i.FORWARD,
]

## The layout this rig was made from.
var layout: Dictionary
## Godot units a voxel.
var scale := 1.0
## Bone name -> rig cell (Vector3i) -> colour: the voxels that move with it.
var cells := {}
## Bone name -> where its joint is, in rig voxels.
var joints := {}

## Rig cells are the model's voxels turned onto Godot's axes: (x, z, -y). This
## is where a cell's lowest corner lands, in rig voxels, less the cell itself:
## it puts the middle of the figure over the origin and its feet on the floor.
var _corner := Vector3.ZERO


## Reads the model at [param vox_path] and shares its voxels out between the
## bones of [param rig_layout]. Returns false if the file cannot be read. A
## voxel no region takes goes to the bone whose joint is nearest, with a
## warning, so a layout that misses a voxel still moves it with something.
func load_vox(vox_path: String, rig_layout: Dictionary) -> bool:
	var read: Dictionary = VoxImporter.new().read_vox_data(vox_path)
	if read["error"] != OK:
		push_error("VoxelRig: cannot read '%s' (%s)." % [vox_path, error_string(read["error"])])
		return false
	var vox = read["vox"]
	if vox.models.is_empty() or vox.models[0].voxels.is_empty():
		push_error("VoxelRig: '%s' has no voxels." % vox_path)
		return false
	var voxels := {}
	for at: Vector3 in vox.models[0].voxels:
		var index: int = vox.models[0].voxels[at]
		var color: Color = vox.colors[index] if index < vox.colors.size() else Color.WHITE
		voxels[Vector3i(at)] = color

	layout = rig_layout
	scale = rig_layout["scale"]
	joints = rig_layout["joints"]
	_share_out(voxels)
	return true


## Where [param bone]'s joint is, in Godot units in the model's space.
func joint(bone: StringName) -> Vector3:
	return joints[bone] * scale


## A [Skeleton3D] with every bone of [constant BONES], each resting unrotated
## at its joint.
func make_skeleton() -> Skeleton3D:
	var skeleton := Skeleton3D.new()
	skeleton.name = &"Skeleton3D"
	for entry: Array in BONES:
		var index := skeleton.add_bone(entry[0])
		var at := joint(entry[0])
		if entry[1] != &"":
			var parent := skeleton.find_bone(entry[1])
			skeleton.set_bone_parent(index, parent)
			at -= joint(entry[1])
		skeleton.set_bone_rest(index, Transform3D(Basis.IDENTITY, at))
	skeleton.reset_bone_poses()
	return skeleton


## The model as one mesh skinned to [param skeleton], every vertex weighted
## wholly to the bone its voxel belongs to. Faces between voxels of the same
## bone are left out and runs of them merged, as the plain importer does;
## faces between two bones are kept, since a joint that bends opens them up.
## Coloured by vertex, as the importer's meshes are.
func make_mesh(skeleton: Skeleton3D) -> ArrayMesh:
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var colors := PackedColorArray()
	var bones := PackedInt32Array()
	var weights := PackedFloat32Array()
	var indices := PackedInt32Array()
	for bone: StringName in cells:
		var index := skeleton.find_bone(bone)
		for face in FACES:
			for quad: Array in _quads(cells[bone], face):
				var first := vertices.size()
				for corner: Vector3 in quad[0]:
					vertices.append((corner + _corner) * scale)
					normals.append(Vector3(face))
					colors.append(quad[1])
					bones.append_array([index, 0, 0, 0])
					weights.append_array([1.0, 0.0, 0.0, 0.0])
				indices.append_array([first, first + 1, first + 2, first, first + 2, first + 3])

	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_COLOR] = colors
	arrays[Mesh.ARRAY_BONES] = bones
	arrays[Mesh.ARRAY_WEIGHTS] = weights
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var material := StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.vertex_color_is_srgb = true
	material.roughness = 1.0
	mesh.surface_set_material(0, material)
	return mesh


## The box, in Godot units in [param bone]'s own space at rest (its joint at the
## origin), that the bone's voxels fill. Empty for a bone with none.
func bone_box(bone: StringName) -> AABB:
	var box := AABB()
	var first := true
	for cell: Vector3i in cells.get(bone, {}):
		var voxel := AABB((Vector3(cell) + _corner) * scale, Vector3.ONE * scale)
		box = voxel if first else box.merge(voxel)
		first = false
	if first:
		return AABB()
	box.position -= joint(bone)
	return box


## How many voxels move with [param bone].
func voxel_count(bone: StringName) -> int:
	return cells.get(bone, {}).size()


## A [PhysicalBoneSimulator3D] for [param skeleton] with a [PhysicalBone3D] for
## each bone of [constant RAGDOLL], a box over its voxels and those of the bones
## it carries, weighing its share of [param mass] kilograms. It is left
## inactive, and the bodies on no physics layer, until the character falls.
func make_ragdoll(skeleton: Skeleton3D, mass: float) -> PhysicalBoneSimulator3D:
	var simulator := PhysicalBoneSimulator3D.new()
	simulator.name = &"Ragdoll"
	simulator.active = false
	for entry: Array in RAGDOLL:
		var bone: StringName = entry[0]
		var box := bone_box(bone)
		for carried: StringName in entry[1]:
			var offset := joint(carried) - joint(bone)
			var carried_box := bone_box(carried)
			carried_box.position += offset
			box = box.merge(carried_box)
		var body := PhysicalBone3D.new()
		body.name = "Physical Bone " + bone
		body.bone_name = bone
		body.mass = mass * entry[5]
		body.collision_layer = 0
		body.collision_mask = 0
		body.body_offset = Transform3D(Basis.IDENTITY, box.get_center())
		var shape := CollisionShape3D.new()
		shape.name = &"Box"
		var cube := BoxShape3D.new()
		cube.size = box.size
		shape.shape = cube
		body.add_child(shape)
		if entry[3] > 0.0:
			# A cone twist joint turns about its own x axis: point that along
			# the limb, from the joint, which is at the bone's origin.
			body.joint_type = PhysicalBone3D.JOINT_TYPE_CONE
			var along: Vector3 = entry[2]
			var turn := Basis(Quaternion(Vector3.RIGHT, along))
			body.joint_offset = Transform3D(turn, -box.get_center())
			body.set(&"joint_constraints/swing_span", entry[3])
			body.set(&"joint_constraints/twist_span", entry[4])
		simulator.add_child(body)
	return simulator


## Gives every voxel to its bone, and works out where the rig's cells sit.
func _share_out(voxels: Dictionary) -> void:
	var low := Vector3i(1 << 20, 1 << 20, 1 << 20)
	var high := -low
	for at: Vector3i in voxels:
		low = low.min(at)
		high = high.max(at)
	# Centred across (x) and front to back (y), standing on its lowest voxel.
	var center_x := (low.x + high.x + 1) * 0.5
	var center_y := (low.y + high.y + 1) * 0.5
	# Model voxel (x, y, z) spans x..x+1, and so on; as a rig cell (x, z, -y) it
	# spans -y-1..-y along z once turned, which the -1 here accounts for.
	_corner = Vector3(-center_x, -low.z, center_y - 1.0)

	for entry: Array in BONES:
		cells[entry[0]] = {}
	var missed := 0
	for at: Vector3i in voxels:
		var bone := _region_of(at)
		if bone == &"":
			bone = _nearest_joint(Vector3(at.x, at.z, -at.y) + _corner + Vector3.ONE * 0.5)
			missed += 1
		cells[bone][Vector3i(at.x, at.z, -at.y)] = voxels[at]
	if missed > 0:
		push_warning("VoxelRig: %d voxels are in no region; each went to the bone with the nearest joint." % missed)


## The bone whose region holds the model voxel [param at], or an empty name.
func _region_of(at: Vector3i) -> StringName:
	for region: Array in layout["regions"]:
		var low: Vector3i = region[1]
		var high: Vector3i = region[2]
		if at.x >= low.x and at.y >= low.y and at.z >= low.z and at.x <= high.x and at.y <= high.y and at.z <= high.z:
			return region[0]
	return &""


func _nearest_joint(point: Vector3) -> StringName:
	var best := &"Root"
	var best_distance := INF
	for bone: StringName in joints:
		var distance := point.distance_squared_to(joints[bone])
		if distance < best_distance:
			best = bone
			best_distance = distance
	return best


## The faces of [param bone_cells] looking out along [param face] that no cell
## of the same bone covers, merged into rectangles of one colour, as
## [code][corners, colour][/code] with the corners in rig voxels (less
## [member _corner]) and wound for Godot, clockwise seen from outside.
func _quads(bone_cells: Dictionary, face: Vector3i) -> Array:
	var axis := 0 if face.x != 0 else (1 if face.y != 0 else 2)
	var across := (axis + 1) % 3
	var up := (axis + 2) % 3
	# Slice (position along the axis, and colour) -> exposed (across, up) set.
	var slices := {}
	for cell: Vector3i in bone_cells:
		if bone_cells.has(cell + face):
			continue
		var key := [cell[axis], bone_cells[cell]]
		if not slices.has(key):
			slices[key] = {}
		slices[key][Vector2i(cell[across], cell[up])] = true

	var quads := []
	for key: Array in slices:
		var open: Dictionary = slices[key]
		var keys := open.keys()
		keys.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.y < b.y or (a.y == b.y and a.x < b.x))
		for start: Vector2i in keys:
			if not open.has(start):
				continue
			var width := 1
			while open.has(start + Vector2i(width, 0)):
				width += 1
			var height := 1
			while true:
				var row_full := true
				for step in width:
					if not open.has(start + Vector2i(step, height)):
						row_full = false
						break
				if not row_full:
					break
				height += 1
			for dy in height:
				for dx in width:
					open.erase(start + Vector2i(dx, dy))
			quads.append([_corners(axis, across, up, key[0] + (1 if face[axis] > 0 else 0), start, width, height, face), key[1]])
	return quads


## The four corners of the rectangle at [param depth] along [param axis],
## from [param start] [param width] across by [param height] up, in the order
## that makes it face [param face] in Godot.
func _corners(axis: int, across: int, up: int, depth: int, start: Vector2i, width: int, height: int, face: Vector3i) -> Array:
	var corners := []
	for offset: Vector2i in [Vector2i(0, 0), Vector2i(width, 0), Vector2i(width, height), Vector2i(0, height)]:
		var corner := Vector3.ZERO
		corner[axis] = depth
		corner[across] = start.x + offset.x
		corner[up] = start.y + offset.y
		corners.append(corner)
	# Godot draws a triangle's front where its corners run clockwise, which is
	# where the right-hand normal of the first two edges points away.
	var first: Vector3 = corners[0]
	var normal := (corners[1] - first).cross(corners[2] - first) as Vector3
	if normal.dot(Vector3(face)) > 0.0:
		corners.reverse()
	return corners
