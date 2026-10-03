## The squad's reactions to an enemy on the move.
##
## Reactions never go off on their own. While an enemy walks where squad
## members on overwatch can see it, a reaction window is open: the walk drops
## to [member slow_motion_scale] of its speed, the camera pulls up to look
## down on everyone who could fire and the enemy they would fire at, and each
## of them gets a prompt with the odds of their shot. The player picks their
## moment, or lets it pass:
##
##   Fire     - 1 to 4: the squad member in that place on the squad panel.
##   Continue - 0: the walk carries on at normal speed, no one fires.
##
## Firing spends that member's reaction. The enemy is held where it stands
## while the shot plays out, then the walk carries on. Prompts come and go as
## the enemy moves in and out of sight, and the window closes when no one has
## a shot left or the walk ends. Each walk is a new trigger, so letting one go
## by does not let the next go by: the player can hold their fire for a
## better moment.
##
## The camera stays on the reaction view between an enemy's moves, until the
## [TurnManager] calls [method release_view] at the end of that enemy's turn.
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

## The enemy walking, and the tween walking it. Null between walks.
var _mover: Unit
var _walk: Tween
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
	for index in FIRE_ACTIONS.size():
		if event.is_action_pressed(FIRE_ACTIONS[index]):
			get_viewport().set_input_as_handled()
			if index < _squad.members.size() and _offers.has(_squad.members[index]):
				_fire(_squad.members[index])
			return


## Walks [param mover] through [param points], [param seconds_per_step] a
## tile, giving the squad the chance to react on the way. Await it: it returns
## once the walk is over, or once the mover has fallen to a reaction and the
## shot that felled it has played out. One walk at a time, which is how the
## [TurnManager] moves its enemies.
func walk(mover: Unit, points: Array[Vector3], seconds_per_step: float) -> void:
	var tween := mover.start_walk(points, seconds_per_step)
	if tween == null:
		return
	if _squad == null:
		await tween.finished
		return

	_mover = mover
	_walk = tween
	_offers_tile = null
	_passed.clear()
	# Polled rather than awaited: the tween never finishes if a reaction kills
	# the mover, and a shot in flight has to land before the walk is over.
	while _firing or (is_instance_valid(mover) and mover.health > 0 and tween.is_running()):
		if not _firing:
			_refresh()
		await get_tree().process_frame

	_set_open(false)
	_offers.clear()
	_mover = null
	_walk = null


## Puts the camera back the way it was, if a reaction window moved it.
func release_view() -> void:
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


## Everyone who could fire at the mover from where they are, holding their
## reaction for it. They have to see it where it stands: it is on the move,
## not leaning out of anything.
func _find_offers() -> Dictionary:
	var offers := {}
	var line_of_sight := LineOfSight.new(_grid)
	for index in mini(_squad.members.size(), FIRE_ACTIONS.size()):
		var member := _squad.members[index]
		if not member.overwatching or not member.reaction_available:
			continue
		var shot: Variant = line_of_sight.find_shot(member, _mover, false)
		if shot != null:
			var aimed := shot as LineOfSight.Shot
			offers[member] = Offer.new(aimed, HitChance.for_shot(member, aimed, true))
	return offers


## Puts up a prompt for every offer, and frames them and the mover.
func _show_offers() -> void:
	var prompts: Array[ReactionPrompts.Prompt] = []
	var framed: Array[Vector3] = []
	for member: Unit in _offers:
		var key := str(_squad.members.find(member) + 1)
		var offer: Offer = _offers[member]
		prompts.append(ReactionPrompts.Prompt.new(member, key, offer.estimate.chance))
		framed.append_array(_body_points(member))
	framed.append_array(_body_points(_mover))

	if _prompts != null:
		_prompts.show_prompts(prompts)
	if _camera_rig != null:
		_camera_rig.frame(framed, camera_pitch)
		_viewing = true


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
	# Everything is worked out again from scratch: the mover may be down, and
	# whoever fired has only just settled back into cover.
	_offers_tile = null
	_apply_speed()


## Points spanning [param unit] from its feet to the top of its head, for
## framing the whole of it.
func _body_points(unit: Unit) -> Array[Vector3]:
	var feet := unit.global_position
	return [feet, feet + Vector3.UP * CombatGrid.UNIT_HEIGHT]
