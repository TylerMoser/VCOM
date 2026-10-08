## Camera for the new map (Scenes/Map.tscn): [WorldMapCamera]'s panning and
## zooming, with its limits taken from the land the scene holds.
##
##   All the way out - the whole land just fits the window, out to the outer
##                     edge of its coast's line, and nothing can be panned.
##   All the way in  - the view is [member closest_view_miles] tall, 25 miles,
##                     whatever the window's size; how wide follows from the
##                     window's shape.
##   Panning         - the view never leaves what is seen all the way out: its
##                     edges stop at that view's edges. In a window wider than
##                     the land, that lets it slide out over the sea either
##                     side, as far as the sea shows all the way out.
##
## The land's extent is measured off the scene's own nodes as it opens, so the
## far limit and the panning follow the land as it is reshaped by hand, and
## all three are worked out for the window's size whenever they are asked for.
## [member WorldMapCamera.fit_margin] is the share of the window the land fills
## all the way out: 1 for a land that just fits.
## [member WorldMapCamera.map_path] and [member WorldMapCamera.max_zoom] are
## not used: this map is no picture.
class_name MapCamera
extends WorldMapCamera

## A mile in the map's units: a unit is 100 m, and a mile 1,609.344 m.
const UNITS_A_MILE := 16.09344

@export_group("Nodes")
## The land. Every Polygon2D under it, however deep, is part of it.
@export var land_path: NodePath = ^"../Land"
## The coast's lines, which are drawn half outside the land: zoomed all the
## way out, the view reaches their outer edge. May be left empty.
@export var coast_path: NodePath = ^"../Coast"

@export_group("Zoom")
## How tall the view is zoomed all the way in, in miles on the map.
@export_range(1.0, 500.0, 0.1, "or_greater", "suffix:mi") var closest_view_miles := 25.0

# The land's rectangle, out to the outer edge of its coast's line.
var _land := Rect2()


func _ready() -> void:
	map_path = ^""
	_measure()
	super()


## Reads the land's extent off the scene.
func _measure() -> void:
	var land := get_node_or_null(land_path)
	if land == null:
		push_error("MapCamera: no land at '%s'; panning and zooming without limits." % land_path)
		return
	var found := false
	for node in land.find_children("*", "Polygon2D", true, false):
		var outline := node as Polygon2D
		var box := _box_of(outline.polygon)
		if not box.has_area():
			continue
		box.position += outline.offset
		box = outline.global_transform * box
		_land = box if not found else _land.merge(box)
		found = true
	if not found:
		push_error("MapCamera: no Polygon2D under '%s'; panning and zooming without limits." % land_path)
		return
	# A line lies half to each side of its points: the coast's reaches half its width off the land.
	var coast := get_node_or_null(coast_path)
	if coast != null:
		var reach := 0.0
		for node in coast.find_children("*", "Line2D", true, false):
			reach = maxf(reach, (node as Line2D).width * 0.5)
		_land = _land.grow(reach)


## The smallest upright rectangle that holds some points.
func _box_of(points: PackedVector2Array) -> Rect2:
	if points.is_empty():
		return Rect2()
	var low := points[0]
	var high := points[0]
	for point in points:
		low = low.min(point)
		high = high.max(point)
	return Rect2(low, high - low)


func _has_map() -> bool:
	return _land.has_area()


func _map_rect() -> Rect2:
	return _land


## The zoom at which the window is [member closest_view_miles] tall. Never
## further out than all the way out: a land smaller than that is seen whole.
func _max_zoom() -> float:
	var screen := get_viewport().get_visible_rect().size
	return maxf(screen.y / (closest_view_miles * UNITS_A_MILE), _min_zoom())


## The middle of the view may be as far from the land's middle as leaves the
## view's edges inside the view all the way out: nowhere at all at that zoom,
## and further the closer the zoom.
func _clamp_to_map(point: Vector2, at_zoom: float) -> Vector2:
	if not _has_map():
		return point
	var screen := get_viewport().get_visible_rect().size
	var room := ((screen / _min_zoom() - screen / at_zoom) * 0.5).max(Vector2.ZERO)
	var middle := _land.get_center()
	return point.clamp(middle - room, middle + room)
