# poke_m buildings

Created 2026-10-29 (Claude), the way the [poke_j buildings](../../poke_j/buildings/README.md) were made. Every building in [poke_m.png](../../../poke_m.png): **two families, 14 complete VOX files**, each family in Base and all six established treatments. The files are directly in `output/poke_m/`; this folder holds their generator, records, previews and the test that puts them into the game. ChatGPT's poke_m files are untouched, and so are the vegetation, rocks, lights and deadwood another agent was adding to `output/poke_m/` at the same time (see Validation).

[Overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json) | [Validation](validation-summary.json)

These are **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale, with real glass, so each can be cut into the game's 16-cubed level pieces and play by the game's rules. That was tested in a copy of the game (below).

## The buildings in the art

poke_m.png is 800 x 880 pixels of native pixel art: a marsh route through a forest between cliffs, a log cabin by the marsh, and at the bottom left the edge of a village. A tile is 16 of its pixels (its stairs are three tiles across, its bridge deck five by three), so a voxel is one of its pixels across and in depth, as in poke_c to poke_h. Its buildings (regions in [reference/regions.json](reference/regions.json)):

| Family | In the art | Footprint (tiles) | Storeys | Canvas XYZ | Occupied XYZ (Base) | Voxels (Base) |
| --- | --- | --- | --- | --- | --- | --- |
| `PokeM_LogCabin` | The log cabin by the marsh | 4 x 2 | 1, of four logs, open to the roof | 80 x 48 x 96 | 72 x 42 x 78 | 63,774 |
| `PokeM_Lodge` | The lodge, two copies, each cut off by the image's edge | 4 x 2 | 1, of three courses, open to its roofs | 80 x 48 x 112 | 80 x 40 x 110 | 90,960 |

