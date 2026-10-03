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
## Whether [method point_at_target] has the hand cursor up.
var _pointing := false


## Whether [param unit] has this action at all: always, unless it needs an
## item the unit is not carrying. An action the unit lacks is left off the
## action bar, where one it has but cannot take right now
## ([method is_available]) is only dimmed. During a battle it changes only as
## the unit uses up what it carries: a unit that throws its last grenade has
## no Throw Grenade from then on.
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


## How many more times [param _unit] can take the action, shown on its button,
## for an action limited that way, such as the medkits a unit can still use
## this battle; -1, showing nothing, for one that is not.
func uses_left(_unit: Unit) -> int:
	return -1


## What the gamepad's A (confirm_action) does while the action is up, for its
## prompt: "Fire", "Move here". Empty for nothing.
func confirm_hint() -> String:
	return ""


## Whether LB and RB (and Tab) cycle the action's targets while it is up,
## rather than the squad.
func cycles_targets() -> bool:
	return false


## Whether what the action lines up has odds, a chance whose sum LT (or Ctrl)
## opens, for the prompts: a shot or a strike, not a medkit, which is never
## rolled.
func shows_odds() -> bool:
	return cycles_targets()


## Called as the gamepad's tile cursor moves to [param _tile] while the action
## is up, as a mouse moving over the map would be seen. An action that picks
## among units can line up the one there.
func cursor_moved(_tile: Vector3i) -> void:
	pass


## Whether a left click on [param _unit], a squad member, is the action's
## rather than a change of selection: one of its targets, as the allies (and
## the unit itself) a medkit is offered for are. False for every action that
## targets none of the squad, so a left click on any of them selects them.
func takes_click_on(_unit: Unit) -> bool:
	return false


## Whether [param event] is a click on the map that carries an action out,
## with either mouse button: left, as a squad member is selected, or right, as
## Move is. A left click on a squad member never gets here, unless the action
## takes it ([method takes_click_on]): it selects them (see
## [ActionController]).
static func is_click(event: InputEvent) -> bool:
	return event is InputEventMouseButton and (
		event.is_action_pressed(&"select_unit") or event.is_action_pressed(&"execute_action")
	)


## The unit [param event] clicks on ([method is_click]), or null for any other
## event, or a click on no unit.
func clicked_unit(event: InputEvent) -> Unit:
	if not is_click(event):
		return null
	return controller.squad.unit_at((event as InputEventMouseButton).position)


## The unit under the mouse, or null.
func hovered_unit() -> Unit:
	return controller.squad.unit_at(get_viewport().get_mouse_position())


func _notification(what: int) -> void:
	# The pause menu, or the battle ending, leaves no target to point at.
	if what == NOTIFICATION_PAUSED or what == NOTIFICATION_EXIT_TREE:
		point_at_target(false)


## Shows the hand cursor over the map while [param pointing], as over a target
## a click would act on, and the arrow otherwise. Changes it only when it
## changes: setting it sends a mouse motion of its own. An action that calls it
## puts the arrow back as it ends.
func point_at_target(pointing: bool) -> void:
	# Nothing follows the mouse while the gamepad is in use, and it is hidden.
	pointing = pointing and not InputDevice.gamepad
	if pointing == _pointing:
		return
	_pointing = pointing
	Input.set_default_cursor_shape(Input.CURSOR_POINTING_HAND if pointing else Input.CURSOR_ARROW)
