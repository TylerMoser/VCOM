## The pause menu's System tab: back to the game, save, load, or quit.
## Save and Load are shown but disabled until there is anything to save.
class_name SystemTab
extends VBoxContainer

## Asks the menu to close; the menu owns the pause, so it does the closing.
signal return_requested

const BUTTON_SIZE := Vector2(320, 52)

const BG_COLOR := Color(0.14, 0.15, 0.2, 0.95)
const HOVER_BG_COLOR := Color(0.18, 0.19, 0.25, 0.95)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)

func _init() -> void:
	name = "System"
	add_theme_constant_override(&"separation", 12)

	var return_button := _add_button("Return to Game")
	return_button.pressed.connect(return_requested.emit)

	var save_button := _add_button("Save")
	save_button.disabled = true
	save_button.tooltip_text = "Not available yet."

	var load_button := _add_button("Load")
	load_button.disabled = true
	load_button.tooltip_text = "Not available yet."

	var exit_button := _add_button("Exit to Desktop")
	exit_button.pressed.connect(_on_exit_pressed)


func _on_exit_pressed() -> void:
	get_tree().quit()


func _add_button(text: String) -> Button:
	var button := Button.new()
	button.text = text
	button.custom_minimum_size = BUTTON_SIZE
	button.size_flags_horizontal = SIZE_SHRINK_CENTER
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.add_theme_font_size_override(&"font_size", 20)
	button.add_theme_stylebox_override(&"normal", _style(BG_COLOR, BORDER_COLOR, 1))
	button.add_theme_stylebox_override(&"hover", _style(HOVER_BG_COLOR, ACCENT_COLOR, 1))
	button.add_theme_stylebox_override(&"pressed", _style(HOVER_BG_COLOR, ACCENT_COLOR, 2))
	button.add_theme_stylebox_override(&"focus", _style(Color.TRANSPARENT, ACCENT_COLOR, 2))
	button.add_theme_stylebox_override(&"disabled", _style(BG_COLOR, BORDER_COLOR, 1))
	button.add_theme_color_override(&"font_disabled_color", Color(0.45, 0.46, 0.5))
	add_child(button)
	return button


static func _style(background: Color, edge: Color, width: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = edge
	style.set_border_width_all(width)
	style.set_corner_radius_all(4)
	return style
