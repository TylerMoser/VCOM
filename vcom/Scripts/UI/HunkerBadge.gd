## A small shield over the corner of a unit's portrait on its card, shown while
## the unit is hunkered down ([member Unit.hunkered]).
class_name HunkerBadge
extends Control

const BADGE_SIZE := Vector2(20, 22)
## The steel blue of cover held hard, apart from the gold of the action pips.
const FILL_COLOR := Color(0.45, 0.7, 1.0)
const RIM_COLOR := Color(0.06, 0.07, 0.1)
## A pale bar down the middle, so it reads as a shield, not a blob.
const STRIPE_COLOR := Color(0.85, 0.93, 1.0)


func _init() -> void:
	custom_minimum_size = BADGE_SIZE
	size = BADGE_SIZE
	mouse_filter = MOUSE_FILTER_IGNORE


func _draw() -> void:
	var outline := _shield(0.0)
	draw_colored_polygon(outline, RIM_COLOR)
	draw_colored_polygon(_shield(2.0), FILL_COLOR)
	var middle := size.x / 2.0
	draw_line(Vector2(middle, 5.0), Vector2(middle, size.y - 6.0), STRIPE_COLOR, 2.0)


## The shield's corners, [param inset] pixels in from the badge's edges: a flat
## top, straight sides, and a point at the bottom.
func _shield(inset: float) -> PackedVector2Array:
	var left := inset
	var right := size.x - inset
	var top := inset
	var shoulder := size.y * 0.5
	return PackedVector2Array([
		Vector2(left, top),
		Vector2(right, top),
		Vector2(right, shoulder),
		Vector2(size.x / 2.0, size.y - inset * 1.4),
		Vector2(left, shoulder),
	])
