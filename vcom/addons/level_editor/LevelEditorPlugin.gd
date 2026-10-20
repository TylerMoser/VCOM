@tool
## The level editor: paints a combat map's [VoxelLevel] in Godot's own 3D view,
## as the GridMap editor painted its blocks, with kinds of piece and brushes of
## several from the level's [PieceLibrary], in the middles of cells and on the
## edges between them.
##
## Select a VoxelLevel node and the Level panel beside the 3D view shows its
## palette. With the
## mouse over the 3D view, a grid shows the floor being painted and a ghost the
## pieces a click would place; left click places them, dragging places more,
## right click (or Shift, or the dock's Erase) takes out the last piece placed
## in each slot. Q and E go down and up a floor, S and Shift+S turn, T moves
## between the middle of a cell and its edge, [ and ] shrink and grow the
## square a click paints, Alt and a click picks the kind under the cursor.
## Those keys are the level editor's alone while a level is selected, over
## Godot's own shortcuts on them.
## Every stroke, press to release, is one step of the scene's undo history.
##
## A level's pieces are its own resource ([LevelData]), saved to its file as
## the scene is saved. The level is drawn again as it is painted, only the
## chunks a click reaches ([method VoxelLevel.place]).
extends EditorPlugin

const Dock := preload("res://addons/level_editor/LevelEditorDock.gd")
const Cursor := preload("res://addons/level_editor/LevelCursor.gd")

var _dock: Dock
var _docked := false
var _cursor: Cursor
## The level being edited.
var _level: VoxelLevel
## The stroke under way: what it has done so far, as [method LevelEditing.apply]
## returns it; every slot it has painted or erased in, as a set, so a square
## dragged over one again, or over a slot of the square before, leaves it be;
## whether it erases.
var _stroke := []
var _stroke_slots := {}
var _stroking := false
var _stroke_erases := false
## The axis the edges of the stroke under way stand across, once it has begun
## on one: it keeps to edges that way ([method LevelEditing.slot_at]).
var _stroke_axis := -1
## Where the mouse last met the floor being painted, in the level's space.
var _hit := Vector3.ZERO
var _has_hit := false
var _shift := false
## Every level's pieces changed since they were last saved, as a set.
var _edited := {}
## The probe driving the editor, if one is, kept while it runs.
var _probe: Object


func _enter_tree() -> void:
	_dock = Dock.new()
	_dock.changed.connect(_refresh_cursor)
	_dock.import_requested.connect(_import_grid_map)
	_dock.rebuild_requested.connect(_rebuild)
	_dock.save_requested.connect(_save_external_data)
	# A probe drives the editor through a script of its own, named by this, as
	# the game is driven by --script: given this plugin, it runs once the
	# editor is up (Docs/LEVEL_EDITOR.md, Probing it).
	var probe := OS.get_environment("VCOM_LEVEL_EDITOR_PROBE")
	if not probe.is_empty():
		var script := load(probe) as GDScript
		if script == null:
			push_error("Level Editor: no probe script at '%s'." % probe)
		else:
			_probe = script.new()
			_probe.call_deferred(&"run", self)


func _exit_tree() -> void:
	_undock()
	_remove_cursor()
	if _dock != null:
		_dock.queue_free()
		_dock = null


func _get_plugin_name() -> String:
	return "Level Editor"


func _handles(object: Object) -> bool:
	return object is VoxelLevel


func _edit(object: Object) -> void:
	var level := object as VoxelLevel
	if level == _level:
		return
	_end_stroke()
	_remove_cursor()
	_level = level
	if _level != null:
		_dock.show_level(_level)
		_cursor = Cursor.new()
		_level.add_child(_cursor, false, Node.INTERNAL_MODE_BACK)
		_cursor.visible = false


func _make_visible(visible: bool) -> void:
	if visible:
		# Beside the 3D view, as the GridMap editor's palette is, so it is in
		# sight whenever a level is selected, never a tab behind the Inspector.
		if not _docked:
			add_control_to_container(CONTAINER_SPATIAL_EDITOR_SIDE_RIGHT, _dock)
			_docked = true
		if _level != null:
			_dock.show_level(_level)
	else:
		_end_stroke()
		_undock()
		if _cursor != null:
			_cursor.visible = false


