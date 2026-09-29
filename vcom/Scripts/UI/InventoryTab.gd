## The pause menu's Inventory tab: a row of sub-tabs, one per kind of gear.
## Lighter than the menu's own tabs, an underline rather than a raised tab,
## so the two rows read as two levels. Each sub-tab is an [ItemBrowser] over
## one kind of item. Opens on its first sub-tab each time the menu does (see
## [method show_inventory]).
class_name InventoryTab
extends TabContainer

const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const TEXT_COLOR := Color(0.7, 0.72, 0.78)
const HOVER_COLOR := Color(0.18, 0.19, 0.25, 0.95)

var _weapons: ItemBrowser
var _battle_items: ItemBrowser


func _init() -> void:
	name = "Inventory"
	add_theme_stylebox_override(&"panel", _panel_style())
	add_theme_stylebox_override(&"tabbar_background", StyleBoxEmpty.new())
	add_theme_stylebox_override(&"tab_selected", _tab_style(Color.TRANSPARENT, ACCENT_COLOR))
	add_theme_stylebox_override(&"tab_hovered", _tab_style(HOVER_COLOR, Color.TRANSPARENT))
	add_theme_stylebox_override(&"tab_unselected", _tab_style(Color.TRANSPARENT, Color.TRANSPARENT))
	add_theme_stylebox_override(&"tab_focus", _focus_style())
	add_theme_color_override(&"font_selected_color", ACCENT_COLOR)
	add_theme_color_override(&"font_unselected_color", TEXT_COLOR)
	add_theme_color_override(&"font_hovered_color", Color.WHITE)
	add_theme_font_size_override(&"font_size", 17)

	_weapons = ItemBrowser.new("Weapons")
	_weapons.empty_text = "No weapons."
	add_child(_weapons)
	_battle_items = ItemBrowser.new("Battle Items")
	_battle_items.empty_text = "No battle items."
	add_child(_battle_items)

	get_tab_bar().gui_input.connect(_on_tab_bar_input)


## Lists what [param inventory] holds and goes back to the first sub-tab; the
## menu calls it on opening, so what it shows is never stale.
func show_inventory(inventory: Inventory) -> void:
	current_tab = 0
	_weapons.show_stacks(inventory.stacks_of(Weapon))
	_battle_items.show_stacks(inventory.stacks_of(BattleItem))


## Down from the sub-tabs goes to the selected square, not whichever square
## happens to lie nearest the middle of the row.
func _on_tab_bar_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_down") and (get_current_tab_control() as ItemBrowser).focus_selection():
		get_tab_bar().accept_event()


## A rule under the sub-tabs, dividing them from what they show.
static func _panel_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color.TRANSPARENT
	style.border_color = BORDER_COLOR
	style.border_width_top = 1
	style.content_margin_top = 20
	return style


## A sub-tab underlined in [param edge], the accent on the open one.
static func _tab_style(background: Color, edge: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = edge
	style.border_width_bottom = 2
	style.corner_radius_top_left = 3
	style.corner_radius_top_right = 3
	style.content_margin_left = 18
	style.content_margin_right = 18
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	return style


## Shows which row the arrow keys move along, with the menu's own tabs also
## able to hold the keyboard.
static func _focus_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.draw_center = false
	style.border_color = Color(ACCENT_COLOR, 0.5)
	style.set_border_width_all(1)
	style.set_corner_radius_all(3)
	return style
