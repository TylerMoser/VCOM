## Breaks the blocks rounds strike and blasts reach, and whatever they were
## holding up.
##
## When the [CombatGrid] reports a strike, the struck block breaks if the
## [member catalog] has a [Destruction] for it; when it reports a blast, so
## does every block inside it, and the debris inside it is thrown about by
## the blast (see [method _on_terrain_blasted]). The block leaves the grid at
## once, so sight, cover and paths change the moment it goes, and its
## destruction plays out what is left of it under this node. Every breakable
## block stacked on it leaves the grid with it, but falls whole, as a
## [FallingBlock], and breaks where it lands; a block that cannot break is left
## where it is, and so is everything on it. A unit left standing on nothing
## drops to the ground below, falling with the rubble of what it stood on and
## passing through it, and through whatever the blocks falling with it break
## into.
##
## A block that wears away ([VoxelDestruction]) is the exception: a strike or
## a blast only breaks voxels off it, through this node's [VoxelTerrain], and
## it breaks as above only once it is worn past standing. What is left of it
## then crumbles, and its voxels and pieces are [VoxelDebris].
##
## Blocks have no collision of their own, so on ready each one without any is
## given a cube, the shape it already is to the rules, for debris to land on,
## or, if it wears away, the shape of its voxels. Debris that no longer belongs
## anywhere is tidied away: a piece knocked off the edge of the map, once it
## has fallen well below it, and one wedged inside a block, where it cannot be
## seen and would jostle for ever.
##
## The pieces debris is broken into, each a body of its own, are found by
## asking the physics ([method pieces_in]), never by walking the scene: with a
## few thousand lying about, walking it took longer than the rest of a blast
## did together.
##
## Each block that breaks is announced ([signal block_broken]), for whatever
## it leaves behind besides its pieces, such as a coin ([Coins]).
class_name TerrainDestruction
extends Node3D

## Emitted as a block breaks, [param destruction] saying what kind it was.
## [param cell] is where it broke: where it stood, or, for one that fell whole,
## the cell it landed in.
signal block_broken(cell: Vector3i, destruction: Destruction)

## Physics layers: the blocks, and the pieces broken off them.
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
## What debris lands on and bumps off: the blocks, other debris, and units.
const DEBRIS_MASK := TERRAIN_LAYER | DEBRIS_LAYER | Unit.BODY_LAYER
## How far below the bottom of the map, in cells, debris falls before it is
## taken away, and how often, in seconds, debris is looked over.
const FALL_LIMIT := 10.0
const TIDY_SECONDS := 1.0

## What breaks, and how.
@export var catalog: DestructionCatalog

@export_group("Nodes")
@export var grid_path: NodePath = ^"../CombatGrid"
@export var grid_map_path: NodePath = ^"../GridMap"

## The voxels of the blocks that wear away, and the voxels broken off them.
var voxels: VoxelTerrain
var voxel_debris: VoxelDebris

var _grid: CombatGrid
var _map: GridMap
## MeshLibrary item id -> the [Destruction] that breaks that block.
var _destructions := {}
## Seconds until debris is next looked over.
var _tidy_in := TIDY_SECONDS


## One broken block and everything it brings down: the debris left so far, by
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
	_map = get_node_or_null(grid_map_path) as GridMap
	if _grid == null or _map == null:
		push_error("TerrainDestruction: missing CombatGrid or GridMap.")
		return
	if catalog == null:
		push_error("TerrainDestruction: no catalog, so nothing will break.")
	else:
		_destructions = catalog.by_item(_map.mesh_library)
		for destruction: Destruction in _destructions.values():
			destruction.prepare()
	voxel_debris = VoxelDebris.new()
	voxel_debris.focus = _looked_at
	add_child(voxel_debris)
	voxels = VoxelTerrain.new(_grid, _map, voxel_debris)
	add_child(voxels)
	# The map gets a copy of the MeshLibrary to change, so the library on disk
	# is left as it is.
	var library := _map.mesh_library.duplicate() as MeshLibrary
	_give_blocks_collision(library)
	voxels.take_on(library, _destructions)
	_map.mesh_library = library
	_map.collision_layer = TERRAIN_LAYER
	_map.collision_mask = 0
	_grid.voxels = voxels
	_grid.terrain_struck.connect(_on_terrain_struck)
	_grid.terrain_blasted.connect(_on_terrain_blasted)
	_grid.round_flown.connect(_on_round_flown)


func _physics_process(delta: float) -> void:
	if voxel_debris == null:
		return
	_wake_in_the_way()
	_tidy_in -= delta
	if _tidy_in > 0.0:
		return
	_tidy_in = TIDY_SECONDS
	_tidy_debris()


