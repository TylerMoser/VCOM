## The Roster's Skills page: a column for each of the character's skill trees
## ([constant Character.TREES]), the trees of their Species, Sub-Species, Main
## Class and Multi-Class, each headed by its name ("Human"), or by its plain
## title ("Species") and empty while the character has none. The species'
## columns are narrow and the classes' three times as wide.
##
## Its sub-tab is titled with the character's unspent skill points, as
## "Skills (2)".
##
## A node open to be learned is learned by holding it down (see
## [SkillButton]), for a skill point, through [code]Campaign.learn()[/code]:
## not during a mission, and never for someone not on the roster (read only).
## One that can be taken again is held again, once for each ring round it.
##
## Rebuilt for each character, since their trees may be shaped nothing like
## the last one's: each is drawn from its [SkillTree] by a [SkillTreeView].
## Learning only restyles the trees, so the selection and the keyboard stay
## where they were.
class_name SkillsPage
extends CharacterPage

const TITLE := "Skills"
## Each column's share of the page's width, by the [Character] property it
## shows (see [constant Character.TREES]); 1 for any not listed.
const SHARES := {&"species": 1, &"sub_species": 1, &"main_class": 3, &"multi_class": 3}

const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const TITLE_COLOR := Color(0.7, 0.72, 0.78)

var _columns: HBoxContainer
## The trees shown, left to right; a column with no tree has none here.
var _trees: Array[SkillTreeView] = []
## The node last given the keyboard, selected; null once the character changes.
var _selected: SkillButton


func _init() -> void:
	super(TITLE)
	_columns = HBoxContainer.new()
	_columns.set_anchors_preset(PRESET_FULL_RECT)
	_columns.add_theme_constant_override(&"separation", 0)
	add_child(_columns)
	_refresh()


## Builds the character's columns afresh, with nothing selected. Every tree
## is given the same row heights, each row as tall as its tallest node in any
## of them, so the trees' rows stay level across the page.
func _refresh() -> void:
	for column in _columns.get_children():
		_columns.remove_child(column)
		column.queue_free()
	_trees.clear()
	_selected = null
	var sources: Array[SkillSource] = []
	var trees: Array[SkillTree] = []
	for entry in Character.TREES:
		var source: SkillSource = character.get(entry[1]) if character != null else null
		sources.append(source)
		if source != null and source.tree != null:
			trees.append(source.tree)
	var heights := SkillTreeView.row_heights(trees)
	for i in Character.TREES.size():
		if i > 0:
			_columns.add_child(_divider())
		var entry: Array = Character.TREES[i]
		_columns.add_child(_column(entry[0], sources[i], SHARES.get(entry[1], 1), heights))
	_show_progress()


func focus_selection() -> bool:
	var target := _selected
	if target == null and not _trees.is_empty():
		target = _trees[0].first()
	if target == null:
		return false
	target.grab_focus()
	return true


## Shows what the character has learned of each tree, which nodes holding
## would learn now, and their unspent points in the sub-tab's title.
func _show_progress() -> void:
	var tabs := get_parent() as TabContainer
	if tabs != null:
		var title := TITLE if character == null else "%s (%d)" % [TITLE, character.skill_points]
		tabs.set_tab_title(tabs.get_tab_idx_from_control(self), title)
	# Built with no one to show before [code]Campaign[/code] exists: the pause
	# menu is made first.
	if character == null:
		return

	var locked := read_only or Campaign.in_mission
	for view in _trees:
		view.show_learned(character.learned_of(view.source))
		for button: SkillButton in view.buttons.values():
			button.learnable = not locked and character.can_learn(view.source, button.tree_node)


## A column: its heading at the top and, under it, the tree of
## [param source], centred, its rows [param heights] tall. Just the heading,
## [param title], without one.
func _column(title: String, source: SkillSource, share: int, heights: PackedFloat32Array) -> VBoxContainer:
	var column := VBoxContainer.new()
	column.size_flags_horizontal = SIZE_EXPAND_FILL
	column.size_flags_stretch_ratio = share
	column.add_theme_constant_override(&"separation", 16)

	var heading := Label.new()
	heading.text = source.display_name if source != null and not source.display_name.is_empty() else title
	heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	heading.add_theme_font_size_override(&"font_size", 16)
	heading.add_theme_color_override(&"font_color", TITLE_COLOR)
	column.add_child(heading)

	if source == null or source.tree == null or source.tree.nodes.is_empty():
		return column
	var view := SkillTreeView.new(source, heights)
	view.size_flags_horizontal = SIZE_SHRINK_CENTER
	for button: SkillButton in view.buttons.values():
		button.focus_entered.connect(_on_focused.bind(button, view))
		button.held.connect(_on_held.bind(button, view))
	column.add_child(view)
	_trees.append(view)
	return column


## Selects [param button], in place of the last one, and points the arrow keys
## from it.
func _on_focused(button: SkillButton, view: SkillTreeView) -> void:
	if _selected != null:
		_selected.selected = false
	_selected = button
	button.selected = true
	_aim_arrows(button, view)


func _on_held(button: SkillButton, view: SkillTreeView) -> void:
	if character != null and Campaign.learn(character, view.source, button.tree_node):
		_show_progress()


## Points the arrow keys from [param button], in [param view], at the nearest
## node each way, now that it has the keyboard and the trees are laid out
## however they are shaped: up and down within its own tree, left and right on
## into the trees beside it. With none that way it stays put, but for up, which
## is left to leave the trees for the sub-tabs.
func _aim_arrows(button: SkillButton, view: SkillTreeView) -> void:
	var everyone: Array = []
	for tree in _trees:
		everyone.append_array(tree.buttons.values())
	var own := view.buttons.values()
	var up := _nearest(button, Vector2.UP, own)
	button.focus_neighbor_top = button.get_path_to(up) if up != null else NodePath()
	for side in [[SIDE_BOTTOM, Vector2.DOWN, own], [SIDE_LEFT, Vector2.LEFT, everyone], [SIDE_RIGHT, Vector2.RIGHT, everyone]]:
		var next := _nearest(button, side[1], side[2])
		button.set_focus_neighbor(side[0], button.get_path_to(next if next != null else button))


## Of [param buttons], the nearest to [param from] in [param direction],
## straight that way before off to one side; null with none that way at all.
static func _nearest(from: SkillButton, direction: Vector2, buttons: Array) -> SkillButton:
	var origin := from.get_global_rect().get_center()
	var best: SkillButton = null
	var best_score := INF
	for button: SkillButton in buttons:
		var offset := button.get_global_rect().get_center() - origin
		var along := offset.dot(direction)
		if button == from or along <= 0.0:
			continue
		var score := along + absf(offset.cross(direction)) * 2.0
		if score < best_score:
			best = button
			best_score = score
	return best


func _divider() -> VSeparator:
	var divider := VSeparator.new()
	var line := StyleBoxLine.new()
	line.color = BORDER_COLOR
	line.vertical = true
	divider.add_theme_stylebox_override(&"separator", line)
	return divider
