# poke_a.jpg — flowers, bushes and grass

5 new appearances; 35 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeA_LeafyTallGrass

Canvas XYZ: **16 x 16 x 12**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[352, 142, 384, 175]`. 

[Source crop](PokeA_LeafyTallGrass_source.png) | [Seven treatments](PokeA_LeafyTallGrass_variations.png) | [Four directions](PokeA_LeafyTallGrass_geometry.png)

- [Base](../PokeA_LeafyTallGrass.vox) — 1659 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeA_LeafyTallGrass_Cartoon.vox) — 1808 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeA_LeafyTallGrass_CratePalette.vox) — 1659 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeA_LeafyTallGrass_TwoColor.vox) — 1659 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeA_LeafyTallGrass_Cartoon_TwoColor.vox) — 1808 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeA_LeafyTallGrass_CratePalette_TwoColor.vox) — 1659 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeA_LeafyTallGrass_Cartoon_CratePalette_TwoColor.vox) — 1808 voxels; 1 paint colors; 1 rooted component(s).

### PokeA_YellowFlowerBed

Canvas XYZ: **16 x 16 x 16**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[450, 32, 501, 78]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeA_YellowFlowerBed_source.png) | [Seven treatments](PokeA_YellowFlowerBed_variations.png) | [Four directions](PokeA_YellowFlowerBed_geometry.png)

- [Base](../PokeA_YellowFlowerBed.vox) — 169 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeA_YellowFlowerBed_Cartoon.vox) — 300 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeA_YellowFlowerBed_CratePalette.vox) — 169 voxels; 4 paint colors; 3 rooted component(s).
- [TwoColor](../PokeA_YellowFlowerBed_TwoColor.vox) — 169 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeA_YellowFlowerBed_Cartoon_TwoColor.vox) — 300 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeA_YellowFlowerBed_CratePalette_TwoColor.vox) — 169 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeA_YellowFlowerBed_Cartoon_CratePalette_TwoColor.vox) — 300 voxels; 3 paint colors; 4 rooted component(s).

### PokeA_PinkWildflowers

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[405, 231, 430, 252]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeA_PinkWildflowers_source.png) | [Seven treatments](PokeA_PinkWildflowers_variations.png) | [Four directions](PokeA_PinkWildflowers_geometry.png)

- [Base](../PokeA_PinkWildflowers.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeA_PinkWildflowers_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeA_PinkWildflowers_CratePalette.vox) — 85 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeA_PinkWildflowers_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeA_PinkWildflowers_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeA_PinkWildflowers_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeA_PinkWildflowers_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

### PokeA_WaterLily

Canvas XYZ: **12 x 12 x 5**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[235, 323, 260, 342]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeA_WaterLily_source.png) | [Seven treatments](PokeA_WaterLily_variations.png) | [Four directions](PokeA_WaterLily_geometry.png)

- [Base](../PokeA_WaterLily.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [Cartoon](../PokeA_WaterLily_Cartoon.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeA_WaterLily_CratePalette.vox) — 161 voxels; 4 paint colors; 1 rooted component(s).
- [TwoColor](../PokeA_WaterLily_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeA_WaterLily_Cartoon_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeA_WaterLily_CratePalette_TwoColor.vox) — 161 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeA_WaterLily_Cartoon_CratePalette_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).

### PokeA_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[431, 335, 452, 358]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeA_ShortGrassPatch_source.png) | [Seven treatments](PokeA_ShortGrassPatch_variations.png) | [Four directions](PokeA_ShortGrassPatch_geometry.png)

- [Base](../PokeA_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeA_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeA_ShortGrassPatch_CratePalette.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeA_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeA_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeA_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeA_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
