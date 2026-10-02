## One thing a level of a [Skill] gives ([member SkillLevel.effects]), for as
## long as the character has that level. A kind of effect is a subclass, as
## [StatBonus] is, set up in the skill's [code].tres[/code]; no code elsewhere
## changes for a new skill of a kind that exists.
##
## Each method here is something the rules ask of every effect a character
## has ([method Character.skill_effects]), and a kind answers only what is
## its own: the rest keep the answer here, which is nothing. A new kind of
## effect that the rules do not ask about yet adds its question here, and
## whoever needs the answer asks it.
##
## Shared by everyone with the skill, so, like the skill, it stays stateless.
class_name SkillEffect
extends Resource


## What the effect adds to [param stat], one of a [Character]'s stats by its
## property's name, such as [code]&"max_health"[/code] (see
## [method Character.total]).
func bonus_to(_stat: StringName) -> int:
	return 0
