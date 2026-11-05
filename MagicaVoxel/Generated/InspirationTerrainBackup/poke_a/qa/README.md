# Complete-model preview harness

Uses the copied VCOM MagicaVoxel importer (license retained). The current scripts read the complete `.vox` files directly from the parent folder. They do not need or generate cell-by-cell files. The copied runtime scripts remain for research, but current previews use imported whole meshes, avoiding the VoxelModel 62-side limit.

Initialize class discovery if needed:

```powershell
& 'C:\Program Files\Godot\Godot_v4.7-stable_win64_console.exe' --headless --path output/poke_a/qa --editor --import --quit
```

Run `preview.gd` for the original tree/sapling or `preview_large.gd` for the large tree, with a graphics device:

```powershell
$qaPath = (Resolve-Path output/poke_a/qa).Path
Start-Process -FilePath 'C:\Program Files\Godot\Godot_v4.7-stable_win64_console.exe' -ArgumentList @('--path', $qaPath, '--script', 'preview_large.gd', '--rendering-method', 'gl_compatibility', '--audio-driver', 'Dummy') -WindowStyle Hidden -Wait -RedirectStandardOutput (Join-Path $qaPath 'whole-render.log') -RedirectStandardError (Join-Path $qaPath 'whole-render-errors.log')
```

Success: `WHOLE_MODEL_QA_PASS` and an empty error log. The scripts verify raw and flattened voxel counts, build imported meshes, write four rotated PNGs, and save complete-model validation JSON beside the source models. No combat behavior is tested.

`historical/` contains older tests performed before the user removed cell pieces. Those records do not define current files or requirements. Do not regenerate deleted pieces to reproduce them.

For the nine style variants and three originals, use `preview_variations.gd` with the same command pattern. Success is `VARIATIONS_QA_PASS`. It writes `variations-godot-validation.json` and per-asset PNGs; compose the comparison with `python output/poke_a/make_variation_sheet.py`.

For combined styles, run `preview_mixtures.gd`; success is `MIXTURES_QA_PASS`. It writes `mixtures-godot-validation.json` and nine renders. Compose the labeled sheet with `python output/poke_a/make_mixture_sheet.py`.
