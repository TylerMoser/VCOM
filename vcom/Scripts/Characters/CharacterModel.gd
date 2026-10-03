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
## kneels behind low cover or braces against high; hunkered down, it ducks
## low behind either ([member hunkered]). While someone has a shot lined up
## that sees it only where it leans out round that cover, it leans out there,
## hunkered or not, and draws back once the shot is over ([method lean_out]).
##
## Its gear is its unit's, each item shown as its [member Item.model]: the gun
## in its hands, a sword it carries as well slung across its back until it is
## drawn, and its grenades and medkits on its belt, three at most. It takes a
## medkit in its left hand to use it on an ally or itself ([method use_medkit]).
##
## When the unit dies the figure breaks apart, as a block crumbles: its voxels
## become lumps of debris in its colour, knocked the way the killing blow went,
## and its gear falls as loose props ([method TerrainDestruction.break_figure],
## [member crumbles_as]). Then it hides, and goes with its unit
## ([method break_apart]).
##
## It bleeds: [Blood] reads its voxels as they are posed ([method voxels]),
## asks it where a blow lands ([method pick_wound]) and which way its own
## blade sweeps ([method swing]), and stains its body and its gear; stained
## voxels stay red in the lumps it breaks into. None of that changes what the
## figure does.
class_name CharacterModel
extends Node3D

## What the figure has made ready, which decides the pose it holds.
enum Readiness { NONE, AIM, MELEE, THROW, CHEER }

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
## What [member crumbles_as] and [member gear_wears_as] are unless set: loaded
## as it readies, not preloaded, as what breaks it apart
## ([TerrainDestruction]) reads them, and a preload here would compile that
## first.
const FIGURE_DESTRUCTION := "res://Resources/Destruction/Figure.tres"
const GEAR_DESTRUCTION := "res://Resources/Destruction/Gear.tres"
## Grenades and medkits shown on the belt at most: one to each of its slots.
const BELT := 3
## How far out of the middle of its tile a lean out of cover takes its head,
## in cells, unless the lean's clip says ([code]reach[/code] in its metadata,
## which the bake measures off the pose).
const LEAN_REACH := 0.7
## A medkit in the left hand, turned in the grenade's grip so it is held up
## with its cross to the front, toward whoever it is held out to.
const MEDKIT_IN_HAND := Basis(Vector3.UP, -PI / 2.0)
## Where it looks attending to itself ([method attend]): how far ahead of its
## feet (x) and how high (y), in metres, about where a medkit pressed to its
## middle is held.
const SELF_LOOK := Vector2(0.6, 0.7)

## The .vox the figure was baked from, which its voxels are read from while
## the game runs, for blood to land on them and for it to break apart
## ([method voxels]).
@export var voxel_model := "res://Characters/BaseCharacter.vox"
## How it breaks apart as its unit dies: how big its lumps are
## ([member VoxelDestruction.crumble_size]), and how heavy, rough and bouncy.
## [constant FIGURE_DESTRUCTION] unless set.
@export var crumbles_as: VoxelDestruction
## How the gear it drops then wears away, once a round or a blast reaches it,
## as a crate's boards do: how heavy and rough it is, how much a point of
## damage breaks off, and how small what is left gets before it crumbles.
## [constant GEAR_DESTRUCTION] unless set.
@export var gear_wears_as: VoxelDestruction

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
## Whether its unit has hunkered down, which has it duck low behind its cover,
## whichever height it is, its weapon hugged close: but for a lean out of it
## ([member leaning]), which shows where a shot sees it.
var hunkered := false
## Which way it is leaning out of its cover: 1 to its left, -1 to its right,
## 0 while it is behind it. Set through [method lean_out] and
## [method lean_back].
var leaning := 0
## Whether its unit has died, and it has broken apart ([method break_apart]).
var dead := false

var _skeleton: Skeleton3D
var _body: MeshInstance3D
var _tree: AnimationTree
var _aim: Node

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
## Medkit props, one for each medkit the unit carries, on the belt after the
## grenades, and whether the first is in the left hand.
var _medkits: Array[Node3D] = []
var _holding_medkit := false
## A medkit borrowed from a squad member beside it, in its hand while it uses
## it, one of [member _medkits] until then ([method use_medkit]).
var _borrowed: Node3D

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
## The cover it is leaning out from, which says whether it leans out standing
## or on one knee; the seconds since it began to; and whether it has been told
## to draw back, which it does once it is done flinching ([method lean_back]).
var _lean_cover := LineOfSight.Cover.HIGH
var _leaned_for := 0.0
var _drawing_back := false
## Seconds left of the reaction (a flinch, a duck) playing on top of its pose.
var _reacting := 0.0

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
## Its voxels, for blood: read the first time they are asked for.
var _voxels: FigureVoxels
## What picks where a blow lands on it: only for show, so never the global
## generator, which the rules draw on.
var _show := RandomNumberGenerator.new()


