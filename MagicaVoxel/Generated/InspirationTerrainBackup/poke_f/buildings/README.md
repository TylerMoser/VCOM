# poke_f buildings

Created 2026-10-28 (Claude), the way the [poke_b game-ready buildings](../../poke_b/game_buildings/README.md) and the [poke_c buildings](../../poke_c/buildings/README.md) were made. Every building in [poke_f.png](../../../poke_f.png): **four families, 28 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_f/`; this folder holds their generator, records, previews and the test that puts them into the game. ChatGPT's poke_f streetlight is untouched; the vegetation and rocks another agent was adding to `output/poke_f/` at the same time were left alone (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

These are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_f.png is 576 x 672 pixels, 16-pixel tiles: an autumn town. Its buildings (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeF_BlueHouse` | The blue-roofed house, six copies | 4 x 3 | 1, of three courses, an attic in the gable | 80 x 64 x 112 | 74 x 56 x 109 | 96,058 |
| `PokeF_DomeCenter` | The building in the middle, under the Poke Ball dome | 6 x 4 | 1, of five courses | 112 x 80 x 144 | 110 x 78 x 132 | 273,598 |
| `PokeF_RoundShop` | The round-cornered building by the pond | 5 x 2 | 2, of two courses | 96 x 48 x 112 | 86 x 40 x 107 | 116,185 |
| `PokeF_TealHall` | The teal building at the bottom right, its left third in view | 8 x 3 and a 1 x 3 wing each side | 2 (three courses and two) | 176 x 64 x 144 | 164 x 56 x 142 | 284,416 |

The six blue houses are one design (template matching finds every copy's front within a few levels of difference, the rest being overlap and trees): two stand alone and four in two pairs, the right house of each pair four tiles along and a tile further back, so that their roofs overlap in the art. A pair is two copies of the model placed so. Not buildings, and not modelled: the streetlights (ChatGPT's `PokeF_TwinGlobeStreetlight`), the stairs and fences, the statue, the pond's bridge, the flower display, signs.

## Made for the game's grid

As the poke_b and poke_c buildings: VCOM places only 16-cubed pieces, in a cell's middle, on the edge between two cells or on the corner where four meet, and a building enters a map as its street lamp does, drawn whole and cut into pieces placed together. So:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (eaves, canopies, sills, planters, the centre's pillars).
- **Levels are z = 16k.** Level 0 is the building's own floor, a stone foundation standing in for the map's ground blocks (opened in MagicaVoxel a building sits on a one-tile stone plinth; in the game it is buried). Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice); the centre's and the hall's doors are two leaves in two slots.
- **Windows** keep within a tile or span two whole tiles (the centre's). Their glass is over a solid sill course a level high: a unit vaults in over the sill and has half cover at it from inside.
- **Upper floors are real** (a slab a level thick to the rules, a room over it), reached only where the art draws a way up (the user's choice). poke_f draws none, so the round shop's and the teal hall's upper rooms are closed off.
- **Corners** where four tiles meet are decoration to the fight: the centre's pillars and the round shop's rounded corners stand there, the walls' edges beside them solid.
- **Every pattern repeats every 16 voxels** on the grid (tiles, panels, boards, roof rows), so the same part of a wall in two tiles is the same piece.
- Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** As poke_c.png, the art draws a tile as 16 pixels across and in depth and foreshortens heights to about 0.46 of a voxel a pixel: the blue house's wall, three courses (48 voxels), is 20 pixels to its eaves. Footprints follow the art's tiles (walls rounded to whole tiles), heights the game, fitted so the model, drawn back in the art's projection, matches the sprite: the round shop's roof measures two tiles deep, not three; the hall's three, its roof standing over its fascia as drawn. [previews/PokeF_*_art.png](previews/) draw each Base model in the art's own projection beside the source crop.

## The user's decisions for these buildings

Carried over from poke_b and poke_c (2026-10-28): doors closed as drawn, each leaf in one slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by the stairs the art draws. Asked for poke_f:

- **The teal hall, modelled, mirrored.** It runs off the image's right edge and its lower half is behind trees, so only about its left third shows. It is completed as a symmetric hall: the visible part as drawn, the rest mirrored from it about the image's edge (its middle), the hidden ground storey inferred.
- **The dome as drawn.** The centre's red dome is the top of a Poke Ball, with its dark band and its button at the front, as in the art (not the generic marks chosen for poke_b's clinic).

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides) is inferred in the same style and listed here.

