# pixelwood_c.jpg: ground tiles

2 new surface families; 6 transition families. Seven VOX treatments per family.

[Shared terrain contract, orientation and validation](../../ground/README.md)

## Surface families

| Family | Pattern | Reference crop | Top/repeat | VCOM styles |
| --- | --- | --- | --- | --- |
| [PixelwoodC_Ground_River](../PixelwoodC_Ground_River.vox) | calm | [[288, 386, 310, 413]](PixelwoodC_Ground_River_source.png) | [Preview](PixelwoodC_Ground_River_top_and_repeat.png) | [Preview](PixelwoodC_Ground_River_variations.png) |
| [PixelwoodC_Ground_BrokenPavers](../PixelwoodC_Ground_BrokenPavers.vox) | broken | [[596, 481, 654, 538]](PixelwoodC_Ground_BrokenPavers_source.png) | [Preview](PixelwoodC_Ground_BrokenPavers_top_and_repeat.png) | [Preview](PixelwoodC_Ground_BrokenPavers_variations.png) |

## Transition families

| Family | Material A / B | Previews |
| --- | --- | --- |
| [PixelwoodC_Ground_TrailEdge](../PixelwoodC_Ground_TrailEdge.vox) | PixelwoodA_Ground_Meadow / PixelwoodA_Ground_WarmDirt | [Top/repeat](PixelwoodC_Ground_TrailEdge_top_and_repeat.png), [VCOM](PixelwoodC_Ground_TrailEdge_variations.png) |
| [PixelwoodC_Ground_TrailOuterCorner](../PixelwoodC_Ground_TrailOuterCorner.vox) | PixelwoodA_Ground_Meadow / PixelwoodA_Ground_WarmDirt | [Top/repeat](PixelwoodC_Ground_TrailOuterCorner_top_and_repeat.png), [VCOM](PixelwoodC_Ground_TrailOuterCorner_variations.png) |
| [PixelwoodC_Ground_TrailInnerCorner](../PixelwoodC_Ground_TrailInnerCorner.vox) | PixelwoodA_Ground_Meadow / PixelwoodA_Ground_WarmDirt | [Top/repeat](PixelwoodC_Ground_TrailInnerCorner_top_and_repeat.png), [VCOM](PixelwoodC_Ground_TrailInnerCorner_variations.png) |
| [PixelwoodC_Ground_ShoreEdge](../PixelwoodC_Ground_ShoreEdge.vox) | PixelwoodA_Ground_Meadow / PixelwoodC_Ground_River | [Top/repeat](PixelwoodC_Ground_ShoreEdge_top_and_repeat.png), [VCOM](PixelwoodC_Ground_ShoreEdge_variations.png) |
| [PixelwoodC_Ground_ShoreOuterCorner](../PixelwoodC_Ground_ShoreOuterCorner.vox) | PixelwoodA_Ground_Meadow / PixelwoodC_Ground_River | [Top/repeat](PixelwoodC_Ground_ShoreOuterCorner_top_and_repeat.png), [VCOM](PixelwoodC_Ground_ShoreOuterCorner_variations.png) |
| [PixelwoodC_Ground_ShoreInnerCorner](../PixelwoodC_Ground_ShoreInnerCorner.vox) | PixelwoodA_Ground_Meadow / PixelwoodC_Ground_River | [Top/repeat](PixelwoodC_Ground_ShoreInnerCorner_top_and_repeat.png), [VCOM](PixelwoodC_Ground_ShoreInnerCorner_variations.png) |

## Assembled tile layouts

- [PixelwoodC_Ground_Trail: all seven treatments](PixelwoodC_Ground_Trail_assembled.png)
- [PixelwoodC_Ground_Shore: all seven treatments](PixelwoodC_Ground_Shore_assembled.png)

## Reuse from an earlier Pixelwood image

- [PixelwoodA_Ground_Meadow](../../pixelwood_a/ground/PixelwoodA_Ground_Meadow_variations.png): reuse all seven files in `output/pixelwood_a/`; no duplicate exports.
- [PixelwoodA_Ground_WarmDirt](../../pixelwood_a/ground/PixelwoodA_Ground_WarmDirt_variations.png): reuse all seven files in `output/pixelwood_a/`; no duplicate exports.

Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.
