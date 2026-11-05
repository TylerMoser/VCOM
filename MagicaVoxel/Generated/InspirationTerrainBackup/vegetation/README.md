# Flowers, bushes and grass

**770 new complete VOX models**: seven treatments for **110 source appearances**. All 25 originals reviewed. Existing bush families are linked and preserved; Pixelwood duplicates retain their first owner.

[Overview](overview.png) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Visual review](visual-review.json) | [Duplicate contents](duplicates.json)

All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.

## Source coverage

| Image | New appearances | New files | Reused families |
| --- | ---: | ---: | ---: |
| [mario.jpg](../mario/vegetation/README.md) | 2 | 14 | 0 |
| [pixelwood_a.jpg](../pixelwood_a/vegetation/README.md) | 3 | 21 | 1 |
| [pixelwood_b.gif](../pixelwood_b/vegetation/README.md) | 0 | 0 | 3 |
| [pixelwood_c.jpg](../pixelwood_c/vegetation/README.md) | 2 | 14 | 4 |
| [poke_a.jpg](../poke_a/vegetation/README.md) | 5 | 35 | 0 |
| [poke_b.png](../poke_b/vegetation/README.md) | 4 | 28 | 0 |
| [poke_c.png](../poke_c/vegetation/README.md) | 5 | 35 | 0 |
| [poke_d.png](../poke_d/vegetation/README.md) | 3 | 21 | 0 |
| [poke_e.png](../poke_e/vegetation/README.md) | 5 | 35 | 0 |
| [poke_f.png](../poke_f/vegetation/README.md) | 3 | 21 | 0 |
| [poke_g.png](../poke_g/vegetation/README.md) | 4 | 28 | 0 |
| [poke_h.png](../poke_h/vegetation/README.md) | 4 | 28 | 1 |
| [poke_i.jpg](../poke_i/vegetation/README.md) | 6 | 42 | 1 |
| [poke_j.jpg](../poke_j/vegetation/README.md) | 3 | 21 | 1 |
| [poke_k.jpg](../poke_k/vegetation/README.md) | 4 | 28 | 1 |
| [poke_l.png](../poke_l/vegetation/README.md) | 2 | 14 | 0 |
| [poke_m.png](../poke_m/vegetation/README.md) | 8 | 56 | 0 |
| [poke_n.png](../poke_n/vegetation/README.md) | 6 | 42 | 1 |
| [poke_o.png](../poke_o/vegetation/README.md) | 5 | 35 | 0 |
| [poke_p.png](../poke_p/vegetation/README.md) | 12 | 84 | 0 |
| [poke_q.png](../poke_q/vegetation/README.md) | 8 | 56 | 0 |
| [poke_r.png](../poke_r/vegetation/README.md) | 3 | 21 | 1 |
| [poke_s.jpg](../poke_s/vegetation/README.md) | 5 | 35 | 3 |
| [poke_t.png](../poke_t/vegetation/README.md) | 4 | 28 | 0 |
| [poke_u.jpg](../poke_u/vegetation/README.md) | 4 | 28 | 0 |

## Comparison sheets

Each family uses a matched camera and lighting across seven treatments; families are framed independently.
- Page 1: [Variations](variations_01.png) | [Cardinal geometry views](geometry_01.png)
- Page 2: [Variations](variations_02.png) | [Cardinal geometry views](geometry_02.png)
- Page 3: [Variations](variations_03.png) | [Cardinal geometry views](geometry_03.png)
- Page 4: [Variations](variations_04.png) | [Cardinal geometry views](geometry_04.png)
- Page 5: [Variations](variations_05.png) | [Cardinal geometry views](geometry_05.png)
- Page 6: [Variations](variations_06.png) | [Cardinal geometry views](geometry_06.png)
- Page 7: [Variations](variations_07.png) | [Cardinal geometry views](geometry_07.png)
- Page 8: [Variations](variations_08.png) | [Cardinal geometry views](geometry_08.png)
- Page 9: [Variations](variations_09.png) | [Cardinal geometry views](geometry_09.png)
- Page 10: [Variations](variations_10.png) | [Cardinal geometry views](geometry_10.png)
- Page 11: [Variations](variations_11.png) | [Cardinal geometry views](geometry_11.png)
- Page 12: [Variations](variations_12.png) | [Cardinal geometry views](geometry_12.png)
- Page 13: [Variations](variations_13.png) | [Cardinal geometry views](geometry_13.png)
- Page 14: [Variations](variations_14.png) | [Cardinal geometry views](geometry_14.png)
- Page 15: [Variations](variations_15.png) | [Cardinal geometry views](geometry_15.png)
- Page 16: [Variations](variations_16.png) | [Cardinal geometry views](geometry_16.png)
- Page 17: [Variations](variations_17.png) | [Cardinal geometry views](geometry_17.png)
- Page 18: [Variations](variations_18.png) | [Cardinal geometry views](geometry_18.png)
- Page 19: [Variations](variations_19.png) | [Cardinal geometry views](geometry_19.png)

## Reproduction

Run from the workspace root:

```powershell
python output/vegetation/generate.py
# Run qa/probe.gd with Godot against qa/game, passing the absolute workspace path after --.
python output/vegetation/validate.py
python output/vegetation/previews.py
python output/vegetation/document.py
```

The isolated QA project contains a snapshot of the current game scripts/addons, with source hashes in `qa/source-provenance.json`. `godot-validation.json` pins every rendered model hash. Original images and all pre-existing top-level delivered VOX files are verified against the preservation baseline.

Inspection is of geometry and rendering, not botanical identification or gameplay behavior. Source projections do not uniquely determine hidden depth or height; recorded sizes are authoring estimates.
