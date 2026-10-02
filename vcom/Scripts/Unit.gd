## A character on the combat map: its health, its per-turn action budget and
## its reaction.
##
## A squad member is someone on the roster: given a [member character], it
## takes its name, colour, stats (health, defense, move, aim, melee accuracy,
## strength, evasion) and equipment from them, painting its Model child.
## Without one (enemies, the test harness) the scene's values and the Model's
## material stand, and it carries only its [member weapon]. What it uses up,
## such as a grenade it throws, it loses for good ([signal used_up]).
## UI reads [member color] until real portraits exist.
##
## It is seen as its [member model], a rigged figure that plays out what it
## does: it turns and runs as the unit walks, raises its gun to shoot, swings
## and throws, flinches, and breaks apart when it dies
## ([method TerrainDestruction.break_figure]). The rules never wait on it,
## but where a moment matters: a shot goes off once the gun is up, a blow lands
## when the swing does, and a grenade leaves the hand at the top of the throw.
## A hit that takes health is announced ([signal hurt]) with where it landed on
## the figure, for [Blood] to wound it there; that too is only for show.
class_name Unit
extends Node3D

signal health_changed(health: int, max_health: int)
signal actions_changed(remaining: int, per_turn: int)
signal reaction_changed(available: bool)
signal overwatch_changed(watching: bool)
## Emitted as the unit leaves the map, while it is still whole enough to be
## read from. Whoever was holding on to it should let go.
signal died
## Emitted as the unit uses [param item] up for good, as it does a grenade by
## throwing it, once it is gone from [member equipment]. Whoever keeps the
## character's gear should take it off them too.
signal used_up(item: Item)
## Emitted as a hit takes [param taken] health off the unit, more than none,
## before it can die of it: for [Blood] to wound its figure and spray. Where the
## hit came from, where on the body it landed and the way a slash swept across
## it are as [method take_damage] was given them.
signal hurt(taken: int, from: Vector3, at: Vector3, blasted: bool, sweep: Vector3)

## Physics layer holding the bodies that mouse clicks on units are tested
## against. Nothing collides with it, so it never affects movement.
const PICK_LAYER := 1 << 1
## Physics layer holding the bodies debris bumps off. A unit pushes debris
## aside as it moves and is never pushed back, so it never affects movement
## either.
const BODY_LAYER := 1 << 3
## How far above a unit's feet the body debris bumps off starts, in cells.
## Debris lying flat on the ground is stood among rather than ground into it.
const BODY_CLEARANCE := 0.15
## Every unit, whichever side it is on.
const GROUP := &"units"
## How fast a unit gathers speed when the ground under it gives way, in cells
## per second per second.
const FALL_ACCELERATION := 9.8
## How far out from the middle of its tile a mouse click picks the unit, in
## cells: its figure, arms down and gun in hand.
const PICK_RADIUS := 0.3
## The gun a unit without a character carries when the scene gives it none.
const PLAIN_RIFLE: Weapon = preload("res://Resources/Rifle.tres")
## How high off its feet a unit's blow comes from, in cells: about its chest.
const STRIKE_HEIGHT := 1.1

## Replaced by [member character]'s name when the unit has one.
@export var display_name := "Unit"
## Who this unit is on the roster: the same resource [member Campaign.roster]
## holds, so the two stay linked.
@export var character: Character
## Replaced by [member character]'s, as are defense, move range, aim and
## evasion.
@export var max_health := 10
## Taken off the damage of every hit this unit takes, down to none. Replaced
## by [member character]'s, armor included ([member Character.total_defense]).
@export var defense := 0
@export var actions_per_turn := 3
## Tiles the unit can walk for each action point spent moving.
@export var move_range := 4
## How far the unit can see, and so shoot, in tiles.
@export var sight_range := 20
## The gun this unit shoots with. A plain rifle if the scene leaves it unset.
## Replaced by the first gun [member character] has equipped, Weapon 1 before
## Weapon 2, when the unit has one; null when they have none, since the unit
## is then offered nothing to shoot with.
@export var weapon: Weapon
## What decides this unit's actions when the computer plays it. The squad
## leaves it empty; an enemy without one sits its turns out.
@export var ai: EnemyAI

