## 20d · The unknown in grey. The land not yet seen is drawn as it is, but in grey and lighter (its
## colours taken off and 40% of the way to white): the shape of the country is known, as from an old
## map, but not what is there now, and its settlements are hidden. No sketch is needed, since the
## lines show through in grey. Where the party has been, colour.
extends RefCounted

const NAME := "The unknown in grey"
const LABEL := "20d"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"look": 1, "grey_light": 0.4, "opacity": 1.0, "veil": Color(0.97, 0.96, 0.93), "grain": 0.0,
			"ragged": 0.2, "ragged_scale": 90.0}
	_mask = Now.fog(kit, [Now.journey()], veil, [])


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
