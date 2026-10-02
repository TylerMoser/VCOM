## Blood, exaggerated as Fat Princess has it: what a hit does to the body it
## lands on, and to everything round it.
##
## A node in each combat map. Whenever a unit takes damage ([signal Unit.hurt])
## its figure is stained round where the hit landed
## ([method FigureVoxels.bleed]), for a round where its tracer was drawn to
## ([member Ballistics.Path.wound]), and blood sprays from there the way the
## blow was going: a round's mostly out of the far side of the body along its
## flight, from an exit wound, and a little back toward the gun; a blade's
## along its swing; a blast's away from where it went off, from wounds on the
## side facing it. The more damage, the more blood.
##
## Each drop is a voxel of blood flying under gravity, all of them drawn by one
## MultiMesh, and it stains the first voxel face it meets, whatever that
## belongs to: a block (traced voxel by voxel, [method CombatGrid.cast]), a
## crate's piece or a lump of debris (found by the physics, then traced through
## the piece's voxels), a figure, or the gear one carries.
## Coins are the exception: blood never touches them, and a drop flies through
## a coin as if it were not there. Where it lands it runs as blood would
## ([BloodFlow]): it pools on flat ground, runs over an edge and down the wall,
## fills the bottom of a crater. When a unit dies its figure breaks apart
## ([method TerrainDestruction.break_figure]), its stained voxels red in the
## lumps, and a moment later a pool spreads out over a few seconds on the
## ground where it stood.
##
## Stains are on the faces of voxels, and stay for the rest of the battle,
## going wherever their voxels go ([VoxelStains]). All of it is only for show:
## nothing in the rules reads blood, and it draws only on a random generator of
## its own, never the global one, so a seeded fight replays the same.
##
## The player can turn it off, to play clean ([member enabled]); a battle
## begun with it off has none at all.
class_name Blood
extends Node3D

## The most damage that counts toward how much a hit bleeds: a hit far beyond
## what any weapon does bleeds no more than this.
const MOST_DAMAGE := 10
## How many faces a hit stains on the body: so many, and so many more for each
## point of damage taken. An exit wound stains half as many.
const WOUND_FACES := 8
const WOUND_FACES_PER_DAMAGE := 4
## How many drops a hit sprays: so many, and so many more for each point of
## damage taken; and the most in flight at once.
const DROPS := 12
const DROPS_PER_DAMAGE := 8
const MOST_DROPS := 2000
## How many faces a drop stains where it lands, between these; how often one is
## a big drop, twice as wide; and how many a big one stains.
const DROP_FACES := Vector2i(3, 9)
const BIG_CHANCE := 0.2
const BIG_DROP_FACES := Vector2i(12, 24)
## How far round where a drop lands, in voxels, it splashes every way alike
## before it runs downhill ([member BloodFlow.splat]).
const LANDING_SPLAT := 1.5

## Of a round's drops, the share sprayed out of the far side of the body; the
## rest spray back toward the gun.
const EXIT_SHARE := 0.65
## How fast each kind of spray flies, in cells a second, between the two, and
## how widely it scatters, as a share of its speed: out of an exit wound; back
## out of the entry; along a blade's swing; away from a blast.
const EXIT_SPEED := Vector2(2.5, 6.0)
const EXIT_SCATTER := 0.35
const BACK_SPEED := Vector2(0.8, 2.5)
const BACK_SCATTER := 0.8
const SWEEP_SPEED := Vector2(2.0, 5.0)
const SWEEP_SCATTER := 0.5
const BLAST_SPEED := Vector2(2.0, 6.0)
const BLAST_SCATTER := 0.6
## How much a blade's spray follows its swing, and how much the way it struck.
const SWEEP_ALONG := 0.8
const SWEEP_ON := 0.4
## How much faster upward every drop sets off, between the two, in cells a
## second.
const LIFT := Vector2(0.0, 1.5)
## How many wounds a blast leaves, at least and at most: one more for every
## three points of damage.
const BLAST_WOUNDS := Vector2i(2, 4)
## Seconds a drop passes through the body it came out of, so it clears the body
## before it can land back on it.
const CLEAR_SECONDS := 0.06

