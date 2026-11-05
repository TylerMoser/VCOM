# poke_i.jpg — flowers, bushes and grass

6 new appearances; 42 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeI_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[640, 244, 714, 334]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeI_ShortGrassPatch_source.png) | [Seven treatments](PokeI_ShortGrassPatch_variations.png) | [Four directions](PokeI_ShortGrassPatch_geometry.png)

- [Base](../PokeI_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeI_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeI_ShortGrassPatch_CratePalette.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [TwoColor](../PokeI_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeI_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeI_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeI_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeI_YellowFlowerBed

Canvas XYZ: **16 x 16 x 16**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[267, 238, 304, 278]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeI_YellowFlowerBed_source.png) | [Seven treatments](PokeI_YellowFlowerBed_variations.png) | [Four directions](PokeI_YellowFlowerBed_geometry.png)

- [Base](../PokeI_YellowFlowerBed.vox) — 169 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeI_YellowFlowerBed_Cartoon.vox) — 300 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeI_YellowFlowerBed_CratePalette.vox) — 169 voxels; 4 paint colors; 3 rooted component(s).
- [TwoColor](../PokeI_YellowFlowerBed_TwoColor.vox) — 169 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeI_YellowFlowerBed_Cartoon_TwoColor.vox) — 300 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeI_YellowFlowerBed_CratePalette_TwoColor.vox) — 169 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeI_YellowFlowerBed_Cartoon_CratePalette_TwoColor.vox) — 300 voxels; 3 paint colors; 4 rooted component(s).

### PokeI_PaleWildflowers

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[449, 155, 474, 177]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeI_PaleWildflowers_source.png) | [Seven treatments](PokeI_PaleWildflowers_variations.png) | [Four directions](PokeI_PaleWildflowers_geometry.png)

- [Base](../PokeI_PaleWildflowers.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeI_PaleWildflowers_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeI_PaleWildflowers_CratePalette.vox) — 85 voxels; 7 paint colors; 3 rooted component(s).
- [TwoColor](../PokeI_PaleWildflowers_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeI_PaleWildflowers_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeI_PaleWildflowers_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeI_PaleWildflowers_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

### PokeI_CropSeedlings

Canvas XYZ: **16 x 16 x 8**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[382, 169, 414, 198]`. Small green shoots from cultivated rows; tilled soil excluded.

[Source crop](PokeI_CropSeedlings_source.png) | [Seven treatments](PokeI_CropSeedlings_variations.png) | [Four directions](PokeI_CropSeedlings_geometry.png)

- [Base](../PokeI_CropSeedlings.vox) — 314 voxels; 3 paint colors; 2 rooted component(s).
- [Cartoon](../PokeI_CropSeedlings_Cartoon.vox) — 348 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeI_CropSeedlings_CratePalette.vox) — 314 voxels; 2 paint colors; 2 rooted component(s).
- [TwoColor](../PokeI_CropSeedlings_TwoColor.vox) — 314 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_TwoColor](../PokeI_CropSeedlings_Cartoon_TwoColor.vox) — 348 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeI_CropSeedlings_CratePalette_TwoColor.vox) — 314 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeI_CropSeedlings_Cartoon_CratePalette_TwoColor.vox) — 348 voxels; 1 paint colors; 1 rooted component(s).

### PokeI_LeafyTallGrass

Canvas XYZ: **16 x 16 x 12**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[551, 117, 581, 136]`. 

[Source crop](PokeI_LeafyTallGrass_source.png) | [Seven treatments](PokeI_LeafyTallGrass_variations.png) | [Four directions](PokeI_LeafyTallGrass_geometry.png)

- [Base](../PokeI_LeafyTallGrass.vox) — 1659 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeI_LeafyTallGrass_Cartoon.vox) — 1808 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeI_LeafyTallGrass_CratePalette.vox) — 1659 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeI_LeafyTallGrass_TwoColor.vox) — 1659 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeI_LeafyTallGrass_Cartoon_TwoColor.vox) — 1808 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeI_LeafyTallGrass_CratePalette_TwoColor.vox) — 1659 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeI_LeafyTallGrass_Cartoon_CratePalette_TwoColor.vox) — 1808 voxels; 1 paint colors; 1 rooted component(s).

### PokeI_WaterLily

Canvas XYZ: **12 x 12 x 5**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[271, 354, 295, 373]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeI_WaterLily_source.png) | [Seven treatments](PokeI_WaterLily_variations.png) | [Four directions](PokeI_WaterLily_geometry.png)

- [Base](../PokeI_WaterLily.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [Cartoon](../PokeI_WaterLily_Cartoon.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeI_WaterLily_CratePalette.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [TwoColor](../PokeI_WaterLily_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeI_WaterLily_Cartoon_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeI_WaterLily_CratePalette_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeI_WaterLily_Cartoon_CratePalette_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

- **PokeI_HedgeShrub**: [Base](../../poke_i/PokeI_HedgeShrub.vox), [Cartoon](../../poke_i/PokeI_HedgeShrub_Cartoon.vox), [CratePalette](../../poke_i/PokeI_HedgeShrub_CratePalette.vox), [TwoColor](../../poke_i/PokeI_HedgeShrub_TwoColor.vox), [Cartoon_TwoColor](../../poke_i/PokeI_HedgeShrub_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../poke_i/PokeI_HedgeShrub_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../poke_i/PokeI_HedgeShrub_Cartoon_CratePalette_TwoColor.vox).

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
