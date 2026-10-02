## Blood running over the faces of voxels from where it landed, as a liquid
## would: out across what it lies on, over edges and down, and downhill first.
## It pools on flat ground, fills the bottom of a crater, and a drop landing by
## a ledge runs over it, down the wall and out across the ground below.
##
## It stains so many faces ([member left]), always the face that is cheapest
## to reach next from where it started: a step across flat ground costs the
## same every way, so a pool comes out round, roughened by noise into a blob
## with lobes ([constant LUMPY]); a step down costs little, so blood runs over
## an edge before it spreads far on top; a step along a wall costs more, so on a
## wall it runs down in a streak; a step up costs a great deal, so it rarely
## climbs; and it never runs on to the underside of anything. Near where it
## landed ([member splat]) it spreads every way alike, splashing a little up a
## wall it struck by. Faces already stained cost little to cross and cost no
## blood, so blood landing in a pool runs out to its edge and makes it bigger.
##
## It runs over a [Surface]: a voxel grid of its own, whose faces it can stain.
## The terrain's is every block on the map across one grid
## ([TerrainSurface]); a loose model's or a prop's is its own
## ([ModelSurface]); a figure's is the figure standing as drawn
## ([FigureVoxels]), so a stain can cross from the chest on to the hips.
##
## It can stain everything at once ([method spread] with all of it), or a few
## faces a frame, as the pool under a body spreads.
class_name BloodFlow
extends RefCounted

const FACES := VoxelStains.FACES
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
## number.
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

	## How big a voxel is in the world.
	func voxel_size() -> float:
		return VoxelShape.SCALE

	func is_stained(_voxel: Vector3i, _face: int) -> bool:
		return false

	func stain(_voxel: Vector3i, _face: int) -> void:
		pass


## The blocks of the map as one grid of voxels, a sixteenth of a cell each,
## along the grid's axes, voxel (0, 0, 0) at the least corner of cell
## (0, 0, 0): blood runs from one block on to the next as if they were one.
class TerrainSurface extends Surface:
	var terrain: VoxelTerrain
	## The grid's voxels in the world.
	var frame: Transform3D
	## What each cell looked at since the last refresh holds: its block's
	## voxels now, its kind, how it is turned and whether it is; empty for a
	## cell with no block drawn from a .vox. And the last cell looked at, which
	## is most often the next.
	var _cells := {}
	var _last_cell := Vector3i.MAX
	var _last_entry: Array = []

	func _init(on: VoxelTerrain, grid: Transform3D, cell_size: Vector3) -> void:
		terrain = on
		frame = grid * Transform3D(Basis.from_scale(cell_size / VoxelShape.BLOCK), Vector3.ZERO)

	func refresh() -> void:
		_cells.clear()
		_last_cell = Vector3i.MAX

	func is_solid(voxel: Vector3i) -> bool:
		var entry := _cell(Vector3i(voxel.x >> 4, voxel.y >> 4, voxel.z >> 4))
		if entry.is_empty():
			return false
		var voxels: PackedByteArray = entry[0]
		return voxels[_index(voxel, entry)] != 0

	func height(voxel: Vector3i, face: int) -> float:
		return (frame * (Vector3(voxel) + HALF + Vector3(FACES[face]) * 0.5)).y

	func slope(_voxel: Vector3i, face: int) -> float:
		return (frame.basis * Vector3(FACES[face])).normalized().y

	func voxel_size() -> float:
		return frame.basis.y.length()

	func is_stained(voxel: Vector3i, face: int) -> bool:
		var cell := cell_of(voxel)
		var stains := terrain.stains_at(cell)
		if stains == null:
			return false
		var entry := _cell(cell)
		return stains.bits_at(_index(voxel, entry)) & _bit(face, entry) != 0

	func stain(voxel: Vector3i, face: int) -> void:
		var cell := cell_of(voxel)
		var entry := _cell(cell)
		if not entry.is_empty():
			terrain.stain(cell, _index(voxel, entry), _bit(face, entry))

	## The cell [param voxel] is in.
	static func cell_of(voxel: Vector3i) -> Vector3i:
		return Vector3i(voxel.x >> 4, voxel.y >> 4, voxel.z >> 4)

	## The voxel at [param index] in the array of the block in [param cell],
	## counted across the grid.
	func voxel_of(cell: Vector3i, index: int) -> Vector3i:
		var entry := _cell(cell)
		var kind: VoxelShape = entry[1]
		var at := kind.voxel_at(index)
		if entry[3]:
			at = _turned(at, entry[2])
		return cell * VoxelShape.BLOCK + at

	func _cell(cell: Vector3i) -> Array:
		if cell == _last_cell:
			return _last_entry
		var entry: Variant = _cells.get(cell)
		if entry == null:
			entry = []
			var kind := terrain.kind_of(cell)
			if kind != null:
				var turn := terrain.turn_of(cell)
				entry = [terrain.voxels_of(cell), kind, turn, not turn.is_equal_approx(Basis.IDENTITY)]
			_cells[cell] = entry
		_last_cell = cell
		_last_entry = entry
		return entry

	## Where [param voxel], counted across the grid, is in its block's array.
	func _index(voxel: Vector3i, entry: Array) -> int:
		var at := Vector3i(voxel.x & 15, voxel.y & 15, voxel.z & 15)
		if entry[3]:
			at = _turned(at, (entry[2] as Basis).inverse())
		return (entry[1] as VoxelShape).index_of(at)

	## The bit of the face [param face], along the grid, in its block's frame.
	func _bit(face: int, entry: Array) -> int:
		if not entry[3]:
			return 1 << face
		return VoxelStains.bit(Vector3i(((entry[2] as Basis).inverse() * Vector3(FACES[face])).round()))

	## [param at], a voxel of a block counted from its cell's least corner,
	## turned by [param turn] about the middle of the cell.
	static func _turned(at: Vector3i, turn: Basis) -> Vector3i:
		var middle := Vector3.ONE * (VoxelShape.BLOCK * 0.5)
		return Vector3i((turn * (Vector3(at) + HALF - middle) + middle - HALF).round())


## One voxel model, standing in the world: a crate's piece, or a prop.
class ModelSurface extends Surface:
	var stains: VoxelStains
	## Its voxels now, laid out as [member stains]' shape's, and its frame in
	## the world.
	var voxels: PackedByteArray
	var frame: Transform3D

	func _init(on: VoxelStains, present: PackedByteArray, placed: Transform3D) -> void:
		stains = on
		voxels = present
		frame = placed

	func is_solid(voxel: Vector3i) -> bool:
		var shape := stains.shape
		return shape.holds(voxel) and voxels[shape.index_of(voxel)] != 0

	func height(voxel: Vector3i, face: int) -> float:
		var shape := stains.shape
		return (frame * (shape.corner + (Vector3(voxel) + HALF + Vector3(FACES[face]) * 0.5) * VoxelShape.SCALE)).y

	func slope(_voxel: Vector3i, face: int) -> float:
		return (frame.basis * Vector3(FACES[face])).normalized().y

	func voxel_size() -> float:
		return frame.basis.y.length() * VoxelShape.SCALE

	func is_stained(voxel: Vector3i, face: int) -> bool:
		return stains.bits_at(stains.shape.index_of(voxel)) & (1 << face) != 0

	func stain(voxel: Vector3i, face: int) -> void:
		stains.stain(stains.shape.index_of(voxel), 1 << face)


## What it runs over.
var surface: Surface
## How many more faces it may stain, and how many it has.
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


## Stains up to [param most] more faces, cheapest to reach first, and returns
## how many it stained.
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
			left -= 1
			stained += 1
			done += 1
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
