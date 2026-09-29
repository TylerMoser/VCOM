## Alternates the player's turn and the enemies' turn.
##
## The player's turn ends once every squad member has spent all their
## actions, or early by holding Shift for [member end_turn_hold_time]
## seconds. Enemies then act one at a time with the camera on them.
##
## What an enemy does is up to its [member Unit.ai]. The turn manager asks it
## for one [AIAction] at a time and carries each out, charging what the squad
## would pay: an action per [member Unit.move_range] tiles walked, one per
## shot. Enemies walk through [Reactions], which gives squad members on
## overwatch their chance to fire at them on the way, and the camera is
## handed back from any reaction view once each enemy's turn is over.
##
## The battle is decided the moment one side is gone, whoever's turn it is:
## won when the last enemy dies, lost when the last squad member does. The
## turns stop, "Victory" or "Defeat" is announced, and either way the game
## goes back to the world map the battle was started from (see
## [method Campaign.end_battle]). Whoever of the squad still stands earns
## their experience then ([method PlayerSquad.award_survivors]), and a win
## earns the party [member victory_gold]. A battle opened on its own stays open, over.
##
##   End turn - hold Shift. Letting go, or pressing any other key, cancels.
class_name TurnManager
extends Node

enum Side { PLAYER, ENEMY }
enum Outcome { UNDECIDED, WON, LOST }

signal turn_started(side: Side)
## Progress of the end-turn hold, from 0 to 1. 0 also means not holding.
signal end_turn_hold_changed(progress: float)

@export var enemy_group := &"enemies"
@export var end_turn_hold_time := 1.0
## Gold the party earns for winning the battle.
@export var victory_gold := 10

@export_group("Enemy pacing")
@export var seconds_per_enemy_step := 0.2
## Pause after the camera arrives on an enemy and after each of its actions.
@export var enemy_action_pause := 0.35
## How long an enemy's sight line hangs there before its shot goes off, so
## the player can see where the fire is coming from.
@export var enemy_aim_seconds := 0.45

@export_group("Nodes")
@export var squad_path: NodePath = ^"../PlayerSquad"
@export var controller_path: NodePath = ^"../ActionController"
@export var grid_path: NodePath = ^"../CombatGrid"
@export var camera_rig_path: NodePath = ^"../CameraRig"
@export var banner_path: NodePath = ^"../HUD/TurnBanner"
@export var overlay_path: NodePath = ^"../HUD/ShotOverlay"
@export var reactions_path: NodePath = ^"../Reactions"

var side := Side.PLAYER
## How the battle went, once one side is gone. No turn starts or ends after
## it is decided.
var outcome := Outcome.UNDECIDED

var _squad: PlayerSquad
var _controller: ActionController
var _grid: CombatGrid
var _camera_rig: CameraRig
var _banner: TurnBanner
var _reactions: Reactions
var _enemy_fire: ShotPlayback

var _hold := 0.0
## Set when another key is pressed during a hold, so Shift+Tab and the like
## never end the turn. Cleared once Shift is released.
var _hold_spoiled := false


func _ready() -> void:
	_squad = get_node_or_null(squad_path) as PlayerSquad
	_controller = get_node_or_null(controller_path) as ActionController
	_grid = get_node_or_null(grid_path) as CombatGrid
	_camera_rig = get_node_or_null(camera_rig_path) as CameraRig
	_banner = get_node_or_null(banner_path) as TurnBanner
	# The overlay only draws enemy fire, so a scene without one still plays.
	var overlay := get_node_or_null(overlay_path) as ShotOverlay
	if overlay == null:
		push_error("TurnManager: no ShotOverlay at '%s'." % overlay_path)
	# Without reactions, enemies simply walk and the squad cannot answer.
	_reactions = get_node_or_null(reactions_path) as Reactions
	if _reactions == null:
		push_error("TurnManager: no Reactions at '%s'." % reactions_path)
	if _squad == null or _controller == null or _grid == null or _camera_rig == null or _banner == null:
		push_error("TurnManager: missing a node it depends on.")
		set_process(false)
		return

	_enemy_fire = ShotPlayback.new(_grid, overlay)
	_enemy_fire.step_out_seconds = seconds_per_enemy_step
	_enemy_fire.aim_seconds = enemy_aim_seconds

	_controller.changed.connect(_on_controller_changed)
	for node in get_tree().get_nodes_in_group(enemy_group):
		var enemy := node as Unit
		if enemy != null:
			enemy.died.connect(_on_unit_died)
	for member in _squad.members:
		member.died.connect(_on_unit_died)
	# Let the HUD finish setting up before the first banner.
	_start_player_turn.call_deferred(false)


## A battle is on while the turn manager is in the tree, so the pause menu
## holds equipment still (see [member Campaign.in_mission]).
func _enter_tree() -> void:
	Campaign.in_mission = true


func _exit_tree() -> void:
	Campaign.in_mission = false


func _input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key != null and key.pressed and not key.echo and not key.is_action(&"end_turn"):
		if Input.is_action_pressed(&"end_turn"):
			_hold_spoiled = true