@export_group("Marksmanship")
## Chance to hit before anything about the shot is taken into account.
@export var aim := 90
## Chance to land a melee strike before the target's evasion is taken off:
## what [member aim] is to a shot (see [method HitChance.for_strike]).
@export var melee_accuracy := 90
## Added to [member melee_weapon]'s damage in every strike that lands, before
## the target's defense comes off it. Nothing to shots.
@export var strength := 0
## Taken off the chance of anyone shooting at this unit, or striking at it.
@export var evasion := 0
## Added per tile this unit stands above what it is shooting at, and taken
## off per tile below it.
@export var height_bonus := 5
## Taken off per full [constant HitChance.DISTANCE_STEP] tiles to the target.
@export var distance_penalty := 5

var health := 0:
	set(value):
		health = clampi(value, 0, max_health)
		health_changed.emit(health, max_health)

var actions_remaining := 0:
	set(value):
		actions_remaining = clampi(value, 0, actions_per_turn)
		actions_changed.emit(actions_remaining, actions_per_turn)

## Whether the unit still has its one reaction. Reactions are taken outside
## the unit's own turn, in answer to something another unit does, and like
## Pathfinder's the unit gets its reaction back at the start of its turn.
var reaction_available := true:
	set(value):
		reaction_available = value
		reaction_changed.emit(reaction_available)

## Whether the unit is on overwatch: holding its reaction for a shot at an
## enemy it sees move, taken when the player calls for it (see [Reactions]).
## Firing, or the unit's next turn coming round, takes it off.
var overwatching := false:
	set(value):
		if overwatching == value:
			return
		overwatching = value
		if model != null:
			model.overwatching = value
		overwatch_changed.emit(overwatching)

## Everything the unit carries into battle, whose tags decide which actions it
## has ([method UnitAction.is_granted]): [member character]'s equipment, copied
## as it enters the map, or without a character just its [member weapon]. It
## only ever changes as the unit uses something up ([method use_up]).
var equipment: Array[Item] = []
## The melee weapon the unit strikes with: the first one [member equipment]
## holds, Weapon 1 before Weapon 2. Null when it has none, and so no Strike.
var melee_weapon: Weapon
## The grenade the unit throws next: the first one [member equipment] holds,
## Item 1 before Item 2 before Item 3. Null once it has none left, and so no
## Throw Grenade.
var grenade: Grenade

## The figure the unit is seen as, its Model child. Null in a scene that gives
## it none, and once the unit has died: it has broken apart then.
var model: CharacterModel

## The tween walking the unit or dropping it. Null, or finished, while it
## stands still.
var _motion: Tween
## The body debris bumps off. Null for a unit with no Model to shape it by.
var _body: AnimatableBody3D
## The last hit, as [method take_damage] was given it: where it came from
## (unknown, infinite, until the unit is first hit), whether it was a blast,
## where on the body it landed (infinite if no one chose) and the way a blade
## swept across it. Only for show: if it kills the unit, its figure breaks
## apart the way it went ([method TerrainDestruction.break_figure]).
var hit_from := Vector3.INF
var hit_blasted := false
var hit_at := Vector3.INF
var hit_sweep := Vector3.ZERO

## Placeholder identity colour, taken from the Model child's material.
var color: Color:
	get:
		var body := model if model != null else get_node_or_null(^"Model") as CharacterModel
		return body.tint() if body != null else Color.WHITE


func _ready() -> void:
	add_to_group(GROUP)
	model = get_node_or_null(^"Model") as CharacterModel
	# Before health is filled, which reads the character's max_health.
	if character != null:
		_take_character()
	else:
		if weapon == null:
			weapon = PLAIN_RIFLE
		equipment = [weapon]
		if weapon.has_tag(Item.MELEE):
			melee_weapon = weapon
	# A character comes into battle as hurt as they left the last one, but
	# alive: anyone on the roster is.
	health = maxi(character.health, 1) if character != null else max_health
	actions_remaining = actions_per_turn
	_dress()
	_add_bodies()


