## Breaks the pieces of the level rounds strike and blasts reach, and whatever
## they were holding up.
##
## When the [CombatGrid] reports a strike, the struck piece ([PieceKind])
## breaks if it has a [Destruction]; when it reports a blast, so does every
## piece inside it, and the debris inside it is thrown about by the blast (see
## [method _on_terrain_blasted]). The piece leaves the rules at once
## ([LevelRules]), so sight, cover and paths change the moment it goes, and its
## voxels leave the level ([VoxelVolume]); its destruction plays out what is
## left of it under this node. Every breakable piece stacked on it leaves the
## rules with it, but falls whole, as a [FallingBlock], and breaks where it
## lands; a piece that cannot break is left where it is, and so is everything
## on it. A piece across an edge stands on the cells either side of it below,
## or on the piece across the same edge below it, and falls once all of those
## have gone. A unit left standing on nothing drops to the ground below,
## falling with the rubble of what it stood on and passing through it, and
## through whatever the pieces falling with it break into.
##
## A piece that wears away ([VoxelDestruction]) is the exception: a strike or
## a blast only breaks voxels off it, through this node's [VoxelTerrain], and
## it breaks as above only once it is worn past standing. What is left of it
## then crumbles, its voxels [VoxelDebris], and the edges of the hole it
## leaves are worn ragged ([method VoxelTerrain.roughen_hole]).
##
## The level gives itself collision, a chunk at a time ([LevelRenderer]), for
## debris to land on. Debris that no longer belongs anywhere is tidied away: a
## piece knocked off the edge of the map, once it has fallen well below it, and
## one wedged inside the level's voxels, where it cannot be seen and would
## jostle for ever.
##
## The pieces debris is broken into, each a body of its own, are found by
## asking the physics ([method pieces_in]), never by walking the scene: with a
## few thousand lying about, walking it took longer than the rest of a blast
## did together.
##
## Each piece that breaks is announced ([signal block_broken]), for whatever
## it leaves behind besides its pieces, such as a coin ([Coins]).
##
## The blood on a breaking piece goes where its voxels go, as it is the
## voxels' own colour: a piece that wears away colours the lumps it crumbles
## into, one that falls whole takes it down with it, drawn as a [VoxelModel],
## and a crate's is carried to the pieces it breaks into voxel by voxel
## ([method VoxelTerrain.carry_blood]), if they wear away. A new kind of
## [Destruction] has to be given its blood the same way, here.
##
## A unit's figure breaks apart here too, as the unit dies
## ([method break_figure]): into lumps of voxel debris, as a block crumbles,
## knocked the way the killing blow went, its gear dropping whole as loose
## models that wear away.
class_name TerrainDestruction
extends Node3D

## Emitted as a piece breaks, [param destruction] saying what kind it was.
## [param cell] is where it broke: where it stood (for one across an edge, the
## cell on its least side), or, for one that fell whole, the cell it landed in.
signal block_broken(cell: Vector3i, destruction: Destruction)

## Physics layers: the level, and the pieces broken off it.
const TERRAIN_LAYER := 1 << 0
const DEBRIS_LAYER := 1 << 2
## The layer every piece is on as well as the debris layer: debris that is a
## body with a node of its own, a broken block's pieces and the parts cut from
## them, as against the voxels' lumps ([VoxelDebris]). Nothing collides with
## it; it is for finding pieces by ([method pieces_in]).
const PIECE_LAYER := 1 << 4
## The group every piece is in, for looking each one over.
const PIECES := &"pieces"
## The most pieces one search finds: more than any blast's box holds.
const MOST_FOUND := 4096
## What debris lands on and bumps off: the level, other debris, and units.
const DEBRIS_MASK := TERRAIN_LAYER | DEBRIS_LAYER | Unit.BODY_LAYER
## How far below the bottom of the map, in cells, debris falls before it is
## taken away, and how often, in seconds, debris is looked over.
const FALL_LIMIT := 10.0
const TIDY_SECONDS := 1.0
## How a figure breaking apart ([method break_figure]) is knocked by the blow
## that killed it, in cells a second. Every lump sets off the way the blow
## went: [constant FIGURE_KNOCK] along a round's way or a blade's swing,
## [constant FIGURE_BLAST_KNOCK] away from a blast, whose push then throws it
## as it throws all debris; lifted by [constant FIGURE_LIFT] of that, and
## shared out by height, so the head is thrown hardest and the feet keep
## [constant FIGURE_FEET_SHARE] of it. A lump within
## [constant FIGURE_WOUND_REACH] cells of where a round or blade landed is
## driven on along it by up to [constant FIGURE_WOUND_PUSH] more. Every lump
## also bursts out from the figure's upright middle by
## [constant FIGURE_SPREAD], scatters by up to [constant FIGURE_SCATTER] and
## tumbles by up to [constant FIGURE_SPIN] radians a second, so the figure
## comes apart rather than toppling whole.
const FIGURE_KNOCK := 2.0
const FIGURE_BLAST_KNOCK := 1.0
const FIGURE_LIFT := 0.3
const FIGURE_FEET_SHARE := 0.15
const FIGURE_WOUND_PUSH := 2.0
const FIGURE_WOUND_REACH := 0.4
const FIGURE_SPREAD := 0.7
const FIGURE_SCATTER := 0.5
const FIGURE_SPIN := 8.0

