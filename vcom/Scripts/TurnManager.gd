## Alternates the player's turn and the enemies' turn.
##
## The player's turn ends once every squad member has spent all their
## actions, or early by holding Shift for [member end_turn_hold_time]
## seconds. Enemies then act one at a time with the camera on them. Until
## there is enemy AI, each enemy spends all but its last action stepping to a
## random neighbouring tile, then shoots a squad member it can see with the
## last one, or steps again if it cannot see any.
##
##   End turn - hold Shift. Letting go, or pressing any other key, cancels.
class_name TurnManager
extends Node

enum Side { PLAYER, ENEMY }

signal turn_started(side: Side)
## Progress of the end-turn hold, from 0 to 1. 0 also means not holding.
signal end_turn_hold_changed(progress: float)

@export var enemy_group := &"enemies"
@export var end_turn_hold_time := 1.0

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

var side := Side.PLAYER

var _squad: PlayerSquad
var _controller: ActionController
var _grid: CombatGrid
var _camera_rig: Node3D
var _banner: TurnBanner
var _overlay: ShotOverlay

var _hold := 0.0
## Set when another key is pressed during a hold, so Shift+Tab and the like
## never end the turn. Cleared once Shift is released.
var _hold_spoiled := false


func _ready() -> void:
	_squad = get_node_or_null(squad_path) as PlayerSquad
	_controller = get_node_or_null(controller_path) as ActionController
	_grid = get_node_or_null(grid_path) as CombatGrid
	_camera_rig = get_node_or_null(camera_rig_path) as Node3D
	_banner = get_node_or_null(banner_path) as TurnBanner
	# The overlay only draws enemy fire, so a scene without one still plays.
	_overlay = get_node_or_null(overlay_path) as ShotOverlay
	if _overlay == null:
		push_error("TurnManager: no ShotOverlay at '%s'." % overlay_path)
	if _squad == null or _controller == null or _grid == null or _camera_rig == null or _banner == null:
		push_error("TurnManager: missing a node it depends on.")
		set_process(false)
		return

	_controller.changed.connect(_on_controller_changed)
	# Let the HUD finish setting up before the first banner.
	_start_player_turn.call_deferred(false)


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
		and Input.is_action_pressed(&"end_turn")
		and not _hold_spoiled
		and not _controller.busy
	)
	_set_hold(_hold + delta if holding else 0.0)
	if _hold >= end_turn_hold_time:
		end_player_turn()


## Ends the player's turn and plays out the enemies' turn.
func end_player_turn() -> void:
	if side != Side.PLAYER or _controller.busy:
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


## Placeholder behaviour until there is enemy AI: wander for every action but
## the last, then shoot someone if anyone is in sight.
func _take_enemy_turn(enemy: Unit) -> void:
	enemy.start_turn()
	_camera_rig.focus_on(enemy.global_position)
	await get_tree().create_timer(enemy_action_pause).timeout

	while enemy.actions_remaining > 0:
		enemy.spend_actions(1)
		# Spending first means no actions left is this one being the last.
		var shot: Variant = _random_shot(enemy) if enemy.actions_remaining == 0 else null
		if shot == null:
			await _take_enemy_step(enemy)
		else:
			await _take_enemy_shot(enemy, shot)
		await get_tree().create_timer(enemy_action_pause).timeout


## One step toward a random open neighbouring tile, or a wasted action if
## boxed in.
func _take_enemy_step(enemy: Unit) -> void:
	var blocked := _grid.occupied_tiles(enemy)
	var options := _grid.neighbours(_grid.tile_at(enemy.global_position)).filter(
		func(tile: Vector3i) -> bool: return not blocked.has(tile)
	)
	if options.is_empty():
		return
	var destination: Vector3i = options.pick_random()
	await enemy.walk([_grid.tile_position(destination)], seconds_per_enemy_step)


## A shot at a squad member [param enemy] can see, picked at random, or null
## if it cannot see any of them.
func _random_shot(enemy: Unit) -> Variant:
	if _squad.members.is_empty():
		return null
	var shots := LineOfSight.new(_grid).find_shots(enemy, _squad.members)
	return null if shots.is_empty() else shots.pick_random()


## The enemy takes [param shot]: leans out of cover if the shot needs it,
## holds the sight line long enough to be seen, fires, and settles back.
func _take_enemy_shot(enemy: Unit, shot: LineOfSight.Shot) -> void:
	var cover := enemy.global_position
	var chance := HitChance.for_shot(enemy, shot).chance
	# Read where to call the result now: a target that dies is gone by then.
	var mark := _grid.cell_center(LineOfSight.eye_cell(shot.target_tile))

	if shot.stepped_out:
		await enemy.walk([_grid.tile_position(shot.from)], seconds_per_enemy_step)
	if _overlay != null:
		_overlay.show_incoming(_grid.cell_center(LineOfSight.eye_cell(shot.from)), mark)
		await get_tree().create_timer(enemy_aim_seconds).timeout

	var hit := enemy.shoot_at(shot.target, chance)
	if _overlay != null:
		# Over the target, not under it: no panel is holding that space.
		_overlay.flash_result(mark, "%d" % enemy.weapon.damage if hit else "MISS", hit, false)
		_overlay.clear()

	if shot.stepped_out:
		await enemy.walk([cover], seconds_per_enemy_step)


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
