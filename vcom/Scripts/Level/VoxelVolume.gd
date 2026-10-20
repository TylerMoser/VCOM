@tool
## Every voxel of a level, as one grid: what the pieces of a [LevelData] add
## up to once each has been stamped into it, a later piece winning voxel by
## voxel where two overlap. It is what the level is drawn from
## ([LevelRenderer]), what rounds are traced through and blasts and bites wear
## ([VoxelTerrain]), and what blood recolours.
##
## Voxels are a sixteenth of a cell, counted from the least corner of cell
## (0, 0, 0), and kept in chunks of [constant SIZE] a side, [constant SIZE]
## being a power of two so a voxel's chunk is a shift away. A chunk holds, for
## each voxel, the place of its colour in the level's [member palette] (0 for
## none) and which piece it belongs to; and the same voxels as rows of bits,
## along x for each y and z and along z for each x and y, which is what the
## mesher works from ([ChunkMesher]). Chunks are made only where a piece puts
## voxels.
##
## The colours are laid out as an image a chunk wide and a chunk squared tall,
## exactly as [LevelRenderer] hands them to the GPU, a layer a chunk, so that
## recolouring a voxel - blood - is a write here and an upload of one layer,
## and never rebuilds a mesh. A face is drawn the colour of the voxel behind
## it, wherever its voxels are, so wearing voxels away needs no upload: the
## colours of what it lays bare are there already.
##
## Built fresh as the level loads, from pieces stamped as images
## ([method Image.blit_rect_mask]) so the work is the engine's, not the
## script's. The rules never read it: they read whole pieces ([LevelRules]).
class_name VoxelVolume
extends RefCounted

## Voxels to a side of a chunk, as a power of two; and to a side of a cell.
const SIZE := 32
const SHIFT := 5
const MASK := SIZE - 1
const AREA := SIZE * SIZE
const LENGTH := AREA * SIZE
const BLOCK := 16
## The place in the palette that every voxel blood recolours takes, as in
## every voxel model's ([constant VoxelShape.BLOOD]).
const BLOOD := VoxelShape.BLOOD
## What a palette entry says beyond its colour, in its flags
## ([constant VoxelModel.FLAG_GRID]): the tile grid is drawn over it; it is
## wet, and glossier for it, as blood is.
const FLAG_GRID := VoxelModel.FLAG_GRID
const FLAG_WET := VoxelModel.FLAG_WET
## The bits of a whole row.
const FULL_ROW := (1 << SIZE) - 1
## The six ways out of a voxel.
const STEPS: Array[Vector3i] = [
	Vector3i(1, 0, 0), Vector3i(-1, 0, 0), Vector3i(0, 1, 0),
	Vector3i(0, -1, 0), Vector3i(0, 0, 1), Vector3i(0, 0, -1),
]


## One chunk of the volume: [constant SIZE] voxels a side from [member origin].
class Chunk:
	var key: Vector3i
	## Its least voxel, in the volume.
	var origin: Vector3i
	## For each voxel, at [code]x + z * SIZE + y * AREA[/code]: the place of its
	## colour in the palette, 0 for none; and its piece, as 1 more than the
	## place of the piece's index in [member owners], 0 for none.
	var colors := PackedByteArray()
	var slots := PackedByteArray()
	var owners := PackedInt32Array()
	## The voxels as rows of bits: along x, bit x, at [code]z + y * SIZE[/code];
	## along z, bit z, at [code]x + y * SIZE[/code].
	var rows_x := PackedInt64Array()
	var rows_z := PackedInt64Array()
	## Its layer of the level's colour texture ([LevelRenderer]).
	var layer := -1

	func _init(at: Vector3i) -> void:
		key = at
		origin = at * SIZE
		colors.resize(LENGTH)
		slots.resize(LENGTH)
		rows_x.resize(AREA)
		rows_z.resize(AREA)

	## The slot of piece [param piece] here, added if it has none yet.
	func owner_slot(piece: int) -> int:
		var at := owners.find(piece)
		if at < 0:
			owners.append(piece)
			at = owners.size() - 1
		return at + 1

	## The piece the voxel at [param index] belongs to, -1 for none.
	func owner_at(index: int) -> int:
		var slot := slots[index]
		return owners[slot - 1] if slot != 0 else -1

	## Whether it has no voxel left at all.
	func is_empty() -> bool:
		for row in rows_x:
			if row != 0:
				return false
		return true


