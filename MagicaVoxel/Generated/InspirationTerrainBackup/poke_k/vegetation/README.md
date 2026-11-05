# poke_k.jpg — flowers, bushes and grass

4 new appearances; 28 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeK_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[633, 331, 654, 351]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeK_ShortGrassPatch_source.png) | [Seven treatments](PokeK_ShortGrassPatch_variations.png) | [Four directions](PokeK_ShortGrassPatch_geometry.png)

- [Base](../PokeK_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeK_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeK_ShortGrassPatch_CratePalette.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeK_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeK_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeK_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeK_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeK_TallGrass

Canvas XYZ: **16 x 16 x 22**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[522, 85, 556, 126]`. 

[Source crop](PokeK_TallGrass_source.png) | [Seven treatments](PokeK_TallGrass_variations.png) | [Four directions](PokeK_TallGrass_geometry.png)

- [Base](../PokeK_TallGrass.vox) — 807 voxels; 3 paint colors; 2 rooted component(s).
- [Cartoon](../PokeK_TallGrass_Cartoon.vox) — 968 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeK_TallGrass_CratePalette.vox) — 807 voxels; 2 paint colors; 2 rooted component(s).
- [TwoColor](../PokeK_TallGrass_TwoColor.vox) — 807 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_TwoColor](../PokeK_TallGrass_Cartoon_TwoColor.vox) — 968 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeK_TallGrass_CratePalette_TwoColor.vox) — 807 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeK_TallGrass_Cartoon_CratePalette_TwoColor.vox) — 968 voxels; 1 paint colors; 1 rooted component(s).

### PokeK_WhiteWildflowers

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[570, 320, 595, 340]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeK_WhiteWildflowers_source.png) | [Seven treatments](PokeK_WhiteWildflowers_variations.png) | [Four directions](PokeK_WhiteWildflowers_geometry.png)

- [Base](../PokeK_WhiteWildflowers.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeK_WhiteWildflowers_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeK_WhiteWildflowers_CratePalette.vox) — 85 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeK_WhiteWildflowers_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeK_WhiteWildflowers_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeK_WhiteWildflowers_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeK_WhiteWildflowers_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

### PokeK_WaterLily

Canvas XYZ: **12 x 12 x 5**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[229, 350, 255, 370]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeK_WaterLily_source.png) | [Seven treatments](PokeK_WaterLily_variations.png) | [Four directions](PokeK_WaterLily_geometry.png)

- [Base](../PokeK_WaterLily.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [Cartoon](../PokeK_WaterLily_Cartoon.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeK_WaterLily_CratePalette.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [TwoColor](../PokeK_WaterLily_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeK_WaterLily_Cartoon_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeK_WaterLily_CratePalette_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeK_WaterLily_Cartoon_CratePalette_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

- **PokeK_RoundedShrub**: [Base](../../poke_k/PokeK_RoundedShrub.vox), [Cartoon](../../poke_k/PokeK_RoundedShrub_Cartoon.vox), [CratePalette](../../poke_k/PokeK_RoundedShrub_CratePalette.vox), [TwoColor](../../poke_k/PokeK_RoundedShrub_TwoColor.vox), [Cartoon_TwoColor](../../poke_k/PokeK_RoundedShrub_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../poke_k/PokeK_RoundedShrub_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../poke_k/PokeK_RoundedShrub_Cartoon_CratePalette_TwoColor.vox).

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
