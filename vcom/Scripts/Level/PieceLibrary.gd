@tool
## Every kind of piece a level can be built of, and the brushes that place
## several at once: the level editor's palette, shared by every map, as the
## blocks' MeshLibrary was.
class_name PieceLibrary
extends Resource

@export var kinds: Array[PieceKind] = []
@export var brushes: Array[PieceBrush] = []


## The kind called [param id], or null if there is none.
func find(id: StringName) -> PieceKind:
	for kind in kinds:
		if kind != null and kind.id == id:
			return kind
	return null
