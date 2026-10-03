## A row of tabs across most of the window, over the game and pausing it while
## it is up: the frame the pause menu and the [VillageMenu] share, so the two
## look and handle alike.
##
## A tab is a [Control] added to [member tabs]; its node name is its title
## unless [method TabContainer.set_tab_title] gives it another. The first tab is
## the one the menu opens on. What opens and closes the menu is the subclass's
## to decide; anything that closes it on Esc must mark the event handled, or
## the pause menu opens on the same press.
##
## With the gamepad the d-pad or the left stick moves the keyboard's focus, A
## presses (ui_accept), LB / RB change tab and LT / RT the sub-tabs of the
## part of the tab the focus is in, and a row of prompts along the bottom
## ([ControlHints]) says so, with what A does on whatever has the focus. A
## subclass handling input in [method Node._unhandled_input] must call
## [code]super(event)[/code] first, as the tab keys are read there.
class_name TabbedMenu
extends CanvasLayer

signal opened
signal closed

## Over every HUD in either scene.
const LAYER := 100
## How much of the window the menu leaves clear on each side.
const MARGIN := Vector2(0.06, 0.08)

const DIM_COLOR := Color(0.0, 0.0, 0.0, 0.55)
const BG_COLOR := Color(0.1, 0.11, 0.15, 0.95)
const TAB_COLOR := Color(0.14, 0.15, 0.2, 0.95)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const TEXT_COLOR := Color(0.85, 0.86, 0.9)
## Pixels between the gamepad's prompts and the bottom of the window.
const HINTS_MARGIN := 10.0

var tabs: TabContainer

var _root: Control
## The gamepad's prompts along the bottom.
var _hints: ControlHints


func _init() -> void:
	layer = LAYER
	# Everything else stops while the menu is up; the menu must not.
	process_mode = PROCESS_MODE_ALWAYS

	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.visible = false
	add_child(_root)

	# Swallows clicks, so nothing behind the menu can be picked while it is up.
	var dim := ColorRect.new()
	dim.color = DIM_COLOR
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.add_child(dim)

	tabs = TabContainer.new()
	tabs.anchor_left = MARGIN.x
	tabs.anchor_right = 1.0 - MARGIN.x
	tabs.anchor_top = MARGIN.y
	tabs.anchor_bottom = 1.0 - MARGIN.y
	tabs.add_theme_stylebox_override(&"panel", _panel_style())
	tabs.add_theme_stylebox_override(&"tab_selected", _tab_style(BG_COLOR, ACCENT_COLOR))
	tabs.add_theme_stylebox_override(&"tab_hovered", _tab_style(TAB_COLOR.lightened(0.08), BORDER_COLOR))
	tabs.add_theme_stylebox_override(&"tab_unselected", _tab_style(TAB_COLOR, BORDER_COLOR))
	tabs.add_theme_stylebox_override(&"tab_focus", _focus_style())
	tabs.add_theme_color_override(&"font_selected_color", ACCENT_COLOR)
	tabs.add_theme_color_override(&"font_unselected_color", TEXT_COLOR)
	tabs.add_theme_color_override(&"font_hovered_color", Color.WHITE)
	tabs.add_theme_font_size_override(&"font_size", 20)
	tabs.get_tab_bar().gui_input.connect(_on_tab_bar_input)
	_root.add_child(tabs)

	_hints = ControlHints.new(false)
	_hints.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_hints.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_hints.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_hints.offset_top = -HINTS_MARGIN
	_hints.offset_bottom = -HINTS_MARGIN
	_root.add_child(_hints)


# What A does changes with the focus, which moves without telling anyone.
func _process(_delta: float) -> void:
	if is_open() and InputDevice.gamepad:
		_hints.show_hints(_gamepad_hints())


func _unhandled_input(event: InputEvent) -> void:
	if not is_open():
		return
	if event.is_action_pressed(&"menu_next_tab") or event.is_action_pressed(&"menu_previous_tab"):
		_step_tab(tabs, 1 if event.is_action_pressed(&"menu_next_tab") else -1)
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed(&"menu_next_subtab") or event.is_action_pressed(&"menu_previous_subtab"):
		var sub_tabs := _sub_tabs()
		if sub_tabs != null:
			_step_tab(sub_tabs, 1 if event.is_action_pressed(&"menu_next_subtab") else -1)
		get_viewport().set_input_as_handled()


func is_open() -> bool:
	return _root.visible


## Shows the menu on its first tab and pauses the game under it.
func open() -> void:
	if is_open():
		return
	_root.visible = true
	get_tree().paused = true
	tabs.current_tab = 0
	_refresh()
	# The tab row takes the keyboard: left and right change tab, down enters it.
	tabs.get_tab_bar().grab_focus()
	opened.emit()


## Hides the menu and lets the game carry on.
func close() -> void:
	if not is_open():
		return
	_root.visible = false
	get_tree().paused = false
	closed.emit()


