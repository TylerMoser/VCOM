## A grenade in flight, flown along a throw's arc and gone as it arrives,
## where the [Explosion] takes over. Only for show: where it goes and what it
## does were settled before it left the hand.
##
## It crosses the ground at a steady speed and falls as anything thrown does,
## so it hangs at the top of a high arc and a long, high throw takes longer
## than a short toss.
class_name ThrownGrenade
extends MeshInstance3D

## How fast a thrown grenade falls, in cells a second per second, which is
## what sets how long a throw is in the air. Stronger than real gravity, so a
## long throw does not keep the turn waiting.
const GRAVITY := 16.0
## Oversized for a grenade, so it can be followed in flight at any zoom.
const RADIUS := 0.15
const COLOR := Color(0.24, 0.3, 0.17)


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


## Flies the grenade along [param throw]'s arc and frees it as it arrives.
## Await it: it returns the moment the grenade gets there, which is when it
## goes off.
func fly(throw: Throwing.Throw) -> void:
	global_position = throw.start
	# Falling 4 x height from the top of the arc over half the flight.
	var seconds := sqrt(8.0 * throw.height / GRAVITY)
	var tween := create_tween()
	tween.tween_method(func(along: float) -> void: global_position = throw.point_at(along), 0.0, 1.0, seconds)
	await tween.finished
	queue_free()
