# poke_h trees and woody shrubs



Created 2026-10-27: **77 complete VOX files**, eleven appearances with Base and all six established variations. No individual cell files or automatic brush packages.



[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)



## Coverage and scale



[poke_h.png](../../poke_h.png) is 560 x 560, consistent with 35 x 35 tiles at 16 pixels per tile. Approximately one source pixel corresponds to one voxel, with 16 voxels per game tile and Godot Mesh scale 0.0625. Sprite width and vertical extent guide the dimensions; square depth and hidden structure are inferred. The top-down projection combines height with canopy depth, so these are relative authoring estimates, not an exact physical recovery.



The source contains lime, emerald and olive broadleaf appearances; a rounded crown with drooping folds; a fruit tree; conifer; spreading tree; leafy, fruit-bearing and stemmed saplings; and a compact fruit bush. The small woody fruit bush is included to preserve its distinct scale. Repeated placements and occluded copies are not additional types. Pink and blue creatures resting among the trees are separate objects and are not included as foliage or ornaments. Wheat, hay, flowers and ground vegetation are excluded.



| Base model | Canvas XYZ | Base occupied XYZ | Canvas tiles XYZ | All styles |

| --- | --- | --- | --- | --- |

| [BroadleafLime](PokeH_BroadleafLime.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Comparison](previews/PokeH_BroadleafLime_family.png) |

| [BroadleafEmerald](PokeH_BroadleafEmerald.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Comparison](previews/PokeH_BroadleafEmerald_family.png) |

| [BroadleafOlive](PokeH_BroadleafOlive.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Comparison](previews/PokeH_BroadleafOlive_family.png) |

| [RoundedCrown](PokeH_RoundedCrown.vox) | 40 x 40 x 40 | 40 x 40 x 40 | 2.5 x 2.5 x 2.5 | [Comparison](previews/PokeH_RoundedCrown_family.png) |

| [FruitTree](PokeH_FruitTree.vox) | 32 x 32 x 40 | 32 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Comparison](previews/PokeH_FruitTree_family.png) |

| [Conifer](PokeH_Conifer.vox) | 40 x 40 x 48 | 35 x 36 x 48 | 2.5 x 2.5 x 3.0 | [Comparison](previews/PokeH_Conifer_family.png) |

| [SpreadingTree](PokeH_SpreadingTree.vox) | 48 x 48 x 48 | 46 x 46 x 48 | 3.0 x 3.0 x 3.0 | [Comparison](previews/PokeH_SpreadingTree_family.png) |

| [LeafySapling](PokeH_LeafySapling.vox) | 12 x 12 x 28 | 10 x 10 x 28 | 0.75 x 0.75 x 1.75 | [Comparison](previews/PokeH_LeafySapling_family.png) |

| [FruitSapling](PokeH_FruitSapling.vox) | 12 x 12 x 28 | 11 x 10 x 28 | 0.75 x 0.75 x 1.75 | [Comparison](previews/PokeH_FruitSapling_family.png) |

| [StemmedSapling](PokeH_StemmedSapling.vox) | 12 x 12 x 28 | 12 x 11 x 28 | 0.75 x 0.75 x 1.75 | [Comparison](previews/PokeH_StemmedSapling_family.png) |

| [CompactFruitBush](PokeH_CompactFruitBush.vox) | 24 x 24 x 24 | 24 x 24 x 24 | 1.5 x 1.5 x 1.5 | [Comparison](previews/PokeH_CompactFruitBush_family.png) |



Source boxes use image XY with top-left origin and exclusive right/bottom edges. They include contextual neighbors and are not segmentation masks. `reference/sapling_detail.png` shows the plain low-foliage sapling at the right edge, distinguishing it from the raised stemmed form. All models are Z-up, grounded at z=0, horizontally canvas-centered, with scene translation `0 0 floor(height/2)` and no required facing direction. The manifest records actual occupied bounds separately from canvas size. Preview framing varies between families, so card sizes do not imply equal world size.



## Modeling choices



- BroadleafLime, BroadleafEmerald and BroadleafOlive preserve the distinct colors and crown profiles. Olive has broader shoulders; the other two have more pointed tiering.

- RoundedCrown has a wider dome with radial folds and coherent broad leaf shading. It is not a recolor of the pointed broadleaf form.

- FruitTree has attached orange-red fruit. CompactFruitBush retains the same visual vocabulary in a 24-cubed model, with a short woody base.

- Conifer has three overlapping pointed whorls. SpreadingTree has a wide lower leaf mass, visible central wood and a smaller upper crown.

