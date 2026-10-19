## 20o · County by county. Setting foot in a county reveals the whole of it, at once, and nothing
## beyond it: the fog lies on the counties not yet entered, each a copy of its own outline, so its
## edge is the county's border exactly. The journey enters 6 counties (115, 112, 116, 113, 121 and 69,
## those of its towns). Exploring becomes a matter of whole counties, which the map already counts
## in, and the frontier is always a border.
extends RefCounted

const NAME := "County by county"
const LABEL := "20o"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var entered := Now.journey_counties(kit)
	var veil := {"veil": Now.PAPER, "opacity": 0.93}
	_mask = Now.fog(kit, [], veil, ["coast", "kingdoms", "rivers"], Now.SKETCH, 0.6, false, entered)
	print("MapStyleProbe: 20o: the journey enters counties %s" % str(entered.keys()))


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
