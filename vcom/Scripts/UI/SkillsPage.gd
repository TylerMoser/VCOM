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
## A [SkillTooltip] beside a node says what its skill is: the node the mouse
## is over, or the one the keyboard is on, whichever of the mouse and the
## keyboard was used last.
##
## Trees taller than the page scroll, under headings that stay put: with the
## mouse wheel or the scroll bar, and to follow the keyboard from node to node.
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
## Between a column's heading and the top of its tree.
const HEADING_GAP := 16
## Between a node and the tooltip beside it.
const TOOLTIP_GAP := 10.0

## The columns' headings in a row of their own, and under it the trees,
## scrolling.
var _headings: HBoxContainer
var _scroll: ScrollContainer
var _columns: HBoxContainer
var _tooltip: SkillTooltip
## The trees shown, left to right; a column with no tree has none here.
var _trees: Array[SkillTreeView] = []
## The node last given the keyboard, selected; null once the character changes.
var _selected: SkillButton
## The node the mouse is over, and the one with the keyboard now, if any.
var _hovered: SkillButton
var _focused: SkillButton
## Whether a key was pressed since the mouse last did anything: the tooltip
## is then the keyboard's node's, not the one the mouse was left over.
var _by_keyboard := false


func _init() -> void:
	super(TITLE)
	var body := VBoxContainer.new()
	body.set_anchors_preset(PRESET_FULL_RECT)
	body.add_theme_constant_override(&"separation", 0)
	add_child(body)

	_scroll = ScrollContainer.new()
	_scroll.size_flags_vertical = SIZE_EXPAND_FILL
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	# The bar shows only once the trees run past the bottom, but its room is
	# kept clear beside them either way, so nothing shifts as it comes and
	# goes.
	_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_RESERVE
	_scroll.follow_focus = true

	# The headings are kept as clear of the bar's room as the trees are, so
	# each stays over its tree.
	var over_trees := MarginContainer.new()
	over_trees.add_theme_constant_override(&"margin_right", ceili(_scroll.get_v_scroll_bar().get_minimum_size().x))
	_headings = HBoxContainer.new()
	_headings.add_theme_constant_override(&"separation", 0)
	over_trees.add_child(_headings)
	body.add_child(over_trees)
	body.add_child(_scroll)

	_columns = HBoxContainer.new()
	_columns.size_flags_horizontal = SIZE_EXPAND_FILL
	# As tall as the scroll at least, so the dividers run all the way down.
	_columns.size_flags_vertical = SIZE_EXPAND_FILL
	_columns.add_theme_constant_override(&"separation", 0)
	# Scrolling moves the node a tooltip is beside.
	_columns.item_rect_changed.connect(_show_tooltip)
	_scroll.add_child(_columns)

	# After the trees, so it is drawn over them, and not in the scroll, which
	# would cut it off at its edges.
	_tooltip = SkillTooltip.new()
	_tooltip.visible = false
	add_child(_tooltip)
	_refresh()


## Notes which of the mouse and the keyboard was used last, before either
## moves anything, and hands the tooltip to its node. The gamepad counts as
## the keyboard: it moves the same focus.
func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	var by_keyboard := _by_keyboard
	if (event is InputEventKey or event is InputEventJoypadButton) and event.is_pressed():
		by_keyboard = true
	elif event is InputEventJoypadMotion and absf((event as InputEventJoypadMotion).axis_value) >= InputDevice.STICK_THRESHOLD:
		by_keyboard = true
	elif event is InputEventMouse:
		by_keyboard = false
	if by_keyboard != _by_keyboard:
		_by_keyboard = by_keyboard
		_show_tooltip()


## Builds the character's columns afresh, with nothing selected, scrolled to
## the top. Every tree is given the same row heights, each row as tall as its
## tallest node in any of them, so the trees' rows stay level across the page.
func _refresh() -> void:
	for row in [_headings, _columns]:
		for child in row.get_children():
			row.remove_child(child)
			child.queue_free()
	_trees.clear()
	_selected = null
	_hovered = null
	_focused = null
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
			_headings.add_child(_divider())
			_columns.add_child(_divider())
		var entry: Array = Character.TREES[i]
		_add_column(entry[0], sources[i], SHARES.get(entry[1], 1), heights)
	_scroll.scroll_vertical = 0
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
		_show_tooltip()
		return

	var locked := read_only or Campaign.in_mission
	for view in _trees:
		view.show_learned(character.learned_of(view.source))
		for button: SkillButton in view.buttons.values():
			button.learnable = not locked and character.can_learn(view.source, button.tree_node)
	# A level just taken changes what its tooltip says.
	_show_tooltip()


