## Who fights, chosen before the world map is left for a battle: the party's
## random encounters ([signal Party.encountered]) open it, framed and pausing
## like the pause menu, on its one Roster tab ([SquadTab]), with whoever
## fought the last battle and still stands already ticked
## ([method Campaign.squad]).
##
## It cannot be closed. Esc (and the gamepad's B) does nothing here, and is
## taken so that the pause menu, which sees it after the scene does, does not
## open over it either. The only way on is holding Start, which starts the
## battle with whoever is ticked ([method Campaign.start_battle]); the world
## map is left as it stands, the party stopped where it was set upon. The
## gamepad's Menu button, which would open the pause menu, takes the keyboard
## to Start instead.
class_name SquadMenu
extends TabbedMenu

## Whose encounters open it.
@export var party_path: NodePath = ^"../Party"

var _tab: SquadTab
## The battle to start once the squad is chosen; null while the menu is shut.
var _map: PackedScene


func _init() -> void:
	super()
	_tab = SquadTab.new()
	_tab.started.connect(_on_started)
	tabs.add_child(_tab)


func _ready() -> void:
	var party := get_node_or_null(party_path) as Party
	if party == null:
		push_error("SquadMenu: no Party at '%s'; no encounter will start a battle." % party_path)
		return
	party.encountered.connect(choose_squad)


func _unhandled_input(event: InputEvent) -> void:
	super(event)
	if not is_open() or get_viewport().is_input_handled():
		return
	if event.is_action_pressed(&"pause_menu") and event is InputEventJoypadButton:
		_tab.focus_start()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed(&"cancel_action") or event.is_action_pressed(&"pause_menu"):
		get_viewport().set_input_as_handled()


## It cannot be closed; Menu takes the keyboard to Start, unless it is there.
func _close_hints() -> Array:
	return [] if _tab.is_start_focused() else [[[&"Menu"], "Go to Start"]]


## Opens to choose who fights a battle on [param map], and starts it once they
## are chosen. Ignored while open, or with nobody on the roster to choose.
func choose_squad(map: PackedScene) -> void:
	if is_open() or map == null or Campaign.roster.characters.is_empty():
		return
	_map = map
	open()


func _refresh() -> void:
	_tab.show_roster(Campaign.roster.characters, Campaign.squad())


func _on_started(chosen: Array[Character]) -> void:
	if _map == null or not Campaign.start_battle(_map, chosen):
		return
	_map = null
	# The battle takes over at the end of the frame, unpaused.
	close()
