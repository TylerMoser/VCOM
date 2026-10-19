## 20e · Out of focus. The land not yet seen is drawn as it is but blurred (the screen behind it read at
## a coarse mip level, a little paled): its broad shapes, colours of forest and water, are there, and
## nothing can be made out. Known land is sharp. As a photograph's depth of field, the eye goes to what
## is in focus: where the party has been.
extends RefCounted

const NAME := "Out of focus"
const LABEL := "20e"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"look": 2, "blur_lod": 3.5, "opacity": 1.0, "veil": Color(0.95, 0.95, 0.93), "grain": 0.0,
			"ragged": 0.2, "ragged_scale": 90.0}
	_mask = Now.fog(kit, [Now.journey()], veil, [])


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
