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
##   Rotate - hold Q / E, or the right stick left and right.
##   Zoom   - mouse wheel, the d-pad up and down a notch at a time, or the
##            right stick up and down. The camera slides in and out along its
##            line of sight, looking down at [member view_pitch] at every zoom.
##
## With the gamepad it pans by following the tile cursor ([TileCursor]), which
## the left stick moves, and the mouse's edge of the screen pans nothing.
##
## Rotation is free: Q / E sweep continuously and settle on any angle. The
## pitch is not the player's to change: tipped up toward the horizon, the view
## would reach past the scenery around the map to its edge.
##
## The player's own moves answer at once, eased only by the smoothing below.
## The game's moves glide, as XCOM 2's camera does (X2Camera_LookAt): looking
## at a point ([method focus_on], [method bring_into_view]), keeping a unit in
## view as it walks ([method follow]), and taking up or leaving a framed view,
## a reaction window's or an enemy's shot's ([method frame],
## [method release_frame]). A glide starts from rest, speeds
## up to [member glide_speed] over [member glide_ramp] seconds and brakes in
## proportion to what is left once it is close, so the camera never jolts into
## motion or stops dead, and the further it goes the longer it takes: most of
## the way across 4 tiles in about 0.4 s, across 40 in about 1.3 s. Zooming and
## tilting glide alike. The player panning or dragging takes the camera back
## mid-glide, from wherever it has got to.
##
## Something that needs a set of units in view, like a reaction window or an
## enemy's shot, can [method frame] them. That sets its own distance and angle
## until [method release_frame] hands them back to the zoom; the player can
## still pan, turn and zoom in the meantime. A framed view never sees further
## than the camera zoomed all the way out, which is what the scenery around a
## map is deep enough to hide ([method _furthest_frame]).
class_name CameraRig
extends Node3D

## How XCOM 2's glides brake, by what they move: each starts braking once it is
## closer than its ramp's seconds times its top speed times the first share,
## and brakes no lower than the second share of its top speed, so it arrives.
const PAN_BRAKE := 0.4
const PAN_LEAST := 0.01
const ZOOM_BRAKE := 0.4
const ZOOM_LEAST := 0.001
const TILT_BRAKE := 0.25
const TILT_LEAST := 0.005


## One of the camera's values gliding to where the game sends it, as XCOM 2
## moves its camera (X2Camera_LookAt.InterpolateLocation and its kin). From
## rest its speed ramps up to a top speed over the ramp's seconds; once it is
## closer than [member brake] of the distance that ramp covers at the top
## speed, it is held to a share of the top speed in proportion to what is left,
## never below [member least] of it, so it eases to a stop. How far up the ramp
## it is carries over from step to step while it is on the move, so a goal
## that moves mid-glide is chased without a jolt; arriving puts it back at rest.
class Glide:
	var brake: float
	var least: float
	## How far up the ramp it is: 0 at rest, 1 at the top speed.
	var alpha := 0.0

	func _init(brake_share: float, least_share: float) -> void:
		brake = brake_share
		least = least_share

	## How far to move this step toward a goal [param left] away, at most
	## [param top] a second, reached from rest in [param ramp] seconds: all of
	## [param left] once it gets there.
	func step(left: float, delta: float, top: float, ramp: float) -> float:
		var ramp_seconds := maxf(ramp, 0.001)
		alpha = minf(alpha + delta / ramp_seconds, 1.0)
		alpha = minf(alpha, clampf(left / maxf(ramp_seconds * top * brake, 0.001), least, 1.0))
		var move := top * delta * alpha
		if move >= left:
			alpha = 0.0
			return left
		return move


@export_group("Nodes")
@export var camera_path: NodePath = ^"Camera3D"
## The level ([VoxelLevel]) the pan bounds are derived from. Leave empty to pan
## without limits.
@export var level_path: NodePath = ^"../Level"
## The grid ([CombatGrid]) a drag takes hold of the ground through. Leave empty
## to take hold of whatever collides on [member drag_layers] instead.
@export var grid_path: NodePath = ^"../CombatGrid"

@export_group("Pan")
## Units per second at full zoom-out; scaled down as the camera moves in.
@export var pan_speed := 24.0
@export var pan_smoothing := 12.0
@export var edge_pan_enabled := true
## Distance in pixels from a screen edge that starts an edge pan.
@export var edge_pan_margin := 16
## How far past the edge of the map the pivot may travel, in units.
@export var pan_margin := 1.0
## What a drag can take hold of with no grid ([member grid_path]): the
## terrain's physics layer. A drag begun over anything else, or over nothing,
## slides the ground at the pivot's height.
@export_flags_3d_physics var drag_layers := 1

