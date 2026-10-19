## 12e · Earth tones. The ground in stone, ash, sand, straw, loam and clay: no green and no blue, which
## are left to the forests and the water. A green on the map then always means forest, where battles
## are met, and a blue always water, whatever the biome; the rainforests are told by a warm laterite
## and a cool peat rather than by green.
extends RefCounted

const NAME := "Earth tones"
const LABEL := "12e"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {}, Now.EARTH)
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
