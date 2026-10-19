## 12n · A coastal strand. A pale sand strand along the sea, a few kilometres deep, ragged by noise
## (harness/data/coast.png: how much of the sea is within 2.7 km, blurred twice), over 12's grounds:
## beaches and dunes, which frame the island and soften the line where the land meets the water.
extends RefCounted

const NAME := "A coastal strand"
const LABEL := "12n"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {"coast_strength": 1.0, "coast_color": Color("#f6ebc8")})
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
