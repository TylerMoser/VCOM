## The one menu for the whole game, over the world map and combat alike: a
## row of tabs across most of the window, pausing the game behind it.
##
## An autoload, so it sits ahead of the current scene in the tree. Input
## reaches the scene first ([method Node._unhandled_input] runs in reverse tree
## order), so Esc backs out of whatever is in progress, such as a combat action
## or a village's menu, and only opens this menu once nothing is left to cancel.
##
## Its tabs are Campaign, Roster, Inventory and System, refilled from
## [code]Campaign[/code] (and the System tab from [code]TileGrid[/code] and
## [code]Blood[/code], whose button is greyed out in battle) each time it
## opens.
extends TabbedMenu

var _campaign: CampaignTab
var _roster: RosterTab
var _inventory: InventoryTab
var _system: SystemTab


func _init() -> void:
	super()
	_campaign = CampaignTab.new()
	tabs.add_child(_campaign)

	_roster = RosterTab.new()
	tabs.add_child(_roster)

	_inventory = InventoryTab.new()
	tabs.add_child(_inventory)

	_system = SystemTab.new()
	_system.return_requested.connect(close)
	tabs.add_child(_system)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"pause_menu"):
		if is_open():
			close()
		else:
			open()
		get_viewport().set_input_as_handled()


func _refresh() -> void:
	_campaign.show_gold(Campaign.gold)
	_roster.show_roster(Campaign.roster)
	_inventory.show_inventory(Campaign.inventory)
	_system.show_grid_state()
	_system.show_blood_state()