@export_group("Nodes")
@export var grid_path: NodePath = ^"../CombatGrid"

## The voxels of the pieces that wear away, and the voxels broken off them.
var voxels: VoxelTerrain
var voxel_debris: VoxelDebris

var _grid: CombatGrid
var _level: VoxelLevel
## Seconds until debris is next looked over.
var _tidy_in := TIDY_SECONDS
## How the figures breaking apart scatter and tumble draws on this, so the
## global generator is left alone.
var _show := RandomNumberGenerator.new()


## One broken piece and everything it brings down: the debris left so far, by
## its physics bodies, and the units dropping through it, who pass through
## whatever more it leaves.
class Collapse:
	var rubble: Array[RID] = []
	var fallers: Array[Unit] = []

	## Adds [param left] to the rubble, for everyone dropping through it.
	func add(left: Array[RID]) -> void:
		rubble.append_array(left)
		for unit in fallers:
			if is_instance_valid(unit):
				unit.pass_through(left)


func _ready() -> void:
	_grid = get_node_or_null(grid_path) as CombatGrid
	if _grid == null or _grid.level == null or _grid.level.volume == null:
		push_error("TerrainDestruction: missing CombatGrid, or its level, so nothing will break.")
		return
	_level = _grid.level
	var prepared := {}
	for index in _level.data.kinds.size():
		var kind := _level.library.find(StringName(_level.data.kinds[index]))
		if kind != null and kind.destruction != null and not prepared.has(kind.destruction):
			prepared[kind.destruction] = true
			kind.destruction.prepare()
	voxel_debris = VoxelDebris.new()
	voxel_debris.focus = _looked_at
	add_child(voxel_debris)
	voxels = VoxelTerrain.new(_grid, _level, voxel_debris)
	add_child(voxels)
	_grid.voxels = voxels
	_grid.terrain_struck.connect(_on_terrain_struck)
	_grid.terrain_blasted.connect(_on_terrain_blasted)
	_grid.round_flown.connect(_on_round_flown)
	_show.randomize()
	# The squad is spawned after this readies ([PlayerSquad]).
	_watch_units.call_deferred()


func _physics_process(delta: float) -> void:
	if voxel_debris == null:
		return
	_wake_in_the_way()
	_tidy_in -= delta
	if _tidy_in > 0.0:
		return
	_tidy_in = TIDY_SECONDS
	_tidy_debris()


## Breaks every piece standing in [param cell] that breaks, brings down every
## breakable piece stacked on it, and drops anyone left standing on nothing.
## [param hit] is the round that broke it, or null. Returns whether anything
## broke. A piece that wears away breaks whole, however much is left of it.
func break_block(cell: Vector3i, hit: CombatGrid.RayHit = null) -> bool:
	if _level == null:
		return false
	var broke := false
	# A copy: breaking a piece takes it out of the rules' own list.
	var standing := _level.rules.pieces_in(cell).duplicate()
	for at in range(standing.size() - 1, -1, -1):
		if break_piece(standing[at], hit):
			broke = true
	return broke


