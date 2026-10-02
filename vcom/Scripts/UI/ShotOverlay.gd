## The shot being lined up, drawn over the map: the sight line from wherever
## the shooter is firing from, a reticle on the target, and a panel naming it
## and its odds. Once the trigger goes, it draws the round's tracer to wherever
## it stops, marks the spot where a stray round struck terrain, and calls the
## result over the target.
##
## It is all screen space, redrawn every frame from the world positions it was
## handed, so it keeps up with the camera without any 3D nodes to place.
##
## A melee strike is lined up the same way ([method show_strike]) and has its
## result called the same way; it has no round to draw.
##
## So is a grenade throw ([method show_throw]): its arc, cut short with a cross
## where something blocks it, and a bracket on everyone its blast would catch,
## with the damage each would take. A blast can hurt several at once, so its
## results are called together ([method flash_results]).
##
## Gold the squad picks up is called here too ([method flash_pickup]), each
## pickup on its own, so it never replaces a result or another pickup.
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
## Gold picked up, called in the colour the menus show the party's gold in.
const GOLD_COLOR := Color(1.0, 0.9, 0.55)

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

## A throw's arc, drawn as dots this far apart on screen over a faint line, in
## the colour of a clear throw or of a blocked one. A blocked arc ends in a
## cross where it is stopped.
const ARC_DOT_SPACING := 11.0
const ARC_DOT_RADIUS := 2.5
const ARC_LINE_WIDTH := 1.5
const ARC_COLOR := Color(1.0, 0.93, 0.8)
const ARC_BLOCKED_COLOR := Color(1.0, 0.3, 0.25)
const ARC_CROSS_SIZE := 7.0
const ARC_CROSS_WIDTH := 3.0
## The brackets on everyone a throw's blast would catch: the reticle, outlined
## so it shows against a unit its own colour, red on the enemy and the gold of
## the reaction pip on the squad, whom the blast hurts just the same. The
## damage each would take goes under the bracket.
const CAUGHT_ENEMY_COLOR := Color(1.0, 0.3, 0.25)
const CAUGHT_SQUAD_COLOR := Color(1.0, 0.78, 0.2)
const CAUGHT_FONT_SIZE := 16
const CAUGHT_GAP := 4.0

## Eye the shot is taken from, and the eye it is aimed at.
var _from := Vector3.ZERO
var _to := Vector3.ZERO
var _aiming := false
## True while the line is someone shooting at the player rather than the
## player lining a shot up. It gets the line and the result, nothing else.
var _incoming := false

## The results being called, as [code][position, text, colour][/code]: one for
## a shot or a strike, one for everyone a blast caught.
var _results: Array = []
## Whether the results sit under their targets rather than over them. The
## target panel owns the space above a shot the player is taking, and nothing
## owns it when the player is the one being shot at.
var _result_below := true
## Seconds of the results left to show. Zero once they have faded out.
var _result_left := 0.0
## The pickups being called, as [code][position, text, seconds left][/code],
## each fading on its own time.
var _pickups: Array = []

## The throw being lined up: the points its arc runs through, whether it ends
## where something blocks it, and everyone its blast would catch, as
## [code][position, text, friendly][/code].
var _throwing := false
var _arc := PackedVector3Array()
var _arc_blocked := false
var _caught: Array = []

## The rounds of the last shot fired, seconds since they were fired, and how
## many their tracers take to draw in to where the rounds stopped.
var _rounds: Array[Ballistics.Path] = []
## Where the tracers start: the muzzle of the gun that fired them, or null to
## start at the eye each round was fired from.
var _muzzle: Variant = null
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
	for pickup: Array in _pickups:
		pickup[2] -= delta
	_pickups = _pickups.filter(func(pickup: Array) -> bool: return pickup[2] > 0.0)
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
	_panel.bind(shot, estimate)
	_aim(from, to)


## Draws a melee strike lined up on [param target], from the striker's eye
## at [param from] to the target's at [param to], with [param estimate] as its
## odds: the same line, reticle and panel as a shot.
func show_strike(from: Vector3, to: Vector3, target: Unit, estimate: HitChance.Estimate) -> void:
	_panel.bind_strike(target, estimate)
	_aim(from, to)


func _aim(from: Vector3, to: Vector3) -> void:
	_from = from
	_to = to
	_aiming = true
	_incoming = false
	visible = true
	set_process(true)
	queue_redraw()


