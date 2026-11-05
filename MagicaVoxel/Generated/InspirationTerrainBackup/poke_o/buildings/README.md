# poke_o buildings

Created 2026-11-03 (Claude), the way the [poke_n buildings](../../poke_n/buildings/README.md) were made. Every building in [poke_o.png](../../../poke_o.png): **three families, 21 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_o/`; this folder holds their generator, records, previews and the test that puts them into the game. ChatGPT's poke_o files are untouched, and so are the vegetation, rocks, deadwood, fences, ground tiles and props another agent added to `output/poke_o/` (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

These are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_o.png is 640 x 640 pixels of native pixel art: a coastal village, six buildings round a paved square between the forest and a beach. A tile is 16 of its pixels (the buildings' roofs and the square's paving lie on that grid, both ways at multiples of 16), so a voxel is one of its pixels across and in depth. Its buildings (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeO_GableHouse` | The gabled house, three copies | 4 x 2 | 1, its walls to z 67 at the sides, open to the roof | 80 x 48 x 112 | 72 x 40 x 102 | 69,570 |
| `PokeO_SkylightHouse` | The skylight house, two copies | 4 x 2 | 1, its walls up to its split roof, open to it | 80 x 48 x 112 | 72 x 41 x 97 | 71,050 |
| `PokeO_WideHouse` | The wide house at the top right | a main block 6 x 2 and a wing 3 x 1 in front of its middle | 1, open to its roofs | 112 x 64 x 112 | 104 x 55 x 112 | 125,372 |

Template matching finds the gabled house three times, alike (each copy differs from the first by 1.6 levels in 255 on average; mirrored, by 19), the skylight house twice (1.7), and the wide house once, its upper roof the skylight house's drawn wider (9.9). No Nintendo marks are drawn on any of them, none is cut off by the image's edge, and none draws a way up; nothing but the houses is a building, so nothing needed asking. Not modelled here: the rest of the scene (parasols, loungers, the sandcastle, palms, the planter, signs, mailboxes, trees, cliffs and the sea), much of it in other folders of `output/poke_o/`.

## Made for the game's grid

