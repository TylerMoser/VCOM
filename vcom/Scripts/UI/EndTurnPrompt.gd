## "End Turn" bar that fills while Shift is held, above the action bar.
extends VBoxContainer

@export var turn_manager_path: NodePath = ^"../../TurnManager"

var _bar: ProgressBar


func _ready() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	visible = false

	var label := Label.new()
	label.text = "End Turn"
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(label)

	_bar = ProgressBar.new()
	_bar.custom_minimum_size = Vector2(160, 8)
	_bar.show_percentage = false
	_bar.max_value = 1.0
	_bar.mouse_filter = MOUSE_FILTER_IGNORE
	_bar.add_theme_stylebox_override(&"background", _bar_style(Color(0.1, 0.11, 0.15, 0.85)))
	_bar.add_theme_stylebox_override(&"fill", _bar_style(Color(1.0, 0.9, 0.55)))
	add_child(_bar)

	var turns := get_node_or_null(turn_manager_path) as TurnManager
	if turns == null:
		push_error("EndTurnPrompt: no TurnManager at '%s'." % turn_manager_path)
		return
	turns.end_turn_hold_changed.connect(_on_hold_changed)


func _on_hold_changed(progress: float) -> void:
	visible = progress > 0.0
	_bar.value = progress


static func _bar_style(color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(2)
	return style
