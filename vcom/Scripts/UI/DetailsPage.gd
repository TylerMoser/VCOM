## The Roster's Details page: the selected character's stats, as one list of
## name and value, a rule between each, and in the bottom-right corner a bar
## of their experience, the count in its tooltip.
class_name DetailsPage
extends CharacterPage

## Each row: the name shown, and the [Character] property it shows.
const STATS := [
	["HP", &"max_health"],
	["Move", &"move_range"],
	["Aim", &"aim"],
	["Evasion", &"evasion"],
]

const LIST_WIDTH := 320
const EXPERIENCE_BAR_SIZE := Vector2(260, 10)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const NAME_COLOR := Color(0.7, 0.72, 0.78)
const VALUE_COLOR := Color(0.95, 0.95, 0.97)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const BAR_BG_COLOR := Color(0.06, 0.07, 0.1, 0.9)

## The value label of each row of [constant STATS], in order.
var _values: Array[Label] = []
var _experience: VBoxContainer
var _experience_bar: ProgressBar


func _init() -> void:
	super("Details")
	var list := VBoxContainer.new()
	list.custom_minimum_size.x = LIST_WIDTH
	list.add_theme_constant_override(&"separation", 0)
	add_child(list)
	for stat in STATS:
		list.add_child(_row(stat[0]))
	_experience = _experience_tracker()
	add_child(_experience)


func _refresh() -> void:
	for i in STATS.size():
		_values[i].text = str(character.get(STATS[i][1])) if character != null else "-"
	var experience := character.experience if character != null else 0
	_experience_bar.max_value = Character.EXPERIENCE_TO_LEVEL
	_experience_bar.value = experience
	_experience.tooltip_text = "Experience: %d / %d" % [experience, Character.EXPERIENCE_TO_LEVEL]


## A caption over a thin bar, pinned to the page's bottom-right corner. The
## tooltip is on the whole tracker, so hovering the caption shows it too.
func _experience_tracker() -> VBoxContainer:
	var tracker := VBoxContainer.new()
	tracker.add_theme_constant_override(&"separation", 6)
	tracker.mouse_filter = MOUSE_FILTER_STOP
	# Held to its minimum size and grown up and left from the corner.
	tracker.anchor_left = 1.0
	tracker.anchor_top = 1.0
	tracker.anchor_right = 1.0
	tracker.anchor_bottom = 1.0
	tracker.grow_horizontal = GROW_DIRECTION_BEGIN
	tracker.grow_vertical = GROW_DIRECTION_BEGIN

	var caption := Label.new()
	caption.text = "Experience"
	caption.mouse_filter = MOUSE_FILTER_IGNORE
	caption.add_theme_font_size_override(&"font_size", 15)
	caption.add_theme_color_override(&"font_color", NAME_COLOR)
	tracker.add_child(caption)

	_experience_bar = ProgressBar.new()
	_experience_bar.custom_minimum_size = EXPERIENCE_BAR_SIZE
	_experience_bar.show_percentage = false
	_experience_bar.mouse_filter = MOUSE_FILTER_IGNORE
	_experience_bar.add_theme_stylebox_override(&"background", _bar_style(BAR_BG_COLOR, BORDER_COLOR))
	_experience_bar.add_theme_stylebox_override(&"fill", _bar_style(ACCENT_COLOR, Color.TRANSPARENT))
	tracker.add_child(_experience_bar)
	return tracker


static func _bar_style(color: Color, edge: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = edge
	style.set_border_width_all(1)
	style.set_corner_radius_all(3)
	return style


## One stat: its name on the left, its value on the right, a rule beneath.
func _row(stat_name: String) -> PanelContainer:
	var row := PanelContainer.new()
	var rule := StyleBoxFlat.new()
	rule.bg_color = Color.TRANSPARENT
	rule.border_color = BORDER_COLOR
	rule.border_width_bottom = 1
	rule.content_margin_left = 4
	rule.content_margin_right = 4
	rule.content_margin_top = 8
	rule.content_margin_bottom = 8
	row.add_theme_stylebox_override(&"panel", rule)

	var line := HBoxContainer.new()
	row.add_child(line)
	var name_label := Label.new()
	name_label.text = stat_name
	name_label.size_flags_horizontal = SIZE_EXPAND_FILL
	name_label.add_theme_font_size_override(&"font_size", 17)
	name_label.add_theme_color_override(&"font_color", NAME_COLOR)
	line.add_child(name_label)
	var value := Label.new()
	value.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	value.add_theme_font_size_override(&"font_size", 17)
	value.add_theme_color_override(&"font_color", VALUE_COLOR)
	line.add_child(value)
	_values.append(value)
	return row
