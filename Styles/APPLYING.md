# Applying a style

Everything needed to make one of the styles in [VISUAL_VARIANTS.md](VISUAL_VARIANTS.md) permanent, beyond the setting values themselves. Written for whoever picks this up later, most likely Claude in a new session.

**Source of truth:** [`harness/VariantList.gd`](harness/VariantList.gd) holds each style's values, and [`harness/Variants.gd`](harness/Variants.gd) shows exactly how each value was applied at runtime. The catalog is generated from them. Where this guide and the code disagree, the code is what produced the screenshots.

**Written 2026-09-26, updated 2026-10-01.** The screenshots and the catalog date from 2026-09-26. Since then:

- the units have become rigged voxel figures;
- the camera's default distance has gone from 22 to 15;
- `BoundaryMap.tscn` has become the map every encounter is fought on;
- terrain now breaks and wears away.

The sections below cover all of that. To undo an applied style, see [REVERT.md](REVERT.md), which records the original look value by value.

**Style 05 has been applied (2026-10-01).** Every style is a set of changes on top of whatever the scene currently is, so from now on:

- `render.sh 0` shows 05.
- Any other style is previewed *on top of 05*. Whatever 05 turned on and that style leaves alone carries into its preview, for example SSIL, which no other style sets.
- To preview or apply another style as the catalog defines it, revert first (REVERT.md), or have the style turn off what it doesn't use.

## Before starting

1. **Renderer: Forward+.** Every style was rendered with Forward+ on D3D12, and most rely on it (SSAO, SSIL, SDFGI, DOF, and the normal buffer the outline pass reads).
   - The switch was committed in `655a976` on 2026-09-26. `vcom/project.godot` has no `renderer/rendering_method` line, so the default, Forward+, is in use.
   - Its `config/features` still says `"GL Compatibility"`. That's a stale tag; it doesn't affect rendering.
   - Confirm the renderer hasn't changed before applying anything.
2. **Preview the style** with the harness (below) on the current code.
   - The screenshots predate the figures and the current camera, so judge the terrain and the light rather than expecting a match.
   - The harness no longer previews the toon styles' units (section 4).
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

- **Where:** every combat map has its own copies of the sub-resources `Environment_world` and `ProceduralSkyMaterial_sky`, and of the `DirectionalLight3D` node:
  - `vcom/Scenes/BoundaryMap.tscn` is the map every encounter is fought on, so it must get the style. Its backdrop is sky blue (`background_color` (0.53, 0.8, 0.97)) where the other two are dark navy. Preview it with `MAP=res://Scenes/BoundaryMap.tscn Styles/harness/render.sh N`.
  - `vcom/Scenes/CombatMap.tscn` is what the harness renders by default, and what the screenshots show.
  - `vcom/Scenes/LineOfSightTest.tscn` is the rules test scene. Ask whether it should match. Recommended: yes.
- **Values:** the catalog uses Godot's own property names. Enums are shown as `Name (int)`, and the `.tscn` stores the int. Properties a style doesn't list stay as they are.
- **Sun direction:** the harness sets `rotation_degrees = Vector3(-elevation, azimuth, 0)`, where azimuth is the direction the light comes *from* (0 = +Z/south, 90 = +X/east). Do not hand-write the resulting `Transform3D` (see CLAUDE.md). Have Godot produce it, e.g. `print(var_to_str(Transform3D(Basis.from_euler(Vector3(deg_to_rad(-elevation), deg_to_rad(azimuth), 0.0)), Vector3(10, 20, -10))))` in a headless script. `Basis.from_euler`'s default YXZ order matches `Node3D.rotation`. Keep the origin at (10, 20, −10); it doesn't affect a directional light, but it keeps the editor gizmo where it was.
- **Sky:** most styles switch `background_mode` to Sky, which makes the ProceduralSkyMaterial visible. The camera looks down, so mostly its *ground* half shows around the map: `ground_bottom_color` is effectively the backdrop colour, and `ground_horizon_color` shows toward the top of the screen.
  - On BoundaryMap, the forest ring is deep enough that no backdrop shows in play (CLAUDE.md, "Scenery around a combat map"). There, the sky matters only through the ambient light. The harness's close view does show it, because that view looks lower than the game camera can.
  - Every map already lights from the sky (`ambient_light_source` Sky), even where the backdrop is a flat colour. Recolouring the sky therefore changes the ambient light everywhere.

