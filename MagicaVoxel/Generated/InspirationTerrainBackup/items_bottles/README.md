# Potion bottles — 2026-11-05

45 original complete VOX models delivered directly to `C:/Users/tandm/Documents/Projects/VoxelXCOM/MagicaVoxel/Items/Bottles/`. No image reference. Authoring support stays here; no per-cell exports or gameplay registration.

Each size has one Empty model and seven colors (Red, Blue, Pink, Cyan, Purple, Green, Yellow), each in Translucent and Opaque liquid versions. Names: `PotionBottle_<Size>_Empty.vox` and `PotionBottle_<Size>_<Color>_<Translucent|Opaque>.vox`.

| Size | Canvas and occupied dimensions | Liquid voxels |
| --- | --- | --- |
| Small | 3 × 3 × 5 | 1 |
| Medium | 5 × 5 × 7 | 10 |
| Large | 7 × 7 × 10 | 52 |

Scale was chosen against existing FragGrenade.vox (4 × 4 × 5 occupied, in a 4 × 8 × 6 canvas) and StickGrenade.vox (4 × 4 × 8). Medium allows slightly more width for actual hollow walls. At 0.0625 it measures 0.3125 × 0.3125 × 0.4375 game units. All files use Z up, ground at zero, scene translation `0 0 floor(height/2)`, one model, explicit palette, and no occupied index 255. Horizontal symmetry is exact. Each bottle has a hollow pale glass shell, narrow mouth, brown cork extending into the mouth, and headspace above a flat liquid surface. Empty means no liquid; the stopper remains present.

Palette is deliberately authored for these items: slot 1 pale glass (210,237,242), slot 2 cork (167,112,65), slot 3 the selected liquid. RGB values and deterministic profiles are in generate.py. Shell MATL uses `_type=_glass`, `_trans=.85`, refractive index 1.5. Translucent liquid uses its own `_glass` material, `_trans=.5`, refractive index 1.33. Opaque liquid uses `_diffuse` with no transparency. RGBA alpha stays 255; MATL controls transparency. Filled variants have identical geometry, cork and shell; only liquid color/material changes.

## Validation and previews

- `structural-audit.json`: official workspace inspector, 45 files, zero errors/warnings.
- `validation.json`: saved-file checks for palette/materials, dimensions, symmetry, face connectivity, enclosed liquid, unchanged empty shell, and exact Translucent/Opaque voxel equality.
- `import-validation.json`: all 45 read and rendered with the current VCOM importer copied into isolated `qa/`; exact voxel counts, mesh dimensions and grounding pass. `importer-provenance.json` hashes the copied source. No game source changes and no combat/inventory testing.
- `empty_sizes.png`: sizes at identical camera scale, plus reverse underside views.
- `small_comparison.png`, `medium_comparison.png`, `large_comparison.png`: every filled model under matched lighting; top translucent, bottom opaque. Rendered previews in `previews/`.

**Verified importer limitation:** current GreedyMeshGenerator combines all glass entries into one surface using the most common glass entry's material and suppresses faces between adjacent glass voxels. Thus the shell's .85 transparency also controls the liquid in these imported-mesh previews, and the visible translucent fill is mainly its top surface. The VOX files correctly retain separate .85/.5 materials and complete liquid volumes. These previews do not establish correct multi-material refraction in MagicaVoxel or the game's separate VoxelModel renderer. Fixing the importer/rendering behavior is a separate integration task; game source was preserved.

## Reproduce

Run `python output/items_bottles/generate.py`, then `validate.py` and the workspace inspector. Generator writes only its 45 named files and refuses to overwrite unknown or hand-modified contents. `setup_qa.py` refreshes the isolated importer from VCOM. Import the scratch project using Godot 4.7, then run `qa/probe.gd` with this folder's absolute path as the first user argument. Run `sheets.py` after previews finish. No random seed or external image generation is involved.
