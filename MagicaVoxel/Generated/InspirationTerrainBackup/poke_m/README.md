# poke_m woodland trees



Created 2026-10-27: **56 complete VOX files**, eight appearances with Base and all six established variations. Complete models only; no per-cell files or brush packages.



[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)



## Source interpretation and scale



[poke_m.png](../../poke_m.png) is an 800 x 880 pixel-art map on a 16-pixel tile grid. Approximately one image pixel corresponds to one voxel, retaining 16 voxels per game tile. Sprite width and visible vertical extent guide the dimensions; canopy depth and unseen structure are inferred. Source projection mixes height with canopy depth, so dimensions are relative authoring estimates, not exact physical recovery.



Eight forms were identified: round crown, compact pointed crown, large clustered-leaf tree, long drooping-leaf tree, broad tiered conifer, small leafy sapling, pine sapling with exposed stem, and a branching sapling with pale buds. Small partly occluded copies are not new species. Creatures perched among branches are excluded, as are reeds, grasses, flowers, water plants, stumps, logs, buildings and terrain. The budding sapling's pale tips belong to its foliage/flowering appearance and are retained; the source does not establish a biological species.



Source crop boxes use top-left XY and exclusive right/bottom edges. They include contextual neighboring objects, not segmentation masks. The enlarged regional views preserve source context for future review. All models are Z-up, stand at z=0, are horizontally centered on their canvas, and use scene translation `0 0 floor(height/2)` with no required facing direction.



| Base model | Canvas XYZ | Base occupied XYZ | Comparison |

| --- | --- | --- | --- |

| [PokeM_RoundCrown](PokeM_RoundCrown.vox) | 32 x 32 x 32 | 32 x 31 x 32 | [All styles](previews/PokeM_RoundCrown_family.png) |

| [PokeM_PointedCrown](PokeM_PointedCrown.vox) | 32 x 32 x 40 | 32 x 31 x 40 | [All styles](previews/PokeM_PointedCrown_family.png) |

| [PokeM_LeafClusterTree](PokeM_LeafClusterTree.vox) | 32 x 32 x 48 | 30 x 30 x 48 | [All styles](previews/PokeM_LeafClusterTree_family.png) |

| [PokeM_DroopingTree](PokeM_DroopingTree.vox) | 32 x 32 x 48 | 30 x 30 x 48 | [All styles](previews/PokeM_DroopingTree_family.png) |

| [PokeM_Conifer](PokeM_Conifer.vox) | 48 x 48 x 48 | 43 x 43 x 48 | [All styles](previews/PokeM_Conifer_family.png) |

| [PokeM_LeafySapling](PokeM_LeafySapling.vox) | 12 x 12 x 28 | 10 x 10 x 28 | [All styles](previews/PokeM_LeafySapling_family.png) |

| [PokeM_PineSapling](PokeM_PineSapling.vox) | 16 x 16 x 32 | 13 x 14 x 32 | [All styles](previews/PokeM_PineSapling_family.png) |

| [PokeM_BuddingSapling](PokeM_BuddingSapling.vox) | 16 x 16 x 24 | 12 x 12 x 24 | [All styles](previews/PokeM_BuddingSapling_family.png) |



## Modeling decisions



- RoundCrown has a broad, low body and rounded shoulders, with a short woody base. PointedCrown has a taller tapered silhouette and restrained shoulder tiers.

- LeafClusterTree builds raised overlapping elliptical leaf clusters around a solid core. DroopingTree uses longer, narrower overlapping leaves and a cooler green ramp. The two are distinct geometry families, not recolors.

- Conifer has three overlapping pointed whorls with broad projecting tips. PineSapling raises and compresses the whorls above a longer exposed stem; this is authored directly so connectivity is preserved.

- LeafySapling has foliage close to its base and a narrow tapered crown.

- BuddingSapling has a connected branching trunk, three irregular leaf/bud groups in Base and four balanced groups in Cartoon. Its pale buds are attached relief. Cartoon retains the identity while making the branch arrangement cardinally symmetric.



All models have filled geometry and continuous internal wood. Base uses restrained asymmetry and coherent clustered color. Cartoon changes leaf/branch arrangements or crown outline, and has exact quarter-turn occupancy and paint symmetry. No perched creature or source ground shadow is built into a model. The leaf sculptor adapts poke_l's cluster construction, while profile crowns adapt established earlier tree recipes; all implementation files are local copies with no runtime dependency on other image folders.



## Variations and palettes