## What pulls a drop down, in cells a second a second.
const GRAVITY := 9.8
## How far below the bottom of the map a drop falls before it is forgotten.
const FALL_LIMIT := 4.0
## How high a figure's middle is off its feet, and how far round it a drop is
## traced against its voxels.
const FIGURE_MIDDLE := 0.85
const FIGURE_REACH := 1.2
## The most pieces of debris one step of a drop looks through for one that
## wears away: the rest it passes.
const DEBRIS_TRIES := 4
## The most time a physics step gives to staining where drops have landed and
## wounds been made, in microseconds; what is left waits for the next. A stain
## a frame or two late is not seen, and a burst of drops landing together is
## not a hitch.
const SPLASH_BUDGET := 2000

## How many faces the pool where a unit died stains, and over how many seconds
## it spreads; and how many seconds after it died it starts, once the lumps its
## figure broke into have mostly landed.
const DEATH_FACES := 800
const DEATH_SECONDS := 3.0
const POOL_DELAY := 1.0
## How far up from where the unit stood the line down to the ground under it
## starts, and how far it looks, in cells.
const POOL_ABOVE := 0.25
const POOL_BELOW := 3.0

const FACES := VoxelStains.FACES

## Whether there is blood at all. Off, battles are fought clean: no wounds,
## drops, stains or pools, on anything. Set from the pause menu's System tab
## ([SystemTab]), which only lets it change between battles, on the world map;
## each combat map reads it once, as it loads, so a battle keeps what it began
## with. Kept here, as [member TileGrid.shown] is, so it holds from battle to
## battle until the game closes; nothing saves it.
static var enabled := true

@export_group("Nodes")
@export var grid_path: NodePath = ^"../CombatGrid"
@export var destruction_path: NodePath = ^"../TerrainDestruction"

var _grid: CombatGrid
var _destruction: TerrainDestruction
var _terrain: BloodFlow.TerrainSurface
## Everything here draws on this, so the global generator is left alone.
var _rng := RandomNumberGenerator.new()

## The drops in flight: where each is, how fast it is going, how many voxels
## across it is, how many faces it will stain, and the figure it came out of,
## which it passes through for the seconds left of [constant CLEAR_SECONDS].
var _positions := PackedVector3Array()
var _velocities := PackedVector3Array()
var _sizes := PackedFloat32Array()
var _volumes := PackedInt32Array()
var _through: Array[FigureVoxels] = []
var _through_for := PackedFloat32Array()
var _drawn: MultiMesh
var _ray := PhysicsRayQueryParameters3D.new()

## Where drops have landed and wounds been made, not yet stained, first first.
var _landings: Array[Landing] = []
## Where each of the dead stood, waiting for its pool, as
## [code][where its feet were, seconds since it died][/code].
var _fallen: Array = []
## The pools spreading there, each as [code][flow, seconds spreading][/code].
var _pools: Array = []


## What a drop meets first on its way, and how far along it is: a block, a
## figure, a loose voxel model, or a lump of debris; or a wound. And how many
## faces the blood there stains.
class Landing:
	var distance := INF
	var volume := 0
	var block: CombatGrid.RayHit
	var figure: FigureVoxels
	var on_figure: FigureVoxels.Hit
	var model: VoxelBody
	## For a loose model: the voxel and face met, counted in its shape.
	var voxel := Vector3i.ZERO
	var face := 0
	## For a lump: its body, and where it was met.
	var lump := RID()
	var point := Vector3.ZERO


