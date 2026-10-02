## Tactical camera rig for the combat map.
##
## This node is the pivot: it sits on the ground plane at the point the camera
## is looking at. The Camera3D child hangs off the rig's local +Z, so rotating
## the rig orbits the camera around that point, and the child's local Z is the
## zoom distance.
##
##   Pan    - WASD, push the mouse against a screen edge, or drag
##            with the middle mouse button, which takes hold of the ground
##            under the cursor and slides it, as it does the world map.
##   Rotate - hold Q / E.
##   Zoom   - mouse wheel. The camera slides in and out along its line of
##            sight, looking down at [member view_pitch] at every zoom.
##
## Rotation is free: Q / E sweep continuously and settle on any angle. The
## pitch is not the player's to change: tipped up toward the horizon, the view
## would reach past the scenery around the map to its edge.
##
## Something that needs a set of units in view, like a reaction window, can
## [method frame] them. That sets its own distance and angle until
## [method release_frame] hands them back to the zoom; the player can still
## pan, turn and zoom in the meantime.
class_name CameraRig
extends Node3D

@export_group("Nodes")
@export var camera_path: NodePath = ^"Camera3D"
## GridMap the pan bounds are derived from. Leave empty to pan without limits.
@export var grid_map_path: NodePath = ^"../GridMap"

@export_group("Pan")
## Units per second at full zoom-out; scaled down as the camera moves in.
@export var pan_speed := 24.0
@export var pan_smoothing := 12.0
@export var edge_pan_enabled := true
## Distance in pixels from a screen edge that starts an edge pan.
@export var edge_pan_margin := 16
## How far past the edge of the map the pivot may travel, in units.
@export var pan_margin := 1.0
## What a drag can take hold of: the terrain's physics layer. A drag begun
## over anything else, or over nothing, slides the ground at the pivot's
## height.
@export_flags_3d_physics var drag_layers := 1

@export_group("Rotate")
## Degrees per second while Q / E are held.
@export var key_rotate_speed := 110.0
@export var rotate_smoothing := 14.0

@export_group("Zoom")
@export var zoom_smoothing := 10.0
## Fraction of the full zoom range covered by one wheel notch.
@export var zoom_step := 1.0 / 12.0
@export var near_distance := 6.0
@export var far_distance := 22.0
## Degrees below horizontal the camera looks down, at every zoom. Keep it
## well above half the camera's vertical FOV (37.5 at the default 75), or the
## top of the screen reaches the horizon.
@export var view_pitch := 55.0

@export_group("Framing")
## Nearest and furthest the camera sits when framing. The near limit keeps a
## framed view an overview even when everything in it stands close together.
## The far limit keeps it from seeing further than the camera zoomed all the
## way out, which is what the scenery around a map is deep enough to hide.
@export var min_frame_distance := 16.0
@export var max_frame_distance := 28.0
## How far out from the centre of the screen framed points may sit, as a
## share of the way to the edge: across, above, and below. Below is tighter
## because the squad panel and the action bar run along the bottom.
@export var frame_margin_x := 0.8
@export var frame_margin_top := 0.8
@export var frame_margin_bottom := 0.55

var _camera: Camera3D

# Targets the player drives directly.
var _pivot := Vector3.ZERO
var _yaw := 0.0
var _zoom := 0.0

# Smoothed values actually written to the transforms.
var _current_pivot := Vector3.ZERO
var _current_yaw := 0.0
var _current_distance := 0.0
var _current_pitch := 0.0

# Set while [method frame] holds the view, in place of the zoom's.
var _framing := false
var _frame_pitch := 0.0
var _frame_distance := 0.0
## Where the camera was looking before [method frame], to go back to.
var _unframed_pivot := Vector3.ZERO

# Set while the middle mouse button drags the view: where the cursor was when
# the drag last moved it, and how high the ground it took hold of is.
var _dragging := false
var _drag_mouse := Vector2.ZERO
var _drag_height := 0.0

var _mouse_seen := false
var _pan_bounds := Rect2()


func _ready() -> void:
	_camera = get_node_or_null(camera_path) as Camera3D
	if _camera == null:
		push_error("CameraRig: no Camera3D at '%s'." % camera_path)
		set_process(false)
		return

	_pan_bounds = _compute_pan_bounds()

	# Adopt the spot, heading and zoom the scene was authored with, so pressing
	# Run does not swing the camera somewhere else on the first frame. The
	# pitch is view_pitch however the rig is tilted in the scene.
	_pivot = position
	_yaw = rotation_degrees.y
	_zoom = clampf(inverse_lerp(near_distance, far_distance, _camera.position.z), 0.0, 1.0)

	_current_pivot = _pivot
	_current_yaw = _yaw
	_current_distance = _zoom_distance()
	_current_pitch = view_pitch


func _notification(what: int) -> void:
	# The button let go behind the pause menu never reaches the rig.
	if what == NOTIFICATION_PAUSED:
		_dragging = false


