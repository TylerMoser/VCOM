# poke_e.png — flowers, bushes and grass

5 new appearances; 35 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeE_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[236, 68, 259, 88]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeE_ShortGrassPatch_source.png) | [Seven treatments](PokeE_ShortGrassPatch_variations.png) | [Four directions](PokeE_ShortGrassPatch_geometry.png)

- [Base](../PokeE_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeE_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeE_ShortGrassPatch_CratePalette.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [TwoColor](../PokeE_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeE_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeE_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeE_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeE_MeadowGrass

Canvas XYZ: **16 x 16 x 16**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[238, 99, 271, 132]`. 

[Source crop](PokeE_MeadowGrass_source.png) | [Seven treatments](PokeE_MeadowGrass_variations.png) | [Four directions](PokeE_MeadowGrass_geometry.png)

- [Base](../PokeE_MeadowGrass.vox) — 618 voxels; 3 paint colors; 2 rooted component(s).
- [Cartoon](../PokeE_MeadowGrass_Cartoon.vox) — 688 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeE_MeadowGrass_CratePalette.vox) — 618 voxels; 2 paint colors; 2 rooted component(s).
- [TwoColor](../PokeE_MeadowGrass_TwoColor.vox) — 618 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_TwoColor](../PokeE_MeadowGrass_Cartoon_TwoColor.vox) — 688 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeE_MeadowGrass_CratePalette_TwoColor.vox) — 618 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeE_MeadowGrass_Cartoon_CratePalette_TwoColor.vox) — 688 voxels; 1 paint colors; 1 rooted component(s).

### PokeE_BlueDaisyBed

Canvas XYZ: **16 x 16 x 12**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[409, 110, 443, 148]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeE_BlueDaisyBed_source.png) | [Seven treatments](PokeE_BlueDaisyBed_variations.png) | [Four directions](PokeE_BlueDaisyBed_geometry.png)

- [Base](../PokeE_BlueDaisyBed.vox) — 151 voxels; 7 paint colors; 3 rooted component(s).
- [Cartoon](../PokeE_BlueDaisyBed_Cartoon.vox) — 252 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeE_BlueDaisyBed_CratePalette.vox) — 151 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeE_BlueDaisyBed_TwoColor.vox) — 151 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeE_BlueDaisyBed_Cartoon_TwoColor.vox) — 252 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeE_BlueDaisyBed_CratePalette_TwoColor.vox) — 151 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeE_BlueDaisyBed_Cartoon_CratePalette_TwoColor.vox) — 252 voxels; 3 paint colors; 4 rooted component(s).

### PokeE_WhiteDaisies

Canvas XYZ: **12 x 12 x 6**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[243, 176, 261, 192]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeE_WhiteDaisies_source.png) | [Seven treatments](PokeE_WhiteDaisies_variations.png) | [Four directions](PokeE_WhiteDaisies_geometry.png)

- [Base](../PokeE_WhiteDaisies.vox) — 85 voxels; 8 paint colors; 3 rooted component(s).
- [Cartoon](../PokeE_WhiteDaisies_Cartoon.vox) — 148 voxels; 6 paint colors; 1 rooted component(s).
- [CratePalette](../PokeE_WhiteDaisies_CratePalette.vox) — 85 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeE_WhiteDaisies_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeE_WhiteDaisies_Cartoon_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeE_WhiteDaisies_CratePalette_TwoColor.vox) — 85 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeE_WhiteDaisies_Cartoon_CratePalette_TwoColor.vox) — 148 voxels; 3 paint colors; 1 rooted component(s).

### PokeE_RedFlower

Canvas XYZ: **12 x 12 x 16**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[272, 79, 289, 98]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeE_RedFlower_source.png) | [Seven treatments](PokeE_RedFlower_variations.png) | [Four directions](PokeE_RedFlower_geometry.png)

- [Base](../PokeE_RedFlower.vox) — 146 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeE_RedFlower_Cartoon.vox) — 260 voxels; 5 paint colors; 1 rooted component(s).
- [CratePalette](../PokeE_RedFlower_CratePalette.vox) — 146 voxels; 4 paint colors; 3 rooted component(s).
- [TwoColor](../PokeE_RedFlower_TwoColor.vox) — 146 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeE_RedFlower_Cartoon_TwoColor.vox) — 260 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeE_RedFlower_CratePalette_TwoColor.vox) — 146 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeE_RedFlower_Cartoon_CratePalette_TwoColor.vox) — 260 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
