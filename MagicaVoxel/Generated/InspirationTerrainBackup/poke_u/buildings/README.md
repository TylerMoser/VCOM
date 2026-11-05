# poke_u buildings

Created 2026-11-03 (Claude), the way the [poke_r buildings](../../poke_r/buildings/README.md) were made. Every building in [poke_u.jpg](../../../poke_u.jpg): **two families, 14 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_u/`; this folder holds their generator, records, previews and the test that puts them into the game. ChatGPT's poke_u files are untouched, and so are the vegetation, rocks, deadwood, fences, ground tiles, props and bridges another agent added to `output/poke_u/` (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

These are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_u.jpg is a 384 x 384 JPEG of native pixel art: a village on floating islands joined by plank bridges, four houses with red-tiled roofs round a pond, signs and trees. A tile is 16 of its pixels (the copies of its trees and houses stand whole tiles apart, and each house's door fills one map tile), so a voxel is one of its pixels across and in depth. Being a JPEG, its colours and edges carry compression noise; measurements were taken on colour classes rather than single pixels, and the cottage's on the median of its three copies laid over each other, which takes the noise out. Its buildings (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeU_Cottage` | The small house, three copies | 3 x 2 | 1, open to its steep gable roof | 64 x 48 x 128 | 64 x 43 x 115 | 69,645 |
| `PokeU_WingHouse` | The big house at the right | an L of 13: a wing 3 x 3 and a part 2 x 2 beside it | 1, open to its roofs | 96 x 64 x 128 | 93 x 55 x 110 | 116,770 |