## 2. Anti-aliasing (every style)

The harness set these on the root viewport at runtime. The permanent equivalents are project settings in `vcom/project.godot` under `[rendering]`:

- MSAA styles: `anti_aliasing/quality/msaa_3d=2` (4×).
- Outline styles (21, 22, 23, 28): leave `msaa_3d` off and set `anti_aliasing/quality/screen_space_aa=2` (SMAA). **MSAA breaks the outline pass:** it resolves averaged normals along edges, and the crease and highlight tests stop firing. FXAA or TAA also work.

Set them in the editor, or with `ProjectSettings.set_setting()` + `ProjectSettings.save()` from a headless script, so the file stays canonical.

## 3. Block materials (07, 15, 19, 22, 28)

The blocks are `vcom/Blocks/*.vox`. The MagicaVoxel addon imports them into meshes that carry their own StandardMaterial3D, built in `vcom/addons/MagicaVoxel_Importer_with_Extensions/MeshGenerators/GreedyMeshGenerator.gd`: vertex colour as albedo, sRGB, roughness 1.

Two libraries point at those imported meshes, and they are the same mesh resources, so a material set on a mesh reaches both:

- `BlockLibrary.tres`, the battlefield;
- `SceneryLibrary.tres`, BoundaryMap's forest ring: the same blocks with shadows off.

Neither MeshLibrary nor GridMap has a material override, so a new material needs a hookup. The harness used option **a**: once the map was ready, it called `mesh.surface_set_material()` on every MeshLibrary item mesh (`Variants._apply_blocks`).

**The grass already has a hookup: the tile grid (since 2026-10-01).** `TileGrid`, a node in each combat map, puts `vcom/Scripts/Combat/TileGrid.gdshader` on the `BrightGrass1` mesh as the map loads, before `TerrainDestruction`. It's the player's optional grid lines, style 19's grid alone, toggled with `G` or on the System tab, and with the grid off it draws exactly as the importer's material. So a style that changes the grass must keep the grid working:

- For the grass, **build on `TileGrid.gdshader`** (add the style's effect to it), and `TileGrid` stays the hookup.
- **Or** give the style's own shader the grid's code: the `global uniform float tile_grid` and the line block in its `fragment()`. Then have `TileGrid` assign that shader instead.
- Keep `render_mode diffuse_burley, specular_schlick_ggx` wherever the standard lighting is meant to stay. Godot 4.7's defaults light a shader differently from `StandardMaterial3D`.
- `voxel_block.gdshader` has a grid of its own (`edge_darken`), which would double up with the player's. Drop it, or drive it from `tile_grid`.
- Other blocks (crates, trees) still have no hookup.

Pick one with the user:

- **a. Runtime hookup:** a small script that assigns the materials in `_ready()`. It's the least invasive option and matches the harness. Make it `@tool` so the editor viewport shows the style too.
  - Put it **on the `GridMap` node, or on a node before `TerrainDestruction` in the tree**, so it runs first. A node's children and its earlier siblings are ready before it.
  - **Why the order matters:** `TerrainDestruction`'s `_ready` has `VoxelShape.read()` copy each wearable block's surface material, and every `WornBlock` is drawn with that copy. A hookup that runs later, as the harness's does, leaves worn blocks in the old look the first time they're hit. The screenshots don't show this, because nothing breaks in them.
- **b. Importer option:** add a "material" import option to the addon so imported meshes use the material directly. The editor and game match with no runtime code, but it modifies a third-party addon, and every `.vox` must be re-imported (`--headless --path . --import`).
- Avoid saving baked copies of the meshes with the material swapped in. That breaks the `.vox` → mesh pipeline.

**Breakable terrain draws blocks in more places than the GridMap.** Terrain didn't break when the styles were rendered. Now each of these needs the style as well:

- **Worn blocks** (grass, trees) take their material from the block's mesh, read when the map loads. The hookup's position covers them (option **a** above). With option **b** they're covered anyway.
- **Falling blocks** draw the library's own mesh, so they follow the hookup with no extra work.
- **Broken crates.**
  - When a crate breaks, it's swapped for `Scenes/Destruct_BrightCrate1.tscn`. That scene's meshes come from importing `Blocks/Destruct_BrightCrate1.vox` as a scene, so they're separate meshes carrying the importer's material, and the MeshLibrary hookup doesn't reach them.
  - Set their material as well. One way is through the pieces scene's mesh resources, once, before any crate breaks (`ScriptedDestruction.prepare()` runs as the map loads).
  - Set it on the mesh (`surface_set_material`), not as a node's `material_override`. When a piece starts wearing, `VoxelBody` redraws it with its mesh's surface material (`VoxelTerrain._model_of()`), so an override would vanish at the first hit.
- **Debris.** `VoxelDebris` draws every voxel broken off with a material of its own: vertex colour, sRGB, roughness 1, set where it builds `_cube`. It needs the style too.
  - For the shader styles, turn grid lines off on it, as `crate_params` does for crates. Its cubes are 6 cm across, not 1 m.
- **Not blocks:** props (rifle, sword, grenade) and coins keep the importer's material. Ask whether they should match (they're small on screen).

