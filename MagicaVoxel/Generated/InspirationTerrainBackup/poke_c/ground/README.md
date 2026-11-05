# poke_c.png: ground tiles

4 new surface families; 9 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeC_Ground_Meadow](../PokeC_Ground_Meadow.vox) | grass | [[752, 532, 764, 544]](PokeC_Ground_Meadow_source.png) | [Preview](PokeC_Ground_Meadow_top_and_repeat.png) | [Preview](PokeC_Ground_Meadow_variations.png) |
| [PokeC_Ground_Flagstone](../PokeC_Ground_Flagstone.vox) | flagstone | [[623, 482, 643, 512]](PokeC_Ground_Flagstone_source.png) | [Preview](PokeC_Ground_Flagstone_top_and_repeat.png) | [Preview](PokeC_Ground_Flagstone_variations.png) |
| [PokeC_Ground_Sand](../PokeC_Ground_Sand.vox) | sand | [[627, 39, 647, 57]](PokeC_Ground_Sand_source.png) | [Preview](PokeC_Ground_Sand_top_and_repeat.png) | [Preview](PokeC_Ground_Sand_variations.png) |
| [PokeC_Ground_River](../PokeC_Ground_River.vox) | ripples | [[353, 263, 378, 281]](PokeC_Ground_River_source.png) | [Preview](PokeC_Ground_River_top_and_repeat.png) | [Preview](PokeC_Ground_River_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeC_Ground_TrailEdge](../PokeC_Ground_TrailEdge.vox) | PokeC_Ground_Meadow / PokeC_Ground_Sand | [Top/repeat](PokeC_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeC_Ground_TrailEdge_variations.png) |
| [PokeC_Ground_TrailOuterCorner](../PokeC_Ground_TrailOuterCorner.vox) | PokeC_Ground_Meadow / PokeC_Ground_Sand | [Top/repeat](PokeC_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeC_Ground_TrailOuterCorner_variations.png) |
| [PokeC_Ground_TrailInnerCorner](../PokeC_Ground_TrailInnerCorner.vox) | PokeC_Ground_Meadow / PokeC_Ground_Sand | [Top/repeat](PokeC_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeC_Ground_TrailInnerCorner_variations.png) |
| [PokeC_Ground_ShoreEdge](../PokeC_Ground_ShoreEdge.vox) | PokeC_Ground_Meadow / PokeC_Ground_River | [Top/repeat](PokeC_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeC_Ground_ShoreEdge_variations.png) |
| [PokeC_Ground_ShoreOuterCorner](../PokeC_Ground_ShoreOuterCorner.vox) | PokeC_Ground_Meadow / PokeC_Ground_River | [Top/repeat](PokeC_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeC_Ground_ShoreOuterCorner_variations.png) |
| [PokeC_Ground_ShoreInnerCorner](../PokeC_Ground_ShoreInnerCorner.vox) | PokeC_Ground_Meadow / PokeC_Ground_River | [Top/repeat](PokeC_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeC_Ground_ShoreInnerCorner_variations.png) |
| [PokeC_Ground_PavingEdge](../PokeC_Ground_PavingEdge.vox) | PokeC_Ground_Meadow / PokeC_Ground_Flagstone | [Top/repeat](PokeC_Ground_PavingEdge_top_and_repeat.png), [VCOM](PokeC_Ground_PavingEdge_variations.png) |
| [PokeC_Ground_PavingOuterCorner](../PokeC_Ground_PavingOuterCorner.vox) | PokeC_Ground_Meadow / PokeC_Ground_Flagstone | [Top/repeat](PokeC_Ground_PavingOuterCorner_top_and_repeat.png), [VCOM](PokeC_Ground_PavingOuterCorner_variations.png) |
| [PokeC_Ground_PavingInnerCorner](../PokeC_Ground_PavingInnerCorner.vox) | PokeC_Ground_Meadow / PokeC_Ground_Flagstone | [Top/repeat](PokeC_Ground_PavingInnerCorner_top_and_repeat.png), [VCOM](PokeC_Ground_PavingInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeC_Ground_Trail: all seven treatments](PokeC_Ground_Trail_assembled.png)
- [PokeC_Ground_Shore: all seven treatments](PokeC_Ground_Shore_assembled.png)
- [PokeC_Ground_Paving: all seven treatments](PokeC_Ground_Paving_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
