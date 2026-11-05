# poke_c tree collection



56 complete VOX models, created 2026-10-26 from [poke_c.png](../../poke_c.png): eight appearances, each with Base and all six established variations. Final VOX files are directly in this folder. No cell pieces or brush packages.



[Rendered overview](overview.png) | [All files](FILES.md) | [Source catalogue](reference/catalogue.png) | [Family manifest](manifest.json)



## Reference interpretation and dimensions



The 800 x 752 image is consistent with a 50 x 47 map of 16-pixel tiles. As for poke_b, approximately one source pixel corresponds to one voxel, and 16 voxels correspond to one game tile. Visible sprite width/height guide the size; depth and unseen branches are inferred. Top-down sprite height includes perspective depth, so the chosen height is an authoring approximation, not a measured real-world height. Cast shadows, neighboring trees, creatures, grass, rocks and buildings are excluded.



There are six shape families and eight appearances: green and olive forest trees; olive and bright broadleaf trees; a spreading tree; a clustered tree; an oval sapling; and a tiered sapling. Repeated, partially occluded placements are not additional species. The names describe appearances without asserting botanical identities. There are no attached fruit/flower colorways in this collection; nearby creatures are not tree ornaments.



| Base model | Canvas XYZ (voxels) | Occupied XYZ | Canvas tiles XYZ | All seven styles |

| --- | --- | --- | --- | --- |

| [ForestGreen](PokeC_ForestGreen.vox) | 32 x 32 x 48 | 31 x 31 x 48 | 2.0 x 2.0 x 3.0 | [Comparison](previews/PokeC_ForestGreen_family.png) |

| [ForestOlive](PokeC_ForestOlive.vox) | 32 x 32 x 48 | 31 x 31 x 48 | 2.0 x 2.0 x 3.0 | [Comparison](previews/PokeC_ForestOlive_family.png) |

| [BroadleafOlive](PokeC_BroadleafOlive.vox) | 32 x 32 x 40 | 31 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Comparison](previews/PokeC_BroadleafOlive_family.png) |

| [SpreadingTree](PokeC_SpreadingTree.vox) | 48 x 48 x 48 | 47 x 47 x 48 | 3.0 x 3.0 x 3.0 | [Comparison](previews/PokeC_SpreadingTree_family.png) |

| [ClusteredTree](PokeC_ClusteredTree.vox) | 48 x 48 x 40 | 45 x 44 x 40 | 3.0 x 3.0 x 2.5 | [Comparison](previews/PokeC_ClusteredTree_family.png) |

| [OvalSapling](PokeC_OvalSapling.vox) | 16 x 16 x 28 | 16 x 15 x 28 | 1.0 x 1.0 x 1.75 | [Comparison](previews/PokeC_OvalSapling_family.png) |

| [TieredSapling](PokeC_TieredSapling.vox) | 12 x 12 x 32 | 11 x 11 x 32 | 0.75 x 0.75 x 2.0 | [Comparison](previews/PokeC_TieredSapling_family.png) |

| [BroadleafBright](PokeC_BroadleafBright.vox) | 32 x 32 x 40 | 31 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Comparison](previews/PokeC_BroadleafBright_family.png) |



All files are Z-up and grounded at z=0, horizontally centered on the canvas, with graph translation `0 0 floor(height/2)`. They have no required front direction. Godot Mesh import scale is 0.0625. The manifest records exact occupied minima/maxima and counts for every output, including Cartoon. Previews are independently framed between families; a sapling is not actually as large as a forest tree.



## Shape decisions



- Forest trees: drooping, overlapping leaf skirts, a pointed leader and a short visible trunk. Two muted green/olive palettes distinguish the source colorways.

- Broadleaf trees: a rounder, shorter crown with scalloped contours and a pointed top, in olive and brighter green. These colorways share geometry.

- Spreading tree: a wide lower crown surrounding a visible central cleft and wood stem, with a smaller upper crown. The hidden structure joins the masses into a complete solid tree.

- Clustered tree: individually rounded side pads, staggered slightly in Base, around a central woody structure and smaller upper pad. Cartoon balances four side pads. This is distinct from the spreading tree and its central opening.

- Oval sapling: compact, narrow oval crown, muted gray-green leaves and a short woody base.

- Tiered sapling: a slender exposed pale stem with a small tiered green crown. Pale bark is preserved in TwoColor; it is not forced to brown merely because other trees have brown trunks.



Base palettes are artist-selected approximations of the reference colors, not a claim of exact pixel sampling. Base geometry is a volumetric reconstruction, not an extrusion of the image. Solid interiors, continuous trunks, root flares and branch supports allow coherent inspection from other sides.



## Styles and palette rules



