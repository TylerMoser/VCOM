# poke_b game-ready buildings

Created 2026-10-28 (Claude), redoing ChatGPT's poke_b buildings the way the poke_c buildings were made. Every building in [poke_b.png](../../../poke_b.png): **six families, 42 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_b/`, named `PokeB_Game...` so that they stand beside ChatGPT's `PokeB_DomeLab` and the rest, which are kept as they were (the user's choice); this folder holds their generator, records, previews and the test that puts them into the game. Nothing else in `output/poke_b/` was changed (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

Like the poke_c buildings, and unlike ChatGPT's (one image pixel to a voxel, doors too small for a soldier, walls off the tile edges, opaque glazing), these are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_b.png is 656 x 960 pixels, 16-pixel tiles. Its six buildings (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeB_GameDomeLab` | The large building, top left | 7 x 4 | 2, of three courses | 128 x 80 x 192 | 120 x 72 x 177 | 361,108 |
| `PokeB_GameRedClinic` | The red-roofed building, top middle | 6 x 4 | 1, of four courses | 112 x 80 x 112 | 102 x 75 x 92 | 218,969 |
| `PokeB_GameGrayEntryHouse` | The middle house, with its door and stair | 5 x 3, a stair tile in front | raised ground floor, mansard storey | 96 x 80 x 128 | 88 x 76 x 128 | 237,750 |
| `PokeB_GameGrayWindowHouse` | The house to its right, three windows across | 5 x 3 | raised ground floor, mansard storey | 96 x 64 x 128 | 88 x 56 x 128 | 222,670 |
| `PokeB_GameCyanEntryHouse` | The house at the bottom left | 5 x 3, a stair tile in front | as the middle house | 96 x 80 x 128 | 88 x 76 x 128 | 237,750 |
| `PokeB_GameFlowerCottage` | The cottage, bottom right, with its outside stair | 5 x 3, a stair column of 3 on its right | 2, of two courses | 112 x 64 x 128 | 102 x 60 x 121 | 196,583 |

The three mansard houses are one design. The cyan house is the middle house recoloured in the art (its roof teal, its boards brown, its door orange: checked pixel by pixel), so it shares all its geometry; the house with three windows has the same mansard storey over a different ground floor, its front without a door, as drawn. Not buildings, and not modelled: the street lamp, post boxes, mailboxes, signs and fences.

## Made for the game's grid

As the poke_c buildings ([their README](../../poke_c/buildings/README.md)): VCOM places only 16-cubed pieces, in a cell's middle, on the edge between two cells or on the corner where four meet, and a building enters a map as its street lamp does, drawn whole and cut into pieces placed together. So:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (the outer halves of the edge pieces: cornices, canopies, sills, bays, stair cheeks).
- **Levels are z = 16k.** Level 0 is the building's own floor, a stone foundation standing in for the map's ground blocks (opened in MagicaVoxel a building sits on a one-tile stone plinth; in the game it is buried). Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice).
- **Windows** keep within a tile or span two whole tiles. Their glass is where the rules want it: over a solid sill course a level high (a unit vaults in over the sill and has half cover at it from inside), or, where the user chose climbing in (below), from the floor up through both levels a unit fills.
- **Upper floors are real**: a slab a level thick to the rules (four or eight voxels to the eye), a room over it.
- **Every pattern repeats every 16 voxels** on the grid (boards three to a tile as the art's six-pixel boards, stone courses jointed every eight, roof tiles and shingles likewise), so the same part of a wall in two tiles is the same piece.
- Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** As poke_c.png, the art draws a tile as 16 pixels across and in depth and foreshortens heights to about 0.46 of a voxel a pixel. Footprints follow the art's tiles (walls rounded to whole tiles: the art draws walls a few pixels in from the tile edge), heights the game: storeys at game height chosen so the model, drawn back in the art's projection, matches the sprite. The lab's facade (56 pixels) fits two three-course storeys; the mansard houses' (a 31-pixel ground floor and cornice) a raised floor, a two-course storey and a cornice band; the cottage's (34 pixels to the eaves) two two-course storeys. [previews/PokeB_Game*_art.png](previews/) draw each Base model in the art's own projection beside the source crop.

## The user's decisions for these buildings

Asked before building (2026-10-28), on top of poke_c's (doors closed as drawn; no lights; TwoColor's minimal-colour rule):

