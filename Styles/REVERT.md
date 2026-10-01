# Reverting to the original look

This file records the game's visual setup as it was on **2026-10-01**, before any style from [VISUAL_VARIANTS.md](VISUAL_VARIANTS.md) was applied, and how to get back to it. It's written for whoever is asked to "revert the visual style" later, most likely Claude in a new session. Read it all before changing anything.

**Baseline commit:** `5f9a0f900be613b1133afd23f6d9ceccc9389bfc` (`5f9a0f9`, "Model changes"). When this was written, the working tree had no uncommitted changes to anything visual, so that commit *is* the original look.

**Applied since:** style `05`, Colour Bounce, on 2026-10-01. It changed only these, and nothing else visual:

- in each of `CombatMap.tscn`, `BoundaryMap.tscn` and `LineOfSightTest.tscn`:
  - the `ProceduralSkyMaterial_sky` sub-resource: five sky colour lines added;
  - the `Environment_world` sub-resource: `background_mode` 1 → 2, `ambient_light_energy` 0.45 → 0.6, and the `ssao_*` / `ssil_*` lines added;
  - the `DirectionalLight3D` node: a new `transform`, plus the `light_color` and `light_energy` lines;
- in `project.godot`: the `anti_aliasing/quality/msaa_3d=2` line.

Undoing it means putting exactly those back as section 1 and section 2 below give them. No script, shader, material or node was added.

**Reference renders:** [REVERT-CombatMap.png](REVERT-CombatMap.png) and [REVERT-BoundaryMap.png](REVERT-BoundaryMap.png), made with the harness's style 0 on 2026-10-01. BoundaryMap is the map every encounter is fought on. (`00-current-look-reference.png` is older, from 2026-09-26: capsule units and a camera at distance 22. The catalog compares against it, so don't use it to verify a revert.)

## How to revert

1. **Find what was changed.** Run these from the repo root:

   ```bash
   git log --oneline 5f9a0f9..HEAD                      # which commits applied the style?
   git diff 5f9a0f9 --stat -- vcom/project.godot vcom/Scenes vcom/Blocks vcom/addons vcom/Scripts vcom/Resources
   git status --short                                    # untracked shaders, scripts, LUT images
   ```

2. **If the style was applied in commits of its own** that touched nothing but visuals, `git revert` those commits. That's the cleanest route. Check each commit's diff first.

3. **Otherwise, revert surgically.** Do **not** `git checkout 5f9a0f9 -- <scene>`. `CombatMap.tscn`, `BoundaryMap.tscn`, `LineOfSightTest.tscn`, `SquadUnit.tscn` and `project.godot` also hold the gameplay (terrain, units, nodes, input), which will have moved on since this commit. Work through the checklist below: put each listed value back exactly, remove what the "must not exist" lists name, and leave everything else alone. Files that exist *only* for a style, such as a copied shader or a material-hookup script, can simply be deleted.

4. **Re-import if the importer was touched** (section 4): `"$G" --headless --path . --import` from `vcom/`.

5. **Verify** (end of this file).

A scene line not shown in a block below is at its Godot default. Restoring a block means making it match exactly, which includes deleting lines a style added. Keep each node's own header line (its `unique_id` and so on) as it is now; only the properties under it are the baseline. The `Transform3D` lines below are copied from the files, so pasting them back is safe (CLAUDE.md warns against *composing* transforms by hand, not against restoring serialised ones).

To print the current visual blocks of the three maps and compare them with this file (from `vcom/`):

```bash
for f in Scenes/CombatMap.tscn Scenes/BoundaryMap.tscn Scenes/LineOfSightTest.tscn; do echo "== $f"; awk '/^\[/{ p = ($0 ~ /ProceduralSkyMaterial|type="Sky"|Environment|Material|PlaneMesh|QuadMesh|Texture|Gradient|CameraAttributes|WorldEnvironment|Light3D|GI"|CameraRig|Camera3D|"Boundary"|"Ground"|"GridMap"|TileHighlights|name="Model"|Outline/) } p && !/"cells"/' "$f"; done
```

