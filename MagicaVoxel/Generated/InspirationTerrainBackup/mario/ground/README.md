# mario.jpg: ground tiles

2 new surface families; 3 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [Mario_Ground_Meadow](../Mario_Ground_Meadow.vox) | grass | [[7, 132, 31, 156]](Mario_Ground_Meadow_source.png) | [Preview](Mario_Ground_Meadow_top_and_repeat.png) | [Preview](Mario_Ground_Meadow_variations.png) |
| [Mario_Ground_PeachDirt](../Mario_Ground_PeachDirt.vox) | dirt | [[610, 238, 650, 260]](Mario_Ground_PeachDirt_source.png) | [Preview](Mario_Ground_PeachDirt_top_and_repeat.png) | [Preview](Mario_Ground_PeachDirt_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [Mario_Ground_TrailEdge](../Mario_Ground_TrailEdge.vox) | Mario_Ground_Meadow / Mario_Ground_PeachDirt | [Top/repeat](Mario_Ground_TrailEdge_top_and_repeat.png), [VCOM](Mario_Ground_TrailEdge_variations.png) |
| [Mario_Ground_TrailOuterCorner](../Mario_Ground_TrailOuterCorner.vox) | Mario_Ground_Meadow / Mario_Ground_PeachDirt | [Top/repeat](Mario_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](Mario_Ground_TrailOuterCorner_variations.png) |
| [Mario_Ground_TrailInnerCorner](../Mario_Ground_TrailInnerCorner.vox) | Mario_Ground_Meadow / Mario_Ground_PeachDirt | [Top/repeat](Mario_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](Mario_Ground_TrailInnerCorner_variations.png) |

## Assembled tile layouts

- [Mario_Ground_Trail: all seven treatments](Mario_Ground_Trail_assembled.png)

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
