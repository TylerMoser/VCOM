# poke_n buildings

Created 2026-11-03 (Claude), the way the [poke_m buildings](../../poke_m/buildings/README.md) were made. Every building in [poke_n.png](../../../poke_n.png): **three families, 21 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_n/`; this folder holds their generator, records, previews and the test that puts them into the game. ChatGPT's poke_n files are untouched, and so are the vegetation, rocks, lights, deadwood, fences, ground tiles and props another agent added to `output/poke_n/` (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

These are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_n.png is 638 x 766 pixels of native pixel art: a village in a forest, three houses along a path that runs down past a lake to a roofed gate. A tile is 16 of its pixels (its forest's trees, two tiles across, repeat every 32), so a voxel is one of its pixels across and in depth, as in poke_m. Its buildings (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeN_RedHouse` | The red house, two copies | 5 x 2 | 1, its walls to z 84, open to the roof | 96 x 48 x 144 | 96 x 47 x 133 | 111,269 |
| `PokeN_Chalet` | The house at the top | an L: a wing 2 x 3, an A-frame block 4 x 2 | 1, of two courses, open to its roofs | 112 x 80 x 144 | 104 x 71 x 133 | 126,812 |
| `PokeN_RoofedGate` | The roofed gate over the path | 4 x 1, open | none: walked through | 80 x 32 x 80 | 80 x 32 x 69 | 14,280 |