@export_group("Rotate")
## Degrees per second while Q / E are held.
@export var key_rotate_speed := 110.0
@export var rotate_smoothing := 14.0

@export_group("Zoom")
@export var zoom_smoothing := 10.0
## Fraction of the full zoom range covered by one wheel notch.
@export var zoom_step := 1.0 / 12.0
## Notches of zoom a second with the right stick pushed all the way.
@export var stick_zoom_speed := 10.0
@export var near_distance := 6.0
@export var far_distance := 22.0
## Degrees below horizontal the camera looks down, at every zoom. Keep it
## well above half the camera's vertical FOV (37.5 at the default 75), or the
## top of the screen reaches the horizon.
@export var view_pitch := 55.0

@export_group("Framing")
## Nearest and furthest the camera sits when framing an overview, the reaction
## view. The near limit keeps a framed view an overview even when everything
## in it stands close together. The far limit keeps it from seeing further than
## the camera zoomed all the way out, which is what the scenery around a map is
## deep enough to hide: it holds for a view looking down more steeply than
## [member view_pitch] (the reaction view's 62 degrees), and a frame at
## [member view_pitch] goes no further than [member far_distance] (see
## [method frame]).
@export var min_frame_distance := 16.0
@export var max_frame_distance := 28.0
## How far out from the centre of the screen framed points may sit, as a
## share of the way to the edge: across, above, and below. Below is tighter
## because the squad panel and the action bar run along the bottom. A unit
## counts as in view ([method has_in_view]) inside the same margins.
@export var frame_margin_x := 0.8
@export var frame_margin_top := 0.8
@export var frame_margin_bottom := 0.55

@export_group("Glide")
## The fastest the camera glides, in tiles a second: XCOM 2's 3000 units a
## second over its 96-unit tile. It is the same at every zoom, as XCOM 2's is,
## so a glide takes as long however far in the camera is.
@export var glide_speed := 31.25
## Seconds a glide takes to speed up to [member glide_speed] from rest.
@export var glide_ramp := 0.35
## The fastest a glide zooms, in shares of the zoom's whole range
## ([member near_distance] to [member far_distance]) a second, and the seconds
## it takes to speed up to that from rest.
@export var glide_zoom_speed := 3.0
@export var glide_zoom_ramp := 0.25
## The fastest a glide tilts the camera, in degrees a second, and the seconds
## it takes to speed up to that from rest.
@export var glide_tilt_speed := 400.0
@export var glide_tilt_ramp := 0.4

@export_group("Follow")
## How far ahead of a unit it follows ([method follow]) the camera looks, in
## tiles along the unit's way.
@export var follow_lead := 1.0

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

# Set while a glide carries the pivot to [member _pivot], and while one carries
# the distance to the frame's or the zoom's, in place of easing after them as
# the player's own moves do. The pitch always glides: only the game tilts it.
var _gliding := false
var _zoom_gliding := false
var _pan_glide := Glide.new(PAN_BRAKE, PAN_LEAST)
var _zoom_glide := Glide.new(ZOOM_BRAKE, ZOOM_LEAST)
var _tilt_glide := Glide.new(TILT_BRAKE, TILT_LEAST)

# The unit [method follow] keeps in view, null when following nothing; the way
# it walks, from where it started; and the stretch of it it is crossing.
var _follow_unit: Node3D
var _follow_path := PackedVector3Array()
var _follow_segment := 0

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
	_update_follow()
	_update_pan(delta)
	_update_stick_zoom(delta)
	_update_zoom(delta)

	position = _current_pivot
	rotation_degrees = Vector3(-_current_pitch, _current_yaw, 0.0)
	_camera.position = Vector3(0.0, 0.0, _current_distance)


## Glides to look at a world position, keeping the current angle and zoom. It
## lets go of any unit [method follow] was keeping in view. A spot the camera
## is on its way to already, gliding or eased after by the player's own pan,
## is left to it: the gamepad's cursor stepping on to a target that an action
## then lines up keeps the stick's easing.
func focus_on(world_position: Vector3) -> void:
	_follow_unit = null
	if _clamp_to_bounds(Vector3(world_position.x, _pivot.y, world_position.z)).is_equal_approx(_pivot):
		return
	_glide_to(world_position)


