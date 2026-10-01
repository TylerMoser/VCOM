## A character's body on the combat map: the rigged voxel figure a [Unit]
## wears, the gear it is seen carrying, and what it is seen doing.
## [code]BakeCharacter.gd[/code] builds it from the model's voxels as
## [code]Scenes/BaseCharacter.tscn[/code].
##
## It is only for show, like debris: the rules read the unit, never its body.
## Most of what it does follows from watching its unit move. It runs while the
## unit walks, as fast as the unit goes, so its feet keep up with a reaction's
## slow motion and stop dead while a walk is held. It faces the way it goes, or
## keeps facing its target while it steps out to shoot. It hops on to and off
## ledges, and flails while the floor drops away under it. The rest the unit
## asks for: aiming while a shot is lined up, the kick of a shot, a sword
## drawn and swung, a grenade wound back and thrown, a flinch, a duck, a
## cheer. Between actions [Postures] says which way it faces and whether it
## kneels behind low cover or braces against high.
##
## Its gear is its unit's, each item shown as its [member Item.model]: the gun
## in its hands, a sword it carries as well slung across its back until it is
## drawn, and up to three grenades on its belt.
##
## When the unit dies its body goes limp, out from under the unit, which is
## gone, and stays where it falls: a [PhysicalBoneSimulator3D] takes over from
## the animations, knocked the way the killing blow came, and a blast throws
## it about as it does debris.
class_name CharacterModel
extends Node3D

## What the figure has made ready, which decides the pose it holds.
enum Readiness { NONE, AIM, MELEE, THROW, CHEER }

## Every fallen body, for a blast to throw about.
const CORPSES := &"corpses"
## How fast it turns on the spot, in degrees a second, and while it walks, in
## degrees a tile walked, so a slowed walk turns slowly too.
const TURN_SPEED := 600.0
const TURN_PER_TILE := 600.0
## Within this many degrees of facing what it turns to, it counts as facing it.
const FACING_TOLERANCE := 12.0
## Seconds the base pose takes to cross-fade, which is how long raising a gun
## to aim takes. Matches the tree's [code]stance[/code] transition.
const RAISE_SECONDS := 0.22
## Seconds a call that turns the body first waits at most for it to come round.
const TURN_TIMEOUT := 0.5
## How high a hop up on to a ledge rises above the straight climb at its
## middle, and a hop down off one above the drop, in cells. Up has to clear the
## edge of the block it climbs.
const HOP_UP := 0.35
const HOP_DOWN := 0.15
## Faster than this across the ground, in cells a second, counts as running.
const MOVING_SPEED := 0.05
## How fast the blends between standing, running and falling follow, a second.
const BLEND_RATE := 12.0
## The speed a killing shot or blow knocks the body with, in cells a second,
## mostly to the upper body, and a blast's (a blast's own push comes on top:
## see [method blast]).
const KNOCK := 3.6
const BLAST_KNOCK := 1.2
## How each part of the body takes a killing blow, as a share of the knock:
## the upper body is thrown, the hips follow, and the shins are kicked the
## other way, so the legs go out from under it rather than leaving it stood
## stiffly on its feet.
const KNOCK_SHARES := {
	&"Hips": 0.5, &"Spine": 1.0, &"Chest": 1.0, &"Neck": 1.0,
	&"LeftUpperArm": 0.8, &"RightUpperArm": 0.8, &"LeftLowerArm": 0.6, &"RightLowerArm": 0.6,
	&"LeftUpperLeg": 0.0, &"RightUpperLeg": 0.0, &"LeftLowerLeg": -0.7, &"RightLowerLeg": -0.7,
}
## The physics layers a fallen body is on and collides with: it is debris
## among debris, landing on terrain and shoved aside by the living.
const FALLEN_LAYER := 1 << 2
const FALLEN_MASK := (1 << 0) | (1 << 2) | (1 << 3)
## How far a body may fall below where it went down before it is taken away,
## in cells: off the edge of the map.
const FALL_LIMIT := 30.0
## Grenades shown on the belt at most.
const BELT := 3

