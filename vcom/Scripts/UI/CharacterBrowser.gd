## A strip of characters across the top, and under it sub-tabs of
## [CharacterPage]s about whichever character is selected: the Roster tab, and
## a hiring board's view of who is for hire. The strip is kept short to leave
## the pages the room; it is centred, and scrolls sideways once there are more
## characters than fit across the panel.
##
## Changing character keeps the open sub-tab, so characters can be compared
## page by page; showing a new list goes back to the first.
##
## Read only, for characters not on the roster, the pages show the
## characters without the means to change them.
class_name CharacterBrowser
extends VBoxContainer

## The character now selected, null once there is none to select.
signal character_selected(character: Character)

## The character now selected, or null when there are none.
var selected: Character

var _strip: HBoxContainer
var _group := ButtonGroup.new()
var _pages: SubTabs


func _init(read_only := false) -> void:
	add_theme_constant_override(&"separation", 12)

	_strip = HBoxContainer.new()
	# Filling the scroller's width is what lets a short strip sit centred; a
	# long one is wider than the scroller and scrolls instead.
	_strip.size_flags_horizontal = SIZE_EXPAND_FILL
	_strip.alignment = BoxContainer.ALIGNMENT_CENTER
	_strip.add_theme_constant_override(&"separation", 8)

	var scroll := ScrollContainer.new()
	scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	scroll.add_child(_strip)
	add_child(scroll)

	_pages = SubTabs.new()
	_pages.size_flags_vertical = SIZE_EXPAND_FILL
	_pages.add_child(DetailsPage.new())
	_pages.add_child(EquipmentPage.new())
	_pages.add_child(SkillsPage.new())
	for page in _pages.get_children():
		(page as CharacterPage).read_only = read_only
	_pages.get_tab_bar().gui_input.connect(_on_pages_bar_input)
	add_child(_pages)


## Fills the strip with [param characters], in order, and selects the first,
## on the first page.
func show_characters(characters: Array[Character]) -> void:
	for button in _strip.get_children():
		_strip.remove_child(button)
		button.queue_free()
	for character in characters:
		if character == null:
			continue
		var button := CharacterButton.new(character, _group)
		# Toggled rather than the group's pressed, which a selection made in
		# code does not send.
		button.toggled.connect(func(on: bool) -> void:
			if on:
				_show_character(character))
		_strip.add_child(button)
	FocusChain.link(_strip.get_children())
	_pages.current_tab = 0
	if _strip.get_child_count() > 0:
		# Without taking focus: the keyboard stays on the tabs until it comes
		# down into the strip.
		(_strip.get_child(0) as CharacterButton).button_pressed = true
	else:
		_show_character(null)


## Moves the keyboard to the selected character. False when there is none.
func focus_selection() -> bool:
	var button := _group.get_pressed_button()
	if button == null:
		return false
	button.grab_focus()
	return true


func _show_character(character: Character) -> void:
	selected = character
	for page in _pages.get_children():
		(page as CharacterPage).show_character(character)
	character_selected.emit(character)


## Up from the pages' tabs goes back to the selected character, not whichever
## one lies nearest the tabs; down goes where the open page says.
func _on_pages_bar_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_up") and focus_selection():
		_pages.get_tab_bar().accept_event()
	elif event.is_action_pressed(&"ui_down") and (_pages.get_current_tab_control() as CharacterPage).focus_selection():
		_pages.get_tab_bar().accept_event()
