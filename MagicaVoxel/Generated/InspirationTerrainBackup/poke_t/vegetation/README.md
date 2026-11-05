# poke_t.png — flowers, bushes and grass

4 new appearances; 28 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeT_LowGrassClump

Canvas XYZ: **16 x 16 x 14**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[352, 463, 380, 492]`. 

[Source crop](PokeT_LowGrassClump_source.png) | [Seven treatments](PokeT_LowGrassClump_variations.png) | [Four directions](PokeT_LowGrassClump_geometry.png)

- [Base](../PokeT_LowGrassClump.vox) — 205 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeT_LowGrassClump_Cartoon.vox) — 312 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeT_LowGrassClump_CratePalette.vox) — 205 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeT_LowGrassClump_TwoColor.vox) — 205 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeT_LowGrassClump_Cartoon_TwoColor.vox) — 312 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeT_LowGrassClump_CratePalette_TwoColor.vox) — 205 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeT_LowGrassClump_Cartoon_CratePalette_TwoColor.vox) — 312 voxels; 1 paint colors; 1 rooted component(s).

### PokeT_SparseBeachGrass

Canvas XYZ: **16 x 16 x 10**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[399, 378, 420, 404]`. 

[Source crop](PokeT_SparseBeachGrass_source.png) | [Seven treatments](PokeT_SparseBeachGrass_variations.png) | [Four directions](PokeT_SparseBeachGrass_geometry.png)

- [Base](../PokeT_SparseBeachGrass.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeT_SparseBeachGrass_Cartoon.vox) — 220 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeT_SparseBeachGrass_CratePalette.vox) — 161 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeT_SparseBeachGrass_TwoColor.vox) — 161 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeT_SparseBeachGrass_Cartoon_TwoColor.vox) — 220 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeT_SparseBeachGrass_CratePalette_TwoColor.vox) — 161 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeT_SparseBeachGrass_Cartoon_CratePalette_TwoColor.vox) — 220 voxels; 1 paint colors; 1 rooted component(s).

### PokeT_SubmergedReeds

Canvas XYZ: **16 x 16 x 20**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[570, 189, 595, 215]`. 

[Source crop](PokeT_SubmergedReeds_source.png) | [Seven treatments](PokeT_SubmergedReeds_variations.png) | [Four directions](PokeT_SubmergedReeds_geometry.png)

- [Base](../PokeT_SubmergedReeds.vox) — 265 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeT_SubmergedReeds_Cartoon.vox) — 416 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeT_SubmergedReeds_CratePalette.vox) — 265 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeT_SubmergedReeds_TwoColor.vox) — 265 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeT_SubmergedReeds_Cartoon_TwoColor.vox) — 416 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeT_SubmergedReeds_CratePalette_TwoColor.vox) — 265 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeT_SubmergedReeds_Cartoon_CratePalette_TwoColor.vox) — 416 voxels; 1 paint colors; 1 rooted component(s).

### PokeT_SubmergedRosette

Canvas XYZ: **16 x 16 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[540, 176, 563, 198]`. 

[Source crop](PokeT_SubmergedRosette_source.png) | [Seven treatments](PokeT_SubmergedRosette_variations.png) | [Four directions](PokeT_SubmergedRosette_geometry.png)

- [Base](../PokeT_SubmergedRosette.vox) — 234 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeT_SubmergedRosette_Cartoon.vox) — 248 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeT_SubmergedRosette_CratePalette.vox) — 234 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeT_SubmergedRosette_TwoColor.vox) — 234 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeT_SubmergedRosette_Cartoon_TwoColor.vox) — 248 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeT_SubmergedRosette_CratePalette_TwoColor.vox) — 234 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeT_SubmergedRosette_Cartoon_CratePalette_TwoColor.vox) — 248 voxels; 1 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