## One kind's voxels, turned one of four ways, made ready to stamp: as rows,
## along x at [code]z + y * 16[/code] and along z at [code]x + y * 16[/code];
## as an image of colours a voxel a pixel, [code]x[/code] across and
## [code]z + y * 16[/code] down, places in the level's palette, with a mask of
## which pixels are voxels; and how many voxels it has, in all and in each half
## of its box (x below 8, x from 8, z below 8, z from 8) for a piece on an edge
## to share between the two cells it stands across.
class Stamp:
	var rows_x := PackedInt64Array()
	var rows_z := PackedInt64Array()
	## Each voxel's place in the level's palette, laid out as [member colors]
	## is: x across, z and y down, a row of 16 for each.
	var places := PackedByteArray()
	var colors: Image
	var mask: Image
	var count := 0
	var halves := PackedInt32Array([0, 0, 0, 0])


## What it is the voxels of.
var data: LevelData
var library: PieceLibrary
## The kind of each of [member data]'s kinds, by its place there, and its
## voxels as its model draws them; null for a kind the library lacks or whose
## voxels cannot be read.
var kinds: Array[PieceKind] = []
var shapes: Array[VoxelShape] = []
## Every chunk, by key: a voxel's chunk is its place shifted down by
## [constant SHIFT].
var chunks := {}
## The level's colours, 256 places, 0 for none: every colour its pieces' models
## use, and blood's at [constant BLOOD]; and each place's flags.
var palette := PackedColorArray()
var flags := PackedByteArray()
## How many voxels each piece had once every piece was stamped, and how many it
## has left now.
var whole := PackedInt32Array()
var counts := PackedInt32Array()
## The lowest layer of voxels: the underside of the floor, which nothing ever
## sees.
var floor_y := 0
## The chunks whose voxels have changed since they were last drawn, and those
## whose colours have, as sets by key.
var dirty := {}
var dirty_colors := {}

## How many voxels each cell held as the level was built, by cell: never
## fewer than it holds, as pieces may overlap and wear only takes voxels away,
## so a cell counted empty truly is.
var _cell_counts := {}
## The stamps made so far, by kind and turn.
var _stamps := {}
## The kinds placed in each slot, as a bit for each kind's place in
## [member data]'s kinds, by slot, and whether each kind wears away: for
## [method lay_bare], made the first time it is needed and forgotten whenever
## the pieces change.
var _kinds_by_slot := {}
var _bares := PackedByteArray()
var _edge_pieces := false
## What [method lay_bare] and [method lay_bare_box] have queued: voxels taken
## away whose neighbours are to be looked at, those whose are not, and the
## slots of whole pieces taken away, whose boxes' outsides are.
var _bare_next := PackedInt32Array()
var _bare_gone := PackedInt32Array()
var _bare_boxes: Array[Vector3i] = []
## Each place in a kind's model palette's place in the level's, by kind and
## place; and each colour and flags' place, by both.
var _mapped := {}
var _places := {}
## The chunk looked up last, which is most often the next.
var _last_key := Vector3i.MAX
var _last_chunk: Chunk


## The volume of [param level], whose kinds come from [param pieces]: empty
## until [method build].
func _init(level: LevelData, pieces: PieceLibrary) -> void:
	data = level
	library = pieces
	palette.resize(256)
	flags.resize(256)
	palette[BLOOD] = VoxelShape.BLOOD_COLOR
	flags[BLOOD] = FLAG_WET
	_places[_place_key(VoxelShape.BLOOD_COLOR, FLAG_WET)] = BLOOD
	sync_kinds()


## Reads the voxels of every kind the level has come to use since this was
## made: a level edited in the editor can take a kind it did not have.
func sync_kinds() -> void:
	for at in range(kinds.size(), data.kinds.size()):
		var id := data.kinds[at]
		var kind := library.find(StringName(id))
		kinds.append(kind)
		var shape: VoxelShape = null
		if kind == null:
			push_error("VoxelVolume: no piece kind '%s' in the library." % id)
		elif kind.model == null:
			push_error("VoxelVolume: piece kind '%s' has no model." % id)
		else:
			shape = VoxelShape.read(kind.model, kind.model_transform)
		shapes.append(shape)


## Stamps every piece of the level in order, each one's voxels over those of
## the pieces before it, and every piece in [param only] if it is given, the
## rest left out. Returns how long it took, in microseconds.
func build(only := PackedInt32Array()) -> int:
	var start := Time.get_ticks_usec()
	_kinds_by_slot.clear()
	chunks.clear()
	_cell_counts.clear()
	_last_key = Vector3i.MAX
	var count := data.count()
	whole.resize(count)
	whole.fill(0)
	var images := {}
	var overlapped := {}
	var lowest := INF
	if only.is_empty():
		for index in count:
			_place(index, images, overlapped)
			lowest = minf(lowest, data.slot_at(index).y)
	else:
		for index in only:
			_place(index, images, overlapped)
			lowest = minf(lowest, data.slot_at(index).y)
	floor_y = int(lowest) * BLOCK if lowest < INF else 0
	for key: Vector3i in images:
		var chunk: Chunk = chunks[key]
		var made: Array = images[key]
		chunk.colors = (made[0] as Image).get_data()
		chunk.slots = (made[1] as Image).get_data()
	# Where pieces overlapped, a piece kept only the voxels no later one took.
	for key: Vector3i in overlapped:
		_recount(chunks[key])
	counts = whole.duplicate()
	dirty.clear()
	for key in chunks:
		dirty[key] = true
	dirty_colors.clear()
	return Time.get_ticks_usec() - start


