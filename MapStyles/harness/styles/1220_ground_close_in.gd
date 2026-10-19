## 12t · Quiet far out, biomes close in. The other way round: the land nearly white far out (15% of the
## atlas palette at and over 400 miles), where the kingdoms' borders and the rivers lead, and the
## biome's colour coming up as the view closes in, 90% at and under 60 miles: the country the party
## is in, felt where the party is.
extends RefCounted

const NAME := "Quiet far out, biomes close in"
const LABEL := "12t"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {
		"fade_far_miles": 400.0, "fade_near_miles": 60.0, "strength_far": 0.15, "strength_near": 0.9,
	}, Now.BOLD)
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
