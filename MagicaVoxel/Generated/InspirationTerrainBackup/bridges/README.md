# Complete bridges

2026-11-03: **17 new families, 119 complete VOX files**, from 11 inspiration images. Each family includes Base and all six established variations. Final files live directly in `output/<source-stem>/`; each image's `bridges/` folder contains its records, reference crops and previews. This folder holds the shared generator and collection QA. No per-cell VOX exports or brush packages are produced.

[Overview](overview.png) · [All models and source notes](FILES.md) · [Source coverage](source-review.json) · [Manifest](manifest.json) · [Validation](validation-summary.json) · [Current importer results](godot-validation.json)

## Coverage and corrections to the old audit

The 25 images were reviewed again using the source overview sheets and full-resolution originals/crops for every bridge candidate. Existing complete crossings are preserved and reused:

- **Pixelwood C:** existing `PixelwoodC_LogBridge`, all seven styles, in the deadwood collection.
- **poke_c covered bridge:** existing `PokeC_BridgePavilion` and `PokeC_BridgeSpan`, all seven styles, with assembly documented in the buildings collection. This batch supplies the separate downstream uncovered bridge.
- **poke_n:** the apparent wooden span is a **roofed gate**, already authored as `PokeN_RoofedGate` in the newer building collection. It has no water beneath it. The old audit and ground tile name `PokeN_Ground_BridgeDeck` predate that identification; no duplicate bridge is created.
- **poke_s:** only the eastern river crossing is a new complete bridge. Pale linear details west of the central plaza are garden walls/edging, already represented by the ruins and fence collections, not additional unsupported river spans.
- **poke_d:** the eastern short arched overpass is included. The lower eastern walled platform with its side stair is a terrain terrace/landing, not another river bridge.
- **poke_p:** two repeated east-west crossings share the six-tile plank-span model; the shorter north-south crossing gets its own five-tile span. The adjacent gray diagonal ramp remains terrain stairs.
- **poke_t:** repeated horizontal crossings and the two end-on views share the eight-tile metal-railed bridge, rotated as needed. Do not create separate files for orientations.

Other images contain terrain steps, ledges, building porches, borders or shorelines, without a missing independent bridge. All per-source decisions and reuse filenames are in `source-review.json` and the local source notes.

## Scale and reconstruction

