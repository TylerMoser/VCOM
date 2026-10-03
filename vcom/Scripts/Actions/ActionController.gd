## Runs the selected unit's actions: which one is active, the map input it
## receives, and the white marker under the selected unit. Disabled outside
## the player's turn.
##
## The action children are the actions offered on the action bar, to each
## unit those it has ([method UnitAction.is_granted]). The first one is made
## active whenever a unit is selected, so every unit must have it.
##
##   Execute - right-click; e.g. hold to preview a move, release to go.
##   Cancel  - Esc puts the active action away.
##
## With the gamepad it also owns the tile cursor ([TileCursor]), the gamepad's
## pointer on the map, which it shows on the player's turn and puts on whoever
## is selected, and the column of prompts down the right of the screen
## ([ControlHints]) saying what each button does with the action that is up:
##
##   Choose an action - d-pad left / right, through those the unit can take.
##   Execute          - A (confirm_action), at the cursor where it points.
##   Cancel           - B puts the active action away.
##   Cursor           - left stick; L3 puts it back on the unit selected.
class_name ActionController
extends Node

## Emitted whenever the active action, the selection or an action's
## availability may have changed.
signal changed

const SELECTED_LAYER := &"selected"
const SELECTED_COLOR := Color(1.0, 1.0, 1.0)
## Pixels between the gamepad's prompts and the corner of the screen, and
## between them and the ammo indicator under them.
const HINTS_MARGIN := 16.0
const HINTS_GAP := 8.0

@export var squad_path: NodePath = ^"../PlayerSquad"
@export var grid_path: NodePath = ^"../CombatGrid"
@export var highlights_path: NodePath = ^"../TileHighlights"
## Followed by the tile cursor. Optional.
@export var camera_path: NodePath = ^"../CameraRig"
## Where the gamepad's prompts go. Optional.
@export var hud_path: NodePath = ^"../HUD"
## The ammo indicator in the corner, which the prompts stand on. Optional.
@export var ammo_path: NodePath = ^"../HUD/AmmoIndicator"

var squad: PlayerSquad
var grid: CombatGrid
var highlights: TileHighlights
var actions: Array[UnitAction] = []
var active: UnitAction
## The gamepad's pointer on the map.
var cursor: TileCursor
## The gamepad's prompts. Null without a HUD.
var hints: ControlHints
var _ammo: Control
## The unit [member active] was begun for.
var _acting: Unit

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
			# The player's turn: the cursor starts on whoever is selected.
			_put_cursor_on_selected()
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

	cursor = TileCursor.new()
	cursor.name = "TileCursor"
	cursor.grid = grid
	cursor.highlights = highlights
	cursor.camera_rig = get_node_or_null(camera_path) as CameraRig
	cursor.moved.connect(_on_cursor_moved)
	add_child(cursor)
	var hud := get_node_or_null(hud_path)
	if hud != null:
		hints = ControlHints.new()
		hints.name = "ControlHints"
		# Down the right of the screen, growing up and to the left from the
		# corner, clear of the squad panel and the action bar.
		hints.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
		hints.grow_horizontal = Control.GROW_DIRECTION_BEGIN
		hints.grow_vertical = Control.GROW_DIRECTION_BEGIN
		hints.offset_right = -HINTS_MARGIN
		hints.offset_bottom = -HINTS_MARGIN
		hints.offset_left = -HINTS_MARGIN
		hints.offset_top = -HINTS_MARGIN
		hud.add_child(hints)
		_ammo = get_node_or_null(ammo_path) as Control
		if _ammo != null:
			_ammo.visibility_changed.connect(_place_hints)
			_ammo.resized.connect(_place_hints)
		_place_hints()
	changed.connect(_show_hints)
	InputDevice.watch(_on_device_changed)

	if not squad.is_node_ready():
		await squad.ready
	squad.selection_changed.connect(_on_selection_changed)
	_on_selection_changed(squad.selected)


func _unhandled_input(event: InputEvent) -> void:
	if busy or not enabled:
		return
	if event.is_action_pressed(&"next_action") or event.is_action_pressed(&"previous_action"):
		_cycle_action(1 if event.is_action_pressed(&"next_action") else -1)
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed(&"recenter"):
		_put_cursor_on_selected()
		get_viewport().set_input_as_handled()
		return
	if active == null:
		return
	# Left-clicking a squad member selects it; PlayerSquad handles that,
	# unless the action up takes them as its target (an ally, or the one
	# selected itself, for a medkit).
	if event.is_action_pressed(&"select_unit") and event is InputEventMouseButton:
		var clicked := squad.unit_at((event as InputEventMouseButton).position)
		if clicked in squad.members and not active.takes_click_on(clicked):
			return
	# The action sees Esc first, so it can back out of a step in progress,
	# such as a path preview, before Esc puts the whole action away.
	if active.handle_input(event):
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed(&"cancel_action"):
		deactivate()
		get_viewport().set_input_as_handled()