## Breaks piece [param piece] of the level, if it breaks, as
## [method break_block] breaks a cell's. Returns whether it broke.
func break_piece(piece: int, hit: CombatGrid.RayHit = null) -> bool:
	var collapse := Collapse.new()
	var before := get_child_count()
	if not _break(piece, hit, collapse):
		return false
	collapse.add(_left_since(before))
	_drop_stranded_units(collapse)
	return true


## Breaks [param model], the figure of a unit that is dying, apart where it
## stands, as a block that wears away crumbles: every voxel of it, posed as it
## is now, becomes a lump of [VoxelDebris] its
## [member CharacterModel.crumbles_as] says how big, in the voxel's colour,
## blood's where blood has recoloured it ([method FigureVoxels.crumble]). The
## gear it carries drops whole ([method _drop_gear]). Then the figure hides
## ([method CharacterModel.break_apart]), to go with its unit.
##
## Everything is knocked the way the blow that killed it went: it came from
## [param from], a blast if [param blasted], landed on the body at [param at]
## (infinite if unknown) and, from a blade, swept along [param sweep]. Unknown
## (infinite), it falls backward. Only for show: nothing in the rules reads
## what a figure breaks into. Returns the lumps' bodies.
func break_figure(model: CharacterModel, from: Vector3, blasted := false, at := Vector3.INF, sweep := Vector3.ZERO) -> Array[RID]:
	var lumps: Array[RID] = []
	if model.dead:
		return lumps
	if _level != null:
		_level.ensure_collision(AABB(model.global_position - Vector3.ONE * 2.0, Vector3.ONE * 4.0))
	var knock := _figure_knock(model, from, blasted, at, sweep)
	var pieces: Array[VoxelDebris.Piece] = []
	var figure := model.voxels()
	if figure != null and voxel_debris != null and model.crumbles_as != null:
		pieces = figure.crumble(model.crumbles_as.crumble_size, _show)
		for piece in pieces:
			piece.velocity = knock.call(piece.transform.origin)
			piece.spin = _random_in_ball() * FIGURE_SPIN
		lumps = voxel_debris.add(pieces, model.crumbles_as)
	if voxels != null and model.gear_wears_as != null:
		_drop_gear(model, knock, pieces, lumps)
	model.break_apart()
	return lumps


## The box, in world space, around everything [param body] collides with. Not
## around its origin: a piece cut from a MagicaVoxel model has its origin at the
## model's, which may be well outside the piece.
static func debris_box(body: PhysicsBody3D) -> AABB:
	var box := AABB()
	var first := true
	for node in body.find_children("*", "CollisionShape3D", true, false):
		var collider := node as CollisionShape3D
		if collider.shape == null:
			continue
		var local: AABB
		if collider.shape is BoxShape3D:
			var size := (collider.shape as BoxShape3D).size
			local = AABB(-size * 0.5, size)
		else:
			local = collider.shape.get_debug_mesh().get_aabb()
		var shape_box := collider.global_transform * local
		box = shape_box if first else box.merge(shape_box)
		first = false
	return box


## Makes [param body] a piece: on [constant PIECE_LAYER], besides whatever it
## is on, and in [constant PIECES].
static func make_piece(body: PhysicsBody3D) -> void:
	body.collision_layer |= PIECE_LAYER
	body.add_to_group(PIECES)


## Every piece whose collision reaches into [param box], in the world, as the
## physics in [param space] has it: far cheaper than looking at every piece, as
## it only looks where the box is.
static func pieces_in(space: PhysicsDirectSpaceState3D, box: AABB) -> Array[RigidBody3D]:
	var shape := BoxShape3D.new()
	shape.size = box.size
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = Transform3D(Basis.IDENTITY, box.get_center())
	query.collision_mask = PIECE_LAYER
	query.collide_with_areas = false
	var found: Array[RigidBody3D] = []
	var seen := {}
	for met in space.intersect_shape(query, MOST_FOUND):
		var body := met.collider as RigidBody3D
		if body != null and not seen.has(body):
			seen[body] = true
			found.append(body)
	return found


## A round tears through the loose voxel models along its flight, and flies on.
func _on_round_flown(from: Vector3, to: Vector3, damage: int) -> void:
	voxels.tear(from, to, damage)


