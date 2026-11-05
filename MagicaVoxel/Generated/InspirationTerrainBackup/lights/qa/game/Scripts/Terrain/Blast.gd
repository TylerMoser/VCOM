## A burst of force from a point, thrown against the pieces of a breaking
## block: what blows a crate apart rather than letting it simply collapse.
##
## It is modelled on a real blast. Its push spreads out from the origin over a
## growing sphere, so it falls off with the square of the distance. A piece
## catches it in proportion to the area it turns toward the origin, so a board
## facing the blast is thrown far harder than one edge-on to it. The same push
## sends a light piece further than a heavy one. And it lands on the side of
## the piece facing the origin, so pieces tumble away as they fly.
##
## A blast's force is a multiplier: 1 is a moderate blast, which throws a
## crate's boards a few cells, 2 is twice as hard, and 0 is no blast at all.
class_name Blast
extends RefCounted

## The impulse a blast of force 1 gives each square cell of surface facing it
## one cell away, in newton-seconds (a cell is a metre). Tuned so that a
## crate's boards land about a cell and a half from it, nine in ten within
## three cells.
const IMPULSE := 90.0
## Nearer the origin than this, in cells, the push stops growing. A real charge
## has a size, and without it a piece touching the origin would be thrown
## infinitely hard.
const CORE := 0.5


## Throws each of [param pieces] away from [param origin] with a blast of
## [param force].
static func burst(pieces: Array[RigidBody3D], origin: Vector3, force: float) -> void:
	if force <= 0.0:
		return
	for body in pieces:
		if not is_instance_valid(body):
			continue
		body.apply_impulse(impulse_on(body, origin, force), contact(body, origin) - body.global_position)


## The impulse a blast of [param force] at [param origin] gives [param body]:
## away from the origin, as strong as the blast is where the piece is, times
## the area the piece shows it.
static func impulse_on(body: PhysicsBody3D, origin: Vector3, force: float) -> Vector3:
	var away := TerrainDestruction.debris_box(body).get_center() - origin
	var direction := away_from(away)
	return direction * strength(away.length(), force) * exposed_area(body, direction)


## Which way a blast pushes a piece [param away] from where it goes off:
## straight up for one right on top of it.
static func away_from(away: Vector3) -> Vector3:
	var distance := away.length()
	return away / distance if distance > 1e-4 else Vector3.UP


## How hard a blast of [param force] pushes each square cell facing it,
## [param distance] cells from where it goes off.
static func strength(distance: float, force: float) -> float:
	return force * IMPULSE / (distance * distance + CORE * CORE)


## Where on [param body] a blast at [param origin] lands: the point of it
## nearest the origin.
static func contact(body: PhysicsBody3D, origin: Vector3) -> Vector3:
	var box := TerrainDestruction.debris_box(body)
	return origin.clamp(box.position, box.end)


## How much of [param body] faces a blast travelling along [param direction]:
## the area it shows, seen from where the blast comes from, in square cells.
static func exposed_area(body: PhysicsBody3D, direction: Vector3) -> float:
	var area := 0.0
	for node in body.find_children("*", "CollisionShape3D", true, false):
		var collider := node as CollisionShape3D
		if collider.shape == null:
			continue
		if collider.shape is BoxShape3D:
			area += box_area((collider.shape as BoxShape3D).size, collider.global_basis.orthonormalized(), direction)
		else:
			area += box_area((collider.global_transform * collider.shape.get_debug_mesh().get_aabb()).size, Basis.IDENTITY, direction)
	return area


## How much of a box [param size] across, turned by [param basis], faces a
## blast travelling along [param direction], in square cells.
static func box_area(size: Vector3, basis: Basis, direction: Vector3) -> float:
	var facing := basis.inverse() * direction
	return (
		absf(facing.x) * size.y * size.z
		+ absf(facing.y) * size.x * size.z
		+ absf(facing.z) * size.x * size.y
	)
