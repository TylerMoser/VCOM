# poke_g.png: ground tiles

4 new surface families; 9 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeG_Ground_Meadow](../PokeG_Ground_Meadow.vox) | grass | [[304, 393, 316, 405]](PokeG_Ground_Meadow_source.png) | [Preview](PokeG_Ground_Meadow_top_and_repeat.png) | [Preview](PokeG_Ground_Meadow_variations.png) |
| [PokeG_Ground_PaleTrail](../PokeG_Ground_PaleTrail.vox) | sand | [[165, 120, 193, 136]](PokeG_Ground_PaleTrail_source.png) | [Preview](PokeG_Ground_PaleTrail_top_and_repeat.png) | [Preview](PokeG_Ground_PaleTrail_variations.png) |
| [PokeG_Ground_RoundedPavers](../PokeG_Ground_RoundedPavers.vox) | cobble | [[423, 204, 450, 237]](PokeG_Ground_RoundedPavers_source.png) | [Preview](PokeG_Ground_RoundedPavers_top_and_repeat.png) | [Preview](PokeG_Ground_RoundedPavers_variations.png) |
| [PokeG_Ground_Pond](../PokeG_Ground_Pond.vox) | ripples | [[77, 60, 98, 80]](PokeG_Ground_Pond_source.png) | [Preview](PokeG_Ground_Pond_top_and_repeat.png) | [Preview](PokeG_Ground_Pond_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeG_Ground_TrailEdge](../PokeG_Ground_TrailEdge.vox) | PokeG_Ground_Meadow / PokeG_Ground_PaleTrail | [Top/repeat](PokeG_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeG_Ground_TrailEdge_variations.png) |
| [PokeG_Ground_TrailOuterCorner](../PokeG_Ground_TrailOuterCorner.vox) | PokeG_Ground_Meadow / PokeG_Ground_PaleTrail | [Top/repeat](PokeG_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeG_Ground_TrailOuterCorner_variations.png) |
| [PokeG_Ground_TrailInnerCorner](../PokeG_Ground_TrailInnerCorner.vox) | PokeG_Ground_Meadow / PokeG_Ground_PaleTrail | [Top/repeat](PokeG_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeG_Ground_TrailInnerCorner_variations.png) |
| [PokeG_Ground_ShoreEdge](../PokeG_Ground_ShoreEdge.vox) | PokeG_Ground_Meadow / PokeG_Ground_Pond | [Top/repeat](PokeG_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeG_Ground_ShoreEdge_variations.png) |
| [PokeG_Ground_ShoreOuterCorner](../PokeG_Ground_ShoreOuterCorner.vox) | PokeG_Ground_Meadow / PokeG_Ground_Pond | [Top/repeat](PokeG_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeG_Ground_ShoreOuterCorner_variations.png) |
| [PokeG_Ground_ShoreInnerCorner](../PokeG_Ground_ShoreInnerCorner.vox) | PokeG_Ground_Meadow / PokeG_Ground_Pond | [Top/repeat](PokeG_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeG_Ground_ShoreInnerCorner_variations.png) |
| [PokeG_Ground_PavingEdge](../PokeG_Ground_PavingEdge.vox) | PokeG_Ground_Meadow / PokeG_Ground_RoundedPavers | [Top/repeat](PokeG_Ground_PavingEdge_top_and_repeat.png), [VCOM](PokeG_Ground_PavingEdge_variations.png) |
| [PokeG_Ground_PavingOuterCorner](../PokeG_Ground_PavingOuterCorner.vox) | PokeG_Ground_Meadow / PokeG_Ground_RoundedPavers | [Top/repeat](PokeG_Ground_PavingOuterCorner_top_and_repeat.png), [VCOM](PokeG_Ground_PavingOuterCorner_variations.png) |
| [PokeG_Ground_PavingInnerCorner](../PokeG_Ground_PavingInnerCorner.vox) | PokeG_Ground_Meadow / PokeG_Ground_RoundedPavers | [Top/repeat](PokeG_Ground_PavingInnerCorner_top_and_repeat.png), [VCOM](PokeG_Ground_PavingInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeG_Ground_Trail: all seven treatments](PokeG_Ground_Trail_assembled.png)
- [PokeG_Ground_Shore: all seven treatments](PokeG_Ground_Shore_assembled.png)
- [PokeG_Ground_Paving: all seven treatments](PokeG_Ground_Paving_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
