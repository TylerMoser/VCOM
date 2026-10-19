## 12k · Snow and bare rock. Whatever the biome, the land over about 1,200 m is bare rock (a warm grey)
## and above the snowline snow: 2,145 m in the far south, falling to 1,550 m in the far north (snow on
## 1.8% of the land: 8.6% of the Temperate Mountains, 5.3% of the Tundra, 2% of the Volcanic
## Mountains; bare rock on 5.4%, all in those three); both edges softened and made ragged by noise.
## The biome's own colour, at 70%, below.
extends RefCounted

const NAME := "Snow and bare rock"
const LABEL := "12k"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {"strength": 0.7, "rock_from": 0.6, "snow_from": 0.8, "snow_north": 0.12})
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
