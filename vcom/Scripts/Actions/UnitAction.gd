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
## The tag an item the unit carries must have for the unit to have this
## action at all, such as [constant Item.GUN] for Shoot. Empty for an action
## every unit has, like Move. Set in the action's [code]_init()[/code], beside
## its name.
@export var required_tag: StringName

## Set by the ActionController that owns this action.
var controller: ActionController


## Whether [param unit] has this action at all: always, unless it needs an
## item the unit is not carrying. An action the unit lacks is left off the
## action bar, where one it has but cannot take right now
## ([method is_available]) is only dimmed. It cannot change during a battle,
## since a unit's equipment does not.
func is_granted(unit: Unit) -> bool:
	return required_tag.is_empty() or unit.carries(required_tag)


## Whether [param _unit] can take the action right now, having it at all
## ([method is_granted]).
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
