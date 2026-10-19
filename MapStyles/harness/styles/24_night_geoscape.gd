## 24 · Night Geoscape. A dark map, as XCOM's Geoscape and many strategy
## games' campaign maps are: a navy sea, slate land lit by its own relief from
## above, a glowing cyan coastline with water rings, deep-blue lakes and bright
## rivers, amber roads that glow, dim violet borders, light settlements and
## names, the party and its route in cyan. Bright means important, and on a
## dark ground only a few things can be bright; easy on the eyes in long
## sessions, and it suits the battle screens' dark menus.
extends RefCounted

const NAME := "Night Geoscape"


func apply(kit) -> void:
	kit.set_land(Color("#1b2734"))
	kit.set_sea(Color("#0b1624"))
	for lake: Polygon2D in kit.lakes():
		lake.color = Color("#10304c")
	kit.color_lines("Rivers", Color("#3d9be0"))
	kit.color_lines("Channels", Color("#3d9be0"))
	kit.style_coast({
		"shore": Color("#5cc8f0"), "shore_share": 0.12, "ring": Color("#2a6f9e", 0.55), "rings": 2,
		"ring_share": 0.07, "ring_min_px": 3.0,
	}, 1.6)
	kit.add_relief(0.55, 0.22, Color(0.0, 0.02, 0.06))
	var woods := {"Conifer": "#1f4a3c", "Broadleaf": "#2b4d2e", "Swamp": "#3b4628", "Tropical": "#1d4f34"}
	for kind: String in woods:
		kit.set_forest(kind, Color(woods[kind], 0.85))
	kit.style_rank("Kingdoms", Color("#9a8fd6"), 9.0, kit.line_material({"dash": 3.0, "gap": 1.0, "dot": 0.8, "dot_gap": 0.8}), "onto")
	kit.style_rank("Duchies", Color("#7a74b0"), 6.0, kit.line_material({"dash": 2.2, "gap": 1.3}), "onto")
	kit.style_rank("Counties", Color("#5c5888"), 4.5, kit.line_material({"dot": 0.85, "gap": 1.1}), "onto")
	for rank: String in ["Kingdoms", "Duchies", "Counties"]:
		var alpha: float = {"Kingdoms": 0.75, "Duchies": 0.6, "Counties": 0.5}[rank]
		kit.set_alpha("Borders/" + rank, alpha)
		kit.set_alpha("BordersOverLakes/" + rank, alpha)
	# The roads glow: a wide faint casing of their own colour under each.
	var glows := {"Highways": "#ffbd59", "Roads": "#c99247", "Lanes": "#8a6a3e"}
	for kind: String in glows:
		kit.color_lines("Roads/" + kind, Color(glows[kind]))
		kit.add_casing("Roads/" + kind, Color(glows[kind], 0.18), {"Highways": 14.0, "Roads": 9.0, "Lanes": 4.0}[kind], "Glow")
	kit.color_lines("Bridges", Color("#e0a64f"))


func ready(kit) -> void:
	kit.trim_sea_ends(0.7)
	kit.tint_settlements("", Color("#dfe7f2"))
	kit.tint_settlements("KingdomCapitals", Color("#ffd27a"))
	kit.tint_settlements("DuchyCapitals", Color("#ffd27a"))
	var labels: Node2D = kit.runtime("MapLabels.gd").new()
	labels.map = kit.map
	labels.dark = true
	kit.map.add_child(labels)
	var route: Node2D = kit.runtime("RouteOverlay.gd").new()
	route.party = kit.at("Party")
	route.route = PackedVector2Array([Vector2(6900.0, 7230.0), Vector2(6420.0, 7020.0)])
	route.safe_color = Color("#4fd1ff")
	route.danger_color = Color("#ff6b5a")
	route.party_color = Color("#4fd1ff")
	route.casing_color = Color("#0b1624")
	route.tick_color = Color("#dfe7f2")
	kit.map.add_child(route)