## The body's material: a flat colour for now (see [member Unit.color]).
@export var body_material: Material:
	set(value):
		body_material = value
		if _body != null:
			_body.set_surface_override_material(0, body_material)

## What it has ready. Set through [method aim_at], [method ready_strike],
## [method ready_throw], [method celebrate] and [method stand_easy].
var readiness := Readiness.NONE
## The cover it holds between actions, from [Postures]: crouched behind low
## cover, braced against high.
var cover := LineOfSight.Cover.NONE
## Whether its unit is on overwatch, which raises its gun.
var overwatching := false
## Whether it has fallen, and is a ragdoll now.
var dead := false

var _skeleton: Skeleton3D
var _body: MeshInstance3D
var _tree: AnimationTree
var _aim: Node
var _ragdoll: PhysicalBoneSimulator3D

## The stance its hands are in: [code]rifle[/code] with a gun, else
## [code]melee[/code] with a sword, else [code]unarmed[/code].
var _stance := &"unarmed"
## Whether a gun carrier has drawn its sword, its gun slung on its back.
var _drawn := false
var _gun: Node3D
var _sword: Node3D
## Grenade props, one for each grenade the unit carries (the first
## [constant BELT] shown), and whether the first is in the left hand.
var _grenades: Array[Node3D] = []
var _holding_grenade := false

## The way it is turning to face, as a yaw about the vertical (0 faces +z).
var _yaw_target := 0.0
## What it aims or looks at, in the world, while it has something ready; and
## what [Postures] says it should keep an eye on otherwise.
var _aim_point: Variant = null
var _watch_point: Variant = null
## The seconds since its readiness last changed.
var _readied_for := 0.0
## Set while putting its things away waits for the end of the frame: an
## action that ends and begins again at once, as a shot does between shots,
## readies them again before then and calls it off, so the gun never drops.
var _easing := false

## Watching the unit move: where it was last frame, and how fast and which
## way it went across the ground since, in cells a second.
var _last_position := Vector3.ZERO
var _speed := 0.0
var _velocity := Vector3.ZERO
## The walk it is on: the points, and how far along it is, and whether it
## keeps its facing as it goes (stepping out to shoot).
var _walk: Array[Vector3] = []
var _walk_from := Vector3.ZERO
var _walk_index := 0
var _strafe := false
var _falling := false
var _blends := {&"move": 0.0, &"air": 0.0}
## The base pose and run last asked of the tree, to ask only on a change.
var _base := &""
var _run := &""
## Seconds left of the act (a strike, throw or draw) playing over the base.
var _acting := 0.0
## The speed the run cycles were made for, in cells a second, from their
## metadata: what a speed of 1 plays them at.
var _run_speed := 5.0


func _ready() -> void:
	_skeleton = get_node_or_null(^"Skeleton3D") as Skeleton3D
	_body = get_node_or_null(^"Skeleton3D/Body") as MeshInstance3D
	_tree = get_node_or_null(^"AnimationTree") as AnimationTree
	_aim = get_node_or_null(^"Skeleton3D/Aim")
	_ragdoll = get_node_or_null(^"Skeleton3D/Ragdoll") as PhysicalBoneSimulator3D
	if _skeleton == null or _body == null or _tree == null:
		push_error("CharacterModel: '%s' is missing its Skeleton3D, Body or AnimationTree; rebake it." % name)
		set_process(false)
		return
	if body_material != null:
		_body.set_surface_override_material(0, body_material)
	var run := _tree.get_animation(&"run_rifle")
	if run != null:
		_run_speed = run.get_meta(&"speed", _run_speed)
	_yaw_target = rotation.y
	_last_position = _ground()
	_update_tree(0.0)


