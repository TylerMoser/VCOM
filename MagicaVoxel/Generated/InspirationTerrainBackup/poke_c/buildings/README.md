# poke_c buildings

Created 2026-10-28 (Claude, continuing ChatGPT's work here). Every building in [poke_c.png](../../../poke_c.png): **five families, 35 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_c/`; this folder holds their generator, records, previews and the test that puts them into the game. The poke_c trees are untouched (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

Unlike this workspace's earlier buildings, these are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_c.png is 800 x 752 pixels, 16-pixel tiles. Its buildings, each modelled once from its first copy (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- |
| `PokeC_Cottage` | The small slate-roofed house, five copies (two partly hidden by a lamp and a bush) | 4 x 3 | 80 x 64 x 112 | 74 x 54 x 99 | 95,325 |
| `PokeC_FlowerBoxCottage` | The same house with flower boxes under its front windows, three copies | 4 x 3 | 80 x 64 x 112 | 74 x 56 x 99 | 96,013 |
| `PokeC_Manor` | The large house, top right | L of 6 x 4, a 2 x 3 wing and a 1 x 2 bay | 160 x 80 x 128 | 152 x 77 x 125 | 238,173 |
| `PokeC_BridgePavilion` | One of the covered bridge's two identical pavilions (eight tiles apart) | 5 x 2 | 96 x 48 x 208 | 90 x 38 x 196 | 124,724 |
| `PokeC_BridgeSpan` | The arched stone span between them | 3 x 2 | 64 x 48 x 80 | 48 x 38 x 76 | 76,544 |

The two cottages are pixel-identical in the art but for the flower boxes (checked by template matching), so they share all their geometry. The covered bridge is 17 tiles long, past MagicaVoxel's 256 voxels a side, so it is two models, as the user chose: the pavilion on its own section of deck, placed twice, and the span between. Assembled (pavilion, span, pavilion) they make the bridge between the two pavilions' outer posts; the art's end walkways, about two tiles each onto the banks, are not modelled (the banks' paving would carry the walkway). Not buildings, and not modelled: the street lamps, post boxes, signs, fences, stairs and the plain stone bridge downstream.

## Made for the game's grid

VCOM places only 16-cubed pieces, in the middle of a cell, on the edge between two cells, or on the corner where four meet ([Docs/LEVELS.md](../../../../VoxelXCOM/Docs/LEVELS.md)); a building enters a map the way its street lamp does, drawn whole and cut into pieces placed together. So every model here keeps to the grid:

- **16 voxels a tile.** Tile boundaries run at x = 8 + 16i and y = 8 + 16j: each canvas is the footprint plus half a tile all round, which holds the outer halves of the edge pieces (eaves, frames, sills, the manor's hood). The importer's centring puts the footprint on the grid: an even width centres on a tile boundary, an odd one on a tile's middle.
- **Levels are z = 16k.** Level 0 (z 0-15) is the building's own floor, a stone foundation with boards on top: in a map it stands in for the ground blocks under the building. The floor surface, where units stand, is z = 16. Opened in MagicaVoxel, a house therefore sits on a one-tile stone plinth; in the game it is buried. The bridge pieces stand on z 0, the river's bed, their walkway on z 64.
- **Walls are three courses** (levels 1-3), as the game's TestMap house: a window's glass in the middle course, at a unit's eye, over a solid sill course (half cover), under a lintel course. A wall is two voxels thick across its boundary, as `SimpleWall1` is.
- **Doors are closed, as drawn,** and each leaf fills exactly one doorway slot: one tile wide, levels 1 and 2 (the user's choice). The manor's double door is two leaves in two slots.
- **Windows keep within their tile**, or span two whole tiles as two pieces side by side (the manor's tall windows). No glass stands in a sill course anywhere but a door's slot; the manor's tall windows reach down the wall, as drawn, over a solid light panel in the sill course.
- **Every pattern repeats every 16 voxels** on the grid (slates three to a tile, as the art's 16-pixel roof tiles; boards, paving and masonry likewise), so the same part of a wall or roof in two tiles is the same piece.
- Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** The art draws one tile as 16 pixels across and in depth but foreshortens heights: its cottage wall, which must be three courses (48 voxels) for a soldier two cells tall to fit through its door, is 22 pixels tall, about 0.46 of a voxel each. Footprints therefore follow the art's tiles (walls rounded to whole tiles), and heights follow the game: storeys, doors and gables at game height, roof pitches chosen so the model, drawn back in the art's projection, matches the sprite (45 degrees for the cottages and the manor's main roof, two up for one across for the pavilions, three for the manor's wing). [previews/PokeC_*_art.png](previews/) draw each Base model in the art's own projection beside the source crop, at the same scale.

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides) is inferred in the same style and listed here.

- **Cottage, FlowerBoxCottage.** Steep slate roof (rectangular slates, a sprinkle of lighter and darker ones) with its ridge front to back, the dark-infilled front gable with a king post, two braces and two small windows, a tan eave beam, a boarded door bay on the left (the door in tile 0, its little window, the brass knob on its left), a timber post, then plaster with two two-pane windows in a light grey surround, dark corner posts, and two tan chimneys on the right slope toward the back. Flower boxes: dark-rimmed planters under the two front windows, leaves and yellow, orange and blue flowers. *Inferred:* the back gable as the front; a window of the same kind in each side wall and two in the back, so every side can be vaulted through; the interior (one room, open to the roof, board floor).
- **Manor.** Main block six tiles by four: fish-scale slate roof, ridge along the front (both slopes as drawn, the back one seen above the ridge), a barrel dormer over the double door, the door's dark arched hood with its light rim, two tall 2 x 2 windows in cream surrounds, timber posts on the bay boundaries. Wing on the left, two tiles wide and set back a tile (the art's is set back about half a tile; the grid allows a whole one): half-timbered with narrow, wide and narrow plaster panels, a steep gable with the tall three-pane window, a tall blue-grey stone chimney at its back on the left slope. A bay on the right end with windows on its three faces, its outer corners cut on the diagonal (the art's is rounded), under a scalloped hip roof. *Inferred:* the back (two tall windows), a window in each end wall, a small window high in the right gable over the bay's roof, the wing's back, an open doorway from the wing into the hall, the bay open to the hall, the interior.
- **BridgePavilion.** A steep two-up-for-one-across slate roof, its ridge front to back over the walkway; sage-green boarded gables with a red-brown tie beam and two struts; white stone-like plaster walls with short grey dashes along the walkway's front and back, red-brown top plates and corner posts running down to the river's bed; a boarded base under the deck (vertical planks) and the deck's red-brown edge beams. The walkway's ends are open: units walk through it along the bridge. *Inferred:* the back as the front; the base boarded on all four sides; the deck's paving inside.
- **BridgeSpan.** Dark stone masonry in courses with a low arch, as drawn (lighter voussoirs round it), cream paving on the deck between two solid red-brown timber rails a level high, a darker post on each tile boundary. Its arch is the river's way through, not the units': under its crown there is no room to stand.

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by all five buildings, 73 colours sampled from the art (the invented floor boards and buried foundation stone noted as such), at fixed indices: a map using several of the buildings adds the colours once.
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows and slots unchanged: bigger slates (two rows of two to a tile) and scales (one to a tile), thicker roofs, deeper eaves and a rounded ridge roll, chunkier posts, two-voxel window frames, simpler half-timbering, fewer and broader colour regions, the door hood's rim and brass made symmetric. The cottage's two chimneys, the manor's wing and bay, and the doors keep their places: these buildings are not symmetrical, as the specification says of houses. The Cartoon span has a round arch with its ring standing proud and chunky posts above its rails.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (greys, woods, lights, sage, leaves, flowers); the mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material; the palette's bytes are unchanged, only a MATL chunk differs. The crate palette's nearest greys are blue-greys, so slate roofs turn teal-grey with teal flecks, and its browns are reddish.
- **TwoColor**, by the user's decision for these buildings (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* So each file has one flat colour for each group of similar materials, glass apart: **slate** (roofs, dark masonry, the manor's stone chimney, the cottages' dark gable infill, which is nearer the slates than the wood and leaves the timbers showing on it, flues, the buried foundation), **wood** (every timber, door, board, beam, rail and planter), **light** (plaster, frames, paving, the cottages' tan chimneys, brass), **sage** (the pavilions' gables, like no other colour, so kept), **leaf** and **flower** (the flower boxes), and **glass**. That is 3 to 6 colours: cottage 4, flower-box cottage 6, manor 4, pavilion 4, span 3, glass included. The suffix keeps its name for continuity.
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry (slate 182, wood 234, light 195, glass 253, leaf 243, flower 229, sage 193), the same in both.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`, `_trans 0.7`, as the game's own `make_windows.py` writes it), which VCOM reads as glass: see-through, tinted by its colour, shattering (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)). The cottages' panes are the art's periwinkle (150, 152, 236) and the manor's its sky blue (130, 178, 222), each lightened a little from the art so the room behind shows. Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, with a sill proud of both faces, as `SimpleWindow1`'s. Glass voxels: cottages 952 (Cartoon 736), manor 3,282 (2,538); the bridge has none, as drawn. There are no lights in these buildings, by the user's choice: street lamps stand beside them.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: every room hollow at levels 1 and 2 away from its walls, no glass in a sill course but a door's. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 35 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass (the bridge assembled between raised banks), 42 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns included); every tile of every house is a floor under its roof; round the outside every wall and closed door is shut at levels 1 and 2; every eye-level window is open over a shut sill, with a line of sight through it and none through the walls beside it, and a vault in through it; nothing else can be stepped through; every room is reachable from outside; the roofs cut away from level 4 (the pavilion's from 7); the bridge's walkway is a floor end to end, shut along both sides, under the pavilions' roofs, and crossable bank to bank.
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family and the assembled bridge), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: the 238 files in `output/poke_c/` from before (the 56 tree models, their generator, records and previews) are unchanged, but for a Buildings section added to its README.md and FILES.md ([preserved-hashes.json](preserved-hashes.json)).

**Not tested:** opening the files in MagicaVoxel's own editor (they are written as this workspace's earlier files are, version 200 with a rooted scene graph, a layer, a palette and a material for each used colour, as the VOX specification allows; the game's importer reads them); adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it (a cell's middle for floors, roofs and chimneys; an edge for walls, gables, doors, windows, beams and rails; a corner for posts) and writes one 16-cubed `.vox` a kind, reusing a kind turned a quarter, a half or three quarters where a piece is one turned (the game's turn: `(x, z)` to `(z, 15 - x)`). Then each kind goes into `Pieces.tres` and the building into a brush (its pieces, slot offsets and turns from the layout the cutter writes). What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces |
| --- | --- | --- | --- | --- |
| Cottage | 138 | 64 | 10 | 2 |
| FlowerBoxCottage | 138 | 67 | 10 | 2 |
| Manor | 326 | 179 | 38 | 4 |
| BridgePavilion | 204 | 72 | 0 | 0 |
| BridgeSpan | 28 | 18 | 0 | 0 |

- **Floor** (a house's level 0): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres` (the wall's).
- **Door** (each leaf's two pieces, levels 1 and 2): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting through windows, as in TestMap's house. A door kind of its own lets one be made passable later.
- **Everything else**: solid, `cutaway` (walls, gables, roofs, chimneys, posts, the bridge's pieces), worn as `SimpleWall1.tres`.
- **Cutaway heights:** 4 for the houses (the roofs and gables), 7 for a pavilion.
- **Costs:** a cut building is many kinds (all five Base buildings about 400), mostly the facades' unique tiles; a map's level palette gains the shared Base palette's 73 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_c/buildings/generate.py
$files = (Get-Content output/poke_c/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_c/$_" }
python tools/inspect_vox.py $files --output output/poke_c/buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom (49 MB), never the game itself:
python output/poke_c/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_c/buildings/compose_previews.py <render folder>
python output/poke_c/buildings/compare_art.py
python output/poke_c/buildings/validate.py
```

`integration.py` copies `qa/godot/building_probe.gd` into the copy, cuts and imports the pieces there, and runs it; `qa/godot/whole_import.gd` is run the same way (`--script res://_probe/whole_import.gd -- <manifest.json> <output/poke_c> <out.json>`) and its result copied to `qa/whole-import.json`, as the integration report is to `qa/integration-report.json`. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O, [generate.py](generate.py) the files and manifest. The generator owns only the 35 building files and this folder's manifest; the trees' generator and manifest are separate.

## Decided

By the user (2026-10-28): doors closed, as drawn, each in exactly one doorway slot; no lights in the buildings; TwoColor's new rule (above); the bridge as a pavilion and a span.

Made without asking, on the evidence above: the game-grid conventions (three-course storeys as TestMap's house, a foundation as level 0, half a tile of margin, 16-voxel periodic patterns); footprints rounded from the art's tiles; roof pitches fitted to the art's projection; the inferred sides, backs and insides listed under Each building; the wing set back a whole tile where the art has about half, and the bay's corners cut on the diagonal where the art's are curved; the tall manor windows' solid lower panel; glass Transparency 0.7 and its two colours; the shared Base palette; the TwoColor groups and their colours; the crate mapping's material classes and index 253 for glass.