The [shared specification](../../knowledge/VARIATIONS.md) defines Base and the six requested treatments: Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Every recolor preserves the exact occupied set, canvas and scene transform of its designated Base or Cartoon authority.



Semantic groups are explicit coordinate dictionaries: leaves, crown core and buds are foliage; roots, trunks, branches and hidden stems are wood. TwoColor uses exactly two occupied indices with distinct RGBA colors, one for each group, including pale buds in the foliage color while preserving their geometry. Lighting still shades those two colors in renders.



Source-guided palettes use saturated greens and warmer brown trunks; drooping leaves and pine needles use cooler greens. CratePalette copies the entire pinned [crate palette](../../knowledge/palettes/crate-palette.json). Foliage maps to green slots 241-246, wood to actual crate browns 178-180, and buds to nearest existing palette colors. TwoColor crate mixtures select one green and one brown once per family and reuse them in both combinations. Index 255 remains unused. Exact mappings, representatives, output and geometry-source hashes are recorded in the manifest.



## Validation and integration



[Structural audit](structural-audit.json) covers all 56 delivered files. Generation rereads each file and verifies dimensions, bounds, connectivity, exact recolor coordinates, C4 geometry and paint, full crate palette identity and two-color counts. [Godot report](godot-validation.json) records whole Mesh imports at scale 0.0625, retained voxel counts and grounded bounds. The QA project copies the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final verification and visual review.



[Contact sheet 1](previews/contact_01.png) and [sheet 2](previews/contact_02.png) cover all variants. [Geometry sheet 1](previews/geometry_01.png) and [sheet 2](previews/geometry_02.png) show four azimuths for Base and Cartoon. Camera/lighting match within each family; families are framed independently, so card sizes do not imply equal world size.



These checks test the whole-model importer/render path, not combat gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. Every model exceeds the 16-cubed PieceKind contract in height. Widths are below the loose-model X limit of 62, but that separate path remains untested. VoxelXCOM is unchanged. Resolve integration separately without automatically generating cell files.



## Reproduction and continuation



From the workspace root:



```powershell

python output/poke_m/generate.py

$pokeMFiles = (Get-ChildItem -LiteralPath output/poke_m -Filter *.vox -File).FullName

python tools/inspect_vox.py $pokeMFiles --output output/poke_m/structural-audit.json

& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_m/qa --script res://preview.gd --rendering-method gl_compatibility

python output/poke_m/compose_previews.py

python output/poke_m/validate.py

```



Automated rendering launches hidden and captures qa/render.log and qa/render-errors.log. Python generation uses the standard library; preview composition uses Pillow. generate.py owns families/palettes, sculpt.py dispatches geometry and creates the budding sapling, profiles.py builds profile crowns and conifers, leaves.py builds clustered/drooping leaves, and voxlib.py supplies VOX I/O. Source image, regions and shared palette are dependencies. Geometry module hashes are recorded in manifest.json.



The generator owns only its 56 named outputs and manifest. It refuses unknown or changed existing files unless `--replace-generated` is deliberately passed; preserve hand edits before that override. After revisions, refresh audits, renders, sheets and visual-review records. Keep future poke_m assets directly here with distinct names. No cell files are needed.





## Lights (2026-10-28)



[PokeM_BronzePostLantern](lights/README.md): seven complete variations with Emit materials, source notes, day/night previews and runtime validation.





## Rocks (2026-10-28)



[7 rock appearances, 49 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.



- [Flowers, bushes and grass](vegetation/README.md): 8 new appearances, 56 complete models, and existing-family reuse links.



## Buildings (2026-10-29)



- [Two buildings, 14 complete models](buildings/README.md): `PokeM_LogCabin` (the log cabin by the marsh) and `PokeM_Lodge` (the lodge, two copies each cut off by the image's edge, together showing it all but its front's left end), each in Base and all six variations, made on VCOM's tile grid at game scale (closed doors, MagicaVoxel Glass windows) as the poke_j buildings are, and tested in a copy of the game. [Overview](buildings/overview.png) | [File index](buildings/FILES.md).

## Complete bridges (2026-11-03)

[Bridge collection for this image](bridges/README.md): 1 new families, 7 complete VOX files with all seven treatments, source crops, cardinal/underside views and bank-placement previews. Existing assets are preserved. Shared validation and generation: [complete bridges](../bridges/README.md).


## Outdoor stairs — 2026-11-03

Added 2 families / 14 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [2 terrain styles, 112 complete models](terrain/README.md): `PokeM_GullyCliff_H3 (3 levels)`, `PokeM_RockMountain_H3 (3 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