Follow [the shared variation specification](../../knowledge/VARIATIONS.md). Each family contains Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Cartoon is exactly quarter-turn symmetric in occupied coordinates and paint. Its mixtures inherit that exact geometry. All other recolors inherit Base occupancy, dimensions and placement.



The two semantic groups are foliage (all leaves) and wood (trunk, roots, branches and hidden core), recorded as explicit coordinate assignments during sculpting. Every TwoColor output uses exactly two palette indices with two distinct RGBA colors. Normal rendered lighting adds visible shading without adding stored paint colors.



CratePalette outputs retain the complete pinned [crate RGBA snapshot](../../knowledge/palettes/crate-palette.json) byte-for-byte. Foliage maps into slots 241-246. Normal bark uses slots 178-180; the pale tiered-sapling stem uses existing light neutral slots 193-196. The two game colors are chosen once per family and reused in both relevant mixtures. Full remaps and actual representative RGBA values are in manifest.json. Distinct source colorways can converge under the reduced game palette; keep their named files to retain source provenance. Index 255 is reserved and never occupied.



## Validation and integration scope



[Structural audit](structural-audit.json): 56 delivered files, zero errors and zero warnings. Generation rereads the serialized files and checks dimensions, bounds, palette entries, coordinate preservation, connectedness, symmetry and color counts. All models are a single six-connected component.



[Godot validation](godot-validation.json) records complete mesh imports, retained voxel counts and grounded mesh bounds at scale 0.0625. The current sibling VCOM importer was copied with its license and [source hashes](qa/source-provenance.json); the game itself was not edited. [Validation summary](validation-summary.json) records final file hashes and visual review evidence.



The contact sheets cover all 56 models; four-angle geometry sheets cover every Base and Cartoon. The comparison camera and lighting remain the same within each family. Import/render testing does not establish combat-map, movement, cover or destruction behavior. No gameplay integration or MagicaVoxel GUI test is claimed.



Every model exceeds the single-cell PieceKind 16-cubed contract in height. Their widths remain below the current loose-model X limit of 62, but that runtime path was not tested here. Integrate separately when requested. Do not generate cell pieces merely to work around runtime limits.



## Reproduction and continuation



From the workspace root:



```powershell

python output/poke_c/generate.py

$pokeCFiles = (Get-ChildItem -LiteralPath output/poke_c -Filter *.vox -File).FullName

python tools/inspect_vox.py $pokeCFiles --output output/poke_c/structural-audit.json

& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_c/qa --script res://preview.gd --rendering-method gl_compatibility

python output/poke_c/compose_previews.py

```



Automated rendering uses Start-Process with WindowStyle Hidden and captures `qa/render.log` and `qa/render-errors.log`. The generation scripts require standard Python; composition requires Pillow. `sculpt.py` owns image-specific geometry, `generate.py` owns families/colors/variation generation and serialized checks, and `voxlib.py` supplies the local VOX helpers. No generator imports another image folder.



Generation rewrites its named outputs and manifest, after comparing existing VOX hashes to the preceding manifest. Unknown or modified files are refused; `--replace-generated` bypasses that protection only for deliberate revisions. Preserve hand edits before using it. Palette snapshot, source image, and helpers are dependencies. Source-region boxes are contextual crops, not exact masks, with top-left XY and exclusive right/bottom coordinates.



After changes, regenerate the relevant previews/audits and update the validation summary. Keep new assets and revisions from poke_c in this folder with distinct descriptive filenames; do not alter poke_a/poke_b models as a side effect.



## Buildings (2026-10-28)



The buildings of poke_c.png are a separate collection in this folder: five families (two cottages, the manor, the covered bridge's pavilion and span), 35 complete models in Base and all six treatments, drawn on VCOM's tile grid with glass so they go into the game cleanly. Their files are here beside the trees; their generator, records, previews and game test are in [buildings/](buildings/README.md), which leaves the tree files above unchanged.





## Lights (2026-10-28)



[PokeC_SilverStreetLantern](lights/README.md): seven complete variations with Emit materials, source notes, day/night previews and runtime validation.





## Rocks (2026-10-28)



[2 rock appearances, 14 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.



- [Flowers, bushes and grass](vegetation/README.md): 5 new appearances, 35 complete models, and existing-family reuse links.

## Complete bridges (2026-11-03)

[Bridge collection for this image](bridges/README.md): 1 new families, 7 complete VOX files with all seven treatments, source crops, cardinal/underside views and bank-placement previews. Existing assets are preserved. Shared validation and generation: [complete bridges](../bridges/README.md).


## Outdoor stairs — 2026-11-03

Added 4 families / 28 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [1 terrain style, 63 complete models](terrain/README.md): `PokeC_BlockCliff_H3 (3 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
