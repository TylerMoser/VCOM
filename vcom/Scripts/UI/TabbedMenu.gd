## A row of tabs across most of the window, over the game and pausing it while
## it is up: the frame the pause menu and the [VillageMenu] share, so the two
## look and handle alike.
##
## A tab is a [Control] added to [member tabs]; its node name is its title
## unless [method TabContainer.set_tab_title] gives it another. The first tab is
## the one the menu opens on. What opens and closes the menu is the subclass's
## to decide; anything that closes it on Esc must mark the event handled, or
## the pause menu opens on the same press.
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

var tabs: TabContainer

var _root: Control


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
