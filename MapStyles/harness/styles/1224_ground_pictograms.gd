## 12x · Biome pictograms. Little pictures scattered sparsely over each biome, as a fantasy map's
## country is shown: snowflakes on the Tundra, volcanoes on the Volcanic Mountains, peaks on the
## Temperate Mountains, cacti in the Desert, grass in the Grassland, conifers in the Evergreen
## Rainforest, reeds in the Swamp, round trees in the Deciduous Forest, palms in the Tropical
## Rainforest. 58 screen pixels apart and on a fifth of the places at every zoom, in a brown ink
## (55%), over a ground of 12's hues at only 35%: the country told by pictures more than colours.
extends RefCounted

const NAME := "Biome pictograms"
const LABEL := "12x"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {
		"strength": 0.35, "icon": PackedInt32Array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
		"icon_color": Color(0.32, 0.27, 0.2, 0.55), "icon_px": 58.0, "icon_density": 0.22,
	})


func panels(_kit) -> Array:
	return Now.VIEWS
