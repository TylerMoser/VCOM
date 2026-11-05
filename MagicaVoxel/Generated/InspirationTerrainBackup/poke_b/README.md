# poke_b tree collection

Created 2026-10-26 from [poke_b.png](../../poke_b.png). **112 complete VOX files: 16 source appearances, each with Base plus all six established variations.** No individual cell files or brush packages.

Start with [the rendered overview](overview.png), [source-region catalogue](reference/catalogue.png), or [the complete file index](FILES.md). The 16 appearances cover six underlying silhouettes; fruit, flowers and distinct foliage colorways receive their own families instead of being omitted as duplicates. These are descriptive asset names, not claims about botanical species.

## Scale and reconstruction

The 656 x 960 reference fits a 41 x 60 grid of 16-pixel tiles. The repeated map details are consistent with that tile spacing. Use one image pixel approximately per voxel and 16 voxels per game tile, with Godot scale 0.0625. Width and vertical extent approximate the visible sprite excluding cast shadows, neighboring trees and ground plants. Sprite bounds are estimated, not segmentation-derived.

The map is an oblique 2D view: sprite height contains both crown depth and vertical projection. These models deliberately use the visible height as an approximate authoring-height target, rather than pretending to recover a unique physical height. Square depth is inferred from crown width. Source-region boxes in `reference/regions.json` and the manifest are image XY, top-left origin, right/bottom exclusive; they include context and are not exact sprite masks.

All models use Z-up, bottom at z=0, horizontal canvas-centered pivot, graph translation `0 0 floor(height/2)`, and no required facing direction. There is no forced rounding to whole tiles. Canvas dimensions differ slightly from occupied bounds, which are measured separately below. Model scale is not normalized across tree types; preview cards alone are individually framed.

| Appearance / Base model | Canvas XYZ | Base occupied XYZ | Canvas tiles XYZ | Family comparison |
| --- | --- | --- | --- | --- |
| [Column](PokeB_Column.vox) | 32 x 32 x 48 | 32 x 31 x 48 | 2.0 x 2.0 x 3.0 | [Seven styles](previews/PokeB_Column_family.png) |
| [ColumnFruit](PokeB_ColumnFruit.vox) | 32 x 32 x 48 | 32 x 31 x 48 | 2.0 x 2.0 x 3.0 | [Seven styles](previews/PokeB_ColumnFruit_family.png) |
| [ColumnFlower](PokeB_ColumnFlower.vox) | 32 x 32 x 48 | 32 x 31 x 48 | 2.0 x 2.0 x 3.0 | [Seven styles](previews/PokeB_ColumnFlower_family.png) |
| [BroadleafLime](PokeB_BroadleafLime.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Seven styles](previews/PokeB_BroadleafLime_family.png) |
| [BroadleafEmerald](PokeB_BroadleafEmerald.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Seven styles](previews/PokeB_BroadleafEmerald_family.png) |
| [BroadleafOlive](PokeB_BroadleafOlive.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Seven styles](previews/PokeB_BroadleafOlive_family.png) |
| [FruitTree](PokeB_FruitTree.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Seven styles](previews/PokeB_FruitTree_family.png) |
| [Conifer](PokeB_Conifer.vox) | 40 x 40 x 48 | 35 x 36 x 48 | 2.5 x 2.5 x 3.0 | [Seven styles](previews/PokeB_Conifer_family.png) |
| [SpreadingGreen](PokeB_SpreadingGreen.vox) | 48 x 48 x 48 | 46 x 46 x 48 | 3.0 x 3.0 x 3.0 | [Seven styles](previews/PokeB_SpreadingGreen_family.png) |
| [SpreadingFlower](PokeB_SpreadingFlower.vox) | 48 x 48 x 48 | 47 x 47 x 48 | 3.0 x 3.0 x 3.0 | [Seven styles](previews/PokeB_SpreadingFlower_family.png) |
| [SpreadingGold](PokeB_SpreadingGold.vox) | 48 x 48 x 48 | 46 x 46 x 48 | 3.0 x 3.0 x 3.0 | [Seven styles](previews/PokeB_SpreadingGold_family.png) |
| [SpreadingOrangeFruit](PokeB_SpreadingOrangeFruit.vox) | 48 x 48 x 48 | 47 x 47 x 48 | 3.0 x 3.0 x 3.0 | [Seven styles](previews/PokeB_SpreadingOrangeFruit_family.png) |
| [SpreadingRed](PokeB_SpreadingRed.vox) | 48 x 48 x 48 | 46 x 46 x 48 | 3.0 x 3.0 x 3.0 | [Seven styles](previews/PokeB_SpreadingRed_family.png) |
| [LandmarkTree](PokeB_LandmarkTree.vox) | 68 x 68 x 80 | 65 x 65 x 80 | 4.25 x 4.25 x 5.0 | [Seven styles](previews/PokeB_LandmarkTree_family.png) |
| [SlenderSapling](PokeB_SlenderSapling.vox) | 12 x 12 x 32 | 11 x 11 x 32 | 0.75 x 0.75 x 2.0 | [Seven styles](previews/PokeB_SlenderSapling_family.png) |
| [SlenderFruitSapling](PokeB_SlenderFruitSapling.vox) | 12 x 12 x 32 | 11 x 11 x 32 | 0.75 x 0.75 x 2.0 | [Seven styles](previews/PokeB_SlenderFruitSapling_family.png) |