func _process(delta: float) -> void:
	if dead:
		return
	_readied_for += delta
	_acting = maxf(_acting - delta, 0.0)
	var unit := get_parent() as Unit
	var walking := unit != null and unit.is_moving()

	var now := _ground()
	var moved := now - _last_position
	_last_position = now
	var across := Vector2(moved.x, moved.z)
	_speed = across.length() / delta if delta > 0.0 else 0.0
	_velocity = Vector3(moved.x, 0.0, moved.z) / delta if delta > 0.0 else Vector3.ZERO
	if not walking:
		_walk.clear()
		_strafe = false
		if _falling:
			_falling = false
			_react(&"land")

	var turning_to := _yaw_target
	if walking and not _strafe and not _falling and _speed > MOVING_SPEED:
		turning_to = atan2(across.x, across.y)
		_yaw_target = turning_to
	elif _aim_point != null:
		var toward: Vector3 = (_aim_point as Vector3) - global_position
		if Vector2(toward.x, toward.z).length() > 0.05:
			turning_to = atan2(toward.x, toward.z)
			_yaw_target = turning_to
	var turn := TURN_PER_TILE * across.length() if walking and not _strafe else TURN_SPEED * delta
	rotation.y = rotate_toward(rotation.y, turning_to, deg_to_rad(maxf(turn, TURN_SPEED * delta * 0.25)))

	var hop := _hop(now) if walking else Vector2.ZERO
	position.y = hop.x
	_tree.set(&"parameters/hop/blend_amount", hop.y)
	_blend(&"move", 1.0 if walking and not _falling else 0.0, delta)
	_blend(&"air", 1.0 if _falling else 0.0, delta)
	_update_tree(delta)


## Starts the unit's walk through [param points]. Facing the way it goes,
## unless [param keep_facing], as a unit stepping out to shoot keeps facing its
## target.
func begin_walk(points: Array[Vector3], keep_facing := false) -> void:
	_walk = points.duplicate()
	_walk_from = _ground()
	_walk_index = 0
	_strafe = keep_facing


## The floor under it is gone: it falls until its unit lands, and lands with
## its knees giving.
func fall() -> void:
	_falling = true


## Turns to face [param point] in the world, and keeps facing it while it
## stands.
func face(point: Vector3) -> void:
	var toward := point - global_position
	if Vector2(toward.x, toward.z).length() > 0.05:
		_yaw_target = atan2(toward.x, toward.z)


## Turns to face [param yaw], from [Postures], and settles into [param held]
## cover there, with an eye on [param watch] if given. [param at_once] faces
## that way straight off, as a battle begins, rather than turning to it.
func settle(held: LineOfSight.Cover, yaw: float, watch: Variant, at_once := false) -> void:
	cover = held
	_yaw_target = yaw
	_watch_point = watch
	if at_once:
		rotation.y = yaw


## Whether it is standing about with nothing to do: not moving, falling or
## fallen, nothing ready and nothing playing. [Postures] only moves it then.
func is_idle() -> bool:
	return not dead and readiness == Readiness.NONE and _walk.is_empty() and not _falling and _acting <= 0.0


## Raises its gun at [param point], turning to it. Lined up on a new point,
## it turns to that one. Without a gun it just faces it.
func aim_at(point: Vector3) -> void:
	_easing = false
	_aim_point = point
	if _stance == &"rifle":
		_set_readiness(Readiness.AIM)
	face(point)


## Draws its sword, if it carries one slung, and squares up to [param point].
func ready_strike(point: Vector3) -> void:
	_easing = false
	_aim_point = point
	_set_readiness(Readiness.MELEE)
	face(point)


## Takes a grenade off its belt into its left hand, ready to throw at
## [param point] in the world, and turns to it; or, with none yet, ready to
## throw the way it faces.
func ready_throw(point: Variant = null) -> void:
	_easing = false
	if point == null:
		point = global_position + global_basis.z * 3.0
	_aim_point = point
	_set_readiness(Readiness.THROW)
	if not _holding_grenade and not _grenades.is_empty():
		_holding_grenade = true
		_place_gear()
	face(point)


## Raises its weapon to cheer a victory, for as long as it stands.
func celebrate() -> void:
	_easing = false
	_aim_point = null
	_set_readiness(Readiness.CHEER)


