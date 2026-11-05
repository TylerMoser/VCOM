# Fences and railings

133 complete VOX files: 19 fence/post appearance families, each with Base and all six established variations. All 25 inspiration images reviewed. Existing delivered models and source images are preserved.

[Overview](overview.png) | [Manifest](manifest.json) | [Source review](source-review.json) | [Validation](validation-summary.json) | [Visual review](visual-review.json)

## Organization and reuse

Final files are directly in `output/<source-image-stem>/`. Each image's `fences/` folder holds source crops, seven-treatment comparisons, cardinal views, repeat previews and local records. This collection folder contains the generator, catalogue, sculpture, validation and isolated Godot QA. No cell-by-cell exports or brushes were generated. Repeated copies of a fence within a source use one family; horizontal/vertical placements are rotations. Source-specific shades and cap profiles remain separate named appearances.

## Scale and placement

One game tile equals 16 voxels. Fence sections use a 40 x 8 canvas horizontally, with a **32-voxel (two-tile) repeat pitch along X**. The extra width accommodates the shared terminal uprights/caps: place the next section 32 voxels along X, not 40. Three-section previews demonstrate the overlap. These are complete reusable two-tile sections, not every arbitrarily long fence run baked into a single asset. The skull shrine/gate post is a separate complete 16 x 12 x 32 model and has no repeat requirement.

Height and upright spacing follow the native pixel-art scale approximately; hidden rear faces and rail thickness are inferred. poke_i is a reduced JPEG with an approximately 9.5-display-pixel tile, restored to the 16-voxel scale. Cartoon uses broader balanced members and deliberate cap shapes. All ordinary Cartoon sections mirror geometry and paint across X and Y. The skull post mirrors X only, retaining its distinct front. Rotations and a shared post can form fence corners, but these deliveries do not include dedicated corner/gate hinge models or an installed map brush. The repeat checks cover straight runs, not gameplay or arbitrary corner combinations.

## Seven treatments

Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Color-only treatments preserve exact occupancy and semantic material masks. The current minimal-material TwoColor rule applies: one flat color for an all-wood, all-metal or stone fence; separate wood and metal colors for a chain fence; separate timber and bone for the skull post. No painted highlights remain in flat styles; renderer lighting still shades surfaces. CratePalette retains the exact pinned crate RGBA bytes. All materials are opaque diffuse, with no emission or glass and no occupied palette index 255.

The rustic poke_p uprights are intentionally separate grounded components, because no connecting rails are visible in the source. Other members must connect to ground through their structure. The skull's real recessed eye/nose openings reveal dark timber backing; these openings and material masks survive recoloring.

## Validation and integration boundary

All 133 files pass binary audit, round-trip checks, bounds/grounding checks, semantic flat-color checks, Cartoon symmetry and palette invariants, and current VCOM standalone VoxelShape/VoxelModel import/render checks in a scratch project copied from the game. The largest axis is 40, below the 62-voxel VoxelModel limit. Base and Cartoon have four-direction previews plus three-section repeat previews (except the standalone skull post). All earlier delivered model hashes are checked against the preservation baseline.

No game files or combat maps were changed. These multi-tile sections are authored assets, not registered PieceKinds. The current level stamp path requires a deliberate integration approach; do not assume loose-model rendering proves terrain placement. Configure decorative fences as solid=false if they should not affect combat. For barriers, cover/climbing are determined by logical piece configuration, not the visible gaps alone.

## Source coverage

