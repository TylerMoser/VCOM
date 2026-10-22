## The squad's reactions to an enemy on the move.
##
## Reactions never go off on their own. While an enemy walks where squad
## members on overwatch can see it, a reaction window is open: the walk drops
## to [member slow_motion_scale] of its speed, the camera pulls up to look
## down on the enemy, the rest of its walk and everyone who could fire at it on
## the way, and each of them with a shot now gets a prompt with the odds of it.
## The player picks their moment, or lets it pass:
##
##   Fire     - 1 to 4: the squad member in that place on the squad panel.
##   Continue - 0: the walk carries on at normal speed, no one fires.
##
## With the gamepad one of the prompts is picked out, the first in squad panel
## order to start with:
##
##   Fire     - A: the one picked out.
##   Choose   - LB / RB: pick out the one before or after it.
##   Continue - B.
##
## Firing spends that member's reaction. The enemy is held where it stands
## while the shot plays out, then the walk carries on. Prompts come and go as
## the enemy moves in and out of sight, and the window closes when no one has
## a shot left or the walk ends. Each walk is a new trigger, so letting one go
## by does not let the next go by: the player can hold their fire for a
## better moment.
##
## The view is framed once, as the window opens: who could fire is worked out
## for every tile left of the walk, so the camera need not move again as the
## enemy goes. After that it only ever widens, for someone with a shot it could
## not foresee (cover shot away on the way). Once the window has stayed shut
## [member release_delay] seconds, or the walk is over, the camera goes back to
## following the enemy, or to where it was looking ([method release_view]).
class_name Reactions
extends Node

## The keys that fire, in squad panel order. Squad members past the last one
## cannot react.
const FIRE_ACTIONS: Array[StringName] = [
	&"reaction_1", &"reaction_2", &"reaction_3", &"reaction_4",
]

## How fast an enemy walks while a reaction window is open, as a share of its
## normal speed.
@export_range(0.01, 1.0) var slow_motion_scale := 0.1
## How far below horizontal the camera looks down while a window is open, in
## degrees.
@export var camera_pitch := 62.0
## Seconds the view holds after a window shuts while the walk goes on, so a
## tile out of sight does not send the camera away and straight back.
@export var release_delay := 0.5
## Seconds a squad member takes to lean out of cover to fire, and back.
@export var step_out_seconds := 0.15
## How long a reaction shot's sight line and odds hang before it goes off.
@export var aim_seconds := 0.4

@export_group("Nodes")
@export var squad_path: NodePath = ^"../PlayerSquad"
@export var grid_path: NodePath = ^"../CombatGrid"
@export var camera_rig_path: NodePath = ^"../CameraRig"
@export var overlay_path: NodePath = ^"../HUD/ShotOverlay"
@export var prompts_path: NodePath = ^"../HUD/ReactionPrompts"


## A shot a squad member could take as a reaction, and its odds. The odds are
## worked out once, when the enemy reaches the tile, and they are what the
## prompt shows and what gets rolled.
class Offer:
	var shot: LineOfSight.Shot
	var estimate: HitChance.Estimate

	func _init(offer_shot: LineOfSight.Shot, offer_estimate: HitChance.Estimate) -> void:
		shot = offer_shot
		estimate = offer_estimate


var _squad: PlayerSquad
var _grid: CombatGrid
var _camera_rig: CameraRig
var _prompts: ReactionPrompts
var _shots: ShotPlayback

## The enemy walking, the tween walking it and the points it walks through.
## Null and empty between walks.
var _mover: Unit
var _walk: Tween
var _walk_points: Array[Vector3] = []
## Squad member (Unit) -> [Offer], for everyone who could fire at the mover
## where it stands right now.
var _offers := {}
## The tile the offers were worked out for. Null to work them out again.
var _offers_tile: Variant = null
## Whether the window is open: the walk slowed and the prompts up.
var _open := false
## Squad members the player let go by with 0 during this walk, as a set. The
## window only opens again for someone new coming into sight.
var _passed := {}
## True while a reaction shot plays out.
var _firing := false
## Whether the camera is on the reaction view, and so needs handing back.
var _viewing := false
## Every point the view has framed since the camera took it up, as a set: it is
## framed again only when a point is added, so it only ever widens.
var _framed := {}
## Seconds the window has been shut while the camera still holds the view.
var _shut_for := 0.0
## The squad member whose prompt the gamepad has picked out: A fires them.
var _focus: Unit


