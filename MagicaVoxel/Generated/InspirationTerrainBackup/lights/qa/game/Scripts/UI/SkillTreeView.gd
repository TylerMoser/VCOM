## One [SkillSource]'s [SkillTree] on the Roster's Skills page: a
## [SkillButton] on each of its nodes' cells, and a link from every node up to
## each node it requires, lit once that one is learned.
##
## It places its buttons itself, by [member SkillTreeNode.cell], rather than in
## containers, since a tree can branch and join any way. A button with rings
## is bigger than one without, so a column is as wide as its widest button and
## a row as tall as the page says ([method row_heights]: its tallest in any
## of the page's trees, so the trees' rows stay level), each button in the
## middle of its cell. A link leaves the bottom of the node required, turns
## across just above the row of the node requiring it and comes down into its
## top, so a path is a straight line and a branch a fork.
class_name SkillTreeView
extends Control

## Room between neighbouring columns, and between rows, where the links run.
const GAP := Vector2(28, 18)
const LINK_WIDTH := 2.0
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)

## What gives the tree, which is what the character learns it from.
var source: SkillSource
var tree: SkillTree
## Every node's button, by the node's id.
var buttons := {}

## The ids of the nodes the character has learned, a node's once for every
## time it has been taken.
var _learned: Array[StringName] = []
## Where each column starts and how wide it is, and the same down the rows.
var _column_at := PackedFloat32Array()
var _widths := PackedFloat32Array()
var _row_at := PackedFloat32Array()
var _heights := PackedFloat32Array()


## [param heights] is how tall each row is, from the top: from
## [method row_heights] over every tree shown beside this one.
func _init(shown: SkillSource, heights: PackedFloat32Array) -> void:
	source = shown
	tree = source.tree
	mouse_filter = MOUSE_FILTER_IGNORE
	var extent := tree.extent()
	_widths.resize(extent.x)
	_widths.fill(SkillButton.SIZE.x)
	for node in tree.nodes:
		_widths[node.cell.x] = maxf(_widths[node.cell.x], SkillButton.size_of(node).x)
	_heights = heights.slice(0, extent.y)
	_column_at = _starts(_widths, GAP.x)
	_row_at = _starts(_heights, GAP.y)
	if extent.x > 0 and extent.y > 0:
		custom_minimum_size = Vector2(_column_at[-1] + _widths[-1], _row_at[-1] + _heights[-1])

	for node in tree.nodes:
		if buttons.has(node.id):
			push_warning("Skill tree has two nodes named '%s'; showing the first." % node.id)
			continue
		for id in node.requires:
			if tree.find(id) == null:
				push_warning("Skill tree node '%s' requires '%s', which the tree does not have." % [node.id, id])
		var button := SkillButton.new(node, _state(node))
		var cell := Vector2(_widths[node.cell.x], _heights[node.cell.y])
		button.position = Vector2(_column_at[node.cell.x], _row_at[node.cell.y]) + (cell - button.size) / 2.0
		add_child(button)
		buttons[node.id] = button


## How tall each row of [param trees] must be, from the top, to hold its
## tallest button in any of them. Given to every one of those trees' views, so
## a row is the same height in each and the trees line up across the page.
static func row_heights(trees: Array[SkillTree]) -> PackedFloat32Array:
	var heights := PackedFloat32Array()
	for shown in trees:
		for node in shown.nodes:
			while heights.size() <= node.cell.y:
				heights.append(SkillButton.SIZE.y)
			heights[node.cell.y] = maxf(heights[node.cell.y], SkillButton.size_of(node).y)
	return heights


## Restyles the nodes and links for [param learned], the ids of the nodes the
## character has learned of the tree, a node's once for every time it has
## been taken.
func show_learned(learned: Array[StringName]) -> void:
	_learned = learned
	for button: SkillButton in buttons.values():
		button.state = _state(button.tree_node)
		button.taken = _learned.count(button.tree_node.id)
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
	for button: SkillButton in buttons.values():
		for id in button.tree_node.requires:
			if buttons.has(id):
				_draw_link(buttons[id], button, ACCENT_COLOR if _learned.has(id) else BORDER_COLOR)


## Learned, open to be learned next (see [method SkillTree.is_open]), or not
## yet reached.
func _state(node: SkillTreeNode) -> SkillButton.State:
	if _learned.has(node.id):
		return SkillButton.State.LEARNED
	if tree.is_open(node, _learned):
		return SkillButton.State.AVAILABLE
	return SkillButton.State.LOCKED


## The link from [param from], the node required, to [param to]: an elbow
## when [param to] is lower down, as a tree is meant to read, from outside
## the one's rings to outside the other's. One on the same row or higher,
## which a tree should not need, is a straight line between the two, under
## their buttons.
func _draw_link(from: SkillButton, to: SkillButton, color: Color) -> void:
	if to.tree_node.cell.y <= from.tree_node.cell.y:
		draw_line(from.position + from.size / 2.0, to.position + to.size / 2.0, color, LINK_WIDTH)
		return
	var start := from.position + Vector2(from.size.x / 2.0, from.size.y)
	var end := to.position + Vector2(to.size.x / 2.0, 0.0)
	var knee := _row_at[to.tree_node.cell.y] - GAP.y / 2.0
	_segment(start, Vector2(start.x, knee), color)
	_segment(Vector2(start.x, knee), Vector2(end.x, knee), color)
	_segment(Vector2(end.x, knee), end, color)


## A straight run of a link, across or down, as a filled bar, so the runs of
## an elbow meet square at the corners.
func _segment(from: Vector2, to: Vector2, color: Color) -> void:
	var half := Vector2.ONE * LINK_WIDTH / 2.0
	draw_rect(Rect2(from.min(to) - half, (to - from).abs() + half * 2.0), color)


## Where each of a run of columns (or rows) [param sizes] across starts, with
## [param gap] between one and the next.
static func _starts(sizes: PackedFloat32Array, gap: float) -> PackedFloat32Array:
	var starts := PackedFloat32Array()
	var at := 0.0
	for across in sizes:
		starts.append(at)
		at += across + gap
	return starts
