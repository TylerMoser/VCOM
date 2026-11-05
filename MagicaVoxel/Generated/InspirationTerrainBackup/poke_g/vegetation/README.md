# poke_g.png — flowers, bushes and grass

4 new appearances; 28 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeG_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[139, 131, 159, 151]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeG_ShortGrassPatch_source.png) | [Seven treatments](PokeG_ShortGrassPatch_variations.png) | [Four directions](PokeG_ShortGrassPatch_geometry.png)

- [Base](../PokeG_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeG_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeG_ShortGrassPatch_CratePalette.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeG_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeG_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeG_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeG_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeG_PinkWhiteDaisies

Canvas XYZ: **16 x 16 x 8**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[62, 141, 84, 161]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeG_PinkWhiteDaisies_source.png) | [Seven treatments](PokeG_PinkWhiteDaisies_variations.png) | [Four directions](PokeG_PinkWhiteDaisies_geometry.png)

- [Base](../PokeG_PinkWhiteDaisies.vox) — 140 voxels; 7 paint colors; 3 rooted component(s).
- [Cartoon](../PokeG_PinkWhiteDaisies_Cartoon.vox) — 236 voxels; 6 paint colors; 4 rooted component(s).
- [CratePalette](../PokeG_PinkWhiteDaisies_CratePalette.vox) — 140 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeG_PinkWhiteDaisies_TwoColor.vox) — 140 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeG_PinkWhiteDaisies_Cartoon_TwoColor.vox) — 236 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeG_PinkWhiteDaisies_CratePalette_TwoColor.vox) — 140 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeG_PinkWhiteDaisies_Cartoon_CratePalette_TwoColor.vox) — 236 voxels; 3 paint colors; 4 rooted component(s).

### PokeG_OrangeDaisies

Canvas XYZ: **16 x 16 x 8**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[109, 155, 132, 177]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeG_OrangeDaisies_source.png) | [Seven treatments](PokeG_OrangeDaisies_variations.png) | [Four directions](PokeG_OrangeDaisies_geometry.png)

- [Base](../PokeG_OrangeDaisies.vox) — 140 voxels; 7 paint colors; 3 rooted component(s).
- [Cartoon](../PokeG_OrangeDaisies_Cartoon.vox) — 236 voxels; 6 paint colors; 4 rooted component(s).
- [CratePalette](../PokeG_OrangeDaisies_CratePalette.vox) — 140 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PokeG_OrangeDaisies_TwoColor.vox) — 140 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeG_OrangeDaisies_Cartoon_TwoColor.vox) — 236 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeG_OrangeDaisies_CratePalette_TwoColor.vox) — 140 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeG_OrangeDaisies_Cartoon_CratePalette_TwoColor.vox) — 236 voxels; 3 paint colors; 4 rooted component(s).

### PokeG_RedFlowerSpray

Canvas XYZ: **12 x 12 x 12**. Approximate source scale: 1 voxel(s) per displayed pixel. Crop XYXY: `[287, 124, 305, 146]`. Three reddish-brown flower heads on short stems beside paths.

[Source crop](PokeG_RedFlowerSpray_source.png) | [Seven treatments](PokeG_RedFlowerSpray_variations.png) | [Four directions](PokeG_RedFlowerSpray_geometry.png)

- [Base](../PokeG_RedFlowerSpray.vox) — 125 voxels; 7 paint colors; 3 rooted component(s).
- [Cartoon](../PokeG_RedFlowerSpray_Cartoon.vox) — 212 voxels; 5 paint colors; 1 rooted component(s).
- [CratePalette](../PokeG_RedFlowerSpray_CratePalette.vox) — 125 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeG_RedFlowerSpray_TwoColor.vox) — 125 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeG_RedFlowerSpray_Cartoon_TwoColor.vox) — 212 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeG_RedFlowerSpray_CratePalette_TwoColor.vox) — 125 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeG_RedFlowerSpray_Cartoon_CratePalette_TwoColor.vox) — 212 voxels; 3 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
