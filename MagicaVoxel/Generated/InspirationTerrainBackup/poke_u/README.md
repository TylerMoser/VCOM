# poke_u scalloped trees

Created 2026-10-27: **14 complete VOX files**, two distinct tree forms with Base and all six established variations. No individual cell files.

[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Source interpretation and dimensions

The supplied file is [poke_u.jpg](../../poke_u.jpg), a 384 x 384 JPEG, rather than poke_u.png. Repeated broad trees have pale green crown tips and overlapping scalloped leaf tiers. Narrow saplings have foliage almost down to the ground. Darkened and partially hidden copies use the same forms; building and cliff shadows are not separate palettes. Creatures, flowers, grass, buildings and terrain are excluded.

The apparent map grid is approximately 16 source pixels per tile, so the working estimate is one source pixel per voxel, with 16 voxels per game tile. Broad trees span roughly 38 x 54 image pixels; saplings roughly 12 x 32. Canvas sizes round these to 40 x 40 x 56 and 12 x 12 x 32. The oblique projection combines height and depth; square depth, hidden branches and exact height are inferred. JPEG compression makes edge measurements approximate. Reference boxes include neighboring context and are not segmentation masks.

| Model | Canvas XYZ | Base occupied XYZ | Styles |
| --- | --- | --- | --- |
| [PokeU_ScallopedTree](PokeU_ScallopedTree.vox) | 40 x 40 x 56 | 36 x 36 x 56 | [Comparison](previews/PokeU_ScallopedTree_family.png) |
| [PokeU_NarrowSapling](PokeU_NarrowSapling.vox) | 12 x 12 x 32 | 10 x 10 x 32 | [Comparison](previews/PokeU_NarrowSapling_family.png) |

## Geometry, colors and variations

Solid crown cores support overlapping ellipsoidal leaf clusters, a woody internal stem, short exposed trunk and small roots. Broad trees use five overlapping scalloped tiers. Saplings use lower foliage and a slender tapered crown. Base permits restrained leaf placement irregularity; Cartoon uses fewer, larger clusters and exact quarter-turn symmetry in both geometry and paint. There is no required front direction. All files are Z-up, horizontally centered and grounded at z=0, with scene translation `0 0 floor(height/2)`.

Each form includes Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor, following the [shared specification](../../knowledge/VARIATIONS.md). Color-only versions preserve the occupied coordinates of Base or Cartoon exactly. Foliage (including hidden canopy cores) uses indices 1-6 in the source; wood, roots and hidden stems use 7-9. TwoColor uses exactly one foliage color and one wood color, with exactly two stored RGBA values. Rendered lighting still shades these colors.

CratePalette uses the complete pinned [crate palette](../../knowledge/palettes/crate-palette.json). Source foliage maps to available greens 241-246 and wood to browns 178-180 by nearest RGB distance within those semantic ranges. Game greens are warmer than some source shadows. Both crate/two-color mixtures reuse the same selected representatives. Index 255 is never occupied. Exact mappings, chosen colors, bounds, hashes and geometry dependencies are saved in the manifest.

## Validation and integration

[Structural audit](structural-audit.json), [Godot report](godot-validation.json) and [final validation record](validation-summary.json) document serialized checks and whole-model Mesh import/rendering at scale 0.0625. Current VCOM importer source is copied locally with its license and [source hashes](qa/source-provenance.json). Count preservation and grounded bounds are checked. Generation and validate.py check connectedness, exact recolor coordinates, Cartoon C4 occupancy/paint, two-color semantics, palette identity and output hashes.

[Style contact sheet](previews/contact_01.png) includes every treatment. [Four-view geometry sheet](previews/geometry_01.png) shows Base and Cartoon at 25, 115, 205 and 295 degree azimuths. Lighting and camera match within each family; independently framed rows do not imply equal world size.

These are import/render checks, not gameplay testing. Both models exceed the 16-cubed PieceKind contract. Their widths are below the separate loose-model limit of 62, but that path is not exercised here. Gameplay, collision, cover and destruction require separate integration. VoxelXCOM is unchanged; do not generate cell files automatically.

## Reproduction and continuation

Run from the workspace root:

```powershell
python output/poke_u/generate.py
$pokeUFiles = (Get-ChildItem -LiteralPath output/poke_u -Filter *.vox -File).FullName
python tools/inspect_vox.py $pokeUFiles --output output/poke_u/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_u/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_u/compose_previews.py
python output/poke_u/validate.py
```

Automated preview runs launch hidden with stdout/stderr saved in qa/. Generation uses deterministic mathematics, standard Python, local sculpt.py and voxlib.py; preview composition uses Pillow. The source image, regions and pinned palette are inputs. The generator writes only its 14 named models and manifest, refusing unknown/changed models unless deliberately passed `--replace-generated`. Preserve hand edits before overriding. Refresh audits, render evidence and visual review after revisions. All future poke_u models belong directly in this folder.

- [Flowers, bushes and grass](vegetation/README.md): 4 new appearances, 28 complete models, and existing-family reuse links.

## Complete bridges (2026-11-03)

[Bridge collection for this image](bridges/README.md): 2 new families, 14 complete VOX files with all seven treatments, source crops, cardinal/underside views and bank-placement previews. Existing assets are preserved. Shared validation and generation: [complete bridges](../bridges/README.md).

## Buildings (2026-11-03)

- [Two buildings, 14 complete models](buildings/README.md): `PokeU_Cottage` (the cottage, three copies) and `PokeU_WingHouse` (the big house with its front wing), each in Base and all six variations, made on VCOM's tile grid at game scale (closed doors, MagicaVoxel Glass windows) as the poke_r buildings are, and tested in a copy of the game. [Overview](buildings/overview.png) | [File index](buildings/FILES.md).

## Terrain (2026-11-04)

- [1 terrain style, 70 complete models](terrain/README.md): `PokeU_IslandRim_H5 (5 levels)` and 2 whole small islands (`PokeU_SmallIsland`, `PokeU_Islet`), modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
