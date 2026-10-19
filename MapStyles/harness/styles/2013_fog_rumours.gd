## 20m · Rumoured places. Every town the party has not seen (the capitals of duchies and counties) is a
## faint ring with a question mark over the fog, the same size on the screen at every zoom
## (runtime/FogMarks.gd): its name and its place are known by hearsay, what it holds is not. The
## villages and hamlets stay hidden. The rest as 20b. The map invites the party to go and see.
extends RefCounted

const NAME := "Rumoured places"
const LABEL := "20m"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	_mask = Now.fog(kit, [Now.journey()])


func ready(kit) -> void:
	var hidden: Dictionary = kit.hide_unseen(_mask, ["KingdomCapitals"])
	var marks: Node2D = kit.runtime("FogMarks.gd").new()
	marks.name = "Rumours"
	for group: String in ["DuchyCapitals", "CountyCapitals"]:
		marks.points.append_array(hidden.get(group, []))
	marks.z_index = 3
	kit.map.add_child(marks)
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
