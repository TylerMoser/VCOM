## Sways a tree's leaves in the breeze. Every mesh directly under this node is
## a clump of leaves, turned about its own origin, where it grows from the
## branch.
##
## The wind blows the same way over the whole map and comes in gusts. A gust
## leans every clump downwind and sets it shaking, each clump about its own
## axis and at its own pace, so the canopy never moves as one piece. Gusts
## travel with the wind, so a tree downwind catches one a moment after a tree
## upwind, and a gust crosses a wood as a wave.
##
## It is only for show: the rules never read it. It runs in the game and not in
## the editor, so the transforms saved in the scene are the leaves at rest, and
## it stops with the tree, under the pause menu.
class_name LeafSway
extends Node3D

## Which way the wind blows, across the ground in world space.
const WIND_DIRECTION := Vector3(1.0, 0.0, 0.4)
## How strong the wind is between gusts, where 1 is the height of a gust.
const CALM := 0.3
## How fast a gust travels downwind, in cells a second.
const GUST_SPEED := 4.0

## How far, in degrees, a clump leans downwind at the height of a gust.
@export var lean_degrees := 7.0
## How far, in degrees, a clump shakes either way at the height of a gust.
@export var flutter_degrees := 4.0
## How often a clump shakes, in shakes a second: each clump picks its own pace
## between these two.
@export var flutter_rate := Vector2(1.0, 1.8)

var _clumps: Array[Clump] = []
## Seconds of breeze so far. Every tree on a map starts on the same frame, so
## they all keep the same time.
var _time := 0.0


## A clump of leaves: where it is at rest, and how it shakes.
class Clump:
	var node: Node3D
	var rest: Transform3D
	## What it shakes about, in the tree's space: mostly across, a little up.
	var axis: Vector3
	## How fast it shakes, in radians a second, and where in the shake it starts.
	var rate: float
	var phase: float


func _ready() -> void:
	for child in get_children():
		var leaves := child as MeshInstance3D
		if leaves == null:
			continue
		var clump := Clump.new()
		clump.node = leaves
		clump.rest = leaves.transform
		var heading := randf() * TAU
		clump.axis = Vector3(cos(heading), randf_range(-0.3, 0.3), sin(heading)).normalized()
		clump.rate = TAU * randf_range(flutter_rate.x, flutter_rate.y)
		clump.phase = randf() * TAU
		_clumps.append(clump)


func _process(delta: float) -> void:
	_time += delta
	var wind := Vector3(WIND_DIRECTION.x, 0.0, WIND_DIRECTION.z).normalized()
	var strength := gust(_time - global_position.dot(wind) / GUST_SPEED)
	# Turning about up x downwind tips a clump's top downwind. The tree may be
	# turned with its block, so the wind is taken into its space first.
	var downwind := global_basis.inverse() * wind
	var lean := Basis(Vector3.UP.cross(downwind).normalized(), deg_to_rad(lean_degrees) * strength)
	var flutter := deg_to_rad(flutter_degrees) * strength
	for clump in _clumps:
		var shake := Basis(clump.axis, flutter * sin(clump.rate * _time + clump.phase))
		clump.node.transform = Transform3D(lean * shake * clump.rest.basis, clump.rest.origin)


## How hard the wind blows at [param time], from [constant CALM] to 1: three
## slow waves out of step with one another, so the gusts come unevenly and
## no two are alike for a long while.
static func gust(time: float) -> float:
	var wave := 0.5 * sin(time * 0.9) + 0.3 * sin(time * 0.43 + 1.7) + 0.2 * sin(time * 2.1 + 4.1)
	return lerpf(CALM, 1.0, smoothstep(-0.6, 0.9, wave))