## Checklist: the original setup

### 1. Renderer and project settings: `vcom/project.godot`

The whole `[rendering]` section is exactly:

```ini
[rendering]

rendering_device/driver.windows="d3d12"
renderer/rendering_method.mobile="forward_plus"
```

- **Renderer: Forward+.** There's no `renderer/rendering_method` line because Forward+ is the default. It was switched from GL Compatibility in commit `655a976` on 2026-09-26, while the styles were being explored, and it's part of the original look: **do not** go back to `gl_compatibility`. A headless run reports `forward_plus` on `d3d12`.
- `[application] config/features` still says `"GL Compatibility"`, a stale tag left over from the switch. It doesn't change rendering, so leave it however you find it.
- **No anti-aliasing:** no `anti_aliasing/*` lines (MSAA 3D off, screen-space AA off, TAA off). Remove any that a style added.
- No `scaling_3d/*`, `lights_and_shadows/*` or `environment/defaults/*` lines either. In effect: a 4096 directional shadow atlas, soft shadow filter quality 2 (Soft Low), and 3D scaling at 1.0.
- No game script touches viewport AA, scaling, camera attributes or environment effects at runtime. The harness did that for its previews; the baseline has none of it.

### 2. Environment, sky and sun: the three combat maps

Each of `vcom/Scenes/CombatMap.tscn`, `BoundaryMap.tscn` and `LineOfSightTest.tscn` has its own copy of these.

**Sky and Environment.** These are the same in CombatMap and LineOfSightTest:

```ini
[sub_resource type="ProceduralSkyMaterial" id="ProceduralSkyMaterial_sky"]

[sub_resource type="Sky" id="Sky_world"]
sky_material = SubResource("ProceduralSkyMaterial_sky")

[sub_resource type="Environment" id="Environment_world"]
background_mode = 1
background_color = Color(0.08, 0.09, 0.12, 1)
sky = SubResource("Sky_world")
ambient_light_source = 3
ambient_light_energy = 0.45
tonemap_mode = 2
```

**BoundaryMap** is identical except for a sky-blue backdrop: `background_color = Color(0.53, 0.8, 0.97, 1)`.

What those values mean:

- `background_mode = 1` (Custom Color): the backdrop is a flat colour, dark navy or sky blue, and the sky is never drawn.
- The `ProceduralSkyMaterial` has **no properties**, so it's all Godot defaults. It isn't visible, but `ambient_light_source = 3` (Sky) lights everything from it at energy 0.45. A style that recoloured the sky changed the ambient light too, even with the backdrop left alone, so empty the material again.
- `tonemap_mode = 2` is Filmic, at the default exposure and white.
- Everything else is off: SSAO, SSIL, SDFGI, glow, fog, volumetric fog and adjustments (`adjustment_enabled`, so no saturation, contrast or colour-correction LUT).
- The `WorldEnvironment` node has only `environment = SubResource("Environment_world")`, with no `camera_attributes`.

**Sun.** It's identical in all three maps:

```ini
[node name="DirectionalLight3D" type="DirectionalLight3D" parent="." ...]
transform = Transform3D(0.57346237, -0.65132743, 0.49690402, 0, 0.60654867, 0.79504645, -0.8192319, -0.45592922, 0.34783283, 10, 20, -10)
shadow_enabled = true
```

- That transform is `rotation_degrees ≈ (-52.66, 55.01, 0)` at origin (10, 20, −10). In the harness's terms it's **elevation 52.66°, azimuth 55.01°**, coming from the south-east: about 10° off the camera's own heading (yaw 45°), which is why faces look front-lit and flat. That's the original look; keep it.
- Every other light property is at its default: energy 1.0, white, angular distance 0 (hard-edged), shadow blur 1.0, PSSM 4 splits, shadow max distance 100.
- **There is only this one light.** Remove any second `DirectionalLight3D`, fill light, `ExtraLight*`, `OmniLight3D` or `SpotLight3D` a style added.

