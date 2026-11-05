# PokeC_SilverStreetLantern

Same silver lantern artwork as poke_b. Reuses its complete geometry and palette under this image folder; not an additional design.

Canvas: 12 × 12 × 40 voxels, Z-up, ground at z=0. Source conversion estimate: 1 voxels per displayed pixel; footprint/depth and height interpreted from sprite. All source-relative proportions are estimates.

[Source crop](PokeC_SilverStreetLantern_source.png) · [All variations, day/night](variations.png) · [Four cardinal views](geometry.png)

| Treatment | File | Voxels | Colors / groups |
| --- | --- | --- | --- |
| Base | [PokeC_SilverStreetLantern.vox](../PokeC_SilverStreetLantern.vox) | 1220 | 4 / emitter, structure |
| Cartoon | [PokeC_SilverStreetLantern_Cartoon.vox](../PokeC_SilverStreetLantern_Cartoon.vox) | 1396 | 4 / emitter, structure |
| CratePalette | [PokeC_SilverStreetLantern_CratePalette.vox](../PokeC_SilverStreetLantern_CratePalette.vox) | 1220 | 4 / emitter, structure |
| TwoColor | [PokeC_SilverStreetLantern_TwoColor.vox](../PokeC_SilverStreetLantern_TwoColor.vox) | 1220 | 2 / emitter, structure |
| Cartoon_TwoColor | [PokeC_SilverStreetLantern_Cartoon_TwoColor.vox](../PokeC_SilverStreetLantern_Cartoon_TwoColor.vox) | 1396 | 2 / emitter, structure |
| CratePalette_TwoColor | [PokeC_SilverStreetLantern_CratePalette_TwoColor.vox](../PokeC_SilverStreetLantern_CratePalette_TwoColor.vox) | 1220 | 2 / emitter, structure |
| Cartoon_CratePalette_TwoColor | [PokeC_SilverStreetLantern_Cartoon_CratePalette_TwoColor.vox](../PokeC_SilverStreetLantern_Cartoon_CratePalette_TwoColor.vox) | 1396 | 2 / emitter, structure |

Luminous voxels use Emit, Emission .75, Power 2. No transparency is implied: these are emitting diffusers/flames, or the burner inside the open stone lantern. Color-only treatments preserve the complete emitter mask. The current minimal-flat-color amendment retains one color per semantic group; light remains a dedicated material.

The separate Pixelwood frame group (where present) supplies `shadowless_colors` in the manifest, independently of the structural post. In other families, assess cap/pillar shadows during level integration.

Runtime voxel reading and day/night surface rendering were checked in an isolated copy of the current game. Preview spill comes from a harness omni. Whole models are not registered level pieces and no cells were exported. See the [collection report](../../lights/README.md), [manifest](manifest.json), and [lighting contract](../../../knowledge/LIGHTS.md).
