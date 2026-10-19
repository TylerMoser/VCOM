## 12m · Fields round the settlements. Where people live, the land is farmed: a patchwork of fields in
## wheat, pasture and fallow (blocks of 2 km, turned 30 degrees so no grid shows), thick round the
## towns and thinning between the villages (harness/data/farmland.png, every settlement a disc by its
## rank, blurred over 4 km), over 12's grounds at 75%. Far out, where a field is under a few pixels,
## an even tint instead. The wild land, where battles are met, is what is left.
extends RefCounted

const NAME := "Fields round the settlements"
const LABEL := "12m"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {
		"strength": 0.75, "farm_strength": 1.1, "farm_cell": 20.0,
		"farm_a": Color("#efe2a6"), "farm_b": Color("#d6e7b5"), "farm_c": Color("#e7d9bd"),
	})
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
