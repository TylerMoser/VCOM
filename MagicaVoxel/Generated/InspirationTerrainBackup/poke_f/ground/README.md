# poke_f.png: ground tiles

3 new surface families; 6 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeF_Ground_DryMeadow](../PokeF_Ground_DryMeadow.vox) | grass | [[408, 297, 420, 309]](PokeF_Ground_DryMeadow_source.png) | [Preview](PokeF_Ground_DryMeadow_top_and_repeat.png) | [Preview](PokeF_Ground_DryMeadow_variations.png) |
| [PokeF_Ground_PaleTrail](../PokeF_Ground_PaleTrail.vox) | dirt | [[218, 33, 241, 66]](PokeF_Ground_PaleTrail_source.png) | [Preview](PokeF_Ground_PaleTrail_top_and_repeat.png) | [Preview](PokeF_Ground_PaleTrail_variations.png) |
| [PokeF_Ground_Pond](../PokeF_Ground_Pond.vox) | ripples | [[174, 404, 198, 426]](PokeF_Ground_Pond_source.png) | [Preview](PokeF_Ground_Pond_top_and_repeat.png) | [Preview](PokeF_Ground_Pond_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeF_Ground_TrailEdge](../PokeF_Ground_TrailEdge.vox) | PokeF_Ground_DryMeadow / PokeF_Ground_PaleTrail | [Top/repeat](PokeF_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeF_Ground_TrailEdge_variations.png) |
| [PokeF_Ground_TrailOuterCorner](../PokeF_Ground_TrailOuterCorner.vox) | PokeF_Ground_DryMeadow / PokeF_Ground_PaleTrail | [Top/repeat](PokeF_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeF_Ground_TrailOuterCorner_variations.png) |
| [PokeF_Ground_TrailInnerCorner](../PokeF_Ground_TrailInnerCorner.vox) | PokeF_Ground_DryMeadow / PokeF_Ground_PaleTrail | [Top/repeat](PokeF_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeF_Ground_TrailInnerCorner_variations.png) |
| [PokeF_Ground_ShoreEdge](../PokeF_Ground_ShoreEdge.vox) | PokeF_Ground_DryMeadow / PokeF_Ground_Pond | [Top/repeat](PokeF_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeF_Ground_ShoreEdge_variations.png) |
| [PokeF_Ground_ShoreOuterCorner](../PokeF_Ground_ShoreOuterCorner.vox) | PokeF_Ground_DryMeadow / PokeF_Ground_Pond | [Top/repeat](PokeF_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeF_Ground_ShoreOuterCorner_variations.png) |
| [PokeF_Ground_ShoreInnerCorner](../PokeF_Ground_ShoreInnerCorner.vox) | PokeF_Ground_DryMeadow / PokeF_Ground_Pond | [Top/repeat](PokeF_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeF_Ground_ShoreInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeF_Ground_Trail: all seven treatments](PokeF_Ground_Trail_assembled.png)
- [PokeF_Ground_Shore: all seven treatments](PokeF_Ground_Shore_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