func _forward_3d_gui_input(camera: Camera3D, event: InputEvent) -> int:
	if _level == null or _level.data == null or _level.library == null:
		return EditorPlugin.AFTER_GUI_INPUT_PASS
	if event is InputEventMouseMotion:
		var motion := event as InputEventMouseMotion
		_shift = motion.shift_pressed
		_aim(camera, motion.position)
		if _stroking:
			_paint()
			return EditorPlugin.AFTER_GUI_INPUT_STOP
		return EditorPlugin.AFTER_GUI_INPUT_PASS
	if event is InputEventMouseButton:
		var button := event as InputEventMouseButton
		if button.button_index != MOUSE_BUTTON_LEFT and button.button_index != MOUSE_BUTTON_RIGHT:
			return EditorPlugin.AFTER_GUI_INPUT_PASS
		_shift = button.shift_pressed
		_aim(camera, button.position)
		if button.pressed:
			if button.button_index == MOUSE_BUTTON_LEFT and button.alt_pressed:
				_pick()
				return EditorPlugin.AFTER_GUI_INPUT_STOP
			var erases := button.button_index == MOUSE_BUTTON_RIGHT or button.shift_pressed or _dock.mode == Dock.Mode.ERASE
			_begin_stroke(erases)
			_paint()
		else:
			_end_stroke()
		return EditorPlugin.AFTER_GUI_INPUT_STOP
	if event is InputEventKey:
		var key := event as InputEventKey
		if not key.pressed or key.echo or key.ctrl_pressed or key.meta_pressed or key.alt_pressed:
			return EditorPlugin.AFTER_GUI_INPUT_PASS
		match key.keycode:
			KEY_Q:
				_dock.step_floor(-1)
			KEY_E:
				_dock.step_floor(1)
			KEY_S:
				_dock.step_turn(-1 if key.shift_pressed else 1)
			KEY_T:
				_dock.set_on_edge(not _dock.on_edge)
			KEY_BRACKETLEFT:
				_dock.step_size(-1)
			KEY_BRACKETRIGHT:
				_dock.step_size(1)
			_:
				return EditorPlugin.AFTER_GUI_INPUT_PASS
		_refresh_cursor()
		# The key is the level editor's alone. Stopping it here keeps it from
		# the 3D view but not from Godot's shortcuts, which come after: Q would
		# pick its Select tool as well, E Rotate, T local space.
		get_viewport().set_input_as_handled()
		return EditorPlugin.AFTER_GUI_INPUT_STOP
	return EditorPlugin.AFTER_GUI_INPUT_PASS


## Saves every level's pieces changed since they were last saved: as the
## scene is saved, or the dock's Save is pressed.
func _save_external_data() -> void:
	for data: LevelData in _edited.keys():
		if is_instance_valid(data) and not data.resource_path.is_empty() and not data.resource_path.contains("::"):
			var error := ResourceSaver.save(data, data.resource_path)
			if error != OK:
				push_error("Level Editor: could not save '%s' (%s)." % [data.resource_path, error_string(error)])
	_edited.clear()


## Finds where the ray from [param camera] through [param at], a point in the
## view, meets the floor being painted, and shows what a click there would do.
func _aim(camera: Camera3D, at: Vector2) -> void:
	var origin := _level.to_local(camera.project_ray_origin(at))
	var heading := _level.global_basis.inverse() * camera.project_ray_normal(at)
	_has_hit = false
	if absf(heading.y) > 1e-5:
		var t := (float(_dock.floor_level) - origin.y) / heading.y
		if t > 0.0:
			_hit = origin + heading * t
			_has_hit = true
	_refresh_cursor()


## Shows what a click at the cursor would do, or hides it with the cursor off
## the floor.
func _refresh_cursor() -> void:
	if _cursor == null or _level == null:
		return
	if not _has_hit:
		_cursor.visible = false
		return
	var slot := LevelEditing.slot_at(Vector3(_hit.x, _dock.floor_level, _hit.z), _dock.on_edge, _stroke_axis if _stroking else -1)
	var erasing := _stroke_erases if _stroking else (_shift or _dock.mode == Dock.Mode.ERASE)
	var selection := _dock.selection()
	var placed := LevelEditing.placements(selection, slot, _dock.turn, _dock.brush_size)
	var slots := LevelEditing.erasures(selection, slot, _dock.turn, _dock.brush_size)
	_cursor.show_at(_level, _level.library, placed, slots, erasing, _dock.floor_level, _hit)


func _begin_stroke(erases: bool) -> void:
	_end_stroke()
	_stroking = true
	_stroke_erases = erases
	_stroke_axis = -1
	_stroke.clear()
	_stroke_slots.clear()


