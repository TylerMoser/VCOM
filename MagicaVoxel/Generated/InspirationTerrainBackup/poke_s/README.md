# poke_s pastel sky-garden trees



## Ruins and temple architecture — 2026-11-03



[Architecture collection](ruins/README.md): 11 families, 77 complete models with all seven treatments; [overview](ruins/overview.png), [temple assembly](ruins/temple_assembly.png), source crops, generator and validation. Includes the raised court/wing, round garden terraces, columns, arches, two sanctuaries and retaining walls. All final files use `PokeS_Ruins…` names directly in this folder. Existing trees and props are preserved and reused.



## Original tree collection



Created 2026-10-27: **147 complete VOX files**, 21 source appearances with Base and all six established variations. Complete models only; no per-cell files or brush packages.



[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)



## Source interpretation and scale



The requested poke_s.png is present as [poke_s.jpg](../../poke_s.jpg), an 894 x 894 compressed and reduced map. Paving and repeated scenery suggest roughly 10 displayed pixels per original tile. We interpret that as 16 voxels per tile (approximately 1.6 voxels per displayed pixel), rather than assuming JPEG pixels are native sprite pixels. This is an estimate; the original tileset is unavailable. Compression, clouds and overlap reduce confidence in small details. Source crop boxes include context, not segmentation masks, and use top-left XY with exclusive right/bottom edges.



Coverage: tiered crowns in mint, teal, pink and gold; tall leafy trees in mint, teal and pink; clustered crowns in teal and gold; green flat-tier crown; pale-trunk ornamentals in mint, teal, pink and gold; narrow saplings in all four colors; compact round shrubs in mint, teal and pink. The named appearances are observed shape/color families, not botanical species. Repeated, cloud-covered or overlapping copies are not additional types. Flowers, grasses, creatures, architecture, clouds and ground shadows are excluded. The small mint examples are partly occluded; their basic form is inferred from the visible crown and corresponding clear colorways.



Tiered crowns use 32 x 32 x 48; tall leafy trees 48 x 48 x 80; clustered crowns 48 x 48 x 64; flat tier 48 x 48 x 48; ornamentals 32 x 32 x 64; narrow saplings 12 x 12 x 28; shrubs 24 x 24 x 28. Depth and unseen branches are inferred. Projection mixes canopy depth with height, so these are relative authoring sizes, not exact physical recovery. Colorways of the same form share geometry.



All models are Z-up, stand at z=0, are horizontally canvas-centered, and use scene translation `0 0 floor(height/2)`, with no required facing direction.



| Base model | Canvas XYZ | Base occupied XYZ | Comparison |

| --- | --- | --- | --- |

| [PokeS_TieredMint](PokeS_TieredMint.vox) | 32 x 32 x 48 | 30 x 30 x 48 | [All styles](previews/PokeS_TieredMint_family.png) |

| [PokeS_TieredTeal](PokeS_TieredTeal.vox) | 32 x 32 x 48 | 30 x 30 x 48 | [All styles](previews/PokeS_TieredTeal_family.png) |

| [PokeS_TieredPink](PokeS_TieredPink.vox) | 32 x 32 x 48 | 30 x 30 x 48 | [All styles](previews/PokeS_TieredPink_family.png) |

| [PokeS_TieredGold](PokeS_TieredGold.vox) | 32 x 32 x 48 | 30 x 30 x 48 | [All styles](previews/PokeS_TieredGold_family.png) |

| [PokeS_TallMint](PokeS_TallMint.vox) | 48 x 48 x 80 | 44 x 44 x 80 | [All styles](previews/PokeS_TallMint_family.png) |

| [PokeS_TallTeal](PokeS_TallTeal.vox) | 48 x 48 x 80 | 44 x 44 x 80 | [All styles](previews/PokeS_TallTeal_family.png) |

| [PokeS_TallPink](PokeS_TallPink.vox) | 48 x 48 x 80 | 44 x 44 x 80 | [All styles](previews/PokeS_TallPink_family.png) |

