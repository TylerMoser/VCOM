## 12, explored · The map with its open land white, as it was before 12b's ground was applied on
## 2026-10-19 (the ground taken off in memory), at the views the variants of 12 (biome ground
## colours) are pictured at: all the way out, where the biomes are the island; the Duchy tier at 200
## miles, where five biomes meet (the Temperate Mountains, the Desert, the Grassland, the Swamp and
## the Evergreen Rainforest's edge); the County tier at 90 miles, where the Temperate Mountains, the
## Desert and the Grassland meet; and 40 miles in the open Grassland round the party's start, with
## its villages, hamlets, roads and a river, where the ground shows most between the forests. Style
## 0 is the map as it is now, the ground included.
##
## Its constants and static helpers serve every variant (styles 1201 to 1225).
extends RefCounted

const NAME := "The map before its ground"
const LABEL := "12 before"
const Kit := preload("res://_probe/StyleKit.gd")
const VIEWS := [
	["A", "Realm: all the way out", null, 0.0],
	["B", "Duchy tier: 200 miles, five biomes", Vector2(6800, 6400), 200.0],
	["C", "County tier: 90 miles, mountains, desert, grassland", Vector2(7021, 6084), 90.0],
	["D", "40 miles: the Grassland round the party's start", Vector2(7302, 7381), 40.0],
]

## The biomes, by kingdom: 1 Tundra Mountains, 2 Volcanic Mountains (and ruins), 3 Temperate
## Mountains, 4 Desert, 5 Grassland, 6 Evergreen Temperate Rainforest, 7 Swamp, 8 Deciduous Forest,
## 9 Tropical Rainforest. Proposal 12's grounds, the base of most variants.
const GROUND_12 := {
	1: "#e9ecef", 2: "#e3dcd5", 3: "#e5e8dc", 4: "#f4e4c4", 5: "#eef0cf",
	6: "#dcebd8", 7: "#e2e6cf", 8: "#e6efd6", 9: "#d9ecce",
}
## Proposal 12's forests: a shade deeper and more solid than the map's, to stand out on a ground that
## is no longer white. [colour, alpha] by kind.
const FORESTS_12 := {
	"Conifer": ["#86b894", 0.72], "Broadleaf": ["#acd085", 0.7],
	"Swamp": ["#a9ad6c", 0.72], "Tropical": ["#6fb87b", 0.75],
}
## An atlas's biome map: the same hues as 12's, about twice as strong.
const BOLD := {
	1: "#d5dee8", 2: "#dcc7bd", 3: "#d4dbc3", 4: "#f2d398", 5: "#e6e9ad",
	6: "#bcdcc8", 7: "#c6cfa0", 8: "#cde4ae", 9: "#b0d9a2",
}
const FORESTS_BOLD := {
	"Conifer": ["#4e8e68", 0.62], "Broadleaf": ["#7cae56", 0.6],
	"Swamp": ["#7a873a", 0.62], "Tropical": ["#3c8e4a", 0.62],
}
## Neighbouring biomes told apart by lightness as well as hue, so that they differ in greyscale and
## to a red-green colour-blind eye: the Temperate Mountains, which border seven others, the lightest,
## and the rest on three steps chosen so that no two neighbours share one.
const STEPS := {
	1: "#dce2ea", 2: "#c9b9ae", 3: "#f6f6f1", 4: "#f8e8bb", 5: "#cdcc93",
	6: "#c2d6c9", 7: "#e0e3c8", 8: "#adc193", 9: "#d2e6c9",
}
## Earth tones only: stone, ash, sand, straw, loam and clay, no green and no blue, which are left to
## the forests and the water.
const EARTH := {
	1: "#e6e7e6", 2: "#d0c0b4", 3: "#f4f0e7", 4: "#f3ddaf", 5: "#e2d4a9",
	6: "#d4cebf", 7: "#efe6cc", 8: "#cdbd99", 9: "#ecdcbb",
}


func apply(kit) -> void:
	kit.without_ground()


func panels(_kit) -> Array:
	return VIEWS


## Gives the land ground.gdshader with [param params]: by default each county coloured by its
## biome's colour in [param palette] (source 0, so the colours meet exactly on the kingdoms' smooth
## borders), the biome map read for whatever goes by biome. Returns the material.
static func ground(kit, params := {}, palette := GROUND_12, regions := "KingdomMap.png") -> ShaderMaterial:
	var settings := {"source": 0, "palette": Kit.palette_of(palette)}
	settings.merge(params, true)
	if settings["source"] == 0:
		colour_counties(kit, palette)
	return kit.style_ground(settings, regions)


## Every county its biome's colour, and every island in a lake the colour of the county round it.
static func colour_counties(kit, palette: Dictionary, jitter := 0.0) -> void:
	for county: Polygon2D in kit.counties():
		var colour := Kit.hex(palette[kit.kingdom_of(county)])
		if jitter > 0.0:
			colour = shaded(colour, county, jitter)
		county.color = colour
	for island: Polygon2D in kit.lake_islands():
		var at: Vector2 = island.polygon[0]
		for county: Polygon2D in kit.counties():
			if Geometry2D.is_point_in_polygon(at, county.polygon):
				island.color = county.color
				break


## [param colour] made lighter or darker, and a little warmer or cooler, by up to [param amount],
## the same for a county every time (by its number).
static func shaded(colour: Color, county: Node, amount: float) -> Color:
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(str(county.name))
	var light := rng.randf_range(-1.0, 1.0) * amount
	var warm := rng.randf_range(-1.0, 1.0) * amount * 0.5
	var out := colour.lightened(light) if light > 0.0 else colour.darkened(-light)
	return Color(clampf(out.r + warm, 0.0, 1.0), out.g, clampf(out.b - warm, 0.0, 1.0))


## The four kinds of forest given [param looks] ({kind: ["#rrggbb", alpha]}).
static func forests(kit, looks: Dictionary) -> void:
	for kind: String in looks:
		var look: Array = looks[kind]
		kit.set_forest(kind, Kit.hex(look[0], look[1]))


## Every piece of forest given its biome's colour ({biome: "#rrggbb"}) at [param alpha].
static func forests_by_biome(kit, colours: Dictionary, alpha: float) -> void:
	var kingdoms: Dictionary = kit.county_kingdoms()
	for piece: Polygon2D in kit.forests():
		var biome: int = kingdoms.get(Kit.county_of_piece(piece), 0)
		if colours.has(biome):
			piece.color = Kit.hex(colours[biome], alpha)
