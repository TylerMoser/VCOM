## The voxels of everything on the map that wears away ([VoxelDestruction]):
## the pieces of the level, worn as one grid of voxels in its [VoxelVolume],
## and the voxel models loose in the world ([VoxelBody]). It wears them: a
## round's bite ([method chip], [method tear]), a blast's crater
## ([method crater]), or a piece breaking up whole ([method take_piece],
## [method crumble]). [TerrainDestruction] makes it and says when.
##
## The level's voxels are one grid, whatever the cells and chunks they are
## kept in, so a bite or a crater is one round shape across however many
## pieces and chunks it reaches, and what it cuts loose is found across them
## too: a lump hanging off one piece, held only by another that is itself cut
## off, drops with it. The level draws what is left as it wears
## ([LevelRenderer]), a bite at once and a blast's craters over the next few
## frames; the voxels themselves, and so the rules, have changed at once.
##
## To the rules a piece is whole until it is worn past standing: less than its
## destruction's [member VoxelDestruction.collapse_below] of its voxels left,
## or, holding something up, nothing joining its bottom to its top any more,
## as a tree's trunk shot through ([method holds_up]). Then [TerrainDestruction]
## breaks it, out of the rules at once, and what is left of it crumbles; the
## edges of the hole it leaves are worn a little into the pieces round it
## ([method roughen_hole]), so a broken block leaves a ragged hole, not a
## clean cube. The level's bottom layer never breaks, and is only ever worn
## [constant FLOOR_DEPTH] voxels deep, since a unit stands on the top of its
## tile whatever is under its feet.
##
## Rounds are traced through the voxels by the grid itself
## ([method CombatGrid.cast]); this only wears what they strike.
##
## A loose model - one of a crate's pieces once the crate has broken, or any
## rigid body drawn by a MagicaVoxel model taken on with
## [method take_on_body] - wears the same way, but is only for show, as all
## debris is: a round tears through it, taking a bite where it goes in, and
## flies on ([method tear]), and a blast craters it as it craters the level.
## Once part of it is cut off from the rest, that part flies on as a model of
## its own if it has [constant SMALLEST_PART] voxels or more, and crumbles
## into lumps if not; one worn past its share crumbles whole. A crate's pieces
## are only taken on the first time a round or a blast reaches them
## ([method take_on_later]): most never are, and taking one on costs more than
## making it.
##
## Which voxels of the level go is decided by the global random generator -
## one number for each round, blast or broken piece - so seeding it replays a
## fight exactly, which pieces break included. Everything else here is only
## for show and draws on a generator of its own, so how much debris there is,
## or what a round tears through on its way, never changes what the rules draw
## next.
##
## Blood recolours voxels themselves ([Blood]), the level's and every loose
## model's ([VoxelModel]), so wherever a voxel goes, its colour goes: a lump
## broken off a bloodied voxel is blood red, and a part cut off a model keeps
## its blood. A crate breaking hands its blood on to its pieces voxel by voxel
## ([method carry_blood]), since its pieces are models of their own.
class_name VoxelTerrain
extends Node3D

const VOXEL := VoxelShape.SCALE
const HALF := Vector3(0.5, 0.5, 0.5)
## How deep, in voxels from its top, the level's bottom layer can be worn. Its
## tiles' floor stays at the top of the layer, where a unit stands, so a deep
## crater would leave the unit standing on air.
const FLOOR_DEPTH := 4
## How far from where a round strikes the voxels it breaks off can be, as many
## times as far as its bite would reach into a solid block, and never further
## than [constant BITE_REACH] cells: a round striking a thin trunk takes a
## slice of it, not the whole trunk from top to bottom.
const BITE_SPREAD := 2.0
const BITE_REACH := 0.5
## How far round its edge a bite or a crater wanders in and out, as a share of
## its size, and how many bumps it has across its size: so it is not a perfect
## ball.
const ROUGHNESS := 0.2
const BUMPS := 2.5
## How many voxels across, at most, the lumps a round or a blast breaks off
## are, and the most lumps a blast throws about. The rest of what a blast
## breaks off is blown to dust, or there would be thousands; which are thrown
## is chosen before any is made ([Batch]), since making a lump costs three
## times what working out which voxels it holds does.
const DEBRIS_CLUMP := 2
const CRATER_DEBRIS := 150
## The fewest voxels a part cut off a loose model can have and fly on as a
## model of its own; and the most loose models a round tears through.
const SMALLEST_PART := 8
const MOST_TORN := 8
## How many voxels a search for what a voxel holds on to looks through before
## it takes the voxel to be held: a quarter of a block. Anything bigger cut off
## is a piece, or part of one, that the rules bring down whole, as a tree's
## crown falls with its trunk shot through.
const HOLD_SEARCH := 1024
## How far into the pieces round it, in voxels, the edges of the hole a
## breaking piece leaves are worn, and how far that wanders in and out, so
## the hole is ragged rather than a clean cube; and how close together the
## wanderings are, in cells.
const RIM_DEPTH := 1.5
const RIM_WANDER := 1.2
const RIM_BUMPS := 4.0

## How fast a voxel a round breaks off flies out of the face it struck, in cells
## a second, between these; how much it scatters about that; how much it is
## carried on the way the round was going; and how fast it tumbles, in radians
## a second.
const CHIP_SPEED_MIN := 1.0
const CHIP_SPEED_MAX := 2.5
const CHIP_SCATTER := 0.8
const CHIP_CARRY := 0.5
const CHIP_SPIN := 15.0
## How fast a piece a blast breaks off flies away from where it goes off, in
## cells a second, and how much faster upward: this much for one right where
## it goes off, and [constant CRATER_FAR_SHARE] of it for one at the crater's
## edge. And how much it scatters about that. The blast's push
## ([method VoxelDebris.burst]) is added to it.
const CRATER_SPEED := 4.0
const CRATER_LIFT := 4.5
const CRATER_FAR_SHARE := 0.4
const CRATER_SCATTER := 1.0
## How much a voxel cut loose from everything scatters as it drops away.
const LOOSE_SCATTER := 0.3
## How much the pieces a block crumbles into scatter and tumble; how hard the
## round that broke it knocks the piece nearest where it struck on along its
## flight, in cells a second; and how far from there the knock reaches, in
## cells.
const CRUMBLE_SCATTER := 0.6
const CRUMBLE_SPIN := 4.0
const CRUMBLE_PUSH := 1.5
const CRUMBLE_REACH := 1.0


## What wearing the level did: whether any voxel went, the pieces now worn
## past standing, which must break, by index, and the box, in the world, round
## every voxel that went.
class Wear:
	var worn := false
	var broken := PackedInt32Array()
	var box := AABB()


## Voxels of the level found near a point, as places in its grid, three
## numbers each, and how near each is, roughened, as a score.
class Found:
	var voxels := PackedInt32Array()
	var scores := PackedFloat32Array()

	func add(at: Vector3i, score: float) -> void:
		voxels.append(at.x)
		voxels.append(at.y)
		voxels.append(at.z)
		scores.append(score)

	func voxel(pick: int) -> Vector3i:
		return Vector3i(voxels[pick * 3], voxels[pick * 3 + 1], voxels[pick * 3 + 2])

	## The [param count] voxels scoring least, by place in the lists.
	func least(count: int) -> PackedInt32Array:
		var picks := PackedInt32Array()
		if scores.is_empty() or count <= 0:
			return picks
		var sorted := scores.duplicate()
		sorted.sort()
		var limit := sorted[mini(count, sorted.size()) - 1]
		for index in scores.size():
			if scores[index] <= limit and picks.size() < count:
				picks.append(index)
		return picks

	## Every voxel scoring under [param limit], by place in the lists.
	func under(limit: float) -> PackedInt32Array:
		var picks := PackedInt32Array()
		for index in scores.size():
			if scores[index] < limit:
				picks.append(index)
		return picks


## Voxels of one loose model found near a point: where each is in the model's
## array, and how near it is, roughened, as a score.
class ModelFound:
	var owners := PackedInt32Array()
	var indices := PackedInt32Array()
	var scores := PackedFloat32Array()

	func least(count: int) -> PackedInt32Array:
		var picks := PackedInt32Array()
		if scores.is_empty() or count <= 0:
			return picks
		var sorted := scores.duplicate()
		sorted.sort()
		var limit := sorted[mini(count, sorted.size()) - 1]
		for index in scores.size():
			if scores[index] <= limit and picks.size() < count:
				picks.append(index)
		return picks

	func under(limit: float) -> PackedInt32Array:
		var picks := PackedInt32Array()
		for index in scores.size():
			if scores[index] < limit:
				picks.append(index)
		return picks

	func voxels_at(picks: PackedInt32Array) -> PackedInt32Array:
		var found := PackedInt32Array()
		for pick in picks:
			found.append(indices[pick])
		return found