| [PokeS_ClusterTeal](PokeS_ClusterTeal.vox) | 48 x 48 x 64 | 42 x 43 x 64 | [All styles](previews/PokeS_ClusterTeal_family.png) |

| [PokeS_ClusterGold](PokeS_ClusterGold.vox) | 48 x 48 x 64 | 42 x 43 x 64 | [All styles](previews/PokeS_ClusterGold_family.png) |

| [PokeS_FlatTierGreen](PokeS_FlatTierGreen.vox) | 48 x 48 x 48 | 44 x 44 x 48 | [All styles](previews/PokeS_FlatTierGreen_family.png) |

| [PokeS_OrnamentalMint](PokeS_OrnamentalMint.vox) | 32 x 32 x 64 | 29 x 28 x 63 | [All styles](previews/PokeS_OrnamentalMint_family.png) |

| [PokeS_OrnamentalTeal](PokeS_OrnamentalTeal.vox) | 32 x 32 x 64 | 29 x 28 x 63 | [All styles](previews/PokeS_OrnamentalTeal_family.png) |

| [PokeS_OrnamentalPink](PokeS_OrnamentalPink.vox) | 32 x 32 x 64 | 29 x 28 x 63 | [All styles](previews/PokeS_OrnamentalPink_family.png) |

| [PokeS_OrnamentalGold](PokeS_OrnamentalGold.vox) | 32 x 32 x 64 | 29 x 28 x 63 | [All styles](previews/PokeS_OrnamentalGold_family.png) |

| [PokeS_SaplingMint](PokeS_SaplingMint.vox) | 12 x 12 x 28 | 11 x 10 x 28 | [All styles](previews/PokeS_SaplingMint_family.png) |

| [PokeS_SaplingTeal](PokeS_SaplingTeal.vox) | 12 x 12 x 28 | 11 x 10 x 28 | [All styles](previews/PokeS_SaplingTeal_family.png) |

| [PokeS_SaplingPink](PokeS_SaplingPink.vox) | 12 x 12 x 28 | 11 x 10 x 28 | [All styles](previews/PokeS_SaplingPink_family.png) |

| [PokeS_SaplingGold](PokeS_SaplingGold.vox) | 12 x 12 x 28 | 11 x 10 x 28 | [All styles](previews/PokeS_SaplingGold_family.png) |

| [PokeS_ShrubMint](PokeS_ShrubMint.vox) | 24 x 24 x 28 | 24 x 23 x 28 | [All styles](previews/PokeS_ShrubMint_family.png) |

| [PokeS_ShrubTeal](PokeS_ShrubTeal.vox) | 24 x 24 x 28 | 24 x 23 x 28 | [All styles](previews/PokeS_ShrubTeal_family.png) |

| [PokeS_ShrubPink](PokeS_ShrubPink.vox) | 24 x 24 x 28 | 24 x 23 x 28 | [All styles](previews/PokeS_ShrubPink_family.png) |



## Geometry and semantic materials



Tiered crowns use overlapping rounded leaf clusters; tall trees use longer drooping clusters. Cluster crowns have three lower lobes in Base and four in Cartoon, supported by visible branching wood below a top lobe. FlatTierGreen has thin spreading shelves and a separate upper cap. Saplings use narrow columnar crowns; shrubs use compact rounded crowns and small inferred woody bases.



Ornamentals have thin pale trunks, ascending forks and pointed diamond-shaped leaf groups at several heights. Base branches are irregular; Cartoon uses balanced cardinal forks. Their light bark is wood, not foliage. The source's delicate shapes are interpreted volumetrically rather than extruded from the sprite. All outputs remain one connected component, including branches and leaves.



Base uses restrained asymmetry and coherent painted regions. Cartoon changes geometry deliberately and applies exact horizontal quarter-turn symmetry to occupancy and paint. Local geometry modules adapt established crown recipes and add the pale-trunk ornamental construction. They have no runtime dependency on other image folders.



## Variations and palette choices



The [shared specification](../../knowledge/VARIATIONS.md) defines Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Each recolor preserves every coordinate, canvas and scene placement of its declared Base or Cartoon authority.



