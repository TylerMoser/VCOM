## A [SkillEffect] that adds to one of the character's stats: Ambition's +1
## HP. The character's own stat is never changed: the bonus is added whenever
## the stat is read ([method Character.total]), so it goes with the level.
class_name StatBonus
extends SkillEffect

## The stat added to, by its [Character] property's name. Every stat a unit
## takes from its character is listed (see [method Unit._take_character]): one
## added there is added here.
@export_enum("max_health", "defense", "move_range", "aim", "melee_accuracy", "strength", "evasion") var stat := "max_health"
## How much is added. Less than nothing takes away.
@export var amount := 1


func bonus_to(to: StringName) -> int:
	return amount if to == stat else 0
