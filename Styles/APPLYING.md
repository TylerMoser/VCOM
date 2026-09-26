# Applying a style

Everything needed to make one of the styles in [VISUAL_VARIANTS.md](VISUAL_VARIANTS.md) permanent, beyond the setting values themselves. Written for whoever picks this up later, most likely Claude in a new session.

**Source of truth:** [`harness/VariantList.gd`](harness/VariantList.gd) holds each style's values, and [`harness/Variants.gd`](harness/Variants.gd) shows exactly how each value was applied at runtime. The catalog is generated from them. Where this guide and the code disagree, the code is what produced the screenshots.

## Before starting

1. **Renderer: Forward+.** Every style was rendered with Forward+ on D3D12, and most rely on it (SSAO, SSIL, SDFGI, DOF, and the normal buffer the outline pass reads). The committed `vcom/project.godot` still says `renderer/rendering_method="gl_compatibility"`. On 2026-09-26 the switch to Forward+ existed only as an uncommitted local edit (delete that line, since Forward+ is the default). Confirm the renderer before applying anything.
2. **Preview the style** with the harness (below) to confirm it still looks like its screenshot on the current code.
3. **Settle the open decisions with the user** (see the end of this file). The biggest one is how block materials get onto the GridMap.

## What each style is made of

| Style | Env / sky / sun | Anti-aliasing | Block material | Units | Outline pass | Colour LUT | Camera |
|---|---|---|---|---|---|---|---|
| 01 Sunlit Diorama | ✓ | MSAA 4× | — | — | — | — | — |
| 04 Soft GI (SDFGI) | ✓ + SDFGI | MSAA 4× | — | — | — | — | — |
| 05 Colour Bounce (SSIL) | ✓ + SSIL | MSAA 4× | — | — | — | — | — |
| 07 Soft Pastel | ✓ | MSAA 4× | shader | — | — | — | — |
| 10 Split-Tone Grade | ✓ | MSAA 4× | — | — | — | 1D | — |
| 11 Tilt-Shift Miniature | ✓ | MSAA 4× | — | — | — | — | DOF |
| 15 Toon Shading | ✓ | MSAA 4× | standard, toon | toon | — | — | — |
| 19 Tactical Readability | ✓ | MSAA 4× | shader | — | — | — | — |
| 21 Ink Outlines | ✓ | SMAA | — | — | ✓ | — | — |
| 22 Cartoon | ✓ | SMAA | standard, toon | toon | ✓ | — | — |
| 23 Bevelled Edge Highlights | ✓ | SMAA | — | — | ✓ | — | — |
| 27 Long-Lens Diorama | ✓ | MSAA 4× | — | — | — | — | FOV |
| 28 Recommended Blend | ✓ | SMAA | shader | — | ✓ | 3D | — |

Each ingredient's recipe follows. Its values are in the style's section of the catalog.

## 1. Environment, sky and sun (every style)

- **Where:** `vcom/Scenes/CombatMap.tscn`: sub-resources `Environment_world` and `ProceduralSkyMaterial_sky`, and the `DirectionalLight3D` node.
- **The test scene too:** `vcom/Scenes/LineOfSightTest.tscn` has its own copies of all three. The harness only rendered `CombatMap`, so ask whether the test scene should match. Recommended: yes.
- **Values:** the catalog uses Godot's own property names. Enums are shown as `Name (int)`, and the `.tscn` stores the int. Properties a style doesn't list stay as they are.
- **Sun direction:** the harness sets `rotation_degrees = Vector3(-elevation, azimuth, 0)`, where azimuth is the direction the light comes *from* (0 = +Z/south, 90 = +X/east). Do not hand-write the resulting `Transform3D` (see CLAUDE.md). Have Godot produce it, e.g. `print(var_to_str(Transform3D(Basis.from_euler(Vector3(deg_to_rad(-elevation), deg_to_rad(azimuth), 0.0)), Vector3(10, 20, -10))))` in a headless script. `Basis.from_euler`'s default YXZ order matches `Node3D.rotation`. Keep the origin at (10, 20, −10); it doesn't affect a directional light, but it keeps the editor gizmo where it was.
- **Sky:** most styles switch `background_mode` to Sky, which makes the ProceduralSkyMaterial visible. The camera looks down, so mostly its *ground* half shows around the map: `ground_bottom_color` is effectively the backdrop colour, and `ground_horizon_color` shows toward the top of the screen.

## 2. Anti-aliasing (every style)

The harness set these on the root viewport at runtime. The permanent equivalents are project settings in `vcom/project.godot` under `[rendering]`:

- MSAA styles: `anti_aliasing/quality/msaa_3d=2` (4×).
- Outline styles (21, 22, 23, 28): leave `msaa_3d` off and set `anti_aliasing/quality/screen_space_aa=2` (SMAA). **MSAA breaks the outline pass:** it resolves averaged normals along edges, and the crease and highlight tests stop firing. FXAA or TAA also work.

