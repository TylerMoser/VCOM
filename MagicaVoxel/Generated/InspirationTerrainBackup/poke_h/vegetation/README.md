# poke_h.png — flowers, bushes and grass

4 new appearances; 28 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeH_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[143, 262, 162, 282]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeH_ShortGrassPatch_source.png) | [Seven treatments](PokeH_ShortGrassPatch_variations.png) | [Four directions](PokeH_ShortGrassPatch_geometry.png)

- [Base](../PokeH_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeH_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeH_ShortGrassPatch_CratePalette.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [TwoColor](../PokeH_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeH_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeH_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeH_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeH_GoldenWheat

Canvas XYZ: **16 x 16 x 28**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[223, 79, 257, 115]`. Standing cereal grass with stalks and seed heads. Harvested hay bales and tools excluded.

[Source crop](PokeH_GoldenWheat_source.png) | [Seven treatments](PokeH_GoldenWheat_variations.png) | [Four directions](PokeH_GoldenWheat_geometry.png)

- [Base](../PokeH_GoldenWheat.vox) — 782 voxels; 3 paint colors; 2 rooted component(s).
- [Cartoon](../PokeH_GoldenWheat_Cartoon.vox) — 972 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeH_GoldenWheat_CratePalette.vox) — 782 voxels; 2 paint colors; 2 rooted component(s).
- [TwoColor](../PokeH_GoldenWheat_TwoColor.vox) — 782 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_TwoColor](../PokeH_GoldenWheat_Cartoon_TwoColor.vox) — 972 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeH_GoldenWheat_CratePalette_TwoColor.vox) — 782 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeH_GoldenWheat_Cartoon_CratePalette_TwoColor.vox) — 972 voxels; 1 paint colors; 1 rooted component(s).

### PokeH_PinkWhiteDaisies

Canvas XYZ: **16 x 16 x 7**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[286, 156, 309, 178]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeH_PinkWhiteDaisies_source.png) | [Seven treatments](PokeH_PinkWhiteDaisies_variations.png) | [Four directions](PokeH_PinkWhiteDaisies_geometry.png)

- [Base](../PokeH_PinkWhiteDaisies.vox) — 126 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeH_PinkWhiteDaisies_Cartoon.vox) — 200 voxels; 6 paint colors; 4 rooted component(s).
- [CratePalette](../PokeH_PinkWhiteDaisies_CratePalette.vox) — 126 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeH_PinkWhiteDaisies_TwoColor.vox) — 126 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeH_PinkWhiteDaisies_Cartoon_TwoColor.vox) — 200 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeH_PinkWhiteDaisies_CratePalette_TwoColor.vox) — 126 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeH_PinkWhiteDaisies_Cartoon_CratePalette_TwoColor.vox) — 200 voxels; 3 paint colors; 4 rooted component(s).

### PokeH_PurpleDaisies

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[413, 446, 434, 466]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeH_PurpleDaisies_source.png) | [Seven treatments](PokeH_PurpleDaisies_variations.png) | [Four directions](PokeH_PurpleDaisies_geometry.png)

- [Base](../PokeH_PurpleDaisies.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeH_PurpleDaisies_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeH_PurpleDaisies_CratePalette.vox) — 85 voxels; 7 paint colors; 3 rooted component(s).
- [TwoColor](../PokeH_PurpleDaisies_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeH_PurpleDaisies_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeH_PurpleDaisies_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeH_PurpleDaisies_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

- **PokeH_CompactFruitBush**: [Base](../../poke_h/PokeH_CompactFruitBush.vox), [Cartoon](../../poke_h/PokeH_CompactFruitBush_Cartoon.vox), [CratePalette](../../poke_h/PokeH_CompactFruitBush_CratePalette.vox), [TwoColor](../../poke_h/PokeH_CompactFruitBush_TwoColor.vox), [Cartoon_TwoColor](../../poke_h/PokeH_CompactFruitBush_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../poke_h/PokeH_CompactFruitBush_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../poke_h/PokeH_CompactFruitBush_Cartoon_CratePalette_TwoColor.vox).

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
