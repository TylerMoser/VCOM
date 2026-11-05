# poke_b.png: ground tiles

5 new surface families; 9 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeB_Ground_Meadow](../PokeB_Ground_Meadow.vox) | grass | [[279, 701, 291, 713]](PokeB_Ground_Meadow_source.png) | [Preview](PokeB_Ground_Meadow_top_and_repeat.png) | [Preview](PokeB_Ground_Meadow_variations.png) |
| [PokeB_Ground_Herringbone](../PokeB_Ground_Herringbone.vox) | herringbone | [[308, 573, 349, 608]](PokeB_Ground_Herringbone_source.png) | [Preview](PokeB_Ground_Herringbone_top_and_repeat.png) | [Preview](PokeB_Ground_Herringbone_variations.png) |
| [PokeB_Ground_WarmHerringbone](../PokeB_Ground_WarmHerringbone.vox) | herringbone | [[154, 33, 202, 71]](PokeB_Ground_WarmHerringbone_source.png) | [Preview](PokeB_Ground_WarmHerringbone_top_and_repeat.png) | [Preview](PokeB_Ground_WarmHerringbone_variations.png) |
| [PokeB_Ground_Lake](../PokeB_Ground_Lake.vox) | caustic | [[530, 810, 573, 850]](PokeB_Ground_Lake_source.png) | [Preview](PokeB_Ground_Lake_top_and_repeat.png) | [Preview](PokeB_Ground_Lake_variations.png) |
| [PokeB_Ground_GardenSoil](../PokeB_Ground_GardenSoil.vox) | dirt | [[542, 715, 552, 733]](PokeB_Ground_GardenSoil_source.png) | [Preview](PokeB_Ground_GardenSoil_top_and_repeat.png) | [Preview](PokeB_Ground_GardenSoil_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeB_Ground_TrailEdge](../PokeB_Ground_TrailEdge.vox) | PokeB_Ground_Meadow / PokeB_Ground_GardenSoil | [Top/repeat](PokeB_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeB_Ground_TrailEdge_variations.png) |
| [PokeB_Ground_TrailOuterCorner](../PokeB_Ground_TrailOuterCorner.vox) | PokeB_Ground_Meadow / PokeB_Ground_GardenSoil | [Top/repeat](PokeB_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeB_Ground_TrailOuterCorner_variations.png) |
| [PokeB_Ground_TrailInnerCorner](../PokeB_Ground_TrailInnerCorner.vox) | PokeB_Ground_Meadow / PokeB_Ground_GardenSoil | [Top/repeat](PokeB_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeB_Ground_TrailInnerCorner_variations.png) |
| [PokeB_Ground_ShoreEdge](../PokeB_Ground_ShoreEdge.vox) | PokeB_Ground_Meadow / PokeB_Ground_Lake | [Top/repeat](PokeB_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeB_Ground_ShoreEdge_variations.png) |
| [PokeB_Ground_ShoreOuterCorner](../PokeB_Ground_ShoreOuterCorner.vox) | PokeB_Ground_Meadow / PokeB_Ground_Lake | [Top/repeat](PokeB_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeB_Ground_ShoreOuterCorner_variations.png) |
| [PokeB_Ground_ShoreInnerCorner](../PokeB_Ground_ShoreInnerCorner.vox) | PokeB_Ground_Meadow / PokeB_Ground_Lake | [Top/repeat](PokeB_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeB_Ground_ShoreInnerCorner_variations.png) |
| [PokeB_Ground_PavingEdge](../PokeB_Ground_PavingEdge.vox) | PokeB_Ground_Meadow / PokeB_Ground_Herringbone | [Top/repeat](PokeB_Ground_PavingEdge_top_and_repeat.png), [VCOM](PokeB_Ground_PavingEdge_variations.png) |
| [PokeB_Ground_PavingOuterCorner](../PokeB_Ground_PavingOuterCorner.vox) | PokeB_Ground_Meadow / PokeB_Ground_Herringbone | [Top/repeat](PokeB_Ground_PavingOuterCorner_top_and_repeat.png), [VCOM](PokeB_Ground_PavingOuterCorner_variations.png) |
| [PokeB_Ground_PavingInnerCorner](../PokeB_Ground_PavingInnerCorner.vox) | PokeB_Ground_Meadow / PokeB_Ground_Herringbone | [Top/repeat](PokeB_Ground_PavingInnerCorner_top_and_repeat.png), [VCOM](PokeB_Ground_PavingInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeB_Ground_Trail: all seven treatments](PokeB_Ground_Trail_assembled.png)
- [PokeB_Ground_Shore: all seven treatments](PokeB_Ground_Shore_assembled.png)
- [PokeB_Ground_Paving: all seven treatments](PokeB_Ground_Paving_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
