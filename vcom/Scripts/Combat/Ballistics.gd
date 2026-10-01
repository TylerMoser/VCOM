## Where a shot's round goes, once the roll has said whether it lands: XCOM 2's
## rules, traced through the voxel grid.
##
## A hit flies along the sight line, eye to eye, so it never passes through
## anything the sight line did not. A miss is aimed at a point near the target
## and flies on until something solid stops it or it leaves the map. Most
## misses are aimed at a ring around the target's body, square to the line of
## fire. When the target has cover facing the shot, a share of them are aimed
## at that cover instead, which is how a missed shot chews up the wall an
## enemy is hiding behind. Either way it is the trace, not the aim point, that
## decides where the round stops.
##
## A miss must not read as something else, so every one keeps two rules. It
## never passes through a unit, friend or foe, and a stray round wounds nobody.
## The one exception is a unit standing in the line of fire itself, which any
## round passes through, since units never block sight. And a miss never
## stops on terrain well short of the target, which would look like a shot
## into the ground. An aim point that breaks either rule is drawn again.
##
## The path is worked out once, as the shot is fired, and nothing afterwards
## second-guesses it: the tracer draws it, and the terrain it ends on is the
## terrain that is struck.
class_name Ballistics
extends RefCounted

## Height above a unit's feet that misses are aimed around: the middle of its
## body.
const BODY_CENTER := CombatGrid.UNIT_HEIGHT * 0.5
## How far a unit's body is taken to reach out from its middle, for keeping
## stray rounds clear of it: the whole of its cell.
const BODY_RADIUS := 0.5
## The ring around the target that misses are aimed at, in cells. Its inside
## edge clears the body, so a miss never looks like it went through.
const MISS_RING_MIN := 0.55
const MISS_RING_MAX := 1.2
## The ring's outside edge for a target nearer than [constant CLOSE_RANGE]
## tiles, where a wide miss would fly off at a silly angle.
const MISS_RING_MAX_CLOSE := 0.8
const CLOSE_RANGE := 2.0
## How far round the ring from straight up a miss can be aimed, either way, in
## degrees. The wedge left out is straight down, through the target's legs.
const MISS_HALF_ANGLE := 150.0
## Share of misses aimed at the target's cover, when it has cover facing the
## shot. Misses aimed at the ring still strike that cover now and then.
const COVER_SHARE := 0.35
## How many aim points a miss may draw before it gives up on chance and works
## its way round the target instead. A miss aimed at the cover spends the
## first half on it.
const MISS_ATTEMPTS := 8
## The marks a miss works round the target through when no aim point it drew
## would do, in degrees from straight up, and how far each is nudged off its
## mark so the round does not run exactly along the grid.
const FALLBACK_ANGLES: Array[float] = [0.0, 45.0, -45.0, 90.0, -90.0, 135.0, -135.0]
const FALLBACK_JITTER := 10.0
## How far short of the target, in cells, a miss may stop on terrain.
const SHORT_OF_TARGET := 2.0
## How far a round flies at most, in cells: far enough to cross any map.
const MAX_FLIGHT := 100.0
## How far past the target, in cells, a round that strikes nothing is flown:
## on to the edge of the map, but at least the first, so it is seen to pass
## the target where the map ends right behind it, and at most the second, so
## a round sent skyward does not hold up the shot.
const FLY_PAST := 3.0
const FLY_PAST_MAX := 8.0
## How far in from the edges of a face of the cover a miss aimed at it is aimed,
## as a share of the face, so it strikes the face and not the corner between
## two.
const FACE_MARGIN := 0.1
## How far behind a face of the cover, in cells, a miss aimed at it is aimed.
## Just past the surface, so the round has come in through that face by the
## time it gets there.
const FACE_DEPTH := 0.001
## The six faces of a cell, as the way each looks out.
const FACES: Array[Vector3i] = [
	Vector3i.UP, Vector3i.DOWN, Vector3i.LEFT, Vector3i.RIGHT, Vector3i.FORWARD, Vector3i.BACK,
]


## The flight of one round: where it was fired from and where it stopped.
class Path:
	## The eye the round was fired from.
	var from: Vector3
	## Where the round stopped: in the target, on terrain, or where it left the
	## map.
	var to: Vector3
	## The terrain the round struck, or null if it stopped in the target or
	## flew off the map.
	var struck: CombatGrid.RayHit


## A shot once it is fired: whether it lands, and where its rounds went.
class Outcome:
	## Whether the roll said the shot lands.
	var hit: bool
	## What the target took once the round landed: the weapon's damage less
	## the target's [member Unit.defense]. 0 for a miss, and for a hit its
	## defense stopped. Filled in by [method Unit.shoot_at] on landing.
	var damage := 0
	## Where the shot's rounds went. There is one: as in XCOM 2, a single round
	## decides what a shot does. It is a list so that a weapon firing several
	## rounds a shot can have them.
	var paths: Array[Path] = []
	## Where the muzzle of the shooter's gun was as it fired, which is where the
	## tracers are drawn from; null without a figure holding a gun. Only for
	## show: every path is still flown from the shooter's eye.
	var muzzle: Variant = null


