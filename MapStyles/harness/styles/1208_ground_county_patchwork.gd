## 12h · County patchwork. Each county its biome's colour made a little lighter or darker, warmer or
## cooler (up to 4%, the same for a county every time), like the patchwork of a hand-coloured estate
## map: the counties show in the ground itself, at every zoom, even where their dotted borders are
## faint or not yet shown (they come at 100 miles now), and the biome still reads by its hue.
extends RefCounted

const NAME := "County patchwork"
const LABEL := "12h"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit)
	Now.colour_counties(kit, Now.GROUND_12, 0.04)
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
