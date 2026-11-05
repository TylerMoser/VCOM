# poke_p.png: ground tiles

6 new surface families; 6 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeP_Ground_Meadow](../PokeP_Ground_Meadow.vox) | grass | [[746, 274, 758, 286]](PokeP_Ground_Meadow_source.png) | [Preview](PokeP_Ground_Meadow_top_and_repeat.png) | [Preview](PokeP_Ground_Meadow_variations.png) |
| [PokeP_Ground_PaleTrail](../PokeP_Ground_PaleTrail.vox) | sand | [[803, 461, 834, 486]](PokeP_Ground_PaleTrail_source.png) | [Preview](PokeP_Ground_PaleTrail_top_and_repeat.png) | [Preview](PokeP_Ground_PaleTrail_variations.png) |
| [PokeP_Ground_RockyGully](../PokeP_Ground_RockyGully.vox) | gravel | [[277, 145, 311, 178]](PokeP_Ground_RockyGully_source.png) | [Preview](PokeP_Ground_RockyGully_top_and_repeat.png) | [Preview](PokeP_Ground_RockyGully_variations.png) |
| [PokeP_Ground_ShallowPool](../PokeP_Ground_ShallowPool.vox) | dapple | [[332, 381, 348, 404]](PokeP_Ground_ShallowPool_source.png) | [Preview](PokeP_Ground_ShallowPool_top_and_repeat.png) | [Preview](PokeP_Ground_ShallowPool_variations.png) |
| [PokeP_Ground_DeepPool](../PokeP_Ground_DeepPool.vox) | calm | [[229, 1091, 251, 1110]](PokeP_Ground_DeepPool_source.png) | [Preview](PokeP_Ground_DeepPool_top_and_repeat.png) | [Preview](PokeP_Ground_DeepPool_variations.png) |
| [PokeP_Ground_Deck](../PokeP_Ground_Deck.vox) | planks | [[705, 427, 732, 442]](PokeP_Ground_Deck_source.png) | [Preview](PokeP_Ground_Deck_top_and_repeat.png) | [Preview](PokeP_Ground_Deck_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeP_Ground_TrailEdge](../PokeP_Ground_TrailEdge.vox) | PokeP_Ground_Meadow / PokeP_Ground_PaleTrail | [Top/repeat](PokeP_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeP_Ground_TrailEdge_variations.png) |
| [PokeP_Ground_TrailOuterCorner](../PokeP_Ground_TrailOuterCorner.vox) | PokeP_Ground_Meadow / PokeP_Ground_PaleTrail | [Top/repeat](PokeP_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeP_Ground_TrailOuterCorner_variations.png) |
| [PokeP_Ground_TrailInnerCorner](../PokeP_Ground_TrailInnerCorner.vox) | PokeP_Ground_Meadow / PokeP_Ground_PaleTrail | [Top/repeat](PokeP_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeP_Ground_TrailInnerCorner_variations.png) |
| [PokeP_Ground_ShoreEdge](../PokeP_Ground_ShoreEdge.vox) | PokeP_Ground_Meadow / PokeP_Ground_ShallowPool | [Top/repeat](PokeP_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeP_Ground_ShoreEdge_variations.png) |
| [PokeP_Ground_ShoreOuterCorner](../PokeP_Ground_ShoreOuterCorner.vox) | PokeP_Ground_Meadow / PokeP_Ground_ShallowPool | [Top/repeat](PokeP_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeP_Ground_ShoreOuterCorner_variations.png) |
| [PokeP_Ground_ShoreInnerCorner](../PokeP_Ground_ShoreInnerCorner.vox) | PokeP_Ground_Meadow / PokeP_Ground_ShallowPool | [Top/repeat](PokeP_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeP_Ground_ShoreInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeP_Ground_Trail: all seven treatments](PokeP_Ground_Trail_assembled.png)
- [PokeP_Ground_Shore: all seven treatments](PokeP_Ground_Shore_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
