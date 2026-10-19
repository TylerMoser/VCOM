## Marks for places heard of but not seen, over the fog of war: a faint ring with a question mark,
## the same size on the screen at every zoom, at each of [member points] (map units). For 20's
## variants (MapStyles/20-fog-of-war/). For real, a Destination would draw this itself while unseen.
extends Node2D

## Where the marks go, in the map's units.
var points: Array = []
## The ring's radius in screen pixels, and its colour.
var radius := 7.0
var color := Color(0.34, 0.28, 0.2, 0.75)
var _font: Font


func _ready() -> void:
	_font = ThemeDB.fallback_font


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	var scale := (get_viewport().get_canvas_transform() * get_global_transform()).get_scale().x
	if scale <= 0.0:
		return
	var r := radius / scale
	var size := int(round(radius * 1.55))
	for point: Vector2 in points:
		draw_circle(point, r, Color(1, 1, 1, 0.55))
		draw_arc(point, r, 0.0, TAU, 24, color, 1.4 / scale, true)
		# The glyph is drawn at the screen's size, then scaled back to the map's.
		draw_set_transform(point, 0.0, Vector2.ONE / scale)
		draw_string(_font, Vector2(-size * 0.28, size * 0.36), "?", HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
