## One ability a character can learn: what it is called, what it looks like
## and what it says about itself. Where it sits in a tree, and what must come
## before it there, belongs to the [SkillTreeNode] placing it, so one skill can
## sit in several trees: the same +1 Move in a species' tree and a class's.
##
## It has a level for each time it can be taken ([member levels]), each giving
## something more, or something else, on top of the levels before it.
##
## Like [Item], it is shared by every tree that holds it, so it stays
## stateless: which levels a character has is theirs
## ([member Character.learned]).
class_name Skill
extends Resource

## The most [member levels] any skill has: learned once and taken four times
## more, which is as many rings as a node on the Skills page ever has to make
## room for.
const MOST_LEVELS := 5

@export var display_name := ""
## A line of colour about it, under its name in its tooltip: what it is, not
## what it does, which is each level's to say.
@export_multiline var flavor := ""
## Shown on its node in a tree. Without one the node shows its rank: its row,
## counted from 1 at the top.
@export var icon: Texture2D
## Its levels, in the order they are taken: the first is what learning the
## skill gives, each one after it what taking it again adds. The skill can be
## taken once for each, a skill point a time, up to [constant MOST_LEVELS],
## and its node shows a ring for every level after the first. With none it can
## still be learned, once, for nothing.
@export var levels: Array[SkillLevel] = []


## How many times it can be taken: once for each of its [member levels], and
## once with none.
func takes() -> int:
	return clampi(levels.size(), 1, MOST_LEVELS)


## Level [param number], the first being 1. Null for one it does not have.
func level(number: int) -> SkillLevel:
	return levels[number - 1] if number >= 1 and number <= levels.size() else null


## What level [param number] gives, in words. Empty for a level it does not
## have, or has no words for.
func describe(number: int) -> String:
	var at := level(number)
	return at.description if at != null else ""
