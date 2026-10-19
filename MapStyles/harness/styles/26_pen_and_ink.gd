## 26 · Pen and ink. Black ink on cream paper and nothing else, as an engraved
## map, matching the settlements' ink drawings exactly: the sea the paper's own
## colour inside an inked coast and its water lines, the lakes a pale wash,
## rivers as tapering ink lines, roads as double lines (highways wider), lanes
## dashed, borders in the classic dash-dot, dashes and dots, forests as small
## inked trees with no fill, faint grey hill shading. The only colour is the
## party's red. Every kind of line is told by its pattern and weight alone,
## which is the strictest test of a map's hierarchy: it reads in greyscale,
## printed, and to every eye.
extends RefCounted

const NAME := "Pen and ink"

const INK := "#1f1c18"
const PAPER := "#f6f0e1"


func apply(kit) -> void:
	kit.set_land(Color(PAPER))
	kit.style_land({"paper": 0.25, "paper_dark": Color("#9a8f78")})
	kit.set_sea(Color("#efe8d6"))
	for lake: Polygon2D in kit.lakes():
		lake.color = Color("#dcdfd8")
	var ink := Color(INK)
	kit.color_lines("Rivers", ink)
	kit.color_lines("Channels", ink)
	kit.scale_widths("Rivers", 0.5)
	kit.scale_widths("Channels", 0.6)
	kit.style_coast({
		"shore": ink, "shore_share": 0.1, "ring": Color(INK, 0.6), "rings": 4, "ring_share": 0.05, "ring_min_px": 2.5,
	}, 2.4)
	kit.add_relief(0.3, 0.0, Color(0.45, 0.45, 0.45))
	var marks := {"Conifer": 1, "Broadleaf": 2, "Swamp": 3, "Tropical": 4}
	for kind: String in marks:
		kit.style_forests(kind, Color(PAPER, 0.0), {
			"glyph": marks[kind], "mark": Color(INK, 0.8), "cell_px": 14.0, "mark_size": 0.62, "density": 0.78,
		})
	for kind: String in ["Highways", "Roads"]:
		kit.scale_widths("Roads/" + kind, 2.2 if kind == "Highways" else 2.0)
		kit.pattern_lines("Roads/" + kind, kit.line_material({
			"fill_from_line": false, "fill": Color(PAPER), "casing": ink,
			"casing_share": 0.32 if kind == "Highways" else 0.38, "casing_min_px": 4.0, "narrow": ink,
		}))
	kit.color_lines("Roads/Lanes", ink)
	kit.pattern_lines("Roads/Lanes", kit.line_material({"dash": 1.6, "gap": 1.1}))
	for bridge: Line2D in kit.lines_in("Bridges"):
		bridge.width *= 2.0
		kit.pattern_line(bridge, kit.line_material({
			"fill_from_line": false, "fill": Color(PAPER), "casing": ink, "casing_share": 0.42, "casing_min_px": 3.0,
			"narrow": ink,
		}))
	kit.style_rank("Kingdoms", ink, 10.0,
			kit.line_material({"dash": 3.0, "gap": 1.0, "dot": 0.85, "dot_gap": 0.85}), "onto")
	kit.style_rank("Duchies", ink, 6.5, kit.line_material({"dash": 2.2, "gap": 1.3}), "onto")
	kit.style_rank("Counties", ink, 5.0, kit.line_material({"dot": 0.85, "gap": 1.15}), "onto")
	for rank: String in ["Kingdoms", "Duchies", "Counties"]:
		var alpha: float = {"Kingdoms": 0.85, "Duchies": 0.65, "Counties": 0.45}[rank]
		kit.set_alpha("Borders/" + rank, alpha)
		kit.set_alpha("BordersOverLakes/" + rank, alpha)


func ready(kit) -> void:
	kit.trim_sea_ends(0.6)
	var labels: Node2D = kit.runtime("MapLabels.gd").new()
	labels.map = kit.map
	labels.serif = true
	labels.ink = Color(INK)
	labels.paper = Color(PAPER)
	kit.map.add_child(labels)
	var route: Node2D = kit.runtime("RouteOverlay.gd").new()
	route.party = kit.at("Party")
	route.route = PackedVector2Array([Vector2(6900.0, 7230.0), Vector2(6420.0, 7020.0)])
	route.safe_color = Color("#c0392b")
	route.danger_color = Color("#5a1810")
	route.party_color = Color("#c0392b")
	route.casing_color = Color(PAPER)
	route.tick_color = Color(INK)
	kit.map.add_child(route)
