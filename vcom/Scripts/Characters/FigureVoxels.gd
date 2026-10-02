## The voxels of a [CharacterModel]'s figure, as blood and breaking apart need
## them: where each one is now, the figure posed as it is, which of their
## faces blood has stained, and what its gear is made of. [Blood] traces its
## drops against them ([method march]), wounds them ([method pick_wound],
## [method bleed]), and lets blood spread over them; as its unit dies, the
## figure breaks apart into lumps of them ([method crumble]).
##
## The figure is rigid, one bone to a voxel ([code]VoxelRig.gd[/code]), so a
## voxel is wherever its bone has put it: each bone's voxels are a little model
## of their own, a part, standing in the bone's frame ([member _frames]). Blood
## spreads over the figure as it was drawn, standing, every bone's voxels side
## by side ([member Rig.shape]), so a stain can cross from the chest on to the
## hips as it would on a body, however the bones have turned since; which way
## is down is still the world's, through each voxel's bone. On a figure this
## small the even splash round a wound ([constant WOUND_SPLAT]) takes most of
## the stain, so a wound leans a little downward rather than running down.
##
## The stains are drawn over the figure by a mesh skinned to its skeleton as
## its body is ([FigureStains]), so they move with it, and go into the lumps it
## breaks into as its unit dies ([method crumble]). Gear is stained as any prop
## is ([method VoxelStains.on]), and keeps its stains when it is dropped.
##
## Like the figure itself, only for show: the rules never read it.
class_name FigureVoxels
extends RefCounted

const VoxelRig := preload("res://Scripts/Characters/VoxelRig.gd")

## How likely a wound is to land on each bone, before the shot is traced to the
## nearest voxel facing it: mostly the torso.
const WOUND_WEIGHTS := {
	&"Chest": 30.0, &"Spine": 20.0, &"Hips": 12.0, &"Head": 8.0,
	&"LeftUpperArm": 4.0, &"RightUpperArm": 4.0, &"LeftLowerArm": 2.0, &"RightLowerArm": 2.0,
	&"LeftUpperLeg": 5.0, &"RightUpperLeg": 5.0, &"LeftLowerLeg": 3.0, &"RightLowerLeg": 3.0,
}
## How many tries picking a wound gets, each a voxel chosen afresh, before it
## gives up: a line to the voxel chosen may pass the figure by at its edge.
const WOUND_TRIES := 6
## How far round a wound, in voxels, blood spreads every way alike before
## downhill costs it less ([member BloodFlow.splat]). On a torso 5 voxels wide
## and 2 deep this wraps round to the back and takes most of a wound.
const WOUND_SPLAT := 2.0
## How far past a figure, in metres, a line through it is traced back from to
## find where it comes out.
const THROUGH := 2.0


## A figure model's voxels, read once from its .vox and shared by every figure
## of it.
class Rig:
	## The figure as drawn, standing: each voxel holds its bone's number, 1 up.
	var shape: VoxelShape
	## Every bone, by number, in [constant VoxelRig.BONES]' order.
	var bones: Array[StringName] = []
	## Each bone's voxels alone, cut to their box, each holding 1 (null for a
	## bone with none); where that box starts in [member shape]; and each one's
	## voxels by place, to pick one at random.
	var parts: Array[VoxelShape] = []
	var offsets: Array[Vector3i] = []
	var places: Array[PackedInt32Array] = []
	## The same voxels, in the same order, as cells of their part, as their
	## middles in its frame, and by their places in [member shape]: what
	## breaking the figure apart reads ([method FigureVoxels.crumble]), worked
	## out once.
	var cells: Array = []
	var centers: Array[PackedVector3Array] = []
	var wholes: Array[PackedInt32Array] = []
	## Each bone's joint, in metres in the figure's space.
	var joints: Array[Vector3] = []
	## The middle of each bone's part, in its shape's frame, and how far from it
	## its farthest corner is, in metres: a line passing further off misses it.
	var middles := PackedVector3Array()
	var radii := PackedFloat32Array()
	## The figure's voxel size over a block's: its space is the shape's grown
	## by this.
	var scale := 1.0
	## Each bone's share of [constant WOUND_WEIGHTS], adding up to 1.
	var weights := PackedFloat32Array()


