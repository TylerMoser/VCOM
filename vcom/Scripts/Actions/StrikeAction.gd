## Strike an enemy standing next to the unit, for one action point, with
## [member Unit.melee_weapon]. Only a unit with a melee weapon equipped has
## it, and it can be taken only while an enemy is next to the unit, next to as
## [method Tactics.is_next_to] has it, so the enemy AI's point-blank range and
## this reach cannot drift apart.
##
## Lined up as a shot is: the targets on offer are the enemies next to the
## unit, nearest first (straight across before diagonal), and the sight line,
## reticle and target panel follow the one lined up.
##
##   Cycle targets - Tab, or Shift+Tab to go back; or click another target.
##   Strike        - Enter or Space, click the target lined up (either
##                   button), or click the tick beside its odds.
##   Show the sum  - hold Ctrl to open the breakdown behind the hit chance.
##
## As with a shot, a click on another target lines it up rather than striking
## it, and the cursor turns to a hand over any target. With the gamepad, as a
## shot is lined up: LB / RB, A, LT, and the tile cursor on the target.
##
## The odds are [method HitChance.for_strike]'s, worked out once when the
## target is lined up, and the blow is [method Unit.strike]'s. While a target
## is lined up the unit squares up to it, its weapon drawn; the blow lands as
## the swing does, with its damage or a miss called over the target, and the
## action is done once the swing is through.
class_name StrikeAction
extends UnitAction

## Action points a strike costs: what a shot does.
const COST := 1

@export var enemy_group := &"enemies"
@export var overlay_path: NodePath = ^"../../HUD/ShotOverlay"

var _unit: Unit
var _targets: Array[Unit] = []
## Index into [member _targets] of the target currently lined up.
var _index := 0
## The odds of the strike lined up, worked out once when it is lined up so the
## number the player is shown is the number that gets rolled.
var _estimate: HitChance.Estimate
var _overlay: ShotOverlay


func _init() -> void:
	display_name = "Strike"
	required_tag = Item.MELEE


func _ready() -> void:
	set_process(false)
	_overlay = get_node_or_null(overlay_path) as ShotOverlay
	if _overlay == null:
		push_error("StrikeAction: no ShotOverlay at '%s'." % overlay_path)
	else:
		_overlay.confirmed.connect(_on_confirmed)


# Every frame, as the camera moves under a still cursor (see ShootAction).
func _process(_delta: float) -> void:
	point_at_target(not controller.busy and _targets.has(hovered_unit()))


func is_available(unit: Unit) -> bool:
	return unit.actions_remaining >= COST and not _adjacent_enemies(unit).is_empty()


func begin(unit: Unit) -> void:
	_unit = unit
	_targets = _adjacent_enemies(unit)
	_index = 0
	_show_target()
	set_process(true)


func end() -> void:
	set_process(false)
	point_at_target(false)
	if _unit != null:
		_unit.stand_easy()
	_unit = null
	_targets.clear()
	_index = 0
	_estimate = null
	if _overlay != null:
		_overlay.clear()


func handle_input(event: InputEvent) -> bool:
	# Tab belongs to the targets for as long as the action is up, as it does
	# while aiming a shot.
	if _targets.is_empty():
		return false
	# Shift+Tab also matches the plain Tab action, so check it first.
	if event.is_action_pressed(&"previous_target"):
		_cycle(-1)
	elif event.is_action_pressed(&"next_target"):
		_cycle(1)
	elif event.is_action_pressed(&"confirm_action"):
		_strike()
	else:
		return _click(clicked_unit(event))
	return true


## The enemy lined up right now, or null while the unit has none next to it.
func current_target() -> Variant:
	return _targets[_index] if not _targets.is_empty() else null


## Makes the strike that is lined up, rolling against the odds the player was
## shown, and calls the result over the target as the blow lands. The action
## is spent either way.
func _strike() -> void:
	var lined_up: Variant = current_target()
	if lined_up == null:
		return
	var target := lined_up as Unit
	var unit := _unit
	var grid := controller.grid
	# Read where to call the result now: a target that dies is gone by then.
	var mark := grid.cell_center(LineOfSight.eye_cell(grid.tile_at(target.global_position)))

	unit.spend_actions(COST)
	if _overlay != null:
		_overlay.clear()
	# Busy while the swing plays out, as a shot is while its round flies: a
	# kill that wins the battle then leaves the action to be put away as it
	# completes, rather than taken out from under it.
	controller.busy = true
	var damage: Variant = await unit.strike(target, _estimate.chance)
	if _overlay != null:
		var hit := damage != null
		_overlay.flash_result(mark, "%d" % damage if hit else "MISS", hit)
	await unit.recover()
	completed.emit()


func _cycle(step: int) -> void:
	_index = posmod(_index + step, _targets.size())
	_show_target()


## Strikes [param clicked] if it is the target lined up, lines it up if it is
## another target, and leaves anything else alone, returning false.
func _click(clicked: Unit) -> bool:
	var at := _targets.find(clicked) if clicked != null else -1
	if at < 0:
		return false
	if at == _index:
		_strike()
	else:
		_index = at
		_show_target()
	return true


func confirm_hint() -> String:
	return "Strike"


func cycles_targets() -> bool:
	return true


## The cursor moved on to [param tile]: an enemy beside the unit there is lined
## up.
func cursor_moved(tile: Vector3i) -> void:
	for at in _targets.size():
		if at != _index and controller.grid.tile_at(_targets[at].global_position) == tile:
			_index = at
			_show_target()
			return


## The tick on the target panel: strike, if this is what is lined up.
func _on_confirmed() -> void:
	if controller.active == self and not controller.busy and current_target() != null:
		_strike()


## The living enemies standing next to [param unit], nearest first.
func _adjacent_enemies(unit: Unit) -> Array[Unit]:
	var grid := controller.grid
	var tile := grid.tile_at(unit.global_position)
	var adjacent: Array[Unit] = []
	for node in get_tree().get_nodes_in_group(enemy_group):
		var enemy := node as Unit
		if enemy == null or enemy.health <= 0:
			continue
		if Tactics.is_next_to(tile, grid.tile_at(enemy.global_position)):
			adjacent.append(enemy)
	var from := unit.global_position
	adjacent.sort_custom(func(a: Unit, b: Unit) -> bool:
		return from.distance_squared_to(a.global_position) < from.distance_squared_to(b.global_position))
	return adjacent


func _show_target() -> void:
	var lined_up: Variant = current_target()
	if lined_up == null:
		return
	var target := lined_up as Unit
	_estimate = HitChance.for_strike(_unit, target)
	_unit.ready_strike(target.global_position)
	if InputDevice.gamepad and controller.cursor != null:
		controller.cursor.snap_to(controller.grid.tile_at(target.global_position))
	if _overlay != null:
		var grid := controller.grid
		_overlay.show_strike(
			grid.cell_center(LineOfSight.eye_cell(grid.tile_at(_unit.global_position))),
			grid.cell_center(LineOfSight.eye_cell(grid.tile_at(target.global_position))),
			target,
			_estimate,
			true,
		)
