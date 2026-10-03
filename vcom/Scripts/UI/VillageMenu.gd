## A village's own menu: a tab for each [Location] in it, in the order its
## [member Destination.locations] lists them. Framed and pausing like the pause
## menu.
##
## A left click (select_unit, as a unit is picked in combat) on the icon of
## the village the party is standing in opens it, as does the gamepad's A with
## the map's reticle on it; a village with nothing in it does not open. The
## tabs are made afresh each time, since every village has its own mix. Esc
## closes it, as do the gamepad's B and Menu. Being in the scene, after the
## pause menu's autoload in the tree, it sees them first and takes them, so the
## pause menu does not open on the same press.
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
	super(event)
	if get_viewport().is_input_handled():
		return
	if is_open():
		if event.is_action_pressed(&"cancel_action") or event.is_action_pressed(&"pause_menu"):
			close()
			get_viewport().set_input_as_handled()
		return
	# It runs through the pause, like every menu: none opens over another.
	if get_tree().paused:
		return
	var clicked := event.is_action_pressed(&"select_unit") and event is InputEventMouseButton
	var pressed := InputDevice.gamepad and event.is_action_pressed(&"confirm_action")
	if (clicked or pressed) and _party != null:
		var village := enterable()
		if village != null and open_village(village):
			get_viewport().set_input_as_handled()


## The village under the pointer (the mouse, or the gamepad's reticle) if the
## party is in it, which is what a click or A there opens; else null.
func enterable() -> Destination:
	var village := Destination.find_under_pointer(get_tree())
	return village if village != null and _party != null and _party.is_at(village) else null


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
