## The pause menu's System tab: back to the game, the tile grid on or off,
## blood on or off, save, load, or quit. Save and Load are shown but disabled
## until there is anything to save.
##
## Blood can only be turned on or off between battles, on the world map: a
## battle keeps the blood it began with ([member Blood.enabled]), so during
## one its button is greyed out, with a note saying where it can be changed.
class_name SystemTab
extends VBoxContainer

## Asks the menu to close; the menu owns the pause, so it does the closing.
signal return_requested

const BUTTON_SIZE := Vector2(320, 52)

const BG_COLOR := Color(0.14, 0.15, 0.2, 0.95)
const HOVER_BG_COLOR := Color(0.18, 0.19, 0.25, 0.95)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const MUTED_COLOR := Color(0.55, 0.56, 0.62)

var _grid_button: Button
var _blood_button: Button
var _blood_note: Label

func _init() -> void:
	name = "System"
	add_theme_constant_override(&"separation", 12)

	var return_button := _add_button("Return to Game")
	return_button.pressed.connect(return_requested.emit)

	_grid_button = _add_button("")
	_grid_button.tooltip_text = "Lines along the edges of the ground's tiles in combat. G toggles them there too."
	_grid_button.pressed.connect(_on_grid_pressed)
	show_grid_state()

	_blood_button = _add_button("")
	_blood_button.tooltip_text = "Wounds, blood spray and pools in combat. Off, battles are fought clean. Only changes on the world map."
	_blood_button.pressed.connect(_on_blood_pressed)
	_blood_note = Label.new()
	_blood_note.text = "Blood can only be changed on the world map."
	_blood_note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_blood_note.add_theme_font_size_override(&"font_size", 15)
	_blood_note.add_theme_color_override(&"font_color", MUTED_COLOR)
	add_child(_blood_note)
	# Not whether a battle is on: the menu is made before Campaign is. It asks
	# as it opens (show_blood_state()).
	_label_blood()
	_blood_note.visible = false

	var save_button := _add_button("Save")
	save_button.disabled = true
	save_button.tooltip_text = "Not available yet."

	var load_button := _add_button("Load")
	load_button.disabled = true
	load_button.tooltip_text = "Not available yet."

	var exit_button := _add_button("Exit to Desktop")
	exit_button.pressed.connect(_on_exit_pressed)


## Labels the grid's button with whether the grid is on. The menu calls it as
## it opens, since G may have changed it in the meantime.
func show_grid_state() -> void:
	_grid_button.text = "Tile Grid: %s" % ("On" if TileGrid.shown else "Off")


## Labels the blood's button with whether there is blood, and greys it out,
## with its note showing, while a battle is on. The menu calls it as it opens.
func show_blood_state() -> void:
	var locked := Campaign.in_mission
	_label_blood()
	_blood_button.disabled = locked
	_blood_note.visible = locked


func _label_blood() -> void:
	_blood_button.text = "Blood: %s" % ("On" if Blood.enabled else "Off")


func _on_grid_pressed() -> void:
	TileGrid.toggle()
	show_grid_state()


func _on_blood_pressed() -> void:
	# The button is greyed out in battle; this is only belt and braces.
	if Campaign.in_mission:
		return
	Blood.enabled = not Blood.enabled
	show_blood_state()


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
