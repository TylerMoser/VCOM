## The journal layout with a fixed bottom-right acceptance button.
class_name QuestBoardTab
extends VBoxContainer

var board: QuestBoard
var _quests: QuestBrowser
var _accept: Button
var _note: Label


func _init(for_board: QuestBoard) -> void:
	board = for_board
	name = board.display_name.validate_node_name()
	add_theme_constant_override(&"separation", 12)
	_quests = QuestBrowser.new("Quests")
	_quests.size_flags_vertical = SIZE_EXPAND_FILL
	add_child(_quests)
	var rule := HSeparator.new()
	var line := StyleBoxLine.new()
	line.color = ItemBrowser.BORDER_COLOR
	rule.add_theme_stylebox_override(&"separator", line)
	add_child(rule)
	var row := HBoxContainer.new()
	row.add_theme_constant_override(&"separation", 16)
	add_child(row)
	_note = Label.new()
	_note.size_flags_horizontal = SIZE_EXPAND_FILL
	_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_note.add_theme_color_override(&"font_color", ItemBrowser.TEXT_COLOR)
	row.add_child(_note)
	_accept = Button.new()
	_accept.text = "Accept Quest"
	_accept.custom_minimum_size = Vector2(180, 44)
	_accept.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_accept.add_theme_font_size_override(&"font_size", 17)
	_accept.add_theme_stylebox_override(&"normal", ItemSquare._style(ItemBrowser.BUTTON_BG_COLOR, ItemBrowser.ACCENT_COLOR, 1))
	_accept.add_theme_stylebox_override(&"hover", ItemSquare._style(ItemBrowser.BUTTON_HOVER_COLOR, ItemBrowser.ACCENT_COLOR, 1))
	_accept.add_theme_stylebox_override(&"pressed", ItemSquare._style(ItemBrowser.BUTTON_HOVER_COLOR, ItemBrowser.ACCENT_COLOR, 2))
	_accept.add_theme_stylebox_override(&"focus", ItemBrowser._button_style(Color.TRANSPARENT, Color.WHITE))
	_accept.add_theme_stylebox_override(&"disabled", ItemSquare._style(ItemBrowser.BUTTON_BG_COLOR, ItemBrowser.BORDER_COLOR, 1))
	_accept.add_theme_color_override(&"font_disabled_color", ItemBrowser.MUTED_COLOR)
	row.add_child(_accept)
	_accept.pressed.connect(_on_accept)
	_quests.selection_changed.connect(_update_action)
	_quests.quest_activated.connect(func() -> void:
		if not _accept.disabled:
			_accept.grab_focus())


func _ready() -> void:
	_quests.show_quests(Campaign.quests_on(board))
	_update_action()


func focus_selection() -> bool:
	return _quests.focus_selection()


func gamepad_hint(focused: Control) -> Array:
	if focused is Button and _quests.is_ancestor_of(focused) and not _accept.disabled:
		return [[&"A"], "Choose"]
	return []


func _update_action() -> void:
	_accept.disabled = _quests.selected == null or Campaign.in_mission
	var selected_button := _quests._group.get_pressed_button()
	_accept.focus_neighbor_top = NodePath()
	if selected_button != null:
		_accept.focus_neighbor_top = _accept.get_path_to(selected_button)


func _on_accept() -> void:
	var quest := _quests.selected
	if not Campaign.accept_quest(board, quest):
		return
	_note.text = "Accepted %s." % quest.title
	_quests.show_quests(Campaign.quests_on(board))
	# Move off the action after accepting: another press chooses the next
	# quest before it can accept. An empty board returns to the settlement tabs.
	if not _quests.focus_selection():
		var parent := get_parent() as TabContainer
		if parent != null:
			parent.get_tab_bar().grab_focus()

