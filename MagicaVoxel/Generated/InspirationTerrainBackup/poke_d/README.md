# poke_d autumn tree collection



91 complete VOX models from [poke_d.png](../../poke_d.png): thirteen source appearances, each with Base and all six established variations. No individual cell files or brush packages.



[Overview](overview.png) | [Complete file index](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)



## Source coverage and scale



The 864 x 848 source is consistent with a 54 x 53 grid of 16-pixel tiles. Approximately one source pixel corresponds to one voxel, with 16 voxels per game tile and Godot Mesh scale 0.0625. Width and height are estimated from visible sprite extents, excluding cast shadows and neighboring objects. Depth is inferred from crown width. Top-down sprite height includes depth projection, so these are useful relative authoring sizes rather than a unique physical reconstruction.



Four size/shape classes appear in red, gold and sage: tall trees, rounded trees, compact trees and slender saplings. A fifth shape has a gold canopy and a broad red flower-like crown. These thirteen appearances are retained separately, even when a reduced palette makes two outputs similar. Repeated placements, occlusion and adjacent ground leaves do not create additional tree types. The names are visual descriptions, not botanical identifications.



| Base model | Canvas XYZ | Base occupied XYZ | Canvas tiles XYZ | Family preview |

| --- | --- | --- | --- | --- |

| [TallRed](PokeD_TallRed.vox) | 32 x 32 x 48 | 29 x 28 x 48 | 2.0 x 2.0 x 3.0 | [Seven treatments](previews/PokeD_TallRed_family.png) |

| [TallGold](PokeD_TallGold.vox) | 32 x 32 x 48 | 29 x 28 x 48 | 2.0 x 2.0 x 3.0 | [Seven treatments](previews/PokeD_TallGold_family.png) |

| [TallSage](PokeD_TallSage.vox) | 32 x 32 x 48 | 29 x 28 x 48 | 2.0 x 2.0 x 3.0 | [Seven treatments](previews/PokeD_TallSage_family.png) |

| [RoundRed](PokeD_RoundRed.vox) | 32 x 32 x 40 | 29 x 30 x 40 | 2.0 x 2.0 x 2.5 | [Seven treatments](previews/PokeD_RoundRed_family.png) |

| [RoundGold](PokeD_RoundGold.vox) | 32 x 32 x 40 | 29 x 30 x 40 | 2.0 x 2.0 x 2.5 | [Seven treatments](previews/PokeD_RoundGold_family.png) |

| [RoundSage](PokeD_RoundSage.vox) | 32 x 32 x 40 | 29 x 30 x 40 | 2.0 x 2.0 x 2.5 | [Seven treatments](previews/PokeD_RoundSage_family.png) |

| [CompactRed](PokeD_CompactRed.vox) | 28 x 28 x 32 | 25 x 24 x 32 | 1.75 x 1.75 x 2.0 | [Seven treatments](previews/PokeD_CompactRed_family.png) |

| [CompactGold](PokeD_CompactGold.vox) | 28 x 28 x 32 | 25 x 24 x 32 | 1.75 x 1.75 x 2.0 | [Seven treatments](previews/PokeD_CompactGold_family.png) |

| [CompactSage](PokeD_CompactSage.vox) | 28 x 28 x 32 | 25 x 24 x 32 | 1.75 x 1.75 x 2.0 | [Seven treatments](previews/PokeD_CompactSage_family.png) |

| [SaplingRed](PokeD_SaplingRed.vox) | 12 x 12 x 32 | 10 x 10 x 32 | 0.75 x 0.75 x 2.0 | [Seven treatments](previews/PokeD_SaplingRed_family.png) |

| [SaplingGold](PokeD_SaplingGold.vox) | 12 x 12 x 32 | 10 x 10 x 32 | 0.75 x 0.75 x 2.0 | [Seven treatments](previews/PokeD_SaplingGold_family.png) |

| [SaplingSage](PokeD_SaplingSage.vox) | 12 x 12 x 32 | 10 x 10 x 32 | 0.75 x 0.75 x 2.0 | [Seven treatments](previews/PokeD_SaplingSage_family.png) |

| [BlossomGold](PokeD_BlossomGold.vox) | 32 x 32 x 40 | 29 x 29 x 40 | 2.0 x 2.0 x 2.5 | [Seven treatments](previews/PokeD_BlossomGold_family.png) |



Source-region boxes in `reference/regions.json` and the manifest use top-left image XY, exclusive right/bottom coordinates. They include surrounding context and are not exact segmentation masks. Canvas sizes and occupied extents are distinct; full measured bounds for every variant are in the manifest. Preview cards are framed independently between families and therefore do not depict relative size across rows.



## Modeling decisions



poke_d has rounded, overlapping leaf scales rather than the noisier leafy silhouettes of poke_b/poke_c. `sculpt.py` builds a filled core and layered tapered leaf volumes, with broad shoulders and hanging lower tips. Color regions follow individual leaf masses instead of random per-voxel noise. The muted sage, warm gold and coral-red palettes are artistic approximations of the source, not claimed exact color extraction.



Tall trees have five layered whorls and a narrow crown; rounded trees have a shorter, fuller canopy; compact trees have smaller total dimensions and a squat canopy; saplings have a narrow upright silhouette. All include a rooted trunk with a continuous hidden wood core. No ground shadow or separate fallen-leaf pile is incorporated.



