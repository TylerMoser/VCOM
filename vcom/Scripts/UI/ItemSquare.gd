## One square in an [ItemBrowser]'s grid: the item's icon, or its name while
## it has none, and a count in the corner once there is more than one.
##
## A toggle button in the browser's group, so one square is selected at a
## time; focusing a square (arrow keys or a click) selects it too, so the
## description follows the keyboard.
class_name ItemSquare
extends Button

const SIZE := Vector2(96, 96)

const BG_COLOR := Color(0.14, 0.15, 0.2, 0.95)
const HOVER_BG_COLOR := Color(0.18, 0.19, 0.25, 0.95)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const TEXT_COLOR := Color(0.85, 0.86, 0.9)
const BADGE_COLOR := Color(0.06, 0.07, 0.1, 0.9)

var stack: ItemStack


func _init(for_stack: ItemStack, group: ButtonGroup) -> void:
	stack = for_stack
	toggle_mode = true
	button_group = group
	custom_minimum_size = SIZE
	clip_text = true
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	tooltip_text = stack.item.display_name

	if stack.item.icon != null:
		icon = stack.item.icon
		expand_icon = true
		icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	else:
		text = stack.item.display_name
		autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_theme_font_size_override(&"font_size", 15)
	add_theme_color_override(&"font_color", TEXT_COLOR)
	add_theme_color_override(&"font_hover_color", Color.WHITE)
	add_theme_color_override(&"font_pressed_color", ACCENT_COLOR)
	add_theme_color_override(&"font_hover_pressed_color", ACCENT_COLOR)
	add_theme_color_override(&"font_focus_color", ACCENT_COLOR)
	add_theme_stylebox_override(&"normal", _style(BG_COLOR, BORDER_COLOR, 1))
	add_theme_stylebox_override(&"hover", _style(HOVER_BG_COLOR, BORDER_COLOR, 1))
	add_theme_stylebox_override(&"pressed", _style(HOVER_BG_COLOR, ACCENT_COLOR, 2))
	add_theme_stylebox_override(&"hover_pressed", _style(HOVER_BG_COLOR, ACCENT_COLOR, 2))
	add_theme_stylebox_override(&"focus", StyleBoxEmpty.new())

	if stack.count > 1:
		add_child(_badge(stack.count))

	focus_entered.connect(func() -> void: button_pressed = true)


## The count, in a dark tab in the bottom-right corner.
static func _badge(count: int) -> Label:
	var badge := Label.new()
	badge.text = str(count)
	badge.mouse_filter = MOUSE_FILTER_IGNORE
	badge.add_theme_font_size_override(&"font_size", 14)
	badge.add_theme_color_override(&"font_color", TEXT_COLOR)
	var style := StyleBoxFlat.new()
	style.bg_color = BADGE_COLOR
	style.set_corner_radius_all(3)
	style.content_margin_left = 6
	style.content_margin_right = 6
	badge.add_theme_stylebox_override(&"normal", style)
	badge.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT, Control.PRESET_MODE_MINSIZE, 4)
	badge.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	badge.grow_vertical = Control.GROW_DIRECTION_BEGIN
	return badge


static func _style(background: Color, edge: Color, width: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = edge
	style.set_border_width_all(width)
	style.set_corner_radius_all(4)
	style.set_content_margin_all(6)
	return style