## Refills the action budget and the reaction at the start of this unit's
## turn, and stands down any overwatch left over from the last one.
func start_turn() -> void:
	actions_remaining = actions_per_turn
	reaction_available = true
	overwatching = false


## Whether anything the unit carries is tagged [param tag], such as
## [constant Item.GUN].
func carries(tag: StringName) -> bool:
	for item in equipment:
		if item != null and item.has_tag(tag):
			return true
	return false


## Spends [param cost] actions. Returns false, spending nothing, if there are
## not enough left.
func spend_actions(cost: int = 1) -> bool:
	if cost > actions_remaining:
		return false
	actions_remaining -= cost
	return true


## Uses up the unit's reaction. Returns false if it has already been used.
func spend_reaction() -> bool:
	if not reaction_available:
		return false
	reaction_available = false
	return true


## Takes [param amount], less the unit's [member defense], off its health, and
## takes the unit off the map if that finishes it. Returns the damage taken,
## which is 0 for a hit the defense stops entirely. Every hit comes through
## here, so defense counts against all of them.
##
## [param from] is where the hit came from, in the world, and [param blasted]
## says it was a blast. [param at] is where on the body it landed, if the one
## dealing it chose ([method CharacterModel.pick_wound]), and [param sweep] the
## way a slash was moving across the body as it landed. They change only how
## the unit is seen to take it: its body flinches away from the hit, or breaks
## apart the way it went, and bleeds where it was hit ([signal hurt]).
func take_damage(amount: int, from := Vector3.INF, blasted := false, at := Vector3.INF, sweep := Vector3.ZERO) -> int:
	var taken := damage_from(amount)
	hit_from = from
	hit_blasted = blasted
	hit_at = at
	hit_sweep = sweep
	if taken > 0:
		hurt.emit(taken, from, at, blasted, sweep)
	health -= taken
	if health <= 0:
		die()
	elif model != null and from.is_finite():
		model.flinch(from)
	return taken


## What a hit of [param amount] would take off the unit's health: the amount
## less its [member defense], down to none. What [method take_damage] takes,
## so a throw can show each unit it would catch what it would do to them.
func damage_from(amount: int) -> int:
	return maxi(amount - defense, 0)


## Takes [param shot] with [param chance] in 100 of landing, and returns how it
## went once the round has landed. The player's [ShootAction], the enemy turn
## and overwatch fire all come through here, so a shot means the same thing
## whoever takes it.
##
## Everything is settled as the round is fired: the roll decides whether it
## lands, and [Ballistics] where it goes. [param show_rounds], if given, is
## called with the [Ballistics.Outcome] at that moment and awaited, so whoever
## is drawing the shot holds the landing until the round is seen to arrive.
## On landing the target takes the weapon's damage if the shot hit, less its
## defense ([member Ballistics.Outcome.damage]), and each round's flight and
## any terrain it struck are reported to [param grid]: the flight for the
## loose debris it tears through on the way ([method CombatGrid.fly]).
##
## It is fired once the unit's figure has turned to the target and raised its
## gun, which it has already if the shot was lined up for it ([method aim_at]).
## A miss is ducked. A hit is seen to land somewhere on the side of the
## target's figure facing the gun, chosen as it is fired
## ([member Ballistics.Path.wound]): the tracer is drawn there, and the target
## bleeds there.
func shoot_at(
	shot: LineOfSight.Shot, chance: int, grid: CombatGrid, show_rounds := Callable()
) -> Ballistics.Outcome:
	if model != null:
		await model.take_aim(aim_point(shot.target, grid))
	var hit := HitChance.roll(chance)
	var outcome := Ballistics.new(grid).fire(self, shot, hit)
	if model != null:
		outcome.muzzle = model.fire()
	# A hit is seen to land on the body somewhere facing the gun, not always
	# at the eye the round flies to; the tracer is drawn there.
	var fired_from: Vector3 = outcome.muzzle if outcome.muzzle != null else outcome.paths[0].from
	if outcome.hit and is_instance_valid(shot.target) and shot.target.model != null:
		for path in outcome.paths:
			var wound := shot.target.model.pick_wound(fired_from)
			if wound.is_finite():
				path.wound = wound
	if show_rounds.is_valid():
		await show_rounds.call(outcome)
	if is_instance_valid(shot.target):
		if outcome.hit:
			var wound: Variant = outcome.paths[0].wound
			outcome.damage = shot.target.take_damage(weapon.damage, fired_from, false, wound if wound != null else Vector3.INF)
		else:
			shot.target.dodge()
	for path in outcome.paths:
		# Along the line its tracer was drawn, for the debris it tears through.
		grid.fly(fired_from, path.drawn_to(), weapon.environment_damage)
		if path.struck != null:
			grid.strike(path.struck, weapon.environment_damage)
	return outcome