## Looks at a world position the way the player's own panning does, easing
## after it at [member pan_smoothing]: how the gamepad's tile cursor carries the
## camera as the stick steps it. A glide under way glides on to it instead.
func pan_to(world_position: Vector3) -> void:
	_follow_unit = null
	_pivot = _clamp_to_bounds(Vector3(world_position.x, _pivot.y, world_position.z))


## Glides to look at [param unit], as XCOM 2's camera does before a unit acts,
## unless the view the camera is settling on has the whole of it inside the
## framing margins already. [method has_in_view] says when it is there.
func bring_into_view(unit: Node3D) -> void:
	if not will_be_in_view(standing(unit.global_position)):
		focus_on(unit.global_position)


## Whether the whole of [param unit] is in view now, inside the framing
## margins: the moment XCOM 2's camera counts as having arrived on it, though
## it may still be gliding the rest of the way.
func has_in_view(unit: Node3D) -> bool:
	return is_in_view(standing(unit.global_position))


## Whether every one of [param points] is inside the framing margins now: well
## in view, clear of the panels along the bottom.
func is_in_view(points: Array[Vector3]) -> bool:
	return _holds(points, _current_pivot, _current_pitch, _current_yaw, _current_distance)


## Whether every one of [param points] will be inside the framing margins of the
## view the camera is settling on: where it is gliding to, or easing after the
## player's pan.
func will_be_in_view(points: Array[Vector3]) -> bool:
	return _holds(points, _pivot, _goal_pitch(), _yaw, _goal_distance())


## A unit standing at [param feet], as the points that keep the whole of it in
## view: its feet and the top of its head.
static func standing(feet: Vector3) -> Array[Vector3]:
	return [feet, feet + Vector3.UP * CombatGrid.UNIT_HEIGHT]


## Whether the camera is still on its way somewhere the game sent it: gliding
## to a spot, a distance or a pitch.
func is_gliding() -> bool:
	return _gliding or _zoom_gliding or _current_pitch != _goal_pitch()


## Keeps [param unit] in view as it walks through [param points], as XCOM 2's
## camera follows a moving unit (X2Camera_FollowMovingUnit): not at all if the
## whole way, from where it stands, is in the view the camera is settling on
## already, and otherwise gliding after the point [member follow_lead] tiles
## ahead of it along its way, so it ends on the last point. Call it as the walk
## starts. It holds until [method stop_following], [method focus_on], the
## player panning or the unit leaving the map, and waits while a framed view
## ([method frame]), a reaction window's, holds the camera.
func follow(unit: Node3D, points: Array[Vector3]) -> void:
	_follow_unit = null
	if points.is_empty():
		return
	var path := PackedVector3Array([unit.global_position])
	path.append_array(PackedVector3Array(points))
	if not _framing:
		var whole: Array[Vector3] = []
		for point in path:
			whole.append_array(standing(point))
		if will_be_in_view(whole):
			return
	_follow_unit = unit
	_follow_path = path
	_follow_segment = 0


## Lets go of whatever [method follow] was keeping in view. The camera settles
## where it was gliding to, the end of the way at the end of a walk.
func stop_following() -> void:
	_follow_unit = null


## Looks down on [param points] from [param pitch] degrees below horizontal,
## keeping the current heading: pivots over the middle of them and pulls back
## until every one sits inside the framing margins, gliding there. An
## [param overview], the reaction view, sits no nearer than
## [member min_frame_distance] even when everything in it stands close
## together; otherwise, as for an enemy's shot, it sits no nearer than the
## player's zoom, pulling back only as far as it must. Looking down no more
## steeply than [member view_pitch], it goes no further back than
## [member far_distance], since anything further sees past the scenery around
## the map; steeper, as the reaction view is, it may go to
## [member max_frame_distance]. Points that do not fit by then are framed as
## well as that allows. Framing again while framed moves the view on; it holds
## until [method release_frame].
func frame(points: Array[Vector3], pitch: float, overview := true) -> void:
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
	_glide_to((low + high) * 0.5)
	_frame_pitch = pitch
	var furthest := _furthest_frame(pitch)
	var nearest := minf(min_frame_distance if overview else _zoom_distance(), furthest)
	_frame_distance = clampf(_distance_to_fit(points, _pivot, pitch, _yaw), nearest, furthest)
	_zoom_gliding = true


