## Breaks a block a few voxels at a time, the second way a block can break: a
## round that strikes it breaks off the voxels round where it struck, a blast
## the voxels round where it goes off, and each falls away on its own, a cube a
## sixteenth of a cell across in the colour it was (see [VoxelDebris]). Any
## block drawn by a MagicaVoxel model can break so, since its voxels are read
## from the model (see [VoxelShape]); giving it one of these in the
## [DestructionCatalog] is all it takes.
##
## What is left of a block stands, worn, and still counts as the whole block to
## the rules: sight, cover and paths are read off whole cells, and a block is
## in its cell or it is not. It goes from the grid only once it has lost so
## much that less than [member collapse_below] of its voxels are left, or, if
## something stands on it, once nothing joins its bottom to its top any more
## (a tree's trunk shot through). Then it breaks as a crate does: everything
## stacked on it falls, anyone on it drops, and what is left of it crumbles
## into pieces [member crumble_size] voxels across. A block on the bottom of
## the map never goes, having nothing under it to fall to, and is only ever
## worn so deep (see [VoxelTerrain]).
##
## How much a round or a blast breaks off is in proportion to the environmental
## damage it does ([member Weapon.environment_damage],
## [member Grenade.environment_damage]): so many voxels a point for a round,
## so big a crater a point for a blast.
##
## [TerrainDestruction] wears and breaks these blocks through its
## [VoxelTerrain], which keeps what is left of each one; [method shatter] is
## not used. Like every [Destruction] it is shared by every block of its kind,
## so it keeps nothing of its own between calls.
class_name VoxelDestruction
extends Destruction

## The share of its voxels a block must keep to stay standing. Worn below it,
## it breaks.
@export_range(0.0, 1.0) var collapse_below := 0.5
## How many voxels a round breaks off for each point of environmental damage
## it does, nearest where it strikes.
@export var voxels_per_damage := 12.0
## How big a crater a blast leaves for each point of environmental damage it
## does, in cubic cells: the volume of the ball round where it goes off whose
## voxels it breaks off. A frag grenade does 10.
@export var crater_per_damage := 0.5

@export_group("Debris")
## How heavy the voxels are, in kilograms per cubic cell (a cell is a metre).
@export var density := 1500.0
@export_range(0.0, 1.0) var friction := 0.8
@export_range(0.0, 1.0) var bounce := 0.1
## How many voxels across, at most, the pieces are that what is left of a
## block crumbles into as it breaks: 1 for single voxels. Each piece is a
## physics body, and a whole block in single voxels would be thousands.
@export_range(1, 8) var crumble_size := 3


## How far from where it goes off a blast doing [param damage] environmental
## damage breaks this block's voxels, in cells: the radius of a ball
## [member crater_per_damage] cubic cells a point.
func crater_radius(damage: int) -> float:
	return pow(3.0 * crater_per_damage * maxf(damage, 0.0) / (4.0 * PI), 1.0 / 3.0)
