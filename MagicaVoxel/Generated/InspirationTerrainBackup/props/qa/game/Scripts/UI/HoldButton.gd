## A button that acts only once it has been held down for [member hold_time],
## filling from left to right as it is held, so a costly choice cannot be made
## by a stray click. Held with the mouse, or with Enter or Space while it has
## the keyboard.
##
## Let go early, or slid off with the mouse still down, and the fill drains
## back; press again to carry on from where it has drained to. Full, it empties
## at once and emits [signal held], and stays empty until it is let go and
## pressed again, so every choice takes a press and a hold of its own. A plain
## click does nothing: listen to [signal held], not [signal BaseButton.pressed].
##
## Its caption is a child label drawn over the fill, so set [member caption]
## rather than [member Button.text], which stays empty.
class_name HoldButton
extends Button

## The button has been held for the whole [member hold_time].
signal held

## How much faster the fill drains than it fills.
const DRAIN_SPEED := 4.0
## Between the button's edge and its caption.
const PADDING := Vector2(22, 9)
## Between the button's edge and the fill, leaving the border showing.
const FILL_INSET := 1.0

const BG_COLOR := Color(0.14, 0.15, 0.2, 0.95)
const HOVER_BG_COLOR := Color(0.18, 0.19, 0.25, 0.95)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const FILL_COLOR := Color(1.0, 0.9, 0.55, 0.4)
const TEXT_COLOR := Color(0.92, 0.93, 0.95)
const MUTED_COLOR := Color(0.45, 0.46, 0.5)

## Seconds it must be held down to act.
var hold_time := 2.0
var caption := "":
	set(value):
		caption = value
		_label.text = value
## How far it has filled, from 0 to 1.
var progress := 0.0

var _label: Label
var _fill: Panel
## Set once full, until the button is let go.
var _spent := false
## Whether the caption is drawn greyed out, to change it only when that
## changes.
var _greyed := false


func _init() -> void:
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	tooltip_text = "Hold to confirm."
	add_theme_stylebox_override(&"normal", _style(BG_COLOR, BORDER_COLOR, 1))
	add_theme_stylebox_override(&"hover", _style(HOVER_BG_COLOR, ACCENT_COLOR, 1))
	add_theme_stylebox_override(&"pressed", _style(HOVER_BG_COLOR, ACCENT_COLOR, 2))
	add_theme_stylebox_override(&"focus", _style(Color.TRANSPARENT, Color.WHITE, 1))
	add_theme_stylebox_override(&"disabled", _style(BG_COLOR, BORDER_COLOR, 1))

	# A button draws its children over itself, so the fill goes over the
	# background and the caption over the fill.
	_fill = Panel.new()
	_fill.mouse_filter = MOUSE_FILTER_IGNORE
	var fill_style := StyleBoxFlat.new()
	fill_style.bg_color = FILL_COLOR
	fill_style.set_corner_radius_all(3)
	_fill.add_theme_stylebox_override(&"panel", fill_style)
	_fill.visible = false
	add_child(_fill)

	_label = Label.new()
	_label.mouse_filter = MOUSE_FILTER_IGNORE
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_label.add_theme_font_size_override(&"font_size", 17)
	_label.add_theme_color_override(&"font_color", TEXT_COLOR)
	_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	_label.minimum_size_changed.connect(_fit_label)
	add_child(_label)

	resized.connect(_place_fill)


func _process(delta: float) -> void:
	# Pressed is only drawn while the press is on the button: a mouse held
	# down but slid off it counts as let go.
	var holding := get_draw_mode() == DRAW_PRESSED
	if not holding:
		_spent = false
	var before := progress
	if holding and not _spent:
		progress = minf(progress + delta / hold_time, 1.0)
		if progress >= 1.0:
			progress = 0.0
			_spent = true
			held.emit()
	elif not holding:
		progress = maxf(progress - delta * DRAIN_SPEED / hold_time, 0.0)
	if progress != before:
		_place_fill()
	if disabled != _greyed:
		_greyed = disabled
		_label.add_theme_color_override(&"font_color", MUTED_COLOR if disabled else TEXT_COLOR)


## Sizes the button round its caption, again whenever the caption's size
## changes. (A Button's own sizing ignores a script's _get_minimum_size.)
func _fit_label() -> void:
	custom_minimum_size = _label.get_combined_minimum_size() + PADDING * 2


func _place_fill() -> void:
	var inner := size - Vector2(FILL_INSET, FILL_INSET) * 2
	_fill.position = Vector2(FILL_INSET, FILL_INSET)
	_fill.size = Vector2(inner.x * progress, inner.y)
	_fill.visible = progress > 0.0


static func _style(background: Color, edge: Color, width: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = edge
	style.set_border_width_all(width)
	style.set_corner_radius_all(4)
	return style
