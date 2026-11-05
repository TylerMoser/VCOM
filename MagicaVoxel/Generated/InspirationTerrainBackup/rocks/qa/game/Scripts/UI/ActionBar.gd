## Bottom-centre row of buttons for the selected unit's actions. Clicking a
## button activates that action, or puts it away if it is already active.
## An action the unit does not have, for want of an item, has no button; one
## it cannot take right now is dimmed. With the gamepad the d-pad's left and
## right are drawn at its ends, the buttons that move along it.
extends HBoxContainer

@export var controller_path: NodePath = ^"../../ActionController"

var _controller: ActionController
var _left: ButtonGlyph
var _right: ButtonGlyph


func _ready() -> void:
	_controller = get_node_or_null(controller_path) as ActionController
	if _controller == null:
		push_error("ActionBar: no ActionController at '%s'." % controller_path)
		return
	if not _controller.is_node_ready():
		await _controller.ready

	_left = ButtonGlyph.new(&"dpad_left")
	_left.size_flags_vertical = SIZE_SHRINK_CENTER
	add_child(_left)
	for action in _controller.actions:
		var button := ActionButton.new(action)
		add_child(button)
		button.pressed.connect(_on_button_pressed.bind(action))
	_right = ButtonGlyph.new(&"dpad_right")
	_right.size_flags_vertical = SIZE_SHRINK_CENTER
	add_child(_right)

	_controller.changed.connect(_refresh)
	InputDevice.watch(_on_device_changed)
	_refresh()


func _on_button_pressed(action: UnitAction) -> void:
	if _controller.active == action:
		_controller.deactivate()
	else:
		_controller.activate(action)


func _on_device_changed(_gamepad: bool) -> void:
	_refresh()


func _refresh() -> void:
	var unit := _controller.squad.selected
	_left.visible = InputDevice.gamepad and unit != null and _controller.enabled
	_right.visible = _left.visible
	for child in get_children():
		var button := child as ActionButton
		if button == null:
			continue
		button.visible = unit == null or button.action.is_granted(unit)
		button.available = _controller.enabled and unit != null and button.action.is_available(unit)
		button.active = button.action == _controller.active
		button.uses = button.action.uses_left(unit) if unit != null and button.visible else -1
