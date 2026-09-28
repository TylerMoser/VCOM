## Breaks the blocks rounds strike, and whatever they were holding up.
##
## When the [CombatGrid] reports a strike, the struck block breaks if the
## [member catalog] has a [Destruction] for it. The block leaves the grid at
## once, so sight, cover and paths change the moment it goes, and its
## destruction plays out what is left of it under this node. A breakable block
## left with nothing under it comes down the same way, so a stack falls with
## the block it stood on; a block that cannot break is left where it is. A unit
## left standing on nothing drops to the ground below, falling with the rubble
## of what it stood on and passing through it.
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


func _physics_process(delta: float) -> void:
	_tidy_in -= delta
	if _tidy_in > 0.0:
		return
	_tidy_in = TIDY_SECONDS
	_tidy_debris()


## Breaks the block at [param cell], if it is one that breaks, along with every
## breakable block stacked on it, and drops anyone left standing on nothing.
## [param hit] is the round that broke it, or null. Returns whether it broke.
func break_block(cell: Vector3i, hit: CombatGrid.RayHit = null) -> bool:
	var before := get_child_count()
	if not _break(cell, hit):
		return false
	var rubble: Array[PhysicsBody3D] = []
	for index in range(before, get_child_count()):
		var left := get_child(index)
		if left is PhysicsBody3D:
			rubble.append(left as PhysicsBody3D)
		for node in left.find_children("*", "PhysicsBody3D", true, false):
			rubble.append(node as PhysicsBody3D)
	_drop_stranded_units(rubble)
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


## Breaks the block at [param cell] and then, one by one, each breakable block
## stacked on it, which the one below leaves standing on nothing.
func _break(cell: Vector3i, hit: CombatGrid.RayHit) -> bool:
	var destruction: Destruction = _destructions.get(_map.get_cell_item(cell))
	if destruction == null:
		return false
	var at := _mesh_transform(cell)
	_map.set_cell_item(cell, GridMap.INVALID_CELL_ITEM)
	destruction.shatter(self, at, hit)
	_break(cell + Vector3i.UP, null)
	return true


## Where the grid draws the mesh of the block at [param cell], in world space:
## the cell, turned the way the block is turned, with the MeshLibrary's offset
## for the block's mesh. What replaces the block stands here to cover it.
func _mesh_transform(cell: Vector3i) -> Transform3D:
	var item := _map.get_cell_item(cell)
	var turn := _map.get_basis_with_orthogonal_index(_map.get_cell_item_orientation(cell))
	var place := Transform3D(turn, _map.map_to_local(cell))
	return _map.global_transform * place * _map.mesh_library.get_item_mesh_transform(item)


## Drops every unit left standing on nothing to the ground below it, through
## [param rubble], the debris of what just broke.
func _drop_stranded_units(rubble: Array[PhysicsBody3D]) -> void:
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		_drop_if_stranded(node as Unit, rubble)


## Drops [param unit] to the ground below if it stands on nothing, through
## [param rubble]. A unit on the move is left to finish first, since it may be
## walking off onto solid ground.
func _drop_if_stranded(unit: Unit, rubble: Array[PhysicsBody3D]) -> void:
	while is_instance_valid(unit) and unit.is_moving():
		await get_tree().process_frame
	if not is_instance_valid(unit) or unit.health <= 0:
		return
	var tile := _grid.tile_at(unit.global_position)
	if _grid.is_solid(tile + Vector3i.DOWN):
		return
	var landing: Variant = _grid.tile_under(tile)
	if landing != null:
		unit.drop_to(_grid.tile_position(landing), rubble)


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