### 3. Camera

**CombatMap and BoundaryMap:**

```ini
[node name="CameraRig" type="Node3D" parent="." ...]
transform = Transform3D(0.7071068, -0.4540581, 0.5420621, 0, 0.7665916, 0.6421351, -0.7071068, -0.4540581, 0.5420621, 10, 1, -10)
script = ExtResource(...CameraRig.gd)

[node name="Camera3D" type="Camera3D" parent="CameraRig" ...]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 15)
current = true
```

**LineOfSightTest:**

```ini
[node name="CameraRig" ...]
transform = Transform3D(1, 0, 0, 0, 0.8090171, 0.58778524, 0, -0.5877853, 0.809017, 7.5, 1, -14.5)

[node name="Camera3D" ...]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 16)
current = true
```

- In CombatMap and BoundaryMap the rig's pivot is (10, 1, −10) at yaw 45°. Its authored tilt is ignored at runtime, since the rig always looks down at `view_pitch`. The camera starts at zoom distance 15. In LineOfSightTest the pivot is (7.5, 1, −14.5) at yaw 0°, distance 16.
- The `Camera3D` sets no `fov`, so it's at the default **75°**, and no `attributes` (no depth of field).
- `vcom/Scripts/CameraRig.gd` exports, at their script defaults with no per-scene overrides: `near_distance = 8.0`, `far_distance = 22.0`, `view_pitch = 55.0`, `min_frame_distance = 16.0`, `max_frame_distance = 28.0`.
  - The 75-tile scenery ring is sized for exactly these values, so restoring them also restores that guarantee (CLAUDE.md, "Scenery around a combat map").
- `CameraRig.gd` has no depth-of-field code. Style 11 suggests adding per-frame DOF distances there; remove that if it was added.

### 4. Block materials: terrain, scenery and debris

