## The pause menu's Inventory tab: a row of sub-tabs, one per kind of gear,
## each an [ItemBrowser] over one kind of item. Opens on its first sub-tab
## each time the menu does (see [method show_inventory]), and keeps up with
## the inventory while the menu is open, as when the Roster equips something.
class_name InventoryTab
extends SubTabs

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
