# poke_c.png — flowers, bushes and grass

5 new appearances; 35 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeC_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[600, 518, 624, 540]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeC_ShortGrassPatch_source.png) | [Seven treatments](PokeC_ShortGrassPatch_variations.png) | [Four directions](PokeC_ShortGrassPatch_geometry.png)

- [Base](../PokeC_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeC_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeC_ShortGrassPatch_CratePalette.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeC_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeC_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeC_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeC_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeC_WhiteDaisies

Canvas XYZ: **16 x 16 x 8**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[25, 255, 53, 284]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeC_WhiteDaisies_source.png) | [Seven treatments](PokeC_WhiteDaisies_variations.png) | [Four directions](PokeC_WhiteDaisies_geometry.png)

- [Base](../PokeC_WhiteDaisies.vox) — 140 voxels; 7 paint colors; 3 rooted component(s).
- [Cartoon](../PokeC_WhiteDaisies_Cartoon.vox) — 236 voxels; 6 paint colors; 4 rooted component(s).
- [CratePalette](../PokeC_WhiteDaisies_CratePalette.vox) — 140 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeC_WhiteDaisies_TwoColor.vox) — 140 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeC_WhiteDaisies_Cartoon_TwoColor.vox) — 236 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeC_WhiteDaisies_CratePalette_TwoColor.vox) — 140 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeC_WhiteDaisies_Cartoon_CratePalette_TwoColor.vox) — 236 voxels; 3 paint colors; 4 rooted component(s).

### PokeC_TallMeadowGrass

Canvas XYZ: **16 x 16 x 24**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[555, 620, 593, 660]`. 

[Source crop](PokeC_TallMeadowGrass_source.png) | [Seven treatments](PokeC_TallMeadowGrass_variations.png) | [Four directions](PokeC_TallMeadowGrass_geometry.png)

- [Base](../PokeC_TallMeadowGrass.vox) — 865 voxels; 3 paint colors; 2 rooted component(s).
- [Cartoon](../PokeC_TallMeadowGrass_Cartoon.vox) — 1048 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeC_TallMeadowGrass_CratePalette.vox) — 865 voxels; 2 paint colors; 2 rooted component(s).
- [TwoColor](../PokeC_TallMeadowGrass_TwoColor.vox) — 865 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_TwoColor](../PokeC_TallMeadowGrass_Cartoon_TwoColor.vox) — 1048 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeC_TallMeadowGrass_CratePalette_TwoColor.vox) — 865 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeC_TallMeadowGrass_Cartoon_CratePalette_TwoColor.vox) — 1048 voxels; 1 paint colors; 1 rooted component(s).

### PokeC_RiverReeds

Canvas XYZ: **16 x 16 x 22**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[348, 284, 371, 313]`. Emergent narrow blades: water is excluded, model rooted at its placement datum.

[Source crop](PokeC_RiverReeds_source.png) | [Seven treatments](PokeC_RiverReeds_variations.png) | [Four directions](PokeC_RiverReeds_geometry.png)

- [Base](../PokeC_RiverReeds.vox) — 281 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../PokeC_RiverReeds_Cartoon.vox) — 452 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeC_RiverReeds_CratePalette.vox) — 281 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../PokeC_RiverReeds_TwoColor.vox) — 281 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeC_RiverReeds_Cartoon_TwoColor.vox) — 452 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeC_RiverReeds_CratePalette_TwoColor.vox) — 281 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeC_RiverReeds_Cartoon_CratePalette_TwoColor.vox) — 452 voxels; 1 paint colors; 1 rooted component(s).

### PokeC_FloatingLeafCluster

Canvas XYZ: **16 x 16 x 3**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[369, 445, 401, 467]`. Small floating green leaf clusters; not rocks or creatures.

[Source crop](PokeC_FloatingLeafCluster_source.png) | [Seven treatments](PokeC_FloatingLeafCluster_variations.png) | [Four directions](PokeC_FloatingLeafCluster_geometry.png)

- [Base](../PokeC_FloatingLeafCluster.vox) — 137 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeC_FloatingLeafCluster_Cartoon.vox) — 120 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeC_FloatingLeafCluster_CratePalette.vox) — 137 voxels; 2 paint colors; 3 rooted component(s).
- [TwoColor](../PokeC_FloatingLeafCluster_TwoColor.vox) — 137 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeC_FloatingLeafCluster_Cartoon_TwoColor.vox) — 120 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeC_FloatingLeafCluster_CratePalette_TwoColor.vox) — 137 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeC_FloatingLeafCluster_Cartoon_CratePalette_TwoColor.vox) — 120 voxels; 1 paint colors; 4 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