func _ready() -> void:
	_grid = get_node_or_null(grid_path) as CombatGrid
	_destruction = get_node_or_null(destruction_path) as TerrainDestruction
	if _grid == null or _destruction == null or _destruction.voxels == null:
		push_error("Blood: missing CombatGrid or TerrainDestruction, so no blood.")
		set_process(false)
		set_physics_process(false)
		return
	# Every figure's voxels are read now, as the map loads, rather than on the
	# first hit, which would catch on them: about 10 ms for the base figure,
	# more for its gear. Even with no blood, as a shot still uses them to draw
	# its tracer on to the body ([method CharacterModel.pick_wound]).
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		var unit := node as Unit
		var figure: FigureVoxels = unit.model.voxels() if unit.model != null else null
		if figure != null:
			figure.prepare()
	if not enabled:
		set_process(false)
		set_physics_process(false)
		return
	_rng.randomize()
	var map := _destruction.get_node_or_null(_destruction.grid_map_path) as GridMap
	var map_frame := map.global_transform if map != null else Transform3D.IDENTITY
	var cell_size := map.cell_size if map != null else Vector3.ONE
	_terrain = BloodFlow.TerrainSurface.new(_destruction.voxels, map_frame, cell_size)
	_ray.collision_mask = TerrainDestruction.DEBRIS_LAYER
	_ray.collide_with_areas = false
	_make_drops()
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		var unit := node as Unit
		unit.hurt.connect(_on_hurt.bind(unit))
		unit.died.connect(_on_died.bind(unit))


func _process(delta: float) -> void:
	_watch_the_fallen(delta)
	_spread_pools(delta)


func _physics_process(delta: float) -> void:
	if not _positions.is_empty():
		_fly(delta)
	_settle()


## Moves every drop on by [param delta] seconds, and lands each that meets
## something on the way.
func _fly(delta: float) -> void:
	var figures := _figures()
	var debris := get_tree().get_node_count_in_group(TerrainDestruction.PIECES) > 0 or _destruction.voxel_debris.count() > 0
	var lowest := _grid.map_bounds().position.y - FALL_LIMIT
	# Backward, so a drop taken out swaps in one already moved.
	var drop := _positions.size() - 1
	while drop >= 0:
		var from := _positions[drop]
		var velocity := _velocities[drop]
		var next_velocity := velocity + Vector3.DOWN * GRAVITY * delta
		var to := from + (velocity + next_velocity) * 0.5 * delta
		_through_for[drop] -= delta
		var through: FigureVoxels = _through[drop] if _through_for[drop] > 0.0 else null
		var landing := _first_met(from, to, figures, through, debris)
		if landing != null:
			landing.volume = _volumes[drop]
			_landings.append(landing)
			_remove(drop)
		elif to.y < lowest:
			_remove(drop)
		else:
			_positions[drop] = to
			_velocities[drop] = next_velocity
		drop -= 1
	_draw_drops()


## Stains where drops have landed and wounds been made, first first, for as
## long as [constant SPLASH_BUDGET] allows, and at least one.
func _settle() -> void:
	var start := Time.get_ticks_usec()
	var done := 0
	while done < _landings.size():
		_splash(_landings[done])
		done += 1
		if Time.get_ticks_usec() - start > SPLASH_BUDGET:
			break
	_landings = _landings.slice(done)


## How many drops are in flight, or have landed and not yet stained.
func drops_in_flight() -> int:
	return _positions.size() + _landings.size()


## How many of the dead are waiting for their pool, or have one still
## spreading.
func pools_to_come() -> int:
	return _fallen.size() + _pools.size()


## Wounds [param unit], which has just taken [param taken] damage from a hit as
## [signal Unit.hurt] says, and sprays its blood. A hit that kills it wounds it
## at once rather than in its turn, as its figure is about to break apart
## ([method TerrainDestruction.break_figure]) and carry the stain into its
## lumps.
@warning_ignore("integer_division")
func _on_hurt(taken: int, from: Vector3, at: Vector3, blasted: bool, sweep: Vector3, unit: Unit) -> void:
	var killing := taken >= unit.health
	taken = mini(taken, MOST_DAMAGE)
	var faces := WOUND_FACES + taken * WOUND_FACES_PER_DAMAGE
	var drops := DROPS + taken * DROPS_PER_DAMAGE
	var middle := unit.global_position + Vector3.UP * FIGURE_MIDDLE
	if not from.is_finite():
		from = middle + Vector3.FORWARD
	var figure: FigureVoxels = unit.model.voxels() if unit.model != null else null
	if figure == null:
		_spray(middle, middle - from, drops, EXIT_SPEED, EXIT_SCATTER, null)
		return
	if blasted:
		_blast_wounds(figure, from, faces, drops, clampi(1 + taken / 3, BLAST_WOUNDS.x, BLAST_WOUNDS.y), middle, killing)
		return
	var hit: FigureVoxels.Hit = figure.hit_near(at, from, _rng) if at.is_finite() else figure.pick_wound(from, _rng)
	if hit == null:
		_spray(middle, middle - from, drops, EXIT_SPEED, EXIT_SCATTER, figure)
		return
	_wound(figure, hit, faces, killing)
	var heading := (hit.point - from).normalized()
	if not sweep.is_zero_approx():
		_spray(hit.point, sweep.normalized() * SWEEP_ALONG + heading * SWEEP_ON, drops, SWEEP_SPEED, SWEEP_SCATTER, figure)
		return
	# Through and through: out of the far side, along the round's flight.
	var exit := figure.exit(hit.point, heading)
	var exit_point := hit.point + heading * VoxelShape.SCALE
	if exit != null:
		exit_point = exit.point
		_wound(figure, exit, faces / 2, killing)
	var forward := roundi(drops * EXIT_SHARE)
	_spray(exit_point, heading, forward, EXIT_SPEED, EXIT_SCATTER, figure)
	_spray(hit.point, -heading, drops - forward, BACK_SPEED, BACK_SCATTER, figure)


