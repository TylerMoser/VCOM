## 12q · Paper and mottle. 12's grounds with a broad mottle and a fine grain over them (up to 35% of the
## way to a brown), anchored to the map and keeping their size on the screen at every zoom: the
## hand-coloured paper of an old atlas, which matches the settlements' pen-and-ink pictures.
extends RefCounted

const NAME := "Paper and mottle"
const LABEL := "12q"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {"paper": 0.35})
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
