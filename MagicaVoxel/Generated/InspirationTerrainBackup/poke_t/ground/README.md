# poke_t.png: ground tiles

6 new surface families; 3 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeT_Ground_CaveSand](../PokeT_Ground_CaveSand.vox) | sand | [[383, 510, 404, 525]](PokeT_Ground_CaveSand_source.png) | [Preview](PokeT_Ground_CaveSand_top_and_repeat.png) | [Preview](PokeT_Ground_CaveSand_variations.png) |
| [PokeT_Ground_DampCaveFloor](../PokeT_Ground_DampCaveFloor.vox) | mud | [[285, 747, 310, 771]](PokeT_Ground_DampCaveFloor_source.png) | [Preview](PokeT_Ground_DampCaveFloor_top_and_repeat.png) | [Preview](PokeT_Ground_DampCaveFloor_variations.png) |
| [PokeT_Ground_CaveRock](../PokeT_Ground_CaveRock.vox) | rock | [[276, 895, 298, 914]](PokeT_Ground_CaveRock_source.png) | [Preview](PokeT_Ground_CaveRock_top_and_repeat.png) | [Preview](PokeT_Ground_CaveRock_variations.png) |
| [PokeT_Ground_ShallowPool](../PokeT_Ground_ShallowPool.vox) | dapple | [[629, 368, 653, 391]](PokeT_Ground_ShallowPool_source.png) | [Preview](PokeT_Ground_ShallowPool_top_and_repeat.png) | [Preview](PokeT_Ground_ShallowPool_variations.png) |
| [PokeT_Ground_DeepPool](../PokeT_Ground_DeepPool.vox) | dapple | [[574, 189, 599, 211]](PokeT_Ground_DeepPool_source.png) | [Preview](PokeT_Ground_DeepPool_top_and_repeat.png) | [Preview](PokeT_Ground_DeepPool_variations.png) |
| [PokeT_Ground_BridgeDeck](../PokeT_Ground_BridgeDeck.vox) | planks | [[765, 333, 789, 361]](PokeT_Ground_BridgeDeck_source.png) | [Preview](PokeT_Ground_BridgeDeck_top_and_repeat.png) | [Preview](PokeT_Ground_BridgeDeck_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeT_Ground_ShoreEdge](../PokeT_Ground_ShoreEdge.vox) | PokeT_Ground_CaveSand / PokeT_Ground_ShallowPool | [Top/repeat](PokeT_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeT_Ground_ShoreEdge_variations.png) |
| [PokeT_Ground_ShoreOuterCorner](../PokeT_Ground_ShoreOuterCorner.vox) | PokeT_Ground_CaveSand / PokeT_Ground_ShallowPool | [Top/repeat](PokeT_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeT_Ground_ShoreOuterCorner_variations.png) |
| [PokeT_Ground_ShoreInnerCorner](../PokeT_Ground_ShoreInnerCorner.vox) | PokeT_Ground_CaveSand / PokeT_Ground_ShallowPool | [Top/repeat](PokeT_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeT_Ground_ShoreInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeT_Ground_Shore: all seven treatments](PokeT_Ground_Shore_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