## Wounds [param figure] [param wounds] times on the side facing a blast at
## [param from], sharing [param faces] and [param drops] out between them, each
## spraying away from it; at once if [param now].
@warning_ignore("integer_division")
func _blast_wounds(figure: FigureVoxels, from: Vector3, faces: int, drops: int, wounds: int, middle: Vector3, now := false) -> void:
	var sprayed := 0
	for wound in wounds:
		var hit := figure.pick_wound(from, _rng)
		if hit == null:
			continue
		_wound(figure, hit, maxi(faces / wounds, 1), now)
		var away := hit.point - from
		away.y = maxf(away.y, 0.0)
		_spray(hit.point, away.normalized() + Vector3.UP * 0.4, drops / wounds, BLAST_SPEED, BLAST_SCATTER, figure)
		sprayed += 1
	if sprayed == 0:
		# A blast right at its feet: blood every way, from the middle.
		_spray(middle, Vector3.UP, drops, BLAST_SPEED, 1.0, figure)


## Stains [param faces] faces of [param figure] round [param hit], with the
## landings, so it waits its turn as they do; or at once if [param now].
func _wound(figure: FigureVoxels, hit: FigureVoxels.Hit, faces: int, now := false) -> void:
	if now:
		figure.bleed(hit, faces, _rng)
		return
	var landing := Landing.new()
	landing.figure = figure
	landing.on_figure = hit
	landing.volume = faces
	_landings.append(landing)


## Notes where [param unit] stood as it dies, to pool blood there once its
## figure has broken apart and the lumps have mostly landed.
func _on_died(unit: Unit) -> void:
	_fallen.append([unit.global_position, 0.0])


## Sprays [param count] drops from [param origin] along [param heading], each
## at a speed drawn from [param speed], scattered by [param scatter] of it and
## lifted a little, passing through [param through] until they are clear of it.
func _spray(origin: Vector3, heading: Vector3, count: int, speed: Vector2, scatter: float, through: FigureVoxels) -> void:
	var toward := heading.normalized() if not heading.is_zero_approx() else Vector3.UP
	for drop in count:
		if _positions.size() >= MOST_DROPS:
			return
		var velocity := (toward + _random_in_ball() * scatter).normalized() * _rng.randf_range(speed.x, speed.y)
		velocity += Vector3.UP * _rng.randf_range(LIFT.x, LIFT.y)
		var big := _rng.randf() < BIG_CHANCE
		_positions.append(origin + _random_in_ball() * VoxelShape.SCALE)
		_velocities.append(velocity)
		_sizes.append(2.0 if big else 1.0)
		_volumes.append(_rng.randi_range(BIG_DROP_FACES.x, BIG_DROP_FACES.y) if big else _rng.randi_range(DROP_FACES.x, DROP_FACES.y))
		_through.append(through)
		_through_for.append(CLEAR_SECONDS)


