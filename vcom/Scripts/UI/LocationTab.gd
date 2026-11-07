## A village menu's tab for one [Location]. A placeholder until the locations
## do something: the location's description in the middle, the way the pause
## menu's Campaign tab shows its placeholder line.
class_name LocationTab
extends Control

const TEXT_COLOR := Color(0.7, 0.72, 0.78)

var location: Location


func _init(for_location: Location, heading: String = "") -> void:
	location = for_location
	name = location.display_name.validate_node_name()

	var content := VBoxContainer.new()
	content.set_anchors_preset(PRESET_FULL_RECT)
	content.add_theme_constant_override(&"separation", 24)
	add_child(content)
	if not heading.is_empty():
		var title := Label.new()
		title.text = heading
		title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		title.add_theme_font_size_override(&"font_size", 26)
		content.add_child(title)

	var message := Label.new()
	message.text = location.description
	message.size_flags_vertical = SIZE_EXPAND_FILL
	message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	message.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	message.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	message.add_theme_font_size_override(&"font_size", 22)
	message.add_theme_color_override(&"font_color", TEXT_COLOR)
	content.add_child(message)
