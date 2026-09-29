## The player's party on the world map: a red dot that travels where it is
## sent.
##
## It is the only thing on the map that moves, so there is nothing to select
## first: a right click (execute_action, as a move is given in combat) anywhere
## sends it to that point at [member travel_speed], over land by the route
## [WorldMapTerrain] finds: straight when nothing is in the way, around the
## coast when something is. A right click on a [Destination]'s icon sends it to
## the destination itself. A right click on the sea, or on land it cannot
## reach, is ignored. A new right click while it is on the way sends it on to
## the new point instead. The left button is left free for other things, such
## as a left click on the village the party is in opening its [VillageMenu].
##
## The dot and its markers are drawn at a fixed size on screen, whatever the
## camera's zoom, so the party stays easy to see on a map drawn thousands of
## pixels across.
class_name Party
extends Node2D

## Finds the way over land. Leave empty to go anywhere, in a straight line.
@export var terrain_path: NodePath = ^"../Terrain"
## Map pixels per second. The map is about 9000 across.
@export var travel_speed := 250.0

@export_group("Look")
## Sizes are in screen pixels.
@export var dot_radius := 6.0
@export var dot_color := Color(0.85, 0.1, 0.1)
@export var destination_color := Color(0.85, 0.1, 0.1, 0.8)

var _terrain: WorldMapTerrain
## The points still to head for, in order, the destination last. Empty when
## the party is not travelling.
var _route := PackedVector2Array()
## Where the party was sent before the terrain could find routes, to set off
## for once it can; null when there is none.
var _waiting_for: Variant = null
## Screen pixels per map pixel as last drawn, to redraw when the zoom changes.
var _drawn_scale := 0.0


func _ready() -> void:
	if not terrain_path.is_empty():
		_terrain = get_node_or_null(terrain_path) as WorldMapTerrain
		if _terrain == null:
			push_error("Party: no WorldMapTerrain at '%s'; travelling in straight lines." % terrain_path)
	if _terrain != null and not _terrain.is_land(global_position):
		push_warning("Party: starts off the land at %s, so it can go nowhere." % global_position)
	if _terrain != null:
		for destination in get_tree().get_nodes_in_group(Destination.GROUP):
			if not _terrain.is_land(destination.global_position):
				push_warning("Party: destination '%s' is off the land at %s, so it can never be reached." % [
					destination.name, destination.global_position])


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"execute_action") and event is InputEventMouseButton:
		var destination := Destination.find_under_mouse(get_tree())
		_send_to(destination.global_position if destination != null else get_global_mouse_position())
		get_viewport().set_input_as_handled()


func _process(delta: float) -> void:
	if _waiting_for != null and _terrain.is_ready():
		var destination: Vector2 = _waiting_for
		_waiting_for = null
		_send_to(destination)
	if not _route.is_empty():
		# Spend the whole frame's travel, carrying on past a turn reached
		# part-way through it.
		var travel := travel_speed * delta
		while travel > 0.0 and not _route.is_empty():
			var leg := global_position.distance_to(_route[0])
			if leg > travel:
				global_position = global_position.move_toward(_route[0], travel)
				break
			global_position = _route[0]
			travel -= leg
			_route.remove_at(0)
		queue_redraw()
	elif not is_equal_approx(_screen_scale(), _drawn_scale):
		queue_redraw()


func _draw() -> void:
	_drawn_scale = _screen_scale()
	# Everything below is sized in screen pixels, so divide by the zoom.
	var px := 1.0 / _drawn_scale

	if not _route.is_empty():
		var from := Vector2.ZERO
		for point in _route:
			draw_dashed_line(from, to_local(point), destination_color, 2.0 * px, 8.0 * px)
			from = to_local(point)
		var target := from
		var arm := 5.0 * px
		draw_line(target + Vector2(-arm, -arm), target + Vector2(arm, arm), destination_color, 2.0 * px)
		draw_line(target + Vector2(-arm, arm), target + Vector2(arm, -arm), destination_color, 2.0 * px)

	draw_circle(Vector2.ZERO, dot_radius * px, dot_color)


## Whether the party has stopped at [param destination]. A trip there ends
## exactly on the destination's position, so this is the party standing on
## that very spot with nowhere left to go.
func is_at(destination: Destination) -> bool:
	return _route.is_empty() and global_position.is_equal_approx(destination.global_position)


## Sets off for [param destination], if it can be reached over land; if not,
## carries on as before.
func _send_to(destination: Vector2) -> void:
	var route := PackedVector2Array([destination])
	if _terrain != null:
		route = _terrain.find_route(global_position, destination)
		if route.is_empty() and not _terrain.is_ready() and _terrain.is_land(destination):
			# Just after the map opens, only straight ways can be found yet:
			# go once the rest can be.
			_waiting_for = destination
			return
	if route.is_empty():
		return
	_waiting_for = null
	_route = route
	queue_redraw()


## Screen pixels per map pixel under the current camera.
func _screen_scale() -> float:
	return (get_viewport().get_canvas_transform() * get_global_transform()).get_scale().x
