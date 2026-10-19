## 20w · A soft horizon. No edge at all: the veil comes in gradually over the outer 70% of the party's
## sight, so what it saw clearly near its way fades into what it only glimpsed, and that into the
## unknown. The quietest frontier, which never draws the eye away from the land itself.
extends RefCounted

const NAME := "A soft horizon"
const LABEL := "20w"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Now.PAPER, "opacity": 0.9, "edge_soft": 1.0}
	_mask = Now.fog(kit, [Now.journey(26.0 * Now.MILE)], veil, ["coast", "kingdoms", "rivers"], Now.SKETCH, 0.6,
			false, {}, 0.7)


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
