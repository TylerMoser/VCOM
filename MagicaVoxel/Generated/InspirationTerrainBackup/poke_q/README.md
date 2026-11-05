# poke_q tropical trees

Created 2026-10-27: **70 complete VOX files**, ten tree forms with Base and all six established variations. No per-cell files or automatic brush packages.

[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Source interpretation and scale

[poke_q.png](../../poke_q.png) is an 800 x 800 pixel-art map on a 16-pixel tile grid. Approximately one source pixel corresponds to one voxel; 16 voxels equal one game tile. Models are sized relative to their own sprites, including the large multi-tile vine tree and palms. Horizontal depth and hidden branches are inferred. Sprite projection mixes canopy depth with height, so these are authoring estimates, not exact physical reconstruction.

Ten forms are covered: the large vine canopy, clustered round crowns on branching wood, a low ring crown with upper cap, a flatter tiered spreading crown, a large leafy conifer, compact pointed tree, pear-shaped sapling, conical sapling, mature palm and palm seedling. Names describe appearance rather than verified species. Repeated and partly occluded placements are not extra types. Perched creatures, large flowers, crystals, dense ground hedges, rocks, architecture and source shadows are excluded. Hanging greenery attached to the large tree is included.

Source crop boxes have top-left XY origin and exclusive right/bottom edges. They include neighbors and sometimes overlapping foliage, not segmentation masks. Larger regional views preserve context. All models are Z-up, stand at z=0, are horizontally canvas-centered, and use scene translation `0 0 floor(height/2)` with no required facing direction.

| Base model | Canvas XYZ | Base occupied XYZ | Comparison |
| --- | --- | --- | --- |
| [PokeQ_VineCanopyTree](PokeQ_VineCanopyTree.vox) | 80 x 80 x 112 | 74 x 76 x 112 | [All styles](previews/PokeQ_VineCanopyTree_family.png) |
| [PokeQ_ClusterCrownTree](PokeQ_ClusterCrownTree.vox) | 48 x 48 x 64 | 42 x 43 x 64 | [All styles](previews/PokeQ_ClusterCrownTree_family.png) |
| [PokeQ_RingCrownTree](PokeQ_RingCrownTree.vox) | 48 x 48 x 40 | 46 x 46 x 40 | [All styles](previews/PokeQ_RingCrownTree_family.png) |
| [PokeQ_FlatTierTree](PokeQ_FlatTierTree.vox) | 48 x 48 x 48 | 44 x 44 x 48 | [All styles](previews/PokeQ_FlatTierTree_family.png) |
| [PokeQ_LeafyConifer](PokeQ_LeafyConifer.vox) | 56 x 56 x 72 | 52 x 52 x 72 | [All styles](previews/PokeQ_LeafyConifer_family.png) |
| [PokeQ_PointedTree](PokeQ_PointedTree.vox) | 32 x 32 x 48 | 32 x 31 x 48 | [All styles](previews/PokeQ_PointedTree_family.png) |
| [PokeQ_PearSapling](PokeQ_PearSapling.vox) | 16 x 16 x 32 | 15 x 15 x 32 | [All styles](previews/PokeQ_PearSapling_family.png) |
| [PokeQ_ConicalSapling](PokeQ_ConicalSapling.vox) | 16 x 16 x 28 | 15 x 14 x 28 | [All styles](previews/PokeQ_ConicalSapling_family.png) |
| [PokeQ_BeachPalm](PokeQ_BeachPalm.vox) | 64 x 64 x 72 | 59 x 54 x 72 | [All styles](previews/PokeQ_BeachPalm_family.png) |
| [PokeQ_PalmSeedling](PokeQ_PalmSeedling.vox) | 32 x 32 x 32 | 29 x 30 x 32 | [All styles](previews/PokeQ_PalmSeedling_family.png) |

## Modeling decisions

- VineCanopyTree uses an 80-wide crown and 112-high canvas. A flared trunk and branching wood support a broad connected upper canopy, lower leaf pads and attached hanging vines. Vines descend to varying heights in Base; Cartoon balances their arrangement and lengths.
- ClusterCrownTree has separate lower crown lobes and a raised upper lobe, with visible wood joining them. Base uses three lower lobes; Cartoon uses four.
- RingCrownTree has a low ring of foliage and a smaller upper cap separated by visible trunk. FlatTierTree retains a similar cleft but broader, flatter leaf masses and different proportions. Both remain connected through wood.
- LeafyConifer uses long overlapping leaf clusters in a tall tapered crown. PointedTree has a more compact solid profile.
- PearSapling and ConicalSapling have distinct small silhouettes; their internal woody stems remain connected to roots.
- BeachPalm has a root flare, ringed trunk, connected arching fronds with shallow edge notches, and central leaves. Base uses seven varied fronds; Cartoon uses eight balanced fronds.
- PalmSeedling has short wood at its base, low radiating leaves and an upright central leaf. It is a separate juvenile form, not a scaled mature trunk.

Geometry is filled where appropriate and all outputs are one connected component. Branch tubes provide structural attachment rather than leaving crown lobes floating. Base uses restrained asymmetry; Cartoon intentionally balances branches, fronds, vines, silhouettes and paint under exact horizontal quarter turns. Crown volumes and local foliage recipes are adapted from established families, with new tropical branching, ring, vine and seedling construction. All geometry modules are local copies, with no runtime dependency on other image folders.

## Variations and palettes

Follow the [shared specification](../../knowledge/VARIATIONS.md) for Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Base plus these six gives seven files per form. Color-only variants retain every coordinate, dimension and scene placement of their declared Base or Cartoon source.

Explicit semantic assignments group leaves, fronds, crown core and hanging leafy vines as foliage; trunks, roots, branches and internal woody stems as wood. Vines are interpreted as leafy greenery for the two-color split. Exactly two occupied indices with two distinct RGBA colors are used in every TwoColor treatment. Palm trunk rings lose their paint shading; leaf and vine geometry stays intact. Lighting still shades the two stored paint colors in previews.

Source-guided palettes use jungle greens, olive crown colors and lighter yellow-green conifer tips. CratePalette copies the entire pinned [crate palette](../../knowledge/palettes/crate-palette.json), maps foliage to 241-246 and wood to actual crate browns 178-180, and never occupies index 255. The two crate/two-color mixtures share selected group colors within each family. Exact mapping tables, representatives, output hashes, geometry authorities and module hashes are in the manifest.

## Validation and integration scope

[Structural audit](structural-audit.json) covers all 70 delivered files. Generation rereads serialized data and checks dimensions, bounds, connectedness, recolor coordinate equality, C4 geometry and paint, full reference palette identity and two-color counts. [Godot report](godot-validation.json) records whole Mesh imports at scale 0.0625 with retained voxel counts and grounded bounds, using the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final checks and visual review.

[Contact 1](previews/contact_01.png), [contact 2](previews/contact_02.png) and [contact 3](previews/contact_03.png) cover all treatments. [Geometry 1](previews/geometry_01.png), [geometry 2](previews/geometry_02.png) and [geometry 3](previews/geometry_03.png) show four azimuths for Base and Cartoon. Camera and lighting match within each family; families are independently framed, so card sizes do not imply equal world size.

This tests whole-model import/rendering, not combat gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. All forms exceed the 16-cubed PieceKind contract. VineCanopyTree occupies 74 voxels across X in Base and 76 in Cartoon, exceeding the separate 62-voxel loose-model limit. BeachPalm occupies 59 across X in Base and 62 in Cartoon, within that bound despite its 64-wide canvas; its separate runtime path is still untested. Preserve complete authoring dimensions and choose integration separately. Thin vines may disappear with distant scenery coarsening. VoxelXCOM remains unchanged. No cell files are needed for this authoring delivery.

## Reproduction and continuation

From the workspace root:

```powershell
python output/poke_q/generate.py
$pokeQFiles = (Get-ChildItem -LiteralPath output/poke_q -Filter *.vox -File).FullName
python tools/inspect_vox.py $pokeQFiles --output output/poke_q/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_q/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_q/compose_previews.py
python output/poke_q/validate.py
```

Automated rendering launches hidden with qa/render.log and qa/render-errors.log. Generation uses standard Python; comparison composition uses Pillow. generate.py owns families and palettes; sculpt.py owns tropical crowns, vines and seedling; profiles.py/leaves.py build established crown types; palm.py builds mature palms; voxlib.py supplies VOX I/O. The image, region JSON and shared palette are dependencies, with module hashes recorded.

The generator owns only its 70 named outputs and manifest. It refuses unknown or changed files unless `--replace-generated` is deliberately supplied; preserve hand edits before that override. After revisions, refresh audits, renders, comparisons and visual-review records. Store future poke_q models directly here with distinct names.


## Rocks (2026-10-28)

[5 rock appearances, 35 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.

- [Flowers, bushes and grass](vegetation/README.md): 8 new appearances, 56 complete models, and existing-family reuse links.


## Outdoor stairs — 2026-11-03

Added 2 families / 14 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [3 terrain styles, 147 complete models](terrain/README.md): `PokeQ_ClayTerrace_H3 (3 levels)`, `PokeQ_RockTerrace_H3 (3 levels)`, `PokeQ_CoastalCliff_H5 (5 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
