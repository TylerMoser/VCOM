## 17 · Map modes. One map, four ways of looking at it, switched from a bar at
## the top (or keys 1 to 4), as strategy games do (Crusader Kings' map modes,
## Google's layers): each mode shows what one question needs and quiets the
## rest.
##   Travel    - roads cased and loud, settlements, the route; no borders,
##               forests faint.
##   Political - kingdoms as pastel areas with their borders and names; no
##               forests, roads faint.
##   Terrain   - the biome's ground, shaded relief, forests strong, water; no
##               borders, roads faint.
##   Danger    - where battles are met: the forests in a red hatch, all else
##               grey, the route red where it runs through them.
## All four panels are the same view (180 miles tall, round the party).
##
## Switching is free: the land draws its colour from a palette its polygons
## index (land.gdshader's palette mode), the forests and roads take theirs from
## shared materials, and layers come and go by their group's alpha. Nothing is
## rebuilt or cut into triangles again.
extends RefCounted

const NAME := "Map modes"
const MODES := ["Travel", "Political", "Terrain", "Danger"]

const PASTEL := ["#ffffff", "#d6e0f3", "#f3d6de", "#ebe4c9", "#f6dfc6", "#e2d8f3", "#d0ebe4", "#e4eac9", "#f3d9d0", "#d6ebcc"]
const BIOME := ["#ffffff", "#e9ecef", "#e3dcd5", "#e5e8dc", "#f4e4c4", "#eef0cf", "#dcebd8", "#e2e6cf", "#e6efd6", "#d9ecce"]

var _land: ShaderMaterial
var _forests := {}
var _roads := {}
var _labels: Node2D
var _route: Node2D
var _bar: CanvasLayer
var _mode := 0


func apply(kit) -> void:
	for county: Polygon2D in kit.counties():
		county.color = Color(kit.kingdom_of(county) / 255.0, kit.duchy_of(county) / 255.0, 0.0, 1.0)
	_land = kit.style_land({"palette_mode": true})
	for island: Polygon2D in kit.lake_islands():
		island.color = Color(5 / 255.0, 0.0, 0.0, 1.0)
	kit.add_relief(0.55, 0.12)
	for kind: String in ["Conifer", "Broadleaf", "Swamp", "Tropical"]:
		var own: Color = kit.forests(kind)[0].color
		_forests[kind] = kit.style_forests(kind, own, {"glyph": 0})
	for kind: String in ["Highways", "Roads", "Lanes"]:
		_roads[kind] = kit.line_material({})
		kit.pattern_lines("Roads/" + kind, _roads[kind])
		kit.scale_widths("Roads/" + kind, 1.6)


func ready(kit) -> void:
	_labels = kit.runtime("MapLabels.gd").new()
	_labels.map = kit.map
	for kind: String in ["capital", "city", "town", "village", "hamlet", "lake"]:
		_labels.kinds[kind][7] = -1.0
	kit.map.add_child(_labels)
	_route = kit.runtime("RouteOverlay.gd").new()
	_route.party = kit.at("Party")
	_route.route = PackedVector2Array([Vector2(6900.0, 7230.0), Vector2(6420.0, 7020.0)])
	kit.map.add_child(_route)
	_bar = CanvasLayer.new()
	_bar.layer = 7
	var tabs := Control.new()
	tabs.set_anchors_preset(Control.PRESET_FULL_RECT)
	tabs.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tabs.draw.connect(_draw_bar.bind(tabs))
	_bar.add_child(tabs)
	kit.probe.add_child(_bar)


func panels(_kit) -> Array:
	var centre := Vector2(7302, 7381)
	return [
		["1", "Travel mode", centre, 180.0],
		["2", "Political mode", centre, 180.0],
		["3", "Terrain mode", centre, 180.0],
		["4", "Danger mode", centre, 180.0],
	]


