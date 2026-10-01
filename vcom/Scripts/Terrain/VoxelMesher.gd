## Builds what a voxel model looks like and what it collides as: every face of
## a voxel that opens on to the air, merged into as few rectangles as their
## colours allow.
##
## The voxels are an array laid out as a [VoxelShape]'s, with its rows to find
## the faces by, and what comes out is in the shape's own frame: a block's
## cell, or a loose model's mesh space. A face on the edge of the model is
## always kept, whatever is beside it, as the importer keeps it, so what is
## left of a model looks exactly like the model where nothing has worn it.
## Faces are wound clockwise seen from outside, Godot's front.
##
## It has to be quick, as every model a round or a blast wears is built again:
## the faces are found a row of voxels at a time, from the rows' bits, so the
## work goes with how much of the model shows, not with how big it is.
class_name VoxelMesher
extends RefCounted

## A rectangle of faces, as [method _rectangles] packs them: the axis it faces
## along, which way (1 or -1), the slice of the model it lies on, where it
## starts across the slice and how far it reaches, and its colour.
const QUAD_AXIS := 0
const QUAD_SIDE := 1
const QUAD_SLICE := 2
const QUAD_A := 3
const QUAD_B := 4
const QUAD_WIDTH := 5
const QUAD_HEIGHT := 6
const QUAD_COLOR := 7
const QUAD_FIELDS := 8
## The order to take a rectangle's corners in for its two triangles, clockwise
## seen from the side it faces, for a face looking up its axis and down it.
## Along the first axis then the second turns anticlockwise seen from the far
## end of the axis it faces along, the three axes being in turn.
const WINDING_UP: Array[int] = [0, 3, 2, 0, 2, 1]
const WINDING_DOWN: Array[int] = [0, 1, 2, 0, 2, 3]

## Which bit of a row each single bit is.
static var BIT := _bit_table()


## The arrays of a mesh surface showing [param voxels], laid out as
## [param shape]'s, whose rows are [param rows], each face the colour the
## shape gives its voxel. Null when no face shows.
static func surface(shape: VoxelShape, voxels: PackedByteArray, rows: PackedInt64Array) -> Variant:
	var quads := _rectangles(shape, voxels, rows, true)
	var quad_count := quads.size() / QUAD_FIELDS
	if quad_count == 0:
		return null
	var vertices := _corners(shape, quads)
	var normals := PackedVector3Array()
	var tints := PackedColorArray()
	var indices := PackedInt32Array()
	normals.resize(quad_count * 4)
	tints.resize(quad_count * 4)
	indices.resize(quad_count * 6)
	for quad in quad_count:
		var at := quad * QUAD_FIELDS
		var side := quads[at + QUAD_SIDE]
		var normal := Vector3.ZERO
		normal[quads[at + QUAD_AXIS]] = side
		var color := shape.colors[quads[at + QUAD_COLOR]]
		var first := quad * 4
		for corner in 4:
			normals[first + corner] = normal
			tints[first + corner] = color
		var order := WINDING_UP if side > 0 else WINDING_DOWN
		for index in 6:
			indices[quad * 6 + index] = first + order[index]
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_COLOR] = tints
	arrays[Mesh.ARRAY_INDEX] = indices
	return arrays


## The triangles of a surface [method surface] built, one after another, for a
## [ConcavePolygonShape3D] to collide as exactly what is drawn.
static func triangles(arrays: Array) -> PackedVector3Array:
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
	var corners := PackedVector3Array()
	corners.resize(indices.size())
	for index in indices.size():
		corners[index] = vertices[indices[index]]
	return corners


## A mesh showing [param voxels], laid out as [param shape]'s, in its colours,
## drawn as its imported mesh is. Null when no face shows.
static func mesh(shape: VoxelShape, voxels: PackedByteArray) -> ArrayMesh:
	var arrays: Variant = surface(shape, voxels, shape.rows_of(voxels))
	if arrays == null:
		return null
	var built := ArrayMesh.new()
	built.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	built.surface_set_material(0, shape.material)
	return built