## Puts away whatever it had ready: lowers its gun, slings its sword, hooks
## an unthrown grenade back on its belt. At the end of the frame, unless
## something is readied again before then.
func stand_easy() -> void:
	if readiness == Readiness.NONE:
		_aim_point = null
		return
	_easing = true
	_stand_easy_now.call_deferred()


func _stand_easy_now() -> void:
	if not _easing or dead:
		return
	_easing = false
	_aim_point = null
	_set_readiness(Readiness.NONE)


## Raises its gun at [param point] and returns once it is aimed: turned to it,
## and the gun up. At once if it already was.
func take_aim(point: Vector3) -> void:
	var already := readiness == Readiness.AIM and _readied_for >= RAISE_SECONDS
	aim_at(point)
	if already and _is_facing():
		return
	await _turned(RAISE_SECONDS)


## The kick of a shot, and its flash at the muzzle. Returns where the muzzle
## is, which is where the round's tracer is drawn from.
func fire() -> Vector3:
	_react(&"fire_rifle")
	var muzzle := muzzle_point()
	if _gun != null:
		var flash := MuzzleFlash.new()
		var marker := _gun.get_node_or_null(^"Muzzle") as Node3D
		(marker if marker != null else _gun).add_child(flash)
	return muzzle


## Where its gun's muzzle is in the world, or its eyes without a gun.
func muzzle_point() -> Vector3:
	if _gun != null:
		var marker := _gun.get_node_or_null(^"Muzzle") as Node3D
		if marker != null:
			return marker.global_position
	return global_position + Vector3.UP * 1.3


## Swings at [param point], squaring up to it first, and returns the moment
## the blow lands. The follow-through plays on after; [method recover] waits
## for it.
func strike(point: Vector3) -> void:
	ready_strike(point)
	await _turned(0.0)
	while _acting > 0.0:
		await get_tree().process_frame
	_act(&"strike_sword")
	await _after(_moment(&"strike_sword", &"impact"))


## Winds up and throws its grenade toward [param point], turning to it first,
## and returns the moment it lets go, with where its hand is then: where the
## grenade starts its flight. The follow-through plays on after.
func throw_toward(point: Vector3) -> Vector3:
	ready_throw(point)
	await _turned(0.0)
	while _acting > 0.0:
		await get_tree().process_frame
	var clip := StringName("throw_%s" % _hands())
	_act(clip)
	await _after(_moment(clip, &"release"))
	var hand := _socket(^"LeftHand/GrenadeGrip")
	var release := hand.global_position if hand != null else global_position + Vector3.UP * 1.6
	# It has left the hand: what flies now is the thrown grenade. The next one
	# comes off the belt only when another throw is readied.
	if _holding_grenade and not _grenades.is_empty():
		_grenades[0].visible = false
	_holding_grenade = false
	return release


## Waits for the blow or throw it is playing to finish.
func recover() -> void:
	while _acting > 0.0 and not dead:
		await get_tree().process_frame


## Flinches from a hit that came from [param from] in the world.
func flinch(from: Vector3) -> void:
	var toward := from - global_position
	var front := global_basis.z
	_react(&"hit_front" if Vector2(toward.x, toward.z).dot(Vector2(front.x, front.z)) >= 0.0 else &"hit_back")


## Ducks a round or blow that went wide.
func dodge() -> void:
	_react(&"dodge")


## Shows what its unit carries: [param gun] in its hands, or [param melee]
## if it has no gun (slung on its back if it has both), and a grenade for each
## of [param grenades] on its belt. Called again as the unit uses something
## up.
func equip(gun: Item, melee: Item, grenades: Array[Item]) -> void:
	_stance = &"rifle" if gun != null else (&"melee" if melee != null else &"unarmed")
	if gun == null or melee == null:
		_drawn = false
	_gun = _swap_prop(_gun, gun)
	_sword = _swap_prop(_sword, melee)
	for prop in _grenades:
		prop.queue_free()
	_grenades.clear()
	for item in grenades:
		var prop := _make_prop(item)
		if prop != null:
			_grenades.append(prop)
	if _holding_grenade and _grenades.is_empty():
		_holding_grenade = false
	_place_gear()


