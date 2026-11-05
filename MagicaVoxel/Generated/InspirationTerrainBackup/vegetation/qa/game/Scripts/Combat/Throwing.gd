## Where a grenade can be thrown, and whom its blast catches: the rules of
## throwing, read off the voxel grid.
##
## A grenade flies in an arc from over the thrower's head to the middle of the
## tile it is thrown at, and goes off there. The arc is a parabola that rises
## higher the further the throw, and it is traced through the grid as a round
## is: if anything solid stands in its way, the throw cannot be made. Nothing
## else stops it. Like a sight line it passes over units, and it needs no
## sight of where it lands, only a clear way there. It is thrown from the tile
## the thrower stands on, never leaning out: its start is high enough to clear
## the full cover beside it.
##
## Where it lands decides what it can reach. It comes down steeply enough to
## drop behind half cover on to the tile beyond, even from the full range,
## but not behind full cover: the tile right behind a block two cells high is
## out of a grenade's reach from anywhere, the thrower's own side of it
## included. Thrown a tile further, past whoever is hiding there, the blast
## still catches them.
##
## The blast is a cube of cells centred on the lower cell of the tile the
## grenade lands in, [member Grenade.blast_size] cells on a side: a 3 takes in
## the eight tiles round the target and the target's own, from the floor under
## them to a unit's head. Everyone with a cell inside it is caught, friend and
## foe alike, the thrower too, and walls inside it shelter nobody. Every
## breakable block inside it breaks.
##
## How far a grenade can be thrown is the same for every unit and every
## grenade: [constant RANGE] tiles across the ground.
class_name Throwing
extends RefCounted

## How far a grenade can be thrown, in tiles across the ground, measured as
## sight range is, so height is left out. The one setting for every unit and
## every grenade.
const RANGE := 10
## How far above the thrower's floor the grenade leaves its hand, in cells:
## over its head, so that it clears the full cover the thrower may be hiding
## behind.
const RELEASE_HEIGHT := 1.9
## How high the arc rises above the straight line from the hand to where the
## grenade goes off, at its middle: this much for every tile thrown, and never
## less than [constant ARC_MIN_HEIGHT], so a short toss still arcs. These set
## what a throw can get over: with less rise, a long throw no longer comes
## down steeply enough to clear the half cover in front of its target.
const ARC_RISE := 0.3
const ARC_MIN_HEIGHT := 0.75
## How long each of the straight pieces the arc is traced and drawn as is,
## across the ground, in cells.
const TRACE_STEP := 0.25


## One throw from a tile at another: the arc the grenade flies, and whether
## anything stops it.
class Throw:
	## The tile the thrower stands on, and the tile it throws at.
	var from: Vector3i
	var target: Vector3i
	## Where the grenade leaves the thrower's hand, and where it goes off: the
	## middle of the target tile's lower cell, which is the middle of its
	## blast.
	var start: Vector3
	var end: Vector3
	## How far the arc rises above the straight line from [member start] to
	## [member end], at its middle, in cells.
	var height := 0.0
	## The arc, as the straight pieces it is traced and drawn as: from
	## [member start] to [member end], or for a blocked throw to where it runs
	## into something.
	var points := PackedVector3Array()
	## Where the arc first runs into something solid, or null if nothing
	## stands in its way.
	var blocked: CombatGrid.RayHit
	## How far it is thrown, in tiles across the ground.
	var distance := 0.0

	## Whether nothing stands in the arc's way, so the throw can be made if it
	## is in range (see [method Throwing.is_in_range]).
	func is_clear() -> bool:
		return blocked == null

	## Where the arc is [param along] of the way from the hand to where the
	## grenade goes off, measured across the ground: 0 at [member start], 1 at
	## [member end]. The grenade crosses the ground at a steady speed, as
	## anything thrown does, so this is also where it is that far through its
	## flight.
	func point_at(along: float) -> Vector3:
		return start.lerp(end, along) + Vector3.UP * (4.0 * height * along * (1.0 - along))


var _grid: CombatGrid


func _init(grid: CombatGrid) -> void:
	_grid = grid


## Whether a grenade thrown from [param from] can be thrown at [param target]
## for distance: no more than [constant RANGE] tiles across the ground, and not
## straight up or down, at the thrower's own feet.
static func is_in_range(from: Vector3i, target: Vector3i) -> bool:
	var distance := ground_distance(from, target)
	return distance > 0.0 and distance <= RANGE


