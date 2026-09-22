## Walk to a tile. Each action point buys [member Unit.move_range] steps, and
## reachable tiles are tinted by how many points it costs to get there.
##
## Holding right-click previews the path to the tile under the cursor;
## releasing walks it. Releasing off the highlighted tiles, or pressing Esc
## while holding, cancels.
class_name MoveAction
extends UnitAction

## Tint for tiles costing 1, 2 and 3 action points.
const COST_COLORS: Array[Color] = [
	Color(0.25, 0.55, 1.0),
	Color(1.0, 0.88, 0.2),
	Color(1.0, 0.5, 0.1),
]
const HIGHLIGHT_LAYER := &"move"
const PATH_LAYER := &"move_path"
## Path tiles are filled almost solid so they stand out from the range.
const PATH_FILL := 0.9

@export var seconds_per_step := 0.12

var _unit: Unit
var _reach: CombatGrid.Reach
var _previewing := false
## Destination of the path being previewed, or null if the cursor is not on a
## reachable tile.
var _preview_tile: Variant = null


func _ready() -> void:
	set_process(false)


# Follow the cursor every frame, not only when the mouse moves, so the path
# stays right while the camera pans or rotates under a still cursor.
func _process(_delta: float) -> void:
	_update_preview(get_viewport().get_mouse_position())


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
		grid.occupied_tiles(unit),
	)

	var tiles := {}
	for tile: Vector3i in _reach.steps:
		if _reach.steps[tile] > 0:
			tiles[tile] = _cost_color(_reach.steps[tile])
	controller.highlights.set_layer(HIGHLIGHT_LAYER, tiles)


func end() -> void:
	_stop_preview()
	controller.highlights.clear_layer(HIGHLIGHT_LAYER)
	_unit = null
	_reach = null


func handle_input(event: InputEvent) -> bool:
	if event.is_action_pressed(&"execute_action") and event is InputEventMouseButton:
		_previewing = true
		set_process(true)
		_update_preview((event as InputEventMouseButton).position)
		return true
	if not _previewing:
		return false

	if event.is_action_released(&"execute_action"):
		var tile: Variant = _preview_tile
		_stop_preview()
		if tile != null:
			_move_to(tile)
		return true
	if event.is_action_pressed(&"cancel_action"):
		_stop_preview()
		return true
	return false


func _update_preview(screen_position: Vector2) -> void:
	var tile: Variant = controller.tile_under_cursor(screen_position)
	if tile != null and _reach.steps.get(tile, 0) == 0:
		tile = null
	if tile == _preview_tile:
		return
	_preview_tile = tile

	if tile == null:
		controller.highlights.clear_layer(PATH_LAYER)
		return
	var tiles := {}
	for step in _reach.path_to(tile):
		tiles[step] = _cost_color(_reach.steps[step])
	controller.highlights.set_layer(PATH_LAYER, tiles, PATH_FILL)


func _stop_preview() -> void:
	_previewing = false
	_preview_tile = null
	set_process(false)
	controller.highlights.clear_layer(PATH_LAYER)


func _move_to(tile: Vector3i) -> void:
	var unit := _unit
	var points: Array[Vector3] = []
	for step in _reach.path_to(tile):
		points.append(controller.grid.tile_position(step))
	unit.spend_actions(_cost(_reach.steps[tile]))
	controller.highlights.clear_layer(HIGHLIGHT_LAYER)
	controller.busy = true

	await unit.walk(points, seconds_per_step)
	completed.emit()


## Action points needed to walk [param steps] tiles.
func _cost(steps: int) -> int:
	return ceili(float(steps) / _unit.move_range)


func _cost_color(steps: int) -> Color:
	return COST_COLORS[clampi(_cost(steps), 1, COST_COLORS.size()) - 1]
