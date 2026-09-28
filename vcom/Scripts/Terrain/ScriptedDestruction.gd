## Breaks a block into pieces cut in advance: a scene of meshes that together
## look like the block, swapped in where it stood and left to fall.
##
## The scene has to be built in the same space as the block's own mesh, the
## same MagicaVoxel frame imported at the blocks' scale of 0.0625, so that
## stood where the block's mesh stood the pieces cover it exactly and the swap
## cannot be seen.
##
## Every mesh in the scene becomes a piece: a rigid body with a box around the
## mesh, as heavy as its size. The box is a shade smaller than the mesh, as no
## real board is cut to fit a gap exactly: a piece as long as a cell is wide
## would otherwise wedge exactly between the blocks either side of the gap the
## block leaves, jammed there and shivering for good. A [RigidBody3D] already in
## the scene is used as it is, so a piece can be hand-tuned, and anything else
## in the scene is left alone, so the scene can carry more than pieces.
##
## Some pieces are cut to overlap - the bars of a crate's frame share its
## corners - and pieces that start out overlapping pass through each other
## rather than bursting the block open like a spring. The round that broke the
## block knocks the pieces nearest where it struck on along its flight. A block
## that fell whole and broke as it landed passes its fall on to its pieces, so
## they carry on down into whatever stopped it. Pieces stay live physics bodies
## for good, for whatever comes along later to knock about again.
##
## Left alone, the pieces simply collapse. With [member blast] on, the block
## bursts apart instead, every time it breaks: a [Blast] from the [Marker3D]
## named DestructOrigin in the pieces scene, as strong as that marker's
## [code]force[/code] metadata says.
class_name ScriptedDestruction
extends Destruction

## Lightest a piece can be, in kilograms, however thin it is cut.
const MIN_MASS := 0.1
## How much smaller a piece's box is than its mesh, as a share of each side:
## enough that no piece cut to a cell's width can span the gap it leaves at any
## angle, and too little to see.
const SLACK := 0.035
## How far two pieces must reach into each other before they count as cut to
## overlap, in cells. Pieces that only touch still collide.
const OVERLAP_TOLERANCE := 0.001
## The marker in a pieces scene a blast goes off at, and the metadata on it
## saying how hard: a [Blast] force, 1 for a moderate blast.
const BLAST_ORIGIN := "DestructOrigin"
const BLAST_FORCE := &"force"

## The pieces the block breaks into, as a scene.
@export var pieces: PackedScene
## Whether the block bursts apart from its pieces scene's DestructOrigin marker
## rather than just collapsing. Off, the marker is ignored.
@export var blast := false

@export_group("Physics")
## How heavy the pieces are, in kilograms per cubic cell.
@export var density := 500.0
## The speed the round gives the piece nearest where it struck, along its
## flight, in cells a second. Pieces further away get less, and none past
## [member push_reach] cells.
@export var push := 1.5
@export var push_reach := 1.0
## The most speed a piece flies apart with, in cells a second, and spin it
## tumbles with, in radians a second, each drawn at random so the collapse is
## not too tidy.
@export var scatter := 0.4
@export var spin := 3.0
@export_range(0.0, 1.0) var friction := 0.8
@export_range(0.0, 1.0) var bounce := 0.1


func shatter(site: TerrainDestruction, at: Transform3D, hit: CombatGrid.RayHit, motion: Destruction.Motion = null) -> void:
	if pieces == null:
		push_error("ScriptedDestruction: '%s' has no pieces scene." % block)
		return
	var broken := pieces.instantiate() as Node3D
	site.add_child(broken)
	broken.global_transform = at
	var bodies := _make_pieces(broken)
	_pass_overlaps(bodies)

	# Held where they are until the next physics step. The grid takes the
	# block's own collision away at the end of this frame, and until then the
	# pieces would start inside it. A block that fell whole left the grid long
	# ago, and its pieces carry straight on with its fall.
	if motion == null:
		for body in bodies:
			body.freeze = true
		await site.get_tree().physics_frame
	for body in bodies:
		if not is_instance_valid(body):
			continue
		body.freeze = false
		var center := TerrainDestruction.debris_box(body).get_center()
		body.linear_velocity = _knock(center, hit)
		body.angular_velocity = _random_in_ball() * spin
		if motion != null:
			body.linear_velocity += motion.at(center)
			body.angular_velocity += motion.angular_velocity
	# The map may have gone while the pieces were held.
	if blast and is_instance_valid(broken):
		_burst(broken, bodies)