## A strike breaks the piece it struck, or, if the piece wears away, breaks
## voxels off it and whatever pieces they are in, and those only if that
## leaves them worn past standing.
func _on_terrain_struck(hit: CombatGrid.RayHit, damage: int) -> void:
	if hit.piece < 0:
		return
	if not voxels.wears_away(hit.piece):
		break_piece(hit.piece, hit)
		return
	var wear := voxels.chip(hit, damage)
	_wake_debris(wear)
	for piece in _top_down(wear.broken):
		break_piece(piece, hit)


## Blows a crater round [param origin] in every piece among [param cells], the
## cells a blast there reaches, that wears away, then breaks every breakable
## piece among them that does not - in a cell, or across an edge with a cell
## either side among them - and every one the crater has worn past standing,
## then throws the debris inside the blast about with a [Blast] of
## [param force]: what it has just broken, as its pieces are let go, and
## whatever was lying there already, the blast's own dead among it, who have
## just broken apart ([method break_figure]).
##
## The pieces break from the top down, so each one is blasted apart where it
## stands rather than first falling on the one below it, the way a piece does
## when something under it breaks; pieces stacked above the blast still fall.
func _on_terrain_blasted(origin: Vector3, cells: Array[Vector3i], damage: int, force: float) -> void:
	var wear := voxels.crater(origin, cells, damage)
	_wake_debris(wear)
	var breaking := wear.broken.duplicate()
	var rules := _level.rules
	var inside := {}
	for cell in cells:
		inside[cell] = true
		for piece in rules.pieces_in(cell):
			if not voxels.wears_away(piece):
				breaking.append(piece)
	for slot in rules.edge_slots():
		if inside.has(LevelData.cell_of(slot)) or inside.has(LevelData.other_cell(slot)):
			for piece in rules.pieces_across(slot):
				if not voxels.wears_away(piece):
					breaking.append(piece)
	for piece in _top_down(breaking):
		break_piece(piece)
	if force <= 0.0 or cells.is_empty():
		return
	# The pieces of what broke are held still until the next physics step
	# (see ScriptedDestruction), and set moving then, before this resumes. The
	# lumps of those the blast has just killed are held until then too, and
	# set off then as fast as the push leaves them ([method VoxelDebris.burst]).
	await get_tree().physics_frame
	Blast.burst(_debris_within(cells), origin, force)
	voxel_debris.burst(origin, _blast_box(cells), force)


## [param pieces], highest first, each once.
func _top_down(pieces: PackedInt32Array) -> PackedInt32Array:
	var seen := {}
	var ordered: Array[int] = []
	for piece in pieces:
		if not seen.has(piece):
			seen[piece] = true
			ordered.append(piece)
	var data := _level.data
	ordered.sort_custom(func(a: int, b: int) -> bool: return data.slot_at(a).y > data.slot_at(b).y)
	return PackedInt32Array(ordered)


## The box, in world space, that [param cells] fill.
func _blast_box(cells: Array[Vector3i]) -> AABB:
	var box := AABB(_grid.cell_center(cells[0]), Vector3.ZERO)
	for cell in cells:
		box = box.expand(_grid.cell_center(cell))
	return box.grow(0.5)


## Every piece lying inside [param cells], free to be thrown about: not held
## still. A block falling whole is no piece, and drops only straight down.
func _debris_within(cells: Array[Vector3i]) -> Array[RigidBody3D]:
	var box := _blast_box(cells)
	var pieces: Array[RigidBody3D] = []
	for body in pieces_in(get_world_3d().direct_space_state, box):
		if not body.freeze and box.has_point(debris_box(body).get_center()):
			pieces.append(body)
	return pieces


## Wakes the debris at rest round what [param wear] wore away, which may have
## been lying on the voxels it took: the physics would leave it resting on air.
## The voxels' own lumps are woken as each worn chunk is drawn again.
func _wake_debris(wear: VoxelTerrain.Wear) -> void:
	if wear.worn:
		_wake_pieces(wear.box.grow(VoxelDebris.LYING_ON))


