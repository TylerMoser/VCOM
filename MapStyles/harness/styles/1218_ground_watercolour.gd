## 12r · Watercolour wash. The atlas palette at 85%, blended over 7 km where biomes meet, the pigment
## pooled darker along those edges and mottled across each wash, on a faint paper: a painter's map,
## where each biome is a wash laid by hand and the borders are drawn over it in ink.
extends RefCounted

const NAME := "Watercolour wash"
const LABEL := "12r"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {"source": 1, "soft_units": 70.0, "wash": 0.6, "paper": 0.2, "strength": 0.85}, Now.BOLD)
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
