## Small panel naming the unit being aimed at: its health, and what it has to
## hide behind. Floats above the reticle, so [ShotOverlay] places it.
class_name TargetPanel
extends PanelContainer

const BAR_SIZE := Vector2(132, 8)

const BG_COLOR := Color(0.1, 0.11, 0.15, 0.85)
const BORDER_COLOR := Color(1.0, 0.3, 0.25)
const STATUS_COLOR := Color(0.78, 0.8, 0.85)

var _name_label: Label
var _health_bar: ProgressBar
var _status_label: Label


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

	_name_label = Label.new()
	_name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name_label.mouse_filter = MOUSE_FILTER_IGNORE
	column.add_child(_name_label)

	_health_bar = ProgressBar.new()
	_health_bar.custom_minimum_size = BAR_SIZE
	_health_bar.show_percentage = false
	_health_bar.step = 1.0
	_health_bar.mouse_filter = MOUSE_FILTER_IGNORE
	_health_bar.add_theme_stylebox_override(&"background", _bar_style(Color(0.2, 0.08, 0.08)))
	_health_bar.add_theme_stylebox_override(&"fill", _bar_style(Color(0.9, 0.3, 0.25)))
	column.add_child(_health_bar)

	_status_label = Label.new()
	_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_status_label.mouse_filter = MOUSE_FILTER_IGNORE
	_status_label.add_theme_font_size_override(&"font_size", 12)
	_status_label.add_theme_color_override(&"font_color", STATUS_COLOR)
	column.add_child(_status_label)


## Shows the target of [param shot], and how it is being shot at.
func bind(shot: LineOfSight.Shot) -> void:
	_name_label.text = shot.target.display_name
	_health_bar.max_value = shot.target.max_health
	_health_bar.value = shot.target.health

	var status := LineOfSight.cover_name(shot.cover)
	if shot.stepped_out:
		status += "  ·  Stepping Out"
	_status_label.text = status
	# The panel is placed by its size, so settle it before anyone reads that.
	reset_size()


static func _bar_style(color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(2)
	return style
