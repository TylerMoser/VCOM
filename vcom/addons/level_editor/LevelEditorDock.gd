@tool
## The level editor's dock: the palette of every kind of piece and every brush
## in the level's library, and how a click paints - paint or erase, in the
## middle of a cell or on an edge, which floor, which way turned, how big a
## square. It holds the choices; the plugin (LevelEditorPlugin.gd) reads them,
## and works the 3D view. Built in code, as the game's own menus are.
extends VBoxContainer

signal changed
## The Import GridMap, Rebuild and Save buttons.
signal import_requested
signal rebuild_requested
signal save_requested

enum Mode { PAINT, ERASE }

## The lowest and highest floor a click paints, and the smallest and biggest
## square, by the panel and by the keys alike.
const FLOORS := Vector2i(-8, 32)
const SIZES := Vector2i(1, 15)

var mode := Mode.PAINT
## Whether a click goes on the edge between two cells rather than in the middle
## of one.
var on_edge := false
## The level a click paints, in cells up from the level's own origin.
var floor_level := 1
## Quarter turns about up, counterclockwise seen from above.
var turn := 0
## Cells to a side of the square a click paints.
var brush_size := 1

var _library: PieceLibrary
var _title: Label
var _counts: Label
var _palette: ItemList
var _paint: Button
var _erase: Button
var _middle: Button
var _edge: Button
var _floor: SpinBox
var _turn: OptionButton
var _size: SpinBox
## What each entry of the palette is, in order: a [PieceKind] or a [PieceBrush].
var _entries: Array[Resource] = []
var _updating := false


func _init() -> void:
	name = "Level"
	custom_minimum_size = Vector2(250, 0)
	_title = Label.new()
	_title.text = "No level selected"
	_title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_title)
	_counts = Label.new()
	_counts.modulate = Color(1, 1, 1, 0.7)
	add_child(_counts)

	var modes := HBoxContainer.new()
	add_child(modes)
	var mode_group := ButtonGroup.new()
	_paint = _toggle(modes, "Paint", mode_group, "Left click places the selection (Shift: erase).")
	_erase = _toggle(modes, "Erase", mode_group, "Left click takes the last piece out of each slot (right click always erases).")
	_paint.button_pressed = true
	_paint.toggled.connect(func(on: bool) -> void: if on: _set_mode(Mode.PAINT))
	_erase.toggled.connect(func(on: bool) -> void: if on: _set_mode(Mode.ERASE))

	var places := HBoxContainer.new()
	add_child(places)
	var place_group := ButtonGroup.new()
	_middle = _toggle(places, "Middle", place_group, "Place in the middle of a cell, as a block (T toggles).")
	_edge = _toggle(places, "Edge", place_group, "Place on the edge between two cells, as a fence or a wall (T toggles).")
	_middle.button_pressed = true
	_middle.toggled.connect(func(on: bool) -> void: if on: set_on_edge(false))
	_edge.toggled.connect(func(on: bool) -> void: if on: set_on_edge(true))

	var grid := GridContainer.new()
	grid.columns = 2
	add_child(grid)
	_floor = _spin(grid, "Floor (Q / E)", FLOORS.x, FLOORS.y, floor_level)
	_floor.value_changed.connect(func(value: float) -> void: if not _updating: floor_level = int(value); changed.emit())
	var turn_label := Label.new()
	turn_label.text = "Turn (S)"
	grid.add_child(turn_label)
	_turn = OptionButton.new()
	for degrees in [0, 90, 180, 270]:
		_turn.add_item("%d°" % degrees)
	_turn.item_selected.connect(func(index: int) -> void: if not _updating: turn = index; changed.emit())
	grid.add_child(_turn)
	_size = _spin(grid, "Size ([ / ])", SIZES.x, SIZES.y, brush_size)
	_size.value_changed.connect(func(value: float) -> void: if not _updating: brush_size = int(value); changed.emit())

	var palette_label := Label.new()
	palette_label.text = "Pieces and brushes"
	add_child(palette_label)
	_palette = ItemList.new()
	_palette.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_palette.custom_minimum_size = Vector2(0, 260)
	_palette.fixed_icon_size = Vector2i(48, 48)
	_palette.icon_mode = ItemList.ICON_MODE_LEFT
	_palette.item_selected.connect(_on_selected)
	add_child(_palette)

	var buttons := HBoxContainer.new()
	add_child(buttons)
	for entry in [["Import GridMap", import_requested, "Make this level from a GridMap in the scene, every block a piece in the middle of its cell."],
			["Rebuild", rebuild_requested, "Build the level afresh from its pieces."],
			["Save", save_requested, "Save the level's pieces to its file."]]:
		var button := Button.new()
		button.text = entry[0]
		button.tooltip_text = entry[2]
		var emitting: Signal = entry[1]
		button.pressed.connect(func() -> void: emitting.emit())
		buttons.add_child(button)

	var help := Label.new()
	help.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	help.modulate = Color(1, 1, 1, 0.7)
	help.text = (
		"Left click / drag: paint (Shift: erase). Right click / drag: erase. "
		+ "Alt + click: pick the piece under the cursor. Q / E: floor down / up. "
		+ "S / Shift+S: turn. T: middle or edge. [ / ]: size. Ctrl+Z: undo."
	)
	add_child(help)