## The box the figure fills standing, in its own space: the rest pose's, arms
## out. What its unit shapes its bodies by.
func body_box() -> AABB:
	if _body == null or _body.mesh == null:
		return AABB()
	return _body.mesh.get_aabb()


## The flat colour its body is painted.
func tint() -> Color:
	var material := body_material as BaseMaterial3D
	return material.albedo_color if material != null else Color.WHITE


## Paints its body [param color], on a copy of its material so a material
## another figure shares is left alone.
func paint(color: Color) -> void:
	var material: BaseMaterial3D = StandardMaterial3D.new()
	if body_material is BaseMaterial3D:
		material = body_material.duplicate()
	material.albedo_color = color
	body_material = material


## Goes limp, knocked from [param from] in the world: thrown back by a shot or
## blow, or by a blast if [param blasted]. The body leaves its unit, which is
## about to be freed, for the unit's parent, and lies where it falls from then
## on.
func fall_dead(from: Vector3, blasted: bool) -> void:
	if dead:
		return
	dead = true
	var map := get_parent().get_parent() if get_parent() != null else null
	if map != null:
		reparent(map, true)
	add_to_group(CORPSES)
	_tree.active = false
	if _aim != null:
		_aim.set(&"active", false)
	if _ragdoll == null:
		return
	for node in _ragdoll.get_children():
		var bone := node as PhysicalBone3D
		if bone != null:
			bone.collision_layer = FALLEN_LAYER
			bone.collision_mask = FALLEN_MASK
	_ragdoll.active = true
	_ragdoll.physical_bones_start_simulation()
	var fell_from := global_position.y
	await get_tree().physics_frame
	var away := global_position - from
	away.y = 0.0
	away = away.normalized() if away.length() > 0.01 else -global_basis.z
	var knock := (away + Vector3.UP * (0.6 if blasted else 0.25)).normalized()
	for node in _ragdoll.get_children():
		var bone := node as PhysicalBone3D
		if bone == null:
			continue
		var share: float = KNOCK_SHARES.get(bone.bone_name, 0.5)
		bone.apply_central_impulse(knock * (BLAST_KNOCK if blasted else KNOCK) * share * bone.mass)
	# A body blasted off the edge of the map falls for good: a timer that goes
	# with it looks now and then, and takes it away once it is well below.
	var lookout := Timer.new()
	lookout.wait_time = 1.0
	lookout.autostart = true
	lookout.timeout.connect(_check_on_map.bind(fell_from))
	add_child(lookout)


## Throws this fallen body about with a [Blast] of [param force] from
## [param origin], as a blast throws debris, if any of it lies within
## [param box].
func blast(origin: Vector3, box: AABB, force: float) -> void:
	if not dead or _ragdoll == null:
		return
	for node in _ragdoll.get_children():
		var bone := node as PhysicalBone3D
		if bone == null or not box.has_point(bone.global_position):
			continue
		bone.apply_impulse(Blast.impulse_on(bone, origin, force), Blast.contact(bone, origin) - bone.global_position)


## Takes the body away once it has fallen [constant FALL_LIMIT] cells below
## [param fell_from], the height it went down at: blasted off the edge of the
## map.
func _check_on_map(fell_from: float) -> void:
	var hips := _ragdoll.get_child(0) as Node3D
	if hips != null and hips.global_position.y < fell_from - FALL_LIMIT:
		queue_free()


func _set_readiness(value: Readiness) -> void:
	if readiness == value:
		return
	var was := readiness
	readiness = value
	_readied_for = 0.0
	if _stance == &"rifle" and _sword != null:
		if value == Readiness.MELEE and not _drawn:
			_draw_or_stow(true)
		elif was == Readiness.MELEE and _drawn:
			_draw_or_stow(false)
	if was == Readiness.THROW:
		_holding_grenade = false
	_place_gear()