## Breaks the block at [param cell], if it is one that breaks, brings down
## every breakable block stacked on it, and drops anyone left standing on
## nothing. [param hit] is the round that broke it, or null. Returns whether it
## broke. A block that wears away breaks whole, however much is left of it.
func break_block(cell: Vector3i, hit: CombatGrid.RayHit = null) -> bool:
	var collapse := Collapse.new()
	var before := get_child_count()
	if not _break(cell, hit, collapse):
		return false
	collapse.add(_left_since(before))
	_drop_stranded_units(collapse)
	return true


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


## A strike breaks the block it struck, or, if the block wears away, breaks
## voxels off it, and the block only if that leaves it worn past standing.
func _on_terrain_struck(hit: CombatGrid.RayHit, damage: int) -> void:
	if not voxels.wears_away(hit.cell):
		break_block(hit.cell, hit)
		return
	var wear := voxels.chip(hit, damage)
	_wake_debris(wear)
	for cell in _top_down(wear.broken):
		break_block(cell, hit)


## Blows a crater round [param origin] in every block among [param cells], the
## cells a blast there reaches, that wears away, then breaks every breakable
## block among them that does not and every one the crater has worn past
## standing, then throws the debris inside the blast about with a [Blast] of
## [param force]: what it has just broken, as its pieces are let go, and
## whatever was lying there already, the fallen among it (see
## [method CharacterModel.blast]), the blast's own dead too.
##
## The blocks break from the top down, so each one is blasted apart where it
## stands rather than first falling on the one below it, the way a block does
## when something under it breaks; blocks stacked above the blast still fall.
func _on_terrain_blasted(origin: Vector3, cells: Array[Vector3i], damage: int, force: float) -> void:
	var wear := voxels.crater(origin, cells, damage)
	_wake_debris(wear)
	var breaking := wear.broken.duplicate()
	for cell in cells:
		if not voxels.wears_away(cell):
			breaking.append(cell)
	for cell in _top_down(breaking):
		break_block(cell)
	if force <= 0.0 or cells.is_empty():
		return
	# The pieces of what broke are held still until the next physics step
	# (see ScriptedDestruction), and set moving then, before this resumes. So
	# are the bodies of those the blast has just killed.
	await get_tree().physics_frame
	Blast.burst(_debris_within(cells), origin, force)
	var box := _blast_box(cells)
	voxel_debris.burst(origin, box, force)
	for node in get_tree().get_nodes_in_group(CharacterModel.CORPSES):
		(node as CharacterModel).blast(origin, box, force)


## [param cells], highest first.
static func _top_down(cells: Array[Vector3i]) -> Array[Vector3i]:
	var ordered := cells.duplicate()
	ordered.sort_custom(func(a: Vector3i, b: Vector3i) -> bool: return a.y > b.y)
	return ordered


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
## The voxels' own lumps are woken as each worn block is redrawn.
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


## Breaks the block at [param cell] where it stands, and lets the blocks
## stacked on it fall.
func _break(cell: Vector3i, hit: CombatGrid.RayHit, collapse: Collapse) -> bool:
	var destruction: Destruction = _destructions.get(_map.get_cell_item(cell))
	if destruction == null:
		return false
	if destruction is VoxelDestruction:
		var shape := voxels.shape_at(cell)
		var frame := voxels.frame_of(cell)
		var left := voxels.take(cell)
		_map.set_cell_item(cell, GridMap.INVALID_CELL_ITEM)
		collapse.add(voxels.crumble(left, shape, frame, destruction as VoxelDestruction, hit))
	else:
		var at := _mesh_transform(cell)
		_map.set_cell_item(cell, GridMap.INVALID_CELL_ITEM)
		destruction.shatter(self, at, hit)
	block_broken.emit(cell, destruction)
	var top := _drop_blocks_above(cell, collapse)
	# Whatever lay on it, or on the blocks falling with it, is woken to fall
	# too: the physics would leave it lying on air.
	var column := AABB(_grid.cell_center(cell) - Vector3.ONE * 0.5, Vector3(1.0, top.y - cell.y + 1, 1.0))
	column = column.grow(VoxelDebris.LYING_ON)
	_wake_pieces(column)
	voxel_debris.wake(column)
	return true


