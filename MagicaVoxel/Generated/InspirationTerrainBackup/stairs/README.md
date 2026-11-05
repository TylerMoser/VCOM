# Outdoor stairs

2026-11-03: **26 families / 182 complete VOX files across 16 source images**, each with Base and all six established variations. The 25 inspiration images were visually reviewed; repeated orientations reuse a family. Existing building and sanctuary stairs were not recreated. Files are directly in `output/<image-stem>/`; local `stairs/` folders hold reference crops, previews, manifests and source notes.

[All files](FILES.md) · [Overview](overview.png) · [Source coverage](source-review.json) · [Manifest](manifest.json) · [Structural and geometry checks](validation-summary.json) · [Current importer results](godot-validation.json) · [Visual review](visual-review.json)

## Source interpretation and scale

Includes gray terrace stairs, olive village steps in four sizes, rough rock-cut steps, the complete poke_d cobbled terrace with side stair and parapets, a double stone flight with a middle landing, two lengths of bamboo-edged timber stairs, mossy terrain flights and cave-bank stairs. The source crop, width, tread count, rise and calibration are recorded for every family. Props such as characters, signs, trees and skull posts are excluded.

One tile is **16 voxels**. Native maps use approximately one source pixel per voxel for horizontal measurement. Scaled JPEGs use 9.5 displayed pixels/tile for poke_i (newer buildings), 12.25 for poke_j, 14.72 for poke_k, and about 10 for poke_s. The older poke_k tree record treated a two-tile tree repeat as one tile; this collection corrects that calibration without changing earlier models.

The images mix ground depth and vertical rise. Tread count and width are measured from visible motifs; run, rise, unseen support and landing depth are reconstructed estimates, not exact recoveries. Canvases include curbs and eight voxels of upper landing; they need not have all dimensions divisible by 16. Most repeated short front and side sprites are the same flight rotated; visibly longer flights receive distinct families. poke_t's side views use the shared six-tread motif, with depth inferred. poke_f's cropped northern stairs reuse the tall flight.

## Placement and construction

Stairs climb along **local +X**, with width along Y and MagicaVoxel Z up. Rotate the entire model around Z to match the map. Ground level is z=0. The upper walking surface is at `rise`; its top occupied voxel is `rise-1`. The first tread is above ground by one riser. Align adjacent lower terrain at z=0 and upper terrain at `rise`. Upper landings are included. The double flight has an additional eight-voxel middle landing at half rise.

Stone flights have solid supports intended to be partly embedded in the terrace. Border timbers, masonry curbs and segmented bamboo follow the slope. These low borders are not invented full-height handrails. The poke_d landing is exceptional: its platform occupies x=0..79 at z=32, and the side stair descends toward +X at x=80..111. Its central access strip is y=16..63. The platform's hidden sides, solid foundation and three-sided parapet closure are inferred from the visible cobbled landing and side flight. Do not bury the tread surfaces when positioning terrain.

All outputs have one internal model, explicit palette, rooted scene graph, horizontal centering and translation `0 0 floor(canvas-height/2)`. No cell-by-cell VOX files or brush packages are generated. All materials are diffuse; no glass or lights are present. Index 255 remains unused.

## Variations

- **Base:** source-inspired stone, wood, bamboo and moss colors; restrained tread nosings and riser shading.
- **Cartoon:** broader curbs and shoulders, cleaner paint, deliberate transverse bilateral geometry and paint. Uphill/downhill direction remains distinct.
- **CratePalette:** identical Base geometry, full pinned crate RGBA palette, material-aware mapping.
- **TwoColor:** the amended minimum-flat-color rule: one color per semantic material, no painted shading. All stone and stone curbs merge; timber and stone stay separate; bamboo and wood stay separate; moss stays separate. A wholly stone flight can use one color.
- **Cartoon_TwoColor:** exact Cartoon geometry with those flat material groups.
- **CratePalette_TwoColor:** exact Base geometry with one existing-palette color per group.
- **Cartoon_CratePalette_TwoColor:** exact Cartoon geometry with the same flat existing-palette representatives.

Canonical suffixes and inheritance follow [VARIATIONS.md](../../knowledge/VARIATIONS.md). The pinned RGBA SHA-256 is `b1a4e811c89d143b006c0a421443dd2e1b3b9da0b6588b176c4d072b67c279c2`.

## Validation and integration limits

The saved files are independently checked for bounded coordinates, connected geometry, exact recolor geometry, Cartoon bilateral paint and geometry, one flat color per material, palette preservation and reserved-index avoidance. Centerline checks verify tread count, monotone rise, continuous surfaces, clear central access and level landings. Existing output VOX hashes are checked against a preservation baseline.

The current VCOM importer is copied into an isolated QA project, with source hashes recorded. Every complete model is imported at scale 0.0625 with greedy meshing, SnapToGround false and FirstKeyframeOnly true. Voxel count, grounding and mesh extents are checked. All styles receive previews; Base and Cartoon also receive four cardinal views and underside views.

**No game files or maps are changed.** Current PieceKind uses 16³ pieces and CombatGrid reasons about logical cells, not miniature tread silhouettes. Whole stairs are not drop-in single-cell PieceKinds. Some exceed the 62-voxel loose-model reader width. Stair appearance does not establish traversability: combat placement, climb rules, cover and destruction need a separate integration task. These checks establish file/import integrity and visual authoring, not gameplay behavior.

## Reproduce and preserve

Run `python output/stairs/generate.py`, then `python output/stairs/validate.py`. `setup_qa.py` copies the current importer. Run Godot with the isolated `qa/game` project and `qa/probe.gd`, passing the absolute workspace path after `--`. After successful renders, run `sheets.py` and `document.py`; inspect the sheets before recording a new visual review. The generator refuses to overwrite files whose hashes differ from its prior manifest, protecting hand edits.
