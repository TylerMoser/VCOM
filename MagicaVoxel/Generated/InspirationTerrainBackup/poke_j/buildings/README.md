# poke_j buildings

Created 2026-10-29 (Claude), the way the [poke_i buildings](../../poke_i/buildings/README.md) were made. Every building in [poke_j.jpg](../../../poke_j.jpg): **two families, 14 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_j/`; this folder holds their generator, records, previews and the test that puts them into the game. ChatGPT's poke_j files are untouched, and so are the vegetation, rocks, lights and deadwood another agent was adding to `output/poke_j/` at the same time (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

These are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_j.jpg is 735 x 565 pixels: a forest village with two ponds, stone stairs, a street lamp and four buildings. Like poke_i it is a JPEG and **scaled down**: a tile is 12.25 of its pixels, not 16 (the forest's trees, two tiles across, repeat every 24.5 pixels across and 49 down), so the art is at 0.765 of its own pixel size and blurred by the scaling and the compression. Every measurement below is in the art's own voxels (its pixels / 0.765), taken from regions, edges and traced lines rather than single pixels. Its buildings (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeJ_RedHouse` | The red house, three copies | 5 x 3 | 1, its walls five courses tall, open to the roof | 96 x 64 x 160 | 96 x 54 x 152 | 143,868 |
| `PokeJ_GreyHouse` | The grey-roofed building at the top | a wing 2 x 2, a middle 3 x 3, a right part 2 x 4 | 1, the wing's walls two and a half courses, the rest four | 128 x 80 x 112 | 118 x 72 x 112 | 236,695 |

Template matching finds the red house three times, none mirrored (a copy differs from the first by 16 levels on average, the mirrored drawing by 22 or more); the three were averaged to measure it, which beats down the JPEG's noise. No Nintendo marks are drawn on either building, and neither draws a way up, so nothing needed asking. Not buildings, and not modelled: the stairs, fences, ponds, plots, the lamp post (another agent's lights) and the trees.

## Made for the game's grid