## The triangles of every face of [param voxels], laid out as [param shape]'s,
## that opens on to the air, merged regardless of colour, for a
## [ConcavePolygonShape3D].
static func faces(shape: VoxelShape, voxels: PackedByteArray) -> PackedVector3Array:
	var quads := _rectangles(shape, voxels, shape.rows_of(voxels), false)
	var quad_count := quads.size() / QUAD_FIELDS
	var corners := _corners(shape, quads)
	var corners_in_order := PackedVector3Array()
	corners_in_order.resize(quad_count * 6)
	for quad in quad_count:
		var order := WINDING_UP if quads[quad * QUAD_FIELDS + QUAD_SIDE] > 0 else WINDING_DOWN
		for index in 6:
			corners_in_order[quad * 6 + index] = corners[quad * 4 + order[index]]
	return corners_in_order


## The four corners of every rectangle packed in [param quads], in
## [param shape]'s frame, one rectangle after another: its least corner, then on
## along its first axis, across both, and along its second.
static func _corners(shape: VoxelShape, quads: PackedInt32Array) -> PackedVector3Array:
	var quad_count := quads.size() / QUAD_FIELDS
	var corners := PackedVector3Array()
	corners.resize(quad_count * 4)
	var scale := VoxelShape.SCALE
	for quad in quad_count:
		var at := quad * QUAD_FIELDS
		var axis := quads[at + QUAD_AXIS]
		var u := (axis + 1) % 3
		var v := (axis + 2) % 3
		var plane := shape.corner[axis] + float(quads[at + QUAD_SLICE] + (1 if quads[at + QUAD_SIDE] > 0 else 0)) * scale
		var a0 := shape.corner[u] + float(quads[at + QUAD_A]) * scale
		var b0 := shape.corner[v] + float(quads[at + QUAD_B]) * scale
		var a1 := a0 + float(quads[at + QUAD_WIDTH]) * scale
		var b1 := b0 + float(quads[at + QUAD_HEIGHT]) * scale
		var first := quad * 4
		if axis == 0:
			corners[first] = Vector3(plane, a0, b0)
			corners[first + 1] = Vector3(plane, a1, b0)
			corners[first + 2] = Vector3(plane, a1, b1)
			corners[first + 3] = Vector3(plane, a0, b1)
		elif axis == 1:
			corners[first] = Vector3(b0, plane, a0)
			corners[first + 1] = Vector3(b0, plane, a1)
			corners[first + 2] = Vector3(b1, plane, a1)
			corners[first + 3] = Vector3(b1, plane, a0)
		else:
			corners[first] = Vector3(a0, b0, plane)
			corners[first + 1] = Vector3(a1, b0, plane)
			corners[first + 2] = Vector3(a1, b1, plane)
			corners[first + 3] = Vector3(a0, b1, plane)
	return corners


