## 20f · Clouds. The unknown under soft white clouds with blue-grey shadows (noise 650 map units across,
## 96%), over land and sea alike, as a strategy game's map hides what has not been explored: nothing
## shows through, not even the coast or the capitals, so every journey is a discovery. The clouds
## part along the party's way.
extends RefCounted

const NAME := "Clouds"
const LABEL := "20f"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"look": 3, "cloud_scale": 650.0, "opacity": 0.96, "veil": Color(0.82, 0.86, 0.92), "grain": 0.0,
			"ragged": 0.35, "ragged_scale": 120.0}
	_mask = Now.fog(kit, [Now.journey()], veil, [], Color(0, 0, 0, 0), 1.0, true)


func ready(kit) -> void:
	kit.hide_unseen(_mask, [])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