## How far apart two tiles are across the ground, in tiles, as sight range
## measures it.
static func ground_distance(a: Vector3i, b: Vector3i) -> float:
	return Vector2(a.x - b.x, a.z - b.z).length()


## The throw from the tile [param from] at the tile [param target]: its arc,
## and whether anything blocks it. Planned whether or not it is in range.
func plan(from: Vector3i, target: Vector3i) -> Throw:
	var throw := Throw.new()
	throw.from = from
	throw.target = target
	throw.start = _grid.tile_position(from) + Vector3.UP * RELEASE_HEIGHT
	throw.end = _grid.cell_center(target)
	throw.distance = ground_distance(from, target)
	var across := Vector2(throw.end.x - throw.start.x, throw.end.z - throw.start.z).length()
	throw.height = maxf(across * ARC_RISE, ARC_MIN_HEIGHT)

	var pieces := maxi(ceili(across / TRACE_STEP), 1)
	for piece in pieces + 1:
		throw.points.append(throw.point_at(float(piece) / pieces))
	# Each piece is cast through the grid as a round is, so the arc never
	# slips between two blocks that meet at a corner.
	for piece in pieces:
		var along := throw.points[piece + 1] - throw.points[piece]
		var hit: Variant = _grid.cast(throw.points[piece], along, along.length())
		if hit != null:
			throw.blocked = hit
			throw.points.resize(piece + 1)
			throw.points.append(throw.blocked.point)
			break
	return throw


## Every throw [param thrower] can make, by the tile it is thrown at: to every
## tile in range whose arc nothing blocks.
func throws_for(thrower: Unit) -> Dictionary:
	var from := _grid.tile_at(thrower.global_position)
	var throws := {}
	for tile in _grid.tiles():
		if not is_in_range(from, tile):
			continue
		var throw := plan(from, tile)
		if throw.is_clear():
			throws[tile] = throw
	return throws


## How far the blast of a grenade of [param size] reaches from its middle
## each way, in cells.
static func blast_reach(size: int) -> int:
	return floori((size - 1) / 2.0)


## Every cell the blast of a grenade of [param size] thrown at [param target]
## reaches, solid or not: a cube [param size] cells on a side centred on the
## target tile's lower cell.
static func blast_cells(target: Vector3i, size: int) -> Array[Vector3i]:
	var reach := blast_reach(size)
	var cells: Array[Vector3i] = []
	for dx in range(-reach, reach + 1):
		for dy in range(-reach, reach + 1):
			for dz in range(-reach, reach + 1):
				cells.append(target + Vector3i(dx, dy, dz))
	return cells


## Whether someone standing on [param tile] is caught by the blast of a
## grenade of [param size] thrown at [param target]: whether either of the
## cells they fill is inside it.
static func is_caught(tile: Vector3i, target: Vector3i, size: int) -> bool:
	var reach := blast_reach(size)
	return (
		absi(tile.x - target.x) <= reach
		and absi(tile.z - target.z) <= reach
		and tile.y <= target.y + reach
		and tile.y + CombatGrid.UNIT_HEIGHT - 1 >= target.y - reach
	)


## Everyone the blast of a grenade of [param size] thrown at [param target]
## catches, friend and foe, whoever threw it included. The throw shows these
## as it is lined up and the blast hurts the same ones, so the two cannot
## disagree.
func caught(target: Vector3i, size: int) -> Array[Unit]:
	var units: Array[Unit] = []
	for node in _grid.get_tree().get_nodes_in_group(Unit.GROUP):
		var unit := node as Unit
		if unit != null and unit.health > 0 and is_caught(_grid.tile_at(unit.global_position), target, size):
			units.append(unit)
	return units


## Every tile anyone standing on would be caught by the blast of a grenade of
## [param size] thrown at [param target]: the ground it covers, for marking on
## the map.
func blast_tiles(target: Vector3i, size: int) -> Array[Vector3i]:
	var reach := blast_reach(size)
	var tiles: Array[Vector3i] = []
	for dx in range(-reach, reach + 1):
		for dz in range(-reach, reach + 1):
			for y in range(target.y - reach - CombatGrid.UNIT_HEIGHT + 1, target.y + reach + 1):
				var cell := Vector3i(target.x + dx, y, target.z + dz)
				if _grid.is_tile(cell):
					tiles.append(cell)
	return tiles
