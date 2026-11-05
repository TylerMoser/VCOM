# poke_m.png: ground tiles

6 new surface families; 6 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeM_Ground_Meadow](../PokeM_Ground_Meadow.vox) | grass | [[153, 617, 165, 629]](PokeM_Ground_Meadow_source.png) | [Preview](PokeM_Ground_Meadow_top_and_repeat.png) | [Preview](PokeM_Ground_Meadow_variations.png) |
| [PokeM_Ground_PaleTrail](../PokeM_Ground_PaleTrail.vox) | sand | [[649, 389, 674, 414]](PokeM_Ground_PaleTrail_source.png) | [Preview](PokeM_Ground_PaleTrail_top_and_repeat.png) | [Preview](PokeM_Ground_PaleTrail_variations.png) |
| [PokeM_Ground_ShallowWater](../PokeM_Ground_ShallowWater.vox) | dapple | [[297, 265, 317, 284]](PokeM_Ground_ShallowWater_source.png) | [Preview](PokeM_Ground_ShallowWater_top_and_repeat.png) | [Preview](PokeM_Ground_ShallowWater_variations.png) |
| [PokeM_Ground_ChannelWater](../PokeM_Ground_ChannelWater.vox) | waves | [[396, 259, 408, 271]](PokeM_Ground_ChannelWater_source.png) | [Preview](PokeM_Ground_ChannelWater_top_and_repeat.png) | [Preview](PokeM_Ground_ChannelWater_variations.png) |
| [PokeM_Ground_PebbleCourt](../PokeM_Ground_PebbleCourt.vox) | gravel | [[42, 819, 65, 843]](PokeM_Ground_PebbleCourt_source.png) | [Preview](PokeM_Ground_PebbleCourt_top_and_repeat.png) | [Preview](PokeM_Ground_PebbleCourt_variations.png) |
| [PokeM_Ground_Deck](../PokeM_Ground_Deck.vox) | diagonalplanks | [[364, 702, 384, 718]](PokeM_Ground_Deck_source.png) | [Preview](PokeM_Ground_Deck_top_and_repeat.png) | [Preview](PokeM_Ground_Deck_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeM_Ground_TrailEdge](../PokeM_Ground_TrailEdge.vox) | PokeM_Ground_Meadow / PokeM_Ground_PaleTrail | [Top/repeat](PokeM_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeM_Ground_TrailEdge_variations.png) |
| [PokeM_Ground_TrailOuterCorner](../PokeM_Ground_TrailOuterCorner.vox) | PokeM_Ground_Meadow / PokeM_Ground_PaleTrail | [Top/repeat](PokeM_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeM_Ground_TrailOuterCorner_variations.png) |
| [PokeM_Ground_TrailInnerCorner](../PokeM_Ground_TrailInnerCorner.vox) | PokeM_Ground_Meadow / PokeM_Ground_PaleTrail | [Top/repeat](PokeM_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeM_Ground_TrailInnerCorner_variations.png) |
| [PokeM_Ground_ShoreEdge](../PokeM_Ground_ShoreEdge.vox) | PokeM_Ground_Meadow / PokeM_Ground_ShallowWater | [Top/repeat](PokeM_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeM_Ground_ShoreEdge_variations.png) |
| [PokeM_Ground_ShoreOuterCorner](../PokeM_Ground_ShoreOuterCorner.vox) | PokeM_Ground_Meadow / PokeM_Ground_ShallowWater | [Top/repeat](PokeM_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeM_Ground_ShoreOuterCorner_variations.png) |
| [PokeM_Ground_ShoreInnerCorner](../PokeM_Ground_ShoreInnerCorner.vox) | PokeM_Ground_Meadow / PokeM_Ground_ShallowWater | [Top/repeat](PokeM_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeM_Ground_ShoreInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeM_Ground_Trail: all seven treatments](PokeM_Ground_Trail_assembled.png)
- [PokeM_Ground_Shore: all seven treatments](PokeM_Ground_Shore_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
