## 21 · Colour-blind safe. About one man in twelve sees colour differently,
## most often with weak red or green cones (deuteranomaly and protanomaly), and
## the present map tells its lines apart almost only by hue: magenta, purple,
## red, brown and grey borders, roads and bridges become muddy browns and greys
## of about the same lightness to them (00-current-look-deutan.png shows it).
## Here every kind differs in at least two of lightness, pattern and shape, and
## the hues come from the blue-orange axis that every common deficiency keeps
## (the Okabe-Ito palette): borders a dark ink told apart by their pattern
## (02), roads cased (04) with highways orange, water one blue family (05),
## forests marked by kind (07), the route blue and its forest stretches
## vermilion. Each view is shown as everyone sees it and through a simulation
## of deuteranopia (Machado et al. 2009, full strength).
extends RefCounted

const NAME := "Colour-blind safe"

const PATTERNED := preload("res://_probe/styles/02_patterned_borders.gd")
const CASED := preload("res://_probe/styles/04_cased_roads.gd")
const WATER := preload("res://_probe/styles/05_one_water.gd")
const SYMBOLS := preload("res://_probe/styles/07_forest_symbols.gd")

var _water := WATER.new()


func apply(kit) -> void:
	PATTERNED.new().apply(kit)
	CASED.new().apply(kit)
	_water.apply(kit)
	SYMBOLS.new().apply(kit)
	# Highways in the Okabe-Ito orange; rivers a deeper blue than the lakes.
	var highway: ShaderMaterial = kit.lines_in("Roads/Highways")[0].material
	highway.set_shader_parameter(&"fill", Color("#f0a81c"))
	highway.set_shader_parameter(&"casing", Color("#8a5a00"))
	highway.set_shader_parameter(&"narrow", Color("#d98e00"))
	kit.color_lines("Rivers", Color("#3b8fd4"))
	kit.color_lines("Channels", Color("#3b8fd4"))
	# Forests in bluish greens, which stay apart from the orange.
	for kind: String in ["Conifer", "Broadleaf", "Swamp", "Tropical"]:
		var piece: Polygon2D = kit.forests(kind)[0]
		(piece.material as ShaderMaterial).set_shader_parameter(&"fill_override",
				{"Conifer": Color("#b9dccb"), "Broadleaf": Color("#cfe5cf"), "Swamp": Color("#d3dcc8"), "Tropical": Color("#b3d9c4")}[kind])


func ready(kit) -> void:
	_water.ready(kit)
	var route: Node2D = kit.runtime("RouteOverlay.gd").new()
	route.party = kit.at("Party")
	route.route = PackedVector2Array([Vector2(6900.0, 7230.0), Vector2(6420.0, 7020.0)])
	route.safe_color = Color("#0072b2")
	route.danger_color = Color("#d55e00")
	route.party_color = Color("#0072b2")
	route.show_summary = false
	kit.map.add_child(route)


func panels(_kit) -> Array:
	return [
		["B", "Duchy tier: 180 miles tall", Vector2(7302, 7381), 180.0, ""],
		["B", "Duchy tier: 180 miles tall", Vector2(7302, 7381), 180.0, "deutan"],
		["C", "County tier: 80 miles tall", Vector2(6150, 8500), 80.0, ""],
		["C", "County tier: 80 miles tall", Vector2(6150, 8500), 80.0, "deutan"],
	]
