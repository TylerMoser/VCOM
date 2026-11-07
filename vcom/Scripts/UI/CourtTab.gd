## One scrolling page for a ruler's identity, favor, and information.
class_name CourtTab
extends ScrollContainer

const FAVOR_ICONS := [
	preload("res://UI/Court/arrow-down.png"),
	preload("res://UI/Court/minus.png"),
	preload("res://UI/Court/arrow-up.png"),
]
const FAVOR_LABELS := ["Not favored", "Neutral", "Favored"]

var court: Court
var _ruler: Label
var _favor: TextureRect


func _init(for_court: Court) -> void:
	court = for_court
	name = court.display_name.validate_node_name()
	horizontal_scroll_mode = SCROLL_MODE_DISABLED
	follow_focus = true
	focus_mode = FOCUS_ALL
	var gutter := MarginContainer.new()
	gutter.size_flags_horizontal = SIZE_EXPAND_FILL
	gutter.add_theme_constant_override(&"margin_right", 16)
	add_child(gutter)
	var page := VBoxContainer.new()
	page.size_flags_horizontal = SIZE_EXPAND_FILL
	page.add_theme_constant_override(&"separation", 24)
	gutter.add_child(page)
	var header := HBoxContainer.new()
	header.add_theme_constant_override(&"separation", 16)
	page.add_child(header)
	_ruler = _label(court.ruler_name, 26)
	_ruler.size_flags_horizontal = SIZE_EXPAND_FILL
	header.add_child(_ruler)
	_favor = TextureRect.new()
	_favor.custom_minimum_size = Vector2(32, 32)
	_favor.size_flags_vertical = SIZE_SHRINK_CENTER
	_favor.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_favor.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_favor.texture = FAVOR_ICONS[court.favor]
	_favor.tooltip_text = "Favor: %s" % FAVOR_LABELS[court.favor]
	header.add_child(_favor)
	page.add_child(_section("Description & Information", court.description))
	page.add_child(_section("Gain Favor By:", _bullets(court.gain_favor_by)))
	page.add_child(_section("Lose Favor By:", _bullets(court.lose_favor_by)))


func focus_selection() -> bool:
	grab_focus()
	return true


static func _section(title: String, text: String) -> VBoxContainer:
	var section := VBoxContainer.new()
	section.add_theme_constant_override(&"separation", 12)
	section.add_child(_label(title, 21))
	var body := _label(text, 17)
	body.add_theme_color_override(&"font_color", ItemBrowser.TEXT_COLOR)
	section.add_child(body)
	return section


static func _label(text: String, font_size: int) -> Label:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override(&"font_size", font_size)
	return label


static func _bullets(items: Array[String]) -> String:
	if items.is_empty():
		return "• none"
	var lines := PackedStringArray()
	for item in items:
		lines.append("• %s" % item)
	return "\n".join(lines)
