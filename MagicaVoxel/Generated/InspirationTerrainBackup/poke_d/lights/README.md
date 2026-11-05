# PokeD_StoneLantern

Small stone garden lantern: broad rounded cap and finial, open chamber, short feet. Source unlit dark chamber; small warm burner inferred for usable night lighting.

Canvas: 16 × 16 × 20 voxels, Z-up, ground at z=0. Source conversion estimate: 1 voxels per displayed pixel; footprint/depth and height interpreted from sprite. All source-relative proportions are estimates.

[Source crop](PokeD_StoneLantern_source.png) · [All variations, day/night](variations.png) · [Four cardinal views](geometry.png)

| Treatment | File | Voxels | Colors / groups |
| --- | --- | --- | --- |
| Base | [PokeD_StoneLantern.vox](../PokeD_StoneLantern.vox) | 1540 | 4 / emitter, stone |
| Cartoon | [PokeD_StoneLantern_Cartoon.vox](../PokeD_StoneLantern_Cartoon.vox) | 1612 | 4 / emitter, stone |
| CratePalette | [PokeD_StoneLantern_CratePalette.vox](../PokeD_StoneLantern_CratePalette.vox) | 1540 | 3 / emitter, stone |
| TwoColor | [PokeD_StoneLantern_TwoColor.vox](../PokeD_StoneLantern_TwoColor.vox) | 1540 | 2 / emitter, stone |
| Cartoon_TwoColor | [PokeD_StoneLantern_Cartoon_TwoColor.vox](../PokeD_StoneLantern_Cartoon_TwoColor.vox) | 1612 | 2 / emitter, stone |
| CratePalette_TwoColor | [PokeD_StoneLantern_CratePalette_TwoColor.vox](../PokeD_StoneLantern_CratePalette_TwoColor.vox) | 1540 | 2 / emitter, stone |
| Cartoon_CratePalette_TwoColor | [PokeD_StoneLantern_Cartoon_CratePalette_TwoColor.vox](../PokeD_StoneLantern_Cartoon_CratePalette_TwoColor.vox) | 1612 | 2 / emitter, stone |

Luminous voxels use Emit, Emission .75, Power 1. No transparency is implied: these are emitting diffusers/flames, or the burner inside the open stone lantern. Color-only treatments preserve the complete emitter mask. The current minimal-flat-color amendment retains one color per semantic group; light remains a dedicated material.

The separate Pixelwood frame group (where present) supplies `shadowless_colors` in the manifest, independently of the structural post. In other families, assess cap/pillar shadows during level integration.

Runtime voxel reading and day/night surface rendering were checked in an isolated copy of the current game. Preview spill comes from a harness omni. Whole models are not registered level pieces and no cells were exported. See the [collection report](../../lights/README.md), [manifest](manifest.json), and [lighting contract](../../../knowledge/LIGHTS.md).
