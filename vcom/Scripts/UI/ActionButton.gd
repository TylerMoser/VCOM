## Square action bar button. Highlighted while its action is active, dimmed
## while the selected unit cannot use it.
class_name ActionButton
extends PanelContainer

signal pressed

const BUTTON_SIZE := Vector2(64, 64)

const BG_COLOR := Color(0.1, 0.11, 0.15, 0.85)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACTIVE_BG_COLOR := Color(0.18, 0.19, 0.25, 0.95)
const ACTIVE_BORDER_COLOR := Color(1.0, 0.9, 0.55)

var action: UnitAction

var active := false:
	set(value):
		active = value
		_update_style()

var available := true:
	set(value):
		available = value
		_update_style()

var _style: StyleBoxFlat


func _init(for_action: UnitAction = null) -> void:
	action = for_action
	custom_minimum_size = BUTTON_SIZE
	mouse_default_cursor_shape = CURSOR_POINTING_HAND

	_style = StyleBoxFlat.new()
	_style.set_corner_radius_all(4)
	_style.set_content_margin_all(4)
	add_theme_stylebox_override(&"panel", _style)
	_update_style()

	# Placeholder until actions have icons.
	var label := Label.new()
	label.text = action.display_name if action != null else ""
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.mouse_filter = MOUSE_FILTER_IGNORE
	add_child(label)


func _gui_input(event: InputEvent) -> void:
	var button := event as InputEventMouseButton
	if button != null and button.button_index == MOUSE_BUTTON_LEFT and button.pressed:
		accept_event()
		if available:
			pressed.emit()


func _update_style() -> void:
	_style.bg_color = ACTIVE_BG_COLOR if active else BG_COLOR
	_style.border_color = ACTIVE_BORDER_COLOR if active else BORDER_COLOR
	_style.set_border_width_all(2 if active else 1)
	modulate.a = 1.0 if available else 0.4
	mouse_default_cursor_shape = CURSOR_POINTING_HAND if available else CURSOR_ARROW
