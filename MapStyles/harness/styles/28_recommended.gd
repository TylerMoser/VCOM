## 28 · Recommended blend. The proposals that each fix one thing, put
## together with nothing that fights: patterned borders (02) at quiet weights
## (01), drawn on the water where they follow it; cased roads (04); one water
## (05) with a fine shoreline and two faint rings (06); forest symbols (07);
## a warm off-white ground with a light biome tint (12) and soft relief (13);
## symbols far out and pictures close in (08); the route planner (09); the
## county borders and lanes a tier later (19); and the kingdoms named (15),
## the one name the map already has. Settlement names, the map key (16) and
## the map modes (17) are the next steps once there are names to show.
extends RefCounted

const NAME := "Recommended blend"

const CASED := preload("res://_probe/styles/04_cased_roads.gd")
const SYMBOLS := preload("res://_probe/styles/07_forest_symbols.gd")
const RANK_SYMBOLS := preload("res://_probe/styles/08_rank_symbols.gd")
const BIOME := preload("res://_probe/styles/12_biome_ground.gd")

const GROUND := "#faf8f2"
const WATER := "#a8d0ee"
const INK := Color(0.27, 0.22, 0.33)

var _symbols := RANK_SYMBOLS.new()


func apply(kit) -> void:
	kit.at("Detail").set_script(kit.runtime("ProgressiveDetail.gd"))
	# Ground: off-white, a little under half way to each biome's colour.
	for county: Polygon2D in kit.counties():
		county.color = Color(GROUND).lerp(Color(BIOME.GROUND[kit.kingdom_of(county)]), 0.45)
	for island: Polygon2D in kit.lake_islands():
		island.color = Color(GROUND)
	kit.add_relief(0.42, 0.1)
	# Water.
	kit.set_sea(Color(WATER))
	for lake: Polygon2D in kit.lakes():
		lake.color = Color(WATER)
	kit.color_lines("Rivers", Color("#6faee3"))
	kit.color_lines("Channels", Color("#6faee3"))
	kit.style_coast({
		"shore": Color("#5f8fbb"), "shore_share": 0.2, "ring": Color("#6f9cc4", 0.4), "rings": 2,
		"ring_share": 0.07, "ring_min_px": 3.0,
	}, 1.4)
	# Forests, roads.
	SYMBOLS.new().apply(kit)
	CASED.new().apply(kit)
	# Borders: patterned, quiet.
	kit.style_rank("Kingdoms", INK, 11.0,
			kit.line_material({"dash": 3.2, "gap": 1.0, "dot": 0.85, "dot_gap": 0.9}), "onto")
	kit.style_rank("Duchies", INK, 7.0, kit.line_material({"dash": 2.4, "gap": 1.3, "round_dashes": true}), "onto")
	kit.style_rank("Counties", INK, 5.5, kit.line_material({"dot": 0.85, "gap": 1.15}), "onto")
	for rank: String in ["Kingdoms", "Duchies", "Counties"]:
		var alpha: float = {"Kingdoms": 0.72, "Duchies": 0.55, "Counties": 0.38}[rank]
		kit.set_alpha("Borders/" + rank, alpha)
		kit.set_alpha("BordersOverLakes/" + rank, alpha)


func ready(kit) -> void:
	kit.trim_sea_ends(0.5)
	_symbols.ready(kit)
	var labels: Node2D = kit.runtime("MapLabels.gd").new()
	labels.map = kit.map
	labels.placeholder_note = false
	for kind: String in ["duchy", "capital", "city", "town", "village", "hamlet", "lake"]:
		labels.kinds[kind][7] = -1.0
	kit.map.add_child(labels)
	var route: Node2D = kit.runtime("RouteOverlay.gd").new()
	route.party = kit.at("Party")
	route.route = PackedVector2Array([Vector2(6900.0, 7230.0), Vector2(6420.0, 7020.0)])
	route.reach_days = 2.0
	kit.map.add_child(route)


func before_panel(kit, index: int, view: Array) -> void:
	_symbols.before_panel(kit, index, view)
