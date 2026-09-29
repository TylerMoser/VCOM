## A character on the combat map: its health, its per-turn action budget and
## its reaction.
##
## A squad member is someone on the roster: given a [member character], it
## takes its name, colour, stats (health, move, aim, evasion) and weapon from them,
## painting its Mesh child. Without one (enemies, the test harness) the
## scene's values and the Mesh's material stand.
## UI reads [member color] until real portraits exist.
class_name Unit
extends Node3D

signal health_changed(health: int, max_health: int)
signal actions_changed(remaining: int, per_turn: int)
signal reaction_changed(available: bool)
signal overwatch_changed(watching: bool)
## Emitted as the unit leaves the map, while it is still whole enough to be
## read from. Whoever was holding on to it should let go.
signal died

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

## Replaced by [member character]'s name when the unit has one.
@export var display_name := "Unit"
## Who this unit is on the roster: the same resource [member Campaign.roster]
## holds, so the two stay linked.
@export var character: Character
## Replaced by [member character]'s, as are move range, aim and evasion.
@export var max_health := 10
@export var actions_per_turn := 3
## Tiles the unit can walk for each action point spent moving.
@export var move_range := 4
## How far the unit can see, and so shoot, in tiles.
@export var sight_range := 20
## The gun this unit shoots with. A plain rifle if the scene leaves it unset.
## Replaced by [member character]'s Weapon 1 when the unit has one.
@export var weapon: Weapon
## What decides this unit's actions when the computer plays it. The squad
## leaves it empty; an enemy without one sits its turns out.
@export var ai: EnemyAI

@export_group("Marksmanship")
## Chance to hit before anything about the shot is taken into account.
@export var aim := 90
## Taken off the chance of anyone shooting at this unit.
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
		overwatch_changed.emit(overwatching)

## The tween walking the unit or dropping it. Null, or finished, while it
## stands still.
var _motion: Tween
## The body debris bumps off. Null for a unit with no Mesh to shape it by.
var _body: AnimatableBody3D

## Placeholder identity colour, taken from the Mesh child's material.
var color: Color:
	get:
		var mesh := get_node_or_null(^"Mesh") as MeshInstance3D
		if mesh != null:
			var material := mesh.get_active_material(0) as BaseMaterial3D
			if material != null:
				return material.albedo_color
		return Color.WHITE


func _ready() -> void:
	add_to_group(GROUP)
	# Before health is filled, which reads the character's max_health.
	if character != null:
		_take_character()
	health = max_health
	actions_remaining = actions_per_turn
	if weapon == null:
		weapon = Weapon.new()
	_add_bodies()


## Refills the action budget and the reaction at the start of this unit's
## turn, and stands down any overwatch left over from the last one.
func start_turn() -> void:
	actions_remaining = actions_per_turn
	reaction_available = true
	overwatching = false


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


## Takes [param amount] off the unit's health, and takes the unit off the map
## if that finishes it.
func take_damage(amount: int) -> void:
	health -= amount
	if health <= 0:
		die()


## Takes [param shot] with [param chance] in 100 of landing, and returns how it
## went once the round has landed. The player's [ShootAction], the enemy turn
## and overwatch fire all come through here, so a shot means the same thing
## whoever takes it.
##
## Everything is settled as the round is fired: the roll decides whether it
## lands, and [Ballistics] where it goes. [param show_rounds], if given, is
## called with the [Ballistics.Outcome] at that moment and awaited, so whoever
## is drawing the shot holds the landing until the round is seen to arrive.
## On landing the target takes the weapon's damage if the shot hit, and any
## terrain a round struck is reported to [param grid].
func shoot_at(
	shot: LineOfSight.Shot, chance: int, grid: CombatGrid, show_rounds := Callable()
) -> Ballistics.Outcome:
	var hit := HitChance.roll(chance)
	var outcome := Ballistics.new(grid).fire(self, shot, hit)
	if show_rounds.is_valid():
		await show_rounds.call(outcome)
	if outcome.hit and is_instance_valid(shot.target):
		shot.target.take_damage(weapon.damage)
	for path in outcome.paths:
		if path.struck != null:
			grid.strike(path.struck, weapon.environment_damage)
	return outcome