## Gives the height and angle back to the zoom. With [param back], the camera
## glides back to what it kept in view before [method frame] took it: the unit
## it follows, if it is following one, or else where it was looking. Without,
## it stays over what it framed, as after an enemy's shot, where going back
## would only be undone by whatever the camera shows next.
func release_frame(back := true) -> void:
	if not _framing:
		return
	_framing = false
	if back and is_instance_valid(_follow_unit):
		# Where the follow is now, though it may be let go this same frame, at
		# the end of the walk, before it moves the camera again.
		_glide_to(_ahead_on_path(_follow_unit.global_position, follow_lead))
	elif back:
		_glide_to(_unframed_pivot)
	_zoom_gliding = true


## Whether [method frame] is holding the view.
func is_framing() -> bool:
	return _framing


## Sets the pivot gliding to look at [param world_position].
func _glide_to(world_position: Vector3) -> void:
	_pivot = _clamp_to_bounds(Vector3(world_position.x, _pivot.y, world_position.z))
	_gliding = true


## The player takes the camera back: a glide stops where it has got to, and
## nothing is followed any more.
func _take_back() -> void:
	_follow_unit = null
	if _gliding:
		_gliding = false
		_pan_glide.alpha = 0.0
		_pivot = _current_pivot


## Moves the glide's goal on with the unit [method follow] keeps in view.
func _update_follow() -> void:
	if not is_instance_valid(_follow_unit):
		_follow_unit = null
		return
	if _framing:
		return
	_glide_to(_ahead_on_path(_follow_unit.global_position, follow_lead))


## The point [param lead] further along the followed way than [param at],
## where the unit is, or the way's end.
func _ahead_on_path(at: Vector3, lead: float) -> Vector3:
	var last := _follow_path.size() - 1
	# The stretch it is crossing only moves on once it is past the stretch's
	# end, so a way that doubles back is never read from the wrong stretch.
	while _follow_segment < last - 1 and _along(at, _follow_segment) >= 1.0:
		_follow_segment += 1
	var from := _follow_path[_follow_segment].lerp(
		_follow_path[_follow_segment + 1], clampf(_along(at, _follow_segment), 0.0, 1.0)
	)
	var left := lead
	for i in range(_follow_segment + 1, last + 1):
		var stretch := from.distance_to(_follow_path[i])
		if stretch >= left:
			return from.move_toward(_follow_path[i], left)
		left -= stretch
		from = _follow_path[i]
	return _follow_path[last]


## How far along stretch [param segment] of the followed way [param at] is: 0
## at its start, 1 at its end.
func _along(at: Vector3, segment: int) -> float:
	var start := _follow_path[segment]
	var way := _follow_path[segment + 1] - start
	if is_zero_approx(way.length_squared()):
		return 1.0
	return (at - start).dot(way) / way.length_squared()


## Whether a camera looking at [param pivot] from [param distance] away, down
## at [param pitch] on heading [param yaw], has every one of [param points]
## inside the framing margins: well in view, clear of the panels at the bottom.
func _holds(points: Array[Vector3], pivot: Vector3, pitch: float, yaw: float, distance: float) -> bool:
	return _distance_to_fit(points, pivot, pitch, yaw) <= distance


## How far back from [param pivot] the camera has to sit, looking down at
## [param pitch] on heading [param yaw], to have all of [param points] inside
## the framing margins.
func _distance_to_fit(points: Array[Vector3], pivot: Vector3, pitch: float, yaw: float) -> float:
	var view := Basis.from_euler(Vector3(deg_to_rad(-pitch), deg_to_rad(yaw), 0.0)).inverse()
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


## The furthest back a framed view looking down at [param pitch] may sit:
## [member max_frame_distance] for one steeper than [member view_pitch], as the
## reaction view is, and no further than the zoom goes for one at the usual
## pitch or shallower, which would otherwise see past the scenery around the
## map.
func _furthest_frame(pitch: float) -> float:
	return max_frame_distance if pitch > view_pitch else far_distance


## Where the distance is going: the frame's while framed, else the zoom's.
func _goal_distance() -> float:
	return _frame_distance if _framing else _zoom_distance()


## Where the pitch is going: the frame's while framed, else [member view_pitch].
func _goal_pitch() -> float:
	return _frame_pitch if _framing else view_pitch


## One wheel notch in [param direction], out if positive. While framed it
## moves the camera by the same distance a notch of zoom would, no further out
## than the frame may go. The player's zoom takes the distance back from any
## glide.
func _step_zoom(direction: float) -> void:
	_zoom_gliding = false
	_zoom_glide.alpha = 0.0
	if _framing:
		var step := zoom_step * (far_distance - near_distance)
		_frame_distance = clampf(
			_frame_distance + direction * step, near_distance, _furthest_frame(_frame_pitch)
		)
	else:
		_zoom = clampf(_zoom + direction * zoom_step, 0.0, 1.0)