## What a piece left of itself as it went from the level: each voxel, by its
## place in the grid, three numbers each, and the place of its colour in the
## level's palette.
class Taken:
	var voxels := PackedInt32Array()
	var places := PackedByteArray()

	func size() -> int:
		return places.size()

	func voxel(index: int) -> Vector3i:
		return Vector3i(voxels[index * 3], voxels[index * 3 + 1], voxels[index * 3 + 2])


## Where a ray first meets a voxel of a model: the point, in the world; the
## face of the voxel it came in through, in the model's frame and as the way it
## looks out in the world, none if the ray started inside; the voxel's place in
## the model's array; and how far the ray went.
class Met:
	var point := Vector3.ZERO
	var face := Vector3i.ZERO
	var normal := Vector3.ZERO
	var index := -1
	var distance := 0.0


## Voxels broken off in one go, grouped into lumps but not made yet: what
## breaks them, how a lump of them sets off once made, and the lumps, each as
## the places of its voxels in the batch. A blast breaks off far more lumps
## than are ever made ([method _scatter]).
class Batch:
	var destruction: VoxelDestruction
	## Sets a lump moving: called with the [VoxelDebris.Piece], standing where
	## it broke off.
	var motion: Callable
	var clumps: Array = []

	## The lump of the voxels at [param clump], places in the batch, standing
	## where they broke off and set moving.
	func make(_clump: Array) -> VoxelDebris.Piece:
		return null


## Voxels broken off one loose model: its kind, frame and palette, and which
## voxels, with the place of the colour each held: blood's, for a voxel blood
## recoloured.
class ShapeBatch extends Batch:
	var shape: VoxelShape
	var frame: Transform3D
	var palette: PackedColorArray
	var indices: PackedInt32Array
	var held: PackedByteArray

	func make(clump: Array) -> VoxelDebris.Piece:
		var least := Vector3i.MAX
		var most := Vector3i.MIN
		for place: int in clump:
			var at := shape.voxel_at(indices[place])
			least = least.min(at)
			most = most.max(at)
		var middle := shape.corner + (Vector3(least) + Vector3(most + Vector3i.ONE)) * 0.5 * VOXEL
		var piece := VoxelDebris.Piece.new()
		# A body cannot be scaled, so a lump of a model grown a shade (a prop) is
		# turned as it was but drawn a block's voxels across.
		piece.transform = Transform3D(frame.basis.orthonormalized(), frame * middle)
		piece.size = Vector3(most - least + Vector3i.ONE) * VOXEL
		piece.voxels = PackedVector3Array()
		piece.colors = PackedColorArray()
		for place: int in clump:
			piece.voxels.append(shape.center_of(indices[place]) - middle)
			piece.colors.append(palette[held[place]])
		motion.call(piece)
		return piece


## Voxels broken off the level, or off a piece that fell from it: each by its
## place, counted in voxels in [member frame], which takes a voxel's place to
## the world, and its colour.
class VolumeBatch extends Batch:
	var frame: Transform3D
	var voxels := PackedInt32Array()
	var colors := PackedColorArray()

	func add(at: Vector3i, color: Color) -> void:
		voxels.append(at.x)
		voxels.append(at.y)
		voxels.append(at.z)
		colors.append(color)

	func voxel(place: int) -> Vector3i:
		return Vector3i(voxels[place * 3], voxels[place * 3 + 1], voxels[place * 3 + 2])

	func make(clump: Array) -> VoxelDebris.Piece:
		var least := Vector3i.MAX
		var most := Vector3i.MIN
		for place: int in clump:
			var at := voxel(place)
			least = least.min(at)
			most = most.max(at)
		var middle := (Vector3(least) + Vector3(most + Vector3i.ONE)) * 0.5
		var piece := VoxelDebris.Piece.new()
		var basis := frame.basis.orthonormalized()
		var across := frame.basis.get_scale().x
		piece.transform = Transform3D(basis, frame * middle)
		piece.size = Vector3(most - least + Vector3i.ONE) * across
		piece.voxels = PackedVector3Array()
		piece.colors = PackedColorArray()
		for place: int in clump:
			piece.voxels.append((Vector3(voxel(place)) + HALF - middle) * across)
			piece.colors.append(colors[place])
		motion.call(piece)
		return piece


## A piece waiting to wear away until a round or a blast first reaches it
## ([method take_on_later]): how it wears, the .vox its model is read from,
## and the bodies it passes through.
class Wearable:
	var destruction: VoxelDestruction
	var source := ""
	var passes: Array = []


var _grid: CombatGrid
var _level: VoxelLevel
var _volume: VoxelVolume
var _rules: LevelRules
var _debris: VoxelDebris
## Voxels lower than this in the level's grid are never worn: the bottom
## layer's, below [constant FLOOR_DEPTH] of its top.
var _floor_limit := 0
## The top of the bottom layer, in voxels.
var _floor_top := 0
## How each of the level's kinds wears away, by its place in the level's
## kinds; null for one that does not.
var _kind_wear: Array[VoxelDestruction] = []
## What a voxel of a piece that does not wear away breaks off as, cut loose.
var _fallback := VoxelDestruction.new()
## Every loose model, by its body, and every piece waiting to be taken on as
## one, by its body.
var _loose := {}
var _wearable := {}
## What roughens bites and craters, reseeded for each.
var _noise := FastNoiseLite.new()
var _bump_scale := 1.0
var _bump_size := 0.0
## What everything only for show draws on, so the global generator, which the
## rules draw on, is left alone.
var _show := RandomNumberGenerator.new()


func _init(grid: CombatGrid, level: VoxelLevel, debris: VoxelDebris) -> void:
	name = &"VoxelTerrain"
	_grid = grid
	_level = level
	_volume = level.volume
	_rules = level.rules
	_debris = debris
	_floor_top = (_rules.bottom + 1) * VoxelVolume.BLOCK
	_floor_limit = _floor_top - FLOOR_DEPTH
	for id in level.data.kinds:
		var kind := level.library.find(StringName(id))
		_kind_wear.append(kind.destruction as VoxelDestruction if kind != null else null)
	_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	_noise.frequency = 1.0
	_show.randomize()
	if level.renderer != null:
		level.renderer.chunk_redrawn.connect(_on_chunk_redrawn)


## Takes on [param body], a rigid body drawn by a MagicaVoxel model, as a loose
## model wearing away as [param destruction] says. The model is the first of
## its MeshInstance3D children drawn by one ([method VoxelModel.take_over]): a
## model of a .vox imported as a scene, the .vox being [param source]
## ([method VoxelShape.source_of]), a mesh imported straight from a .vox,
## which needs none, or one already drawn as a [VoxelModel], as a prop a figure
## dropped is, blood and all. [param passes] are the bodies it passes through,
## which it hands on to the parts cut from it ([member VoxelBody.passes]). It
## is made a piece ([method TerrainDestruction.make_piece]), if it was not one,
## for rounds and blasts to find it by. Returns its [VoxelBody], or null if no
## voxel model draws it.
func take_on_body(body: RigidBody3D, destruction: VoxelDestruction, source := "", passes: Array = []) -> VoxelBody:
	if _loose.has(body):
		return _loose[body]
	_wearable.erase(body)
	for child in body.get_children():
		var drawn := child as MeshInstance3D
		if drawn == null:
			continue
		var model := VoxelModel.take_over(drawn, source)
		if model == null or model.count == 0:
			continue
		var loose := VoxelBody.new(model, destruction, body)
		loose.passes = passes
		body.add_child(loose)
		TerrainDestruction.make_piece(body)
		_keep(body, loose)
		return loose
	return null


## Lets [param body] wear away as [method take_on_body] would, but takes it on
## only the first time a round or a blast reaches it ([method _model_of]), as a
## crate's pieces are: taking a piece on costs more than making it, and most
## pieces are never hit. Until then it is just a piece
## ([method TerrainDestruction.make_piece]), noted as one that wears.
func take_on_later(body: RigidBody3D, destruction: VoxelDestruction, source := "", passes: Array = []) -> void:
	if _loose.has(body) or _wearable.has(body):
		return
	var waiting := Wearable.new()
	waiting.destruction = destruction
	waiting.source = source
	waiting.passes = passes
	_wearable[body] = waiting
	TerrainDestruction.make_piece(body)
	body.tree_exiting.connect(_forget.bind(body), CONNECT_ONE_SHOT)


## How many loose models there are: pieces taken on, not those still waiting
## to be ([method take_on_later]).
func loose_count() -> int:
	return _loose.size()


## Whether piece [param piece] of the level wears away.
func wears_away(piece: int) -> bool:
	return _wear_of_piece(piece) != null


