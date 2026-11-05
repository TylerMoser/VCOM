# poke_i buildings

Created 2026-10-29 (Claude), the way the [poke_g buildings](../../poke_g/buildings/README.md) were made. Every building in [poke_i.jpg](../../../poke_i.jpg): **three families, 21 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_i/`; this folder holds their generator, records, previews and the test that puts them into the game. ChatGPT's poke_i files are untouched; the vegetation and rocks another agent was adding to `output/poke_i/` at the same time were left alone (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

These are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_i.jpg is 736 x 559 pixels: a forest village with berry plots, flower beds and a stream. Unlike the other images it is a JPEG and **scaled down**: a tile is 9.5 of its pixels, not 16 (measured from the forest's repeat, 19.0 pixels for its two-tile trees, and the fences' posts, one a tile), so the art is at 0.594 of its own pixel size and blurred by the scaling and the compression. Every measurement below is in the art's own voxels (its pixels / 0.594), taken from regions, edges and template matches rather than single pixels. Its buildings (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeI_SmallHouse` | The small house, three copies | 4 x 2 | 1, of three courses, open to the roof | 80 x 48 x 96 | 72 x 40 x 93 | 68,706 |
| `PokeI_ChimneyHouse` | The house with the chimney, two copies | 5 x 3 | 1, of four courses, open to the roof | 96 x 64 x 144 | 88 x 56 x 130 | 127,282 |
| `PokeI_DayCare` | The large building at the top, by its fenced yard | a hall 6 x 3 and a wing 2 x 2 | 1, of four courses; the nave open to its clerestory | 144 x 64 x 128 | 136 x 60 x 127 | 192,729 |

Template matching finds the small house three times and the chimney house twice, none mirrored. The large building is drawn like Diamond and Pearl's day care, its yard of hedges and a pond beside it. No Nintendo marks are drawn on any of them. Not buildings, and not modelled: the yard's hedges and pond, the fences, stairs, bridges, plots and flower beds, the signs.

## Made for the game's grid