## Removes the unit from play. It leaves its groups at once rather than when
## the node is freed, so nothing shoots at it or walks around it in the
## meantime.
func die() -> void:
	died.emit()
	for group in get_groups():
		remove_from_group(group)
	queue_free()


## Walks through [param points] in order, taking [param seconds_per_step]
## for each. Await it to wait until the unit arrives.
func walk(points: Array[Vector3], seconds_per_step: float) -> void:
	var tween := start_walk(points, seconds_per_step)
	if tween != null:
		await tween.finished


## Starts the same walk as [method walk] and hands back the tween playing it,
## for a caller that needs to slow the walk down or hold it still. Null if
## there is nowhere to go.
##
## The tween dies with the unit, without ever finishing, so a caller whose
## walker might be killed on the way must not wait on [signal Tween.finished].
func start_walk(points: Array[Vector3], seconds_per_step: float) -> Tween:
	if points.is_empty():
		return null
	var tween := create_tween()
	for point in points:
		tween.tween_property(self, ^"global_position", point, seconds_per_step)
	_motion = tween
	return tween


## Whether the unit is walking or dropping.
func is_moving() -> bool:
	return _motion != null and _motion.is_running()


## Drops the unit straight down to [param point], gathering speed as it
## falls, as it does when the ground under it gives way. [param rubble] is the
## debris of what it stood on, which falls with it: the unit passes through
## those pieces for good, since landing on the heap from above it would grind
## them into the ground.
func drop_to(point: Vector3, rubble: Array[PhysicsBody3D] = []) -> void:
	var height := maxf(global_position.y - point.y, 0.0)
	if _motion != null:
		_motion.kill()
	_motion = create_tween()
	var fall := _motion.tween_property(self, ^"global_position", point, sqrt(2.0 * height / FALL_ACCELERATION))
	fall.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	pass_through(rubble)


## Lets the unit pass through [param bodies] for good: more of the rubble it is
## dropping through, left by a block that fell with it and broke on the way.
func pass_through(bodies: Array[PhysicsBody3D]) -> void:
	if _body == null:
		return
	for body in bodies:
		if is_instance_valid(body):
			_body.add_collision_exception_with(body)


## Takes on [member character]'s name, colour, stats and Weapon 1 (a plain
## rifle if that slot is empty). Copied once, when the unit enters the map:
## the rules read the unit, never the character.
func _take_character() -> void:
	display_name = character.display_name
	max_health = character.max_health
	move_range = character.move_range
	aim = character.aim
	evasion = character.evasion
	weapon = character.weapon_1
	_paint(character.color)


## Colours the Mesh child [param tint], on a copy of its material so a
## material another unit shares is left alone.
func _paint(tint: Color) -> void:
	var mesh := get_node_or_null(^"Mesh") as MeshInstance3D
	if mesh == null:
		return
	var material := mesh.get_active_material(0) as BaseMaterial3D
	material = material.duplicate() if material != null else StandardMaterial3D.new()
	material.albedo_color = tint
	mesh.set_surface_override_material(0, material)


## Gives the unit a body shaped like its Mesh child for mouse clicks to land
## on, and a frictionless capsule round it for debris to bump off, clear of the
## ground by [constant BODY_CLEARANCE]. Both move with the unit however it is
## moved.
func _add_bodies() -> void:
	var mesh := get_node_or_null(^"Mesh") as MeshInstance3D
	if mesh == null or mesh.mesh == null:
		return

	var pick_shape := CollisionShape3D.new()
	pick_shape.shape = mesh.mesh.create_convex_shape()
	var pick := StaticBody3D.new()
	pick.name = &"PickBody"
	pick.collision_layer = PICK_LAYER
	pick.collision_mask = 0
	pick.transform = mesh.transform
	pick.add_child(pick_shape)
	add_child(pick)

	var box := mesh.transform * mesh.mesh.get_aabb()
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
