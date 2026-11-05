# poke_q.png: ground tiles

5 new surface families; 6 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeQ_Ground_Meadow](../PokeQ_Ground_Meadow.vox) | grass | [[92, 377, 104, 389]](PokeQ_Ground_Meadow_source.png) | [Preview](PokeQ_Ground_Meadow_top_and_repeat.png) | [Preview](PokeQ_Ground_Meadow_variations.png) |
| [PokeQ_Ground_BeachSand](../PokeQ_Ground_BeachSand.vox) | sand | [[474, 558, 486, 570]](PokeQ_Ground_BeachSand_source.png) | [Preview](PokeQ_Ground_BeachSand_top_and_repeat.png) | [Preview](PokeQ_Ground_BeachSand_variations.png) |
| [PokeQ_Ground_CrackedTrail](../PokeQ_Ground_CrackedTrail.vox) | cracked | [[301, 349, 321, 374]](PokeQ_Ground_CrackedTrail_source.png) | [Preview](PokeQ_Ground_CrackedTrail_top_and_repeat.png) | [Preview](PokeQ_Ground_CrackedTrail_variations.png) |
| [PokeQ_Ground_TerraceClay](../PokeQ_Ground_TerraceClay.vox) | cracked | [[312, 211, 340, 233]](PokeQ_Ground_TerraceClay_source.png) | [Preview](PokeQ_Ground_TerraceClay_top_and_repeat.png) | [Preview](PokeQ_Ground_TerraceClay_variations.png) |
| [PokeQ_Ground_Sea](../PokeQ_Ground_Sea.vox) | caustic | [[596, 703, 613, 719]](PokeQ_Ground_Sea_source.png) | [Preview](PokeQ_Ground_Sea_top_and_repeat.png) | [Preview](PokeQ_Ground_Sea_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeQ_Ground_TrailEdge](../PokeQ_Ground_TrailEdge.vox) | PokeQ_Ground_Meadow / PokeQ_Ground_BeachSand | [Top/repeat](PokeQ_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeQ_Ground_TrailEdge_variations.png) |
| [PokeQ_Ground_TrailOuterCorner](../PokeQ_Ground_TrailOuterCorner.vox) | PokeQ_Ground_Meadow / PokeQ_Ground_BeachSand | [Top/repeat](PokeQ_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeQ_Ground_TrailOuterCorner_variations.png) |
| [PokeQ_Ground_TrailInnerCorner](../PokeQ_Ground_TrailInnerCorner.vox) | PokeQ_Ground_Meadow / PokeQ_Ground_BeachSand | [Top/repeat](PokeQ_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeQ_Ground_TrailInnerCorner_variations.png) |
| [PokeQ_Ground_ShoreEdge](../PokeQ_Ground_ShoreEdge.vox) | PokeQ_Ground_BeachSand / PokeQ_Ground_Sea | [Top/repeat](PokeQ_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeQ_Ground_ShoreEdge_variations.png) |
| [PokeQ_Ground_ShoreOuterCorner](../PokeQ_Ground_ShoreOuterCorner.vox) | PokeQ_Ground_BeachSand / PokeQ_Ground_Sea | [Top/repeat](PokeQ_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeQ_Ground_ShoreOuterCorner_variations.png) |
| [PokeQ_Ground_ShoreInnerCorner](../PokeQ_Ground_ShoreInnerCorner.vox) | PokeQ_Ground_BeachSand / PokeQ_Ground_Sea | [Top/repeat](PokeQ_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeQ_Ground_ShoreInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeQ_Ground_Trail: all seven treatments](PokeQ_Ground_Trail_assembled.png)
- [PokeQ_Ground_Shore: all seven treatments](PokeQ_Ground_Shore_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