## How piece [param piece] of the level comes apart, or null if it never does.
func destruction_of(piece: int) -> Destruction:
	var kind := _level.kind_of(piece)
	return kind.destruction if kind != null else null


## The loose model [param body] is, taken on now if it was a piece waiting to
## wear away; null if it does not wear away. For blood to stain it.
func model_of(body: Object) -> VoxelBody:
	return _model_of(body)


## Whether [param point], in the world, is inside a voxel of the level.
func is_solid_at(point: Vector3) -> bool:
	return _volume.is_solid(VoxelVolume.voxel_under(_level.to_local(point)))


## Where the level's voxels are in the world: a voxel's place, counted in
## voxels, to the world.
func voxel_frame() -> Transform3D:
	return _level.global_transform * Transform3D(Basis.from_scale(Vector3.ONE * VOXEL), Vector3.ZERO)


## Breaks off the voxels nearest where [param hit] struck a piece that wears
## away, so many for each point of [param damage] (the struck piece's
## [member VoxelDestruction.voxels_per_damage]), from whichever pieces they are
## in, out to [constant BITE_SPREAD] times as far as the bite would go into a
## solid block. Each flies out of the face the round struck.
func chip(hit: CombatGrid.RayHit, damage: int) -> Wear:
	var destruction := _wear_of_piece(hit.piece)
	if destruction == null:
		return Wear.new()
	var budget := roundi(damage * destruction.voxels_per_damage)
	if budget <= 0:
		return Wear.new()
	# Half a voxel in, so the voxel struck is the nearest. Into a solid block the
	# bite would be a half ball of budget voxels, which sets how far it reaches
	# and how much its edge is roughened.
	var center := _level.to_local(hit.point + hit.direction * VOXEL * 0.5)
	var radius := _bite_radius(budget)
	var reach := minf(radius * BITE_SPREAD, BITE_REACH)
	_roughen(radius, randi())
	var found := Found.new()
	_gather(center, reach, 1.0, found)
	_level.ensure_collision(AABB(hit.point - Vector3.ONE, Vector3.ONE * 2.0))
	var outward := -hit.direction
	if hit.face != Vector3i.ZERO:
		outward = (_level.global_basis * Vector3(hit.face)).normalized()
	var batches: Array = []
	var wear := _wear_away(found, found.least(budget), _chip_motion(outward, hit.direction), true, batches)
	_scatter(batches)
	return wear


## Tears through every loose model a round flying from [param from] to
## [param to] passes through, with [param damage] environmental damage behind
## it, up to [constant MOST_TORN] of them: breaks off so many voxels for each
## point (each model's [member VoxelDestruction.voxels_per_damage]) nearest
## where it goes into the model, which fly out of the face it went in by and
## on the way it was going, and the round flies on. Only for show: nothing the
## rules decide waits on it.
func tear(from: Vector3, to: Vector3, damage: int) -> void:
	if (_loose.is_empty() and _wearable.is_empty()) or from.is_equal_approx(to):
		return
	var heading := from.direction_to(to)
	var length := from.distance_to(to)
	var batches: Array = []
	# Found first and torn after, as tearing one can cut new models from it.
	for loose in _models_along(from, to):
		if not is_instance_valid(loose):
			continue
		var model := loose.model
		var met := march(model.shape, model.voxels, model.frame(), from, heading, length)
		if met == null:
			continue
		var budget := roundi(damage * loose.destruction.voxels_per_damage)
		if budget <= 0:
			continue
		var center := met.point + heading * VOXEL * 0.5
		var radius := _bite_radius(budget)
		var reach := minf(radius * BITE_SPREAD, BITE_REACH)
		_roughen(radius, _show.randi())
		var found := ModelFound.new()
		_gather_voxels(model.shape, model.voxels, model.rows, model.frame(), center, reach, 1.0, found, 0)
		var outward := met.normal if met.face != Vector3i.ZERO else -heading
		_wear_model(loose, found.voxels_at(found.least(budget)), _chip_motion(outward, heading), batches)
	_scatter(batches)


## Blows a crater round [param origin], where a blast doing [param damage]
## environmental damage goes off, in every piece of the level that wears away
## within [param cells], the cells the blast reaches: every voxel within its
## piece's [method VoxelDestruction.crater_radius] of it, roughened. Every
## loose model inside the blast is cratered the same way, inside the blast.
## Up to [constant CRATER_DEBRIS] lumps of what they lose fly off as debris.
##
## The bottom of the map, only ever worn [constant FLOOR_DEPTH] deep, is blown
## into a bowl instead: as wide as the ball is where it meets the ground, and
## [constant FLOOR_DEPTH] deep in the middle, under where the blast went off.
func crater(origin: Vector3, cells: Array[Vector3i], damage: int) -> Wear:
	var wear := Wear.new()
	var batches: Array = []
	var largest := 0.0
	for destruction in _kind_wear:
		if destruction != null:
			largest = maxf(largest, destruction.crater_radius(damage))
	if largest > 0.0 and not cells.is_empty():
		_roughen(largest, randi())
		var inside := _cell_box(cells)
		var local := _level.to_local(origin)
		var found := Found.new()
		# Above the floor, a ball; each voxel goes by its own piece's crater.
		_gather(local, largest + _bump_size, largest, found, 1.0, -INF, inside, -1, damage)
		var ground := float(_floor_top) * VOXEL
		var across := sqrt(maxf(largest * largest - pow(local.y - ground, 2.0), 0.0))
		if across > 0.0:
			var under := Vector3(local.x, ground, local.z)
			_gather(under, across + _bump_size, across, found, across / (FLOOR_DEPTH * VOXEL), across - _bump_size, inside, 1, damage)
		_level.ensure_collision(_level.global_transform * inside)
		wear = _wear_away(found, found.under(1.0), _crater_motion(origin, largest), false, batches)

	# Then every loose model the blast reaches: only for show. A piece waiting
	# to wear away is only taken on if the crater reaches its box.
	if not (_loose.is_empty() and _wearable.is_empty()) and not cells.is_empty():
		var box := _level.global_transform * _cell_box(cells)
		for body in TerrainDestruction.pieces_in(get_world_3d().direct_space_state, box):
			var how := _wear_of(body)
			if how == null:
				continue
			var radius := how.crater_radius(damage)
			if radius <= 0.0:
				continue
			var near := TerrainDestruction.debris_box(body)
			if origin.distance_to(origin.clamp(near.position, near.end)) > radius * (1.0 + ROUGHNESS) + VOXEL:
				continue
			var loose := _model_of(body)
			if loose == null:
				continue
			var model := loose.model
			_roughen(radius, _show.randi())
			var found := ModelFound.new()
			_gather_voxels(model.shape, model.voxels, model.rows, model.frame(), origin, radius + _bump_size, radius, found, 0, 1.0, radius - _bump_size, -INF, box)
			_wear_model(loose, found.voxels_at(found.under(1.0)), _crater_motion(origin, radius), batches)
	_scatter(batches, CRATER_DEBRIS)
	return wear


## Takes piece [param piece] out of the level's voxels, all it has left, as it
## breaks or falls: returns what it left, for it to crumble or fall as.
func take_piece(piece: int) -> Taken:
	var taken := Taken.new()
	var voxels := _volume.voxels_of(piece)
	var wanted := PackedInt32Array()
	wanted.resize(voxels.size() * 3)
	for at in voxels.size():
		wanted[at * 3] = int(voxels[at].x)
		wanted[at * 3 + 1] = int(voxels[at].y)
		wanted[at * 3 + 2] = int(voxels[at].z)
	var places := PackedByteArray()
	var owners := PackedInt32Array()
	_volume.remove_many(wanted, places, owners)
	_volume.lay_bare_box(_level.data.slot_at(piece), wanted)
	for at in places.size():
		if places[at] == 0:
			continue
		taken.voxels.append(wanted[at * 3])
		taken.voxels.append(wanted[at * 3 + 1])
		taken.voxels.append(wanted[at * 3 + 2])
		taken.places.append(places[at])
	if not taken.places.is_empty():
		var origin := LevelData.voxel_origin(_level.data.slot_at(piece))
		_level.ensure_collision(_level.global_transform * AABB(Vector3(origin) * VOXEL, Vector3.ONE))
	return taken