Explicit coordinate groups separate foliage/crown core from wood/trunks/roots/branches. TwoColor uses exactly two occupied indices with distinct RGBA colors, one per group. Ornamentals use pale wood as their second source-color representative; the other families use brown wood. Lighting still shades these two paint colors in previews.



CratePalette copies the complete pinned [crate palette](../../knowledge/palettes/crate-palette.json). Mint/green foliage maps to the saved green ramp 241-246. Teal, pink and gold foliage searches all existing usable entries 1-254 for the nearest RGB color, preserving the source hue as far as the palette permits. Brown wood maps to 178-180; ornamental pale bark maps to light neutral entries 193-196. Both crate/two-color mixtures share selected group colors per family. If nearest foliage and wood map to the same RGBA, the nearest distinct foliage choice is used, preserving exactly two colors. Index 255 is unused. Exact mapping tables and representatives in manifest.json are authoritative; CratePalette may shift or compress the pastel ramps but never invents colors.



## Validation and integration



[Structural audit](structural-audit.json) covers 147 files. Generation rereads every output and checks dimensions, bounds, connectivity, exact recolor coordinates, C4 geometry/paint, full reference palette identity and two-color counts. [Godot report](godot-validation.json) records whole Mesh imports at scale 0.0625 with retained voxel counts and grounded bounds using the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final checks and visual review.



Six contact sheets cover all 21 appearances and seven treatments each; six geometry sheets show Base and Cartoon at four azimuths. Camera and lighting match within a family; different families are independently framed, so card size is not world scale. Each family also has a source-and-variants comparison linked above.



These checks exercise whole-model import/rendering, not gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. Every model exceeds the 16-cubed PieceKind contract. Widths are below the separate 62-voxel loose-model limit, but that path is untested. Fine ornamental branches may be lost with distant scenery coarsening. VoxelXCOM remains unchanged. Handle integration separately without automatically creating cell files.



## Reproduce and continue



From the workspace root:



```powershell

python output/poke_s/generate.py

$pokeSFiles = (Get-ChildItem -LiteralPath output/poke_s -Filter *.vox -File).FullName

python tools/inspect_vox.py $pokeSFiles --output output/poke_s/structural-audit.json

& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_s/qa --script res://preview.gd --rendering-method gl_compatibility

python output/poke_s/compose_previews.py

python output/poke_s/validate.py

```



Automated rendering launches hidden with qa/render.log and qa/render-errors.log. Generation uses standard Python; composition uses Pillow. Local generate.py, sculpt.py, profiles.py, leaves.py, crowns.py, palm.py and voxlib.py, source regions/image and the shared palette are dependencies. Some inherited geometry helpers are unused by this family but retained to keep local imports self-contained; hashes are recorded in the manifest.



The generator owns only its 147 named files and manifest. It refuses unknown or changed files unless `--replace-generated` is deliberately supplied; preserve hand edits before overriding. After revisions, refresh audits, renders, comparisons and visual-review records. Keep future poke_s models directly here with distinct names.





## Lights (2026-10-28)



[PokeS_IvoryScrollLantern](lights/README.md): seven complete variations with Emit materials, source notes, day/night previews and runtime validation.





## Rocks (2026-10-28)



[4 rock appearances, 28 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.



- [Flowers, bushes and grass](vegetation/README.md): 5 new appearances, 35 complete models, and existing-family reuse links.

## Complete bridges (2026-11-03)

[Bridge collection for this image](bridges/README.md): 1 new families, 7 complete VOX files with all seven treatments, source crops, cardinal/underside views and bank-placement previews. Existing assets are preserved. Shared validation and generation: [complete bridges](../bridges/README.md).


## Outdoor stairs — 2026-11-03

Added 2 families / 14 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [2 terrain styles, 147 complete models](terrain/README.md): `PokeS_IslandRim_H3 (3 levels)`, `PokeS_Terrace_H2 (2 levels)` and 2 whole small islands (`PokeS_SmallIsland`, `PokeS_Islet`), modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
