@tool
## What the level editor (addons/level_editor) puts down and takes up for one
## click, worked out apart from the editor itself, so probes can do exactly
## what a click does.
##
## A click is in a slot ([LevelData]): the middle of a cell, or the edge
## between two cells. What it places is a kind of piece ([PieceKind]) or a
## brush of several ([PieceBrush]), turned the editor's turn, repeated over a
## square of cells the brush size across. A piece placed on an edge running
## along z is turned a quarter more, so a model drawn running along x, as a
## fence is, always runs along its edge.
class_name LevelEditing
extends RefCounted


## Every piece one click places, as [code][kind id, slot, turn][/code], in the
## order placed: [param selection] (a [PieceKind] or a [PieceBrush]) put down
## in [param slot] turned [param turn] quarter turns, over a square of
## [param size] cells a side round it.
static func placements(selection: Resource, slot: Vector3i, turn: int, size: int) -> Array:
	var placed := []
	if selection == null:
		return placed
	for base in square(slot, size):
		var along := turn + (1 if base.x & 1 == 1 else 0)
		if selection is PieceKind:
			placed.append([(selection as PieceKind).id, base, posmod(along, 4)])
		elif selection is PieceBrush:
			var brush := selection as PieceBrush
			for index in brush.size():
				var offset := turned_offset(brush.offsets[index], along)
				placed.append([brush.kinds[index], base + offset, posmod(brush.turn_of(index) + along, 4)])
	return placed


## Every slot a click takes a piece out of: the slot [param slot] and those of
## a square of [param size] cells a side round it, and, for a brush, every slot
## its pieces would stand in.
static func erasures(selection: Resource, slot: Vector3i, turn: int, size: int) -> Array[Vector3i]:
	var slots: Array[Vector3i] = []
	if selection is PieceBrush:
		for placed: Array in placements(selection, slot, turn, size):
			if not placed[1] in slots:
				slots.append(placed[1])
		return slots
	slots.assign(square(slot, size))
	return slots


## The slots of a square of [param size] cells a side whose middle, or near
## middle, is [param slot]: the same kind of slot as it, a cell apart.
static func square(slot: Vector3i, size: int) -> Array[Vector3i]:
	var slots: Array[Vector3i] = []
	var low := -((maxi(size, 1) - 1) >> 1)
	for dx in range(low, low + maxi(size, 1)):
		for dz in range(low, low + maxi(size, 1)):
			slots.append(slot + Vector3i(dx * 2, 0, dz * 2))
	return slots


## [param offset], a slot offset (half cells across, cells up), turned
## [param turn] quarter turns about up, as a piece's model turns
## ([method VoxelVolume.turned]): x to -z, z to x.
static func turned_offset(offset: Vector3i, turn: int) -> Vector3i:
	var x := offset.x
	var z := offset.z
	for step in posmod(turn, 4):
		var was := x
		x = z
		z = -was
	return Vector3i(x, offset.y, z)


## The slot a point at [param at] on the floor, in the level's own space, falls
## in: the middle of the cell under it, or with [param on_edge] the edge of
## that cell nearest it. Given [param axis], 0 or 2, only edges across that
## axis are taken: a stroke begun on an edge running along z keeps to such
## edges, so dragging a fence along a row of cells past their corners never
## turns it across them.
static func slot_at(at: Vector3, on_edge: bool, axis := -1) -> Vector3i:
	var cell := Vector3i(floori(at.x), roundi(at.y), floori(at.z))
	if not on_edge:
		return LevelData.centre_slot(cell)
	var across := Vector2(at.x - cell.x, at.z - cell.z)
	var ways := []
	if axis != 2:
		ways.append([across.x, Vector2i(-1, 0)])
		ways.append([1.0 - across.x, Vector2i(1, 0)])
	if axis != 0:
		ways.append([across.y, Vector2i(0, -1)])
		ways.append([1.0 - across.y, Vector2i(0, 1)])
	var nearest: Array = ways[0]
	for way: Array in ways:
		if way[0] < nearest[0]:
			nearest = way
	return LevelData.edge_slot(cell, nearest[1])


## Which axis the edge in [param slot] stands across: 0 for one between two
## cells along x, 2 along z; -1 for the middle of a cell.
static func edge_axis(slot: Vector3i) -> int:
	if slot.x & 1 == 1:
		return 0
	if slot.z & 1 == 1:
		return 2
	return -1


## Applies [param edits] to [param level], each [code]["add", id, slot, turn][/code]
## or [code]["erase", slot][/code], and returns what was done, in order, as the
## level editor's undo and redo replay it ([method redo], [method undo]): each
## [code]["add" or "remove", index, id, slot, turn][/code]. A piece added over
## the same kind turned the same way, last in its slot, is left out: it would
## change nothing but the count, as painting over what is painted already does.
## Any other kind is laid over what is there, winning voxel by voxel.
static func apply(level: VoxelLevel, edits: Array) -> Array:
	var done := []
	level.begin_edit()
	for edit: Array in edits:
		if edit[0] == "add":
			var here := level.data.indices_at(edit[2])
			if not here.is_empty():
				var last := here[here.size() - 1]
				if level.data.kind_id(last) == StringName(edit[1]) and level.data.turn_at(last) == posmod(edit[3], 4):
					continue
			var index := level.place(edit[1], edit[2], edit[3])
			done.append(["add", index, edit[1], edit[2], edit[3]])
		elif edit[0] == "erase":
			var here := level.data.indices_at(edit[1])
			if here.is_empty():
				continue
			var index := here[here.size() - 1]
			var was := level.remove(index)
			done.append(["remove", index, was[0], was[1], was[2]])
	level.end_edit()
	return done


## Does again what [method apply] did, from what it returned.
static func redo(level: VoxelLevel, done: Array) -> void:
	level.begin_edit()
	for step: Array in done:
		if step[0] == "add":
			level.insert(step[1], step[2], step[3], step[4])
		else:
			level.remove(step[1])
	level.end_edit()


## Undoes what [method apply] did, from what it returned, last first.
static func undo(level: VoxelLevel, done: Array) -> void:
	level.begin_edit()
	for at in range(done.size() - 1, -1, -1):
		var step: Array = done[at]
		if step[0] == "add":
			level.remove(step[1])
		else:
			level.insert(step[1], step[2], step[3], step[4])
	level.end_edit()
