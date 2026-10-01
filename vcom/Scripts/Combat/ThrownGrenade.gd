## A grenade in flight, flown along a throw's arc and gone as it arrives,
## where the [Explosion] takes over. Only for show: where it goes and what it
## does were settled before it left the hand.
##
## It crosses the ground at a steady speed and falls as anything thrown does,
## so it hangs at the top of a high arc and a long, high throw takes longer
## than a short toss. It leaves from the thrower's hand, which is near but not
## quite where the arc the rules traced begins, and eases on to that arc early
## in its flight. It flies as the grenade's own model, tumbling, if
## [method show_model] gives it one, and as a plain ball otherwise.
class_name ThrownGrenade
extends MeshInstance3D

## How fast a thrown grenade falls, in cells a second per second, which is
## what sets how long a throw is in the air. Stronger than real gravity, so a
## long throw does not keep the turn waiting.
const GRAVITY := 16.0
## Oversized for a grenade, so it can be followed in flight at any zoom.
const RADIUS := 0.15
const COLOR := Color(0.24, 0.3, 0.17)
## How much bigger than in the hand a grenade's model flies, for the same
## reason, and how fast it tumbles, in turns a second.
const MODEL_SCALE := 1.4
const TUMBLE := 2.5
## How much of its flight, from the start, the grenade takes to ease from the
## hand on to the arc.
const EASE_IN := 0.3

var _model: Node3D


func _init() -> void:
	var sphere := SphereMesh.new()
	sphere.radius = RADIUS
	sphere.height = RADIUS * 2.0
	sphere.radial_segments = 12
	sphere.rings = 6
	var material := StandardMaterial3D.new()
	material.albedo_color = COLOR
	material.roughness = 0.6
	sphere.material = material
	mesh = sphere


## Flies [param scene], a grenade's [member Item.model], in place of the ball.
func show_model(scene: PackedScene) -> void:
	if scene == null:
		return
	_model = scene.instantiate() as Node3D
	if _model == null:
		return
	_model.scale = Vector3.ONE * MODEL_SCALE
	add_child(_model)
	mesh = null


## Flies the grenade along [param throw]'s arc and frees it as it arrives.
## Await it: it returns the moment the grenade gets there, which is when it
## goes off. It leaves from [param release], the thrower's hand, if given.
func fly(throw: Throwing.Throw, release: Variant = null) -> void:
	var from: Vector3 = release if release != null else throw.start
	var off_arc := from - throw.start
	global_position = from
	# Falling 4 x height from the top of the arc over half the flight.
	var seconds := sqrt(8.0 * throw.height / GRAVITY)
	var tween := create_tween()
	tween.tween_method(func(along: float) -> void:
		global_position = throw.point_at(along) + off_arc * (1.0 - smoothstep(0.0, EASE_IN, along))
		if _model != null:
			_model.rotation = Vector3(along * seconds * TUMBLE * TAU, along * seconds * TUMBLE * 2.0, 0.0)
	, 0.0, 1.0, seconds)
	await tween.finished
	queue_free()
