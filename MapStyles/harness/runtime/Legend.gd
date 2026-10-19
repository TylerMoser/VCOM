## A map key in the bottom right corner, and a line picked out as if the mouse
## were on it, with a tooltip saying what it is. The key's samples are read off
## the map's own nodes (their colours and widths at this zoom), so it is true
## to whatever style the map has. A runtime node for the map style harness:
## for real, the key is a panel toggled by a key and the pick follows the
## pointer (a grid of the lines by square, as MapDetail keeps).
extends CanvasLayer

## The map, to read samples and lines from.
var map: Node2D
## Rows of the key: [title, kind, node path to sample or a Color, more]. Kinds:
## "area", "line", "icon", "party".
var rows: Array = []
var title := "Map key  (K)"
## The point of the screen the pretend pointer is at, as a share of the screen;
## none when x is under 0.
var pointer := Vector2(-1, -1)
## The groups a line may be picked from.
var pickable: Array[String] = ["Rivers", "Roads/Highways", "Roads/Roads", "Roads/Lanes",
		"Borders/Kingdoms", "Borders/Duchies", "Borders/Counties", "Channels"]

var _panel: Control
var _glow: Line2D
var _tip := ""


func _ready() -> void:
	layer = 6
	_panel = Control.new()
	_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.draw.connect(_draw_panel)
	add_child(_panel)


## Picks the line nearest the pretend pointer, outlines it in a glow, and
## writes what it is. Called once the view is where it will be captured.
func pick() -> void:
	if _glow != null:
		_glow.queue_free()
		_glow = null
	_tip = ""
	if pointer.x < 0.0:
		_panel.queue_redraw()
		return
	var viewport := map.get_viewport()
	var screen := viewport.get_visible_rect().size
	var view := viewport.get_canvas_transform()
	var at := view.affine_inverse() * (screen * pointer)
	var best: Line2D = null
	var best_distance := INF
	for group in pickable:
		var node := map.get_node_or_null(group)
		if node == null or not (node as CanvasItem).is_visible_in_tree() or (node as CanvasItem).modulate.a <= 0.01:
			continue
		for line: Line2D in node.find_children("*", "Line2D", true, false):
			if line.modulate.a <= 0.01 or str(line.name).contains("Casing"):
				continue
			var points := line.points
			for i in points.size() - 1:
				var d := Geometry2D.get_closest_point_to_segment(at, points[i], points[i + 1]).distance_to(at)
				if d < best_distance:
					best_distance = d
					best = line
	if best == null:
		return
	_glow = Line2D.new()
	_glow.points = best.points
	_glow.width = best.width * 2.4 + 12.0 / view.get_scale().x
	_glow.default_color = Color(1.0, 0.85, 0.1, 0.5)
	_glow.joint_mode = Line2D.LINE_JOINT_ROUND
	_glow.begin_cap_mode = Line2D.LINE_CAP_ROUND
	_glow.end_cap_mode = Line2D.LINE_CAP_ROUND
	_glow.z_index = 9
	map.add_child(_glow)
	_tip = describe(best)
	_panel.queue_redraw()


## What a line is, in words, from its name and group.
static func describe(line: Line2D) -> String:
	var title := str(line.name)
	var group := str(line.get_parent().name)
	var numbers: Array[String] = []
	var current := ""
	for c in title:
		if c.is_valid_int():
			current += c
		elif not current.is_empty():
			numbers.append(str(int(current)))
			current = ""
	if not current.is_empty():
		numbers.append(str(int(current)))
	if title.begins_with("River"):
		return "River %s" % numbers[0]
	if title.contains("Channel"):
		return "Channel to a Swamp village"
	if title.begins_with("Kingdoms"):
		return "Kingdom border  ·  Kingdom %s | Kingdom %s" % [numbers[0], numbers[1]]
	if title.begins_with("Duchies"):
		return "Duchy border  ·  Duchy %s | Duchy %s" % [numbers[0], numbers[1]]
	if title.begins_with("Counties"):
		return "County border  ·  County %s | County %s" % [numbers[0], numbers[1]]
	if group == "Lanes":
		return "Lane to a village in County %s" % numbers[0]
	# "Road040To038", "RoadFork221To041": from a settlement (by its county) or
	# a fork to the next.
	var ends := title.trim_prefix("Road").split("To")
	var named: Array[String] = []
	for end in ends:
		var digits := end.trim_prefix("Fork")
		if digits.is_valid_int():
			named.append(("fork %d" if end.begins_with("Fork") else "County %d") % int(digits))
	var kind := "Highway" if group == "Highways" else "Road"
	if named.size() == 2:
		return "%s  ·  %s to %s" % [kind, named[0], named[1]]
	return kind