func _ready() -> void:
	_squad = get_node_or_null(squad_path) as PlayerSquad
	_grid = get_node_or_null(grid_path) as CombatGrid
	if _squad == null or _grid == null:
		push_error("Reactions: missing PlayerSquad or CombatGrid.")
		set_process_unhandled_input(false)
		return
	# The rest only show the window. Without them the reactions still work.
	_camera_rig = get_node_or_null(camera_rig_path) as CameraRig
	if _camera_rig == null:
		push_error("Reactions: no CameraRig at '%s'." % camera_rig_path)
	_prompts = get_node_or_null(prompts_path) as ReactionPrompts
	if _prompts == null:
		push_error("Reactions: no ReactionPrompts at '%s'." % prompts_path)
	var overlay := get_node_or_null(overlay_path) as ShotOverlay
	if overlay == null:
		push_error("Reactions: no ShotOverlay at '%s'." % overlay_path)

	_shots = ShotPlayback.new(_grid, overlay)
	_shots.step_out_seconds = step_out_seconds
	_shots.aim_seconds = aim_seconds
	_shots.player_fire = true


func _unhandled_input(event: InputEvent) -> void:
	if not _open or _firing:
		return
	if event.is_action_pressed(&"reaction_continue"):
		get_viewport().set_input_as_handled()
		_passed.merge(_offers)
		_set_open(false)
		return
	if event.is_action_pressed(&"reaction_next") or event.is_action_pressed(&"reaction_previous"):
		get_viewport().set_input_as_handled()
		_move_focus(1 if event.is_action_pressed(&"reaction_next") else -1)
		return
	if event.is_action_pressed(&"reaction_fire"):
		get_viewport().set_input_as_handled()
		if _offers.has(_focus):
			_fire(_focus)
		return
	for index in FIRE_ACTIONS.size():
		if event.is_action_pressed(FIRE_ACTIONS[index]):
			get_viewport().set_input_as_handled()
			if index < _squad.members.size() and _offers.has(_squad.members[index]):
				_fire(_squad.members[index])
			return


## Walks [param mover] through [param points], [param seconds_per_step] a
## tile, giving the squad the chance to react on the way. Await it: it returns
## once the walk is over, or once the mover has fallen to a reaction and the
## shot that felled it has played out, with the camera let go. One walk at a
## time, which is how the [TurnManager] moves its enemies.
func walk(mover: Unit, points: Array[Vector3], seconds_per_step: float, vaults := PackedFloat32Array()) -> void:
	var tween := mover.start_walk(points, seconds_per_step, false, vaults)
	if tween == null:
		return
	if _squad == null:
		await tween.finished
		return

	_mover = mover
	_walk = tween
	_walk_points = points
	_offers_tile = null
	_passed.clear()
	# Polled rather than awaited: the tween never finishes if a reaction kills
	# the mover, and a shot in flight has to land before the walk is over.
	while _firing or (is_instance_valid(mover) and mover.health > 0 and tween.is_running()):
		if not _firing:
			_refresh()
			_release_when_shut()
		await get_tree().process_frame

	_set_open(false)
	_offers.clear()
	_mover = null
	_walk = null
	_walk_points = []
	release_view()


## Puts the camera back the way it was, if a reaction window moved it: back to
## following the enemy, or to where it was looking before.
func release_view() -> void:
	_framed.clear()
	_shut_for = 0.0
	if not _viewing:
		return
	_viewing = false
	if _camera_rig != null:
		_camera_rig.release_frame()


## Whether a reaction window is open.
func is_open() -> bool:
	return _open


## Works out the offers again once the mover reaches a new tile, and opens or
## closes the window to match.
func _refresh() -> void:
	var tile := _grid.tile_at(_mover.global_position)
	if tile == _offers_tile:
		return
	_offers_tile = tile
	_offers = _find_offers()

	if _offers.is_empty():
		_set_open(false)
	elif not _open:
		for member: Unit in _offers:
			if not _passed.has(member):
				_set_open(true)
				break
	if _open:
		_show_offers()


## Lets the view go once the window has been shut [member release_delay]
## seconds with the walk still going, which a tile out of sight is not.
func _release_when_shut() -> void:
	if not _viewing or _open:
		_shut_for = 0.0
		return
	_shut_for += get_process_delta_time()
	if _shut_for >= release_delay:
		release_view()


## Everyone who could fire at the mover from where they are, holding their
## reaction for it. They have to see it where it stands: it is on the move,
## not leaning out of anything.
func _find_offers() -> Dictionary:
	var offers := {}
	var line_of_sight := LineOfSight.new(_grid)
	for member in _ready_to_react():
		var shot: Variant = line_of_sight.find_shot(member, _mover, false)
		if shot != null:
			var aimed := shot as LineOfSight.Shot
			offers[member] = Offer.new(aimed, HitChance.for_shot(member, aimed, true))
	return offers


## The squad members who would fire at the mover if they saw it: on overwatch,
## holding their reaction, with a round, and with a key to fire them.
func _ready_to_react() -> Array[Unit]:
	var reacting: Array[Unit] = []
	for index in mini(_squad.members.size(), FIRE_ACTIONS.size()):
		var member := _squad.members[index]
		if member.overwatching and member.reaction_available and member.can_fire():
			reacting.append(member)
	return reacting


