# poke_e.png: ground tiles

4 new surface families; 9 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeE_Ground_Meadow](../PokeE_Ground_Meadow.vox) | grass | [[126, 247, 138, 259]](PokeE_Ground_Meadow_source.png) | [Preview](PokeE_Ground_Meadow_top_and_repeat.png) | [Preview](PokeE_Ground_Meadow_variations.png) |
| [PokeE_Ground_PaleTrail](../PokeE_Ground_PaleTrail.vox) | sand | [[210, 257, 229, 280]](PokeE_Ground_PaleTrail_source.png) | [Preview](PokeE_Ground_PaleTrail_top_and_repeat.png) | [Preview](PokeE_Ground_PaleTrail_variations.png) |
| [PokeE_Ground_Herringbone](../PokeE_Ground_Herringbone.vox) | herringbone | [[194, 8, 226, 35]](PokeE_Ground_Herringbone_source.png) | [Preview](PokeE_Ground_Herringbone_top_and_repeat.png) | [Preview](PokeE_Ground_Herringbone_variations.png) |
| [PokeE_Ground_Lake](../PokeE_Ground_Lake.vox) | caustic | [[125, 112, 158, 146]](PokeE_Ground_Lake_source.png) | [Preview](PokeE_Ground_Lake_top_and_repeat.png) | [Preview](PokeE_Ground_Lake_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeE_Ground_TrailEdge](../PokeE_Ground_TrailEdge.vox) | PokeE_Ground_Meadow / PokeE_Ground_PaleTrail | [Top/repeat](PokeE_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeE_Ground_TrailEdge_variations.png) |
| [PokeE_Ground_TrailOuterCorner](../PokeE_Ground_TrailOuterCorner.vox) | PokeE_Ground_Meadow / PokeE_Ground_PaleTrail | [Top/repeat](PokeE_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeE_Ground_TrailOuterCorner_variations.png) |
| [PokeE_Ground_TrailInnerCorner](../PokeE_Ground_TrailInnerCorner.vox) | PokeE_Ground_Meadow / PokeE_Ground_PaleTrail | [Top/repeat](PokeE_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeE_Ground_TrailInnerCorner_variations.png) |
| [PokeE_Ground_ShoreEdge](../PokeE_Ground_ShoreEdge.vox) | PokeE_Ground_Meadow / PokeE_Ground_Lake | [Top/repeat](PokeE_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeE_Ground_ShoreEdge_variations.png) |
| [PokeE_Ground_ShoreOuterCorner](../PokeE_Ground_ShoreOuterCorner.vox) | PokeE_Ground_Meadow / PokeE_Ground_Lake | [Top/repeat](PokeE_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeE_Ground_ShoreOuterCorner_variations.png) |
| [PokeE_Ground_ShoreInnerCorner](../PokeE_Ground_ShoreInnerCorner.vox) | PokeE_Ground_Meadow / PokeE_Ground_Lake | [Top/repeat](PokeE_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeE_Ground_ShoreInnerCorner_variations.png) |
| [PokeE_Ground_PavingEdge](../PokeE_Ground_PavingEdge.vox) | PokeE_Ground_Meadow / PokeE_Ground_Herringbone | [Top/repeat](PokeE_Ground_PavingEdge_top_and_repeat.png), [VCOM](PokeE_Ground_PavingEdge_variations.png) |
| [PokeE_Ground_PavingOuterCorner](../PokeE_Ground_PavingOuterCorner.vox) | PokeE_Ground_Meadow / PokeE_Ground_Herringbone | [Top/repeat](PokeE_Ground_PavingOuterCorner_top_and_repeat.png), [VCOM](PokeE_Ground_PavingOuterCorner_variations.png) |
| [PokeE_Ground_PavingInnerCorner](../PokeE_Ground_PavingInnerCorner.vox) | PokeE_Ground_Meadow / PokeE_Ground_Herringbone | [Top/repeat](PokeE_Ground_PavingInnerCorner_top_and_repeat.png), [VCOM](PokeE_Ground_PavingInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeE_Ground_Trail: all seven treatments](PokeE_Ground_Trail_assembled.png)
- [PokeE_Ground_Shore: all seven treatments](PokeE_Ground_Shore_assembled.png)
- [PokeE_Ground_Paving: all seven treatments](PokeE_Ground_Paving_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
