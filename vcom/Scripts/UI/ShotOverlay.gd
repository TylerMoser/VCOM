## The shot being lined up, drawn over the map: the sight line from wherever
## the shooter is firing from, a reticle on the target, and a panel naming it
## and its odds. Once the trigger goes, it draws the round's tracer to wherever
## it stops, marks the spot where a stray round struck terrain, and calls the
## result over the target.
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

## How fast a round flies, in cells a second, and the length of the streak its
## tracer draws, in cells.
const ROUND_SPEED := 60.0
const TRACER_LENGTH := 2.0
const TRACER_WIDTH := 2.0
const TRACER_COLOR := Color(1.0, 0.95, 0.7)
## A softer, wider streak under the tracer, so it reads against bright ground.
const TRACER_GLOW_WIDTH := 6.0
const TRACER_GLOW_COLOR := Color(1.0, 0.65, 0.25, 0.4)
## The mark where a round struck terrain: how long it stays up, and the flash
## it starts as and the ring that flash spreads into, in pixels.
const IMPACT_SECONDS := 0.5
const IMPACT_FLASH_RADIUS := 5.0
const IMPACT_RADIUS := 16.0
const IMPACT_WIDTH := 2.0
const IMPACT_COLOR := Color(1.0, 0.85, 0.55)

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

## The rounds of the last shot fired, seconds since they were fired, and how
## many their tracers take to draw in to where the rounds stopped.
var _rounds: Array[Ballistics.Path] = []
var _round_time := 0.0
var _rounds_seconds := 0.0
## Marks where rounds struck terrain, as [code][position, seconds left][/code].
var _impacts: Array = []

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
	_round_time += delta
	for impact: Array in _impacts:
		impact[1] -= delta
	_impacts = _impacts.filter(func(impact: Array) -> bool: return impact[1] > 0.0)
	if _is_idle():
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


## Draws each round of [param outcome] flying from where it was fired to where
## it stops, and returns once they have all got there, which is when the shot
## lands. A round that struck terrain leaves a mark where it hit. Pass it to
## [method Unit.shoot_at] to hold the shot's landing until then.
func show_rounds(outcome: Ballistics.Outcome) -> void:
	_rounds = outcome.paths
	_round_time = 0.0
	var flight := 0.0
	for path in _rounds:
		flight = maxf(flight, path.from.distance_to(path.to) / ROUND_SPEED)
	_rounds_seconds = flight + TRACER_LENGTH / ROUND_SPEED
	visible = true
	set_process(true)
	queue_redraw()

	await get_tree().create_timer(flight).timeout
	for path in outcome.paths:
		if path.struck != null:
			_impacts.append([path.to, IMPACT_SECONDS])


func clear() -> void:
	_aiming = false
	_incoming = false
	_panel.visible = false
	if _is_idle():
		visible = false
		set_process(false)


## Whether there is nothing left to draw: no aim up, no tracer still drawing
## in, no mark where a round struck, and no result showing.
func _is_idle() -> bool:
	return (
		not _aiming
		and _result_left <= 0.0
		and _round_time >= _rounds_seconds
		and _impacts.is_empty()
	)


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
			_panel.position = _panel_position(target)
	else:
		_panel.visible = false

	for path in _rounds:
		_draw_round(camera, path)
	for impact: Array in _impacts:
		_draw_impact(camera, impact[0], impact[1])

	if _result_left > 0.0 and not camera.is_position_behind(_result_at):
		_draw_result(camera.unproject_position(_result_at), _result_below)


## Where the target panel goes for a reticle at [param target]: over it, or
## under it when a target near the top of the screen leaves no room above,
## and never off either side.
func _panel_position(target: Vector2) -> Vector2:
	var clearance := RETICLE_SIZE + PANEL_GAP
	var top := target.y - clearance - _panel.size.y
	if top < PANEL_GAP:
		top = target.y + clearance
	var furthest_left := maxf(size.x - _panel.size.x - PANEL_GAP, PANEL_GAP)
	var left := clampf(target.x - _panel.size.x * 0.5, PANEL_GAP, furthest_left)
	return Vector2(left, top)


## Four corner brackets around [param center], leaving the target itself
## clear to look at.
func _draw_reticle(center: Vector2) -> void:
	for corner: Vector2 in [Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1), Vector2(1, 1)]:
		var point := center + corner * RETICLE_SIZE
		var arm := corner * RETICLE_ARM
		draw_line(point, point - Vector2(arm.x, 0.0), RETICLE_COLOR, RETICLE_WIDTH, true)
		draw_line(point, point - Vector2(0.0, arm.y), RETICLE_COLOR, RETICLE_WIDTH, true)


## The tracer of the round that flew [param path]: a streak
## [constant TRACER_LENGTH] long behind the round, which draws in to where the
## round stopped once it gets there.
func _draw_round(camera: Camera3D, path: Ballistics.Path) -> void:
	var length := path.from.distance_to(path.to)
	var travelled := _round_time * ROUND_SPEED
	if is_zero_approx(length) or travelled >= length + TRACER_LENGTH:
		return
	var head := path.from.lerp(path.to, minf(travelled, length) / length)
	var tail := path.from.lerp(path.to, clampf(travelled - TRACER_LENGTH, 0.0, length) / length)
	if camera.is_position_behind(head) or camera.is_position_behind(tail):
		return
	var from := camera.unproject_position(tail)
	var to := camera.unproject_position(head)
	draw_line(from, to, TRACER_GLOW_COLOR, TRACER_GLOW_WIDTH, true)
	draw_line(from, to, TRACER_COLOR, TRACER_WIDTH, true)


## The mark where a round struck terrain at [param at], with [param left]
## seconds to go: a flash that spreads into a ring as it fades.
func _draw_impact(camera: Camera3D, at: Vector3, left: float) -> void:
	if camera.is_position_behind(at):
		return
	var center := camera.unproject_position(at)
	var gone := 1.0 - left / IMPACT_SECONDS
	var color := IMPACT_COLOR
	color.a = 1.0 - gone
	draw_circle(center, lerpf(IMPACT_FLASH_RADIUS, 0.0, gone), color)
	draw_arc(
		center, lerpf(IMPACT_FLASH_RADIUS, IMPACT_RADIUS, gone), 0.0, TAU, 24, color, IMPACT_WIDTH, true
	)


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
