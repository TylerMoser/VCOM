# Terrain kits

2026-11-03/04: **the ground shapes of all 25 inspiration images as modular voxel kits: 44 styles, 330 pieces, 2,338 complete VOX files** (2,310 of the kits' pieces, 28 of 4 whole small floating islands), each in Base and the six established variations. Every ridge, cliff, raised terrace, bank, ledge, gully wall, cave wall, island rim, platform and retaining wall the images draw is a style here, with its cave mouths, waterfalls, drains and notches as extra pieces of it. The files sit beside each image's other models in `output/<image>/`; this folder holds the code, the checks and the evidence, and `output/<image>/terrain/` each image's notes and previews.

[All files](FILES.md) | [Overview](overview.png) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [In-game report](qa/integration-report.json) | [Whole import](qa/whole-import.json) | [Structural audit](qa/structural-audit.json) | [Authoring notes](../../knowledge/TERRAIN.md)

## The user's decisions (2026-11-03)

- **Modular kits.** For each distinct style an image draws: complete pieces on the game's grid, one tile wide at the height drawn (the straight face, outer and inner corners, and the ends, falls, mouths and gullies drawn), turned and placed side by side; each image its own files in its own colours, with previews of the pieces put together as the image draws them.
- **Heights as drawn, in whole levels.** An image with tall and short cliffs gets several styles.
- **Also cave mouths, waterfalls and retaining walls** (not Mario's backdrop hills).
- **Floating islands both ways**: rim pieces hanging down, and a few whole small islands.

## A piece

A piece is one tile, 16 x 16 voxels, and a whole column: `16 x 16 x 16(H+1)` for a style `H` levels high. Its lowest level (z 0-15) is the image's lower ground tile, the ground collection's file copied voxel for voxel in the same treatment, so a piece stands among the plain ground tiles without a seam; over a water tile, whose surface is two voxels down, the cliff's foot stands on the water. Its face is set back four voxels from the tile's edge and stands out of that line by the style's relief (columns, lumps, beds, blocks, crags), its top the upper ground tile's top three layers, the grass hanging over the face. A floating rim has no lower ground: its rock hangs to z 0. Every pattern repeats every 16 voxels along a face and is measured round the corners the same way, so the pieces join along a run and round corners.

The pieces, drawn facing local -y (MagicaVoxel's front) and turned in quarter turns about z to fit:

- **Fill**: a raised tile with raised ground all round: the column, no face.
- **Straight**: a face along one side (local -y).
- **OuterCorner**: faces on two sides meeting round a convex corner (local -y and -x).
- **InnerCorner**: raised ground all round but one diagonal: the concave corner (the notch at local -x -y).
- **Ridge**: a raised strip a tile wide: faces on two opposite sides (local -y and +y).
- **RidgeEnd**: the end of such a strip: faces on three sides (local -y, +y and -x).
- **Pillar**: a single raised tile: faces all round.

and the extras a style has:

- **Fall**: the straight face with the river (its own water tile) pouring over the rim in a sheet down to the pool below (its own water tile), foam over the lip and where it lands.
- **Channel**: a raised fill tile carrying the river to a fall: the water tile on top.
- **NarrowFall**: a spring: a narrow stream rising a few voxels back from the edge and falling down the middle of the face into its pool (off a floating rim, into the air, ending in mist).
- **CaveMouth**: the straight face with a round-headed opening at its foot going 11 voxels back to a dark end, the lower ground carried in as its floor.
- **Archway**: the masonry wall's straight face with a round-headed passage at its foot, as the cave mouth is.
- **Drain**: the straight face with a round-headed, barred outfall at its foot, in a ring of dressed stone.
- **Notch**: the straight face with a V-shaped gully cut down it, narrowing to nothing 11 voxels back.

**Placing them** is the autotiling every 2D map uses: for each raised tile, the lower of its four neighbours pick the piece and its turn (none lower: Fill, or InnerCorner if a diagonal is; one: Straight; two at a corner: OuterCorner; two opposite: Ridge; three: RidgeEnd; four: Pillar). `layout.py` does it (`piece_for`, `place`), and the previews and the in-game test put every style together that way. A turn `q` takes (x, y) to (15-y, x) q times, VCOM's own turn. For VCOM a piece's column is cut into its `H+1` 16-cubed cells, one a level, as the level editor places a cell's middle piece: the test does exactly that.

**Whole islands** are the rim style's pieces laid out as an island, with the rock hanging below in a mass that tapers to a point: two for poke_s, two for poke_u, as the images' small islands are, each one model on the grid (its underside two whole levels deep).

## The styles

Heights were measured on each image's own faces: the face's drawn height in the image's pixels, from under the rim to the foot, times 16 over the image's pixels a tile is a height in voxels as drawn, divided by the image's vertical foreshortening K (drawn pixels a voxel of height, over a pixel a voxel across) to a true height, and rounded to whole levels. K is the one each image's buildings were made with (0.46 for the Pokemon maps that have none of their own; poke_m 0.5; poke_o and poke_r 0.375; poke_u 0.4375); Pixelwood's, 0.88, is its house's (its author put the wall top at z 34 for 30 art pixels drawn), Mario's, 0.7, its blocks'. Every style's colours are its art's own, read off its pixels; its measurements, crop and the reasons are in its image's notes.

| Image | Style | Family | Levels | Px a tile | K | Lower ground | Extra pieces |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| [mario](../mario/terrain/README.md) | GrassPlatform_H1 | MarioPlatform | 1 | 48 | 0.7 | Meadow | - |
| [mario](../mario/terrain/README.md) | GrassPlatform_H2 | MarioPlatform | 2 | 48 | 0.7 | Meadow | - |
| [mario](../mario/terrain/README.md) | TrimPlatform_H2 | ZigzagTrim | 2 | 48 | 0.7 | Meadow | - |
| [pixelwood_a](../pixelwood_a/terrain/README.md) | EarthBank_H2 | EarthBank | 2 | 48 | 0.88 | Meadow | - |
| [pixelwood_b](../pixelwood_b/terrain/README.md) | SlateLedge_H1 | StrataCliff | 1 | 80 | 0.88 | Meadow | - |
| [pixelwood_c](../pixelwood_c/terrain/README.md) | EarthBank_H2 | EarthBank | 2 | 49 | 0.88 | Meadow | Fall, Channel |
| [poke_a](../poke_a/terrain/README.md) | EarthCliff_H3 | StripedCliff | 3 | 12.25 | 0.46 | Meadow | Fall, Channel |
| [poke_b](../poke_b/terrain/README.md) | CourseCliff_H5 | LumpyWall | 5 | 16 | 0.46 | Meadow | - |
| [poke_c](../poke_c/terrain/README.md) | BlockCliff_H3 | FacetedCliff | 3 | 16 | 0.46 | Meadow | Fall, Channel |
| [poke_d](../poke_d/terrain/README.md) | RockLedge_H3 | LumpyWall | 3 | 16 | 0.46 | OchreFloor | - |
| [poke_d](../poke_d/terrain/README.md) | RockBank_H3 | LumpyWall | 3 | 16 | 0.46 | River | Drain |
| [poke_d](../poke_d/terrain/README.md) | RiverCliff_H6 | LumpyWall | 6 | 16 | 0.46 | River | Fall, Channel |
| [poke_d](../poke_d/terrain/README.md) | RetainingWall_H5 | Masonry | 5 | 16 | 0.46 | Cobblestone | Archway |
| [poke_e](../poke_e/terrain/README.md) | EarthBank_H1 | LumpyWall | 1 | 16 | 0.46 | Meadow | - |
| [poke_e](../poke_e/terrain/README.md) | LakeBank_H1 | LumpyWall | 1 | 16 | 0.46 | Lake | - |
| [poke_f](../poke_f/terrain/README.md) | StonyBank_H4 | StonyBank | 4 | 16 | 0.46 | DryMeadow | - |
| [poke_g](../poke_g/terrain/README.md) | RockLedge_H2 | LumpyWall | 2 | 16 | 0.46 | Meadow | - |
| [poke_h](../poke_h/terrain/README.md) | FarmBank_H1 | LumpyWall | 1 | 16 | 0.46 | Meadow | - |
| [poke_h](../poke_h/terrain/README.md) | PondCliff_H3 | LumpyWall | 3 | 16 | 0.46 | Pond | - |
| [poke_i](../poke_i/terrain/README.md) | EarthCliff_H3 | StripedCliff | 3 | 9.5 | 0.46 | Meadow | NarrowFall |
| [poke_j](../poke_j/terrain/README.md) | EarthCliff_H3 | StripedCliff | 3 | 12.25 | 0.46 | Meadow | - |
| [poke_j](../poke_j/terrain/README.md) | PondBank_H3 | StripedCliff | 3 | 12.25 | 0.46 | Pond | - |
| [poke_k](../poke_k/terrain/README.md) | EarthCliff_H3 | StripedCliff | 3 | 14.75 | 0.46 | Meadow | - |
| [poke_k](../poke_k/terrain/README.md) | LakeBank_H3 | StripedCliff | 3 | 14.75 | 0.46 | Lake | - |
| [poke_l](../poke_l/terrain/README.md) | TerraceBlock_H2 | LumpyWall | 2 | 16 | 0.46 | Meadow | Notch |
| [poke_m](../poke_m/terrain/README.md) | GullyCliff_H3 | LumpyWall | 3 | 16 | 0.5 | Meadow | Fall, Channel |
| [poke_m](../poke_m/terrain/README.md) | RockMountain_H3 | LumpyWall | 3 | 16 | 0.5 | Meadow | - |
| [poke_n](../poke_n/terrain/README.md) | EarthCliff_H2 | StripedCliff | 2 | 16 | 0.46 | Meadow | - |
| [poke_n](../poke_n/terrain/README.md) | RedRockCliff_H9 | FacetedCliff | 9 | 16 | 0.46 | Meadow | - |
| [poke_o](../poke_o/terrain/README.md) | EarthBank_H1 | LumpyWall | 1 | 16 | 0.375 | Meadow | - |
| [poke_o](../poke_o/terrain/README.md) | EarthLedge_H2 | LumpyWall | 2 | 16 | 0.375 | Meadow | - |
| [poke_o](../poke_o/terrain/README.md) | OrangeRock_H5 | FacetedCliff | 5 | 16 | 0.375 | Meadow | - |
| [poke_o](../poke_o/terrain/README.md) | PurpleRockPool_H2 | LumpyWall | 2 | 16 | 0.375 | InlandPool | - |
| [poke_p](../poke_p/terrain/README.md) | GullyWall_H2 | LumpyWall | 2 | 16 | 0.46 | RockyGully | CaveMouth |
| [poke_q](../poke_q/terrain/README.md) | ClayTerrace_H3 | FacetedCliff | 3 | 16 | 0.46 | TerraceClay | - |
| [poke_q](../poke_q/terrain/README.md) | RockTerrace_H3 | FacetedCliff | 3 | 16 | 0.46 | Meadow | - |
| [poke_q](../poke_q/terrain/README.md) | CoastalCliff_H5 | FacetedCliff | 5 | 16 | 0.46 | BeachSand | - |
| [poke_r](../poke_r/terrain/README.md) | EarthCliff_H3 | StripedCliff | 3 | 16 | 0.375 | Meadow | - |
| [poke_r](../poke_r/terrain/README.md) | RaisedBed_H1 | LumpyWall | 1 | 16 | 0.375 | Meadow | - |
| [poke_s](../poke_s/terrain/README.md) | IslandRim_H3 | IslandRim | 3 | 10 | 0.46 | none (floating) | Fall, Channel |
| [poke_s](../poke_s/terrain/README.md) | Terrace_H2 | LumpyWall | 2 | 10 | 0.46 | Meadow | CaveMouth, Fall, Channel |
| [poke_t](../poke_t/terrain/README.md) | CaveWall_H4 | LumpyWall | 4 | 16 | 0.46 | CaveSand | CaveMouth |
| [poke_t](../poke_t/terrain/README.md) | RockPlatform_H4 | LumpyWall | 4 | 16 | 0.46 | CaveSand | - |
| [poke_u](../poke_u/terrain/README.md) | IslandRim_H5 | IslandRim | 5 | 16 | 0.4375 | none (floating) | NarrowFall |

The families (`families.py`):

- **StripedCliff**: the earth cliff of rounded columns most of the Pokemon maps draw: lit along the top, shaded toward the foot, a dark crease between columns, the top's grass hanging over in a jagged edge.
- **LumpyWall**: rock or earth in rounded lumps, in one or more courses (each lit along its top, dark under it), topped by the grass hanging over or by a rim of the rock itself.
- **StrataCliff**: horizontal beds, each top edge standing out and lit, its foot tucked in and dark, joints staggered bed to bed.
- **FacetedCliff**: angular blocks in rows, each standing out its own amount, lit along its top and left edge, a dark crease below and to the right.
- **EarthBank**: a near-flat earth wall, a light band under the scalloped grass rim, darker blotches, a jagged dark foot.
- **StonyBank**: a bank faced with rounded stones of several sizes, lit along their tops, dark seams, a dark foot.
- **IslandRim**: the rim of a floating island: rows of crags hanging under the grass, each row tucked in from the one above and tapering to points, nothing below.
- **MarioPlatform**: Paper Mario's raised ground: a flat top with a pale rim line, a fringe of grass tongues over warm soil marked with small crosses.
- **ZigzagTrim**: Paper Mario's trimmed side: a band of orange with dark red triangles over a dark teal wall.
- **Masonry**: a built wall: staggered courses of dressed stone, a few of other stones among them, a coping.

## The seven treatments

- **Base**: the art's colours.
- **Cartoon**: simpler, bolder shapes: wider columns and lumps, an even rim a voxel further out, larger blocks and courses, and fewer shades. Every piece with a face differs from Base in shape.
- **CratePalette**: Base's geometry exactly, the pinned crate palette byte for byte, each colour on the nearest entry of its material's range; the copied ground keeps its tile's own crate entries.
- **TwoColor**: Base's geometry, one flat colour for each material, per the rule: *"Don't require exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors and combining all similar colors into large chunks of single-color voxels."* A face's shades, lines and lit edges are its material's one colour; the grass hanging over a face is its top tile's grass; a fall's water and foam its river's water; the copied ground tiles are the ground collection's own TwoColor tiles, each of their groups one colour. There is no glass and no light in terrain.
- **Cartoon_TwoColor**, **CratePalette_TwoColor**, **Cartoon_CratePalette_TwoColor**: the combinations, each on its geometry's exact occupancy.

Palette index 255 (the game's blood) is never used; every material is diffuse.

## Checks

- [validate.py](validate.py) reads every file back (2338 files, 0 problems): its canvas whole tiles and levels, its voxels the manifest's, grounded, one connected model, index 255 unused, no glass; each treatment on its geometry's exact occupancy and Cartoon a different shape; the crate palette byte for byte; one colour a material in TwoColor; a piece's lowest level holding its lower ground tile intact, a Fill's top its upper tile's; and the 4293 files of ChatGPT's of before 2026-10-28 in the image folders unchanged ([preserved-hashes.json](preserved-hashes.json)).
- [qa/structural-audit.json](qa/structural-audit.json): the workspace's own `tools/inspect_vox.py` over every file.
- [qa/whole-import.json](qa/whole-import.json): every file read and meshed whole by the game's own MagicaVoxel importer at Scale 0.0625 in a scratch copy of VCOM (2338 of 2338: counts, grounded, size).
- [qa/integration-report.json](qa/integration-report.json): **in the game** (a scratch copy of VCOM checked identical to the real one first), every style in every treatment and every island: the delivered files cut into the game's cells and laid out (the standard layout: straight runs, outer and inner corners, a ridge with both ends, a pillar, the fill and the style's extras, on a field of its ground), the rules asked: every tile a floor at its level and nothing stood on inside a cliff, a one-level face climbed and a taller one not, the plateau reached from below only over a one-level face (a floating one from its own top), and the level stamped voxel for voxel as the files are (336 scenes, 336 passing every check). [qa/renders/](qa/renders/) has a few by day, dusk and night in the game's renderer.

## What to know when using them

- **Kit pieces join at one height and one style.** A raised area of one style is all its pieces; a step from one height to another, or one style to another, is two raised areas meeting, not a transition piece. A diagonal ledge (poke_g's) is laid out stepped, as tiles are.
- **The heights are as drawn**, so the tallest are tall: poke_n's red rock 9 levels, poke_d's river cliffs 6, poke_b's three-course cliffs and poke_d's retaining wall 5. They are measured with each image's K, which the buildings were made with; the [stairs collection](../stairs/README.md) measured its rises differently (poke_b's and poke_k's stairs rise 32 voxels, 2 levels), so its stairs are lower than these cliffs: a stair climbs part of a face, or the stair's rise wants revising.
- **Water is static, opaque voxel art**, as the ground collection's: the rules see a fall's or a pool's cell as solid ground, nothing in VCOM swims or flows.
- **A cave mouth, an archway and a drain are recesses in one tile** (11 voxels deep at most, a dark end), not passages: to the rules the cell is solid. The [Codex waterfalls and caves](../codex_waterfalls_caves/README.md) are whole models of the falls' curtains and of cave entrances with real passages, meant to be placed beside cliffs; these kits are those cliffs, with a fall or a mouth of their own as a piece.
- Approximations: the faces' depths, hidden sides and the islands' undersides are inferred from 2D art; poke_o's orange outcrop is cut off by the frame (its top tier measured); poke_u's narrow fall is clipped in the art and reconstructed; poke_s is a blurred JPEG.

## Reproduction

```
python output/terrain/generate.py           # writes the files and manifest.json (refuses others' files)
python output/terrain/validate.py           # validation-summary.json
python output/terrain/compose_previews.py   # previews and overview.png
python output/terrain/document.py           # these documents
python output/terrain/qa/terrain_test.py --game <scratch copy of VoxelXCOM/vcom> --files output [--render]
```

`styles.py` holds every style (its family, levels, colours, ground tiles, measurements and notes), `families.py` the families, `kit.py` the pieces and painting, `layout.py` the autotiling, `islands.py` the whole islands. The generator writes only the files its manifest lists, and refuses any file already there that it did not write.
