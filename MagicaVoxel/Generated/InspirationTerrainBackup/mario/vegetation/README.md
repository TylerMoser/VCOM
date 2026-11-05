# mario.jpg — flowers, bushes and grass

2 new appearances; 14 complete VOX files. [Collection index](../../vegetation/README.md).

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## New models

### Mario_BladeClump

Canvas XYZ: **12 x 12 x 12**. Approximate source scale: 0.333 voxel(s) per displayed pixel. Crop XYXY: `[568, 346, 608, 384]`. Dark outlined V-shaped grass; volumetric radial interpretation of side-view artwork.

[Source crop](Mario_BladeClump_source.png) | [Seven treatments](Mario_BladeClump_variations.png) | [Four directions](Mario_BladeClump_geometry.png)

- [Base](../Mario_BladeClump.vox) — 144 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../Mario_BladeClump_Cartoon.vox) — 236 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../Mario_BladeClump_CratePalette.vox) — 144 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../Mario_BladeClump_TwoColor.vox) — 144 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../Mario_BladeClump_Cartoon_TwoColor.vox) — 236 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../Mario_BladeClump_CratePalette_TwoColor.vox) — 144 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../Mario_BladeClump_Cartoon_CratePalette_TwoColor.vox) — 236 voxels; 1 paint colors; 1 rooted component(s).

### Mario_SerratedBush

Canvas XYZ: **32 x 16 x 16**. Approximate source scale: 0.333 voxel(s) per displayed pixel. Crop XYXY: `[244, 170, 344, 234]`. Low jagged silhouette in background, interpreted as freestanding bush; not the blue hill characters.

[Source crop](Mario_SerratedBush_source.png) | [Seven treatments](Mario_SerratedBush_variations.png) | [Four directions](Mario_SerratedBush_geometry.png)

- [Base](../Mario_SerratedBush.vox) — 4889 voxels; 3 paint colors; 1 rooted component(s).
- [Cartoon](../Mario_SerratedBush_Cartoon.vox) — 5000 voxels; 3 paint colors; 1 rooted component(s).
- [CratePalette](../Mario_SerratedBush_CratePalette.vox) — 4889 voxels; 2 paint colors; 1 rooted component(s).
- [TwoColor](../Mario_SerratedBush_TwoColor.vox) — 4889 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_TwoColor](../Mario_SerratedBush_Cartoon_TwoColor.vox) — 5000 voxels; 1 paint colors; 1 rooted component(s).
- [CratePalette_TwoColor](../Mario_SerratedBush_CratePalette_TwoColor.vox) — 4889 voxels; 1 paint colors; 1 rooted component(s).
- [Cartoon_CratePalette_TwoColor](../Mario_SerratedBush_Cartoon_CratePalette_TwoColor.vox) — 5000 voxels; 1 paint colors; 1 rooted component(s).

## Reused models

No previously authored bush family is required for this source.

## Scope and continuation

Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.

Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.
