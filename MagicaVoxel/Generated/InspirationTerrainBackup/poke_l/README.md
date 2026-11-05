# poke_l layered trees

Created 2026-10-27: **21 complete VOX files**, three tree forms with Base and all six established variations. No per-cell files or brush packages.

[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Source interpretation and scale

[poke_l.png](../../poke_l.png) is a 272 x 192 unscaled sprite sheet on a 16-pixel tile grid. Approximately one source pixel corresponds to one voxel; 16 voxels equal one game tile. Unlike the preceding resized JPEG maps, this sheet supports direct pixel-scale estimates. Square canopy depth and hidden geometry remain inferred; sprite vertical extent mixes height with canopy projection.

There are three complete tree forms: a taller layered tree with spreading lower leaf clusters, a shorter rounder crown with broad shoulders, and a narrow sapling. The isolated sprites below the terrain provide the clearest references. Trees in the upper map repeat these forms. The small tree cut off at the map's bottom edge is treated as a clipped sapling, not a separate species. Rocks, terrain, water outlines, small ground vegetation and painted ground shadows are excluded.

The tall tree uses a 40 x 40 x 48 canvas, the round tree 40 x 40 x 44, and the sapling 16 x 16 x 32. Crop boxes include small amounts of context and shadow; these are reference regions, not segmentation masks. Actual geometry bounds are recorded separately below and in the manifest. Shadows are not voxels.

| Base model | Canvas XYZ | Occupied XYZ | Comparison |
| --- | --- | --- | --- |
| [PokeL_LayeredTree](PokeL_LayeredTree.vox) | 40 x 40 x 48 | 36 x 36 x 48 | [All styles](previews/PokeL_LayeredTree_family.png) |
| [PokeL_RoundedTree](PokeL_RoundedTree.vox) | 40 x 40 x 44 | 38 x 38 x 44 | [All styles](previews/PokeL_RoundedTree_family.png) |
| [PokeL_Sapling](PokeL_Sapling.vox) | 16 x 16 x 32 | 14 x 14 x 32 | [All styles](previews/PokeL_Sapling_family.png) |

## Modeling and palettes

The new local sculptor builds solid crown cores with overlapping elliptical leaf clusters arranged in successive rings. Raised leaf centers and dark lower rims interpret the sprite's scalloped leaf drawing in 3D. The taller form narrows more quickly above its low skirt; the rounded form retains broader shoulders. The sapling uses fewer, smaller clusters and a narrow trunk. Wood continues into the canopy so all forms remain connected and solid inside.

Base uses twelve clusters around large-tree rings, slight angle offsets and coherent leaf paint. Cartoon uses eight larger clusters, balanced rings and exact horizontal quarter-turn symmetry in both occupancy and paint. Sapling counts reduce from eight to four. Thus Cartoon is a geometry treatment, not only a recolor. A canonical quarter enforces exact C4 symmetry. No directional baked sunlight or ground shadow is included in the paint.

Models are Z-up, rooted at z=0, horizontally canvas-centered, with scene translation `0 0 floor(height/2)`. They have no required forward direction. The palette is guided by the source's dark green leaf rims, mid-green lobes and yellow-green upper clusters, with brown wood. Fine black sprite outlines are interpreted as shadowed boundaries rather than literal black shells.

The [shared variation specification](../../knowledge/VARIATIONS.md) applies: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Color-only variants preserve every occupied coordinate of their designated Base or Cartoon source, including raised leaf relief.

Semantic groups are explicit coordinate assignments: foliage is all leaf geometry and crown core; wood is trunk, roots and internal stem. TwoColor occupies exactly two indices with two distinct RGBA colors, one per group. Lit previews still shade faces. CratePalette copies the full pinned [crate palette](../../knowledge/palettes/crate-palette.json), maps foliage to 241-246 and wood to actual crate browns 178-180, and leaves index 255 unused. Both crate/two-color mixtures reuse the same two selected group colors. Exact color maps, representative colors, dimensions, counts and source hashes are in manifest.json.

## Validation and integration

[Structural audit](structural-audit.json) covers the 21 delivered models. The generator rereads serialized files and checks dimensions, bounds, palette indices, single-component connectivity, exact recolor coordinates, C4 occupancy and paint, pinned palette hash and two-color counts. [Godot report](godot-validation.json) records whole Mesh imports at scale 0.0625, retained voxel counts and grounded bounds, using the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final evidence and visual review.

[All-style sheet](previews/contact_01.png) covers every treatment. [Four-view sheet](previews/geometry_01.png) shows Base and Cartoon from four azimuths. Camera and lighting match within families; each family is framed independently, so card size is not world size.

These checks exercise the whole-model importer and renderer, not combat gameplay, collision, cover, destruction or the MagicaVoxel GUI. All trees exceed the 16-cubed PieceKind contract in height. Widths remain below the loose-model X limit of 62, but that separate runtime path is untested. VoxelXCOM was not changed. Integration is separate and must not automatically create cell files.

## Reproduce and continue

From the workspace root:

```powershell
python output/poke_l/generate.py
$pokeLFiles = (Get-ChildItem -LiteralPath output/poke_l -Filter *.vox -File).FullName
python tools/inspect_vox.py $pokeLFiles --output output/poke_l/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_l/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_l/compose_previews.py
python output/poke_l/validate.py
```

Automated rendering launches hidden and captures qa/render.log and qa/render-errors.log. Python generation uses the standard library; preview composition uses Pillow. The local generator, sculptor and VOX helpers have no runtime dependencies on other image folders. The source image, source-region JSON and shared pinned palette are dependencies.

The generator owns its 21 named outputs and manifest. It refuses unknown or changed existing files unless `--replace-generated` is deliberately passed; preserve hand edits before that override. After revisions, regenerate, audit, render, compose and visually review the outputs before updating the review record. Save additional poke_l assets directly here with distinct filenames.


## Rocks (2026-10-28)

[6 rock appearances, 42 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.

- [Flowers, bushes and grass](vegetation/README.md): 2 new appearances, 14 complete models, and existing-family reuse links.

## Terrain (2026-11-04)

- [1 terrain style, 56 complete models](terrain/README.md): `PokeL_TerraceBlock_H2 (2 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
