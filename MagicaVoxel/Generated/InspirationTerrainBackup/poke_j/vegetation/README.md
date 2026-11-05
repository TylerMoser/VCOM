# poke_j.jpg — flowers, bushes and grass

3 new appearances; 21 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeJ_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[374, 287, 397, 305]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeJ_ShortGrassPatch_source.png) | [Seven treatments](PokeJ_ShortGrassPatch_variations.png) | [Four directions](PokeJ_ShortGrassPatch_geometry.png)

- [Base](../PokeJ_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeJ_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeJ_ShortGrassPatch_CratePalette.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeJ_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeJ_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeJ_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeJ_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeJ_WhiteWildflowers

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[347, 170, 371, 188]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeJ_WhiteWildflowers_source.png) | [Seven treatments](PokeJ_WhiteWildflowers_variations.png) | [Four directions](PokeJ_WhiteWildflowers_geometry.png)

- [Base](../PokeJ_WhiteWildflowers.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeJ_WhiteWildflowers_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeJ_WhiteWildflowers_CratePalette.vox) — 85 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeJ_WhiteWildflowers_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeJ_WhiteWildflowers_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeJ_WhiteWildflowers_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeJ_WhiteWildflowers_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

### PokeJ_WaterLily

Canvas XYZ: **12 x 12 x 5**. Approximate source scale: 0.667 voxel(s) per displayed pixel. Crop XYXY: `[348, 266, 374, 288]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeJ_WaterLily_source.png) | [Seven treatments](PokeJ_WaterLily_variations.png) | [Four directions](PokeJ_WaterLily_geometry.png)

- [Base](../PokeJ_WaterLily.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [Cartoon](../PokeJ_WaterLily_Cartoon.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeJ_WaterLily_CratePalette.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [TwoColor](../PokeJ_WaterLily_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeJ_WaterLily_Cartoon_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeJ_WaterLily_CratePalette_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeJ_WaterLily_Cartoon_CratePalette_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

- **PokeJ_RoundedShrub**: [Base](../../poke_j/PokeJ_RoundedShrub.vox), [Cartoon](../../poke_j/PokeJ_RoundedShrub_Cartoon.vox), [CratePalette](../../poke_j/PokeJ_RoundedShrub_CratePalette.vox), [TwoColor](../../poke_j/PokeJ_RoundedShrub_TwoColor.vox), [Cartoon_TwoColor](../../poke_j/PokeJ_RoundedShrub_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../poke_j/PokeJ_RoundedShrub_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../poke_j/PokeJ_RoundedShrub_Cartoon_CratePalette_TwoColor.vox).

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
