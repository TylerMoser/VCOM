## One equipment slot along the top of the Roster's Equipment page: the
## slot's name, and what the character has in it or "Empty".
##
## A toggle button in the page's group, so one slot is selected at a time;
## focusing it (arrow keys or a click) selects it too.
class_name SlotButton
extends Button

const WIDTH := 132.0
## Between the button's edge and its captions.
const MARGIN := 8

const BG_COLOR := Color(0.14, 0.15, 0.2, 0.95)
const HOVER_BG_COLOR := Color(0.18, 0.19, 0.25, 0.95)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const TEXT_COLOR := Color(0.85, 0.86, 0.9)
const MUTED_COLOR := Color(0.55, 0.56, 0.62)

## The [Character] property this slot is, from [member Character.slots].
var slot: StringName
## The slot's name, as shown.
var title: String

var _box: VBoxContainer
var _item_label: Label


func _init(for_title: String, for_slot: StringName, group: ButtonGroup) -> void:
	slot = for_slot
	title = for_title
	toggle_mode = true
	button_group = group
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	add_theme_stylebox_override(&"normal", _style(BG_COLOR, BORDER_COLOR, 1))
	add_theme_stylebox_override(&"hover", _style(HOVER_BG_COLOR, BORDER_COLOR, 1))
	add_theme_stylebox_override(&"pressed", _style(HOVER_BG_COLOR, ACCENT_COLOR, 2))
	add_theme_stylebox_override(&"hover_pressed", _style(HOVER_BG_COLOR, ACCENT_COLOR, 2))
	add_theme_stylebox_override(&"focus", StyleBoxEmpty.new())

	# A button does not lay out children, so this box is stretched over it and
	# the button takes its size from the box's (see _fit_box).
	_box = VBoxContainer.new()
	_box.mouse_filter = MOUSE_FILTER_IGNORE
	_box.add_theme_constant_override(&"separation", 2)
	_box.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT, Control.PRESET_MODE_MINSIZE, MARGIN)
	_box.minimum_size_changed.connect(_fit_box)
	add_child(_box)

	var caption := Label.new()
	caption.text = title
	caption.mouse_filter = MOUSE_FILTER_IGNORE
	caption.add_theme_font_size_override(&"font_size", 13)
	caption.add_theme_color_override(&"font_color", MUTED_COLOR)
	_box.add_child(caption)

	_item_label = Label.new()
	_item_label.mouse_filter = MOUSE_FILTER_IGNORE
	_item_label.clip_text = true
	_item_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_item_label.add_theme_font_size_override(&"font_size", 16)
	_box.add_child(_item_label)
	show_item(null)
	_fit_box()

	focus_entered.connect(func() -> void: button_pressed = true)


## Shows [param item] as what is in the slot, or "Empty" for null.
func show_item(item: Item) -> void:
	_item_label.text = item.display_name if item != null else "Empty"
	_item_label.add_theme_color_override(&"font_color", TEXT_COLOR if item != null else MUTED_COLOR)
	tooltip_text = item.display_name if item != null else ""


## Sizes the button round its box, at a fixed width so the slots line up.
## Again whenever the box's size changes, since in _init() the labels have no
## font yet. (A Button's own sizing ignores a script's _get_minimum_size.)
func _fit_box() -> void:
	custom_minimum_size = Vector2(WIDTH, _box.get_combined_minimum_size().y + MARGIN * 2)


static func _style(background: Color, edge: Color, width: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = edge
	style.set_border_width_all(width)
	style.set_corner_radius_all(4)
	return style
