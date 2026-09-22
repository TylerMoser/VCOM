## Bottom-centre row of buttons for the selected unit's actions. Clicking a
## button activates that action, or puts it away if it is already active.
extends HBoxContainer

@export var controller_path: NodePath = ^"../../ActionController"

var _controller: ActionController


func _ready() -> void:
	_controller = get_node_or_null(controller_path) as ActionController
	if _controller == null:
		push_error("ActionBar: no ActionController at '%s'." % controller_path)
		return
	if not _controller.is_node_ready():
		await _controller.ready

	for action in _controller.actions:
		var button := ActionButton.new(action)
		add_child(button)
		button.pressed.connect(_on_button_pressed.bind(action))

	_controller.changed.connect(_refresh)
	_refresh()


func _on_button_pressed(action: UnitAction) -> void:
	if _controller.active == action:
		_controller.deactivate()
	else:
		_controller.activate(action)


func _refresh() -> void:
	var unit := _controller.squad.selected
	for button: ActionButton in get_children():
		button.available = _controller.enabled and unit != null and button.action.is_available(unit)
		button.active = button.action == _controller.active
