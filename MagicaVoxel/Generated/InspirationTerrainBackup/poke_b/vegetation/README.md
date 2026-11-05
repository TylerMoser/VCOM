# poke_b.png — flowers, bushes and grass

4 new appearances; 28 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeB_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[375, 99, 397, 120]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeB_ShortGrassPatch_source.png) | [Seven treatments](PokeB_ShortGrassPatch_variations.png) | [Four directions](PokeB_ShortGrassPatch_geometry.png)

- [Base](../PokeB_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeB_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeB_ShortGrassPatch_CratePalette.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [TwoColor](../PokeB_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeB_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeB_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeB_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeB_PinkDaisies

Canvas XYZ: **16 x 16 x 7**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[363, 108, 385, 130]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeB_PinkDaisies_source.png) | [Seven treatments](PokeB_PinkDaisies_variations.png) | [Four directions](PokeB_PinkDaisies_geometry.png)

- [Base](../PokeB_PinkDaisies.vox) — 126 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeB_PinkDaisies_Cartoon.vox) — 200 voxels; 6 paint colors; 4 rooted component(s).
- [CratePalette](../PokeB_PinkDaisies_CratePalette.vox) — 126 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeB_PinkDaisies_TwoColor.vox) — 126 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeB_PinkDaisies_Cartoon_TwoColor.vox) — 200 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeB_PinkDaisies_CratePalette_TwoColor.vox) — 126 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeB_PinkDaisies_Cartoon_CratePalette_TwoColor.vox) — 200 voxels; 3 paint colors; 4 rooted component(s).

### PokeB_GardenBlades

Canvas XYZ: **16 x 16 x 22**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[554, 706, 581, 736]`. 

[Source crop](PokeB_GardenBlades_source.png) | [Seven treatments](PokeB_GardenBlades_variations.png) | [Four directions](PokeB_GardenBlades_geometry.png)

- [Base](../PokeB_GardenBlades.vox) — 281 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeB_GardenBlades_Cartoon.vox) — 452 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeB_GardenBlades_CratePalette.vox) — 281 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeB_GardenBlades_TwoColor.vox) — 281 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeB_GardenBlades_Cartoon_TwoColor.vox) — 452 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeB_GardenBlades_CratePalette_TwoColor.vox) — 281 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeB_GardenBlades_Cartoon_CratePalette_TwoColor.vox) — 452 voxels; 1 paint colors; 1 rooted component(s).

### PokeB_GardenFlower

Canvas XYZ: **12 x 12 x 16**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[541, 693, 563, 719]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeB_GardenFlower_source.png) | [Seven treatments](PokeB_GardenFlower_variations.png) | [Four directions](PokeB_GardenFlower_geometry.png)

- [Base](../PokeB_GardenFlower.vox) — 146 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeB_GardenFlower_Cartoon.vox) — 260 voxels; 5 paint colors; 1 rooted component(s).
- [CratePalette](../PokeB_GardenFlower_CratePalette.vox) — 146 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeB_GardenFlower_TwoColor.vox) — 146 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeB_GardenFlower_Cartoon_TwoColor.vox) — 260 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeB_GardenFlower_CratePalette_TwoColor.vox) — 146 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeB_GardenFlower_Cartoon_CratePalette_TwoColor.vox) — 260 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