## Wakes every piece at rest whose middle is inside [param box].
func _wake_pieces(box: AABB) -> void:
	for body in pieces_in(get_world_3d().direct_space_state, box):
		if body.sleeping and box.has_point(debris_box(body).get_center()):
			body.sleeping = false


## Gives every lump lying still without a body in the way of a unit on the move
## its body back, so the unit shoves it aside rather than walking through it.
func _wake_in_the_way() -> void:
	if not voxel_debris.has_still():
		return
	# The unit's cell, both its cells high, and a lump's height below its feet.
	var size := Vector3(1.0, CombatGrid.UNIT_HEIGHT + VoxelDebris.LYING_ON, 1.0)
	var below := Vector3(0.5, VoxelDebris.LYING_ON, 0.5)
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		var unit := node as Unit
		if unit != null and unit.is_moving():
			voxel_debris.wake(AABB(unit.global_position - below, size), true)


## The middle of the tile the camera is looking at: where the middle of its
## view first meets the ground. Failing that, where the camera is.
func _looked_at() -> Vector3:
	var camera := get_viewport().get_camera_3d()
	if camera == null:
		return _grid.map_bounds().get_center()
	var hit: Variant = _grid.cast(camera.global_position, -camera.global_basis.z)
	if hit == null:
		return camera.global_position
	return _grid.tile_position((hit as CombatGrid.RayHit).cell + Vector3i.UP)


## Breaks piece [param piece] where it stands, and lets the pieces stacked on
## it fall.
func _break(piece: int, hit: CombatGrid.RayHit, collapse: Collapse) -> bool:
	var rules := _level.rules
	if not rules.is_standing(piece):
		return false
	var destruction := voxels.destruction_of(piece)
	if destruction == null:
		return false
	var data := _level.data
	var slot := data.slot_at(piece)
	rules.remove(piece, slot)
	var taken := voxels.take_piece(piece)
	if destruction is VoxelDestruction:
		collapse.add(voxels.crumble(taken, voxels.voxel_frame(), destruction as VoxelDestruction, hit))
		collapse.add(voxels.roughen_hole(slot))
	else:
		var frame := _level.frame_of(piece)
		var kind := _level.kind_of(piece)
		var before := get_child_count()
		destruction.shatter(self, frame * kind.model_transform, hit)
		voxels.carry_blood(taken, data.kind_at(piece), slot, data.turn_at(piece), frame, _pieces_since(before))
	block_broken.emit(LevelData.cell_of(slot), destruction)
	var top := _drop_pieces_above(slot, collapse)
	# Whatever lay on it, or on the pieces falling with it, is woken to fall
	# too: the physics would leave it lying on air.
	var low := _level.to_global(LevelData.box_center(slot) - Vector3.ONE * 0.5)
	var column := AABB(low, Vector3(1.0, top - slot.y + 1, 1.0)).grow(VoxelDebris.LYING_ON)
	_wake_pieces(column)
	voxel_debris.wake(column)
	# The hole shows at once.
	_level.redraw_now()
	return true


## Lets each breakable piece stacked on the one that stood in [param slot], up
## to the first that cannot break, fall whole, to break where it lands, and
## the pieces across edges left with nothing under them. They leave the rules
## now, with the piece they stood on, so the rules never wait for them to come
## down. Returns the level just above the last one that fell.
func _drop_pieces_above(slot: Vector3i, collapse: Collapse) -> int:
	var rules := _level.rules
	var top := slot.y
	var waiting: Array[Vector3i] = _above(slot)
	while not waiting.is_empty():
		var above: Vector3i = waiting.pop_front()
		if not _unsupported(above):
			continue
		var standing := (rules.pieces_in(LevelData.cell_of(above)) if LevelData.is_centre(above) else rules.pieces_across(above)).duplicate()
		var fell := false
		for piece in standing:
			if voxels.destruction_of(piece) == null:
				continue
			rules.remove(piece, above)
			_drop_whole(piece, collapse)
			fell = true
		if fell:
			top = maxi(top, above.y)
			waiting.append_array(_above(above))
	return top + 1


