## 12u · With shaded relief. 12's grounds under proposal 13's shaded relief (harness/data/hillshade.png,
## lit from the north-west; up to 32% shade and 8% light, over the land and the forests): the biome
## says what the country is, the relief where its ranges and valleys run. Proposal 17's Terrain mode
## is this pair.
extends RefCounted

const NAME := "With shaded relief"
const LABEL := "12u"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit)
	Now.forests(kit, Now.FORESTS_12)
	kit.add_relief(0.32, 0.08)


func panels(_kit) -> Array:
	return Now.VIEWS
