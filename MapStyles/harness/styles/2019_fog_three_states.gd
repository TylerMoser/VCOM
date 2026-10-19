## 20s · Seen, remembered, unknown. Three states, as a real-time strategy game's fog has: in sight now
## (20 miles round the party) in full colour; seen before but out of sight now in grey, remembered as
## it was; never seen under the paper veil. On a campaign map nothing moves yet, but it says how old
## the party's knowledge of a place is, and leaves room for things that do (other parties, events)
## to show only where the party can see them.
extends RefCounted

const NAME := "Seen, remembered, unknown"
const LABEL := "20s"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Now.PAPER, "opacity": 0.93, "ragged": 0.25, "ragged_scale": 90.0,
			"party": Now.JOURNEY[Now.JOURNEY.size() - 1], "sight": Now.SIGHT, "memory": 1.0, "memory_look": 1}
	_mask = Now.fog(kit, [Now.journey()], veil)


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
