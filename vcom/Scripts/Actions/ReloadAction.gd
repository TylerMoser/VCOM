## Load a fresh magazine into the unit's gun, as XCOM's Reload does, for the
## actions the gun's [member Weapon.reload] says (one, for the rifle). Only a
## unit carrying a gun with a magazine has it, and it is dimmed while the
## magazine is full or the unit has too few actions left for it.
##
## Like Hunker Down it shows nothing on the map while it is up. Confirming
## spends the actions and plays the reload on the figure (the magazine is full
## from the moment the new one is seated, [method Unit.reload]); nothing is
## called over the unit's head, as the animation says enough. The unit can
## carry on with its turn; with the magazine full again the action is put
## away.
##
##   Reload - Enter or Space, or A on the gamepad.
class_name ReloadAction
extends UnitAction

var _unit: Unit


func _init() -> void:
	display_name = "Reload"
	required_tag = Item.GUN


func confirm_hint() -> String:
	return "Reload"


## A gun that never runs dry ([member Weapon.magazine] 0) has nothing to
## reload, so the action is not offered at all.
func is_granted(unit: Unit) -> bool:
	return super(unit) and unit.has_magazine()


func is_available(unit: Unit) -> bool:
	return unit.can_reload() and unit.actions_remaining >= unit.reload_cost()


func begin(unit: Unit) -> void:
	_unit = unit


func end() -> void:
	_unit = null


func handle_input(event: InputEvent) -> bool:
	if not event.is_action_pressed(&"confirm_action"):
		return false
	_reload()
	return true


## Spends the actions and plays the reload out, busy until the figure has
## finished it.
func _reload() -> void:
	var unit := _unit
	unit.spend_actions(unit.reload_cost())
	controller.busy = true
	await unit.reload()
	if is_instance_valid(unit):
		await unit.recover()
	completed.emit()