## Builds the chunks keyed [param keys] afresh from the level's pieces, as the
## level editor changes them: every piece whose box reaches them stamped in
## again, in order, so what a later piece covered shows again once it is
## erased. Chunks left with no voxel go; those round them are drawn again, as
## their faces against these may show or hide now.
func restamp(keys: Array[Vector3i]) -> void:
	sync_kinds()
	var count := data.count()
	whole.resize(count)
	counts.resize(count)
	var limit := {}
	var images := {}
	for key in keys:
		limit[key] = true
		var chunk := Chunk.new(key)
		var old: Chunk = chunks.get(key)
		if old != null:
			chunk.layer = old.layer
		chunks[key] = chunk
		images[key] = [
			Image.create(SIZE, AREA, false, Image.FORMAT_R8),
			Image.create(SIZE, AREA, false, Image.FORMAT_R8),
		]
	_last_key = Vector3i.MAX
	var overlapped := {}
	var lowest := INF
	for index in count:
		var slot := data.slot_at(index)
		lowest = minf(lowest, slot.y)
		var origin := LevelData.voxel_origin(slot)
		for key in _chunks_round(origin, origin + Vector3i.ONE * (BLOCK - 1)):
			if limit.has(key):
				_place(index, images, overlapped, limit)
				break
	floor_y = int(lowest) * BLOCK if lowest < INF else 0
	for key in keys:
		var chunk: Chunk = chunks[key]
		var made: Array = images[key]
		chunk.colors = (made[0] as Image).get_data()
		chunk.slots = (made[1] as Image).get_data()
	for key: Vector3i in overlapped:
		_recount(chunks[key])
	for key in keys:
		var chunk: Chunk = chunks[key]
		if chunk.is_empty():
			chunks.erase(key)
		else:
			dirty_colors[key] = true
		dirty[key] = true
		for step in STEPS:
			dirty[key + step] = true
		for index in chunk.owners:
			counts[index] = whole[index]


## Notes that piece [param index] has been taken out of the level, every piece
## after it now one earlier: each chunk's pieces are numbered again to match.
## The chunks it was in are the caller's to build again ([method restamp]).
func piece_removed(index: int) -> void:
	_kinds_by_slot.clear()
	for chunk: Chunk in chunks.values():
		for place in chunk.owners.size():
			if chunk.owners[place] > index:
				chunk.owners[place] -= 1
			elif chunk.owners[place] == index:
				chunk.owners[place] = -1
	if index < whole.size():
		whole.remove_at(index)
	if index < counts.size():
		counts.remove_at(index)


## Notes that a piece has been put in the level at [param index], every piece
## from there on now one later. The chunks it is in are the caller's to build
## again ([method restamp]).
func piece_inserted(index: int) -> void:
	_kinds_by_slot.clear()
	for chunk: Chunk in chunks.values():
		for place in chunk.owners.size():
			if chunk.owners[place] >= index:
				chunk.owners[place] += 1
	whole.insert(index, 0)
	counts.insert(index, 0)


## The keys of the chunks the box of a piece in [param slot] reaches.
static func keys_of(slot: Vector3i) -> Array[Vector3i]:
	var origin := LevelData.voxel_origin(slot)
	return _chunks_round(origin, origin + Vector3i.ONE * (BLOCK - 1))


## The chunk holding [param voxel], or null if none does.
func chunk_of(voxel: Vector3i) -> Chunk:
	var key := Vector3i(voxel.x >> SHIFT, voxel.y >> SHIFT, voxel.z >> SHIFT)
	if key == _last_key:
		return _last_chunk
	_last_key = key
	_last_chunk = chunks.get(key)
	return _last_chunk


## Where [param voxel] is in its chunk's arrays.
static func index_of(voxel: Vector3i) -> int:
	return (voxel.x & MASK) + ((voxel.z & MASK) << SHIFT) + ((voxel.y & MASK) << (SHIFT * 2))


## The voxel at [param index] of the chunk keyed [param key].
static func voxel_at(key: Vector3i, index: int) -> Vector3i:
	return key * SIZE + Vector3i(index & MASK, index >> (SHIFT * 2), (index >> SHIFT) & MASK)


## The place of [param voxel]'s colour in the palette, 0 if there is no voxel.
func color_at(voxel: Vector3i) -> int:
	var chunk := chunk_of(voxel)
	return chunk.colors[index_of(voxel)] if chunk != null else 0


