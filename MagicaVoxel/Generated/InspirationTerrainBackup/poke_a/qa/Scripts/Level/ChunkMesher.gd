@tool
## Builds what one chunk of a [VoxelVolume] looks like: every face of a voxel
## that opens on to the air, merged into as few rectangles as its shape allows,
## whatever the colours, since the colours are drawn from a texture voxel by
## voxel ([LevelRenderer], Voxels.gdshader). A face between two voxels is
## never drawn, nor one against the next chunk's voxels, which are read too, so
## nothing hidden is drawn anywhere: not inside a block, not between two
## blocks, not between two chunks. Nor is the underside of the floor, which
## nothing ever sees.
##
## It works from the chunk's rows of bits ([member VoxelVolume.Chunk.rows_x],
## [member VoxelVolume.Chunk.rows_z]): a face looking along y or z is a bit of
## a row along x whose neighbour row up or across lacks it, and one looking
## along x a bit of a row along z whose neighbour row along x lacks it, so the
## faces of a whole row are found in one sum of bits. Each slice's faces are
## then merged greedily, a row at a time: a run of bits, grown down as far as
## every row below has the same run. A rectangle never crosses into the next
## chunk, as each chunk is drawn from its own layer of colours.
##
## It serves any cube of voxels laid out so, [code]n[/code] a side: a chunk, a
## piece's own box ([VoxelVolume.Stamp]) for the scenery, which is drawn a kind
## at a time, or the box of any other voxel model ([VoxelModel]): a figure, a
## prop, a crate's board.
class_name ChunkMesher
extends RefCounted

## A rectangle as [method rectangles] packs it: the axis it faces along (0 x,
## 1 y, 2 z), which way (1 or -1), the slice it lies on, where it starts along
## the bits of its rows and down its rows, and how far it reaches each way.
const AXIS := 0
const SIDE := 1
const SLICE := 2
const ALONG := 3
const DOWN := 4
const WIDTH := 5
const HEIGHT := 6
const FIELDS := 7

## Which bit a single bit is, by the bit's value modulo 67, which is different
## for every bit a row of 64 can have: [code]BIT[bit % 67][/code]. For
## anything that walks the bits of a row of voxels.
static var BIT := _bit_table()
## Every rectangle's two triangles, as a list of corners: rectangle q is
## corners 4q to 4q + 3, taken in an order that winds them clockwise seen from
## outside ([method arrays]), so one list serves every mesh.
static var _indices := PackedInt32Array()


## The neighbours of a chunk, for [method rectangles]: the rows of the chunk
## on each side that the faces on that side are against, empty where there is
## none.
class Near:
	var east := PackedInt64Array()
	var west := PackedInt64Array()
	var up := PackedInt64Array()
	var down := PackedInt64Array()
	var north := PackedInt64Array()
	var south := PackedInt64Array()


## Every face of the voxels of an [param n]-sided cube whose rows are
## [param rows_x] and [param rows_z], that opens on to the air, inside the cube
## or against the neighbours in [param near], merged into rectangles, packed
## [constant FIELDS] numbers each. Faces looking down on the slice
## [param floor_slice] are left out, the underside of the floor; all faces
## looking down are, with [param no_down], for scenery only ever seen from
## above.
static func rectangles(n: int, rows_x: PackedInt64Array, rows_z: PackedInt64Array, near: Near, floor_slice := -1, no_down := false) -> PackedInt32Array:
	var quads := PackedInt32Array()
	var rows := PackedInt64Array()
	rows.resize(n)
	var last := n - 1
	# Up and down: slice y, a row for each z, bits along x, the rows of a
	# slice side by side and the slices a chunk's area apart. Past the top or
	# bottom slice, the row against it is the chunk above's bottom slice or the
	# one below's top.
	_slices(n, rows_x, near.up, 0, n, 1, 1, 1, rows, quads, -1)
	if not no_down:
		_slices(n, rows_x, near.down, last * n, n, 1, 1, -1, rows, quads, floor_slice)
	# North and south: slice z, a row for each y, bits along x, the slices side
	# by side and the rows a chunk's width apart.
	_slices(n, rows_x, near.north, 0, 1, n, 2, 1, rows, quads, -1)
	_slices(n, rows_x, near.south, last, 1, n, 2, -1, rows, quads, -1)
	# East and west: slice x, a row for each y, bits along z, laid out alike.
	_slices(n, rows_z, near.east, 0, 1, n, 0, 1, rows, quads, -1)
	_slices(n, rows_z, near.west, last, 1, n, 0, -1, rows, quads, -1)
	return quads


