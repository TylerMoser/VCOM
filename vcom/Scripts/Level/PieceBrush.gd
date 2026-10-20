@tool
## A few pieces the level editor places together in one click, as a group:
## a whole tree, its trunk and its crown, rather than each in turn.
##
## Each piece is a kind, a slot offset from where the brush is placed (x and z
## in half cells, y in cells, as [LevelData] counts slots) and a turn, in
## quarter turns about up. The editor turns the whole brush with its own turn,
## offsets and pieces alike, and an offset is always kept a whole cell in each
## direction or half of one (a piece on an edge), so the brush stays on the
## grid wherever it is placed. Pieces are placed in order, so a later one wins
## where two overlap.
class_name PieceBrush
extends Resource

## What the level editor calls it.
@export var display_name := ""
## Each piece's kind ([member PieceKind.id]), slot offset and turn, one entry
## of each list a piece.
@export var kinds: Array[StringName] = []
@export var offsets: Array[Vector3i] = []
@export var turns: PackedInt32Array = []


## How many pieces it places.
func size() -> int:
	return mini(kinds.size(), offsets.size())


## The turn of piece [param index], 0 if none was given.
func turn_of(index: int) -> int:
	return turns[index] if index < turns.size() else 0
