## Who can see whom, and what they have to hide behind. XCOM's rules, read
## off the voxel grid.
##
## A unit fills two cells, the tile it stands on and the one above, and it
## sights from the centre of that upper cell. Cover is whatever is solid
## beside a tile: one cell tall and it is low cover, which a sight line
## passes clean over; two cells or more and it is high cover, which stops the
## line dead.
##
## A unit behind cover leans out to either side of it to shoot around it, so
## high cover only denies a shot when the step out does not clear it either.
## A unit caught in the open has nothing to lean out from and fires from
## where it stands.
##
## The same leaning gives a unit away, as it does in XCOM 2: a target is seen
## on its own tile or on any tile it could lean out to, so whoever can shoot
## round their cover can be shot back at round it. That is what makes sight
## run both ways. A target on the move leans nowhere, so a reaction has to see
## it where it stands.
##
## Other units are ignored throughout: soldiers do not block line of sight,
## only terrain does.
class_name LineOfSight
extends RefCounted

enum Cover { NONE, LOW, HIGH }

## The four sides a tile can have cover on, as offsets across the ground.
const COVER_DIRECTIONS: Array[Vector2i] = [
	Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1),
]
## Cells above its own tile that a unit sights from.
const EYE_HEIGHT := 1


## One unit's shot at another: where it is taken from, and what the target
## has going for it.
class Shot:
	var target: Unit
	var target_tile: Vector3i
	## The tile the shot is taken from: the shooter's own, or the one it
	## leans out to.
	var from: Vector3i
	## True when [member from] is not the tile the shooter stands on.
	var stepped_out: bool
	## The tile the target is seen on: its own, or, when the shooter cannot see
	## that, one it leans out to round its own cover. The sight line runs here.
	var seen_at: Vector3i
	## True when [member seen_at] is not the tile the target stands on: the
	## shot catches it leaning out.
	var leaning: bool
	## The cover the target has against this shot: its own tile's, wherever it
	## is seen.
	var cover: Cover
	## True when the target is in cover, but none of it faces this shot.
	## Catching a target in the open is not flanking it: there was nothing to
	## get around.
	var flanked: bool
	## Distance from [member from] to the tile the target stands on, in tiles.
	var distance: float


var _grid: CombatGrid


func _init(grid: CombatGrid) -> void:
	_grid = grid


## The cell a unit standing on [param tile] sights from.
static func eye_cell(tile: Vector3i) -> Vector3i:
	return tile + Vector3i.UP * EYE_HEIGHT


## What to call a target's standing on screen: what it is hiding behind, or
## why it is not.
static func cover_name(cover: Cover, flanked := false) -> String:
	match cover:
		Cover.HIGH:
			return "Full Cover"
		Cover.LOW:
			return "Half Cover"
		_:
			return "Flanked" if flanked else "In the Open"


## The cover on each side of [param tile], as a dictionary of ground
## direction (Vector2i) -> [enum Cover]. Sides with nothing to hide behind
## are left out.
func cover_at(tile: Vector3i) -> Dictionary:
	var sides := {}
	for direction in COVER_DIRECTIONS:
		var beside := tile + Vector3i(direction.x, 0, direction.y)
		if not _grid.is_solid(beside):
			continue
		sides[direction] = Cover.HIGH if _grid.is_solid(beside + Vector3i.UP) else Cover.LOW
	return sides


## The cover a unit on [param tile] has against a shot from [param from]: the
## best of the sides facing the shooter. Flanking falls out of this - come at
## a unit from a side its cover does not face and it has none.
func cover_against(tile: Vector3i, from: Vector3i) -> Cover:
	var toward_shooter := Vector2i(from.x - tile.x, from.z - tile.z)
	var best := Cover.NONE
	var sides := cover_at(tile)
	for direction: Vector2i in sides:
		var side: Cover = sides[direction]
		var faces_shooter := direction.x * toward_shooter.x + direction.y * toward_shooter.y > 0
		if faces_shooter and side > best:
			best = side
	return best


## The tiles [param unit] can shoot from: the one it stands on first, then
## the tiles beside its cover it can lean out to ([method lean_tiles]), so a
## unit in the open only ever shoots from where it is.
func firing_positions(unit: Unit) -> Array[Vector3i]:
	var positions: Array[Vector3i] = [_grid.tile_at(unit.global_position)]
	positions.append_array(lean_tiles(unit))
	return positions


