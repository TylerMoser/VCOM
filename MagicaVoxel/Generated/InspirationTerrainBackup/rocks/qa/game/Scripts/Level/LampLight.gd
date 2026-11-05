@tool
## What a kind of piece's glowing voxels give off, where MagicaVoxel's numbers
## for them are not what is wanted: a kind's [member PieceKind.lamp]. Every
## setting left as it is takes MagicaVoxel's, so a kind with none, or with
## this left blank, is lit exactly as its .vox says (Docs/LIGHTS.md).
##
## In MagicaVoxel a lamp's bulb is painted with the Emit material. Its
## Emission is how brightly the voxels glow, at dusk and at night; its Power is
## how much light they cast round them: none at 0, and each step up doubles
## the light's brightness and reach (a street lamp's Power of 2 is brightness
## 4, reaching 7 cells). The light stands where the glowing voxels are, in
## their colour ([Lamps]).
##
## Shared by every piece of its kind, so, like a [Weapon], it keeps nothing of
## a level's.
class_name LampLight
extends Resource

## How brightly the voxels glow, 0 to 1, in place of MagicaVoxel's Emission;
## below 0, the Emission. 0 puts them out: they neither glow nor cast light.
@export_range(-1.0, 1.0, 0.01) var glow := -1.0
## How bright the light is, in place of what MagicaVoxel's Power makes it
## (2 to the Power); below 0, the Power's. 0 casts no light at all.
@export var energy := -1.0
## How far the light reaches, in cells, in place of what the Power makes it
## (3.5 times 2 to one less than the Power); 0 or less, the Power's, or 7 for
## a light that only [member energy] gives.
@export var reach := -1.0
## The light's colour; left clear (alpha 0), the colour of the glowing voxels,
## the average of them if they are several.
@export var color := Color(0.0, 0.0, 0.0, 0.0)
## Where the light stands from the middle of the glowing voxels, in cells, as
## the kind's model lies before the piece is turned (it turns with the piece).
@export var offset := Vector3.ZERO
## The size of the rectangle the light shines from, in cells, when lamps are
## area lights ([member Lamps.area_lights]): just under the glowing voxels,
## facing down.
@export var area_size := Vector2(0.3, 0.3)
