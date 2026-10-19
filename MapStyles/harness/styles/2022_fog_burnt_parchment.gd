## 20v · Burnt parchment. The unknown is the parchment beyond a burnt, ragged edge: a browned band 16
## screen pixels deep along the edge, darker paper with a heavier grain beyond, the edge torn by noise
## at two scales. The known land seems cut out of an old map, which suits the pen-and-ink settlements.
extends RefCounted

const NAME := "Burnt parchment"
const LABEL := "20v"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Color(0.9, 0.84, 0.72), "opacity": 0.95, "grain": 0.12, "ragged": 0.45,
			"ragged_scale": 70.0, "edge_soft": 0.25, "burn": Color(0.42, 0.26, 0.1, 0.8), "burn_px": 16.0}
	_mask = Now.fog(kit, [Now.journey()], veil, ["coast", "kingdoms", "rivers"], Color(0.4, 0.3, 0.18))


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
