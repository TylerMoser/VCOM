## Base for something a unit can do on its turn, shown as a button on the
## action bar. Actions are children of the ActionController, which starts and
## stops them; while one is active it receives the map input the HUD and the
## squad do not use.
class_name UnitAction
extends Node

## Emitted once the action has finished playing out, so the controller can
## refresh it or put it away.
signal completed

@export var display_name := "Action"

## Set by the ActionController that owns this action.
var controller: ActionController


func is_available(_unit: Unit) -> bool:
	return true


## Called when the action becomes active for [param _unit].
func begin(_unit: Unit) -> void:
	pass


## Called when the action stops being active. Undo whatever [method begin]
## put on screen.
func end() -> void:
	pass


## Map input while active. Return true if the event was used.
func handle_input(_event: InputEvent) -> bool:
	return false
