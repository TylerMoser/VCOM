@tool
## A combat map's ground, walls, trees and scenery: a level built of pieces
## ([LevelData], [PieceKind]), as the level editor (addons/level_editor) leaves
## it, in place of the GridMaps the maps were once painted in.
##
## Built afresh every time the map loads, in the editor as in the game. A
## battlefield gives the rules what stands where ([member rules]), and every
## voxel of its pieces as one grid ([member volume]), which it draws a chunk at
## a time with every hidden face left out, and which destruction wears and
## blood recolours. Scenery ([member scenery]) is only drawn, every piece of a
## kind one mesh shared by all, and coarser copies of them further from the
## battlefield it surrounds ([member battlefield_path]).
##
## Its space is the grid's: cell (x, y, z) runs from (x, y, z) to
## (x + 1, y + 1, z + 1), sixteen voxels a side, as a GridMap's cells did with
## cells a metre across and centred.
class_name VoxelLevel
extends Node3D

## Emitted once it has been built afresh.
signal built

## The pieces it is built of. A level's [LevelData] is its own file, shared
## with nothing else.
@export var data: LevelData:
	set(value):
		data = value
		if is_node_ready():
			build()
## The kinds of piece it is built of.
@export var library: PieceLibrary:
	set(value):
		library = value
		if is_node_ready():
			build()
## Whether it is only scenery: drawn, but nothing in the rules, nothing that
## breaks, no collision.
@export var scenery := false:
	set(value):
		scenery = value
		if is_node_ready():
			build()
## Scenery only: the battlefield it surrounds, whose edge its rows of level of
## detail are counted from ([SceneryRenderer]'s constants say which rows draw
## which copy). With none there, every piece is drawn in full detail.
@export var battlefield_path: NodePath = ^"../Level"

## What the rules see of it, and every voxel of it: a battlefield's; null for
## scenery.
var rules: LevelRules
var volume: VoxelVolume
## What draws it.
var renderer: LevelRenderer
var scenery_renderer: SceneryRenderer
## How long the last build took, in microseconds: the voxels, and drawing them.
var build_times := Vector2i.ZERO
## The most time a frame gives to drawing again what destruction has worn, in
## microseconds, beyond what it asks to be drawn at once
## ([method redraw_now]); and to giving chunks the collision they are still
## waiting for, after the level is built.
var redraw_budget := 4000
var collision_budget := 2000
## How deep edits are batched ([method begin_edit]), and the slots they have
## changed meanwhile, as a set.
var _batching := 0
var _pending := {}


func _ready() -> void:
	build()


func _process(_delta: float) -> void:
	if renderer == null:
		return
	if not volume.dirty.is_empty() or not volume.dirty_colors.is_empty() or volume.has_bare():
		renderer.refresh(redraw_budget)
	if not renderer.is_collided():
		renderer.stream_collision(collision_budget)


## A chunk drawn again since the last physics step is given its collision
## again here, ahead of the step and ahead of the debris (VoxelDebris lets
## what wear broke off go in its own [method Node._physics_process], after
## this one in the tree): so a bite's lumps never start out inside the voxels
## they were, and the collision is made a frame after the bite is drawn, not
## on the bite's own frame.
func _physics_process(_delta: float) -> void:
	if renderer != null and renderer.has_worn_collision():
		renderer.stream_collision(collision_budget, true)


## Gives collision now to the chunks round [param box], in the world, before
## debris is put there: a level is given its collision over the frames after
## it is built, and what lands where there is none yet would fall through.
func ensure_collision(box: AABB) -> void:
	if renderer == null:
		return
	var local := global_transform.affine_inverse() * box
	renderer.ensure_collision(VoxelVolume.voxel_under(local.position), VoxelVolume.voxel_under(local.end))


## Builds it afresh from its [member data]: what the rules see, its voxels, and
## what draws them.
func build() -> void:
	if renderer != null:
		renderer.queue_free()
		renderer = null
	if scenery_renderer != null:
		scenery_renderer.queue_free()
		scenery_renderer = null
	rules = null
	volume = null
	if data == null or library == null:
		return
	if scenery:
		scenery_renderer = SceneryRenderer.new(data, library)
		var field := get_node_or_null(battlefield_path) as VoxelLevel
		if field != null and field.rules != null:
			var low := field.rules.bounds_min
			var high := field.rules.bounds_max
			scenery_renderer.battlefield = Rect2i(low.x, low.z, high.x - low.x + 1, high.z - low.z + 1)
		elif not battlefield_path.is_empty():
			push_error("VoxelLevel: no battlefield at '%s' for the scenery's level of detail: it is all drawn in full." % battlefield_path)
		add_child(scenery_renderer, false, Node.INTERNAL_MODE_FRONT)
		build_times = Vector2i(0, scenery_renderer.build())
		built.emit()
		return
	rules = LevelRules.new(data, library)
	volume = VoxelVolume.new(data, library)
	var voxels_took := volume.build()
	renderer = LevelRenderer.new(volume, not Engine.is_editor_hint())
	add_child(renderer, false, Node.INTERNAL_MODE_FRONT)
	build_times = Vector2i(voxels_took, renderer.build())
	built.emit()