**Two of the three are cut off by the image's edges.** The cabin is drawn whole. The lodge at the bottom left shows its front but for its left end, which lies past the image's left edge; the structure at the very bottom shows only its roof, its walls below the image's bottom edge. Asked what to model, the user chose all three (below). The two cut-off ones turned out to be **one building**: their roofs are pixel for pixel the same wherever both show, eight tiles apart across and six down, so one model covers both, and together they show it all but the front's left end. The bottom copy gives the roof's whole width, the first copy the front; the front's left end is completed as its right end is drawn. No Nintendo marks are drawn on either, and neither draws a way up. Not buildings, and not modelled: the stairs, the bridge deck, the fences, the signpost, the lamp post (another agent's lights), the trainers and Pokémon.

## Made for the game's grid

As the poke_j buildings: VCOM places only 16-cubed pieces, in a cell's middle, on the edge between two cells or on the corner where four meet, and a building enters a map as its street lamp does, drawn whole and cut into pieces placed together. So:

- **16 voxels a tile**, boundaries at x = 8 + 16i and y = 8 + 16j, half a tile of margin all round (eaves, verges, log ends, the porch, sills).
- **Levels are z = 16k.** Level 0 is the building's own floor, a stone foundation standing in for the map's ground blocks (opened in MagicaVoxel a building sits on a one-tile stone plinth; in the game it is buried). Units stand on the top of a cell.
- **Walls are two voxels thick** across their boundary at the levels a unit fills. What stands higher, over the storey (the lodge's upper part), is drawn where the art draws it. **Doors are closed, as drawn**, each leaf exactly one doorway slot, one tile wide and the two levels a unit fills (the user's choice).
- **Windows** keep within a tile, or stand over a tile boundary where the art draws them so (each half its own window piece). Their glass is over a solid sill course a level high: a unit vaults in over the sill and has half cover at it from inside.
- **No upper floors**: the art draws no way up (the user's rule: floors only where stairs are drawn), so each building is one storey open to its roof; the lodge's upper part is open to the room under it.
- **Corners** where four tiles meet are decoration to the fight: the cabin's log ends and the lodge's corner posts stand there.
- **Every pattern repeats every 16 voxels** on the grid. Front is local **-Y** (Godot +Z), Z up, grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a Mesh at Scale **0.0625**. Palette index 255 (the game's blood) is never used.

**Scale.** A tile is 16 across and in depth. Heights here are foreshortened to **0.5**, a little less than the 0.46 of the earlier images: the doors are 15 and 16 pixels tall for the two levels a door fills, and at 0.5 the lodge's window, porch beam, fascias and roofs fall where the art draws them, measured row by row. The cabin's walls are four logs (z 16-47, as its four log ends a corner show), its roof rising to z 75 and its ridge cap to z 77; the lodge's walls three courses (to z 64), its lower roof rising to z 82 and its upper roof to z 107 under a ridge board to z 109. [previews/PokeM_*_art.png](previews/) draw each Base model in the art's own projection beside the source crop, at the same scale.

**Where the grid moves things.** The art draws the cabin's walls a few pixels inside the four tiles its roof covers; here the walls are those four tiles, so its door and window keep their drawn tiles, and the roof overhangs them three voxels. The lodge's door is drawn over a boundary of the map's tiles; here the lodge's tiles lie half a tile off the map's, so that its door fills a tile and its walls stand within three voxels of where they are drawn.

## The user's decisions for these buildings

Carried over from the earlier images (2026-10-28): doors closed as drawn, each leaf in one slot; no lights in the buildings; TwoColor's minimal-colour rule; upper floors reached only by the stairs the art draws. For poke_m (2026-10-29), asked what to do with the two buildings the image cuts off, the user chose **"All three"**: the cabin, the lodge completed, and the structure at the bottom, its walls and front invented from its roof and the lodge's style. As that structure is a second copy of the lodge, the lodge's model is both.

## Each building

What the art shows is followed; what it cannot show (sides, backs, insides, the lodge's left end) is inferred in the same style and listed here.

- **LogCabin.** Four tiles by two, one storey of four logs, each eight voxels tall, a dark seam under it and a light rounded top, as drawn. The side walls' logs run out four voxels past the front and back walls in round ends, dark bark round a light heart, four a corner, as drawn. A steep gable roof of grey slates, its ridge front to back, rising 0.8 a voxel in (to z 75), the slates in rows of the art's four greys under a raised ridge cap eight voxels wide, dark verges, the eaves three out. The front gable over a light beam (a log a voxel proud, z 48-55): dark boards with light battens, a king post up the middle and rafters under the verges, as drawn. The front: the plank door in tile 1 (closed) in a dark frame, a light handle; a window of two panes in tile 2, a light frame with light streaks across its glass, a log sill. *Inferred:* the back gable as the front's; a window over each side's tile boundary and one over the back's, the front's kind; the interior (plank floor, open to the roof). The art's window is four voxels wider than its tile; here it keeps within it.
- **Lodge.** Four tiles by two, one storey of three courses: cream brick walls on a grey stone plinth, a dark band under the eaves, big timber corner posts, light on their left and shaded on their right, as drawn. Over the walls a fascia of dark boards (z 64-71), and over that a low gable roof of brown boards, its ridge along the front, rising 0.5 a voxel in (to z 82), its eaves three out at the front and back and eight at the ends over barge boards, a light ridge board where it shows beside the upper part, its boards dark in front and light behind, as drawn. Rising through it in the middle, an upper part of light boards (from the fascia to z 87) under a dark fascia of its own and a low gable roof, its ridge along the front, rising 0.67 a voxel in (to z 107) under a light ridge board, its boards dark in front and light behind, as drawn; it stands where the art draws it, over the storey, off the tile grid. The front: a window over the boundary between tiles 0 and 1 in a dark frame, a light streak across its glass, a dark sill; the door in tile 2 (closed), grey-brown planks in a dark frame with a light band and handle, a transom over it, posts either side of it and a porch beam over them, as drawn. *Inferred:* the front's left end (the image cuts it off), as its right end is drawn: the left corner post and its wall; the back's two windows and a window over each side's tile boundary, the front's kind; the interior (plank floor, open to both roofs). The art's two roof tiers are read as a lower gable with the upper part through it, which puts their edges where the art draws them from the front.

## Treatments

Seven files a family, the [shared specification's](../../../knowledge/VARIATIONS.md) names and order: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Every voxel carries a material label in the sculptor ([palettes.py](palettes.py)), so each treatment paints the same geometry and the groups survive recolouring.

- **Base** uses one palette shared by the two buildings, 36 colours: the art's own (it is native pixel art, so each is a colour it draws, read pixel by pixel), the invented floors, ceilings and buried foundation stone noted as such, glass a little lighter so that what is behind still shows.
- **Cartoon** is the same building simplified and regularised on the same grid, its doors, windows and slots unchanged: slates in rows twice as deep in fewer tones, logs without their shade, a wider king post and rafters, bigger bricks, boards in wider stripes, inner frames on the windows, no streaks on the glass.
- **CratePalette** copies the pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte for byte and maps each colour to its nearest entry among those allowed for its material (greys, lights, woods); the mapping is in the manifest. Glass is crate index 253 (115, 190, 211), kept for glass alone and given the Glass material.
- **TwoColor**, by the user's rule (2026-10-28): *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* The cabin three groups (roof, wood, glass: its slates' greys and dark outlines one grey, its logs, door, frames and gables one brown, the handle folded into the wood); the lodge four (roof, wood, light, glass: its roofs' boards one brown, its posts, porch, door, frames, sill and plinth one lighter wood, its brick walls and the upper part's boards one cream).
- **The mixtures**: Cartoon_TwoColor paints the Cartoon geometry with the same group colours; CratePalette_TwoColor and Cartoon_CratePalette_TwoColor paint each group with one crate entry, the same in both (in the manifest), no two groups of a family on one entry.

## Glass

Every pane is a palette colour drawn with MagicaVoxel's **Glass** material (`_type _glass`), which VCOM reads as glass (its [Docs/GLASS.md](../../../../VoxelXCOM/Docs/GLASS.md)): the art's pale blue at `_trans 0.7`, its white streaks as a lighter glass at 0.5. Panes are a voxel thick in a wall's inner layer, a voxel back from the frame, as `SimpleWindow1`'s. Glass voxels (Base): the cabin 720, the lodge 1,050. There are no lights in these buildings, by the user's choice.

## Validation

All of it was run, and passed:

- **Generation** ([generate.py](generate.py)) reads every file back: canvas, voxels and palette as intended, Glass on exactly the glass indices, index 255 unused, one connected model, recolours on exactly their source's voxels, the crate palette byte for byte, one colour a group in TwoColor, Cartoon a different shape from Base. It refuses to overwrite a file it did not write last (`--replace-generated` to override).
- **[validate.py](validate.py)** re-checks all of that from disk and the evidence below, and the grid: nothing in the middle of a storey's tiles at the two levels units fill there, and no glass in a sill course but a door's slot. It writes [validation-summary.json](validation-summary.json).
- **Structural audit**: `tools/inspect_vox.py`, 14 files, no errors or warnings ([structural-audit.json](structural-audit.json)).
- **Whole import** ([qa/godot/whole_import.gd](qa/godot/whole_import.gd)): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625: voxel counts, glass voxels recognised as glass, grounded at y 0, the occupied size ([qa/whole-import.json](qa/whole-import.json)).
- **In the game** ([qa/integration.py](qa/integration.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd)), in a scratch copy of VCOM, never the game itself: every treatment of every family cut into the game's 16-cubed pieces, imported, placed in a level of grass, 14 scenes, and asked what the game sees ([qa/integration-report.json](qa/integration-report.json)). Every check passed: the level the game stamps is the model voxel for voxel (count and checksum of every voxel's place, colour and glass, pieces placed with turns); every tile is a floor at its level, under the roof; round each building, at the two levels a unit fills, every wall, sill and closed door is shut and every window open; a line of sight through each window at the eye and none through the walls or doors; a vault in over each sill; nothing else can be stepped through; every tile reachable from the street; the view cuts away at the roof. The geometry tested was checked to be the files' (each scene's stamping checksum recomputed from the final sculptor).
- **Visual review**: renders in the game's own renderer (its environment, sun, glass shaders and time of day) from four sides, from the game's camera, cut away at the roof, at dusk and at night, a soldier figure for scale ([previews/](previews/): `_family`, `_geometry`, `_ingame` for each family), and each Base drawn in the art's projection beside the source (`_art`).
- **Preserved**: ChatGPT's 240 poke_m files from before these buildings (its models, generators, records and previews) are unchanged, and `output/poke_m/`'s README.md and FILES.md only had a section on these buildings added at their end ([preserved-hashes.json](preserved-hashes.json)). Another agent was writing poke_m vegetation, rocks, lights and deadwood into the same folder while these were made; none of its files was touched, nor are they checked here.

**Not tested:** opening the files in MagicaVoxel's own editor; adding the pieces to the game's `Pieces.tres` and painting them in the level editor; a battle fought through them (destruction, blood, AI).

## Putting them into the game

Nothing in VoxelXCOM was changed. To bring a building in, cut it as the test does: [qa/cut_pieces.py](qa/cut_pieces.py) assigns each voxel to a slot by the role the sculptor gave it and writes one 16-cubed `.vox` a kind, reusing a kind turned where a piece is one turned. What the kinds should be, as the test set them:

| Base | Pieces | Kinds | Window pieces | Door pieces |
| --- | --- | --- | --- | --- |
| LogCabin | 88 | 49 | 7 | 2 |
| Lodge | 124 | 75 | 10 | 2 |

The two Base buildings come to 124 kinds.

- **Floor** (level 0): solid, `tile_grid`, a `VoxelDestruction` as the ground's; not `cutaway`.
- **Window** (an edge piece with glass, not a door): `window` and `cutaway`, worn as `SimpleWindow1.tres`.
- **Door** (each leaf's two pieces): solid, `cutaway`; there is no door mechanic yet, so units enter by vaulting through windows.
- **Everything else**: solid, `cutaway`, worn as `SimpleWall1.tres`.
- **Cutaway heights:** the cabin 3, the lodge 4 (the roof).
- **Costs:** a map's level palette gains the shared Base palette's 36 colours (of 254).

## Reproduction

From the workspace root (Python 3 with Pillow; Godot 4.7 for the game test):

```powershell
python output/poke_m/buildings/generate.py
$files = (Get-Content output/poke_m/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { "output/poke_m/$_" }
python tools/inspect_vox.py $files --output output/poke_m/buildings/structural-audit.json
# The game test needs a scratch copy of VoxelXCOM/vcom, never the game itself:
python output/poke_m/buildings/qa/integration.py --game <copy of vcom> --render --out <render folder>
python output/poke_m/buildings/compose_previews.py <render folder>
python output/poke_m/buildings/compare_art.py
python output/poke_m/buildings/validate.py
```

`qa/godot/whole_import.gd` is run in the copy as poke_g's notes say. [sculpt.py](sculpt.py) owns the geometry, [palettes.py](palettes.py) the colours and groups, [voxlib.py](voxlib.py) the VOX I/O, [generate.py](generate.py) the files and manifest. The generator owns only the 14 building files and this folder's manifest.

## Decided

By the user (2026-10-28), for every building: doors closed, as drawn, each in exactly one doorway slot; no lights; TwoColor's minimal-colour rule; upper floors reached only by stairs the art draws. For poke_m (2026-10-29): model all three of its buildings, the two cut off by the image's edges completed.

Made without asking, on the evidence above: that the two cut-off structures are one building, from their identical roofs, and one model for both; completing the lodge's unseen left end as its right end is drawn; heights at 0.5 for this image; the game-grid conventions (as poke_j's); the cabin's walls on the four tiles its roof covers and its window kept within its tile; the lodge's tiles half a tile off the map's so that its door fills one; the lodge's two roof tiers read as a lower gable with an upper part rising through it, the upper part off the tile grid where the art draws it; the cabin's log ends as the side walls' logs running out past the corners; the inferred sides, backs and insides listed under Each building; glass clarities and colours; the shared Base palette; each family's TwoColor groups, colours and folds; the crate mapping's material classes, index 253 for glass, and no two groups of a family on one crate entry.