## Breaks [param taken], what a piece left of itself, up into lumps at most
## [member VoxelDestruction.crumble_size] voxels across and lets them fall.
## [param frame] takes a voxel's place in [param taken] to the world: the
## level's ([method voxel_frame]) for a piece breaking where it stood, the place
## it landed for one that fell. [param hit] is the round that broke it, if one
## did, which knocks the lumps nearest where it struck on along its flight;
## [param motion] is how it was moving, if it fell whole, which its lumps carry
## on. Returns their bodies.
func crumble(taken: Taken, frame: Transform3D, destruction: VoxelDestruction, hit: CombatGrid.RayHit = null, motion: Destruction.Motion = null) -> Array[RID]:
	var batch := VolumeBatch.new()
	batch.frame = frame
	for index in taken.size():
		batch.add(taken.voxel(index), _volume.palette[taken.places[index]])
	batch.destruction = destruction if destruction != null else _fallback
	batch.motion = func(piece: VoxelDebris.Piece) -> void:
		var center := piece.transform.origin
		piece.velocity = _random_in_ball() * CRUMBLE_SCATTER
		piece.spin = _random_in_ball() * CRUMBLE_SPIN
		if hit != null:
			var nearness := 1.0 - clampf(center.distance_to(hit.point) / CRUMBLE_REACH, 0.0, 1.0)
			piece.velocity += hit.direction * CRUMBLE_PUSH * nearness
		if motion != null:
			piece.velocity += motion.at(center)
			piece.spin += motion.angular_velocity
	_group(batch, batch.destruction.crumble_size)
	return _scatter([batch])


## Wears a ragged rim round the hole the piece in [param slot] left as it
## broke: up to [constant RIM_DEPTH] voxels into every piece round it that
## wears away, wandering in and out, so the hole a block leaves is not a clean
## cube. What it wears off drops away; nothing it wears is worn past standing
## by it, as the rules decide that only as a round or blast lands. Draws on the
## global generator once, as a bite does. Returns the lumps' bodies.
func roughen_hole(slot: Vector3i) -> Array[RID]:
	var origin := LevelData.voxel_origin(slot)
	var reach := ceili(RIM_DEPTH + RIM_WANDER)
	var least := origin - Vector3i.ONE * reach
	var most := origin + Vector3i.ONE * (VoxelVolume.BLOCK - 1 + reach)
	least.y = maxi(least.y, _floor_limit)
	_noise.seed = randi()
	var frame := voxel_frame()
	var hole := AABB(Vector3(origin), Vector3.ONE * VoxelVolume.BLOCK)
	var batch := VolumeBatch.new()
	batch.frame = frame
	batch.destruction = _fallback
	var removed := PackedInt32Array()
	var destruction: VoxelDestruction = null
	for x in range(least.x, most.x + 1):
		for z in range(least.z, most.z + 1):
			for y in range(least.y, most.y + 1):
				var voxel := Vector3i(x, y, z)
				var middle := Vector3(voxel) + HALF
				if hole.has_point(middle):
					continue
				var distance := middle.distance_to(middle.clamp(hole.position, hole.end))
				if distance > RIM_DEPTH + RIM_WANDER:
					continue
				if not _volume.is_solid(voxel):
					continue
				var piece := _volume.owner_at(voxel)
				var how := _wear_of_piece(piece)
				if how == null:
					continue
				var wander := _noise.get_noise_3dv(middle * VOXEL * RIM_BUMPS) * RIM_WANDER
				if distance + wander >= RIM_DEPTH:
					continue
				var place := _volume.remove(voxel)
				if place == 0:
					continue
				destruction = how
				batch.add(voxel, _volume.palette[place])
				removed.append_array(PackedInt32Array([voxel.x, voxel.y, voxel.z]))
	if batch.colors.is_empty():
		return []
	_volume.lay_bare(removed)
	if destruction != null:
		batch.destruction = destruction
	batch.motion = _falling_motion(Vector3.ZERO, Vector3.ZERO, Vector3.ZERO, LOOSE_SCATTER, CHIP_SPIN * 0.2)
	var batches: Array = [batch]
	_drop_loose(removed, batches)
	for each: Batch in batches:
		if each.clumps.is_empty():
			_group(each, DEBRIS_CLUMP)
	return _scatter(batches)


## Whether what is left of piece [param piece] can still hold up whatever
## stands on it: nothing does, or some run of its own voxels still joins the
## bottom of its box to the top. A tree's trunk shot through holds up its crown
## no longer, however much of the rest of it is left. Searched from every voxel
## along the bottom, upward first, until one reaches the top.
func holds_up(piece: int) -> bool:
	var slot := _level.data.slot_at(piece)
	var above := slot + Vector3i.UP
	if LevelData.is_centre(slot):
		if not _rules.is_solid(LevelData.cell_of(above)):
			return true
	elif not _rules.has_edge_slot(above):
		return true
	var origin := LevelData.voxel_origin(slot)
	var top := origin.y + VoxelVolume.BLOCK - 1
	var box := AABB(Vector3(origin), Vector3.ONE * VoxelVolume.BLOCK)
	var seen := {}
	var stack: Array[Vector3i] = []
	for at in _volume.voxels_of(piece):
		var voxel := Vector3i(at)
		if voxel.y == origin.y:
			stack.append(voxel)
			seen[voxel] = true
	# Up is pushed last, so it is searched first.
	var steps: Array[Vector3i] = [Vector3i.DOWN, Vector3i.LEFT, Vector3i.RIGHT, Vector3i.FORWARD, Vector3i.BACK, Vector3i.UP]
	while not stack.is_empty():
		var at: Vector3i = stack.pop_back()
		if at.y == top:
			return true
		for step in steps:
			var next := at + step
			if seen.has(next) or not box.has_point(Vector3(next) + HALF):
				continue
			if _volume.owner_at(next) != piece:
				continue
			seen[next] = true
			stack.append(next)
	return false


## Carries the blood on [param taken], what a piece of kind [param kind]
## standing in [param slot] turned [param turn] left of itself, on to the
## pieces [param bodies] it has just broken into in [param frame] (where its
## voxels stood, as its kind's own model has them, unturned): every voxel of a
## piece that sat in a voxel blood had recoloured is recoloured too, the piece
## taken on as a loose model ([method _model_of]) if it was not yet. A piece
## that does not wear away is left clean.
func carry_blood(taken: Taken, kind: int, slot: Vector3i, turn: int, frame: Transform3D, bodies: Array[RigidBody3D]) -> void:
	var shape: VoxelShape = _volume.shapes[kind] if kind >= 0 and kind < _volume.shapes.size() else null
	if shape == null:
		return
	var origin := LevelData.voxel_origin(slot)
	# Each bloodied voxel, as a voxel of the kind's own model, and where it was.
	var bloodied := {}
	var points := PackedVector3Array()
	for index in taken.size():
		if taken.places[index] != VoxelVolume.BLOOD:
			continue
		var own := VoxelVolume.turned(taken.voxel(index) - origin, 4 - posmod(turn, 4))
		if not shape.holds(own):
			continue
		bloodied[own] = true
		points.append(frame * shape.center_of(shape.index_of(own)))
	if bloodied.is_empty():
		return
	var to_block := frame.affine_inverse()
	for body in bodies:
		if not is_instance_valid(body):
			continue
		var box := TerrainDestruction.debris_box(body).grow(VOXEL)
		var holds := false
		for point in points:
			if box.has_point(point):
				holds = true
				break
		if not holds:
			continue
		var loose := _model_of(body)
		if loose == null:
			continue
		# From the piece's frame to the block's.
		var model := loose.model
		var into := to_block * model.frame()
		for index in model.shape.length:
			if model.voxels[index] != 0 and bloodied.has(shape.voxel_under(into * model.shape.center_of(index))):
				model.recolor(index, VoxelVolume.BLOOD)


## How piece [param piece] wears away, or null if it does not, or is no piece.
func _wear_of_piece(piece: int) -> VoxelDestruction:
	if piece < 0 or piece >= _level.data.count():
		return null
	return _kind_wear[_level.data.kind_at(piece)]


## The box, in the level's space, that [param cells] fill.
static func _cell_box(cells: Array[Vector3i]) -> AABB:
	var box := AABB(Vector3(cells[0]), Vector3.ONE)
	for cell in cells:
		box = box.merge(AABB(Vector3(cell), Vector3.ONE))
	return box