As the poke_g, poke_f, poke_b and poke_c buildings: VCOM places only 16-cubed pieces, in a cell's middle, on the edge between two cells or on the corner where four meet, and a building enters a map as its street lamp does, drawn whole and cut into pieces placed together. So:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (eaves, sills, beams, the canopy).
- **Levels are z = 16k.** Level 0 is the building's own floor, a stone foundation standing in for the map's ground blocks (opened in MagicaVoxel a building sits on a one-tile stone plinth; in the game it is buried). Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice); the day care's door is two leaves in two slots.
- **Windows** keep within a tile, or stand over a tile boundary where the art draws them so (each half its own window piece). Their glass is over a solid sill course a level high: a unit vaults in over the sill and has half cover at it from inside.
- **No upper floors**: the art draws no way up anywhere (the user's rule: floors only where stairs are drawn), so each building is one storey open to its roof; the chimney house's gable windows and the day care's clerestory light it from above.
- **An opening a unit walks through inside a building** (the day care's arcades) is open in whole tiles at the two levels a unit fills, the wall above it standing on piers at the corners between the tiles: any piece in an edge's slot shuts that edge to the rules, so a wall with a doorway in part of a tile would be a wall.
- **Corners** where four tiles meet are decoration to the fight: the houses' corner posts and the day care's piers and posts stand there.
- **Every pattern repeats every 16 voxels** on the grid. Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** In the art's own voxels a tile is 16 across and in depth and heights are foreshortened to about 0.46, as in every image so far. The small house's walls measure three and a half tiles across and its roof two and a half deep, eave to eave; the chimney house's nearly five by three; the day care's hall six by three and its wing two by two. Heights fitted to the eaves, apexes and doors: the small house's eaves about z 70 (three courses here), the chimney house's and the day care's about z 80 (four), the small roof rising 26, the steep one 46. [previews/PokeI_*_art.png](previews/) draw each Base model in the art's own projection beside the source crop, enlarged to the model's scale.

## The user's decisions for these buildings

Carried over from the earlier images (2026-10-28): doors closed as drawn, each leaf in one slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by the stairs the art draws. Nothing new needed asking for poke_i: it draws no marks and no way up.

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides) is inferred in the same style and listed here.

- **SmallHouse.** Four tiles by two, one storey of three courses: brown board walls between dark corner posts, a dark base course, a beam round it under the eaves. A gable roof of orange shingles with its ridge front to back, rising 0.8 a voxel in (26 to the ridge), three voxels thick, eaves and verges three out, a light band along the ridge and a light batten across the left slope near the back, as drawn. The front gable dark boards and battens, as drawn. The front: the red door in tile 1 (closed) with a pale jamb at its left and a knob, a two-pane window in a thick white frame in tile 2. *Inferred:* a window over the middle of each side and two at the back, the back gable as the front's, the interior (plank floor, open to the roof). The art's batten, a light bar level across the slope, is drawn as a batten at one depth, which the slope tips.
- **ChimneyHouse.** Five tiles by three, one storey of four courses: brown board walls between dark posts, a beam round it (level 4) and the course above it cream, as drawn. A steep gable roof of orange shingles, its ridge front to back, rising 1.15 a voxel in (46 to the ridge), a light ridge band; a grey stone chimney on the right slope at the back, its cap and dark flue, standing over the ridge, as drawn. The front gable cream, dark boards and battens for the twelve voxels under the ridge, and two windows over tiles 1 and 3 (glass in level 5). The front: the red door in tile 1 (closed), a three-pane window in tile 3 in a cream panel across tiles 2 to 4, as drawn. *Inferred:* a window in each side's middle tile and two at the back, the back gable as the front's with its two windows, the interior (open to the roof).
- **DayCare.** A hall six tiles by three and a wing two by two on its right, one storey of four courses, cream walls, a dark base course, a beam round it at the eaves' course, dark timber posts at the corners, either side of the door's bay and where the wing meets the hall, as drawn. The hall is a nave of four tiles between two aisles of one, as a clerestory hall is built: the aisles under a hipped roof of orange tiles from the eaves (z 80) rising a voxel a voxel to the nave's walls; the nave's walls rising two courses over it (to z 111), cream, the clerestory window over the canopy (tiles 2 and 3) as drawn and windows in its back and sides; over the nave a faceted roof rising from its walls to a flat top (z 124) with two light rails along the top's edges, as drawn; the wing under a hipped roof of its own, a valley between them. The front: the double door of dark glass (tiles 2 and 3, closed) under a hood of red-brown tiles seven voxels out; windows of four panes in tiles 1 and 4 and over the wing's two tiles. Inside, arcades open the aisles and the wing to the nave at the two levels a unit fills, the walls above them on corner piers. *Inferred:* the arcades and piers (the art shows no inside; they carry the nave's walls), the back's and sides' windows, the interior (plank floor; the nave open to its roof). The art's roof is faceted further than the grid allows simply; it is read as aisles' hips and a clerestory, as its outline and the cream gable over the canopy suggest.

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by the three buildings, 64 colours taken from the art (the JPEG's: medians and clusters of whole regions, the small features' from their brightest pixels; the invented floors, ceilings and buried foundation stone noted as such), at fixed indices.
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows and slots unchanged: broader shingles, boards and battens, chunkier posts, a wider ridge band and batten, inner frames on the windows, wider rails on the day care.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (greys, lights, woods, reds, flowers); the mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material.
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* Four groups each, glass included: the houses' roof, wood, light, glass (the red doors folded into the roofs' orange, the chimney's stone into the light), the day care's roof, light, wood, glass (the canopy in the roof's colour).
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry, the same in both (in the manifest), no two groups of a family on one entry.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`), which VCOM reads as glass (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)): the windows' pale blues at `_trans 0.7`, the day care's door darker glass at 0.45, as drawn. Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, as `SimpleWindow1`'s. Glass voxels (Base): the small house 700, the chimney house 1,508, the day care 5,004. There are no lights in these buildings, by the user's choice.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, and no glass in a sill course but a door's slot. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 21 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass, 21 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns); every tile is a floor at its level, under the roof; round each building, at the two levels a unit fills, every wall, sill and closed door is shut and every window open; a line of sight through each window at the eye and none through the walls or doors; a vault in over each sill; nothing else can be stepped through; every tile reachable from the street; the view cuts away at the roof. The cut was also checked to leave the day care's arcades with no piece at the two levels a unit fills (open), their piers corner pieces. The geometry tested was checked to be the files' (each scene's stamping checksum recomputed from the final sculptor).
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away at the roof, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: ChatGPT's 130 poke_i files from before these buildings (its models, generator, records and previews) are unchanged, and `output/poke_i/`'s README.md and FILES.md only had a section on these buildings added at their end ([preserved-hashes.json](preserved-hashes.json)). Another agent was writing poke_i vegetation and rocks into the same folder while these were made; none of its files was touched, nor are they checked here.

**Not tested:** opening the files in MagicaVoxel's own editor; adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it and writes one 16-cubed `.vox` a kind, reusing a kind turned where a piece is one turned. What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces |
| --- | --- | --- | --- | --- |
| SmallHouse | 105 | 52 | 7 | 2 |
| ChimneyHouse | 188 | 83 | 9 | 2 |
| DayCare | 308 | 130 | 30 | 4 |

All three Base buildings come to 265 kinds.

- **Floor** (level 0): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres`.
- **Door** (each leaf's two pieces): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting through windows.
- **Everything else**: solid, `cutaway`, worn as `SimpleWall1.tres`.
- **Cutaway heights:** the small house 4, the chimney house 5, the day care 5 (the roof).
- **Costs:** a map's level palette gains the shared Base palette's 64 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_i/buildings/generate.py
$files = (Get-Content output/poke_i/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_i/$_" }
python tools/inspect_vox.py $files --output output/poke_i/buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom, never the game itself:
python output/poke_i/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_i/buildings/compose_previews.py <render folder>
python output/poke_i/buildings/compare_art.py
python output/poke_i/buildings/validate.py
```

`qa/godot/whole_import.gd` is run in the copy as poke_g's notes say. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O, [generate.py](generate.py) the files and manifest. The generator owns only the 21 building files and this folder's manifest.

## Decided

By the user (2026-10-28), for every building: doors closed, as drawn, each in exactly one doorway slot; no lights; TwoColor's minimal-colour rule; upper floors reached only by stairs the art draws.

Made without asking, on the evidence above: reading the scaled JPEG at 9.5 pixels a tile; the game-grid conventions (as poke_g's); footprints rounded from the art's tiles (the small house four by two where its walls measure three and a half by two; the chimney house five by three; the day care's hall six by three and its wing two by two); the small house's walls three courses and the others four, fitted to the eaves; the roofs' pitches fitted to the apexes (0.8 and 1.15 a voxel); one storey each, open to the roof; the small house's light bar a batten across the slope; the chimney's place; the day care read as a clerestory hall (aisles' hips, a raised nave with a faceted flat-topped roof and rails, a hipped wing) with arcades on corner piers inside, its canopy a hood; the inferred sides, backs and insides listed under Each building; glass clarities and colours; the shared Base palette; each family's TwoColor groups, colours and folds; the crate mapping's material classes, index 253 for glass, and no two groups of a family on one crate entry.
