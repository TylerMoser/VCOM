## 12j · Uplands and lowlands. 12's grounds made cooler and darker with the height (toward a
## blue-grey, up to 45%) and warmer near sea level (up to 50% toward a cream): the shape of the land
## in the ground's tone, without the shading of a relief. The three mountain kingdoms darken toward
## their spines, the river plains glow warm.
extends RefCounted

const NAME := "Uplands and lowlands"
const LABEL := "12j"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {"height_shade": 0.45, "low_shade": 0.5})
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
