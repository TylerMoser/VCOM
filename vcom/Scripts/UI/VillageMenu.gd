## A village's own menu: a tab for each [Location] in it, in the order its
## [member Destination.locations] lists them. Framed and pausing like the pause
## menu.
##
## A left click (select_unit, as a unit is picked in combat) on the icon of
## the village the party is standing in opens it; a village with nothing in it
## does not open. The tabs are made afresh each time, since every village has
## its own mix. Esc closes it. Being in the scene, after the pause menu's
## autoload in the tree, it sees Esc first and takes it, so the pause menu does
## not open on the same press.
class_name VillageMenu
extends TabbedMenu

## Only a village the party is in opens.
@export var party_path: NodePath = ^"../Party"

var _party: Party


func _ready() -> void:
	_party = get_node_or_null(party_path) as Party
	if _party == null:
		push_error("VillageMenu: no Party at '%s'; no village can be entered." % party_path)


func _unhandled_input(event: InputEvent) -> void:
	if is_open():
		if event.is_action_pressed(&"cancel_action"):
			close()
			get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed(&"select_unit") and event is InputEventMouseButton and _party != null:
		var village := Destination.find_under_mouse(get_tree())
		if village != null and _party.is_at(village) and open_village(village):
			get_viewport().set_input_as_handled()


## Opens on the first of [param village]'s locations, with a tab for each.
## False, opening nothing, when it has none or the menu is already open.
func open_village(village: Destination) -> bool:
	if is_open():
		return false
	for tab in tabs.get_children():
		tabs.remove_child(tab)
		tab.queue_free()
	for location in village.locations:
		if location == null:
			continue
		tabs.add_child(location.make_tab())
		# Titled here rather than by the node name, which cannot hold every
		# character a name might.
		tabs.set_tab_title(tabs.get_tab_count() - 1, location.display_name)
	if tabs.get_tab_count() == 0:
		return false
	open()
	return true
