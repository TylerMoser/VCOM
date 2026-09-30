## Hold the unit's reaction for a shot at an enemy it sees move, for every
## action it has left. Only a unit carrying a gun has it.
##
## While the action is up, the ground the unit would cover is marked on the
## map. Confirming spends the rest of the unit's turn and puts it on
## overwatch. Nothing fires by itself: when an enemy moves into view,
## [Reactions] slows the action down and the player chooses whether, and
## when, to take the shot. It is a reaction, so it costs
## [constant HitChance.REACTION_PENALTY] aim and cannot be taken if the unit
## has already used its reaction.
##
##   Go on overwatch - Enter or Space.
class_name OverwatchAction
extends UnitAction

const HIGHLIGHT_LAYER := &"overwatch"
## The gold of the reaction pip, so the ground reads as what the reaction is
## held for.
const HIGHLIGHT_COLOR := Color(1.0, 0.78, 0.2)
## Faint, so the terrain still reads through a field of watched tiles.
const HIGHLIGHT_FILL := 0.3

var _unit: Unit


func _init() -> void:
	display_name = "Overwatch"
	required_tag = Item.GUN


func is_available(unit: Unit) -> bool:
	return unit.actions_remaining > 0 and unit.reaction_available and not unit.overwatching


func begin(unit: Unit) -> void:
	_unit = unit
	var tiles := {}
	for tile: Vector3i in LineOfSight.new(controller.grid).watched_tiles(unit):
		tiles[tile] = HIGHLIGHT_COLOR
	controller.highlights.set_layer(HIGHLIGHT_LAYER, tiles, HIGHLIGHT_FILL)


func end() -> void:
	_unit = null
	controller.highlights.clear_layer(HIGHLIGHT_LAYER)


func handle_input(event: InputEvent) -> bool:
	if not event.is_action_pressed(&"confirm_action"):
		return false
	_unit.spend_actions(_unit.actions_remaining)
	_unit.overwatching = true
	completed.emit()
	return true