## A drag in progress follows the mouse from here, ahead of the HUD, which
## would keep the motion over its panels to itself and stall the drag there.
func _input(event: InputEvent) -> void:
	if not _dragging:
		return
	if event.is_action_released(&"camera_free_look"):
		_dragging = false
	elif event is InputEventMouseMotion:
		_drag_to((event as InputEventMouseMotion).position)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"camera_zoom_in"):
		_step_zoom(-1.0)
	elif event.is_action_pressed(&"camera_zoom_out"):
		_step_zoom(1.0)
	elif event.is_action_pressed(&"camera_free_look") and event is InputEventMouseButton:
		# Only a press nothing on the HUD took starts a drag. The action is named
		# for when this button turned the camera.
		_start_drag((event as InputEventMouseButton).position)
	elif event is InputEventMouseMotion:
		_mouse_seen = true


func _process(delta: float) -> void:
	_update_rotation(delta)
	_update_pan(delta)

	var distance := _frame_distance if _framing else _zoom_distance()
	var pitch := _frame_pitch if _framing else view_pitch
	_current_distance = lerpf(_current_distance, distance, _weight(delta, zoom_smoothing))
	_current_pitch = lerpf(_current_pitch, pitch, _weight(delta, zoom_smoothing))

	position = _current_pivot
	rotation_degrees = Vector3(-_current_pitch, _current_yaw, 0.0)
	_camera.position = Vector3(0.0, 0.0, _current_distance)


## Centres the camera on a world position, keeping the current angle and zoom.
func focus_on(world_position: Vector3) -> void:
	_pivot = _clamp_to_bounds(Vector3(world_position.x, _pivot.y, world_position.z))


## Looks down on [param points] from [param pitch] degrees below horizontal,
## keeping the current heading: pivots over the middle of them and pulls back
## until every one sits inside the framing margins. Framing again while
## framed moves the view on; it holds until [method release_frame].
func frame(points: Array[Vector3], pitch: float) -> void:
	if points.is_empty() or _camera == null:
		return
	if not _framing:
		_unframed_pivot = _pivot
		_framing = true
	var low := points[0]
	var high := points[0]
	for point in points:
		low = low.min(point)
		high = high.max(point)
	var middle := (low + high) * 0.5
	_pivot = _clamp_to_bounds(Vector3(middle.x, _pivot.y, middle.z))
	_frame_pitch = pitch
	_frame_distance = clampf(
		_distance_to_fit(points, _pivot, pitch), min_frame_distance, max_frame_distance
	)


## Gives the height and angle back to the zoom, and looks where the camera
## was looking before [method frame] took it.
func release_frame() -> void:
	if not _framing:
		return
	_framing = false
	_pivot = _unframed_pivot


## Whether [method frame] is holding the view.
func is_framing() -> bool:
	return _framing


## How far back from [param pivot] the camera has to sit, on the current
## heading and looking down at [param pitch], to have all of [param points]
## inside the framing margins.
func _distance_to_fit(points: Array[Vector3], pivot: Vector3, pitch: float) -> float:
	var view := Basis.from_euler(Vector3(deg_to_rad(-pitch), deg_to_rad(_yaw), 0.0)).inverse()
	var screen := get_viewport().get_visible_rect().size
	var half_height := tan(deg_to_rad(_camera.fov * 0.5))
	var half_width := half_height * screen.x / screen.y
	var distance := 0.0
	for point in points:
		# The point as the rig sees it. The camera sits at z = distance looking
		# down -z, so the point is (distance - z) in front of it, and must be no
		# further off-centre than the margin allows at that depth.
		var local := view * (point - pivot)
		var margin_y := frame_margin_top if local.y > 0.0 else frame_margin_bottom
		distance = maxf(distance, local.z + absf(local.x) / (half_width * frame_margin_x))
		distance = maxf(distance, local.z + absf(local.y) / (half_height * margin_y))
	return distance


## One wheel notch in [param direction], out if positive. While framed it
## moves the camera by the same distance a notch of zoom would.
func _step_zoom(direction: float) -> void:
	if _framing:
		var step := zoom_step * (far_distance - near_distance)
		_frame_distance = clampf(
			_frame_distance + direction * step, near_distance, max_frame_distance
		)
	else:
		_zoom = clampf(_zoom + direction * zoom_step, 0.0, 1.0)


func _update_rotation(delta: float) -> void:
	var turn := Input.get_axis(&"camera_rotate_left", &"camera_rotate_right")
	_yaw += turn * key_rotate_speed * delta
	_current_yaw = lerpf(_current_yaw, _yaw, _weight(delta, rotate_smoothing))

	# Free rotation accumulates, so fold both values back by whole turns
	# together. The gap between them is what the smoothing reads.
	var turns := floorf(_yaw / 360.0) * 360.0
	if not is_zero_approx(turns):
		_yaw -= turns
		_current_yaw -= turns


