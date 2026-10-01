## How a kind of block comes apart once it breaks.
##
## Each way of breaking is a subclass - [ScriptedDestruction] swaps in pieces
## cut in advance and lets them fall - and each breakable block gets a
## resource of one of them, naming the block and holding what it breaks into.
## The resources are listed in a [DestructionCatalog], which is how
## [TerrainDestruction] knows what breaks.
##
## By the time a destruction is asked to break a block, the block is already
## gone from the grid: sight, cover and paths have moved on. A destruction
## only plays out what is left of it. One resource serves every block of its
## kind, so, like a [Weapon], it must not keep anything between calls.
class_name Destruction
extends Resource

## The block this breaks, by its name in the map's MeshLibrary.
@export var block := ""
## How heavy the block is whole, in kilograms: what it weighs as it falls when
## the block under it breaks, and so how hard it shoves the debris it meets on
## the way down. A crate's boards weigh about 300 together.
@export var mass := 300.0
## The chance, from 0 to 1, that the block leaves a coin as it breaks,
## floating where it broke for the squad to pick up (see [Coins]). Rolled
## every time one breaks, where it stood or where it landed after a fall.
@export_range(0.0, 1.0) var coin_chance := 0.0


## How a block was moving as it broke, for its pieces to carry on the same way.
class Motion:
	## How fast the block's centre was moving, in cells a second.
	var velocity := Vector3.ZERO
	## How fast it was turning about its centre, in radians a second.
	var angular_velocity := Vector3.ZERO
	## Its centre, in world space.
	var center := Vector3.ZERO

	## How fast the part of the block at [param point], in world space, was
	## moving.
	func at(point: Vector3) -> Vector3:
		return velocity + angular_velocity.cross(point - center)


## Plays out the block breaking. [param at] is where the block's mesh stood,
## in world space, so what replaces it can stand in exactly the same place.
## Anything left behind goes under [param site]. [param hit] is the round that
## broke it, or null if it broke for want of anything under it. [param motion]
## is null for a block that broke where it stood; for one that fell whole and
## broke as it landed it is how the block was falling, which its pieces carry
## on. The base destruction leaves nothing behind.
func shatter(_site: TerrainDestruction, _at: Transform3D, _hit: CombatGrid.RayHit, _motion: Motion = null) -> void:
	pass