func _process(delta: float) -> void:
	if not Input.is_action_pressed(&"end_turn"):
		_hold_spoiled = false
	var holding := (
		side == Side.PLAYER
		and not is_over()
		and Input.is_action_pressed(&"end_turn")
		and not _hold_spoiled
		and not _controller.busy
	)
	_set_hold(_hold + delta if holding else 0.0)
	if _hold >= end_turn_hold_time:
		end_player_turn()


## Ends the player's turn and plays out the enemies' turn.
func end_player_turn() -> void:
	if side != Side.PLAYER or _controller.busy or is_over():
		return
	side = Side.ENEMY
	_set_hold(0.0)
	_controller.enabled = false
	turn_started.emit(side)

	await _banner.announce("Enemy Turn")
	for node in get_tree().get_nodes_in_group(enemy_group):
		var enemy := node as Unit
		if enemy != null:
			await _take_enemy_turn(enemy)
			if _reactions != null:
				_reactions.release_view()
		# A reaction may have finished the last enemy, or a shot the last of
		# the squad.
		if is_over():
			return
	_start_player_turn(true)


func _start_player_turn(focus_camera: bool) -> void:
	side = Side.PLAYER
	for unit in _squad.members:
		unit.start_turn()
	if focus_camera and _squad.selected != null:
		_camera_rig.focus_on(_squad.selected.global_position)
	_controller.enabled = true
	turn_started.emit(side)
	_banner.announce("Player Turn")


## Plays out [param enemy]'s turn: asks its AI what to do with each action
## and carries it out, until it is out of actions, its AI ends the turn, or a
## reaction finishes it.
func _take_enemy_turn(enemy: Unit) -> void:
	enemy.start_turn()
	if enemy.ai == null:
		push_warning("TurnManager: '%s' has no ai, so it sits its turn out." % enemy.name)
		return
	_camera_rig.focus_on(enemy.global_position)
	await get_tree().create_timer(enemy_action_pause, false).timeout

	while enemy.actions_remaining > 0 and not is_over():
		var action := enemy.ai.choose_action(Tactics.new(enemy, _grid, _squad.members))
		if action == null or action.kind == AIAction.Kind.END_TURN:
			return
		if action.kind == AIAction.Kind.MOVE:
			await _move_enemy(enemy, action.path)
			# A reaction on the way may have finished it, and the node with it.
			if not is_instance_valid(enemy) or enemy.health <= 0:
				return
		else:
			enemy.spend_actions(ShootAction.COST)
			await _enemy_fire.play(enemy, action.shot, action.estimate)
		await get_tree().create_timer(enemy_action_pause, false).timeout


## Walks [param enemy] along [param path], through [Reactions] so the squad
## can answer. It pays what the squad would: an action per
## [member Unit.move_range] tiles, and at least one, so an AI that asks for
## nothing still spends the action and the turn always runs out. A path
## longer than the enemy has actions for is cut short.
func _move_enemy(enemy: Unit, path: Array[Vector3i]) -> void:
	var walked := path.slice(0, enemy.actions_remaining * enemy.move_range)
	enemy.spend_actions(maxi(ceili(float(walked.size()) / enemy.move_range), 1))
	if walked.is_empty():
		return

	var points: Array[Vector3] = []
	for tile in walked:
		points.append(_grid.tile_position(tile))
	# Keep the camera with the enemy, unless a reaction view is holding it.
	if not _camera_rig.is_framing():
		_camera_rig.focus_on(points[-1])
	if _reactions != null:
		await _reactions.walk(enemy, points, seconds_per_enemy_step)
	else:
		await enemy.walk(points, seconds_per_enemy_step)


## Whether the battle has been decided, one way or the other.
func is_over() -> bool:
	return outcome != Outcome.UNDECIDED


func _on_unit_died() -> void:
	# A dying unit leaves its groups, and the squad, only after it has said
	# so, so count who is left once it has.
	_end_if_decided.call_deferred()


## Ends the battle once either side is gone: stops the turns, announces how
## it went, then goes back to the world map the battle was started from.
func _end_if_decided() -> void:
	if is_over():
		return
	if get_tree().get_nodes_in_group(enemy_group).is_empty():
		outcome = Outcome.WON
	elif _squad.members.is_empty():
		outcome = Outcome.LOST
	else:
		return
	_squad.award_survivors()
	if outcome == Outcome.WON:
		Campaign.gold += victory_gold
	_set_hold(0.0)
	_controller.enabled = false
	await _banner.announce("Victory" if outcome == Outcome.WON else "Defeat")
	Campaign.end_battle()


func _on_controller_changed() -> void:
	if side != Side.PLAYER or _controller.busy:
		return
	# With nobody left to give orders to, nothing ends the turn either, so
	# the loop stops here rather than spinning through empty turns.
	if _squad.members.is_empty():
		return
	for unit in _squad.members:
		if unit.actions_remaining > 0:
			return
	end_player_turn.call_deferred()


func _set_hold(seconds: float) -> void:
	if is_equal_approx(seconds, _hold):
		return
	_hold = seconds
	end_turn_hold_changed.emit(clampf(_hold / end_turn_hold_time, 0.0, 1.0))
