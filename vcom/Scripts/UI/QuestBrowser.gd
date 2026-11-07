## A quest list and independently scrolling details, sharing the item browser's
## typography and colors. The list takes one third of the available width.
class_name QuestBrowser
extends HBoxContainer

signal selection_changed
signal quest_activated

var selected: Quest
var _list: VBoxContainer
var _group := ButtonGroup.new()
var _details_scroll: ScrollContainer
var _title: Label
var _details: Label
var _empty: Label


func _init(title: String) -> void:
	name = title
	add_theme_constant_override(&"separation", 24)
	_list = VBoxContainer.new()
	_list.size_flags_horizontal = SIZE_EXPAND_FILL
	_list.add_theme_constant_override(&"separation", 8)
	_empty = Label.new()
	_empty.text = "No %s." % title.to_lower()
	_empty.add_theme_color_override(&"font_color", ItemBrowser.MUTED_COLOR)
	_list.add_child(_empty)
	add_child(ItemBrowser._scroller(_list))
	var divider := VSeparator.new()
	var line := StyleBoxLine.new()
	line.color = ItemBrowser.BORDER_COLOR
	line.vertical = true
	divider.add_theme_stylebox_override(&"separator", line)
	add_child(divider)
	var details := VBoxContainer.new()
	details.size_flags_horizontal = SIZE_EXPAND_FILL
	details.add_theme_constant_override(&"separation", 12)
	_title = Label.new()
	_title.add_theme_font_size_override(&"font_size", 26)
	_title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	details.add_child(_title)
	_details = Label.new()
	_details.add_theme_font_size_override(&"font_size", 17)
	_details.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	details.add_child(_details)
	var gutter := MarginContainer.new()
	gutter.size_flags_horizontal = SIZE_EXPAND_FILL
	gutter.add_theme_constant_override(&"margin_right", 16)
	gutter.add_child(details)
	_details_scroll = ItemBrowser._scroller(gutter)
	_details_scroll.size_flags_stretch_ratio = 2.0
	add_child(_details_scroll)
	_show(null)


func show_quests(quests: Array[Quest]) -> void:
	var keep := selected
	var had_focus := false
	for child in _list.get_children():
		if child == _empty:
			continue
		had_focus = had_focus or child.has_focus()
		(child as Button).button_group = null
		_list.remove_child(child)
		child.queue_free()
	var pick: Button = null
	var buttons: Array[Button] = []
	for quest in quests:
		if quest == null:
			continue
		var button := Button.new()
		button.text = quest.title
		button.tooltip_text = quest.title
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.clip_text = true
		button.custom_minimum_size.y = 44
		button.toggle_mode = true
		button.button_group = _group
		button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		button.add_theme_font_size_override(&"font_size", 17)
		button.add_theme_color_override(&"font_color", ItemBrowser.TEXT_COLOR)
		button.add_theme_color_override(&"font_pressed_color", ItemBrowser.ACCENT_COLOR)
		button.add_theme_color_override(&"font_hover_pressed_color", ItemBrowser.ACCENT_COLOR)
		button.add_theme_stylebox_override(&"normal", ItemSquare._style(ItemBrowser.BUTTON_BG_COLOR, ItemBrowser.BORDER_COLOR, 1))
		button.add_theme_stylebox_override(&"hover", ItemSquare._style(ItemBrowser.BUTTON_HOVER_COLOR, ItemBrowser.BORDER_COLOR, 1))
		button.add_theme_stylebox_override(&"pressed", ItemSquare._style(ItemBrowser.BUTTON_HOVER_COLOR, ItemBrowser.ACCENT_COLOR, 2))
		button.add_theme_stylebox_override(&"hover_pressed", button.get_theme_stylebox(&"pressed"))
		button.add_theme_stylebox_override(&"focus", ItemBrowser._button_style(Color.TRANSPARENT, Color.WHITE))
		button.focus_entered.connect(func() -> void: button.button_pressed = true)
		button.gui_input.connect(func(event: InputEvent) -> void:
			if event.is_action_pressed(&"ui_accept"):
				quest_activated.emit()
				button.accept_event())
		button.toggled.connect(func(on: bool) -> void:
			if on:
				_show(quest))
		_list.add_child(button)
		buttons.append(button)
		if pick == null or quest == keep:
			pick = button
	for i in buttons.size():
		var button := buttons[i]
		if i > 0:
			button.focus_neighbor_top = button.get_path_to(buttons[i - 1])
		button.focus_neighbor_bottom = button.get_path_to(buttons[mini(i + 1, buttons.size() - 1)])
	_empty.visible = pick == null
	if pick == null:
		_show(null)
	else:
		pick.button_pressed = true
		if had_focus:
			pick.grab_focus()


func focus_selection() -> bool:
	var button := _group.get_pressed_button()
	if button == null:
		return false
	button.grab_focus()
	return true


func _show(quest: Quest) -> void:
	selected = quest
	_details_scroll.scroll_vertical = 0
	_title.visible = quest != null
	_title.text = quest.title if quest != null else ""
	_details.text = _description(quest) if quest != null else "Quest details will appear here."
	_details.add_theme_color_override(&"font_color", ItemBrowser.TEXT_COLOR if quest != null else ItemBrowser.MUTED_COLOR)
	selection_changed.emit()


static func _description(quest: Quest) -> String:
	return "Type: %s\n\n%s\n\nStatus: %s\nQuest giver: %s\nLocation: %s\n\nObjectives\n%s\n\nRewards\n%s" % [
		["Main Quest", "Major Quest", "Minor Quest"][quest.category],
		quest.description,
		quest.status,
		quest.quest_giver if not quest.quest_giver.is_empty() else "Unknown",
		quest.location if not quest.location.is_empty() else "Unknown",
		quest.objectives if not quest.objectives.is_empty() else "No objectives listed.",
		quest.rewards if not quest.rewards.is_empty() else "No rewards listed.",
	]
