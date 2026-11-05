# poke_s.jpg — flowers, bushes and grass

5 new appearances; 35 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### PokeS_ShortGrassPatch

Canvas XYZ: **16 x 16 x 4**. Approximate source scale: 1.6 voxel(s) per displayed pixel. Crop XYXY: `[371, 434, 390, 448]`. One tile of short grass accents, without soil or a solid terrain slab. Repeating placements share this model.

[Source crop](PokeS_ShortGrassPatch_source.png) | [Seven treatments](PokeS_ShortGrassPatch_variations.png) | [Four directions](PokeS_ShortGrassPatch_geometry.png)

- [Base](../PokeS_ShortGrassPatch.vox) — 121 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeS_ShortGrassPatch_Cartoon.vox) — 108 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeS_ShortGrassPatch_CratePalette.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeS_ShortGrassPatch_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeS_ShortGrassPatch_Cartoon_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeS_ShortGrassPatch_CratePalette_TwoColor.vox) — 121 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeS_ShortGrassPatch_Cartoon_CratePalette_TwoColor.vox) — 108 voxels; 1 paint colors; 4 rooted component(s).

### PokeS_PinkFlowerCarpet

Canvas XYZ: **16 x 16 x 10**. Approximate source scale: 1.6 voxel(s) per displayed pixel. Crop XYXY: `[320, 374, 355, 395]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeS_PinkFlowerCarpet_source.png) | [Seven treatments](PokeS_PinkFlowerCarpet_variations.png) | [Four directions](PokeS_PinkFlowerCarpet_geometry.png)

- [Base](../PokeS_PinkFlowerCarpet.vox) — 142 voxels; 6 paint colors; 3 rooted component(s).
- [Cartoon](../PokeS_PinkFlowerCarpet_Cartoon.vox) — 212 voxels; 5 paint colors; 4 rooted component(s).
- [CratePalette](../PokeS_PinkFlowerCarpet_CratePalette.vox) — 142 voxels; 5 paint colors; 3 rooted component(s).
- [TwoColor](../PokeS_PinkFlowerCarpet_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeS_PinkFlowerCarpet_Cartoon_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeS_PinkFlowerCarpet_CratePalette_TwoColor.vox) — 142 voxels; 3 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeS_PinkFlowerCarpet_Cartoon_CratePalette_TwoColor.vox) — 212 voxels; 3 paint colors; 4 rooted component(s).

### PokeS_Sunflower

Canvas XYZ: **16 x 16 x 32**. Approximate source scale: 1.6 voxel(s) per displayed pixel. Crop XYXY: `[700, 151, 714, 174]`. Flower heads and leaves are solid forms; stems and depth are inferred from the overhead sprite.

[Source crop](PokeS_Sunflower_source.png) | [Seven treatments](PokeS_Sunflower_variations.png) | [Four directions](PokeS_Sunflower_geometry.png)

- [Base](../PokeS_Sunflower.vox) — 367 voxels; 5 paint colors; 1 rooted component(s).
- [Cartoon](../PokeS_Sunflower_Cartoon.vox) — 436 voxels; 5 paint colors; 1 rooted component(s).
- [CratePalette](../PokeS_Sunflower_CratePalette.vox) — 367 voxels; 3 paint colors; 1 rooted component(s).
- [TwoColor](../PokeS_Sunflower_TwoColor.vox) — 367 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../PokeS_Sunflower_Cartoon_TwoColor.vox) — 436 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeS_Sunflower_CratePalette_TwoColor.vox) — 367 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeS_Sunflower_Cartoon_CratePalette_TwoColor.vox) — 436 voxels; 3 paint colors; 1 rooted component(s).

### PokeS_GardenTallGrass

Canvas XYZ: **16 x 16 x 20**. Approximate source scale: 1.6 voxel(s) per displayed pixel. Crop XYXY: `[398, 239, 423, 261]`. 

[Source crop](PokeS_GardenTallGrass_source.png) | [Seven treatments](PokeS_GardenTallGrass_variations.png) | [Four directions](PokeS_GardenTallGrass_geometry.png)

- [Base](../PokeS_GardenTallGrass.vox) — 727 voxels; 3 paint colors; 2 rooted component(s).
- [Cartoon](../PokeS_GardenTallGrass_Cartoon.vox) — 880 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../PokeS_GardenTallGrass_CratePalette.vox) — 727 voxels; 2 paint colors; 2 rooted component(s).
- [TwoColor](../PokeS_GardenTallGrass_TwoColor.vox) — 727 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_TwoColor](../PokeS_GardenTallGrass_Cartoon_TwoColor.vox) — 880 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../PokeS_GardenTallGrass_CratePalette_TwoColor.vox) — 727 voxels; 1 paint colors; 2 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeS_GardenTallGrass_Cartoon_CratePalette_TwoColor.vox) — 880 voxels; 1 paint colors; 1 rooted component(s).

### PokeS_FloatingLeaves

Canvas XYZ: **16 x 16 x 3**. Approximate source scale: 1.6 voxel(s) per displayed pixel. Crop XYXY: `[133, 239, 146, 251]`. Small green aquatic leaf cluster; no clear flower in compressed source.

[Source crop](PokeS_FloatingLeaves_source.png) | [Seven treatments](PokeS_FloatingLeaves_variations.png) | [Four directions](PokeS_FloatingLeaves_geometry.png)

- [Base](../PokeS_FloatingLeaves.vox) — 137 voxels; 2 paint colors; 3 rooted component(s).
- [Cartoon](../PokeS_FloatingLeaves_Cartoon.vox) — 120 voxels; 2 paint colors; 4 rooted component(s).
- [CratePalette](../PokeS_FloatingLeaves_CratePalette.vox) — 137 voxels; 1 paint colors; 3 rooted component(s).
- [TwoColor](../PokeS_FloatingLeaves_TwoColor.vox) — 137 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_TwoColor](../PokeS_FloatingLeaves_Cartoon_TwoColor.vox) — 120 voxels; 1 paint colors; 4 rooted component(s).
- [CratePalette_TwoColor](../PokeS_FloatingLeaves_CratePalette_TwoColor.vox) — 137 voxels; 1 paint colors; 3 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../PokeS_FloatingLeaves_Cartoon_CratePalette_TwoColor.vox) — 120 voxels; 1 paint colors; 4 rooted component(s).

## Reused models

- **PokeS_ShrubMint**: [Base](../../poke_s/PokeS_ShrubMint.vox), [Cartoon](../../poke_s/PokeS_ShrubMint_Cartoon.vox), [CratePalette](../../poke_s/PokeS_ShrubMint_CratePalette.vox), [TwoColor](../../poke_s/PokeS_ShrubMint_TwoColor.vox), [Cartoon_TwoColor](../../poke_s/PokeS_ShrubMint_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../poke_s/PokeS_ShrubMint_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../poke_s/PokeS_ShrubMint_Cartoon_CratePalette_TwoColor.vox).
- **PokeS_ShrubTeal**: [Base](../../poke_s/PokeS_ShrubTeal.vox), [Cartoon](../../poke_s/PokeS_ShrubTeal_Cartoon.vox), [CratePalette](../../poke_s/PokeS_ShrubTeal_CratePalette.vox), [TwoColor](../../poke_s/PokeS_ShrubTeal_TwoColor.vox), [Cartoon_TwoColor](../../poke_s/PokeS_ShrubTeal_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../poke_s/PokeS_ShrubTeal_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../poke_s/PokeS_ShrubTeal_Cartoon_CratePalette_TwoColor.vox).
- **PokeS_ShrubPink**: [Base](../../poke_s/PokeS_ShrubPink.vox), [Cartoon](../../poke_s/PokeS_ShrubPink_Cartoon.vox), [CratePalette](../../poke_s/PokeS_ShrubPink_CratePalette.vox), [TwoColor](../../poke_s/PokeS_ShrubPink_TwoColor.vox), [Cartoon_TwoColor](../../poke_s/PokeS_ShrubPink_Cartoon_TwoColor.vox), [CratePalette_TwoColor](../../poke_s/PokeS_ShrubPink_CratePalette_TwoColor.vox), [Cartoon_CratePalette_TwoColor](../../poke_s/PokeS_ShrubPink_Cartoon_CratePalette_TwoColor.vox).

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