## Draws again, now, whatever has worn since it was last drawn: for a round's
## bite, seen at once, where a blast's craters are drawn over a few frames.
func redraw_now() -> void:
	if renderer != null:
		renderer.refresh()


## Places a piece of the kind [param id] in [param slot], turned [param turn]
## quarter turns, last of all, so it wins where it overlaps any piece before it,
## and draws it. Returns its index. For the level editor: in a battle, the rules
## and the grid have taken their own hold of the level as it loaded.
func place(id: StringName, slot: Vector3i, turn: int) -> int:
	var index := data.add(id, slot, turn)
	_edited([slot], index, -1)
	return index


## Places a piece as [method place] does, but at [param index] in the order:
## how undoing an erase puts a piece back where it was.
func insert(index: int, id: StringName, slot: Vector3i, turn: int) -> void:
	data.insert(index, id, slot, turn)
	_edited([slot], index, -1)


## Takes piece [param index] out, and draws again what it covered. Returns what
## it was: its kind's id, its slot and its turn.
func remove(index: int) -> Array:
	var was := [data.kind_id(index), data.slot_at(index), data.turn_at(index)]
	data.remove(index)
	_edited([was[1]], -1, index)
	return was


## Takes out the piece placed last in [param slot], if there is one, as
## [method remove] does. Returns its index then, or -1 if the slot was empty.
func erase(slot: Vector3i) -> int:
	var here := data.indices_at(slot)
	if here.is_empty():
		return -1
	var index := here[here.size() - 1]
	remove(index)
	return index


## Holds back drawing again after each piece placed or taken out until
## [method end_edit], which draws everything they changed at once: a click
## with a brush or a big square places many.
func begin_edit() -> void:
	_batching += 1


## Draws everything changed since [method begin_edit].
func end_edit() -> void:
	_batching = maxi(_batching - 1, 0)
	if _batching == 0 and not _pending.is_empty():
		var slots: Array[Vector3i] = []
		slots.assign(_pending.keys())
		_pending.clear()
		_redraw_slots(slots)


## Brings what the rules see, the voxels and what draws them up to date with
## [member data] after pieces in [param slots] changed: [param inserted] is the
## index of a piece put in, and [param removed] of one taken out, -1 for none.
## Only the chunks those pieces reach are built again, so painting stays quick
## on a big level; and while edits are batched ([method begin_edit]) only the
## pieces' numbering is brought up to date, once each, and the rest waits.
func _edited(slots: Array[Vector3i], inserted: int, removed: int) -> void:
	if library == null:
		return
	if not scenery and volume != null:
		if removed >= 0:
			volume.piece_removed(removed)
		if inserted >= 0:
			volume.piece_inserted(inserted)
	if _batching > 0:
		for slot in slots:
			_pending[slot] = true
		return
	_redraw_slots(slots)


## Builds again what the rules see and the chunks or regions the pieces in
## [param slots] reach, and draws them.
func _redraw_slots(slots: Array[Vector3i]) -> void:
	if scenery:
		if scenery_renderer == null:
			build()
		else:
			scenery_renderer.rebuild_slots(slots)
		built.emit()
		return
	rules = LevelRules.new(data, library)
	if volume == null or renderer == null:
		build()
		return
	var keys := {}
	for slot in slots:
		for key in VoxelVolume.keys_of(slot):
			keys[key] = true
	var list: Array[Vector3i] = []
	list.assign(keys.keys())
	volume.restamp(list)
	renderer.set_palette()
	renderer.refresh()
	built.emit()


## The kind of piece [param index] of [member data].
func kind_of(index: int) -> PieceKind:
	if data == null or library == null or index < 0 or index >= data.count():
		return null
	return library.find(data.kind_id(index))


## The middle of [param cell], in the world.
func cell_center(cell: Vector3i) -> Vector3:
	return to_global(Vector3(cell) + Vector3.ONE * 0.5)


## The cell [param world] is in.
func cell_at(world: Vector3) -> Vector3i:
	return Vector3i(to_local(world).floor())


## Where the box of piece [param index] stands in the world, as its model is
## drawn there: its middle, turned as the piece is. Its voxels, counted from the
## box's least corner, are a sixteenth of a cell each from there, less half a
## cell each way.
func frame_of(index: int) -> Transform3D:
	var turn := Basis(Vector3.UP, data.turn_at(index) * PI * 0.5)
	return global_transform * Transform3D(turn, LevelData.box_center(data.slot_at(index)))
