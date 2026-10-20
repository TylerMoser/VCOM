@tool
## What the rules see of a level: which cells are solid and which edges have
## something standing across them, read off its pieces, never their voxels.
##
## A solid piece ([member PieceKind.solid]) in the middle of a cell fills that
## cell, whatever its shape, and one on the edge between two cells stands
## across that edge, until it breaks: then it is gone from here at once
## ([method remove]), so sight, cover and paths change the moment it goes,
## however much of it is still to be seen falling. How worn a piece looks
## changes nothing here. Pieces that are not solid are left out altogether.
##
## [CombatGrid] asks this rather than the GridMap it once read; the level keeps
## one for the battle, made fresh from the level's [LevelData] as it loads.
class_name LevelRules
extends RefCounted

## The pieces standing in each cell and across each edge, by slot
## ([LevelData]), in the order placed.
var _cells := {}
var _edges := {}
## Whether each piece of the level still stands to the rules, by index: one
## that is not solid never does.
var standing := PackedByteArray()
## The box, in cells, round every cell any piece was placed in, and round the
## edges' cells too.
var bounds_min := Vector3i.ZERO
var bounds_max := Vector3i.ZERO
## The level's lowest layer of cells: its floor, which never breaks.
var bottom := 0


## The rules of [param data], built of [param library]'s kinds.
func _init(data: LevelData = null, library: PieceLibrary = null) -> void:
	if data == null or library == null:
		return
	var count := data.count()
	standing.resize(count)
	var kinds: Array[PieceKind] = []
	for id in data.kinds:
		kinds.append(library.find(StringName(id)))
	var first := true
	for index in count:
		var slot := data.slot_at(index)
		var low := LevelData.cell_of(slot)
		var high := LevelData.other_cell(slot)
		if first:
			bounds_min = low
			bounds_max = high
			first = false
		else:
			bounds_min = bounds_min.min(low)
			bounds_max = bounds_max.max(high)
		var kind := kinds[data.kind_at(index)]
		if kind == null or not kind.solid:
			continue
		standing[index] = 1
		var table := _cells if LevelData.is_centre(slot) else _edges
		var here: PackedInt32Array = table.get(slot, PackedInt32Array())
		here.append(index)
		table[slot] = here
	bottom = bounds_min.y


## Whether a solid piece stands in [param cell].
func is_solid(cell: Vector3i) -> bool:
	return _cells.has(LevelData.centre_slot(cell))


## Whether a solid piece stands across the edge of [param cell] toward
## [param direction], one of the four ways across the ground, at the cell's
## own level.
func has_edge(cell: Vector3i, direction: Vector2i) -> bool:
	return _edges.has(LevelData.edge_slot(cell, direction))


## Whether a solid piece stands across the edge in [param slot].
func has_edge_slot(slot: Vector3i) -> bool:
	return _edges.has(slot)


## The pieces standing in [param cell], in the order placed: the last is the
## one on top, which is what a round striking the cell strikes.
func pieces_in(cell: Vector3i) -> PackedInt32Array:
	return _cells.get(LevelData.centre_slot(cell), PackedInt32Array())


## The pieces standing across the edge in [param slot], in the order placed.
func pieces_across(slot: Vector3i) -> PackedInt32Array:
	return _edges.get(slot, PackedInt32Array())


## Every cell a solid piece stands in.
func solid_cells() -> Array[Vector3i]:
	var cells: Array[Vector3i] = []
	for slot: Vector3i in _cells:
		cells.append(LevelData.cell_of(slot))
	return cells


## Every edge a solid piece stands across, by slot.
func edge_slots() -> Array[Vector3i]:
	var slots: Array[Vector3i] = []
	slots.assign(_edges.keys())
	return slots


## Whether piece [param index] still stands.
func is_standing(index: int) -> bool:
	return index >= 0 and index < standing.size() and standing[index] != 0


## Takes piece [param index], standing in [param slot], out of the rules: it
## has broken, or fallen with what it stood on. Returns whether it stood.
func remove(index: int, slot: Vector3i) -> bool:
	if not is_standing(index):
		return false
	standing[index] = 0
	var table := _cells if LevelData.is_centre(slot) else _edges
	var here: PackedInt32Array = table.get(slot, PackedInt32Array())
	var at := here.find(index)
	if at >= 0:
		here.remove_at(at)
	if here.is_empty():
		table.erase(slot)
	else:
		table[slot] = here
	return true