- **BlueHouse.** Four tiles by three, one storey of three courses, a 45-degree roof of blue tiles in rows with its ridge front to back, eaves four voxels out and verges three. The front gable is dark timber with a king post, light diagonal braces and two small attic windows, as drawn. On the front: dark corner posts, a timber band under the eaves with a light top, the blue panelled door (tile 1, closed) with a small window and a brass knob on its left, and a double window over tiles 2 and 3 in a white surround, each pane over a blue flower box of leaves and yellow and red flowers. Two beige chimneys on the right slope, the back one taller, as drawn. *Inferred:* the back gable as the front; a window in each side and two at the back; the interior (plank floor, open to the roof). The art's door stands a little left of the tile it is in; it is centred in tile 1, its knob moved onto the leaf.
- **DomeCenter.** Six tiles by four, one tall storey (levels 1-5): white walls with purple-blue windows each over two tiles (glass in levels 2-3), a glass double door over tiles 2 and 3 (closed) between banded wooden posts, under a dark blue canopy, two stone steps before it; above, a band of blue panels in a grid (levels 4-5) on a dark blue line; a flat roof of the same panels with a dark rim (level 6). On the roof the dome, 56 voxels across: red, a highlight on its upper left, the Poke Ball's dark band round its foot and its button at the front (a light rim, a dark ring, a light middle), as drawn. Four square pillars of banded wood at the corners rise above the roof to light caps. *Inferred:* the back (two windows), a window over two tiles in each side, the interior (tile floor). The art's dome is drawn wider than deep; it is round, a hemisphere.
- **RoundShop.** Five tiles by two, its corners rounded (radius 10; 12 in Cartoon), two storeys of two courses (ground levels 1-2, the slab level 3, upper levels 4-5): white panels in grey frames, dark columns at the rounded corners with a light line, a red band round it between the storeys (a voxel proud), a white band under the roof. The front, as drawn: two windows (tiles 1 and 3) over planters of pink and orange flowers, the glass double door (tile 2, closed); upstairs the wide window in the middle, white panels either side. A low hipped roof of salmon tiles, rounded at its corners like the walls, two voxels out, a dark lowest row. *Inferred:* windows on both storeys in each side and at the back; the interior (tile floors; the upper storey closed off). Its upper floor and its floor's paving stop at the rounded walls (corrected 2026-10-29: the first files had the upper floor's slab in whole tiles, which poked out past the four curved corners at the band; the seven files were made again and tested again, every check passing).
- **TealHall.** Completed mirrored (above). A main block eight tiles by three: a ground storey of three courses, teal with a dark teal wainscot; a beige band at the upper floor (level 4); an upper storey of two courses, a white strip with a window in every tile all round (glass in level 6), as drawn on the front; a brown fascia with a beige top line (level 7); a hipped teal roof on the walls, eaves three voxels out over the fascia, hip lines from its corners and a lighter flat top along its ridge, as drawn. A lower teal wing either side, a tile wide and three deep, four levels high under a flat teal roof, a window in its front as the art's left wing has. *Inferred, the art hiding them:* the right half (mirrored), the ground storey's front (a double door in its middle, tiles 4 and 5, closed; tall windows in tiles 2, 3, 6 and 7), the back, the wings opening into the hall through its side walls, the interior (the upper storey closed off).

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by all four buildings, 87 colours sampled from the art (the invented floors, ceilings and buried foundation stone noted as such), at fixed indices.
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows and slots unchanged: broader tiles and panels, two-voxel frames, chunkier posts, pillars and chimney caps, the house's gable braces bolder and its flower boxes plainer, a thicker band and a bigger button on the dome, rounder corners on the shop, a deeper eave and a bigger step on the hall.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (greys, lights, woods, reds, teals, blues, leaves, flowers); the mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material. The palette has no teal of the hall's kind, so the hall turns blue (252).
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* Groups of similar materials, each family giving its groups its own colour from the art: the blue house 6 (light, blue, wood, leaf, flower, glass), the centre 6 (light, blue, red, dark, wood, glass), the shop 6 (light, red, grey, leaf, flower, glass; its planters' wood folded into its grey), the hall 4 (teal, light, dark, glass), glass included.
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry, the same in both (in the manifest), no two groups of a family on one entry.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`, `_trans 0.7`, as the game's own `make_windows.py` writes it), which VCOM reads as glass (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)). Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, as `SimpleWindow1`'s. Colours lightened a little from the art's so the room behind shows: the house's and the centre's purple-blue, the shop's sky blue, the hall's pale cyan. Glass voxels (Base): house 1,368, centre 2,288, shop 1,460, hall 4,452. There are no lights in these buildings, by the user's choice: the streetlights stand beside them.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, and no glass in a sill course but a door's slot. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 28 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass, 28 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns); every tile of every storey is a floor at its level, under the roof; round each storey, at the two levels a unit fills, every wall, sill and closed door is shut and every window open; a line of sight through each window at the eye and none through the walls or doors; a vault in over each sill; nothing else can be stepped through; every ground floor is reachable from the street, and the shop's and the hall's upper storeys are not (closed off, the user's rule); the view cuts away at each storey.
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away at each storey, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: ChatGPT's poke_f streetlight files (its seven models and its `lights/` folder) are unchanged, and `output/poke_f/`'s README.md and FILES.md only had a section on these buildings added at their end ([preserved-hashes.json](preserved-hashes.json)). Another agent was writing poke_f vegetation and rocks into the same folder while these were made; none of its files was touched, nor are they checked here.

**Not tested:** opening the files in MagicaVoxel's own editor (they are written as the poke_b and poke_c buildings are, version 200 with a rooted scene graph, a layer, a palette and a material for each used colour); adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it (a cell's middle for floors, slabs, roofs, the dome and the chimneys; an edge for walls, doors, windows, canopies, bands and planters; a corner for posts, pillars and rounded corners) and writes one 16-cubed `.vox` a kind, reusing a kind turned where a piece is one turned (the game's turn: `(x, z)` to `(z, 15 - x)`). Then each kind goes into `Pieces.tres` and the building into a brush (its pieces, slot offsets and turns from the layout the cutter writes). What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces |
| --- | --- | --- | --- | --- |
| BlueHouse | 141 | 67 | 16 | 2 |
| DomeCenter | 240 | 84 | 24 | 4 |
| RoundShop | 182 | 70 | 15 | 2 |
| TealHall | 374 | 78 | 40 | 4 |

All four Base buildings come to 299 kinds.

- **Floor** (level 0): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres`.
- **Door** (each leaf's two pieces): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting through windows. A door kind of its own lets one be made passable later.
- **Everything else**: solid, `cutaway`, worn as `SimpleWall1.tres`.
- **Cutaway heights:** the house 4, the centre 6, the shop 3 and 6, the hall 4 and 7 (each storey's ceiling).
- **Costs:** a map's level palette gains the shared Base palette's 87 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_f/buildings/generate.py
$files = (Get-Content output/poke_f/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_f/$_" }
python tools/inspect_vox.py $files --output output/poke_f/buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom, never the game itself:
python output/poke_f/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_f/buildings/compose_previews.py <render folder>
python output/poke_f/buildings/compare_art.py
python output/poke_f/buildings/validate.py
```

`integration.py` copies `qa/godot/building_probe.gd` into the copy, cuts and imports the pieces there, and runs it (`--scenes` runs only some); `qa/godot/whole_import.gd` is run the same way (`--script res://_probe/whole_import.gd -- <manifest.json> <output/poke_f> <out.json>`) and its result copied to `qa/whole-import.json`, as the integration report is to `qa/integration-report.json`. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O, [generate.py](generate.py) the files and manifest. The generator owns only the 28 building files and this folder's manifest.

## Decided

By the user (2026-10-28): doors closed, as drawn, each in exactly one doorway slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by stairs the art draws; the teal hall modelled and completed mirrored; the centre's dome as drawn, the Poke Ball's band and button kept.

Made without asking, on the evidence above: the game-grid conventions (as poke_b's, with storeys of three courses for the house, five for the centre, two for the shop and three and two for the hall, fitted to the art's heights); footprints rounded from the art's tiles (the shop two tiles deep and the hall three, as their roofs measure); one model for the six houses; the centre's dome round where the art draws it wider than deep, its upper band and roof opaque blue panels where the art's could be read as glass, its pillars at the corners as decoration; the shop's rounded corners as corner pieces; everything of the hall the art hides (above); the inferred sides, backs and insides listed under Each building; glass clarities and colours; the shared Base palette; each family's TwoColor groups, colours and folds; the crate mapping's material classes, index 253 for glass, and no two groups of a family on one crate entry.
