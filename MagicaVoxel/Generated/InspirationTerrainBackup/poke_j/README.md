# poke_j trees and hedge shrub

Created 2026-10-27: **21 complete VOX files**, three appearances with Base and all six established variations. Complete models only; no per-cell files or brush packages.

[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Source interpretation and scale

The requested poke_j.png is present as [poke_j.jpg](../../poke_j.jpg), a 735 x 565 JPEG. The original is preserved. Forest placements repeat about every 24 image pixels, consistent with a resized tile map. Approximately 24 displayed pixels are interpreted as one tile, retaining 16 voxels per tile. This scale is inferred rather than verified against an original tileset.

The source contains a repeated lime-green forest tree and a distinct desaturated blue-gray colorway of the same pointed, round-bodied crown. These receive separate families while sharing geometry. A low rounded shrub is included as a third woody appearance. Repeated copies, occluded crowns and JPEG artifacts do not create additional types. Pale-topped brown objects beside trees appear to be separate small props/stumps, not attached fruit or blossoms, and are excluded along with rocks, flowers, water plants, buildings and characters. No distinct sapling type was identified.

Both tree colorways use 16 x 16 x 28 canvases, approximately one tile wide and 1.75 tiles tall; the shrub uses 12 x 12 x 8. The visible sprites are roughly 24-28 pixels wide and 40-44 tall, with shrubs around 18-24 wide and 12 high. These are approximate extents in compressed artwork. Square crown depth and hidden structure are inferred. Source projection mixes canopy depth with vertical height, so these sizes preserve relative proportions rather than recovering exact physical dimensions. Crop boxes include contextual neighbors and use top-left XY with exclusive right/bottom edges.

| Base model | Canvas XYZ | Occupied XYZ | Comparison |
| --- | --- | --- | --- |
| [PokeJ_LimeForestTree](PokeJ_LimeForestTree.vox) | 16 x 16 x 28 | 16 x 16 x 28 | [All styles](previews/PokeJ_LimeForestTree_family.png) |
| [PokeJ_SlateForestTree](PokeJ_SlateForestTree.vox) | 16 x 16 x 28 | 16 x 16 x 28 | [All styles](previews/PokeJ_SlateForestTree_family.png) |
| [PokeJ_RoundedShrub](PokeJ_RoundedShrub.vox) | 12 x 12 x 8 | 12 x 12 x 8 | [All styles](previews/PokeJ_RoundedShrub_family.png) |

## Geometry, colors and variations

Models are filled 3D forms with continuous wood, rooted at z=0, Z-up and centered horizontally on their canvas. Scene translation is `0 0 floor(height/2)`. Trees have a broad, rounded lower crown and pointed upper canopy with restrained lobes and clustered leaf paint. Their silhouette is fuller and less tiered than poke_i. The shrub is a low dome with a small woody base. Base has restrained asymmetry; Cartoon simplifies paint into coherent bands and balances geometry and paint under exact horizontal quarter turns.

The local sculptor adapts established construction with new roundforest and roundshrub profiles. It has no runtime dependency on other image folders. Source-guided foliage ranges from dark green to lime for the bright tree, muted blue-green/slate for the alternate tree, and warmer green for the shrub. JPEG artifacts are not treated as intentional leaf texture. The slate and lime trees share coordinates to preserve their common source shape; their source-colored treatments remain distinct.

Follow the [shared variation specification](../../knowledge/VARIATIONS.md). Each family includes Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Recolors preserve the exact Base or Cartoon coordinate set. Cartoon changes geometry deliberately while retaining dimensions and identity.

Explicit semantic groups assign foliage to leaves and wood to roots, trunk and hidden core. TwoColor uses exactly two occupied indices with distinct RGBA values, one per group; rendered lighting still shades faces. The low shrub retains a small woody base and internal stem. CratePalette copies the entire pinned [crate palette](../../knowledge/palettes/crate-palette.json). Lime and shrub foliage map to green slots 241-246; slate foliage maps to existing blue-gray/neutral slots 204, 205, 206 and 193, preserving its distinct color identity. Bark maps to 178-180. No model occupies index 255. The two crate/two-color mixtures share the same two selected game colors. Manifest records include exact mappings, palette hashes, bounds, counts and geometry-source hashes.

## Validation and integration

[Structural audit](structural-audit.json) covers 21 delivered VOX files. The generator rereads every output and checks dimensions, bounds, connectivity, exact recolor coordinates, C4 symmetry, full reference palette identity and two-color counts. [Godot report](godot-validation.json) records whole Mesh imports at scale 0.0625, voxel preservation and grounded bounds. QA uses a copy of the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final checks and visual review.

[All-style sheet](previews/contact_01.png) shows every treatment; [four-view sheet](previews/geometry_01.png) shows Base and Cartoon from four azimuths. Camera and lighting match within each family; cards for different families are framed independently and do not indicate equal world size.

This validates structural correctness and whole-model import/rendering, not combat gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. Both mature tree colorways exceed the 16-cubed PieceKind contract in height. Smaller canvases also require an explicit integration decision rather than assuming compatibility from their dimensions. All widths are below the loose-model limit of 62 voxels; that runtime path was not tested. VoxelXCOM remains unchanged. Integration must not automatically generate per-cell assets.

## Reproduction and continuation

From the workspace root:

```powershell
python output/poke_j/generate.py
$pokeJFiles = (Get-ChildItem -LiteralPath output/poke_j -Filter *.vox -File).FullName
python tools/inspect_vox.py $pokeJFiles --output output/poke_j/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_j/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_j/compose_previews.py
python output/poke_j/validate.py
```

Rendering may be launched hidden with stdout/stderr redirected to qa/render.log and qa/render-errors.log. Python generation uses the standard library; preview composition uses Pillow. After geometry changes, regenerate, audit, render, compose and visually review the sheets before updating the review record. Validation does not substitute for visual review.

The generator owns only its 21 named outputs and manifest. It refuses existing unknown or changed files unless `--replace-generated` is deliberately passed; preserve hand edits before any override. Keep future assets from this image directly in this folder with distinct filenames. Local generators, source regions, pinned palette, audits and previews preserve all decisions for future sessions.


## Lights (2026-10-28)

[PokeJ_DarkStreetLantern](lights/README.md): seven complete variations with Emit materials, source notes, day/night previews and runtime validation.

- [Flowers, bushes and grass](vegetation/README.md): 3 new appearances, 21 complete models, and existing-family reuse links.

## Buildings (2026-10-29)

- [Two buildings, 14 complete models](buildings/README.md): `PokeJ_RedHouse` (three copies in the art) and `PokeJ_GreyHouse` (the grey-roofed building, three parts stepped front to back), each in Base and all six variations, made on VCOM's tile grid at game scale (closed doors, MagicaVoxel Glass windows) as the poke_i buildings are, measured from the scaled JPEG at 12.25 pixels a tile, and tested in a copy of the game. [Overview](buildings/overview.png) | [File index](buildings/FILES.md).


## Outdoor stairs — 2026-11-03

Added 1 families / 7 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [2 terrain styles, 98 complete models](terrain/README.md): `PokeJ_EarthCliff_H3 (3 levels)`, `PokeJ_PondBank_H3 (3 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
