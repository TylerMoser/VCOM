## One ability a character can learn: what it is called, what it looks like
## and what it says about itself. Where it sits in a tree, and what must come
## before it there, belongs to the [SkillTreeNode] placing it, so one skill can
## sit in several trees: the same +1 Move in a species' tree and a class's.
##
## Like [Item], it is shared by every tree that holds it, so it stays
## stateless. It does nothing yet.
class_name Skill
extends Resource

@export var display_name := ""
@export_multiline var description := ""
## Shown on its node in a tree. Without one the node shows its rank: its row,
## counted from 1 at the top.
@export var icon: Texture2D
