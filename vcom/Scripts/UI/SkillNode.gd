## One ability in a skill tree on the Roster's Skills page, styled by whether
## the character has learned it, can learn it next, or has yet to reach it.
##
## A toggle button in the page's group, so one node is selected at a time,
## marked by a ring round it; focusing it (arrow keys or a click) selects it
## too. Selecting only highlights for now.
class_name SkillNode
extends Button

enum State { LOCKED, AVAILABLE, LEARNED }

const SIZE := Vector2(44, 44)
## How far outside the node the selection ring is drawn.
const RING_GAP := 4.0

const BG_COLOR := Color(0.14, 0.15, 0.2, 0.95)
const LOCKED_BG_COLOR := Color(0.09, 0.1, 0.13, 0.95)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const MUTED_COLOR := Color(0.45, 0.46, 0.5)
const DARK_TEXT_COLOR := Color(0.1, 0.11, 0.15)
const RING_COLOR := Color(0.95, 0.95, 0.97)

var state := State.LOCKED


func _init(number: int, node_state: State, group: ButtonGroup) -> void:
	state = node_state
	text = str(number)
	toggle_mode = true
	button_group = group
	custom_minimum_size = SIZE
	size_flags_horizontal = SIZE_SHRINK_CENTER
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	add_theme_font_size_override(&"font_size", 17)

	var background: Color = {State.LOCKED: LOCKED_BG_COLOR, State.AVAILABLE: BG_COLOR, State.LEARNED: ACCENT_COLOR}[state]
	var edge: Color = {State.LOCKED: BORDER_COLOR, State.AVAILABLE: ACCENT_COLOR, State.LEARNED: ACCENT_COLOR}[state]
	var font: Color = {State.LOCKED: MUTED_COLOR, State.AVAILABLE: ACCENT_COLOR, State.LEARNED: DARK_TEXT_COLOR}[state]
	var style := _style(background, edge)
	var hover := _style(background.lightened(0.08), edge)
	# The ring shows selection, so pressed looks like the state itself.
	for slot in [&"normal", &"pressed", &"disabled"]:
		add_theme_stylebox_override(slot, style)
	for slot in [&"hover", &"hover_pressed"]:
		add_theme_stylebox_override(slot, hover)
	add_theme_stylebox_override(&"focus", StyleBoxEmpty.new())
	for slot in [&"font_color", &"font_pressed_color", &"font_hover_color", &"font_hover_pressed_color", &"font_focus_color"]:
		add_theme_color_override(slot, font)

	toggled.connect(func(_on: bool) -> void: queue_redraw())
	focus_entered.connect(func() -> void: button_pressed = true)


func _draw() -> void:
	if button_pressed:
		draw_rect(Rect2(-Vector2.ONE * RING_GAP, size + Vector2.ONE * RING_GAP * 2), RING_COLOR, false, 2.0)


static func _style(background: Color, edge: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = edge
	style.set_border_width_all(2)
	style.set_corner_radius_all(4)
	return style
