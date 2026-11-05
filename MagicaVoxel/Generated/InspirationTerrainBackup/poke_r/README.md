# poke_r forest trees and round shrub

Created 2026-10-27: **28 complete VOX files**, four forms with Base and all six established variations. Complete models only; no per-cell files or brush packages.

[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Source and scale

[poke_r.png](../../poke_r.png) is an 896 x 640 pixel-art map on a 16-pixel tile grid. Approximately one source pixel corresponds to one voxel. Four forms are included: a rounded olive tree with nested crown tiers, a broad conifer with pointed overlapping whorls, a small pale-tipped sapling and round planted shrubs beside buildings. Repeated/overlapping copies are not new types; the shrubs shaded by buildings use the same form. Crops, flowers, grasses, architecture, terrain and ground shadows are excluded.

The olive tree is 32 x 32 x 40, conifer 48 x 48 x 48, sapling 16 x 16 x 28, and shrub 16 cubed. Square depth and hidden structure are inferred. Top-down projection mixes canopy depth with height, so these are relative authoring estimates. Source crop boxes use top-left XY and exclusive right/bottom edges, include contextual neighbors, and are not segmentation masks. The shrub crop shows repeated placements of the same form.

All models are Z-up, grounded at z=0, horizontally canvas-centered, and use scene translation `0 0 floor(height/2)`, with no required facing direction.

| Base model | Canvas XYZ | Base occupied XYZ | Comparison |
| --- | --- | --- | --- |
| [PokeR_OliveTieredTree](PokeR_OliveTieredTree.vox) | 32 x 32 x 40 | 32 x 32 x 40 | [All styles](previews/PokeR_OliveTieredTree_family.png) |
| [PokeR_BroadConifer](PokeR_BroadConifer.vox) | 48 x 48 x 48 | 43 x 43 x 48 | [All styles](previews/PokeR_BroadConifer_family.png) |
| [PokeR_SmallSapling](PokeR_SmallSapling.vox) | 16 x 16 x 28 | 16 x 15 x 28 | [All styles](previews/PokeR_SmallSapling_family.png) |
| [PokeR_RoundShrub](PokeR_RoundShrub.vox) | 16 x 16 x 16 | 16 x 16 x 16 | [All styles](previews/PokeR_RoundShrub_family.png) |

## Modeling and variations

OliveTieredTree has broad lower shoulders, narrower upper tiers and coherent olive paint bands. BroadConifer uses three overlapping pointed whorls, a small top leader and cooler gray-green foliage. SmallSapling raises a compact crown above a short exposed stem, with a lighter crown tip. RoundShrub has a low rounded crown, small inferred woody base and internal stem. All geometry is filled and connected. Source ground shadows and building shadows are not baked into the model.

The local sculptor adapts established crown recipes with a revised tiered olive profile. Base has restrained irregularity; Cartoon balances silhouette and painted regions under exact horizontal quarter turns. The code has no runtime dependency on other image folders.

Follow the [shared variation specification](../../knowledge/VARIATIONS.md) for Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Each recolor preserves every occupied coordinate, dimension and scene placement of its designated Base or Cartoon authority.

Explicit coordinate groups separate foliage/crown core from wood/trunk/roots/internal stems. Every TwoColor model occupies exactly two palette indices with distinct RGBA colors, one per group. Lit previews still shade both colors. CratePalette copies the entire pinned [crate palette](../../knowledge/palettes/crate-palette.json), maps foliage to green slots 241-246 and wood to crate browns 178-180, and never uses voxel index 255. This changes the source's muted olive and gray-green hues to the available game greens. Both crate/two-color mixtures reuse the same selected group colors within each family. Manifest records contain exact mappings, representative colors, bounds, counts, hashes and geometry sources.

## Validation and integration

[Structural audit](structural-audit.json) covers all 28 delivered files. Generation rereads serialized data and checks dimensions, bounds, connectedness, recolor coordinate equality, C4 occupancy/paint, reference palette identity and two-color counts. [Godot report](godot-validation.json) records whole Mesh imports at scale 0.0625 with retained voxel counts and grounded bounds, using the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final verification and visual review.

[Contact sheet](previews/contact_01.png) covers all treatments. [Geometry sheet](previews/geometry_01.png) shows Base and Cartoon from four azimuths. Camera and lighting match within families; different families are framed independently, so card size is not world scale.

These checks exercise the whole-model importer/render path, not gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. The trees and sapling exceed the 16-cubed PieceKind contract; the shrub fits that canvas but still needs explicit integration settings and registration. Widths are below the loose-model X limit of 62, but that separate runtime path is untested. VoxelXCOM remains unchanged. Integration is separate and must not automatically generate cell files.

## Reproduction and continuation

From the workspace root:

```powershell
python output/poke_r/generate.py
$pokeRFiles = (Get-ChildItem -LiteralPath output/poke_r -Filter *.vox -File).FullName
python tools/inspect_vox.py $pokeRFiles --output output/poke_r/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_r/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_r/compose_previews.py
python output/poke_r/validate.py
```

Automated renders launch hidden and capture qa/render.log and qa/render-errors.log. Generation uses standard Python; composition uses Pillow. Local generate.py, sculpt.py, voxlib.py, the source image/regions and pinned palette are dependencies. The generator owns only its 28 named files and manifest. It refuses unknown or changed files unless `--replace-generated` is deliberately supplied; preserve hand edits before that override. After revisions, refresh audits, renders, comparisons and visual-review records. Keep future poke_r models directly here with distinct filenames.

- [Flowers, bushes and grass](vegetation/README.md): 3 new appearances, 21 complete models, and existing-family reuse links.

## Buildings (2026-11-03)

- [Two buildings, 14 complete models](buildings/README.md): `PokeR_RedHouse` (the red house, four copies) and `PokeR_Shop` (the flat-roofed shop with its red rooftop housing), each in Base and all six variations, made on VCOM's tile grid at game scale (closed doors, MagicaVoxel Glass windows) as the poke_o buildings are, and tested in a copy of the game. [Overview](buildings/overview.png) | [File index](buildings/FILES.md).


## Outdoor stairs — 2026-11-03

Added 1 families / 7 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [2 terrain styles, 98 complete models](terrain/README.md): `PokeR_EarthCliff_H3 (3 levels)`, `PokeR_RaisedBed_H1 (1 level)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
