# poke_d.png — flowers, bushes and grass

3 new appearances; 21 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeD_DryTallGrass

Canvas XYZ: **16 x 16 x 16**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[588, 85, 621, 121]`. 

[Source crop](PokeD_DryTallGrass_source.png) | [Seven treatments](PokeD_DryTallGrass_variations.png) | [Four directions](PokeD_DryTallGrass_geometry.png)

- [Base](../PokeD_DryTallGrass.vox) — 618 voxels; 3 paint colors; 2 rooted component(s).
- [Cartoon](../PokeD_DryTallGrass_Cartoon.vox) — 688 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeD_DryTallGrass_CratePalette.vox) — 618 voxels; 3 paint colors; 2 rooted component(s).
- [TwoColor](../PokeD_DryTallGrass_TwoColor.vox) — 618 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_TwoColor](../PokeD_DryTallGrass_Cartoon_TwoColor.vox) — 688 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeD_DryTallGrass_CratePalette_TwoColor.vox) — 618 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeD_DryTallGrass_Cartoon_CratePalette_TwoColor.vox) — 688 voxels; 1 paint colors; 1 rooted component(s).

### PokeD_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[701, 346, 729, 368]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeD_ShortGrassPatch_source.png) | [Seven treatments](PokeD_ShortGrassPatch_variations.png) | [Four directions](PokeD_ShortGrassPatch_geometry.png)

- [Base](../PokeD_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeD_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeD_ShortGrassPatch_CratePalette.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [TwoColor](../PokeD_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeD_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeD_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeD_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeD_GoldenLeafClump

Canvas XYZ: **24 x 24 x 20**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[640, 143, 674, 178]`. Low pointed golden leaf mass on east bank, distinct from the woody gold tree families.

[Source crop](PokeD_GoldenLeafClump_source.png) | [Seven treatments](PokeD_GoldenLeafClump_variations.png) | [Four directions](PokeD_GoldenLeafClump_geometry.png)

- [Base](../PokeD_GoldenLeafClump.vox) — 1244 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeD_GoldenLeafClump_Cartoon.vox) — 1292 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeD_GoldenLeafClump_CratePalette.vox) — 1244 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeD_GoldenLeafClump_TwoColor.vox) — 1244 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeD_GoldenLeafClump_Cartoon_TwoColor.vox) — 1292 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeD_GoldenLeafClump_CratePalette_TwoColor.vox) — 1244 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeD_GoldenLeafClump_Cartoon_CratePalette_TwoColor.vox) — 1292 voxels; 1 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
