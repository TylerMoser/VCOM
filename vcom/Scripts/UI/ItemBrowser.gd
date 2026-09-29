## The view the Inventory sub-tabs share: a grid of squares on the left, one
## per stack, and the selected item's name and description on the right.
## Split evenly down the middle, each half scrolling on its own once its
## content outgrows it.
##
## Given stacks by [method show_stacks]; it only shows them and never changes
## the inventory. A browser given an action ([method set_action], such as the
## Equipment page's Equip) shows a button for it under the description, and
## asks for it on the selected stack with [signal action_requested]; Enter or
## a double-click on a square asks too.
class_name ItemBrowser
extends HBoxContainer

signal action_requested(stack: ItemStack)

const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const TEXT_COLOR := Color(0.85, 0.86, 0.9)
const MUTED_COLOR := Color(0.55, 0.56, 0.62)
const BUTTON_BG_COLOR := Color(0.14, 0.15, 0.2, 0.95)
const BUTTON_HOVER_COLOR := Color(0.18, 0.19, 0.25, 0.95)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)

## What the right side says when there are no stacks to show.
var empty_text := "Nothing here."

var _grid: HFlowContainer
var _details_scroll: ScrollContainer
var _group := ButtonGroup.new()
var _name_label: Label
var _description_label: Label
var _action: Button
## The stack whose description is showing.
var _selected: ItemStack


func _init(title: String) -> void:
	name = title
	add_theme_constant_override(&"separation", 24)

	_grid = HFlowContainer.new()
	_grid.size_flags_horizontal = SIZE_EXPAND_FILL
	_grid.add_theme_constant_override(&"h_separation", 8)
	_grid.add_theme_constant_override(&"v_separation", 8)
	add_child(_scroller(_grid))

	var divider := VSeparator.new()
	var line := StyleBoxLine.new()
	line.color = BORDER_COLOR
	line.vertical = true
	divider.add_theme_stylebox_override(&"separator", line)
	add_child(divider)

	var details := VBoxContainer.new()
	details.size_flags_horizontal = SIZE_EXPAND_FILL
	details.add_theme_constant_override(&"separation", 12)
	_name_label = Label.new()
	_name_label.add_theme_font_size_override(&"font_size", 26)
	_name_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	details.add_child(_name_label)
	_description_label = Label.new()
	_description_label.add_theme_font_size_override(&"font_size", 17)
	_description_label.add_theme_color_override(&"font_color", TEXT_COLOR)
	_description_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	details.add_child(_description_label)
	_action = _action_button()
	details.add_child(_action)
	# Keeps the text off the scrollbar when a long description brings it up.
	var gutter := MarginContainer.new()
	gutter.size_flags_horizontal = SIZE_EXPAND_FILL
	gutter.add_theme_constant_override(&"margin_right", 16)
	gutter.add_child(details)
	_details_scroll = _scroller(gutter)
	add_child(_details_scroll)


## Fills the grid with [param stacks], in order. The item that was selected
## stays selected if it is still there, as after equipping one of several;
## otherwise the first is. The keyboard stays in the grid if it was there.
func show_stacks(stacks: Array[ItemStack]) -> void:
	var keep: Item = _selected.item if _selected != null else null
	var had_focus := false
	for square in _grid.get_children():
		had_focus = had_focus or square.has_focus()
		_grid.remove_child(square)
		square.queue_free()
	var pick: ItemSquare = null
	for stack in stacks:
		var square := ItemSquare.new(stack, _group)
		# Toggled rather than the group's pressed, which a selection made in
		# code does not send.
		square.toggled.connect(func(on: bool) -> void:
			if on:
				_show(stack))
		square.activated.connect(func() -> void:
			if _action.visible and not _action.disabled:
				action_requested.emit(stack))
		_grid.add_child(square)
		if pick == null or (stack.item == keep and pick.stack.item != keep):
			pick = square
	FocusChain.link(_grid.get_children())
	if pick == null:
		_show(null)
		return
	# Without taking focus unless the grid had it: otherwise the keyboard
	# stays where it is until it comes down into the grid.
	pick.button_pressed = true
	if had_focus:
		pick.grab_focus()


## Gives the browser an action on the selected stack, shown as a button with
## [param text] under its description. An empty text takes it away.
func set_action(text: String) -> void:
	_action.text = text
	_action.visible = not text.is_empty() and _selected != null


## Whether the action can be taken now; its button is greyed out otherwise.
## It never can with nothing selected.
func set_action_enabled(enabled: bool) -> void:
	_action.set_meta(&"enabled", enabled)
	_action.disabled = not enabled or _selected == null


## Moves the keyboard to the selected square. False when there is none.
func focus_selection() -> bool:
	var square := _group.get_pressed_button()
	if square == null:
		return false
	square.grab_focus()
	return true


func _show(stack: ItemStack) -> void:
	_selected = stack
	_details_scroll.scroll_vertical = 0
	# With nothing to show there is nothing to act on, and no name to leave
	# a blank line above the empty text.
	_action.visible = not _action.text.is_empty() and stack != null
	_action.disabled = stack == null or not _action.get_meta(&"enabled", true)
	_name_label.visible = stack != null
	if stack == null:
		_name_label.text = ""
		_description_label.text = empty_text
		_description_label.add_theme_color_override(&"font_color", MUTED_COLOR)
		return
	_name_label.text = stack.item.display_name
	_description_label.text = stack.item.description
	_description_label.add_theme_color_override(&"font_color", TEXT_COLOR)


func _action_button() -> Button:
	var button := Button.new()
	button.visible = false
	button.custom_minimum_size = Vector2(160, 40)
	button.size_flags_horizontal = SIZE_SHRINK_BEGIN
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.add_theme_font_size_override(&"font_size", 17)
	button.add_theme_stylebox_override(&"normal", _button_style(BUTTON_BG_COLOR, ACCENT_COLOR))
	button.add_theme_stylebox_override(&"hover", _button_style(BUTTON_HOVER_COLOR, ACCENT_COLOR))
	button.add_theme_stylebox_override(&"pressed", _button_style(BUTTON_HOVER_COLOR, ACCENT_COLOR))
	button.add_theme_stylebox_override(&"focus", _button_style(Color.TRANSPARENT, Color.WHITE))
	button.add_theme_stylebox_override(&"disabled", _button_style(BUTTON_BG_COLOR, BORDER_COLOR))
	button.add_theme_color_override(&"font_disabled_color", MUTED_COLOR)
	button.pressed.connect(func() -> void:
		if _selected != null:
			action_requested.emit(_selected))
	return button


static func _button_style(background: Color, edge: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = edge
	style.set_border_width_all(1)
	style.set_corner_radius_all(4)
	return style


## One half of the view: as wide as the other, scrolling down only, and only
## once [param content] is taller than the half.
static func _scroller(content: Control) -> ScrollContainer:
	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = SIZE_EXPAND_FILL
	scroll.size_flags_stretch_ratio = 1.0
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	# Keeps the square the arrow keys land on in view.
	scroll.follow_focus = true
	scroll.add_child(content)
	return scroll
