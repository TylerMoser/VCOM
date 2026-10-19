## 25 · Parchment atlas. An old hand-coloured atlas, which is what the
## settlements' pen-and-ink pictures (the Penflower Ink pack) were drawn for:
## parchment with a faint grain and sepia hill shading, a sea-green sea framed
## by an inked coast and water lines, the kingdoms' borders in red-brown
## dash-and-dot with a watercolour wash along each side in the kingdom's colour,
## brown roads (solid, dashed, dotted by rank), forests as inked trees over a
## green wash, and names set in a serif. Every kind of line differs by pattern
## as much as by colour, as engravers had to.
extends RefCounted

const NAME := "Parchment atlas"

const PAPER := "#ecdfbf"
## Watercolour washes along the kingdoms' borders, by kingdom.
const WASH := ["#ecdfbf", "#7f93c4", "#c47f8f", "#b59a47", "#d18d5a", "#9480c0", "#5e9e98", "#8f9c52", "#c46a5c", "#6aa36f"]


func apply(kit) -> void:
	for county: Polygon2D in kit.counties():
		county.color = Color(kit.kingdom_of(county) / 255.0, kit.duchy_of(county) / 255.0, 0.0, 1.0)
	for island: Polygon2D in kit.lake_islands():
		island.color = Color(0.0, 0.0, 0.0, 1.0)
	var palette := []
	for code: String in WASH:
		palette.append(Color(code))
	kit.style_land({
		"palette_mode": true, "palette": palette, "band_px": 18.0, "band_base": Color(PAPER),
		"band_strength": 0.5, "paper": 0.5, "paper_dark": Color("#8a6a3e"),
	})
	kit.set_sea(Color("#bfd2c4"))
	for lake: Polygon2D in kit.lakes():
		lake.color = Color("#a6c2b5")
	kit.color_lines("Rivers", Color("#4f7f7a"))
	kit.color_lines("Channels", Color("#4f7f7a"))
	kit.scale_widths("Rivers", 0.75)
	kit.style_coast({
		"shore": Color("#3a2e22"), "shore_share": 0.11, "ring": Color("#5f766c", 0.7), "rings": 4,
		"ring_share": 0.055, "ring_min_px": 2.5,
	}, 2.4)
	kit.add_relief(0.45, 0.06, Color(0.42, 0.33, 0.2))
	var marks := {"Conifer": 1, "Broadleaf": 2, "Swamp": 3, "Tropical": 4}
	for kind: String in marks:
		kit.style_forests(kind, Color("#a9b278", 0.38), {
			"glyph": marks[kind], "mark": Color("#41402a", 0.72), "cell_px": 15.0, "mark_size": 0.68, "density": 0.75,
		})
	var ink := Color("#5b3a1e")
	kit.scale_widths("Roads/Highways", 1.2)
	kit.color_lines("Roads/Highways", ink)
	kit.color_lines("Roads/Roads", ink)
	kit.pattern_lines("Roads/Roads", kit.line_material({"dash": 2.4, "gap": 1.2}))
	kit.color_lines("Roads/Lanes", Color("#7a5a3c"))
	kit.pattern_lines("Roads/Lanes", kit.line_material({"dot": 0.9, "gap": 1.1}))
	kit.color_lines("Bridges", Color("#2e2014"))
	kit.style_rank("Kingdoms", Color("#8a2e1e"), 9.0,
			kit.line_material({"dash": 3.0, "gap": 1.0, "dot": 0.85, "dot_gap": 0.85}), "onto")
	kit.style_rank("Duchies", Color("#7a5236"), 5.5, kit.line_material({"dash": 2.2, "gap": 1.3}), "onto")
	kit.style_rank("Counties", Color("#8f7656"), 4.5, kit.line_material({"dot": 0.85, "gap": 1.15}), "onto")
	for rank: String in ["Kingdoms", "Duchies", "Counties"]:
		var alpha: float = {"Kingdoms": 0.9, "Duchies": 0.7, "Counties": 0.5}[rank]
		kit.set_alpha("Borders/" + rank, alpha)
		kit.set_alpha("BordersOverLakes/" + rank, alpha)


func ready(kit) -> void:
	kit.trim_sea_ends(0.6)
	var labels: Node2D = kit.runtime("MapLabels.gd").new()
	labels.map = kit.map
	labels.serif = true
	labels.ink = Color("#3b2a1a")
	labels.paper = Color("#f1e6c8")
	kit.map.add_child(labels)
	var route: Node2D = kit.runtime("RouteOverlay.gd").new()
	route.party = kit.at("Party")
	route.route = PackedVector2Array([Vector2(6900.0, 7230.0), Vector2(6420.0, 7020.0)])
	route.safe_color = Color("#2d5a87")
	route.danger_color = Color("#a3261c")
	route.party_color = Color("#a3261c")
	route.casing_color = Color("#f4ead0")
	route.tick_color = Color("#3b2a1a")
	kit.map.add_child(route)