- LeafySapling has foliage close to ground; FruitSapling adds attached fruit; StemmedSapling raises the crown above a longer visible trunk.



Palettes are source-guided approximations, using the shared green vocabulary also seen in poke_e. Geometry is filled and has continuous structural wood, not a flat sprite extrusion. Base uses restrained asymmetry and broad color clusters. Cartoon balances the crown and paint under exact quarter turns. The local implementation adapts the established crown construction to this image, including new domed and compact profiles; it does not import another image folder at runtime.



## Variation rules



The [shared specification](../../knowledge/VARIATIONS.md) defines Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Base plus these six gives seven files per appearance. Color-only variants preserve every occupied coordinate, canvas and scene placement of their designated Base or Cartoon authority.



Semantic groups are explicit coordinate assignments: all leaves and attached fruit are foliage; roots, trunks, branches and hidden cores are wood. TwoColor removes separate fruit paint while preserving fruit relief, giving exactly two occupied palette indices and two distinct RGBA colors. Lighting still shades those colors in previews. The two game colors are selected once per family and reused in both crate/two-color mixtures.



CratePalette copies the complete pinned [crate RGBA snapshot](../../knowledge/palettes/crate-palette.json). Greens map to slots 241-246; wood to crate browns 178-180; fruit to nearest suitable saved palette colors. Exact mappings, representative colors, indices and palette hashes are in manifest.json. Palette reduction may make source colorways look similar; keep their named outputs for provenance. No occupied voxel uses reserved index 255.



## Validation and integration scope



[Structural audit](structural-audit.json): 77 delivered files, zero errors and zero warnings. Generation rereads serialized files and checks dimensions, bounds, palette indices, connectedness, coordinate preservation, symmetry, reference palette identity and exactly two colors where required. Every model is one six-connected component.



[Godot report](godot-validation.json) records all complete Mesh imports at scale 0.0625 with retained voxel counts and grounded bounds. QA copies the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final hashes and visual review evidence. Contact sheets cover every treatment; geometry sheets show four azimuths for Base and Cartoon.



These checks exercise the whole-model importer/render path, not combat gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. Every model exceeds the 16-cubed PieceKind contract in at least height. Widths are below the loose-model X limit of 62, but that separate runtime path is untested. VoxelXCOM was not changed. Integration remains separate and must not automatically create cell files.



## Reproduce and continue



From the workspace root:



```powershell

python output/poke_h/generate.py

$pokeHFiles = (Get-ChildItem -LiteralPath output/poke_h -Filter *.vox -File).FullName

python tools/inspect_vox.py $pokeHFiles --output output/poke_h/structural-audit.json

& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_h/qa --script res://preview.gd --rendering-method gl_compatibility

python output/poke_h/compose_previews.py

```



Automated rendering uses Start-Process with WindowStyle Hidden and captures `qa/render.log` and `qa/render-errors.log`. Generation needs standard Python; preview composition needs Pillow. `generate.py` owns families/palettes/variation checks; `sculpt.py` owns geometry; `voxlib.py` supplies local VOX I/O. The source image, region JSON and pinned palette are also dependencies.



The generator checks existing model hashes against the prior manifest and refuses unknown or hand-edited files unless `--replace-generated` is deliberately supplied. Preserve hand edits before that override. It rewrites its named outputs and manifest; rendering/composition refresh their own artifacts. After revisions, refresh audits, previews and the visual-review summary. Store future poke_h assets directly in this folder with distinct filenames.





## Rocks (2026-10-28)



[2 rock appearances, 14 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.



## Buildings (2026-10-29)



- [The farmhouse, 7 complete models](buildings/README.md): `PokeH_Farmhouse`, poke_b's flower cottage drawn again with a porch on two vine-wrapped posts, in Base and all six variations, made on VCOM's tile grid at game scale (two storeys, the outside stair, closed doors, MagicaVoxel Glass windows) as the poke_g buildings are, and tested in a copy of the game. [Overview](buildings/overview.png) | [File index](buildings/FILES.md).



- [Flowers, bushes and grass](vegetation/README.md): 4 new appearances, 28 complete models, and existing-family reuse links.

## Complete bridges (2026-11-03)

[Bridge collection for this image](bridges/README.md): 1 new families, 7 complete VOX files with all seven treatments, source crops, cardinal/underside views and bank-placement previews. Existing assets are preserved. Shared validation and generation: [complete bridges](../bridges/README.md).


## Outdoor stairs — 2026-11-03

Added 1 families / 7 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [2 terrain styles, 98 complete models](terrain/README.md): `PokeH_FarmBank_H1 (1 level)`, `PokeH_PondCliff_H3 (3 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
