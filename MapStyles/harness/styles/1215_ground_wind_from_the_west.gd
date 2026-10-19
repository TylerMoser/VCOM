## 12o · The wind from the west. The island's weather comes from the west (a decision of the map's
## from the start), so its west is wetter and its east drier: 12's grounds tinted greener toward the
## west coast and warmer and browner toward the east, across every biome, a little tilted to follow
## the island's lie. A gradient no border interrupts, under the biomes' own steps.
extends RefCounted

const NAME := "The wind from the west"
const LABEL := "12o"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {
		"moisture": 1.0, "wet_west": Color(0.9, 1.0, 0.92), "dry_east": Color(1.0, 0.92, 0.8),
	})
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