var _grid: CombatGrid
var _rng: RandomNumberGenerator


## Misses draw their aim points from [param rng]. Left out, it is a generator
## seeded from the global one, so that seeding the global generator replays a
## fight exactly, rolls and misses alike.
func _init(grid: CombatGrid, rng: RandomNumberGenerator = null) -> void:
	_grid = grid
	_rng = rng
	if _rng == null:
		_rng = RandomNumberGenerator.new()
		_rng.seed = randi()


## Where the rounds go when [param shooter] takes [param shot], which the roll
## has already said does or does not [param hit].
func fire(shooter: Unit, shot: LineOfSight.Shot, hit: bool) -> Outcome:
	var outcome := Outcome.new()
	outcome.hit = hit
	outcome.paths.append(path_for(shooter, shot, hit))
	return outcome


## The flight of a round [param shooter] fires at [param shot]'s target: into
## it along the sight line if the shot [param hit], somewhere near it if not.
func path_for(shooter: Unit, shot: LineOfSight.Shot, hit: bool) -> Path:
	var from := _grid.cell_center(LineOfSight.eye_cell(shot.from))
	# The target's eye wherever it actually stands: a reaction shot can catch
	# it between tiles.
	var offset := _grid.cell_center(LineOfSight.eye_cell(shot.target_tile)) - _grid.tile_position(shot.target_tile)
	var eye := shot.target.global_position + offset
	if not hit:
		return _miss(shooter, shot, from, eye)
	var path := Path.new()
	path.from = from
	path.to = eye
	return path


## A miss by [param shooter], fired from [param from] at a target whose eye is
## at [param eye]. See the class description for the rules it keeps.
func _miss(shooter: Unit, shot: LineOfSight.Shot, from: Vector3, eye: Vector3) -> Path:
	var body := shot.target.global_position + Vector3.UP * BODY_CENTER
	var others := _bystanders(shooter, shot.target, from, eye)
	# The ring's axes, square to the line of fire: up, as near as the line
	# allows, and across.
	var toward := from.direction_to(body)
	var up := Vector3.UP - toward * toward.dot(Vector3.UP)
	if up.is_zero_approx():
		up = toward.cross(Vector3.RIGHT)
	up = up.normalized()
	var across := toward.cross(up).normalized()
	var outer := MISS_RING_MAX_CLOSE if shot.distance < CLOSE_RANGE else MISS_RING_MAX

	var cover_faces := []
	if shot.cover != LineOfSight.Cover.NONE and _rng.randf() < COVER_SHARE:
		cover_faces = _cover_faces(shot, from)
	var cover_cells := {}
	for pick: Array in cover_faces:
		cover_cells[pick[0]] = true

	for attempt in MISS_ATTEMPTS:
		var at_cover := not cover_faces.is_empty() and attempt * 2 < MISS_ATTEMPTS
		var aim := _cover_point(cover_faces) if at_cover else _ring_point(body, up, across, outer)
		var path := _trace(from, aim, body)
		# Aimed at the cover, it has to be the cover that stops it.
		if at_cover and (path.struck == null or not cover_cells.has(path.struck.cell)):
			continue
		if _is_fair(path, body, others):
			return path

	# Nothing drawn would do, so the target must be hemmed in. Work round it
	# from over its head, further out each time round, and take the first fair
	# miss. Should none be, go over its head as high as that went.
	var farthest := outer
	for lift: float in [0.0, 1.0, 2.0, 4.0]:
		farthest = outer + lift
		for mark in FALLBACK_ANGLES:
			var angle := mark + _rng.randf_range(-FALLBACK_JITTER, FALLBACK_JITTER)
			var path := _trace(from, _around(body, up, across, angle, farthest), body)
			if _is_fair(path, body, others):
				return path
	var over := _rng.randf_range(-FALLBACK_JITTER, FALLBACK_JITTER)
	return _trace(from, _around(body, up, across, over, farthest), body)


## A round fired from [param from] through [param aim], at a target whose
## body is centred on [param body], flown until it strikes something or
## leaves the map.
func _trace(from: Vector3, aim: Vector3, body: Vector3) -> Path:
	var direction := from.direction_to(aim)
	var path := Path.new()
	path.from = from
	path.struck = _grid.cast(from, direction, MAX_FLIGHT)
	if path.struck != null:
		path.to = path.struck.point
	else:
		path.to = _fly_off(from, direction, from.distance_to(body))
	return path


## Whether [param path] is a fair miss at a target whose body is centred on
## [param body]: clear of everyone in [param others], the target included, and
## not stopped on terrain well short of it.
func _is_fair(path: Path, body: Vector3, others: Array[Unit]) -> bool:
	if path.struck != null and path.struck.distance < path.from.distance_to(body) - SHORT_OF_TARGET:
		return false
	for unit in others:
		if passes_through(unit, path.from, path.to):
			return false
	return true


