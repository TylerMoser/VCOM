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
## On the new map, [code]Scenes/Map.tscn[/code], the terrain is a
## [MapNavigation] instead: the party keeps off the water, crossing it only by
## a bridge, and takes the fastest way, which it works out on a thread of its
## own while the party waits where it is (a fifth of a second at the most).
## Its pace on each leg is the ground's ([constant MapNavigation.ROAD_MILES_PER_DAY]
## and the rest), and the clock counts the time it takes. A right click on
## water, or on land it cannot reach, is ignored, as on the old map.
##
## With no terrain ([member terrain_path] left empty) it goes wherever it is
## sent in a straight line, over the sea as over the land.
##
## With the gamepad, A does what the right click does, at the [MapReticle] in
## the middle of the screen, and L3 (recenter) brings the party back into the
## middle of the view.
##
## It travels in steps of [member step_length]. Every step heals everyone on
## the roster by [member heal_per_step] ([method Campaign.heal]), wherever it
## is taken, so wounds mend on the road. Each step that ends in a
## [Forest] then rolls that forest's chance of a random encounter, and one that
## comes up is announced with [signal encountered]; the [SquadMenu] takes it
## from there, choosing who fights and starting the battle. The world map
## waits out of the tree meanwhile, so once the battle is over the party is
## back where it was set upon, still on its way.
##
## The dot and its markers are drawn at a fixed size on screen, whatever the
## camera's zoom, so the party stays easy to see on a map drawn thousands of
## pixels across.
class_name Party
extends Node2D

## A random encounter came up: a battle on [param map] is to be fought.
signal encountered(map: PackedScene)

## Finds the way over land: the old map's [WorldMapTerrain], or the new map's
## [MapNavigation]. Leave empty to go anywhere, in a straight line.
@export var terrain_path: NodePath = ^"../Terrain"
## Map pixels per second, on a map with no clock. The map is about 9000
## across.
@export var travel_speed := 250.0
## The map's clock, on a map that has one (the new map). With it the party
## goes [member miles_per_day] instead of [member travel_speed], and time
## passes on it while the party moves, and only then.
@export var clock_path: NodePath
## Miles the party covers in a day of the clock's, a mile being
## [constant MapCamera.UNITS_A_MILE] of the map's units. Read only with a
## clock, and only where no [MapNavigation] gives each leg its own pace.
@export_range(0.0, 200.0, 0.5, "or_greater") var miles_per_day := 25.0
## How far the party goes, in map pixels, from one chance of a random
## encounter to the next. The chance itself is each forest's.
@export var step_length := 50.0
## Health every wounded character on the roster gets back each step, never
## past their most.
@export_range(0, 100, 1, "or_greater") var heal_per_step := 1

@export_group("Look")
## Sizes are in screen pixels.
@export var dot_radius := 6.0
@export var dot_color := Color(0.85, 0.1, 0.1)
@export var destination_color := Color(0.85, 0.1, 0.1, 0.8)

var _terrain: WorldMapTerrain
var _navigation: MapNavigation
var _clock: MapClock
## The points still to head for, in order, the destination last. Empty when
## the party is not travelling.
var _route := PackedVector2Array()
## Miles a day on the leg to each point of [member _route], from a
## [MapNavigation]; empty when every leg goes at [method speed].
var _paces := PackedFloat32Array()
## Whether a route is being worked out, which the party waits for where it is.
var _planning := false
## Where the party was sent before the terrain could find routes, to set off
## for once it can; null when there is none.
var _waiting_for: Variant = null
## Map pixels travelled since the last step.
var _stepped := 0.0
## Screen pixels per map pixel as last drawn, to redraw when the zoom changes.
var _drawn_scale := 0.0


func _ready() -> void:
	if not clock_path.is_empty():
		_clock = get_node_or_null(clock_path) as MapClock
		if _clock == null:
			push_error("Party: no MapClock at '%s'; travelling at its travel speed, and no time passes." % clock_path)
	if not terrain_path.is_empty():
		var terrain := get_node_or_null(terrain_path)
		_terrain = terrain as WorldMapTerrain
		_navigation = terrain as MapNavigation
		if _terrain == null and _navigation == null:
			push_error("Party: no WorldMapTerrain or MapNavigation at '%s'; travelling in straight lines." % terrain_path)
		elif _navigation != null and not _navigation.is_ready():
			_navigation = null
	if _terrain == null and _navigation == null:
		return
	if not can_go_to(global_position):
		push_warning("Party: starts off the land at %s, so it can go nowhere." % global_position)
	for destination in get_tree().get_nodes_in_group(Destination.GROUP):
		if not can_go_to(destination.global_position):
			push_warning("Party: destination '%s' is off the land at %s, so it can never be reached." % [
				destination.name, destination.global_position])


func _unhandled_input(event: InputEvent) -> void:
	var clicked := event.is_action_pressed(&"execute_action") and event is InputEventMouseButton
	if clicked or (InputDevice.gamepad and event.is_action_pressed(&"confirm_action")):
		var destination := Destination.find_under_pointer(get_tree())
		_send_to(destination.global_position if destination != null else pointed_at())
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed(&"recenter"):
		var camera := get_viewport().get_camera_2d() as WorldMapCamera
		if camera != null:
			camera.focus_on(global_position)
		get_viewport().set_input_as_handled()


## The spot of the map the player points at: under the mouse, or with the
## gamepad under the reticle.
func pointed_at() -> Vector2:
	return InputDevice.pointer_on_canvas(self)