**Shader styles (07, 19, 28):** copy [`harness/shaders/voxel_block.gdshader`](harness/shaders/voxel_block.gdshader) into the project, for example as `vcom/Scripts/Rendering/VoxelBlock.gdshader` (existing shaders sit beside scripts, like `Scripts/Combat/TileHighlight.gdshader`). Set the parameters from the catalog; unset ones default to "off".

- **Crates:** they need their own ShaderMaterial instance when `crate_params` is listed (19 turns grid lines off for them). The crate mesh isn't aligned to the block grid; its MeshLibrary transform is offset 1.3125 in z. The harness matched items whose name contains "crate".
- **Assumptions to revisit:**
  - The shader assumes 1 m blocks with faces on integer world coordinates, and the walkable floor surface at y = 1 (`floor_y`). Contact AO, skirt darkening and `height_gain` all key off `floor_y`.
  - The terrain has already moved past the first assumption. Worn blocks and craters have faces every 1/16 m inside a cell, and a crater digs up to 4 voxels into the bottom layer, below `floor_y`.
  - Before settling the values, look at grid lines, contact AO and skirt darkening on a worn tree and on a grenade crater.
  - Multi-storey terrain (on the todo list) would need another look at the three `floor_y` effects as well.
- **Lighting:** the shader defines its own `light()`, which replaces Godot's diffuse for every light type. Future omni or spot lights will go through its banding and wrap settings too.

**Built-in toon (15, 22):** blocks keep a StandardMaterial3D. Duplicate the importer's material, which keeps `vertex_color_use_as_albedo` and `vertex_color_is_srgb`, then set `diffuse_mode` Toon, `specular_mode` Disabled and `roughness` 0.15, using the same hookup. The same goes for the crate pieces and the debris above.

## 4. Unit materials (15, 22)

The units are no longer capsules. Each wears the rigged figure `Scenes/BaseCharacter.tscn`, painted one flat colour through its `CharacterModel.body_material`, a plain StandardMaterial3D.

Set the toon values on these materials:

- **Values:** `diffuse_mode` 3 (Toon), `specular_mode` 1 (Toon), `roughness` 0.3, `rim_enabled` true, `rim` 0.5, `rim_tint` 0.3.
- **`Mat_unit` in `vcom/Scenes/SquadUnit.tscn`**, which every squad member starts from. `Unit._paint()` hands the character's colour to `CharacterModel.paint()`, which duplicates the material and sets only `albedo_color`, so the toon settings carry to every member.
- **`Mat_enemy1`** in `BoundaryMap.tscn`, `CombatMap.tscn` and `LineOfSightTest.tscn`. Its albedo is slate grey, `Color(0.32, 0.35, 0.4)`, so blood shows on the enemies; leave it, and keep any style's unit colours off red for the same reason.
- **`Mat_player1`–`Mat_player8`** in `LineOfSightTest.tscn`, if it is to match.