## The faces of [param source]'s rows looking toward [param side] along
## [param axis], a slice at a time, merged into [param quads]. Row
## [code]r[/code] of slice [code]s[/code] is at
## [code]s * slice_stride + r * row_stride[/code], and the row a face is
## against is the same row of the next slice that way, or, past the last
## slice, the row of [param beyond] at
## [code]beyond_start + r * row_stride[/code]: none if [param beyond] is
## empty, so every face there shows. Faces on the slice [param skip] are left
## out.
static func _slices(
	n: int, source: PackedInt64Array, beyond: PackedInt64Array, beyond_start: int,
	slice_stride: int, row_stride: int, axis: int, side: int, rows: PackedInt64Array,
	quads: PackedInt32Array, skip: int
) -> void:
	var has_beyond := not beyond.is_empty()
	var last := n - 1
	var edge := last if side > 0 else 0
	for slice in n:
		if slice == skip:
			continue
		var start := slice * slice_stride
		var any := 0
		if slice != edge:
			var against := start + side * slice_stride
			for r in n:
				var shown := source[start + r * row_stride] & ~source[against + r * row_stride]
				rows[r] = shown
				any |= shown
		elif has_beyond:
			for r in n:
				var shown := source[start + r * row_stride] & ~beyond[beyond_start + r * row_stride]
				rows[r] = shown
				any |= shown
		else:
			for r in n:
				var shown := source[start + r * row_stride]
				rows[r] = shown
				any |= shown
		if any != 0:
			_merge(rows, n, axis, side, slice, quads)


## The arrays of a mesh surface showing [param quads], rectangles of a cube
## whose least voxel is [param origin], each voxel [param scale] across, and
## voxel (0, 0, 0) at [param offset]: where each corner is, in the space the
## voxels are counted in; its normal; in CUSTOM0 its place in voxels within
## the cube, and [param layer], the cube's layer of colours, times 8 plus
## which way its face looks (0 +x, 1 -x, 2 +y, 3 -y, 4 +z, 5 -z); and in
## CUSTOM1 the rectangle's extent across its face, counted within the cube.
## The shader finds the voxel behind each pixel from those alone
## (Voxels.gdshader), so they hold however the corners are drawn: moved by a
## skeleton, a figure's are. No index array: [method index_array] gives one
## that serves every mesh.
static func arrays(quads: PackedInt32Array, origin: Vector3i, layer: int, scale: float, offset := Vector3.ZERO) -> Array:
	@warning_ignore("integer_division")
	var count := quads.size() / FIELDS
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var places := PackedFloat32Array()
	var extents := PackedFloat32Array()
	vertices.resize(count * 4)
	normals.resize(count * 4)
	places.resize(count * 16)
	extents.resize(count * 16)
	var base := Vector3(origin)
	for quad in count:
		var at := quad * FIELDS
		var axis := quads[at]
		var side := quads[at + 1]
		var plane := float(quads[at + 2] + (1 if side > 0 else 0))
		var a0 := float(quads[at + 3])
		var a1 := a0 + quads[at + 5]
		var b0 := float(quads[at + 4])
		var b1 := b0 + quads[at + 6]
		# Corners in order (least, along the face's first axis, across both,
		# along its second), its rows running along a different pair of axes
		# for each; and the extent across the face, by the shader's two axes
		# for it.
		var c0: Vector3
		var c1: Vector3
		var c2: Vector3
		var c3: Vector3
		var e0: float
		var e1: float
		var e2: float
		var e3: float
		var normal: Vector3
		if axis == 0:
			c0 = Vector3(plane, b0, a0)
			c1 = Vector3(plane, b1, a0)
			c2 = Vector3(plane, b1, a1)
			c3 = Vector3(plane, b0, a1)
			e0 = b0; e1 = a0; e2 = b1; e3 = a1
			normal = Vector3(side, 0, 0)
		elif axis == 1:
			c0 = Vector3(a0, plane, b0)
			c1 = Vector3(a0, plane, b1)
			c2 = Vector3(a1, plane, b1)
			c3 = Vector3(a1, plane, b0)
			e0 = a0; e1 = b0; e2 = a1; e3 = b1
			normal = Vector3(0, side, 0)
		else:
			c0 = Vector3(a0, b0, plane)
			c1 = Vector3(a1, b0, plane)
			c2 = Vector3(a1, b1, plane)
			c3 = Vector3(a0, b1, plane)
			e0 = a0; e1 = b0; e2 = a1; e3 = b1
			normal = Vector3(0, 0, side)
		# Clockwise seen from outside with the one index list (0, 1, 2 and 0,
		# 2, 3): looking up its axis, the second and fourth corners swap.
		if side > 0:
			var swap := c1
			c1 = c3
			c3 = swap
		var packed := float(layer * 8 + axis * 2 + (0 if side > 0 else 1))
		var v := quad * 4
		vertices[v] = (base + c0) * scale + offset
		vertices[v + 1] = (base + c1) * scale + offset
		vertices[v + 2] = (base + c2) * scale + offset
		vertices[v + 3] = (base + c3) * scale + offset
		normals[v] = normal
		normals[v + 1] = normal
		normals[v + 2] = normal
		normals[v + 3] = normal
		# Written out, four floats a corner, which is quicker than a loop.
		var f := v * 4
		places[f] = c0.x
		places[f + 1] = c0.y
		places[f + 2] = c0.z
		places[f + 3] = packed
		places[f + 4] = c1.x
		places[f + 5] = c1.y
		places[f + 6] = c1.z
		places[f + 7] = packed
		places[f + 8] = c2.x
		places[f + 9] = c2.y
		places[f + 10] = c2.z
		places[f + 11] = packed
		places[f + 12] = c3.x
		places[f + 13] = c3.y
		places[f + 14] = c3.z
		places[f + 15] = packed
		extents[f] = e0
		extents[f + 1] = e1
		extents[f + 2] = e2
		extents[f + 3] = e3
		extents[f + 4] = e0
		extents[f + 5] = e1
		extents[f + 6] = e2
		extents[f + 7] = e3
		extents[f + 8] = e0
		extents[f + 9] = e1
		extents[f + 10] = e2
		extents[f + 11] = e3
		extents[f + 12] = e0
		extents[f + 13] = e1
		extents[f + 14] = e2
		extents[f + 15] = e3
	var made := []
	made.resize(Mesh.ARRAY_MAX)
	made[Mesh.ARRAY_VERTEX] = vertices
	made[Mesh.ARRAY_NORMAL] = normals
	made[Mesh.ARRAY_CUSTOM0] = places
	made[Mesh.ARRAY_CUSTOM1] = extents
	return made


