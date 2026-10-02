## The Roster's Skills page: a column for each of the character's skill trees,
## the trees of their Species, Sub-Species, Main Class and Multi-Class, each
## headed by its name ("Human"), or by its plain title ("Species") and empty
## while the character has none. The species' columns are narrow and the
## classes' three times as wide.
##
## Its sub-tab is titled with the character's unspent skill points, as
## "Skills (2)".
##
## Rebuilt for each character, since their trees may be shaped nothing like
## the last one's: each is drawn from its [SkillTree] by a [SkillTreeView].
## Nothing can be learned yet, so every node that requires none is open and
## the rest are locked.
class_name SkillsPage
extends CharacterPage

const TITLE := "Skills"
## Each column: the title it falls back to, the [Character] property holding
## the [SkillSource] whose tree it shows, and its share of the width. A new
## kind of tree is a row here.
const COLUMNS := [
	["Species", &"species", 1],
	["Sub-Species", &"sub_species", 1],
	["Main Class", &"main_class", 3],
	["Multi-Class", &"multi_class", 3],
]

const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const TITLE_COLOR := Color(0.7, 0.72, 0.78)

var _columns: HBoxContainer
var _group: ButtonGroup
## The trees shown, left to right; a column with no tree has none here.
var _trees: Array[SkillTreeView] = []


func _init() -> void:
	super(TITLE)
	_columns = HBoxContainer.new()
	_columns.set_anchors_preset(PRESET_FULL_RECT)
	_columns.add_theme_constant_override(&"separation", 0)
	add_child(_columns)
	_refresh()


## Builds the character's columns afresh, with a new group, which drops the
## selection on the last character's tree, and puts their skill points in the
## sub-tab's title.
func _refresh() -> void:
	for column in _columns.get_children():
		_columns.remove_child(column)
		column.queue_free()
	_trees.clear()
	_group = ButtonGroup.new()
	for i in COLUMNS.size():
		if i > 0:
			_columns.add_child(_divider())
		var source: SkillSource = character.get(COLUMNS[i][1]) if character != null else null
		_columns.add_child(_column(COLUMNS[i][0], source, COLUMNS[i][2]))

	var tabs := get_parent() as TabContainer
	if tabs != null:
		var title := TITLE if character == null else "%s (%d)" % [TITLE, character.skill_points]
		tabs.set_tab_title(tabs.get_tab_idx_from_control(self), title)


func focus_selection() -> bool:
	var target := _group.get_pressed_button()
	if target == null and not _trees.is_empty():
		target = _trees[0].first()
	if target == null:
		return false
	target.grab_focus()
	return true


## A column: its heading at the top and, under it, the tree of
## [param source], centred. Just the heading, [param title], without one.
func _column(title: String, source: SkillSource, share: int) -> VBoxContainer:
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
	# Nothing is learned until skill points can be spent.
	var learned: Array[StringName] = []
	var view := SkillTreeView.new(source.tree, learned, _group)
	view.size_flags_horizontal = SIZE_SHRINK_CENTER
	for button: SkillButton in view.buttons.values():
		button.focus_entered.connect(_aim_arrows.bind(button, view))
	column.add_child(view)
	_trees.append(view)
	return column


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