## What a drop flying from [param from] to [param to] meets first, if anything:
## the terrain, any of [param figures] but [param through], or the debris if
## there is any ([param debris]). Coins are never looked for: blood passes them
## by.
func _first_met(from: Vector3, to: Vector3, figures: Array, through: FigureVoxels, debris: bool) -> Landing:
	var length := from.distance_to(to)
	if length <= 0.0:
		return null
	var heading := (to - from) / length
	var landing: Landing = null
	var reach := length
	var block: Variant = _grid.cast(from, heading, reach, true, true)
	if block != null:
		landing = Landing.new()
		landing.block = block
		landing.distance = (block as CombatGrid.RayHit).distance
		reach = landing.distance
	for entry: Array in figures:
		var figure: FigureVoxels = entry[0]
		if figure == through or not _passes_near(from, heading, reach, entry[1], entry[2]):
			continue
		var hit := figure.march(from, heading, reach)
		if hit != null:
			landing = Landing.new()
			landing.figure = figure
			landing.on_figure = hit
			landing.distance = hit.distance
			reach = hit.distance
	if debris:
		var met := _debris_met(from, heading, reach)
		if met != null:
			landing = met
	return landing


## The first piece of debris a drop going from [param from] along
## [param heading] meets within [param reach]: a lump, or a loose voxel model
## where the line meets one of its voxels, such as the gear a figure dropped
## as it broke apart. Pieces that do not wear away and blocks falling whole are
## passed.
func _debris_met(from: Vector3, heading: Vector3, reach: float) -> Landing:
	_ray.from = from
	_ray.to = from + heading * reach
	var passed: Array[RID] = []
	var space := get_world_3d().direct_space_state
	for attempt in DEBRIS_TRIES:
		_ray.exclude = passed
		var met := space.intersect_ray(_ray)
		if met.is_empty():
			return null
		var body: Object = met.collider
		var rid: RID = met.rid
		if body == null:
			# Lumps are made on the physics server, and have no node.
			var landing := Landing.new()
			landing.lump = rid
			landing.point = met.position
			landing.distance = from.distance_to(met.position)
			return landing
		if body is RigidBody3D and not body is FallingBlock:
			var model := _destruction.voxels.model_of(body)
			if model != null:
				var hit := VoxelTerrain.march(model.shape, model.voxels, model.frame(), from, heading, reach)
				if hit != null and hit.face != Vector3i.ZERO:
					var landing := Landing.new()
					landing.model = model
					landing.voxel = model.shape.voxel_at(hit.index)
					landing.face = FACES.find(hit.face)
					landing.distance = hit.distance
					return landing
		passed.append(rid)
	return null


## Stains what [param landing] met, and lets the blood run. What it met may
## have gone since, or worn: the flow only stains faces still there.
func _splash(landing: Landing) -> void:
	var volume := landing.volume
	if landing.block != null:
		var hit := landing.block
		if hit.index < 0 or hit.face == Vector3i.ZERO:
			return
		var start := _terrain.voxel_of(hit.cell, hit.index)
		BloodFlow.new(_terrain, start, FACES.find(hit.face), volume, _rng, LANDING_SPLAT).spread(volume)
	elif landing.figure != null:
		if landing.figure.is_valid():
			landing.figure.bleed(landing.on_figure, volume, _rng)
	elif landing.model != null:
		if not is_instance_valid(landing.model):
			return
		var model := landing.model
		var surface := BloodFlow.ModelSurface.new(model.stained(), model.voxels, model.frame())
		BloodFlow.new(surface, landing.voxel, landing.face, volume, _rng, LANDING_SPLAT).spread(volume)
	elif landing.lump.is_valid():
		_destruction.voxel_debris.stain(landing.lump, landing.point)


## Starts a pool where each of the dead stood, [constant POOL_DELAY] after it
## died.
func _watch_the_fallen(delta: float) -> void:
	for place in range(_fallen.size() - 1, -1, -1):
		var entry: Array = _fallen[place]
		entry[1] += delta
		if entry[1] < POOL_DELAY:
			continue
		_fallen.remove_at(place)
		_start_pool(entry[0])


