## The pause menu's Campaign tab, the one it opens on: how the party is
## getting on. For now a placeholder line in the middle, and the party's gold
## in the bottom-right corner.
class_name CampaignTab
extends Control

const TEXT_COLOR := Color(0.7, 0.72, 0.78)
const CAPTION_COLOR := Color(0.55, 0.56, 0.62)
const GOLD_COLOR := Color(1.0, 0.9, 0.55)

var _gold: Label


func _init() -> void:
	name = "Campaign"

	var message := Label.new()
	message.text = "The party is on an adventure!"
	message.set_anchors_preset(PRESET_FULL_RECT)
	message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	message.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	message.add_theme_font_size_override(&"font_size", 22)
	message.add_theme_color_override(&"font_color", TEXT_COLOR)
	add_child(message)

	var purse := HBoxContainer.new()
	purse.add_theme_constant_override(&"separation", 10)
	# Held to its minimum size and grown up and left from the corner.
	purse.anchor_left = 1.0
	purse.anchor_top = 1.0
	purse.anchor_right = 1.0
	purse.anchor_bottom = 1.0
	purse.grow_horizontal = GROW_DIRECTION_BEGIN
	purse.grow_vertical = GROW_DIRECTION_BEGIN
	add_child(purse)
	var caption := Label.new()
	caption.text = "Gold"
	caption.add_theme_font_size_override(&"font_size", 17)
	caption.add_theme_color_override(&"font_color", CAPTION_COLOR)
	purse.add_child(caption)
	_gold = Label.new()
	_gold.add_theme_font_size_override(&"font_size", 22)
	_gold.add_theme_color_override(&"font_color", GOLD_COLOR)
	purse.add_child(_gold)


## Shows the party's [param gold]; the menu calls it on opening.
func show_gold(gold: int) -> void:
	_gold.text = str(gold)
