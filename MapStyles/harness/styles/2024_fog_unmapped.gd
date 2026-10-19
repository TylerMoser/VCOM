## 20x · Unmapped, not veiled. No veil colour at all: the land not yet seen is simply blank, the land's
## own white, as an unfinished map is, with what everyone knows drawn on it in its own look (the coast,
## the kingdoms' borders, the great rivers and lakes, the nine capitals). The sea stays blue. The map
## does not look fogged, only incomplete, and the party's journey fills it in.
extends RefCounted

const NAME := "Unmapped, not veiled"
const LABEL := "20x"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Color(1, 1, 1), "opacity": 1.0, "grain": 0.0, "ragged": 0.2, "ragged_scale": 90.0}
	_mask = Now.fog(kit, [Now.journey()], veil, ["coast", "kingdoms", "rivers", "lakes"], Color(0, 0, 0, 0), 1.0)


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
