## Blood running over the faces of voxels from where it landed, as a liquid
## would: out across what it lies on, over edges and down, and downhill first.
## It pools on flat ground, fills the bottom of a crater, and a drop landing by
## a ledge runs over it, down the wall and out across the ground below.
##
## It runs face by face, always to the face that is cheapest to reach next
## from where it started, and recolours the voxel of each face it reaches that
## blood has not, until it has stained so many faces ([member left]): every
## face of the voxel open to the air turns red, and each costs one, so a unit
## of blood is a face of red whatever it lands on, the ground or a board's
## edge. A step across flat ground costs the same every way, so a pool comes
## out round, roughened by noise into a blob with lobes ([constant LUMPY]); a
## step down costs little, so blood runs over an edge before it spreads far on
## top; a step along a wall costs more, so on a wall it runs down in a streak;
## a step up costs a great deal, so it rarely climbs; and it never runs on to
## the underside of anything. Near where it landed ([member splat]) it spreads
## every way alike, splashing a little up a wall it struck by. A face whose
## voxel is red already costs little to cross and costs no blood, so blood
## landing in a pool runs out to its edge and makes it bigger.
##
## It runs over a [Surface]: a voxel grid of its own, whose voxels it
## recolours. The level's is every piece of it across one grid
## ([VolumeSurface]); any other voxel model's - a loose model, a prop - is its
## own ([ModelSurface], over its [VoxelModel]); a figure's is the figure
## standing as drawn ([FigureVoxels]), so blood can cross from the chest on to
## the hips.
##
## It can stain everything at once ([method spread] with all of it), or a few
## faces a frame, as the pool under a body spreads.
class_name BloodFlow
extends RefCounted

## The six ways a face can look, by number: +x, -x, +y, -y, +z, -z. A face's
## opposite is its number with the lowest bit flipped.
const FACES: Array[Vector3i] = [
	Vector3i(1, 0, 0), Vector3i(-1, 0, 0), Vector3i(0, 1, 0),
	Vector3i(0, -1, 0), Vector3i(0, 0, 1), Vector3i(0, 0, -1),
]
## The faces next to each face across each of its four edges lie this way,
## as face numbers: along the two axes the face does not look along.
const ALONG: Array = [[2, 3, 4, 5], [2, 3, 4, 5], [0, 1, 4, 5], [0, 1, 4, 5], [0, 1, 2, 3], [0, 1, 2, 3]]
const HALF := Vector3(0.5, 0.5, 0.5)

## What a step costs blood: across flat ground; downhill; sideways along a
## wall; and so much more for every voxel it would climb.
const ACROSS := 1.0
const DOWNHILL := 0.3
const SIDEWAYS := 2.0
const CLIMB := 6.0
## The share of its cost a step on to a face already stained costs.
const POOLED := 0.3
## How far the cost of a step wanders from place to place, as a share of it,
## and how far apart the wanderings are, in voxels: so a pool comes out a blob
## with lobes. And how much more it wanders face by face, so a drop's few faces
## are not the same cross every time.
const LUMPY := 0.7
const LUMP_SIZE := 5.0
const SPECKLE := 0.9
## The most faces looked at: so many, and so many more for each face it may
## stain. Blood landing in the middle of a big pool may not reach its edge.
const VISITS := 24
const VISITS_PER_FACE := 3

## Packing a face into one number: each of a voxel's three places, offset so it
## is never less than nothing, in [constant PLACE_BITS] bits, and the face.
const PLACE_BITS := 20
const OFFSET := 1 << (PLACE_BITS - 1)
const PLACE_MASK := (1 << PLACE_BITS) - 1

## What roughens every flow; each starts somewhere of its own in it.
static var _noise := _make_noise()


## A voxel grid blood can run over. Voxels are counted along its own axes;
## a face is a voxel and the way it looks out, one of [constant FACES] by
## number. Blood stains a voxel, recolouring it, so a face is stained once its
## voxel is.
class Surface:
	## Forgets anything it has kept about what is where: the surface may have
	## worn, moved or turned since it was last asked.
	func refresh() -> void:
		pass

	## Whether [param voxel] is there.
	func is_solid(_voxel: Vector3i) -> bool:
		return false

	## How high the middle of the face [param face] of [param voxel] is in the
	## world.
	func height(_voxel: Vector3i, _face: int) -> float:
		return 0.0

	## How far up the face [param face] of [param voxel] looks in the world:
	## 1 for a floor, 0 for a wall, -1 for an underside.
	func slope(_voxel: Vector3i, _face: int) -> float:
		return 1.0

	## How many faces of [param voxel] are open to the air: what turns red as
	## blood recolours it.
	func open_faces(voxel: Vector3i) -> int:
		var open := 0
		for way in FACES:
			if not is_solid(voxel + way):
				open += 1
		return open

	## How big a voxel is in the world.
	func voxel_size() -> float:
		return VoxelShape.SCALE

	func is_stained(_voxel: Vector3i, _face: int) -> bool:
		return false

	func stain(_voxel: Vector3i, _face: int) -> void:
		pass


