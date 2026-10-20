@tool
## A level as it is built: every piece placed, in the order it was placed. A
## combat map's ground, walls and trees, as the level editor leaves them, and
## what [VoxelLevel] builds the map from each time it loads.
##
## A piece is a kind ([PieceKind]), a slot and a turn. A slot is where a piece
## can stand, counted across the ground in half cells and up in cells: x and z
## both even is the middle of cell (x / 2, y, z / 2); one of them odd is the
## edge between two cells side by side, x odd the edge between cells x / 2 and
## x / 2 + 1 (rounded down) along x, z odd the same along z. Both odd, a cell's
## corner, is no slot. A piece's box, 16 voxels a side, has its least corner
## at voxel ([method voxel_origin]): a piece on an edge stands half in each
## cell. Its turn is in quarter turns about up, counterclockwise seen from
## above, about the middle of its box.
##
## Pieces can share a slot or overlap: the later one wins voxel by voxel
## ([VoxelVolume]). Nothing here changes in play: what breaks is the
## battle's to keep ([LevelRules], [VoxelVolume]), never this resource's.
class_name LevelData
extends Resource

## How many numbers each piece takes in [member pieces]: its kind, its slot's
## x, y and z, and its turn.
const FIELDS := 5
const KIND := 0
const SLOT_X := 1
const SLOT_Y := 2
const SLOT_Z := 3
const TURN := 4

## The kinds the level uses, by [member PieceKind.id]: [member pieces] names
## each by its place here, so a library can grow or be reordered under it.
@export var kinds: PackedStringArray = []
## Every piece, [constant FIELDS] numbers each, in the order placed.
@export var pieces: PackedInt32Array = []


## How many pieces there are.
func count() -> int:
	@warning_ignore("integer_division")
	return pieces.size() / FIELDS


## The kind of piece [param index], by its place in [member kinds].
func kind_at(index: int) -> int:
	return pieces[index * FIELDS + KIND]


## The id of the kind of piece [param index].
func kind_id(index: int) -> StringName:
	return StringName(kinds[kind_at(index)])


## The slot piece [param index] stands in.
func slot_at(index: int) -> Vector3i:
	var at := index * FIELDS
	return Vector3i(pieces[at + SLOT_X], pieces[at + SLOT_Y], pieces[at + SLOT_Z])


## The turn of piece [param index], in quarter turns.
func turn_at(index: int) -> int:
	return pieces[index * FIELDS + TURN]


## The place of the kind [param id] in [member kinds], added if it is not there.
func kind_index(id: StringName) -> int:
	var at := kinds.find(String(id))
	if at < 0:
		kinds.append(String(id))
		at = kinds.size() - 1
	return at


## Places a piece of the kind [param id] in [param slot], turned [param turn]
## quarter turns, last of all, and returns its index.
func add(id: StringName, slot: Vector3i, turn: int) -> int:
	pieces.append_array(PackedInt32Array([kind_index(id), slot.x, slot.y, slot.z, posmod(turn, 4)]))
	return count() - 1


## Places a piece as [method add] does, but at [param index] in the order, the
## pieces from there on one later: how undoing an erase puts a piece back where
## it was.
func insert(index: int, id: StringName, slot: Vector3i, turn: int) -> void:
	var at := index * FIELDS
	var values := [kind_index(id), slot.x, slot.y, slot.z, posmod(turn, 4)]
	for field in FIELDS:
		pieces.insert(at + field, values[field])


## Takes piece [param index] out, the pieces after it one earlier.
func remove(index: int) -> void:
	var at := index * FIELDS
	for field in FIELDS:
		pieces.remove_at(at)


## The pieces standing in [param slot], in the order placed.
func indices_at(slot: Vector3i) -> PackedInt32Array:
	var found := PackedInt32Array()
	for index in count():
		var at := index * FIELDS
		if pieces[at + SLOT_X] == slot.x and pieces[at + SLOT_Y] == slot.y and pieces[at + SLOT_Z] == slot.z:
			found.append(index)
	return found


## Whether [param slot] is the middle of a cell.
static func is_centre(slot: Vector3i) -> bool:
	return slot.x & 1 == 0 and slot.z & 1 == 0


## Whether [param slot] is the edge between two cells.
static func is_edge(slot: Vector3i) -> bool:
	return (slot.x & 1) + (slot.z & 1) == 1


## The slot in the middle of [param cell].
static func centre_slot(cell: Vector3i) -> Vector3i:
	return Vector3i(cell.x * 2, cell.y, cell.z * 2)


## The slot on the edge of [param cell] toward [param direction], one of the
## four ways across the ground.
static func edge_slot(cell: Vector3i, direction: Vector2i) -> Vector3i:
	return Vector3i(cell.x * 2 + direction.x, cell.y, cell.z * 2 + direction.y)


## The cell [param slot] is the middle of; for an edge, the cell on its least
## side ([method other_cell] is the one on its far side).
static func cell_of(slot: Vector3i) -> Vector3i:
	return Vector3i(slot.x >> 1, slot.y, slot.z >> 1)


## For an edge, the cell on its far side; for the middle of a cell, that cell.
static func other_cell(slot: Vector3i) -> Vector3i:
	return Vector3i((slot.x + 1) >> 1, slot.y, (slot.z + 1) >> 1)


## The way across the ground from [method cell_of] to [method other_cell] for
## an edge; none for the middle of a cell.
static func edge_direction(slot: Vector3i) -> Vector2i:
	return Vector2i(slot.x & 1, slot.z & 1)


## The voxel at the least corner of the box of a piece in [param slot],
## counting a cell as sixteen voxels.
static func voxel_origin(slot: Vector3i) -> Vector3i:
	return Vector3i(slot.x * 8, slot.y * 16, slot.z * 8)


## The middle of the box of a piece in [param slot], in cells, in the level's
## own space, where cell (0, 0, 0) runs from 0 to 1 on each axis.
static func box_center(slot: Vector3i) -> Vector3:
	return Vector3(slot.x * 0.5 + 0.5, slot.y + 0.5, slot.z * 0.5 + 0.5)
