# poke_d.png: ground tiles

5 new surface families; 6 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PokeD_Ground_OchreFloor](../PokeD_Ground_OchreFloor.vox) | dirt | [[663, 572, 675, 584]](PokeD_Ground_OchreFloor_source.png) | [Preview](PokeD_Ground_OchreFloor_top_and_repeat.png) | [Preview](PokeD_Ground_OchreFloor_variations.png) |
| [PokeD_Ground_PaleTrail](../PokeD_Ground_PaleTrail.vox) | sand | [[560, 502, 586, 528]](PokeD_Ground_PaleTrail_source.png) | [Preview](PokeD_Ground_PaleTrail_top_and_repeat.png) | [Preview](PokeD_Ground_PaleTrail_variations.png) |
| [PokeD_Ground_Cobblestone](../PokeD_Ground_Cobblestone.vox) | cobble | [[280, 246, 316, 277]](PokeD_Ground_Cobblestone_source.png) | [Preview](PokeD_Ground_Cobblestone_top_and_repeat.png) | [Preview](PokeD_Ground_Cobblestone_variations.png) |
| [PokeD_Ground_River](../PokeD_Ground_River.vox) | ripples | [[348, 115, 385, 152]](PokeD_Ground_River_source.png) | [Preview](PokeD_Ground_River_top_and_repeat.png) | [Preview](PokeD_Ground_River_variations.png) |
| [PokeD_Ground_GrayRock](../PokeD_Ground_GrayRock.vox) | rock | [[227, 412, 241, 432]](PokeD_Ground_GrayRock_source.png) | [Preview](PokeD_Ground_GrayRock_top_and_repeat.png) | [Preview](PokeD_Ground_GrayRock_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PokeD_Ground_TrailEdge](../PokeD_Ground_TrailEdge.vox) | PokeD_Ground_OchreFloor / PokeD_Ground_PaleTrail | [Top/repeat](PokeD_Ground_TrailEdge_top_and_repeat.png), [VCOM](PokeD_Ground_TrailEdge_variations.png) |
| [PokeD_Ground_TrailOuterCorner](../PokeD_Ground_TrailOuterCorner.vox) | PokeD_Ground_OchreFloor / PokeD_Ground_PaleTrail | [Top/repeat](PokeD_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PokeD_Ground_TrailOuterCorner_variations.png) |
| [PokeD_Ground_TrailInnerCorner](../PokeD_Ground_TrailInnerCorner.vox) | PokeD_Ground_OchreFloor / PokeD_Ground_PaleTrail | [Top/repeat](PokeD_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PokeD_Ground_TrailInnerCorner_variations.png) |
| [PokeD_Ground_ShoreEdge](../PokeD_Ground_ShoreEdge.vox) | PokeD_Ground_OchreFloor / PokeD_Ground_River | [Top/repeat](PokeD_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PokeD_Ground_ShoreEdge_variations.png) |
| [PokeD_Ground_ShoreOuterCorner](../PokeD_Ground_ShoreOuterCorner.vox) | PokeD_Ground_OchreFloor / PokeD_Ground_River | [Top/repeat](PokeD_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PokeD_Ground_ShoreOuterCorner_variations.png) |
| [PokeD_Ground_ShoreInnerCorner](../PokeD_Ground_ShoreInnerCorner.vox) | PokeD_Ground_OchreFloor / PokeD_Ground_River | [Top/repeat](PokeD_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PokeD_Ground_ShoreInnerCorner_variations.png) |

## Assembled tile layouts

- [PokeD_Ground_Trail: all seven treatments](PokeD_Ground_Trail_assembled.png)
- [PokeD_Ground_Shore: all seven treatments](PokeD_Ground_Shore_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
