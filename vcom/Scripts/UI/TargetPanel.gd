## Small panel naming the unit being aimed at: its health, what it is hiding
## behind, and the chance the shot lands. Holding the details key opens the
## sum behind that chance, so a bad shot can be read rather than guessed at.
##
## Floats above the reticle, so [ShotOverlay] places it and decides when the
## breakdown is showing.
class_name TargetPanel
extends PanelContainer

const BAR_SIZE := Vector2(148, 8)

const BG_COLOR := Color(0.1, 0.11, 0.15, 0.88)
const BORDER_COLOR := Color(1.0, 0.3, 0.25)
const STATUS_COLOR := Color(0.78, 0.8, 0.85)
const TERM_COLOR := Color(0.7, 0.72, 0.78)

## The chance is coloured by how good it is, so it reads at a glance.
const GOOD_COLOR := Color(0.45, 0.9, 0.5)
const FAIR_COLOR := Color(1.0, 0.82, 0.3)
const POOR_COLOR := Color(1.0, 0.45, 0.4)
const GOOD_CHANCE := 75
const FAIR_CHANCE := 40

var _name_label: Label
var _health_bar: ProgressBar
var _status_label: Label
var _chance_label: Label
var _details: VBoxContainer

## Whether the breakdown under the chance is open.
var details_shown := false:
	set(value):
		if details_shown == value:
			return
		details_shown = value
		_details.visible = value
		reset_size()


func _init() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE

	var style := StyleBoxFlat.new()
	style.bg_color = BG_COLOR
	style.border_color = BORDER_COLOR
	style.set_border_width_all(1)
	style.set_corner_radius_all(4)
	style.set_content_margin_all(8)
	add_theme_stylebox_override(&"panel", style)

	var column := VBoxContainer.new()
	column.mouse_filter = MOUSE_FILTER_IGNORE
	column.add_theme_constant_override(&"separation", 4)
	add_child(column)

	_name_label = _label("", HORIZONTAL_ALIGNMENT_CENTER)
	column.add_child(_name_label)

	_health_bar = ProgressBar.new()
	_health_bar.custom_minimum_size = BAR_SIZE
	_health_bar.show_percentage = false
	_health_bar.step = 1.0
	_health_bar.mouse_filter = MOUSE_FILTER_IGNORE
	_health_bar.add_theme_stylebox_override(&"background", _bar_style(Color(0.2, 0.08, 0.08)))
	_health_bar.add_theme_stylebox_override(&"fill", _bar_style(Color(0.9, 0.3, 0.25)))
	column.add_child(_health_bar)

	_status_label = _label("", HORIZONTAL_ALIGNMENT_CENTER, 12, STATUS_COLOR)
	column.add_child(_status_label)

	_chance_label = _label("", HORIZONTAL_ALIGNMENT_CENTER, 28)
	column.add_child(_chance_label)

	_details = VBoxContainer.new()
	_details.mouse_filter = MOUSE_FILTER_IGNORE
	_details.visible = false
	_details.add_theme_constant_override(&"separation", 1)
	column.add_child(_details)


## Shows the target of [param shot] and its odds of being hit.
func bind(shot: LineOfSight.Shot, estimate: HitChance.Estimate) -> void:
	_name_label.text = shot.target.display_name
	_health_bar.max_value = shot.target.max_health
	_health_bar.value = shot.target.health

	var status := LineOfSight.cover_name(shot.cover, shot.flanked)
	if shot.stepped_out:
		status += "  ·  Stepping Out"
	_status_label.text = status

	_chance_label.text = "%d%%" % estimate.chance
	_chance_label.add_theme_color_override(&"font_color", _chance_color(estimate.chance))
	_fill_details(estimate)
	# The panel is placed by its size, so settle it before anyone reads that.
	reset_size()


## One row per term that was worth anything, name on the left and what it was
## worth on the right.
func _fill_details(estimate: HitChance.Estimate) -> void:
	for row in _details.get_children():
		_details.remove_child(row)
		row.queue_free()

	for term in estimate.terms:
		var row := HBoxContainer.new()
		row.mouse_filter = MOUSE_FILTER_IGNORE
		var name_label := _label(term.label, HORIZONTAL_ALIGNMENT_LEFT, 12, TERM_COLOR)
		name_label.size_flags_horizontal = SIZE_EXPAND_FILL
		row.add_child(name_label)
		row.add_child(_label("%+d" % term.value, HORIZONTAL_ALIGNMENT_RIGHT, 12, TERM_COLOR))
		_details.add_child(row)


static func _chance_color(chance: int) -> Color:
	if chance >= GOOD_CHANCE:
		return GOOD_COLOR
	return FAIR_COLOR if chance >= FAIR_CHANCE else POOR_COLOR


static func _label(
	text: String, alignment: HorizontalAlignment, font_size := 0, color := Color.WHITE
) -> Label:
	var label := Label.new()
	label.text = text
	label.horizontal_alignment = alignment
	label.mouse_filter = MOUSE_FILTER_IGNORE
	if font_size > 0:
		label.add_theme_font_size_override(&"font_size", font_size)
	if color != Color.WHITE:
		label.add_theme_color_override(&"font_color", color)
	return label


static func _bar_style(color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(2)
	return style