## Adds to [param found] every voxel of the level within [param reach] cells
## of [param center] (in the level's space) that may be worn: a voxel of a
## piece that wears away, above the floor's [constant FLOOR_DEPTH], each scored
## by how far it is, roughened, over [param scale]. Distance up and down counts
## [param squash] times over, for a crater flatter than a ball. One nearer
## than [param certain] scores nothing at all, however the edge is roughened.
## One outside [param inside], if it has volume, in the level's space, is left
## out; and those above the bottom layer if [param layer] is 1, or in it if -1.
## Given [param damage], a voxel is only worn within its own piece's crater of
## that damage, as pieces of different kinds blast differently.
##
## Only the voxels inside the ball are looked at: each row of a chunk is cut to
## the run of it inside the ball, and only the voxels there are visited.
func _gather(
	center: Vector3, reach: float, scale: float, found: Found, squash := 1.0, certain := -INF,
	inside := AABB(), layer := 0, damage := -1
) -> void:
	var size := float(VoxelVolume.BLOCK)
	var middle := center * size
	var far := reach * size
	var least := Vector3i((middle - Vector3.ONE * far).floor())
	var most := Vector3i((middle + Vector3.ONE * far).floor())
	least.y = maxi(least.y, _floor_limit)
	if layer == 1:
		most.y = mini(most.y, _floor_top - 1)
	elif layer == -1:
		least.y = maxi(least.y, _floor_top)
	if least.y > most.y:
		return
	var limited := inside.has_volume()
	var flatten := squash * squash
	var frame := voxel_frame()
	for key in _volume.chunks_in(least, most):
		var chunk: VoxelVolume.Chunk = _volume.chunks[key]
		# Which of the chunk's pieces wear, and how far their craters reach.
		var wears := PackedByteArray()
		var radii := PackedFloat32Array()
		wears.resize(chunk.owners.size() + 1)
		radii.resize(chunk.owners.size() + 1)
		for place in chunk.owners.size():
			var how := _wear_of_piece(chunk.owners[place])
			if how != null:
				wears[place + 1] = 1
				radii[place + 1] = how.crater_radius(damage) if damage >= 0 else reach
		var origin := chunk.origin
		var low := (least - origin).clamp(Vector3i.ZERO, Vector3i.ONE * VoxelVolume.MASK)
		var high := (most - origin).clamp(Vector3i.ZERO, Vector3i.ONE * VoxelVolume.MASK)
		var rows := chunk.rows_x
		var slots := chunk.slots
		for y in range(low.y, high.y + 1):
			var across_y := origin.y + y + 0.5 - middle.y
			for z in range(low.z, high.z + 1):
				var row := rows[z + (y << VoxelVolume.SHIFT)]
				if row == 0:
					continue
				var across_z := origin.z + z + 0.5 - middle.z
				var left := far * far - across_z * across_z - across_y * across_y * flatten
				if left < 0.0:
					continue
				var half_run := sqrt(left)
				var first := maxi(ceili(middle.x - half_run - 0.5) - origin.x, low.x)
				var last := mini(floori(middle.x + half_run - 0.5) - origin.x, high.x)
				if first > last:
					continue
				var run := row & ((1 << (last + 1)) - 1) & ~((1 << first) - 1)
				var row_at := (z << VoxelVolume.SHIFT) + (y << (VoxelVolume.SHIFT * 2))
				while run != 0:
					var low_bit := run & -run
					run ^= low_bit
					var x: int = ChunkMesher.BIT[low_bit % 67]
					var slot := slots[row_at + x]
					if slot == 0 or wears[slot] == 0:
						continue
					var across_x := origin.x + x + 0.5 - middle.x
					var distance := sqrt(across_x * across_x + across_z * across_z + across_y * across_y * flatten) / size
					if distance > reach:
						continue
					var voxel := origin + Vector3i(x, y, z)
					if limited and not inside.has_point((Vector3(voxel) + HALF) / size):
						continue
					var score := 0.0
					if damage >= 0:
						# Each piece is cratered as far as its own kind blasts.
						var own := radii[slot]
						if distance > own + _bump_size:
							continue
						if distance >= own - _bump_size:
							score = (distance + _bump(frame * (Vector3(voxel) + HALF))) / own
					elif distance >= certain:
						score = (distance + _bump(frame * (Vector3(voxel) + HALF))) / scale
					found.add(voxel, score)


## Breaks off the voxels of [param found] at [param picks], then everything
## those leave holding on to nothing ([method _drop_loose]), grouped into lumps
## at most [constant DEBRIS_CLUMP] voxels across added to [param batches]. Each
## lump sets off as [param motion] says, or, one cut loose, just drops. Says
## which pieces are worn past standing, and draws what is left of the level: at
## once if [param now], else over the next few frames.
func _wear_away(found: Found, picks: PackedInt32Array, motion: Callable, now: bool, batches: Array) -> Wear:
	var wear := Wear.new()
	var by_destruction := {}
	var lost := {}
	var removed := PackedInt32Array()
	var frame := voxel_frame()
	var wanted := PackedInt32Array()
	wanted.resize(picks.size() * 3)
	for at in picks.size():
		var pick := picks[at]
		wanted[at * 3] = found.voxels[pick * 3]
		wanted[at * 3 + 1] = found.voxels[pick * 3 + 1]
		wanted[at * 3 + 2] = found.voxels[pick * 3 + 2]
	var places := PackedByteArray()
	var owners := PackedInt32Array()
	_volume.remove_many(wanted, places, owners)
	for at in places.size():
		var place := places[at]
		if place == 0:
			continue
		var voxel := Vector3i(wanted[at * 3], wanted[at * 3 + 1], wanted[at * 3 + 2])
		removed.append(voxel.x)
		removed.append(voxel.y)
		removed.append(voxel.z)
		var piece := owners[at]
		lost[piece] = true
		var destruction := _wear_of_piece(piece)
		if destruction == null:
			destruction = _fallback
		var batch: VolumeBatch = by_destruction.get(destruction)
		if batch == null:
			batch = VolumeBatch.new()
			batch.frame = frame
			batch.destruction = destruction
			batch.motion = motion
			by_destruction[destruction] = batch
			batches.append(batch)
		batch.add(voxel, _volume.palette[place])
	for batch: VolumeBatch in by_destruction.values():
		_group(batch, DEBRIS_CLUMP)
	_volume.lay_bare(removed)
	var loose_from := batches.size()
	for piece: int in _drop_loose(removed, batches):
		lost[piece] = true
	for index in range(loose_from, batches.size()):
		_group(batches[index], DEBRIS_CLUMP)
	if removed.is_empty():
		return wear
	wear.worn = true
	var least := Vector3i.MAX
	var most := Vector3i.MIN
	for index in range(0, removed.size(), 3):
		var at := Vector3i(removed[index], removed[index + 1], removed[index + 2])
		least = least.min(at)
		most = most.max(at)
	wear.box = _level.global_transform * AABB(Vector3(least) * VOXEL, Vector3(most - least + Vector3i.ONE) * VOXEL)
	for piece: int in lost:
		if piece < 0 or not _rules.is_standing(piece) or _never_breaks(piece):
			continue
		var destruction := _wear_of_piece(piece)
		if destruction == null:
			continue
		if _volume.counts[piece] < destruction.collapse_below * _volume.whole[piece] or not holds_up(piece):
			wear.broken.append(piece)
	if now:
		_level.redraw_now()
	return wear