Blood is drawn with a material of its own, `VoxelStains.material` in `Scripts/Terrain/VoxelStains.gd`, on every stain overlay and every drop in flight. A style that changes how units or blocks are shaded does not reach it: give it the same treatment there (toon diffuse, say) if blood should match, and check its stains, which sit 2 mm off the faces they cover, under any outline pass.

`Unit.color` reads `albedo_color` back through `CharacterModel.tint()`, and that doesn't change. Don't edit `BaseCharacter.tscn` or the figure's own vertex-colour material (`VoxelRig`): every unit covers it with `body_material`, and the scene is regenerated by `BakeCharacter.gd`.

**The harness no longer previews this.** `Variants._apply_units` looks for each unit's `Mesh` child, which the figures don't have, so it changes nothing. Rendering 15 or 22 today shows the figures in their usual shading, and the screenshots for 15 and 22 show the old capsules. To preview the toon units, `_apply_units` would have to set the toon values on each `Units/*/Model`'s `body_material`, a duplicate per unit.

## 5. Outline pass (21, 22, 23, 28)

- Copy [`harness/shaders/outline.gdshader`](harness/shaders/outline.gdshader) into the project, e.g. as `vcom/Scripts/Rendering/Outline.gdshader`.
- Add a `MeshInstance3D` (e.g. `OutlinePass`) to each map that gets the style: `BoundaryMap.tscn` above all, `CombatMap.tscn`, and `LineOfSightTest.tscn` if it is to match. Mirror `Variants._add_outline`:
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

- The values in the catalog were tuned for what was then the default zoom, with the camera 22 m from its pivot. The close view needed its own values (`camera_b`), because fixed distances only suit one zoom level.
- **Those fixed values no longer fit the default view.** The camera now starts 15 m out, zooming between `near_distance` 6 and `far_distance` 22, so 22 is now the furthest zoom. The ratios below carry over.
- For real use, `CameraRig.gd` should set the DOF distances from `_current_distance` every frame so the focus follows zoom. Starting ratios from the default view: near = 0.68·d (transition 0.23·d), far = 1.23·d (transition 0.45·d), amount 0.12. Then tune by eye so foreground units stay sharp at close zoom.
- Put the `CameraAttributesPractical` on the rig's `Camera3D` (`attributes`) so the camera owns it. The harness put it on the WorldEnvironment.

## 8. Camera field of view (27)

- `CameraRig/Camera3D`: `fov` 40 (currently 75).
- Scale every distance by ×2.11 (tan 37.5° / tan 20°) to keep the framing. These are the current values, as of 2026-10-02:

  | Setting | Now | At FOV 40 |
  |---|---|---|
  | CameraRig `near_distance` | 6 | 12.7 |
  | CameraRig `far_distance` | 22 | 46.4 |
  | CameraRig `min_frame_distance` (framing a reaction) | 16 | 33.7 |
  | CameraRig `max_frame_distance` | 28 | 59.0 |
  | Camera3D's authored z position, BoundaryMap and CombatMap | 15 | 31.6 |
  | Camera3D's authored z position, LineOfSightTest | 16 | 33.7 |

  The rig reads its starting zoom from the Camera3D's position. The `CameraRig.gd` values are the script's defaults, with no per-scene overrides, so change them in the script.
- Pan speed scales with `_current_distance / far_distance`, so it doesn't change.
- Check that the sun's `directional_shadow_max_distance` (100) still covers the map from 59 m, the furthest framing distance.
- **The scenery ring:** at `view_pitch` 55°, the narrower lens from the scaled distance sees less far past the pivot than the 75° lens does. The top of the screen reaches about 1.3 × the unscaled zoom distance beyond the pivot, against about 2.0 now. So the 75-tile ring should still hide its outer edge. Confirm with renders zoomed all the way out and framed at the limit (CLAUDE.md, "Scenery around a combat map").

## 9. Global illumination (04, 05)

