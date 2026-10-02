## One [SkillSource]'s [SkillTree] on the Roster's Skills page: a
## [SkillButton] on each of its nodes' cells, and a link from every node up to
## each node it requires, lit once that one is learned.
##
## It places its buttons itself, by [member SkillTreeNode.cell], rather than in
## containers, since a tree can branch and join any way. A link leaves the
## bottom of the node required, turns across just above the row of the node
## requiring it and comes down into its top, so a path is a straight line and a
## branch a fork.
class_name SkillTreeView
extends Control

## Room between neighbouring nodes: across between columns, and down between
## rows, where the links run.
const GAP := Vector2(28, 18)
const LINK_WIDTH := 2.0
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)

## What gives the tree, which is what the character learns it from.
var source: SkillSource
var tree: SkillTree
## Every node's button, by the node's id.
var buttons := {}

## The ids of the nodes the character has learned.
var _learned: Array[StringName] = []


func _init(shown: SkillSource) -> void:
	source = shown
	tree = source.tree
	mouse_filter = MOUSE_FILTER_IGNORE
	custom_minimum_size = (Vector2(tree.extent()) * (SkillButton.SIZE + GAP) - GAP).max(Vector2.ZERO)
	for node in tree.nodes:
		if buttons.has(node.id):
			push_warning("Skill tree has two nodes named '%s'; showing the first." % node.id)
			continue
		for id in node.requires:
			if tree.find(id) == null:
				push_warning("Skill tree node '%s' requires '%s', which the tree does not have." % [node.id, id])
		var button := SkillButton.new(node, _state(node))
		button.position = _corner(node.cell)
		add_child(button)
		buttons[node.id] = button


## Restyles the nodes and links for [param learned], the ids of the nodes the
## character has learned of the tree.
func show_learned(learned: Array[StringName]) -> void:
	_learned = learned
	for button: SkillButton in buttons.values():
		button.state = _state(button.tree_node)
	queue_redraw()


## The button the keyboard comes down to from the sub-tabs: the top row's
## leftmost.
func first() -> SkillButton:
	var best: SkillButton = null
	for button: SkillButton in buttons.values():
		var cell := button.tree_node.cell
		if best == null or Vector2i(cell.y, cell.x) < Vector2i(best.tree_node.cell.y, best.tree_node.cell.x):
			best = button
	return best


func _draw() -> void:
	for node in tree.nodes:
		for id in node.requires:
			var required := tree.find(id)
			if required != null:
				_draw_link(required.cell, node.cell, ACCENT_COLOR if _learned.has(id) else BORDER_COLOR)


## Learned, open to be learned next (see [method SkillTree.is_open]), or not
## yet reached.
func _state(node: SkillTreeNode) -> SkillButton.State:
	if _learned.has(node.id):
		return SkillButton.State.LEARNED
	if tree.is_open(node, _learned):
		return SkillButton.State.AVAILABLE
	return SkillButton.State.LOCKED


## The link from the node at [param from], required, to the one at [param to]:
## an elbow when [param to] is lower down, as a tree is meant to read. One on
## the same row or higher, which a tree should not need, is a straight line
## between the two, under their buttons.
func _draw_link(from: Vector2i, to: Vector2i, color: Color) -> void:
	var half := SkillButton.SIZE / 2.0
	if to.y <= from.y:
		draw_line(_corner(from) + half, _corner(to) + half, color, LINK_WIDTH)
		return
	var start := _corner(from) + Vector2(half.x, SkillButton.SIZE.y)
	var end := _corner(to) + Vector2(half.x, 0.0)
	var knee := end.y - GAP.y / 2.0
	_segment(start, Vector2(start.x, knee), color)
	_segment(Vector2(start.x, knee), Vector2(end.x, knee), color)
	_segment(Vector2(end.x, knee), end, color)


## A straight run of a link, across or down, as a filled bar, so the runs of
## an elbow meet square at the corners.
func _segment(from: Vector2, to: Vector2, color: Color) -> void:
	var half := Vector2.ONE * LINK_WIDTH / 2.0
	draw_rect(Rect2(from.min(to) - half, (to - from).abs() + half * 2.0), color)


## Where the button on [param cell] has its top-left corner.
func _corner(cell: Vector2i) -> Vector2:
	return Vector2(cell) * (SkillButton.SIZE + GAP)
