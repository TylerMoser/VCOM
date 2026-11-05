## What a skill is, shown by the Roster's Skills page beside the node the
## mouse is over or the keyboard is on (a built-in tooltip only follows the
## mouse). From the top: the skill's name; its flavour text; "Current:" and
## what the level the character has gives, once they have taken it; "Next:"
## and what the next level would, while there is one left to take. A part
## with nothing to say is left out.
##
## A fixed width, as tall as its text. It never takes the mouse, so the node
## under it can still be hovered and held.
class_name SkillTooltip
extends PanelContainer

const WIDTH := 300.0
## Round the text, inside the border.
const PADDING := 12
## The "Current:" and "Next:" column, so what follows them lines up.
const PREFIX_WIDTH := 66.0
const ROW_GAP := 6

const BG_COLOR := Color(0.07, 0.08, 0.11, 0.97)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const NAME_COLOR := Color(0.95, 0.95, 0.97)
const FLAVOR_COLOR := Color(0.6, 0.62, 0.68)
const TEXT_COLOR := Color(0.85, 0.86, 0.9)
const CURRENT_COLOR := Color(0.7, 0.72, 0.78)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)

var _name: Label
var _flavor: Label
var _current: HBoxContainer
var _next: HBoxContainer


func _init() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	custom_minimum_size.x = WIDTH
	var style := StyleBoxFlat.new()
	style.bg_color = BG_COLOR
	style.border_color = BORDER_COLOR
	style.set_border_width_all(1)
	style.set_corner_radius_all(4)
	style.set_content_margin_all(PADDING)
	add_theme_stylebox_override(&"panel", style)

	var rows := VBoxContainer.new()
	rows.mouse_filter = MOUSE_FILTER_IGNORE
	rows.add_theme_constant_override(&"separation", ROW_GAP)
	add_child(rows)
	var inner := WIDTH - PADDING * 2.0
	_name = _text(17, NAME_COLOR, inner)
	rows.add_child(_name)
	_flavor = _text(14, FLAVOR_COLOR, inner)
	# No italic comes with the theme's font, so the same one is slanted.
	var slanted := FontVariation.new()
	slanted.variation_transform = Transform2D(Vector2(1.0, 0.2), Vector2(0.0, 1.0), Vector2.ZERO)
	_flavor.add_theme_font_override(&"font", slanted)
	rows.add_child(_flavor)
	_current = _level_row("Current:", CURRENT_COLOR, inner)
	rows.add_child(_current)
	_next = _level_row("Next:", ACCENT_COLOR, inner)
	rows.add_child(_next)


## Fills the tooltip for [param skill], which the character has taken
## [param taken] times, and fits it to what it now says.
func show_skill(skill: Skill, taken: int) -> void:
	_name.text = skill.display_name
	_flavor.text = skill.flavor
	_flavor.visible = not skill.flavor.is_empty()
	_show_level(_current, skill.describe(taken))
	_show_level(_next, skill.describe(taken + 1) if taken < skill.takes() else "")
	reset_size()


func _show_level(row: HBoxContainer, says: String) -> void:
	(row.get_child(1) as Label).text = says
	row.visible = not says.is_empty()


## A row for one level: [param prefix] in [param color], then what the level
## gives, wrapped in what is left of [param width].
func _level_row(prefix: String, color: Color, width: float) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.mouse_filter = MOUSE_FILTER_IGNORE
	row.add_theme_constant_override(&"separation", 0)
	var label := _text(15, color, PREFIX_WIDTH)
	label.text = prefix
	label.size_flags_vertical = SIZE_SHRINK_BEGIN
	row.add_child(label)
	row.add_child(_text(15, TEXT_COLOR, width - PREFIX_WIDTH))
	return row


## A label that wraps at [param width]. The width is its minimum too, so it
## is that wide before any container lays it out, and knows how many lines it
## runs to the moment its text is set.
func _text(font_size: int, color: Color, width: float) -> Label:
	var label := Label.new()
	label.mouse_filter = MOUSE_FILTER_IGNORE
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.custom_minimum_size.x = width
	label.add_theme_font_size_override(&"font_size", font_size)
	label.add_theme_color_override(&"font_color", color)
	return label
