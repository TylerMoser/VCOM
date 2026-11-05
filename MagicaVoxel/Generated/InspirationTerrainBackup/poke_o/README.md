# poke_o coastal trees

Created 2026-10-27: **49 complete VOX files**, seven appearances with Base and all six established variations. Complete models only; no per-cell files or brush packages.

[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Source and scale

[poke_o.png](../../poke_o.png) is a 640 x 640 pixel-art map on a 16-pixel tile grid. Approximately one source pixel corresponds to one voxel, with 16 voxels per game tile. Canopy width and visible vertical extent guide sizing; square depth and hidden structure are inferred. Top-down projection mixes height with depth, so these are relative authoring estimates.

Seven appearances are included: broad olive crown, taller narrow olive crown, long-leaf lime tree, long-leaf mint tree, low-foliage cypress-like sapling, round sapling on an exposed stem, and beach palm. The two long-leaf trees share geometry but have distinct source palettes. The cypress label describes silhouette rather than a verified species. Repeated or occluded copies are not new types. Perched creatures, bright hedges, flowers, grasses, rocks, beach props and painted ground shadows are excluded.

The broad crown is 32 x 32 x 40; the narrow and long-leaf trees are 32 x 32 x 48; saplings are 16 x 16 x 32; the palm is 32 x 32 x 40. Crops include contextual neighbors and use top-left XY with exclusive right/bottom edges; they are not segmentation masks. Models are Z-up, rooted at z=0, horizontally canvas-centered, with scene translation `0 0 floor(height/2)` and no required facing direction.

| Base model | Canvas XYZ | Base occupied XYZ | Comparison |
| --- | --- | --- | --- |
| [PokeO_BroadCrown](PokeO_BroadCrown.vox) | 32 x 32 x 40 | 32 x 31 x 40 | [All styles](previews/PokeO_BroadCrown_family.png) |
| [PokeO_NarrowCrown](PokeO_NarrowCrown.vox) | 32 x 32 x 48 | 32 x 31 x 48 | [All styles](previews/PokeO_NarrowCrown_family.png) |
| [PokeO_LimeLeafTree](PokeO_LimeLeafTree.vox) | 32 x 32 x 48 | 30 x 30 x 48 | [All styles](previews/PokeO_LimeLeafTree_family.png) |
| [PokeO_MintLeafTree](PokeO_MintLeafTree.vox) | 32 x 32 x 48 | 30 x 30 x 48 | [All styles](previews/PokeO_MintLeafTree_family.png) |
| [PokeO_CypressSapling](PokeO_CypressSapling.vox) | 16 x 16 x 32 | 15 x 15 x 32 | [All styles](previews/PokeO_CypressSapling_family.png) |
| [PokeO_StemmedSapling](PokeO_StemmedSapling.vox) | 16 x 16 x 32 | 16 x 15 x 32 | [All styles](previews/PokeO_StemmedSapling_family.png) |
| [PokeO_BeachPalm](PokeO_BeachPalm.vox) | 32 x 32 x 40 | 30 x 28 x 40 | [All styles](previews/PokeO_BeachPalm_family.png) |

## Modeling decisions

- BroadCrown has rounded shoulders and a pointed crown. NarrowCrown has a taller, more columnar profile with subtle shoulder transitions.
- LimeLeafTree and MintLeafTree use long overlapping leaf clusters around a solid crown core. The source mint ramp is cooler and lighter; lime is warmer. Neither includes a perched creature.
- CypressSapling has a narrow crown extending close to the ground. StemmedSapling raises its crown over a longer exposed trunk.
- BeachPalm has a flared root base, solid ringed trunk, arching radial fronds with shallow edge notches, and short upright central leaves. Base has seven varied fronds; Cartoon has eight balanced fronds and exact C4 geometry/paint. Fronds remain connected to the trunk; no source ground shadow or surrounding beach props are included.

All models have continuous wood and filled interiors appropriate to their forms. Cartoon changes geometry deliberately and has exact horizontal quarter-turn occupancy and paint symmetry. Base uses restrained irregularity and coherent color clusters. The local sculptor dispatches profile crowns and drooping leaf construction adapted from established families, with new palm geometry. All implementation files are local; no runtime imports from other image folders.

## Variations and palette

The [shared specification](../../knowledge/VARIATIONS.md) defines the six treatments: Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Every recolor preserves its designated Base or Cartoon's exact coordinates, dimensions and scene placement.

Explicit semantic groups divide leaves/fronds/crown core from wood/trunk/roots/hidden stems. TwoColor uses exactly two occupied indices with distinct RGBA values, one per group. The palm's fronds and central leaves all share one foliage paint color; ringed bark loses its paint shading while geometry remains intact. Preview lighting still shades both colors.

CratePalette copies the entire pinned [crate palette](../../knowledge/palettes/crate-palette.json). Foliage maps to slots 241-246 and wood to actual crate browns 178-180. Palette reduction may make the lime and mint treatments more similar; their distinct source families remain recorded. Both crate/two-color mixtures use the same selected foliage/wood colors within each family. Index 255 is unused. Exact mappings, palettes, occupied bounds, counts and geometry-source hashes are in manifest.json.

## Validation and integration

[Structural audit](structural-audit.json) covers all 49 outputs. Generation rereads serialized files and verifies dimensions, bounds, connectivity, recolor coordinate equality, C4 occupancy and paint, full reference palette hash and two-color counts. [Godot report](godot-validation.json) records whole Mesh imports at scale 0.0625, retained voxel counts and grounded bounds using the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final checks and visual review.

[Contact sheet 1](previews/contact_01.png) and [sheet 2](previews/contact_02.png) cover all treatments. [Geometry sheet 1](previews/geometry_01.png) and [sheet 2](previews/geometry_02.png) show four azimuths for Base and Cartoon. Camera/lighting match within families; different families are framed independently, so card size is not world scale.

These checks exercise the whole-model importer/render path, not gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. Every model exceeds the 16-cubed PieceKind contract in height. Widths remain below the loose-model limit of 62, but that separate runtime path is untested. VoxelXCOM remains unchanged. Integration must be handled separately without automatically generating cell files.

## Reproduce and continue

From the workspace root:

```powershell
python output/poke_o/generate.py
$pokeOFiles = (Get-ChildItem -LiteralPath output/poke_o -Filter *.vox -File).FullName
python tools/inspect_vox.py $pokeOFiles --output output/poke_o/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_o/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_o/compose_previews.py
python output/poke_o/validate.py
```

Automated rendering launches hidden and captures qa/render.log and qa/render-errors.log. Python generation uses the standard library; composition uses Pillow. generate.py owns families and palettes; sculpt.py owns dispatch/palm construction; profiles.py and leaves.py own crown construction; voxlib.py supplies VOX I/O. Source image, regions and shared palette are dependencies. Module hashes are recorded in the manifest.

The generator owns only its 49 named files and manifest. It refuses unknown or changed existing files unless `--replace-generated` is deliberately supplied; preserve hand edits before that override. After revisions, refresh audits, renders, comparison sheets and visual-review records. Save future poke_o models directly here with distinct names.


## Rocks (2026-10-28)

[3 rock appearances, 21 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.

- [Flowers, bushes and grass](vegetation/README.md): 5 new appearances, 35 complete models, and existing-family reuse links.

## Buildings (2026-11-03)

- [Three buildings, 21 complete models](buildings/README.md): `PokeO_GableHouse` (the gabled house, three copies, a dormer on its left slope), `PokeO_SkylightHouse` (the skylight house, two copies) and `PokeO_WideHouse` (the wide house with its rooftop units and a front wing), each in Base and all six variations, made on VCOM's tile grid at game scale (closed doors, MagicaVoxel Glass windows) as the poke_n buildings are, and tested in a copy of the game. [Overview](buildings/overview.png) | [File index](buildings/FILES.md).

## Terrain (2026-11-04)

- [4 terrain styles, 196 complete models](terrain/README.md): `PokeO_EarthBank_H1 (1 level)`, `PokeO_EarthLedge_H2 (2 levels)`, `PokeO_OrangeRock_H5 (5 levels)`, `PokeO_PurpleRockPool_H2 (2 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
