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
## Blocks have no collision of their own, so on ready each one without any is
## given a cube, the shape it already is to the rules, for debris to land on.
## Debris that no longer belongs anywhere is tidied away: a piece knocked off
## the edge of the map, once it has fallen well below it, and one wedged inside
## a block, where it cannot be seen and would jostle for ever.
class_name TerrainDestruction
extends Node3D

## Physics layers: the blocks, and the pieces broken off them.
const TERRAIN_LAYER := 1 << 0
const DEBRIS_LAYER := 1 << 2
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

var _grid: CombatGrid
var _map: GridMap
## MeshLibrary item id -> the [Destruction] that breaks that block.
var _destructions := {}
## Seconds until debris is next looked over.
var _tidy_in := TIDY_SECONDS


## One broken block and everything it brings down: the debris left so far, and
## the units dropping through it, who pass through whatever more it leaves.
class Collapse:
	var rubble: Array[PhysicsBody3D] = []
	var fallers: Array[Unit] = []

	## Adds [param left] to the rubble, for everyone dropping through it.
	func add(left: Array[PhysicsBody3D]) -> void:
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
	_give_blocks_collision()
	_grid.terrain_struck.connect(_on_terrain_struck)
	_grid.terrain_blasted.connect(_on_terrain_blasted)


func _physics_process(delta: float) -> void:
	_tidy_in -= delta
	if _tidy_in > 0.0:
		return
	_tidy_in = TIDY_SECONDS
	_tidy_debris()


## Breaks the block at [param cell], if it is one that breaks, brings down
## every breakable block stacked on it, and drops anyone left standing on
## nothing. [param hit] is the round that broke it, or null. Returns whether it
## broke.
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


func _on_terrain_struck(hit: CombatGrid.RayHit, _damage: int) -> void:
	break_block(hit.cell, hit)


## Breaks every breakable block among [param cells], the cells a blast at
## [param origin] reaches, then throws the debris inside the blast about with a
## [Blast] of [param force]: what it has just broken, as its pieces are let
## go, and whatever was lying there already, the fallen among it (see
## [method CharacterModel.blast]), the blast's own dead too.
##
## The blocks break from the top down, so each one is blasted apart where it
## stands rather than first falling on the one below it, the way a block does
## when something under it breaks; blocks stacked above the blast still fall.
func _on_terrain_blasted(origin: Vector3, cells: Array[Vector3i], _damage: int, force: float) -> void:
	var ordered := cells.duplicate()
	ordered.sort_custom(func(a: Vector3i, b: Vector3i) -> bool: return a.y > b.y)
	for cell in ordered:
		break_block(cell)
	if force <= 0.0 or cells.is_empty():
		return
	# The pieces of what broke are held still until the next physics step
	# (see ScriptedDestruction), and set moving then, before this resumes. So
	# are the bodies of those the blast has just killed.
	await get_tree().physics_frame
	Blast.burst(_debris_within(cells), origin, force)
	var box := _blast_box(cells)
	for node in get_tree().get_nodes_in_group(CharacterModel.CORPSES):
		(node as CharacterModel).blast(origin, box, force)


## The box, in world space, that [param cells] fill.
func _blast_box(cells: Array[Vector3i]) -> AABB:
	var box := AABB(_grid.cell_center(cells[0]), Vector3.ZERO)
	for cell in cells:
		box = box.expand(_grid.cell_center(cell))
	return box.grow(0.5)


## Every piece of debris lying inside [param cells], free to be thrown about:
## not held still, and not a block falling whole, which drops only straight
## down.
func _debris_within(cells: Array[Vector3i]) -> Array[RigidBody3D]:
	var box := _blast_box(cells)
	var pieces: Array[RigidBody3D] = []
	for node in find_children("*", "RigidBody3D", true, false):
		var body := node as RigidBody3D
		if body is FallingBlock or body.freeze:
			continue
		if box.has_point(debris_box(body).get_center()):
			pieces.append(body)
	return pieces


## Breaks the block at [param cell] where it stands, and lets the blocks
## stacked on it fall.
func _break(cell: Vector3i, hit: CombatGrid.RayHit, collapse: Collapse) -> bool:
	var destruction: Destruction = _destructions.get(_map.get_cell_item(cell))
	if destruction == null:
		return false
	var at := _mesh_transform(cell)
	_map.set_cell_item(cell, GridMap.INVALID_CELL_ITEM)
	destruction.shatter(self, at, hit)
	_drop_blocks_above(cell, collapse)
	return true


## Lets each breakable block stacked on [param cell], up to the first that
## cannot break, fall whole, to break where it lands. They leave the grid now,
## with the block they stood on, so the rules never wait for them to come down.
func _drop_blocks_above(cell: Vector3i, collapse: Collapse) -> void:
	var above := cell + Vector3i.UP
	var destruction: Destruction = _destructions.get(_map.get_cell_item(above))
	while destruction != null:
		var block := _falling_block(above, destruction)
		_map.set_cell_item(above, GridMap.INVALID_CELL_ITEM)
		block.landed.connect(_on_landed.bind(destruction, collapse))
		above += Vector3i.UP
		destruction = _destructions.get(_map.get_cell_item(above))


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


## Breaks a block that fell whole where it landed, [param at], its pieces
## carrying on its fall, and lets anyone dropping through the collapse pass
## through them.
func _on_landed(at: Transform3D, motion: Destruction.Motion, destruction: Destruction, collapse: Collapse) -> void:
	var before := get_child_count()
	destruction.shatter(self, at, null, motion)
	collapse.add(_left_since(before))


## Every piece of debris among, or under, the children added since there were
## [param before] of them: whatever a breaking block has just left. Blocks
## falling whole are not among them; they never meet a unit.
func _left_since(before: int) -> Array[PhysicsBody3D]:
	var left: Array[PhysicsBody3D] = []
	for index in range(before, get_child_count()):
		var child := get_child(index)
		if child is FallingBlock:
			continue
		if child is PhysicsBody3D:
			left.append(child as PhysicsBody3D)
		for node in child.find_children("*", "PhysicsBody3D", true, false):
			left.append(node as PhysicsBody3D)
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
## wedged inside a block. Only pieces still moving are looked at, since one
## at rest is neither falling nor jostling.
func _tidy_debris() -> void:
	var limit := _grid.map_bounds().position.y - FALL_LIMIT
	for node in find_children("*", "RigidBody3D", true, false):
		var body := node as RigidBody3D
		if body.sleeping or body.freeze:
			continue
		var center := debris_box(body).get_center()
		if center.y < limit or _grid.is_solid(_map.local_to_map(_map.to_local(center))):
			body.queue_free()


## Gives each block with no collision shape a cube that fills its cell. The
## map gets a copy of the MeshLibrary to hold them, so the library on disk, and
## any block given a shape of its own there, is left as it is.
func _give_blocks_collision() -> void:
	var library := _map.mesh_library.duplicate() as MeshLibrary
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
	_map.mesh_library = library
	_map.collision_layer = TERRAIN_LAYER
	_map.collision_mask = 0