## Whether there is a voxel at [param voxel].
func is_solid(voxel: Vector3i) -> bool:
	var chunk := chunk_of(voxel)
	return chunk != null and chunk.colors[index_of(voxel)] != 0


## The piece [param voxel] belongs to, by its index in the level; -1 if none.
func owner_at(voxel: Vector3i) -> int:
	var chunk := chunk_of(voxel)
	return chunk.owner_at(index_of(voxel)) if chunk != null else -1


## Whether [param cell] may hold any voxel: false only if it surely holds none.
func cell_has_voxels(cell: Vector3i) -> bool:
	return _cell_counts.get(cell, 0) > 0


## The voxel a point at [param local], in the level's own space, falls in.
static func voxel_under(local: Vector3) -> Vector3i:
	return Vector3i((local * BLOCK).floor())


## The middle of [param voxel], in the level's own space.
static func center_of(voxel: Vector3i) -> Vector3:
	return (Vector3(voxel) + Vector3.ONE * 0.5) / BLOCK


## The colour [param voxel] is drawn in, for what it breaks off as: clear if it
## is not there.
func color_of(voxel: Vector3i) -> Color:
	var place := color_at(voxel)
	return palette[place] if place != 0 else Color(0, 0, 0, 0)


## Takes the voxel at [param voxel] away, and returns the place of its colour,
## 0 if there was none. Its piece keeps a voxel fewer, and its chunk is drawn
## again, as is the chunk beside it if it was on the chunk's face, whose face
## there may now show.
func remove(voxel: Vector3i) -> int:
	var chunk := chunk_of(voxel)
	if chunk == null:
		return 0
	var index := index_of(voxel)
	var place := chunk.colors[index]
	if place == 0:
		return 0
	var piece := chunk.owner_at(index)
	chunk.colors[index] = 0
	chunk.slots[index] = 0
	var x := voxel.x & MASK
	var y := voxel.y & MASK
	var z := voxel.z & MASK
	chunk.rows_x[z + (y << SHIFT)] &= ~(1 << x)
	chunk.rows_z[x + (y << SHIFT)] &= ~(1 << z)
	if piece >= 0:
		counts[piece] -= 1
	# A cell's count is left as it was: it need only never be too few.
	dirty[chunk.key] = true
	if x == 0:
		dirty[chunk.key + Vector3i.LEFT] = true
	elif x == MASK:
		dirty[chunk.key + Vector3i.RIGHT] = true
	if y == 0:
		dirty[chunk.key + Vector3i.DOWN] = true
	elif y == MASK:
		dirty[chunk.key + Vector3i.UP] = true
	if z == 0:
		dirty[chunk.key + Vector3i.FORWARD] = true
	elif z == MASK:
		dirty[chunk.key + Vector3i.BACK] = true
	return place


## Takes away every voxel of [param voxels] (three numbers each), as
## [method remove] does one, and puts in [param places] the place of each one's
## colour, 0 where there was none, and in [param owners] its piece, -1 for
## none. Quicker than one at a time: a blast takes thousands.
func remove_many(voxels: PackedInt32Array, places: PackedByteArray, owners: PackedInt32Array) -> void:
	var count := voxels.size() / 3
	places.resize(count)
	owners.resize(count)
	var last_key := Vector3i.MAX
	var chunk: Chunk = null
	var colors := PackedByteArray()
	var slots := PackedByteArray()
	var rows_x := PackedInt64Array()
	var rows_z := PackedInt64Array()
	var chunk_owners := PackedInt32Array()
	for at in count:
		var x := voxels[at * 3]
		var y := voxels[at * 3 + 1]
		var z := voxels[at * 3 + 2]
		var key := Vector3i(x >> SHIFT, y >> SHIFT, z >> SHIFT)
		if key != last_key:
			last_key = key
			chunk = chunks.get(key)
			if chunk != null:
				colors = chunk.colors
				slots = chunk.slots
				rows_x = chunk.rows_x
				rows_z = chunk.rows_z
				chunk_owners = chunk.owners
				dirty[key] = true
		places[at] = 0
		owners[at] = -1
		if chunk == null:
			continue
		var lx := x & MASK
		var ly := y & MASK
		var lz := z & MASK
		var index := lx + (lz << SHIFT) + (ly << (SHIFT * 2))
		var place := colors[index]
		if place == 0:
			continue
		var slot := slots[index]
		var piece := chunk_owners[slot - 1] if slot != 0 else -1
		colors[index] = 0
		slots[index] = 0
		rows_x[lz + (ly << SHIFT)] &= ~(1 << lx)
		rows_z[lx + (ly << SHIFT)] &= ~(1 << lz)
		if piece >= 0:
			counts[piece] -= 1
		places[at] = place
		owners[at] = piece
		if lx == 0:
			dirty[key + Vector3i.LEFT] = true
		elif lx == MASK:
			dirty[key + Vector3i.RIGHT] = true
		if ly == 0:
			dirty[key + Vector3i.DOWN] = true
		elif ly == MASK:
			dirty[key + Vector3i.UP] = true
		if lz == 0:
			dirty[key + Vector3i.FORWARD] = true
		elif lz == MASK:
			dirty[key + Vector3i.BACK] = true
	_last_key = Vector3i.MAX


