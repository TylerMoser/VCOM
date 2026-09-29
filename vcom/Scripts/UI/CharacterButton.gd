## One character in the Roster tab's strip: their portrait, or a square of
## their colour while they have none, with their name underneath.
##
## A toggle button in the strip's group, so one character is selected at a
## time; focusing it (arrow keys or a click) selects it too.
class_name CharacterButton
extends Button

const PORTRAIT_SIZE := Vector2(52, 52)
## Between the button's edge and the portrait and name.
const MARGIN := 6

const HOVER_BG_COLOR := Color(0.18, 0.19, 0.25, 0.95)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const TEXT_COLOR := Color(0.85, 0.86, 0.9)

var character: Character

var _box: VBoxContainer
var _name_label: Label


func _init(for_character: Character, group: ButtonGroup) -> void:
	character = for_character
	toggle_mode = true
	button_group = group
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	tooltip_text = character.display_name
	add_theme_stylebox_override(&"normal", _style(Color.TRANSPARENT, Color.TRANSPARENT))
	add_theme_stylebox_override(&"hover", _style(HOVER_BG_COLOR, Color.TRANSPARENT))
	add_theme_stylebox_override(&"pressed", _style(HOVER_BG_COLOR, ACCENT_COLOR))
	add_theme_stylebox_override(&"hover_pressed", _style(HOVER_BG_COLOR, ACCENT_COLOR))
	add_theme_stylebox_override(&"focus", StyleBoxEmpty.new())

	# A button does not lay out children, so this box is stretched over it and
	# the button takes its size from the box's (see _fit_box).
	_box = VBoxContainer.new()
	_box.mouse_filter = MOUSE_FILTER_IGNORE
	_box.add_theme_constant_override(&"separation", 4)
	_box.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT, Control.PRESET_MODE_MINSIZE, MARGIN)
	_box.minimum_size_changed.connect(_fit_box)
	add_child(_box)

	var portrait: Control
	if character.portrait != null:
		var picture := TextureRect.new()
		picture.texture = character.portrait
		picture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		picture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		portrait = picture
	else:
		var swatch := ColorRect.new()
		swatch.color = character.color
		portrait = swatch
	portrait.custom_minimum_size = PORTRAIT_SIZE
	portrait.size_flags_horizontal = SIZE_SHRINK_CENTER
	portrait.mouse_filter = MOUSE_FILTER_IGNORE
	_box.add_child(portrait)

	_name_label = Label.new()
	_name_label.text = character.display_name
	_name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name_label.add_theme_font_size_override(&"font_size", 14)
	_name_label.mouse_filter = MOUSE_FILTER_IGNORE
	_box.add_child(_name_label)
	_fit_box()

	_on_toggled(false)
	toggled.connect(_on_toggled)
	focus_entered.connect(func() -> void: button_pressed = true)


## Sizes the button round its box. Again whenever the box's size changes,
## since in _init() the name has no font yet, and so no size. (A Button's own
## sizing ignores a script's _get_minimum_size.)
func _fit_box() -> void:
	custom_minimum_size = _box.get_combined_minimum_size() + Vector2(MARGIN, MARGIN) * 2


func _on_toggled(on: bool) -> void:
	_name_label.add_theme_color_override(&"font_color", ACCENT_COLOR if on else TEXT_COLOR)


static func _style(background: Color, edge: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = edge
	style.set_border_width_all(2)
	style.set_corner_radius_all(4)
	return style
