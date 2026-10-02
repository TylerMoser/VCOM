## One ability a character can learn: what it is called, what it looks like
## and what it says about itself. Where it sits in a tree, and what must come
## before it there, belongs to the [SkillTreeNode] placing it, so one skill can
## sit in several trees: the same +1 Move in a species' tree and a class's.
##
## It can be taken more than once ([member repeats]), for more of what it
## gives or something else each time.
##
## Like [Item], it is shared by every tree that holds it, so it stays
## stateless. It does nothing yet, however often it is taken.
class_name Skill
extends Resource

## The most [member repeats] any skill has: as many rings as a node on the
## Skills page ever has to make room for.
const MOST_REPEATS := 4

@export var display_name := ""
@export_multiline var description := ""
## Shown on its node in a tree. Without one the node shows its rank: its row,
## counted from 1 at the top.
@export var icon: Texture2D
## How many more times it can be taken after the first, each for a skill point
## of its own. Its node shows a ring round it for each.
@export_range(0, MOST_REPEATS) var repeats := 0