- **04 (SDFGI):** the `sdfgi_*` properties, a soft PCSS sun (`light_angular_distance` 3) and the studio-grey sky.
  - **Verified:** the GridMap blocks feed SDFGI. In a sun-only render, shadowed faces went pure black with SDFGI off and filled with coloured bounce with it on.
  - The heaviest option here.
  - **Untested:** how SDFGI copes with the terrain changing. Blocks now break, wear away voxel by voxel, and scatter thousands of debris lumps. Test a grenade crater, a broken crate stack and a felled tree before relying on it.
- **05 (SSIL):** the `ssil_*` properties. It's screen-space, so it only bounces light from what's on screen. It's also cheaper.
- **VoxelGI (not tried):** the search summary saved in [GoogleSearch.png](GoogleSearch.png) recommends it, and it would suit a small bounded map. It needs a `VoxelGI` node over the map bounds, baked in the editor or with `VoxelGI.bake()` at runtime. It's static once baked, so every broken or worn block would leave stale light behind until a re-bake. Terrain now changes with nearly every shot, so measure the re-bake cost early. Try it as a new harness style next to 04 before committing to it.

## Previewing and checking with the harness

[`harness/`](harness/) renders any style from the real game, without changing the project:

```bash
Styles/harness/render.sh 21 28        # from the repo root -> Styles/harness/out/NN-name.png
Styles/harness/render.sh 0            # style 0 = the scene exactly as it currently is
MAP=res://Scenes/BoundaryMap.tscn Styles/harness/render.sh 28   # the encounter map instead of CombatMap
```

The script copies the harness into `vcom/_probe/`, runs Godot with a window (`--headless` can't render), and deletes `_probe/` again. Set `GODOT=` if the editor isn't at `C:\Program Files\Godot\Godot_v4.7-stable_win64_console.exe`, and `OUT_DIR=` to write somewhere other than `Styles/harness/out/`.

**Verifying an applied style:** compare like with like.

1. **Before** applying, render the style with the harness on the current code, for both CombatMap and BoundaryMap.
2. Apply the style, then render style 0 for both maps and compare them with those renders.
   - Repeat renders are byte-identical on this machine (RTX 3060 Laptop, D3D12, Godot 4.7-stable). That was checked for unchanged styles on 2026-09-26 and for style 0 on both maps on 2026-10-01. A faithful application should therefore match closely; another GPU or driver may differ slightly.
   - The `Styles/NN-*.png` screenshots can't be matched any more: they show the old capsules and the old camera distance.
   - For 15 and 22, expect the units to differ, since the harness no longer changes them (section 4).
3. Check that `--headless --path . --quit-after 120` loads with no new errors.
4. Play-test rotating, zooming and panning, since the renders cover only two fixed views. Break some terrain while you're at it (section 3).

**Tuning or adding a style:** edit `VariantList.gd` for values and `VariantNotes.gd` for the description, cost and kept list, then re-render. To refresh the catalog's per-style sections, run `dump_notes.gd` (usage in its header) and paste its output into `VISUAL_VARIANTS.md`.

**Capture details:**
- 1280×720 per panel, `--fixed-fps 60`.
- Left panel: 150 frames after load, through the map's authored camera. That's distance 15 now; the screenshots were taken at 22.
- Right panel: 90 more frames through a separate Camera3D at pivot (9, 1, −8), yaw 38°, pitch 36°, distance 15. The distance is scaled by the FOV ratio for style 27. The HUD and TileHighlights are hidden and a caption is added.
- The probe turns off the rig's edge-pan and input so a stray cursor can't move the camera.

## Open decisions (ask when applying)

1. The block-material hookup: a runtime `@tool` script or an importer option (section 3).
2. Whether `LineOfSightTest.tscn` should get the same look (recommended: yes). `BoundaryMap.tscn` always should.
3. For 11: should the focus follow zoom (section 7), and how much blur is acceptable during play?
4. For 27: is the camera change wanted? It changes how zoom feels, not just the art.
5. For the block and toon styles: should the props and coins match too? Broken crates and debris do need the style, or broken terrain will look out of place (section 3).
6. Performance budget, for 04 (SDFGI is heavy) and for MSAA at high resolutions.