## The index array for a mesh of [param quads] rectangles laid out as
## [method arrays] lays them out.
static func index_array(quads: int) -> PackedInt32Array:
	if _indices.size() < quads * 6:
		@warning_ignore("integer_division")
		var start := _indices.size() / 6
		var grown := maxi(quads, start * 2)
		_indices.resize(grown * 6)
		for quad in range(start, grown):
			var corner := quad * 4
			var at := quad * 6
			_indices[at] = corner
			_indices[at + 1] = corner + 1
			_indices[at + 2] = corner + 2
			_indices[at + 3] = corner
			_indices[at + 4] = corner + 2
			_indices[at + 5] = corner + 3
	return _indices.slice(0, quads * 6)


## The format flags every mesh of [method arrays] needs: its two custom
## arrays are four floats a corner.
static func format() -> int:
	return (Mesh.ARRAY_CUSTOM_RGBA_FLOAT << Mesh.ARRAY_FORMAT_CUSTOM0_SHIFT) | (Mesh.ARRAY_CUSTOM_RGBA_FLOAT << Mesh.ARRAY_FORMAT_CUSTOM1_SHIFT)


## Merges [param rows], [param n] rows of bits on one slice, into rectangles,
## greedily, and packs each into [param quads]: a run of bits along a row,
## then down every row below that has the whole run. The rows are left empty.
static func _merge(rows: PackedInt64Array, n: int, axis: int, side: int, slice: int, quads: PackedInt32Array) -> void:
	for b in n:
		var row := rows[b]
		while row != 0:
			var low := row & -row
			var a: int = BIT[low % 67]
			var rest := ~(row >> a)
			var width: int = BIT[(rest & -rest) % 67]
			var run := ((1 << width) - 1) << a
			var down := 1
			while b + down < n and rows[b + down] & run == run:
				rows[b + down] &= ~run
				down += 1
			row &= ~run
			quads.append(axis)
			quads.append(side)
			quads.append(slice)
			quads.append(a)
			quads.append(b)
			quads.append(width)
			quads.append(down)
		rows[b] = 0


static func _bit_table() -> PackedByteArray:
	var table := PackedByteArray()
	table.resize(67)
	for bit in 63:
		table[(1 << bit) % 67] = bit
	return table
