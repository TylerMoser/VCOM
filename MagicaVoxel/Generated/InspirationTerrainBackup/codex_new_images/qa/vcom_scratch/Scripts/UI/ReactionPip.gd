## The unit's reaction: a filled triangle while it is available, a hollow one
## once spent. Same colours as the action circles; the shape alone marks it
## as the reaction. While the reaction is [member readied] - held for
## overwatch - the triangle gets a bright rim.
class_name ReactionPip
extends ActionPip

## How much of the triangle the gold keeps inside the rim.
const READIED_INNER_SCALE := 0.5

@export var readied_color := Color(1.0, 0.97, 0.85)

var readied := false:
	set(value):
		if readied == value:
			return
		readied = value
		queue_redraw()


func _draw() -> void:
	if not available:
		var outline := _triangle(2.0)
		outline.append(outline[0])
		draw_polyline(outline, spent_color, 2.0, true)
		return
	var corners := _triangle(1.0)
	if not readied:
		draw_colored_polygon(corners, available_color)
		return
	draw_colored_polygon(corners, readied_color)
	# Shrunk toward the incentre, which is equally far from every side, so the
	# rim is the same width all the way round.
	var centre := _incentre(corners)
	var inner := PackedVector2Array()
	for corner in corners:
		inner.append(centre + (corner - centre) * READIED_INNER_SCALE)
	draw_colored_polygon(inner, available_color)


## The corners of the triangle, pointing up, [param inset] pixels in from the
## pip's edges.
func _triangle(inset: float) -> PackedVector2Array:
	return PackedVector2Array([
		Vector2(size.x / 2.0, inset),
		Vector2(size.x - inset, size.y - inset),
		Vector2(inset, size.y - inset),
	])


static func _incentre(corners: PackedVector2Array) -> Vector2:
	var a := corners[1].distance_to(corners[2])
	var b := corners[2].distance_to(corners[0])
	var c := corners[0].distance_to(corners[1])
	return (corners[0] * a + corners[1] * b + corners[2] * c) / (a + b + c)
