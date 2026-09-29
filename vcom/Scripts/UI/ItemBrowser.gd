## The view the Inventory sub-tabs share: a grid of squares on the left, one
## per stack, and the selected item's name and description on the right.
## Split evenly down the middle, each half scrolling on its own once its
## content outgrows it.
##
## Given stacks by [method show_stacks]; it only shows them and never changes
## the inventory.
class_name ItemBrowser
extends HBoxContainer

const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const TEXT_COLOR := Color(0.85, 0.86, 0.9)
const MUTED_COLOR := Color(0.55, 0.56, 0.62)

## What the right side says when there are no stacks to show.
var empty_text := "Nothing here."

var _grid: HFlowContainer
var _details_scroll: ScrollContainer
var _group := ButtonGroup.new()
var _name_label: Label
var _description_label: Label


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
	# Keeps the text off the scrollbar when a long description brings it up.
	var gutter := MarginContainer.new()
	gutter.size_flags_horizontal = SIZE_EXPAND_FILL
	gutter.add_theme_constant_override(&"margin_right", 16)
	gutter.add_child(details)
	_details_scroll = _scroller(gutter)
	add_child(_details_scroll)


## Fills the grid with [param stacks], in order, and selects the first.
func show_stacks(stacks: Array[ItemStack]) -> void:
	for square in _grid.get_children():
		_grid.remove_child(square)
		square.queue_free()
	for stack in stacks:
		var square := ItemSquare.new(stack, _group)
		# Toggled rather than the group's pressed, which a selection made in
		# code does not send.
		square.toggled.connect(func(on: bool) -> void:
			if on:
				_show(stack))
		_grid.add_child(square)
	_chain_squares()
	if stacks.is_empty():
		_show(null)
	else:
		# Without taking focus: the keyboard stays on the tabs until it comes
		# down into the grid.
		(_grid.get_child(0) as ItemSquare).button_pressed = true


## Moves the keyboard to the selected square. False when there is none.
func focus_selection() -> bool:
	var square := _group.get_pressed_button()
	if square == null:
		return false
	square.grab_focus()
	return true


## Left and right step through the squares in reading order, wrapping to the
## row above or below, and stop at the first and last rather than leaving
## the grid for whatever lies beside it (the tab rows, by distance).
func _chain_squares() -> void:
	var squares := _grid.get_children()
	for i in squares.size():
		var square := squares[i] as Control
		var before: Node = squares[i - 1] if i > 0 else square
		var after: Node = squares[i + 1] if i + 1 < squares.size() else square
		square.focus_neighbor_left = square.get_path_to(before)
		square.focus_neighbor_right = square.get_path_to(after)


func _show(stack: ItemStack) -> void:
	_details_scroll.scroll_vertical = 0
	if stack == null:
		_name_label.text = ""
		_description_label.text = empty_text
		_description_label.add_theme_color_override(&"font_color", MUTED_COLOR)
		return
	_name_label.text = stack.item.display_name
	_description_label.text = stack.item.description
	_description_label.add_theme_color_override(&"font_color", TEXT_COLOR)


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
