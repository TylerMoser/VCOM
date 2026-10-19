## 18 · Focus lens. Detail gathers round the party and thins out with
## distance from it: within about 40 miles every border, road, lane and
## village is drawn as now; past about 90 the county and duchy borders, the
## lanes and the lesser roads fade away and the villages and hamlets go, while
## kingdom borders, highways, rivers, lakes, towns and cities stay as the
## frame of the map. A dashed ring shows two days' travel. What the party can
## act on is crisp; the rest of the island is quieter context.
##
## Each faded line keeps its own colour and takes map_line.gdshader with a
## focus: one uniform, the party's position, shared by every material, set
## once a frame for real. The forests fade a little too (forest.gdshader).
extends RefCounted

const NAME := "Focus lens"

const PARTY := Vector2(7302.0, 7381.0)
const MILE := 16.09344
## Whole within this many miles of the party, at its floor beyond the second.
const INNER_MILES := 40.0
const OUTER_MILES := 90.0
## The share of each layer left far from the party.
const FLOORS := {
	"Borders/Kingdoms": 0.5, "BordersOverLakes/Kingdoms": 0.5,
	"Borders/Duchies": 0.12, "BordersOverLakes/Duchies": 0.12,
	"Borders/Counties": 0.0, "BordersOverLakes/Counties": 0.0,
	"Roads/Highways": 0.6, "Roads/Roads": 0.22, "Roads/Lanes": 0.0,
	"Bridges": 0.25, "Channels": 0.0, "Rivers": 0.7,
}

var _far_places: Array = []


func apply(kit) -> void:
	var inner := INNER_MILES * MILE
	var outer := OUTER_MILES * MILE
	for path: String in FLOORS:
		var material: ShaderMaterial = kit.line_material({
			"focus": PARTY, "focus_inner": inner, "focus_outer": outer, "focus_floor": FLOORS[path],
		})
		kit.pattern_lines(path, material)
	for kind: String in ["Conifer", "Broadleaf", "Swamp", "Tropical"]:
		var own: Color = kit.forests(kind)[0].color
		kit.style_forests(kind, own, {
			"glyph": 0, "focus": PARTY, "focus_inner": inner, "focus_outer": outer, "focus_floor": 0.55,
		})


func ready(kit) -> void:
	var outer: float = OUTER_MILES * MILE
	for group: String in ["Villages", "Hamlets"]:
		for place: Node2D in kit.settlements(group):
			if place.position.distance_to(PARTY) > outer:
				place.visible = false
	for place: Node2D in kit.settlements("CountyCapitals"):
		if place.position.distance_to(PARTY) > outer:
			place.modulate.a = 0.55
	var ring: Node2D = kit.runtime("RouteOverlay.gd").new()
	ring.party = kit.at("Party")
	ring.reach_days = 2.0
	ring.party_color = Color("#d93025")
	kit.map.add_child(ring)
