## What of a level is cut away from the view so as to see into its buildings,
## from one height up ([method VoxelLevel.cut_away]): every building piece
## ([member PieceKind.cutaway]) at that height or above, and every other piece
## resting on those, in the same column or on the same edge. Only for show:
## the rules see every piece as they always do.
##
## Besides the pieces, it says where things are hidden with them: whatever is
## at or above the lowest building piece cut away in its column, a cell across,
## or over one cut away on an edge, within [constant STRIP] of it
## ([method covers_point], [method covers_cell]). So a unit, a coin or a lump
## standing on a cut roof is hidden, and one on a floor below it is not.
##
## A building piece cut away is cut away however broken, but only those still
## standing hide what is over them: a roof shot through no longer hides what
## falls in.
class_name LevelCutaway
extends RefCounted

## How far either side of an edge, in cells, a point is over the piece across
## it: half the thickest wall's voxels and a lump lying on its top.
const STRIP := 0.2
## Higher than any level.
const NONE := 1 << 30

## The height cut away from, in levels (cell y).
var from_level := 0
## The pieces cut away, by their index in the level's [LevelData], as a set.
var pieces := {}

## The lowest level a building piece cut away still stands at in each column,
## by the cell's x and z; and across each edge, by the edge's slot's x and z.
var _columns := {}
var _edges := {}


## What of [param data], whose kinds are [param kinds] (by their place in its
## kinds), is cut away from [param from] up, seen as [param rules] sees it now.
func _init(data: LevelData, kinds: Array[PieceKind], rules: LevelRules, from: int) -> void:
	from_level = from
	var count := data.count()
	for index in count:
		var slot := data.slot_at(index)
		if slot.y < from:
			continue
		var kind := kinds[data.kind_at(index)]
		if kind == null or not kind.cutaway:
			continue
		pieces[index] = true
		if kind.solid and not rules.is_standing(index):
			continue
		var table := _columns if LevelData.is_centre(slot) else _edges
		var key := Vector2i(slot.x >> 1, slot.z >> 1) if LevelData.is_centre(slot) else Vector2i(slot.x, slot.z)
		table[key] = mini(table.get(key, NONE), slot.y)
	# Whatever rests on them goes with them: a crate in the loft, a fence on a
	# roof.
	for index in count:
		if pieces.has(index):
			continue
		var slot := data.slot_at(index)
		if slot.y >= from and covers_slot(slot):
			pieces[index] = true


## Whether a piece in [param slot] rests on a piece cut away: in its column,
## or, on an edge, across that edge or in either column beside it.
func covers_slot(slot: Vector3i) -> bool:
	if LevelData.is_centre(slot):
		return _columns.get(Vector2i(slot.x >> 1, slot.z >> 1), NONE) <= slot.y
	if _edges.get(Vector2i(slot.x, slot.z), NONE) <= slot.y:
		return true
	var low := LevelData.cell_of(slot)
	var high := LevelData.other_cell(slot)
	return covers_cell(Vector3i(low.x, slot.y, low.z)) or covers_cell(Vector3i(high.x, slot.y, high.z))


## Whether something in [param cell], or a unit standing on it as a tile, is
## over a piece cut away in its column.
func covers_cell(cell: Vector3i) -> bool:
	return _columns.get(Vector2i(cell.x, cell.z), NONE) <= cell.y


## Whether something at [param local], in the level's own space, is over a
## piece cut away: in its column, or across an edge within [constant STRIP] of
## it.
func covers_point(local: Vector3) -> bool:
	if local.y < from_level:
		return false
	var cell := Vector3i(local.floor())
	if covers_cell(cell):
		return true
	if _edges.is_empty():
		return false
	var across := local.x - cell.x
	var along := local.z - cell.z
	if across < STRIP and _edge_covers(Vector2i(cell.x * 2 - 1, cell.z * 2), cell.y):
		return true
	if across > 1.0 - STRIP and _edge_covers(Vector2i(cell.x * 2 + 1, cell.z * 2), cell.y):
		return true
	if along < STRIP and _edge_covers(Vector2i(cell.x * 2, cell.z * 2 - 1), cell.y):
		return true
	return along > 1.0 - STRIP and _edge_covers(Vector2i(cell.x * 2, cell.z * 2 + 1), cell.y)


## Whether a piece cut away stands across the edge at [param key] (its slot's
## x and z) at [param level] or below.
func _edge_covers(key: Vector2i, level: int) -> bool:
	return _edges.get(key, NONE) <= level


## Whether it cuts away the same pieces as [param other].
func same_pieces(other: LevelCutaway) -> bool:
	if other == null or other.pieces.size() != pieces.size():
		return false
	for piece: int in pieces:
		if not other.pieces.has(piece):
			return false
	return true
