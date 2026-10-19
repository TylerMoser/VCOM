## 20t · The fog returns. What the party saw long ago fades back under the veil, by how long ago (the
## mask's second channel, painted with the time along the journey): its start is three quarters
## veiled again, the last leg clear. Knowledge goes out of date, so going back is worth something;
## for real, the recency would be the campaign's clock when each place was seen, and fade over days.
extends RefCounted

const NAME := "The fog returns"
const LABEL := "20t"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Now.PAPER, "opacity": 0.93, "ragged": 0.25, "ragged_scale": 90.0, "age_fade": 0.75}
	_mask = Now.fog(kit, [Now.journey()], veil)


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