## The right stick zooms smoothly, as far in a second as
## [member stick_zoom_speed] notches of the wheel.
func _update_stick_zoom(delta: float) -> void:
	var push := Input.get_axis(&"camera_zoom_stick_in", &"camera_zoom_stick_out")
	if not is_zero_approx(push):
		_step_zoom(push * stick_zoom_speed * delta)


## Brings the distance and the pitch to where they are going: the player's
## zoom eases after the wheel, the game's glides, and so does every tilt.
func _update_zoom(delta: float) -> void:
	var distance := _goal_distance()
	if _zoom_gliding:
		var top := glide_zoom_speed * (far_distance - near_distance)
		var left := absf(distance - _current_distance)
		_current_distance = move_toward(
			_current_distance, distance, _zoom_glide.step(left, delta, top, glide_zoom_ramp)
		)
		_zoom_gliding = _current_distance != distance
	else:
		_current_distance = lerpf(_current_distance, distance, _weight(delta, zoom_smoothing))
	var pitch := _goal_pitch()
	_current_pitch = move_toward(
		_current_pitch,
		pitch,
		_tilt_glide.step(absf(pitch - _current_pitch), delta, glide_tilt_speed, glide_tilt_ramp)
	)


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
	# A drag can carry the cursor to an edge, which must not push back at it,
	# and a mouse left lying at one while the gamepad is in use pushes nothing.
	if edge_pan_enabled and _mouse_seen and not _dragging and not InputDevice.gamepad:
		input += _edge_pan_input()
	input = input.limit_length(1.0)

	if not input.is_zero_approx():
		_take_back()
		# Pan relative to where the camera is looking, and scale the rate with
		# the zoom so the map slides past at a steady speed on screen.
		var yaw := deg_to_rad(_current_yaw)
		var right := Vector3(cos(yaw), 0.0, -sin(yaw))
		var forward := Vector3(-sin(yaw), 0.0, -cos(yaw))
		var speed := pan_speed * (_current_distance / far_distance)
		_pivot = _clamp_to_bounds(_pivot + (right * input.x + forward * -input.y) * speed * delta)

	if _gliding:
		var gap := _pivot - _current_pivot
		var left := gap.length()
		var move := _pan_glide.step(left, delta, glide_speed, glide_ramp)
		if move >= left:
			_current_pivot = _pivot
			_gliding = false
		else:
			_current_pivot += gap / left * move
	else:
		_current_pivot = _current_pivot.lerp(_pivot, _weight(delta, pan_smoothing))


## Takes hold of the ground under [param mouse]. The drag slides a level
## plane at the height of whatever terrain is there, so a raised block taken
## hold of stays under the cursor as surely as the floor does.
func _start_drag(mouse: Vector2) -> void:
	if _camera == null:
		return
	_take_back()
	_dragging = true
	_drag_mouse = mouse
	_drag_height = _pivot.y
	var from := _camera.project_ray_origin(mouse)
	var heading := _camera.project_ray_normal(mouse)
	# The grid's cells are all there from the first frame of a battle, where the
	# level's collision is given it over the first few seconds
	# (LevelRenderer.stream_collision), and they change the moment a block
	# breaks.
	var grid := get_node_or_null(grid_path) as CombatGrid
	if grid != null:
		var met: Variant = grid.cast(from, heading, _camera.far)
		if met != null:
			_drag_height = (met as CombatGrid.RayHit).point.y
		return
	var to := from + heading * _camera.far
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
	var level := get_node_or_null(level_path) as VoxelLevel
	if level == null or level.rules == null:
		return Rect2()

	# From the middle of the least cell any piece stands in to the middle of
	# the greatest, as the grid's cells were counted.
	var a := level.cell_center(level.rules.bounds_min)
	var b := level.cell_center(level.rules.bounds_max)
	var rect := Rect2(Vector2(minf(a.x, b.x), minf(a.z, b.z)), Vector2.ZERO)
	rect.end = Vector2(maxf(a.x, b.x), maxf(a.z, b.z))
	return rect.grow(pan_margin)


## Framerate-independent exponential smoothing weight.
func _weight(delta: float, sharpness: float) -> float:
	return 1.0 - exp(-sharpness * delta)
