## The village menu's tab for a [HiringBoard]: who is for hire there, shown
## as the Roster tab shows the party but read only, and along the bottom a
## [PurchaseBar] that hires the selected character for their
## [member Character.hire_cost]. Hired, they leave the board for the end of
## the roster.
##
## Filled from [method Campaign.for_hire] as it enters the tree, which is each
## time the village menu opens, since the menu makes its tabs afresh.
class_name HiringBoardTab
extends VBoxContainer

const TEXT_COLOR := Color(0.7, 0.72, 0.78)

var board: HiringBoard

var _browser: CharacterBrowser
var _empty: Label
var _bar: PurchaseBar


func _init(for_board: HiringBoard) -> void:
	board = for_board
	name = board.display_name.validate_node_name()
	add_theme_constant_override(&"separation", 12)

	_browser = CharacterBrowser.new(true)
	_browser.size_flags_vertical = SIZE_EXPAND_FILL
	_browser.character_selected.connect(_on_character_selected.unbind(1))
	add_child(_browser)

	_empty = Label.new()
	_empty.text = "No one here is looking for work."
	_empty.size_flags_vertical = SIZE_EXPAND_FILL
	_empty.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_empty.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_empty.add_theme_font_size_override(&"font_size", 22)
	_empty.add_theme_color_override(&"font_color", TEXT_COLOR)
	add_child(_empty)

	_bar = PurchaseBar.new()
	_bar.held.connect(_on_hire_held)
	add_child(_bar)


func _ready() -> void:
	_show_board()


## Moves the keyboard to the selected character, coming down from the village
## menu's tabs. False when no one is for hire.
func focus_selection() -> bool:
	return _browser.focus_selection()


func _show_board() -> void:
	var characters := Campaign.for_hire(board)
	_browser.visible = not characters.is_empty()
	_empty.visible = characters.is_empty()
	_browser.show_characters(characters)


func _on_character_selected() -> void:
	var character := _browser.selected
	if character == null:
		_bar.show_no_offer()
	else:
		_bar.show_offer("Hire", character.display_name, character.hire_cost)


func _on_hire_held() -> void:
	var character := _browser.selected
	if character == null or not Campaign.hire(board, character):
		return
	_bar.news = "%s joined the roster." % character.display_name
	_show_board()
