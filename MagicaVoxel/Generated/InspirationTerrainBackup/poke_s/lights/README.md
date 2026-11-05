# PokeS_IvoryScrollLantern

Ivory curved shepherd-hook fixture repeated beside waterfalls. Small compressed image: scroll and hanging lantern reconstructed; approx. 10 displayed pixels per tile. Bilateral depth symmetry, intentional offset lantern preserved.

Canvas: 24 × 16 × 56 voxels, Z-up, ground at z=0. Source conversion estimate: 1.6 voxels per displayed pixel; footprint/depth and height interpreted from sprite. All source-relative proportions are estimates.

[Source crop](PokeS_IvoryScrollLantern_source.png) · [All variations, day/night](variations.png) · [Four cardinal views](geometry.png)

| Treatment | File | Voxels | Colors / groups |
| --- | --- | --- | --- |
| Base | [PokeS_IvoryScrollLantern.vox](../PokeS_IvoryScrollLantern.vox) | 1180 | 4 / emitter, structure |
| Cartoon | [PokeS_IvoryScrollLantern_Cartoon.vox](../PokeS_IvoryScrollLantern_Cartoon.vox) | 1408 | 4 / emitter, structure |
| CratePalette | [PokeS_IvoryScrollLantern_CratePalette.vox](../PokeS_IvoryScrollLantern_CratePalette.vox) | 1180 | 4 / emitter, structure |
| TwoColor | [PokeS_IvoryScrollLantern_TwoColor.vox](../PokeS_IvoryScrollLantern_TwoColor.vox) | 1180 | 2 / emitter, structure |
| Cartoon_TwoColor | [PokeS_IvoryScrollLantern_Cartoon_TwoColor.vox](../PokeS_IvoryScrollLantern_Cartoon_TwoColor.vox) | 1408 | 2 / emitter, structure |
| CratePalette_TwoColor | [PokeS_IvoryScrollLantern_CratePalette_TwoColor.vox](../PokeS_IvoryScrollLantern_CratePalette_TwoColor.vox) | 1180 | 2 / emitter, structure |
| Cartoon_CratePalette_TwoColor | [PokeS_IvoryScrollLantern_Cartoon_CratePalette_TwoColor.vox](../PokeS_IvoryScrollLantern_Cartoon_CratePalette_TwoColor.vox) | 1408 | 2 / emitter, structure |

Luminous voxels use Emit, Emission .75, Power 2. No transparency is implied: these are emitting diffusers/flames, or the burner inside the open stone lantern. Color-only treatments preserve the complete emitter mask. The current minimal-flat-color amendment retains one color per semantic group; light remains a dedicated material.

The separate Pixelwood frame group (where present) supplies `shadowless_colors` in the manifest, independently of the structural post. In other families, assess cap/pillar shadows during level integration.

Runtime voxel reading and day/night surface rendering were checked in an isolated copy of the current game. Preview spill comes from a harness omni. Whole models are not registered level pieces and no cells were exported. See the [collection report](../../lights/README.md), [manifest](manifest.json), and [lighting contract](../../../knowledge/LIGHTS.md).