## Shape and appearance decisions

- Column: tall, narrow, layered forest crown, with plain, orange-red fruit and purple-flower appearances. Adjacent repeated placements are the same source type, not extra tree types.
- Broadleaf: shorter, rounder pointed crown in lime, emerald and olive, plus the fruit-bearing appearance. These colorways intentionally share geometry.
- Conifer: pointed three-whorl canopy with projecting tips. The red plants beside some conifers are separate ground mushrooms/plants, not attached tree fruit, and are excluded.
- Spreading: wide lower canopy ring, exposed wood in the central cleft, and a smaller upper crown. Includes green, purple-flowered, gold/orange, orange-fruited and red-orange appearances. Ground fruit/litter is excluded; attached fruit is retained.
- Landmark: the large central tree has a thick rooted trunk, branch forks and a multi-lobed crown. Base uses five surrounding lobes; Cartoon uses four balanced lobes and a central crown.
- Slender sapling: the small narrow ornamental tree, both plain and fruit-bearing. It is less than a tile wide and two tiles tall.

Base geometry includes broad leaf color clusters, slightly uneven contours, roots and hidden structural wood. It is a hand-directed procedural 3D interpretation, not a flat extrusion or an exact volumetric recovery of the image. Cartoon uses cleaner region colors, balanced canopy tiers, fourfold geometry and paint symmetry, and repeated ornament placement.

## Variation rules applied

The shared [variation specification](../../knowledge/VARIATIONS.md) remains authoritative. Each family contains:

1. Base: reference-inspired shape and colors.
2. Cartoon: clean, exactly quarter-turn-symmetric shape and paint.
3. CratePalette: exact Base occupancy, recolored into the pinned game palette.
4. TwoColor: exact Base occupancy; one foliage color and one wood color.
5. Cartoon_TwoColor: exact saved Cartoon occupancy, the same two family colors.
6. CratePalette_TwoColor: exact Base occupancy, two existing game colors.
7. Cartoon_CratePalette_TwoColor: exact Cartoon occupancy, the same two game colors.

Leaves, attached fruit and flowers comprise the foliage group for reduction. Trunk, branches, roots and hidden core comprise wood. TwoColor intentionally removes the separate orange/purple paint while retaining any ornament relief. Groups are explicit coordinate assignments during generation, not guessed after recoloring. Color-only variants preserve every occupied coordinate and the scene placement.

CratePalette uses the complete [pinned RGBA snapshot](../../knowledge/palettes/crate-palette.json) byte-for-byte. Green foliage maps to indices 241-246; warm autumn foliage maps within 217-238; wood maps to actual crate browns 178-180. Decorations choose the nearest available reference RGB across indices 1-254. Every family records its exact remap and two representative colors in [manifest.json](manifest.json). No active voxel uses 0 or reserved index 255. Red/olive families may converge with other families under game-palette reduction; preserve those named outputs to retain provenance.