## Strikes [param target], standing next to this unit, with
## [member melee_weapon], with [param chance] in 100 of landing. Returns the
## damage the target took, or null for a miss: the weapon's damage with this
## unit's [member strength] added first, then the target's defense taken off
## as with a shot. The player's [StrikeAction] comes through here, as every
## shot comes through [method shoot_at], so a strike means the same thing
## whoever makes one.
##
## Nothing flies, and a miss touches nothing: no terrain is struck either way.
## It lands as the unit's swing does, so await it; [method recover] waits out
## the follow-through after. A miss is ducked.
func strike(target: Unit, chance: int) -> Variant:
	if model != null:
		await model.strike(target.global_position)
	if not is_instance_valid(target):
		return null
	if not HitChance.roll(chance):
		target.dodge()
		return null
	# Where the blade lands, and the way it sweeps across the body, for the
	# wound and its spray. Only for show.
	var at := Vector3.INF
	var sweep := Vector3.ZERO
	var from := global_position + Vector3.UP * STRIKE_HEIGHT
	if model != null:
		sweep = model.swing()
	if target.model != null:
		at = target.model.pick_wound(from)
	return target.take_damage(melee_weapon.damage + strength, from, false, at, sweep)


## Throws [member grenade] along [param throw] and returns what its blast did,
## once it has gone off: a [code][over, damage][/code] pair for everyone it
## caught, [code]over[/code] being the eye of the unit as it stood and
## [code]damage[/code] what it took. The player's [ThrowGrenadeAction] comes
## through here, as every shot comes through [method shoot_at], so a throw
## means the same thing whoever makes one.
##
## Nothing is rolled: a grenade goes off where it is thrown, as in XCOM 2. The
## unit's figure winds up and throws, and the grenade is used up the moment it
## leaves the hand ([method use_up]). [param show_flight], if given, is called
## then with the throw, the grenade and where the hand let go of it, and
## awaited, so whoever is drawing the flight holds the blast until the grenade
## is seen to arrive. Then everyone the blast catches
## ([method Throwing.caught]), this unit included, takes the grenade's damage
## less their defense, and the blast is reported to [param grid] for the
## terrain to break.
func throw_at(throw: Throwing.Throw, grid: CombatGrid, show_flight := Callable()) -> Array:
	var thrown := grenade
	if thrown == null:
		return []
	var release := throw.start
	if model != null:
		release = await model.throw_toward(throw.end)
	use_up(thrown)
	if show_flight.is_valid():
		await show_flight.call(throw, thrown, release)
	var landed := []
	for unit in Throwing.new(grid).caught(throw.target, thrown.blast_size):
		# Read where to call it now: a unit the blast kills is gone after.
		var over := grid.cell_center(LineOfSight.eye_cell(grid.tile_at(unit.global_position)))
		landed.append([over, unit.take_damage(thrown.damage, throw.end, true)])
	grid.blast(
		throw.end,
		Throwing.blast_cells(throw.target, thrown.blast_size),
		thrown.environment_damage,
		thrown.blast_force,
	)
	return landed


## Takes [param item] out of [member equipment] for good, used up, as a
## grenade is once thrown, and says so ([signal used_up]) for the character's
## gear to follow. With its last grenade gone, the unit has no Throw Grenade.
func use_up(item: Item) -> void:
	var index := equipment.find(item)
	if index < 0:
		return
	equipment.remove_at(index)
	grenade = _first_grenade()
	_dress()
	used_up.emit(item)