## Breaks off every voxel of the level the voxels at [param removed] (three
## numbers each) leave holding on to nothing, into lumps that just drop, added
## to [param batches] a batch for each kind of piece they break off. Returns
## the pieces that lost voxels so.
##
## Each voxel left next to one gone is searched from, through every voxel
## joined to it face to face, whatever piece, cell or chunk it is in, until the
## search reaches one that holds on: the floor below its
## [constant FLOOR_DEPTH], which is never worn, or a piece that does not wear
## away. A search that grows past [constant HOLD_SEARCH] voxels is taken to be
## held: what is bigger is a piece the rules bring down whole.
func _drop_loose(removed: PackedInt32Array, batches: Array) -> Dictionary:
	var pieces := {}
	if removed.is_empty():
		return pieces
	# 1 held, 2 being searched, 3 loose.
	var known := {}
	# Each chunk's pieces that hold whatever touches them, by slot, worked out
	# once a search first comes into the chunk.
	var anchors := {}
	# Down is taken last, so it is searched first: most voxels are held by the
	# ground under them. Each way's step, and how far it is in a chunk's
	# arrays; a voxel on a chunk's face asks the volume instead.
	var steps: Array[Vector3i] = [Vector3i.UP, Vector3i.LEFT, Vector3i.RIGHT, Vector3i.FORWARD, Vector3i.BACK, Vector3i.DOWN]
	var offsets := PackedInt32Array([VoxelVolume.AREA, -1, 1, -VoxelVolume.SIZE, VoxelVolume.SIZE, -VoxelVolume.AREA])
	var loose: Array[Vector3i] = []
	var stack: Array[Vector3i] = []
	var searched: Array[Vector3i] = []
	var last := VoxelVolume.MASK
	for index in range(0, removed.size(), 3):
		var gone := Vector3i(removed[index], removed[index + 1], removed[index + 2])
		var chunk := _volume.chunk_of(gone)
		var lx := gone.x & last
		var ly := gone.y & last
		var lz := gone.z & last
		var at_index := lx + (lz << VoxelVolume.SHIFT) + (ly << (VoxelVolume.SHIFT * 2))
		var inside := lx > 0 and lx < last and ly > 0 and ly < last and lz > 0 and lz < last
		for way in 6:
			var start := gone + steps[way]
			var solid := false
			if inside:
				solid = chunk.colors[at_index + offsets[way]] != 0
			else:
				solid = _volume.is_solid(start)
			if not solid or known.has(start):
				continue
			stack.clear()
			searched.clear()
			stack.append(start)
			searched.append(start)
			known[start] = 2
			var held := false
			while not stack.is_empty():
				var at: Vector3i = stack.pop_back()
				if at.y < _floor_limit or searched.size() > HOLD_SEARCH or _anchored(at, anchors):
					held = true
					break
				var here := _volume.chunk_of(at)
				var hx := at.x & last
				var hy := at.y & last
				var hz := at.z & last
				var here_index := hx + (hz << VoxelVolume.SHIFT) + (hy << (VoxelVolume.SHIFT * 2))
				var within := hx > 0 and hx < last and hy > 0 and hy < last and hz > 0 and hz < last
				for step in 6:
					var next := at + steps[step]
					var state: int = known.get(next, 0)
					if state == 1:
						held = true
						break
					if state != 0:
						continue
					var next_solid := false
					if within:
						next_solid = here.colors[here_index + offsets[step]] != 0
					else:
						next_solid = _volume.is_solid(next)
					if not next_solid:
						continue
					known[next] = 2
					stack.append(next)
					searched.append(next)
				if held:
					break
			var mark := 1 if held else 3
			for voxel in searched:
				known[voxel] = mark
			if not held:
				loose.append_array(searched)
	if loose.is_empty():
		return pieces
	var frame := voxel_frame()
	var dropping := _falling_motion(Vector3.ZERO, Vector3.ZERO, Vector3.ZERO, LOOSE_SCATTER, CHIP_SPIN * 0.2)
	var by_destruction := {}
	var wanted := PackedInt32Array()
	wanted.resize(loose.size() * 3)
	for at in loose.size():
		wanted[at * 3] = loose[at].x
		wanted[at * 3 + 1] = loose[at].y
		wanted[at * 3 + 2] = loose[at].z
	var places := PackedByteArray()
	var owners := PackedInt32Array()
	_volume.remove_many(wanted, places, owners)
	_volume.lay_bare(wanted)
	for at in loose.size():
		var voxel := loose[at]
		var place := places[at]
		var piece := owners[at]
		if place == 0:
			continue
		pieces[piece] = true
		var destruction := _wear_of_piece(piece)
		if destruction == null:
			destruction = _fallback
		var batch: VolumeBatch = by_destruction.get(destruction)
		if batch == null:
			batch = VolumeBatch.new()
			batch.frame = frame
			batch.destruction = destruction
			batch.motion = dropping
			by_destruction[destruction] = batch
			batches.append(batch)
		batch.add(voxel, _volume.palette[place])
	return pieces


## Whether [param voxel] is of a piece that holds whatever touches it: one
## standing that does not wear away, which the rules keep whole. Each chunk's
## such pieces are worked out once into [param anchors], by the chunk's key, as
## a flag a slot.
func _anchored(voxel: Vector3i, anchors: Dictionary) -> bool:
	var chunk := _volume.chunk_of(voxel)
	if chunk == null:
		return false
	var flags: PackedByteArray = anchors.get(chunk.key, PackedByteArray())
	if flags.is_empty():
		flags.resize(chunk.owners.size() + 1)
		for place in chunk.owners.size():
			var piece := chunk.owners[place]
			if piece >= 0 and _wear_of_piece(piece) == null and _rules.is_standing(piece):
				flags[place + 1] = 1
		anchors[chunk.key] = flags
	return flags[chunk.slots[VoxelVolume.index_of(voxel)]] == 1


## Whether [param voxel] holds on where it is whatever is cut away round it:
## the floor below its [constant FLOOR_DEPTH], or a voxel of a piece standing
## that does not wear away, which the rules keep whole.
func _holds_on(voxel: Vector3i) -> bool:
	if voxel.y < _floor_limit:
		return true
	var piece := _volume.owner_at(voxel)
	return piece >= 0 and _wear_of_piece(piece) == null and _rules.is_standing(piece)


## Whether piece [param piece] never breaks however worn: a solid piece in the
## middle of a cell of the bottom layer.
func _never_breaks(piece: int) -> bool:
	var slot := _level.data.slot_at(piece)
	return LevelData.is_centre(slot) and slot.y == _rules.bottom


## Wakes the debris lying round the chunk [param key] once it is drawn again,
## and so collides again, as what is left of it: whatever lay on what wore
## away would rest on air.
func _on_chunk_redrawn(key: Vector3i) -> void:
	var least := Vector3(key * VoxelVolume.SIZE) * VOXEL
	var box := _level.global_transform * AABB(least, Vector3.ONE * VoxelVolume.SIZE * VOXEL)
	box = box.grow(VoxelDebris.LYING_ON)
	_debris.wake(box)
	if not is_inside_tree():
		return
	for body in TerrainDestruction.pieces_in(get_world_3d().direct_space_state, box):
		if body.sleeping and box.has_point(TerrainDestruction.debris_box(body).get_center()):
			body.sleeping = false


## Breaks the voxels at [param indices] off the loose model [param loose],
## grouped into lumps at most [constant DEBRIS_CLUMP] voxels across added to
## [param batches], each setting off as [param motion] says, carried on as the
## model was moving; then settles what is left of it ([method _settle]).
func _wear_model(loose: VoxelBody, indices: PackedInt32Array, motion: Callable, batches: Array) -> void:
	var model := loose.model
	var lost := PackedInt32Array()
	var held := PackedByteArray()
	for index in indices:
		var what := model.remove(index)
		if what != 0:
			lost.append(index)
			held.append(what)
	if lost.is_empty():
		return
	var moving := loose.body.linear_velocity
	var carried := func(piece: VoxelDebris.Piece) -> void:
		motion.call(piece)
		piece.velocity += moving
	batches.append(_batch(lost, held, model, DEBRIS_CLUMP, loose.destruction, carried))
	_settle(loose, batches)


## Settles what is left of [param loose] after it has lost voxels: crumbles it
## if it is worn past its share, or too small to stand on its own; else cuts
## every part no longer joined to the rest off it, as a model of its own if it
## is big enough and as lumps added to [param batches] if not, and draws,
## collides and weighs what is left as it is.
func _settle(loose: VoxelBody, batches: Array) -> void:
	var model := loose.model
	if model.count < SMALLEST_PART or model.count < loose.destruction.collapse_below * loose.whole:
		_crumble_model(loose, batches)
		return
	var parts := _parts(model)
	if parts.size() > 1:
		var from := loose.body
		var dropping := _falling_motion(from.linear_velocity, from.angular_velocity, from.global_position, LOOSE_SCATTER, CHIP_SPIN * 0.2)
		for place in range(1, parts.size()):
			var part := parts[place]
			if part.size() >= SMALLEST_PART:
				_split_off(loose, part)
				continue
			var held := PackedByteArray()
			for index in part:
				held.append(model.remove(index))
			batches.append(_batch(part, held, model, DEBRIS_CLUMP, loose.destruction, dropping))
		loose.restart()
	loose.rebuild()


## Breaks what is left of the loose model [param loose] up into lumps
## [member VoxelDestruction.crumble_size] voxels across, carrying on as it was
## moving, adds them to [param batches], and takes the model away.
func _crumble_model(loose: VoxelBody, batches: Array) -> void:
	var model := loose.model
	var from := loose.body
	var indices := PackedInt32Array()
	var held := PackedByteArray()
	for index in model.shape.length:
		if model.voxels[index] != 0:
			indices.append(index)
			held.append(model.voxels[index])
	var falling := _falling_motion(from.linear_velocity, from.angular_velocity, from.global_position, CRUMBLE_SCATTER, CRUMBLE_SPIN)
	batches.append(_batch(indices, held, model, loose.destruction.crumble_size, loose.destruction, falling))
	_forget(from)
	# Out of the way at once: its lumps are let go at the next physics step.
	from.hide()
	from.collision_layer = 0
	from.collision_mask = 0
	from.queue_free()


