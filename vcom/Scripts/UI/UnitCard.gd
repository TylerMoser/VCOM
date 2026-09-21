## HUD card for one unit: portrait, health bar, and a pip per action.
## Clicking it emits [signal pressed]; [member selected] highlights it.
class_name UnitCard
extends PanelContainer

signal pressed

const PORTRAIT_SIZE := Vector2(72, 72)

const BG_COLOR := Color(0.1, 0.11, 0.15, 0.85)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const SELECTED_BG_COLOR := Color(0.18, 0.19, 0.25, 0.95)
const SELECTED_BORDER_COLOR := Color(1.0, 0.9, 0.55)

var unit: Unit

var selected := false:
	set(value):
		selected = value
		_update_style()

var _style: StyleBoxFlat
var _portrait: ColorRect
var _health_bar: ProgressBar
var _pips: HBoxContainer


func _init() -> void:
	mouse_default_cursor_shape = CURSOR_POINTING_HAND

	_style = StyleBoxFlat.new()
	_style.set_corner_radius_all(4)
	# Fixed margins, so the thicker selected border does not shift the layout.
	_style.set_content_margin_all(6)
	add_theme_stylebox_override(&"panel", _style)
	_update_style()

	# Children ignore the mouse so every click on the card reaches the card.
	var column := VBoxContainer.new()
	column.mouse_filter = MOUSE_FILTER_IGNORE
	column.add_theme_constant_override(&"separation", 6)
	add_child(column)

	# Stand-in for the character portrait.
	_portrait = ColorRect.new()
	_portrait.custom_minimum_size = PORTRAIT_SIZE
	_portrait.size_flags_horizontal = SIZE_SHRINK_CENTER
	_portrait.mouse_filter = MOUSE_FILTER_IGNORE
	column.add_child(_portrait)

	_health_bar = ProgressBar.new()
	_health_bar.custom_minimum_size = Vector2(PORTRAIT_SIZE.x, 8)
	_health_bar.show_percentage = false
	_health_bar.step = 1.0
	_health_bar.mouse_filter = MOUSE_FILTER_IGNORE
	_health_bar.add_theme_stylebox_override(&"background", _bar_style(Color(0.2, 0.08, 0.08)))
	_health_bar.add_theme_stylebox_override(&"fill", _bar_style(Color(0.3, 0.8, 0.35)))
	column.add_child(_health_bar)

	_pips = HBoxContainer.new()
	_pips.alignment = BoxContainer.ALIGNMENT_CENTER
	_pips.mouse_filter = MOUSE_FILTER_IGNORE
	_pips.add_theme_constant_override(&"separation", 6)
	column.add_child(_pips)


func _gui_input(event: InputEvent) -> void:
	var button := event as InputEventMouseButton
	if button != null and button.button_index == MOUSE_BUTTON_LEFT and button.pressed:
		accept_event()
		pressed.emit()


## Shows [param target] on this card and follows its health and actions.
func bind(target: Unit) -> void:
	unit = target
	tooltip_text = unit.display_name
	_portrait.color = unit.color
	unit.health_changed.connect(_on_health_changed)
	unit.actions_changed.connect(_on_actions_changed)
	_on_health_changed(unit.health, unit.max_health)
	_on_actions_changed(unit.actions_remaining, unit.actions_per_turn)


func _update_style() -> void:
	_style.bg_color = SELECTED_BG_COLOR if selected else BG_COLOR
	_style.border_color = SELECTED_BORDER_COLOR if selected else BORDER_COLOR
	_style.set_border_width_all(2 if selected else 1)


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
