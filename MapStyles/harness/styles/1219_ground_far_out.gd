## 12s · Biomes far out, quiet close in. The atlas palette whole at and over 400 miles tall, where the
## map is about the realm, fading by the logarithm of the height to a quarter of it at and under 40
## miles, where it is about the road ahead: 14b's rule for the borders, given to the ground. All the
## way out the island is a biome map; close in the roads and forests have the white land back.
extends RefCounted

const NAME := "Biomes far out, quiet close in"
const LABEL := "12s"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {
		"fade_far_miles": 400.0, "fade_near_miles": 40.0, "strength_far": 1.0, "strength_near": 0.25,
	}, Now.BOLD)
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
