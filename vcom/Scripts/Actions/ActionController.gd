## Runs the selected unit's actions: which one is active, the map input it
## receives, and the white marker under the selected unit.
##
## The action children are the actions offered on the action bar. The first
## one is made active whenever a unit is selected.
##
##   Execute - right-click, e.g. on a highlighted tile to move there.
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
		squad.locked = busy
		_mark_selected_tile()


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
	if busy or active == null:
		return
	if event.is_action_pressed(&"cancel_action"):
		deactivate()
		get_viewport().set_input_as_handled()
		return
	# Clicking a squad member selects it; PlayerSquad handles that.
	if event is InputEventMouseButton:
		if squad.unit_at((event as InputEventMouseButton).position) in squad.members:
			return
	if active.handle_input(event):
		get_viewport().set_input_as_handled()


## Makes [param action] the active action for the selected unit, if it is
## available to that unit.
func activate(action: UnitAction) -> void:
	var unit := squad.selected
	if busy or unit == null or action == active or not action.is_available(unit):
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


## Tiles standing units occupy, except [param except]'s own, as a set.
func occupied_tiles(except: Unit = null) -> Dictionary:
	var tiles := {}
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		if node != except:
			tiles[grid.tile_at((node as Unit).global_position)] = true
	return tiles


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
	if unit != null and not actions.is_empty():
		activate(actions[0])
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


func _mark_selected_tile() -> void:
	var unit := squad.selected
	if unit == null or busy:
		highlights.clear_layer(SELECTED_LAYER)
	else:
		highlights.set_layer(SELECTED_LAYER, {grid.tile_at(unit.global_position): SELECTED_COLOR})