As the poke_n buildings: VCOM places only 16-cubed pieces, in a cell's middle, on the edge between two cells or on the corner where four meet, and a building enters a map as its street lamp does, drawn whole and cut into pieces placed together. So:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (eaves, verges, sills, boards, handles).
- **Levels are z = 16k.** Level 0 is a house's own floor, a stone foundation standing in for the map's ground blocks (opened in MagicaVoxel a house sits on a one-tile stone plinth; in the game it is buried). Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice); every door here is drawn exactly a tile wide.
- **Windows** keep within a tile, or stand over a tile boundary where the art draws them so (each half its own window piece). Their glass is over a solid sill course a level high: a unit vaults in over the sill and has half cover at it from inside. Glass higher up (vents, high windows, the skylight, the dormer) is above the levels a unit fills and changes nothing in the fight.
- **No upper floors**: the art draws no way up (the user's rule: floors only where stairs are drawn), so each house is one storey open to its roof, the wide house's high windows lighting it from above.
- **An opening a unit walks through inside a building** (the wide house's, from its wing into its main block) is open in whole tiles at the levels a unit fills, the wall over it on piers at the corners.
- **Corners** where four tiles meet are decoration to the fight: the piers stand there.
- **Every pattern repeats every 16 voxels** on the grid. Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** A tile is 16 across and in depth, and heights are foreshortened to **0.375** here, less than in the earlier images (0.46 to 0.5): every door is drawn 12 pixels tall (and 16 wide) for its two levels. Heights fitted to the art, measured in its projection from the ground line under each door: the gabled house's side walls to z 67 under eaves (three out, z 68) rising 0.97 a voxel in to its ridge (z 101), a light board across its front at z 64-67 under the khaki gable; the skylight house's and the wide house's flat roofs at z 95, their facets descending 0.6 a voxel to the left eave; the wide house's wing a lean-to from z 68 at its front to z 76 at the main block's wall. Then every feature was checked against the art's pixels in that projection, and each falls within a pixel or two of where it is drawn: the roofs' edges, ridges and verges, the board, the vents and high windows, the doors and windows, the skylight, the rooftop units. [previews/PokeO_*_art.png](previews/) draw each Base model in the art's own projection beside the source crop, at the same scale.

**Where the grid moves things.** The houses' walls are drawn 58 pixels across (3.6 tiles), three pixels inside the tile edges, under roofs lying exactly on them (four tiles); here the walls are on the tile edges, four tiles, under roofs three voxels out, so each house is eight voxels wider than drawn (its walls 66 across where 58 are drawn, its roof 72 where 64 are). Each door and window is in the tile the art draws it in, within a voxel or two of its drawn columns. A house's depth is not drawn; its roof is drawn 40 to 42 deep, two tiles with their overhangs, and so two tiles it is. The wide house's main block is drawn 89 pixels across (5.5 tiles) under a roof of six, here six tiles; its wing a tile deep in front of tiles 1-3, its door in the middle one, as drawn.

## The user's decisions for these buildings

Carried over from the earlier images (2026-10-28): doors closed as drawn, each leaf in one slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by the stairs the art draws. poke_o asked for no new call: it draws no Nintendo marks, no building cut off by the image's edge, and no structure but houses.

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides) is inferred in the same style and listed here. The three share one tileset: cream walls darkening toward what is over them, a dark lintel over the ground floor (z 48-50), a teal strip along the walls' foot, the red door (three small dark panes across its top, a gold handle at its left) and windows of glass in level 2 in a grey frame over a white sill.

- **GableHouse.** Four tiles by two, one storey open to its roof: across the front a light board (z 64-67, three voxels out) under the khaki gable, a small vent window in it (dark glass, grey frame); a front gable roof of pink tiles, its ridge front to back, in stripes along it under a light band, its eaves three out (z 68) rising 0.97 a voxel in to the ridge (z 101), its verges three out, as drawn. On the left slope a dormer with its own little gable roof along x, its gable facing left glazed in a white frame. The front: the red door in tile 1 (closed) and a window in tile 2, as drawn. *Inferred:* the back (two windows, the board and the gable with its vent as in front), a window in each side, the interior (plank floor, open to the roof). The dormer is a reading: the art draws its triangle of glass as if seen from the side (the tileset copies a 3D model drawn in perspective), and no shape seen square-on from the front shows a triangle so; a dormer facing left with a glazed gable is the reading made, which from straight ahead shows as a small roof and from the left as the drawn triangle.
- **SkylightHouse.** Four tiles by two, one storey open to its roof: the art's split roof, flat over tiles 2 and 3 (z 95) with a skylight in it (a pane flush with the roof's top in a dark frame a voxel proud, the frame deeper along its back, the roof cut away under it), and over tiles 0 and 1 a facet descending 0.6 a voxel to its left eave (z 73), in courses darkening toward the eave, as drawn; the roof four voxels out in front and three at the back. The front wall rises to the roof: the red door in tile 1 and a window in tile 2, the lintel, a light board a voxel proud (z 64-67), and over it a band of wall with a small high window under the roof's front edge, as drawn. *Inferred:* the back (two windows), a window in each side, the interior.
- **WideHouse.** A main block of six tiles by two under the skylight house's split roof (flat over tiles 2-5 at z 95, its facet over tiles 0 and 1), two grey air-conditioning units standing on its flat part (a light rim round a dark fan grille on top, dark slots across their fronts), as drawn; in front of its tiles 1-3 a wing a tile deep under a lower split roof, a lean-to against the main block's wall from z 68 at its front to z 76 (so its back meets the main roof's edge, as drawn), its facet over tile 1; the red door in the wing's middle tile (closed); on the main block's front, in tile 4, a window under two high windows (dark glass over white sills) just under the roof's edge, as drawn. Inside, one room: the wing opens into the main block across its three tiles, up to the wing's roof, the wall above on piers at the tile corners. *Inferred:* the back (two windows and two high ones), a window in each side, the wing's plain sides and its front beside the door (the art hides them behind a mailbox and a small tree), the opening and piers, the interior.

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by the three buildings, 36 colours: the art's own (native pixel art, read pixel by pixel, one tileset for all three), the invented floors, ceilings and buried foundation stone noted as such, glass a little lighter so that what is behind still shows.
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows and slots unchanged: walls in two plain bands, roofs in wider stripes and courses, a door's three panes made one, inner frames on the windows, a bigger handle, one row of slots on the rooftop units.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (greys, lights, woods, reds, teals, and for the roofs a class of the crate palette's pinks, 213, 214, 219 and 220); the creams are kept off 246, a pale yellow-green that would have turned them green. The mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material.
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* The gabled house and the skylight house five groups (roof, light, dark, door, glass: the window frames folded into the walls' cream, the teal foot into the khaki); the wide house six (its large grey rooftop units a colour of their own).
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry, the same in both (in the manifest), no two groups of a family on one entry.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`), which VCOM reads as glass (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)): the art's blues a little lighter at `_trans 0.7`, and a darker blue for the vents and high windows the art draws dark. Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, as `SimpleWindow1`'s; the skylight's lies flush with the roof's top, the roof's layers under it cut away; the dormer's fills its gable. Glass voxels (Base): the gabled house 1,234, the skylight house 1,098, the wide house 1,350. There are no lights in these buildings, by the user's choice.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, and no glass in a sill course but a door's slot. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 21 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass, 21 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns); every tile is a floor at its level, under the roof; round each house at the two levels a unit fills, every wall, sill and closed door shut and every window open, a line of sight through each window at the eye and none through the walls or doors, a vault in over each sill, nothing else stepped through, and every tile reachable from the street (the wide house's wing through its main block); the view cut away at the roof. The geometry tested was checked to be the files' (each scene's stamping checksum recomputed from the final sculptor).
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away at the roof, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: ChatGPT's 217 poke_o files from before these buildings (its models, generator, records and previews) are unchanged, and `output/poke_o/`'s README.md and FILES.md only had a section on these buildings added at their end ([preserved-hashes.json](preserved-hashes.json)). The other agent's poke_o files were not touched, nor are they checked here.

**Not tested:** opening the files in MagicaVoxel's own editor; adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it and writes one 16-cubed `.vox` a kind, reusing a kind turned where a piece is one turned. What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces |
| --- | --- | --- | --- | --- |
| GableHouse | 116 | 62 | 13 | 2 |
| SkylightHouse | 114 | 72 | 6 | 2 |
| WideHouse | 194 | 115 | 13 | 2 |

The three Base buildings come to 249 kinds. The window pieces count each pane's pieces: the gabled house's two vents stand over two tiles and two levels each.

- **Floor** (level 0): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres`. The skylight and the dormer's gable lie in roof pieces, which stay solid.
- **Door** (each leaf's two pieces): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting through windows.
- **Everything else**: solid, `cutaway`, worn as `SimpleWall1.tres`. The wide house's piers, on corners, block nothing.
- **Cutaway heights:** 4 for all three (over the ground floor's board and lintel; the walls go on up to the roofs).
- **Costs:** a map's level palette gains the shared Base palette's 36 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_o/buildings/generate.py
$files = (Get-Content output/poke_o/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_o/$_" }
python tools/inspect_vox.py $files --output output/poke_o/buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom, never the game itself:
python output/poke_o/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_o/buildings/compose_previews.py <render folder>
python output/poke_o/buildings/compare_art.py
python output/poke_o/buildings/validate.py
```

`qa/godot/whole_import.gd` is run in the copy as poke_g's notes say. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O, [generate.py](generate.py) the files and manifest. The generator owns only the 21 building files and this folder's manifest.

## Decided

By the user (2026-10-28), for every building: doors closed, as drawn, each in exactly one doorway slot; no lights; TwoColor's minimal-colour rule; upper floors reached only by stairs the art draws. poke_o raised no new question.

Made without asking, on the evidence above: heights at 0.375, fitted to the doors; the game-grid conventions (as poke_n's); the houses four tiles by two (their walls on the tile edges where they are drawn three pixels inside, two tiles deep from their roofs' drawn depth); the gabled house's dormer read as a dormer facing left with a glazed gable; the split roofs read as flat parts with facets, the skylight flush in a raised frame; the wide house's rooftop units as air-conditioning units, its wing a tile deep under a lean-to (as the drawn roof reaches the main roof's edge), the opening and piers between them; the inferred sides, backs and insides listed under Each building; glass colours and clarity; the shared Base palette; each family's TwoColor groups, colours and folds; the crate mapping's material classes (a pink class for the roofs, 246 left out of the creams'), index 253 for glass, and no two groups of a family on one crate entry.
