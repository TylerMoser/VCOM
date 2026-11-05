# poke_r.png — flowers, bushes and grass

3 new appearances; 21 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeR_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[373, 242, 398, 264]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeR_ShortGrassPatch_source.png) | [Seven treatments](PokeR_ShortGrassPatch_variations.png) | [Four directions](PokeR_ShortGrassPatch_geometry.png)

- [Base](../PokeR_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeR_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeR_ShortGrassPatch_CratePalette.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeR_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeR_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeR_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeR_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeR_GardenTallGrass

Canvas XYZ: **16 x 16 x 28**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[356, 350, 385, 391]`. 

[Source crop](PokeR_GardenTallGrass_source.png) | [Seven treatments](PokeR_GardenTallGrass_variations.png) | [Four directions](PokeR_GardenTallGrass_geometry.png)

- [Base](../PokeR_GardenTallGrass.vox) — 996 voxels; 3 paint colors; 2 rooted component(s).
- [Cartoon](../PokeR_GardenTallGrass_Cartoon.vox) — 1188 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeR_GardenTallGrass_CratePalette.vox) — 996 voxels; 2 paint colors; 2 rooted component(s).
- [TwoColor](../PokeR_GardenTallGrass_TwoColor.vox) — 996 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_TwoColor](../PokeR_GardenTallGrass_Cartoon_TwoColor.vox) — 1188 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeR_GardenTallGrass_CratePalette_TwoColor.vox) — 996 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeR_GardenTallGrass_Cartoon_CratePalette_TwoColor.vox) — 1188 voxels; 1 paint colors; 1 rooted component(s).

### PokeR_WhiteDaisies

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[349, 239, 373, 262]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeR_WhiteDaisies_source.png) | [Seven treatments](PokeR_WhiteDaisies_variations.png) | [Four directions](PokeR_WhiteDaisies_geometry.png)

- [Base](../PokeR_WhiteDaisies.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeR_WhiteDaisies_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeR_WhiteDaisies_CratePalette.vox) — 85 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeR_WhiteDaisies_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeR_WhiteDaisies_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeR_WhiteDaisies_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeR_WhiteDaisies_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

- **PokeR_RoundShrub**: [Base](../../poke_r/PokeR_RoundShrub.vox), [Cartoon](../../poke_r/PokeR_RoundShrub_Cartoon.vox), [CratePalette](../../poke_r/PokeR_RoundShrub_CratePalette.vox), [TwoColor](../../poke_r/PokeR_RoundShrub_TwoColor.vox), [Cartoon_TwoColor](../../poke_r/PokeR_RoundShrub_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../poke_r/PokeR_RoundShrub_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../poke_r/PokeR_RoundShrub_Cartoon_CratePalette_TwoColor.vox).

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
