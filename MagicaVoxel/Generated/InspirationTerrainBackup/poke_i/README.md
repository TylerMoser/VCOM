# poke_i trees and hedge shrub



Created 2026-10-27: **21 complete VOX files**, three appearances with Base and all six established variations. Complete models only; no per-cell files or brush packages.



[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)



## Source interpretation and scale



The requested poke_i.png is present as [poke_i.jpg](../../poke_i.jpg), a 736 x 559 JPEG. That original is preserved. Repeated forest placements are roughly 19-20 image pixels apart, consistent with a resized tile map. We interpret approximately 19.3 displayed pixels as one tile and retain 16 voxels per tile, rather than assuming one JPEG pixel equals one voxel. This inferred scale is approximate; there is no original unscaled map or tileset to verify it against.



There is one repeated mature forest tree: a pointed top, overlapping scalloped shoulders, dark teal-green lower foliage and a short brown trunk. Three narrow planted saplings beside the left fence repeat a second type. Low rounded hedge shrubs near paths and fences are included as a third woody form. Overlapping trees, shadowed copies and JPEG artifacts are not separate species. Crops, flowers, rocks, buildings and characters are excluded.



The mature tree uses a 16 x 16 x 28 canvas, the sapling 8 x 8 x 16 and the hedge shrub 8 x 8 x 6. Square depth and hidden structure are inferred. Source projection mixes canopy depth with vertical height, so these dimensions preserve relative sprite proportions rather than claiming exact physical recovery. Source crop boxes include contextual neighbors and use top-left XY with exclusive right/bottom edges.



| Base model | Canvas XYZ | Occupied XYZ | Comparison |

| --- | --- | --- | --- |

| [PokeI_ForestTree](PokeI_ForestTree.vox) | 16 x 16 x 28 | 15 x 14 x 28 | [All styles](previews/PokeI_ForestTree_family.png) |

| [PokeI_Sapling](PokeI_Sapling.vox) | 8 x 8 x 16 | 7 x 7 x 16 | [All styles](previews/PokeI_Sapling_family.png) |

| [PokeI_HedgeShrub](PokeI_HedgeShrub.vox) | 8 x 8 x 6 | 6 x 6 x 6 | [All styles](previews/PokeI_HedgeShrub_family.png) |



## Geometry, colors and variations



Models are filled 3D forms with continuous wood, rooted at z=0, Z-up and centered horizontally on their canvas. Scene translation is `0 0 floor(height/2)`. The forest tree has three subtle overlapping shoulders rather than wide isolated pine tiers; the sapling has a slender tapered crown; the shrub is a low round mass. Base uses restrained asymmetric silhouette and leaf clusters. Cartoon uses the same family profile with exact horizontal quarter-turn symmetry in occupancy and paint, cleaner color bands and balanced outlines.



The local sculptor adapts the established tree construction with new forest, slender and hedge profiles. It has no runtime dependency on another image folder. Source-guided greens range from dark teal to muted yellow-green; the hedge is warmer. JPEG compression is not reproduced as voxel noise. Bark uses three restrained browns.



Follow the [shared variation specification](../../knowledge/VARIATIONS.md). Each family includes Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Recolors preserve the exact Base or Cartoon coordinate set. Cartoon changes geometry deliberately while retaining dimensions and identity.



Explicit semantic groups assign foliage to leaves and wood to roots, trunk and hidden core. TwoColor uses exactly two occupied indices with distinct RGBA values, one per group; rendered lighting still shades faces. The low shrub retains a small woody base and internal stem. CratePalette copies the entire pinned [crate palette](../../knowledge/palettes/crate-palette.json), maps foliage to 241-246 and bark to 178-180, and never occupies index 255. The two crate/two-color mixtures share the same two selected game colors. Manifest records include exact mappings, palette hashes, bounds, counts and geometry-source hashes.



## Validation and integration



[Structural audit](structural-audit.json) covers 21 delivered VOX files. The generator rereads every output and checks dimensions, bounds, connectivity, exact recolor coordinates, C4 symmetry, full reference palette identity and two-color counts. [Godot report](godot-validation.json) records whole Mesh imports at scale 0.0625, voxel preservation and grounded bounds. QA uses a copy of the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final checks and visual review.



[All-style sheet](previews/contact_01.png) shows every treatment; [four-view sheet](previews/geometry_01.png) shows Base and Cartoon from four azimuths. Camera and lighting match within each family; cards for different families are framed independently and do not indicate equal world size.



This validates structural correctness and whole-model import/rendering, not combat gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. The mature tree exceeds the 16-cubed PieceKind contract in height. Smaller canvases also require an explicit integration decision rather than assuming compatibility from their dimensions. All widths are below the loose-model limit of 62 voxels; that runtime path was not tested. VoxelXCOM remains unchanged. Integration must not automatically generate per-cell assets.



## Reproduction and continuation



From the workspace root:



```powershell

python output/poke_i/generate.py

$pokeIFiles = (Get-ChildItem -LiteralPath output/poke_i -Filter *.vox -File).FullName

python tools/inspect_vox.py $pokeIFiles --output output/poke_i/structural-audit.json

& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_i/qa --script res://preview.gd --rendering-method gl_compatibility

python output/poke_i/compose_previews.py

python output/poke_i/validate.py

```



Rendering may be launched hidden with stdout/stderr redirected to qa/render.log and qa/render-errors.log. Python generation uses the standard library; preview composition uses Pillow. After geometry changes, regenerate, audit, render, compose and visually review the sheets before updating the review record. Validation does not substitute for visual review.



The generator owns only its 21 named outputs and manifest. It refuses existing unknown or changed files unless `--replace-generated` is deliberately passed; preserve hand edits before any override. Keep future assets from this image directly in this folder with distinct filenames. Local generators, source regions, pinned palette, audits and previews preserve all decisions for future sessions.





## Rocks (2026-10-28)



[3 rock appearances, 21 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.



- [Flowers, bushes and grass](vegetation/README.md): 6 new appearances, 42 complete models, and existing-family reuse links.



## Buildings (2026-10-29)



- [Three buildings, 21 complete models](buildings/README.md): `PokeI_SmallHouse` (three copies in the art), `PokeI_ChimneyHouse` (two copies) and `PokeI_DayCare` (a clerestory hall and its wing), each in Base and all six variations, made on VCOM's tile grid at game scale (closed doors, MagicaVoxel Glass windows) as the poke_g buildings are, measured from the scaled JPEG at 9.5 pixels a tile, and tested in a copy of the game. [Overview](buildings/overview.png) | [File index](buildings/FILES.md).

## Complete bridges (2026-11-03)

[Bridge collection for this image](bridges/README.md): 3 new families, 21 complete VOX files with all seven treatments, source crops, cardinal/underside views and bank-placement previews. Existing assets are preserved. Shared validation and generation: [complete bridges](../bridges/README.md).


## Outdoor stairs — 2026-11-03

Added 1 families / 7 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [1 terrain style, 56 complete models](terrain/README.md): `PokeI_EarthCliff_H3 (3 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
