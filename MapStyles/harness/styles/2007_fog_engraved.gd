## 20g · Terra incognita, engraved. The unknown on a paper veil hatched by an engraver (diagonal lines 6
## screen pixels apart in a brown ink, 40%), as old maps filled what they did not know; the coast and
## the kingdoms' borders sketched in the same ink. It says "not known" in a way no flat tint does, and
## suits the settlements' pen-and-ink pictures.
extends RefCounted

const NAME := "Terra incognita, engraved"
const LABEL := "20g"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"look": 4, "veil": Color(0.95, 0.92, 0.85), "opacity": 0.95, "ink": Color(0.42, 0.33, 0.22, 0.4),
			"hatch_px": 6.0, "hatch_width": 0.18, "ragged": 0.3, "ragged_scale": 90.0}
	_mask = Now.fog(kit, [Now.journey()], veil, ["coast", "kingdoms"], Color(0.38, 0.3, 0.2))


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