## Recolours what taking away the voxels at [param removed] (three numbers
## each) has laid bare where it is the inside of the ground, not the skin of a
## block. A kind's model is coloured as a block standing alone - the grass's
## turf hangs down all four of its sides - so where two blocks of a kind meet,
## their skins are buried against each other, and a crater cutting across the
## join would show every block's outline. So a voxel of a kind that wears away
## (the ground, trees, fences, walls; never a crate, whose lid is a lid
## whatever stood on it), buried on every side until now, on the edge of its
## own piece's box with a piece of the same kind placed in the slot across that
## edge, takes the colour its own model gives the voxel just inside it. Nothing
## that could be seen before changes, and the rules never read a colour.
##
## Not done here but queued, and done all at once by [method flush_bare] as the
## level is next drawn ([method LevelRenderer.refresh]), before any chunk is
## meshed again: at once for a round's bite, the next frame for a blast, whose
## chunks are drawn over the frames after it anyway, so the blast's own frame,
## the dearest, does not pay for it.
func lay_bare(removed: PackedInt32Array) -> void:
	if not removed.is_empty():
		_bare_next.append_array(removed)


## As [method lay_bare], for a whole piece in [param slot] just taken away,
## every voxel of it [param removed]: only the voxels just outside its box can
## have been laid bare by it, so only those are looked at.
func lay_bare_box(slot: Vector3i, removed: PackedInt32Array) -> void:
	if not removed.is_empty():
		_bare_gone.append_array(removed)
		_bare_boxes.append(slot)


## Whether [method lay_bare] or [method lay_bare_box] has queued anything.
func has_bare() -> bool:
	return not _bare_next.is_empty() or not _bare_boxes.is_empty()


## Does what [method lay_bare] and [method lay_bare_box] have queued, as one:
## a voxel laid bare by two of them at once is judged by both. Returns how many
## voxels were recoloured.
func flush_bare() -> int:
	if not has_bare():
		return 0
	_ready_to_lay_bare()
	var gone := {}
	for list: PackedInt32Array in [_bare_next, _bare_gone]:
		for at in range(0, list.size(), 3):
			gone[Vector3i(list[at], list[at + 1], list[at + 2])] = true
	var changed := 0
	var edges := _edge_pieces
	# The chunk last looked in, its colours read straight from its array: most
	# voxels next to one taken away were taken away too.
	var last_key := Vector3i.MAX
	var colors := PackedByteArray()
	var here := false
	var removed := _bare_next
	for at in range(0, removed.size(), 3):
		var x := removed[at]
		var y := removed[at + 1]
		var z := removed[at + 2]
		for step in STEPS:
			var bx := x + step.x
			var by := y + step.y
			var bz := z + step.z
			# Only a voxel on the edge of a box can be laid bare so: a cell's
			# boundary, or with pieces on edges, the middle of one too.
			var mx := bx & (BLOCK - 1)
			var mz := bz & (BLOCK - 1)
			var my := by & (BLOCK - 1)
			if not (mx == 0 or mx == BLOCK - 1 or mz == 0 or mz == BLOCK - 1 or my == 0 or my == BLOCK - 1):
				if not edges or not (mx == 7 or mx == 8 or mz == 7 or mz == 8):
					continue
			var key := Vector3i(bx >> SHIFT, by >> SHIFT, bz >> SHIFT)
			if key != last_key:
				last_key = key
				var chunk: Chunk = chunks.get(key)
				here = chunk != null
				if here:
					colors = chunk.colors
			if not here:
				continue
			var place := colors[(bx & MASK) + ((bz & MASK) << SHIFT) + ((by & MASK) << (SHIFT * 2))]
			if place == 0 or place == BLOOD:
				continue
			changed += _lay_bare_one(Vector3i(bx, by, bz), gone)
	for slot in _bare_boxes:
		var origin := LevelData.voxel_origin(slot)
		for a in BLOCK:
			for b in BLOCK:
				changed += _lay_bare_one(origin + Vector3i(-1, a, b), gone)
				changed += _lay_bare_one(origin + Vector3i(BLOCK, a, b), gone)
				changed += _lay_bare_one(origin + Vector3i(a, -1, b), gone)
				changed += _lay_bare_one(origin + Vector3i(a, BLOCK, b), gone)
				changed += _lay_bare_one(origin + Vector3i(a, b, -1), gone)
				changed += _lay_bare_one(origin + Vector3i(a, b, BLOCK), gone)
	_bare_next = PackedInt32Array()
	_bare_gone = PackedInt32Array()
	_bare_boxes.clear()
	return changed


