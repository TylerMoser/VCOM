## 12w · Forests in the biome's family. 12's grounds, and every piece of forest in a deeper shade of
## its own biome's hue (at 60%) rather than of its kind of tree: grey-green in the Tundra, olive-brown
## on the Volcanic Mountains, a gold-olive scrub in the Desert, deep green in the rainforests. Ground
## and forest are one family per biome, told apart by depth, so each country reads as one whole and
## no forest's green clashes with its ground.
extends RefCounted

const NAME := "Forests in the biome's family"
const LABEL := "12w"
const Now := preload("res://_probe/styles/1200_ground_now.gd")
const FORESTS := {
	1: "#7f9a92", 2: "#8f8a6e", 3: "#7c9c76", 4: "#a9a066", 5: "#97b064",
	6: "#4f8a69", 7: "#86894a", 8: "#73a457", 9: "#3f8d50",
}


func apply(kit) -> void:
	Now.ground(kit)
	Now.forests_by_biome(kit, FORESTS, 0.6)


func panels(_kit) -> Array:
	return Now.VIEWS