## Validation and game use

The [structural audit](structural-audit.json) covers exactly the 112 delivered files: zero errors and zero warnings. The generator rereads saved files and checks sizes, bounds, active palette entries, connectivity, recolor coordinate equality, Cartoon geometry/paint symmetry, exact palette hashes and two used colors. Every model is one six-connected component.

[Godot validation](godot-validation.json) confirms all 112 models imported as complete meshes at scale 0.0625, retained every voxel and stood at ground height zero. The QA project copies the current sibling importer with its license and [source hashes](qa/source-provenance.json). This tests the whole-model Mesh importer, not battle-map integration, gameplay, collision, destruction, or the single-cell PieceKind reader.

All six style treatments were reviewed in matched-camera contact sheets. Base and Cartoon were also reviewed from four azimuths. See [validation summary](validation-summary.json), `previews/contact_01.png` through `contact_04.png`, and `geometry_01.png` through `geometry_04.png`. Lighting creates shaded rendered pixels even on strictly two-color paint. No MagicaVoxel GUI validation is claimed.

Current integration limits still apply: PieceKind reads a 16-cubed cell, and VoxelShape.WIDEST is 62 for loose-model X extent. All these complete trees exceed one cell in height; the landmark also exceeds that loose-model width limit. These are correctly sized authoring assets, not already registered combat pieces. Integrate separately when requested; do not automatically recreate cell parts. VoxelXCOM was not modified.

## Reproduce and continue

From the workspace root:

```powershell
python output/poke_b/generate.py
$pokeBFiles = (Get-Content output/poke_b/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { Join-Path 'output/poke_b' $_ }
python tools/inspect_vox.py $pokeBFiles --output output/poke_b/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_b/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_b/compose_previews.py
```

The render command is interactive when invoked manually. Automated runs use a hidden Start-Process and capture `qa/render.log` and `qa/render-errors.log`. The generator uses only the Python standard library; preview composition uses Pillow. `voxlib.py` contains the local writer/reader helpers inherited from poke_a, so regeneration does not depend on importing the poke_a generator.

`generate.py` names its 112 outputs explicitly through the family/style tables. It checks existing files against their last manifest hashes and refuses unknown or hand-edited files. `--replace-generated` bypasses that protection for deliberate revisions only. Preserve hand edits separately before regenerating. The generator replaces manifest.json; render/compose steps refresh their own outputs. After a deliberate model revision, rerun affected validation and update the review summary rather than retaining stale successful evidence.

Keep all final VOX files directly in this folder. Store subsequent source-derived models here, with distinct names for new shapes/versions. Do not infer that one file is redundant merely because palette reduction makes two source colorways look alike.


## Building collection

- [Six buildings, 42 complete models](buildings/README.md): domed lab, red clinic, three mansard-house appearances and flower cottage. [Building overview](buildings/overview.png) | [Building file index](buildings/FILES.md). Added 2026-10-28; original tree generator and records remain separate.


## Lights (2026-10-28)

[PokeB_SilverStreetLantern](lights/README.md): seven complete variations with Emit materials, source notes, day/night previews and runtime validation.

## Game-ready buildings (2026-10-28)

- [Six buildings redone for the game, 42 complete models](game_buildings/README.md): `PokeB_GameDomeLab`, `PokeB_GameRedClinic`, `PokeB_GameGrayEntryHouse`, `PokeB_GameGrayWindowHouse`, `PokeB_GameCyanEntryHouse`, `PokeB_GameFlowerCottage`, each in Base and all six variations, made on VCOM's tile grid at game scale (storeys, raised floors, stairs, closed doors, MagicaVoxel Glass windows) as the poke_c buildings are, and tested in a copy of the game. [Overview](game_buildings/overview.png) | [File index](game_buildings/FILES.md). ChatGPT's buildings above are kept as they were, by the user's choice.

- [Flowers, bushes and grass](vegetation/README.md): 4 new appearances, 28 complete models, and existing-family reuse links.


## Outdoor stairs — 2026-11-03

Added 2 families / 14 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [1 terrain style, 49 complete models](terrain/README.md): `PokeB_CourseCliff_H5 (5 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