Template matching finds the small house three times, alike: laid over each other, the three differ only in what stands round them and in front of them (trees, and a bush over the lowest one's door), never in the house; none is mirrored. The big house is drawn once: a wing a tile ahead of the rest on the right, under its own gable, and a part beside it under a lean-to with the door, which gives it the name used here. No Nintendo marks are drawn on either, neither is cut off by the image's edge, and neither draws a way up; the signs and bridges (in other folders of `output/poke_u/`) are not buildings, so nothing needed asking. Not modelled here: the rest of the scene (the islands and their cliffs, the bridges, the pond, signs, trees, grass, the people and creatures).

## Made for the game's grid

As the poke_r buildings: VCOM places only 16-cubed pieces, in a cell's middle, on the edge between two cells or on the corner where four meet, and a building enters a map as its street lamp does, drawn whole and cut into pieces placed together. So:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (eaves, verges, beams, posts, flower boxes).
- **Levels are z = 16k.** Level 0 is a building's own floor, a stone foundation standing in for the map's ground blocks (opened in MagicaVoxel a building sits on a one-tile stone plinth; in the game it is buried). Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice); both doors here are drawn on a single tile.
- **Windows** keep within a tile, each its own window piece. Their glass is over a solid sill course a level high: a unit vaults in over the sill and has half cover at it from inside. The gables' windows are above the levels a unit fills and change nothing in the fight.
- **No upper floors**: the art draws no way up (the user's rule: floors only where stairs are drawn), so each building is one storey open to its roof, its gables' windows lighting it from above.
- **Corners** where four tiles meet are decoration to the fight: the timber posts stand there.
- **Every pattern repeats every 16 voxels** on the grid. Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** A tile is 16 across and in depth, and heights are foreshortened to **0.4375**: both houses' doors are drawn 14 pixels tall for their two levels. Heights fitted to the art, measured in its projection from the ground line under each door: the cottage's ground floor to z 53 under a beam (z 54-63, two voxels out) on posts three out, its gables over it, its gable roof rising 1.07 a voxel in from its eaves (z 75) to the ridge (z 108); the wing house's wing the same but for its ridge (z 104) and its beam (z 56-64), the part beside it to an eave over its door at z 70 (a beam under it, z 52-58), its lean-to rising to the wing's ridge at the back. Then every feature was checked against the art's pixels in that projection (the table under [How close it is](#how-close-it-is), below), and nearly all fall within a pixel or two of where they are drawn.

**Where the grid moves things.** The cottage is drawn three and a half tiles wide: its corner posts 57 pixels apart, the door half a tile in from the left post, on a map tile exactly, and the two windows on the next two. Here it is three tiles wide, its walls on the door's tile's left edge and the right window's right edge, the half tile left of the door left out; but its corner posts stand where they are drawn, three to six voxels out beyond the walls' corners, the front wall carried out to them under a beam across the front, so its front is as wide as drawn and its ridge exactly over the drawn one. Its eaves reach the canvas's edges, seven voxels out, four and two pixels short of the drawn ones. It is two tiles deep (its roof is drawn 43 deep along the ridge: two tiles and the verges). The wing house's wing is drawn three tiles wide (its gable's apex three pixels left of their middle), its left part two and a half, with its corner post half a tile left of the door's tile as the cottage's: here two, the post where drawn. The wing stands 14 rows ahead of the left part in the art, a tile (16) here; the ground row is taken between the two, so the wing's features sit a row or two low and the left part's a row high.

### How close it is

Measured in the art's projection (rows down the image; x across), model against art:

| Feature | Model | Art |
| --- | --- | --- |
| Cottage: ridge, front apex top, back apex | x 87-88, row 103.3, row 60.3 | x 87, 103.5, 61 |
| Cottage: gable's feet, eaves' ends | rows 120.8, x 56 and 119 | 121-122, x 52 and 121 |
| Cottage: beam, posts, door | rows 121-125.4, 126.4-143, 126-140 | 121-125, 126-143, 126-139 |
| Cottage: windows' glass, flower boxes, gable windows | rows 130.4-133, 136.3-139.4, 112.9-119 | 131-133, 136-139, 113-120 |
| Cottage: chimneys' tops (tall, short) | rows 65.7-75.7, 81.6-88.6 | 66-75, 81.5-88.5 |
| Wing house: wing's apex top, gable's feet, gable window | rows 136.1, 151.8, 144.8-150 | 136.5, 152, 145-150 |
| Wing house: wing's beam, eave and beam over the door, door | rows 151.6-155.5, 133.9-137 and 138.2-141.2, 141-155 | 151-155, 135-137 and 139-141, 142-155 |
| Wing house: chimneys' tops (tall, short) | rows 88.9-98.9, 103.5-111.5 | 89-98, 103.5-111.5 |
| Wing house: the roof's top line, the left end's back corner | rows 81.1, 95.9 | 85, 93 |

The exceptions, each explained under Each building: the wing house's roof top, 4 rows higher than drawn, and its left end's corner, 3 lower; the wing's ground-floor window, 3 pixels left of drawn (kept within its tile); the small window by the wing house's door, whose glass sits 2 rows higher than drawn, as the rules put glass over the sill course. [previews/PokeU_*_art.png](previews/) draw each Base model in the art's own projection beside the source crop, at the same scale.

## The user's decisions for these buildings

Carried over from the earlier images (2026-10-28): doors closed as drawn, each leaf in one slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by the stairs the art draws. poke_u asked for no new call: it draws no Nintendo marks, no building cut off by the image's edge, and no structure but these two buildings.

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides) is inferred in the same style and listed here.

- **Cottage.** Three tiles by two, one storey open to its roof: cream walls; a timber frame at the front, two posts standing out from the corners under a beam across the whole front (its top lit, its underside dark); the front gable over it dark between timbers, a post under the ridge and two braces climbing from beside the windows' feet to the roof, two windows in white frames in it, as drawn; a steep gable roof of red tiles, its ridge front to back over the middle, a dark ridge line, the tiles in courses with dark lines between them and a few lighter, its eaves seven voxels out, its verges' boards dark red, four voxels out in front and five at the back. The ground floor: the red door in tile 0 (closed), brown jambs, lit and shaded strips down its sides, a window in a white frame in its upper half, a recessed panel below and a cream knob at the left, as drawn; two windows of two panes in tiles 1 and 2, white frames over dark sills, each over a dark red flower box two voxels out with cream flowers and grey-green leaves. On the right slope two beige chimney stacks, as drawn: the taller behind (its cap z 111-114), the shorter in front of it and to its left (z 104-105), each with its cap a voxel wider all round, lit on top and shaded at its sides, and a dark flue in its top. *Inferred:* the back (its timber frame and gable as in front, two windows without boxes), a window in each side, the interior (plank floor, open to the roof).
- **WingHouse.** An L of thirteen tiles, one storey open to its roofs. The wing, three tiles by three on the right, its front a tile ahead of the rest: a gable roof of red tiles with its ridge front to back (z 104), eaves four voxels out, its front gable dark over a beam on two corner posts, a window of two panes in a white frame in it with a timber either side, as drawn; on its front two windows with flower boxes, the first as drawn and the second (tile 3) inferred under the tree that hides it, tile 4 plain. The part beside it, two tiles by two: under the eave of a lean-to over its door, a beam on a corner post standing out from its corner, as the cottage's; the red door in tile 0 (closed), the cottage's door, and in tile 1 a small window of one pane with a flower box, as drawn. On the wing's right slope two chimney stacks, the cottage's, as drawn. *The roof over the left part:* the art draws its upper part with the tiles of a slope running front to back, a front band with the courses of a slope facing the front over the door, a lit face at its left end, its top a flat line at the height of the wing's ridge, and no back slope at all; no single shape seen at the art's angle gives all of that. It is read here as a lean-to rising from its eave over the door (z 70) to the wing's ridge at the back (z 104), hipped at its left end, joined to the wing's left slope along a valley: from the art's angle that gives the drawn top line (4 rows high), the left end's diagonal (3 rows low at its corner), the eave over the door, the lit face at the left end and the front-facing courses; the front band's stepped edge is drawn flatter than this hip. Its back, which the art cannot show, is then a tall wall. *Inferred:* the back (the wing's gable dark, a window in its half the lean-to leaves, the rest of the back cream, three windows on the ground floor), windows in each side, the interior.

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by the two buildings, 33 colours: the medians of each material's pixels in the art (the cottage's from its three copies), the invented floors, ceilings and buried foundation stone noted as such, glass a little lighter so that what is behind still shows. Each roof is one material in one set of colours on all its faces, as the game lights them itself: the colour of the art's faces turned neither left nor right (it draws its left slopes lit and its right ones shaded).
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows and slots unchanged: the roofs' courses and tiles twice as big, no lighter tiles, a wider ridge line, the window frames doubled, the flower boxes three voxels deep, the door's strips wider and its lower panel left out, the posts and beams a voxel wider and deeper, the chimneys shaded a voxel further down.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (reds for the roofs, doors and flower boxes, lights for the walls, frames, flowers and chimneys, woods for the timber, the gables' infill and the floors, greys for the foundation and the sills, leaves for the flowers' leaves); 246, a pale yellow-green, is kept out of the lights, as in poke_o. The mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material.
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* Both houses four groups: roof, light, dark and glass, the doors and flower boxes folded into the roof's red and the gables' dark infill into the timber's brown.
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry, the same in both (in the manifest), no two groups of a family on one entry. The light group is put on 195 by hand: its nearest, 194, a mid grey, would take a third of the walls' contrast with the timber's 235 away.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`), which VCOM reads as glass (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)): the art's periwinkle a little lighter, (140, 150, 245) at `_trans 0.7`. Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, as `SimpleWindow1`'s; the doors' panes are in the doors. Glass voxels (Base): the cottage 596, the wing house 828. There are no lights in these buildings, by the user's choice.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, and no glass in a sill course but a door's slot. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 14 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass, 14 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns); every tile is a floor at its level, under the roof; round each building at the two levels a unit fills, every wall, sill and closed door shut and every window open, a line of sight through each window at the eye and none through the walls or doors, a vault in over each sill, nothing else stepped through, and every tile reachable from the street; the view cut away at the roof. The geometry tested was checked to be the files' (each scene's stamping checksum recomputed from the final sculptor).
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away at the roof, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: ChatGPT's 87 poke_u files from before these buildings (its models, generator, records and previews) are unchanged, and `output/poke_u/`'s README.md and FILES.md only had a section on these buildings added at their end ([preserved-hashes.json](preserved-hashes.json)). The other agent's poke_u files were not touched, nor are they checked here.

**Not tested:** opening the files in MagicaVoxel's own editor; adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it and writes one 16-cubed `.vox` a kind, reusing a kind turned where a piece is one turned. What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces |
| --- | --- | --- | --- | --- |
| Cottage | 107 | 69 | 8 | 2 |
| WingHouse | 170 | 105 | 12 | 2 |

The two Base buildings come to 174 kinds.

- **Floor** (level 0): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres`.
- **Door** (each leaf's two pieces): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting through windows.
- **Everything else**: solid, `cutaway`, worn as `SimpleWall1.tres`. The timber posts, on corners, block nothing.
- **Cutaway heights:** 4 for both (over the beams; the walls go on up to the roofs).
- **Costs:** a map's level palette gains the shared Base palette's 33 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_u/buildings/generate.py
$files = (Get-Content output/poke_u/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_u/$_" }
python tools/inspect_vox.py $files --output output/poke_u/buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom, never the game itself:
python output/poke_u/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_u/buildings/compose_previews.py <render folder>
python output/poke_u/buildings/compare_art.py
python output/poke_u/buildings/validate.py
```

`qa/godot/whole_import.gd` is run in the copy as poke_g's notes say. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O, [generate.py](generate.py) the files and manifest. The generator owns only the 14 building files and this folder's manifest.

## Decided

By the user (2026-10-28), for every building: doors closed, as drawn, each in exactly one doorway slot; no lights; TwoColor's minimal-colour rule; upper floors reached only by stairs the art draws. poke_u raised no new question.

Made without asking, on the evidence above: one pixel a voxel and heights at 0.4375, fitted to the doors; the game-grid conventions (as poke_r's); the cottage three tiles by two (the half tile drawn left of its door left out, its corner posts where drawn beyond its walls), its two stacks read as two chimneys; the big house named the wing house and made an L of a wing three by three and a part two by two, its wing a tile ahead where the art draws it 14 rows ahead, the roof over its left part read as a lean-to hipped at its left end, rising to the wing's ridge at the back; the second window of the wing's front, under the tree, and the plain tile beside it; the inferred sides, backs and insides listed under Each building; glass colour and clarity; the shared Base palette, from the colours' medians; the TwoColor groups, colours and folds; the crate mapping's material classes (246 left out of the lights'), the light group on 195 by hand, index 253 for glass, and no two groups of a family on one crate entry.