## The slots resting on the one at [param slot]: for a cell's middle, the
## middle of the cell above and the four edges round it; for an edge, the edge
## above.
static func _above(slot: Vector3i) -> Array[Vector3i]:
	var up := slot + Vector3i.UP
	var found: Array[Vector3i] = [up]
	if LevelData.is_centre(slot):
		var cell := LevelData.cell_of(up)
		for way: Vector2i in LineOfSight.COVER_DIRECTIONS:
			found.append(LevelData.edge_slot(cell, way))
	return found


## Whether whatever stands in [param slot] has nothing under it any more: for
## a cell's middle, no solid piece in the cell below; for an edge, none in the
## cells below it on either side, and no piece across the edge below it.
func _unsupported(slot: Vector3i) -> bool:
	var rules := _level.rules
	if LevelData.is_centre(slot):
		return not rules.is_solid(LevelData.cell_of(slot) + Vector3i.DOWN)
	if rules.has_edge_slot(slot + Vector3i.DOWN):
		return false
	return not rules.is_solid(LevelData.cell_of(slot) + Vector3i.DOWN) and not rules.is_solid(LevelData.other_cell(slot) + Vector3i.DOWN)


## Takes piece [param piece] out of the level's voxels and lets it fall whole
## as a [FallingBlock] showing what is left of it, as heavy as its share of its
## destruction's mass, to break where it lands. Its voxels keep their colours,
## blood and all: it is drawn as a [VoxelModel] in the level's palette.
func _drop_whole(piece: int, collapse: Collapse) -> void:
	var destruction := voxels.destruction_of(piece)
	var whole := maxi(_level.volume.whole[piece], 1)
	var taken := voxels.take_piece(piece)
	if taken.size() == 0:
		return
	var slot := _level.data.slot_at(piece)
	var origin := LevelData.voxel_origin(slot)
	# Its voxels as a model of their own, in its box, unturned: they are turned
	# already, as the level holds them.
	var shape := VoxelShape.new(Vector3i.ONE * VoxelVolume.BLOCK, -Vector3.ONE * 0.5)
	shape.colors = _level.volume.palette
	var left := PackedByteArray()
	left.resize(shape.length)
	for index in taken.size():
		left[shape.index_of(taken.voxel(index) - origin)] = taken.places[index]
	var share := float(taken.size()) / whole
	var block := FallingBlock.new(VoxelModel.new(shape, left).show_on(),
		maxf(destruction.mass * share, ScriptedDestruction.MIN_MASS))
	add_child(block)
	var middle := _level.to_global(LevelData.box_center(slot))
	block.global_transform = Transform3D(_level.global_basis, middle)
	_level.ensure_collision(AABB(middle - Vector3(1.0, 8.0, 1.0), Vector3(2.0, 9.0, 2.0)))
	block.landed.connect(_on_landed.bind(piece, taken, collapse))


## Breaks piece [param piece], which fell whole leaving [param taken] of
## itself, where it landed: [param at] is where its box stood then, unturned,
## its pieces carrying on its fall, and lets anyone dropping through
## [param collapse] pass through them.
func _on_landed(at: Transform3D, motion: Destruction.Motion, piece: int, taken: VoxelTerrain.Taken, collapse: Collapse) -> void:
	var destruction := voxels.destruction_of(piece)
	var data := _level.data
	var slot := data.slot_at(piece)
	if destruction is VoxelDestruction:
		var origin := Vector3(LevelData.voxel_origin(slot)) + Vector3.ONE * (VoxelVolume.BLOCK * 0.5)
		var frame := at * Transform3D(Basis.from_scale(Vector3.ONE * VoxelTerrain.VOXEL), -origin * VoxelTerrain.VOXEL)
		collapse.add(voxels.crumble(taken, frame, destruction as VoxelDestruction, null, motion))
	else:
		var turned := at * Transform3D(Basis(Vector3.UP, data.turn_at(piece) * PI * 0.5), Vector3.ZERO)
		var before := get_child_count()
		destruction.shatter(self, turned * _level.kind_of(piece).model_transform, null, motion)
		collapse.add(_left_since(before))
		voxels.carry_blood(taken, data.kind_at(piece), slot, data.turn_at(piece), turned, _pieces_since(before))
	block_broken.emit(_level.cell_at(motion.center), destruction)


