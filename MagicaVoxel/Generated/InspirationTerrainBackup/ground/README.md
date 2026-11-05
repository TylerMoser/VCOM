# Ground texture collection

Reviewed all 25 inspiration images. This collection contains **101 surface families and 147 transition families, 248 families / 1,736 complete VOX files**, with Base and all six established variations. Final files live directly in `output/<image-stem>/`. Supporting source crops, unlit top/repeat previews and VCOM previews live in that image folder's `ground/` directory. These are intentionally authored terrain tiles, not fragments cut from larger models.

## Using the tiles

- Each canvas is **16 x 16 x 16**, one game cell across, Z-up, translation `0 0 8`. Land reaches z=15, except one-voxel recessed paving joints, cracks and plank grooves. Water fills z=0..13, leaving its surface two voxels below the top of adjoining land. Blocks are filled and connected, with a complete bottom plane.
- Import as MagicaVoxel Mesh, scale **0.0625**, GreedyMeshGenerator=true, SnapToGround=false, FirstKeyframeOnly=true. Standard PieceKind translation is `(0,-0.5,0)`. Repeat at 16 voxels / one game unit. These are whole intended ground blocks; no extra cell exports or brush packages are needed.
- Flat floor tops preserve the source-like proportions and the tile interface. Grass and dirt silhouettes are intentionally identical across styles. Cartoon changes their drawn motifs into broader balanced patches; it changes paving, furrow and crack geometry only where the surface remains usable. This terrain-specific exception avoids sculpting unwanted bumps into a floor solely to distinguish a style.
- Top/repeat previews show exact stored paint, without lighting; Godot previews show lit surfaces and real grooves. A flat-color tile can still have visible cracks or lighting on its geometry.
- Water is **static opaque diffuse voxel art**, not glass, an animated shader, a fluid, or a swimming rule. Pale wave colors are the same water material and merge in TwoColor. Land support generally needs solid=true; decorative water and mixed shores need an explicit gameplay decision when registered. Do not apply the props' solid=false default indiscriminately to floors. VCOM rules work at cell scale, not at the painted shoreline inside a mixed tile.
- No game assets, PieceLibrary, maps or gameplay rules were changed. The isolated current-VCOM QA imports, reads every tile through both the mesh and 16-cubed block readers, checks voxel counts, and renders every treatment. This is not combat-map placement or movement testing.

## Transitions and orientation

`Trail`, `Shore`, and `Paving` families combine named surface families in the manifest. They are construction helpers inferred from visible boundaries, not claims of 147 additional distinct source textures. The source image's particular road width is assembled from repeated tiles; it is not baked into a giant road model.

The unrotated **Edge** has material A at x<8 and B at x>=8. **OuterCorner** has A in the x<8,y<8 quarter; **InnerCorner** has A everywhere except the x>=8,y>=8 quarter. Rotate by quarter-turns as needed. Natural straight edges have a small one-voxel irregularity, returning to x=8 at both ends; Cartoon edges are clean. Endpoints and corner interfaces align. The same A/B surface motifs and palette mappings are used in the cores and edges. Paving borders have a flush two-column curb band; no raised sidewalk obstruction is added. Corners use clean square topology; a complete automatic 47-tile blob/road-junction system is outside this collection.

The 3x3 repetition views of transition tiles deliberately repeat that *same* mixed tile, making bands or a checkerboard. They are seam diagnostics, not the intended layout of a whole shoreline. Arrange cores and rotated edge/corner cases to build a continuous shape.

## Source interpretation and materials

Source swatches establish colors and recognizable motifs; this is **reconstructed voxel terrain, not a pixel-perfect extrusion**. Clean grass swatches were selected using proximity to a visually chosen source color. Material hue filters exclude nearby characters, flowers, foliage and shadows. Four-tone quantization limits JPEG noise. The generator records the resulting representative RGB per surface in the manifest. A few tiny or partly covered soil/rock swatches use explicit visually matched representatives; see `palette_source()`.

Herringbone/parquet, irregular cobbles, large flagstones, pale brick, broken mossy pavers, wood grain, cultivated furrows, sparse grass, coarse grass, grit, cracks, cave floor, sand, caustics, shallow-water patches and river ripples have separate deterministic motifs. Underground fill, layer depth and invisible cross-sections are inferred. Terrain from the same material but genuinely different source colors keeps a separate appearance family. Lighting shadows alone are not separate textures.

TwoColor follows the user's **2026-10-28 amendment**, minimizing flat material colors. Single-material earth, sand, rock, wood and water can use one paint color. Grass over earth keeps two; stone/mortar and moss remain meaningful groups. Paving curbs merge with paving in flat variants. Recolors preserve exact occupancy. CratePalette copies the pinned 1,024 RGBA bytes unchanged and restricts mappings to suitable palette ranges; no occupied palette index 255. No Glass or Emit materials are used.

