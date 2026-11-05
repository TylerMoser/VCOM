# Codex waterfalls and cave entrances

**19 waterfall families and three cave entrances: 154 complete VOX files**, each with Base and all six established variations. Created as Codex's own interpretations while another author may be working on similar subjects. Every model name contains `_Codex_`; all VOX files remain directly in their source image's output folder. Supporting material uses `codex_waterfalls_caves/` folders. No existing model is replaced.

[All files](FILES.md) · [Overview](overview.png) · [Source decisions](source-review.json) · [Manifest](manifest.json) · [Validation](validation-summary.json) · [Current importer results](godot-validation.json) · [Visual review](visual-review.json)

## Coverage and reference fidelity

This fills the waterfall and cave-mouth entries in the previous remaining-assets audit. The nine affected source images were reopened and inspected at full resolution, with enlarged candidate crops. The source review retains all 25 original image hashes and distinguishes reinspection from prior audit context.

Waterfalls include Pixelwood C's broad curtain; poke_a's short terrace falls; both sizes of poke_c cascades; three green-water drops in poke_d; poke_m's repeated foamy spillway; nine bounded/island forms in poke_s; and the two narrow blue ribbons in poke_u. All have a lip, continuous descending water geometry and a foam/impact termination. Free island falls have a small attached mist toe, not an invented rock basin. Repeated forms and orientations reuse the appropriate family.

Caves cover poke_p's pointed gully mouth, poke_t's small eastern opening, and its larger southern recess. Each has a faceted rock surround, roof, a floor and an **actual air passage through its depth**. No black plane pretends to be a hole. Tiny western dark marks are shadows/rock details, not additional caves. The black void beyond the southern opening is background and is not voxel geometry.

One tile equals 16 voxels. Native maps use approximately one source pixel per voxel; Pixelwood C uses about 48 displayed pixels/tile, poke_a 10.5, and poke_s 10. Widths and relative lengths follow the visible features. Projection mixes depth and height, so drop, hidden tunnel depth, splash depth and unseen endings are documented estimates. Clipped/occluded poke_u ribbons and poke_d's inlet are explicit reconstructions. The models omit surrounding terrain networks, trees, characters and existing props.

## Placement

All files are MagicaVoxel Z-up, horizontally centered, grounded at z=0, with a rooted scene graph and translation `0 0 floor(canvas-height/2)`. One complete single model is saved per file; no cell exports or brush packages.

Waterfalls face **-Y** and span X. Incoming water is behind the lip at larger Y. The receiving water surface is near z=4; the lip is near `drop+4`. For stepped cascades, each tier advances eight voxels toward +Y as it rises. Their final lip and inlet occupy the back of the model. Only the narrow water sheet and its short water tabs are included: adjacent cliff geometry must be placed behind/alongside it. Do not bury the visible curtain in terrain. Free-fall mist is a stylized static termination rather than a fluid simulation.

Caves open toward **-Y**, with the tunnel continuing to +Y. Align adjoining terrain with the rocky sides and roof; leave the passage clear. Their floor surface is z=2, so place the model accordingly if a level floor is required. The rear opening is deliberately left open for connection to future cave geometry. The mouth dimensions are nominal; the arch reduces clear height toward its sides. Independent checks verify at least a 16-voxel-wide, 22-voxel-high center passage through every depth slice.

## Seven variations and materials

- **Base:** source-inspired blue/green water with streaks, bright crest/impact foam, or earth-colored cave rock with coherent facets and a recessed floor. Colors are interpreted from compressed references rather than claimed exact original palettes.
- **Cartoon:** thicker, more regular water ribbons/lips and rounded foam lobes; simpler, broader cave facets and stronger feet. Geometry and paint have exact left/right symmetry across X. Flow direction, lip height and open passages remain distinct and intact.
- **CratePalette:** identical Base occupancy with the pinned crate RGBA palette copied byte-for-byte. Water uses its existing blue/teal entries, foam its pale entries, rock/floor its earth ranges.
- **TwoColor:** the amended minimum-flat-color rule. Following the ground collection, **all water and pale foam merge to one water color**; their sculpted relief remains. Cave rock and earthy floor each retain one flat color. No shading/noise inside a semantic group.
- **Cartoon_TwoColor:** exact Cartoon geometry and the same flat source-color groups.
- **CratePalette_TwoColor:** exact Base geometry, one game-palette color per semantic group.
- **Cartoon_CratePalette_TwoColor:** exact Cartoon geometry with those same game-palette representatives.

Water is static opaque diffuse voxel art, consistent with the ground collection. No glass, emission, fluid behavior or animation is implied. All cave materials are also diffuse. Index 255 is reserved and unused. Palette SHA-256: `b1a4e811c89d143b006c0a421443dd2e1b3b9da0b6588b176c4d072b67c279c2`.

## Checks and game use

The on-disk validator checks structure, coordinate bounds, connectedness, exact geometry inheritance for recolors, Cartoon symmetry, flat semantic groups, reserved-index avoidance, continuous water sheets across their full drops, and real cave air corridors/floors. Source and output hashes are persisted. A baseline tracks prior VOX files; concurrent changes by another author are reported without restoring or overwriting them.

An isolated Godot project copies the current VCOM MagicaVoxel importer and records source hashes. Every final file is imported as a Mesh at scale 0.0625, with greedy meshing, SnapToGround false and FirstKeyframeOnly true. Voxel counts, grounding and bounds are checked. Previews cover every style, plus Base/Cartoon cardinal and underside views.

These models have **not** been placed in a live combat map. Whole-model imports do not test navigation, swimming, cover, destruction or cave transitions. Current single-cell PieceKind expects 16³ models, and the loose VoxelModel reader has a 62-voxel width limit; many authored pieces are larger. Configure water as decoration/nonblocking where appropriate; cave rock needs deliberate terrain/rules integration. No files in VoxelXCOM are changed by this batch.

## Reproduction and concurrent work

`generate.py` writes only its own listed `_Codex_` output files and refuses modified/unowned files. `validate.py` checks saved files. `setup_qa.py` refreshes the isolated importer. Run Godot with `qa/game` and `qa/probe.gd`, passing the absolute workspace path after `--`; then run `sheets.py` and `document.py`. Inspect the images before refreshing `visual-review.json`.

Preserve other authors' versions, even when they depict the same reference. Local image records here and the separate `knowledge/CODEX_WATERFALLS_CAVES.md` prevent concurrent work from replacing shared collection notes. The shared backlog may be updated with a short link after completion.
