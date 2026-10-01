## Builds what a block's voxels look like and what they collide as: every face
## of a voxel that opens on to the air, merged into as few rectangles as their
## colours allow.
##
## The voxels are a [VoxelShape]'s array, with its rows ([method VoxelShape.rows_of])
## to find the faces by, and so is what comes out: a cell one across, centred on
## its middle, unturned. A face on the edge of the cell is always kept,
## whatever is in the next cell, as the importer keeps it, so what is left of a
## block looks exactly like the block where nothing has worn it. Faces are
## wound clockwise seen from outside, Godot's front.
##
## It has to be quick, as every block a round or a blast wears is built again
## at once: the faces are found a row of sixteen voxels at a time, from the
## rows' bits, so the work goes with how much of the block shows, not with how
## big it is.
class_name VoxelMesher
extends RefCounted

const SIZE := VoxelShape.SIZE
const AREA := SIZE * SIZE
## A rectangle of faces, as [method _rectangles] packs them: the axis it faces
## along, which way (1 or -1), the slice of the cell it lies on, where it
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
## Which bit of a row each single bit is.
const BIT := {
	1 << 0: 0, 1 << 1: 1, 1 << 2: 2, 1 << 3: 3, 1 << 4: 4, 1 << 5: 5, 1 << 6: 6, 1 << 7: 7,
	1 << 8: 8, 1 << 9: 9, 1 << 10: 10, 1 << 11: 11, 1 << 12: 12, 1 << 13: 13, 1 << 14: 14, 1 << 15: 15,
}
## Where a face of voxel (x, y, z) goes among the slices' squares, for faces
## looking along x, y and z: [code]x * X + y * Y + z * Z[/code]. A slice is
## [constant AREA] long, at the voxel's place along the axis, and across it the
## next axis in turn counts one and the one after [constant SIZE].
const PLACE_X: Array[int] = [AREA, SIZE, 1]
const PLACE_Y: Array[int] = [1, AREA, SIZE]
const PLACE_Z: Array[int] = [SIZE, 1, AREA]
## The order to take a rectangle's corners in for its two triangles, clockwise
## seen from the side it faces, for a face looking up its axis and down it.
## Along the first axis then the second turns anticlockwise seen from the far
## end of the axis it faces along, the three axes being in turn.
const WINDING_UP: Array[int] = [0, 3, 2, 0, 2, 1]
const WINDING_DOWN: Array[int] = [0, 1, 2, 0, 2, 3]


## The arrays of a mesh surface showing [param voxels], whose rows are
## [param rows], each face the colour [param colors] gives its voxel. Null when
## no face shows.
static func surface(voxels: PackedByteArray, rows: PackedInt32Array, colors: PackedColorArray) -> Variant:
	var quads := _rectangles(voxels, rows, true)
	var quad_count := quads.size() / QUAD_FIELDS
	if quad_count == 0:
		return null
	var vertices := _corners(quads)
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
		var color := colors[quads[at + QUAD_COLOR]]
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


## A mesh showing [param voxels] in [param shape]'s colours, drawn as its
## imported mesh is. Null when no face shows.
static func mesh(voxels: PackedByteArray, shape: VoxelShape) -> ArrayMesh:
	var arrays: Variant = surface(voxels, VoxelShape.rows_of(voxels), shape.colors)
	if arrays == null:
		return null
	var built := ArrayMesh.new()
	built.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	built.surface_set_material(0, shape.material)
	return built


## The triangles of every face of [param voxels] that opens on to the air,
## merged regardless of colour, for a [ConcavePolygonShape3D].
static func faces(voxels: PackedByteArray) -> PackedVector3Array:
	var quads := _rectangles(voxels, VoxelShape.rows_of(voxels), false)
	var quad_count := quads.size() / QUAD_FIELDS
	var corners := _corners(quads)
	var corners_in_order := PackedVector3Array()
	corners_in_order.resize(quad_count * 6)
	for quad in quad_count:
		var order := WINDING_UP if quads[quad * QUAD_FIELDS + QUAD_SIDE] > 0 else WINDING_DOWN
		for index in 6:
			corners_in_order[quad * 6 + index] = corners[quad * 4 + order[index]]
	return corners_in_order