func before_panel(kit, index: int, _view: Array) -> void:
	_mode = index
	var mode: String = MODES[index]
	var palette := []
	for i in 10:
		var code: String = {"Travel": "#ffffff", "Danger": "#f0f0ee"}.get(mode, "")
		if mode == "Political":
			code = PASTEL[i]
		elif mode == "Terrain":
			code = BIOME[i]
		palette.append(Color.html(code))
	_land.set_shader_parameter(&"palette", palette)
	_land.set_shader_parameter(&"duchy_shade", 0.05 if mode == "Political" else 0.0)
	for name: String in ["ReliefShade", "ReliefLight"]:
		(kit.at(name) as CanvasItem).visible = mode == "Terrain"

	var alphas := {
		"Travel": {"Borders": 0.0, "BordersOverLakes": 0.0, "Forests": 0.45, "Roads": 1.0, "Bridges": 1.0,
				"Rivers": 1.0, "Lakes": 1.0, "Channels": 1.0, "Settlements": 1.0},
		"Political": {"Borders": 1.0, "BordersOverLakes": 1.0, "Forests": 0.0, "Roads": 0.25, "Bridges": 0.25,
				"Rivers": 0.6, "Lakes": 1.0, "Channels": 0.5, "Settlements": 1.0},
		"Terrain": {"Borders": 0.0, "BordersOverLakes": 0.0, "Forests": 1.0, "Roads": 0.3, "Bridges": 0.3,
				"Rivers": 1.0, "Lakes": 1.0, "Channels": 1.0, "Settlements": 0.6},
		"Danger": {"Borders": 0.0, "BordersOverLakes": 0.0, "Forests": 1.0, "Roads": 0.45, "Bridges": 0.45,
				"Rivers": 0.45, "Lakes": 1.0, "Channels": 0.45, "Settlements": 1.0},
	}
	for path: String in alphas[mode]:
		kit.set_alpha(path, alphas[mode][path])

	for kind: String in _forests:
		var material: ShaderMaterial = _forests[kind]
		match mode:
			"Danger":
				material.set_shader_parameter(&"fill_override", Color("#e2583e"))
				material.set_shader_parameter(&"fill_alpha", 0.3)
				material.set_shader_parameter(&"glyph", 6)
				material.set_shader_parameter(&"mark", Color("#a8321c", 0.55))
				material.set_shader_parameter(&"cell_px", 7.0)
				material.set_shader_parameter(&"mark_size", 0.5)
			"Terrain":
				material.set_shader_parameter(&"fill_override", Color(0, 0, 0, 0))
				material.set_shader_parameter(&"fill_alpha", 0.8)
				material.set_shader_parameter(&"glyph", 0)
			_:
				material.set_shader_parameter(&"fill_override", Color(0, 0, 0, 0))
				material.set_shader_parameter(&"fill_alpha", 0.5)
				material.set_shader_parameter(&"glyph", 0)

	var cased := {"Highways": ["#ffc451", "#b5761a"], "Roads": ["#fffaf0", "#9c8f7d"], "Lanes": ["#ffffff", "#b5aa9a"]}
	for kind: String in _roads:
		var material: ShaderMaterial = _roads[kind]
		match mode:
			"Travel":
				material.set_shader_parameter(&"fill_from_line", false)
				material.set_shader_parameter(&"fill", Color.html(cased[kind][0]))
				material.set_shader_parameter(&"casing", Color.html(cased[kind][1]))
				material.set_shader_parameter(&"casing_share", 0.3)
				material.set_shader_parameter(&"casing_min_px", 3.5)
				material.set_shader_parameter(&"narrow", Color.html(cased[kind][1]))
			"Danger":
				material.set_shader_parameter(&"fill_from_line", false)
				material.set_shader_parameter(&"fill", Color("#8e8e8e"))
				material.set_shader_parameter(&"casing_share", 0.0)
			_:
				material.set_shader_parameter(&"fill_from_line", true)
				material.set_shader_parameter(&"casing_share", 0.0)

	_labels.visible = mode == "Political"
	_route.visible = mode == "Travel" or mode == "Danger"
	_route.safe_color = Color("#1a73e8") if mode == "Travel" else Color("#5f6368")
	_route.queue_redraw()
	(_bar.get_child(0) as Control).queue_redraw()


func _draw_bar(tabs: Control) -> void:
	var font: Font = ThemeDB.fallback_font
	var size := 15
	var widths := []
	var total := 0.0
	for mode: String in MODES:
		var w := font.get_string_size(mode, HORIZONTAL_ALIGNMENT_LEFT, -1.0, size).x + 44.0
		widths.append(w)
		total += w
	var x := (tabs.size.x - total) * 0.5
	var y := 14.0
	var back := StyleBoxFlat.new()
	back.bg_color = Color(0.08, 0.09, 0.12, 0.85)
	back.set_corner_radius_all(8)
	tabs.draw_style_box(back, Rect2(x - 6.0, y - 6.0, total + 12.0, 40.0))
	for i in MODES.size():
		var box := Rect2(x, y, widths[i], 28.0)
		if i == _mode:
			var on := StyleBoxFlat.new()
			on.bg_color = Color(0.95, 0.96, 0.98)
			on.set_corner_radius_all(6)
			tabs.draw_style_box(on, box)
		var ink := Color(0.1, 0.1, 0.12) if i == _mode else Color(0.88, 0.89, 0.92)
		tabs.draw_string(font, box.position + Vector2(10, 20), str(i + 1), HORIZONTAL_ALIGNMENT_LEFT, -1.0, 12,
				Color(ink, 0.6))
		tabs.draw_string(font, box.position + Vector2(26, 20), MODES[i], HORIZONTAL_ALIGNMENT_LEFT, -1.0, size, ink)
		x += widths[i]