As the poke_i buildings: VCOM places only 16-cubed pieces, in a cell's middle, on the edge between two cells or on the corner where four meet, and a building enters a map as its street lamp does, drawn whole and cut into pieces placed together. So:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (eaves, verges, sills, beams, flower boxes).
- **Levels are z = 16k.** Level 0 is the building's own floor, a stone foundation standing in for the map's ground blocks (opened in MagicaVoxel a building sits on a one-tile stone plinth; in the game it is buried). Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice).
- **The art draws its doors on the map's tiles and its walls half a tile off them**: the red house's walls are five tiles across under a roof six tiles across, and its door is in the roof's third tile, over the walls' second tile boundary. In VCOM a door fills one tile between walls on tile boundaries, so the red house's door is half a tile left of where it is drawn (tile 1); the grey house's walls stand within three voxels of their drawn places but for its right part's right wall, seven voxels in (the part is two and a quarter tiles across in the art, two here), and its door is in its middle part's middle tile, four voxels right of where it is drawn.
- **Windows** keep within a tile, or stand over a tile boundary where the art draws them so (each half its own window piece). Their glass is over a solid sill course a level high: a unit vaults in over the sill and has half cover at it from inside. Glass higher up (the red house's fan windows, the grey house's long window over its door) is above the levels a unit fills and changes nothing in the fight.
- **No upper floors**: the art draws no way up anywhere (the user's rule: floors only where stairs are drawn), so each building is one storey open to its roof; the red house's fan windows and the grey house's skylight light it from above.
- **An opening a unit walks through inside a building** (the grey house's arcade between its wing and its middle) is open in whole tiles at the two levels a unit fills, the wall above it on piers at the corners between the tiles, as poke_i's day care's arcades are.
- **Corners** where four tiles meet are decoration to the fight: the houses' corner posts and the arcade's piers stand there.
- **Every pattern repeats every 16 voxels** on the grid. Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** In the art's own voxels a tile is 16 across and in depth and heights are foreshortened to about 0.46, as in every image so far. The red house's walls measure exactly five tiles across, its roof six from eave to eave and a little over three deep; the grey house's parts two, a little over three and two and a quarter across. Heights fitted to the art (its door, beam, eaves and apex for the red house, traced column by column; its fascias, roof edges and bases for the grey house): the red house's beam at z 64, its walls to z 96 under the eaves, its roof rising 1.1 a voxel in to z 142 and its chimney to z 151; the grey house's walls to z 80 and the wing's to z 56, a level of roof over each. [previews/PokeJ_*_art.png](previews/) draw each Base model in the art's own projection beside the source crop, enlarged to the model's scale.

## The user's decisions for these buildings

Carried over from the earlier images (2026-10-28): doors closed as drawn, each leaf in one slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by the stairs the art draws. Nothing new needed asking for poke_j: it draws no marks and no way up.

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides) is inferred in the same style and listed here.

- **RedHouse.** Five tiles by three, one storey: cream stone walls in courses between dark corner posts, a dark beam round it a voxel proud (z 64-71). A steep gable roof of red tiles, its ridge front to back, rising 1.1 a voxel in (to z 142), three voxels thick, the tiles in rows along the ridge with no joints across them, as drawn, a dark line along the ridge; the eaves seven voxels out and the verges two, as drawn, dark barge boards under the verges. A stone chimney at the back of the left slope: cream stone in courses, a darker head, a light cap and a dark flue, its top over the ridge. The front gable, from the beam to the roof, half-timbered as drawn: a post up its middle and two braces from its foot out to the roof, a voxel proud, and between them a fan window, its arc in a dark frame, the timbers its bars, its glass a voxel back. The front: the red door in tile 1 (closed), boarded, in a dark frame five voxels a side with a lintel over it; a window of four panes in tile 3, a dark frame and light bars, its head level with the lintel, as drawn. *Inferred:* the back gable as the front's, fan window and all; a window in each side's middle tile and two at the back (tiles 1 and 3), the front's kind; the interior (plank floor, open to the roof). The art's window reaches nearly to the ground; here its glass starts over the sill course.
- **GreyHouse.** Three parts, stepped as drawn: a low wing on the left, two tiles by two, set a tile back from the middle; the middle, three tiles by three; the right part, two tiles by four, a tile in front of the middle. One storey: the wing's walls to z 56, the rest's to z 80; cream stone walls in courses, white posts at the outer corners, as drawn. Flat roofs a level thick, two voxels out, as drawn: grey tops with standing seams along y (the art's stripes) and a dark line round them, their edges dark in three bands, light over dark, the wing's lower. On the right part's roof a skylight, as drawn: glass in a white frame two voxels over the roof, the roof open under it, light streaks across it in Base. Three white vents at the back, as drawn: a light grey stack under a white cap with a dark slot across it, two on the main roof and one on the wing's. The front: the wing's window of two panes over its tile boundary, a box of pink flowers under it; the middle's door in tile 3 (closed), wood in a dark frame with a pane in its top, under a long window across the middle; the right part's window of four panes over its tile boundary, a light apron and two flower boxes under it. *Inferred:* the windows of the wing's left side and back, the middle's back and the right part's side and back, the fronts' kinds; the right part's side in front of the middle in stone (the art draws a strip of it); the interior: one room, an arcade on two stone piers opening the wing to the middle and the middle open to the right part, floor tiles. The art draws the right part a little over half a tile in front of the middle and the wing three quarters of a tile behind it; both are a tile here, and the art's slanted joint between the middle and the right part is a square step.

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by the two buildings, 64 colours taken from the art (the JPEG's: medians of whole regions, the red house's from its three copies averaged, the small features' from their brightest pixels; the invented floors, ceilings and buried foundation stone noted as such), at fixed indices.
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows and slots unchanged: rows of roof tiles twice as deep and plain, stone blocks twice as big and plain, wider posts, timbers, door boards and frames, inner frames on the windows, a wider lip on the chimney; the grey house's seams twice as wide, its flower boxes topped with plain pink, a wider skylight frame without streaks, plain vent caps.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (greys, lights, woods, reds, flowers, leaves); the mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material.
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* The red house four groups (roof, light, wood, glass: the red door folded into the roof's red, the chimney's stone into the light, its head and flue into the wood), the grey house five (roof, light, wood, flower, glass: the roofs one mid grey, between their light seamed tops and dark edges, since the tops' own grey drew them near white beside the light walls; the stone walls, white posts and frames one light colour; the vents' slots in the roof's grey; the flowers' pink kept as the one accent).
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry, the same in both (in the manifest), no two groups of a family on one entry.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`), which VCOM reads as glass (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)): the windows' and fan windows' pale blues at `_trans 0.7`, the skylight a deeper blue at 0.6 with lighter streaks at 0.5, the grey house's door pane at 0.5. Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, as `SimpleWindow1`'s; the skylight's lies flat in its frame. Glass voxels (Base): the red house 3,828, the grey house 4,138. There are no lights in these buildings, by the user's choice.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, and no glass in a sill course but a door's slot. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 14 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass, 14 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns); every tile is a floor at its level, under the roof; round each building, at the two levels a unit fills, every wall, sill and closed door is shut and every window open; a line of sight through each window at the eye and none through the walls or doors; a vault in over each sill; nothing else can be stepped through; every tile reachable from the street (the grey house's middle through its arcade and its open side); the view cuts away at the roof. The geometry tested was checked to be the files' (each scene's stamping checksum recomputed from the final sculptor).
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away at the roof, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: ChatGPT's 130 poke_j files from before these buildings (its models, generator, records and previews) are unchanged, and `output/poke_j/`'s README.md and FILES.md only had a section on these buildings added at their end ([preserved-hashes.json](preserved-hashes.json)). Another agent was writing poke_j vegetation, rocks, lights and deadwood into the same folder while these were made; none of its files was touched, nor are they checked here.

**Not tested:** opening the files in MagicaVoxel's own editor; adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it and writes one 16-cubed `.vox` a kind, reusing a kind turned where a piece is one turned. What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces |
| --- | --- | --- | --- | --- |
| RedHouse | 204 | 101 | 34 | 2 |
| GreyHouse | 233 | 103 | 30 | 2 |

The two Base buildings come to 204 kinds.

- **Floor** (level 0): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres`. The red house's fan windows are window pieces too, high in its gables.
- **Door** (each leaf's two pieces): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting through windows.
- **Everything else**: solid, `cutaway`, worn as `SimpleWall1.tres`. The skylight's pieces are roof pieces with glass in them, solid to the rules.
- **Cutaway heights:** the red house 4, the grey house 3 (the wing's roof starts in level 3).
- **Costs:** a map's level palette gains the shared Base palette's 64 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_j/buildings/generate.py
$files = (Get-Content output/poke_j/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_j/$_" }
python tools/inspect_vox.py $files --output output/poke_j/buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom, never the game itself:
python output/poke_j/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_j/buildings/compose_previews.py <render folder>
python output/poke_j/buildings/compare_art.py
python output/poke_j/buildings/validate.py
```

`qa/godot/whole_import.gd` is run in the copy as poke_g's notes say. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O, [generate.py](generate.py) the files and manifest. The generator owns only the 14 building files and this folder's manifest.

## Decided

By the user (2026-10-28), for every building: doors closed, as drawn, each in exactly one doorway slot; no lights; TwoColor's minimal-colour rule; upper floors reached only by stairs the art draws.

Made without asking, on the evidence above: reading the scaled JPEG at 12.25 pixels a tile and measuring the red house from its three copies averaged; the game-grid conventions (as poke_i's); the red house five tiles by three with its walls, its door moved half a tile left into tile 1 and its window into tile 3 (the art draws both on the map's tiles, between the walls' boundaries); its heights fitted to the art (beam z 64, walls to z 96, pitch 1.1, chimney to z 151); its fan window's shape, the timbers' slope and the gable's stone; the grey house's grid (its parts two, three and two tiles across, the right part narrower than drawn, the door in the middle's middle tile), its steps a whole tile each, its square step for the art's slanted joint, the wing's walls to z 56 and the rest's to z 80; flat seamed roofs a level thick; the skylight a pane in the roof; one room inside, the arcade on piers and the open side; the inferred sides, backs and insides listed under Each building; glass clarities and colours; the shared Base palette; each family's TwoColor groups, colours and folds (the grey house's roofs a mid grey, its light stone and white trim one colour, its flowers kept); the crate mapping's material classes, index 253 for glass, and no two groups of a family on one crate entry.