## The four corners of every rectangle packed in [param quads], in the cell,
## one rectangle after another: its least corner, then on along its first
## axis, across both, and along its second.
static func _corners(quads: PackedInt32Array) -> PackedVector3Array:
	var quad_count := quads.size() / QUAD_FIELDS
	var corners := PackedVector3Array()
	corners.resize(quad_count * 4)
	for quad in quad_count:
		var at := quad * QUAD_FIELDS
		var axis := quads[at + QUAD_AXIS]
		var plane := float(quads[at + QUAD_SLICE] + (1 if quads[at + QUAD_SIDE] > 0 else 0)) / SIZE - 0.5
		var a0 := float(quads[at + QUAD_A]) / SIZE - 0.5
		var b0 := float(quads[at + QUAD_B]) / SIZE - 0.5
		var a1 := a0 + float(quads[at + QUAD_WIDTH]) / SIZE
		var b1 := b0 + float(quads[at + QUAD_HEIGHT]) / SIZE
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


## Every face of [param voxels] that opens on to the air, merged into
## rectangles, each packed as [constant QUAD_FIELDS] numbers. Faces merge only
## with faces of the same colour if [param by_colour], else with any.
##
## Each of the six ways a face can look is done in turn. A row of
## [param rows] - the sixteen voxels along x at one y and z - shows its faces
## that way in one sum of bits: along x, the voxels whose next voxel along the
## row is empty; along y or z, the voxels whose neighbouring row is empty there.
## Each such face goes into its slice of the cell, as a square across the
## slice's two other axes, and each slice with any is merged.
static func _rectangles(voxels: PackedByteArray, rows: PackedInt32Array, by_colour: bool) -> PackedInt32Array:
	var quads := PackedInt32Array()
	var masks := PackedInt32Array()
	masks.resize(SIZE * AREA)
	# For each slice, which of its lines across have a face in them.
	var lines := PackedInt32Array()
	lines.resize(SIZE)
	for axis in 3:
		var place_x := PLACE_X[axis]
		var place_y := PLACE_Y[axis]
		var place_z := PLACE_Z[axis]
		for side: int in [1, -1]:
			var slices := 0
			for z in SIZE:
				for y in SIZE:
					var row := rows[y + z * SIZE]
					if row == 0:
						continue
					var shown := _shown(rows, row, y, z, axis, side)
					var at := VoxelShape.ORIGIN + y * VoxelShape.STRIDE_Y + z * VoxelShape.STRIDE_Z
					var place := y * place_y + z * place_z
					while shown != 0:
						var low := shown & -shown
						shown ^= low
						var x: int = BIT[low]
						# The voxel's face goes in its slice along the axis it
						# faces, at its place across the slice.
						var square := place + x * place_x
						masks[square] = voxels[at + x] if by_colour else 1
						var slice := square / AREA
						slices |= 1 << slice
						lines[slice] |= 1 << ((square % AREA) / SIZE)
			for slice in SIZE:
				if slices & (1 << slice):
					_merge(masks, slice * AREA, lines[slice], axis, side, slice, quads)
					lines[slice] = 0
	return quads


## The voxels of [param row], at [param y] and [param z], with a face looking
## along [param axis] toward [param side], as bits of the row: those whose
## neighbour that way is empty. [param rows] are all the rows; a neighbour
## outside the cell is always empty.
static func _shown(rows: PackedInt32Array, row: int, y: int, z: int, axis: int, side: int) -> int:
	if axis == 0:
		return row & ~(row >> 1) if side > 0 else row & ~(row << 1)
	var ny := y
	var nz := z
	if axis == 1:
		ny += side
	else:
		nz += side
	if ny < 0 or nz < 0 or ny >= SIZE or nz >= SIZE:
		return row
	return row & ~rows[ny + nz * SIZE]


## Merges the faces of one slice of the cell, its square of
## [member masks] from [param offset], into rectangles, greedily: along the
## first axis as far as the colour holds, then along the second as far as the
## whole run does. [param lines] says which lines across it hold any. The
## square is left empty.
static func _merge(masks: PackedInt32Array, offset: int, lines: int, axis: int, side: int, slice: int, quads: PackedInt32Array) -> void:
	for b in SIZE:
		if not lines & (1 << b):
			continue
		var line := offset + b * SIZE
		var a := 0
		while a < SIZE:
			var color := masks[line + a]
			if color == 0:
				a += 1
				continue
			var width := 1
			while a + width < SIZE and masks[line + a + width] == color:
				width += 1
			var height := 1
			var grows := true
			while grows and b + height < SIZE:
				var next := line + height * SIZE + a
				for step in width:
					if masks[next + step] != color:
						grows = false
						break
				if grows:
					height += 1
			for y in height:
				var row := line + y * SIZE + a
				for x in width:
					masks[row + x] = 0
			quads.append(axis)
			quads.append(side)
			quads.append(slice)
			quads.append(a)
			quads.append(b)
			quads.append(width)
			quads.append(height)
			quads.append(color)
			a += width
