# poke_k trees and hedge shrub

Created 2026-10-27: **21 complete VOX files**, three appearances with Base and all six established variations. Complete models only; no per-cell files or brush packages.

[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Source interpretation and scale

The requested poke_k.png is present as [poke_k.jpg](../../poke_k.jpg), a 736 x 736 JPEG. The original is preserved. Forest placements repeat about every 29-30 image pixels, consistent with a resized tile map. Approximately 29.4 displayed pixels are interpreted as one tile, retaining 16 voxels per tile. This scale is inferred rather than verified against an original tileset.

The source contains a repeated lime-green forest tree and a distinct desaturated blue-gray colorway of the same pointed, round-bodied crown. These receive separate families while sharing geometry. A low rounded shrub is included as a third woody appearance. Repeated copies, occluded crowns and JPEG artifacts do not create additional types. Pale-topped brown objects beside trees appear to be separate small props/stumps, not attached fruit or blossoms, and are excluded along with flowers, water plants, tall grass, bridges and terrain. No distinct sapling type was identified.

Both tree colorways use 16 x 16 x 28 canvases, approximately one tile wide and 1.75 tiles tall; the shrub uses 12 x 12 x 8. The visible sprites are roughly 30-36 pixels wide and 48-52 tall, with shrubs around 26-32 wide and 16-20 high. These are approximate extents in compressed artwork. Square crown depth and hidden structure are inferred. Source projection mixes canopy depth with vertical height, so these sizes preserve relative proportions rather than recovering exact physical dimensions. Crop boxes include contextual neighbors and use top-left XY with exclusive right/bottom edges.

| Base model | Canvas XYZ | Occupied XYZ | Comparison |
| --- | --- | --- | --- |
| [PokeK_LimeForestTree](PokeK_LimeForestTree.vox) | 16 x 16 x 28 | 16 x 16 x 28 | [All styles](previews/PokeK_LimeForestTree_family.png) |
| [PokeK_SlateForestTree](PokeK_SlateForestTree.vox) | 16 x 16 x 28 | 16 x 16 x 28 | [All styles](previews/PokeK_SlateForestTree_family.png) |
| [PokeK_RoundedShrub](PokeK_RoundedShrub.vox) | 12 x 12 x 8 | 12 x 12 x 8 | [All styles](previews/PokeK_RoundedShrub_family.png) |

## Geometry, colors and variations

Models are filled 3D forms with continuous wood, rooted at z=0, Z-up and centered horizontally on their canvas. Scene translation is `0 0 floor(height/2)`. Trees have a broad, rounded lower crown and pointed upper canopy with restrained lobes and clustered leaf paint. Their silhouette is fuller and less tiered than poke_i. The shrub is a low dome with a small woody base. Base has restrained asymmetry; Cartoon simplifies paint into coherent bands and balances geometry and paint under exact horizontal quarter turns.

The source repeats the same tree/shrub artwork seen in poke_j at a different image scale. Accordingly, this family deliberately reuses the verified poke_j roundforest and roundshrub geometry and palette treatment, with independent local generators, source regions and named outputs. It does not invent shape differences for repeated source artwork. It has no runtime dependency on other image folders. Source-guided foliage ranges from dark green to lime for the bright tree, muted blue-green/slate for the alternate tree, and warmer green for the shrub. JPEG artifacts are not treated as intentional leaf texture. The slate and lime trees share coordinates to preserve their common source shape; their source-colored treatments remain distinct.

Follow the [shared variation specification](../../knowledge/VARIATIONS.md). Each family includes Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Recolors preserve the exact Base or Cartoon coordinate set. Cartoon changes geometry deliberately while retaining dimensions and identity.

Explicit semantic groups assign foliage to leaves and wood to roots, trunk and hidden core. TwoColor uses exactly two occupied indices with distinct RGBA values, one per group; rendered lighting still shades faces. The low shrub retains a small woody base and internal stem. CratePalette copies the entire pinned [crate palette](../../knowledge/palettes/crate-palette.json). Lime and shrub foliage map to green slots 241-246; slate foliage maps to existing blue-gray/neutral slots 204, 205, 206 and 193, preserving its distinct color identity. Bark maps to 178-180. No model occupies index 255. The two crate/two-color mixtures share the same two selected game colors. Manifest records include exact mappings, palette hashes, bounds, counts and geometry-source hashes.

## Validation and integration

[Structural audit](structural-audit.json) covers 21 delivered VOX files. The generator rereads every output and checks dimensions, bounds, connectivity, exact recolor coordinates, C4 symmetry, full reference palette identity and two-color counts. [Godot report](godot-validation.json) records whole Mesh imports at scale 0.0625, voxel preservation and grounded bounds. QA uses a copy of the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final checks and visual review.

[All-style sheet](previews/contact_01.png) shows every treatment; [four-view sheet](previews/geometry_01.png) shows Base and Cartoon from four azimuths. Camera and lighting match within each family; cards for different families are framed independently and do not indicate equal world size.

This validates structural correctness and whole-model import/rendering, not combat gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. Both mature tree colorways exceed the 16-cubed PieceKind contract in height. Smaller canvases also require an explicit integration decision rather than assuming compatibility from their dimensions. All widths are below the loose-model limit of 62 voxels; that runtime path was not tested. VoxelXCOM remains unchanged. Integration must not automatically generate per-cell assets.

## Reproduction and continuation

From the workspace root:

```powershell
python output/poke_k/generate.py
$pokeKFiles = (Get-ChildItem -LiteralPath output/poke_k -Filter *.vox -File).FullName
python tools/inspect_vox.py $pokeKFiles --output output/poke_k/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_k/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_k/compose_previews.py
python output/poke_k/validate.py
```

Rendering may be launched hidden with stdout/stderr redirected to qa/render.log and qa/render-errors.log. Python generation uses the standard library; preview composition uses Pillow. After geometry changes, regenerate, audit, render, compose and visually review the sheets before updating the review record. Validation does not substitute for visual review.

The generator owns only its 21 named outputs and manifest. It refuses existing unknown or changed files unless `--replace-generated` is deliberately passed; preserve hand edits before any override. Keep future assets from this image directly in this folder with distinct filenames. Local generators, source regions, pinned palette, audits and previews preserve all decisions for future sessions.

- [Flowers, bushes and grass](vegetation/README.md): 4 new appearances, 28 complete models, and existing-family reuse links.


## Outdoor stairs — 2026-11-03

Added 1 families / 7 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [2 terrain styles, 98 complete models](terrain/README.md): `PokeK_EarthCliff_H3 (3 levels)`, `PokeK_LakeBank_H3 (3 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
