## 12i · Biome bands at the borders. The biome's colour only in a band 26 screen pixels wide inside
## each kingdom's border, fading to the land's white within (proposal 03's band, in the biome's
## colour rather than a kingdom's): every kingdom framed by its country, the middle of the map left
## white for the roads and settlements. The band keeps its width on the screen at every zoom, read
## from harness/data/kingdom_edge.png (how far each pixel is from a kingdom's border).
extends RefCounted

const NAME := "Biome bands at the borders"
const LABEL := "12i"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {"band_px": 26.0}, Now.BOLD)


func panels(_kit) -> Array:
	return Now.VIEWS
