# pixelwood_b voxel families

Created 2026-10-28: **28 complete VOX files**, four appearances with Base and all six established treatments. All models are directly in this image folder; no cell files or brush packages.

[Overview](overview.png) | [Model catalogue](FILES.md) | [Source crops](reference/catalogue.png) | [Manifest](manifest.json)

## Source interpretation and scale

Source: [pixelwood_b.gif](../../pixelwood_b.gif). The three pixelwood references share an art set. Process in order A, B, C; store a repeated family only in the first folder and link later appearances to it. [Collection index](../PIXELWOOD.md) records ownership and duplicates.

B adds triangular, tiered conifers in green and olive, and white-barked tiered trees in lime and olive. WhiteBark is a visual label, not a verified botanical identification. The round broadleaf trees, square shrub and stump repeat A and are linked through [duplicate records](duplicates.json) and [duplicate crop sheet](reference/duplicates.png).

The 1210-square GIF enlarges its original art pixels fivefold. About 80 displayed pixels form a tile. Conifer sprites are about 40 x 48 original pixels; white-barked trees about 32 x 56. The GIF has five frames. All four modeled tree crop regions are byte-identical across those frames ([animation check](reference/animation-review.json)); frame 0 is the modeling authority. Sampled full frames 0, 2 and 4 were inspected. No animated tree variants are required.

Square canopy depth and hidden structure are inferred; sprite height includes projected depth. Dimensions are authoring estimates at 16 voxels per tile, not recovered original 3D measurements. Crop boxes are top-left XY with exclusive right/bottom edges and include context.

| Base | Canvas XYZ | Occupied XYZ | Treatments |
| --- | --- | --- | --- |
| [PixelwoodB_ConiferGreen](PixelwoodB_ConiferGreen.vox) | 40 x 40 x 48 | 39 x 39 x 48 | [Comparison](previews/PixelwoodB_ConiferGreen_family.png) |
| [PixelwoodB_ConiferOlive](PixelwoodB_ConiferOlive.vox) | 40 x 40 x 48 | 39 x 39 x 48 | [Comparison](previews/PixelwoodB_ConiferOlive_family.png) |
| [PixelwoodB_WhiteBarkLime](PixelwoodB_WhiteBarkLime.vox) | 32 x 32 x 56 | 31 x 30 x 56 | [Comparison](previews/PixelwoodB_WhiteBarkLime_family.png) |
| [PixelwoodB_WhiteBarkOlive](PixelwoodB_WhiteBarkOlive.vox) | 32 x 32 x 56 | 31 x 30 x 56 | [Comparison](previews/PixelwoodB_WhiteBarkOlive_family.png) |

## Geometry and style contracts

Round trees use a broad, nearly flat crown with chunky hanging leaf clusters, a short trunk and roots. The shrub uses four raised leaf lobes over a squared lower body. Conifers have three triangular overlapping whorls and an enclosed upper stem. White-barked trees have three rounded leafy tiers, dark bark markings and pale branch-end knots. Stumps have a flared bark base and a distinct cut face. Shapes are filled and face-connected, with classified hidden stems.

Cartoon simplifies repeated clusters, balances the geometry and paint under exact horizontal quarter turns, and uses cleaner broad paint regions. The square shrub's naturally balanced Base is retained; Cartoon regularizes its lobe heights. No family has a required front. Models stand at local z=0, are horizontally canvas-centered and use scene translation `0 0 floor(height/2)`, Z-up and voxel scale 0.0625.

Every family includes Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. See the [shared specification](../../knowledge/VARIATIONS.md). Recolors retain the exact Base or Cartoon coordinate set. Source indices 1-6 classify foliage and hidden crown cores; 7-9 classify wood, roots, stems and branches. **For stumps only, group 1 is cut end grain and group 2 is bark/internal wood.** The internal helper calls group 1 `foliage`; this is a numeric group label for stumps, not green paint. Pale birch markings and branch ends all remain wood.

TwoColor occupies exactly two distinct colors, one per group. Birch keeps pale wood; stump keeps cut wood versus darker bark. Flat paint still receives lighting in previews. CratePalette copies the entire pinned [crate RGBA palette](../../knowledge/palettes/crate-palette.json): foliage maps to slots 241-246, ordinary wood to 178-180, white bark to 193-196/248, and stump cut wood to 178-183. Nearest RGB selection is constrained to those semantic ranges; distinct two-color representatives are enforced. Both crate/two-color mixtures reuse the same choices. Index 255 is never occupied. Exact mappings, representatives, hashes, bounds and source geometry are in the manifest.

## Validation and integration limits

[Structural audit](structural-audit.json) covers all 28 files. [Godot report](godot-validation.json) records whole Mesh import/render at 0.0625 using a local copy of the current VCOM importer, with retained voxel counts and grounded bounds. Its license is retained and [source hashes](qa/source-provenance.json) record provenance. [Final validation](validation-summary.json) records final output hashes and visual review.

[Style sheet](previews/contact_01.png) includes every treatment. [Geometry sheet](previews/geometry_01.png) shows four azimuths for Base and Cartoon. Lighting and camera match within each family; cards for different families are framed independently. Generation and validate.py check serialization, connectedness, exact recolor geometry, C4 geometry/paint, semantic two-color reduction, palette identity, hashes and render evidence.

This does not test gameplay, collision, cover, destruction, or MagicaVoxel GUI behavior. Trees and the 20-wide stump exceed the single-cell 16-cubed PieceKind contract. The shrub fits that canvas but still needs registration and gameplay decisions. All occupied widths fit below the separate loose-model 62-voxel X limit; that runtime path was not exercised. VoxelXCOM was not modified. Resolve game integration separately without automatically producing cell files.

## Reproduction and future work

```powershell
python output/pixelwood_b/generate.py
$pixelFiles = (Get-Content output/pixelwood_b/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { Join-Path 'output/pixelwood_b' $_ }
python tools/inspect_vox.py $pixelFiles --output output/pixelwood_b/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/pixelwood_b/qa --script res://preview.gd --rendering-method gl_compatibility
python output/pixelwood_b/compose_previews.py
python output/pixelwood_b/validate.py
```

Automated renderer runs launch hidden with qa/render.log and qa/render-errors.log. Generation uses standard Python and deterministic mathematics; preview assembly uses Pillow. Local generate.py, sculpt.py, voxlib.py, source image, crop regions and pinned palette are dependencies. Each generator owns only its 28 named models and manifest. Unknown or modified models are protected unless `--replace-generated` is explicitly supplied for a deliberate revision; preserve hand edits before overriding. Refresh audits, renders and visual review after changes. Keep future models here and consult collection duplicate records first.


## Building assets

- [Timber house: seven complete variations](house/README.md), 80-cubed canvas, hollow interior and source-faithful asymmetric facade. [Comparison](house/comparison.png). Added 2026-10-28; tree records above remain separate.


## Lights (2026-10-28)

[PixelwoodB_Campfire](lights/README.md): seven complete variations with Emit materials, source notes, day/night previews and runtime validation.


## Rocks (2026-10-28)

[4 rock appearances, 28 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.

- [Flowers, bushes and grass](vegetation/README.md): 0 new appearances, 0 complete models, and existing-family reuse links.

## Terrain (2026-11-04)

- [1 terrain style, 49 complete models](terrain/README.md): `PixelwoodB_SlateLedge_H1 (1 level)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