## Puts up a prompt for every offer, and frames them and the mover.
func _show_offers() -> void:
	var prompts: Array[ReactionPrompts.Prompt] = []
	var offered := _offered()
	# The one picked out may have died since: a typed array will not take it.
	if not is_instance_valid(_focus) or not offered.has(_focus):
		_focus = offered[0] if not offered.is_empty() else null
	for member: Unit in _offers:
		var key := str(_squad.members.find(member) + 1)
		var offer: Offer = _offers[member]
		var prompt := ReactionPrompts.Prompt.new(member, key, offer.estimate.chance)
		prompt.focused = member == _focus
		prompts.append(prompt)

	if _prompts != null:
		_prompts.show_prompts(prompts)
	_frame_view()


## Frames the mover, the rest of its walk and everyone who could fire at it
## on the way, once, as the camera takes up the view; then frames it again only
## to take in someone with a shot it did not foresee, so it only ever widens.
func _frame_view() -> void:
	if _camera_rig == null:
		return
	var wanted: Array[Vector3] = []
	for member: Unit in _offers:
		wanted.append_array(_body_points(member))
	if not _viewing:
		var rest := _rest_of_walk()
		for point in rest:
			wanted.append_array(CameraRig.standing(point))
		for member in _watchers(rest):
			wanted.append_array(_body_points(member))
	var grew := false
	for point in wanted:
		if not _framed.has(point):
			_framed[point] = true
			grew = true
	if not grew:
		return
	var points: Array[Vector3] = []
	points.assign(_framed.keys())
	_camera_rig.frame(points, camera_pitch)
	_viewing = true


## Where the mover is, and every point of its walk still ahead of it.
func _rest_of_walk() -> Array[Vector3]:
	var rest: Array[Vector3] = [_mover.global_position]
	var tile := _grid.tile_at(_mover.global_position)
	var ahead := 0
	for index in _walk_points.size():
		if _grid.tile_at(_walk_points[index]) == tile:
			ahead = index
			break
	rest.append_array(_walk_points.slice(ahead))
	return rest


## Everyone ready to react who will see the mover on one of [param rest], the
## rest of its walk, where [method _find_offers] will find them a shot.
func _watchers(rest: Array[Vector3]) -> Array[Unit]:
	var line_of_sight := LineOfSight.new(_grid)
	var watchers: Array[Unit] = []
	for member in _ready_to_react():
		for point in rest:
			if line_of_sight.watches(member, _grid.tile_at(point)):
				watchers.append(member)
				break
	return watchers


## Everyone with a shot on offer, in squad panel order: the order the gamepad
## moves its pick through.
func _offered() -> Array[Unit]:
	var offered: Array[Unit] = []
	for member in _squad.members:
		if _offers.has(member):
			offered.append(member)
	return offered


## Picks out the prompt [param step] along from the one picked out, wrapping
## round.
func _move_focus(step: int) -> void:
	var offered := _offered()
	if offered.is_empty():
		return
	var at := offered.find(_focus) if is_instance_valid(_focus) else -1
	_focus = offered[posmod(at + step, offered.size())] if at >= 0 else offered[0]
	_show_offers()


## Opens or closes the window: the walk's speed and the prompts.
func _set_open(open: bool) -> void:
	if _open == open:
		return
	_open = open
	if not open and _prompts != null:
		_prompts.clear()
	_apply_speed()


## Sets the walk's speed for the state the window is in: held still while a
## shot plays out, slowed while the window is open.
func _apply_speed() -> void:
	if _walk == null or not _walk.is_valid():
		return
	if _firing:
		_walk.set_speed_scale(0.0)
	elif _open:
		_walk.set_speed_scale(slow_motion_scale)
	else:
		_walk.set_speed_scale(1.0)


## [param member] takes its offered shot at the mover, with the odds its
## prompt showed. The mover is held still until the shot has played out.
func _fire(member: Unit) -> void:
	var offer: Offer = _offers[member]
	_firing = true
	_apply_speed()
	member.spend_reaction()
	member.overwatching = false
	_offers.erase(member)
	# The prompts are no use while the shot plays out: nothing else can fire.
	if _prompts != null:
		_prompts.clear()

	await _shots.play(member, offer.shot, offer.estimate)

	_firing = false
	# A mover the shot felled is gone: the window closes now, not when the walk
	# next looks, so nothing is fired at it in between.
	if not is_instance_valid(_mover) or _mover.health <= 0:
		_set_open(false)
		_offers.clear()
		return
	# Everything is worked out again from scratch: whoever fired has only just
	# settled back into cover.
	_offers_tile = null
	_apply_speed()


## Points spanning [param unit] from its feet to the top of its head, for
## framing the whole of it.
func _body_points(unit: Unit) -> Array[Vector3]:
	return CameraRig.standing(unit.global_position)