## Removes the unit from play. It leaves its groups at once rather than when
## the node is freed, so nothing shoots at it or walks around it in the
## meantime. Its figure breaks apart as [signal died] goes out, the way the hit
## that killed it went ([method TerrainDestruction.break_figure]), leaving
## its lumps and its gear on the map; with nothing on the map to break it, it
## just goes.
func die() -> void:
	died.emit()
	for group in get_groups():
		remove_from_group(group)
	if model != null:
		model.break_apart()
		model = null
	queue_free()


## Walks through [param points] in order, taking [param seconds_per_step]
## for each. Await it to wait until the unit arrives. Its figure faces the
## way it goes, unless [param keep_facing], as a unit stepping out of cover
## to shoot keeps facing its target.
func walk(points: Array[Vector3], seconds_per_step: float, keep_facing := false) -> void:
	var tween := start_walk(points, seconds_per_step, keep_facing)
	if tween != null:
		await tween.finished


## Starts the same walk as [method walk] and hands back the tween playing it,
## for a caller that needs to slow the walk down or hold it still. Null if
## there is nowhere to go. The figure runs as fast as the tween moves it, so
## it slows and stops with it.
##
## The tween dies with the unit, without ever finishing, so a caller whose
## walker might be killed on the way must not wait on [signal Tween.finished].
func start_walk(points: Array[Vector3], seconds_per_step: float, keep_facing := false) -> Tween:
	if points.is_empty():
		return null
	var tween := create_tween()
	for point in points:
		tween.tween_property(self, ^"global_position", point, seconds_per_step)
	_motion = tween
	if model != null:
		model.begin_walk(points, keep_facing)
	return tween


## Whether the unit is walking or dropping.
func is_moving() -> bool:
	return _motion != null and _motion.is_running()


## Drops the unit straight down to [param point], gathering speed as it
## falls, as it does when the ground under it gives way. [param rubble] is the
## debris of what it stood on, by physics body, which falls with it: the unit
## passes through those pieces for good, since landing on the heap from above
## it would grind them into the ground.
func drop_to(point: Vector3, rubble: Array[RID] = []) -> void:
	var height := maxf(global_position.y - point.y, 0.0)
	if _motion != null:
		_motion.kill()
	_motion = create_tween()
	var fall := _motion.tween_property(self, ^"global_position", point, sqrt(2.0 * height / FALL_ACCELERATION))
	fall.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	pass_through(rubble)
	if model != null:
		model.fall()


## Lets the unit pass through [param bodies], physics bodies, for good: more of
## the rubble it is dropping through, left by a block that fell with it and
## broke on the way. By body rather than node, since the voxels broken off a
## block that wears away have none ([VoxelDebris]).
func pass_through(bodies: Array[RID]) -> void:
	if _body == null:
		return
	for body in bodies:
		if body.is_valid():
			PhysicsServer3D.body_add_collision_exception(_body.get_rid(), body)


## Turns the unit's figure to [param point] in the world, a target's eye, and
## raises its gun at it, as a shot at it is lined up. Lined up on another, it
## turns to that one. Only for show, as is everything down to
## [method recover]: the rules never ask the figure anything.
func aim_at(point: Vector3) -> void:
	if model != null:
		model.aim_at(point)


## Where to aim at [param target] on [param grid]: its eye, wherever it stands,
## between tiles if a reaction catches it walking.
func aim_point(target: Unit, grid: CombatGrid) -> Vector3:
	var tile := grid.tile_at(target.global_position)
	return target.global_position + (grid.cell_center(LineOfSight.eye_cell(tile)) - grid.tile_position(tile))


## Squares the unit's figure up to [param point] in the world, its melee
## weapon drawn, as a strike is lined up.
func ready_strike(point: Vector3) -> void:
	if model != null:
		model.ready_strike(point)


## Has the unit's figure take a grenade in hand, turned to [param point] in
## the world as a throw is lined up there, or facing as it is if null.
func ready_throw(point: Variant = null) -> void:
	if model != null:
		model.ready_throw(point)


## Has the unit's figure put away what it had ready for an action: lower its
## gun, sling its sword, hook its grenade back on.
func stand_easy() -> void:
	if model != null:
		model.stand_easy()


