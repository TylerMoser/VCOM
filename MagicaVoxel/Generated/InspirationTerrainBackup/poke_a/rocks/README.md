# Rocks from poke_a.jpg

Discrete rocks modeled; repeated placements within image represented once. Buildings, continuous cliff walls, water foam, loose items, creatures and shells are excluded.

## PokeA_PointedRiverRock

Single pointed stream rock; source resized, approximately one tile wide.

Canvas: 16 × 14 × 18 voxels. Source conversion estimate: 1 voxels per displayed pixel. Depth and physical height inferred from sprite perspective. Actual occupied bounds are in the manifest.

[Source crop](PokeA_PointedRiverRock_source.png) · [Seven variations](PokeA_PointedRiverRock_variations.png) · [Four-direction geometry](PokeA_PointedRiverRock_geometry.png)

| Style | VOX | Voxels | Used colors |
| --- | --- | --- | --- |
| Base | [PokeA_PointedRiverRock.vox](../PokeA_PointedRiverRock.vox) | 1250 | 4 |
| Cartoon | [PokeA_PointedRiverRock_Cartoon.vox](../PokeA_PointedRiverRock_Cartoon.vox) | 1368 | 3 |
| CratePalette | [PokeA_PointedRiverRock_CratePalette.vox](../PokeA_PointedRiverRock_CratePalette.vox) | 1250 | 2 |
| TwoColor | [PokeA_PointedRiverRock_TwoColor.vox](../PokeA_PointedRiverRock_TwoColor.vox) | 1250 | 1 |
| Cartoon_TwoColor | [PokeA_PointedRiverRock_Cartoon_TwoColor.vox](../PokeA_PointedRiverRock_Cartoon_TwoColor.vox) | 1368 | 1 |
| CratePalette_TwoColor | [PokeA_PointedRiverRock_CratePalette_TwoColor.vox](../PokeA_PointedRiverRock_CratePalette_TwoColor.vox) | 1250 | 1 |
| Cartoon_CratePalette_TwoColor | [PokeA_PointedRiverRock_Cartoon_CratePalette_TwoColor.vox](../PokeA_PointedRiverRock_Cartoon_CratePalette_TwoColor.vox) | 1368 | 1 |

Whole models, Z-up, translation `0 0 floor(canvas height/2)`, Mesh scale .0625, grounded and opaque diffuse. Minimal-color variants use one flat color for plain stone, two for moss/stone or crystal/stone. No water planes, foam, emission or automatic gameplay behavior.

[Collection evidence and reproduction](../../rocks/README.md) · [Authoring knowledge](../../../knowledge/ROCKS.md)
