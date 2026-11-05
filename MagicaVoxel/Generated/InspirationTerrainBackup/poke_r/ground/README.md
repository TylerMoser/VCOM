# poke_r.png: ground tiles

4 new surface families; 6 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeR_Ground_Meadow](../PokeR_Ground_Meadow.vox) | grass | [[600, 576, 612, 588]](PokeR_Ground_Meadow_source.png) | [Preview](PokeR_Ground_Meadow_top_and_repeat.png) | [Preview](PokeR_Ground_Meadow_variations.png) |
| [PokeR_Ground_PaleTrail](../PokeR_Ground_PaleTrail.vox) | dirt | [[451, 291, 467, 321]](PokeR_Ground_PaleTrail_source.png) | [Preview](PokeR_Ground_PaleTrail_top_and_repeat.png) | [Preview](PokeR_Ground_PaleTrail_variations.png) |
| [PokeR_Ground_GardenSoil](../PokeR_Ground_GardenSoil.vox) | soil | [[407, 353, 419, 369]](PokeR_Ground_GardenSoil_source.png) | [Preview](PokeR_Ground_GardenSoil_top_and_repeat.png) | [Preview](PokeR_Ground_GardenSoil_variations.png) |
| [PokeR_Ground_Pond](../PokeR_Ground_Pond.vox) | ripples | [[475, 603, 501, 625]](PokeR_Ground_Pond_source.png) | [Preview](PokeR_Ground_Pond_top_and_repeat.png) | [Preview](PokeR_Ground_Pond_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeR_Ground_TrailEdge](../PokeR_Ground_TrailEdge.vox) | PokeR_Ground_Meadow / PokeR_Ground_PaleTrail | [Top/repeat](PokeR_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeR_Ground_TrailEdge_variations.png) |
| [PokeR_Ground_TrailOuterCorner](../PokeR_Ground_TrailOuterCorner.vox) | PokeR_Ground_Meadow / PokeR_Ground_PaleTrail | [Top/repeat](PokeR_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeR_Ground_TrailOuterCorner_variations.png) |
| [PokeR_Ground_TrailInnerCorner](../PokeR_Ground_TrailInnerCorner.vox) | PokeR_Ground_Meadow / PokeR_Ground_PaleTrail | [Top/repeat](PokeR_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeR_Ground_TrailInnerCorner_variations.png) |
| [PokeR_Ground_ShoreEdge](../PokeR_Ground_ShoreEdge.vox) | PokeR_Ground_Meadow / PokeR_Ground_Pond | [Top/repeat](PokeR_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeR_Ground_ShoreEdge_variations.png) |
| [PokeR_Ground_ShoreOuterCorner](../PokeR_Ground_ShoreOuterCorner.vox) | PokeR_Ground_Meadow / PokeR_Ground_Pond | [Top/repeat](PokeR_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeR_Ground_ShoreOuterCorner_variations.png) |
| [PokeR_Ground_ShoreInnerCorner](../PokeR_Ground_ShoreInnerCorner.vox) | PokeR_Ground_Meadow / PokeR_Ground_Pond | [Top/repeat](PokeR_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeR_Ground_ShoreInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeR_Ground_Trail: all seven treatments](PokeR_Ground_Trail_assembled.png)
- [PokeR_Ground_Shore: all seven treatments](PokeR_Ground_Shore_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