## Every face of [param voxels], laid out as [param shape]'s, that opens on to
## the air, merged into rectangles, each packed as [constant QUAD_FIELDS]
## numbers. Faces merge only with faces of the same colour if
## [param by_colour], else with any.
##
## Each of the six ways a face can look is done in turn. A row of
## [param rows] - the voxels along x at one y and z - shows its faces that way
## in one sum of bits: along x, the voxels whose next voxel along the row is
## empty; along y or z, the voxels whose neighbouring row is empty there. Each
## such face goes into its slice of the model, a rectangle across the slice's
## two other axes, at its place there, and each slice with any is merged.
@warning_ignore("integer_division")
static func _rectangles(shape: VoxelShape, voxels: PackedByteArray, rows: PackedInt64Array, by_colour: bool) -> PackedInt32Array:
	var size := shape.size
	var quads := PackedInt32Array()
	var masks := PackedInt32Array()
	# For each line across each slice, whether a face has gone into it.
	var lines := PackedByteArray()
	for axis in 3:
		var u := (axis + 1) % 3
		var v := (axis + 2) % 3
		var slices := size[axis]
		var width := size[u]
		var height := size[v]
		var area := width * height
		# Where a face of voxel (x, y, z) goes: its slice along the axis, then
		# along the next axis one at a time, and the one after a line at a time.
		var place := Vector3i.ZERO
		place[axis] = area
		place[u] = 1
		place[v] = width
		var place_x := place.x
		var size_y := size.y
		var size_z := size.z
		var origin := shape.origin
		var stride_y := shape.stride_y
		var stride_z := shape.stride_z
		masks.resize(slices * area)
		lines.resize(slices * height)
		var used := PackedByteArray()
		used.resize(slices)
		for side: int in [1, -1]:
			used.fill(0)
			for z in size_z:
				for y in size_y:
					var row := rows[y + z * size_y]
					if row == 0:
						continue
					var shown := _shown(rows, row, y, z, axis, side, size_y, size_z)
					var at := origin + y * stride_y + z * stride_z
					var row_place := y * place.y + z * place.z
					while shown != 0:
						var low := shown & -shown
						shown ^= low
						var x: int = BIT[low]
						var square := row_place + x * place_x
						masks[square] = voxels[at + x] if by_colour else 1
						var slice := square / area
						used[slice] = 1
						lines[slice * height + (square - slice * area) / width] = 1
			for slice in slices:
				if used[slice] != 0:
					_merge(masks, slice * area, lines, slice * height, width, height, axis, side, slice, quads)
	return quads


## The voxels of [param row], at [param y] and [param z], with a face looking
## along [param axis] toward [param side], as bits of the row: those whose
## neighbour that way is empty. [param rows] are all the rows of a model
## [param size_y] voxels along y and [param size_z] along z; a neighbour
## outside it is always empty.
static func _shown(rows: PackedInt64Array, row: int, y: int, z: int, axis: int, side: int, size_y: int, size_z: int) -> int:
	if axis == 0:
		return row & ~(row >> 1) if side > 0 else row & ~(row << 1)
	var ny := y
	var nz := z
	if axis == 1:
		ny += side
	else:
		nz += side
	if ny < 0 or nz < 0 or ny >= size_y or nz >= size_z:
		return row
	return row & ~rows[ny + nz * size_y]


## Merges the faces of one slice of the model - its rectangle of
## [param masks] from [param offset], [param width] across and [param height]
## lines down - into rectangles, greedily: along the first axis as far as the
## colour holds, then down as far as the whole run does. [param lines] from
## [param line_offset] says which lines hold any. Both are left empty.
static func _merge(
	masks: PackedInt32Array, offset: int, lines: PackedByteArray, line_offset: int, width: int, height: int,
	axis: int, side: int, slice: int, quads: PackedInt32Array
) -> void:
	for b in height:
		if lines[line_offset + b] == 0:
			continue
		lines[line_offset + b] = 0
		var line := offset + b * width
		var a := 0
		while a < width:
			var color := masks[line + a]
			if color == 0:
				a += 1
				continue
			var run := 1
			while a + run < width and masks[line + a + run] == color:
				run += 1
			var down := 1
			var grows := true
			while grows and b + down < height:
				var next := line + down * width + a
				for step in run:
					if masks[next + step] != color:
						grows = false
						break
				if grows:
					down += 1
			for y in down:
				var cleared := line + y * width + a
				for x in run:
					masks[cleared + x] = 0
			quads.append(axis)
			quads.append(side)
			quads.append(slice)
			quads.append(a)
			quads.append(b)
			quads.append(run)
			quads.append(down)
			quads.append(color)
			a += run


## Which bit each single bit of a row is, for every bit a row can have.
static func _bit_table() -> Dictionary:
	var table := {}
	for bit in VoxelShape.WIDEST + 1:
		table[1 << bit] = bit
	return table