## Where a line first meets the figure: the point and the way the face it met
## looks, in the world, and how far along the line it is; the voxel and face,
## by number. On the body, the voxel is counted in [member Rig.shape] and
## [member bone] is its bone's number; on gear, [member gear] is what draws it,
## and the voxel is counted in its shape, standing in [member frame].
class Hit:
	var point := Vector3.ZERO
	var normal := Vector3.ZERO
	var distance := 0.0
	var voxel := Vector3i.ZERO
	var face := 0
	var bone := -1
	var gear: MeshInstance3D
	var frame := Transform3D.IDENTITY


## The stains of a figure's body, drawn by a mesh skinned to its skeleton, each
## stained face weighted wholly to its voxel's bone, as the body's are.
class FigureStains extends VoxelStains:
	## The skeleton's index of each bone, by number.
	var bone_index := PackedInt32Array()

	func _arrays() -> Variant:
		var arrays: Variant = super()
		if arrays == null:
			return null
		var corners := _drawn_voxels.size() * 4
		var bones := PackedInt32Array()
		var weights := PackedFloat32Array()
		bones.resize(corners * 4)
		weights.resize(corners * 4)
		for quad in _drawn_voxels.size():
			var bone := bone_index[shape.voxels[_drawn_voxels[quad]] - 1]
			for corner in 4:
				bones[(quad * 4 + corner) * 4] = bone
				weights[(quad * 4 + corner) * 4] = 1.0
		arrays[Mesh.ARRAY_BONES] = bones
		arrays[Mesh.ARRAY_WEIGHTS] = weights
		return arrays


## A figure as blood runs over it: standing as drawn, which way is down taken
## from each voxel's bone as it is posed now.
class FigureSurface extends BloodFlow.Surface:
	var figure: FigureVoxels

	func _init(on: FigureVoxels) -> void:
		figure = on

	func refresh() -> void:
		figure._pose()

	func is_solid(voxel: Vector3i) -> bool:
		var shape := figure.rig.shape
		return shape.holds(voxel) and shape.voxels[shape.index_of(voxel)] != 0

	func height(voxel: Vector3i, face: int) -> float:
		var shape := figure.rig.shape
		var frame := figure._frames[shape.voxels[shape.index_of(voxel)] - 1]
		return (frame * (shape.corner + (Vector3(voxel) + BloodFlow.HALF + Vector3(BloodFlow.FACES[face]) * 0.5) * VoxelShape.SCALE)).y

	func slope(voxel: Vector3i, face: int) -> float:
		var shape := figure.rig.shape
		var frame := figure._frames[shape.voxels[shape.index_of(voxel)] - 1]
		return (frame.basis * Vector3(BloodFlow.FACES[face])).normalized().y

	func voxel_size() -> float:
		return figure.rig.scale * VoxelShape.SCALE

	func is_stained(voxel: Vector3i, face: int) -> bool:
		return figure.stains != null and figure.stains.bits_at(figure.rig.shape.index_of(voxel)) & (1 << face) != 0

	func stain(voxel: Vector3i, face: int) -> void:
		figure.stained().stain(figure.rig.shape.index_of(voxel), 1 << face)


## Every figure model's rig, by the path of its .vox.
static var _rigs := {}

## The figure's model's voxels.
var rig: Rig
## The blood on its body, null until some lands there ([method stained]).
var stains: FigureStains

var _model: CharacterModel
var _skeleton: Skeleton3D
var _body: MeshInstance3D
## The skeleton's index of each bone, by number.
var _bone_index := PackedInt32Array()
## Each bone's part's frame in the world, as the figure was posed when last
## asked, and when that was; and where each part's middle is in the world.
var _frames: Array[Transform3D] = []
var _middles := PackedVector3Array()
var _posed_at := -1
## The gear it carries, as posed when last asked: what draws each, its voxels,
## their frame in the world, and the middle and reach of the ball round them.
var _gear: Array[MeshInstance3D] = []
var _gear_shapes: Array[VoxelShape] = []
var _gear_frames: Array[Transform3D] = []
var _gear_middles := PackedVector3Array()
var _gear_radii := PackedFloat32Array()


## The voxels of [param model], whose figure is drawn from the .vox at
## [param path]. Check [member rig]: null if the model has no layout, or its
## voxels cannot be read.
func _init(model: CharacterModel, path: String) -> void:
	_model = model
	_skeleton = model.get_node_or_null(^"Skeleton3D") as Skeleton3D
	_body = model.get_node_or_null(^"Skeleton3D/Body") as MeshInstance3D
	rig = _rig_of(path)
	if rig == null or _skeleton == null:
		rig = null
		return
	for bone in rig.bones:
		_bone_index.append(_skeleton.find_bone(bone))
	_frames.resize(rig.bones.size())
	_middles.resize(rig.bones.size())


