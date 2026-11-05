# PokeM_BronzePostLantern

Visible at lower image edge: bronze pointed hood, broad cream chamber and thin pole. Base and lower stem are cropped away; inferred matching stepped pedestal, total height 48.

Canvas: 16 × 16 × 48 voxels, Z-up, ground at z=0. Source conversion estimate: 1 voxels per displayed pixel; footprint/depth and height interpreted from sprite. All source-relative proportions are estimates.

[Source crop](PokeM_BronzePostLantern_source.png) · [All variations, day/night](variations.png) · [Four cardinal views](geometry.png)

| Treatment | File | Voxels | Colors / groups |
| --- | --- | --- | --- |
| Base | [PokeM_BronzePostLantern.vox](../PokeM_BronzePostLantern.vox) | 1860 | 4 / emitter, structure |
| Cartoon | [PokeM_BronzePostLantern_Cartoon.vox](../PokeM_BronzePostLantern_Cartoon.vox) | 2100 | 4 / emitter, structure |
| CratePalette | [PokeM_BronzePostLantern_CratePalette.vox](../PokeM_BronzePostLantern_CratePalette.vox) | 1860 | 4 / emitter, structure |
| TwoColor | [PokeM_BronzePostLantern_TwoColor.vox](../PokeM_BronzePostLantern_TwoColor.vox) | 1860 | 2 / emitter, structure |
| Cartoon_TwoColor | [PokeM_BronzePostLantern_Cartoon_TwoColor.vox](../PokeM_BronzePostLantern_Cartoon_TwoColor.vox) | 2100 | 2 / emitter, structure |
| CratePalette_TwoColor | [PokeM_BronzePostLantern_CratePalette_TwoColor.vox](../PokeM_BronzePostLantern_CratePalette_TwoColor.vox) | 1860 | 2 / emitter, structure |
| Cartoon_CratePalette_TwoColor | [PokeM_BronzePostLantern_Cartoon_CratePalette_TwoColor.vox](../PokeM_BronzePostLantern_Cartoon_CratePalette_TwoColor.vox) | 2100 | 2 / emitter, structure |

Luminous voxels use Emit, Emission .75, Power 2. No transparency is implied: these are emitting diffusers/flames, or the burner inside the open stone lantern. Color-only treatments preserve the complete emitter mask. The current minimal-flat-color amendment retains one color per semantic group; light remains a dedicated material.

The separate Pixelwood frame group (where present) supplies `shadowless_colors` in the manifest, independently of the structural post. In other families, assess cap/pillar shadows during level integration.

Runtime voxel reading and day/night surface rendering were checked in an isolated copy of the current game. Preview spill comes from a harness omni. Whole models are not registered level pieces and no cells were exported. See the [collection report](../../lights/README.md), [manifest](manifest.json), and [lighting contract](../../../knowledge/LIGHTS.md).