## The physics bodies of every piece of debris among, or under, the children
## added since there were [param before] of them: whatever a breaking block
## has just left. Blocks falling whole are not among them; they never meet a
## unit.
func _left_since(before: int) -> Array[RID]:
	var left: Array[RID] = []
	for index in range(before, get_child_count()):
		var child := get_child(index)
		if child is FallingBlock:
			continue
		if child is PhysicsBody3D:
			left.append((child as PhysicsBody3D).get_rid())
		for node in child.find_children("*", "PhysicsBody3D", true, false):
			left.append((node as PhysicsBody3D).get_rid())
	return left


## Every piece among, or under, the children added since there were
## [param before] of them, as [method _left_since] finds them, as nodes.
func _pieces_since(before: int) -> Array[RigidBody3D]:
	var pieces: Array[RigidBody3D] = []
	for index in range(before, get_child_count()):
		var child := get_child(index)
		if child is FallingBlock:
			continue
		if child is RigidBody3D:
			pieces.append(child as RigidBody3D)
		for node in child.find_children("*", "RigidBody3D", true, false):
			pieces.append(node as RigidBody3D)
	return pieces


## Drops every unit left standing on nothing to the ground below it, through
## the debris of [param collapse].
func _drop_stranded_units(collapse: Collapse) -> void:
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		_drop_if_stranded(node as Unit, collapse)


## Drops [param unit] to the ground below if it stands on nothing, through the
## debris of [param collapse]. A unit on the move is left to finish first,
## since it may be walking off onto solid ground.
func _drop_if_stranded(unit: Unit, collapse: Collapse) -> void:
	while is_instance_valid(unit) and unit.is_moving():
		await get_tree().process_frame
	if not is_instance_valid(unit) or unit.health <= 0:
		return
	var tile := _grid.tile_at(unit.global_position)
	if _grid.is_solid(tile + Vector3i.DOWN):
		return
	var landing: Variant = _grid.tile_under(tile)
	if landing != null:
		unit.drop_to(_grid.tile_position(landing), collapse.rubble)
		collapse.fallers.append(unit)


## Watches every unit on the map, to break its figure apart as it dies.
func _watch_units() -> void:
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		var unit := node as Unit
		if unit != null and not unit.died.is_connected(_on_unit_died):
			unit.died.connect(_on_unit_died.bind(unit))


## Breaks [param unit]'s figure apart as the unit dies, the way the hit that
## killed it went.
func _on_unit_died(unit: Unit) -> void:
	if unit.model != null:
		break_figure(unit.model, unit.hit_from, unit.hit_blasted, unit.hit_at, unit.hit_sweep)


## How fast each part of [param model], breaking apart, is knocked by the blow
## that killed it, as [method break_figure] was given it: a callable taking the
## part's middle, in the world, and giving the speed it sets off at (see
## [constant FIGURE_KNOCK]).
func _figure_knock(model: CharacterModel, from: Vector3, blasted: bool, at: Vector3, sweep: Vector3) -> Callable:
	var feet := model.global_position
	var tall := maxf(model.body_box().size.y, 0.5)
	var middle := feet + Vector3.UP * tall * 0.5
	var source := from if from.is_finite() else middle + model.global_basis.z
	var way := (at if at.is_finite() else middle) - source
	var level := Vector3(way.x, 0.0, way.z)
	if not sweep.is_zero_approx():
		# A blade sends it on along its swing, and a little on from the striker.
		level = Vector3(sweep.x, 0.0, sweep.z).normalized() + level.normalized() * 0.5
	var along := level.normalized() if level.length() > 0.01 else -model.global_basis.z
	var knock := (along + Vector3.UP * FIGURE_LIFT).normalized() * (FIGURE_BLAST_KNOCK if blasted else FIGURE_KNOCK)
	var push := Vector3.ZERO
	if at.is_finite() and not blasted:
		push = (sweep if not sweep.is_zero_approx() else way).normalized() * FIGURE_WOUND_PUSH
	return func(center: Vector3) -> Vector3:
		var height := clampf((center.y - feet.y) / tall, 0.0, 1.0)
		var speed := knock * lerpf(FIGURE_FEET_SHARE, 1.0, height) * _show.randf_range(0.75, 1.25)
		var out := Vector3(center.x - feet.x, 0.0, center.z - feet.z)
		if out.length() > 0.01:
			speed += out.normalized() * FIGURE_SPREAD
		speed += _random_in_ball() * FIGURE_SCATTER
		if not push.is_zero_approx():
			speed += push * (1.0 - clampf(center.distance_to(at) / FIGURE_WOUND_REACH, 0.0, 1.0))
		return speed


