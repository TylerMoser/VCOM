# poke_h buildings

Created 2026-10-28/29 (Claude), the way the [poke_g buildings](../../poke_g/buildings/README.md) were made. The one building in [poke_h.png](../../../poke_h.png): **one family, 7 complete VOX files**, in Base and all six established treatments. The files are directly in `output/poke_h/`; this folder holds their generator, records, previews and the test that puts them into the game. ChatGPT's poke_h files are untouched; the vegetation another agent was adding to `output/poke_h/` at the same time was left alone (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

This is **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so it can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The building in the art

poke_h.png is 560 x 560 pixels, 16-pixel tiles: farmland, its fields, haystacks, fences and a bridge round one house (its region in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeH_Farmhouse` | The house in the middle of the fields | 5 x 3, a porch row of 5 in front, the stair's 3 beside it | 2, of two courses, and the outside stair | 112 x 80 x 128 | 104 x 73 x 121 | 225,695 |

The farmhouse is poke_b's flower cottage drawn again: aligned with it, the art matches pixel for pixel from the ridge down to the upper storey's floor (86-92% of the pixels the same, the rest trees and vines), and below that a porch across the front replaces the cottage's two hoods over its door and its bay. So its body, roof, windows and stair are [poke_b's cottage](../../poke_b/game_buildings/README.md), copied and moved a tile back to make room for the porch's row, and its colours are the cottage's. Not modelled: the garden's flower borders round the porch (scenery, not the house), the fields, fences, haystacks and the bridge.

## Made for the game's grid

As the poke_g, poke_f, poke_b and poke_c buildings:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (eaves, the bay, the flower boxes, the stair's stringer and its vines).
- **Levels are z = 16k.** Level 0 is the building's own floor, a stone foundation standing in for the map's ground blocks, boards under the porch. Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice): the front door and the upper door at the stair's landing.
- **Windows** keep within a tile, glass over a solid sill course a level high, so a unit vaults in over the sill; the upper storey's tall window by the stair's middle is glass at both its levels, climbed in by from the stair.
- **Upper floors are real**, reached only where the art draws a way up (the user's choice): here the outside stair, a level a tile over three tiles to a landing at the upper door.
- **Corners** where four tiles meet are decoration to the fight: the house's corner posts and the porch's two posts and their vines stand there.
- **The porch** is a row of five tiles of the footprint in front of the house: its floor boards level-0 pieces, its roof (level 3) over a unit's head, never in the slot between the stair's first tile and the ground before it.
- **Every pattern repeats every 16 voxels** on the grid, but the vines' (placed by a fixed hash). Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** As poke_b.png's, whose drawing this is: a tile 16 pixels across and in depth, heights foreshortened to about 0.46 of a voxel a pixel. The porch, drawn about 15 voxels out with its posts' feet behind the garden's flower borders, is a tile out. [previews/PokeH_Farmhouse_art.png](previews/PokeH_Farmhouse_art.png) draws the Base model in the art's own projection beside the source crop.

## The user's decisions

Carried over (2026-10-28): doors closed as drawn, each leaf in one slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by the stairs the art draws, here the outside stair; the cottage's marks and makings as poke_b's were. Nothing new was asked for poke_h: the farmhouse is the cottage with a porch.

## The building

- **Farmhouse.** poke_b's flower cottage (its notes have it in full): five tiles by three, two storeys of two courses, cream walls, a bell-cast roof of red shingles with its ridge front to back and two roof lights on its left slope, a small window high in each gable; the front's door (tile 1, closed, teal, with a sidelight and brass), the box bay window (tile 3), two-pane windows upstairs over flower boxes; on its right the outside stair, its red-brown stringer, to the landing at the upper door, and the tall window one climbs in by. New, as drawn in poke_h.png: **the porch**, a shingled roof across the whole front a tile out, from just over the band at the wall (z 58) down to its front edge (z 50, its underside a voxel above a unit's head), its shingles in rows darker toward the edge, joints every six voxels; on **two posts** at its front corners **wrapped in flowering vines** (leaves, pink, rose, orange and yellow flowers); boards under it; the bay's top a shingled lid under it; and **vines with flowers up the stair's stringer**. *Inferred:* as the cottage's, its sides, back and interior.

## Treatments

Seven files, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)).

- **Base**: 47 colours, the cottage's and the porch's and vines' sampled from poke_h.png, at fixed indices.
- **Cartoon**: the cottage's Cartoon (broader shingles and boards, two-voxel frames, chunkier posts, the bell roof higher), and here the porch's shingle rows broader, its posts chunkier, the vines in simpler clumps.
- **CratePalette**: the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte, each colour mapped to its nearest entry among those allowed for its material; glass crate index 253, kept for glass alone.
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* The cottage's 7 groups: light, red, dark (the wood folded into it), teal, leaf, flower, glass.
- **The mixtures** as the other families': Cartoon_TwoColor the Cartoon geometry in the group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor each group on one crate entry (in the manifest), no two on one.

## Glass

MagicaVoxel's **Glass** material (`_type _glass`), as the cottage's: the windows' pale blue at `_trans 0.7`, the roof lights' darker glass at 0.45. Glass voxels (Base): 2,117. No lights, by the user's choice.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back (canvas, voxels, palette, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape) and refuses to overwrite a file it did not write last.
- **[validate.py](validate.py)** re-checks that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, no glass in a sill course but a door's slot or the window climbed in by ([validation-summary.json](validation-summary.json)).
- **Structural audit**: `tools/inspect_vox.py`, 7 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own importer at Scale 0.0625 ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: all seven treatments cut into the game's pieces, placed in a level of grass, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level stamped is the model voxel for voxel; every tile of both storeys is a floor at its level, under the roof; every wall, sill and closed door shut and every window open, at the two levels a unit fills; sight through each window and none through the walls; a vault in over each sill from the street; the stair a level a tile, climbed from the grass before it, and the climb in at its tall window; nothing else stepped through; both storeys reachable from the street; the view cut away at each storey. The first run found the porch's roof standing in the slot between the stair's first tile and the grass before it, which shut the way up; that was mended (the porch's end past the house is the porch's own edge piece) and the run made again. The geometry tested was checked to be the files'.
- **Visual review**: renders in the game's own renderer from four sides, from the game's camera, cut away at each storey, at dusk and at night ([previews/](previews/)), and the Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: ChatGPT's 301 poke_h files from before this building are unchanged, and `output/poke_h/`'s README.md and FILES.md only had a section on it added at their end ([preserved-hashes.json](preserved-hashes.json)). Another agent was writing poke_h vegetation into the same folder meanwhile; none of its files was touched.

**Not tested:** opening the files in MagicaVoxel's own editor; adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through it.

## Putting it into the game

Nothing in VoxelXCOM was changed. Cut it as the test does ([qa/cut_pieces.py](qa/cut_pieces.py)): Base comes to 251 pieces of 128 kinds, 13 of them window pieces and 4 door pieces. Floors (level 0, the porch's boards among them) solid, `tile_grid`, not `cutaway`; windows `window` and `cutaway`, worn as `SimpleWindow1.tres`; doors solid, `cutaway`; the stair's pieces solid and not `cutaway` (it stays in view as the ground does); everything else solid, `cutaway`, worn as `SimpleWall1.tres`. Cutaway heights 3 and 6. A map's level palette gains 47 colours.

## Reproduction

```powershell
python output/poke_h/buildings/generate.py
$files = (Get-Content output/poke_h/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_h/$_" }
python tools/inspect_vox.py $files --output output/poke_h/buildings/structural-audit.json
python output/poke_h/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_h/buildings/compose_previews.py <render folder>
python output/poke_h/buildings/compare_art.py
python output/poke_h/buildings/validate.py
```

`qa/godot/whole_import.gd` is run in the copy as poke_g's notes say. The generator owns only the 7 building files and this folder's manifest.

## Decided

By the user (2026-10-28), for every building: doors closed as drawn, each in one slot; no lights; TwoColor's minimal-colour rule; upper floors reached only by stairs the art draws.

Made without asking: the farmhouse as poke_b's cottage, its geometry and colours copied, with the porch added (the art is the cottage's drawing above the porch); the porch a row of footprint tiles a tile out, its roof sloping from z 58 to z 50 so a unit passes under it, on two posts at its front corners; the vines' placement (a fixed hash, each leaf touching the post, the stringer or a leaf already grown, so the model holds together); the garden's flower borders left out as scenery; the porch's boards; the bay's lid under the porch; the inferred sides, back and interior as the cottage's.
