## Get down behind cover and stay down until the squad's next turn, or until
## moving off. Every unit has it, as it needs nothing carried, but it can only
## be taken in cover: with a side of the tile against something solid
## ([method LineOfSight.cover_at]). Out of cover its button is dimmed.
##
## Confirming costs [constant COST], and the unit can carry on with the rest of
## its turn: shooting, striking and throwing from where it is, stepping out of
## cover to shoot and back included, leave it hunkered. It hunkers down
## ([member Unit.hunkered]): its figure ducks low and its card on the squad
## panel shows a shield. Until the start of the player's next turn every shot
## at it that its cover counts against loses [constant HitChance.HUNKER] more
## aim, on top of the cover's own; a shot that flanks it, or comes after its
## cover is shot away, does not ([method HitChance.hunker_penalty]). Moving,
## or falling when the ground goes, stands it up at once
## ([method Unit.start_walk], [method Unit.drop_to]); it can hunker down again
## for another action wherever it ends up in cover.
##
##   Hunker down - Enter or Space, or A on the gamepad.
class_name HunkerDownAction
extends UnitAction

## Action points hunkering down costs.
const COST := 1

var _unit: Unit


func _init() -> void:
	display_name = "Hunker Down"


func confirm_hint() -> String:
	return "Hunker down"


func is_available(unit: Unit) -> bool:
	return unit.actions_remaining >= COST and not unit.hunkered and is_in_cover(unit, controller.grid)


## Whether [param unit] has cover on any side of the tile it stands on, high
## or low, which is what hunkering down needs.
static func is_in_cover(unit: Unit, grid: CombatGrid) -> bool:
	return not LineOfSight.new(grid).cover_at(grid.tile_at(unit.global_position)).is_empty()


func begin(unit: Unit) -> void:
	_unit = unit


func end() -> void:
	_unit = null


func handle_input(event: InputEvent) -> bool:
	if not event.is_action_pressed(&"confirm_action"):
		return false
	_unit.spend_actions(COST)
	_unit.hunkered = true
	completed.emit()
	return true
