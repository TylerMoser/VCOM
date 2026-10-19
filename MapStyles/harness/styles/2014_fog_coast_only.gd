## 20n · Only the coast. Nothing is known but the island's shape: the coast sketched in ink over the
## paper veil, and no capital, border or river. The strongest sense of an unknown country, and the
## calmest map at the start of a campaign; every name and line on it is the party's own discovery.
extends RefCounted

const NAME := "Only the coast"
const LABEL := "20n"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	_mask = Now.fog(kit, [Now.journey()], Now.VEIL, ["coast"])


func ready(kit) -> void:
	kit.hide_unseen(_mask, [])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