## The tiles beside its cover that [param unit] can lean out to: where it
## shoots round its cover from, and where it can be seen and shot at in turn.
## Cover is what makes the lean possible, so a unit in the open has none.
func lean_tiles(unit: Unit) -> Array[Vector3i]:
	var tile := _grid.tile_at(unit.global_position)
	var leans: Array[Vector3i] = []
	var occupied := _grid.occupied_tiles(unit)
	for direction: Vector2i in cover_at(tile):
		# Lean out along the cover, to one side of it and then the other.
		for side: Vector2i in [
			Vector2i(-direction.y, direction.x), Vector2i(direction.y, -direction.x)
		]:
			var peek := tile + Vector3i(side.x, 0, side.y)
			if peek in leans or occupied.has(peek) or not _grid.is_tile(peek):
				continue
			leans.append(peek)
	return leans


## The shot [param shooter] has at [param target], or null if it cannot see
## it. Firing from where it stands beats leaning out, so a unit only steps
## out when it has to.
##
## The target is seen on its own tile wherever any of the shooter's positions
## sees that. Only when none does is it seen leaning out
## ([member Shot.leaning]): on the nearest of its own [method lean_tiles] to
## the first of the shooter's positions that sees one. Its cover, and the
## shot's distance and height, are still its own tile's. [param leans] false
## leaves its leans out, for a target on the move, which leans nowhere: a
## reaction has to see it where it stands.
func find_shot(shooter: Unit, target: Unit, leans := true) -> Variant:
	var shooter_tile := _grid.tile_at(shooter.global_position)
	var target_tile := _grid.tile_at(target.global_position)
	var positions := firing_positions(shooter)
	var seen_at := target_tile
	var sighted: Variant = _sight_tile(shooter_tile, positions, target_tile, shooter.sight_range)
	if sighted == null and leans and _tile_distance(shooter_tile, target_tile) <= shooter.sight_range:
		var leans_out := lean_tiles(target)
		for position in positions:
			var lean: Variant = _nearest_in_sight(position, leans_out)
			if lean != null:
				sighted = position
				seen_at = lean
				break
	if sighted == null:
		return null

	var from: Vector3i = sighted
	var shot := Shot.new()
	shot.target = target
	shot.target_tile = target_tile
	shot.from = from
	shot.stepped_out = from != shooter_tile
	shot.seen_at = seen_at
	shot.leaning = seen_at != target_tile
	shot.cover = cover_against(target_tile, from)
	shot.flanked = shot.cover == Cover.NONE and not cover_at(target_tile).is_empty()
	shot.distance = _tile_distance(from, target_tile)
	return shot


## Every tile [param unit] could shoot someone standing on, as a set. This is
## the ground a unit on overwatch covers: a reaction's target is on the move,
## so where it could lean out to from there counts for nothing.
func watched_tiles(unit: Unit) -> Dictionary:
	var tile := _grid.tile_at(unit.global_position)
	var positions := firing_positions(unit)
	var watched := {}
	for target_tile in _grid.tiles():
		if target_tile == tile:
			continue
		if _sight_tile(tile, positions, target_tile, unit.sight_range) != null:
			watched[target_tile] = true
	return watched


## Every shot [param shooter] has at the living units in [param targets],
## nearest first.
func find_shots(shooter: Unit, targets: Array[Unit]) -> Array[Shot]:
	var shots: Array[Shot] = []
	for target in targets:
		if target.health <= 0:
			continue
		var shot: Variant = find_shot(shooter, target)
		if shot != null:
			shots.append(shot)
	shots.sort_custom(func(a: Shot, b: Shot) -> bool: return a.distance < b.distance)
	return shots


## The first of [param positions] with a clear sight line to someone on
## [param target_tile], or null if none has one. Out past [param sight_range]
## tiles from [param tile], where the unit stands, is out of sight however
## clear the line.
func _sight_tile(
	tile: Vector3i, positions: Array[Vector3i], target_tile: Vector3i, sight_range: int
) -> Variant:
	if _tile_distance(tile, target_tile) > sight_range:
		return null
	for from in positions:
		if _grid.is_line_clear(eye_cell(from), eye_cell(target_tile)):
			return from
	return null


## The nearest of [param tiles] to [param from] that it has a clear sight line
## to, or null if it has one to none of them.
func _nearest_in_sight(from: Vector3i, tiles: Array[Vector3i]) -> Variant:
	var nearest: Variant = null
	for tile in tiles:
		if not _grid.is_line_clear(eye_cell(from), eye_cell(tile)):
			continue
		if nearest == null or _tile_distance(from, tile) < _tile_distance(from, nearest as Vector3i):
			nearest = tile
	return nearest


## How far apart two tiles are across the ground, in tiles. Height is left
## out, the same way the grid treats a climb as one step like any other.
static func _tile_distance(a: Vector3i, b: Vector3i) -> float:
	return Vector2(a.x - b.x, a.z - b.z).length()