- **The blocks are `vcom/Blocks/*.vox`**, imported by the MagicaVoxel addon. Each imported mesh carries the material built in `vcom/addons/MagicaVoxel_Importer_with_Extensions/MeshGenerators/GreedyMeshGenerator.gd`:

  ```gdscript
  var material = StandardMaterial3D.new()
  material.vertex_color_is_srgb = true
  material.vertex_color_use_as_albedo = true
  material.roughness = 1
  ```

  Everything else is at its default: Burley diffuse, Schlick-GGX specular, metallic 0, no rim. The scene importer (the crate's pieces) builds its meshes with the same generator, so it gets the same material.
- **The addon is unmodified** since it was added in `184c84d`: `git diff 5f9a0f9 -- vcom/addons/` must come back empty. If a style added a material import option (APPLYING.md option **b**), restore the addon and the import files, then re-import.
- **Import options**, the `[params]` of each `.vox.import`:
  - `Blocks/BrightGrass1`, `BrightCrate1`, `SkinnyTree1Bottom`, `SkinnyTree1Top`: `Scale=0.0625 GreedyMeshGenerator=true SnapToGround=false FirstKeyframeOnly=true`
  - `Blocks/Destruct_BrightCrate1` (imported as a scene): `Scale=0.0625 GreedyMeshGenerator=true SnapToGround=false OriginsToGeometry=false ImportAnimation=true AnimationFPS=8.0 AnimationLoop=true AnimationAutoplay=false`
  - `Characters/BaseCharacter`, `Items/Coin2`, `Rifle2`, `Shortsword2`, `StickGrenade`: `Scale=0.063 GreedyMeshGenerator=true SnapToGround=false FirstKeyframeOnly=true`
- **`Blocks/BlockLibrary.tres` and `Blocks/SceneryLibrary.tres`** each hold the four blocks, with the mesh taken straight from the `.vox` and no material.
  - `mesh_cast_shadow` is `1` in BlockLibrary and `0` in SceneryLibrary. That difference is the scenery's performance setup, not a style, so keep it.
- **No runtime material hookup** (APPLYING.md option **a**). In the baseline:
  - nothing calls `surface_set_material()` on MeshLibrary meshes;
  - there's no `BlockMaterials` node, and neither GridMap has a script;
  - there's no `vcom/Scripts/Rendering/` folder.

  Delete any hookup script or node, and any copied `VoxelBlock.gdshader`. The **only** shader in the project at baseline is `vcom/Scripts/Combat/TileHighlight.gdshader`, the tile highlights, which no style touches.

  **Exception, added after this baseline: the tile grid. Keep it.** On 2026-10-01 the game gained an optional tile grid. It's a gameplay option, not a style, and isn't part of anything to revert. It consists of:
  - `vcom/Scripts/Combat/TileGrid.gd`, a `TileGrid` node in each combat map before `TerrainDestruction`;
  - `TileGrid.gdshader`;
  - the `toggle_grid` input action and the `tile_grid` shader global in `project.godot`;
  - the **Tile Grid** button on the System tab.

  It does call `surface_set_material()`, putting `TileGrid.gdshader` on the grass mesh, but with the grid off that shader draws as the importer's material does: CombatMap and LineOfSightTest render identically, and BoundaryMap differs in 7 pixels of 1.8 million. So a revert leaves it exactly as it is.
- **What takes its material from the blocks:**
  - `WornBlock`, `VoxelBody` and `VoxelMesher` use `VoxelShape.material`, which is the imported mesh's own, so they follow the blocks back with no code change.
  - **Broken crates** are swapped for `Scenes/Destruct_BrightCrate1.tscn`, which has no material overrides: its meshes carry the importer's material. `ScriptedDestruction` sets only physics materials on the pieces. APPLYING.md suggests giving the pieces a style's material, for example in `ScriptedDestruction.prepare()`; remove any such code.
  - `VoxelDebris` builds its own material: vertex colour as albedo, sRGB, roughness 1.0 (`VoxelDebris.gd`, where `_cube.material` is set). So does `VoxelRig` for the baked figure, but every unit overrides it (section 5).
  - If a style edited either of those scripts, put those three settings back.
- **BoundaryMap's scenery ground plane** (`Boundary/Ground`) is the grass block's top colour. A style that recoloured grass may have recoloured it to match. Restore:

  ```ini
  [sub_resource type="StandardMaterial3D" id="StandardMaterial3D_h16oa"]
  vertex_color_is_srgb = true
  albedo_color = Color(0.45882353, 0.654902, 0.2627451, 1)

  [sub_resource type="PlaneMesh" id="PlaneMesh_frw4l"]
  material = SubResource("StandardMaterial3D_h16oa")
  size = Vector2(183, 201)
  ```

  The node itself: `transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 15.5, 0.98, -24.5)`, `cast_shadow = 0`, `mesh = SubResource("PlaneMesh_frw4l")`, `script = ExtResource(...SceneryGround.gd)`.

### 5. Unit materials

Every unit wears `Scenes/BaseCharacter.tscn` (baked; never edit it by hand), painted one flat colour through `CharacterModel.body_material`:

- **Squad:** `vcom/Scenes/SquadUnit.tscn` has `[sub_resource type="StandardMaterial3D" id="Mat_unit"]` with **no properties**, set as the Model's `body_material`.
  - `Unit._paint()` hands it to `CharacterModel.paint()`, which duplicates it and sets only `albedo_color` to the character's `color`. So anything a style put on `Mat_unit` (toon diffuse, rim and so on) reached every squad member. Empty it again.
  - If a style changed `CharacterModel.paint()` or `Unit._paint()` instead, restore those to the baseline commit.
- **Enemies:** `Mat_enemy1` is `albedo_color = Color(0.85, 0.15, 0.15, 1)` and nothing else, in CombatMap, BoundaryMap and LineOfSightTest.
- **LineOfSightTest's eight squad units:** `Mat_player1`–`Mat_player8`, albedo only, alpha 1:
  - 1: (0.2, 0.45, 0.9)
  - 2: (0.25, 0.75, 0.3)
  - 3: (0.95, 0.8, 0.15)
  - 4: (0.6, 0.35, 0.85)
  - 5: (0.95, 0.5, 0.15)
  - 6: (0.15, 0.75, 0.8)
  - 7: (0.95, 0.45, 0.7)
  - 8: (0.85, 0.85, 0.8)
- **Character colours** (`vcom/Resources/Characters/*.tres`, `color`) are character data, not part of the look. No style changes them.
- **Props** (rifle, sword, grenade, coin): the importer's material, with no overrides in `Scenes/Props/*.tscn`.

### 6. Post-processing, GI and effects: none

The baseline has none of the following. Delete any that exist:

- **Outline pass:** no `OutlinePass` / `OutlinePost` `MeshInstance3D` (a full-screen `QuadMesh` with a `render_priority = -128` ShaderMaterial) in any map, and no `Outline.gdshader` in the project.
- **Colour-correction LUT:** no `adjustment_color_correction`, no `GradientTexture1D`, and no LUT image imported as `Texture3D`.
- **Depth of field:** no `CameraAttributesPractical` on the WorldEnvironment or the Camera3D.
- **Global illumination:** no SDFGI, SSIL or SSAO on the Environment, and no `VoxelGI` / `LightmapGI` node or baked GI data.

**Not part of any style, so leave these alone:**

- the tile highlights (`TileHighlights.gd` and its shader)
- the optional tile grid (`TileGrid.gd` and its shader; see section 4)
- `Explosion`, `MuzzleFlash` and `ThrownGrenade`
- the `SquadStart` editor squares
- the HUD and every menu (built in code with `StyleBoxFlat`)
- the world map (2D)
- `PreviewAnimations`' own preview lighting
- the harness in `Styles/harness/`

## Verify

From `vcom/`, with `G="/c/Program Files/Godot/Godot_v4.7-stable_win64_console.exe"`:

1. **It loads.** Run `"$G" --headless --path . --quit-after 120` and check there are no new errors.

2. **It renders as it did.** From the repo root, give each run a fresh output folder:

   ```bash
   OUT_DIR=<fresh dir> Styles/harness/render.sh 0
   MAP=res://Scenes/BoundaryMap.tscn OUT_DIR=<another fresh dir> Styles/harness/render.sh 0
   ```

   Compare the output with `REVERT-CombatMap.png` and `REVERT-BoundaryMap.png`.
   - **On 2026-10-01 these renders were byte-identical across runs on this machine** (D3D12, Godot 4.7-stable). The md5s were `0ced74c0b59bfe0757326686eba9af08` for CombatMap and `db3a4d2d4b5f4f81fc4a5f1e468343f0` for BoundaryMap. So, as long as nothing else on those maps has changed, a faithful revert reproduces them exactly.
   - **Once the maps' content has moved on** (terrain, units, the figure, the HUD), the files can't match byte for byte. Compare the look instead:
     - a flat dark-navy backdrop on CombatMap, sky blue on BoundaryMap;
     - bright, evenly front-lit grass and crates with little shading between faces;
     - crisp shadows falling mostly away from the camera, so little shadow shows;
     - flat-coloured figures;
     - no outlines, colour grade, blur or bounce light.

3. **It plays as it did.** Rotate, zoom and pan in a real run, since the renders show only two fixed views.

The harness's `MAP=` option (`--map=` in `VisualProbe.gd`) was added on 2026-10-01 so BoundaryMap could be rendered. Without it the harness renders CombatMap.