## Has the unit's figure cheer, its side having won.
func celebrate() -> void:
	if model != null:
		model.celebrate()


## Has the unit's figure duck a shot or blow that missed it.
func dodge() -> void:
	if model != null:
		model.dodge()


## Waits until the unit's figure has finished the blow or throw it is playing:
## the follow-through after the moment that counted.
func recover() -> void:
	if model != null:
		await model.recover()


## Takes on [member character]'s name, colour, stats and equipment, shooting
## with the first gun in it, striking with the first melee weapon and throwing
## the first grenade. Copied once, when the unit enters the map: the
## rules read the unit, never the character. Its health starts at the
## character's, wounds and all.
func _take_character() -> void:
	display_name = character.display_name
	max_health = character.max_health
	defense = character.total_defense
	move_range = character.move_range
	aim = character.aim
	melee_accuracy = character.melee_accuracy
	strength = character.strength
	evasion = character.evasion
	equipment.clear()
	weapon = null
	melee_weapon = null
	for slot in Character.slots:
		var item := character.get(slot[1]) as Item
		if item == null:
			continue
		equipment.append(item)
		if weapon == null and item is Weapon and item.has_tag(Item.GUN):
			weapon = item as Weapon
		if melee_weapon == null and item is Weapon and item.has_tag(Item.MELEE):
			melee_weapon = item as Weapon
	grenade = _first_grenade()
	_paint(character.color)


## The first grenade [member equipment] holds, or null.
func _first_grenade() -> Grenade:
	for item in equipment:
		if item is Grenade and item.has_tag(Item.GRENADE):
			return item as Grenade
	return null


## Colours the Model child [param tint], on a copy of its material so a
## material another unit shares is left alone.
func _paint(tint: Color) -> void:
	if model != null:
		model.paint(tint)


## Shows on the unit's figure what it carries: its gun in hand, its melee
## weapon, and a grenade on the belt for each it has left.
func _dress() -> void:
	if model == null:
		return
	var grenades: Array[Item] = []
	for item in equipment:
		if item is Grenade:
			grenades.append(item)
	model.equip(weapon, melee_weapon, grenades)


## Gives the unit an upright cylinder round its figure for mouse clicks to
## land on, and a frictionless capsule round it for debris to bump off, as
## thick as the figure's body and clear of the ground by
## [constant BODY_CLEARANCE]. Both move with the unit however it is moved, and
## neither turns with the figure.
func _add_bodies() -> void:
	if model == null:
		return
	var box := model.transform * model.body_box()
	if not box.has_volume():
		return

	var cylinder := CylinderShape3D.new()
	cylinder.radius = PICK_RADIUS
	cylinder.height = box.end.y
	var pick_shape := CollisionShape3D.new()
	pick_shape.shape = cylinder
	pick_shape.position = Vector3(0.0, box.end.y * 0.5, 0.0)
	var pick := StaticBody3D.new()
	pick.name = &"PickBody"
	pick.collision_layer = PICK_LAYER
	pick.collision_mask = 0
	pick.add_child(pick_shape)
	add_child(pick)

	var capsule := CapsuleShape3D.new()
	capsule.radius = minf(box.size.x, box.size.z) * 0.5
	capsule.height = maxf(box.end.y - BODY_CLEARANCE, capsule.radius * 2.0)
	var shape := CollisionShape3D.new()
	shape.shape = capsule
	shape.position = Vector3(box.get_center().x, BODY_CLEARANCE + capsule.height * 0.5, box.get_center().z)
	_body = AnimatableBody3D.new()
	_body.name = &"Body"
	_body.collision_layer = BODY_LAYER
	_body.collision_mask = 0
	# Frictionless, so debris that lands on a unit slides off it. With friction
	# a board can balance on the round top of the capsule and rock there for
	# good, keeping every piece it touches awake.
	var material := PhysicsMaterial.new()
	material.friction = 0.0
	_body.physics_material_override = material
	# Not synced to physics: that takes the body's place from the physics
	# server, and a body moved by its parent, as this one is by the unit's
	# tweens, would be left behind.
	_body.sync_to_physics = false
	_body.add_child(shape)
	add_child(_body)