func _update_pan(delta: float) -> void:
	var input := Input.get_vector(
		&"camera_pan_left", &"camera_pan_right", &"camera_pan_forward", &"camera_pan_back"
	)
	# A drag can carry the cursor to an edge, which must not push back at it.
	if edge_pan_enabled and _mouse_seen and not _dragging:
		input += _edge_pan_input()
	input = input.limit_length(1.0)

	if not input.is_zero_approx():
		# Pan relative to where the camera is looking, and scale the rate with
		# the zoom so the map slides past at a steady speed on screen.
		var yaw := deg_to_rad(_current_yaw)
		var right := Vector3(cos(yaw), 0.0, -sin(yaw))
		var forward := Vector3(-sin(yaw), 0.0, -cos(yaw))
		var speed := pan_speed * (_current_distance / far_distance)
		_pivot = _clamp_to_bounds(_pivot + (right * input.x + forward * -input.y) * speed * delta)

	_current_pivot = _current_pivot.lerp(_pivot, _weight(delta, pan_smoothing))


## Takes hold of the ground under [param mouse]. The drag slides a level
## plane at the height of whatever terrain is there, so a raised block taken
## hold of stays under the cursor as surely as the floor does.
func _start_drag(mouse: Vector2) -> void:
	if _camera == null:
		return
	_dragging = true
	_drag_mouse = mouse
	_drag_height = _pivot.y
	var from := _camera.project_ray_origin(mouse)
	var to := from + _camera.project_ray_normal(mouse) * _camera.far
	var query := PhysicsRayQueryParameters3D.create(from, to, drag_layers)
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if not hit.is_empty():
		_drag_height = (hit.position as Vector3).y


## Slides the view so the ground that was under the cursor is under it again
## at [param mouse]. The smoothed pivot moves by as much at once: easing after
## the cursor would let the ground slip out from under it.
func _drag_to(mouse: Vector2) -> void:
	# A release the rig never saw (the window lost focus) ends the drag here.
	if not Input.is_action_pressed(&"camera_free_look"):
		_dragging = false
		return
	var held: Variant = _ground_under(_drag_mouse)
	var reached: Variant = _ground_under(mouse)
	_drag_mouse = mouse
	if held == null or reached == null:
		return
	# Moving the camera moves the point under the cursor by as much, so going
	# from where the cursor reaches now to what it held puts that back under it.
	var slide := _clamp_to_bounds(_pivot + (held as Vector3) - (reached as Vector3)) - _pivot
	# Both points are on a level plane: any height between them is rounding.
	slide.y = 0.0
	_pivot += slide
	_current_pivot += slide


## Where the camera's ray through [param mouse] meets the level plane being
## dragged, or null if it never does: the plane is level with the camera or
## above it.
func _ground_under(mouse: Vector2) -> Variant:
	return Plane(Vector3.UP, _drag_height).intersects_ray(
		_camera.project_ray_origin(mouse), _camera.project_ray_normal(mouse)
	)


func _edge_pan_input() -> Vector2:
	var window := get_window()
	if window == null or not window.has_focus():
		return Vector2.ZERO
	var viewport := get_viewport()
	return _edge_pan_direction(
		viewport.get_mouse_position(), Vector2(viewport.get_visible_rect().size)
	)


## Which way a cursor at [param mouse] pushes the camera, given a viewport of
## [param size]. Zero unless the cursor is inside the viewport and within
## [member edge_pan_margin] pixels of an edge.
func _edge_pan_direction(mouse: Vector2, size: Vector2) -> Vector2:
	if mouse.x < 0.0 or mouse.y < 0.0 or mouse.x > size.x or mouse.y > size.y:
		return Vector2.ZERO

	var margin := float(edge_pan_margin)
	var input := Vector2.ZERO
	if mouse.x < margin:
		input.x = -1.0
	elif mouse.x > size.x - margin:
		input.x = 1.0
	if mouse.y < margin:
		input.y = -1.0
	elif mouse.y > size.y - margin:
		input.y = 1.0
	return input


func _zoom_distance() -> float:
	return lerpf(near_distance, far_distance, _zoom)


func _clamp_to_bounds(point: Vector3) -> Vector3:
	if not _pan_bounds.has_area():
		return point
	return Vector3(
		clampf(point.x, _pan_bounds.position.x, _pan_bounds.end.x),
		point.y,
		clampf(point.z, _pan_bounds.position.y, _pan_bounds.end.y),
	)


func _compute_pan_bounds() -> Rect2:
	var grid := get_node_or_null(grid_map_path) as GridMap
	if grid == null:
		return Rect2()

	var cells := grid.get_used_cells()
	if cells.is_empty():
		return Rect2()

	var low := cells[0]
	var high := cells[0]
	for cell in cells:
		low = Vector3i(mini(low.x, cell.x), mini(low.y, cell.y), mini(low.z, cell.z))
		high = Vector3i(maxi(high.x, cell.x), maxi(high.y, cell.y), maxi(high.z, cell.z))

	var a := grid.to_global(grid.map_to_local(low))
	var b := grid.to_global(grid.map_to_local(high))
	var rect := Rect2(Vector2(minf(a.x, b.x), minf(a.z, b.z)), Vector2.ZERO)
	rect.end = Vector2(maxf(a.x, b.x), maxf(a.z, b.z))
	return rect.grow(pan_margin)


## Framerate-independent exponential smoothing weight.
func _weight(delta: float, sharpness: float) -> float:
	return 1.0 - exp(-sharpness * delta)