func _ready() -> void:
	_show.randomize()
	_skeleton = get_node_or_null(^"Skeleton3D") as Skeleton3D
	_body = get_node_or_null(^"Skeleton3D/Body") as MeshInstance3D
	_tree = get_node_or_null(^"AnimationTree") as AnimationTree
	_aim = get_node_or_null(^"Skeleton3D/Aim")
	if crumbles_as == null:
		crumbles_as = load(FIGURE_DESTRUCTION)
	if gear_wears_as == null:
		gear_wears_as = load(GEAR_DESTRUCTION)
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
	_leaned_for += delta
	_acting = maxf(_acting - delta, 0.0)
	_reacting = maxf(_reacting - delta, 0.0)
	if _drawing_back and _reacting <= 0.0:
		_stop_leaning()
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
	_stop_leaning()
	_walk = points.duplicate()
	_walk_from = _ground()
	_walk_index = 0
	_strafe = keep_facing


## The floor under it is gone: it falls until its unit lands, and lands with
## its knees giving.
func fall() -> void:
	_stop_leaning()
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


## Whether it is standing about with nothing to do: not moving, falling,
## leaning out or broken apart, nothing ready, nothing it attends to
## ([method attend]) and nothing playing. [Postures] only moves it then.
func is_idle() -> bool:
	return (
		not dead and readiness == Readiness.NONE and _aim_point == null and leaning == 0
		and _walk.is_empty() and not _falling and _acting <= 0.0
	)


## Leans out round the end of the cover it is behind, to its left
## ([param side] 1) or its right (-1), as a unit does for as long as a shot is
## lined up at it that sees it only there ([member LineOfSight.Shot.leaning]).
## It turns to face that cover, [param yaw], which is [param held] high, leaning
## out from low cover on one knee, and looks round it at [param watch] in the
## world: whoever has it in their sights. Asked again while it leans, it changes
## sides or what it watches. It leans only while it has nothing else to do: not
## with anything ready, nor walking or falling.
func lean_out(side: int, held: LineOfSight.Cover, yaw: float, watch: Vector3) -> void:
	if dead or side == 0 or readiness != Readiness.NONE or not _walk.is_empty() or _falling:
		return
	_drawing_back = false
	side = signi(side)
	if leaning != side or _lean_cover != held:
		_leaned_for = 0.0
	leaning = side
	_lean_cover = held
	_yaw_target = yaw
	_watch_point = watch


## Draws back behind its cover: on its next frame, or once the flinch or duck
## it is playing is over, so that a shot which catches it leaning out is seen
## to land on it out there. Asked to lean out again before then, as it is when
## the shot it leans out for is lined up again the moment it is over, it stays
## out, and never bobs back between two shots.
func lean_back() -> void:
	if leaning != 0:
		_drawing_back = true


## Whether it has leaned out as far as it is going to: the lean faded in, which
## takes [constant RAISE_SECONDS] as any base pose does, and turned to its
## cover, or given [constant TURN_TIMEOUT] to. True while it is not leaning.
func has_leaned_out() -> bool:
	if leaning == 0 or dead:
		return true
	return _leaned_for >= TURN_TIMEOUT or (_leaned_for >= RAISE_SECONDS and _is_facing())


## How far out of the middle of its tile leaning out to [param side] of
## [param held] cover takes the middle of its head, in cells: what the lean was
## made to reach, which its clip carries.
func lean_reach(side: int, held: LineOfSight.Cover) -> float:
	var animation := _tree.get_animation(_lean_pose(side, held)) if _tree != null else null
	return animation.get_meta(&"reach", LEAN_REACH) if animation != null else LEAN_REACH


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