Set them in the editor, or with `ProjectSettings.set_setting()` + `ProjectSettings.save()` from a headless script, so the file stays canonical.

## 3. Block materials (07, 15, 19, 22, 28)

The blocks are `vcom/Blocks/*.vox`. The MagicaVoxel addon imports them into meshes that carry their own StandardMaterial3D, built in `Addons/MagicaVoxel_Importer_with_Extensions/MeshGenerators/GreedyMeshGenerator.gd`: vertex colour as albedo, sRGB, roughness 1. `BlockLibrary.tres` points at those imported meshes. Neither MeshLibrary nor GridMap has a material override, so a new material needs a hookup. The harness used option **a**: at startup it called `mesh.surface_set_material()` on every MeshLibrary item mesh (`Variants._apply_blocks`).

Pick one with the user:

- **a. Runtime hookup:** a small script (on the GridMap, or a `BlockMaterials` node beside it) that assigns the materials in `_ready()`. It's the least invasive option and matches the harness exactly. Make it `@tool` so the editor viewport shows the style too.
- **b. Importer option:** add a "material" import option to the addon so imported meshes use the material directly. The editor and game match with no runtime code, but it modifies a third-party addon, and every `.vox` must be re-imported (`--headless --path . --import`).
- Avoid saving baked copies of the meshes with the material swapped in. That breaks the `.vox` → mesh pipeline.

**Shader styles (07, 19, 28):** copy [`harness/shaders/voxel_block.gdshader`](harness/shaders/voxel_block.gdshader) into the project, for example as `vcom/Scripts/Rendering/VoxelBlock.gdshader` (existing shaders sit beside scripts, like `Scripts/Combat/TileHighlight.gdshader`). Set the parameters from the catalog; unset ones default to "off".

- **Crates:** they need their own ShaderMaterial instance when `crate_params` is listed (19 turns grid lines off for them). The crate mesh isn't aligned to the block grid; its MeshLibrary transform is offset 1.3125 in z. The harness matched items whose name contains "crate".
- **Assumptions to revisit if the terrain changes:** 1 m blocks with faces on integer world coordinates; the walkable floor surface at y = 1 (`floor_y`). Contact AO, skirt darkening and `height_gain` all key off `floor_y`, so multi-storey terrain (on the todo list) needs another look at those three.
- **Lighting:** the shader defines its own `light()`, which replaces Godot's diffuse for every light type. Future omni or spot lights will go through its banding and wrap settings too.

**Built-in toon (15, 22):** blocks keep a StandardMaterial3D. Duplicate the importer's material, which keeps `vertex_color_use_as_albedo` and `vertex_color_is_srgb`, then set `diffuse_mode` Toon, `specular_mode` Disabled and `roughness` 0.15, using the same hookup.

## 4. Unit materials (15, 22)

Set these on sub-resources `Mat_player1`–`Mat_player4` and `Mat_enemy1` in `CombatMap.tscn`, plus the copies in `LineOfSightTest.tscn`: `diffuse_mode` 3 (Toon), `specular_mode` 1 (Toon), `roughness` 0.3, `rim_enabled` true, `rim` 0.5, `rim_tint` 0.3. `Unit.color` reads `albedo_color` from these materials, and that doesn't change.

## 5. Outline pass (21, 22, 23, 28)

- Copy [`harness/shaders/outline.gdshader`](harness/shaders/outline.gdshader) into the project, e.g. as `vcom/Scripts/Rendering/Outline.gdshader`.
- Add a `MeshInstance3D` to `CombatMap.tscn` (e.g. `OutlinePass`), mirroring `Variants._add_outline`:
  - `mesh`: a QuadMesh of `size` (2, 2).
  - `material_override`: a ShaderMaterial with the shader and `render_priority` −128.
  - `cast_shadow` Off, `extra_cull_margin` 16384, `ignore_occlusion_culling` true.
  - Position doesn't matter; the vertex shader makes it full-screen.
- **`render_priority` −128 is required.** The pass reads the screen as it was before translucent objects draw, so it must draw first. Otherwise it paints over the translucent TileHighlights.
- It needs Forward+ and a non-MSAA anti-aliasing mode (section 2).
- Uniforms not listed for a style keep the shader defaults. The `debug_masks` uniform paints silhouettes red, convex edges green and concave creases blue, which is how the thresholds were tuned.
- Cost: one full-screen pass of about 12 texture reads per pixel.

## 6. Colour-correction LUT (10, 28)

Both styles set `adjustment_enabled` true and assign `adjustment_color_correction` on the Environment. Godot applies the LUT after tonemapping, in display (sRGB) space.

