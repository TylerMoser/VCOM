## Walk to a tile. Each action point buys [member Unit.move_range] steps, and
## reachable tiles are tinted by how many points it costs to get there.
class_name MoveAction
extends UnitAction

## Tint for tiles costing 1, 2 and 3 action points.
const COST_COLORS: Array[Color] = [
	Color(0.25, 0.55, 1.0),
	Color(1.0, 0.88, 0.2),
	Color(1.0, 0.5, 0.1),
]
const HIGHLIGHT_LAYER := &"move"

@export var seconds_per_step := 0.12

var _unit: Unit
var _reach: CombatGrid.Reach


func _init() -> void:
	display_name = "Move"


func is_available(unit: Unit) -> bool:
	return unit.actions_remaining > 0


func begin(unit: Unit) -> void:
	_unit = unit
	var grid := controller.grid
	_reach = grid.find_reachable(
		grid.tile_at(unit.global_position),
		unit.move_range * unit.actions_remaining,
		controller.occupied_tiles(unit),
	)

	var tiles := {}
	for tile: Vector3i in _reach.steps:
		var cost := _cost(_reach.steps[tile])
		if cost > 0:
			tiles[tile] = COST_COLORS[mini(cost, COST_COLORS.size()) - 1]
	controller.highlights.set_layer(HIGHLIGHT_LAYER, tiles)


func end() -> void:
	controller.highlights.clear_layer(HIGHLIGHT_LAYER)
	_unit = null
	_reach = null


func handle_input(event: InputEvent) -> bool:
	if not event.is_action_pressed(&"execute_action") or event is not InputEventMouseButton:
		return false
	var tile: Variant = controller.tile_under_cursor((event as InputEventMouseButton).position)
	if tile == null or _reach.steps.get(tile, 0) == 0:
		return false
	_move_to(tile)
	return true


func _move_to(tile: Vector3i) -> void:
	var unit := _unit
	var path := _reach.path_to(tile)
	unit.spend_actions(_cost(_reach.steps[tile]))
	controller.highlights.clear_layer(HIGHLIGHT_LAYER)
	controller.busy = true

	var tween := unit.create_tween()
	for step in path:
		tween.tween_property(unit, ^"global_position", controller.grid.tile_position(step), seconds_per_step)
	await tween.finished
	completed.emit()


## Action points needed to walk [param steps] tiles.
func _cost(steps: int) -> int:
	return ceili(float(steps) / _unit.move_range)