## Cuts the voxels at [param part] off the loose model [param loose] as a
## model of its own ([method VoxelModel.split]), blood and all: a body of its
## own beside it, drawing, colliding and weighing as those voxels, flying on as
## that part of the model was moving. The two start out touching, so they pass
## through each other, as a crate's pieces cut to overlap do, and the part
## passes through whatever the model did, which may be lying through it.
func _split_off(loose: VoxelBody, part: PackedInt32Array) -> VoxelBody:
	var from := loose.body
	var model := loose.model
	var rigid := RigidBody3D.new()
	rigid.name = from.name
	rigid.collision_layer = from.collision_layer
	rigid.collision_mask = from.collision_mask
	rigid.continuous_cd = from.continuous_cd
	rigid.physics_material_override = from.physics_material_override
	var cut := model.split(part)
	cut.drawn.transform = from.global_transform.affine_inverse() * model.drawn.global_transform
	rigid.add_child(cut.drawn)
	var collider := CollisionShape3D.new()
	collider.shape = BoxShape3D.new()
	rigid.add_child(collider)
	var split := VoxelBody.new(cut, loose.destruction, rigid)
	split.whole_mass = loose.whole_mass * cut.count / maxi(loose.whole, 1)
	rigid.add_child(split)
	from.get_parent().add_child(rigid)
	rigid.global_transform = from.global_transform
	TerrainDestruction.make_piece(rigid)
	# What either passes through, the other knows of, taken on or not yet.
	var passes: Array = [from]
	for other in loose.passes:
		if is_instance_valid(other):
			passes.append(other)
	loose.passes = passes.slice(1)
	for other in passes:
		rigid.add_collision_exception_with(other)
		var theirs: VoxelBody = _loose.get(other)
		if theirs != null:
			theirs.passes.append(rigid)
		elif _wearable.has(other):
			(_wearable[other] as Wearable).passes.append(rigid)
	split.passes = passes
	rigid.linear_velocity = _moving_at(from, split.world_box().get_center())
	rigid.angular_velocity = from.angular_velocity
	_keep(rigid, split)
	split.rebuild()
	return split


## The parts of what is left of [param model], each every voxel joined to the
## others face to face, as their places in its array, the biggest first.
func _parts(model: VoxelModel) -> Array[PackedInt32Array]:
	var shape := model.shape
	var voxels := model.voxels
	var steps := shape.steps()
	var seen := PackedByteArray()
	seen.resize(shape.length)
	var parts: Array[PackedInt32Array] = []
	for z in shape.size.z:
		for y in shape.size.y:
			var row := model.rows[y + z * shape.size.y]
			var row_start := shape.origin + y * shape.stride_y + z * shape.stride_z
			while row != 0:
				var low := row & -row
				row ^= low
				var start: int = row_start + ChunkMesher.BIT[low % 67]
				if seen[start] != 0:
					continue
				seen[start] = 1
				var part := PackedInt32Array([start])
				var next := 0
				while next < part.size():
					var at := part[next]
					next += 1
					for step in steps:
						var near := at + step
						if voxels[near] != 0 and seen[near] == 0:
							seen[near] = 1
							part.append(near)
				parts.append(part)
	parts.sort_custom(func(a: PackedInt32Array, b: PackedInt32Array) -> bool: return a.size() > b.size())
	return parts


## How fast the point [param at], in the world, of [param body] is moving.
static func _moving_at(body: RigidBody3D, at: Vector3) -> Vector3:
	return body.linear_velocity + body.angular_velocity.cross(at - body.global_position)


## Notes [param model] as the loose model [param body] is, and forgets it once
## the body goes.
func _keep(body: RigidBody3D, model: VoxelBody) -> void:
	_loose[body] = model
	model.tree_exiting.connect(_forget.bind(body), CONNECT_ONE_SHOT)


## Forgets [param body], a loose model or a piece waiting to be one.
func _forget(body: RigidBody3D) -> void:
	_loose.erase(body)
	_wearable.erase(body)


## The loose model [param body] is, taken on now if it was a piece waiting to
## wear away ([method take_on_later]); null if it does not wear away.
func _model_of(body: Object) -> VoxelBody:
	var model: VoxelBody = _loose.get(body)
	if model != null:
		return model
	var waiting: Wearable = _wearable.get(body)
	if waiting == null:
		return null
	return take_on_body(body as RigidBody3D, waiting.destruction, waiting.source, waiting.passes)


## How [param body] wears away, taken on or still waiting to be; null if it
## does not.
func _wear_of(body: Object) -> VoxelDestruction:
	var model: VoxelBody = _loose.get(body)
	if model != null:
		return model.destruction
	var waiting: Wearable = _wearable.get(body)
	return waiting.destruction if waiting != null else null


## Every loose model whose body a round flying from [param from] to [param to]
## passes through, nearest first, up to [constant MOST_TORN]; a piece waiting
## to wear away is taken on as it is found.
func _models_along(from: Vector3, to: Vector3) -> Array[VoxelBody]:
	var found: Array[VoxelBody] = []
	var query := PhysicsRayQueryParameters3D.create(from, to, TerrainDestruction.PIECE_LAYER)
	query.collide_with_areas = false
	query.hit_from_inside = true
	var passed: Array[RID] = []
	var space := get_world_3d().direct_space_state
	# A few pieces that do not wear away may be passed through on the way.
	for attempt in MOST_TORN * 2:
		query.exclude = passed
		var met := space.intersect_ray(query)
		if met.is_empty():
			break
		passed.append(met.rid)
		var model := _model_of(met.collider)
		if model != null:
			found.append(model)
			if found.size() >= MOST_TORN:
				break
	return found


## Makes the lumps of [param batches] and lets them fall: up to [param most]
## of them, chosen at random before any is made, the rest blown to dust; every
## one if [param most] is less than 0. Returns their bodies.
func _scatter(batches: Array, most := -1) -> Array[RID]:
	var total := 0
	for batch: Batch in batches:
		total += batch.clumps.size()
	# Which to make, numbered through each batch's lumps in turn.
	var chosen := PackedByteArray()
	chosen.resize(total)
	if most < 0 or total <= most:
		chosen.fill(1)
	else:
		var numbers := PackedInt32Array()
		numbers.resize(total)
		for number in total:
			numbers[number] = number
		for pick in most:
			var other := _show.randi_range(pick, total - 1)
			var swap := numbers[pick]
			numbers[pick] = numbers[other]
			numbers[other] = swap
			chosen[numbers[pick]] = 1
	var by_destruction := {}
	var number := 0
	for batch: Batch in batches:
		for clump: Array in batch.clumps:
			if chosen[number] != 0:
				var list: Array = by_destruction.get_or_add(batch.destruction, [])
				list.append(batch.make(clump))
			number += 1
	var made: Array[RID] = []
	for destruction: VoxelDestruction in by_destruction:
		var pieces: Array[VoxelDebris.Piece] = []
		pieces.assign(by_destruction[destruction])
		made.append_array(_debris.add(pieces, destruction))
	return made


## The voxels at [param indices] in [param model], standing where it stands
## now, which held [param held] each, as a [ShapeBatch]: grouped into lumps at
## most [param size] voxels across, broken off as [param destruction] breaks
## them, to set off as [param motion] says once made, each voxel in the colour
## it held in the model's palette, blood's included. They are grouped on a
## grid set at random, so no two models come apart along the same lines.
func _batch(
	indices: PackedInt32Array, held: PackedByteArray, model: VoxelModel, size: int,
	destruction: VoxelDestruction, motion: Callable
) -> ShapeBatch:
	var batch := ShapeBatch.new()
	var shape := model.shape
	batch.shape = shape
	batch.frame = model.frame()
	batch.palette = model.palette
	batch.indices = indices
	batch.held = held
	batch.destruction = destruction
	batch.motion = motion
	if indices.is_empty():
		return batch
	var shift := Vector3i(_show.randi_range(0, size - 1), _show.randi_range(0, size - 1), _show.randi_range(0, size - 1))
	var clumps := {}
	for place in indices.size():
		var key := (shape.voxel_at(indices[place]) + shift) / size
		var clump: Array = clumps.get_or_add(key, [])
		clump.append(place)
	batch.clumps = clumps.values()
	return batch


## Groups the voxels of [param batch], broken off the level, into lumps at most
## [param size] voxels across, on a grid set at random, so no two breaks come
## apart along the same lines.
func _group(batch: VolumeBatch, size: int) -> void:
	var shift := Vector3i(_show.randi_range(0, size - 1), _show.randi_range(0, size - 1), _show.randi_range(0, size - 1))
	var clumps := {}
	for place in batch.colors.size():
		var at := batch.voxel(place) + shift
		var key := Vector3i(floori(float(at.x) / size), floori(float(at.y) / size), floori(float(at.z) / size))
		var clump: Array = clumps.get_or_add(key, [])
		clump.append(place)
	batch.clumps = clumps.values()


## How the lumps a round breaks off set off: out of [param outward], the face
## it struck, and on along [param heading], the way it was going, tumbling.
func _chip_motion(outward: Vector3, heading: Vector3) -> Callable:
	return func(piece: VoxelDebris.Piece) -> void:
		piece.velocity = (
			outward * _show.randf_range(CHIP_SPEED_MIN, CHIP_SPEED_MAX)
			+ _random_in_ball() * CHIP_SCATTER
			+ heading * CHIP_CARRY
		)
		piece.spin = _random_in_ball() * CHIP_SPIN