## Makes what [method lay_bare] reads, the first time it is needed: the kinds
## in each slot, and which kinds wear away.
func _ready_to_lay_bare() -> void:
	if _bares.size() != kinds.size():
		_bares.resize(kinds.size())
		for kind in kinds.size():
			_bares[kind] = 1 if kinds[kind] != null and kinds[kind].destruction is VoxelDestruction else 0
	if _kinds_by_slot.is_empty():
		_edge_pieces = false
		for piece in data.count():
			var slot := data.slot_at(piece)
			_kinds_by_slot[slot] = int(_kinds_by_slot.get(slot, 0)) | (1 << mini(data.kind_at(piece), 62))
			if not LevelData.is_centre(slot):
				_edge_pieces = true


## [method flush_bare] for one voxel, [param bare], next to some of those in
## [param gone], every voxel just taken away, as a set. Returns 1 if it was
## recoloured.
func _lay_bare_one(bare: Vector3i, gone: Dictionary) -> int:
	var chunk := chunk_of(bare)
	if chunk == null:
		return 0
	var index := index_of(bare)
	var place := chunk.colors[index]
	if place == 0 or place == BLOOD:
		return 0
	var owned := chunk.slots[index]
	if owned == 0:
		return 0
	var piece := chunk.owners[owned - 1]
	var kind := data.kind_at(piece)
	if kind >= _bares.size() or _bares[kind] == 0:
		return 0
	# On the edge of its box, with its own kind across that edge.
	var slot := data.slot_at(piece)
	var local := bare - LevelData.voxel_origin(slot)
	var kind_bit := 1 << mini(kind, 62)
	var inward := Vector3i.ZERO
	for axis in 3:
		var outward := 0
		if local[axis] == 0:
			outward = -1
		elif local[axis] == BLOCK - 1:
			outward = 1
		else:
			continue
		var beyond := slot
		beyond[axis] += outward if axis == 1 else outward * 2
		if int(_kinds_by_slot.get(beyond, 0)) & kind_bit != 0:
			inward[axis] = -outward
	if inward == Vector3i.ZERO:
		return 0
	var inner := local + inward
	var inside := _stamp(kind, data.turn_at(piece)).places[inner.x + inner.z * BLOCK + inner.y * BLOCK * BLOCK]
	if inside == 0 or inside == place:
		return 0
	# Buried on every side until now.
	for around in STEPS:
		var next := bare + around
		if not gone.has(next) and not is_solid(next):
			return 0
	chunk = chunk_of(bare)
	chunk.colors[index] = inside
	dirty_colors[chunk.key] = true
	return 1


## Gives [param voxel], which must be there, the colour at [param place] in the
## palette: blood's ([constant BLOOD]) as blood lands on it. Only its chunk's
## colours go to the GPU again; nothing is meshed again. Returns whether it
## changed.
func recolor(voxel: Vector3i, place: int) -> bool:
	var chunk := chunk_of(voxel)
	if chunk == null:
		return false
	var index := index_of(voxel)
	if chunk.colors[index] == 0 or chunk.colors[index] == place:
		return false
	chunk.colors[index] = place
	dirty_colors[chunk.key] = true
	return true


## The voxels piece [param piece] still has, as places in the volume.
func voxels_of(piece: int) -> PackedVector3Array:
	var found := PackedVector3Array()
	if piece < 0 or piece >= data.count() or counts[piece] <= 0:
		return found
	var origin := LevelData.voxel_origin(data.slot_at(piece))
	for key in _chunks_round(origin, origin + Vector3i.ONE * (BLOCK - 1)):
		var chunk: Chunk = chunks.get(key)
		if chunk == null:
			continue
		var owned := chunk.owners.find(piece) + 1
		if owned == 0:
			continue
		var least := (origin - chunk.origin).clamp(Vector3i.ZERO, Vector3i.ONE * MASK)
		var most := (origin + Vector3i.ONE * (BLOCK - 1) - chunk.origin).clamp(Vector3i.ZERO, Vector3i.ONE * MASK)
		for y in range(least.y, most.y + 1):
			for z in range(least.z, most.z + 1):
				var row := chunk.rows_x[z + (y << SHIFT)]
				if row == 0:
					continue
				var at := (z << SHIFT) + (y << (SHIFT * 2))
				for x in range(least.x, most.x + 1):
					if row & (1 << x) != 0 and chunk.slots[at + x] == owned:
						found.append(Vector3(chunk.origin + Vector3i(x, y, z)))
	return found


## The keys of every chunk the box of voxels from [param least] to
## [param most], both included, reaches into.
static func _chunks_round(least: Vector3i, most: Vector3i) -> Array[Vector3i]:
	var keys: Array[Vector3i] = []
	for x in range(least.x >> SHIFT, (most.x >> SHIFT) + 1):
		for y in range(least.y >> SHIFT, (most.y >> SHIFT) + 1):
			for z in range(least.z >> SHIFT, (most.z >> SHIFT) + 1):
				keys.append(Vector3i(x, y, z))
	return keys


