# poke_q.png — flowers, bushes and grass

8 new appearances; 56 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeQ_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[661, 605, 683, 625]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeQ_ShortGrassPatch_source.png) | [Seven treatments](PokeQ_ShortGrassPatch_variations.png) | [Four directions](PokeQ_ShortGrassPatch_geometry.png)

- [Base](../PokeQ_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeQ_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeQ_ShortGrassPatch_CratePalette.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [TwoColor](../PokeQ_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeQ_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeQ_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeQ_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeQ_GiantRedFlower

Canvas XYZ: **40 x 40 x 24**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[235, 330, 280, 371]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeQ_GiantRedFlower_source.png) | [Seven treatments](PokeQ_GiantRedFlower_variations.png) | [Four directions](PokeQ_GiantRedFlower_geometry.png)

- [Base](../PokeQ_GiantRedFlower.vox) — 1477 voxels; 5 paint colors; 1 rooted component(s).
- [Cartoon](../PokeQ_GiantRedFlower_Cartoon.vox) — 1528 voxels; 5 paint colors; 1 rooted component(s).
- [CratePalette](../PokeQ_GiantRedFlower_CratePalette.vox) — 1477 voxels; 4 paint colors; 1 rooted component(s).
- [TwoColor](../PokeQ_GiantRedFlower_TwoColor.vox) — 1477 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeQ_GiantRedFlower_Cartoon_TwoColor.vox) — 1528 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeQ_GiantRedFlower_CratePalette_TwoColor.vox) — 1477 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeQ_GiantRedFlower_Cartoon_CratePalette_TwoColor.vox) — 1528 voxels; 3 paint colors; 1 rooted component(s).

### PokeQ_PurpleBellFlower

Canvas XYZ: **16 x 16 x 28**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[523, 351, 545, 385]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeQ_PurpleBellFlower_source.png) | [Seven treatments](PokeQ_PurpleBellFlower_variations.png) | [Four directions](PokeQ_PurpleBellFlower_geometry.png)

- [Base](../PokeQ_PurpleBellFlower.vox) — 739 voxels; 6 paint colors; 1 rooted component(s).
- [Cartoon](../PokeQ_PurpleBellFlower_Cartoon.vox) — 892 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeQ_PurpleBellFlower_CratePalette.vox) — 739 voxels; 5 paint colors; 1 rooted component(s).
- [TwoColor](../PokeQ_PurpleBellFlower_TwoColor.vox) — 739 voxels; 2 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeQ_PurpleBellFlower_Cartoon_TwoColor.vox) — 892 voxels; 2 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeQ_PurpleBellFlower_CratePalette_TwoColor.vox) — 739 voxels; 2 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeQ_PurpleBellFlower_Cartoon_CratePalette_TwoColor.vox) — 892 voxels; 2 paint colors; 1 rooted component(s).

### PokeQ_PurpleSpatheFlower

Canvas XYZ: **24 x 24 x 40**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[302, 713, 330, 749]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeQ_PurpleSpatheFlower_source.png) | [Seven treatments](PokeQ_PurpleSpatheFlower_variations.png) | [Four directions](PokeQ_PurpleSpatheFlower_geometry.png)

- [Base](../PokeQ_PurpleSpatheFlower.vox) — 2479 voxels; 6 paint colors; 1 rooted component(s).
- [Cartoon](../PokeQ_PurpleSpatheFlower_Cartoon.vox) — 2808 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeQ_PurpleSpatheFlower_CratePalette.vox) — 2479 voxels; 4 paint colors; 1 rooted component(s).
- [TwoColor](../PokeQ_PurpleSpatheFlower_TwoColor.vox) — 2479 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeQ_PurpleSpatheFlower_Cartoon_TwoColor.vox) — 2808 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeQ_PurpleSpatheFlower_CratePalette_TwoColor.vox) — 2479 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeQ_PurpleSpatheFlower_Cartoon_CratePalette_TwoColor.vox) — 2808 voxels; 3 paint colors; 1 rooted component(s).

### PokeQ_DenseGroundHedge

Canvas XYZ: **32 x 32 x 20**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[351, 351, 393, 396]`. Dense low finely textured ground hedge; separate from tree canopy. Repeat this complete patch for broad beds.

[Source crop](PokeQ_DenseGroundHedge_source.png) | [Seven treatments](PokeQ_DenseGroundHedge_variations.png) | [Four directions](PokeQ_DenseGroundHedge_geometry.png)

- [Base](../PokeQ_DenseGroundHedge.vox) — 12059 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeQ_DenseGroundHedge_Cartoon.vox) — 12268 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeQ_DenseGroundHedge_CratePalette.vox) — 12059 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeQ_DenseGroundHedge_TwoColor.vox) — 12059 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeQ_DenseGroundHedge_Cartoon_TwoColor.vox) — 12268 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeQ_DenseGroundHedge_CratePalette_TwoColor.vox) — 12059 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeQ_DenseGroundHedge_Cartoon_CratePalette_TwoColor.vox) — 12268 voxels; 1 paint colors; 1 rooted component(s).

### PokeQ_TropicalLeafRosette

Canvas XYZ: **24 x 24 x 16**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[370, 478, 400, 513]`. 

[Source crop](PokeQ_TropicalLeafRosette_source.png) | [Seven treatments](PokeQ_TropicalLeafRosette_variations.png) | [Four directions](PokeQ_TropicalLeafRosette_geometry.png)

- [Base](../PokeQ_TropicalLeafRosette.vox) — 1044 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeQ_TropicalLeafRosette_Cartoon.vox) — 1056 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeQ_TropicalLeafRosette_CratePalette.vox) — 1044 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeQ_TropicalLeafRosette_TwoColor.vox) — 1044 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeQ_TropicalLeafRosette_Cartoon_TwoColor.vox) — 1056 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeQ_TropicalLeafRosette_CratePalette_TwoColor.vox) — 1044 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeQ_TropicalLeafRosette_Cartoon_CratePalette_TwoColor.vox) — 1056 voxels; 1 paint colors; 1 rooted component(s).

### PokeQ_WhiteDaisies

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[242, 254, 261, 274]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeQ_WhiteDaisies_source.png) | [Seven treatments](PokeQ_WhiteDaisies_variations.png) | [Four directions](PokeQ_WhiteDaisies_geometry.png)

- [Base](../PokeQ_WhiteDaisies.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeQ_WhiteDaisies_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeQ_WhiteDaisies_CratePalette.vox) — 85 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeQ_WhiteDaisies_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeQ_WhiteDaisies_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeQ_WhiteDaisies_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeQ_WhiteDaisies_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

### PokeQ_OrangeDaisies

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[348, 236, 371, 258]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeQ_OrangeDaisies_source.png) | [Seven treatments](PokeQ_OrangeDaisies_variations.png) | [Four directions](PokeQ_OrangeDaisies_geometry.png)

- [Base](../PokeQ_OrangeDaisies.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeQ_OrangeDaisies_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeQ_OrangeDaisies_CratePalette.vox) — 85 voxels; 7 paint colors; 3 rooted component(s).
- [TwoColor](../PokeQ_OrangeDaisies_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeQ_OrangeDaisies_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeQ_OrangeDaisies_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeQ_OrangeDaisies_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
