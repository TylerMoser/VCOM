## 12l · Green river valleys. In the dry country a green strip follows every river, as oases and
## water meadows do: wide along the great rivers, a thread along a stream (harness/data/wetness.png,
## each river drawn four times its width and blurred over 3.4 km). Fullest in the Desert (1.0), then
## the Grassland (0.8), the Volcanic Mountains (0.6), the Temperate Mountains (0.45) and the Tundra
## (0.35); none in the four wet biomes, which are green already. Where the water is, the land lives.
extends RefCounted

const NAME := "Green river valleys"
const LABEL := "12l"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {
		"wet_strength": 0.85,
		"dry": PackedFloat32Array([0.0, 0.35, 0.6, 0.45, 1.0, 0.8, 0.0, 0.0, 0.0, 0.0]),
	})
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