Template matching finds the red house twice, alike (over the house, the second copy differs from the first by 6.5 levels in 255 on average; mirrored, by 33). No Nintendo marks are drawn on any of them, and none draws a way up. The gate is a roof on posts across the path, with no walls and no water under it; whether it counts among the buildings was asked (below). (The ground tile `PokeN_Ground_BridgeDeck` in `ground/` was sampled from inside this roof's planks, its source region 405-439 x 651-669.) Not modelled here: the rest of the scene (the steps in the path, fences, a bench, a sign, lamp posts, the lake, the trees), some of it in other folders of `output/poke_n/`.

## Made for the game's grid

As the poke_m buildings: VCOM places only 16-cubed pieces, in a cell's middle, on the edge between two cells or on the corner where four meet, and a building enters a map as its street lamp does, drawn whole and cut into pieces placed together. So:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (eaves, verges, sills, the bay, flower boxes, the gate's roof).
- **Levels are z = 16k.** Level 0 is a house's own floor, a stone foundation standing in for the map's ground blocks (opened in MagicaVoxel a house sits on a one-tile stone plinth; in the game it is buried). The gate has no floor: it stands on the map's own ground, its posts' feet sunk into it. Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice). The red house's door is drawn as a pair of leaves only a tile and a quarter wide, so here it is one door in one slot with both leaves drawn on it (poke_c's manor's, drawn two tiles wide, took two slots).
- **Windows** keep within a tile, or stand over a tile boundary where the art draws them so (each half its own window piece). Their glass is over a solid sill course a level high: a unit vaults in over the sill and has half cover at it from inside. Glass higher up (the houses' upper windows, the chalet's gable windows) is above the levels a unit fills and changes nothing in the fight.
- **No upper floors**: the art draws no way up (the user's rule: floors only where stairs are drawn), so each house is one storey open to its roof, its upper windows lighting it from above.
- **An opening a unit walks through inside a building** (the chalet's, from its wing into its A-frame block) is open in a whole tile at the two levels a unit fills, the roof over it on piers at the corners.
- **Corners** where four tiles meet are decoration to the fight: the corner posts and quoins, the piers and the gate's posts stand there.
- **Every pattern repeats every 16 voxels** on the grid. Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** A tile is 16 across and in depth, and heights are foreshortened to 0.46, as in most of the earlier images: the red house's door is 14 pixels tall for its two levels and the chalet's ground floor 16. Heights fitted to the art, measured row by row and column by column: the red house's walls to z 84 under a roof rising 1.05 a voxel in to z 128 (its verges traced across the front), the chalet's walls to z 48, its A-frame rising 3.2 a voxel in to a flat top at z 120 and its wing's hip 2.5 to z 90, the gate's roof from z 48 on its posts to z 68. [previews/PokeN_*_art.png](previews/) draw each Base model in the art's own projection beside the source crop, at the same scale. The red house was then checked feature by feature against the art's pixels in that projection: its roof's ridge and back edge, its chimney's cap and front, its dormer, its bay and its glass all fall within a pixel or two of where they are drawn.

**Where the grid moves things.** The red house's walls are drawn 76 pixels across (4.75 tiles), from a tile edge of the map, under a roof of 100; here five tiles from that edge under a roof of 96 (the canvas's half tile of margin), which puts its door in one tile (tile 3, within a voxel of its drawn middle) and its windows, bay, chimney and dormer within a voxel or two of where they are drawn. Its roof is drawn about 44 voxels deep, front to back: here the house is two tiles deep, the front verge two out as drawn and the back one seven, two voxels short of the drawn depth (the canvas's margin). The chalet's A-frame block is drawn three and a half tiles across between its corner posts and its wing one and a half; here four and two, on the map's own tiles: the block's left wall and the wing's door are on them, and the art draws the block's right wall and the wing's left wall 7 and 8 voxels inside them (rounding down instead would put them 9 and 8 outside). The gate's posts are drawn four tiles apart, as here, on the corners of the tiles.

## The user's decisions for these buildings

Carried over from the earlier images (2026-10-28): doors closed as drawn, each leaf in one slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by the stairs the art draws. For poke_n (2026-11-03), asked whether the roofed gate counts among the buildings, the user chose **"Model the gate"**: a family like the houses, in all seven treatments, its posts corner pieces, its roof over the path a level over a unit's head, the path open, tested with the rule checks adapted to a structure walked through.

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides) is inferred in the same style and listed here.

- **RedHouse.** Five tiles by two, one storey open to its roof: the ground floor's cream plaster in courses between yellow-brown stone quoins at the corners, a dark beam over it (z 48-55), above it the upper floor's dark timber between two wide windows of two panes over boxes of pink, purple and orange flowers, as drawn. A steep gable roof of red tiles, its ridge front to back, rising 1.05 a voxel in (to z 128), the tiles in rows along the ridge under a light band, the eaves eight voxels out (dark red at their edges) and the verges over grey barge boards, the front one two out and the back one seven (the roof runs further back than the house, as drawn); the front gable cream over a dark timber. A shed dormer on the right slope, its flat roof of the roof's tiles running out over the right wall and its triangular face light grey-green with louvres, as drawn; a chimney at the back of the left slope, as drawn: red-brown brick in courses standing on the roof, through its back over the back wall, under a tall light cap a voxel wider all round, its top a light rim round a darker inside and the dark navy flue, its top over the ridge. The front: a bay window across tiles 1 and 2 under a red awning, cream panels either side of its glass, the glass in level 2 over a solid base and within tile 1, open to the room behind it there; the blue double door in tile 3 (closed), its two leaves with their knobs drawn on the one door, as drawn. *Inferred:* the back and back gable as the front's, a window of the bay's kind in each side and two at the back, the upper windows round the sides and back, the interior (plank floor, open to the roof). The art draws the bay's glass a little lower, partly in what is here its sill course.
- **Chalet.** An L, one storey of two courses: a wing of two tiles by three on the left and an A-frame block of four tiles by two on the right, a tile further forward, both of cream stone in courses between timber posts at the outer corners. The A-frame block's steep gable roof rises 3.2 a voxel in from its side walls to a flat top (z 120) running front to back, as drawn, its eaves three out and verges two; its front gable cream with darker spots over a dark beam (z 48-55), two dark braces rising from the beam's ends, three windows (two side by side, one over them) under a white verge, as drawn; its ground floor's two windows in its middle tiles with dark sills. The wing's steep hipped roof rises 2.5 a voxel in to a ridge along its length (z 90) under a white fascia along its front, as drawn; its front: the door in tile 1 (closed), red-brown boards with a pane in its top, and beside it a lamp, unlit, as the user chose no lights. A tall pale stone chimney stands down the A-frame's right slope near its back, two dark vents near its top, as drawn. Inside, one room: the wing opens into the A-frame block through a tile at the two levels a unit fills, the roof over it on piers. *Inferred:* the back gable (one window), the windows of the A-frame block's side and back and of the wing's side and back, the opening and piers, the interior (plank floor, open to both roofs). The art draws the A-frame's top flat and its roof all the way back to the house's top edge; here that flat top runs the block's whole depth.
- **RoofedGate.** Four tiles by one, open: a dark post at each corner of the tiles, from its foot sunk in the ground up to the roof; tie beams between them at the front, back and ends, from level 3 up, over a unit's head; a gable roof of brown planks over them, its ridge along the gate, rising 1.1 a voxel in from its eaves (z 48, eight out all round) under a dark cap, its back slope the art's dark band along the top, as drawn. *Inferred:* the two posts at the back (the art shows the front two; the roof hides the back), the tie beams. Units walk under it from any side; its posts are corner pieces, decoration to the fight, so they block no step, sight or shot.

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by the three buildings, 75 colours: the art's own (native pixel art, read pixel by pixel), the invented floors, ceilings and buried foundation stone noted as such, glass a little lighter so that what is behind still shows. Each roof is one material in one set of colours on both slopes, as the game lights them itself (the art draws the left slopes darker).
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows and slots unchanged: roof rows twice as deep and plain, bigger plaster and stone blocks, wider quoins, posts and braces, inner frames on the windows, plain flowers, wider planks on the gate.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (greys, lights, woods, reds, blues, flowers, leaves); the mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material.
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* The red house five groups (roof, light, wood, door, glass: its flowers folded into the roof's red, its quoins and its chimney's brick into the wood, its chimney's cap into the light, its blue door kept); the chalet four (roof, light, wood, glass: its door into the roof's orange, its pale chimney into the light); the gate two (its roof's planks, its posts and beams).
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry, the same in both (in the manifest), no two groups of a family on one entry.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`), which VCOM reads as glass (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)): the art's blues a little lighter at `_trans 0.7`. Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, as `SimpleWindow1`'s; the bay's is its front. Glass voxels (Base): the red house 2,769, the chalet 2,246; the gate has none. There are no lights in these buildings, by the user's choice: the chalet's lamp is drawn unlit.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, and no glass in a sill course but a door's slot. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 21 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass, 21 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns); every tile is a floor at its level, under the roof; for the houses, round each one at the two levels a unit fills, every wall, sill and closed door shut and every window open, a line of sight through each window at the eye and none through the walls or doors, a vault in over each sill, nothing else stepped through, and every tile reachable from the street (the chalet's A-frame block through its wing); for the gate, every edge round it open at those levels, sight through it from every side, a step in from the ground on every side; the view cut away at the roof. For the gate the test lays the map's grass under it and checks the walking itself (ten steps in, from every side): poke_n's copy of the test adds both. The red house's seven scenes were run again after its last fit to the art, the others' geometry unchanged since their run; the geometry tested was checked to be the files' (each scene's stamping checksum recomputed from the final sculptor).
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away at the roof, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: ChatGPT's 151 poke_n files from before these buildings (its models, generator, records and previews) are unchanged, and `output/poke_n/`'s README.md and FILES.md only had a section on these buildings added at their end ([preserved-hashes.json](preserved-hashes.json)). The other agent's poke_n files were not touched, nor are they checked here.

**Not tested:** opening the files in MagicaVoxel's own editor; adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it and writes one 16-cubed `.vox` a kind, reusing a kind turned where a piece is one turned. What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces |
| --- | --- | --- | --- | --- |
| RedHouse | 168 | 110 | 33 | 2 |
| Chalet | 196 | 119 | 19 | 2 |
| RoofedGate | 36 | 12 | 0 | 0 |

The three Base buildings come to 241 kinds.

- **Floor** (level 0, the houses): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`. The gate has none: place it on the map's ground.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres`.
- **Door** (each leaf's two pieces): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting through windows.
- **Everything else**: solid, `cutaway`, worn as `SimpleWall1.tres`. The gate's posts and its roof's pieces are of this kind; its posts, on corners, block nothing.
- **Cutaway heights:** 3 for all three (the roof).
- **Costs:** a map's level palette gains the shared Base palette's 75 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_n/buildings/generate.py
$files = (Get-Content output/poke_n/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_n/$_" }
python tools/inspect_vox.py $files --output output/poke_n/buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom, never the game itself:
python output/poke_n/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_n/buildings/compose_previews.py <render folder>
python output/poke_n/buildings/compare_art.py
python output/poke_n/buildings/validate.py
```

`qa/godot/whole_import.gd` is run in the copy as poke_g's notes say. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O, [generate.py](generate.py) the files and manifest. The generator owns only the 21 building files and this folder's manifest.

## Decided

By the user (2026-10-28), for every building: doors closed, as drawn, each in exactly one doorway slot; no lights; TwoColor's minimal-colour rule; upper floors reached only by stairs the art draws. For poke_n (2026-11-03): model the roofed gate, as a family like the houses, walked through.

Made without asking, on the evidence above: heights at 0.46; the game-grid conventions (as poke_m's); the red house five tiles by two from its drawn left wall, two deep with its roof's back verge seven out, its double door one door in one slot (drawn a tile and a quarter wide), its bay across tiles 1 and 2 with its glass in tile 1 raised over the sill course and open to the room, its dormer a shed dormer, its chimney's brick standing on the roof, one storey open to the roof; the chalet read as an L (the wing a tile back, the A-frame block a tile forward), four tiles and two where three and a half and one and a half are drawn, its A-frame's flat top running the block's depth, the wing's hip at 2.5, the opening and piers between them, its lamp unlit; the gate a gable of planks on four posts with tie beams in level 3, standing on the map's ground; the inferred sides, backs and insides listed under Each building; glass clarities and colours; the shared Base palette; each family's TwoColor groups, colours and folds; the crate mapping's material classes, index 253 for glass, and no two groups of a family on one crate entry; the test's two additions for the gate.
