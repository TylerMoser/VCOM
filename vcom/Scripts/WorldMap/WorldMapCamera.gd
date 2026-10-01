## Camera for the world map, driven like the combat map's [CameraRig] where a
## flat map allows.
##
##   Pan  - WASD / arrow keys, or push the mouse against a screen edge, as in
##          combat, or drag with the middle mouse button, which grabs the map
##          and slides it. That button's action is camera_free_look, named for
##          when it turned the combat camera, which no longer uses it.
##   Zoom - mouse wheel, toward the point under the cursor.
##
## Zoomed all the way out the whole map fits on screen; all the way in, one
## pixel of the map image is one pixel of the view. The centre of the view
## never leaves the map.
class_name WorldMapCamera
extends Camera2D

@export_group("Nodes")
## Sprite whose rectangle is the map: it sets the pan bounds and the zoom-out
## limit. Leave empty to pan and zoom without limits.
@export var map_path: NodePath = ^"../Map"

@export_group("Pan")
## Screen pixels per second the map slides past, at any zoom.
@export var pan_speed := 900.0
@export var pan_smoothing := 12.0
@export var edge_pan_enabled := true
## Distance in pixels from a screen edge that starts an edge pan.
@export var edge_pan_margin := 16

@export_group("Zoom")
@export var zoom_smoothing := 10.0
## How much one wheel notch magnifies or shrinks the view.
@export var zoom_step := 1.25
## Closest zoom: 1 shows the map image at its own resolution.
@export var max_zoom := 1.0
## Share of the screen the whole map fills when zoomed all the way out.
@export var fit_margin := 0.9

var _map: Sprite2D

# Targets the player drives directly.
var _target_position := Vector2.ZERO
var _target_zoom := 1.0

# Smoothed values actually written to the camera.
var _current_position := Vector2.ZERO
var _current_zoom := 1.0

var _dragging := false
var _mouse_seen := false


func _ready() -> void:
	if not map_path.is_empty():
		_map = get_node_or_null(map_path) as Sprite2D
		if _map == null:
			push_error("WorldMapCamera: no Sprite2D at '%s'; panning without limits." % map_path)

	# Start with the whole map in view, centred on it.
	_target_zoom = _min_zoom()
	_target_position = _map_rect().get_center() if _map != null else global_position
	_current_zoom = _target_zoom
	_current_position = _target_position
	_apply()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"camera_zoom_in"):
		_step_zoom(zoom_step)
	elif event.is_action_pressed(&"camera_zoom_out"):
		_step_zoom(1.0 / zoom_step)
	elif event.is_action_pressed(&"camera_free_look"):
		_dragging = true
	elif event.is_action_released(&"camera_free_look"):
		_dragging = false
	elif event is InputEventMouseMotion:
		_mouse_seen = true
		if not _dragging:
			return
		# relative is in the viewport's own pixels, the same units the zoom
		# scales, so the map stays under the cursor whatever the window size.
		# The drag skips the smoothing for the same reason.
		var motion := (event as InputEventMouseMotion).relative
		_target_position = _clamp_to_map(_target_position - motion / _current_zoom)
		_current_position = _target_position


func _process(delta: float) -> void:
	# The zoom-out limit follows the window, so resizing it never leaves the
	# view zoomed out past the whole map.
	_target_zoom = clampf(_target_zoom, _min_zoom(), max_zoom)
	_update_pan(delta)

	# Smooth the zoom in log space so each notch takes as long in as out.
	var log_zoom := lerpf(log(_current_zoom), log(_target_zoom), _weight(delta, zoom_smoothing))
	_current_zoom = exp(log_zoom)
	_current_position = _current_position.lerp(_target_position, _weight(delta, pan_smoothing))
	_apply()


## Centres the view on a point of the map, keeping the current zoom.
func focus_on(map_position: Vector2) -> void:
	_target_position = _clamp_to_map(map_position)


## One wheel notch, multiplying the zoom by [param factor]. The point under the
## cursor stays under it, so the wheel zooms toward what the player points at.
func _step_zoom(factor: float) -> void:
	var zoom_to := clampf(_target_zoom * factor, _min_zoom(), max_zoom)
	if is_equal_approx(zoom_to, _target_zoom):
		return
	var viewport := get_viewport()
	var offset := viewport.get_mouse_position() - viewport.get_visible_rect().size * 0.5
	var anchor := _target_position + offset / _target_zoom
	_target_zoom = zoom_to
	_target_position = _clamp_to_map(anchor - offset / _target_zoom)


func _update_pan(delta: float) -> void:
	var input := Input.get_vector(
		&"camera_pan_left", &"camera_pan_right", &"camera_pan_forward", &"camera_pan_back"
	)
	if edge_pan_enabled and _mouse_seen and not _dragging:
		input += _edge_pan_input()
	input = input.limit_length(1.0)
	if not input.is_zero_approx():
		_target_position = _clamp_to_map(_target_position + input * pan_speed / _current_zoom * delta)


func _edge_pan_input() -> Vector2:
	var window := get_window()
	if window == null or not window.has_focus():
		return Vector2.ZERO
	var viewport := get_viewport()
	var mouse := viewport.get_mouse_position()
	var size := viewport.get_visible_rect().size
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


## The zoom at which the whole map fills [member fit_margin] of the screen.
func _min_zoom() -> float:
	if _map == null:
		return minf(0.01, max_zoom)
	var size := _map_rect().size
	var screen := get_viewport().get_visible_rect().size
	return minf(minf(screen.x / size.x, screen.y / size.y) * fit_margin, max_zoom)


## The map sprite's rectangle in global space, where the camera sits.
func _map_rect() -> Rect2:
	return _map.get_global_transform() * _map.get_rect()


func _clamp_to_map(point: Vector2) -> Vector2:
	if _map == null:
		return point
	var rect := _map_rect()
	return point.clamp(rect.position, rect.end)


func _apply() -> void:
	global_position = _current_position
	zoom = Vector2(_current_zoom, _current_zoom)


## Framerate-independent exponential smoothing weight.
func _weight(delta: float, sharpness: float) -> float:
	return 1.0 - exp(-sharpness * delta)
