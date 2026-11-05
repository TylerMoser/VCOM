## One thing a level of a [Skill] gives ([member SkillLevel.effects]). A kind
## of effect is a subclass, as [StatBonus], [CombatGold] and [SkillPointGrant]
## are, set up in the skill's [code].tres[/code]; no code elsewhere changes
## for a new skill of a kind that exists.
##
## There are two sorts. One lasts as long as the character has the level:
## the rules ask every effect a character has
## ([method Character.skill_effects]) a question when they need its answer, as
## [method bonus_to] is asked whenever a stat is read and
## [method gold_after_combat] as a battle ends, and nothing is stored.
## The other happens once, as the level is taken ([method when_taken]), and
## what it did is the character's from then on. A kind answers only what is
## its own, and the rest keep the answer here, which is nothing. A new kind
## that the rules do not ask about yet adds its question here, and whoever
## needs the answer asks it.
##
## Shared by everyone with the skill, so, like the skill, it stays stateless.
class_name SkillEffect
extends Resource


## What the effect adds to [param stat], one of a [Character]'s stats by its
## property's name, such as [code]&"max_health"[/code] (see
## [method Character.total]).
func bonus_to(_stat: StringName) -> int:
	return 0


## Gold the effect finds the party after a combat its character fought in and
## came through (see [method Character.combat_gold]).
func gold_after_combat() -> int:
	return 0


## Done once, to [param character], as they take the level the effect is in
## ([method Character.learn]), the skill point for it already spent. Nothing
## unless the kind is one that happens there and then. Not done for a level a
## character starts out with, set in their [code].tres[/code]: what such a
## level would have given them is set there too.
func when_taken(_character: Character) -> void:
	pass
