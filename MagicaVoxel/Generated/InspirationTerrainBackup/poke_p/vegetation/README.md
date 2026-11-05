# poke_p.png — flowers, bushes and grass

12 new appearances; 84 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeP_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[450, 195, 472, 217]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeP_ShortGrassPatch_source.png) | [Seven treatments](PokeP_ShortGrassPatch_variations.png) | [Four directions](PokeP_ShortGrassPatch_geometry.png)

- [Base](../PokeP_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeP_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeP_ShortGrassPatch_CratePalette.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeP_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeP_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeP_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeP_TealTallGrass

Canvas XYZ: **16 x 16 x 16**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[353, 490, 383, 522]`. 

[Source crop](PokeP_TealTallGrass_source.png) | [Seven treatments](PokeP_TealTallGrass_variations.png) | [Four directions](PokeP_TealTallGrass_geometry.png)

- [Base](../PokeP_TealTallGrass.vox) — 2141 voxels; 2 paint colors; 1 rooted component(s).
- [Cartoon](../PokeP_TealTallGrass_Cartoon.vox) — 2348 voxels; 2 paint colors; 1 rooted component(s).
- [CratePalette](../PokeP_TealTallGrass_CratePalette.vox) — 2141 voxels; 1 paint colors; 1 rooted component(s).
- [TwoColor](../PokeP_TealTallGrass_TwoColor.vox) — 2141 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeP_TealTallGrass_Cartoon_TwoColor.vox) — 2348 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeP_TealTallGrass_CratePalette_TwoColor.vox) — 2141 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_TealTallGrass_Cartoon_CratePalette_TwoColor.vox) — 2348 voxels; 1 paint colors; 1 rooted component(s).

### PokeP_PinkRoundFlower

Canvas XYZ: **16 x 16 x 10**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[124, 124, 144, 144]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeP_PinkRoundFlower_source.png) | [Seven treatments](PokeP_PinkRoundFlower_variations.png) | [Four directions](PokeP_PinkRoundFlower_geometry.png)

- [Base](../PokeP_PinkRoundFlower.vox) — 142 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeP_PinkRoundFlower_Cartoon.vox) — 212 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeP_PinkRoundFlower_CratePalette.vox) — 142 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeP_PinkRoundFlower_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeP_PinkRoundFlower_Cartoon_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeP_PinkRoundFlower_CratePalette_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_PinkRoundFlower_Cartoon_CratePalette_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).

### PokeP_RedRoundFlower

Canvas XYZ: **16 x 16 x 10**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[173, 156, 194, 177]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeP_RedRoundFlower_source.png) | [Seven treatments](PokeP_RedRoundFlower_variations.png) | [Four directions](PokeP_RedRoundFlower_geometry.png)

- [Base](../PokeP_RedRoundFlower.vox) — 142 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeP_RedRoundFlower_Cartoon.vox) — 212 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeP_RedRoundFlower_CratePalette.vox) — 142 voxels; 4 paint colors; 3 rooted component(s).
- [TwoColor](../PokeP_RedRoundFlower_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeP_RedRoundFlower_Cartoon_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeP_RedRoundFlower_CratePalette_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_RedRoundFlower_Cartoon_CratePalette_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).

### PokeP_BlueRoundFlower

Canvas XYZ: **16 x 16 x 10**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[174, 125, 195, 146]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeP_BlueRoundFlower_source.png) | [Seven treatments](PokeP_BlueRoundFlower_variations.png) | [Four directions](PokeP_BlueRoundFlower_geometry.png)

- [Base](../PokeP_BlueRoundFlower.vox) — 142 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeP_BlueRoundFlower_Cartoon.vox) — 212 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeP_BlueRoundFlower_CratePalette.vox) — 142 voxels; 4 paint colors; 3 rooted component(s).
- [TwoColor](../PokeP_BlueRoundFlower_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeP_BlueRoundFlower_Cartoon_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeP_BlueRoundFlower_CratePalette_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_BlueRoundFlower_Cartoon_CratePalette_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).

### PokeP_WhiteRoundFlower

Canvas XYZ: **16 x 16 x 10**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[191, 140, 210, 162]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeP_WhiteRoundFlower_source.png) | [Seven treatments](PokeP_WhiteRoundFlower_variations.png) | [Four directions](PokeP_WhiteRoundFlower_geometry.png)

- [Base](../PokeP_WhiteRoundFlower.vox) — 142 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeP_WhiteRoundFlower_Cartoon.vox) — 212 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeP_WhiteRoundFlower_CratePalette.vox) — 142 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeP_WhiteRoundFlower_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeP_WhiteRoundFlower_Cartoon_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeP_WhiteRoundFlower_CratePalette_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_WhiteRoundFlower_Cartoon_CratePalette_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).

### PokeP_YellowRoundFlower

Canvas XYZ: **16 x 16 x 10**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[462, 173, 483, 194]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeP_YellowRoundFlower_source.png) | [Seven treatments](PokeP_YellowRoundFlower_variations.png) | [Four directions](PokeP_YellowRoundFlower_geometry.png)

- [Base](../PokeP_YellowRoundFlower.vox) — 142 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeP_YellowRoundFlower_Cartoon.vox) — 212 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeP_YellowRoundFlower_CratePalette.vox) — 142 voxels; 4 paint colors; 3 rooted component(s).
- [TwoColor](../PokeP_YellowRoundFlower_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeP_YellowRoundFlower_Cartoon_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeP_YellowRoundFlower_CratePalette_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_YellowRoundFlower_Cartoon_CratePalette_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).

### PokeP_PurpleRoundFlower

Canvas XYZ: **16 x 16 x 10**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[218, 360, 240, 386]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeP_PurpleRoundFlower_source.png) | [Seven treatments](PokeP_PurpleRoundFlower_variations.png) | [Four directions](PokeP_PurpleRoundFlower_geometry.png)

- [Base](../PokeP_PurpleRoundFlower.vox) — 142 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeP_PurpleRoundFlower_Cartoon.vox) — 212 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeP_PurpleRoundFlower_CratePalette.vox) — 142 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeP_PurpleRoundFlower_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeP_PurpleRoundFlower_Cartoon_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeP_PurpleRoundFlower_CratePalette_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_PurpleRoundFlower_Cartoon_CratePalette_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).

### PokeP_PinkFlowerSpikes

Canvas XYZ: **16 x 16 x 28**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[710, 209, 765, 243]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeP_PinkFlowerSpikes_source.png) | [Seven treatments](PokeP_PinkFlowerSpikes_variations.png) | [Four directions](PokeP_PinkFlowerSpikes_geometry.png)

- [Base](../PokeP_PinkFlowerSpikes.vox) — 851 voxels; 6 paint colors; 1 rooted component(s).
- [Cartoon](../PokeP_PinkFlowerSpikes_Cartoon.vox) — 1892 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeP_PinkFlowerSpikes_CratePalette.vox) — 851 voxels; 4 paint colors; 1 rooted component(s).
- [TwoColor](../PokeP_PinkFlowerSpikes_TwoColor.vox) — 851 voxels; 2 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeP_PinkFlowerSpikes_Cartoon_TwoColor.vox) — 1892 voxels; 2 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeP_PinkFlowerSpikes_CratePalette_TwoColor.vox) — 851 voxels; 2 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_PinkFlowerSpikes_Cartoon_CratePalette_TwoColor.vox) — 1892 voxels; 2 paint colors; 1 rooted component(s).

### PokeP_TinyPinkDaisyPatch

Canvas XYZ: **16 x 16 x 5**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[611, 221, 656, 250]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeP_TinyPinkDaisyPatch_source.png) | [Seven treatments](PokeP_TinyPinkDaisyPatch_variations.png) | [Four directions](PokeP_TinyPinkDaisyPatch_geometry.png)

- [Base](../PokeP_TinyPinkDaisyPatch.vox) — 101 voxels; 5 paint colors; 3 rooted component(s).
- [Cartoon](../PokeP_TinyPinkDaisyPatch_Cartoon.vox) — 152 voxels; 4 paint colors; 4 rooted component(s).
- [CratePalette](../PokeP_TinyPinkDaisyPatch_CratePalette.vox) — 101 voxels; 3 paint colors; 3 rooted component(s).
- [TwoColor](../PokeP_TinyPinkDaisyPatch_TwoColor.vox) — 101 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeP_TinyPinkDaisyPatch_Cartoon_TwoColor.vox) — 152 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeP_TinyPinkDaisyPatch_CratePalette_TwoColor.vox) — 101 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_TinyPinkDaisyPatch_Cartoon_CratePalette_TwoColor.vox) — 152 voxels; 3 paint colors; 4 rooted component(s).

### PokeP_SubmergedFern

Canvas XYZ: **16 x 16 x 16**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[363, 350, 387, 377]`. 

[Source crop](PokeP_SubmergedFern_source.png) | [Seven treatments](PokeP_SubmergedFern_variations.png) | [Four directions](PokeP_SubmergedFern_geometry.png)

- [Base](../PokeP_SubmergedFern.vox) — 213 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeP_SubmergedFern_Cartoon.vox) — 200 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeP_SubmergedFern_CratePalette.vox) — 213 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeP_SubmergedFern_TwoColor.vox) — 213 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeP_SubmergedFern_Cartoon_TwoColor.vox) — 200 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeP_SubmergedFern_CratePalette_TwoColor.vox) — 213 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_SubmergedFern_Cartoon_CratePalette_TwoColor.vox) — 200 voxels; 1 paint colors; 1 rooted component(s).

### PokeP_DryBankReeds

Canvas XYZ: **16 x 16 x 20**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[271, 316, 304, 353]`. 

[Source crop](PokeP_DryBankReeds_source.png) | [Seven treatments](PokeP_DryBankReeds_variations.png) | [Four directions](PokeP_DryBankReeds_geometry.png)

- [Base](../PokeP_DryBankReeds.vox) — 265 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeP_DryBankReeds_Cartoon.vox) — 416 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeP_DryBankReeds_CratePalette.vox) — 265 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeP_DryBankReeds_TwoColor.vox) — 265 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeP_DryBankReeds_Cartoon_TwoColor.vox) — 416 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeP_DryBankReeds_CratePalette_TwoColor.vox) — 265 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeP_DryBankReeds_Cartoon_CratePalette_TwoColor.vox) — 416 voxels; 1 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
