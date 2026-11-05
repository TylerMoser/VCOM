# poke_n.png — flowers, bushes and grass

6 new appearances; 42 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeN_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[366, 230, 388, 252]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeN_ShortGrassPatch_source.png) | [Seven treatments](PokeN_ShortGrassPatch_variations.png) | [Four directions](PokeN_ShortGrassPatch_geometry.png)

- [Base](../PokeN_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeN_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeN_ShortGrassPatch_CratePalette.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [TwoColor](../PokeN_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeN_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeN_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeN_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeN_PurpleFlowerSpikes

Canvas XYZ: **16 x 16 x 28**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[382, 190, 427, 224]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeN_PurpleFlowerSpikes_source.png) | [Seven treatments](PokeN_PurpleFlowerSpikes_variations.png) | [Four directions](PokeN_PurpleFlowerSpikes_geometry.png)

- [Base](../PokeN_PurpleFlowerSpikes.vox) — 851 voxels; 6 paint colors; 1 rooted component(s).
- [Cartoon](../PokeN_PurpleFlowerSpikes_Cartoon.vox) — 1892 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeN_PurpleFlowerSpikes_CratePalette.vox) — 851 voxels; 5 paint colors; 1 rooted component(s).
- [TwoColor](../PokeN_PurpleFlowerSpikes_TwoColor.vox) — 851 voxels; 2 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeN_PurpleFlowerSpikes_Cartoon_TwoColor.vox) — 1892 voxels; 2 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeN_PurpleFlowerSpikes_CratePalette_TwoColor.vox) — 851 voxels; 2 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeN_PurpleFlowerSpikes_Cartoon_CratePalette_TwoColor.vox) — 1892 voxels; 2 paint colors; 1 rooted component(s).

### PokeN_YellowStarFlowers

Canvas XYZ: **16 x 16 x 20**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[287, 416, 315, 441]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeN_YellowStarFlowers_source.png) | [Seven treatments](PokeN_YellowStarFlowers_variations.png) | [Four directions](PokeN_YellowStarFlowers_geometry.png)

- [Base](../PokeN_YellowStarFlowers.vox) — 280 voxels; 5 paint colors; 3 rooted component(s).
- [Cartoon](../PokeN_YellowStarFlowers_Cartoon.vox) — 420 voxels; 5 paint colors; 1 rooted component(s).
- [CratePalette](../PokeN_YellowStarFlowers_CratePalette.vox) — 280 voxels; 4 paint colors; 3 rooted component(s).
- [TwoColor](../PokeN_YellowStarFlowers_TwoColor.vox) — 280 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeN_YellowStarFlowers_Cartoon_TwoColor.vox) — 420 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeN_YellowStarFlowers_CratePalette_TwoColor.vox) — 280 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeN_YellowStarFlowers_Cartoon_CratePalette_TwoColor.vox) — 420 voxels; 3 paint colors; 1 rooted component(s).

### PokeN_PinkWhiteDaisies

Canvas XYZ: **16 x 16 x 7**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[460, 157, 488, 189]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeN_PinkWhiteDaisies_source.png) | [Seven treatments](PokeN_PinkWhiteDaisies_variations.png) | [Four directions](PokeN_PinkWhiteDaisies_geometry.png)

- [Base](../PokeN_PinkWhiteDaisies.vox) — 126 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeN_PinkWhiteDaisies_Cartoon.vox) — 200 voxels; 6 paint colors; 4 rooted component(s).
- [CratePalette](../PokeN_PinkWhiteDaisies_CratePalette.vox) — 126 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeN_PinkWhiteDaisies_TwoColor.vox) — 126 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeN_PinkWhiteDaisies_Cartoon_TwoColor.vox) — 200 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeN_PinkWhiteDaisies_CratePalette_TwoColor.vox) — 126 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeN_PinkWhiteDaisies_Cartoon_CratePalette_TwoColor.vox) — 200 voxels; 3 paint colors; 4 rooted component(s).

### PokeN_SubmergedFern

Canvas XYZ: **16 x 16 x 16**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[29, 687, 56, 715]`. 

[Source crop](PokeN_SubmergedFern_source.png) | [Seven treatments](PokeN_SubmergedFern_variations.png) | [Four directions](PokeN_SubmergedFern_geometry.png)

- [Base](../PokeN_SubmergedFern.vox) — 213 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeN_SubmergedFern_Cartoon.vox) — 200 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeN_SubmergedFern_CratePalette.vox) — 213 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeN_SubmergedFern_TwoColor.vox) — 213 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeN_SubmergedFern_Cartoon_TwoColor.vox) — 200 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeN_SubmergedFern_CratePalette_TwoColor.vox) — 213 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeN_SubmergedFern_Cartoon_CratePalette_TwoColor.vox) — 200 voxels; 1 paint colors; 1 rooted component(s).

### PokeN_FloatingLeafCluster

Canvas XYZ: **16 x 16 x 3**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[82, 657, 116, 685]`. 

[Source crop](PokeN_FloatingLeafCluster_source.png) | [Seven treatments](PokeN_FloatingLeafCluster_variations.png) | [Four directions](PokeN_FloatingLeafCluster_geometry.png)

- [Base](../PokeN_FloatingLeafCluster.vox) — 137 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeN_FloatingLeafCluster_Cartoon.vox) — 120 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeN_FloatingLeafCluster_CratePalette.vox) — 137 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeN_FloatingLeafCluster_TwoColor.vox) — 137 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeN_FloatingLeafCluster_Cartoon_TwoColor.vox) — 120 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeN_FloatingLeafCluster_CratePalette_TwoColor.vox) — 137 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeN_FloatingLeafCluster_Cartoon_CratePalette_TwoColor.vox) — 120 voxels; 1 paint colors; 4 rooted component(s).

## Reused models

- **PokeN_RoundShrub**: [Base](../../poke_n/PokeN_RoundShrub.vox), [Cartoon](../../poke_n/PokeN_RoundShrub_Cartoon.vox), [CratePalette](../../poke_n/PokeN_RoundShrub_CratePalette.vox), [TwoColor](../../poke_n/PokeN_RoundShrub_TwoColor.vox), [Cartoon_TwoColor](../../poke_n/PokeN_RoundShrub_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../poke_n/PokeN_RoundShrub_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../poke_n/PokeN_RoundShrub_Cartoon_CratePalette_TwoColor.vox).

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
