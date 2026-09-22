## Runs the selected unit's actions: which one is active, the map input it
## receives, and the white marker under the selected unit. Disabled outside
## the player's turn.
##
## The action children are the actions offered on the action bar. The first
## one is made active whenever a unit is selected.
##
##   Execute - right-click; e.g. hold to preview a move, release to go.
##   Cancel  - Esc puts the active action away.
class_name ActionController
extends Node

## Emitted whenever the active action, the selection or an action's
## availability may have changed.
signal changed

const SELECTED_LAYER := &"selected"
const SELECTED_COLOR := Color(1.0, 1.0, 1.0)

@export var squad_path: NodePath = ^"../PlayerSquad"
@export var grid_path: NodePath = ^"../CombatGrid"
@export var highlights_path: NodePath = ^"../TileHighlights"

var squad: PlayerSquad
var grid: CombatGrid
var highlights: TileHighlights
var actions: Array[UnitAction] = []
var active: UnitAction

## True while an action plays out. Actions set it when they start executing,
## and it clears when they emit [signal UnitAction.completed]. Selection and
## action input wait until then.
var busy := false:
	set(value):
		busy = value
		_update_lock()

## False while it is not the player's turn: no action is active, and
## selection and action input are ignored. Re-enabling activates the
## default action again.
var enabled := true:
	set(value):
		if enabled == value:
			return
		if not value:
			deactivate()
		enabled = value
		_update_lock()
		if enabled:
			_activate_default()
		changed.emit()


func _ready() -> void:
	squad = get_node_or_null(squad_path) as PlayerSquad
	grid = get_node_or_null(grid_path) as CombatGrid
	highlights = get_node_or_null(highlights_path) as TileHighlights
	if squad == null or grid == null or highlights == null:
		push_error("ActionController: missing PlayerSquad, CombatGrid or TileHighlights.")
		return

	for child in get_children():
		var action := child as UnitAction
		if action != null:
			action.controller = self
			action.completed.connect(_on_action_completed)
			actions.append(action)

	if not squad.is_node_ready():
		await squad.ready
	squad.selection_changed.connect(_on_selection_changed)
	_on_selection_changed(squad.selected)


func _unhandled_input(event: InputEvent) -> void:
	if busy or not enabled or active == null:
		return
	# Left-clicking a squad member selects it; PlayerSquad handles that.
	if event.is_action_pressed(&"select_unit") and event is InputEventMouseButton:
		if squad.unit_at((event as InputEventMouseButton).position) in squad.members:
			return
	# The action sees Esc first, so it can back out of a step in progress,
	# such as a path preview, before Esc puts the whole action away.
	if active.handle_input(event):
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed(&"cancel_action"):
		deactivate()
		get_viewport().set_input_as_handled()


## Makes [param action] the active action for the selected unit, if it is
## available to that unit.
func activate(action: UnitAction) -> void:
	var unit := squad.selected
	if busy or not enabled or unit == null or action == active or not action.is_available(unit):
		return
	if active != null:
		active.end()
	active = action
	active.begin(unit)
	changed.emit()


func deactivate() -> void:
	if busy or active == null:
		return
	active.end()
	active = null
	changed.emit()


## The tile whose floor is under [param screen_position], or null.
func tile_under_cursor(screen_position: Vector2) -> Variant:
	var camera := get_viewport().get_camera_3d()
	if camera == null:
		return null
	return grid.pick_tile(
		camera.project_ray_origin(screen_position), camera.project_ray_normal(screen_position)
	)


func _on_selection_changed(unit: Unit) -> void:
	deactivate()
	_mark_selected_tile()
	_activate_default()
	changed.emit()


func _on_action_completed() -> void:
	busy = false
	var unit := squad.selected
	var action := active
	action.end()
	if action.is_available(unit):
		action.begin(unit)
	else:
		active = null
	changed.emit()


func _activate_default() -> void:
	if squad.selected != null and not actions.is_empty():
		activate(actions[0])


func _update_lock() -> void:
	squad.locked = busy or not enabled
	_mark_selected_tile()


func _mark_selected_tile() -> void:
	var unit := squad.selected
	if unit == null or busy or not enabled:
		highlights.clear_layer(SELECTED_LAYER)
	else:
		highlights.set_layer(SELECTED_LAYER, {grid.tile_at(unit.global_position): SELECTED_COLOR})
