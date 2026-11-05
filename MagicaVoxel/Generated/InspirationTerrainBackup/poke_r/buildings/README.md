# poke_r buildings

Created 2026-11-03 (Claude), the way the [poke_o buildings](../../poke_o/buildings/README.md) were made. Every building in [poke_r.png](../../../poke_r.png): **two families, 14 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_r/`; this folder holds their generator, records, previews and the test that puts them into the game. ChatGPT's poke_r files are untouched, and so are the vegetation, rocks, deadwood, fences, ground tiles and props another agent added to `output/poke_r/` (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

These are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_r.png is 896 x 640 pixels of native pixel art: a village in a forest, four red houses along its paths and a flat-roofed building on a terrace at the right, with fields and a pond. A tile is 16 of its pixels (the buildings' roofs lie on that grid, both ways at multiples of 16), so a voxel is one of its pixels across and in depth. Its buildings (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeR_RedHouse` | The red house, four copies | 5 x 3 | 1, open to its tall gable roof | 96 x 64 x 144 | 88 x 58 x 143 | 129,397 |
| `PokeR_Shop` | The flat-roofed building at the right | 7 x 3 | 1, its walls six courses tall, open to its roof | 128 x 64 x 176 | 118 x 55 x 173 | 239,587 |

Template matching finds the red house four times, alike: laid over each other, the four differ only in what stands round them (trees, mailboxes, fences, the ground), never in the house; none is mirrored. The flat-roofed building is drawn once; its red awnings and shopfront door make it a shop, the name used here. No Nintendo marks are drawn on either, neither is cut off by the image's edge, and neither draws a way up; nothing but these is a building, so nothing needed asking. Not modelled here: the rest of the scene (the outdoor steps, the fields, fences, mailboxes, signs, trees, cliffs and the pond), much of it in other folders of `output/poke_r/`.

## Made for the game's grid

As the poke_o buildings: VCOM places only 16-cubed pieces, in a cell's middle, on the edge between two cells or on the corner where four meet, and a building enters a map as its street lamp does, drawn whole and cut into pieces placed together. So:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (eaves, verges, boards, awnings, handles).
- **Levels are z = 16k.** Level 0 is a building's own floor, a stone foundation standing in for the map's ground blocks (opened in MagicaVoxel a building sits on a one-tile stone plinth; in the game it is buried). Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice); both doors here are drawn a tile wide.
- **Windows** keep within a tile, or stand over a tile boundary where the art draws them so (each part its own window piece). Their glass is over a solid sill course a level high: a unit vaults in over the sill and has half cover at it from inside. Glass higher up (the house's gable windows, the shop's upper windows) is above the levels a unit fills and changes nothing in the fight.
- **No upper floors**: the art draws no way up (the user's rule: floors only where stairs are drawn), so each building is one storey open to its roof, its upper windows lighting it from above.
- **Corners** where four tiles meet are decoration to the fight: the house's corner boards and the shop's corner bricks stand there.
- **Every pattern repeats every 16 voxels** on the grid. Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** A tile is 16 across and in depth, and heights are foreshortened to **0.375**, as in poke_o.png: both doors are drawn 12 pixels tall (and 16 wide) for their two levels. Heights fitted to the art, measured in its projection from the ground line under each door: the red house's ground floor to z 62 under a white board (z 63-70, four voxels out), its side walls to z 70, its gable roof rising 1.7 a voxel in from its eaves (three out, z 69) to the ridge (z 142); the shop's walls to z 112 (two storeys of three courses each), an ochre band at their top (z 100-112), its roof a slab to z 122 under a floor of grey tiles inside a parapet to z 130, the red housing on it to z 172. Then every feature was checked against the art's pixels in that projection, and each falls within a pixel or so of where it is drawn (the verges and eaves, the board, the gable windows and vent, the doors and windows, the parapet's edges and faces, the band, the awnings, the housing's top and front), with two exceptions. The red house's back apex projects 8.6 pixels higher than drawn: the art draws the back of the roof lower and shallower than the front (its back verge falls 1.4 a pixel across, the front one 1.7), as a perspective view of a 3D model shows the far end smaller, and the roof here keeps its ridge level, true to the front. And its ground-floor window's glass sits 2 pixels higher than drawn, as the rules put glass in level 2. [previews/PokeR_*_art.png](previews/) draw each Base model in the art's own projection beside the source crop, at the same scale.

**Where the grid moves things.** The red house's walls are drawn 70 pixels across (4.4 tiles), five pixels inside a roof lying exactly on five of the map's tiles; here its walls are on those five tiles' edges, so it is twelve voxels wider than drawn, its roof three voxels further out each side. Its door is on its drawn map tile (tile 1, exactly), its windows within a voxel or two of their drawn columns; its roof is drawn some 54 deep at the eaves, three tiles with their overhangs. The shop's walls are drawn 106 pixels across (6.6 tiles), three pixels inside a roof on seven tiles; here seven tiles, its parapet flush with its walls, its door in the middle tile (drawn a voxel left of it).

## The user's decisions for these buildings

Carried over from the earlier images (2026-10-28): doors closed as drawn, each leaf in one slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by the stairs the art draws. poke_r asked for no new call: it draws no Nintendo marks, no building cut off by the image's edge, and no structure but these two buildings.

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides) is inferred in the same style and listed here.

