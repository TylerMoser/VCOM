## 12y · The forests carry the biome. The open land stays white, as now; instead every piece of forest
## takes its biome's colour (at 50%, a little stronger than now), so half the land, the wild half,
## is a biome map by itself: blue-grey forests in the Tundra, ash-brown on the Volcanic Mountains,
## gold-olive scrub in the Desert, deep green in the rainforests. No new layer and no shader: four
## scenes' colours become one a biome. The ground's white keeps every line at its full contrast.
extends RefCounted

const NAME := "The forests carry the biome"
const LABEL := "12y"
const Now := preload("res://_probe/styles/1200_ground_now.gd")
const FORESTS := {
	1: "#9fb3b8", 2: "#b39b8a", 3: "#8fae86", 4: "#c9b16a", 5: "#a9c26a",
	6: "#5e9a7d", 7: "#9a9a52", 8: "#86b85f", 9: "#3f9a55",
}


func apply(kit) -> void:
	kit.without_ground()
	Now.forests_by_biome(kit, FORESTS, 0.5)


func panels(_kit) -> Array:
	return Now.VIEWS