## Plays drawing (or slinging) the sword, swapping it with the gun at the
## moment the hand is over the shoulder.
func _draw_or_stow(drawing: bool) -> void:
	var clip := &"draw_sword" if drawing else &"stow_sword"
	_act(clip)
	await _after(_moment(clip, &"swap"))
	if dead:
		return
	_drawn = drawing
	_place_gear()


## Puts every prop in its socket for how the figure stands now.
func _place_gear() -> void:
	if _gun != null:
		_put(_gun, ^"Back/RifleSlot" if _drawn else ^"RightHand/RifleGrip")
	if _sword != null:
		_put(_sword, ^"RightHand/SwordGrip" if _stance == &"melee" or _drawn else ^"Back/SwordSlot")
	var on_belt := 0
	for index in _grenades.size():
		var prop := _grenades[index]
		if index == 0 and _holding_grenade:
			_put(prop, ^"LeftHand/GrenadeGrip")
			prop.visible = true
			continue
		prop.visible = on_belt < BELT
		if on_belt < BELT:
			_put(prop, NodePath("Belt/Grenade%d" % (on_belt + 1)))
		on_belt += 1


func _put(prop: Node3D, socket: NodePath) -> void:
	var holder := _socket(socket)
	if holder == null:
		return
	if prop.get_parent() != holder:
		if prop.get_parent() != null:
			prop.get_parent().remove_child(prop)
		holder.add_child(prop)
	prop.transform = Transform3D.IDENTITY


func _socket(path: NodePath) -> Node3D:
	return _skeleton.get_node_or_null(path) as Node3D if _skeleton != null else null


## [param old], the prop shown for an item, replaced by one for [param item],
## or kept if it already shows it.
func _swap_prop(old: Node3D, item: Item) -> Node3D:
	if old != null and item != null and old.get_meta(&"item", null) == item:
		return old
	if old != null:
		old.queue_free()
	return _make_prop(item)


func _make_prop(item: Item) -> Node3D:
	if item == null or item.model == null:
		return null
	var prop := item.model.instantiate() as Node3D
	if prop == null:
		return null
	prop.set_meta(&"item", item)
	return prop


## The stance the hands are in for the base poses: a gun carrier with its
## sword out holds it as a swordsman does.
func _hands() -> StringName:
	return &"melee" if _drawn else _stance


func _base_pose() -> StringName:
	var hands := _hands()
	match readiness:
		Readiness.CHEER:
			return StringName("cheer_%s" % hands)
		Readiness.AIM:
			if _stance == &"rifle":
				return &"aim_rifle"
		Readiness.MELEE:
			return &"ready_melee"
		Readiness.THROW:
			return StringName("ready_throw_%s" % hands)
	if overwatching and hands == &"rifle":
		match cover:
			LineOfSight.Cover.LOW:
				return &"overwatch_crouch_rifle"
			LineOfSight.Cover.HIGH:
				return &"wall_rifle"
			_:
				return &"overwatch_rifle"
	match cover:
		LineOfSight.Cover.LOW:
			return StringName("crouch_%s" % hands)
		LineOfSight.Cover.HIGH:
			return StringName("wall_%s" % hands)
	return StringName("stand_%s" % hands)


