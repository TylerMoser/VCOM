## 12f · By the land, not the kingdom. The biomes as the land was shaped (SourceData/TerrainMap.png),
## not as the kingdoms were later drawn along rivers and ridges: on 3.9% of the land the country is a
## neighbour's, so a desert runs on a little past its kingdom's border, a mountain range crosses
## into the grassland, and the colour no longer jumps at every political line. The ground then says
## what the country is like and the borders say whose it is: two things, told apart. Blended over 1
## km where the biomes meet, which hides the picture's 335 m pixels close in.
extends RefCounted

const NAME := "By the land, not the kingdom"
const LABEL := "12f"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {"source": 1, "soft_units": 10.0}, Now.GROUND_12, "TerrainMap.png")
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
