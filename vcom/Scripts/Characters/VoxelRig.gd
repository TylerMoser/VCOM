## How a voxel character model becomes a rigged one: the humanoid skeleton every
## character shares, where its joints sit in one particular model, and which
## bone each of the model's voxels moves with.
##
## Every voxel follows exactly one bone, all the way, so a limb moves as a solid
## block and never bends or stretches: the action-figure look of segmented
## voxel characters. Each bone is meshed on its own, keeping the faces where it
## meets another bone, so a joint that bends shows the ends of the blocks it
## joins rather than a hole. The mesh is coloured as every voxel model is, by
## the voxel shader from a texture of the figure's voxels ([VoxelModel]), so a
## unit paints it in its colour and blood recolours it voxel by voxel.
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

## The layout of every model that has one, by the model's path: what
## [code]BakeCharacter.gd[/code] bakes it with, and what a figure reads its
## voxels by while the game runs ([FigureVoxels]).
const LAYOUTS := {
	"res://Characters/BaseCharacter.vox": BASE_CHARACTER,
}

## The layout this rig was made from.
var layout: Dictionary
## Godot units a voxel.
var scale := 1.0
## Bone name -> rig cell (Vector3i) -> the place of its colour in
## [member colors]: the voxels that move with it.
var cells := {}
## The model's palette, each colour at the place its voxels hold, as a
## [VoxelShape] keeps one.
var colors := PackedColorArray()
## The least and most rig cells of any voxel.
var least := Vector3i.ZERO
var most := Vector3i.ZERO
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
	# Each voxel's place, as VoxelShape counts them: its colour's in the file,
	# one up, 0 being none.
	var voxels := {}
	for at: Vector3 in vox.models[0].voxels:
		voxels[Vector3i(at)] = int(vox.models[0].voxels[at]) + 1
	colors.resize(256)
	for index in mini(vox.colors.size(), 255):
		colors[index + 1] = vox.colors[index]

	layout = rig_layout
	scale = rig_layout["scale"]
	joints = rig_layout["joints"]
	_share_out(voxels)
	return true


## Where [param bone]'s joint is, in Godot units in the model's space.
func joint(bone: StringName) -> Vector3:
	return joints[bone] * scale


## Where the least corner of the rig cell [param cell] is, in Godot units in
## the model's space: where its voxel is drawn from.
func voxel_corner(cell: Vector3i) -> Vector3:
	return (Vector3(cell) + _corner) * scale


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


## The figure as drawn, standing, as one voxel model ([VoxelShape]): its rig
## cells from the least, each holding the place of its colour, in the
## figure's space shrunk to a block's voxels ([member VoxelShape.scale]). What
## its body is coloured from, as it is baked ([method make_mesh]) and while the
## game runs ([FigureVoxels]).
func make_shape() -> VoxelShape:
	var shape := VoxelShape.new(most - least + Vector3i.ONE, (Vector3(least) + _corner) * VoxelShape.SCALE)
	shape.scale = scale / VoxelShape.SCALE
	shape.colors = colors.duplicate()
	for bone: StringName in cells:
		var bone_cells: Dictionary = cells[bone]
		for cell: Vector3i in bone_cells:
			shape.voxels[shape.index_of(cell - least)] = bone_cells[cell]
			shape.count += 1
	shape.reserve_blood()
	shape.rows = shape.rows_of(shape.voxels)
	return shape


## The model as one mesh skinned to [param skeleton], every vertex weighted
## wholly to the bone its voxel belongs to. Each bone is meshed on its own, as
## a level's chunk is ([ChunkMesher]): faces between voxels of the same bone
## left out and the rest merged by shape alone, faces between two bones kept,
## since a joint that bends opens them up. It is coloured by the voxel shader
## from the figure's voxels ([method make_shape]): each corner carries its
## voxel ([method ChunkMesher.arrays]), so the figure is coloured however it is
## posed. A unit draws it in its own colours ([VoxelModel]); its surface's
## material, which only the editor shows, is the model's commonest colour,
## flat, as no texture can be saved from a bake run headless, where the
## textures it made never reach a GPU to be read back.
func make_mesh(skeleton: Skeleton3D) -> ArrayMesh:
	var shape := make_shape()
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var places := PackedFloat32Array()
	var extents := PackedFloat32Array()
	var bones := PackedInt32Array()
	var weights := PackedFloat32Array()
	var offset := (Vector3(least) + _corner) * scale
	for bone: StringName in cells:
		var bone_cells: Dictionary = cells[bone]
		if bone_cells.is_empty():
			continue
		var own := PackedByteArray()
		own.resize(shape.length)
		for cell: Vector3i in bone_cells:
			own[shape.index_of(cell - least)] = 1
		var made := ChunkMesher.arrays(VoxelModel.rectangles_of(shape, shape.rows_of(own)), Vector3i.ZERO, 0, scale, offset)
		var corners: PackedVector3Array = made[Mesh.ARRAY_VERTEX]
		vertices.append_array(corners)
		normals.append_array(made[Mesh.ARRAY_NORMAL])
		places.append_array(made[Mesh.ARRAY_CUSTOM0])
		extents.append_array(made[Mesh.ARRAY_CUSTOM1])
		var index := skeleton.find_bone(bone)
		for corner in corners.size():
			bones.append_array([index, 0, 0, 0])
			weights.append_array([1.0, 0.0, 0.0, 0.0])

	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_CUSTOM0] = places
	arrays[Mesh.ARRAY_CUSTOM1] = extents
	arrays[Mesh.ARRAY_BONES] = bones
	arrays[Mesh.ARRAY_WEIGHTS] = weights
	@warning_ignore("integer_division")
	arrays[Mesh.ARRAY_INDEX] = ChunkMesher.index_array(vertices.size() / 4)
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, [], {}, ChunkMesher.format())
	var counts := PackedInt32Array()
	counts.resize(256)
	for held in shape.voxels:
		counts[held] += 1
	var commonest := 1
	for place in range(1, 256):
		if counts[place] > counts[commonest]:
			commonest = place
	var flat := StandardMaterial3D.new()
	flat.albedo_color = shape.colors[commonest]
	flat.roughness = 1.0
	mesh.surface_set_material(0, flat)
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
	least = Vector3i(low.x, low.z, -high.y)
	most = Vector3i(high.x, high.z, -low.y)

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
