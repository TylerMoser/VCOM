## 20i · Knowledge fades with distance. The fog is thin near what the party has seen (35%) and thickens
## the further it lies from it (to 95%), read from the mask blurred to its sixth mip level, about 64
## km across: the land just beyond the party's sight is half known, guessed from what it saw, and the
## far side of the realm is a blank. No hard frontier anywhere.
extends RefCounted

const NAME := "Knowledge fades with distance"
const LABEL := "20i"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Now.PAPER, "opacity": 0.95, "distance_lod": 6.0, "near_opacity": 0.35, "ragged": 0.2,
			"ragged_scale": 90.0}
	_mask = Now.fog(kit, [Now.journey()], veil)


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