## Drops the gear [param model] carries as it breaks apart: each prop it shows
## whole, a rigid body of its own under this node that wears away as its
## [member CharacterModel.gear_wears_as] says, taken on the first time a round
## or a blast reaches it, as a crate's pieces are
## ([method VoxelTerrain.take_on_later]); the prop's [VoxelModel] goes with its
## mesh, blood and all. It sets off as [param knock] says. A prop passes
## through the rest of the gear and the figure's [param lumps] (made of
## [param pieces]) that it starts out overlapping: the hand round a grip, the
## back a sword lies across.
func _drop_gear(model: CharacterModel, knock: Callable, pieces: Array[VoxelDebris.Piece], lumps: Array[RID]) -> void:
	var wear := model.gear_wears_as
	var material := PhysicsMaterial.new()
	material.friction = wear.friction
	material.bounce = wear.bounce
	var dropped: Array[RigidBody3D] = []
	var boxes: Array[AABB] = []
	for prop: VoxelModel in model.gear():
		var drawn := prop.drawn
		if drawn.mesh == null:
			continue
		var frame := drawn.global_transform
		var bounds := drawn.mesh.get_aabb()
		var body := RigidBody3D.new()
		body.name = "Dropped%s" % drawn.get_parent().name
		body.collision_layer = DEBRIS_LAYER
		body.collision_mask = DEBRIS_MASK
		body.continuous_cd = true
		body.physics_material_override = material
		var voxel := VoxelShape.SCALE * prop.shape.scale
		body.mass = maxf(wear.density * prop.count * voxel * voxel * voxel, ScriptedDestruction.MIN_MASS)
		add_child(body, true)
		# A physics body must not be scaled: it takes the box's middle and the
		# mesh's turn, and the mesh keeps any scale it has.
		body.global_transform = Transform3D(frame.basis.orthonormalized(), frame * bounds.get_center())
		drawn.reparent(body, true)
		var box := BoxShape3D.new()
		box.size = bounds.size * frame.basis.get_scale() * (1.0 - ScriptedDestruction.SLACK)
		var collider := CollisionShape3D.new()
		collider.shape = box
		body.add_child(collider)
		body.linear_velocity = knock.call(body.global_position)
		body.angular_velocity = _random_in_ball() * FIGURE_SPIN
		dropped.append(body)
		boxes.append(frame * bounds)
	for one in dropped.size():
		var passes: Array = []
		for other in dropped.size():
			if other != one and boxes[one].intersects(boxes[other]):
				dropped[one].add_collision_exception_with(dropped[other])
				passes.append(dropped[other])
		for lump in mini(pieces.size(), lumps.size()):
			var piece := pieces[lump]
			if boxes[one].intersects(piece.transform * AABB(-piece.size * 0.5, piece.size)):
				PhysicsServer3D.body_add_collision_exception(dropped[one].get_rid(), lumps[lump])
		voxels.take_on_later(dropped[one], wear, "", passes)


## A point picked evenly from inside a ball one across, from [member _show].
func _random_in_ball() -> Vector3:
	var point := Vector3(_show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0))
	while point.length_squared() > 1.0:
		point = Vector3(_show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0))
	return point


## Takes away debris that no longer belongs: fallen well below the map, or
## wedged inside the level's voxels. Only pieces still moving are looked at,
## since one at rest is neither falling nor jostling, and a block falling whole
## is left to land.
func _tidy_debris() -> void:
	var limit := _grid.map_bounds().position.y - FALL_LIMIT
	for node in get_tree().get_nodes_in_group(PIECES):
		var body := node as RigidBody3D
		if body == null or body.sleeping or body.freeze:
			continue
		var center := debris_box(body).get_center()
		if center.y < limit or voxels.is_solid_at(center):
			body.queue_free()
	voxel_debris.tidy(limit, voxels.is_solid_at)
