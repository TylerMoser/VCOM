## 20b · The journey. What the fog clears is what the party has seen: everything within 20 miles of
## where it has been, painted into a mask as it travels (StyleKit.fog_mask(), a picture of the sheet
## at 1 km a pixel), not a ring. After some 160 miles from its start through five towns, a winding
## corridor of known land; the rest as 20 had it, a paper veil with the coast, the kingdoms' borders
## and the great rivers sketched over it. This is the mechanism every variant after it builds on.
extends RefCounted

const NAME := "The journey"
const LABEL := "20b"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	_mask = Now.fog(kit, [Now.journey()])


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
