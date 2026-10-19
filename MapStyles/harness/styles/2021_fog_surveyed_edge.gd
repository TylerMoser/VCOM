## 20u · A surveyed edge. The fog cut sharp where the party's sight ended, with a fine ink line along the
## edge (the borders' ink, 85%, 1.6 screen pixels), as a surveyor marks the limit of his survey: the
## frontier of what is known is a line on the map, plain at every zoom, and the known land within it
## reads as a finished sheet.
extends RefCounted

const NAME := "A surveyed edge"
const LABEL := "20u"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Now.PAPER, "opacity": 0.9, "edge_soft": 0.04, "rim": Color(0.24, 0.2, 0.3, 0.85),
			"rim_px": 1.6}
	_mask = Now.fog(kit, [Now.journey()], veil)


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
