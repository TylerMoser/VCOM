## Rings round the settlements that have something in them (a Destination's
## locations: a hiring board, a market), in the one colour the map keeps for
## them, with what they hold beside the ring. Sized in screen pixels. A
## runtime node for the map style harness; for real, Destination._draw().
extends Node2D

var map: Node2D
var color := Color("#e8a317")
var label_color := Color("#6b4a00")
var halo := Color(1, 1, 1, 0.9)

var _places: Array = []
var _font: Font


func _ready() -> void:
	z_index = 7
	_font = ThemeDB.fallback_font
	for place in map.get_node("Settlements").find_children("*", "Node2D", true, false):
		var locations: Variant = place.get("locations")
		if locations is Array and not (locations as Array).is_empty():
			_places.append(place)


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	var s := get_viewport().get_canvas_transform().get_scale().x
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE / s)
	for place: Node2D in _places:
		if not place.is_visible_in_tree():
			continue
		var at := place.position * s
		var radius: float = place.get("icon_height") * 0.75 + 4.0
		draw_arc(at, radius + 2.0, 0.0, TAU, 48, Color(1, 1, 1, 0.9), 5.0)
		draw_arc(at, radius + 2.0, 0.0, TAU, 48, color, 3.0)
		var names: Array[String] = []
		for location in place.get("locations"):
			names.append(str(location.get("display_name")))
		var text := ", ".join(names)
		var spot := at + Vector2(radius + 8.0, 5.0)
		draw_string_outline(_font, spot, text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, 13, 4, halo)
		draw_string(_font, spot, text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, 13, label_color)
