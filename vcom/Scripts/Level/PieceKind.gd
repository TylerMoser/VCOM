@tool
## One kind of thing a level is built of: a voxel model a block's size, 16
## voxels a side, drawn in MagicaVoxel and imported from a single-model .vox as
## a mesh at Scale 0.0625, as the blocks always were.
##
## A level ([LevelData]) places it in a slot: the middle of a cell, as a block
## stood in a GridMap, the edge between two cells side by side, as a fence or a
## wall does, its box then half in one cell and half in the other, or the
## corner where four cells meet, as a post does, a quarter of its box in each.
## Pieces may overlap, the one placed later winning voxel by voxel
## ([VoxelVolume]).
##
## To the rules a piece is whole until it breaks, wherever it stands: one in a
## cell fills that cell, one on an edge stands across that edge, and one on a
## corner is only decoration to the fight, blocking nothing, though it stands
## on what is under it and holds up what rests on it ([LevelRules]). A window
## ([member window]) is decoration to the fight wherever it stands. How it
## breaks is its [member destruction], as a block's was.
## Every level shares a kind, so, like a [Weapon], it keeps nothing of a level's.
class_name PieceKind
extends Resource

## What every level calls it ([member LevelData.kinds]). A level keeps the
## names, so a kind is never renamed once a level uses it.
@export var id: StringName
## Its model: a mesh imported from a .vox holding one model, at Scale 0.0625.
## Its voxels are read from that .vox as a level is built ([VoxelShape]).
@export var model: Mesh
## Where the model's mesh sits in the piece's box, whose origin is the box's
## middle: what a MeshLibrary item's mesh transform was. Down half a box for
## a model drawn standing on MagicaVoxel's ground, as the importer leaves it.
@export var model_transform := Transform3D(Basis.IDENTITY, Vector3(0.0, -0.5, 0.0))
## How it comes apart: a [VoxelDestruction] for a piece that wears away, a
## [ScriptedDestruction] for one that breaks into pieces cut in advance. None,
## and it never breaks.
@export var destruction: Destruction
## Whether the rules see it at all: a piece that is not solid is only drawn,
## for decoration, and stops no unit, round or sight line. Debris still lands
## on it and blood stains it.
@export var solid := true
## Whether the optional tile grid ([TileGrid]) is drawn on its voxels: on the
## ground, not on trees or crates.
@export var tile_grid := false
## Whether the level editor places it on an edge between two cells to begin
## with, rather than in the middle of one: fences and walls.
@export var edge_piece := false
## Whether the level editor places it on the corner where four cells meet to
## begin with: posts. It wins over [member edge_piece].
@export var corner_piece := false
## Whether it is part of a building, which may be cut away to see inside:
## walls, gables and roofs, not the ground, trees or crates. Only for show: the
## rules see a piece cut away as whole as any other.
@export var cutaway := false
## Whether it is a window: as a piece on a corner is, only decoration to the
## fight, wherever it stands. No sight line, step, cover, lean, throw, click or
## whole ray meets it, so units see, shoot, throw and vault through it, and it
## gives no cover; what makes a window cover is the piece under it, the sill,
## which is a piece like any other. A round traced voxel by voxel still meets
## its frame, as any piece that wears away, and passes its glass. It stands,
## holds up what rests on it and breaks as any piece does ([LevelRules]). Its
## glass, a colour MagicaVoxel draws as glass, is only for show: whole or
## shattered, the window is the same to the rules (Docs/GLASS.md).
@export var window := false


## What to call it in the level editor.
func display_name() -> String:
	return String(id) if id != &"" else resource_path.get_file().get_basename()
