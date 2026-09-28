## A breakable block that lost what held it up, falling whole until it lands.
##
## By the time it falls, the block has left the grid along with the one it
## stood on, so to the rules it is already gone: this is only the block as it
## looks, coming down. [TerrainDestruction] builds it from the block's own mesh
## and collision, standing exactly where the grid drew it, and breaks it where
## it lands. It is held still until a physics step after the one it was made
## in, while the grid takes the block's own collision away, and then drops
## straight down its own column, never turning. It is a hair narrower than the
## block, so it slides down between blocks either side of it rather than
## wedging between them, as a block exactly as wide as the gap would. It is
## frictionless, so it neither drags on the blocks either side of it nor pins
## the loose pieces it comes down on. It knocks debris about but never meets a
## unit: nobody stands in its column but those dropping with it, and they pass
## through.
##
## Where the wreck under it can get out of the way - a stack in the open,
## blasted apart - it falls most of a cell and smashes. Where it cannot - a
## stack in a slot between two columns, whose wreck the columns hold in place -
## it drops on to the wreck and breaks there.
##
## It has landed once something stops its fall: once it has got going and its
## downward speed drops below half the fastest it reached. A light piece
## striking it on the way down does not do that; the ground, the heap below it,
## or the block below it landing does. One that never gets going, held up from
## the start, has landed once it has sat still a moment, and one that has not
## landed a few seconds after it was let go has landed wherever it is.
##
## It says where and how it landed as it was two steps before it was seen to
## stop, still clear of whatever stopped it and still falling. Contact is only
## found within a couple of hundredths of a cell, so the step that reaches the
## ground can carry the block well into it at full speed, and only the step
## after stops it; pieces born there would start stuck in the ground. From two
## steps back they take the landing themselves, and blocks stacked on one
## another, which stop on the same step, are wound back together.
class_name FallingBlock
extends RigidBody3D

## Emitted once, as the block lands. [param at] is where its mesh stood, in
## world space, and [param motion] how the block was moving, two steps before
## it was seen to stop.
signal landed(at: Transform3D, motion: Destruction.Motion)

## How fast it must be falling, in cells a second, before being slowed counts
## as landing. Slower than that, it is still settling on to what is under it,
## or being jostled by debris flung up into it as the block under it bursts.
const FALLING_SPEED := 0.5
## The share of its fastest downward speed a block keeps while still falling.
const LANDED_SHARE := 0.5
## Slower than this, in cells a second, for [constant REST_SECONDS], a block
## that never got going has landed where it is.
const REST_SPEED := 0.2
const REST_SECONDS := 0.25
## Seconds after it is let go that it has landed, whatever it is doing.
const LONGEST_FALL := 3.0
## How much narrower than the block it is on each side, in cells.
const CLEARANCE := 0.01

## The block's mesh.
var _mesh: MeshInstance3D
## The physics frame it was made in. It is held still until a later one.
var _made_in := 0
var _landed := false
## Seconds since it was let go, and seconds it has been still.
var _falling_for := 0.0
var _still_for := 0.0
## The fastest it has fallen, in cells a second.
var _fastest := 0.0
## Where it stood and how it was moving, one step back and two steps back.
var _last := Step.new()
var _earlier := Step.new()


## Where a block stood and how it was moving, after one physics step.
class Step:
	var transform := Transform3D.IDENTITY
	var velocity := Vector3.ZERO
	var angular_velocity := Vector3.ZERO

	func _init(body: RigidBody3D = null) -> void:
		if body != null:
			transform = body.global_transform
			velocity = body.linear_velocity
			angular_velocity = body.angular_velocity


## A block showing [param mesh], placed within it by [param mesh_transform],
## colliding as a box round [param shapes] - a MeshLibrary item's list of
## shapes, each followed by its transform - and weighing [param block_mass]
## kilograms.
func _init(mesh: Mesh, mesh_transform: Transform3D, shapes: Array, block_mass: float) -> void:
	name = &"FallingBlock"
	_mesh = MeshInstance3D.new()
	_mesh.name = &"Mesh"
	_mesh.mesh = mesh
	_mesh.transform = mesh_transform
	add_child(_mesh)

	# A block with no shapes of its own collides as the box round its mesh,
	# or, with no mesh either, as a cube a cell across.
	var bounds := AABB(-Vector3.ONE * 0.5, Vector3.ONE)
	if mesh != null:
		bounds = mesh_transform * mesh.get_aabb()
	for index in range(0, shapes.size() - 1, 2):
		var shape_bounds: AABB = (shapes[index + 1] as Transform3D) * (shapes[index] as Shape3D).get_debug_mesh().get_aabb()
		bounds = shape_bounds if index == 0 else bounds.merge(shape_bounds)
	var box := BoxShape3D.new()
	box.size = bounds.size - Vector3(CLEARANCE * 2.0, 0.0, CLEARANCE * 2.0)
	var collider := CollisionShape3D.new()
	collider.shape = box
	collider.position = bounds.get_center()
	add_child(collider)

	mass = block_mass
	lock_rotation = true
	var material := PhysicsMaterial.new()
	material.friction = 0.0
	physics_material_override = material
	collision_layer = TerrainDestruction.DEBRIS_LAYER
	collision_mask = TerrainDestruction.TERRAIN_LAYER | TerrainDestruction.DEBRIS_LAYER
	continuous_cd = true
	freeze = true


func _ready() -> void:
	_made_in = Engine.get_physics_frames()


func _physics_process(delta: float) -> void:
	if _landed:
		return
	if freeze:
		# Held where it stood until a physics step after the one it was made
		# in: the grid takes the block's own collision away at the end of
		# that frame, and until then the block would start inside it.
		if Engine.get_physics_frames() > _made_in:
			freeze = false
			_last = Step.new(self)
			_earlier = _last
		return
	_falling_for += delta
	var falling := -linear_velocity.y
	_fastest = maxf(_fastest, falling)
	_still_for = _still_for + delta if linear_velocity.length() < REST_SPEED else 0.0
	var stopped := _fastest >= FALLING_SPEED and falling < _fastest * LANDED_SHARE
	if stopped or _still_for >= REST_SECONDS or _falling_for >= LONGEST_FALL:
		_land()
		return
	_earlier = _last
	_last = Step.new(self)


## Says the block has landed, as it was two steps before it was seen to stop,
## and takes it away: what it breaks into takes its place.
func _land() -> void:
	_landed = true
	var center := global_transform.affine_inverse() * TerrainDestruction.debris_box(self).get_center()
	var motion := Destruction.Motion.new()
	motion.velocity = _earlier.velocity
	motion.angular_velocity = _earlier.angular_velocity
	motion.center = _earlier.transform * center
	var at := _earlier.transform * _mesh.transform
	# Out of the physics at once, before the next step, so its pieces are not
	# born inside it.
	hide()
	process_mode = Node.PROCESS_MODE_DISABLED
	queue_free()
	landed.emit(at, motion)
