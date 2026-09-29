## A village menu's tab for one [Location]. A placeholder until the locations
## do something: the location's description in the middle, the way the pause
## menu's Campaign tab shows its placeholder line.
class_name LocationTab
extends Control

const TEXT_COLOR := Color(0.7, 0.72, 0.78)

var location: Location


func _init(for_location: Location) -> void:
	location = for_location
	name = location.display_name.validate_node_name()

	var message := Label.new()
	message.text = location.description
	message.set_anchors_preset(PRESET_FULL_RECT)
	message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	message.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	message.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	message.add_theme_font_size_override(&"font_size", 22)
	message.add_theme_color_override(&"font_color", TEXT_COLOR)
	add_child(message)
