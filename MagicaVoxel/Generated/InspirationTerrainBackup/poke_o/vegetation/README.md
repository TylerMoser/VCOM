# poke_o.png — flowers, bushes and grass

5 new appearances; 35 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeO_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[184, 270, 206, 290]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeO_ShortGrassPatch_source.png) | [Seven treatments](PokeO_ShortGrassPatch_variations.png) | [Four directions](PokeO_ShortGrassPatch_geometry.png)

- [Base](../PokeO_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeO_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeO_ShortGrassPatch_CratePalette.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeO_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeO_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeO_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeO_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeO_BeachGrass

Canvas XYZ: **16 x 16 x 12**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[463, 92, 485, 115]`. Sparse curved wind-bent blades; Cartoon uses balanced outward blades.

[Source crop](PokeO_BeachGrass_source.png) | [Seven treatments](PokeO_BeachGrass_variations.png) | [Four directions](PokeO_BeachGrass_geometry.png)

- [Base](../PokeO_BeachGrass.vox) — 178 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeO_BeachGrass_Cartoon.vox) — 264 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeO_BeachGrass_CratePalette.vox) — 178 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeO_BeachGrass_TwoColor.vox) — 178 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeO_BeachGrass_Cartoon_TwoColor.vox) — 264 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeO_BeachGrass_CratePalette_TwoColor.vox) — 178 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeO_BeachGrass_Cartoon_CratePalette_TwoColor.vox) — 264 voxels; 1 paint colors; 1 rooted component(s).

### PokeO_DenseMeadowGrass

Canvas XYZ: **16 x 16 x 16**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[410, 179, 446, 210]`. 

[Source crop](PokeO_DenseMeadowGrass_source.png) | [Seven treatments](PokeO_DenseMeadowGrass_variations.png) | [Four directions](PokeO_DenseMeadowGrass_geometry.png)

- [Base](../PokeO_DenseMeadowGrass.vox) — 2141 voxels; 2 paint colors; 1 rooted component(s).
- [Cartoon](../PokeO_DenseMeadowGrass_Cartoon.vox) — 2348 voxels; 2 paint colors; 1 rooted component(s).
- [CratePalette](../PokeO_DenseMeadowGrass_CratePalette.vox) — 2141 voxels; 1 paint colors; 1 rooted component(s).
- [TwoColor](../PokeO_DenseMeadowGrass_TwoColor.vox) — 2141 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeO_DenseMeadowGrass_Cartoon_TwoColor.vox) — 2348 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeO_DenseMeadowGrass_CratePalette_TwoColor.vox) — 2141 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeO_DenseMeadowGrass_Cartoon_CratePalette_TwoColor.vox) — 2348 voxels; 1 paint colors; 1 rooted component(s).

### PokeO_WhiteDaisies

Canvas XYZ: **12 x 12 x 8**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[193, 286, 208, 308]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeO_WhiteDaisies_source.png) | [Seven treatments](PokeO_WhiteDaisies_variations.png) | [Four directions](PokeO_WhiteDaisies_geometry.png)

- [Base](../PokeO_WhiteDaisies.vox) — 114 voxels; 7 paint colors; 3 rooted component(s).
- [Cartoon](../PokeO_WhiteDaisies_Cartoon.vox) — 196 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeO_WhiteDaisies_CratePalette.vox) — 114 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeO_WhiteDaisies_TwoColor.vox) — 114 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeO_WhiteDaisies_Cartoon_TwoColor.vox) — 196 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeO_WhiteDaisies_CratePalette_TwoColor.vox) — 114 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeO_WhiteDaisies_Cartoon_CratePalette_TwoColor.vox) — 196 voxels; 3 paint colors; 1 rooted component(s).

### PokeO_OrangeDaisies

Canvas XYZ: **12 x 12 x 8**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[383, 282, 402, 303]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeO_OrangeDaisies_source.png) | [Seven treatments](PokeO_OrangeDaisies_variations.png) | [Four directions](PokeO_OrangeDaisies_geometry.png)

- [Base](../PokeO_OrangeDaisies.vox) — 114 voxels; 7 paint colors; 3 rooted component(s).
- [Cartoon](../PokeO_OrangeDaisies_Cartoon.vox) — 196 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeO_OrangeDaisies_CratePalette.vox) — 114 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeO_OrangeDaisies_TwoColor.vox) — 114 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeO_OrangeDaisies_Cartoon_TwoColor.vox) — 196 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeO_OrangeDaisies_CratePalette_TwoColor.vox) — 114 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeO_OrangeDaisies_Cartoon_CratePalette_TwoColor.vox) — 196 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
