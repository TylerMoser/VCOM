## The Roster's Skills page: the character's skill trees, one column each,
## Species and Sub-Species narrow and the two class trees three times as wide.
##
## Placeholder so far: the Species trees are a single path of numbered
## [SkillNode]s, top to bottom, in the same fixed states for everyone, and the
## class trees are still empty. Skills, and a character's progress through
## them, come as data later.
class_name SkillsPage
extends CharacterPage

## Each column: its title, its share of the width, and how many nodes its
## path has (none yet for the class trees).
const SECTIONS := [
	["Species", 1, 4],
	["Sub-Species", 1, 4],
	["Main Class", 3, 0],
	["Multi-Class", 3, 0],
]
## Where every character stands on a path until there is real progress.
const PLACEHOLDER_STATES := [
	SkillNode.State.AVAILABLE,
	SkillNode.State.LOCKED,
	SkillNode.State.LOCKED,
	SkillNode.State.LOCKED,
]

const LINK_SIZE := Vector2(2, 18)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const TITLE_COLOR := Color(0.7, 0.72, 0.78)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)

var _group := ButtonGroup.new()
## Every tree's nodes, a column at a time, top to bottom.
var _paths: Array[Array] = []


func _init() -> void:
	super("Skills")
	var columns := HBoxContainer.new()
	columns.set_anchors_preset(PRESET_FULL_RECT)
	columns.add_theme_constant_override(&"separation", 0)
	add_child(columns)
	for i in SECTIONS.size():
		if i > 0:
			columns.add_child(_divider())
		columns.add_child(_section(SECTIONS[i][0], SECTIONS[i][1], SECTIONS[i][2]))
	_link_across()


## Clears the selection: it was on the last character's tree.
func _refresh() -> void:
	var selected := _group.get_pressed_button()
	if selected != null:
		selected.button_pressed = false


func focus_selection() -> bool:
	var target := _group.get_pressed_button()
	if target == null and not _paths.is_empty():
		target = _paths[0][0]
	if target == null:
		return false
	target.grab_focus()
	return true


## A column: its title at the top and, under it, its path of nodes joined by
## links, centred.
func _section(title: String, share: int, nodes: int) -> VBoxContainer:
	var section := VBoxContainer.new()
	section.size_flags_horizontal = SIZE_EXPAND_FILL
	section.size_flags_stretch_ratio = share
	section.add_theme_constant_override(&"separation", 16)

	var heading := Label.new()
	heading.text = title
	heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	heading.add_theme_font_size_override(&"font_size", 16)
	heading.add_theme_color_override(&"font_color", TITLE_COLOR)
	section.add_child(heading)

	if nodes == 0:
		return section
	var path := VBoxContainer.new()
	path.add_theme_constant_override(&"separation", 0)
	section.add_child(path)
	var column: Array[SkillNode] = []
	for n in nodes:
		var state: SkillNode.State = PLACEHOLDER_STATES[n] if n < PLACEHOLDER_STATES.size() else SkillNode.State.LOCKED
		if n > 0:
			# Lit once the path has been walked past the node above it.
			path.add_child(_link(column[n - 1].state == SkillNode.State.LEARNED))
		var node := SkillNode.new(n + 1, state, _group)
		path.add_child(node)
		column.append(node)
	# Down from the last node goes nowhere rather than off the page.
	column[-1].focus_neighbor_bottom = column[-1].get_path_to(column[-1])
	_paths.append(column)
	return section


## Left and right move between the trees at the same depth, and stop at the
## outer ones rather than wandering into an empty column or the tabs.
func _link_across() -> void:
	for i in _paths.size():
		for n in _paths[i].size():
			var node: SkillNode = _paths[i][n]
			var left: SkillNode = _paths[i - 1][mini(n, _paths[i - 1].size() - 1)] if i > 0 else node
			var right: SkillNode = _paths[i + 1][mini(n, _paths[i + 1].size() - 1)] if i + 1 < _paths.size() else node
			node.focus_neighbor_left = node.get_path_to(left)
			node.focus_neighbor_right = node.get_path_to(right)


func _link(lit: bool) -> ColorRect:
	var link := ColorRect.new()
	link.color = ACCENT_COLOR if lit else BORDER_COLOR
	link.custom_minimum_size = LINK_SIZE
	link.size_flags_horizontal = SIZE_SHRINK_CENTER
	link.mouse_filter = MOUSE_FILTER_IGNORE
	return link


func _divider() -> VSeparator:
	var divider := VSeparator.new()
	var line := StyleBoxLine.new()
	line.color = BORDER_COLOR
	line.vertical = true
	divider.add_theme_stylebox_override(&"separator", line)
	return divider
