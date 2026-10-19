## 20k · The roads are known. Roads are what travellers talk about: the highways and roads, with their
## bridges, show over the fog in their own look, and so do the towns they join (the capitals of
## kingdoms, duchies and counties), with the coast and the kingdoms' borders. What the fog keeps is
## the land between the roads: the forests, the villages and hamlets, the lanes, the lesser borders.
## A party can plan a road journey from the start, and must explore to find what lies off it.
extends RefCounted

const NAME := "The roads are known"
const LABEL := "20k"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Now.PAPER, "opacity": 0.9, "ragged": 0.25, "ragged_scale": 90.0}
	_mask = Now.fog(kit, [Now.journey()], veil, ["coast", "kingdoms", "roads"], Color(0, 0, 0, 0), 1.0)


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals", "DuchyCapitals", "CountyCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
