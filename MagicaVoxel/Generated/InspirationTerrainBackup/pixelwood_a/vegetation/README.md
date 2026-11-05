# pixelwood_a.jpg — flowers, bushes and grass

3 new appearances; 21 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PixelwoodA_WhiteDaisy

Canvas XYZ: **16 x 16 x 10**. Approximate source scale: 0.333 voxel(s) per displayed pixel. Crop XYXY: `[601, 40, 649, 92]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PixelwoodA_WhiteDaisy_source.png) | [Seven treatments](PixelwoodA_WhiteDaisy_variations.png) | [Four directions](PixelwoodA_WhiteDaisy_geometry.png)

- [Base](../PixelwoodA_WhiteDaisy.vox) — 142 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PixelwoodA_WhiteDaisy_Cartoon.vox) — 212 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PixelwoodA_WhiteDaisy_CratePalette.vox) — 142 voxels; 6 paint colors; 3 rooted component(s).
- [TwoColor](../PixelwoodA_WhiteDaisy_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PixelwoodA_WhiteDaisy_Cartoon_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PixelwoodA_WhiteDaisy_CratePalette_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PixelwoodA_WhiteDaisy_Cartoon_CratePalette_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).

### PixelwoodA_PurpleFlowerSpike

Canvas XYZ: **12 x 12 x 20**. Approximate source scale: 0.333 voxel(s) per displayed pixel. Crop XYXY: `[45, 397, 84, 449]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PixelwoodA_PurpleFlowerSpike_source.png) | [Seven treatments](PixelwoodA_PurpleFlowerSpike_variations.png) | [Four directions](PixelwoodA_PurpleFlowerSpike_geometry.png)

- [Base](../PixelwoodA_PurpleFlowerSpike.vox) — 335 voxels; 5 paint colors; 1 rooted component(s).
- [Cartoon](../PixelwoodA_PurpleFlowerSpike_Cartoon.vox) — 384 voxels; 5 paint colors; 1 rooted component(s).
- [CratePalette](../PixelwoodA_PurpleFlowerSpike_CratePalette.vox) — 335 voxels; 4 paint colors; 1 rooted component(s).
- [TwoColor](../PixelwoodA_PurpleFlowerSpike_TwoColor.vox) — 335 voxels; 2 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PixelwoodA_PurpleFlowerSpike_Cartoon_TwoColor.vox) — 384 voxels; 2 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PixelwoodA_PurpleFlowerSpike_CratePalette_TwoColor.vox) — 335 voxels; 2 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PixelwoodA_PurpleFlowerSpike_Cartoon_CratePalette_TwoColor.vox) — 384 voxels; 2 paint colors; 1 rooted component(s).

### PixelwoodA_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 0.333 voxel(s) per displayed pixel. Crop XYXY: `[357, 56, 416, 92]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PixelwoodA_ShortGrassPatch_source.png) | [Seven treatments](PixelwoodA_ShortGrassPatch_variations.png) | [Four directions](PixelwoodA_ShortGrassPatch_geometry.png)

- [Base](../PixelwoodA_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PixelwoodA_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PixelwoodA_ShortGrassPatch_CratePalette.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [TwoColor](../PixelwoodA_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PixelwoodA_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PixelwoodA_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PixelwoodA_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

## Reused models

- **PixelwoodA_SquareShrub**: [Base](../../pixelwood_a/PixelwoodA_SquareShrub.vox), [Cartoon](../../pixelwood_a/PixelwoodA_SquareShrub_Cartoon.vox), [CratePalette](../../pixelwood_a/PixelwoodA_SquareShrub_CratePalette.vox), [TwoColor](../../pixelwood_a/PixelwoodA_SquareShrub_TwoColor.vox), [Cartoon_TwoColor](../../pixelwood_a/PixelwoodA_SquareShrub_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../pixelwood_a/PixelwoodA_SquareShrub_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../pixelwood_a/PixelwoodA_SquareShrub_Cartoon_CratePalette_TwoColor.vox).

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
