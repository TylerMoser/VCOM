## 20l · The forests show through. Forests are where battles are met, so their extent is common
## knowledge even where the land is not: in the fog every forest is hatched in a rust ink (diagonal
## lines 6 screen pixels apart, 55%; harness/data/forest_mask.png), a warning rather than a picture.
## The rest as 20b. A party can see that the way ahead crosses forest before it has been there.
extends RefCounted

const NAME := "The forests show through"
const LABEL := "20l"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Now.PAPER, "opacity": 0.93, "forest_ink": Color(0.62, 0.3, 0.2, 0.55), "forest_px": 6.0,
			"ragged": 0.25, "ragged_scale": 90.0}
	_mask = Now.fog(kit, [Now.journey()], veil)


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