## Throws [param bodies] apart with a [Blast] from the DestructOrigin marker
## in [param broken], as hard as its force metadata says.
func _burst(broken: Node3D, bodies: Array[RigidBody3D]) -> void:
	var origin := broken.find_child(BLAST_ORIGIN, true, false) as Node3D
	if origin == null:
		push_warning("ScriptedDestruction: '%s' has blast on but no %s marker in its pieces scene, so it only collapses." % [block, BLAST_ORIGIN])
		return
	Blast.burst(bodies, origin.global_position, float(origin.get_meta(BLAST_FORCE, 1.0)))


## Makes every bare mesh under [param broken] a piece of its own, and returns
## every piece there, including any the scene built for itself.
func _make_pieces(broken: Node3D) -> Array[RigidBody3D]:
	for node in broken.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		if mesh.mesh != null and mesh.mesh.get_surface_count() > 0 and not _in_body(mesh, broken):
			_give_body(mesh)

	var material := PhysicsMaterial.new()
	material.friction = friction
	material.bounce = bounce
	var bodies: Array[RigidBody3D] = []
	if broken is RigidBody3D:
		bodies.append(broken as RigidBody3D)
	for node in broken.find_children("*", "RigidBody3D", true, false):
		bodies.append(node as RigidBody3D)
	for body in bodies:
		body.collision_layer = TerrainDestruction.DEBRIS_LAYER
		body.collision_mask = TerrainDestruction.DEBRIS_MASK
		# Thin pieces fall fast enough to slip through one another in a step.
		body.continuous_cd = true
		if body.physics_material_override == null:
			body.physics_material_override = material
	return bodies


## Puts [param mesh] into a rigid body of its own, standing where it stood,
## with a box a shade inside it to collide with and a weight to match.
func _give_body(mesh: MeshInstance3D) -> void:
	var body := RigidBody3D.new()
	body.name = "%sPiece" % mesh.name
	mesh.get_parent().add_child(body)
	# A physics body must not be scaled, so the body takes the mesh's place
	# and turn and the mesh keeps any scale it has.
	body.transform = mesh.transform.orthonormalized()
	mesh.reparent(body)

	var box := mesh.transform * mesh.mesh.get_aabb()
	var shape := BoxShape3D.new()
	shape.size = box.size * (1.0 - SLACK)
	var collider := CollisionShape3D.new()
	collider.shape = shape
	collider.position = box.get_center()
	body.add_child(collider)
	body.mass = maxf(box.size.x * box.size.y * box.size.z * density, MIN_MASS)


## Lets pieces that start out overlapping pass through each other.
func _pass_overlaps(bodies: Array[RigidBody3D]) -> void:
	var boxes: Array[AABB] = []
	for body in bodies:
		boxes.append(TerrainDestruction.debris_box(body).grow(-OVERLAP_TOLERANCE))
	for i in bodies.size():
		for j in range(i + 1, bodies.size()):
			if boxes[i].intersects(boxes[j]):
				bodies[i].add_collision_exception_with(bodies[j])


## The speed a piece centred on [param center] flies off with: a knock along
## the flight of the round that struck, [param hit], if one did and it is near
## enough, and a little at random.
func _knock(center: Vector3, hit: CombatGrid.RayHit) -> Vector3:
	var velocity := _random_in_ball() * scatter
	if hit != null:
		var nearness := 1.0 - clampf(center.distance_to(hit.point) / push_reach, 0.0, 1.0)
		velocity += hit.direction * push * nearness
	return velocity


## Whether [param node] already sits in a rigid body within [param broken].
static func _in_body(node: Node, broken: Node) -> bool:
	var parent := node.get_parent()
	while parent != null:
		if parent is RigidBody3D:
			return true
		if parent == broken:
			return false
		parent = parent.get_parent()
	return false


## A point drawn at random from the ball of radius one.
static func _random_in_ball() -> Vector3:
	var point := Vector3(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0), randf_range(-1.0, 1.0))
	while point.length_squared() > 1.0:
		point = Vector3(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0), randf_range(-1.0, 1.0))
	return point
