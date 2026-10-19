## 22 · Google Maps. The whole map restyled in the manner of Google's own:
## a warm light-grey land, mint woods, one light blue for all water with no
## coastline, white roads between grey casings and amber highways, borders as
## thin grey dashes, settlements as small dots, names in dark grey with a white
## halo, and the route in Google's blue. The look players already read without
## thinking; every line type is told apart by at least two of colour,
## lightness, width and pattern.
extends RefCounted

const NAME := "Google Maps"
const Symbols := preload("res://_probe/runtime/Symbols.gd")

const LAND := "#f3f1ec"
const WATER := "#a9d2f3"
const RIVER := "#8cc2ee"
const WOODS := {"Conifer": "#c4e2c3", "Broadleaf": "#d2eac6", "Swamp": "#d4dfbf", "Tropical": "#bfe0bd"}
## Each road kind: width share, fill, casing, least pixels for a casing.
const ROADS := {
	"Highways": [2.0, "#fcd581", "#e3a43b", 4.0],
	"Roads": [2.0, "#ffffff", "#d3cdc3", 4.5],
	"Lanes": [1.75, "#ffffff", "#ddd8cf", 5.0],
}


func apply(kit) -> void:
	kit.set_land(Color(LAND))
	kit.set_sea(Color(WATER))
	for lake: Polygon2D in kit.lakes():
		lake.color = Color(WATER)
	kit.color_lines("Rivers", Color(RIVER))
	kit.color_lines("Channels", Color(RIVER))
	kit.style_coast({"shore": Color("#97c3e6"), "shore_share": 0.4, "rings": 0}, 0.3)
	for kind: String in WOODS:
		kit.set_forest(kind, Color(WOODS[kind]))
	for kind: String in ROADS:
		var look: Array = ROADS[kind]
		kit.scale_widths("Roads/" + kind, look[0])
		kit.pattern_lines("Roads/" + kind, kit.line_material({
			"fill_from_line": false, "fill": Color(look[1]), "casing": Color(look[2]), "casing_share": 0.3,
			"casing_min_px": look[3], "narrow": Color(look[2]).darkened(0.05),
		}))
	for bridge: Line2D in kit.lines_in("Bridges"):
		var on_lane: bool = bridge.get_parent().name == &"Lanes"
		var kind: String = "Lanes" if on_lane else ("Highways" if bridge.width > 15.0 else "Roads")
		bridge.width = {"Lanes": 4.0, "Highways": 10.0, "Roads": 7.0}[kind] * ROADS[kind][0] * 1.4
		kit.pattern_line(bridge, kit.line_material({
			"fill_from_line": false, "fill": Color(ROADS[kind][1]), "casing": Color("#a8a29a"), "casing_share": 0.4,
			"casing_min_px": 3.0, "narrow": Color("#a8a29a"),
		}))
	kit.style_rank("Kingdoms", Color("#8f8499"), 7.0, kit.line_material({"dash": 2.4, "gap": 1.0}), "onto")
	kit.style_rank("Duchies", Color("#a69eae"), 5.0, kit.line_material({"dash": 1.6, "gap": 1.2}), "onto")
	kit.style_rank("Counties", Color("#c2bcc6"), 4.0, kit.line_material({"dash": 0.9, "gap": 0.9}), "onto")


func ready(kit) -> void:
	kit.trim_sea_ends(0.12)
	var ink := Color("#5f6368")
	var symbols := {}
	for group: String in Symbols.FOR_GROUP:
		var look: Array = Symbols.FOR_GROUP[group]
		symbols[group] = [Symbols.texture(look[0], ink, Color(1, 1, 1, 0.95)), look[1]]
	for place: Node2D in kit.settlements():
		var group := str(place.get_parent().name)
		place.set("icon", symbols[group][0])
		place.set("icon_height", symbols[group][1])
	var labels: Node2D = kit.runtime("MapLabels.gd").new()
	labels.map = kit.map
	labels.ink = Color("#3c4043")
	kit.map.add_child(labels)
	var route: Node2D = kit.runtime("RouteOverlay.gd").new()
	route.party = kit.at("Party")
	route.route = PackedVector2Array([Vector2(6900.0, 7230.0), Vector2(6420.0, 7020.0)])
	route.danger_color = Color("#ea4335")
	kit.map.add_child(route)
