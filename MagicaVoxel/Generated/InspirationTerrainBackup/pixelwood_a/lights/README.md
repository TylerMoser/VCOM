# PixelwoodA_PostLantern

Square amber lantern, dark corner mullions, broad hipped cap and squared foot. Three source pixels per voxel.

Canvas: 16 × 16 × 40 voxels, Z-up, ground at z=0. Source conversion estimate: 0.3333 voxels per displayed pixel; footprint/depth and height interpreted from sprite. All source-relative proportions are estimates.

[Source crop](PixelwoodA_PostLantern_source.png) · [All variations, day/night](variations.png) · [Four cardinal views](geometry.png)

| Treatment | File | Voxels | Colors / groups |
| --- | --- | --- | --- |
| Base | [PixelwoodA_PostLantern.vox](../PixelwoodA_PostLantern.vox) | 2868 | 5 / emitter, frame, structure |
| Cartoon | [PixelwoodA_PostLantern_Cartoon.vox](../PixelwoodA_PostLantern_Cartoon.vox) | 3016 | 5 / emitter, frame, structure |
| CratePalette | [PixelwoodA_PostLantern_CratePalette.vox](../PixelwoodA_PostLantern_CratePalette.vox) | 2868 | 4 / emitter, frame, structure |
| TwoColor | [PixelwoodA_PostLantern_TwoColor.vox](../PixelwoodA_PostLantern_TwoColor.vox) | 2868 | 3 / emitter, frame, structure |
| Cartoon_TwoColor | [PixelwoodA_PostLantern_Cartoon_TwoColor.vox](../PixelwoodA_PostLantern_Cartoon_TwoColor.vox) | 3016 | 3 / emitter, frame, structure |
| CratePalette_TwoColor | [PixelwoodA_PostLantern_CratePalette_TwoColor.vox](../PixelwoodA_PostLantern_CratePalette_TwoColor.vox) | 2868 | 3 / emitter, frame, structure |
| Cartoon_CratePalette_TwoColor | [PixelwoodA_PostLantern_Cartoon_CratePalette_TwoColor.vox](../PixelwoodA_PostLantern_Cartoon_CratePalette_TwoColor.vox) | 3016 | 3 / emitter, frame, structure |

Luminous voxels use Emit, Emission .75, Power 1.5. No transparency is implied: these are emitting diffusers/flames, or the burner inside the open stone lantern. Color-only treatments preserve the complete emitter mask. The current minimal-flat-color amendment retains one color per semantic group; light remains a dedicated material.

The separate Pixelwood frame group (where present) supplies `shadowless_colors` in the manifest, independently of the structural post. In other families, assess cap/pillar shadows during level integration.

Runtime voxel reading and day/night surface rendering were checked in an isolated copy of the current game. Preview spill comes from a harness omni. Whole models are not registered level pieces and no cells were exported. See the [collection report](../../lights/README.md), [manifest](manifest.json), and [lighting contract](../../../knowledge/LIGHTS.md).
