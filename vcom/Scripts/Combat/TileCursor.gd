## The gamepad's pointer on the combat map: a tile, marked in its own colour on
## top of every other highlight, that the left stick moves a tile at a time,
## with the camera following it. Where the mouse points with the keyboard and
## mouse, this points with the gamepad: Move walks to it, Throw Grenade aims at
## it ([method ActionController.pointed_tile]).
##
## The stick steps it across the ground the way it is pushed on screen, so up
## is always away from the camera however it is turned, in any of eight
## directions: once as the stick is pushed, then again after
## [constant FIRST_REPEAT] and every [constant REPEAT] seconds while it is
## held. Each step goes to the next column of the grid that way with a tile in
## it, the tile nearest the cursor's height there, skipping up to
## [constant MOST_SKIPPED] columns with none (a tree, a wall), and goes nowhere
## past the map's edge.
##
## Over the tile a small pyramid points down at it, bobbing, so the cursor
## stands out from the move range's squares of much the same blue: just above
## an empty tile, and over the head of a unit standing on one, which hides the
## square. Any higher over an empty tile and, seen from the camera's pitch, it
## reads as over the tile beyond.
##
## The [ActionController] owns it, shows it while the gamepad is in use on the
## player's turn, and puts it on whoever is selected.
class_name TileCursor
extends Node

## Moved by the stick, or put somewhere ([method snap_to]).
signal moved(tile: Vector3i)

const LAYER := &"cursor"
const COLOR := Color(0.45, 1.0, 1.0)
## Outline more than fill, so what it lies on reads through it.
const FILL := 0.35
## How far the stick goes before it steps.
const PUSH := 0.5
const FIRST_REPEAT := 0.3
const REPEAT := 0.085
## Columns without a tile stepped over in one step.
const MOST_SKIPPED := 3
## How far above the cursor a tile can be found in the next column.
const HIGHEST_STEP := 4
## The marker over the tile: how high its point floats above the floor, over
## an empty tile and over a unit's head, how far it bobs, how fast, how fast
## it turns, and how fast it rises or drops between the two heights.
const MARKER_HEIGHT := 0.45
const MARKER_OVER_UNIT := 2.25
const MARKER_CLIMB := 12.0
const MARKER_BOB := 0.12
const MARKER_BOB_SPEED := 4.0
const MARKER_TURN_SPEED := 1.5
const MARKER_SIZE := Vector2(0.22, 0.34)

var grid: CombatGrid
var highlights: TileHighlights
## Followed by the camera, if there is one.
var camera_rig: CameraRig
## The tile it is on, or null before it is put anywhere.
var tile: Variant = null
## Whether it is drawn and the stick moves it.
var shown := false:
	set(value):
		if shown == value:
			return
		shown = value
		_held = Vector2i.ZERO
		_mark()

## The direction the stick last stepped it, and how long until it steps again.
var _held := Vector2i.ZERO
var _repeat_in := 0.0
var _marker: MeshInstance3D
var _time := 0.0
## How high the marker's point is over the floor now, easing to its height.
var _lift := MARKER_HEIGHT


func _ready() -> void:
	var pyramid := CylinderMesh.new()
	pyramid.top_radius = MARKER_SIZE.x
	pyramid.bottom_radius = 0.0
	pyramid.height = MARKER_SIZE.y
	pyramid.radial_segments = 4
	pyramid.rings = 1
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = COLOR
	pyramid.material = material
	_marker = MeshInstance3D.new()
	_marker.name = "Marker"
	_marker.mesh = pyramid
	_marker.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_marker.visible = false
	add_child(_marker)


func _process(delta: float) -> void:
	_place_marker(delta)
	if not shown or tile == null:
		return
	var stick := Input.get_vector(&"cursor_left", &"cursor_right", &"cursor_up", &"cursor_down")
	if stick.length() < PUSH:
		_held = Vector2i.ZERO
		return
	var step := _ground_step(stick)
	if step != _held:
		_held = step
		_repeat_in = FIRST_REPEAT
		_step(step)
		return
	_repeat_in -= delta
	if _repeat_in <= 0.0:
		_repeat_in += REPEAT
		_step(step)


## Puts the cursor on [param to], and the camera on it if [param follow].
func snap_to(to: Vector3i, follow := true) -> void:
	tile = to
	_mark()
	if follow:
		_follow()
	moved.emit(to)


## The tile the cursor is on, found again in its column if the ground there has
## changed since (a block shot away under it), or null.
func current() -> Variant:
	if tile == null:
		return null
	var at: Vector3i = tile
	if grid.is_tile(at):
		return at
	var found: Variant = _tile_in_column(at.x, at.z, at.y)
	if found != null:
		tile = found
		_mark()
	return found


## Moves one step [param step] across the ground, if there is anywhere to go.
func _step(step: Vector2i) -> void:
	var from: Variant = current()
	if from == null:
		return
	var at: Vector3i = from
	for reach in range(1, MOST_SKIPPED + 2):
		var found: Variant = _tile_in_column(at.x + step.x * reach, at.z + step.y * reach, at.y)
		if found != null:
			snap_to(found)
			return


## Which of the eight ways across the grid the stick, pushed [param stick] on
## screen, points: up the screen is away from the camera.
func _ground_step(stick: Vector2) -> Vector2i:
	var camera := get_viewport().get_camera_3d()
	var right := Vector3.RIGHT
	var forward := Vector3.FORWARD
	if camera != null:
		right = camera.global_basis.x
		forward = -camera.global_basis.z
	right.y = 0.0
	forward.y = 0.0
	var way := right.normalized() * stick.x + forward.normalized() * -stick.y
	var angle := snappedf(atan2(way.z, way.x), PI / 4.0)
	return Vector2i(roundi(cos(angle)), roundi(sin(angle)))


## The tile in column ([param x], [param z]) nearest height [param near_y], the
## higher of two as near, or null when the column has none.
func _tile_in_column(x: int, z: int, near_y: int) -> Variant:
	var best: Variant = null
	for y in range(near_y + HIGHEST_STEP, -1, -1):
		var candidate := Vector3i(x, y, z)
		if not grid.is_tile(candidate):
			continue
		if best == null or absi(y - near_y) < absi((best as Vector3i).y - near_y):
			best = candidate
	return best


## Bobs and turns the marker over the tile, or hides it.
func _place_marker(delta: float) -> void:
	_marker.visible = shown and tile != null and grid != null
	if not _marker.visible:
		return
	_time += delta
	var wanted := MARKER_OVER_UNIT if _unit_on(tile) else MARKER_HEIGHT
	_lift = lerpf(_lift, wanted, 1.0 - exp(-MARKER_CLIMB * delta))
	var lift := _lift + MARKER_SIZE.y * 0.5 + (1.0 + sin(_time * MARKER_BOB_SPEED)) * 0.5 * MARKER_BOB
	_marker.position = grid.tile_position(tile) + Vector3.UP * lift
	_marker.rotation.y = _time * MARKER_TURN_SPEED


## Whether a living unit, of either side, stands on [param on].
func _unit_on(on: Vector3i) -> bool:
	for unit in get_tree().get_nodes_in_group(&"units"):
		if is_instance_valid(unit) and grid.tile_at((unit as Node3D).global_position) == on:
			return true
	return false


func _mark() -> void:
	if highlights == null:
		return
	if shown and tile != null:
		highlights.set_layer(LAYER, {tile: COLOR}, FILL, true)
	else:
		highlights.clear_layer(LAYER)


func _follow() -> void:
	if camera_rig != null and tile != null:
		camera_rig.focus_on(grid.tile_position(tile))
