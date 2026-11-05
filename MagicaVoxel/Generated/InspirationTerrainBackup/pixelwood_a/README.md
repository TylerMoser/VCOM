# pixelwood_a voxel families

Created 2026-10-28: **28 complete VOX files**, four appearances with Base and all six established treatments. All models are directly in this image folder; no cell files or brush packages.

[Overview](overview.png) | [Model catalogue](FILES.md) | [Source crops](reference/catalogue.png) | [Manifest](manifest.json)

## Source interpretation and scale

Source: [pixelwood_a.jpg](../../pixelwood_a.jpg). The three pixelwood references share an art set. Process in order A, B, C; store a repeated family only in the first folder and link later appearances to it. [Collection index](../PIXELWOOD.md) records ownership and duplicates.

A supplies a squat round broadleaf crown in lime and muted olive, a small four-lobed square shrub, and a cut stump. Both round-tree colorways are retained because the same complete palette treatments recur across placements and images; dark undersides within each tree are shading, not extra families. Stumps are included as tree remnants. Fallen logs, grass, mushrooms, flowers, terrain and architecture are outside this tree exercise.

The 720-square JPEG is enlarged approximately three times from its underlying pixel art. A 48-pixel displayed tile is treated as 16 voxels. Round sprites span about 144 displayed pixels, giving 48-voxel crowns. Small shrubs span roughly one tile; stumps span about 20 original pixels including roots. Compression and projection make these estimates approximate.

Square canopy depth and hidden structure are inferred; sprite height includes projected depth. Dimensions are authoring estimates at 16 voxels per tile, not recovered original 3D measurements. Crop boxes are top-left XY with exclusive right/bottom edges and include context.

| Base | Canvas XYZ | Occupied XYZ | Treatments |
| --- | --- | --- | --- |
| [PixelwoodA_RoundLime](PixelwoodA_RoundLime.vox) | 48 x 48 x 48 | 46 x 46 x 48 | [Comparison](previews/PixelwoodA_RoundLime_family.png) |
| [PixelwoodA_RoundOlive](PixelwoodA_RoundOlive.vox) | 48 x 48 x 48 | 46 x 46 x 48 | [Comparison](previews/PixelwoodA_RoundOlive_family.png) |
| [PixelwoodA_SquareShrub](PixelwoodA_SquareShrub.vox) | 16 x 16 x 16 | 14 x 14 x 16 | [Comparison](previews/PixelwoodA_SquareShrub_family.png) |
| [PixelwoodA_Stump](PixelwoodA_Stump.vox) | 20 x 20 x 16 | 20 x 19 x 16 | [Comparison](previews/PixelwoodA_Stump_family.png) |

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
python output/pixelwood_a/generate.py
$pixelFiles = (Get-Content output/pixelwood_a/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { Join-Path 'output/pixelwood_a' $_ }
python tools/inspect_vox.py $pixelFiles --output output/pixelwood_a/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/pixelwood_a/qa --script res://preview.gd --rendering-method gl_compatibility
python output/pixelwood_a/compose_previews.py
python output/pixelwood_a/validate.py
```

Automated renderer runs launch hidden with qa/render.log and qa/render-errors.log. Generation uses standard Python and deterministic mathematics; preview assembly uses Pillow. Local generate.py, sculpt.py, voxlib.py, source image, crop regions and pinned palette are dependencies. Each generator owns only its 28 named models and manifest. Unknown or modified models are protected unless `--replace-generated` is explicitly supplied for a deliberate revision; preserve hand edits before overriding. Refresh audits, renders and visual review after changes. Keep future models here and consult collection duplicate records first.


## Building assets

- [Ridge tent: seven complete variations](tent/README.md), 64 x 64 x 32 canvas, hollow interior and actual entrance/vents. [Comparison](tent/comparison.png). Added 2026-10-28; tree records above remain separate.


## Lights (2026-10-28)

[PixelwoodA_PostLantern](lights/README.md): seven complete variations with Emit materials, source notes, day/night previews and runtime validation.


## Rocks (2026-10-28)

[4 rock appearances, 28 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.

- [Flowers, bushes and grass](vegetation/README.md): 3 new appearances, 21 complete models, and existing-family reuse links.

## Terrain (2026-11-04)

- [1 terrain style, 49 complete models](terrain/README.md): `PixelwoodA_EarthBank_H2 (2 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