## The level's voxels as one grid ([VoxelVolume]), a sixteenth of a cell each,
## along the level's axes: blood runs from one piece on to the next as if they
## were one, as they are.
class VolumeSurface extends Surface:
	var volume: VoxelVolume
	## The level's voxels in the world: a voxel's place, counted in voxels, to
	## the world.
	var frame: Transform3D

	func _init(on: VoxelVolume, level: Transform3D) -> void:
		volume = on
		frame = level * Transform3D(Basis.from_scale(Vector3.ONE / VoxelShape.BLOCK), Vector3.ZERO)

	func is_solid(voxel: Vector3i) -> bool:
		return volume.is_solid(voxel)

	func height(voxel: Vector3i, face: int) -> float:
		return (frame * (Vector3(voxel) + HALF + Vector3(FACES[face]) * 0.5)).y

	func slope(_voxel: Vector3i, face: int) -> float:
		return (frame.basis * Vector3(FACES[face])).normalized().y

	func voxel_size() -> float:
		return frame.basis.y.length()

	func is_stained(voxel: Vector3i, _face: int) -> bool:
		return volume.color_at(voxel) == VoxelVolume.BLOOD

	func stain(voxel: Vector3i, _face: int) -> void:
		volume.recolor(voxel, VoxelVolume.BLOOD)


## Any other voxel model ([VoxelModel]), standing in the world as it stands
## now: a crate's piece, a prop, in a figure's hand or dropped.
class ModelSurface extends Surface:
	var model: VoxelModel
	## Its frame in the world, as it was when the flow last looked.
	var frame: Transform3D

	func _init(on: VoxelModel) -> void:
		model = on
		frame = on.frame()

	func refresh() -> void:
		if is_instance_valid(model):
			frame = model.frame()

	func is_solid(voxel: Vector3i) -> bool:
		return model.is_solid(voxel)

	func height(voxel: Vector3i, face: int) -> float:
		return (frame * (model.shape.corner + (Vector3(voxel) + HALF + Vector3(FACES[face]) * 0.5) * VoxelShape.SCALE)).y

	func slope(_voxel: Vector3i, face: int) -> float:
		return (frame.basis * Vector3(FACES[face])).normalized().y

	func voxel_size() -> float:
		return frame.basis.y.length() * VoxelShape.SCALE

	func is_stained(voxel: Vector3i, _face: int) -> bool:
		return model.voxels[model.shape.index_of(voxel)] == VoxelModel.BLOOD

	func stain(voxel: Vector3i, _face: int) -> void:
		model.recolor(model.shape.index_of(voxel), VoxelModel.BLOOD)


## What it runs over.
var surface: Surface
## How many more faces it may stain, and how many it has: a voxel it recolours
## stains every one of its faces open to the air.
var left := 0
var stained := 0
## How far from where it landed, in voxels, it spreads every way alike.
var splat := 0.0

## The faces reached and not yet settled, as a heap, cheapest first: what it
## cost to reach each, and the face.
var _costs := PackedFloat32Array()
var _keys := PackedInt64Array()
## The faces settled, as a set.
var _settled := {}
var _visits := 0
var _most_visits := 0
var _start := Vector3.ZERO
## Where it is in the noise, and what speckles its edge.
var _offset := Vector3.ZERO
var _seed := 0


## Blood landing on the face [param face] of [param voxel] of
## [param on], enough to stain [param volume] faces, spreading every way alike
## within [param splat_radius] voxels of it. [param rng] places it in the noise.
func _init(on: Surface, voxel: Vector3i, face: int, volume: int, rng: RandomNumberGenerator, splat_radius := 0.0) -> void:
	surface = on
	left = volume
	splat = splat_radius
	_start = Vector3(voxel)
	_offset = Vector3(rng.randf(), rng.randf(), rng.randf()) * 1000.0
	_seed = rng.randi()
	_most_visits = VISITS + volume * VISITS_PER_FACE
	_push(0.0, _key(voxel, face))


