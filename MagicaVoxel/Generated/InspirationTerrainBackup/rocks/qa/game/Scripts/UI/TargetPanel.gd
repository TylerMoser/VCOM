## Small panel naming the unit being aimed at: its health, what it is hiding
## behind, and the chance the shot lands. Holding the details key opens the
## sum behind that chance, so a bad shot can be read rather than guessed at.
## An ally a medkit is lined up on gets the same panel edged in green, with
## the health it would gain where the chance would be ([method bind_heal]).
##
## While the player is lining the shot or strike up, a tick box beside the
## chance confirms it: clicking it emits [signal confirmed]. With the gamepad
## an A glyph stands there instead, the button that takes it. It never takes the
## keyboard, so Enter and Space still reach the action, and the rest of the
## panel lets the mouse through to the map, so the target under it can still
## be clicked.
##
## Floats above the reticle, so [ShotOverlay] places it and decides when the
## breakdown is showing.
class_name TargetPanel
extends PanelContainer

## The tick beside the chance was clicked: take the shot or strike shown.
signal confirmed

const BAR_SIZE := Vector2(148, 8)

const BG_COLOR := Color(0.1, 0.11, 0.15, 0.88)
const BORDER_COLOR := Color(1.0, 0.3, 0.25)
## The edge and the health to gain of a medkit lined up on an ally.
const HEAL_COLOR := Color(0.45, 0.9, 0.5)
const STATUS_COLOR := Color(0.78, 0.8, 0.85)
const TERM_COLOR := Color(0.7, 0.72, 0.78)

## The chance is coloured by how good it is, so it reads at a glance.
const GOOD_COLOR := Color(0.45, 0.9, 0.5)
const FAIR_COLOR := Color(1.0, 0.82, 0.3)
const POOR_COLOR := Color(1.0, 0.45, 0.4)
const GOOD_CHANCE := 75
const FAIR_CHANCE := 40

## The tick box: the roster's tick, black on a pale box, as a ticked box reads,
## filled with the menus' accent under the mouse.
const TICK := preload("res://UI/black_tick.png")
const CONFIRM_SIZE := Vector2(26, 26)
## Between the box's edge and the tick.
const CONFIRM_MARGIN := 4.0
## Between the chance and the box.
const CONFIRM_GAP := 8
const CONFIRM_COLOR := Color(0.88, 0.9, 0.94)
const CONFIRM_HOVER_COLOR := Color(1.0, 0.9, 0.55)
const CONFIRM_PRESSED_COLOR := Color(0.85, 0.72, 0.35)

var _style: StyleBoxFlat
var _name_label: Label
var _health_bar: ProgressBar
var _status_label: Label
var _chance_label: Label
var _confirm: Button
## The gamepad's A, in the tick box's place while the gamepad is in use.
var _confirm_glyph: ButtonGlyph
## Whether what is shown can be confirmed from here.
var _confirmable := false
## As wide as the tick box, on the chance's other side, so the chance stays in
## the middle of the panel.
var _confirm_pad: Control
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

	_style = StyleBoxFlat.new()
	_style.bg_color = BG_COLOR
	_style.border_color = BORDER_COLOR
	_style.set_border_width_all(1)
	_style.set_corner_radius_all(4)
	_style.set_content_margin_all(8)
	add_theme_stylebox_override(&"panel", _style)

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

	var chance_row := HBoxContainer.new()
	chance_row.mouse_filter = MOUSE_FILTER_IGNORE
	chance_row.alignment = BoxContainer.ALIGNMENT_CENTER
	chance_row.add_theme_constant_override(&"separation", CONFIRM_GAP)
	column.add_child(chance_row)

	_confirm_pad = Control.new()
	_confirm_pad.custom_minimum_size = CONFIRM_SIZE
	_confirm_pad.mouse_filter = MOUSE_FILTER_IGNORE
	chance_row.add_child(_confirm_pad)

	_chance_label = _label("", HORIZONTAL_ALIGNMENT_CENTER, 28)
	chance_row.add_child(_chance_label)

	_confirm = Button.new()
	_confirm.icon = TICK
	_confirm.expand_icon = true
	_confirm.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_confirm.custom_minimum_size = CONFIRM_SIZE
	_confirm.size_flags_vertical = SIZE_SHRINK_CENTER
	# Never the keyboard's: Space on a focused button would press it as well as
	# reach the action.
	_confirm.focus_mode = FOCUS_NONE
	_confirm.mouse_default_cursor_shape = CURSOR_POINTING_HAND
	_confirm.add_theme_stylebox_override(&"normal", _box_style(CONFIRM_COLOR))
	_confirm.add_theme_stylebox_override(&"hover", _box_style(CONFIRM_HOVER_COLOR))
	_confirm.add_theme_stylebox_override(&"pressed", _box_style(CONFIRM_PRESSED_COLOR))
	_confirm.add_theme_stylebox_override(&"hover_pressed", _box_style(CONFIRM_PRESSED_COLOR))
	_confirm.add_theme_stylebox_override(&"focus", StyleBoxEmpty.new())
	_confirm.pressed.connect(confirmed.emit)
	chance_row.add_child(_confirm)

	_confirm_glyph = ButtonGlyph.new(&"A")
	_confirm_glyph.custom_minimum_size = CONFIRM_SIZE
	_confirm_glyph.size_flags_vertical = SIZE_SHRINK_CENTER
	chance_row.add_child(_confirm_glyph)

	_details = VBoxContainer.new()
	_details.mouse_filter = MOUSE_FILTER_IGNORE
	_details.visible = false
	_details.add_theme_constant_override(&"separation", 1)
	column.add_child(_details)


