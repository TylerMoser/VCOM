## The faces of one voxel model that blood has stained, and the overlay that
## shows them: a red square over each, a hair proud of the face.
##
## Blood stains faces, not voxels: the top of the ground a pool lies on, not the
## side of the block under it unless the blood ran down that too. Each voxel's
## stained faces are the bits of one number, a bit for each way a face can look
## ([constant FACES]), kept by the voxel's place in its model's array
## ([VoxelShape]), so a model takes no room for blood until some lands on it.
##
## The model is still drawn by whatever drew it; the stains are drawn over it by
## an overlay of their own ([member overlay]), a [MeshInstance3D] in the model's
## frame holding just the stained faces. So blood landing never redraws a block
## or a figure, only the overlay, once at the end of the frame however much
## landed. A stain shows only while its voxel is there: one worn away takes its
## stain with it (its lump of debris is coloured as blood instead, see
## [VoxelTerrain]), and the faces wear lays bare are clean. A face is only ever
## stained while it is open to the air, and voxels are never added, so one
## stained stays open.
##
## Only for show, as debris is: nothing in the rules reads it.
class_name VoxelStains
extends RefCounted

## Bright red, as Fat Princess has it.
const COLOR := Color(0.78, 0.02, 0.03)
## How far proud of its face a stain is drawn, in metres: enough that the two
## never fight over which shows, too little to see.
const PROUD := 0.002
## The six ways a face can look, in the order of their bits: +x, -x, +y, -y, +z,
## -z. A face's opposite is its number with the lowest bit flipped.
const FACES: Array[Vector3i] = [
	Vector3i(1, 0, 0), Vector3i(-1, 0, 0), Vector3i(0, 1, 0),
	Vector3i(0, -1, 0), Vector3i(0, 0, 1), Vector3i(0, 0, -1),
]
## What an overlay is called, under whatever it is drawn over.
const OVERLAY := &"Stains"
## The metadata a model drawn by a mesh keeps its stains in ([method on]).
const KEPT := &"stains"

## What every stain, and every drop of blood in flight, is drawn with: a little
## glossy, so a pool catches the light as wet blood does, but not so much that
## the sun's glint on it washes it out.
static var material: StandardMaterial3D = _material()

## The model's kind: how its voxels are laid out.
var shape: VoxelShape
## Each stained voxel's faces, as bits, by its place in the array.
var faces := {}
## The model's voxel size over [constant VoxelShape.SCALE]: 1 for blocks and
## their pieces, a shade more for figures and props, which are drawn 0.063 a
## voxel. Its mesh space is the shape's frame grown by this.
var scale := 1.0
## Says which of the model's voxels are there now, as an array laid out as
## [member shape]'s. Unset, the kind's own are.
var voxels := Callable()
## What draws the stains, under the model ([method attach]).
var overlay: MeshInstance3D

## The voxel of each square the overlay was last built with, in order.
var _drawn_voxels := PackedInt32Array()
## Whether a redraw is waiting for the end of the frame.
var _queued := false


func _init(kind: VoxelShape, voxel_scale := 1.0) -> void:
	shape = kind
	scale = voxel_scale


## The bit of the face looking along [param direction], one of
## [constant FACES].
static func bit(direction: Vector3i) -> int:
	return 1 << FACES.find(direction)


## The stains of the voxel model [param drawn] shows, a mesh imported straight
## from a .vox, such as a prop: kept on it, made the first time they are asked
## for and drawn over it. Null if its mesh is not from a .vox.
static func on(drawn: MeshInstance3D) -> VoxelStains:
	if drawn.has_meta(KEPT):
		return drawn.get_meta(KEPT)
	var kind := shape_of(drawn)
	if kind == null:
		return null
	var stains := VoxelStains.new(kind, scale_of(drawn, kind))
	stains.attach(drawn)
	drawn.set_meta(KEPT, stains)
	return stains


## The voxels of the model [param drawn] shows, if its mesh was imported
## straight from a .vox; null if not. Shared by everything drawn by that mesh.
static func shape_of(drawn: MeshInstance3D) -> VoxelShape:
	if drawn.mesh == null or drawn.mesh.resource_path.get_extension().to_lower() != "vox":
		return null
	var kind := VoxelShape.read_mesh(drawn.mesh)
	return kind if kind != null and kind.count > 0 else null