## Makes [param action] the active action for the selected unit, if the unit
## has it and can take it now.
func activate(action: UnitAction) -> void:
	var unit := squad.selected
	if busy or not enabled or unit == null or action == active:
		return
	if not action.is_granted(unit) or not action.is_available(unit):
		return
	if active != null:
		active.end()
	active = action
	_acting = unit
	active.begin(unit)
	changed.emit()


func deactivate() -> void:
	if busy or active == null:
		return
	active.end()
	active = null
	changed.emit()


## The tile the player points at: with the gamepad the tile cursor's, else
## the one under the mouse. Null on no tile. What Move walks to and Throw
## Grenade aims at.
func pointed_tile() -> Variant:
	if InputDevice.gamepad:
		return cursor.current() if cursor != null and cursor.shown else null
	return tile_under_cursor(get_viewport().get_mouse_position())


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
	_update_cursor()
	_put_cursor_on_selected()
	_activate_default()
	changed.emit()


func _on_action_completed() -> void:
	busy = false
	var unit := squad.selected
	var action := active
	action.end()
	active = null
	# Disabled while it played out (it won the battle), it stays put away.
	if enabled:
		if not is_instance_valid(_acting) or unit != _acting:
			# The unit fell to its own action, as a thrower can to its own
			# grenade, and the selection moved on while it played out: whoever
			# has it now starts afresh, as on any change of selection.
			_activate_default()
		elif action.is_available(unit):
			active = action
			action.begin(unit)
	changed.emit()


func _activate_default() -> void:
	if squad.selected != null and not actions.is_empty():
		activate(actions[0])


## Makes the next action the selected unit can take active, [param step] along
## the action bar, wrapping round; from none, the first or the last.
func _cycle_action(step: int) -> void:
	var unit := squad.selected
	if unit == null:
		return
	var offered: Array[UnitAction] = []
	for action in actions:
		if action.is_granted(unit) and action.is_available(unit):
			offered.append(action)
	if offered.is_empty():
		return
	var at := offered.find(active)
	if at < 0:
		at = -1 if step > 0 else 0
	activate(offered[posmod(at + step, offered.size())])


func _put_cursor_on_selected() -> void:
	if cursor != null and squad.selected != null:
		cursor.snap_to(grid.tile_at(squad.selected.global_position), InputDevice.gamepad)


## Shows the cursor while the gamepad is in use on the player's turn, with
## nothing playing out.
func _update_cursor() -> void:
	if cursor == null:
		return
	cursor.shown = InputDevice.gamepad and enabled and not busy and squad.selected != null
	if cursor.shown and cursor.tile == null:
		_put_cursor_on_selected()


func _on_cursor_moved(tile: Vector3i) -> void:
	if active != null and enabled and not busy and InputDevice.gamepad:
		active.cursor_moved(tile)
	_show_hints()


func _on_device_changed(_gamepad: bool) -> void:
	_update_cursor()
	if active != null and enabled and not busy:
		# An action showing what the mouse points at shows the cursor's now,
		# and the other way round: begun again, it starts from the pointer.
		var action := active
		action.end()
		action.begin(_acting)
	_show_hints()


## Fills the gamepad's prompts for what is up now: what A does with the active
## action, B to put it away, and what the rest of the pad does on the
## player's turn. Nothing between turns.
func _show_hints() -> void:
	if hints == null:
		return
	if not enabled or busy or squad.selected == null:
		hints.show_hints([])
		return
	var rows := []
	if active != null:
		rows.append([[&"A"], active.confirm_hint()])
		rows.append([[&"B"], "Put away"])
	rows.append([[&"dpad_horizontal"], "Choose action"])
	if active != null and active.cycles_targets():
		rows.append([[&"LB", &"RB"], "Target"])
		if active.shows_odds():
			rows.append([[&"LT"], "Hold: odds breakdown"])
	else:
		rows.append([[&"LB", &"RB"], "Squad member"])
	rows.append([[&"LS"], "Move cursor"])
	rows.append([[&"L3"], "Cursor to squad member"])
	rows.append([[&"RS"], "Turn and zoom"])
	rows.append([[&"R3"], "Tile grid"])
	rows.append([[&"View"], "Hold: end turn"])
	rows.append([[&"Menu"], "Menu"])
	hints.show_hints(rows)


## Stands the prompts on the ammo indicator while it shows, else in the
## corner: their bottom edge there, and their size grows them up from it.
func _place_hints() -> void:
	if hints == null:
		return
	var bottom := -HINTS_MARGIN
	if _ammo != null and _ammo.visible:
		bottom -= _ammo.size.y + HINTS_GAP
	hints.offset_bottom = bottom
	hints.offset_top = bottom


func _update_lock() -> void:
	squad.locked = busy or not enabled
	_mark_selected_tile()
	_update_cursor()
	_show_hints()


func _mark_selected_tile() -> void:
	var unit := squad.selected
	if unit == null or busy or not enabled:
		highlights.clear_layer(SELECTED_LAYER)
	else:
		highlights.set_layer(SELECTED_LAYER, {grid.tile_at(unit.global_position): SELECTED_COLOR})
