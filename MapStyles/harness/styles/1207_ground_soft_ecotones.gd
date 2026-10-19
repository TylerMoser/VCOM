## 12g · Soft ecotones. Where two biomes meet, their colours blend over some 14 km (140 units, a disc
## of 17 taps), as real country changes: the steppe greens toward the forest, the desert's sand fades
## into the grassland's straw. No hard edge in the ground at all, so a kingdom's border is drawn by
## its line alone, and a party crossing it sees the country change before the border says so.
extends RefCounted

const NAME := "Soft ecotones"
const LABEL := "12g"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {"source": 1, "soft_units": 140.0})
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
