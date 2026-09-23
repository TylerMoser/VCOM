## The shot being lined up, drawn over the map: the sight line from wherever
## the shooter is firing from, a reticle on the target, and a panel naming it
## and its odds. Once the trigger goes, it calls the result over the target,
## which is the only thing that separates a miss from nothing happening.
##
## It is all screen space, redrawn every frame from the world positions it was
## handed, so it keeps up with the camera without any 3D nodes to place.
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
## Fire coming the other way, drawn paler so it does not read as your own aim.
const INCOMING_COLOR := Color(1.0, 0.88, 0.85, 0.9)

## How long a hit or a miss stays up, how far it drifts while it fades, and
## how far it clears the target by.
const RESULT_SECONDS := 0.9
const RESULT_RISE := 26.0
const RESULT_GAP := 8.0
const RESULT_FONT_SIZE := 24
const HIT_COLOR := Color(1.0, 0.82, 0.3)
const MISS_COLOR := Color(0.85, 0.88, 0.95)
const RESULT_OUTLINE_COLOR := Color(0.04, 0.04, 0.07)
const RESULT_OUTLINE_WIDTH := 5

## Eye the shot is taken from, and the eye it is aimed at.
var _from := Vector3.ZERO
var _to := Vector3.ZERO
var _aiming := false
## True while the line is someone shooting at the player rather than the
## player lining a shot up. It gets the line and the result, nothing else.
var _incoming := false

var _result := ""
var _result_at := Vector3.ZERO
var _result_color := Color.WHITE
## Whether the result sits under the target rather than over it. The target
## panel owns the space above a shot the player is taking, and nothing owns
## it when the player is the one being shot at.
var _result_below := true
## Seconds of the result left to show. Zero once it has faded out.
var _result_left := 0.0

var _panel: TargetPanel


func _init() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	visible = false
	set_process(false)

	_panel = TargetPanel.new()
	add_child(_panel)


# The camera moves under a still target, so redraw every frame rather than
# only when the shot changes.
func _process(delta: float) -> void:
	if _result_left > 0.0:
		_result_left = maxf(_result_left - delta, 0.0)
	# Nothing left to draw once the aim is down and the result has faded.
	if not _aiming and _result_left <= 0.0:
		visible = false
		set_process(false)
		return
	if _aiming and not _incoming:
		_panel.details_shown = Input.is_action_pressed(&"show_shot_details")
	queue_redraw()


## Draws [param shot], fired from the eye at [param from] toward the eye at
## [param to], with [param estimate] as its odds.
func show_shot(
	from: Vector3, to: Vector3, shot: LineOfSight.Shot, estimate: HitChance.Estimate
) -> void:
	_from = from
	_to = to
	_aiming = true
	_incoming = false
	_panel.bind(shot, estimate)
	visible = true
	set_process(true)
	queue_redraw()


## Calls [param text] at the world position [param at], for as long as
## [constant RESULT_SECONDS]. Outlives [method clear], so the result of a
## shot is still readable once the aim has been put away.
##
## [param below] puts it under the target, which is where it belongs while
## the target panel holds the space above. Callers decide once rather than
## letting it follow the panel, which would jump as the panel comes and goes.
func flash_result(at: Vector3, text: String, hit: bool, below := true) -> void:
	_result = text
	_result_at = at
	_result_color = HIT_COLOR if hit else MISS_COLOR
	_result_below = below
	_result_left = RESULT_SECONDS
	visible = true
	set_process(true)


## Draws the line of a shot taken at the player, from the eye at [param from]
## to the eye at [param to]. No reticle and no panel: those belong to the
## player's own aim.
func show_incoming(from: Vector3, to: Vector3) -> void:
	_from = from
	_to = to
	_aiming = true
	_incoming = true
	visible = true
	set_process(true)
	queue_redraw()


func clear() -> void:
	_aiming = false
	_incoming = false
	_panel.visible = false
	if _result_left <= 0.0:
		visible = false
		set_process(false)


func _draw() -> void:
	var camera := get_viewport().get_camera_3d()
	if camera == null:
		return

	# Nothing to aim at once the target is behind the camera.
	if _aiming and not camera.is_position_behind(_to):
		var target := camera.unproject_position(_to)
		if not camera.is_position_behind(_from):
			draw_dashed_line(
				camera.unproject_position(_from),
				target,
				INCOMING_COLOR if _incoming else LINE_COLOR,
				LINE_WIDTH,
				LINE_DASH,
				true,
				true,
			)
		if _incoming:
			_panel.visible = false
		else:
			_draw_reticle(target)
			_panel.visible = true
			_panel.position = target - Vector2(
				_panel.size.x * 0.5, RETICLE_SIZE + PANEL_GAP + _panel.size.y
			)
	else:
		_panel.visible = false

	if _result_left > 0.0 and not camera.is_position_behind(_result_at):
		_draw_result(camera.unproject_position(_result_at), _result_below)


## Four corner brackets around [param center], leaving the target itself
## clear to look at.
func _draw_reticle(center: Vector2) -> void:
	for corner: Vector2 in [Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1), Vector2(1, 1)]:
		var point := center + corner * RETICLE_SIZE
		var arm := corner * RETICLE_ARM
		draw_line(point, point - Vector2(arm.x, 0.0), RETICLE_COLOR, RETICLE_WIDTH, true)
		draw_line(point, point - Vector2(0.0, arm.y), RETICLE_COLOR, RETICLE_WIDTH, true)


## The result, drifting up and fading as its time runs out. It is outlined
## because it lands over the map, which is as bright as the text is.
func _draw_result(at: Vector2, below: bool) -> void:
	var gone := 1.0 - _result_left / RESULT_SECONDS
	var font := get_theme_default_font()
	var width := font.get_string_size(
		_result, HORIZONTAL_ALIGNMENT_LEFT, -1.0, RESULT_FONT_SIZE
	).x
	var color := _result_color
	# Hold it, then fade it away over the back half.
	color.a = minf((1.0 - gone) * 2.0, 1.0)

	# Either way it drifts upward: from below it climbs toward the target,
	# from above it climbs away from it.
	var gap := RETICLE_SIZE + RESULT_GAP
	var offset := gap + (1.0 - gone) * RESULT_RISE if below else -gap - gone * RESULT_RISE
	var corner := at + Vector2(-width * 0.5, offset)

	var outline := RESULT_OUTLINE_COLOR
	outline.a = color.a
	draw_string_outline(
		font,
		corner,
		_result,
		HORIZONTAL_ALIGNMENT_LEFT,
		-1.0,
		RESULT_FONT_SIZE,
		RESULT_OUTLINE_WIDTH,
		outline,
	)
	draw_string(font, corner, _result, HORIZONTAL_ALIGNMENT_LEFT, -1.0, RESULT_FONT_SIZE, color)
