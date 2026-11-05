# PokeJ_DarkStreetLantern

Small dark lantern left of north house. JPEG obscures detail; inferred faceted cap and small luminous chamber. Existing scale estimate: 24 displayed pixels per tile.

Canvas: 10 × 10 × 28 voxels, Z-up, ground at z=0. Source conversion estimate: 0.6667 voxels per displayed pixel; footprint/depth and height interpreted from sprite. All source-relative proportions are estimates.

[Source crop](PokeJ_DarkStreetLantern_source.png) · [All variations, day/night](variations.png) · [Four cardinal views](geometry.png)

| Treatment | File | Voxels | Colors / groups |
| --- | --- | --- | --- |
| Base | [PokeJ_DarkStreetLantern.vox](../PokeJ_DarkStreetLantern.vox) | 620 | 4 / emitter, structure |
| Cartoon | [PokeJ_DarkStreetLantern_Cartoon.vox](../PokeJ_DarkStreetLantern_Cartoon.vox) | 732 | 4 / emitter, structure |
| CratePalette | [PokeJ_DarkStreetLantern_CratePalette.vox](../PokeJ_DarkStreetLantern_CratePalette.vox) | 620 | 4 / emitter, structure |
| TwoColor | [PokeJ_DarkStreetLantern_TwoColor.vox](../PokeJ_DarkStreetLantern_TwoColor.vox) | 620 | 2 / emitter, structure |
| Cartoon_TwoColor | [PokeJ_DarkStreetLantern_Cartoon_TwoColor.vox](../PokeJ_DarkStreetLantern_Cartoon_TwoColor.vox) | 732 | 2 / emitter, structure |
| CratePalette_TwoColor | [PokeJ_DarkStreetLantern_CratePalette_TwoColor.vox](../PokeJ_DarkStreetLantern_CratePalette_TwoColor.vox) | 620 | 2 / emitter, structure |
| Cartoon_CratePalette_TwoColor | [PokeJ_DarkStreetLantern_Cartoon_CratePalette_TwoColor.vox](../PokeJ_DarkStreetLantern_Cartoon_CratePalette_TwoColor.vox) | 732 | 2 / emitter, structure |

Luminous voxels use Emit, Emission .75, Power 1.5. No transparency is implied: these are emitting diffusers/flames, or the burner inside the open stone lantern. Color-only treatments preserve the complete emitter mask. The current minimal-flat-color amendment retains one color per semantic group; light remains a dedicated material.

The separate Pixelwood frame group (where present) supplies `shadowless_colors` in the manifest, independently of the structural post. In other families, assess cap/pillar shadows during level integration.

Runtime voxel reading and day/night surface rendering were checked in an isolated copy of the current game. Preview spill comes from a harness omni. Whole models are not registered level pieces and no cells were exported. See the [collection report](../../lights/README.md), [manifest](manifest.json), and [lighting contract](../../../knowledge/LIGHTS.md).
