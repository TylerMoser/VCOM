# PokeN_TealStreetlight

Dark teal disc cap, recessed gray-blue diffuser band and flared pedestal. Luminescence inferred from identifiable lamp fixture in daytime source.

Canvas: 16 × 16 × 40 voxels, Z-up, ground at z=0. Source conversion estimate: 1 voxels per displayed pixel; footprint/depth and height interpreted from sprite. All source-relative proportions are estimates.

[Source crop](PokeN_TealStreetlight_source.png) · [All variations, day/night](variations.png) · [Four cardinal views](geometry.png)

| Treatment | File | Voxels | Colors / groups |
| --- | --- | --- | --- |
| Base | [PokeN_TealStreetlight.vox](../PokeN_TealStreetlight.vox) | 1460 | 4 / emitter, structure |
| Cartoon | [PokeN_TealStreetlight_Cartoon.vox](../PokeN_TealStreetlight_Cartoon.vox) | 1780 | 4 / emitter, structure |
| CratePalette | [PokeN_TealStreetlight_CratePalette.vox](../PokeN_TealStreetlight_CratePalette.vox) | 1460 | 4 / emitter, structure |
| TwoColor | [PokeN_TealStreetlight_TwoColor.vox](../PokeN_TealStreetlight_TwoColor.vox) | 1460 | 2 / emitter, structure |
| Cartoon_TwoColor | [PokeN_TealStreetlight_Cartoon_TwoColor.vox](../PokeN_TealStreetlight_Cartoon_TwoColor.vox) | 1780 | 2 / emitter, structure |
| CratePalette_TwoColor | [PokeN_TealStreetlight_CratePalette_TwoColor.vox](../PokeN_TealStreetlight_CratePalette_TwoColor.vox) | 1460 | 2 / emitter, structure |
| Cartoon_CratePalette_TwoColor | [PokeN_TealStreetlight_Cartoon_CratePalette_TwoColor.vox](../PokeN_TealStreetlight_Cartoon_CratePalette_TwoColor.vox) | 1780 | 2 / emitter, structure |

Luminous voxels use Emit, Emission .75, Power 2. No transparency is implied: these are emitting diffusers/flames, or the burner inside the open stone lantern. Color-only treatments preserve the complete emitter mask. The current minimal-flat-color amendment retains one color per semantic group; light remains a dedicated material.

The separate Pixelwood frame group (where present) supplies `shadowless_colors` in the manifest, independently of the structural post. In other families, assess cap/pillar shadows during level integration.

Runtime voxel reading and day/night surface rendering were checked in an isolated copy of the current game. Preview spill comes from a harness omni. Whole models are not registered level pieces and no cells were exported. See the [collection report](../../lights/README.md), [manifest](manifest.json), and [lighting contract](../../../knowledge/LIGHTS.md).
