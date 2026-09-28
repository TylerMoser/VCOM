# CLAUDE.md

Working notes for VCOM, a turn-based tactics prototype (XCOM / Star Wars: Zero Company) in Godot
4.7 on a voxel grid. `README.md` has the player-facing rules; this file is about working in the
code.

## Layout

The git root is `VoxelXCOM/`; the Godot project is `vcom/`, which is where commands are run from.
`MagicaVoxel/` holds source `.vox` art outside the project. `Styles/` holds candidate visual styles
(screenshots, exact settings, a render harness) not yet applied; `Styles/APPLYING.md` explains how
to apply one.

```
vcom/Scripts/
  Unit.gd              health, actions, reaction, walking, shoot_at()
  PlayerSquad.gd       members + selection; drops the dead
  TurnManager.gd       turn order, end-turn hold, carrying out enemy AI decisions
  Reactions.gd         reaction window: slow motion, number prompts, reaction fire
  CameraRig.gd         orbiting tactical camera; frame() / release_frame() for the reaction view
  Combat/
    CombatGrid.gd      tiles, pathfinding, is_line_clear(), cast(), pick_tile(), terrain_struck
    LineOfSight.gd     cover, step-out, find_shots() -> Shot
    HitChance.gd       the to-hit sum (Estimate + Term), roll()
    Ballistics.gd      where a round goes: hits along the sight line, XCOM 2 misses -> Path
    ShotPlayback.gd    shots not taken from the action bar: lean out, show, shoot_at(), lean back
    Weapon.gd          Resource: damage, environment_damage
    TileHighlights.gd  named layers of coloured squares
  AI/
    EnemyAI.gd         Resource base: choose_action(tactics) -> AIAction
    AssaultAI.gd       close in, point-blank when adjacent, best odds with the last action
    AIAction.gd        MOVE (path) / SHOOT (shot + estimate) / END_TURN
    Tactics.gd         shared queries: adjacent_foes, shots_at, best_shot, advance, paths
  Terrain/
    TerrainDestruction.gd  breaks struck blocks, drops what they held, drops stranded units, tidies debris
    Destruction.gd         Resource base: how a kind of block comes apart, shatter(); mass; Motion
    ScriptedDestruction.gd pieces cut in advance, swapped in and left to fall or blasted apart
    FallingBlock.gd        a block whose support broke, falling whole until it lands
    Blast.gd               a burst from a point: impulse by distance and the area a piece shows
    DestructionCatalog.gd  Resource: every breakable block, shared by every map
  Actions/             UnitAction base + ActionController + Move/Shoot/Overwatch
  UI/                  every HUD widget, built in code
```

## Architecture

**Actions are nodes.** `ActionController` takes its `UnitAction` children as the actions offered on
the action bar; `ActionBar` builds one button per child. The first child is the default activated on
selection. Add an action by writing a `UnitAction` subclass and adding it as a child in the scene —
no UI code changes needed.

An action gets `begin(unit)` / `end()` / `handle_input(event)` / `is_available(unit)`, sets
`controller.busy = true` while it plays out, and emits `completed` when done. The controller then
re-`begin`s it if it is still available, or drops it.

**Highlights are named layers.** `TileHighlights.set_layer(name, {tile: Color}, fill)` — each caller
owns a layer, last set draws on top. Current layers: `selected`, `move`, `move_path`,
`shoot_step_out`, `overwatch`.

**The HUD is written in code, not scenes.** Widgets build their children in `_init()` and style
themselves with `StyleBoxFlat` overrides. Follow that rather than adding `.tscn` files for UI.

**Node wiring is `@export var *_path: NodePath` + `get_node_or_null` + `push_error`.** Keep that
pattern. Something optional (like `ShotOverlay` in `ShootAction` and `TurnManager`) errors but
carries on behind `if x != null`; something essential bails.

**Enemy AI is a `Resource` that only decides.** Each enemy has `Unit.ai` (like `Unit.weapon`), set in
the scene to a shared `.tres` such as `Resources/AI/Assault.tres`. `TurnManager._take_enemy_turn`
asks `ai.choose_action(Tactics.new(...))` once per action and carries out the `AIAction`, charging
squad costs: `ceil(tiles / move_range)` for a move (at least 1, and cut to what the unit can afford),
`ShootAction.COST` for a shot. So a new enemy type is an `EnemyAI` subclass plus a `.tres`; no turn,
reaction or camera code changes. Put reusable queries on `Tactics`, not in one AI. AI resources are
shared between units, so they must stay stateless (the same rule as `Weapon`). An enemy with no `ai`
sits its turn out with a warning.