## How much bigger the voxels [param drawn] shows are than a block's, its mesh
## being of [param kind]'s: props are imported at 0.063 a voxel, a shade more
## than the blocks' 0.0625, which what the mesh measures over what the shape
## does says.
static func scale_of(drawn: MeshInstance3D, kind: VoxelShape) -> float:
	return drawn.mesh.get_aabb().size.x / (kind.size.x * VoxelShape.SCALE)


## Where [member shape]'s voxels are laid out in the world, for a model whose
## mesh space is [param drawn]'s: that space, shrunk back to the shape's frame
## by [member scale].
func frame_on(drawn: Node3D) -> Transform3D:
	return drawn.global_transform * Transform3D(Basis.from_scale(Vector3.ONE * scale), Vector3.ZERO)


## Draws the stains under [param holder], at [param at] in it: the model's
## mesh space.
func attach(holder: Node, at := Transform3D.IDENTITY) -> void:
	overlay = MeshInstance3D.new()
	overlay.name = OVERLAY
	# Coplanar with what it lies on, so it would only shadow itself.
	overlay.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	holder.add_child(overlay)
	overlay.transform = at
	if not faces.is_empty():
		changed()


## Takes the overlay away: the model is gone, or its blood has gone on to
## whatever it broke into.
func detach() -> void:
	if overlay != null and is_instance_valid(overlay):
		overlay.queue_free()
	overlay = null


## The stained faces of the voxel at [param index], as bits.
func bits_at(index: int) -> int:
	return faces.get(index, 0)


## Whether any face is stained at all.
func is_empty() -> bool:
	return faces.is_empty()


## Stains the faces [param bits] of the voxel at [param index], and returns the
## bits that were not stained already. The overlay is redrawn at the end of the
## frame.
func stain(index: int, bits: int) -> int:
	var had: int = faces.get(index, 0)
	var added := bits & ~had
	if added != 0:
		faces[index] = had | added
		changed()
	return added


## Redraws the overlay at the end of the frame, once however many faces are
## stained or voxels worn away before then.
func changed() -> void:
	if _queued:
		return
	_queued = true
	redraw.call_deferred()


## Builds the overlay afresh from the faces stained now.
func redraw() -> void:
	_queued = false
	if overlay == null or not is_instance_valid(overlay):
		return
	var arrays: Variant = _arrays()
	if arrays == null:
		overlay.mesh = null
		return
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	mesh.surface_set_material(0, material)
	overlay.mesh = mesh


## The arrays of a mesh with a square over each stained face of a voxel that is
## there now, a hair proud of the face, in the model's mesh space; null if none
## shows. [member _drawn_voxels] is left holding each square's voxel.
func _arrays() -> Variant:
	var present: PackedByteArray = voxels.call() if voxels.is_valid() else shape.voxels
	if present.size() != shape.length:
		present = shape.voxels
	var quads := PackedInt32Array()
	_drawn_voxels.clear()
	for index: int in faces:
		if present[index] == 0:
			continue
		var bits: int = faces[index]
		var at := shape.voxel_at(index)
		for face in 6:
			if bits & (1 << face) == 0:
				continue
			# One face, as VoxelMesher packs a rectangle of them.
			var axis := face >> 1
			quads.append_array([axis, 1 if face & 1 == 0 else -1, at[axis], at[(axis + 1) % 3], at[(axis + 2) % 3], 1, 1, 0])
			_drawn_voxels.append(index)
	var count := _drawn_voxels.size()
	if count == 0:
		return null
	var vertices := VoxelMesher._corners(shape, quads)
	var normals := PackedVector3Array()
	var indices := PackedInt32Array()
	normals.resize(count * 4)
	indices.resize(count * 6)
	# Proud of the face by PROUD in metres, once grown to the mesh's space.
	var lift := PROUD / scale
	for quad in count:
		var at := quad * VoxelMesher.QUAD_FIELDS
		var side := quads[at + VoxelMesher.QUAD_SIDE]
		var normal := Vector3.ZERO
		normal[quads[at + VoxelMesher.QUAD_AXIS]] = side
		var first := quad * 4
		for corner in 4:
			vertices[first + corner] = (vertices[first + corner] + normal * lift) * scale
			normals[first + corner] = normal
		var order := VoxelMesher.WINDING_UP if side > 0 else VoxelMesher.WINDING_DOWN
		for index in 6:
			indices[quad * 6 + index] = first + order[index]
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_INDEX] = indices
	return arrays


static func _material() -> StandardMaterial3D:
	var made := StandardMaterial3D.new()
	made.albedo_color = COLOR
	made.roughness = 0.55
	made.metallic_specular = 0.35
	return made
