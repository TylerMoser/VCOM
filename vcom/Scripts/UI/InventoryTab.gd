## The pause menu's Inventory tab: a row of sub-tabs, one per kind of gear,
## each an [ItemBrowser] over one kind of item. Opens on its first sub-tab
## each time the menu does (see [method show_inventory]), and keeps up with
## the inventory while the menu is open, as when the Roster equips something.
##
## A [Market]'s tab shows its stock in one too.
class_name InventoryTab
extends SubTabs

## What [method selected_stack] gives may have changed: another square was
## picked, another sub-tab opened, or the inventory changed under it.
signal selection_changed

var _weapons: ItemBrowser
var _armor: ItemBrowser
var _battle_items: ItemBrowser
var _inventory: Inventory


func _init() -> void:
	super()
	name = "Inventory"

	_weapons = ItemBrowser.new("Weapons")
	_weapons.empty_text = "No weapons."
	add_child(_weapons)
	_armor = ItemBrowser.new("Armor")
	_armor.empty_text = "No armor."
	add_child(_armor)
	_battle_items = ItemBrowser.new("Battle Items")
	_battle_items.empty_text = "No battle items."
	add_child(_battle_items)

	for browser: ItemBrowser in [_weapons, _armor, _battle_items]:
		browser.selection_changed.connect(selection_changed.emit.unbind(1))
	tab_changed.connect(selection_changed.emit.unbind(1))
	get_tab_bar().gui_input.connect(_on_tab_bar_input)


## Lists what [param inventory] holds and goes back to the first sub-tab; the
## menu calls it on opening, so what it shows is never stale.
func show_inventory(inventory: Inventory) -> void:
	current_tab = 0
	if _inventory != inventory:
		if _inventory != null:
			_inventory.changed.disconnect(_fill)
		_inventory = inventory
		_inventory.changed.connect(_fill)
	_fill()


## The stack selected on the open sub-tab, or null when it has none.
func selected_stack() -> ItemStack:
	return (get_current_tab_control() as ItemBrowser).selected


## Lists what the inventory holds now, keeping each sub-tab's selection.
func _fill() -> void:
	_weapons.show_stacks(_inventory.stacks_of(Weapon))
	_armor.show_stacks(_inventory.stacks_of(Armor))
	_battle_items.show_stacks(_inventory.stacks_of(BattleItem))


## Down from the sub-tabs goes to the selected square, not whichever square
## happens to lie nearest the middle of the row.
func _on_tab_bar_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_down") and (get_current_tab_control() as ItemBrowser).focus_selection():
		get_tab_bar().accept_event()
