## The [SquadMenu]'s one tab: the roster, as the pause menu's Roster tab
## shows it, and along the bottom a footer for choosing who fights.
##
## A double-click on a character (or Enter, Space or A on one) ticks them, or
## unticks them, up to [constant Campaign.SQUAD_SIZE]; with that many ticked,
## another is refused until one is unticked. The footer says so and counts
## them, and its [HoldButton] starts the battle once held, greyed out while
## nobody is ticked. Single clicks still pick whose pages show, and their
## equipment can still be changed: the battle has not begun. The footer's note
## names the gamepad's A while the gamepad is in use.
class_name SquadTab
extends VBoxContainer

## Start was held: [param chosen] are to fight.
signal started(chosen: Array[Character])

const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const TEXT_COLOR := Color(0.7, 0.72, 0.78)
const HINT := "Double click a character to select them for combat. %d / %d characters selected."
const GAMEPAD_HINT := "Press A on a character to select them for combat. %d / %d characters selected."

var _browser: CharacterBrowser
var _note: Label
var _start: HoldButton
## Who is ticked, in the order they were.
var _chosen: Array[Character] = []


func _init() -> void:
	name = "Roster"
	add_theme_constant_override(&"separation", 12)

	_browser = CharacterBrowser.new()
	_browser.size_flags_vertical = SIZE_EXPAND_FILL
	_browser.character_activated.connect(_toggle)
	add_child(_browser)

	# The footer, laid out as the shops' purchase bar: a rule, then the note
	# on the left and the button on the right.
	var rule := HSeparator.new()
	var line := StyleBoxLine.new()
	line.color = BORDER_COLOR
	rule.add_theme_stylebox_override(&"separator", line)
	add_child(rule)

	var row := HBoxContainer.new()
	row.add_theme_constant_override(&"separation", 10)
	add_child(row)
	_note = Label.new()
	_note.size_flags_horizontal = SIZE_EXPAND_FILL
	_note.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_note.add_theme_font_size_override(&"font_size", 16)
	_note.add_theme_color_override(&"font_color", TEXT_COLOR)
	row.add_child(_note)
	_start = HoldButton.new()
	_start.caption = "Start"
	_start.held.connect(_on_start_held)
	row.add_child(_start)


## Shows [param characters], in order, with those of them in [param ticked]
## ticked, as many as fit.
func show_roster(characters: Array[Character], ticked: Array[Character]) -> void:
	_chosen.clear()
	for character in ticked:
		if characters.has(character) and _chosen.size() < Campaign.SQUAD_SIZE:
			_chosen.append(character)
	_browser.show_characters(characters)
	_refresh()


func _ready() -> void:
	InputDevice.watch(_refresh.unbind(1))


## What A does on a character, for the gamepad's prompts ([TabbedMenu]):
## ticks or unticks them, or nothing with the squad full.
func gamepad_hint(focused: Control) -> Array:
	var button := focused as CharacterButton
	if button == null:
		return []
	if _chosen.has(button.character):
		return [[&"A"], "Untick"]
	return [[&"A"], "Tick"] if _chosen.size() < Campaign.SQUAD_SIZE else []


## Gives the Start button the keyboard, to be held there. False while it is
## greyed out.
func focus_start() -> bool:
	if _start.disabled:
		return false
	_start.grab_focus()
	return true


## Whether the Start button has the keyboard.
func is_start_focused() -> bool:
	return _start.has_focus()


## Moves the keyboard to the selected character, coming down from the menu's
## tab. False when there is nobody.
func focus_selection() -> bool:
	return _browser.focus_selection()


func _toggle(character: Character) -> void:
	if _chosen.has(character):
		_chosen.erase(character)
	elif _chosen.size() < Campaign.SQUAD_SIZE:
		_chosen.append(character)
	else:
		return
	_refresh()


func _refresh() -> void:
	_browser.show_ticks(_chosen)
	_note.text = (GAMEPAD_HINT if InputDevice.gamepad else HINT) % [_chosen.size(), Campaign.SQUAD_SIZE]
	_start.disabled = _chosen.is_empty()


func _on_start_held() -> void:
	if not _chosen.is_empty():
		started.emit(_chosen.duplicate())