- **Raised floors, climbed into at windows.** The mansard houses stand on a stone base a level high, as drawn. Their front stairs climb a level a tile, as the game climbs, and their ground-floor windows reach down to the base (they are tall in the art), so soldiers climb in through them from the street, a level up. There is no cover at them from inside.
- **Floors, stairs only where drawn.** Upper storeys have floors and rooms, reached only where the art shows a way up: the cottage's outside stair. The lab's and the mansard houses' upper rooms are closed off (the test checks that nothing reaches them).
- **Generic marks on the clinic.** Its roundel keeps the shape and colours (red above, white below, a grey rim) but not the Poke Ball's band and button; its sign is a white panel with red blocks, no letters.
- **Keep both.** ChatGPT's 42 poke_b building files and their folder are left as they were; these take new names beside them.

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides) is inferred in the same style and listed here.

- **DomeLab.** Seven tiles by four, two storeys of three courses (ground levels 1-3, the upper floor's slab level 4, upper levels 5-7) under a flat red roof (level 8) in stripes, inside a parapet with a stepped pediment over the middle bay. A dome on the roof, 59 voxels across and a little taller than round, as the art draws it large: a red ring at its foot, a glazed band of glass and white mullions, a cream cap. The front: fluted cream corner pilasters wrapping both faces, thin pilasters either side of the middle bay, two-pane windows in brown and white frames (both storeys in tiles 1 and 5, the upper storey in tile 3), small square panels in the band between the storeys, a dentil cornice; in the middle bay the glass double door (closed) under a glazed transom, and over it the sign, a white panel in a black frame with a blue leaf-like emblem (an interpretation of the art's). Tile floors. *Inferred:* the back (windows in tiles 1, 3 and 5 on both storeys, the thin pilasters), two windows in each side on each storey, the interior.
- **RedClinic.** Six tiles by four, one tall storey of four courses (levels 1-4), a white parapet (level 5) round a low red-tiled roof, a skylight on its right as drawn (a raised light frame, glass, the roof open under it so the room shows), dark corner pillars wrapping both faces. The front, as drawn: a red portico over tiles 1-3 (canopy, cheeks, a red step) sheltering a small window, the sliding glass doors (closed) and the sign; the roundel standing on the canopy over the door; a grey tank; and the dark teal window over tiles 4 and 5, a solid panel under its glass (the sill course) with a brass plate. Tile floors. *Inferred:* two windows in each side and two at the back, the interior. The art's door stands half a tile off the grid of its walls; it moved to tile 2, and the portico, roundel and sign with it.
- **GrayEntryHouse.** Five tiles by three on a stone base a level high (its face in bands of blue-grey stone, a light ledge on top), the ground floor raised to level 2: a storey of tan boards (levels 2-3) with light pilasters at the corners; a stone cornice (level 4, the mansard storey's slab behind it); the mansard storey (levels 5-6), steep slate slopes leaning in five voxels, two dormers front and back (grey cheeks, a white face, two narrow windows in blue frames, glass in level 6 over a sill panel, a light flat top); a low hipped top (level 7) inside a light coping, its courses darker toward the edge as drawn, and a chimney toward the back on the left. The front: a narrow window with a louvred shutter (tile 1), the blue-grey door (tiles 2, levels 2-3, closed) up a stair of light treads between cheeks, a shallow bay over tiles 3-4 standing six voxels out (the art's eight would pass the edge slot's half tile: its cornice must stay within it) with a window over the boundary between its tiles and a shutter either side, and the house-number plate on the bay's side by the door (drawn on the front just right of the door, where the bay is). The art's door stands half a tile off the grid the dormers and bay keep to; it moved to tile 2, by the bay, as the art has the stair beside it. *Inferred:* a window in each side and two at the back, the dormers at the back, the interior (plank floors; the mansard storey closed off).
- **GrayWindowHouse.** The same house without the door and bay: three windows across the front (tiles 1-3) and louvred shutters at the ends, as drawn, its boards brown. *Inferred:* a window in each side and three at the back, as the front. It has no door at all, as its front is drawn; it is entered by its windows.
- **CyanEntryHouse.** The GrayEntryHouse's geometry with the art's cyan house's colours: a teal mansard and top, brown boards, an orange door.
- **FlowerCottage.** Five tiles by three, two storeys of two courses (ground levels 1-2, the slab level 3, upper levels 4-5), cream walls with a red-brown plinth and a floor band, dark corner posts. A bell-cast roof (flat at the eaves and the ridge, steepest between, as the art's arched gable draws it) with its ridge front to back, two roof lights of dark glass in raised grey frames on its left slope, as drawn, and a small window high in the front gable. The front, as drawn: the teal door with a glazed sidelight under a shingled hood (tile 1), a box bay window under a hood (tile 3), two-pane windows upstairs over brown flower boxes full of leaves and orange, pink and yellow flowers. On the right, the outside stair over three tiles: light treads a level a tile to a grey landing at the upper door, a red-brown stringer on its open side. The upper door is closed (the user's rule), so the upper floor would be shut off: beside the stair a tall window reaches down to the upper floor, which a soldier climbs in by from the stair (inferred: the art cannot show that wall). *Inferred:* the left side (behind trees in the art) and the back, with windows on both storeys and a gable window at the back; the right wall's upper door and window; the interior.

**Stairs.** A stair climbs a level a tile, as the game climbs: each tile's block stands a level higher than the last. Its treads are one even flight (four voxels up for four along; eight in Cartoon) cut so that each tile's middle, where a unit stands, is exactly at the tile's top; the treads rising above a tile toward the next lie in the edge slot between the two, and the last tile's back half is a flat landing. The stairs' pieces are not cut away with the building (the floor selector shows a stair as it does the ground).

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by all six buildings, 136 colours sampled from the art (the invented floors, ceilings and buried foundation stone noted as such), at fixed indices: a map using several of the buildings adds the colours once.
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows, stairs and slots unchanged: broader boards, slates, tiles and shingles, two-voxel window frames, chunkier pilasters, pillars, cornices and parapets, a plain cornice on the lab and a ball finial on its dome, a rounded canopy and a bigger roundel on the clinic, crowned dormers on the mansard houses, a taller bell roof and plainer flower boxes on the cottage, stairs in steps of eight. The buildings keep their asymmetric fronts, as the specification says of houses.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (greys, lights, woods, reds, teals, blue-greys, leaves, flowers); the mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material. The palette has no salmon, so the lab's roof turns orange (222); its nearest stone greys are blue-greys.
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* Groups of similar materials, each family giving its groups its own most telling colour from the art: the lab 4 (light, red, dark, glass), the clinic 4 (light, red, dark, glass), the mansard houses 5 (light, stone, grey slate, wood, glass; the cyan house's slate is its teal), the cottage 7 (light, red, dark, teal for its doors, leaf, flower, glass), glass included. Where a group would be like another in a family it is folded into it (the lab's and clinic's few woods into their dark, the mansard houses' dark lines into their stone).
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry, the same in both (in the manifest), no two groups of a family on one entry: the nearest, except that the mansard houses' stone takes the crate palette's dark blue-grey (206) and their slate its palest grey (193), since the nearest would be its three near-identical pale greys and lose the art's dark stone under mid slate under a light coping.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`, `_trans` its clarity, as the game's own `make_windows.py` writes it), which VCOM reads as glass (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)). Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, as `SimpleWindow1`'s; the dome's glazed band is a shell a voxel and a half thick between its mullions. Colours lightened a little from the art's so the room behind shows, clarity 0.7; the clinic's teal window (0.5) and the cottage's roof lights (0.45) are darker glass, as drawn. Glass voxels (Base): lab 7,184, clinic 1,947, mansard houses 1,368 (three windows: 1,896), cottage 2,117. There are no lights in these buildings, by the user's choice.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, and no glass in a sill course but a door's slot or the window climbed into from the cottage's stair. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 42 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass, 42 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns); every tile of every storey is a floor at its level, under the roof; round each storey, at the two levels a unit fills, every wall, sill and closed door is shut and every window open; a line of sight through each window at the eye and none through the walls or doors; a vault in over each sill (lab, clinic, cottage), a climb in from the street through each of the mansard houses' tall windows, and a climb in from the cottage's stair to its upper floor; nothing else can be stepped through, from the street or a stair; the stairs are tiles a level apart; every storey with a way in drawn is reachable from the street, and the lab's and mansard houses' upper storeys are not (closed off, the user's choice); the view cuts away at each storey.
- The game test ran all 42 scenes, then the 18 that three last refinements touched (the game camera's framing, the cottage's soldier moved onto its stair, the mansard houses' crate mixtures) again; the report holds each scene's latest run.
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away at each storey, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: the 642 files in `output/poke_b/` from before (ChatGPT's 42 buildings and their folder, the 112 trees, the lantern, their generators, records and previews) are unchanged, but for a section on these buildings added to its README.md and FILES.md ([preserved-hashes.json](preserved-hashes.json)).

**Not tested:** opening the files in MagicaVoxel's own editor (they are written as the poke_c buildings are, version 200 with a rooted scene graph, a layer, a palette and a material for each used colour); adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it (a cell's middle for floors, slabs, roofs and stairs; an edge for walls, cornices, doors, windows, dormers, bays, cheeks and the stringer; a corner where four tiles meet) and writes one 16-cubed `.vox` a kind, reusing a kind turned where a piece is one turned (the game's turn: `(x, z)` to `(z, 15 - x)`). A roof's eaves go to the edge of the roof they hang from (over the cottage's stair, the house's side wall), so a stair keeps its headroom. Then each kind goes into `Pieces.tres` and the building into a brush (its pieces, slot offsets and turns from the layout the cutter writes). What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces | Stair kinds (not cut away) |
| --- | --- | --- | --- | --- | --- |
| DomeLab | 355 | 129 | 39 | 2 | 0 |
| RedClinic | 192 | 64 | 11 | 2 | 0 |
| GrayEntryHouse | 211 | 130 | 18 | 2 | 11 |
| GrayWindowHouse | 200 | 105 | 20 | 0 | 0 |
| CyanEntryHouse | 211 | 130 | 18 | 2 | 11 |
| FlowerCottage | 221 | 105 | 13 | 4 | 14 |

All six Base buildings come to 663 kinds.

- **Floor** (level 0): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres`.
- **Door** (each leaf's two pieces): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting or climbing through windows. A door kind of its own lets one be made passable later.
- **Stair** (its middles, its tread edges, cheeks and stringer): solid, not `cutaway`.
- **Everything else**: solid, `cutaway`, worn as `SimpleWall1.tres`.
- **Cutaway heights:** the lab 4 and 8, the clinic 5, the mansard houses 4 and 7, the cottage 3 and 6 (each storey's ceiling).
- **Costs:** a map's level palette gains the shared Base palette's 136 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_b/game_buildings/generate.py
$files = (Get-Content output/poke_b/game_buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_b/$_" }
python tools/inspect_vox.py $files --output output/poke_b/game_buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom, never the game itself:
python output/poke_b/game_buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_b/game_buildings/compose_previews.py <render folder>
python output/poke_b/game_buildings/compare_art.py
python output/poke_b/game_buildings/validate.py
```

`integration.py` copies `qa/godot/building_probe.gd` into the copy, cuts and imports the pieces there, and runs it; `qa/godot/whole_import.gd` is run the same way (`--script res://_probe/whole_import.gd -- <manifest.json> <output/poke_b> <out.json>`) and its result copied to `qa/whole-import.json`, as the integration report is to `qa/integration-report.json`. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O (a copy of poke_c's), [generate.py](generate.py) the files and manifest. The generator owns only the 42 `PokeB_Game` files and this folder's manifest; ChatGPT's building generator (`../buildings/`), the trees' and the lantern's are separate.

## Decided

By the user (2026-10-28): doors closed, as drawn, each in exactly one doorway slot; no lights in the buildings; TwoColor's minimal-colour rule; the mansard houses' floors raised as drawn and climbed into at their tall windows; upper floors reached only by stairs the art draws; generic marks on the clinic; ChatGPT's files kept and these named beside them.

Made without asking, on the evidence above: the game-grid conventions (as poke_c's, with storeys of three courses for the lab, four for the clinic and two for the mansard houses and the cottage, fitted to the art's heights); footprints rounded from the art's tiles; the doors of the clinic and the two entry houses moved half a tile onto their walls' grid (and the clinic's portico, roundel and sign with its door; the entry houses' house-number plate to the bay's side); the entry houses' bay six voxels deep where the art's is eight; the lab's dome a little bigger and taller than round, and its emblem an interpretation; the cottage's stair window, so its upper floor can be entered with the door closed; the inferred sides, backs and insides listed under Each building; the stairs' tread cut; glass clarities and colours; the shared Base palette; each family's TwoColor groups, colours and folds; the crate mapping's material classes, index 253 for glass, no two groups of a family on one crate entry, and the mansard houses' stone and slate entries picked for contrast.