Exclusions: roofs and walls; entire bridges/buildings; loose stones, flowers, reeds, wheat, bushes and props already in other collections; characters, objects reflected or drawn in water; vertical waterfall effects; black cave voids; white spritesheet backgrounds; clouds/sky around poke_s and poke_u. Pixelwood B's gray horizontal bands are slate ledge/cliff faces, **not roads**: SlateLedge is a reusable rock-material interpretation. CliffRock/TerraceEarth tiles likewise adapt exposed geological material to a ground block, rather than replicating a whole cliff. The Pixelwood C log bridge is already a deadwood model; its gray broken pavers are included here.

## Reproduction and evidence

Run from the workspace root:

```powershell
python output/ground/generate.py
python output/ground/validate.py --binary
# Run qa/probe.gd through Godot in qa/game, with the absolute workspace path as its user argument.
python output/ground/previews.py
python output/ground/validate.py
python output/ground/document.py
```

`generate.py` refuses to overwrite an unrecognized or manually changed VOX file. `preservation-baseline.json` pins previously delivered models. `manifest.json` records each output hash, canvas, counts and flat material groups. `source-inventory.json`, `source-review.json`, `structural-audit.json`, `godot-validation.json`, `validation-summary.json` and `visual-review.json` record the actual checks. `qa/source-provenance.json` pins copied game source; the scratch copy lives under this collection, never in VoxelXCOM. `surface_styles_*.png` and `transition_styles_*.png` compare all seven styles in repeated grids; `runtime_overview_*.png` show actual VCOM block renders.

## Browse by source

- [mario.jpg](../mario/ground/README.md): 5 families / 35 files.
- [pixelwood_a.jpg](../pixelwood_a/ground/README.md): 5 families / 35 files.
- [pixelwood_b.gif](../pixelwood_b/ground/README.md): 1 families / 7 files; Pixelwood meadow/dirt reuse.
- [pixelwood_c.jpg](../pixelwood_c/ground/README.md): 8 families / 56 files; Pixelwood meadow/dirt reuse.
- [poke_a.jpg](../poke_a/ground/README.md): 10 families / 70 files.
- [poke_b.png](../poke_b/ground/README.md): 14 families / 98 files.
- [poke_c.png](../poke_c/ground/README.md): 13 families / 91 files.
- [poke_d.png](../poke_d/ground/README.md): 11 families / 77 files.
- [poke_e.png](../poke_e/ground/README.md): 13 families / 91 files.
- [poke_f.png](../poke_f/ground/README.md): 9 families / 63 files.
- [poke_g.png](../poke_g/ground/README.md): 13 families / 91 files.
- [poke_h.png](../poke_h/ground/README.md): 10 families / 70 files.
- [poke_i.jpg](../poke_i/ground/README.md): 11 families / 77 files.
- [poke_j.jpg](../poke_j/ground/README.md): 9 families / 63 files.
- [poke_k.jpg](../poke_k/ground/README.md): 9 families / 63 files.
- [poke_l.png](../poke_l/ground/README.md): 2 families / 14 files.
- [poke_m.png](../poke_m/ground/README.md): 12 families / 84 files.
- [poke_n.png](../poke_n/ground/README.md): 11 families / 77 files.
- [poke_o.png](../poke_o/ground/README.md): 15 families / 105 files.
- [poke_p.png](../poke_p/ground/README.md): 12 families / 84 files.
- [poke_q.png](../poke_q/ground/README.md): 11 families / 77 files.
- [poke_r.png](../poke_r/ground/README.md): 10 families / 70 files.
- [poke_s.jpg](../poke_s/ground/README.md): 14 families / 98 files.
- [poke_t.png](../poke_t/ground/README.md): 9 families / 63 files.
- [poke_u.jpg](../poke_u/ground/README.md): 11 families / 77 files.

## Collection preview sheets

Surface styles and repeats: [1](surface_styles_01.png), [2](surface_styles_02.png), [3](surface_styles_03.png), [4](surface_styles_04.png), [5](surface_styles_05.png), [6](surface_styles_06.png), [7](surface_styles_07.png), [8](surface_styles_08.png), [9](surface_styles_09.png).

Transition styles and repeats: [1](transition_styles_01.png), [2](transition_styles_02.png), [3](transition_styles_03.png), [4](transition_styles_04.png), [5](transition_styles_05.png), [6](transition_styles_06.png), [7](transition_styles_07.png), [8](transition_styles_08.png), [9](transition_styles_09.png), [10](transition_styles_10.png), [11](transition_styles_11.png), [12](transition_styles_12.png), [13](transition_styles_13.png).

VCOM rendered blocks: [1](runtime_overview_01.png), [2](runtime_overview_02.png), [3](runtime_overview_03.png), [4](runtime_overview_04.png), [5](runtime_overview_05.png), [6](runtime_overview_06.png).

Completed 2026-10-30. Final visual review and validation records are stored alongside this document.