## Shows the tooltip beside the node it is for, or hides it with none: the
## node with the keyboard when a key was pressed last, else the one under the
## mouse. None for a node scrolled out of sight, as the wheel can scroll the
## one under the mouse.
func _show_tooltip() -> void:
	var target := _focused if _by_keyboard and _focused != null else _hovered
	if target == null or target.tree_node.skill == null or not _scroll.get_global_rect().intersects(target.get_global_rect()):
		_tooltip.visible = false
		return
	_tooltip.show_skill(target.tree_node.skill, target.taken)
	_tooltip.visible = true
	# To the node's right, or its left where that would run off the page, and
	# no lower than the page's bottom.
	var node := Rect2(target.global_position - global_position, target.size)
	var at := Vector2(node.end.x + TOOLTIP_GAP, node.position.y)
	if at.x + _tooltip.size.x > size.x:
		at.x = node.position.x - TOOLTIP_GAP - _tooltip.size.x
	at.y = clampf(at.y, 0.0, maxf(size.y - _tooltip.size.y, 0.0))
	_tooltip.position = at


## A column: its heading in the headings' row, [param source]'s name or else
## [param title], and under it in the trees' row the source's tree, centred,
## its rows [param heights] tall, or nothing without one.
##
## The two rows are laid out apart, so the heading and the tree are each made
## as wide as the wider of the two: the rows then share their width out
## alike, and every heading stays over its tree.
func _add_column(title: String, source: SkillSource, share: int, heights: PackedFloat32Array) -> void:
	var heading := Label.new()
	heading.text = source.display_name if source != null and not source.display_name.is_empty() else title
	heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	heading.size_flags_horizontal = SIZE_EXPAND_FILL
	heading.size_flags_stretch_ratio = share
	heading.add_theme_font_size_override(&"font_size", 16)
	heading.add_theme_color_override(&"font_color", TITLE_COLOR)
	# The gap under it is part of it, so the dividers beside it run on down
	# into the trees'.
	var gap := StyleBoxEmpty.new()
	gap.content_margin_bottom = HEADING_GAP
	heading.add_theme_stylebox_override(&"normal", gap)
	_headings.add_child(heading)

	var column := VBoxContainer.new()
	column.size_flags_horizontal = SIZE_EXPAND_FILL
	column.size_flags_stretch_ratio = share
	_columns.add_child(column)
	var width := heading.get_minimum_size().x
	if source != null and source.tree != null and not source.tree.nodes.is_empty():
		var view := SkillTreeView.new(source, heights)
		view.size_flags_horizontal = SIZE_SHRINK_CENTER
		for button: SkillButton in view.buttons.values():
			button.focus_entered.connect(_on_focused.bind(button, view))
			button.focus_exited.connect(_on_unfocused.bind(button))
			button.mouse_entered.connect(_on_hovered.bind(button, true))
			button.mouse_exited.connect(_on_hovered.bind(button, false))
			button.held.connect(_on_held.bind(button, view))
		column.add_child(view)
		_trees.append(view)
		width = maxf(width, view.custom_minimum_size.x)
	heading.custom_minimum_size.x = width
	column.custom_minimum_size.x = width


## Selects [param button], in place of the last one, and points the arrow keys
## from it.
func _on_focused(button: SkillButton, view: SkillTreeView) -> void:
	if _selected != null:
		_selected.selected = false
	_selected = button
	button.selected = true
	_focused = button
	_aim_arrows(button, view)
	_show_tooltip()


## The keyboard has left [param button]: for another node, which has said so
## already, or for somewhere off the trees.
func _on_unfocused(button: SkillButton) -> void:
	if _focused == button:
		_focused = null
		_show_tooltip()


func _on_hovered(button: SkillButton, over: bool) -> void:
	if over:
		_hovered = button
	elif _hovered == button:
		_hovered = null
	_show_tooltip()


func _on_held(button: SkillButton, view: SkillTreeView) -> void:
	if character != null and Campaign.learn(character, view.source, button.tree_node):
		_show_progress()


## Points the arrow keys from [param button], in [param view], at the nearest
## node each way, now that it has the keyboard and the trees are laid out
## however they are shaped: up and down within its own tree, left and right on
## into the trees beside it. With none to the left or right it stays put. With
## none above or below it, the key is left to leave the trees: up for the
## sub-tabs, down for whatever lies under the page (the squad menu's Start, a
## hiring board's Hire), and nowhere when nothing does.
func _aim_arrows(button: SkillButton, view: SkillTreeView) -> void:
	var everyone: Array = []
	for tree in _trees:
		everyone.append_array(tree.buttons.values())
	var own := view.buttons.values()
	for side in [[SIDE_TOP, Vector2.UP], [SIDE_BOTTOM, Vector2.DOWN]]:
		var next := _nearest(button, side[1], own)
		button.set_focus_neighbor(side[0], button.get_path_to(next) if next != null else NodePath())
	for side in [[SIDE_LEFT, Vector2.LEFT], [SIDE_RIGHT, Vector2.RIGHT]]:
		var next := _nearest(button, side[1], everyone)
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
