# poke_m.png — flowers, bushes and grass

8 new appearances; 56 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeM_BankReeds

Canvas XYZ: **16 x 16 x 28**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[206, 92, 230, 131]`. 

[Source crop](PokeM_BankReeds_source.png) | [Seven treatments](PokeM_BankReeds_variations.png) | [Four directions](PokeM_BankReeds_geometry.png)

- [Base](../PokeM_BankReeds.vox) — 341 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeM_BankReeds_Cartoon.vox) — 572 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeM_BankReeds_CratePalette.vox) — 341 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeM_BankReeds_TwoColor.vox) — 341 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeM_BankReeds_Cartoon_TwoColor.vox) — 572 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeM_BankReeds_CratePalette_TwoColor.vox) — 341 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeM_BankReeds_Cartoon_CratePalette_TwoColor.vox) — 572 voxels; 1 paint colors; 1 rooted component(s).

### PokeM_LowMeadowGrass

Canvas XYZ: **16 x 16 x 12**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[120, 717, 154, 750]`. 

[Source crop](PokeM_LowMeadowGrass_source.png) | [Seven treatments](PokeM_LowMeadowGrass_variations.png) | [Four directions](PokeM_LowMeadowGrass_geometry.png)

- [Base](../PokeM_LowMeadowGrass.vox) — 468 voxels; 3 paint colors; 2 rooted component(s).
- [Cartoon](../PokeM_LowMeadowGrass_Cartoon.vox) — 528 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeM_LowMeadowGrass_CratePalette.vox) — 468 voxels; 2 paint colors; 2 rooted component(s).
- [TwoColor](../PokeM_LowMeadowGrass_TwoColor.vox) — 468 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_TwoColor](../PokeM_LowMeadowGrass_Cartoon_TwoColor.vox) — 528 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeM_LowMeadowGrass_CratePalette_TwoColor.vox) — 468 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeM_LowMeadowGrass_Cartoon_CratePalette_TwoColor.vox) — 528 voxels; 1 paint colors; 1 rooted component(s).

### PokeM_SubmergedReeds

Canvas XYZ: **16 x 16 x 20**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[303, 159, 326, 191]`. Underwater color appearance, opaque geometry; water surface not included.

[Source crop](PokeM_SubmergedReeds_source.png) | [Seven treatments](PokeM_SubmergedReeds_variations.png) | [Four directions](PokeM_SubmergedReeds_geometry.png)

- [Base](../PokeM_SubmergedReeds.vox) — 265 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeM_SubmergedReeds_Cartoon.vox) — 416 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeM_SubmergedReeds_CratePalette.vox) — 265 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeM_SubmergedReeds_TwoColor.vox) — 265 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeM_SubmergedReeds_Cartoon_TwoColor.vox) — 416 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeM_SubmergedReeds_CratePalette_TwoColor.vox) — 265 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeM_SubmergedReeds_Cartoon_CratePalette_TwoColor.vox) — 416 voxels; 1 paint colors; 1 rooted component(s).

### PokeM_AquaticRosette

Canvas XYZ: **16 x 16 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[221, 303, 244, 325]`. 

[Source crop](PokeM_AquaticRosette_source.png) | [Seven treatments](PokeM_AquaticRosette_variations.png) | [Four directions](PokeM_AquaticRosette_geometry.png)

- [Base](../PokeM_AquaticRosette.vox) — 234 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeM_AquaticRosette_Cartoon.vox) — 248 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeM_AquaticRosette_CratePalette.vox) — 234 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeM_AquaticRosette_TwoColor.vox) — 234 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeM_AquaticRosette_Cartoon_TwoColor.vox) — 248 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeM_AquaticRosette_CratePalette_TwoColor.vox) — 234 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeM_AquaticRosette_Cartoon_CratePalette_TwoColor.vox) — 248 voxels; 1 paint colors; 1 rooted component(s).

### PokeM_WaterLily

Canvas XYZ: **12 x 12 x 5**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[315, 285, 340, 307]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeM_WaterLily_source.png) | [Seven treatments](PokeM_WaterLily_variations.png) | [Four directions](PokeM_WaterLily_geometry.png)

- [Base](../PokeM_WaterLily.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [Cartoon](../PokeM_WaterLily_Cartoon.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeM_WaterLily_CratePalette.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [TwoColor](../PokeM_WaterLily_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeM_WaterLily_Cartoon_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeM_WaterLily_CratePalette_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeM_WaterLily_Cartoon_CratePalette_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).

### PokeM_PinkWildflowers

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[665, 316, 689, 339]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeM_PinkWildflowers_source.png) | [Seven treatments](PokeM_PinkWildflowers_variations.png) | [Four directions](PokeM_PinkWildflowers_geometry.png)

- [Base](../PokeM_PinkWildflowers.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeM_PinkWildflowers_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeM_PinkWildflowers_CratePalette.vox) — 85 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeM_PinkWildflowers_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeM_PinkWildflowers_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeM_PinkWildflowers_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeM_PinkWildflowers_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

### PokeM_BlueWildflowers

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[650, 332, 672, 352]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeM_BlueWildflowers_source.png) | [Seven treatments](PokeM_BlueWildflowers_variations.png) | [Four directions](PokeM_BlueWildflowers_geometry.png)

- [Base](../PokeM_BlueWildflowers.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeM_BlueWildflowers_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeM_BlueWildflowers_CratePalette.vox) — 85 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeM_BlueWildflowers_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeM_BlueWildflowers_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeM_BlueWildflowers_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeM_BlueWildflowers_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

### PokeM_OrangeWildflowers

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[687, 382, 708, 401]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeM_OrangeWildflowers_source.png) | [Seven treatments](PokeM_OrangeWildflowers_variations.png) | [Four directions](PokeM_OrangeWildflowers_geometry.png)

- [Base](../PokeM_OrangeWildflowers.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeM_OrangeWildflowers_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeM_OrangeWildflowers_CratePalette.vox) — 85 voxels; 7 paint colors; 3 rooted component(s).
- [TwoColor](../PokeM_OrangeWildflowers_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeM_OrangeWildflowers_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeM_OrangeWildflowers_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeM_OrangeWildflowers_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