**Enemies walk through `Reactions.walk()`.** It starts the walk with `Unit.start_walk()` so it holds
the tween, then polls it each frame: on every new tile it works out who on overwatch could fire
(`_find_offers`), opens or closes the window, slows the tween (`slow_motion_scale`), and holds it at
speed 0 while a reaction shot plays out. `TurnManager` calls `release_view()` after each enemy's
turn to hand the camera back. A window only exists during a walk; nothing else opens one.

**A shot is settled when it is fired and lands when it arrives.** `Unit.shoot_at(shot, chance,
grid, show_rounds)` rolls, then asks `Ballistics` for the round's `Path`: the sight line for a hit;
for a miss, XCOM 2's placement, an aim point on a ring around the target's body (or, `COVER_SHARE`
of the time, on the target's cover) traced with `CombatGrid.cast()` until something stops it or it
leaves the map. It then awaits `show_rounds` (`ShotOverlay.show_rounds`, which draws the tracer and
returns as it lands), and only then damages the target and reports any terrain the round struck
through `CombatGrid.strike()` as `terrain_struck`. `shoot_at` is a coroutine; always `await` it.

**Breakable blocks are data.** `TerrainDestruction` (a node in each map) listens to
`terrain_struck` and looks the struck block up in `Resources/Destruction/Catalog.tres`, a
`DestructionCatalog` of `Destruction` resources each naming a block by its MeshLibrary item name.
A block with no entry never breaks. A breaking block leaves the grid at once, then its destruction's
`shatter(site, at, hit, motion)` plays out what is left under the `TerrainDestruction` node, `at`
being where the grid drew the block's mesh.

**Stacks fall, then break.** Every breakable block stacked on a broken one, up to the first that
cannot break, leaves the grid in the same moment but does not break yet: it becomes a
`FallingBlock` (its own mesh and collision, as heavy as its destruction's `mass`) that drops
straight down its column and breaks where it lands, calling `shatter` with a `Destruction.Motion`
so its pieces carry on its fall. It has landed once something takes more than half its speed away
after it has got going (0.5 cells a second), once it has sat still for a quarter of a second, or
three seconds after it was let go; it reports where it was two physics steps earlier (see
Gotchas). A unit left standing on nothing drops (`Unit.drop_to`) through the rubble, and
`TerrainDestruction.Collapse` lets it pass through the pieces the falling blocks leave later too
(`Unit.pass_through`). Where the wreck under a falling block can get out of the way (a stack in the
open, blasted apart) the blocks fall nearly a whole cell and smash; in a one-cell slot between two
columns the columns hold the wreck in place, and the blocks drop on to it.

To make another object break like the crate:

1. Model the pieces in MagicaVoxel in the same frame as the block's own model, as separate models.
2. Import the `.vox` as a Scene at **Scale 0.0625**, the blocks' scale, or the pieces will not line
   up with the block they replace. Make an inherited scene of it in `Scenes/` to add to.
3. Make a `ScriptedDestruction` `.tres` in `Resources/Destruction/` naming the block and that scene,
   and add it to `Catalog.tres`. Set its **Mass** to what the block weighs whole, if it is not
   about a crate's 300 kg; that is only felt while it falls.

Every bare mesh in the scene becomes a rigid body with a box collider, 3.5% smaller than the mesh
(`ScriptedDestruction.SLACK`, see Gotchas); a `RigidBody3D` you author is used as it is, and other
nodes are left alone. A new way of breaking is a `Destruction` subclass that overrides `shatter()`,
the same shape as a new enemy being an `EnemyAI` subclass; it should honour `motion` when given
one, adding `motion.at(point)` to what it throws each part of the block at.

That block just collapses, which is the default. To have it burst apart instead, as the crate does:

4. In the pieces scene, add a `Marker3D` named **`DestructOrigin`** where the blast goes off, with a
   `float` metadata entry **`force`**: 1 is a moderate blast (a crate's boards land about a cell and
   a half out, nine in ten within three), 2 is twice as hard, 0 is none; left out, it is 1.
5. Tick **Blast** on the block's `ScriptedDestruction` `.tres`.

Untick Blast to go back to the plain collapse; the marker is then ignored, so it can stay in the
scene. The blast goes off every time the block breaks, including when it comes down because the
block under it broke. Blast on with no marker warns and collapses. Where the marker sits shapes the
burst: the crate's is at the bottom centre, like a charge underneath, so it throws up and out; one
at the middle of the block throws evenly every way.

`Blast.burst(pieces, origin, force)` works on any `RigidBody3D`s, so a new `Destruction` can use it
too. Each piece gets an impulse away from the origin of `force * Blast.IMPULSE / (r² + Blast.CORE²)`
times the area it turns toward the origin (from its box colliders), applied at its point nearest the
origin. So the push falls off with the square of the distance, as a real blast's does, but stays
finite at the origin; a board facing the blast is thrown harder than one edge-on to it, a light
piece further than a heavy one, and pieces tumble as they fly. `IMPULSE` is what force 1 means, and
is the only thing to retune if every blast is too strong or too weak.

**Physics is only for debris.** Layers: 1 terrain, 2 unit clicks (`Unit.PICK_LAYER`), 3 debris,
4 unit bodies (`Unit.BODY_LAYER`). Blocks have no collision in the MeshLibrary, so
`TerrainDestruction` gives the map a copy of it with a cube on every shapeless block. Debris stays
live for good and sleeps when still. Each unit carries a frictionless `AnimatableBody3D` capsule,
starting `Unit.BODY_CLEARANCE` above its feet, that shoves debris aside and is never pushed back.
A `FallingBlock` is on the debris layer but never collides with units: nobody can stand in its
column but units dropping with it. It is 1 cm narrower than its cell on each side
(`FallingBlock.CLEARANCE`), cannot turn, and is frictionless, so it slides down between the blocks
either side of it instead of wedging between them. Debris knocked off the map, or wedged inside a
block, is removed. The rules never look at debris.

## Conventions

- `##` doc comments on every class and non-obvious method, written in plain prose explaining *why*,
  not restating the signature.
- `&"name"` StringNames for groups and input actions; `^"path"` NodePaths.
- Nullable returns use `Variant` with a `null` check (`find_shot`, `current_shot`, `pick_tile`), so
  callers need an explicit type annotation to unpack them.
- Units are in group `units` plus `players` or `enemies`.

## Combat rules that must not drift

- A unit fills **two cells** (`CombatGrid.UNIT_HEIGHT`) and sights from the centre of the upper one
  (`LineOfSight.EYE_HEIGHT`). This is what makes 1-cell blocks half cover (never blocks sight) and
  2-cell blocks full cover (blocks it).
- **Step-out requires cover.** A unit in the open fires from its own tile only.
- **Flanked ≠ uncovered.** `Shot.flanked` is true only when the target has cover that does not face
  the shot. A target in the open is "In the Open" and gets no flanking bonus.
- Everything about a shot — cover, height, distance — is measured from `Shot.from`, the tile the
  shot is *taken* from, which may be a step-out tile.
- **Hit chance is computed once**, when the shot is lined up (`ShootAction._estimate`), and that is
  what gets rolled. Do not recompute at fire time. A reaction's shot is lined up each time the enemy
  reaches a new tile (`Reactions._find_offers`); its prompt shows that estimate and firing rolls it.
- `Unit.shoot_at(shot, chance, grid, show_rounds)` is the single place a shot is resolved.
  `ShootAction`, the enemy AI and reaction fire all go through it; keep it that way so they cannot
  diverge.
- **Where a round goes is decided once, after the roll, when it is fired** (XCOM 2's order), by
  `Ballistics`, and nothing recomputes it: the tracer draws that path and the terrain it ends on is
  what `terrain_struck` reports. One path per shot, as in XCOM 2.
- **A hit flies the sight line**, eye to eye, so it never touches terrain. Only misses strike it.
- **Stray rounds never wound anyone and never pass through a unit**, the target included, except a
  unit standing in the line of fire itself, which every round passes through since units never block
  sight. A miss never stops on terrain more than `Ballistics.SHORT_OF_TARGET` short of the target.
- **Damage and terrain strikes land when the round does**, inside `shoot_at`, not when it is fired.
- **A broken block leaves the grid the moment the round strikes it**, before any debris moves, so
  sight, cover and paths never wait on physics, and so does every breakable block stacked on it,
  though it is still to be seen falling. Debris, and a falling block, is for show: nothing in the
  rules reads it.
- **Reactions are Pathfinder's:** one per unit, refilled in `Unit.start_turn()`. Overwatch spends all
  remaining actions to hold it, and its shot takes `HitChance.REACTION_PENALTY` via
  `for_shot(..., reaction = true)`.
- **Enemy shots roll the odds their AI chose them by.** `Tactics` builds each `AIAction.shoot` with
  its `HitChance` estimate, and the turn manager rolls that one; it never recomputes.
- **Reactions are the player's call, never automatic.** Only an enemy *walking* in sight opens a
  window (not leaning out to shoot). Keys `1`-`4` follow `PlayerSquad.members`, which is the squad
  panel's order; `0` passes on the current move only, and the next move is a new trigger.
- Units never block line of sight. Only terrain does.

## Verification

This project is verified by **running Godot headless and looking at rendered frames**, not by
reasoning about the code. Godot is at
`C:\Program Files\Godot\Godot_v4.7-stable_win64_console.exe` (use the `_console` build so stdout is
captured). Run from `vcom/`.

```bash
G="/c/Program Files/Godot/Godot_v4.7-stable_win64_console.exe"

# Does the main scene load without errors?
"$G" --headless --path . --quit-after 120

# Render real frames, then Read a PNG. --headless CANNOT render; omit it.
"$G" --path . --quit-after 150 --write-movie out/f.png --resolution 1280x720

# Drive logic or inspect state: a SceneTree subclass with _initialize() + await process_frame.
"$G" --headless --path . --script /abs/path/probe.gd

# Run a specific scene
"$G" --path . res://Scenes/LineOfSightTest.tscn
```

Probe scripts belong in the scratchpad directory, not the repo. To render a scene in a particular
state, write a temporary `res://_probe/Probe.tscn` + `.gd` that instantiates the map and drives it,
render, then **delete `_probe/`**.

`Scenes/LineOfSightTest.tscn` is the harness for the sight and shot rules. Four sight lanes: open,
half cover, step-out around a pillar, and a wall that can only be leaned around from the north.
Three shot lanes: a target in the open with a crate backstop behind it, a low crate wall running
under the line of fire into the target's half cover, and a squad member standing right behind the
target. Its crates break, so a probe that shoots there changes the lanes as it goes. Prefer adding
a lane there over reasoning about geometry in your head.

Physics runs headless, and with `--fixed-fps 60` every physics step is exactly 1/60 s, so debris
can be tested without rendering: break a block by calling `CombatGrid.strike()` with a hand-built
`RayHit`, then wait on `physics_frame`.

A `--script` probe's scene is not ready during `_initialize()`: its nodes' `_ready` runs once the
main loop starts, so await a frame after `root.add_child()` before reading anything `_ready` sets up.

## Gotchas

**New `class_name` scripts do not resolve until you import.** Creating a `.gd` outside the editor
leaves it out of the global class cache, and every script referencing it fails with
`Could not find type "X"`. Run `--headless --path . --import` once after adding one.

**`_unhandled_input` runs in reverse tree order.** `ActionController` sits after `PlayerSquad` in
`CombatMap.tscn`, which is the only reason the active action can swallow `Tab` before the squad
cycles. Do not reorder those nodes.

**A unit's tween dies with it, without finishing.** `create_tween()` binds to the node, so a unit
freed mid-walk leaves `await tween.finished` hanging forever. Anything that can kill a walker on the
way (a reaction) must poll `tween.is_running()` instead, as `Reactions.walk()` does. A tween is still
`is_valid()` on the frame it finishes, so `is_running()` is the test for "still going".

**`is_action_pressed` ignores extra modifiers but honours required ones.** `Shift+Tab` matches both
`next_target` and `previous_target`, so `previous_target` must be tested **first** (see
`ShootAction.handle_input` and `PlayerSquad._unhandled_input`). `Ctrl+Tab` still matches
`next_target`, which is why `show_shot_details` can safely be Ctrl.

**A held key does not re-trigger `is_action_pressed`.** Real behaviour, and desirable — you cannot
hold `Enter` to machine-gun. When scripting input in a probe, send press *and* release or the second
press does nothing.

**`Vector2i` has no `dot()`.** Multiply the components out.

**`.tscn` `load_steps` must be bumped** when you add `ext_resource`/`sub_resource` entries by hand
(it is total resources + 1).

**Do not hand-write `Transform3D`, GridMap `data`, or `project.godot` input events.** The text
serialization order is not the constructor order. Have Godot print `var_to_str(...)`, or build the
scene with a script and `PackedScene.pack()` + `ResourceSaver.save()`. When packing, every node must
have `owner` set to the root, recursively, or it is silently dropped; clear `scene_file_path` for a
standalone copy. But set it only on the nodes you add: re-saving an instantiated scene with every
descendant owned also saves the children HUD widgets build in `_init()` (the target panel, the
banner's label), which then get built twice, and reshuffles resource ids. To add to an existing
scene, generate it that way and splice just the new blocks into the original text.

**`CombatGrid.cast()` never cuts a corner; `is_line_clear()` does.** A sight line slips between two
blocks that meet at a corner, a ray does not. Use `is_line_clear` for who can see whom and `cast` for
where something lands; a hit follows the sight line and is never cast.

**Headless quirks:** the dummy renderer logs a spurious `Parameter "material" is null` for
`StandardMaterial3D` overrides, and the viewport mouse position is pinned at `(0,0)` while the
window reports focus.

**`AnimatableBody3D.sync_to_physics` leaves a body behind when its parent moves.** It hands the
body's transform to the physics server, and a parent moving underneath does not tell it. A unit's
body moves with the unit's tweens, so it is not synced. Jolt still moves a kinematic body with
velocity when its transform is set, so it pushes debris properly.

**A GridMap cell's collision goes at the end of the frame, not on `set_cell_item()`.** Debris
spawned where a block just was would start inside the block's old collision and be flung out, so
`ScriptedDestruction` holds the pieces frozen until the next `physics_frame`.

**A kinematic body driven into a heap grinds thin pieces into whatever is under them.** That is why
a unit dropping into its own rubble passes through it (`drop_to`'s `rubble`), and why its body
starts above its feet.

**A board landing on a round top with friction balances there and never comes to rest.** Jolt has
no rolling resistance, so a blasted board on top of a unit's capsule kept rocking and turning, and
kept every piece it touched awake: a whole heap creeping for as long as it was watched. That is why
unit bodies are frictionless; the board slides off instead.

**Contact is only found within 2 cm, so a fast body can end a step well inside what it hit.** Jolt
makes contacts within its speculative distance (0.02); a block falling 6 cells a second moves 10 cm
a step, so the step that reaches the floor can carry it 8 cm in, still at full speed, and only the
next stops it. That is why a `FallingBlock` reports where it was two steps before it was seen to
stop, and why its pieces are let go at once with continuous collision rather than held a step.

**Anything cut exactly as wide as a gap wedges in it and shivers for good.** A board one cell long
lying across the one-cell gap a broken block leaves between two others jams at the slightest turn,
and Jolt pushes it out of both walls every step, feeding energy into every piece it touches. That
is why debris boxes are 3.5% smaller than their meshes (`ScriptedDestruction.SLACK`) and a falling
block is 1 cm narrower than its cell.

**Probe runs in parallel can log `Jolt Physics job system exceeded the maximum number of jobs`.**
That is several Godot processes fighting over the CPU, not the scene; it does not appear run alone.

**Map coordinates:** floor blocks sit at `y=0` and walkable tiles at `y=1` in both current maps.
`CombatGrid.tile_position(tile)` is the floor surface (where units stand);
`CombatGrid.cell_center(cell)` is the middle of a cell (used for eye positions).

**`LineOfSightTest.tscn` is generated**, by a throwaway script that instantiates `CombatMap.tscn`,
rebuilds the GridMap and repositions units. That script is not in the repo, so edit the scene
directly or write a fresh generator.

## Known gaps

- A shared `Weapon` resource must stay stateless; give it `resource_local_to_scene` before adding
  per-unit state like rounds remaining.
- Only crates break, and only one way. `Weapon.environment_damage` reaches `terrain_struck` but
  nothing reads it yet: any strike breaks a crate.
- Rounds fly straight through debris: the trace only sees the grid.
- A column of crates broken between two standing columns mostly heaps up in its own one-cell slot.
  The columns either side hold the struck crate's wreck in place, so the crates above only drop a
  fifth of a cell on to it before breaking, and their pieces take more room loose than as crates.
  Stood in the open the same stack clears its column. Clearing a slot would need debris that can
  be crushed, or thinned out once it settles.
- The squad panel does not wrap: past about five members it runs under the action bar, which it does
  in the harness (eight).
