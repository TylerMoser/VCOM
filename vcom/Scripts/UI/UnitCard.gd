## HUD card for one unit: portrait, health bar, and a pip per action.
class_name UnitCard
extends PanelContainer

const PORTRAIT_SIZE := Vector2(72, 72)

var unit: Unit

var _portrait: ColorRect
var _health_bar: ProgressBar
var _pips: HBoxContainer


func _init() -> void:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.11, 0.15, 0.85)
	style.border_color = Color(0.3, 0.32, 0.4)
	style.set_border_width_all(1)
	style.set_corner_radius_all(4)
	style.set_content_margin_all(6)
	add_theme_stylebox_override(&"panel", style)

	var column := VBoxContainer.new()
	column.add_theme_constant_override(&"separation", 6)
	add_child(column)

	# Stand-in for the character portrait.
	_portrait = ColorRect.new()
	_portrait.custom_minimum_size = PORTRAIT_SIZE
	_portrait.size_flags_horizontal = SIZE_SHRINK_CENTER
	column.add_child(_portrait)

	_health_bar = ProgressBar.new()
	_health_bar.custom_minimum_size = Vector2(PORTRAIT_SIZE.x, 8)
	_health_bar.show_percentage = false
	_health_bar.step = 1.0
	_health_bar.add_theme_stylebox_override(&"background", _bar_style(Color(0.2, 0.08, 0.08)))
	_health_bar.add_theme_stylebox_override(&"fill", _bar_style(Color(0.3, 0.8, 0.35)))
	column.add_child(_health_bar)

	_pips = HBoxContainer.new()
	_pips.alignment = BoxContainer.ALIGNMENT_CENTER
	_pips.add_theme_constant_override(&"separation", 6)
	column.add_child(_pips)


## Shows [param target] on this card and follows its health and actions.
func bind(target: Unit) -> void:
	unit = target
	tooltip_text = unit.display_name
	_portrait.color = unit.color
	unit.health_changed.connect(_on_health_changed)
	unit.actions_changed.connect(_on_actions_changed)
	_on_health_changed(unit.health, unit.max_health)
	_on_actions_changed(unit.actions_remaining, unit.actions_per_turn)


func _on_health_changed(health: int, max_health: int) -> void:
	_health_bar.max_value = max_health
	_health_bar.value = health


func _on_actions_changed(remaining: int, per_turn: int) -> void:
	while _pips.get_child_count() < per_turn:
		_pips.add_child(ActionPip.new())
	while _pips.get_child_count() > per_turn:
		var extra := _pips.get_child(_pips.get_child_count() - 1)
		_pips.remove_child(extra)
		extra.queue_free()
	for i in per_turn:
		(_pips.get_child(i) as ActionPip).available = i < remaining


static func _bar_style(color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(2)
	return style