func _draw_panel() -> void:
	var font: Font = ThemeDB.fallback_font
	var screen := _panel.size
	var view := map.get_viewport().get_canvas_transform()
	var s := view.get_scale().x
	var size := 13
	var row_h := 21.0
	var width := 236.0
	var height := 34.0 + row_h * rows.size() + 6.0
	var box := Rect2(screen - Vector2(width + 14.0, height + 14.0), Vector2(width, height))
	var style := StyleBoxFlat.new()
	style.bg_color = Color(1, 1, 1, 0.93)
	style.border_color = Color(0, 0, 0, 0.18)
	style.set_border_width_all(1)
	style.set_corner_radius_all(6)
	style.shadow_color = Color(0, 0, 0, 0.12)
	style.shadow_size = 6
	_panel.draw_style_box(style, box)
	_panel.draw_string(font, box.position + Vector2(12, 22), title, HORIZONTAL_ALIGNMENT_LEFT, -1.0, 14,
			Color(0.13, 0.13, 0.14))
	for i in rows.size():
		var row: Array = rows[i]
		var top := box.position + Vector2(12.0, 34.0 + row_h * i)
		var sample := Rect2(top + Vector2(0, 3), Vector2(44, row_h - 6))
		_draw_sample(row, sample, s)
		_panel.draw_string(font, top + Vector2(56, 15), row[0], HORIZONTAL_ALIGNMENT_LEFT, -1.0, size,
				Color(0.2, 0.2, 0.22))
	if not _tip.is_empty():
		var at := screen * pointer
		_draw_pointer(at)
		var extent := font.get_string_size(_tip, HORIZONTAL_ALIGNMENT_LEFT, -1.0, 13)
		var tip := Rect2(at + Vector2(18, 14), extent + Vector2(16, 10))
		var tip_style := StyleBoxFlat.new()
		tip_style.bg_color = Color(0.1, 0.11, 0.15, 0.9)
		tip_style.set_corner_radius_all(4)
		_panel.draw_style_box(tip_style, tip)
		_panel.draw_string(font, tip.position + Vector2(8, 5 + font.get_ascent(13)), _tip, HORIZONTAL_ALIGNMENT_LEFT,
				-1.0, 13, Color(0.95, 0.95, 0.97))


func _draw_sample(row: Array, r: Rect2, s: float) -> void:
	var kind: String = row[1]
	var source: Variant = row[2]
	var middle := Vector2(r.position.x, r.get_center().y)
	match kind:
		"area":
			var color: Color = source if source is Color else (map.get_node(source) as Polygon2D).color
			_panel.draw_rect(r, Color.WHITE)
			_panel.draw_rect(r, color)
			_panel.draw_rect(r, Color(0, 0, 0, 0.15), false, 1.0)
		"line":
			var line := map.get_node(source) as Line2D
			var w := clampf(line.width * s, 1.0, 9.0)
			if row.size() > 3:
				w = row[3]
			_panel.draw_line(middle, middle + Vector2(r.size.x, 0), line.default_color * Color(1, 1, 1, line.modulate.a), w)
		"icon":
			var place: Node = map.get_node(source)
			var icon: Texture2D = place.get("icon")
			var h: float = minf(place.get("icon_height"), r.size.y + 4.0)
			var w := h * icon.get_width() / icon.get_height()
			_panel.draw_texture_rect(icon, Rect2(r.get_center() - Vector2(w, h) * 0.5, Vector2(w, h)), false)
		"party":
			_panel.draw_circle(r.get_center(), 6.0, Color(0.85, 0.1, 0.1))


func _draw_pointer(at: Vector2) -> void:
	var arrow := PackedVector2Array([at, at + Vector2(0, 17), at + Vector2(4.5, 13), at + Vector2(8, 20),
			at + Vector2(10.5, 19), at + Vector2(7, 12), at + Vector2(12.5, 12)])
	_panel.draw_colored_polygon(arrow, Color.WHITE)
	var closed := arrow.duplicate()
	closed.append(at)
	_panel.draw_polyline(closed, Color.BLACK, 1.2, true)