## The keys of every chunk the box of voxels from [param least] to
## [param most] reaches into that there is.
func chunks_in(least: Vector3i, most: Vector3i) -> Array[Vector3i]:
	var keys: Array[Vector3i] = []
	for key in _chunks_round(least, most):
		if chunks.has(key):
			keys.append(key)
	return keys


## Stamps piece [param index] into the chunks its box reaches, made as needed,
## through [param images] (each chunk's colour and slot images, by key, kept
## until the build is done), and notes in [param overlapped] each chunk where it
## landed on voxels already there. Given [param limit], a set of keys, only
## into those.
func _place(index: int, images: Dictionary, overlapped: Dictionary, limit := {}) -> void:
	var kind := data.kind_at(index)
	if kind < 0 or kind >= shapes.size() or shapes[kind] == null:
		return
	var stamp := _stamp(kind, data.turn_at(index))
	if stamp.count == 0:
		return
	var slot := data.slot_at(index)
	var origin := LevelData.voxel_origin(slot)
	var slot_image := Image.create(BLOCK, BLOCK * BLOCK, false, Image.FORMAT_R8)
	for key in _chunks_round(origin, origin + Vector3i.ONE * (BLOCK - 1)):
		if not limit.is_empty() and not limit.has(key):
			continue
		var chunk: Chunk = chunks.get(key)
		if chunk == null:
			chunk = Chunk.new(key)
			chunks[key] = chunk
			images[key] = [
				Image.create(SIZE, AREA, false, Image.FORMAT_R8),
				Image.create(SIZE, AREA, false, Image.FORMAT_R8),
			]
		var local := origin - chunk.origin
		var owned := chunk.owner_slot(index)
		var x0 := maxi(0, -local.x)
		var x1 := mini(BLOCK, SIZE - local.x)
		var z0 := maxi(0, -local.z)
		var z1 := mini(BLOCK, SIZE - local.z)
		if x0 >= x1 or z0 >= z1:
			continue
		# Writing through these writes the chunk's and the stamp's own arrays
		# (a packed array is shared, not copied), without asking the objects for
		# them each time round.
		var into_x := chunk.rows_x
		var into_z := chunk.rows_z
		var from_x := stamp.rows_x
		var from_z := stamp.rows_z
		var clash := 0
		var shift_x := local.x
		var shift_z := local.z
		for y in BLOCK:
			var row_y := (local.y + y) << SHIFT
			var stamp_y := y * BLOCK
			var to := local.z + row_y
			if shift_x >= 0:
				for z in range(z0, z1):
					var bits := (from_x[z + stamp_y] << shift_x) & FULL_ROW
					clash |= into_x[to + z] & bits
					into_x[to + z] |= bits
			else:
				for z in range(z0, z1):
					var bits := from_x[z + stamp_y] >> -shift_x
					clash |= into_x[to + z] & bits
					into_x[to + z] |= bits
			to = local.x + row_y
			if shift_z >= 0:
				for x in range(x0, x1):
					into_z[to + x] |= (from_z[x + stamp_y] << shift_z) & FULL_ROW
			else:
				for x in range(x0, x1):
					into_z[to + x] |= from_z[x + stamp_y] >> -shift_z
		if clash != 0:
			overlapped[key] = true
		slot_image.fill(Color8(owned, 0, 0))
		var made: Array = images[key]
		for y in BLOCK:
			var source := Rect2i(x0, y * BLOCK + z0, x1 - x0, z1 - z0)
			var to := Vector2i(local.x + x0, local.z + z0 + ((local.y + y) << SHIFT))
			(made[0] as Image).blit_rect_mask(stamp.colors, stamp.mask, source, to)
			(made[1] as Image).blit_rect_mask(slot_image, stamp.mask, source, to)
	whole[index] = stamp.count
	var low := LevelData.cell_of(slot)
	if LevelData.is_centre(slot):
		_cell_counts[low] = _cell_counts.get(low, 0) + stamp.count
	else:
		var high := LevelData.other_cell(slot)
		var along := 0 if slot.x & 1 == 1 else 2
		_cell_counts[low] = _cell_counts.get(low, 0) + stamp.halves[along]
		_cell_counts[high] = _cell_counts.get(high, 0) + stamp.halves[along + 1]


## Counts afresh how many voxels each piece in [param chunk] has, for a chunk
## where pieces overlapped: the earlier piece lost what the later took.
func _recount(chunk: Chunk) -> void:
	var here := PackedInt32Array()
	here.resize(chunk.owners.size() + 1)
	for index in LENGTH:
		here[chunk.slots[index]] += 1
	for place in chunk.owners.size():
		var piece := chunk.owners[place]
		var stamp := _stamp(data.kind_at(piece), data.turn_at(piece))
		# What the piece would have had here, less what it kept.
		var meant := _stamp_count_in(piece, stamp, chunk)
		whole[piece] -= meant - here[place + 1]