## Lets each breakable block stacked on [param cell], up to the first that
## cannot break, fall whole, to break where it lands. They leave the grid now,
## with the block they stood on, so the rules never wait for them to come down.
## Returns the cell just above the last one that fell.
func _drop_blocks_above(cell: Vector3i, collapse: Collapse) -> Vector3i:
	var above := cell + Vector3i.UP
	var destruction: Destruction = _destructions.get(_map.get_cell_item(above))
	while destruction != null:
		if destruction is VoxelDestruction:
			_drop_worn_block(above, destruction as VoxelDestruction, collapse)
		else:
			var block := _falling_block(above, destruction)
			block.landed.connect(_on_landed.bind(destruction, collapse))
		_map.set_cell_item(above, GridMap.INVALID_CELL_ITEM)
		above += Vector3i.UP
		destruction = _destructions.get(_map.get_cell_item(above))
	return above


## Puts the block at [param cell] under this node as a [FallingBlock], standing
## where the grid draws it, with the mesh and collision the grid gives it, and
## as heavy as [param destruction] says it is whole.
func _falling_block(cell: Vector3i, destruction: Destruction) -> FallingBlock:
	var item := _map.get_cell_item(cell)
	var library := _map.mesh_library
	var block := FallingBlock.new(library.get_item_mesh(item), library.get_item_mesh_transform(item),
		library.get_item_shapes(item), destruction.mass)
	add_child(block)
	var turn := _map.get_basis_with_orthogonal_index(_map.get_cell_item_orientation(cell))
	block.global_transform = _map.global_transform * Transform3D(turn, _map.map_to_local(cell))
	return block


## Lets the block at [param cell], one that wears away, fall whole as what is
## left of it, as heavy as its share of [param destruction]'s mass, to crumble
## where it lands.
func _drop_worn_block(cell: Vector3i, destruction: VoxelDestruction, collapse: Collapse) -> void:
	var shape := voxels.shape_at(cell)
	var frame := voxels.frame_of(cell)
	var share := float(voxels.count_at(cell)) / maxi(shape.count, 1)
	var left := voxels.take(cell)
	var block := FallingBlock.new(VoxelMesher.mesh(shape, left), Transform3D.IDENTITY, [],
		maxf(destruction.mass * share, ScriptedDestruction.MIN_MASS))
	add_child(block)
	block.global_transform = frame
	block.landed.connect(_on_worn_block_landed.bind(destruction, collapse, left, shape))


## Breaks a block that fell whole where it landed, [param at], its pieces
## carrying on its fall, and lets anyone dropping through the collapse pass
## through them.
func _on_landed(at: Transform3D, motion: Destruction.Motion, destruction: Destruction, collapse: Collapse) -> void:
	var before := get_child_count()
	destruction.shatter(self, at, null, motion)
	collapse.add(_left_since(before))
	block_broken.emit(_map.local_to_map(_map.to_local(motion.center)), destruction)


## Crumbles [param left], what was left of a block of [param shape]'s kind
## that fell whole, where it landed, [param at] being its frame there.
func _on_worn_block_landed(
	at: Transform3D, motion: Destruction.Motion, destruction: VoxelDestruction, collapse: Collapse,
	left: PackedByteArray, shape: VoxelShape
) -> void:
	collapse.add(voxels.crumble(left, shape, at, destruction, null, motion))
	block_broken.emit(_map.local_to_map(_map.to_local(motion.center)), destruction)


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


## Where the grid draws the mesh of the block at [param cell], in world space:
## the cell, turned the way the block is turned, with the MeshLibrary's offset
## for the block's mesh. What replaces the block stands here to cover it.
func _mesh_transform(cell: Vector3i) -> Transform3D:
	var item := _map.get_cell_item(cell)
	var turn := _map.get_basis_with_orthogonal_index(_map.get_cell_item_orientation(cell))
	var place := Transform3D(turn, _map.map_to_local(cell))
	return _map.global_transform * place * _map.mesh_library.get_item_mesh_transform(item)


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


## Takes away debris that no longer belongs: fallen well below the map, or
## wedged inside a block, inside its voxels if it wears away. Only pieces still
## moving are looked at, since one at rest is neither falling nor jostling, and
## a block falling whole is left to land.
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


## Gives each block of [param library] with no collision shape a cube that fills
## its cell. A block given a shape of its own in the library keeps it.
func _give_blocks_collision(library: MeshLibrary) -> void:
	var cube := BoxShape3D.new()
	cube.size = _map.cell_size
	# A cell's origin is its centre only along the axes the grid centres on.
	var middle := Vector3(
		0.0 if _map.cell_center_x else _map.cell_size.x * 0.5,
		0.0 if _map.cell_center_y else _map.cell_size.y * 0.5,
		0.0 if _map.cell_center_z else _map.cell_size.z * 0.5,
	)
	for item in library.get_item_list():
		if library.get_item_shapes(item).is_empty():
			library.set_item_shapes(item, [cube, Transform3D(Basis.IDENTITY, middle)])
