## Pick an enemy to fire at, for one action point.
##
## The targets on offer are whatever [LineOfSight] says the unit can see, so a
## unit behind high cover leans out around it to find its shot. The tile it
## leans out to is marked on the map, and the sight line, reticle and target
## panel all follow the target.
##
##   Cycle targets - Tab, or Shift+Tab to go back.
##
## Pulling the trigger is not wired up yet: this is the targeting interface
## only, and for now every shot is meant to hit.
class_name ShootAction
extends UnitAction

## Action points a shot costs.
const COST := 1
## Marker on the tile the shooter leans out to, when the shot needs one.
const STEP_OUT_LAYER := &"shoot_step_out"
const STEP_OUT_COLOR := Color(1.0, 0.45, 0.35)

@export var enemy_group := &"enemies"
@export var overlay_path: NodePath = ^"../../HUD/ShotOverlay"

var _unit: Unit
var _shots: Array[LineOfSight.Shot] = []
## Index into [member _shots] of the target currently lined up.
var _index := 0
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
	controller.highlights.clear_layer(STEP_OUT_LAYER)
	if _overlay != null:
		_overlay.clear()


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
	else:
		return false
	return true


## The shot lined up right now, or null while the unit has no targets.
func current_shot() -> Variant:
	return _shots[_index] if not _shots.is_empty() else null


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
		)
