## Walk to a tile. Each action point buys [member Unit.move_range] steps, and
## reachable tiles are tinted by how many points it costs to get there.
##
## Holding right-click previews the path to the tile under the cursor;
## releasing walks it. Releasing off the highlighted tiles, or pressing Esc
## while holding, cancels.
##
## With the gamepad the path to the tile cursor ([TileCursor]) is always
## previewed, following it as the left stick moves it, and A walks it. A with
## the cursor on another squad member selects them instead.
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

## Seconds a step of the walk takes: the pace the run cycle is made for (a
## stride a tile), the same as an enemy's.
@export var seconds_per_step := 0.2

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
	if InputDevice.gamepad:
		_update_preview(controller.pointed_tile())
	elif _previewing:
		_update_preview(controller.tile_under_cursor(get_viewport().get_mouse_position()))
	elif _preview_tile != null:
		_update_preview(null)


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
	set_process(true)


func end() -> void:
	set_process(false)
	_stop_preview()
	controller.highlights.clear_layer(HIGHLIGHT_LAYER)
	_unit = null
	_reach = null


func handle_input(event: InputEvent) -> bool:
	if InputDevice.gamepad and event.is_action_pressed(&"confirm_action"):
		var tile: Variant = controller.pointed_tile()
		var member := _member_on(tile)
		if member != null:
			controller.squad.select(member)
		elif tile != null and _reach.steps.get(tile, 0) > 0:
			_stop_preview()
			_move_to(tile)
		return true
	if event.is_action_pressed(&"execute_action") and event is InputEventMouseButton:
		_previewing = true
		_update_preview(controller.tile_under_cursor((event as InputEventMouseButton).position))
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


func confirm_hint() -> String:
	return "Select" if _member_on(controller.pointed_tile()) != null else "Move here"


## The squad member other than the one moving who stands on [param tile], or
## null.
func _member_on(tile: Variant) -> Unit:
	if tile == null:
		return null
	for member in controller.squad.members:
		if member != _unit and controller.grid.tile_at(member.global_position) == tile:
			return member
	return null


## Shows the path to [param tile], or none when it is null or out of reach.
func _update_preview(tile: Variant) -> void:
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
