## A panel of gamepad prompts: a row for each thing the player can do right
## now, its button or buttons ([ButtonGlyph]) and what it does. Shown only
## while the gamepad is in use ([InputDevice]): with the keyboard and mouse it
## hides, and the controls are as the README has them.
##
## Whoever owns it says what is on offer with [method show_hints], as often as
## it likes; it only rebuilds when that changes. A column, as combat and the
## world map have down the right of the screen, or a row, as the menus have
## along the bottom.
class_name ControlHints
extends PanelContainer

const BG_COLOR := Color(0.1, 0.11, 0.15, 0.8)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const TEXT_COLOR := Color(0.88, 0.89, 0.93)
const FONT_SIZE := 15
## Between a row's glyphs, between them and the words, and between rows.
const GLYPH_GAP := 3
const TEXT_GAP := 7
const ROW_GAP := 6
const COLUMN_GAP := 18

var _box: BoxContainer
## The rows showing, as given: [code][[buttons...], words][/code].
var _rows: Array = []


func _init(vertical := true) -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	visible = false
	var style := StyleBoxFlat.new()
	style.bg_color = BG_COLOR
	style.border_color = BORDER_COLOR
	style.set_border_width_all(1)
	style.set_corner_radius_all(4)
	style.set_content_margin_all(8)
	add_theme_stylebox_override(&"panel", style)
	_box = VBoxContainer.new() if vertical else HBoxContainer.new()
	_box.mouse_filter = MOUSE_FILTER_IGNORE
	_box.add_theme_constant_override(&"separation", ROW_GAP if vertical else COLUMN_GAP)
	add_child(_box)


func _ready() -> void:
	InputDevice.watch(_on_device_changed)
	_update_visible()


## Shows [param rows], each [code][[buttons...], words][/code], such as
## [code][[&"LB", &"RB"], "Squad member"][/code], in place of what was showing.
## A row that is empty, or has no buttons or no words, is left out; with no
## rows the panel hides.
func show_hints(rows: Array) -> void:
	if rows == _rows:
		return
	_rows = rows.duplicate(true)
	for child in _box.get_children():
		_box.remove_child(child)
		child.queue_free()
	for row: Array in _rows:
		if row.size() < 2:
			continue
		var buttons: Array = row[0]
		var words: String = row[1]
		if buttons.is_empty() or words.is_empty():
			continue
		var line := HBoxContainer.new()
		line.mouse_filter = MOUSE_FILTER_IGNORE
		line.add_theme_constant_override(&"separation", GLYPH_GAP)
		for button: StringName in buttons:
			line.add_child(ButtonGlyph.new(button))
		var label := Label.new()
		label.text = words
		label.mouse_filter = MOUSE_FILTER_IGNORE
		label.add_theme_font_size_override(&"font_size", FONT_SIZE)
		label.add_theme_color_override(&"font_color", TEXT_COLOR)
		# The words sit a little apart from the buttons, more than the buttons
		# from each other.
		var spacer := Control.new()
		spacer.custom_minimum_size = Vector2(TEXT_GAP - GLYPH_GAP, 0)
		spacer.mouse_filter = MOUSE_FILTER_IGNORE
		line.add_child(spacer)
		line.add_child(label)
		_box.add_child(line)
	_update_visible()
	_collapse()


## Shrinks to nothing at the edge or middle it grows from, so it takes the
## size of its rows again, growing the way its grow directions say. (A
## [method Control.reset_size] would keep its top-left corner instead, and a
## panel in the bottom-right corner would grow off the screen.)
func _collapse() -> void:
	offset_left = _edge(offset_left, offset_right, grow_horizontal)
	offset_right = offset_left
	offset_top = _edge(offset_top, offset_bottom, grow_vertical)
	offset_bottom = offset_top


static func _edge(begin: float, end: float, grow: GrowDirection) -> float:
	match grow:
		GROW_DIRECTION_BEGIN:
			return end
		GROW_DIRECTION_END:
			return begin
	return (begin + end) * 0.5


func _on_device_changed(_gamepad: bool) -> void:
	_update_visible()


func _update_visible() -> void:
	visible = InputDevice.gamepad and _box.get_child_count() > 0