## How the lumps a blast going off at [param origin] breaks off set off: away
## from it, the harder the nearer, out to a crater [param radius] across, and
## tumbling; what the blast drives down into the ground, the ground throws back
## up.
func _crater_motion(origin: Vector3, radius: float) -> Callable:
	return func(piece: VoxelDebris.Piece) -> void:
		var away := piece.transform.origin - origin
		var share := lerpf(1.0, CRATER_FAR_SHARE, clampf(away.length() / radius, 0.0, 1.0))
		away.y = absf(away.y)
		piece.velocity = (
			Blast.away_from(away) * CRATER_SPEED * share
			+ Vector3.UP * CRATER_LIFT * share
			+ _random_in_ball() * CRATER_SCATTER
		)
		piece.spin = _random_in_ball() * CHIP_SPIN


## How lumps that drop away from something set off: as the point they broke
## from was moving, on a body moving at [param linear] and turning at
## [param angular] about [param center], give or take [param scatter] cells a
## second, and turning as it turned, give or take [param spin] radians a
## second.
func _falling_motion(linear: Vector3, angular: Vector3, center: Vector3, scatter: float, spin: float) -> Callable:
	return func(piece: VoxelDebris.Piece) -> void:
		piece.velocity = linear + angular.cross(piece.transform.origin - center) + _random_in_ball() * scatter
		piece.spin = angular + _random_in_ball() * spin


## How far a bite of [param budget] voxels reaches into a solid model, as a
## half ball, in cells.
static func _bite_radius(budget: int) -> float:
	return pow(3.0 * budget / TAU, 1.0 / 3.0) * VOXEL


## Adds to [param found], as [param owner]'s, every one of [param voxels] -
## laid out as [param shape]'s, with [param rows], standing in [param frame] -
## within [param reach] of [param center], scored by how far it is, roughened,
## over [param scale]. Distance up and down counts [param squash] times over,
## for a crater flatter than a ball. One nearer than [param certain] scores
## nothing at all, however the edge is roughened. One lower than
## [param lowest], in the world, or, if [param inside] has volume, outside it,
## is left out. For loose models: the level's voxels are gathered by
## [method _gather].
##
## Only the voxels inside the ball are looked at: each row of the model is
## cut to the run of it inside the ball, and only the voxels there are visited.
func _gather_voxels(
	shape: VoxelShape, voxels: PackedByteArray, rows: PackedInt64Array, frame: Transform3D, center: Vector3,
	reach: float, scale: float, found: ModelFound, owner: int, squash := 1.0, certain := -INF, lowest := -INF,
	inside := AABB()
) -> void:
	var local := frame.affine_inverse() * center
	var up := (frame.basis.inverse() * Vector3.UP).normalized()
	# In voxels from the least corner of voxel (0, 0, 0) from here on.
	var middle := (local - shape.corner) / VOXEL
	var far := reach / VOXEL
	var last_voxel := shape.size - Vector3i.ONE
	var least := Vector3i((middle - Vector3.ONE * far).floor()).clamp(Vector3i.ZERO, last_voxel)
	var most := Vector3i((middle + Vector3.ONE * far).floor()).clamp(Vector3i.ZERO, last_voxel)
	# Squashed up and down along the model's y only if that is up: otherwise
	# rows are cut to the whole ball, which holds the squashed one.
	var level := absf(up.y) > 0.999
	var flatten := squash * squash if level else 1.0
	var stretch := squash * squash - 1.0
	var limited := inside.has_volume()
	for z in range(least.z, most.z + 1):
		var across_z := z + 0.5 - middle.z
		for y in range(least.y, most.y + 1):
			var row := rows[y + z * shape.size.y]
			if row == 0:
				continue
			# A model standing upright has the whole row at one height.
			if level and lowest > -INF and (frame * (shape.corner + Vector3(0.0, (y + 0.5) * VOXEL, 0.0))).y < lowest:
				continue
			var across_y := y + 0.5 - middle.y
			var left := far * far - across_z * across_z - across_y * across_y * flatten
			if left < 0.0:
				continue
			var half_run := sqrt(left)
			var first := maxi(ceili(middle.x - half_run - 0.5), 0)
			var last := mini(floori(middle.x + half_run - 0.5), last_voxel.x)
			if first > last:
				continue
			var run := row & ((1 << (last + 1)) - 1) & ~((1 << first) - 1)
			var row_start := shape.origin + y * shape.stride_y + z * shape.stride_z
			while run != 0:
				var low := run & -run
				run ^= low
				var x: int = ChunkMesher.BIT[low % 67]
				var offset := Vector3(x + 0.5 - middle.x, across_y, across_z) * VOXEL
				var rise := offset.dot(up)
				var distance := sqrt(offset.length_squared() + rise * rise * stretch)
				if distance > reach:
					continue
				var score := 0.0
				if distance >= certain or not level or limited:
					var world := frame * (shape.corner + (Vector3(x, y, z) + HALF) * VOXEL)
					if world.y < lowest:
						continue
					if limited and not inside.has_point(world):
						continue
					if distance >= certain:
						score = (distance + _bump(world)) / scale
				found.owners.append(owner)
				found.indices.append(row_start + x)
				found.scores.append(score)


## Where a ray from [param origin] along [param heading], normalised, first
## meets one of [param voxels] - laid out as [param shape]'s, standing in
## [param frame] - within [param max_distance] of [param origin], as a [Met];
## null if it meets none. Traced voxel by voxel through the model's box, as
## [method CombatGrid.cast] goes cell by cell.
static func march(shape: VoxelShape, voxels: PackedByteArray, frame: Transform3D, origin: Vector3, heading: Vector3, max_distance: float) -> Met:
	var inverse := frame.affine_inverse()
	# Counted in voxels from the least corner of voxel (0, 0, 0), along the ray
	# in voxels.
	var from := (inverse * origin - shape.corner) / VOXEL
	var along := (inverse.basis * heading).normalized()
	var bounds := Vector3(shape.size)

	# Where the ray is inside the model's box, between enter and leave.
	var enter := -INF
	var leave := INF
	var entered_on := -1
	for axis in 3:
		if is_zero_approx(along[axis]):
			if from[axis] < 0.0 or from[axis] > bounds[axis]:
				return null
			continue
		var near := -from[axis] / along[axis]
		var far := (bounds[axis] - from[axis]) / along[axis]
		if near > far:
			var swap := near
			near = far
			far = swap
		if near > enter:
			enter = near
			entered_on = axis
		leave = minf(leave, far)
	if leave < maxf(enter, 0.0):
		return null
	var t := maxf(enter, 0.0)
	if enter < 0.0:
		entered_on = -1

	var voxel := Vector3i((from + along * (t + 1e-4)).floor()).clamp(Vector3i.ZERO, shape.size - Vector3i.ONE)
	var step := Vector3i.ZERO
	var next_cross := Vector3(INF, INF, INF)
	var cross_spacing := Vector3(INF, INF, INF)
	for axis in 3:
		if is_zero_approx(along[axis]):
			continue
		step[axis] = int(signf(along[axis]))
		var boundary := voxel[axis] + (1 if step[axis] > 0 else 0)
		next_cross[axis] = (boundary - from[axis]) / along[axis]
		cross_spacing[axis] = absf(1.0 / along[axis])
	while voxels[shape.index_of(voxel)] == 0:
		var axis := next_cross.min_axis_index()
		t = next_cross[axis]
		voxel[axis] += step[axis]
		if t > leave or voxel[axis] < 0 or voxel[axis] >= shape.size[axis]:
			return null
		next_cross[axis] += cross_spacing[axis]
		entered_on = axis

	var met := Met.new()
	met.point = frame * (shape.corner + (from + along * t) * VOXEL)
	met.distance = origin.distance_to(met.point)
	if met.distance > max_distance:
		return null
	met.index = shape.index_of(voxel)
	if entered_on >= 0:
		met.face[entered_on] = -step[entered_on]
		met.normal = (frame.basis * Vector3(met.face)).normalized()
	return met


## Sets bites and craters roughening afresh, from [param seed], for one
## [param size] cells across.
func _roughen(size: float, seed: int) -> void:
	_noise.seed = seed
	_bump_size = size * ROUGHNESS
	_bump_scale = BUMPS / maxf(size, VOXEL)


## How far the edge of the bite or crater being made wanders in or out at
## [param point], in cells.
func _bump(point: Vector3) -> float:
	return _noise.get_noise_3dv(point * _bump_scale) * _bump_size


## A point drawn at random from the ball of radius one.
func _random_in_ball() -> Vector3:
	var point := Vector3(_show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0))
	while point.length_squared() > 1.0:
		point = Vector3(_show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0), _show.randf_range(-1.0, 1.0))
	return point
