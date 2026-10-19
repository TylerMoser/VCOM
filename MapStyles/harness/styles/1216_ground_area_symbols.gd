## 12p · Area symbols. Each biome's ground carries a small mark of its own, as topographic maps mark
## sand, marsh and rock: ice crosses on the Tundra, cinders on the Volcanic Mountains, rock strokes on
## the Temperate Mountains, dune arcs on the Desert, grass tufts on the Grassland, leaves on the
## Evergreen Rainforest, marsh tufts in the Swamp, rings in the Deciduous Forest, stipple in the
## Tropical Rainforest. 15 screen pixels apart at every zoom, in a faint brown ink (30%), over 12's
## grounds at 70%. The biome reads by its mark in greyscale and to any eye.
extends RefCounted

const NAME := "Area symbols"
const LABEL := "12p"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {
		"strength": 0.7, "pattern": PackedInt32Array([0, 5, 6, 4, 7, 2, 8, 3, 9, 1]),
		"pattern_color": Color(0.33, 0.28, 0.2, 0.3), "pattern_px": 15.0, "pattern_size": 0.55,
		"pattern_density": 0.8,
	})
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
