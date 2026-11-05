# poke_a — complete tree models

All deliverables are complete models. Per the user's instruction on 2026-10-26, the earlier cell-by-cell files were deleted and are not required. Generators no longer create them, and current manifests and preview scripts do not depend on them.

| File | Canvas | Occupied size | Voxels |
| --- | --- | --- | ---: |
| [Large forest tree](PokeA_ForestTree_Large.vox) | 32×32×64 | 32×32×64 | 24,888 |
| [Original forest tree](PokeA_ForestTree.vox) | 16×16×32 | 16×14×28 | 2,183 |
| [Sapling](PokeA_Sapling.vox) | 16³ | 8×7×15 | 291 |

The large tree spans **2×2 tiles and 4 levels** at scale 0.0625. It retains the original tree's rounded leaf tiers, pointed crown, green-to-teal palette and brown wooden core, with geometry evaluated at the larger resolution. It is not just an enlarged canvas or a blocky nearest-neighbor resize. The earlier trees remain available as smaller variants.

## Style variations

Nine additional complete models are available: Cartoon, CratePalette and TwoColor versions of each tree above. See [the variation file index and comparison](VARIATIONS.md) for downloads, exact color/symmetry guarantees, and regeneration instructions.

## Reference interpretation

Source: `../../poke_a.jpg` (735×480). This is a wooded, terraced route with cliff shelves, streams, waterfalls, bridge, paths, flowers and low shrubs. Two tree forms are visible: the mature forest tree repeated in dense stands and the much smaller sapling on ledges and paths. Examples occur around (119,135) and (102,130). Hidden and overlapped trees were not counted as extra species; low repeated shrubs are separate objects. Unseen sides are inferred from the source's single stylized viewpoint.

The shared 15-entry palette preserves yellow-green upper foliage, dark teal lower leaves and brown bark. Index 255 is unused. Models are solid and face-connected, with wooden cores and buttress roots. All materials are diffuse. MagicaVoxel axes are Z-up; the grounded scene translations are `0 0 32` for the large tree, `0 0 16` for the original and `0 0 8` for the sapling.

## Generation and records

- `generate_trees.py`: writes only the original complete tree, sapling and `manifest.json`.
- `generate_large_tree.py`: writes only the large complete tree and `large-manifest.json`; imports palette/writer helpers from the first script without invoking its main.
- Both generators are deterministic. They overwrite their named outputs; preserve hand edits under a new name before regenerating.
- `vox-audit.json` and `large-vox-audit.json` describe only the surviving complete files.
- `qa/preview.gd` and `qa/preview_large.gd` import and render complete models directly, without any cell files.
- Older runtime split tests are retained under `qa/historical/` solely as historical evidence. Their deleted filenames are not current deliverables or dependencies. Earlier assembly previews are likewise historical.

## Validation and game integration

The complete files passed binary audits and connectivity checks. Before the cell files were removed, the large tree's 24,888 voxels were also verified through the game's terrain reader as an exact assembly; those results are historical, not an instruction to recreate parts. Current previews use the game's unmodified whole-model MagicaVoxel importer, which handles the complete 64-tall tree.

At game scale 0.0625, the current PieceKind terrain reader supports 16³ cells. Separately, VoxelModel's custom mesher has a 62-voxel maximum side, so the complete 64-tall tree cannot be handed to that mesher unchanged. These are integration constraints to resolve if game integration is requested, not reasons to split the delivered art. No integration or combat/destruction playtest was performed, and VoxelXCOM remains unchanged.

Use [the larger tree comparison](previews/large_tree_0.png) for scale (large tree on left, original on right; grid spacing is one game tile). The comparison was rendered from the former temporary terrain pieces; geometry exactly matches the surviving complete tree. `previews/complete_large_tree_*.png` are direct whole-model previews when the current QA script is run. Reference crops and earlier small-tree previews are retained in `previews/`.

## Combined styles

[Cartoon + TwoColor, CratePalette + TwoColor, and all three combined](MIXTURES.md) are available for each tree: nine additional complete models with a labeled preview and validation records.


## Rocks (2026-10-28)

[1 rock appearances, 7 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.

- [Flowers, bushes and grass](vegetation/README.md): 5 new appearances, 35 complete models, and existing-family reuse links.

## Complete bridges (2026-11-03)

[Bridge collection for this image](bridges/README.md): 1 new families, 7 complete VOX files with all seven treatments, source crops, cardinal/underside views and bank-placement previews. Existing assets are preserved. Shared validation and generation: [complete bridges](../bridges/README.md).

## Terrain (2026-11-04)

- [1 terrain style, 63 complete models](terrain/README.md): `PokeA_EarthCliff_H3 (3 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
