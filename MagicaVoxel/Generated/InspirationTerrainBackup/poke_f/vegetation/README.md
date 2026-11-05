# poke_f.png — flowers, bushes and grass

3 new appearances; 21 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeF_PinkFlowerBed

Canvas XYZ: **16 x 16 x 12**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[224, 463, 250, 491]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeF_PinkFlowerBed_source.png) | [Seven treatments](PokeF_PinkFlowerBed_variations.png) | [Four directions](PokeF_PinkFlowerBed_geometry.png)

- [Base](../PokeF_PinkFlowerBed.vox) — 151 voxels; 7 paint colors; 3 rooted component(s).
- [Cartoon](../PokeF_PinkFlowerBed_Cartoon.vox) — 252 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeF_PinkFlowerBed_CratePalette.vox) — 151 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeF_PinkFlowerBed_TwoColor.vox) — 151 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeF_PinkFlowerBed_Cartoon_TwoColor.vox) — 252 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeF_PinkFlowerBed_CratePalette_TwoColor.vox) — 151 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeF_PinkFlowerBed_Cartoon_CratePalette_TwoColor.vox) — 252 voxels; 3 paint colors; 4 rooted component(s).

### PokeF_WaterLily

Canvas XYZ: **12 x 12 x 5**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[188, 377, 209, 402]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeF_WaterLily_source.png) | [Seven treatments](PokeF_WaterLily_variations.png) | [Four directions](PokeF_WaterLily_geometry.png)

- [Base](../PokeF_WaterLily.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [Cartoon](../PokeF_WaterLily_Cartoon.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeF_WaterLily_CratePalette.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [TwoColor](../PokeF_WaterLily_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeF_WaterLily_Cartoon_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeF_WaterLily_CratePalette_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeF_WaterLily_Cartoon_CratePalette_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).

### PokeF_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[189, 281, 210, 301]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeF_ShortGrassPatch_source.png) | [Seven treatments](PokeF_ShortGrassPatch_variations.png) | [Four directions](PokeF_ShortGrassPatch_geometry.png)

- [Base](../PokeF_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeF_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeF_ShortGrassPatch_CratePalette.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [TwoColor](../PokeF_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeF_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeF_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeF_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
