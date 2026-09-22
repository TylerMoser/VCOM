## The shot being lined up, drawn over the map: the sight line from wherever
## the shooter is firing from, a reticle on the target, and a panel naming it.
##
## It is all screen space, redrawn every frame from the two world positions it
## was handed, so it keeps up with the camera without any 3D nodes to place.
class_name ShotOverlay
extends Control

## Half-width of the reticle, and the length of each of its corner arms.
const RETICLE_SIZE := 22.0
const RETICLE_ARM := 8.0
const RETICLE_WIDTH := 2.0
## Pixels between the top of the reticle and the target panel above it.
const PANEL_GAP := 10.0

const LINE_COLOR := Color(1.0, 0.45, 0.35, 0.85)
const LINE_WIDTH := 2.0
const LINE_DASH := 9.0
const RETICLE_COLOR := Color(1.0, 0.3, 0.25)

## Eye the shot is taken from, and the eye it is aimed at.
var _from := Vector3.ZERO
var _to := Vector3.ZERO

var _panel: TargetPanel


func _init() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	visible = false
	set_process(false)

	_panel = TargetPanel.new()
	add_child(_panel)


# The camera moves under a still target, so redraw every frame rather than
# only when the shot changes.
func _process(_delta: float) -> void:
	queue_redraw()


## Draws [param shot], fired from the eye at [param from] toward the eye at
## [param to].
func show_shot(from: Vector3, to: Vector3, shot: LineOfSight.Shot) -> void:
	_from = from
	_to = to
	_panel.bind(shot)
	visible = true
	set_process(true)
	queue_redraw()


func clear() -> void:
	visible = false
	set_process(false)


func _draw() -> void:
	var camera := get_viewport().get_camera_3d()
	# Nothing to aim at once the target is behind the camera.
	if camera == null or camera.is_position_behind(_to):
		_panel.visible = false
		return

	var target := camera.unproject_position(_to)
	if not camera.is_position_behind(_from):
		draw_dashed_line(
			camera.unproject_position(_from), target, LINE_COLOR, LINE_WIDTH, LINE_DASH, true, true
		)
	_draw_reticle(target)

	_panel.visible = true
	_panel.position = target - Vector2(
		_panel.size.x * 0.5, RETICLE_SIZE + PANEL_GAP + _panel.size.y
	)


## Four corner brackets around [param center], leaving the target itself
## clear to look at.
func _draw_reticle(center: Vector2) -> void:
	for corner: Vector2 in [Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1), Vector2(1, 1)]:
		var point := center + corner * RETICLE_SIZE
		var arm := corner * RETICLE_ARM
		draw_line(point, point - Vector2(arm.x, 0.0), RETICLE_COLOR, RETICLE_WIDTH, true)
		draw_line(point, point - Vector2(0.0, arm.y), RETICLE_COLOR, RETICLE_WIDTH, true)
