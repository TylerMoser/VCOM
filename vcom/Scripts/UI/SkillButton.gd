## One node of a skill tree on the Roster's Skills page ([SkillTreeView]): a
## circle styled by whether the character has learned it, can learn it next,
## or has yet to reach it. It shows its skill's icon, or without one its rank
## (its row, counted from 1), and the skill's name and description on hover.
##
## Held down while [member learnable], with the mouse or with Enter or Space,
## it fills like a clock's face, from the top round clockwise, for
## [constant HOLD_TIME], as a [HoldButton] fills from the left, and then emits
## [signal held]. Let go early, or slid off with the mouse still down, and the
## fill drains back. Full, it empties at once and stays empty until let go and
## pressed again, so a press learns one skill at most.
##
## Focusing it (arrow keys or a click) selects it, marked by a ring round it;
## the page keeps one selected at a time. It draws itself, every one of its
## theme's boxes left empty, so the fill can go under its rank or icon.
class_name SkillButton
extends Button

## The button has been held for the whole [constant HOLD_TIME]: learn it.
signal held

enum State { LOCKED, AVAILABLE, LEARNED }

const SIZE := Vector2(44, 44)
const BORDER_WIDTH := 2.0
## How far outside the circle the selection ring is drawn.
const RING_GAP := 4.0
## Seconds it must be held down to learn: a [HoldButton]'s.
const HOLD_TIME := 2.0
## How much faster the fill drains than it fills: a [HoldButton]'s.
const DRAIN_SPEED := 4.0
## Points round a whole circle, for the border, the ring and the fill's edge.
const SEGMENTS := 64
## Across the square an icon is drawn in, inside the border.
const ICON_SIZE := 26.0

const BG_COLOR := Color(0.14, 0.15, 0.2, 0.95)
const LOCKED_BG_COLOR := Color(0.09, 0.1, 0.13, 0.95)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const MUTED_COLOR := Color(0.45, 0.46, 0.5)
const DARK_TEXT_COLOR := Color(0.1, 0.11, 0.15)
const RING_COLOR := Color(0.95, 0.95, 0.97)
## The fill as it is held: a [HoldButton]'s.
const FILL_COLOR := Color(1.0, 0.9, 0.55, 0.4)
## An icon on a node not yet reached is dimmed to this.
const LOCKED_ICON_COLOR := Color(1, 1, 1, 0.35)

## The place in its tree the button shows.
var tree_node: SkillTreeNode
var state := State.LOCKED:
	set(value):
		state = value
		queue_redraw()
## Whether holding it learns it now. Set by the page; without it the button
## can be selected but never fills.
var learnable := false
## Drawn with a ring round it.
var selected := false:
	set(value):
		selected = value
		queue_redraw()
## How far it has filled, from 0 to 1.
var progress := 0.0

## Set once full, until the button is let go.
var _spent := false


func _init(shown: SkillTreeNode, node_state: State) -> void:
	tree_node = shown
	state = node_state
	custom_minimum_size = SIZE
	size = SIZE
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	add_theme_font_size_override(&"font_size", 17)
	for slot in [&"normal", &"hover", &"pressed", &"hover_pressed", &"disabled", &"focus"]:
		add_theme_stylebox_override(slot, StyleBoxEmpty.new())
	var skill := tree_node.skill
	if skill != null:
		tooltip_text = skill.display_name if skill.description.is_empty() else "%s\n%s" % [skill.display_name, skill.description]


func _process(delta: float) -> void:
	# Pressed is only drawn while the press is on the button: a mouse held
	# down but slid off it counts as let go.
	var holding := learnable and get_draw_mode() == DRAW_PRESSED
	if get_draw_mode() != DRAW_PRESSED:
		_spent = false
	var before := progress
	if holding and not _spent:
		progress = minf(progress + delta / HOLD_TIME, 1.0)
		if progress >= 1.0:
			progress = 0.0
			_spent = true
			held.emit()
	elif not holding:
		progress = maxf(progress - delta * DRAIN_SPEED / HOLD_TIME, 0.0)
	if progress != before:
		queue_redraw()


## Only the circle takes the mouse, not the corners of its square.
func _has_point(point: Vector2) -> bool:
	return point.distance_to(size / 2.0) <= minf(size.x, size.y) / 2.0


func _draw() -> void:
	var center := size / 2.0
	var radius := minf(size.x, size.y) / 2.0
	var background: Color = {State.LOCKED: LOCKED_BG_COLOR, State.AVAILABLE: BG_COLOR, State.LEARNED: ACCENT_COLOR}[state]
	if is_hovered():
		background = background.lightened(0.08)
	var edge: Color = {State.LOCKED: BORDER_COLOR, State.AVAILABLE: ACCENT_COLOR, State.LEARNED: ACCENT_COLOR}[state]
	draw_circle(center, radius - BORDER_WIDTH / 2.0, background, true, -1.0, true)
	if progress > 0.0:
		draw_colored_polygon(_sector(center, radius - BORDER_WIDTH, progress), FILL_COLOR)
	draw_arc(center, radius - BORDER_WIDTH / 2.0, 0.0, TAU, SEGMENTS, edge, BORDER_WIDTH, true)
	_draw_face(center)
	if selected:
		draw_arc(center, radius + RING_GAP, 0.0, TAU, SEGMENTS, RING_COLOR, 2.0, true)


## The skill's icon, dimmed while locked, or the node's rank.
func _draw_face(center: Vector2) -> void:
	var skill := tree_node.skill
	if skill != null and skill.icon != null:
		var tint := LOCKED_ICON_COLOR if state == State.LOCKED else Color.WHITE
		draw_texture_rect(skill.icon, Rect2(center - Vector2.ONE * ICON_SIZE / 2.0, Vector2.ONE * ICON_SIZE), false, tint)
		return
	var color: Color = {State.LOCKED: MUTED_COLOR, State.AVAILABLE: ACCENT_COLOR, State.LEARNED: DARK_TEXT_COLOR}[state]
	var font := get_theme_font(&"font")
	var font_size := get_theme_font_size(&"font_size")
	var rank := str(tree_node.cell.y + 1)
	var width := font.get_string_size(rank, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
	var baseline := center.y + (font.get_ascent(font_size) - font.get_descent(font_size)) / 2.0
	draw_string(font, Vector2(center.x - width / 2.0, baseline), rank, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)


## The slice of the circle [param fraction] of the way round, from the top
## clockwise (y runs down the screen, so the angle grows that way).
static func _sector(center: Vector2, radius: float, fraction: float) -> PackedVector2Array:
	var points := PackedVector2Array([center])
	var steps := maxi(ceili(SEGMENTS * fraction), 2)
	for i in steps + 1:
		var angle := -PI / 2.0 + TAU * fraction * i / steps
		points.append(center + Vector2(cos(angle), sin(angle)) * radius)
	return points
