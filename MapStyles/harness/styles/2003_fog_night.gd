## 20c · Night fog. The unknown in a deep blue-black (92%), over the sea as well as the land, as the
## dark of a strategy game's unexplored map; the coast, the kingdoms' borders and the great rivers
## sketched over it in a pale silver, and the nine capitals. The known land stands out as the only lit
## country on the map, which makes the party's journey the brightest thing there is.
extends RefCounted

const NAME := "Night fog"
const LABEL := "20c"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Color(0.1, 0.13, 0.19), "opacity": 0.92, "grain": 0.05, "ragged": 0.25, "ragged_scale": 90.0}
	_mask = Now.fog(kit, [Now.journey()], veil, ["coast", "kingdoms", "rivers"], Color(0.76, 0.82, 0.9), 0.6, true)


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
