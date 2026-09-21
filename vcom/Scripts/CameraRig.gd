## Tactical camera rig for the combat map.
##
## This node is the pivot: it sits on the ground plane at the point the camera
## is looking at. The Camera3D child hangs off the rig's local +Z, so rotating
## the rig orbits the camera around that point, and the child's local Z is the
## zoom distance.
##
##   Pan    - WASD / arrow keys, or push the mouse against a screen edge.
##   Rotate - hold Q / E, or drag with the middle mouse button (drag also tilts).
##   Zoom   - mouse wheel. Zooming in also lowers the camera toward the action.
##
## Rotation is free: Q / E sweep continuously and settle on any angle.
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
@export var pan_margin := 4.0

@export_group("Rotate")
## Degrees per second while Q / E are held.
@export var key_rotate_speed := 110.0
## Degrees per pixel of middle-mouse drag.
@export var drag_rotate_speed := 0.3
@export var rotate_smoothing := 14.0
## Degrees of manual tilt allowed above and below the zoom-driven pitch.
@export var free_pitch_range := 15.0

@export_group("Zoom")
@export var zoom_smoothing := 10.0
## Fraction of the full zoom range covered by one wheel notch.
@export var zoom_step := 0.1
@export var near_distance := 8.0
@export var far_distance := 30.0
## Pitch in degrees below horizontal, zoomed all the way in.
@export var near_pitch := 25.0
## Pitch in degrees below horizontal, zoomed all the way out.
@export var far_pitch := 55.0

var _camera: Camera3D

# Targets the player drives directly.
var _pivot := Vector3.ZERO
var _yaw := 0.0
var _zoom := 0.0
var _pitch_offset := 0.0

# Smoothed values actually written to the transforms.
var _current_pivot := Vector3.ZERO
var _current_yaw := 0.0
var _current_distance := 0.0
var _current_pitch := 0.0

var _drag_rotating := false
var _mouse_seen := false
var _pan_bounds := Rect2()


func _ready() -> void:
	_camera = get_node_or_null(camera_path) as Camera3D
	if _camera == null:
		push_error("CameraRig: no Camera3D at '%s'." % camera_path)
		set_process(false)
		return

	_pan_bounds = _compute_pan_bounds()

	# Adopt whatever framing the scene was authored with, so pressing Run does
	# not snap the camera somewhere else on the first frame.
	_pivot = position
	_yaw = rotation_degrees.y
	_zoom = clampf(inverse_lerp(near_distance, far_distance, _camera.position.z), 0.0, 1.0)
	_pitch_offset = clampf(-rotation_degrees.x - _zoom_pitch(), -free_pitch_range, free_pitch_range)

	_current_pivot = _pivot
	_current_yaw = _yaw
	_current_distance = _zoom_distance()
	_current_pitch = _zoom_pitch() + _pitch_offset


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"camera_zoom_in"):
		_zoom = clampf(_zoom - zoom_step, 0.0, 1.0)
	elif event.is_action_pressed(&"camera_zoom_out"):
		_zoom = clampf(_zoom + zoom_step, 0.0, 1.0)
	elif event.is_action_pressed(&"camera_free_look"):
		_drag_rotating = true
	elif event.is_action_released(&"camera_free_look"):
		_drag_rotating = false
	elif event is InputEventMouseMotion:
		_mouse_seen = true
		if not _drag_rotating:
			return
		# screen_relative is raw screen pixels. relative is scaled by the
		# project's canvas stretch, which would make drag sensitivity depend on
		# the window size.
		var motion := (event as InputEventMouseMotion).screen_relative
		_yaw -= motion.x * drag_rotate_speed
		# Dragging up orbits the camera up, toward a more top-down view.
		_pitch_offset = clampf(
			_pitch_offset - motion.y * drag_rotate_speed,
			-free_pitch_range,
			free_pitch_range,
		)


func _process(delta: float) -> void:
	_update_rotation(delta)
	_update_pan(delta)

	_current_distance = lerpf(_current_distance, _zoom_distance(), _weight(delta, zoom_smoothing))
	_current_pitch = lerpf(
		_current_pitch, _zoom_pitch() + _pitch_offset, _weight(delta, zoom_smoothing)
	)

	position = _current_pivot
	rotation_degrees = Vector3(-_current_pitch, _current_yaw, 0.0)
	_camera.position = Vector3(0.0, 0.0, _current_distance)


## Centres the camera on a world position, keeping the current angle and zoom.
func focus_on(world_position: Vector3) -> void:
	_pivot = _clamp_to_bounds(Vector3(world_position.x, _pivot.y, world_position.z))


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
	if edge_pan_enabled and _mouse_seen and not _drag_rotating:
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


func _zoom_pitch() -> float:
	return lerpf(near_pitch, far_pitch, _zoom)


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