## The gamepad's prompts: what moves the focus, what A does on what has it,
## the tab and sub-tab buttons where there is more than one, and how the menu
## closes ([method _close_hints]). Each row is [code][[buttons...], words][/code].
func _gamepad_hints() -> Array:
	var rows := [[[&"dpad"], "Move"]]
	var focused := get_viewport().gui_get_focus_owner()
	if focused != null and _root.is_ancestor_of(focused):
		var accept := _accept_hint(focused)
		if not accept.is_empty():
			rows.append(accept)
	if tabs.get_tab_count() > 1:
		rows.append([[&"LB", &"RB"], "Tab"])
	if _sub_tabs() != null:
		rows.append([[&"LT", &"RT"], "Sub-tab"])
	rows.append_array(_close_hints())
	return rows


## How the menu closes, as rows of prompts: B, unless a subclass says
## otherwise.
func _close_hints() -> Array:
	return [[[&"B"], "Close"]]


## What A does with [param focused]: what it says with a
## [code]gamepad_hint(focused)[/code] method returning a row, or an empty one
## for nothing (a skill that cannot be learned); else what the first control
## it is in with such a method says; else "Hold" and its caption
## on a [HoldButton], its text on any other button A presses ("Select" with
## none), and nothing on a button that the focus alone selects (a toggle: a
## character, a slot, an item) or on a tab row.
func _accept_hint(focused: Control) -> Array:
	if focused.has_method(&"gamepad_hint"):
		return focused.call(&"gamepad_hint", focused)
	var node: Node = focused.get_parent()
	while node != null and node != self:
		if node.has_method(&"gamepad_hint"):
			var row: Array = node.call(&"gamepad_hint", focused)
			if not row.is_empty():
				return row
		node = node.get_parent()
	var button := focused as BaseButton
	if button == null or button.disabled or button.toggle_mode:
		return []
	if button is HoldButton:
		return [[&"A"], "Hold: %s" % (button as HoldButton).caption]
	if button is Button and not (button as Button).text.is_empty():
		return [[&"A"], (button as Button).text]
	return [[&"A"], "Select"]


## The sub-tabs LT / RT change: those holding the focus, the innermost, else
## the first showing in the open tab. Null with none.
func _sub_tabs() -> TabContainer:
	var focused := get_viewport().gui_get_focus_owner()
	var node: Node = focused.get_parent() if focused != null and tabs.is_ancestor_of(focused) else null
	while node != null and node != tabs:
		if node is TabContainer and (node as TabContainer).get_tab_count() > 1:
			return node
		node = node.get_parent()
	return _first_sub_tabs(tabs.get_current_tab_control())


## [param under] if it is a row of tabs (the Inventory tab is one), else the
## first showing inside it, depth first. Null with none.
func _first_sub_tabs(under: Control) -> TabContainer:
	if under == null or not under.visible:
		return null
	if under is TabContainer and (under as TabContainer).get_tab_count() > 1:
		return under
	for child in under.get_children():
		var found := _first_sub_tabs(child as Control)
		if found != null:
			return found
	return null


## Moves [param row] [param step] tabs along, stopping at the ends, and gives
## its tab row the keyboard, as opening the menu gives the menu's own.
func _step_tab(row: TabContainer, step: int) -> void:
	var to := clampi(row.current_tab + step, 0, row.get_tab_count() - 1)
	if to != row.current_tab:
		row.current_tab = to
	row.get_tab_bar().grab_focus()


## Fills the tabs from the game's state as the menu opens, so that it never
## holds state of its own. Nothing to fill here.
func _refresh() -> void:
	pass


## Down from the tabs into a tab with a [code]focus_selection()[/code] goes
## where that says (the Roster's selected character), not to whatever lies
## nearest the middle of the tab row. It returns false when it has nothing to
## focus, and the keyboard then moves as usual.
func _on_tab_bar_input(event: InputEvent) -> void:
	if not event.is_action_pressed(&"ui_down"):
		return
	var tab := tabs.get_current_tab_control()
	if tab != null and tab.has_method(&"focus_selection") and tab.call(&"focus_selection"):
		tabs.get_tab_bar().accept_event()


static func _panel_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = BG_COLOR
	style.border_color = BORDER_COLOR
	style.set_border_width_all(1)
	style.set_corner_radius_all(4)
	style.corner_radius_top_left = 0
	style.set_content_margin_all(32)
	return style


## Shows which row of tabs the arrow keys move along, where a tab has a row
## of its own inside it.
static func _focus_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.draw_center = false
	style.border_color = Color(ACCENT_COLOR, 0.5)
	style.set_border_width_all(1)
	style.set_corner_radius_all(4)
	return style


## A tab with a bar of [param edge] along its top, the accent on the open one.
static func _tab_style(background: Color, edge: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = edge
	style.border_width_top = 2
	style.corner_radius_top_left = 4
	style.corner_radius_top_right = 4
	style.content_margin_left = 28
	style.content_margin_right = 28
	style.content_margin_top = 10
	style.content_margin_bottom = 10
	return style