## Turns to [param point] in the world and looks at it, with nothing readied,
## and keeps facing it until it stands easy ([method stand_easy]), whatever
## [Postures] would have it face meanwhile: an ally a medkit is lined up on, the
## chest of the unit at [param point]. Given null, it attends to itself: it
## keeps the way it faces and looks down in front of its own middle, where a
## medkit used on itself is held ([constant SELF_LOOK]).
func attend(point: Variant = null) -> void:
	_easing = false
	_set_readiness(Readiness.NONE)
	if point == null:
		# Ahead the way it is turning to, not the way it happens to face, so a
		# turn under way finishes.
		var ahead := Vector3(sin(_yaw_target), 0.0, cos(_yaw_target))
		_aim_point = global_position + ahead * SELF_LOOK.x + Vector3.UP * SELF_LOOK.y
		_watch_point = _aim_point
		return
	_aim_point = point
	_watch_point = point
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


## Loads a fresh magazine into its gun, played over its arms and head so it
## stays as it stands, kneels or hunkers, and returns the moment the new one is
## seated (the clip's [code]seat[/code]). The rest plays on after;
## [method recover] waits for it. Puts away anything it had ready first. At once
## without a rifle in its hands.
func reload() -> void:
	_easing = false
	_aim_point = null
	_set_readiness(Readiness.NONE)
	while _acting > 0.0 and not dead:
		await get_tree().process_frame
	if dead or _stance != &"rifle" or _drawn:
		return
	_act_upper(&"reload_rifle")
	await _after(_moment(&"reload_rifle", &"seat"))


## Takes a medkit off its belt in its left hand and holds it out to the ally
## whose chest is at [param point] in the world, next to it, turning to face
## them first, and returns the moment the ally is seen to be treated (the
## clip's [code]apply[/code]). The medkit goes back on the belt as the clip
## ends; [method recover] waits for that. Played over the left arm alone, so it
## stays as it stands, kneels or hunkers, the right hand keeping its weapon,
## and it looks at the ally throughout. Puts away anything it had ready
## first. Given null, it treats itself: it presses the medkit to its own
## middle instead ([code]use_medkit_self[/code]), looking down at it, at the
## same moments. [param borrowed] is a medkit it uses from a squad member beside
## it: with none of its own on its belt it appears in the hand at the clip's
## [code]take[/code] and goes at its [code]stow[/code]; with one, its own is
## shown, a medkit being a medkit.
func use_medkit(point: Variant = null, borrowed: Item = null) -> void:
	attend(point)
	await _turned(0.0)
	while _acting > 0.0 and not dead:
		await get_tree().process_frame
	if dead:
		return
	var clip := &"use_medkit" if point != null else &"use_medkit_self"
	_act_left(clip)
	_carry_medkit(clip, borrowed)
	await _after(_moment(clip, &"apply"))


## Moves the first medkit from the belt to the left hand at [param clip]'s
## [code]take[/code] and back at its [code]stow[/code]; with none on the belt,
## [param borrowed] is made to show in the hand meanwhile, then let go.
func _carry_medkit(clip: StringName, borrowed: Item) -> void:
	var take := _moment(clip, &"take")
	var stow := _moment(clip, &"stow")
	await _after(take)
	if dead:
		return
	if _medkits.is_empty() and borrowed != null:
		_borrowed = _make_prop(borrowed)
		if _borrowed != null:
			_medkits.append(_borrowed)
	_holding_medkit = true
	_place_gear()
	await _after(stow - take)
	if dead:
		return
	_holding_medkit = false
	if _borrowed != null:
		_medkits.erase(_borrowed)
		# Freed already if the belt was rebuilt meanwhile ([method equip]).
		if is_instance_valid(_borrowed):
			_borrowed.queue_free()
		_borrowed = null
	_place_gear()


## Waits for the blow, throw, reload or medkit it is playing to finish.
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
## of [param grenades] and a medkit for each of [param kits] on its belt.
## Called again as the unit uses something up.
func equip(gun: Item, melee: Item, grenades: Array[Item], kits: Array[Item] = []) -> void:
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
	for prop in _medkits:
		prop.queue_free()
	_medkits.clear()
	for item in kits:
		var prop := _make_prop(item)
		if prop != null:
			_medkits.append(prop)
	if _holding_medkit and _medkits.is_empty():
		_holding_medkit = false
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


## Its voxels as blood and breaking apart need them: where each is now, and
## the stains on them. Null if they cannot be read.
func voxels() -> FigureVoxels:
	if _voxels == null:
		_voxels = FigureVoxels.new(self, voxel_model)
	return _voxels if _voxels.rig != null else null