## How many of [param stamp]'s voxels piece [param piece] would put in
## [param chunk] with nothing over it.
func _stamp_count_in(piece: int, stamp: Stamp, chunk: Chunk) -> int:
	var local := LevelData.voxel_origin(data.slot_at(piece)) - chunk.origin
	var total := 0
	for y in BLOCK:
		for z in BLOCK:
			if local.z + z < 0 or local.z + z >= SIZE:
				continue
			var bits := stamp.rows_x[z + y * BLOCK]
			bits = (bits << local.x) & FULL_ROW if local.x >= 0 else bits >> -local.x
			while bits != 0:
				bits &= bits - 1
				total += 1
	return total


## The stamp of kind [param kind] (its place in the level's kinds), turned
## [param turn] quarter turns, made the first time it is asked for.
func _stamp(kind: int, turn: int) -> Stamp:
	var key := kind * 4 + turn
	if _stamps.has(key):
		return _stamps[key]
	var stamp := Stamp.new()
	stamp.rows_x.resize(BLOCK * BLOCK)
	stamp.rows_z.resize(BLOCK * BLOCK)
	var colors := PackedByteArray()
	colors.resize(BLOCK * BLOCK * BLOCK)
	var alpha := PackedByteArray()
	alpha.resize(BLOCK * BLOCK * BLOCK * 2)
	var shape := shapes[kind]
	var grid := FLAG_GRID if kinds[kind] != null and kinds[kind].tile_grid else 0
	for y in BLOCK:
		for z in BLOCK:
			for x in BLOCK:
				var place := shape.voxels[shape.index_of(Vector3i(x, y, z))]
				if place == 0:
					continue
				var to := turned(Vector3i(x, y, z), turn)
				var at := to.x + to.z * BLOCK + to.y * BLOCK * BLOCK
				colors[at] = _map(kind, place, shape, grid)
				alpha[at * 2] = 255
				alpha[at * 2 + 1] = 255
				stamp.rows_x[to.z + to.y * BLOCK] |= 1 << to.x
				stamp.rows_z[to.x + to.y * BLOCK] |= 1 << to.z
				stamp.count += 1
				stamp.halves[0 if to.x < 8 else 1] += 1
				stamp.halves[2 if to.z < 8 else 3] += 1
	stamp.places = colors
	stamp.colors = Image.create_from_data(BLOCK, BLOCK * BLOCK, false, Image.FORMAT_R8, colors)
	stamp.mask = Image.create_from_data(BLOCK, BLOCK * BLOCK, false, Image.FORMAT_LA8, alpha)
	_stamps[key] = stamp
	return stamp


## [param at], a voxel of a piece's box counted from its least corner, turned
## [param turn] quarter turns about up, counterclockwise seen from above, about
## the middle of the box: as [code]Basis(Vector3.UP, turn * PI / 2)[/code] turns
## the piece's model.
static func turned(at: Vector3i, turn: int) -> Vector3i:
	var x := at.x
	var z := at.z
	for step in posmod(turn, 4):
		var was := x
		x = z
		z = BLOCK - 1 - was
	return Vector3i(x, at.y, z)


## The place in the level's palette of place [param place] of kind
## [param kind]'s model palette, given [param flags]: the same colour with the
## same flags shares a place across kinds. Past 254 colours, the nearest there
## is stands in, with an error.
func _map(kind: int, place: int, shape: VoxelShape, flag_bits: int) -> int:
	var key := kind * 256 + place
	if _mapped.has(key):
		return _mapped[key]
	var color := shape.colors[place]
	var color_key := _place_key(color, flag_bits)
	var mapped: int = _places.get(color_key, 0)
	if mapped == 0:
		mapped = _places.size()
		if mapped >= BLOOD:
			mapped = _nearest(color)
			push_error("VoxelVolume: more than %d colours in one level; %s drawn as the nearest." % [BLOOD - 1, color])
		else:
			palette[mapped] = color
			flags[mapped] = flag_bits
			_places[color_key] = mapped
	_mapped[key] = mapped
	return mapped


## The place in the palette whose colour is nearest [param color].
func _nearest(color: Color) -> int:
	var best := 1
	var best_distance := INF
	for place in range(1, BLOOD):
		var other := palette[place]
		var distance := Vector3(other.r - color.r, other.g - color.g, other.b - color.b).length_squared()
		if distance < best_distance:
			best_distance = distance
			best = place
	return best


static func _place_key(color: Color, flag_bits: int) -> String:
	return "%s/%d" % [color.to_html(), flag_bits]