BlossomGold has a gold lower canopy and broad red upper petals, with a smaller red center cap. Base uses five petal directions; Cartoon uses four for matching cardinal views. This crown is treated as foliage for TwoColor reduction, not as a third material.



All models use Z-up, ground at z=0, horizontal canvas-centered pivot, graph translation `0 0 floor(height/2)`, and no mandatory front direction. They are solid volumes, not flat sprite extrusions. Unseen depth/back structure is inferred.



## Variations and palette choices



The [shared specification](../../knowledge/VARIATIONS.md) defines the six suffixes: Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Base is the seventh file. Cartoon balances leaf whorls and repeated shapes, simplifies painted regions and obeys exact quarter-turn geometry/paint symmetry. Color-only variants retain the exact occupied coordinates, dimensions and placement of their designated Base or Cartoon source.



Semantic groups are explicit coordinate labels: foliage includes all leaves and the blossom crown; wood includes roots, trunk and hidden structural core. Indices 1-6 and 10-15 encode original foliage, and 7-9 encode wood. This is a local generator convention, not a universal rule for imported models. Every TwoColor file occupies exactly two indices with distinct RGBA values. BlossomGold reduces all red/gold foliage to one gold representative plus wood. Scene lighting still shades the rendered faces.



CratePalette preserves all 1,024 bytes of the pinned [crate palette](../../knowledge/palettes/crate-palette.json). Red foliage maps to existing red/coral slots 219-221; gold maps within 179/228/229/230; sage maps to green slots 241-246; bark maps to the actual crate browns 178-180. The red range deliberately excludes the orange slot 222 to keep red trees recognizable. Sage becomes more saturated under the existing green palette. Exact remaps and the two game-palette colors for each family are recorded in manifest.json; both crate/two-color mixtures reuse the same selections. No occupied voxel uses reserved index 255.



## Validation and game scope



[Structural audit](structural-audit.json): exactly 91 delivered VOX files, zero errors and zero warnings. Generation rereads serialized output to check bounds, indices, connectivity, source-coordinate equality, symmetry, palette hashes and two-color counts. Every model is a single six-connected component.



[Godot report](godot-validation.json) records import counts, mesh bounds, surfaces and ground alignment. QA uses the current sibling VCOM whole-model Mesh importer copied with its license and [source hashes](qa/source-provenance.json), at scale 0.0625. [Validation summary](validation-summary.json) ties final checks and review evidence to the delivered hashes.



All seven treatments are reviewed in `previews/contact_01.png` through `contact_04.png`; Base and Cartoon are also reviewed from four azimuths in the corresponding geometry sheets. Cameras and lighting match within each family. No MagicaVoxel GUI validation, combat-map integration, collision, destruction or gameplay testing is claimed.



These models exceed the 16-cubed PieceKind cell contract in height. Their widths are below the loose-model X limit of 62, but that runtime path is not tested here. VoxelXCOM is unchanged. Integrate separately when requested, without automatically generating cell parts.



## Reproduce and continue



From the workspace root:



```powershell

python output/poke_d/generate.py

$pokeDFiles = (Get-ChildItem -LiteralPath output/poke_d -Filter *.vox -File).FullName

python tools/inspect_vox.py $pokeDFiles --output output/poke_d/structural-audit.json

& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_d/qa --script res://preview.gd --rendering-method gl_compatibility

python output/poke_d/compose_previews.py

```



Automated renders use Start-Process with WindowStyle Hidden and capture `qa/render.log` and `qa/render-errors.log`. Generation uses standard Python; preview composition uses Pillow. `generate.py` owns the output family list, palettes and serialization checks; `sculpt.py` owns the new leaf-scale geometry; `voxlib.py` is the local VOX helper. Nothing imports another image folder at runtime.



The generator rewrites its named outputs and manifest after checking existing VOX hashes against the last manifest. Unknown/modified files are refused unless `--replace-generated` is deliberately passed. Preserve hand edits before using that override. The source image, source-region JSON, palette snapshot and local scripts are dependencies. After editing models, refresh audits, renders and the validation summary rather than retaining stale evidence. Keep future poke_d assets directly in this output folder under distinct names.





## Lights (2026-10-28)



[PokeD_StoneLantern](lights/README.md): seven complete variations with Emit materials, source notes, day/night previews and runtime validation.





## Rocks (2026-10-28)



[4 rock appearances, 28 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.



- [Flowers, bushes and grass](vegetation/README.md): 3 new appearances, 21 complete models, and existing-family reuse links.

## Complete bridges (2026-11-03)

[Bridge collection for this image](bridges/README.md): 3 new families, 21 complete VOX files with all seven treatments, source crops, cardinal/underside views and bank-placement previews. Existing assets are preserved. Shared validation and generation: [complete bridges](../bridges/README.md).


## Outdoor stairs — 2026-11-03

Added 2 families / 14 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [4 terrain styles, 224 complete models](terrain/README.md): `PokeD_RockLedge_H3 (3 levels)`, `PokeD_RockBank_H3 (3 levels)`, `PokeD_RiverCliff_H6 (6 levels)`, `PokeD_RetainingWall_H5 (5 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).

## Codex spotted mushrooms — 2026-11-04

Added the two-mushroom riverbank clump in all seven styles. [Collection and previews](../codex_missed_vegetation/README.md). Files use `_Codex_` names.
