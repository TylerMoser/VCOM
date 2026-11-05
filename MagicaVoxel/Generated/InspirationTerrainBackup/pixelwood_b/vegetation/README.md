# pixelwood_b.gif — flowers, bushes and grass

0 new appearances; 0 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

## Reused models

- **PixelwoodA_SquareShrub**: [Base](../../pixelwood_a/PixelwoodA_SquareShrub.vox), [Cartoon](../../pixelwood_a/PixelwoodA_SquareShrub_Cartoon.vox), [CratePalette](../../pixelwood_a/PixelwoodA_SquareShrub_CratePalette.vox), [TwoColor](../../pixelwood_a/PixelwoodA_SquareShrub_TwoColor.vox), [Cartoon_TwoColor](../../pixelwood_a/PixelwoodA_SquareShrub_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../pixelwood_a/PixelwoodA_SquareShrub_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../pixelwood_a/PixelwoodA_SquareShrub_Cartoon_CratePalette_TwoColor.vox).
- **PixelwoodA_WhiteDaisy**: [Base](../../pixelwood_a/PixelwoodA_WhiteDaisy.vox), [Cartoon](../../pixelwood_a/PixelwoodA_WhiteDaisy_Cartoon.vox), [CratePalette](../../pixelwood_a/PixelwoodA_WhiteDaisy_CratePalette.vox), [TwoColor](../../pixelwood_a/PixelwoodA_WhiteDaisy_TwoColor.vox), [Cartoon_TwoColor](../../pixelwood_a/PixelwoodA_WhiteDaisy_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../pixelwood_a/PixelwoodA_WhiteDaisy_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../pixelwood_a/PixelwoodA_WhiteDaisy_Cartoon_CratePalette_TwoColor.vox).
- **PixelwoodA_ShortGrassPatch**: [Base](../../pixelwood_a/PixelwoodA_ShortGrassPatch.vox), [Cartoon](../../pixelwood_a/PixelwoodA_ShortGrassPatch_Cartoon.vox), [CratePalette](../../pixelwood_a/PixelwoodA_ShortGrassPatch_CratePalette.vox), [TwoColor](../../pixelwood_a/PixelwoodA_ShortGrassPatch_TwoColor.vox), [Cartoon_TwoColor](../../pixelwood_a/PixelwoodA_ShortGrassPatch_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../pixelwood_a/PixelwoodA_ShortGrassPatch_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../pixelwood_a/PixelwoodA_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox).

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
