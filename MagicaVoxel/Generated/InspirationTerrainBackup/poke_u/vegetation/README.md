# poke_u.jpg — flowers, bushes and grass

4 new appearances; 28 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeU_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[150, 267, 170, 279]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeU_ShortGrassPatch_source.png) | [Seven treatments](PokeU_ShortGrassPatch_variations.png) | [Four directions](PokeU_ShortGrassPatch_geometry.png)

- [Base](../PokeU_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeU_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeU_ShortGrassPatch_CratePalette.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeU_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeU_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeU_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeU_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeU_PaleTallGrass

Canvas XYZ: **16 x 16 x 24**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[112, 325, 145, 364]`. 

[Source crop](PokeU_PaleTallGrass_source.png) | [Seven treatments](PokeU_PaleTallGrass_variations.png) | [Four directions](PokeU_PaleTallGrass_geometry.png)

- [Base](../PokeU_PaleTallGrass.vox) — 865 voxels; 3 paint colors; 2 rooted component(s).
- [Cartoon](../PokeU_PaleTallGrass_Cartoon.vox) — 1048 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeU_PaleTallGrass_CratePalette.vox) — 865 voxels; 3 paint colors; 2 rooted component(s).
- [TwoColor](../PokeU_PaleTallGrass_TwoColor.vox) — 865 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_TwoColor](../PokeU_PaleTallGrass_Cartoon_TwoColor.vox) — 1048 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeU_PaleTallGrass_CratePalette_TwoColor.vox) — 865 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeU_PaleTallGrass_Cartoon_CratePalette_TwoColor.vox) — 1048 voxels; 1 paint colors; 1 rooted component(s).

### PokeU_PinkWhiteDaisies

Canvas XYZ: **16 x 16 x 7**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[171, 269, 197, 291]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeU_PinkWhiteDaisies_source.png) | [Seven treatments](PokeU_PinkWhiteDaisies_variations.png) | [Four directions](PokeU_PinkWhiteDaisies_geometry.png)

- [Base](../PokeU_PinkWhiteDaisies.vox) — 126 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeU_PinkWhiteDaisies_Cartoon.vox) — 200 voxels; 6 paint colors; 4 rooted component(s).
- [CratePalette](../PokeU_PinkWhiteDaisies_CratePalette.vox) — 126 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeU_PinkWhiteDaisies_TwoColor.vox) — 126 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeU_PinkWhiteDaisies_Cartoon_TwoColor.vox) — 200 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeU_PinkWhiteDaisies_CratePalette_TwoColor.vox) — 126 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeU_PinkWhiteDaisies_Cartoon_CratePalette_TwoColor.vox) — 200 voxels; 3 paint colors; 4 rooted component(s).

### PokeU_OrangeDaisies

Canvas XYZ: **12 x 12 x 7**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[204, 301, 228, 319]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeU_OrangeDaisies_source.png) | [Seven treatments](PokeU_OrangeDaisies_variations.png) | [Four directions](PokeU_OrangeDaisies_geometry.png)

- [Base](../PokeU_OrangeDaisies.vox) — 101 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeU_OrangeDaisies_Cartoon.vox) — 160 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeU_OrangeDaisies_CratePalette.vox) — 101 voxels; 7 paint colors; 3 rooted component(s).
- [TwoColor](../PokeU_OrangeDaisies_TwoColor.vox) — 101 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeU_OrangeDaisies_Cartoon_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeU_OrangeDaisies_CratePalette_TwoColor.vox) — 101 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeU_OrangeDaisies_Cartoon_CratePalette_TwoColor.vox) — 160 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