- **RedHouse.** Five tiles by three, one storey open to its roof: white siding in horizontal boards, a blue strip along the walls' foot and grey boards at the corners; across the front a white board (z 63-70, four voxels out) under the tall front gable, in which stand two windows of two panes (periwinkle glass in a dark outline and a grey frame) and near the top a grey louvred vent; a steep gable roof of red, its ridge front to back over the middle, darker lines down its slopes near the eaves, a dark red verge two voxels out in front and four at the back, as drawn. The ground floor: the red door in tile 1 (closed), a window in its upper part, a lighter lower panel and a white handle, as drawn; a window of two panes over tiles 2 and 3. *Inferred:* the back (its own board, gable windows and vent as in front, two ground-floor windows), a window in each side, the interior (plank floor, open to the roof). Left out: the art draws two faint diagonal lines down the roof from its ridge toward the gable and small grey triangles at the gable's lower corners, which no single shape seen square-on gives; the roof here is a plain gable.
- **Shop.** Seven tiles by three, one storey of six courses open to its roof: cream walls, ochre bricks at the corners in courses of two tones, an ochre band under the roof; three pairs of windows above (sky-blue glass in a dark outline and a grey frame) and two pairs below in level 2, each under a red awning three voxels out over its frame, as drawn; the green door in tile 3 (closed), a round window in it and a gold handle, between ochre pilasters under an ochre lintel. Its flat roof: a slab to z 122, its top a floor of grey tiles in a grid, inside a grey parapet to z 130, six voxels wide at the sides and back and four at the front, its face dark below the floor's level and light above, its inner faces dark; on it, as drawn, a tall red housing (18 voxels by 13, to z 172), its front lighter at its edges and its left side shaded, a dark opening in its top inside a darker ring. *Inferred:* the back (its windows as in front), a window below and one above in each side, the interior. What the housing is the art does not say (a vent or the head of a stair); it is drawn as it stands, solid but for the opening.

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by the two buildings, 30 colours: the art's own (native pixel art, read pixel by pixel), the invented floors, ceilings and buried foundation stone noted as such, glass a little lighter so that what is behind still shows. The house's roof is one material in one set of colours on both slopes, as the game lights them itself (the art draws its right slope lighter).
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows and slots unchanged: siding boards twice as tall, the roof's lines and the floor tiles twice as far apart, the bricks in courses twice as tall, the window frames doubled, wider corner boards and bricks, a bigger handle.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (reds for the house's roof and door and the shop's awnings and housing, greys for the parapet, tiles and frames, lights for the siding and cream, woods for the ochre, leaves for the green door, blues for the house's foot); the creams are kept off 246, a pale yellow-green, as in poke_o. The mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material.
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* The red house four groups (roof, light, dark, glass: its door folded into the roof's red, its frames and blue foot into the grey); the shop six (its grey roof, cream, ochre, red, green door, glass: its frames folded into the roof's grey).
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry, the same in both (in the manifest), no two groups of a family on one entry.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`), which VCOM reads as glass (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)): the art's blues a little lighter at `_trans 0.7`, the house's periwinkle and the shop's sky blue. Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, as `SimpleWindow1`'s; the doors' panes are in the doors. Glass voxels (Base): the red house 1,900, the shop 3,794. There are no lights in these buildings, by the user's choice.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, and no glass in a sill course but a door's slot. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 14 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass, 14 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns); every tile is a floor at its level, under the roof; round each building at the two levels a unit fills, every wall, sill and closed door shut and every window open, a line of sight through each window at the eye and none through the walls or doors, a vault in over each sill, nothing else stepped through, and every tile reachable from the street; the view cut away at the roof. The geometry tested was checked to be the files' (each scene's stamping checksum recomputed from the final sculptor).
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away at the roof, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: ChatGPT's 151 poke_r files from before these buildings (its models, generator, records and previews) are unchanged, and `output/poke_r/`'s README.md and FILES.md only had a section on these buildings added at their end ([preserved-hashes.json](preserved-hashes.json)). The other agent's poke_r files were not touched, nor are they checked here.

**Not tested:** opening the files in MagicaVoxel's own editor; adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it and writes one 16-cubed `.vox` a kind, reusing a kind turned where a piece is one turned. What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces |
| --- | --- | --- | --- | --- |
| RedHouse | 189 | 85 | 18 | 2 |
| Shop | 284 | 86 | 30 | 2 |

The two Base buildings come to 171 kinds. The window pieces count each pane's pieces: the shop's paired windows stand over two and three tiles, the house's gable windows over two levels.

- **Floor** (level 0): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres`.
- **Door** (each leaf's two pieces): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting through windows.
- **Everything else**: solid, `cutaway`, worn as `SimpleWall1.tres`. The corner boards and bricks, on corners, block nothing.
- **Cutaway heights:** 4 for both (over the house's board and the shop's ground floor; the walls go on up to the roofs).
- **Costs:** a map's level palette gains the shared Base palette's 30 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_r/buildings/generate.py
$files = (Get-Content output/poke_r/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_r/$_" }
python tools/inspect_vox.py $files --output output/poke_r/buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom, never the game itself:
python output/poke_r/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_r/buildings/compose_previews.py <render folder>
python output/poke_r/buildings/compare_art.py
python output/poke_r/buildings/validate.py
```

`qa/godot/whole_import.gd` is run in the copy as poke_g's notes say. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O, [generate.py](generate.py) the files and manifest. The generator owns only the 14 building files and this folder's manifest.

## Decided

By the user (2026-10-28), for every building: doors closed, as drawn, each in exactly one doorway slot; no lights; TwoColor's minimal-colour rule; upper floors reached only by stairs the art draws. poke_r raised no new question.

Made without asking, on the evidence above: heights at 0.375, fitted to the doors; the game-grid conventions (as poke_o's); the red house five tiles by three (its walls on the five tiles its roof is drawn on, three deep from its roof's drawn depth), its roof a plain steep gable kept level to the back where the art draws the back lower, the diagonal lines and corner triangles drawn on it left out, its board, its vent; the flat-roofed building named a shop and made seven tiles by three, its door in the middle tile, its roof a slab with a parapet and a floor of tiles, its rooftop housing drawn as it stands (a vent or a stair's head, not named), its awnings three voxels out over their windows; the inferred sides, backs and insides listed under Each building; glass colours and clarity; the shared Base palette; each family's TwoColor groups, colours and folds; the crate mapping's material classes (246 left out of the creams'), index 253 for glass, and no two groups of a family on one crate entry.
