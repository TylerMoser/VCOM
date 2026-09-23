## Pick an enemy to fire at, for one action point.
##
## The targets on offer are whatever [LineOfSight] says the unit can see, so a
## unit behind high cover leans out around it to find its shot. The tile it
## leans out to is marked on the map, and the sight line, reticle and target
## panel all follow the target.
##
##   Cycle targets - Tab, or Shift+Tab to go back.
##   Fire          - Enter or Space.
##   Show the sum  - hold Ctrl to open the breakdown behind the hit chance.
##
## A shot that needs a step out plays it: the unit leans out to the tile it
## found the shot from, fires, and settles back into its cover. The shot
## itself is instant, and whether it lands is [HitChance]'s business.
class_name ShootAction
extends UnitAction

## Action points a shot costs.
const COST := 1
## Marker on the tile the shooter leans out to, when the shot needs one.
const STEP_OUT_LAYER := &"shoot_step_out"
const STEP_OUT_COLOR := Color(1.0, 0.45, 0.35)

## Seconds the unit takes to lean out of cover, and to settle back in.
@export var step_out_seconds := 0.15
@export var enemy_group := &"enemies"
@export var overlay_path: NodePath = ^"../../HUD/ShotOverlay"

var _unit: Unit
var _shots: Array[LineOfSight.Shot] = []
## Index into [member _shots] of the target currently lined up.
var _index := 0
## The odds of the shot lined up, worked out once when it is lined up so the
## number the player is shown is the number that gets rolled.
var _estimate: HitChance.Estimate
var _overlay: ShotOverlay


func _init() -> void:
	display_name = "Shoot"


func _ready() -> void:
	_overlay = get_node_or_null(overlay_path) as ShotOverlay
	if _overlay == null:
		push_error("ShootAction: no ShotOverlay at '%s'." % overlay_path)


func is_available(unit: Unit) -> bool:
	return unit.actions_remaining >= COST and not _find_shots(unit).is_empty()


func begin(unit: Unit) -> void:
	_unit = unit
	_shots = _find_shots(unit)
	_index = 0
	_show_shot()


func end() -> void:
	_unit = null
	_shots.clear()
	_index = 0
	_estimate = null
	_clear_aim()


func handle_input(event: InputEvent) -> bool:
	# Tab belongs to the targets for as long as the action is up, so it never
	# cycles the squad out from under the player mid-aim.
	if _shots.is_empty():
		return false
	# Shift+Tab also matches the plain Tab action, so check it first.
	if event.is_action_pressed(&"previous_target"):
		_cycle(-1)
	elif event.is_action_pressed(&"next_target"):
		_cycle(1)
	elif event.is_action_pressed(&"confirm_action"):
		_fire()
	else:
		return false
	return true


## The shot lined up right now, or null while the unit has no targets.
func current_shot() -> Variant:
	return _shots[_index] if not _shots.is_empty() else null


## Takes the shot that is lined up: leans out if it needs to, rolls against
## the odds the player was shown, calls the result, and comes back to cover.
## The action is spent either way.
func _fire() -> void:
	var shot: Variant = current_shot()
	if shot == null:
		return
	var aimed := shot as LineOfSight.Shot
	var estimate := _estimate
	var unit := _unit
	var cover := unit.global_position
	# Read where to call the result now: a target that dies is gone by then.
	var mark := controller.grid.cell_center(LineOfSight.eye_cell(aimed.target_tile))

	unit.spend_actions(COST)
	# Drop the aim before anything moves: the target may be about to leave
	# the map, and the sight line is drawn from where the unit was.
	_clear_aim()
	controller.busy = true

	if aimed.stepped_out:
		await unit.walk([controller.grid.tile_position(aimed.from)], step_out_seconds)

	var hit := unit.shoot_at(aimed.target, estimate.chance)
	if _overlay != null:
		_overlay.flash_result(mark, "%d" % unit.weapon.damage if hit else "MISS", hit)

	if aimed.stepped_out:
		await unit.walk([cover], step_out_seconds)
	completed.emit()


func _cycle(step: int) -> void:
	_index = posmod(_index + step, _shots.size())
	_show_shot()


func _find_shots(unit: Unit) -> Array[LineOfSight.Shot]:
	var enemies: Array[Unit] = []
	for node in get_tree().get_nodes_in_group(enemy_group):
		var enemy := node as Unit
		if enemy != null:
			enemies.append(enemy)
	return LineOfSight.new(controller.grid).find_shots(unit, enemies)


func _show_shot() -> void:
	var shot: Variant = current_shot()
	if shot == null:
		return
	var aimed := shot as LineOfSight.Shot
	_estimate = HitChance.for_shot(_unit, aimed)

	if aimed.stepped_out:
		controller.highlights.set_layer(STEP_OUT_LAYER, {aimed.from: STEP_OUT_COLOR})
	else:
		controller.highlights.clear_layer(STEP_OUT_LAYER)

	if _overlay != null:
		var grid := controller.grid
		_overlay.show_shot(
			grid.cell_center(LineOfSight.eye_cell(aimed.from)),
			grid.cell_center(LineOfSight.eye_cell(aimed.target_tile)),
			aimed,
			_estimate,
		)


func _clear_aim() -> void:
	controller.highlights.clear_layer(STEP_OUT_LAYER)
	if _overlay != null:
		_overlay.clear()