## Draws a throw being lined up: its arc through [param arc], ending in a
## cross if it is [param blocked] where it stops, and a bracket on each of
## [param caught], [code][position, damage, friendly][/code] for everyone its
## blast would catch, with the damage under it. Replaces any throw drawn
## before; [method clear] puts it away.
func show_throw(arc: PackedVector3Array, blocked: bool, caught: Array) -> void:
	_arc = arc
	_arc_blocked = blocked
	_caught = caught
	_throwing = true
	visible = true
	set_process(true)
	queue_redraw()


## Calls [param text] at the world position [param at], for as long as
## [constant RESULT_SECONDS]. Outlives [method clear], so the result of a
## shot is still readable once the aim has been put away. Replaces whatever
## was being called before.
##
## [param below] puts it under the target, which is where it belongs while
## the target panel holds the space above. Callers decide once rather than
## letting it follow the panel, which would jump as the panel comes and goes.
func flash_result(at: Vector3, text: String, hit: bool, below := true) -> void:
	flash_results([[at, text, hit]], below)


## Calls several results at once, as a blast that caught several units does:
## each of [param results] is [code][position, text, hit][/code], called as
## [method flash_result] calls one. Together they replace whatever was being
## called before.
func flash_results(results: Array, below := true) -> void:
	_results.clear()
	for result: Array in results:
		_results.append([result[0], result[1], HIT_COLOR if result[2] else MISS_COLOR])
	_result_below = below
	_result_left = RESULT_SECONDS
	visible = true
	set_process(true)


## Calls [param text] over the world position [param at], in gold, for as long
## as a result: gold picked up, such as "+1 Gold" over a squad member who has
## taken a coin. Unlike a result it replaces nothing, so a pickup made as a shot
## lands, or several at once, are all called. Outlives [method clear] as a
## result does.
func flash_pickup(at: Vector3, text: String) -> void:
	_pickups.append([at, text, RESULT_SECONDS])
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
## [method Unit.shoot_at] to hold the shot's landing until then. The tracers
## come out of the gun's muzzle where the outcome says where it was, and a
## hit's goes in where it is seen to land on the target
## ([method Ballistics.Path.drawn_to]), not at the eye it flies to.
func show_rounds(outcome: Ballistics.Outcome) -> void:
	_rounds = outcome.paths
	_muzzle = outcome.muzzle
	_round_time = 0.0
	var flight := 0.0
	for path in _rounds:
		flight = maxf(flight, _start_of(path).distance_to(path.drawn_to()) / ROUND_SPEED)
	_rounds_seconds = flight + TRACER_LENGTH / ROUND_SPEED
	visible = true
	set_process(true)
	queue_redraw()

	await get_tree().create_timer(flight, false).timeout
	for path in outcome.paths:
		if path.struck != null:
			_impacts.append([path.to, IMPACT_SECONDS])


func clear() -> void:
	_aiming = false
	_incoming = false
	_throwing = false
	_arc = PackedVector3Array()
	_caught = []
	_panel.visible = false
	if _is_idle():
		visible = false
		set_process(false)
	queue_redraw()


## Whether there is nothing left to draw: no aim or throw up, no tracer still
## drawing in, no mark where a round struck, and no result or pickup showing.
func _is_idle() -> bool:
	return (
		not _aiming
		and not _throwing
		and _result_left <= 0.0
		and _round_time >= _rounds_seconds
		and _impacts.is_empty()
		and _pickups.is_empty()
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

	if _throwing:
		_draw_arc(camera)
		for caught: Array in _caught:
			_draw_caught(camera, caught[0], caught[1], caught[2])

	for path in _rounds:
		_draw_round(camera, path)
	for impact: Array in _impacts:
		_draw_impact(camera, impact[0], impact[1])

	if _result_left > 0.0:
		for result: Array in _results:
			if not camera.is_position_behind(result[0]):
				_draw_result(camera.unproject_position(result[0]), result[1], result[2], _result_below, _result_left)
	for pickup: Array in _pickups:
		if not camera.is_position_behind(pickup[0]):
			_draw_result(camera.unproject_position(pickup[0]), pickup[1], GOLD_COLOR, false, pickup[2])


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
## clear to look at, in [param color], over a dark outline if
## [param outlined].
func _draw_reticle(center: Vector2, color := RETICLE_COLOR, outlined := false) -> void:
	# Each stroke as [colour, width], the outline first so the colour goes over it.
	var strokes := [[RESULT_OUTLINE_COLOR, RETICLE_WIDTH + 2.0]] if outlined else []
	strokes.append([color, RETICLE_WIDTH])
	for stroke: Array in strokes:
		for corner: Vector2 in [Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1), Vector2(1, 1)]:
			var point := center + corner * RETICLE_SIZE
			var arm := corner * RETICLE_ARM
			draw_line(point, point - Vector2(arm.x, 0.0), stroke[0], stroke[1], true)
			draw_line(point, point - Vector2(0.0, arm.y), stroke[0], stroke[1], true)