| Source | New families | Decision |
| --- | ---: | --- |
| [mario.jpg](../mario/fences/README.md) | 0 | No fence identified; stone columns, signs and background shapes excluded. |
| [pixelwood_a.jpg](../pixelwood_a/fences/README.md) | 0 | No fence identified. Brown horizontal banks are terrain, not palisades. |
| [pixelwood_b.gif](../pixelwood_b/fences/README.md) | 0 | Gray bands are exposed cliff strata, not fences; no fence family generated. |
| [pixelwood_c.jpg](../pixelwood_c/fences/README.md) | 0 | Gray cliff ledges at the natural-log crossing are terrain. The crossing itself is in the deadwood collection. |
| [poke_a.jpg](../poke_a/fences/README.md) | 1 | Timber bridge picket railing. Delivered as a complete repeatable section without the bridge deck. |
| [poke_b.png](../poke_b/fences/README.md) | 2 | Rose-brown rounded pickets and dark square-post iron railings are distinct families. Repeated runs and rotated placements reuse these sections. |
| [poke_c.png](../poke_c/fences/README.md) | 2 | White garden pickets and dark timber bridge guardrails. Building walls, stairs and sign boards are excluded. |
| [poke_d.png](../poke_d/fences/README.md) | 0 | Solid stone bridge parapets and masonry retaining walls, rather than open fences; no fence family generated. |
| [poke_e.png](../poke_e/fences/README.md) | 1 | Pale two-rail garden pickets around flowers; corners and repeated runs use rotations of the section. |
| [poke_f.png](../poke_f/fences/README.md) | 1 | Ochre garden fence with large end posts and a continuous cap rail. Stair stringers are excluded. |
| [poke_g.png](../poke_g/fences/README.md) | 0 | No independent fence identified. Bench backs, stairs and building trim are excluded. |
| [poke_h.png](../poke_h/fences/README.md) | 1 | Warm timber farm pickets, repeated around wheat and along the bridge. One appearance family covers both uses. |
| [poke_i.jpg](../poke_i/fences/README.md) | 2 | Brown split rails around cultivated plots, plus a paler close-picket bridge railing. Resized source: estimated native tile is about 9.5 displayed pixels; restored to 16 voxel scale. |
| [poke_j.jpg](../poke_j/fences/README.md) | 0 | No fence identified; stairs, ledges and house trim are excluded. |
| [poke_k.jpg](../poke_k/fences/README.md) | 0 | No fence identified; stair edges and cliff ledges are excluded. |
| [poke_l.png](../poke_l/fences/README.md) | 1 | Pale arched garden edging/hoop fence shown both in-scene and as isolated tiles. Depth and planted feet inferred. |
| [poke_m.png](../poke_m/fences/README.md) | 0 | No independent fence identified. Bridge deck sides, stair stringers and building edges are excluded. |
| [poke_n.png](../poke_n/fences/README.md) | 1 | Broad cool-white/gray garden pickets around cottages. Repeated corner runs use rotations of one family. |
| [poke_o.png](../poke_o/fences/README.md) | 0 | No fence identified. Benches, signs and living tree boundaries are excluded. |
| [poke_p.png](../poke_p/fences/README.md) | 1 | Short rustic timber uprights bordering bridges. No connecting rails are visible: posts remain separate grounded components in the complete section. |
| [poke_q.png](../poke_q/fences/README.md) | 3 | Green bamboo palisade, capped posts joined by metal chains, and skull-and-crossbones shrine/gate posts. The skull post has a distinct front and is not mirrored front-to-back. |
| [poke_r.png](../poke_r/fences/README.md) | 1 | Pale narrow garden pickets. Color and cap profile retained as a separate source appearance. |
| [poke_s.jpg](../poke_s/fences/README.md) | 1 | Pale formal garden/bridge edging interpreted as a low stone balustrade. Fine supports and hidden faces inferred from the reduced image; solid architecture is excluded. |
| [poke_t.png](../poke_t/fences/README.md) | 1 | Rounded metal bridge handrails, delivered without the deck. Narrow stair sidewalls are excluded. |
| [poke_u.jpg](../poke_u/fences/README.md) | 0 | No fence identified. Green signs and bridge deck edges are excluded. |

## Reproduce

Run `python output/fences/generate.py`; run `qa/probe.gd` through the saved scratch Godot project with the absolute workspace as its user argument; then run `python output/fences/previews.py` and `python output/fences/validate.py`. Inspect the rendered comparisons. The generator refuses to overwrite a file changed since the previous manifest. The render probe caches model hashes: invalidate matching report entries if you change rendering code. `qa/source-provenance.json` pins the copied game sources.
