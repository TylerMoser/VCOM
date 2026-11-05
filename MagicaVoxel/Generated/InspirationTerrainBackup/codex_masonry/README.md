# Codex masonry details

Completed 2026-11-04: four families, 28 complete VOX files, all seven established styles. Models live directly in the corresponding source-image folders, with `_Codex_` names. Existing files and other authors' work are preserved. No per-cell files are produced.

The original audit grouped several already-covered objects into this gap. Reuse `PokeD_RoughStoneStairs` (including rock shoulders), `PokeD_StairLanding` (including retaining foundation, coping and side flight), and `PokeD_StoneOverpass` from the stairs/bridges collections, with their six variations. Natural cliff faces between them remain terrain work, not missing masonry. The new straight wall and corner are reusable sections derived from the existing terrace's visual vocabulary, not additional buildings claimed to be visible in the source.

## Placement and styles

One tile = 16 voxels. MagicaVoxel Z-up, grounded at z=0, scene translation `0 0 floor(canvas_height/2)`. Drain faces -Y; position its back inside the riverbank without filling the bore. Its five bars have genuine open gaps. Straight wall spans X, with capped top at z=39 (Cartoon 40); corner returns along +Y. Align matching wall tops; overlap end profiles as needed, without overlapping different styles. Hidden depth and wall repeat lengths are reconstructed.

Pedestal is 32x32x16, calibrated from approximately 48 displayed pixels per tile. The existing chest remains separate: center it on the recessed seat at z=10 (0.625 game units). The Base chest has a verified 22x17 occupied footprint, fitting the 24x24 seat; check other variant footprints before placement. Water and the chest are excluded.

Base follows source hues, stepped bevels and masonry courses. Cartoon regularizes silhouettes: X reflection for wall/drain, diagonal reflection for corner, fourfold rotation for pedestal. Recolors preserve their Base or Cartoon geometry exactly. CratePalette uses the pinned full crate palette, nearest RGB among permitted indices 1..254, with explicit mapping in the manifest. TwoColor and mixtures use one flat stone color, plus one metal color for the drain; mortar and coping merge with stone. Sculpted joints remain visible without painted shading. No glass or emission is used.

## Verification and reproduction

`python output/codex_masonry/generate.py` regenerates only unchanged owned outputs and refuses to overwrite modified or unowned files. `validate.py` rereads serialized files and checks geometry inheritance, palette, material groups, symmetry, bounds, connectivity and drain gaps. `setup_qa.py` copies the current VCOM importer into an isolated scratch project; `qa/probe.gd` checks imported counts, bounds and grounding and renders every variant plus Base/Cartoon cardinal and underside views. `sheets.py` composes the review sheets. See validation-summary.json, godot-validation.json and visual-review.json for final evidence.

Whole-model importer validation does not establish combat integration. The current PieceKind reader is cell-sized and the loose-model path has a 62-voxel limit. Keep requested proportions; do not shrink or split these automatically. No game-project files are changed, and arch gaps do not imply navigation behavior.

[All files](FILES.md) · [Styles](styles_1.png) · [Geometry](geometry_1.png)


| Family | Canvas | Source interpretation |
| --- | --- | --- |
| PokeD_Codex_BarredDrain | 32 x 16 x 32 | Small half-round riverbank outlet. Five recessed bars, open gaps and through bore; hidden depth inferred. Source approximately two tiles wide. |
| PokeD_Codex_RetainingWall | 64 x 16 x 48 | Reusable four-tile straight section extracted from the masonry vocabulary of the lower terrace; inferred repeat length and hidden back. Not a separate new structure in the image. |
| PokeD_Codex_RetainingCorner | 48 x 48 x 48 | L-shaped outside corner matching the terrace masonry and pale coping. Repeatable assembly component; hidden return inferred. |
| PixelwoodC_Codex_ChestPedestal | 32 x 32 x 16 | Square slate plinth under existing treasure chest; bevelled base, inset top and raised border. 48 displayed pixels per tile. Chest excluded; center it above z=10. |
