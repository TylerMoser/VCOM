## A [SkillEffect] that hands the character skill points the moment its level
## is taken: Adaptability's 5. Once, and theirs to spend from then on, as
## points earned from experience are. The point the level cost is spent
## first, so Adaptability leaves a character four better off.
class_name SkillPointGrant
extends SkillEffect

## How many skill points are gained.
@export var amount := 1


func when_taken(character: Character) -> void:
	character.skill_points += amount
