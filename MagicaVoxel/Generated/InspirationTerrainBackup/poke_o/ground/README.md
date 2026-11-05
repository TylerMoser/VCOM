# poke_o.png: ground tiles

6 new surface families; 9 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeO_Ground_Meadow](../PokeO_Ground_Meadow.vox) | grass | [[205, 185, 217, 197]](PokeO_Ground_Meadow_source.png) | [Preview](PokeO_Ground_Meadow_top_and_repeat.png) | [Preview](PokeO_Ground_Meadow_variations.png) |
| [PokeO_Ground_Herringbone](../PokeO_Ground_Herringbone.vox) | herringbone | [[310, 244, 327, 261]](PokeO_Ground_Herringbone_source.png) | [Preview](PokeO_Ground_Herringbone_top_and_repeat.png) | [Preview](PokeO_Ground_Herringbone_variations.png) |
| [PokeO_Ground_BeachSand](../PokeO_Ground_BeachSand.vox) | sand | [[500, 342, 513, 367]](PokeO_Ground_BeachSand_source.png) | [Preview](PokeO_Ground_BeachSand_top_and_repeat.png) | [Preview](PokeO_Ground_BeachSand_variations.png) |
| [PokeO_Ground_Sea](../PokeO_Ground_Sea.vox) | caustic | [[564, 249, 592, 274]](PokeO_Ground_Sea_source.png) | [Preview](PokeO_Ground_Sea_top_and_repeat.png) | [Preview](PokeO_Ground_Sea_variations.png) |
| [PokeO_Ground_DeepSea](../PokeO_Ground_DeepSea.vox) | dapple | [[603, 401, 627, 421]](PokeO_Ground_DeepSea_source.png) | [Preview](PokeO_Ground_DeepSea_top_and_repeat.png) | [Preview](PokeO_Ground_DeepSea_variations.png) |
| [PokeO_Ground_InlandPool](../PokeO_Ground_InlandPool.vox) | dapple | [[473, 619, 489, 633]](PokeO_Ground_InlandPool_source.png) | [Preview](PokeO_Ground_InlandPool_top_and_repeat.png) | [Preview](PokeO_Ground_InlandPool_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeO_Ground_TrailEdge](../PokeO_Ground_TrailEdge.vox) | PokeO_Ground_Meadow / PokeO_Ground_BeachSand | [Top/repeat](PokeO_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeO_Ground_TrailEdge_variations.png) |
| [PokeO_Ground_TrailOuterCorner](../PokeO_Ground_TrailOuterCorner.vox) | PokeO_Ground_Meadow / PokeO_Ground_BeachSand | [Top/repeat](PokeO_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeO_Ground_TrailOuterCorner_variations.png) |
| [PokeO_Ground_TrailInnerCorner](../PokeO_Ground_TrailInnerCorner.vox) | PokeO_Ground_Meadow / PokeO_Ground_BeachSand | [Top/repeat](PokeO_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeO_Ground_TrailInnerCorner_variations.png) |
| [PokeO_Ground_ShoreEdge](../PokeO_Ground_ShoreEdge.vox) | PokeO_Ground_BeachSand / PokeO_Ground_Sea | [Top/repeat](PokeO_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeO_Ground_ShoreEdge_variations.png) |
| [PokeO_Ground_ShoreOuterCorner](../PokeO_Ground_ShoreOuterCorner.vox) | PokeO_Ground_BeachSand / PokeO_Ground_Sea | [Top/repeat](PokeO_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeO_Ground_ShoreOuterCorner_variations.png) |
| [PokeO_Ground_ShoreInnerCorner](../PokeO_Ground_ShoreInnerCorner.vox) | PokeO_Ground_BeachSand / PokeO_Ground_Sea | [Top/repeat](PokeO_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeO_Ground_ShoreInnerCorner_variations.png) |
| [PokeO_Ground_PavingEdge](../PokeO_Ground_PavingEdge.vox) | PokeO_Ground_Meadow / PokeO_Ground_Herringbone | [Top/repeat](PokeO_Ground_PavingEdge_top_and_repeat.png), [VCOM](PokeO_Ground_PavingEdge_variations.png) |
| [PokeO_Ground_PavingOuterCorner](../PokeO_Ground_PavingOuterCorner.vox) | PokeO_Ground_Meadow / PokeO_Ground_Herringbone | [Top/repeat](PokeO_Ground_PavingOuterCorner_top_and_repeat.png), [VCOM](PokeO_Ground_PavingOuterCorner_variations.png) |
| [PokeO_Ground_PavingInnerCorner](../PokeO_Ground_PavingInnerCorner.vox) | PokeO_Ground_Meadow / PokeO_Ground_Herringbone | [Top/repeat](PokeO_Ground_PavingInnerCorner_top_and_repeat.png), [VCOM](PokeO_Ground_PavingInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeO_Ground_Trail: all seven treatments](PokeO_Ground_Trail_assembled.png)
- [PokeO_Ground_Shore: all seven treatments](PokeO_Ground_Shore_assembled.png)
- [PokeO_Ground_Paving: all seven treatments](PokeO_Ground_Paving_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