## Shows the target of [param shot] and its odds of being hit, with the tick
## box to fire if [param confirmable]: while the player lines it up, not while
## a shot they already called plays out.
func bind(shot: LineOfSight.Shot, estimate: HitChance.Estimate, confirmable := false) -> void:
	var status := LineOfSight.cover_name(shot.cover, shot.flanked)
	if shot.stepped_out:
		status += "  ·  Stepping Out"
	_show(shot.target, status, estimate, confirmable, "Fire")


## Shows [param target] as the target of a melee strike, with its odds of
## being hit, and the tick box to strike if [param confirmable]. Its cover
## counts for nothing in melee, so the panel says it is a strike instead.
func bind_strike(target: Unit, estimate: HitChance.Estimate, confirmable := false) -> void:
	_show(target, "Melee", estimate, confirmable, "Strike")


## Shows [param target] as the ally a medkit is lined up on: its health, what
## it would be after, and the [param amount] it would gain in place of a
## chance, nothing being rolled, with the tick box to use it if
## [param confirmable]. Edged in green rather than red. [param kit] names the
## medkit in the status line: "Medkit", or whose it is if borrowed.
func bind_heal(target: Unit, amount: int, confirmable := false, kit := "Medkit") -> void:
	var status := "%s  ·  %d → %d HP" % [kit, target.health, target.health + amount]
	_show_unit(target, status, confirmable, "Heal", HEAL_COLOR)
	_chance_label.text = "+%d HP" % amount
	_chance_label.add_theme_color_override(&"font_color", HEAL_COLOR)
	_fill_details(null)
	reset_size()


func _ready() -> void:
	InputDevice.watch(_on_device_changed)
	_show_confirm()


func _show(target: Unit, status: String, estimate: HitChance.Estimate, confirmable: bool, verb: String) -> void:
	_show_unit(target, status, confirmable, verb, BORDER_COLOR)
	_chance_label.text = "%d%%" % estimate.chance
	_chance_label.add_theme_color_override(&"font_color", chance_color(estimate.chance))
	_fill_details(estimate)
	# The panel is placed by its size, so settle it before anyone reads that.
	reset_size()


## What every target shows: its name and health, [param status] under them,
## the tick box if [param confirmable] (taking it [param verb]s), and an edge
## in [param border].
func _show_unit(target: Unit, status: String, confirmable: bool, verb: String, border: Color) -> void:
	_confirmable = confirmable
	_show_confirm()
	_confirm.tooltip_text = "%s (Enter / Space, or click the target)" % verb
	_style.border_color = border
	_name_label.text = target.display_name
	_health_bar.max_value = target.max_health
	_health_bar.value = target.health
	_status_label.text = status


## The tick box with the mouse, A with the gamepad, or neither when there is
## nothing to confirm here.
func _show_confirm() -> void:
	_confirm.visible = _confirmable and not InputDevice.gamepad
	_confirm_glyph.visible = _confirmable and InputDevice.gamepad
	_confirm_pad.visible = _confirmable


func _on_device_changed(_gamepad: bool) -> void:
	_show_confirm()


## One row per term that was worth anything, name on the left and what it was
## worth on the right. None without an [param estimate]: a heal is not rolled.
func _fill_details(estimate: HitChance.Estimate) -> void:
	for row in _details.get_children():
		_details.remove_child(row)
		row.queue_free()
	if estimate == null:
		return

	for term in estimate.terms:
		var row := HBoxContainer.new()
		row.mouse_filter = MOUSE_FILTER_IGNORE
		var name_label := _label(term.label, HORIZONTAL_ALIGNMENT_LEFT, 12, TERM_COLOR)
		name_label.size_flags_horizontal = SIZE_EXPAND_FILL
		row.add_child(name_label)
		row.add_child(_label("%+d" % term.value, HORIZONTAL_ALIGNMENT_RIGHT, 12, TERM_COLOR))
		_details.add_child(row)


## The colour a hit chance is shown in: green for a good shot, amber for a
## fair one, red for a poor one.
static func chance_color(chance: int) -> Color:
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


static func _box_style(color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(4)
	style.set_content_margin_all(CONFIRM_MARGIN)
	return style


static func _bar_style(color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(2)
	return style
