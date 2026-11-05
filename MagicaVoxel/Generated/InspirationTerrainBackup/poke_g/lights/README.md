# PokeG_RoundStreetlight

Wide low-domed gray head, short pale diffuser band, slender stem and tiered round base.

Canvas: 16 × 16 × 48 voxels, Z-up, ground at z=0. Source conversion estimate: 1 voxels per displayed pixel; footprint/depth and height interpreted from sprite. All source-relative proportions are estimates.

[Source crop](PokeG_RoundStreetlight_source.png) · [All variations, day/night](variations.png) · [Four cardinal views](geometry.png)

| Treatment | File | Voxels | Colors / groups |
| --- | --- | --- | --- |
| Base | [PokeG_RoundStreetlight.vox](../PokeG_RoundStreetlight.vox) | 1492 | 4 / emitter, structure |
| Cartoon | [PokeG_RoundStreetlight_Cartoon.vox](../PokeG_RoundStreetlight_Cartoon.vox) | 1876 | 4 / emitter, structure |
| CratePalette | [PokeG_RoundStreetlight_CratePalette.vox](../PokeG_RoundStreetlight_CratePalette.vox) | 1492 | 4 / emitter, structure |
| TwoColor | [PokeG_RoundStreetlight_TwoColor.vox](../PokeG_RoundStreetlight_TwoColor.vox) | 1492 | 2 / emitter, structure |
| Cartoon_TwoColor | [PokeG_RoundStreetlight_Cartoon_TwoColor.vox](../PokeG_RoundStreetlight_Cartoon_TwoColor.vox) | 1876 | 2 / emitter, structure |
| CratePalette_TwoColor | [PokeG_RoundStreetlight_CratePalette_TwoColor.vox](../PokeG_RoundStreetlight_CratePalette_TwoColor.vox) | 1492 | 2 / emitter, structure |
| Cartoon_CratePalette_TwoColor | [PokeG_RoundStreetlight_Cartoon_CratePalette_TwoColor.vox](../PokeG_RoundStreetlight_Cartoon_CratePalette_TwoColor.vox) | 1876 | 2 / emitter, structure |

Luminous voxels use Emit, Emission .75, Power 2. No transparency is implied: these are emitting diffusers/flames, or the burner inside the open stone lantern. Color-only treatments preserve the complete emitter mask. The current minimal-flat-color amendment retains one color per semantic group; light remains a dedicated material.

The separate Pixelwood frame group (where present) supplies `shadowless_colors` in the manifest, independently of the structural post. In other families, assess cap/pillar shadows during level integration.

Runtime voxel reading and day/night surface rendering were checked in an isolated copy of the current game. Preview spill comes from a harness omni. Whole models are not registered level pieces and no cells were exported. See the [collection report](../../lights/README.md), [manifest](manifest.json), and [lighting contract](../../../knowledge/LIGHTS.md).
