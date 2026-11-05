# poke_g buildings

Created 2026-10-28/29 (Claude), the way the [poke_f buildings](../../poke_f/buildings/README.md) were made. Every building in [poke_g.png](../../../poke_g.png): **seven families, 49 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_g/`; this folder holds their generator, records, previews and the test that puts them into the game. ChatGPT's poke_g files are untouched; the vegetation, rocks and streetlight another agent was adding to `output/poke_g/` at the same time were left alone (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

These are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_g.png is 560 x 768 pixels, 16-pixel tiles: a forest town. Its buildings (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeG_GreenHouse` | The stepped green house, two copies | 4 x 3: a block 2 x 3, a wing 2 x 3 | 2 in the block, 1 in the wing | 80 x 64 x 112 | 68 x 54 x 98 | 109,308 |
| `PokeG_GreenHouseMirrored` | The third stepped green house, drawn mirrored | 4 x 3 | as above | 80 x 64 x 112 | 68 x 54 x 98 | 109,308 |
| `PokeG_GreenWideHouse` | The green house under one roof, four copies | 4 x 3 | 2 | 80 x 64 x 112 | 68 x 54 x 98 | 121,456 |
| `PokeG_DomeCenter` | The building in the middle, under the Poke Ball dome | 6 x 4 | 1, of five courses | 112 x 80 x 144 | 110 x 78 x 132 | 273,598 |
| `PokeG_RedCenter` | The red-roofed building at the bottom middle | 5 x 3 | 1, of three courses | 96 x 64 x 96 | 86 x 59 x 93 | 117,048 |
| `PokeG_Mart` | The shop at the bottom left | 4 x 3 | 1, of three courses | 80 x 64 x 96 | 68 x 54 x 88 | 93,914 |
| `PokeG_WoodLodge` | The lodge at the top right | 5 x 4 and a porch tile | 1, of three courses | 96 x 96 x 96 | 86 x 85 x 96 | 159,159 |

The seven green houses are two designs: template matching finds the stepped house three times (once mirrored, its wing on the left) and the wide house four times, the bottom two behind trees. The domed centre is poke_f's centre drawn again: recoloured pixel by pixel, its blue panels and bands become red-brown tiles and everything else is the same, so its geometry is poke_f's, copied whole, and only its palette is poke_g's. Not buildings, and not modelled: the streetlights, the benches, the signs, the fences and stairs, the log.

## Made for the game's grid

