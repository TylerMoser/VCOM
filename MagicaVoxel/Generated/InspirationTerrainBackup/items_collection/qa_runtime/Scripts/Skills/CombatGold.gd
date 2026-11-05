## A [SkillEffect] that finds the party gold after every combat the character
## fights in and comes through: Money Grubbing's +1 Gold. Nothing for a
## battle they sat out on the roster, and nothing if they fell in it
## ([method PlayerSquad.award_survivors], which pays it).
class_name CombatGold
extends SkillEffect

## Gold the party gains each time.
@export var amount := 1


func gold_after_combat() -> int:
	return amount
