## One action a computer-controlled unit has settled on: walk somewhere, take
## a shot, load a fresh magazine, or stop for the turn. An [EnemyAI] picks it and the [TurnManager]
## carries it out, charging it the same actions the squad would pay.
class_name AIAction
extends RefCounted

enum Kind { MOVE, SHOOT, RELOAD, END_TURN }

var kind := Kind.END_TURN
## For a move: the tiles walked through, in order, ending where the unit
## stops. It costs an action per [member Unit.move_range] tiles, like the
## squad's moves.
var path: Array[Vector3i] = []
## For a shot: who it is aimed at, and from where.
var shot: LineOfSight.Shot
## For a shot: its odds, worked out when it was chosen. These are what get
## rolled, never a fresh sum at the moment it goes off.
var estimate: HitChance.Estimate


## Walk through [param tiles], ending on the last of them.
static func move(tiles: Array[Vector3i]) -> AIAction:
	var action := AIAction.new()
	action.kind = Kind.MOVE
	action.path = tiles
	return action


## Take [param aimed], rolling against [param odds].
static func shoot(aimed: LineOfSight.Shot, odds: HitChance.Estimate) -> AIAction:
	var action := AIAction.new()
	action.kind = Kind.SHOOT
	action.shot = aimed
	action.estimate = odds
	return action


## Load a fresh magazine, for the actions its gun's [member Weapon.reload]
## costs. Not named [code]reload[/code]: called on the class, that would be
## the class's own [method Script.reload].
static func reload_gun() -> AIAction:
	var action := AIAction.new()
	action.kind = Kind.RELOAD
	return action


## Do nothing more this turn.
static func end_turn() -> AIAction:
	return AIAction.new()
