## Throw a grenade the unit carries at a tile, for one action point. Only a
## unit with a grenade equipped has it. It throws the first one it carries,
## Item 1 before Item 2, and that grenade is gone for good once thrown; with
## the last one gone, so is the action.
##
## While the action is up, every tile the unit can throw to is tinted faintly:
## those within [constant Throwing.RANGE] tiles whose arc nothing blocks. The
## tile under the cursor shows the throw there: its arc, the ground its blast
## covers, and a bracket on everyone it would catch with the damage each would
## take, gold on the squad, whom it hurts as much as anyone, the thrower
## included. An arc that runs into something is drawn red up to where it is
## stopped, with a cross there, and cannot be thrown.
##
##   Throw - right-click a tile, or Enter / Space to throw at the tile under
##           the cursor.
##
## Nothing is rolled: a grenade goes off where it is thrown. Which way it can
## go and whom its blast catches is [Throwing]'s business, and what the blast
## does is [method Unit.throw_at]'s.
class_name ThrowGrenadeAction
extends UnitAction

## Action points a throw costs: what a shot does.
const COST := 1
const RANGE_LAYER := &"throw_range"
const BLAST_LAYER := &"throw_blast"
## Faint, borders and all (the colour's alpha dims both), so the terrain still
## reads through a field of tiles in reach and the blast stands out on it.
const RANGE_COLOR := Color(1.0, 0.6, 0.3, 0.5)
const RANGE_FILL := 0.25
const BLAST_COLOR := Color(1.0, 0.2, 0.1)
const BLAST_FILL := 0.7
## Seconds the action holds on once the blast has gone off, so it is seen
## before the tiles in reach come back up for another throw.
const AFTERMATH_SECONDS := 0.5

@export var overlay_path: NodePath = ^"../../HUD/ShotOverlay"
## Where the grenade in flight and its explosion are put: the map.
@export var effects_path: NodePath = ^"../.."

var _unit: Unit
var _throwing: Throwing
## Tile -> [Throwing.Throw], for every throw the unit can make.
var _throws := {}
## The tile under the cursor, or null while it is on no tile.
var _aimed: Variant = null
## The throw at [member _aimed], clear or blocked. Null while the cursor is on
## no tile in range.
var _throw: Throwing.Throw
var _overlay: ShotOverlay
var _effects: Node


func _init() -> void:
	display_name = "Throw Grenade"
	required_tag = Item.GRENADE


func _ready() -> void:
	set_process(false)
	_overlay = get_node_or_null(overlay_path) as ShotOverlay
	if _overlay == null:
		push_error("ThrowGrenadeAction: no ShotOverlay at '%s'." % overlay_path)
	_effects = get_node_or_null(effects_path)
	if _effects == null:
		push_error("ThrowGrenadeAction: no node at '%s' to show the throw in." % effects_path)


# Follow the cursor every frame, not only when the mouse moves, so the throw
# stays right while the camera pans or turns under a still cursor.
func _process(_delta: float) -> void:
	_aim(controller.tile_under_cursor(get_viewport().get_mouse_position()))


func is_available(unit: Unit) -> bool:
	return unit.actions_remaining >= COST and unit.grenade != null


func begin(unit: Unit) -> void:
	_unit = unit
	_throwing = Throwing.new(controller.grid)
	_throws = _throwing.throws_for(unit)
	var tiles := {}
	for tile: Vector3i in _throws:
		tiles[tile] = RANGE_COLOR
	controller.highlights.set_layer(RANGE_LAYER, tiles, RANGE_FILL)
	_aimed = null
	set_process(true)


func end() -> void:
	set_process(false)
	_clear_aim()
	controller.highlights.clear_layer(RANGE_LAYER)
	_unit = null
	_throwing = null
	_throws.clear()
	_aimed = null


func handle_input(event: InputEvent) -> bool:
	if event.is_action_pressed(&"execute_action") and event is InputEventMouseButton:
		_aim(controller.tile_under_cursor((event as InputEventMouseButton).position))
		_throw_lined_up()
		return true
	if event.is_action_pressed(&"confirm_action"):
		_throw_lined_up()
		return true
	return false


## Lines up the throw at [param tile], the tile under the cursor, or puts the
## throw away while it is on no tile in range.
func _aim(tile: Variant) -> void:
	if tile == _aimed:
		return
	_aimed = tile
	var from := controller.grid.tile_at(_unit.global_position)
	if tile == null or not Throwing.is_in_range(from, tile):
		_clear_aim()
		return
	_throw = _throws[tile] if _throws.has(tile) else _throwing.plan(from, tile)
	_show_throw()


## Throws the throw lined up, if the unit can make it: spends the action,
## flies the grenade, and calls what the blast did over everyone it caught.
func _throw_lined_up() -> void:
	if _throw == null or not _throw.is_clear():
		return
	var throw := _throw
	var unit := _unit
	unit.spend_actions(COST)
	# Drop the aim before anything moves: the blast is about to change the
	# ground it was worked out on.
	set_process(false)
	_clear_aim()
	controller.highlights.clear_layer(RANGE_LAYER)
	controller.busy = true

	var landed: Array = await unit.throw_at(throw, controller.grid, _fly)
	if _overlay != null and not landed.is_empty():
		var results := []
		for entry: Array in landed:
			results.append([entry[0], "%d" % entry[1], true])
		# Over the heads: no panel holds the space above them.
		_overlay.flash_results(results, false)
	# Hold on while the blast plays out and anyone it knocked off their feet
	# lands, so the next throw is worked out on the ground as it now stands.
	await get_tree().create_timer(AFTERMATH_SECONDS, false).timeout
	while _anyone_falling():
		await get_tree().process_frame
	completed.emit()


## Shows [param throw] in flight and [param grenade] going off at the end of
## it. Handed to [method Unit.throw_at], which holds the blast until it
## returns, as the grenade arrives.
func _fly(throw: Throwing.Throw, grenade: Grenade) -> void:
	if _effects == null:
		return
	var flying := ThrownGrenade.new()
	_effects.add_child(flying)
	await flying.fly(throw)
	Explosion.go_off(_effects, throw.end, grenade.blast_size)


func _show_throw() -> void:
	var caught := []
	if _throw.is_clear():
		var grenade := _unit.grenade
		var tiles := {}
		for tile in _throwing.blast_tiles(_throw.target, grenade.blast_size):
			tiles[tile] = BLAST_COLOR
		controller.highlights.set_layer(BLAST_LAYER, tiles, BLAST_FILL)
		var grid := controller.grid
		for unit in _throwing.caught(_throw.target, grenade.blast_size):
			caught.append([
				grid.cell_center(LineOfSight.eye_cell(grid.tile_at(unit.global_position))),
				"%d" % unit.damage_from(grenade.damage),
				unit in controller.squad.members,
			])
	else:
		controller.highlights.clear_layer(BLAST_LAYER)
	if _overlay != null:
		_overlay.show_throw(_throw.points, not _throw.is_clear(), caught)


func _clear_aim() -> void:
	_throw = null
	controller.highlights.clear_layer(BLAST_LAYER)
	if _overlay != null:
		_overlay.clear()


## Whether anyone is on the move, as a unit whose floor a blast broke is while
## it drops to the ground below.
func _anyone_falling() -> bool:
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		if (node as Unit).is_moving():
			return true
	return false