## Whether the figure is still there to bleed: it is gone once it has broken
## apart.
func is_valid() -> bool:
	return is_instance_valid(_model) and not _model.dead and is_instance_valid(_skeleton)


## Where a line from [param origin] along [param heading], normalised, first
## meets the figure within [param max_distance], or null if it does not; its
## gear too if [param with_gear].
func march(origin: Vector3, heading: Vector3, max_distance: float, with_gear := true) -> Hit:
	_pose()
	var best: Hit = null
	var reach := max_distance
	for bone in rig.parts.size():
		var part := rig.parts[bone]
		if part == null or not _passes_near(origin, heading, reach, _middles[bone], rig.radii[bone]):
			continue
		var met := VoxelTerrain.march(part, part.voxels, _frames[bone], origin, heading, reach)
		if met == null or met.face == Vector3i.ZERO:
			continue
		reach = met.distance
		best = _hit(met)
		best.bone = bone
		best.voxel = part.voxel_at(met.index) + rig.offsets[bone]
	if with_gear:
		for item in _gear.size():
			if not _passes_near(origin, heading, reach, _gear_middles[item], _gear_radii[item]):
				continue
			var shape := _gear_shapes[item]
			var met := VoxelTerrain.march(shape, shape.voxels, _gear_frames[item], origin, heading, reach)
			if met == null or met.face == Vector3i.ZERO:
				continue
			reach = met.distance
			best = _hit(met)
			best.gear = _gear[item]
			best.frame = _gear_frames[item]
			best.voxel = shape.voxel_at(met.index)
	return best


## Where a blow from [param from] lands on the figure, on the side facing it:
## a voxel picked at random, mostly on the torso ([constant WOUND_WEIGHTS]),
## and the first one the line from [param from] to it meets. Null if no line
## tried meets the figure.
func pick_wound(from: Vector3, rng: RandomNumberGenerator) -> Hit:
	_pose()
	for attempt in WOUND_TRIES:
		var bone := rng.rand_weighted(rig.weights)
		var places := rig.places[bone]
		if places.is_empty():
			continue
		var target := _frames[bone] * rig.parts[bone].center_of(places[rng.randi() % places.size()])
		var toward := target - from
		if toward.is_zero_approx():
			continue
		var hit := march(from, toward.normalized(), toward.length() + VoxelShape.SCALE, false)
		if hit != null:
			return hit
	return null


## Where a blow from [param from] that was seen to land at [param at] lands on
## the figure as it stands now, which may have moved a little since: on the
## line from one to the other, or failing that, anywhere facing [param from].
func hit_near(at: Vector3, from: Vector3, rng: RandomNumberGenerator) -> Hit:
	var toward := at - from
	if not toward.is_zero_approx():
		var hit := march(from, toward.normalized(), toward.length() + 0.5, false)
		if hit != null:
			return hit
	return pick_wound(from, rng)


## Where a line going in at [param entry] along [param heading] comes out of
## the figure: the last of its voxels on the line, met tracing back from beyond
## it. Null if there is none.
func exit(entry: Vector3, heading: Vector3) -> Hit:
	return march(entry + heading * THROUGH, -heading, THROUGH, false)


## Stains [param faces] faces round where [param hit] landed on the figure, or
## the gear it met, leaning downward. [param rng] roughens it.
func bleed(hit: Hit, faces: int, rng: RandomNumberGenerator) -> void:
	var surface: BloodFlow.Surface
	if hit.gear != null:
		var on := VoxelStains.on(hit.gear)
		if on == null:
			return
		surface = BloodFlow.ModelSurface.new(on, on.shape.voxels, hit.frame)
	else:
		surface = FigureSurface.new(self)
	BloodFlow.new(surface, hit.voxel, hit.face, faces, rng, WOUND_SPLAT).spread(faces)