## Shows [param level]'s library in the palette, and what it holds.
func show_level(level: VoxelLevel) -> void:
	if level == null:
		_title.text = "No level selected"
		_counts.text = ""
		return
	_title.text = "%s%s" % [level.name, " (scenery)" if level.scenery else ""]
	if level.data != null:
		_counts.text = "%d pieces - %s" % [level.data.count(), level.data.resource_path.get_file()]
	else:
		_counts.text = "No level data: Import a GridMap, or give it a LevelData."
	if level.library != _library:
		_library = level.library
		_fill_palette()


## Refreshes the count of pieces shown for [param level].
func show_count(level: VoxelLevel) -> void:
	if level != null and level.data != null:
		_counts.text = "%d pieces - %s" % [level.data.count(), level.data.resource_path.get_file()]


## What a click places: the palette's selection.
func selection() -> Resource:
	var picked := _palette.get_selected_items()
	if picked.is_empty() or picked[0] >= _entries.size():
		return null
	return _entries[picked[0]]


## Selects the kind of piece [param id] in the palette, as picking it in the
## view does.
func select_kind(id: StringName) -> void:
	for index in _entries.size():
		var entry := _entries[index]
		if entry is PieceKind and (entry as PieceKind).id == id:
			_palette.select(index)
			_on_selected(index)
			return


## Goes up or down [param by] floors, no further than the panel shows.
func step_floor(by: int) -> void:
	floor_level = clampi(floor_level + by, FLOORS.x, FLOORS.y)
	_sync()


## Turns [param by] quarter turns.
func step_turn(by: int) -> void:
	turn = posmod(turn + by, 4)
	_sync()


## Grows or shrinks the square a click paints by [param by] cells a side.
func step_size(by: int) -> void:
	brush_size = clampi(brush_size + by, SIZES.x, SIZES.y)
	_sync()


## Puts a click on the edge between cells, or in the middle of one.
func set_on_edge(edge: bool) -> void:
	on_edge = edge
	_sync()


func _set_mode(to: Mode) -> void:
	mode = to
	changed.emit()


func _sync() -> void:
	_updating = true
	_floor.value = floor_level
	_turn.select(turn)
	_size.value = brush_size
	_middle.set_pressed_no_signal(not on_edge)
	_edge.set_pressed_no_signal(on_edge)
	_paint.set_pressed_no_signal(mode == Mode.PAINT)
	_erase.set_pressed_no_signal(mode == Mode.ERASE)
	_updating = false
	changed.emit()


func _on_selected(index: int) -> void:
	# A fence or a wall goes on an edge to begin with.
	var entry := _entries[index] if index < _entries.size() else null
	if entry is PieceKind:
		set_on_edge((entry as PieceKind).edge_piece)
	elif entry is PieceBrush:
		var brush := entry as PieceBrush
		var first: PieceKind = _library.find(brush.kinds[0]) if brush.size() > 0 and _library != null else null
		if first != null:
			set_on_edge(first.edge_piece)
	changed.emit()


func _fill_palette() -> void:
	_palette.clear()
	_entries.clear()
	if _library == null:
		return
	for kind in _library.kinds:
		if kind == null:
			continue
		var at := _palette.add_item("%s%s" % [kind.display_name(), "  (edge)" if kind.edge_piece else ("  (decoration)" if not kind.solid else "")])
		_entries.append(kind)
		_preview(kind.model, at)
	for brush in _library.brushes:
		if brush == null:
			continue
		var at := _palette.add_item("Brush: %s (%d)" % [brush.display_name, brush.size()])
		_entries.append(brush)
		var first: PieceKind = _library.find(brush.kinds[0]) if brush.size() > 0 else null
		if first != null:
			_preview(first.model, at)
	if _palette.item_count > 0:
		_palette.select(0)


## Fetches a picture of [param model] for the palette's entry [param at].
func _preview(model: Mesh, at: int) -> void:
	if model == null or not Engine.is_editor_hint():
		return
	var previewer := EditorInterface.get_resource_previewer()
	previewer.queue_edited_resource_preview(model, self, &"_on_preview", at)


func _on_preview(_path: String, preview: Texture2D, _thumbnail: Texture2D, at: Variant) -> void:
	if preview != null and int(at) < _palette.item_count:
		_palette.set_item_icon(int(at), preview)


static func _toggle(parent: Control, text: String, group: ButtonGroup, tip: String) -> Button:
	var button := Button.new()
	button.text = text
	button.toggle_mode = true
	button.button_group = group
	button.tooltip_text = tip
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parent.add_child(button)
	return button


static func _spin(parent: Control, text: String, low: int, high: int, value: int) -> SpinBox:
	var label := Label.new()
	label.text = text
	parent.add_child(label)
	var spin := SpinBox.new()
	spin.min_value = low
	spin.max_value = high
	spin.value = value
	spin.step = 1
	parent.add_child(spin)
	return spin