## Starts blood pooling out on the ground under [param stood], where a unit's
## feet were as it died: on its tile, or below if it died falling.
func _start_pool(stood: Vector3) -> void:
	var met: Variant = _grid.cast(stood + Vector3.UP * POOL_ABOVE, Vector3.DOWN, POOL_ABOVE + POOL_BELOW, true, true)
	if met == null:
		return
	var hit := met as CombatGrid.RayHit
	if hit.index < 0 or hit.face == Vector3i.ZERO:
		return
	var flow := BloodFlow.new(_terrain, _terrain.voxel_of(hit.cell, hit.index), FACES.find(hit.face), DEATH_FACES, _rng)
	_pools.append([flow, 0.0])


## Spreads each pool under a body a little further: quickly at first, slowing
## as it reaches its size.
func _spread_pools(delta: float) -> void:
	for place in range(_pools.size() - 1, -1, -1):
		var entry: Array = _pools[place]
		var flow: BloodFlow = entry[0]
		var seconds: float = entry[1] + delta
		entry[1] = seconds
		var share := 1.0 - pow(1.0 - minf(seconds / DEATH_SECONDS, 1.0), 2.0)
		var due := roundi(DEATH_FACES * share) - flow.stained
		if due > 0:
			flow.spread(due)
		if seconds >= DEATH_SECONDS or flow.is_done():
			_pools.remove_at(place)


## Every figure a drop might meet, as [code][voxels, middle, reach][/code]: a
## drop passing further than reach from its middle is not traced against it. A
## unit's that has died has broken apart, and its lumps are debris.
func _figures() -> Array:
	var found := []
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		var unit := node as Unit
		if unit == null or unit.model == null:
			continue
		var figure := unit.model.voxels()
		if figure != null:
			found.append([figure, unit.global_position + Vector3.UP * FIGURE_MIDDLE, FIGURE_REACH])
	return found


## Whether a line from [param from] along [param heading], [param length]
## long, passes within [param radius] of [param point].
static func _passes_near(from: Vector3, heading: Vector3, length: float, point: Vector3, radius: float) -> bool:
	var along := clampf((point - from).dot(heading), 0.0, length)
	return (from + heading * along).distance_squared_to(point) <= radius * radius


func _remove(drop: int) -> void:
	var last := _positions.size() - 1
	if drop != last:
		_positions[drop] = _positions[last]
		_velocities[drop] = _velocities[last]
		_sizes[drop] = _sizes[last]
		_volumes[drop] = _volumes[last]
		_through[drop] = _through[last]
		_through_for[drop] = _through_for[last]
	_positions.resize(last)
	_velocities.resize(last)
	_sizes.resize(last)
	_volumes.resize(last)
	_through.resize(last)
	_through_for.resize(last)


func _make_drops() -> void:
	var cube := BoxMesh.new()
	cube.size = Vector3.ONE * VoxelShape.SCALE
	cube.material = VoxelStains.material
	_drawn = MultiMesh.new()
	_drawn.transform_format = MultiMesh.TRANSFORM_3D
	_drawn.mesh = cube
	_drawn.instance_count = MOST_DROPS
	_drawn.visible_instance_count = 0
	var drawn := MultiMeshInstance3D.new()
	drawn.name = &"Drops"
	drawn.multimesh = _drawn
	drawn.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	# Never culled, so it never works out its bounds as the drops move.
	drawn.custom_aabb = AABB(-Vector3.ONE * VoxelDebris.REACH, Vector3.ONE * VoxelDebris.REACH * 2.0)
	add_child(drawn)


func _draw_drops() -> void:
	var count := _positions.size()
	for drop in count:
		_drawn.set_instance_transform(drop, Transform3D(Basis.from_scale(Vector3.ONE * _sizes[drop]), _positions[drop]))
	_drawn.visible_instance_count = count


## A point drawn at random from the ball of radius one.
func _random_in_ball() -> Vector3:
	var point := Vector3(_rng.randf_range(-1.0, 1.0), _rng.randf_range(-1.0, 1.0), _rng.randf_range(-1.0, 1.0))
	while point.length_squared() > 1.0:
		point = Vector3(_rng.randf_range(-1.0, 1.0), _rng.randf_range(-1.0, 1.0), _rng.randf_range(-1.0, 1.0))
	return point