func _update_tree(delta: float) -> void:
	var base := _base_pose()
	if base != _base:
		_base = base
		_tree.set(&"parameters/stance/transition_request", String(base))
	var run := StringName("run_%s" % _hands())
	if run != _run:
		_run = run
		_tree.set(&"parameters/run/transition_request", String(run))
	# Which way it runs, in its own space (+y forward): forward, unless it
	# keeps facing its target as it steps, when it may go back or to a side.
	var heading := Vector2(0.0, 1.0)
	if _strafe and _speed > MOVING_SPEED:
		var local := global_basis.orthonormalized().inverse() * _velocity
		heading = Vector2(local.x, local.z).normalized()
	_tree.set(&"parameters/run_rifle/blend_position", heading)
	_tree.set(&"parameters/run_scale/scale", _speed / _run_speed)
	_tree.set(&"parameters/move/blend_amount", _blends[&"move"])
	_tree.set(&"parameters/air/blend_amount", _blends[&"air"])

	if _aim != null:
		var aiming := readiness in [Readiness.AIM, Readiness.MELEE, Readiness.THROW] and _aim_point != null
		var target_weight := 1.0 if aiming and readiness == Readiness.AIM else 0.0
		_aim.set(&"aim_weight", move_toward(float(_aim.get(&"aim_weight")), target_weight, delta / RAISE_SECONDS))
		if aiming:
			var toward: Vector3 = (_aim_point as Vector3) - (global_position + Vector3.UP * 1.25)
			_aim.set(&"aim_pitch", atan2(toward.y, Vector2(toward.x, toward.z).length()))
		var look: Variant = _aim_point if aiming else _watch_point
		var look_weight := 0.0 if look == null else (1.0 if aiming else 0.6)
		if look != null:
			_aim.set(&"look_point", look)
		_aim.set(&"look_weight", move_toward(float(_aim.get(&"look_weight")), look_weight, delta * 3.0))


## Where the unit stands, its feet on the floor: the model's own place, less
## any hop it is lifted by.
func _ground() -> Vector3:
	var unit := get_parent() as Node3D
	return unit.global_position if unit != null else global_position


## How far above the straight walk the body is lifted on the step it is
## taking, hopping up or down a level (x), and how far into the tucked hop pose
## it is (y).
func _hop(now: Vector3) -> Vector2:
	while _walk_index < _walk.size():
		var from := _walk_from if _walk_index == 0 else _walk[_walk_index - 1]
		var to := _walk[_walk_index]
		var span := Vector2(to.x - from.x, to.z - from.z)
		var along := 1.0
		if span.length_squared() > 1e-6:
			along = clampf(Vector2(now.x - from.x, now.z - from.z).dot(span) / span.length_squared(), 0.0, 1.0)
		if along >= 0.999 and _walk_index < _walk.size() - 1:
			_walk_index += 1
			continue
		var rise := to.y - from.y
		if absf(rise) < 0.01:
			return Vector2.ZERO
		# Up, it rises early and clears the edge; down, it stays up and drops
		# late. Either way the lift is nothing at the ends of the step.
		var arc := along * (1.0 - along)
		var lift := arc * (rise + 4.0 * HOP_UP if rise > 0.0 else 4.0 * HOP_DOWN - rise)
		return Vector2(lift, sin(PI * along))
	return Vector2.ZERO


func _blend(parameter: StringName, target: float, delta: float) -> void:
	_blends[parameter] = move_toward(_blends[parameter], target, delta * BLEND_RATE)


func _act(clip: StringName) -> void:
	var animation := _tree.get_animation(clip)
	_acting = animation.length if animation != null else 0.0
	_tree.set(&"parameters/act_pick/transition_request", String(clip))
	_tree.set(&"parameters/act/request", AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE)


func _react(clip: StringName) -> void:
	if dead:
		return
	_tree.set(&"parameters/react_pick/transition_request", String(clip))
	_tree.set(&"parameters/react/request", AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE)


## The time of [param marker] in [param clip], from the metadata the bake
## left on it.
func _moment(clip: StringName, marker: StringName) -> float:
	var animation := _tree.get_animation(clip)
	return animation.get_meta(marker, 0.0) if animation != null else 0.0


func _after(seconds: float) -> void:
	if seconds > 0.0:
		await get_tree().create_timer(seconds, false).timeout


func _is_facing() -> bool:
	return absf(angle_difference(rotation.y, _yaw_target)) <= deg_to_rad(FACING_TOLERANCE)


## Waits until it has turned to face what it is turning to, and at least
## [param seconds] have passed, giving up after [constant TURN_TIMEOUT]. Time
## the game spends paused does not count: nothing turns meanwhile.
func _turned(seconds: float) -> void:
	var waited := 0.0
	while not dead and (waited < seconds or not _is_facing()) and waited < maxf(seconds, TURN_TIMEOUT):
		await get_tree().process_frame
		if not get_tree().paused:
			waited += get_process_delta_time()
