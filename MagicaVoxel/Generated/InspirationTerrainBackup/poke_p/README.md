# poke_p teal forest trees



Created 2026-10-27: **14 complete VOX files**, two forms with Base and all six established variations. Complete models only; no cell files or brush packages.



[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)



## Source and scale



[poke_p.png](../../poke_p.png) is 960 x 1348, including a black margin below the map. The artwork uses a 16-pixel tile grid; approximately one source pixel corresponds to one voxel. The mature tree is roughly 32 pixels wide and 48 tall; the sapling is roughly 16 wide and 28 tall. Repeated stacked saplings form tall-looking columns near forest edges, but isolated examples establish that these are placements of one small sprite, not extra species. There are two unique tree forms.



TealLayeredTree uses 32 x 32 x 48 voxels; TealSapling uses 16 x 16 x 28. Canopy depth and hidden structure are inferred. Sprite projection combines height and depth, so these are relative authoring sizes, not exact physical recovery. The black margin, ground shadows, tall grass, flowers, stumps, terrain and buildings are excluded.



Source crop boxes use top-left XY and exclusive right/bottom edges; they include context and are not segmentation masks. All models are Z-up, stand at z=0, are horizontally canvas-centered, and use scene translation `0 0 floor(height/2)` with no required facing direction.



| Base model | Canvas XYZ | Base occupied XYZ | Comparison |

| --- | --- | --- | --- |

| [PokeP_TealLayeredTree](PokeP_TealLayeredTree.vox) | 32 x 32 x 48 | 30 x 30 x 48 | [All styles](previews/PokeP_TealLayeredTree_family.png) |

| [PokeP_TealSapling](PokeP_TealSapling.vox) | 16 x 16 x 28 | 15 x 14 x 28 | [All styles](previews/PokeP_TealSapling_family.png) |



## Geometry and palette



The mature tree has overlapping drooping leaf clusters around a filled crown core, with a tapered top and short woody base. The small sapling has a narrow columnar crown with subtle shoulders and a continuous internal stem. Base preserves restrained irregularity; Cartoon balances the outline, leaf arrangements and painted regions under exact horizontal quarter turns. The local sculptor adapts the established drooping leaf and column-profile construction without importing other image folders at runtime.



The source palette is saturated teal with lighter mint-green upper leaves and brown wood. Explicit coordinate groups separate all foliage and crown core from trunk, roots and internal stems. TwoColor uses exactly two occupied indices with distinct RGBA values, one per group. Lighting still shades those paint colors in renders.



The [shared variation specification](../../knowledge/VARIATIONS.md) defines Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Each recolor preserves every coordinate, dimension and scene placement of its saved Base or Cartoon authority.



CratePalette copies the full pinned [crate palette](../../knowledge/palettes/crate-palette.json). The saved palette has no close saturated teal ramp, so foliage maps to the existing cool candidates 241, 242, 205, 206, 252, 253 and 254. This deliberately allows blue-gray and cyan as well as dark green, rather than forcing the source into yellow-green. Wood maps to crate browns 178-180. The two crate/two-color mixtures share the same selected pair within each family. No occupied voxel uses index 255. Manifest records include exact mappings, representative colors, hashes, counts and geometry authorities.



## Validation and integration



[Structural audit](structural-audit.json) covers all 14 delivered files. Generation rereads outputs and checks dimensions, bounds, connectivity, exact recolor coordinates, C4 geometry/paint, pinned palette identity and two-color counts. [Godot report](godot-validation.json) records whole Mesh imports at scale 0.0625, retained voxel counts and grounded bounds using the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final evidence and visual review.



[Contact sheet](previews/contact_01.png) shows every treatment. [Geometry sheet](previews/geometry_01.png) shows four azimuths for Base and Cartoon. Camera and lighting match within each family; different families are framed independently, so card size is not world scale.



This validates structure and the whole-model import/render path, not gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. Both models exceed the 16-cubed PieceKind contract in height. Widths remain below the loose-model limit of 62, but that separate runtime path is untested. VoxelXCOM remains unchanged. Integration is separate and must not automatically create cell files.



## Reproduce and continue



From the workspace root:



```powershell

python output/poke_p/generate.py

$pokePFiles = (Get-ChildItem -LiteralPath output/poke_p -Filter *.vox -File).FullName

python tools/inspect_vox.py $pokePFiles --output output/poke_p/structural-audit.json

& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_p/qa --script res://preview.gd --rendering-method gl_compatibility

python output/poke_p/compose_previews.py

python output/poke_p/validate.py

```



Automated renders launch hidden and capture qa/render.log and qa/render-errors.log. Generation uses standard Python; composition uses Pillow. Local generate.py, sculpt.py, profiles.py, leaves.py and voxlib.py, the original image, region JSON and pinned palette are dependencies. Geometry module hashes are recorded in manifest.json.



The generator owns only its 14 named files and manifest. It refuses unknown or changed existing files unless `--replace-generated` is deliberately supplied; preserve hand edits before overriding. After revisions, refresh audits, renders, sheets and visual-review records. Keep future poke_p assets directly here with distinct names.





## Rocks (2026-10-28)



[4 rock appearances, 28 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.



- [Flowers, bushes and grass](vegetation/README.md): 12 new appearances, 84 complete models, and existing-family reuse links.

## Complete bridges (2026-11-03)

[Bridge collection for this image](bridges/README.md): 2 new families, 14 complete VOX files with all seven treatments, source crops, cardinal/underside views and bank-placement previews. Existing assets are preserved. Shared validation and generation: [complete bridges](../bridges/README.md).


## Outdoor stairs — 2026-11-03

Added 1 families / 7 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [1 terrain style, 56 complete models](terrain/README.md): `PokeP_GullyWall_H2 (2 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