## The figure as it stands now, broken up into lumps at most [param size]
## voxels across, as [VoxelDebris.Piece]s not yet moving: as a block crumbles,
## each bone's voxels cut on a grid set at random by [param rng], so a lump is
## always the voxels of one bone, standing as that bone is posed. A voxel is
## [param tint], or blood's colour if any of its faces is stained.
func crumble(size: int, tint: Color, rng: RandomNumberGenerator) -> Array[VoxelDebris.Piece]:
	_pose()
	var pieces: Array[VoxelDebris.Piece] = []
	for bone in rig.parts.size():
		var part := rig.parts[bone]
		if part == null:
			continue
		var frame := _frames[bone]
		# A body cannot be scaled: a lump is turned as its bone is, and drawn a
		# block's voxels across, a shade smaller than the figure's.
		var turn := frame.basis.orthonormalized()
		var cells: Array[Vector3i] = rig.cells[bone]
		var centers := rig.centers[bone]
		var wholes := rig.wholes[bone]
		var shift := Vector3i(rng.randi_range(0, size - 1), rng.randi_range(0, size - 1), rng.randi_range(0, size - 1))
		var clumps := {}
		for voxel in cells.size():
			var clump: Array = clumps.get_or_add((cells[voxel] + shift) / size, [])
			clump.append(voxel)
		for clump: Array in clumps.values():
			var least := Vector3i.MAX
			var most := Vector3i.MIN
			for voxel: int in clump:
				least = least.min(cells[voxel])
				most = most.max(cells[voxel])
			var middle := part.corner + (Vector3(least) + Vector3(most + Vector3i.ONE)) * 0.5 * VoxelShape.SCALE
			var piece := VoxelDebris.Piece.new()
			piece.transform = Transform3D(turn, frame * middle)
			piece.size = Vector3(most - least + Vector3i.ONE) * VoxelShape.SCALE
			piece.voxels = PackedVector3Array()
			piece.colors = PackedColorArray()
			piece.voxels.resize(clump.size())
			piece.colors.resize(clump.size())
			for at in clump.size():
				var voxel: int = clump[at]
				piece.voxels[at] = centers[voxel] - middle
				var bled := stains != null and stains.bits_at(wholes[voxel]) != 0
				piece.colors[at] = VoxelStains.COLOR if bled else tint
			pieces.append(piece)
	return pieces


## The blood on the figure's body, made the first time it is asked for, drawn
## over it by a mesh skinned to its skeleton.
func stained() -> FigureStains:
	if stains == null:
		stains = FigureStains.new(rig.shape, rig.scale)
		stains.bone_index = _bone_index
		stains.attach(_skeleton)
		stains.overlay.skeleton = NodePath("..")
		if _body != null:
			stains.overlay.skin = _body.skin
		# Its mesh's bounds are those of the stains on the figure standing as
		# drawn; posed, they may lie a way off them.
		stains.overlay.extra_cull_margin = 2.0
	return stains


## Reads the voxels of the gear it carries now, which would otherwise be read
## from their .vox the first time a drop of blood came near it.
func prepare() -> void:
	for drawn in _model.gear():
		VoxelStains.shape_of(drawn)


## Works out where each bone's voxels are now, and its gear's, once a frame.
func _pose() -> void:
	var now := Engine.get_process_frames() * 4096 + Engine.get_physics_frames()
	if now == _posed_at:
		return
	_posed_at = now
	var skeleton_frame := _skeleton.global_transform
	var grow := Transform3D(Basis.from_scale(Vector3.ONE * rig.scale), Vector3.ZERO)
	for bone in rig.bones.size():
		var pose := _skeleton.get_bone_global_pose(_bone_index[bone])
		# Bones rest unrotated at their joints, so a voxel's place in the
		# figure's space, less its joint, is its place in its bone.
		_frames[bone] = skeleton_frame * pose * Transform3D(Basis.IDENTITY, -rig.joints[bone]) * grow
		_middles[bone] = _frames[bone] * rig.middles[bone]
	_gear.clear()
	_gear_shapes.clear()
	_gear_frames.clear()
	_gear_middles.clear()
	_gear_radii.clear()
	for drawn in _model.gear():
		var shape := VoxelStains.shape_of(drawn)
		if shape == null:
			continue
		var frame := drawn.global_transform * Transform3D(Basis.from_scale(Vector3.ONE * VoxelStains.scale_of(drawn, shape)), Vector3.ZERO)
		var span := Vector3(shape.size) * VoxelShape.SCALE
		_gear.append(drawn)
		_gear_shapes.append(shape)
		_gear_frames.append(frame)
		_gear_middles.append(frame * (shape.corner + span * 0.5))
		_gear_radii.append((frame.basis * span).length() * 0.5 + VoxelShape.SCALE)


