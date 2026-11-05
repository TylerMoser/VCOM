# poke_e woodland tree collection

70 complete VOX models from [poke_e.png](../../poke_e.png): ten tree appearances, each with Base and all six established variations. No cell-by-cell files or automatic brush packages.

[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Source interpretation and scale

The 480 x 480 map is consistent with a 30 x 30 grid of 16-pixel tiles. Approximately one source pixel corresponds to one voxel, with 16 voxels per game tile and Godot Mesh scale 0.0625. Visible sprite extents guide the authoring dimensions. Depth and unseen sides are inferred; the oblique sprite height combines physical height and projected crown depth, so this is a relative-scale reconstruction, not exact physical recovery.

Ten appearances are represented: fuller tufted and narrower pointed broadleaf crowns sharing lime-green colors; olive and emerald broadleaf appearances; a fruit-bearing tree; a tiered conifer; a spreading tree with an upper crown; a large cloud-like landmark tree; a leafy sapling; and a stemmed sapling. The tufted/pointed distinction is an interpretation of crown contours, not two different color palettes. Source samples share their major green RGB values. Occluded copies and repeated placements do not require separate models.

| Base model | Canvas XYZ | Base occupied XYZ | Canvas tiles XYZ | Seven-style comparison |
| --- | --- | --- | --- | --- |
| [BroadleafTufted](PokeE_BroadleafTufted.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Preview](previews/PokeE_BroadleafTufted_family.png) |
| [BroadleafPointed](PokeE_BroadleafPointed.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Preview](previews/PokeE_BroadleafPointed_family.png) |
| [BroadleafOlive](PokeE_BroadleafOlive.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Preview](previews/PokeE_BroadleafOlive_family.png) |
| [BroadleafEmerald](PokeE_BroadleafEmerald.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Preview](previews/PokeE_BroadleafEmerald_family.png) |
| [FruitTree](PokeE_FruitTree.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Preview](previews/PokeE_FruitTree_family.png) |
| [Conifer](PokeE_Conifer.vox) | 40 x 40 x 48 | 35 x 36 x 48 | 2.5 x 2.5 x 3.0 | [Preview](previews/PokeE_Conifer_family.png) |
| [SpreadingTree](PokeE_SpreadingTree.vox) | 48 x 48 x 48 | 46 x 46 x 48 | 3.0 x 3.0 x 3.0 | [Preview](previews/PokeE_SpreadingTree_family.png) |
| [LandmarkTree](PokeE_LandmarkTree.vox) | 68 x 68 x 64 | 65 x 65 x 64 | 4.25 x 4.25 x 4.0 | [Preview](previews/PokeE_LandmarkTree_family.png) |
| [LeafySapling](PokeE_LeafySapling.vox) | 12 x 12 x 28 | 10 x 10 x 28 | 0.75 x 0.75 x 1.75 | [Preview](previews/PokeE_LeafySapling_family.png) |
| [StemmedSapling](PokeE_StemmedSapling.vox) | 12 x 12 x 28 | 12 x 11 x 28 | 0.75 x 0.75 x 1.75 | [Preview](previews/PokeE_StemmedSapling_family.png) |

The landmark is deliberately broad and shorter than the poke_b landmark: 68 x 68 x 64 voxels, approximately 4.25 x 4.25 x 4 tiles. It follows this image rather than inheriting poke_b's 80-voxel height. Saplings are 12 x 12 x 28, under one tile wide. Dimensions are not forced to whole-tile multiples. Previews are independently framed across families; their card sizes do not imply equal world size.

Source regions use top-left image XY with exclusive right/bottom coordinates. These are contextual crops, not segmentation masks. Ground flowers, grass, cast shadows, fences and nearby trees are excluded from the models. All files are grounded at z=0, use MagicaVoxel Z-up, have a horizontally canvas-centered pivot, and scene translation `0 0 floor(height/2)`. There is no mandatory facing direction.

## Shape and material decisions

- Tufted broadleaf: fuller upper shoulders and several small upper crown masses. Pointed broadleaf: more tapered upper profile and distinct crown tiers. They intentionally share the source green palette.
- Olive broadleaf: a broader rounded lower silhouette with muted olive colors. Emerald broadleaf: darker, cooler foliage on a pointed crown.
- Fruit tree: attached orange-red fruit distributed around the crown; no ground fruit or flower bed is included.
- Conifer: three overlapping pointed whorls with projecting tips.
- Spreading tree: lower canopy ring, exposed central wood, smaller upper crown; structural wood connects the masses.
- Landmark tree: large overlapping rounded lobes and a thick, rooted branching trunk. Base has five surrounding lobes; Cartoon balances four.
- Leafy sapling: foliage begins near the ground. Stemmed sapling: a compact crown raised on an exposed dark-brown stem. Neither includes the adjacent ground plants.

Colors are reference-guided and include sampled major green values, with artistic interpolation/selection for 3D shading. They are not an exact image-pixel reproduction. Geometry is a solid volumetric reconstruction, including internal wood. The local sculpt was adapted from the established poke_b approach because these sources share a visual vocabulary, then adjusted for poke_e crown profiles and scale. No output imports another image folder at runtime.

## Variations

The [shared specification](../../knowledge/VARIATIONS.md) defines Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Together with Base, these are seven files per appearance. Cartoon uses exact quarter-turn symmetry for shape and paint, cleaner regions and balanced crown structure. Mixtures inherit the saved Cartoon geometry or Base geometry as appropriate; recolors preserve coordinates, size and placement.

Explicit semantic labels distinguish foliage from wood at generation time. Fruit belongs to foliage during two-color reduction; its relief remains but orange paint is removed. Every TwoColor file uses precisely two occupied palette indices with distinct RGBA colors. Lighting still shades the rendered faces. Two-color selections remain consistent between the relevant mixtures.

CratePalette copies the full pinned [crate RGBA snapshot](../../knowledge/palettes/crate-palette.json). Foliage maps into existing greens 241-246, bark to crate browns 178-180, and fruit to the closest existing reference colors. Full mappings, palette hash, representative RGBA colors and chosen game-palette indices are recorded per family in manifest.json. Palette reduction may make some source appearances converge; retain all family filenames for provenance. Index 255 is reserved and unused.

## Validation and integration scope

[Structural audit](structural-audit.json): 70 delivered files, zero errors and zero warnings. Generation rereads serialized VOX files and checks dimensions, bounds, indices, connectivity, exact recolor occupancy, Cartoon symmetry, palette hashes and two-color counts. Every model is a single six-connected component.

[Godot report](godot-validation.json) records complete-model Mesh imports at scale 0.0625, retained voxel counts and grounded bounds. The QA folder contains the current sibling importer, its license, and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final checks, visual review and delivered hashes.

Contact sheets cover all seven treatments per appearance; geometry sheets cover four azimuths of Base and Cartoon. Camera and light are identical within each comparison. This validates structural correctness and the whole-model reader/importer/render path, not combat gameplay or MagicaVoxel GUI behavior.

All models exceed the 16-cubed PieceKind cell contract in height. The landmark also exceeds the current loose-model X limit of 62 voxels. Complete authoring dimensions are preserved; integration is a separate request and does not automatically justify generating cell parts. VoxelXCOM was not modified.

## Reproduction and continuation

From the workspace root:

```powershell
python output/poke_e/generate.py
$pokeEFiles = (Get-ChildItem -LiteralPath output/poke_e -Filter *.vox -File).FullName
python tools/inspect_vox.py $pokeEFiles --output output/poke_e/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_e/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_e/compose_previews.py
```

Automated rendering uses Start-Process with WindowStyle Hidden and captures `qa/render.log` and `qa/render-errors.log`. The generator needs standard Python; preview composition needs Pillow. `generate.py` owns family and palette definitions, `sculpt.py` owns geometry, and `voxlib.py` is the local VOX helper. The source image, region JSON and pinned palette are also dependencies.

Generation rewrites only its named model outputs and manifest, checking existing VOX hashes against the prior manifest. Unknown/changed models are refused unless `--replace-generated` is deliberately supplied. Preserve hand edits before overriding. Render and composition scripts refresh their own artifacts. After revisions, rerun checks and update the review summary rather than retaining stale successful records. Keep further poke_e models directly in this folder under distinct descriptive names.

- [Flowers, bushes and grass](vegetation/README.md): 5 new appearances, 35 complete models, and existing-family reuse links.

## Terrain (2026-11-04)

- [2 terrain styles, 98 complete models](terrain/README.md): `PokeE_EarthBank_H1 (1 level)`, `PokeE_LakeBank_H1 (1 level)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