As the poke_f, poke_b and poke_c buildings: VCOM places only 16-cubed pieces, in a cell's middle, on the edge between two cells or on the corner where four meet, and a building enters a map as its street lamp does, drawn whole and cut into pieces placed together. So:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (eaves, canopies, sills, signs, the canopy's posts).
- **Levels are z = 16k.** Level 0 is the building's own floor, a stone foundation standing in for the map's ground blocks (opened in MagicaVoxel a building sits on a one-tile stone plinth; in the game it is buried). Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice); the domed centre's door is two leaves in two slots.
- **Windows** keep within a tile, or stand over a tile boundary where the art draws them so (the green houses'), each half its own window piece. Their glass is over a solid sill course a level high: a unit vaults in over the sill and has half cover at it from inside.
- **Upper floors are real** (a slab a level thick to the rules, a room over it), reached only where the art draws a way up (the user's choice). poke_g draws none, so the green houses' upper rooms are closed off.
- **Corners** where four tiles meet are decoration to the fight: the domed centre's pillars, the red centre's rounded corners and the lodge's porch posts stand there, the walls' edges beside them solid.
- **A porch a tile out** (the lodge's) is a tile of the footprint: its floor a level-0 piece, its roof the middle of its tile a level over a unit's head.
- **Every pattern repeats every 16 voxels** on the grid (seams, panels, boards, tiles, dots, planks), so the same part of a wall in two tiles is the same piece.
- Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** As poke_f.png, the art draws a tile as 16 pixels across and in depth and foreshortens heights to about 0.46 of a voxel a pixel. Footprints follow the art's tiles, measured pixel by pixel (walls rounded to whole tiles), heights the game, fitted so the model drawn back in the art's projection matches the sprite: the red centre's and the Mart's roofs measure three tiles deep, the lodge's four with its porch a tile out. [previews/PokeG_*_art.png](previews/) draw each Base model in the art's own projection beside the source crop.

## The user's decisions for these buildings

Carried over from poke_b, poke_c and poke_f (2026-10-28): doors closed as drawn, each leaf in one slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by the stairs the art draws. Asked for poke_g:

- **Nintendo's marks as drawn, all of them**: the domed centre's Poke Ball (its band and button), the red centre's Poke Ball emblem over its door, and the Mart's sign with MART on it.
- **The mirrored green house is a model of its own.** The game turns pieces but cannot mirror them, so the stepped house drawn with its wing on the left is `PokeG_GreenHouseMirrored`, the same house mirrored voxel for voxel, its pieces kinds of their own.

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides) is inferred in the same style and listed here.

- **GreenHouse.** Four tiles by three. A block of two storeys two tiles wide (the ground storey levels 1-3 with the beam in level 3, the upper floor's slab in level 3, the upper storey levels 4-5) and a wing of one storey two tiles wide beside it, levels 1-3, the door in its first tile (closed, red-brown planks, its knob on the right) with a cream jamb beside it, as drawn. Brown panels framed by dark timber lines, darker in the ground storey; a dark green plinth; the beam round the house between the storeys, a voxel proud, light above and dark below; cream window frames round two-pane windows, the block's standing over the boundary in its middle as drawn (each half its own window piece), glass in level 2 below and level 5 above. Flat roofs of green standing seams (the art draws them flat, and a pitch would show its steps as lines across the seams), seams every eight voxels with lighter and darker panels, a darker edge and its outline at the eaves and verges, two voxels out at the eaves and one at the verges; the block's from its walls' top (level 6), the wing's from its own (level 4) against the block's wall. *Inferred:* a window in each side's middle tile on both storeys (the block's right side above the wing's roof), the back's windows as the front's, the ground floor opening into the wing through the middle tile of the wall between them, which bears the upper storey's wall; the interior (plank floors; the upper storey closed off).
- **GreenHouseMirrored.** The stepped house mirrored left to right, voxel for voxel: its door, storeys and windows mirrored with it.
- **GreenWideHouse.** Four tiles by three, two storeys as the stepped house's block, all under one flat seamed roof. The front, as drawn: the door in tile 1 (closed, its knob on the left) with a cream jamb, a window within tile 2 on the ground floor; upstairs two windows over the boundaries between tiles 0 and 1 and tiles 2 and 3, standing in one cream panel across the front. *Inferred:* the sides' and the back's windows (the back's on both storeys as the front's upper ones), the interior (the upper storey closed off).
- **DomeCenter.** poke_f's domed centre, its geometry copied whole (see [poke_f's notes](../../poke_f/buildings/README.md)): six tiles by four, one tall storey of five courses, white walls, purple-blue windows each over two tiles, the glass double door under a canopy between banded posts, two steps before it, a band of tiles above and a flat tiled roof, on it the red dome of a Poke Ball with its band and button at the front, banded wooden pillars at the corners. Here its panels, band and canopy are red-brown tiles, as poke_g.png draws them.
- **RedCenter.** Five tiles by three, one storey of three courses with rounded corners (radius 8; 9 in Cartoon), the arcs corner pieces: light blue-grey walls, white at the rounded corners, a grey foot, a dark line under a band round its top (level 3); dark grey fluted pillars two voxels proud in the end tiles, front and back, as drawn. The front: the glass door (tile 2, closed) in a dark grey frame, its knob; over it a red canopy seven voxels out, its top sloping a little from the wall, narrowing toward its front edge as drawn, on two dark grey posts; above the canopy the Poke Ball emblem, as drawn, two voxels proud, on the middle section's front, which rises a course above the walls (level 4). The roof (levels 4-5), red, in three sections front to back as drawn: a barrel vault over the middle and, either side, a quarter round rising from the side walls to it, a shell three voxels thick two voxels out all round, rounded at its corners like the walls, shaded in stripes across as the art is; the walls rise under it to meet it. *Inferred:* the sides and back (windows of the door's glass, one in each side and two at the back, glass in level 2; the back's pillars as the front's), a ceiling at the walls' top, the interior (tile floor). The art draws the emblem round as seen from above; here it is a disc on the wall, round to the eye in front.
- **Mart.** Four tiles by three, one storey of three courses: light blue-grey walls, white for five voxels at each corner, a dark line under a band round its top (level 3), a flat roof (level 4) white over the corners; on it the blue slab, inset five voxels, rounded at its corners (radius 6) and along its top edge (radius 4), square tiles with pale dots on its top, a light stripe round its face, as drawn. The front: the glass door (tile 1, closed) in a dark grey frame, its knob; the shop window over tiles 2 and 3, three panes and a transom near its top, glass in level 2 over a grey riser (the art's window runs to the ground: its lower part here is the sill course, solid); dark grey columns two voxels proud beside the left corner, between the door and the window and beside the right corner; in front of the slab the sign, a board three voxels thick from the band up, white along its top, MART on its face in blue in the art's five-by-five letters, doubled in height (proud by a voxel in Cartoon). *Inferred:* windows of the shop window's kind in each side and two at the back, the interior (tile floor).
- **WoodLodge.** Five tiles by four and a porch tile in front of tile 2, one storey of three courses: at each end of every wall a corner panel and a timber post, as drawn, plain panelling between, a beam along the top; windows of small panes (grey bars every five voxels across, white ones every seven up) in tiles 1 and 3 of the front, glass in levels 2-3 over the sill course; the door in tile 2 (closed, dark planks, an iron ring). Over it all a thick flat roof (level 4 and two voxels of level 5) of planks along the front, two voxels out, its fascia vertical boards, a light rim along its edge; on it the raised part, inset five to eight voxels, its corners chamfered, faced and planked the same way; the flat roof carried a tile out over the porch, a flagged path under it, on two timber posts at its front corners, as drawn. *Inferred:* windows in tiles 1-3 at the back and in the middle two tiles of each side, a ceiling under the roof, the interior (plank floor). The art draws the windows a little toward the ends and the porch about twelve voxels deep; here they are within their tiles and the porch a tile out.

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by all seven buildings, 119 colours sampled from the art (the invented floors, ceilings and buried foundation stone noted as such; the domed centre's poke_f's but for its red-brown tiles), at fixed indices.
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows and slots unchanged: thicker roofs, broader seams, panels, boards and tiles, fewer bars in the windows, chunkier posts, bigger knobs, rounder corners on the red centre, a bigger emblem, fewer dots on the Mart's slab and its letters a voxel proud, wider chamfers on the lodge.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (greys, lights, woods, reds, blues, leaves, flowers); the mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material.
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* Groups of similar materials, each family giving its groups its own colour from the art: the green houses 4 (green, wood, light, glass; the doors and dark timber folded into the wood), the domed centre 6 (light, brown, red, dark, wood, glass), the red centre 4 (light, red, grey, glass), the Mart 4 (light, blue, grey, glass; the letters in the slab's blue), the lodge 4 (wood, dark, light, glass; the path folded into the dark), glass included.
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry, the same in both (in the manifest), no two groups of a family on one entry.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`, `_trans 0.7`, as the game's own `make_windows.py` writes it), which VCOM reads as glass (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)). Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, as `SimpleWindow1`'s. Colours lightened a little from the art's so the room behind shows: the green houses' cyan, the centres' and the Mart's and the lodge's blue-purples. Glass voxels (Base): the stepped houses 1,080 each, the wide house 1,340, the domed centre 2,288, the red centre 936, the Mart 1,051, the lodge 2,592. There are no lights in these buildings, by the user's choice: the streetlights stand beside them.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, and no glass in a sill course but a door's slot. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 49 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass, 49 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns); every tile of every storey is a floor at its level, under the roof; round each storey, at the two levels a unit fills, every wall, sill and closed door is shut and every window open; a line of sight through each window at the eye and none through the walls or doors; a vault in over each sill; nothing else can be stepped through; every ground floor is reachable from the street, and the green houses' upper storeys are not (closed off, the user's rule); the view cuts away at each storey. The geometry tested was checked to be the files' (each scene's stamping checksum recomputed from the final sculptor).
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away at each storey, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: ChatGPT's 157 poke_g files from before these buildings (its models, generator, records and previews) are unchanged, and `output/poke_g/`'s README.md and FILES.md only had a section on these buildings added at their end ([preserved-hashes.json](preserved-hashes.json)). Another agent was writing poke_g vegetation, rocks and a streetlight into the same folder while these were made; none of its files was touched, nor are they checked here.

**Not tested:** opening the files in MagicaVoxel's own editor (they are written as the poke_f buildings are, version 200 with a rooted scene graph, a layer, a palette and a material for each used colour); adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it (a cell's middle for floors, slabs and roofs; an edge for walls, doors, windows, canopies, bands, signs and the canopy's posts; a corner for pillars, rounded corners and the porch's posts) and writes one 16-cubed `.vox` a kind, reusing a kind turned where a piece is one turned (the game's turn: `(x, z)` to `(z, 15 - x)`). Then each kind goes into `Pieces.tres` and the building into a brush (its pieces, slot offsets and turns from the layout the cutter writes). What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces |
| --- | --- | --- | --- | --- |
| GreenHouse | 158 | 74 | 14 | 2 |
| GreenHouseMirrored | 158 | 74 | 14 | 2 |
| GreenWideHouse | 162 | 78 | 17 | 2 |
| DomeCenter | 240 | 84 | 24 | 4 |
| RedCenter | 155 | 81 | 4 | 2 |
| Mart | 128 | 47 | 6 | 2 |
| WoodLodge | 213 | 67 | 18 | 2 |

All seven Base buildings come to 505 kinds (the mirrored house's 74 its own: mirror images are no turn of the stepped house's).

- **Floor** (level 0): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres`.
- **Door** (each leaf's two pieces): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting through windows. A door kind of its own lets one be made passable later.
- **Everything else**: solid, `cutaway`, worn as `SimpleWall1.tres`.
- **Cutaway heights:** the green houses 3 and 6, the domed centre 6, the red centre 4, the Mart 4, the lodge 4 (each storey's ceiling).
- **Costs:** a map's level palette gains the shared Base palette's 119 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_g/buildings/generate.py
$files = (Get-Content output/poke_g/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_g/$_" }
python tools/inspect_vox.py $files --output output/poke_g/buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom, never the game itself:
python output/poke_g/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_g/buildings/compose_previews.py <render folder>
python output/poke_g/buildings/compare_art.py
python output/poke_g/buildings/validate.py
```

`integration.py` copies `qa/godot/building_probe.gd` into the copy, cuts and imports the pieces there, and runs it (`--scenes` runs only some); `qa/godot/whole_import.gd` is run the same way (`--script res://_probe/whole_import.gd -- <manifest.json> <output/poke_g> <out.json>`) and its result copied to `qa/whole-import.json`, as the integration report is to `qa/integration-report.json`. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O, [generate.py](generate.py) the files and manifest. The generator owns only the 49 building files and this folder's manifest.

## Decided

By the user (2026-10-28): doors closed, as drawn, each in exactly one doorway slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by stairs the art draws; Nintendo's marks as drawn (both Poke Balls, the MART sign); the mirrored green house a model of its own.

Made without asking, on the evidence above: the game-grid conventions (as poke_f's: storeys of three courses, two for the green houses' upper storeys where the art draws about one and a half, the beam the ground storey's third course); footprints rounded from the art's tiles, measured pixel by pixel (the stepped house's block and wing two tiles each where the art draws two and a half and one and a half, chosen because its windows and door then stand where drawn; the red centre's and the Mart's three tiles deep, as their roofs measure); the green roofs flat; windows over tile boundaries where the art draws them so, within their tiles where it nearly does (the wide house's lower window, the lodge's); the red centre's roof as a barrel vault between two quarter rounds, its emblem a vertical disc, its canopy in the front margin on two posts, the art's shallow bay round its door left out; the Mart's walls three courses where the art draws two and a half (a door is two levels), its shop window's lower part a solid riser, its sign a vertical board, its letters the art's doubled in height; the lodge's porch a tile out on corner posts, its flat roofs a hollow slab with a board fascia; the domed centre's geometry copied whole from poke_f; everything inferred listed under Each building; glass clarities and colours; the shared Base palette; each family's TwoColor groups, colours and folds; the crate mapping's material classes, index 253 for glass, and no two groups of a family on one crate entry.
