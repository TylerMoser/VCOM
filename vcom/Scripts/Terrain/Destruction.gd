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


## Plays out the block breaking. [param at] is where the block's mesh stood,
## in world space, so what replaces it can stand in exactly the same place.
## Anything left behind goes under [param site]. [param hit] is the round that
## broke it, or null if it fell for want of anything under it. The base
## destruction leaves nothing behind.
func shatter(_site: TerrainDestruction, _at: Transform3D, _hit: CombatGrid.RayHit) -> void:
	pass
