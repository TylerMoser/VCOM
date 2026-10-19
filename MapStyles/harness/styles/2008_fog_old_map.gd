## 20h · An old map. The unknown drawn from an old map rather than veiled blank: parchment (94%), the
## coast and the great rivers sketched in sepia, and little hill marks wherever the land is over about
## 900 m (elevation.png, 26 screen pixels apart), as a medieval mapmaker drew ranges he had only heard
## of. No borders: an old map's are out of date. The kingdoms' capitals, which every old map has.
extends RefCounted

const NAME := "An old map"
const LABEL := "20h"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Color(0.94, 0.89, 0.78), "opacity": 0.94, "hills_from": 0.52, "hills_px": 26.0,
			"ink": Color(0.45, 0.35, 0.22, 0.5), "grain": 0.1, "ragged": 0.3, "ragged_scale": 90.0}
	_mask = Now.fog(kit, [Now.journey()], veil, ["coast", "rivers"], Color(0.46, 0.34, 0.2))


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