- **Style 10 (1D):** a `GradientTexture1D` (width 256) whose `Gradient` uses the offsets and colours in the catalog. It can be a scene sub-resource or its own `.tres`. Godot reads it per channel, like curves.
- **Style 28 (3D):** generated by `Variants._make_lut_3d`, a 33³ LUT. Godot samples it without a half-texel offset, so texel *i* holds the output for input (*i* + 0.5)/33. To make it permanent, either:
  - save it as a PNG strip of 33 slices side by side (1089×33) and import it as **Texture3D** (horizontal slices 33, vertical 1, lossless compression, no mipmaps). This is the usual Godot LUT workflow, and the PNG stays editable; or
  - build it at startup with the same function.

  Either way, compare against the screenshot. 8-bit PNG storage differs from the harness's half-float texture only by rounding.

## 7. Depth of field (11)

- The values in the catalog were tuned for the default zoom, with the camera 22 m from its pivot. The close view needed its own values (`camera_b`), because fixed distances only suit one zoom level.
- For real use, `CameraRig.gd` should set the DOF distances from `_current_distance` every frame so the focus follows zoom. Starting ratios from the default view: near = 0.68·d (transition 0.23·d), far = 1.23·d (transition 0.45·d), amount 0.12. Then tune by eye so foreground units stay sharp at close zoom.
- Put the `CameraAttributesPractical` on the rig's `Camera3D` (`attributes`) so the camera owns it. The harness put it on the WorldEnvironment.

## 8. Camera field of view (27)

- `CameraRig/Camera3D`: `fov` 40 (currently 75).
- Scale distance by ×2.11 (tan 37.5° / tan 20°) to keep the framing: CameraRig's `near_distance` 8 → 16.9 and `far_distance` 30 → 63.3, and the Camera3D's authored z position 22 → 46.4. The rig reads its starting zoom from that position.
- Pan speed scales with `_current_distance / far_distance`, so it doesn't change. Check that the sun's `directional_shadow_max_distance` (100) still covers the map from 63 m.

## 9. Global illumination (04, 05)

- **04 (SDFGI):** the `sdfgi_*` properties, a soft PCSS sun (`light_angular_distance` 3) and the studio-grey sky.
  - **Verified:** the GridMap blocks feed SDFGI. In a sun-only render, shadowed faces went pure black with SDFGI off and filled with coloured bounce with it on.
  - The heaviest option here.
  - **Untested:** how SDFGI copes with blocks being destroyed at runtime (destructible terrain is on the todo list). Test that before relying on it.
- **05 (SSIL):** the `ssil_*` properties. It's screen-space, so it only bounces light from what's on screen. It's also cheaper.
- **VoxelGI (not tried):** the search summary saved in [GoogleSearch.png](GoogleSearch.png) recommends it, and it would suit a small bounded map. It needs a `VoxelGI` node over the map bounds, baked in the editor or with `VoxelGI.bake()` at runtime. It's static once baked, so destroyed blocks would need a re-bake. Try it as a new harness style next to 04 before committing to it.

## Previewing and checking with the harness

[`harness/`](harness/) renders any style from the real game, without changing the project:

```bash
Styles/harness/render.sh 21 28        # from the repo root -> Styles/harness/out/NN-name.png
Styles/harness/render.sh 0            # style 0 = the scene exactly as it currently is
```

The script copies the harness into `vcom/_probe/`, runs Godot with a window (`--headless` can't render), and deletes `_probe/` again. Set `GODOT=` if the editor isn't at `C:\Program Files\Godot\Godot_v4.7-stable_win64_console.exe`.

**Verifying an applied style:** render style 0 and compare it with that style's `Styles/NN-*.png`. When this was written, re-rendering unchanged styles produced byte-identical PNGs on the original machine (RTX 3060 Laptop, D3D12, Godot 4.7-stable). A faithful application should therefore match closely; another GPU or driver may differ slightly. Then check that `--headless --path . --quit-after 120` loads with no new errors, and play-test rotating, zooming and panning, since the screenshots cover only two fixed views.

**Tuning or adding a style:** edit `VariantList.gd` for values and `VariantNotes.gd` for the description, cost and kept list, then re-render. To refresh the catalog's per-style sections, run `dump_notes.gd` (usage in its header) and paste its output into `VISUAL_VARIANTS.md`.

**Capture details:**
- 1280×720 per panel, `--fixed-fps 60`.
- Left panel: 150 frames after load.
- Right panel: 90 more frames through a separate Camera3D at pivot (9, 1, −8), yaw 38°, pitch 36°, distance 15. The distance is scaled by the FOV ratio for style 27. The HUD and TileHighlights are hidden and a caption is added.
- The probe turns off the rig's edge-pan and input so a stray cursor can't move the camera.

## Open decisions (ask when applying)

1. The block-material hookup: a runtime `@tool` script or an importer option (section 3).
2. Whether `LineOfSightTest.tscn` should get the same look (recommended: yes).
3. For 11: should the focus follow zoom (section 7), and how much blur is acceptable during play?
4. For 27: is the camera change wanted? It changes how zoom feels, not just the art.
5. Whether to commit the Forward+ renderer switch, if it is still uncommitted.
6. Performance budget, for 04 (SDFGI is heavy) and for MSAA at high resolutions.