## Whether [param point] is somewhere the party could be sent: on land, with
## land to go by (off the water, on the new map). It may still be cut off
## from it by the water.
func can_go_to(point: Vector2) -> bool:
	if _navigation != null:
		return _navigation.is_passable(point)
	return _terrain == null or _terrain.is_land(point)


func _process(delta: float) -> void:
	if _waiting_for != null and _terrain.is_ready():
		var destination: Vector2 = _waiting_for
		_waiting_for = null
		_send_to(destination)
	if not _route.is_empty() and not _planning:
		# Spend the whole frame travelling, carrying on past a turn reached
		# part-way through it at the next leg's pace.
		var time_left := delta
		var moved := 0.0
		while time_left > 0.0 and not _route.is_empty():
			var pace := _pace()
			if pace <= 0.0:
				break
			var leg := global_position.distance_to(_route[0])
			var reach := pace * time_left
			if leg > reach:
				global_position = global_position.move_toward(_route[0], reach)
				moved += reach
				time_left = 0.0
				break
			global_position = _route[0]
			moved += leg
			time_left -= leg / pace
			_route.remove_at(0)
			if not _paces.is_empty():
				_paces.remove_at(0)
		queue_redraw()
		# Only the part of the frame spent travelling: the trip's last frame
		# ends early.
		if _clock != null:
			_clock.advance(delta - time_left)
		_take_steps(moved)
	elif not is_equal_approx(_screen_scale(), _drawn_scale):
		queue_redraw()


## How fast the party travels, in map pixels a second: [member miles_per_day]
## by the map's clock where there is one, else [member travel_speed].
func speed() -> float:
	if _clock == null or _clock.seconds_per_day <= 0.0:
		return travel_speed
	return miles_per_day * MapCamera.UNITS_A_MILE / _clock.seconds_per_day


## How fast the party travels on the leg ahead, in map pixels a second: the
## leg's own pace where the route gives one, else [method speed].
func _pace() -> float:
	if _paces.is_empty() or _clock == null or _clock.seconds_per_day <= 0.0:
		return speed()
	return _paces[0] * MapCamera.UNITS_A_MILE / _clock.seconds_per_day


func _draw() -> void:
	_drawn_scale = _screen_scale()
	# Everything below is sized in screen pixels, so divide by the zoom.
	var px := 1.0 / _drawn_scale

	if not _route.is_empty():
		var points := PackedVector2Array([Vector2.ZERO])
		for point in _route:
			points.append(to_local(point))
		_draw_dashes(points, destination_color, 2.0 * px, 8.0 * px)
		var target := points[points.size() - 1]
		var arm := 5.0 * px
		draw_line(target + Vector2(-arm, -arm), target + Vector2(arm, arm), destination_color, 2.0 * px)
		draw_line(target + Vector2(-arm, arm), target + Vector2(arm, -arm), destination_color, 2.0 * px)

	draw_circle(Vector2.ZERO, dot_radius * px, dot_color)


## A dashed line through [param points], its dashes and gaps [param dash]
## long, laid along the whole line rather than started afresh at each turn,
## which on a route of many short legs would leave it all dash.
func _draw_dashes(points: PackedVector2Array, color: Color, width: float, dash: float) -> void:
	var segments := PackedVector2Array()
	var drawing := true
	var left := dash
	for i in points.size() - 1:
		var a := points[i]
		var b := points[i + 1]
		var length := a.distance_to(b)
		var along := 0.0
		while along < length:
			var step := minf(left, length - along)
			if drawing:
				segments.append(a.lerp(b, along / length))
				segments.append(a.lerp(b, (along + step) / length))
			along += step
			left -= step
			if left <= 0.0:
				drawing = not drawing
				left = dash
	if not segments.is_empty():
		draw_multiline(segments, color, width)


## Whether the party has stopped at [param destination]. A trip there ends
## exactly on the destination's position, so this is the party standing on
## that very spot with nowhere left to go.
func is_at(destination: Destination) -> bool:
	return _route.is_empty() and global_position.is_equal_approx(destination.global_position)


## Counts [param distance] travelled towards the next step. At the end of
## each it heals the roster, and in a forest rolls its chance of an encounter.
## A frame long enough to take several steps heals and rolls for each where
## the party stands, which is near enough at any real frame rate.
func _take_steps(distance: float) -> void:
	_stepped += distance
	while step_length > 0.0 and _stepped >= step_length:
		_stepped -= step_length
		Campaign.heal(heal_per_step)
		var forest := Forest.find_at(get_tree(), global_position)
		if forest != null and forest.roll_encounter():
			encountered.emit(forest.encounter_map)
			return


## Sets off for [param destination], if it can be reached over land; if not,
## carries on as before. On the new map the way is worked out on a thread,
## and the party waits for it ([method _on_route]).
func _send_to(destination: Vector2) -> void:
	if _navigation != null:
		if not _navigation.is_passable(destination):
			return
		_planning = true
		_navigation.request_route(global_position, destination, _on_route)
		return
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
	_paces = PackedFloat32Array()
	queue_redraw()


## The new map's way to where the party was last sent: it sets off along it,
## or, when there is none, carries on as before.
func _on_route(route: MapRoute) -> void:
	_planning = false
	if route == null or route.points.is_empty():
		return
	_waiting_for = null
	_route = route.points
	_paces = route.miles_per_day
	queue_redraw()


## Screen pixels per map pixel under the current camera.
func _screen_scale() -> float:
	return (get_viewport().get_canvas_transform() * get_global_transform()).get_scale().x
