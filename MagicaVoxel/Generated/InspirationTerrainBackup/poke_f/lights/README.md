# PokeF_TwinGlobeStreetlight

Paired low-domed lamps on rising Y arms and one ringed pedestal. Two heads in one complete file.

Canvas: 32 × 12 × 48 voxels, Z-up, ground at z=0. Source conversion estimate: 1 voxels per displayed pixel; footprint/depth and height interpreted from sprite. All source-relative proportions are estimates.

[Source crop](PokeF_TwinGlobeStreetlight_source.png) · [All variations, day/night](variations.png) · [Four cardinal views](geometry.png)

| Treatment | File | Voxels | Colors / groups |
| --- | --- | --- | --- |
| Base | [PokeF_TwinGlobeStreetlight.vox](../PokeF_TwinGlobeStreetlight.vox) | 1644 | 4 / emitter, structure |
| Cartoon | [PokeF_TwinGlobeStreetlight_Cartoon.vox](../PokeF_TwinGlobeStreetlight_Cartoon.vox) | 2128 | 4 / emitter, structure |
| CratePalette | [PokeF_TwinGlobeStreetlight_CratePalette.vox](../PokeF_TwinGlobeStreetlight_CratePalette.vox) | 1644 | 4 / emitter, structure |
| TwoColor | [PokeF_TwinGlobeStreetlight_TwoColor.vox](../PokeF_TwinGlobeStreetlight_TwoColor.vox) | 1644 | 2 / emitter, structure |
| Cartoon_TwoColor | [PokeF_TwinGlobeStreetlight_Cartoon_TwoColor.vox](../PokeF_TwinGlobeStreetlight_Cartoon_TwoColor.vox) | 2128 | 2 / emitter, structure |
| CratePalette_TwoColor | [PokeF_TwinGlobeStreetlight_CratePalette_TwoColor.vox](../PokeF_TwinGlobeStreetlight_CratePalette_TwoColor.vox) | 1644 | 2 / emitter, structure |
| Cartoon_CratePalette_TwoColor | [PokeF_TwinGlobeStreetlight_Cartoon_CratePalette_TwoColor.vox](../PokeF_TwinGlobeStreetlight_Cartoon_CratePalette_TwoColor.vox) | 2128 | 2 / emitter, structure |

Luminous voxels use Emit, Emission .75, Power 2. No transparency is implied: these are emitting diffusers/flames, or the burner inside the open stone lantern. Color-only treatments preserve the complete emitter mask. The current minimal-flat-color amendment retains one color per semantic group; light remains a dedicated material.

The separate Pixelwood frame group (where present) supplies `shadowless_colors` in the manifest, independently of the structural post. In other families, assess cap/pillar shadows during level integration.

Runtime voxel reading and day/night surface rendering were checked in an isolated copy of the current game. Preview spill comes from a harness omni. Whole models are not registered level pieces and no cells were exported. See the [collection report](../../lights/README.md), [manifest](manifest.json), and [lighting contract](../../../knowledge/LIGHTS.md).
