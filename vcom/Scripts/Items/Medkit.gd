## A medkit: bandages, splints and salves to patch up the wounded in the
## field. Any unit carrying one has Use Medkit ([UseMedkitAction]), which heals
## the unit itself, or an ally standing next to it, by [member heal], and so
## does a squad member standing next to it while it has a use left, drawing on
## its uses.
##
## Unlike a [Grenade] it is never used up: each one carried can be used once a
## battle ([member Unit.medkits]), and is ready again for the next. Two carried
## are two uses.
##
## Shared between every stack and unit that holds one, so, like every
## [Item], it stays stateless: the uses left are the unit's.
class_name Medkit
extends BattleItem

## Health it gives back to the one it is used on, never above their most
## ([member Unit.max_health]).
@export var heal := 4