## Paints, or erases, at the cursor: each slot once a stroke, however many
## times the square passes over it, so an erasing drag takes one piece a slot
## and no more. The slots one click fills may repeat (a brush's pieces can share
## one), so only those of the clicks before are left out.
func _paint() -> void:
	if not _stroking or not _has_hit:
		return
	var slot := LevelEditing.slot_at(Vector3(_hit.x, _dock.floor_level, _hit.z), _dock.on_edge, _stroke_axis)
	if _stroke_axis < 0:
		_stroke_axis = LevelEditing.edge_axis(slot)
	var selection := _dock.selection()
	var edits := []
	if _stroke_erases:
		for each in LevelEditing.erasures(selection, slot, _dock.turn, _dock.brush_size):
			if not _stroke_slots.has(each):
				edits.append(["erase", each])
	elif selection != null:
		for placed: Array in LevelEditing.placements(selection, slot, _dock.turn, _dock.brush_size):
			if not _stroke_slots.has(placed[1]):
				edits.append(["add", placed[0], placed[1], placed[2]])
	if edits.is_empty():
		return
	for edit: Array in edits:
		_stroke_slots[edit[1] if edit[0] == "erase" else edit[2]] = true
	var done := LevelEditing.apply(_level, edits)
	if done.is_empty():
		return
	_stroke.append_array(done)
	_touched(_level)


## Makes the stroke one step of the scene's undo history, done already.
func _end_stroke() -> void:
	if not _stroking:
		return
	_stroking = false
	if _stroke.is_empty() or _level == null:
		return
	var done := _stroke.duplicate(true)
	var undo := get_undo_redo()
	undo.create_action("%s %s" % ["Erase in" if _stroke_erases else "Paint", _level.name], UndoRedo.MERGE_DISABLE, _level)
	undo.add_do_method(self, &"_redo", _level, done)
	undo.add_undo_method(self, &"_undo", _level, done)
	undo.commit_action(false)
	_stroke.clear()


func _redo(level: VoxelLevel, done: Array) -> void:
	LevelEditing.redo(level, done)
	_touched(level)


func _undo(level: VoxelLevel, done: Array) -> void:
	LevelEditing.undo(level, done)
	_touched(level)


## Notes [param level]'s pieces as changed, to be saved with the scene.
func _touched(level: VoxelLevel) -> void:
	if level.data != null:
		_edited[level.data] = true
	EditorInterface.mark_scene_as_unsaved()
	if level == _level:
		_dock.show_count(level)
	_refresh_cursor()


## Selects the kind of the last piece placed in the slot under the cursor.
func _pick() -> void:
	if not _has_hit:
		return
	var slot := LevelEditing.slot_at(Vector3(_hit.x, _dock.floor_level, _hit.z), _dock.on_edge)
	var here := _level.data.indices_at(slot)
	if not here.is_empty():
		_dock.select_kind(_level.data.kind_id(here[here.size() - 1]))
		_refresh_cursor()


## Makes the level's pieces those of the first GridMap in the edited scene,
## every block a piece in the middle of its cell: undoable, the level's file
## kept. A level with no data gets a file of its own in res://Levels.
func _import_grid_map() -> void:
	if _level == null:
		return
	var root := EditorInterface.get_edited_scene_root()
	var found: Array = root.find_children("*", "GridMap", true, false) if root != null else []
	if found.is_empty():
		push_warning("Level Editor: no GridMap in the scene to import.")
		return
	var grid := found[0] as GridMap
	var made := LevelImport.from_grid_map(grid)
	if _level.data == null:
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://Levels"))
		var path := "res://Levels/%s%s.tres" % [root.name, "" if _level.name == "Level" else String(_level.name)]
		ResourceSaver.save(made, path)
		_level.data = load(path)
		_touched(_level)
		return
	var data := _level.data
	var undo := get_undo_redo()
	undo.create_action("Import %s into %s" % [grid.name, _level.name], UndoRedo.MERGE_DISABLE, _level)
	undo.add_do_property(data, &"kinds", made.kinds)
	undo.add_do_property(data, &"pieces", made.pieces)
	undo.add_do_method(_level, &"build")
	undo.add_do_method(self, &"_touched", _level)
	undo.add_undo_property(data, &"kinds", data.kinds.duplicate())
	undo.add_undo_property(data, &"pieces", data.pieces.duplicate())
	undo.add_undo_method(_level, &"build")
	undo.add_undo_method(self, &"_touched", _level)
	undo.commit_action()


func _rebuild() -> void:
	if _level != null:
		_level.build()
		_dock.show_count(_level)


func _undock() -> void:
	if _docked and _dock != null:
		remove_control_from_container(CONTAINER_SPATIAL_EDITOR_SIDE_RIGHT, _dock)
		_docked = false


func _remove_cursor() -> void:
	if _cursor != null and is_instance_valid(_cursor):
		_cursor.queue_free()
	_cursor = null