One tile equals **16 voxels**. Native 16-pixel maps use one source pixel per voxel horizontally, with footprints rounded to tile dimensions. Reduced JPEGs use established/reassessed scale estimates: poke_a about 10.5 displayed pixels per tile, poke_i **9.5** (the later building calibration, superseding the older tree note's 19.3), poke_s about 10. Vertical depth and hidden supports cannot be recovered exactly from these oblique sprites; the source notes identify the interpretation.

The source image **clips poke_h's far bank**. Its approximately 128-pixel visible span is completed to a 160-voxel, ten-tile bridge with a matching far end. This is an explicit reconstruction, not a measured full length. The island bridges' subtle sag, concealed ties and bank anchors, and other unseen undersides are likewise inferred. No unseen railing was added to a source that shows none.

All models run along local **X**, with width along Y and Z up. Rotate a complete model by 90 degrees for a north-south crossing. Source images mix orientation and projection; a rotated use is not an extra family. The manifest records complete canvas size, occupied bounds, deck elevation, source crop, scale, paint and output hashes.

## Complete oversized bridge in one file

`PokeD_FourArchBridge` is **320 × 80 × 96** voxels: a full 20-tile crossing with four arches. Its length exceeds a single VOX model's 256-voxel axis limit. Each treatment is therefore **one VOX scene file with two internal 160 × 80 × 96 architectural halves**, placed by its rooted scene graph at X offsets -80 and +80. The complete span stays at source scale and requires no separate part files. This is not a cell grid or runtime brush.

All other files have one internal model. The explicit rooted graph centers the complete bridge horizontally and grounds its lowest voxels at z=0. Single-model translation is `0 0 floor(height/2)`; oversized halves use that same Z translation plus their X offset. The custom root `_canvas` attribute records the complete authoring canvas; importers can ignore it because the actual scene transforms place every voxel correctly. `voxlib.py` reads and flattens that graph for QA. The repository's structural inspector correctly reports local half-model bounds; use the collection manifest and Godot report for complete scene bounds.

## Construction and placement

- Timber bridges include decks, connected longitudinal beams and bank-end supports. Pickets, closed timber guards, sparse posts and tubular metal rails are differentiated according to the source. The diagonal-board bridge includes its light metal corner plates.
- Stone bridges have genuine open arches through their depth, masonry piers, a continuous deck, and the source-appropriate guards. Arch rise is constrained below the deck so a broad shallow arch cannot accidentally cut through the road.
- Explicit plank gaps are retained in poke_f and poke_u. Supporting beams connect the planks; these gaps are visual geometry, not a claim about combat pathfinding.
- The poke_p bridges include 24 voxels of anchor margin at both ends, enough for all three posts to stand on the bank; their clear wooden spans are 96 and 80 voxels. Low wooden anchoring pads under the sparse posts are intended to be concealed by the banks. Other bridges reach their canvas ends apart from the documented small plank seams.
- `deck` in the manifest is the **end/bank walking-surface elevation**, measured from the asset's lowest support, not its overall height. Place matching terrain tops at that height. The arched timber bridge rises eight voxels in its middle; island spans sag two or three. Recessed bank piles belong below the adjacent terrain surface.
- Each Base preview has a `_banks.png` diagnostic with two simple green terrain blocks aligned to its endpoints. They are placement guides, not exported terrain or a recreated source map. Underside and cardinal views expose the beam, pier, arch and anchoring geometry.

Use MagicaVoxel **Mesh** import, scale **0.0625**, GreedyMeshGenerator enabled, SnapToGround disabled, FirstKeyframeOnly enabled. There is no added glass or lighting; all bridge materials are diffuse, including visually metal rails and fasteners.

## Seven styles

1. **Base:** manually interpreted source timber/masonry/paving/metal/ivy palettes, with restrained board grain, mortar and paving patterns. These are source-inspired RGB choices, not exact recovery of original palettes from JPEGs.
2. **Cartoon:** chunkier supports and coping, simpler broad patterning, regularized deck curvature and exact bilateral geometry/paint across the bridge's longitudinal center plane. The bridge's length, endpoint heights, open arches and functional direction remain intact.
3. **CratePalette:** exact Base occupancy, with the pinned crate RGBA array copied byte-for-byte. Each material maps only to its allowed existing palette ranges. Per-family mappings are saved.
4. **TwoColor:** the user's amended **minimal flat material colors** rule. All timber becomes one color; masonry/coping/paving share one stone color; metal and ivy retain their own groups where present. Pure wood or stone bridges can therefore use one color. No within-group paint variation remains.
5. **Cartoon_TwoColor:** exact Cartoon occupancy with flat semantic colors.
6. **CratePalette_TwoColor:** exact Base occupancy with one pinned-palette representative per semantic group.
7. **Cartoon_CratePalette_TwoColor:** exact Cartoon occupancy using those same flat game-palette representatives.

Palette index 255 is never occupied. The pinned palette hash is `b1a4e811c89d143b006c0a421443dd2e1b3b9da0b6588b176c4d072b67c279c2`.

## Validation, evidence and practical limits

`validate.py` independently reads the saved files and verifies chunk structure, bounded local coordinates, connected geometry, exact color-only geometry inheritance, distinct Cartoon geometry, Cartoon bilateral paint/occupancy, flat semantic groups, reserved-index avoidance, complete deck runs (excluding declared seams), and genuinely open arches. It verifies preservation of **4,970 earlier VOX files**.

`qa/probe.gd` imports every complete file using a copied snapshot of the **current VCOM MagicaVoxel importer**, checks voxel count, grounding and complete mesh dimensions, and renders all styles. For all seven oversized bridge files it checks **every flattened global coordinate and palette index** against independently read expected data, so the internal halves cannot silently overlap or leave a seam. `qa/source-provenance.json` records the source hashes. `godot-validation.json` binds results to each final VOX hash and the render-probe hash. The visual review includes all-style sheets, Base/Cartoon cardinal and underside views, and bank-placement previews.

These are authored complete structures. **No VoxelXCOM game files or combat maps were changed.** The large bridge files are not single 16³ PieceKinds, and most exceed the 62-voxel loose-model renderer limit. Combat terrain integration needs a deliberate multi-tile placement/rules approach; do not shrink the model to force it into one cell. The previews use imported Meshes, not the combat voxel shader. Navigation, cover, destruction, blood, cutaway and live battles were not tested. Decorative nonblocking elements need `solid=false` when configured as such; walkable decks need appropriate support rules.

## Reproduce

```powershell
python output/bridges/generate.py
python output/bridges/validate.py
python output/bridges/setup_qa.py
```

Run Godot 4.7 with `--path output/bridges/qa/game --script <absolute-path-to-qa/probe.gd> -- <absolute-workspace-path>`, then `python output/bridges/sheets.py` and `python output/bridges/document.py`. Review the resulting images before renewing `visual-review.json`. An optional second user argument filters the probe by family substring. Successful renders are cached by model and probe hash, with results saved after every file.

The generator only overwrites its own unchanged prior outputs and refuses to replace hand edits. It never runs generators in VoxelXCOM or rewrites existing bridge assets. Existing source palettes, unknown prior chunks and game assets are preserved by leaving those files untouched.