## Whether the line from [param from] to [param to] passes through
## [param unit]'s body, taken as a capsule filling its two cells.
static func passes_through(unit: Unit, from: Vector3, to: Vector3) -> bool:
	var feet := unit.global_position
	var closest := Geometry3D.get_closest_points_between_segments(
		from,
		to,
		feet + Vector3.UP * BODY_RADIUS,
		feet + Vector3.UP * (CombatGrid.UNIT_HEIGHT - BODY_RADIUS),
	)
	return closest[0].distance_to(closest[1]) < BODY_RADIUS


## Where a round from [param from] heading [param direction], at a target
## [param target_distance] away, is last seen having struck nothing: where it
## passes the edge of the ground, however high it is by then, held to between
## [constant FLY_PAST] and [constant FLY_PAST_MAX] past the target.
func _fly_off(from: Vector3, direction: Vector3, target_distance: float) -> Vector3:
	var bounds := _grid.map_bounds()
	var distance := MAX_FLIGHT
	for axis: int in [Vector3.AXIS_X, Vector3.AXIS_Z]:
		if is_zero_approx(direction[axis]):
			continue
		var edge := bounds.end[axis] if direction[axis] > 0.0 else bounds.position[axis]
		distance = minf(distance, (edge - from[axis]) / direction[axis])
	distance = clampf(distance, target_distance + FLY_PAST, target_distance + FLY_PAST_MAX)
	return from + direction * distance


## A point drawn at random on the ring around [param body] that misses are
## aimed at, out to [param outer] cells. [param up] and [param across] are the
## ring's axes.
func _ring_point(body: Vector3, up: Vector3, across: Vector3, outer: float) -> Vector3:
	var angle := _rng.randf_range(-MISS_HALF_ANGLE, MISS_HALF_ANGLE)
	return _around(body, up, across, angle, _rng.randf_range(MISS_RING_MIN, outer))


## The point [param radius] cells from [param body], [param degrees] round
## from [param up] toward [param across].
static func _around(body: Vector3, up: Vector3, across: Vector3, degrees: float, radius: float) -> Vector3:
	var angle := deg_to_rad(degrees)
	return body + (up * cos(angle) + across * sin(angle)) * radius


## The faces of [param shot]'s target's cover that a round from [param from]
## could strike, as [code][cell, face][/code] pairs: every face open to the air
## and turned toward the shooter, of every solid cell beside the target on the
## shooter's side, up to the top of its body. That takes in the wall either
## side of the cover proper, which is what a shot along a wall meets first.
func _cover_faces(shot: LineOfSight.Shot, from: Vector3) -> Array:
	var faces := []
	var toward_shooter := Vector2i(shot.from.x - shot.target_tile.x, shot.from.z - shot.target_tile.z)
	for dx in [-1, 0, 1]:
		for dz in [-1, 0, 1]:
			if dx * toward_shooter.x + dz * toward_shooter.y <= 0:
				continue
			for height in CombatGrid.UNIT_HEIGHT:
				var cell := shot.target_tile + Vector3i(dx, height, dz)
				if not _grid.is_solid(cell):
					continue
				var center := _grid.cell_center(cell)
				for face in FACES:
					if _grid.is_solid(cell + face):
						continue
					var outward := _grid.cell_center(cell + face) - center
					if outward.dot(from - (center + outward * 0.5)) > 0.0:
						faces.append([cell, face])
	return faces


## A point just behind one of [param faces], picked at random, for a miss
## aimed at the cover to be aimed through.
func _cover_point(faces: Array) -> Vector3:
	var pick: Array = faces[_rng.randi_range(0, faces.size() - 1)]
	var cell: Vector3i = pick[0]
	var face: Vector3i = pick[1]
	var center := _grid.cell_center(cell)
	var outward := _grid.cell_center(cell + face) - center
	var point := center + outward * (0.5 - FACE_DEPTH)
	for axis in 3:
		if face[axis] != 0:
			continue
		var along := Vector3i.ZERO
		along[axis] = 1
		var half := (_grid.cell_center(cell + along) - center) * 0.5
		point += half * _rng.randf_range(-1.0, 1.0) * (1.0 - 2.0 * FACE_MARGIN)
	return point


## The units a miss by [param shooter] at [param target] must keep clear of:
## everyone but the shooter, less anyone standing in the line of fire from
## [param from] to the target's [param eye]. Any round passes through them,
## hit or miss, since units never block sight. The target is always kept
## clear of.
func _bystanders(shooter: Unit, target: Unit, from: Vector3, eye: Vector3) -> Array[Unit]:
	var units: Array[Unit] = []
	for node in _grid.get_tree().get_nodes_in_group(Unit.GROUP):
		var unit := node as Unit
		if unit == shooter or (unit != target and passes_through(unit, from, eye)):
			continue
		units.append(unit)
	return units
