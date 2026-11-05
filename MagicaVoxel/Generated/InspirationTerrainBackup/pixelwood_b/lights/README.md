# PixelwoodB_Campfire

Five GIF frames reviewed. Static flame inspired by frame 0; eight-sided rock ring and charred logs; no animation or detached sparks.

Canvas: 24 × 24 × 28 voxels, Z-up, ground at z=0. Source conversion estimate: 0.2 voxels per displayed pixel; footprint/depth and height interpreted from sprite. All source-relative proportions are estimates.

[Source crop](PixelwoodB_Campfire_source.png) · [All variations, day/night](variations.png) · [Four cardinal views](geometry.png)

| Treatment | File | Voxels | Colors / groups |
| --- | --- | --- | --- |
| Base | [PixelwoodB_Campfire.vox](../PixelwoodB_Campfire.vox) | 2695 | 6 / emitter, stone, wood |
| Cartoon | [PixelwoodB_Campfire_Cartoon.vox](../PixelwoodB_Campfire_Cartoon.vox) | 3056 | 5 / emitter, stone, wood |
| CratePalette | [PixelwoodB_Campfire_CratePalette.vox](../PixelwoodB_Campfire_CratePalette.vox) | 2695 | 6 / emitter, stone, wood |
| TwoColor | [PixelwoodB_Campfire_TwoColor.vox](../PixelwoodB_Campfire_TwoColor.vox) | 2695 | 3 / emitter, stone, wood |
| Cartoon_TwoColor | [PixelwoodB_Campfire_Cartoon_TwoColor.vox](../PixelwoodB_Campfire_Cartoon_TwoColor.vox) | 3056 | 3 / emitter, stone, wood |
| CratePalette_TwoColor | [PixelwoodB_Campfire_CratePalette_TwoColor.vox](../PixelwoodB_Campfire_CratePalette_TwoColor.vox) | 2695 | 3 / emitter, stone, wood |
| Cartoon_CratePalette_TwoColor | [PixelwoodB_Campfire_Cartoon_CratePalette_TwoColor.vox](../PixelwoodB_Campfire_Cartoon_CratePalette_TwoColor.vox) | 3056 | 3 / emitter, stone, wood |

Luminous voxels use Emit, Emission .75, Power 1.5. No transparency is implied: these are emitting diffusers/flames, or the burner inside the open stone lantern. Color-only treatments preserve the complete emitter mask. The current minimal-flat-color amendment retains one color per semantic group; light remains a dedicated material.

The separate Pixelwood frame group (where present) supplies `shadowless_colors` in the manifest, independently of the structural post. In other families, assess cap/pillar shadows during level integration.

Runtime voxel reading and day/night surface rendering were checked in an isolated copy of the current game. Preview spill comes from a harness omni. Whole models are not registered level pieces and no cells were exported. See the [collection report](../../lights/README.md), [manifest](manifest.json), and [lighting contract](../../../knowledge/LIGHTS.md).
