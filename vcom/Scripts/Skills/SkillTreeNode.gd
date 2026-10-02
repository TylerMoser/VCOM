## A place in a [SkillTree]: the [Skill] there, the cell of the tree's grid it
## sits in, and the nodes of the same tree that must be learned before it.
##
## Every shape of tree is a layout of these: a path is a column of nodes, each
## requiring the one above; a branch is two requiring the same one; a node
## requiring two joins their branches again.
class_name SkillTreeNode
extends Resource

## Names the node within its tree, for [member requires] and for what a
## character has learned of the tree ([member Character.learned]). Unique in
## its tree, and never renamed once in play, since saves will keep it.
@export var id: StringName
@export var skill: Skill
## Where the node sits: its column, counted from 0 at the left, and its row,
## from 0 at the top. The tree is as wide and as tall as its nodes reach.
@export var cell := Vector2i.ZERO
## The [member id]s of the nodes in the same tree that must all be learned
## before this one can be: taken once, however often they can be. A node
## requiring none is where the tree starts.
@export var requires: Array[StringName] = []


## How many times in all the node can be taken: once, and again for each of
## its skill's [member Skill.repeats].
func takes() -> int:
	return 1 + (skill.repeats if skill != null else 0)
