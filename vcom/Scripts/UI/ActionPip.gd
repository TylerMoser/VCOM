## One action point: a filled circle while available, a hollow ring once spent.
class_name ActionPip
extends Control

@export var available_color := Color(1.0, 0.78, 0.2)
@export var spent_color := Color(0.35, 0.35, 0.4)

var available := true:
	set(value):
		if available == value:
			return
		available = value
		queue_redraw()


func _init() -> void:
	custom_minimum_size = Vector2(16, 16)
	mouse_filter = MOUSE_FILTER_IGNORE


func _draw() -> void:
	var center := size / 2.0
	var radius := minf(size.x, size.y) / 2.0 - 1.0
	if available:
		draw_circle(center, radius, available_color, true, -1.0, true)
	else:
		draw_circle(center, radius - 1.0, spent_color, false, 2.0, true)