## Stains up to [param most] more faces, recolouring the voxels of those
## cheapest to reach first, and returns how many it stained: a voxel's open
## faces all at once, so at the last a few past [param most].
func spread(most: int) -> int:
	surface.refresh()
	var done := 0
	while done < most and left > 0 and not _keys.is_empty() and _visits < _most_visits:
		var cost := _costs[0]
		var key := _keys[0]
		_pop()
		if _settled.has(key):
			continue
		_settled[key] = true
		_visits += 1
		var voxel := _voxel_of(key)
		var face := key & 7
		# Still open to the air: the surface may have worn since it was reached.
		if not surface.is_solid(voxel) or surface.is_solid(voxel + FACES[face]):
			continue
		if not surface.is_stained(voxel, face):
			surface.stain(voxel, face)
			var shown := surface.open_faces(voxel)
			left -= shown
			stained += shown
			done += shown
		_reach_from(voxel, face, cost)
	return done


## Whether it has stained all it can.
func is_done() -> bool:
	return left <= 0 or _keys.is_empty() or _visits >= _most_visits


## Reaches the four faces next to the face [param face] of [param voxel], which
## cost [param cost] to reach, across its edges: up the side of a voxel rising
## beside it, on along the same plane, or round the edge on to the voxel's own
## side, whichever is there, as water would go.
func _reach_from(voxel: Vector3i, face: int, cost: float) -> void:
	var out := FACES[face]
	var here := surface.height(voxel, face)
	var size := surface.voxel_size()
	for way: int in ALONG[face]:
		var along := FACES[way]
		var next := voxel
		var next_face := face
		var corner := voxel + along + out
		if surface.is_solid(corner):
			next = corner
			next_face = way ^ 1
		elif surface.is_solid(voxel + along):
			next = voxel + along
		else:
			next_face = way
		var key := _key(next, next_face)
		if _settled.has(key):
			continue
		var slope := surface.slope(next, next_face)
		if slope < -0.5:
			continue
		var step := ACROSS
		if Vector3(next).distance_to(_start) > splat:
			var rise := (surface.height(next, next_face) - here) / size
			if rise < -0.05:
				step = DOWNHILL
			elif rise > 0.05:
				step = ACROSS + rise * CLIMB
			elif absf(slope) < 0.5:
				step = SIDEWAYS
		if surface.is_stained(next, next_face):
			step *= POOLED
		else:
			var speckle := float(hash(key ^ _seed) & 0xffff) / 0xffff - 0.5
			step *= maxf(1.0 + LUMPY * _noise.get_noise_3dv(Vector3(next) / LUMP_SIZE + _offset) + SPECKLE * speckle, 0.1)
		_push(cost + step, key)


func _push(cost: float, key: int) -> void:
	var at := _costs.size()
	_costs.append(cost)
	_keys.append(key)
	while at > 0:
		var parent := (at - 1) >> 1
		if _costs[parent] <= cost:
			break
		_costs[at] = _costs[parent]
		_keys[at] = _keys[parent]
		at = parent
	_costs[at] = cost
	_keys[at] = key


## Takes the cheapest face off the heap.
func _pop() -> void:
	var last := _costs.size() - 1
	var cost := _costs[last]
	var key := _keys[last]
	_costs.resize(last)
	_keys.resize(last)
	if last == 0:
		return
	var at := 0
	while true:
		var child := at * 2 + 1
		if child >= last:
			break
		if child + 1 < last and _costs[child + 1] < _costs[child]:
			child += 1
		if _costs[child] >= cost:
			break
		_costs[at] = _costs[child]
		_keys[at] = _keys[child]
		at = child
	_costs[at] = cost
	_keys[at] = key


static func _key(voxel: Vector3i, face: int) -> int:
	return (
		((voxel.x + OFFSET) << (PLACE_BITS * 2 + 3))
		| ((voxel.y + OFFSET) << (PLACE_BITS + 3))
		| ((voxel.z + OFFSET) << 3)
		| face
	)


static func _voxel_of(key: int) -> Vector3i:
	return Vector3i(
		((key >> (PLACE_BITS * 2 + 3)) & PLACE_MASK) - OFFSET,
		((key >> (PLACE_BITS + 3)) & PLACE_MASK) - OFFSET,
		((key >> 3) & PLACE_MASK) - OFFSET,
	)


static func _make_noise() -> FastNoiseLite:
	var noise := FastNoiseLite.new()
	noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	noise.frequency = 1.0
	return noise
