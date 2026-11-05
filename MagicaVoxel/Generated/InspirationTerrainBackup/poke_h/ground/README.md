# poke_h.png: ground tiles

4 new surface families; 6 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeH_Ground_Meadow](../PokeH_Ground_Meadow.vox) | grass | [[414, 472, 426, 484]](PokeH_Ground_Meadow_source.png) | [Preview](PokeH_Ground_Meadow_top_and_repeat.png) | [Preview](PokeH_Ground_Meadow_variations.png) |
| [PokeH_Ground_FarmDirt](../PokeH_Ground_FarmDirt.vox) | dirt | [[304, 161, 332, 191]](PokeH_Ground_FarmDirt_source.png) | [Preview](PokeH_Ground_FarmDirt_top_and_repeat.png) | [Preview](PokeH_Ground_FarmDirt_variations.png) |
| [PokeH_Ground_Pond](../PokeH_Ground_Pond.vox) | ripples | [[218, 379, 237, 402]](PokeH_Ground_Pond_source.png) | [Preview](PokeH_Ground_Pond_top_and_repeat.png) | [Preview](PokeH_Ground_Pond_variations.png) |
| [PokeH_Ground_BridgeDeck](../PokeH_Ground_BridgeDeck.vox) | planks | [[453, 461, 483, 480]](PokeH_Ground_BridgeDeck_source.png) | [Preview](PokeH_Ground_BridgeDeck_top_and_repeat.png) | [Preview](PokeH_Ground_BridgeDeck_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeH_Ground_TrailEdge](../PokeH_Ground_TrailEdge.vox) | PokeH_Ground_Meadow / PokeH_Ground_FarmDirt | [Top/repeat](PokeH_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeH_Ground_TrailEdge_variations.png) |
| [PokeH_Ground_TrailOuterCorner](../PokeH_Ground_TrailOuterCorner.vox) | PokeH_Ground_Meadow / PokeH_Ground_FarmDirt | [Top/repeat](PokeH_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeH_Ground_TrailOuterCorner_variations.png) |
| [PokeH_Ground_TrailInnerCorner](../PokeH_Ground_TrailInnerCorner.vox) | PokeH_Ground_Meadow / PokeH_Ground_FarmDirt | [Top/repeat](PokeH_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeH_Ground_TrailInnerCorner_variations.png) |
| [PokeH_Ground_ShoreEdge](../PokeH_Ground_ShoreEdge.vox) | PokeH_Ground_Meadow / PokeH_Ground_Pond | [Top/repeat](PokeH_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeH_Ground_ShoreEdge_variations.png) |
| [PokeH_Ground_ShoreOuterCorner](../PokeH_Ground_ShoreOuterCorner.vox) | PokeH_Ground_Meadow / PokeH_Ground_Pond | [Top/repeat](PokeH_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeH_Ground_ShoreOuterCorner_variations.png) |
| [PokeH_Ground_ShoreInnerCorner](../PokeH_Ground_ShoreInnerCorner.vox) | PokeH_Ground_Meadow / PokeH_Ground_Pond | [Top/repeat](PokeH_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeH_Ground_ShoreInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeH_Ground_Trail: all seven treatments](PokeH_Ground_Trail_assembled.png)
- [PokeH_Ground_Shore: all seven treatments](PokeH_Ground_Shore_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