## Whether a line from [param from] along [param heading], [param length]
## long, passes within [param radius] of [param point].
static func _passes_near(from: Vector3, heading: Vector3, length: float, point: Vector3, radius: float) -> bool:
	var along := clampf((point - from).dot(heading), 0.0, length)
	return (from + heading * along).distance_squared_to(point) <= radius * radius


func _hit(met: VoxelTerrain.Met) -> Hit:
	var hit := Hit.new()
	hit.point = met.point
	hit.normal = met.normal
	hit.distance = met.distance
	hit.face = VoxelStains.FACES.find(met.face)
	return hit


## The rig of the figure model at [param path], read the first time it is asked
## for. Null, with an error, if it has no layout or cannot be read.
static func _rig_of(path: String) -> Rig:
	if _rigs.has(path):
		return _rigs[path]
	var rig: Rig = null
	if not VoxelRig.LAYOUTS.has(path):
		push_error("FigureVoxels: no layout for '%s' in VoxelRig.LAYOUTS, so it never bleeds." % path)
	else:
		var source := VoxelRig.new()
		if source.load_vox(path, VoxelRig.LAYOUTS[path]):
			rig = _read(source)
	_rigs[path] = rig
	return rig


## The rig [param source] has shared its model's voxels out by.
static func _read(source: VoxelRig) -> Rig:
	var rig := Rig.new()
	rig.scale = source.scale / VoxelShape.SCALE
	var least := Vector3i.MAX
	var most := Vector3i.MIN
	for bone: StringName in source.cells:
		for cell: Vector3i in source.cells[bone]:
			least = least.min(cell)
			most = most.max(cell)
	# The shape's frame is the figure's space shrunk by its scale.
	var to_shape := VoxelShape.SCALE / source.scale
	rig.shape = VoxelShape.new(most - least + Vector3i.ONE, source.voxel_corner(least) * to_shape)
	var total := 0.0
	for entry: Array in VoxelRig.BONES:
		var bone: StringName = entry[0]
		var number := rig.bones.size()
		rig.bones.append(bone)
		rig.joints.append(source.joint(bone))
		var weight: float = WOUND_WEIGHTS.get(bone, 0.0)
		var cells: Dictionary = source.cells.get(bone, {})
		if cells.is_empty():
			rig.parts.append(null)
			rig.offsets.append(Vector3i.ZERO)
			rig.places.append(PackedInt32Array())
			rig.cells.append([] as Array[Vector3i])
			rig.centers.append(PackedVector3Array())
			rig.wholes.append(PackedInt32Array())
			rig.weights.append(0.0)
			rig.middles.append(Vector3.ZERO)
			rig.radii.append(0.0)
			continue
		var low := Vector3i.MAX
		var high := Vector3i.MIN
		for cell: Vector3i in cells:
			low = low.min(cell)
			high = high.max(cell)
		var part := VoxelShape.new(high - low + Vector3i.ONE, source.voxel_corner(low) * to_shape)
		var places := PackedInt32Array()
		var at: Array[Vector3i] = []
		var centers := PackedVector3Array()
		var wholes := PackedInt32Array()
		for cell: Vector3i in cells:
			var place := part.index_of(cell - low)
			part.voxels[place] = 1
			part.count += 1
			places.append(place)
			at.append(cell - low)
			centers.append(part.center_of(place))
			wholes.append(rig.shape.index_of(cell - least))
			rig.shape.voxels[rig.shape.index_of(cell - least)] = number + 1
			rig.shape.count += 1
		rig.cells.append(at)
		rig.centers.append(centers)
		rig.wholes.append(wholes)
		part.rows = part.rows_of(part.voxels)
		var span := Vector3(part.size) * VoxelShape.SCALE
		rig.middles.append(part.corner + span * 0.5)
		rig.radii.append(span.length() * 0.5 * rig.scale + VoxelShape.SCALE)
		rig.parts.append(part)
		rig.offsets.append(low - least)
		rig.places.append(places)
		rig.weights.append(weight)
		total += weight
	rig.shape.rows = rig.shape.rows_of(rig.shape.voxels)
	if total > 0.0:
		for bone in rig.weights.size():
			rig.weights[bone] /= total
	return rig
