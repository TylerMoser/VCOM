## One level of a [Skill]: what taking the skill that time gives, in words
## and in effect. A character has the [member effects] of every level they
## have taken, the earlier ones with the later, so a level says and gives only
## what it adds: Ambition's second is one more HP, not two.
class_name SkillLevel
extends Resource

## What the level gives, as the skill's tooltip says it: after "Current:" once
## it is the last level taken, and after "Next:" while it is the next to take.
@export_multiline var description := ""
## What the level gives, for the rules. With none it gives nothing but its
## words.
@export var effects: Array[SkillEffect] = []
