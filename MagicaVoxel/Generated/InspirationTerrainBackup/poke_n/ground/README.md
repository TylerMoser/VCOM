# poke_n.png: ground tiles

5 new surface families; 6 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeN_Ground_Meadow](../PokeN_Ground_Meadow.vox) | grass | [[200, 126, 212, 138]](PokeN_Ground_Meadow_source.png) | [Preview](PokeN_Ground_Meadow_top_and_repeat.png) | [Preview](PokeN_Ground_Meadow_variations.png) |
| [PokeN_Ground_PaleTrail](../PokeN_Ground_PaleTrail.vox) | sand | [[349, 432, 370, 457]](PokeN_Ground_PaleTrail_source.png) | [Preview](PokeN_Ground_PaleTrail_top_and_repeat.png) | [Preview](PokeN_Ground_PaleTrail_variations.png) |
| [PokeN_Ground_DeepLake](../PokeN_Ground_DeepLake.vox) | dapple | [[28, 685, 45, 704]](PokeN_Ground_DeepLake_source.png) | [Preview](PokeN_Ground_DeepLake_top_and_repeat.png) | [Preview](PokeN_Ground_DeepLake_variations.png) |
| [PokeN_Ground_ShallowLake](../PokeN_Ground_ShallowLake.vox) | dapple | [[115, 649, 133, 666]](PokeN_Ground_ShallowLake_source.png) | [Preview](PokeN_Ground_ShallowLake_top_and_repeat.png) | [Preview](PokeN_Ground_ShallowLake_variations.png) |
| [PokeN_Ground_BridgeDeck](../PokeN_Ground_BridgeDeck.vox) | planks | [[405, 651, 439, 669]](PokeN_Ground_BridgeDeck_source.png) | [Preview](PokeN_Ground_BridgeDeck_top_and_repeat.png) | [Preview](PokeN_Ground_BridgeDeck_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeN_Ground_TrailEdge](../PokeN_Ground_TrailEdge.vox) | PokeN_Ground_Meadow / PokeN_Ground_PaleTrail | [Top/repeat](PokeN_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeN_Ground_TrailEdge_variations.png) |
| [PokeN_Ground_TrailOuterCorner](../PokeN_Ground_TrailOuterCorner.vox) | PokeN_Ground_Meadow / PokeN_Ground_PaleTrail | [Top/repeat](PokeN_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeN_Ground_TrailOuterCorner_variations.png) |
| [PokeN_Ground_TrailInnerCorner](../PokeN_Ground_TrailInnerCorner.vox) | PokeN_Ground_Meadow / PokeN_Ground_PaleTrail | [Top/repeat](PokeN_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeN_Ground_TrailInnerCorner_variations.png) |
| [PokeN_Ground_ShoreEdge](../PokeN_Ground_ShoreEdge.vox) | PokeN_Ground_Meadow / PokeN_Ground_DeepLake | [Top/repeat](PokeN_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeN_Ground_ShoreEdge_variations.png) |
| [PokeN_Ground_ShoreOuterCorner](../PokeN_Ground_ShoreOuterCorner.vox) | PokeN_Ground_Meadow / PokeN_Ground_DeepLake | [Top/repeat](PokeN_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeN_Ground_ShoreOuterCorner_variations.png) |
| [PokeN_Ground_ShoreInnerCorner](../PokeN_Ground_ShoreInnerCorner.vox) | PokeN_Ground_Meadow / PokeN_Ground_DeepLake | [Top/repeat](PokeN_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeN_Ground_ShoreInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeN_Ground_Trail: all seven treatments](PokeN_Ground_Trail_assembled.png)
- [PokeN_Ground_Shore: all seven treatments](PokeN_Ground_Shore_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