## The arc of the throw being lined up: a faint line through its points with
## dots spaced evenly along it on screen, however it is foreshortened, and a
## cross where it ends if something blocks it there.
func _draw_arc(camera: Camera3D) -> void:
	var color := ARC_BLOCKED_COLOR if _arc_blocked else ARC_COLOR
	var faint := color
	faint.a *= 0.35
	# Distance along the screen still to go before the next dot.
	var to_dot := 0.0
	for index in _arc.size() - 1:
		if camera.is_position_behind(_arc[index]) or camera.is_position_behind(_arc[index + 1]):
			continue
		var from := camera.unproject_position(_arc[index])
		var to := camera.unproject_position(_arc[index + 1])
		draw_line(from, to, faint, ARC_LINE_WIDTH, true)
		var length := from.distance_to(to)
		var along := to_dot
		while along <= length:
			draw_circle(from.lerp(to, along / length) if length > 0.0 else from, ARC_DOT_RADIUS, color)
			along += ARC_DOT_SPACING
		to_dot = along - length
	if _arc_blocked and not _arc.is_empty() and not camera.is_position_behind(_arc[-1]):
		var stop := camera.unproject_position(_arc[-1])
		for arm: Vector2 in [Vector2(1, 1), Vector2(1, -1)]:
			draw_line(stop - arm * ARC_CROSS_SIZE, stop + arm * ARC_CROSS_SIZE, color, ARC_CROSS_WIDTH, true)


## The bracket on someone a throw's blast would catch, whose eye is at
## [param at]: in red on an enemy and in gold on the squad, [param friendly],
## with [param text], the damage they would take, under it.
func _draw_caught(camera: Camera3D, at: Vector3, text: String, friendly: bool) -> void:
	if camera.is_position_behind(at):
		return
	var center := camera.unproject_position(at)
	var color := CAUGHT_SQUAD_COLOR if friendly else CAUGHT_ENEMY_COLOR
	_draw_reticle(center, color, true)
	var font := get_theme_default_font()
	var width := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, CAUGHT_FONT_SIZE).x
	var corner := center + Vector2(-width * 0.5, RETICLE_SIZE + CAUGHT_GAP + font.get_ascent(CAUGHT_FONT_SIZE))
	draw_string_outline(
		font, corner, text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, CAUGHT_FONT_SIZE, RESULT_OUTLINE_WIDTH, RESULT_OUTLINE_COLOR
	)
	draw_string(font, corner, text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, CAUGHT_FONT_SIZE, color)


## The tracer of the round that flew [param path]: a streak
## [constant TRACER_LENGTH] long behind the round, which draws in to where it
## is drawn landing ([method Ballistics.Path.drawn_to]) once it gets there.
func _draw_round(camera: Camera3D, path: Ballistics.Path) -> void:
	var start := _start_of(path)
	var end := path.drawn_to()
	var length := start.distance_to(end)
	var travelled := _round_time * ROUND_SPEED
	if is_zero_approx(length) or travelled >= length + TRACER_LENGTH:
		return
	var head := start.lerp(end, minf(travelled, length) / length)
	var tail := start.lerp(end, clampf(travelled - TRACER_LENGTH, 0.0, length) / length)
	if camera.is_position_behind(head) or camera.is_position_behind(tail):
		return
	var from := camera.unproject_position(tail)
	var to := camera.unproject_position(head)
	draw_line(from, to, TRACER_GLOW_COLOR, TRACER_GLOW_WIDTH, true)
	draw_line(from, to, TRACER_COLOR, TRACER_WIDTH, true)


## Where [param path]'s tracer starts: the muzzle, if the shot came from a
## gun someone was seen holding, else the eye the round was fired from.
func _start_of(path: Ballistics.Path) -> Vector3:
	return _muzzle if _muzzle != null else path.from


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


## A result, [param text] in [param color] at [param at], drifting up and
## fading as its time runs out, with [param left] seconds of it to go. It is
## outlined because it lands over the map, which is as bright as the text is.
func _draw_result(at: Vector2, text: String, base_color: Color, below: bool, left: float) -> void:
	var gone := 1.0 - left / RESULT_SECONDS
	var font := get_theme_default_font()
	var width := font.get_string_size(
		text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, RESULT_FONT_SIZE
	).x
	var color := base_color
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
		text,
		HORIZONTAL_ALIGNMENT_LEFT,
		-1.0,
		RESULT_FONT_SIZE,
		RESULT_OUTLINE_WIDTH,
		outline,
	)
	draw_string(font, corner, text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, RESULT_FONT_SIZE, color)