## Where a round or a blow coming from [param from] is seen to land on the
## figure: a point on the side facing it, mostly on the torso. Infinite if
## there is none to be found.
func pick_wound(from: Vector3) -> Vector3:
	var figure := voxels()
	var hit: FigureVoxels.Hit = figure.pick_wound(from, _show) if figure != null else null
	return hit.point if hit != null else Vector3.INF


## The way its blade sweeps as a strike lands, in the world: down across the
## front of it from its right to its left, as [code]strike_sword[/code] swings.
func swing() -> Vector3:
	return (global_basis * Vector3(0.75, -0.45, 0.3)).normalized()


## What draws each thing it carries that blood can land on: each prop's voxel
## model, those shown.
func gear() -> Array[MeshInstance3D]:
	var drawn: Array[MeshInstance3D] = []
	var props: Array = [_gun, _sword]
	props.append_array(_grenades)
	props.append_array(_medkits)
	for held in props:
		if held == null or not is_instance_valid(held) or not (held as Node3D).is_visible_in_tree():
			continue
		for node in (held as Node3D).find_children("*", "MeshInstance3D", true, false):
			var mesh := node as MeshInstance3D
			# Only the models themselves: not the stains drawn over them.
			if mesh.mesh != null and mesh.mesh.resource_path.get_extension().to_lower() == "vox":
				drawn.append(mesh)
	return drawn


## Goes to pieces as its unit dies, once whatever breaks it apart has taken
## its voxels and its gear ([method TerrainDestruction.break_figure]): it stops
## and hides, and goes when its unit does. Nothing of it is left standing.
func break_apart() -> void:
	dead = true
	visible = false
	set_process(false)
	if _tree != null:
		_tree.active = false
	if _aim != null:
		_aim.set(&"active", false)


func _set_readiness(value: Readiness) -> void:
	if readiness == value:
		return
	var was := readiness
	readiness = value
	_readied_for = 0.0
	if value != Readiness.NONE:
		_stop_leaning()
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


## Puts every prop in its socket for how the figure stands now. The belt's
## slots go to the grenades first, then the medkits.
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
	for index in _medkits.size():
		var prop := _medkits[index]
		if index == 0 and _holding_medkit:
			_put(prop, ^"LeftHand/GrenadeGrip")
			prop.basis = MEDKIT_IN_HAND
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
	# Leaning out comes before hunkering down: it shows where a shot that sees
	# it only there is aimed, which the cover would hide it from ducked down.
	if leaning != 0:
		return _lean_pose(leaning, _lean_cover)
	if hunkered:
		return StringName("hunker_%s" % hands)
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


## The pose of a lean out to [param side] of [param held] cover, for the hands
## as they are: standing at the end of high cover, on one knee at the end of
## low.
func _lean_pose(side: int, held: LineOfSight.Cover) -> StringName:
	return StringName("%s_lean_%s_%s" % [
		"crouch" if held == LineOfSight.Cover.LOW else "wall", "left" if side > 0 else "right", _hands(),
	])


## Stands it back behind its cover, there and then.
func _stop_leaning() -> void:
	leaning = 0
	_drawing_back = false


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
		# Leaning out, it has its eyes on whoever it leans out to look at.
		var look_weight := 0.0 if look == null else (1.0 if aiming or leaning != 0 else 0.6)
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


## Plays [param clip] over the arms and head alone ([code]upper[/code] in the
## tree), counting as acting until it ends, as [method _act] does.
func _act_upper(clip: StringName) -> void:
	var animation := _tree.get_animation(clip)
	_acting = animation.length if animation != null else 0.0
	_tree.set(&"parameters/upper_pick/transition_request", String(clip))
	_tree.set(&"parameters/upper/request", AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE)


## Plays [param clip] over the left arm alone ([code]left[/code] in the
## tree), counting as acting until it ends, as [method _act] does.
func _act_left(clip: StringName) -> void:
	var animation := _tree.get_animation(clip)
	_acting = animation.length if animation != null else 0.0
	_tree.set(&"parameters/left_pick/transition_request", String(clip))
	_tree.set(&"parameters/left/request", AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE)


func _react(clip: StringName) -> void:
	if dead:
		return
	var animation := _tree.get_animation(clip)
	_reacting = animation.length if animation != null else 0.0
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
