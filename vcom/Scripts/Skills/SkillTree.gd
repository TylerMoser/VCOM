## The skills a [SkillSource] (a species, a sub-species, a class) offers, as
## [SkillTreeNode]s laid out on a grid, each requiring the nodes it names.
## The tree has no fixed shape: paths, branches and joins are all just where
## its nodes sit and what they require.
##
## Data, like [Item]: shared by everyone with that species or class, and never
## changed in play. What a character has learned of it is theirs
## ([member Character.learned]).
class_name SkillTree
extends Resource

@export var nodes: Array[SkillTreeNode] = []


## The node named [param id], or null when the tree has none.
func find(id: StringName) -> SkillTreeNode:
	for node in nodes:
		if node.id == id:
			return node
	return null


## How many columns across and rows down the nodes reach.
func extent() -> Vector2i:
	var most := Vector2i(-1, -1)
	for node in nodes:
		most = most.max(node.cell)
	return most + Vector2i.ONE


## Whether [param node] is open to someone who has learned [param learned] of
## this tree: every node it requires is among them.
func is_open(node: SkillTreeNode, learned: Array[StringName]) -> bool:
	for id in node.requires:
		if not learned.has(id):
			return false
	return true
