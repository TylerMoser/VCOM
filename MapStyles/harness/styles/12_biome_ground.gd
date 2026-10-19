## 12 · Biome ground colours. The open land is no longer one white: each
## kingdom, which is a biome, has a pale ground of its own country's colour
## (snow-grey tundra, ash-brown volcanic land, sand desert, straw grassland,
## moss-green rainforest...), light enough for every line to read over it. Where
## the party is, and what kind of country lies ahead, shows at a glance, as
## deserts and ice do on Google's land cover. The forests are a shade deeper
## and more solid, so they stand out from a ground that is no longer white.
extends RefCounted

const NAME := "Biome ground colours"

## By kingdom: 1 Tundra Mountains, 2 Volcanic Mountains / Ruins, 3 Temperate
## Mountains, 4 Desert, 5 Grassland, 6 Evergreen Temperate Rainforest,
## 7 Swamp, 8 Deciduous Forest, 9 Tropical Rainforest.
const GROUND := {
	1: "#e9ecef", 2: "#e3dcd5", 3: "#e5e8dc", 4: "#f4e4c4", 5: "#eef0cf",
	6: "#dcebd8", 7: "#e2e6cf", 8: "#e6efd6", 9: "#d9ecce",
}
const FORESTS := {
	"Conifer": ["#86b894", 0.72], "Broadleaf": ["#acd085", 0.7],
	"Swamp": ["#a9ad6c", 0.72], "Tropical": ["#6fb87b", 0.75],
}


func apply(kit) -> void:
	for county: Polygon2D in kit.counties():
		county.color = kit.hex(GROUND[kit.kingdom_of(county)])
	# An island in a lake takes the ground of the county it lies in.
	for island: Polygon2D in kit.lake_islands():
		var at: Vector2 = island.polygon[0]
		for county: Polygon2D in kit.counties():
			if Geometry2D.is_point_in_polygon(at, county.polygon):
				island.color = county.color
				break
	for kind: String in FORESTS:
		var look: Array = FORESTS[kind]
		kit.set_forest(kind, kit.hex(look[0], look[1]))
