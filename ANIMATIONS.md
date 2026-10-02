# ANIMATIONS.md

Everything about how VCOM's characters are rigged and animated: where the animations came from,
how they are generated and baked, how the game plays them, every animation that exists, every
decision behind them with its trade-offs, what is missing, and step-by-step recipes for adding
more by hand. It is written for whoever adds the next animation, a person or a future Claude
session that has none of the context of the session that built this.

`CLAUDE.md` has the short version of the same architecture (search it for "rigged voxel figure");
this file is the long one. `README.md` has the one paragraph a player needs.

---

## Contents

1. [Quick reference](#1-quick-reference)
2. [Where the animations came from](#2-where-the-animations-came-from)
3. [The pipeline at a glance](#3-the-pipeline-at-a-glance)
4. [Coordinates, units and conventions](#4-coordinates-units-and-conventions)
5. [The rig](#5-the-rig)
6. [How the animations are generated](#6-how-the-animations-are-generated)
7. [The bake script](#7-the-bake-script)
8. [The animation tree](#8-the-animation-tree)
9. [The runtime: CharacterModel and friends](#9-the-runtime-charactermodel-and-friends)
10. [Catalogue of every animation](#10-catalogue-of-every-animation)
11. [Props](#11-props)
12. [Decisions, with their pros and cons](#12-decisions-with-their-pros-and-cons)
13. [Recipes: adding and changing animations](#13-recipes-adding-and-changing-animations)
14. [Verifying an animation](#14-verifying-an-animation)
15. [Known gaps and limitations](#15-known-gaps-and-limitations)
16. [Gotchas and troubleshooting](#16-gotchas-and-troubleshooting)
17. [Performance](#17-performance)
18. [Every file involved](#18-every-file-involved)
19. [History: how this was built](#19-history-how-this-was-built)
20. [Glossary](#20-glossary)

---

## 1. Quick reference

All commands run from `vcom/` (the Godot project), with Godot at
`C:\Program Files\Godot\Godot_v4.7-stable_win64_console.exe` (the `_console` build, so stdout is
captured). In Git Bash:

```bash
G="/c/Program Files/Godot/Godot_v4.7-stable_win64_console.exe"
cd /c/Users/tandm/Documents/Projects/VoxelXCOM/vcom
```

### Bake the character

```bash
# Rebuild Scenes/BaseCharacter.tscn, Characters/BaseCharacterBody.res and
# Characters/BaseCharacterAnimations.res from Characters/BaseCharacter.vox. Takes a few seconds.
"$G" --headless --path . --script res://Scripts/Characters/BakeCharacter.gd

# The same, naming the model and the scene to write (any model with a layout, see 13.8).
"$G" --headless --path . --script res://Scripts/Characters/BakeCharacter.gd -- res://Characters/BaseCharacter.vox res://Scenes/BaseCharacter.tscn
```

A good bake prints one line:

```
BakeCharacter: res://Characters/BaseCharacter.vox -> res://Scenes/BaseCharacter.tscn: 536 voxels on 18 bones, 552 vertices, 38 animations.
```

Bake again after **any** change to `Characters/BaseCharacter.vox`, `Scripts/Characters/VoxelRig.gd`,
`Scripts/Characters/HumanoidAnimations.gd`, `Scripts/Characters/BakeCharacter.gd`, or the rifle's
`Foregrip` marker in `Scenes/Props/Rifle.tscn`. Changes to `CharacterModel.gd`, `AimModifier.gd` and
`Postures.gd` need no bake: the scene refers to those scripts and they take effect at once.

A script error does not end a `--script` run (Godot sits idle afterwards), so when scripting it give it
a timeout: `timeout 180 "$G" --headless ...`.

If the Godot editor is open while you bake, tell it to reload `Scenes/BaseCharacter.tscn` (and any map
that is open) rather than saving it over the new one.

### Look at animations

```bash
# Render frames of clips to images, with the right props, and a contact sheet of them all.
# Needs a window: never pass --headless here.
"$G" --path . --script res://Scripts/Characters/PreviewAnimations.gd --resolution 360x400 -- stand_rifle run_rifle strike_sword

# Options: --frames N (default 6), --view three_quarter|side|front|back|top, --out <folder>,
# --scene <figure scene> (default res://Scenes/BaseCharacter.tscn).
"$G" --path . --script res://Scripts/Characters/PreviewAnimations.gd --resolution 360x400 -- crouch_rifle --view side --frames 4
```

Output goes to `user://animation_preview` unless `--out` says otherwise; on this machine that is
`C:/Users/tandm/AppData/Roaming/Godot/app_userdata/VCOM/animation_preview/`. The run prints the
folder. Each clip's frames are `<clip>_NN.png`; `sheet.png` is all of them, a row per clip in the
order given.

### Add an animation (the short version)

1. Write a pose function in `HumanoidAnimations.gd` (section 6, recipes in 13).
2. Register it in `make_library()`, and if the tree must play it, in the list that feeds the tree
   (`STANCE_POSES`, `RIFLE_POSES`, `MELEE_POSES`, `ACTS` or `REACTS`).
3. Bake.
4. Preview it with `PreviewAnimations.gd`.
5. Make `CharacterModel.gd` ask for it at the right moment, and the game code call that.
6. Drive it in a map and look (section 14).

---

## 2. Where the animations came from

### They were written, not found

Every animation in the game was written in code during one session, by Claude (Anthropic's model,
running as Claude Code) at the user's request. **No animation data came from anywhere else**: no
downloaded packs, no Mixamo, no motion capture, no asset store, nothing retargeted, and no Blender
or other DCC tool (none is installed on the machine). No web pages, tutorials or repositories were
consulted while building it. There is nothing to credit or license.

Each animation is a GDScript function in `vcom/Scripts/Characters/HumanoidAnimations.gd` that
describes, as numbers, where the feet and hands go and how the body leans over time. The bake
(`BakeCharacter.gd`) samples those functions into an ordinary Godot `AnimationLibrary`,
`vcom/Characters/BaseCharacterAnimations.res`.

The motion itself comes from general knowledge of how these movements work (how a run cycle is
built, how soldiers carry and shoulder rifles, how a throw winds up and follows through) put into
numbers and then corrected by looking at rendered frames.

### Inspirations

- **The project's own art direction.** `MagicaVoxel/CharacterInspiration/` holds the references the
  user collected:
  - `Ex_Goblin.png`, `Ex_Ogre.png`, `Ex_Skeleton.png`: chibi voxel figures with big heads and limbs
    made of separate, rigid blocks.
  - `Ex_Boy.vox` and `Ex_Girl.vox`: MagicaVoxel-style 32-cubed character templates. The base
    character (`BaseCharacter.vox`) shares their proportions and scene layout: legs two voxels square
    and nine tall, a five-wide torso, arms straight out at shoulder height, a 7x6x7 head.
  - `Ex_ADAM.vox`.
  - `Ex_Dwarves.url`, a link to <https://mrmgames.itch.io/voxel-dwarf-characters-pack>.

  These are why the rig is rigid: each voxel follows one bone, so limbs move as solid blocks, like the
  segmented figures in those images. Nothing from them was copied; they set the look to aim for.
- **XCOM 2** (and XCOM: Enemy Unknown) set the behaviour:
  - soldiers kneel behind low cover and press up to high cover;
  - they turn and aim at the target you are choosing before you confirm;
  - they step out of cover to shoot and back in;
  - overwatch has its own stance;
  - a Ranger draws a sword when Slash is chosen;
  - the dead fall as ragdolls and stay (as they did here at first; they now break apart, section 9.8).

  The game's rules were already modelled on XCOM 2, so the animations follow the same playbook.
- **Classic animation principles:**
  - anticipation before a strike or throw (the wind-up);
  - follow-through after it;
  - squash on landing;
  - breathing and weight drift in idles;
  - the head held steadier than the torso;
  - a run built from contact, push-off, flight and recovery.
- **Standard techniques** for procedural character animation:
  - analytic two-bone inverse kinematics (law of cosines with a pole vector);
  - procedural gait (a foot planted on the ground while in contact, swung through an arc otherwise);
  - additive animation layering;
  - one-bone rigid skinning for segmented models;
  - ragdolls through Godot's `PhysicalBoneSimulator3D` and `PhysicalBone3D` on Jolt (since replaced by
    breaking the figure apart, section 9.8).

### How the list of animations was chosen

Not from a template. The game's code was read for every moment a unit does something, and each got
what it needs to be seen doing:

| In the game | What it needed | Animations |
|---|---|---|
| `Unit.walk()` / `start_walk()` (Move, enemy moves, `Reactions.walk()`) | a run that keeps pace with the tween, including slow motion and holds | `run_rifle`, `run_melee`, `run_unarmed` |
| `CombatGrid.MAX_CLIMB` 1 and `MAX_DROP` 2 (a step can climb or drop) | a hop | `hop` (pose), plus a lift arc |
| `ShootAction`, `ShotPlayback` (player shots, enemy shots, reactions) | aim at the target, the kick, step out and back with the gun up | `aim_rifle`, `fire_rifle`, `back_rifle`, `strafe_left_rifle`, `strafe_right_rifle` |
| `OverwatchAction` / `Unit.overwatching` | an overwatch stance | `overwatch_rifle`, `overwatch_crouch_rifle` |
| `StrikeAction` / `Unit.strike()` | a guard, a swing whose impact the blow lands on, drawing and stowing a sword a rifleman carries | `ready_melee`, `strike_sword`, `draw_sword`, `stow_sword` |
| `ThrowGrenadeAction` / `Unit.throw_at()` | holding a grenade ready, a throw whose release the grenade leaves at | `ready_throw_*`, `throw_*` |
| `Unit.take_damage()` | a flinch on a hit, a duck on a miss | `hit_front`, `hit_back`, `dodge` |
| `Unit.die()` | a death | breaking apart into voxel debris, not an animation (section 9.8; a ragdoll at first) |
| `Unit.drop_to()` (the floor broke) | a fall and a landing | `fall` (pose), `land` |
| `TurnManager` deciding the battle | the winners cheering | `cheer_*` |
| `LineOfSight.cover_at()` (cover beside the tile) | kneeling behind low cover, bracing at high | `crouch_*`, `wall_*` |
| Standing about | an idle | `stand_*` |

Items decide the three versions of most of these: a unit with a gun is in the **rifle** stance, one
with a melee weapon and no gun in the **melee** stance, one with neither **unarmed**
(`Item.GUN`, `Item.MELEE` tags; see `CharacterModel.equip()`).

### Questions asked before building, and the answers

Before any code was written, four decisions were put to the user:

| Question | Options offered | Answer |
|---|---|---|
| Props: the items had no 3D models. Should the rig hold and wear the gear? | Placeholder props (recommended) / Empty hands / Sockets only | **Placeholder props**: simple `.vox` models for the Rifle, Shortsword and Frag Grenade, repaintable in MagicaVoxel; the gun held two-handed, the sword drawn for a Strike and slung otherwise, grenades on the belt until thrown. |
| Run speed: the squad moved at 0.12 s a tile (about 8 tiles a second) and enemies at 0.2. | 0.2 s for both (recommended) / Keep 0.12 and 0.2 / 0.25 s for both | **0.2 s for both**: about 5 strides a second, a brisk run that reads. `MoveAction.seconds_per_step` went from 0.12 to 0.2. |
| What happens to a unit that dies? | Fall and stay (recommended) / Fall, then fade / Ragdoll | **Ragdoll**: physics takes over at death; blasts fling bodies; they tumble off ledges. Bodies stay for the battle. Later replaced: the dead break apart into chunks (section 9.8). |
| Should units take cover visually, as in XCOM? | Cover stances (recommended) / Stand, face enemy / Stand, keep facing | **Cover stances**: an idle unit turns to the cover that faces its nearest enemy, kneeling behind half cover, bracing at full cover; in the open it faces that enemy. |

Everything else was decided along the way. Those decisions are in section 12.

### How they were checked

The animations could not be watched while being written, so every one was checked by rendering
Godot frames to images and looking at them, from the side, the front, three-quarters and the game's
own camera, laid out as contact sheets. Several first attempts were wrong and fixed that way:

- **The kneel was a squat.** The kneeling knee was being bent toward a forward-and-up pole; it
  needed to point down and forward to touch the floor (`_crouch`'s `Vector3(0, -1, 0.7)`).
- **The cheer's fists were inside the head.** The head is wider than the shoulders, so the fists
  moved out to ±6.5 voxels.
- **The dead stood stiffly for a third of a second.** A balanced ragdoll on flat feet resists a light
  push. The knock went up and the shins were kicked the other way (`KNOCK_SHARES`). The ragdoll has
  since gone: the dead break apart (section 9.8).
- **The two-handed rifle hold was out of reach.** These arms reach only 8 voxels to the palm, which
  decided where the rifle sits: under the chin with the off hand on the magazine (section 6.9).
- **The hit flinch was too faint** at the game's zoom, so it was made about 1.6 times stronger. It is
  still subtle.

Then the whole thing was driven through real game actions in the maps: shots, kills, strikes,
throws, an enemy turn with overwatch reactions, drops off broken crates, hops, step-outs, the
victory cheer. Three seeded headless auto-battles were played to the end with no script errors.
Section 14 has how to repeat that.

---

## 3. The pipeline at a glance

```
 MagicaVoxel                       bake time (BakeCharacter.gd, by hand)                        run time
 -----------                       -----------------------------------------                    --------

 BaseCharacter.vox ──► VoxelRig.gd ──► Skeleton3D (18 bones, unrotated T-pose)
   536 voxels,           layout:       Body: one skinned ArrayMesh (552 vertices,               Unit (rules) ──► CharacterModel.gd
   one colour            joints +        every vertex wholly one bone) ──► <model>Body.res        tells it what      drives the tree,
                         regions                                                                   happens            faces, hops, props,
                                         │                                                                            breaks apart on death
 Scenes/Props/Rifle.tscn ─(Foregrip)─► HumanoidAnimations.gd                                    Postures.gd ──────► settle(cover, yaw)
                                         poses as functions of time, IK ──► AnimationLibrary      (map node)
                                         (38 clips) ──► <model>Animations.res                   AimModifier.gd ───► bends spine/chest,
                                         AnimationNodeBlendTree (the tree)                        (on the skeleton)    turns the head
                                         │
                                       BakeCharacter.gd ──► Scenes/BaseCharacter.tscn
                                         sockets (BoneAttachment3Ds), AnimationPlayer,
                                         AnimationTree, CharacterModel script on the root
```

- **VoxelRig** (`Scripts/Characters/VoxelRig.gd`) knows the humanoid skeleton and each model's
  layout. It shares the model's voxels out between bones, meshes them, and builds the skeleton.
- **HumanoidAnimations** (`Scripts/Characters/HumanoidAnimations.gd`) authors every animation for a
  rig, and the blend tree that plays them.
- **BakeCharacter** (`Scripts/Characters/BakeCharacter.gd`) runs both and writes the scene and the
  two resources.
- **CharacterModel** (`Scripts/Characters/CharacterModel.gd`), the scene's root script, plays it all
  at run time. It watches its unit, takes requests from it, carries props, and breaks apart when its
  unit dies.
- **AimModifier** (`Scripts/Characters/AimModifier.gd`) is a `SkeletonModifier3D` that bends the
  upper body to aim up or down and turns the head.
- **Postures** (`Scripts/Characters/Postures.gd`) is a node in each combat map that settles idle
  figures into cover or turns them to the nearest enemy.
- **PreviewAnimations** (`Scripts/Characters/PreviewAnimations.gd`) renders clips to images.

The rules never read any of it. A unit is still its tile and its two cells. The figure decides only
*when* a few things happen, never *what*: a shot fires once the gun is up, a strike lands at the
swing's impact, a grenade leaves at the throw's release. A unit without a figure plays the same game,
at once. (`CLAUDE.md`, "Combat rules that must not drift", has this as a rule.)

---

## 4. Coordinates, units and conventions

Getting these wrong is the most common way to break a pose, so they come first.

### Three coordinate systems

| System | Axes | Unit | Origin | Used for |
|---|---|---|---|---|
| **Model voxels** (MagicaVoxel's own) | x across, y depth (the face looks toward **-y**), **z up** | 1 voxel | the model box's corner | the layout's `regions`; what MagicaVoxel shows |
| **Rig voxels** | Godot's axes: **x to the figure's left**, **y up**, **z forward** (the figure faces **+z**) | 1 voxel | under the middle of the figure, on its lowest voxel | joints, every pose, every animation, prop item space |
| **Godot units** | the same axes | 1 cell = 1 tile = 1 metre to the physics | the figure's root | the baked scene, the skeleton, the game |

A model voxel `(x, y, z)` becomes the rig cell `(x, z, -y)`, then is centred: the cell's lowest corner
lands at `(x - cx, z - z0, -y + cy - 1)` in rig voxels, where `cx` and `cy` are the middle of the
model's voxels across and front to back, and `z0` the lowest. That is `VoxelRig._corner` (with
`cx = 16.5`, `cy = 16`, `z0 = 0` for the base character). This is the same turn the MagicaVoxel
importer makes (`vox_to_godot = Basis(RIGHT, FORWARD, UP)`), so the figure faces the way Godot's
`MODEL_FRONT` does.

### Scale

- **0.063 Godot units a voxel** (`VoxelRig.BASE_CHARACTER["scale"]`): what the plain import of the
  model used, so the figure stands 27 × 0.063 = **1.701** cells tall. Blocks use 0.0625; the figure
  is a hair larger, and props use 0.063 to match it.
- **A tile is 1 Godot unit, about 15.87 voxels.**
- The figure's rest box (arms out) is 1.575 wide, 1.701 tall and 0.378 deep (the head's depth).

### Rotations

Every bone rests **unrotated**, lined up with the model's axes, at the T-pose the model was drawn in.
So a rotation means the same thing on every bone. Signs, all right-handed:

| Rotation | Upright bone (spine, neck, head) | Hanging leg (thigh, shin) | Arm in the T-pose |
|---|---|---|---|
| **+x** tips +y toward +z | leans **forward** (head: looks down) | swings **back** (a positive shin turn bends the knee) | — |
| **+y** turns +z toward +x | turns to the figure's **left** | turns out or in | right arm (-x) toward **+z** (forward); left arm forward is **-y** |
| **+z** tips +y toward -x | leans to the figure's **right** | — | right arm (-x) **down** is +90; left arm (+x) down is -90 |

`Pose.turn(bone, Vector3(x, y, z))` takes degrees and builds the rotation with
`Quaternion.from_euler()`, Godot's default **YXZ** order: yaw first, then pitch about the turned x,
then roll. It **replaces** the bone's rotation; it does not add to it.

A thigh swinging *forward* is a **negative** x turn. A shin bending at the knee is **positive** x.
Head pitch down is positive x. Easy to get backwards.

### Time

Seconds throughout. Loops are sampled over `[0, length]`, with the last key equal to the first, so a
pose function for a loop must be periodic over its length (use `sin(TAU * time / period)` with the
period dividing the length).

### Names

- Bones use Godot's `SkeletonProfileHumanoid` names: `Hips`, `Spine`, `Chest`, `LeftUpperArm` and
  so on, plus `Root`.
- Clips are `snake_case`. A stance-specific clip ends in its stance: `stand_rifle`, `crouch_melee`,
  `throw_unarmed`.
- Animation tracks are `Skeleton3D:<Bone>`, relative to the figure's root.

---

## 5. The rig

### Bones

Eighteen bones, parent before child, from `VoxelRig.BONES`. Joints are in rig voxels; "offset" is
the bone's rest position from its parent's joint; "voxels" is how many of the base character's
voxels move with it.

| # | Bone | Parent | Joint (rig voxels) | Offset | Voxels | What it is |
|---|---|---|---|---|---|---|
| 0 | `Root` | — | (0, 0, 0) | — | 0 | the floor under the figure; moved by the strike's lunge |
| 1 | `Hips` | Root | (0, 9, 0) | (0, 9, 0) | 30 | pelvis, 5x3x2; moved for bob, crouches, weight shifts |
| 2 | `Spine` | Hips | (0, 12, 0) | (0, 3, 0) | 30 | lower torso, 5x3x2 |
| 3 | `Chest` | Spine | (0, 15, 0) | (0, 3, 0) | 40 | upper torso to the shoulders, 5x4x2; arms and rifle poses ride on it |
| 4 | `Neck` | Chest | (0, 19, 0) | (0, 4, 0) | 2 | one voxel column |
| 5 | `Head` | Neck | (0, 20, 0) | (0, 1, 0) | 286 | the 7x7x6 head (over half the voxels) |
| 6 | `LeftUpperArm` | Chest | (3.5, 18, 0) | (3.5, 3, 0) | 20 | 5x2x2 |
| 7 | `LeftLowerArm` | LeftUpperArm | (7.5, 18, 0) | (4, 0, 0) | 12 | forearm, 3x2x2 |
| 8 | `LeftHand` | LeftLowerArm | (10.5, 18, 0) | (3, 0, 0) | 4 | 2x1x2, the upper half of the arm's thickness |
| 9 | `RightUpperArm` | Chest | (-3.5, 18, 0) | (-3.5, 3, 0) | 20 | |
| 10 | `RightLowerArm` | RightUpperArm | (-7.5, 18, 0) | (-4, 0, 0) | 12 | |
| 11 | `RightHand` | RightLowerArm | (-10.5, 18, 0) | (-3, 0, 0) | 4 | |
| 12 | `LeftUpperLeg` | Hips | (1.5, 9, 0) | (1.5, 0, 0) | 16 | thigh, 2x4x2 |
| 13 | `LeftLowerLeg` | LeftUpperLeg | (1.5, 5, 0) | (0, -4, 0) | 16 | shin, 2x4x2 |
| 14 | `LeftFoot` | LeftLowerLeg | (1.5, 1, 0) | (0, -4, 0) | 6 | 2x1x3, toes forward |
| 15 | `RightUpperLeg` | Hips | (-1.5, 9, 0) | (-1.5, 0, 0) | 16 | |
| 16 | `RightLowerLeg` | RightUpperLeg | (-1.5, 5, 0) | (0, -4, 0) | 16 | |
| 17 | `RightFoot` | RightLowerLeg | (-1.5, 1, 0) | (0, -4, 0) | 6 | |

That is 536 voxels in all. The shoulder joints sit **one voxel in from where the arm meets the body**
(the torso spans x -2.5 to 2.5, the joints are at ±3.5). With the pivot there, a lowered arm hangs
flush beside the torso instead of sinking into it.

What the proportions mean for animating:

- **Arm:** upper arm 4 voxels, forearm 3, palm centre 1 more: **8 voxels from shoulder to palm**.
- **Leg:** thigh 4, shin 4: **8 voxels from hip to ankle**. The ankle is 1 voxel above the floor.
- **Shoulders** at x ±3.5, y 18. **Hips** at x ±1.5, y 9.
- **Palm centres** at (∓1, 0.5, 0) in each hand's own space: the middle of the hand's voxels
  (`VoxelRig.bone_box`).

### The layout

A model's layout is a dictionary in `VoxelRig.gd`. The base character's is `BASE_CHARACTER`:

- `"scale"`: Godot units a voxel (0.063).
- `"joints"`: bone → joint in rig voxels (the table above).
- `"regions"`: `[bone, lowest corner, highest corner]`, inclusive, in **model voxel coordinates**
  (MagicaVoxel's, z up). The first region that holds a voxel takes it. The order matters: the head
  and arms are tested before the chest, so the chest's full-width box only gets what is left.

```gdscript
[&"Head", Vector3i(0, 0, 20), Vector3i(255, 255, 255)],       # z 20 and up
[&"Neck", Vector3i(0, 0, 19), Vector3i(255, 255, 19)],
[&"RightHand", Vector3i(0, 0, 17), Vector3i(5, 255, 18)],     # the arm rows are z 17-18
[&"RightLowerArm", Vector3i(6, 0, 17), Vector3i(8, 255, 18)],
[&"RightUpperArm", Vector3i(9, 0, 17), Vector3i(13, 255, 18)],
[&"LeftHand", Vector3i(27, 0, 17), Vector3i(255, 255, 18)],
[&"LeftLowerArm", Vector3i(24, 0, 17), Vector3i(26, 255, 18)],
[&"LeftUpperArm", Vector3i(19, 0, 17), Vector3i(23, 255, 18)],
[&"Chest", Vector3i(0, 0, 15), Vector3i(255, 255, 18)],
[&"Spine", Vector3i(0, 0, 12), Vector3i(255, 255, 14)],
[&"Hips", Vector3i(0, 0, 9), Vector3i(255, 255, 11)],
[&"RightUpperLeg", Vector3i(0, 0, 5), Vector3i(16, 255, 8)],  # x 14-15 is the right leg, 17-18 the left
[&"LeftUpperLeg", Vector3i(17, 0, 5), Vector3i(255, 255, 8)],
[&"RightLowerLeg", Vector3i(0, 0, 1), Vector3i(16, 255, 4)],
[&"LeftLowerLeg", Vector3i(17, 0, 1), Vector3i(255, 255, 4)],
[&"RightFoot", Vector3i(0, 0, 0), Vector3i(16, 255, 0)],
[&"LeftFoot", Vector3i(17, 0, 0), Vector3i(255, 255, 0)],
```

A voxel no region takes goes to the bone whose joint is nearest, and the bake warns
(`VoxelRig: N voxels are in no region; ...`). A clean bake prints no warning. The regions were
found by printing the model as text, a front view and a side view of which voxels are filled, to see
where the legs, torso, arms and head are.

### The mesh

`VoxelRig.make_mesh()` writes one `ArrayMesh`, one surface:

- Each bone is meshed on its own. A face between two voxels of the **same** bone is left out, as
  the plain importer does; a face between voxels of **different** bones is **kept**, since a joint
  that bends opens it up. So a bent elbow shows the end of each block rather than a hole.
- Faces are merged greedily into rectangles of one colour (per bone, per face direction, per slice).
- Every vertex has bone weights `[bone, 0, 0, 0]` / `[1, 0, 0, 0]`: wholly one bone. Nothing ever
  stretches.
- Winding is clockwise seen from outside (Godot's front face), checked per quad.
- The vertex colours are the model's palette, on a vertex-colour material. In play every unit puts a
  flat-colour `body_material` over it (section 9), so the vertex colours only show in the editor
  and the preview tool (the base character is all one grey anyway).

The base character becomes 552 vertices. The skin is `Skeleton3D.create_skin_from_rest_transforms()`,
saved with the scene.

### No ragdoll

Until 2026-10-02 the bake gave every figure a ragdoll: a `PhysicalBoneSimulator3D` named `Ragdoll`
under the skeleton, 12 `PhysicalBone3D` boxes (hands, feet and head riding on the forearm, shin and
neck) with cone joints, 40 kg in all, inactive and on no physics layer until death. The dead now
break apart into voxel debris instead (section 9.8), which needs nothing baked, so
`VoxelRig.make_ragdoll()`, `RAGDOLL` and `RAGDOLL_MASS` went with it. Git history has them, with the
table of bodies, joints and masses, should a ragdoll be wanted again.

### The sockets

`BakeCharacter._sockets()` puts `BoneAttachment3D`s under the skeleton, with `Node3D` sockets under
them. A prop is put **at** a socket with an identity transform, so the socket is where the prop's
grip goes and how it is turned. Origins below are in voxels in the bone's own space.

| Socket | Bone | Origin | Prop +z (forward) | Prop +y (up) | Scale | Holds |
|---|---|---|---|---|---|---|
| `RightHand/RifleGrip` | RightHand | (-1, 0.5, 0) | (-1, 0, 0): along the hand, as a pistol's barrel runs on from the forearm | (0, 1, 0) | 1 | the gun in hand |
| `RightHand/SwordGrip` | RightHand | (-1, 0.5, 0) | (0, 0, 1): out of the fist on the thumb side | (0, 1, 0) | 1 | the sword in hand |
| `LeftHand/GrenadeGrip` | LeftHand | (1, 0.5, 0) | (0, 0, 1) | (0, 1, 0) | 1 | a grenade being thrown |
| `Back/RifleSlot` | Chest | (-1.25, -0.6, -2.6) | (0.51, 0.86, 0): up to the left shoulder | (0.86, -0.51, 0) | 1 | the gun, slung while the sword is out |
| `Back/SwordSlot` | Chest | (-2.5, 4.0, -2.2) | (0.45, -0.89, 0): hilt over the right shoulder, blade down to the left | (-0.89, -0.45, 0) | 1 | the sword, slung while the gun is out |
| `Belt/Grenade1` | Hips | (2.2, 1.5, -2.1) | (0, 0, 1) | (0.42, 0.91, 0): leaning 25° out to the left | 0.8 | stick grenades tucked into the back of the belt by their handles, heads up |
| `Belt/Grenade2` | Hips | (-2.2, 1.5, -2.1) | (0, 0, 1) | (-0.42, 0.91, 0): leaning 25° out to the right | 0.8 | |
| `Belt/Grenade3` | Hips | (0, 1.5, -2.7) | (0, 0, 1) | (0, 1, 0) | 0.8 | |

The three grip transforms come from `HumanoidAnimations` (`rifle_grip`, `sword_grip`, `grenade_grip`),
so the sockets and the poses that put hands on props always agree. The back and belt slots are
`BakeCharacter.SLOTS`; the belt's 0.8 is `BakeCharacter.BELT_SCALE`, so three grenades fit. Side by
side and upright, the stick grenades' heads made one solid band across the back with the handles
hanging under it like a kilt; fanned out, the three heads stand apart. The grip socket holds a stick
grenade mid-handle with its head out of the back of the hand, which reads as gripping the handle
through the whole throw.

### The unit's bodies

The figure shapes its unit's physics bodies (`Unit._add_bodies()`), neither of which turns with it:

- **Click body**: an upright `CylinderShape3D` of radius `Unit.PICK_RADIUS` (0.3) and the figure's
  height, on `Unit.PICK_LAYER`. Before the rig it was the convex hull of the T-posed mesh, arms out.
- **Debris capsule**: as before, as thick as the figure's body (0.189 radius, from the rest box's
  depth), starting `Unit.BODY_CLEARANCE` above the feet.

---

## 6. How the animations are generated

All of this is `Scripts/Characters/HumanoidAnimations.gd`.

### 6.1 Pose functions

Every animation is a function `(time: float, …) -> Pose`. A `Pose` (an inner class) holds every
bone's local rotation and two offsets:

| `Pose` member | What it is |
|---|---|
| `rotations` | bone → `Quaternion`, the bone's rotation relative to its parent (starts at identity for all) |
| `root` | offset of the `Root` bone from where it rests, in rig voxels (the strike's lunge) |
| `hips` | offset of `Hips` from where they rest, in the root's space (bob, crouch, weight shift) |
| `turn(bone, degrees)` | sets a bone's rotation from Euler degrees (YXZ); replaces, does not add |
| `move(root, hips)` | sets both offsets |
| `at(bone) -> Transform3D` | where the bone is and how it is turned, in the model's space, worked out down the chain from the root (cached until anything changes) |
| `face(bone, basis)` | turns a bone so it ends up turned `basis` in the model's space |
| `reach(upper, lower, end, target, pole, hinge_at_rest, effector, end_basis)` | the two-bone IK (6.2) |

A pose function normally:

1. Moves the hips (`pose.move`) and turns them and the torso (`_torso`).
2. Plants the feet (`_foot`, `_ankle`).
3. Puts the hands where they go, or on whatever they hold (`_hand`, `_hold`, `_rifle`, `_carry`).
4. Adjusts the head.

Order matters: hands placed relative to the chest must come **after** the torso is turned, because
`pose.at(&"Chest")` reads the torso's current rotation.

The standing idle in full:

```gdscript
## Standing about, breathing.
func _stand(time: float, stance: StringName) -> Pose:
	var pose := _pose()
	var breath := sin(TAU * time / 2.4)
	var drift := sin(TAU * time / 4.8)
	pose.move(Vector3.ZERO, Vector3(0.2 * drift, -0.5 + 0.15 * breath, 0.0))
	pose.turn(&"Hips", Vector3(0, -8.0 + drift * 2.0, 0))
	_torso(pose, 4.0 + breath * 1.2, 8.0 - drift * 2.0, 0.0, 0.5)
	pose.turn(&"Head", Vector3(-2.0, drift * 6.0, 0))
	_foot(pose, &"Left", _ankle(Vector3(2.0, 0, 1.2)), 8.0)
	_foot(pose, &"Right", _ankle(Vector3(-2.0, 0, -0.8)), -14.0)
	_carry(pose, stance, breath)
	return pose
```

That reads: breathe every 2.4 s and drift the weight every 4.8 s; hips half a voxel down and bobbing
0.15 with the breath; hips turned 8° to the right with the torso turned back 8° (a bladed stance);
lean 4° forward plus the breath; head slightly up and wandering ±6°; left foot forward and out,
right foot back and out; hold whatever the stance holds.

### 6.2 The two-bone IK

`Pose.reach()` bends a limb (upper, lower, end bone) so a point on the end bone (the **effector**,
in the end bone's own space) lands on a **target** in the model's space, with the middle joint (elbow
or knee) toward a **pole** direction.

1. **Lengths.** `L1` is the upper bone (the offset to the lower bone's joint). `L2` is the lower bone
   plus the effector: with `end_basis` given, the end bone's orientation is known, so the solver
   aims the end bone's *joint* at `target - end_basis * effector` and `L2` is just the lower bone;
   without it, the end bone carries straight on, so the effector is folded into the lower span.
2. **The elbow, by the law of cosines.** With `d` the distance to the goal (clamped so the triangle
   exists), the middle joint is `along = (L1² - L2² + d²) / 2d` along the line to the goal and
   `out = √(L1² - along²)` off it, toward the pole's part square to that line.
3. **Out of reach** leaves the limb straight toward the target, `d` clamped to `L1 + L2 - 0.001`.
4. **Twist.** Each segment's rotation maps a frame (the segment's rest direction, the limb's rest
   hinge axis) to (its new direction, the new hinge axis), the hinge being
   `(elbow - shoulder) × (end - elbow)`. The rest hinges are constants:
   - `ELBOW_RIGHT` = +y and `ELBOW_LEFT` = -y: in the T-pose an elbow bends the forearm forward.
   - `KNEE` = +x: a knee bends the shin back.

   This fixes the limb's roll, so a square voxel limb does not spin about its length. With the limb
   straight, the hinge comes from the pole (`side × toward`).
5. **The end bone** is turned to `end_basis` if given, else left straight (identity) on the forearm or
   shin.
6. The results are written as local rotations: upper relative to its parent's current global
   rotation, lower relative to the upper, end relative to the lower.

Poles in use:

| Limb | Typical pole | Why |
|---|---|---|
| leg (`_foot` default) | the foot's yaw applied to +z, plus a little up | knee over the toes |
| kneeling leg (`_crouch`) | `Vector3(0, -1, 0.7)` | knee down to the floor |
| right arm holding the rifle (`_rifle` default) | `Vector3(-1, -1, -0.3)` | elbow down and out to the right, a touch back |
| left arm on the rifle (`_rifle` default) | `Vector3(1, -1, 0)` | elbow down and out to the left |
| aim and step poses | right `(-1.2, -1, 0)`, left `(1, -1, 0)` | elbows down and out |
| hanging and pumping arms | `(±0.3 to 0.6, 0 to -0.2, -1)` | elbows back |

A pole on the wrong side twists the limb 180° or bends it the wrong way; see section 16.

### 6.3 The helpers

| Helper | What it does |
|---|---|
| `_foot(pose, side, ankle, yaw, pitch, knee)` | IK the leg so the ankle is at `ankle`, the foot turned `yaw`° out and pitched `pitch`° toes down; `knee` overrides the pole |
| `_ankle(on_floor)` | the ankle position over a floor point, for a flat foot: the point plus the ankle's height (1 voxel) |
| `_hand(pose, side, palm, pole, basis)` | IK the arm so the **palm centre** is at `palm`; the hand turned `basis` if given, else straight on from the forearm |
| `_hold(pose, side, item, grip, pole)` | IK the arm so a prop held through `grip` ends up at `item` (its grip point and orientation): the hand goes to `item * grip.inverse()` |
| `_item(grip, forward, up)` | a prop's transform: its grip at `grip`, its +z along `forward`, its +y toward `up` (`Basis.looking_at(forward, up, true)`) |
| `_rifle(pose, rifle_in_chest, right_pole, left_pole)` | the rifle in both hands: placed relative to the **chest** (so it rides the body), the right hand on its grip, the left palm on `rifle_foregrip` |
| `_low_ready()` | the rifle carried: grip at chest (-1.5, -0.5, 3), muzzle down and to the left `(0.55, -0.35, 0.75)` |
| `_shouldered()` | the rifle aimed: grip at chest (0, 2, 4.3), muzzle straight ahead |
| `_torso(pose, lean, turn, tilt, steady)` | shares a lean (forward), turn (left) and tilt (right) between spine (45/40/50%) and chest (55/60/50%), and turns the neck and head back by `steady` of it so the head looks where it was |
| `_carry(pose, stance, sway, left_free)` | what the hands do at rest per stance: rifle at low ready (or one-handed, muzzle down by the hip, if `left_free`), sword low at the right side, or empty hands hanging; `sway` bobs them with the breath |

"Chest space" means the `Chest` bone's own frame: origin at the chest joint (rig (0, 15, 0) at rest),
turning with the torso. "Hip space" is the same for `Hips` (rig (0, 9, 0)).

### 6.4 Prop grips

Set in `HumanoidAnimations._init()` from the rig, in voxels in the hand's own space:

- **`rifle_grip`**: `Transform3D(Basis(UP, -90°), right palm)`. The rifle's +z (barrel) runs along
  the right hand's length (-x), its top up the back of the hand.
- **`sword_grip`**: `Transform3D(identity, right palm)`. The blade stands out of the fist on the
  thumb side (+z), its edges up and down the hand.
- **`grenade_grip`**: `Transform3D(identity, left palm)`.
- **`rifle_foregrip`**: read from `Scenes/Props/Rifle.tscn`'s `Foregrip` marker (`read_rifle()`),
  (0, 1, 3) in the rifle's own voxels: under the receiver, just behind the fore-end. Move the
  marker, rebake, and the left hand follows.

### 6.5 Time: sine waves and keyframe tables

- **Loops** are driven by sine waves of the time: breathing (`sin(TAU * t / 2.4)`), drift, scanning,
  bounces. Every period divides the clip's length so the loop closes.
- **One-shots** are keyframe tables: arrays of `[time, value, value…]` eased by `_keyed(keys, time)`.
  `_keyed` finds the two keys around the time and `lerp`s between them with `smoothstep`, so every
  key is a gentle stop. Values may be floats or vectors. The strike and the throw are built this way
  (section 10 has their tables).
- **Reactions** are shaped by a rise and a decay: `smoothstep(0, rise, t) * (1 - smoothstep(a, b, t))`,
  a quick jolt that eases off.
- **The run** is a gait formula, `_stride(phase, x)`, for each foot, half a cycle apart:
  - **Stance**, the first 27% of the cycle from touchdown: the foot is planted. In the model's space
    it sweeps back from `+reach` to `-reach` as the ground goes by:
    `reach = cycle × RUN_SPEED / scale × 0.27 × 0.5` = **4.29 voxels**. Late in the stance the heel
    lifts up to 1.2 voxels and the toes pitch down to 35°.
  - **Swing**: the foot kicks up behind and swings forward to 1.1 × reach. Its height is
    `sin(π u) × 4.2 + sin(π min(2u, 1)) × 1.2`, and its pitch eases from 35° to -15°.
  - The hips are lowest at mid-stance and highest in flight:
    `-1.4 + 0.55 × -cos(2π · 2(phase - 0.135))`.

### 6.6 Sampling and the tracks

`_loop(length, fn)` and `_once(length, fn, only)` call `_sample()`:

- **30 samples a second** (`FPS`), at `t = length × i / n` for `i` from 0 to `n` inclusive
  (`n = ceil(length × 30)`).
- A **rotation track** (`TYPE_ROTATION_3D`) per bone keyed, path `Skeleton3D:<Bone>`.
- **Position tracks** (`TYPE_POSITION_3D`) for `Root` and `Hips` when they are keyed, valued
  `(rest offset + pose offset) × scale` in Godot units.
- Each rotation key is **flipped to the same hemisphere as the last** (q and -q are the same turn, but
  blending between opposite signs swings the long way round).
- `Animation.optimize(0.005, 0.005)` then drops keys a straight blend between their neighbours would
  give anyway, which took the library from 855 KB to 384 KB.
- Loops get `LOOP_LINEAR`; one-shots stay `LOOP_NONE`.
- `only` limits the bones keyed. Additive clips key only what they move.

### 6.7 Additive clips

The reactions (`fire_rifle`, `hit_front`, `hit_back`, `dodge`, `land`) are **changes**, not poses.
Their functions return rotations measured from **identity** (the rest), and they key only the bones
they move:
- `fire_rifle`, `hit_front`, `hit_back` and `dodge` key `UPPER_BODY` (`Spine`, `Chest`, `Neck`, `Head`);
- `land` keys `UPPER_BODY + LEGS` (with the `Hips` position).

The tree adds them on top of whatever the body is doing (a one-shot in **ADD** mode). Because every
bone rests unrotated, a clip's rotation *is* its change. So the same flinch works standing, kneeling,
aiming or mid-run. The rifle kicks with a shot because the arms holding it ride on the chest the
recoil turns.

### 6.8 Metadata

Moments the game waits on are stored on the clips (`Animation.set_meta`) and read by `CharacterModel`
(`_moment(clip, marker)` and `_ready()`):

| Clip | Meta | Value | Read for |
|---|---|---|---|
| `run_rifle`, `run_melee`, `run_unarmed` | `speed` | 5.0 (tiles a second) | `run_scale` = actual speed / this |
| `strike_sword` | `impact` | 0.27 s | `Unit.strike()` rolls and deals damage then |
| `throw_rifle`, `throw_melee`, `throw_unarmed` | `release` | 0.36 s | the grenade leaves the hand then |
| `draw_sword` | `swap` | 0.17 s | the sword comes into the hand, the gun goes on the back |
| `stow_sword` | `swap` | 0.2 s | the reverse |

Change a moment in **both** places, the key table and the `set_meta` line in `make_library()`.

### 6.9 What the proportions forced

These chibi arms reach only 8 voxels from shoulder to palm; the rifle is 18 long. Holding it in both
hands therefore only works with:

- **The aim** centred **under the chin**: grip at rig (0, 17, 4.3), the stock tucked into the chest
  (it overlaps the chest by about a voxel), the muzzle 19.5 voxels (1.23 cells) up.
- **The off hand under the receiver** (the `Foregrip` marker at the rifle's (0, 1, 3)), not out on
  the fore-end, which neither hand could reach in an aim.
- **The carried rifle** angled muzzle down and **to the left**, `(0.55, -0.35, 0.75)`, which brings
  its front end toward the left shoulder.

Where a target is still out of reach the IK leaves the arm straight toward it, and the palm can stop
up to about a voxel short. At 1.5 pixels a voxel at default zoom that hardly shows. Any new pose that
holds the rifle should be checked from the side and the front for this.

---

## 7. The bake script

`vcom/Scripts/Characters/BakeCharacter.gd`, a `SceneTree` script run with `--script`, like
`BakeLand.gd`.

### Why it exists

- **The model is drawn in MagicaVoxel, which cannot rig or animate.** Something has to turn the
  voxels into a skinned, rigged, animated scene, and there is no Blender.
- **The plain importer cannot do it.** It makes a single mesh with greedy faces that span bones, so
  a face cannot be split by bone. Rigid skinning needs each bone meshed on its own (section 5).
- **Hand-writing a rigged scene is error-prone** (CLAUDE.md: do not hand-write `Transform3D`s), and
  so is keying 38 animations by hand.
- **Animations depend on the model's proportions** (IK targets, hip heights), so they have to be
  generated *for* the rig. One command regenerates all of it consistently whenever the model, the
  rig or the animation code changes.

### What it does, step by step

1. Reads the arguments: `[vox] [scene]`, defaulting to `res://Characters/BaseCharacter.vox` and
   `res://Scenes/BaseCharacter.tscn`.
2. Looks the model's layout up in `LAYOUTS`, which is `VoxelRig.LAYOUTS` (fails if there is none).
3. `VoxelRig.load_vox()` reads the voxels with the MagicaVoxel importer addon's own reader
   (`vox-importer-common.gd`) and shares them out by the layout.
4. Makes the root `Node3D`, named after the model, with `CharacterModel.gd` as its script and its
   `voxel_model` set to the model's path, which blood reads the figure's voxels by (section 9.12).
5. `make_skeleton()`, then the `Body` `MeshInstance3D` with `make_mesh()`, saved as
   **`<model>Body.res`** beside the model, with its skin.
6. Adds `Aim`, a `SkeletonModifier3D` with `AimModifier.gd`.
7. Builds `HumanoidAnimations` for the rig, reads the rifle's foregrip from `RIFLE_SCENE`
   (`res://Scenes/Props/Rifle.tscn`), and adds the sockets (section 5).
8. `make_library()`, saved as **`<model>Animations.res`** beside the model, put on an
   `AnimationPlayer` as its default library (`""`).
9. An `AnimationTree` with `make_tree()` as its root, `anim_player` = `../AnimationPlayer`, active.
10. Sets every node's `owner` to the root and packs and saves the scene.
11. Prints the summary line.

The resulting scene:

```
BaseCharacter (Node3D)                         CharacterModel.gd
  Skeleton3D (Skeleton3D)                      18 bones, rest = T-pose
    Body (MeshInstance3D)                      BaseCharacterBody.res, skin from the rest
    Aim (SkeletonModifier3D)                   AimModifier.gd
    RightHand (BoneAttachment3D → RightHand)
      RifleGrip, SwordGrip (Node3D)
    LeftHand (BoneAttachment3D → LeftHand)
      GrenadeGrip (Node3D)
    Back (BoneAttachment3D → Chest)
      RifleSlot, SwordSlot (Node3D)
    Belt (BoneAttachment3D → Hips)
      Grenade1, Grenade2, Grenade3 (Node3D, scale 0.8)
  AnimationPlayer (AnimationPlayer)            library "" = BaseCharacterAnimations.res
  AnimationTree (AnimationTree)                the blend tree, embedded; anim_player = ../AnimationPlayer
```

### What it overwrites

The scene and both `.res` files, every time. **Never edit them by hand or in the editor.** Change the
scripts and bake. Changes made in the editor's animation panel to `BaseCharacterAnimations.res` are
lost at the next bake (13.9 has how to keep hand-made clips).

### Notes

- The bake **does not** touch the props, the item resources, the maps or `CharacterModel.gd`.
- The unit scenes (`SquadUnit.tscn` and every map) instance `Scenes/BaseCharacter.tscn` by path, so a
  re-bake is picked up by all of them.
- `Characters/BaseCharacter.vox.import` (the plain mesh import) still exists from before the rig.
  Nothing uses its mesh now; it is harmless, and re-exporting the `.vox` re-imports it pointlessly.
- A new `class_name` script (if you add one) needs `--headless --path . --import` once before a bake
  or a run can use it.
- The bake takes a few seconds; building the library is about 80 ms of it.

---

## 8. The animation tree

Every figure plays its animations through one `AnimationTree`, whose root is the
`AnimationNodeBlendTree` from `HumanoidAnimations.make_tree()`.

```
 [19 base-pose clips] ─► stance (Transition, xfade 0.22) ─────────────────────────┐
                                                                                   ├─► move (Blend2) ─► hop (Blend2, legs only) ─► air (Blend2) ─► act (OneShot, BLEND) ─► react (OneShot, ADD) ─► output
 run_rifle (BlendSpace2D: forward/back/left/right) ┐                               │        ▲                    ▲                    ▲                    ▲
 run_melee ────────────────────────────────────────┼─► run (Transition, 0.15) ─► run_scale ─┘    hop_pose (hop)       fall_pose (fall)     act_pick (Transition,     react_pick (Transition,
 run_unarmed ──────────────────────────────────────┘                    (TimeScale)                                                        xfade 0, reset):         xfade 0, reset):
                                                                                                                                           strike_sword,            fire_rifle, hit_front,
                                                                                                                                           throw_rifle/melee/       hit_back, dodge, land
                                                                                                                                           unarmed, draw_sword,
                                                                                                                                           stow_sword
```

### Nodes

| Node | Type | Settings | Role |
|---|---|---|---|
| (19 clips named after their animations) | `AnimationNodeAnimation` | — | the base loops |
| `stance` | `AnimationNodeTransition` | 19 inputs, one per base pose, named as the clip; `xfade_time` 0.22; reset off | which base pose is held; the cross-fade is how long raising a gun takes |
| `run_rifle` | `AnimationNodeBlendSpace2D` | points `forward` (0, 1) `run_rifle`, `back` (0, -1) `back_rifle`, `left` (1, 0) `strafe_left_rifle`, `right` (-1, 0) `strafe_right_rifle`; `sync` on | the rifleman's run, any way across the ground in his own space |
| `run_melee`, `run_unarmed` | `AnimationNodeAnimation` | — | the other runs |
| `run` | `AnimationNodeTransition` | inputs `run_rifle`, `run_melee`, `run_unarmed`; xfade 0.15 | which run |
| `run_scale` | `AnimationNodeTimeScale` | — | how fast the run plays |
| `move` | `AnimationNodeBlend2` | — | base pose (0) to running (1) |
| `hop_pose` | `AnimationNodeAnimation` | `hop` | |
| `hop` | `AnimationNodeBlend2` | filter on: `Hips` and the six leg bones | legs tucked for a hop |
| `fall_pose` | `AnimationNodeAnimation` | `fall` | |
| `air` | `AnimationNodeBlend2` | — | falling |
| `<act>_clip` (6) | `AnimationNodeAnimation` | — | the acts |
| `act_pick` | `AnimationNodeTransition` | 6 inputs, xfade 0, reset on | which act |
| `act` | `AnimationNodeOneShot` | `MIX_MODE_BLEND`, fade in 0.1, out 0.22 | an act played whole over everything below |
| `<react>_clip` (5) | `AnimationNodeAnimation` | — | the reactions |
| `react_pick` | `AnimationNodeTransition` | 5 inputs, xfade 0, reset on | which reaction |
| `react` | `AnimationNodeOneShot` | **`MIX_MODE_ADD`**, fade in 0.03, out 0.12 | a reaction added on top |
| `output` | `AnimationNodeOutput` | — | |

### Parameters

What `CharacterModel` sets each frame or on demand. Paths are `parameters/<node>/<name>` on the
`AnimationTree`.

| Parameter | Type | Set by | Meaning |
|---|---|---|---|
| `parameters/stance/transition_request` | String | `_update_tree()`, on a change | the base pose to hold (`_base_pose()`) |
| `parameters/stance/current_state` | String (read) | — | the pose being held |
| `parameters/run/transition_request` | String | `_update_tree()`, on a change | `run_<hands>` |
| `parameters/run_rifle/blend_position` | Vector2 | every frame | which way it runs in its own space: (0, 1) forward, unless the walk keeps its facing |
| `parameters/run_scale/scale` | float | every frame | horizontal speed ÷ the run's `speed` meta (5): 1 at the normal 0.2 s a tile, 0.1 in a reaction's slow motion, 0 while held |
| `parameters/move/blend_amount` | float | every frame | eases to 1 while the unit moves (and is not falling), else 0, at `BLEND_RATE` (12) a second |
| `parameters/hop/blend_amount` | float | every frame | `sin(π along)` on a step that climbs or drops, else 0 |
| `parameters/air/blend_amount` | float | every frame | eases to 1 while falling |
| `parameters/act_pick/transition_request` | String | `_act(clip)` | the act to play |
| `parameters/act/request` | int | `_act(clip)` | `ONE_SHOT_REQUEST_FIRE` |
| `parameters/act/active` | bool (read) | — | whether an act is playing |
| `parameters/react_pick/transition_request` | String | `_react(clip)` | the reaction |
| `parameters/react/request` | int | `_react(clip)` | `ONE_SHOT_REQUEST_FIRE` |

Each clip node also exposes `current_length` and `backward`; nothing sets them.

### Things to know about the tree

- **The tree resource is shared by every figure** (it is in the scene, and every unit instances the
  scene). Set *parameters* per figure; never change a node's *properties* (fade times, cross-fade,
  filters) at run time, or every figure changes.
- The base Transition cross-fades poses in **joint space**, so for its 0.22 s a held rifle can drift
  in the hands. Nothing keeps the hands on the gun mid-blend.
- `act` replaces everything below it while it plays (with its fades), so an act must be a whole pose
  and should start and end close to the base pose it is played over.
- `react` adds; its clips must be changes from the rest, keyed only where they change something.
- A Transition feeding a one-shot has xfade 0 and resets its input, so the one-shot always starts the
  picked clip from its beginning; the one-shot does the fading.
- Firing a one-shot that is already playing restarts it.

---

## 9. The runtime: CharacterModel and friends

### 9.1 What CharacterModel is

`Scripts/Characters/CharacterModel.gd`, `class_name CharacterModel`, the root of every figure. A
unit's `Model` child, so `Unit.model`. It is presentational: the rules never read it.

On `_ready()` it finds its `Skeleton3D`, `Body`, `AnimationTree` and `Aim` (errors and stops if the
first three are missing: rebake), and loads `crumbles_as` and `gear_wears_as` if the scene sets none
(section 9.8). It puts `body_material` on the body, reads the run's `speed` meta, and sends the tree
its first state.

### 9.2 What it reads from its unit every frame

Its unit is its parent (`get_parent() as Unit`). Each frame it compares the unit's position with last
frame's:

| It sees | It does |
|---|---|
| the unit moving (`Unit.is_moving()`) | `move` blend to 1; `run_scale` = horizontal speed / 5 |
| moving, and not keeping its facing | turns toward the way it goes, at `TURN_PER_TILE` (600°) per tile walked, so a slowed walk turns slowly too |
| moving while keeping its facing (a step out) | keeps facing; feeds the direction of travel, in its own space, to `run_rifle`'s blend position (so it sidesteps or backs up with the rifle up) |
| a step of the walk that climbs or drops | lifts the figure (its own `position.y`, never the unit's) by `along × (1 - along) × (rise + 4 × HOP_UP)` going up, or `× (4 × HOP_DOWN - rise)` going down, and blends in the hop pose by `sin(π along)` |
| the unit no longer moving | drops the walk; if it was falling, plays `land` |
| an aim point set | turns toward it |
| otherwise | turns toward the yaw `Postures` or `face()` gave it, at `TURN_SPEED` (600° a second), never slower than 150° a second |

The hop lives on the figure, so the unit still moves in a straight line between tiles and
`tile_at()` (which reactions read mid-walk) never sees it. Up, the arc rises early and clears the
block's edge (`HOP_UP` 0.35 puts the feet about 0.1 over it at the edge); down, it stays up and drops
late (`HOP_DOWN` 0.15).

### 9.3 Readiness, cover and the base pose

`readiness` is one of `NONE`, `AIM`, `MELEE`, `THROW`, `CHEER`, set by the calls in 9.4. `cover`
(`LineOfSight.Cover`) comes from `Postures`. `overwatching` comes from the unit's setter. The **hands**
are `melee` while a gun carrier has drawn its sword, else the stance. `_base_pose()` picks:

| readiness | other conditions | base pose |
|---|---|---|
| `CHEER` | — | `cheer_<hands>` |
| `AIM` | has a gun | `aim_rifle` (without a gun, AIM falls through to the rows below) |
| `MELEE` | — | `ready_melee` |
| `THROW` | — | `ready_throw_<hands>` |
| `NONE` | overwatching, hands `rifle`, low cover | `overwatch_crouch_rifle` |
| `NONE` | overwatching, hands `rifle`, high cover | `wall_rifle` (no visible overwatch in high cover) |
| `NONE` | overwatching, hands `rifle`, no cover | `overwatch_rifle` |
| `NONE` | low cover | `crouch_<hands>` |
| `NONE` | high cover | `wall_<hands>` |
| `NONE` | no cover | `stand_<hands>` |

The run is always `run_<hands>`.

### 9.4 The calls

All are reached through thin `Unit` wrappers that do nothing without a figure, so the rules work
without one.

| `CharacterModel` | `Unit` wrapper | Called from | What it shows |
|---|---|---|---|
| `begin_walk(points, keep_facing)` | inside `Unit.start_walk()` | every walk | the walk's points, for the hops; whether to keep facing |
| `fall()` | inside `Unit.drop_to()` | `TerrainDestruction` dropping a stranded unit | falls until the unit stops, then lands |
| `face(point)` | — | the readiness calls | turns to a point |
| `settle(cover, yaw, watch, at_once)` | — | `Postures` | cover, facing, what to keep an eye on; `at_once` snaps (first look of a battle) |
| `is_idle()` | — | `Postures` | not moving, falling or dead, nothing ready, no act playing |
| `aim_at(point)` | `Unit.aim_at(point)` | `ShootAction._show_shot()`, `ShotPlayback.play()` | readiness `AIM`, faces the point, the aim modifier pitches to it |
| `ready_strike(point)` | `Unit.ready_strike(point)` | `StrikeAction._show_target()` | readiness `MELEE`, draws a slung sword, faces the target |
| `ready_throw(point = null)` | `Unit.ready_throw(point)` | `ThrowGrenadeAction.begin()` (no point) and `_aim()` (the throw's end) | readiness `THROW`, a grenade from the belt into the left hand, faces the point |
| `celebrate()` | `Unit.celebrate()` | `TurnManager._end_if_decided()` for the winning side | readiness `CHEER` |
| `stand_easy()` | `Unit.stand_easy()` | each action's `end()`, `ShotPlayback.play()` after a shot | back to `NONE`, at the end of the frame (see below) |
| `take_aim(point)` (coroutine) | inside `Unit.shoot_at()` | every shot | aims, returns once turned and the gun up; at once if it already was |
| `fire() -> Vector3` | inside `Unit.shoot_at()` | every shot | plays `fire_rifle`, a `MuzzleFlash` at the gun's `Muzzle`; returns the muzzle's position for the tracer |
| `muzzle_point()` | — | `fire()` | the `Muzzle` marker's position, or eye height without a gun |
| `strike(point)` (coroutine) | inside `Unit.strike()` | every strike | squares up, waits out a draw, plays `strike_sword`, returns at `impact` |
| `throw_toward(point) -> Vector3` (coroutine) | inside `Unit.throw_at()` | every throw | turns, plays `throw_<hands>`, returns at `release` with the hand's position; hides the grenade in hand |
| `recover()` (coroutine) | `Unit.recover()` | `StrikeAction._strike()` | waits for the act playing to end |
| `flinch(from)` | inside `Unit.take_damage()` (non-lethal hits) | every hit that does not kill | `hit_front` if `from` is in front of it, else `hit_back` |
| `dodge()` | `Unit.dodge()` | `Unit.shoot_at()` and `Unit.strike()` on a miss | plays `dodge` on the target |
| `equip(gun, melee, grenades)` | `Unit._dress()` | `Unit._ready()`, `Unit.use_up()` | shows the gear (9.6) |
| `break_apart()` | `TerrainDestruction.break_figure()`, and `Unit.die()` | every death, once its voxels and gear are taken | marks it `dead`, hides it, stops its tree and aim (9.8) |
| `paint(color)` / `tint()` | `Unit._paint()` / `Unit.color` | `Unit._take_character()` / UI | the flat body colour |
| `body_box()` | — | `Unit._add_bodies()` | the rest box |

**Standing easy waits for the end of the frame.** An action that ends and begins again at once (Shoot
re-begins after each shot if the unit can shoot again) calls `stand_easy()` then `aim_at()` in the same
frame. The second call cancels the first (`_easing`), so the gun never drops between shots.

### 9.5 The timing contract with the rules

Where the rules wait for the figure:

- **A shot**: `Unit.shoot_at()` awaits `take_aim()`. That returns at once if the figure has been
  aiming at least `RAISE_SECONDS` (0.22) and faces within `FACING_TOLERANCE` (12°). Otherwise it waits
  at least 0.22 s and until it faces the target, giving up after `TURN_TIMEOUT` (0.5 s; paused time
  does not count). Then the roll, the path, the kick and flash, the tracer, the landing.
- **A strike**: `Unit.strike()` awaits `CharacterModel.strike()`, which squares up (up to 0.5 s),
  waits for any act still playing (the draw, 0.45 s), plays `strike_sword` and returns at its impact
  (0.27 s in). Then the roll and the damage. `StrikeAction` calls the result and waits
  `Unit.recover()` (the remaining 0.48 s) before completing.
- **A throw**: `Unit.throw_at()` awaits `throw_toward()`, which turns, waits for any act, plays the
  throw and returns at release (0.36 s in) with the hand's position. Then the grenade is used up and
  flown from the hand.

Everything else (flinches, ducks, landings, cheers, runs) never makes the rules wait.

### 9.6 Gear

`equip(gun, melee, grenades)` makes a prop for each item from its `Item.model` scene and calls
`_place_gear()`:

| Item | Where it goes |
|---|---|
| gun | `RightHand/RifleGrip`, or `Back/RifleSlot` while the sword is drawn |
| melee weapon | `RightHand/SwordGrip` if there is no gun (melee stance) or it is drawn; else `Back/SwordSlot` |
| grenades | the first one in `LeftHand/GrenadeGrip` while a throw is readied; the next three on `Belt/Grenade1`..`3`; more are carried unseen |

- **Stances.** `rifle` with a gun, else `melee` with a melee weapon, else `unarmed`.
- **Drawing and stowing.** A rifleman with a sword draws it when a strike is readied (`draw_sword`)
  and stows it when the readiness ends (`stow_sword`). The props swap at the clip's `swap` moment, the
  hand over the right shoulder.
- **Refreshing.** `Unit._dress()` calls `equip()` as the unit enters the map and after `Unit.use_up()`.
  A prop for the same item is kept, and the grenades are rebuilt.
- **A thrown grenade** is hidden at release (the `ThrownGrenade` takes over). The next one comes off
  the belt only when another throw is readied.
- **An item with no `model`** is carried unseen.

### 9.7 The aim modifier

`Scripts/Characters/AimModifier.gd`, the skeleton's `Aim` child, a `SkeletonModifier3D` run after
the animations each frame (it changes the pose they leave and never builds up):

- **Aim**: `aim_weight` (0 to 1) bends the body to `aim_pitch` (radians above level), shared out 40%
  to the spine and 60% to the chest, so the arms and the gun come with it. `CharacterModel` eases the
  weight to 1 while `AIM` is ready, over `RAISE_SECONDS`, and sets the pitch from a point 1.25 cells
  above the feet to the aim point.
- **Look**: `look_weight` turns the head toward `look_point`. The turn is measured from the chest's
  front so the head never winds past `LOOK_YAW_LIMIT` (70°) side to side or `LOOK_PITCH_LIMIT` (35°)
  up and down, from `EYE_RISE` (0.2) above the head's joint. The weight is 1 toward the aim point
  while anything is readied, 0.6 toward the nearest foe (from `Postures`) otherwise, eased at 3 a
  second.

### 9.8 Death: breaking apart

As a unit dies, its figure breaks apart where it stands, as a block that wears away crumbles: into
lumps of voxel debris in the unit's colour, knocked the way the killing blow went, with its gear
dropping whole beside them. Nothing is animated: the pose it died in is what breaks.

1. `Unit.take_damage(amount, from, blasted, at, sweep)` keeps each hit on the unit (`hit_from`,
   `hit_blasted`, `hit_at`, `hit_sweep`). On a death `Unit.die()` emits `died`.
2. `TerrainDestruction` watches every unit's `died` (`_watch_units()`, deferred until the squad has
   spawned) and calls `break_figure(model, from, blasted, at, sweep)`:
   - `FigureVoxels.crumble()` cuts each bone's voxels, posed as they are, into lumps
     `crumbles_as.crumble_size` (3, `Resources/Destruction/Figure.tres`) across, on a grid shifted at
     random for each bone, so a lump is one bone's, turned as its bone is. A voxel is the unit's
     `tint()`, or blood red if blood stained any of its faces. The base figure's 536 voxels make some
     60 to 90 lumps, about 39 kg in all (`density` 300).
   - `_figure_knock()` sets each lump moving: along a round's way or a blade's swing at
     `FIGURE_KNOCK` (2 cells a second), or away from a blast at `FIGURE_BLAST_KNOCK` (1), lifted by
     `FIGURE_LIFT` of that and shared out by height, from `FIGURE_FEET_SHARE` of it at the feet to all
     of it at the head; up to `FIGURE_WOUND_PUSH` more within `FIGURE_WOUND_REACH` of where a round or
     blade landed; out from the body's upright middle at `FIGURE_SPREAD`; scattered by up to
     `FIGURE_SCATTER` and tumbling at up to `FIGURE_SPIN` radians a second. What is random in it draws
     on `TerrainDestruction._show`, never the global generator.
   - `VoxelDebris.add()` makes the lumps, held until the next physics step as all new debris is; a
     blast that killed the unit pushes them then (`VoxelDebris.burst()`), as it pushes all its debris.
   - `_drop_gear()` drops each prop shown in its sockets (`gear()`) whole: a `RigidBody3D` named
     `Dropped<prop>` under `TerrainDestruction`, the prop's mesh moved into it with any blood on it, a
     box round it 3.5% small, weighing `gear_wears_as.density` (`Gear.tres`, a crate board's) a cubic
     cell of its voxels (the rifle 4 kg), knocked as the lumps round it are. It passes through the rest
     of the gear and the lumps it starts inside (a hand round a grip), and wears away as a crate's
     boards do once a round or a blast first reaches it (`VoxelTerrain.take_on_later()`;
     `VoxelBody.scale` is 1.008, the props' 0.063 over the blocks' 0.0625).
   - `CharacterModel.break_apart()` marks it `dead`, hides it and stops its tree and aim modifier.
3. `Unit.die()` leaves its groups and frees itself, the hidden figure with it.

The lumps and gear come to rest in 2 to 3 seconds and stay for the battle: debris among debris,
thrown by blasts, shoved by the living, tidied once off the map. Blood's pool spreads where the unit
stood a second after the death (`Blood.POOL_DELAY`); a killing wound is stained at once, so its blood
is in the lumps. With blood off the figure breaks apart the same, with no red.

**Before: the ragdoll.** Until 2026-10-02 the dead were ragdolls (the user's first answer, section 2):
`fall_dead(from, blasted)` moved the figure out from under its unit, froze its pose and handed it to
a `PhysicalBoneSimulator3D` of 12 boxes with cone joints, knocked from where the hit came at `KNOCK`
(3.6) with the shins kicked the other way (`KNOCK_SHARES`) so it dropped at once, and a blast threw
the bodies in the `CORPSES` group about (`CharacterModel.blast()`). It went when the user asked for
the dead to break apart as the blocks do (section 12, decision 31). Git history has it.

### 9.9 Postures

`Scripts/Characters/Postures.gd`, a `Node` in each combat map (`CombatMap.tscn`, `BoundaryMap.tscn`,
`LineOfSightTest.tscn`), after `Reactions`. Every `interval` (0.2 s), for every living unit in
`player_group` and `enemy_group` whose figure `is_idle()`:

1. Finds its nearest living foe (the other group).
2. Takes `LineOfSight.cover_at(tile)` and picks the side whose direction faces that foe most squarely,
   if better than `facing_enough` (0.3, about 70°); between two about as square, the higher cover
   wins.
3. With such a side: that cover (low or high), facing the side. Without one: no cover, facing the foe.
4. `settle(cover, yaw, the foe's eye, first look?)`. The first look of a battle snaps every figure
   round at once.

Cover shot away stands a figure back up within 0.2 s. With no foe left, a figure stays as it is.

### 9.10 Effects

- **`Scripts/Combat/MuzzleFlash.gd`**: two crossed blades and an `OmniLight3D` under the gun's
  `Muzzle`, for `SECONDS` (0.07). `LENGTH` 0.22, `WIDTH` 0.1, `LIGHT_ENERGY` 3, `LIGHT_RANGE` 2.5.
  Each shot's is turned a random quarter about the barrel. Frees itself.
- **`Scripts/Combat/ThrownGrenade.gd`**: flies the grenade's own model (`show_model(scene)`,
  `MODEL_SCALE` 1.4, tumbling at `TUMBLE` 2.5 turns a second about the middle of its meshes, not
  its grip, so a stick grenade turns end over end on the arc rather than swinging round its
  handle) or the old ball. It leaves from the hand and eases on to the planned arc over the first
  `EASE_IN` (30%) of the flight.
- **`ShotOverlay`** draws a shot's tracers from `Ballistics.Outcome.muzzle` when the shooter's figure
  held a gun, else from the eye. Only the drawing changed: every path is still flown from the eye.

### 9.11 Constants

`CharacterModel`:

| Constant | Value | Meaning |
|---|---|---|
| `TURN_SPEED` | 600 | degrees a second, turning on the spot |
| `TURN_PER_TILE` | 600 | degrees a tile walked, turning while walking |
| `FACING_TOLERANCE` | 12 | degrees within which it counts as facing |
| `RAISE_SECONDS` | 0.22 | how long raising the gun takes (matches `stance`'s xfade) |
| `TURN_TIMEOUT` | 0.5 | most a call waits for the body to turn |
| `HOP_UP` / `HOP_DOWN` | 0.35 / 0.15 | hop heights over the straight climb or drop, cells |
| `MOVING_SPEED` | 0.05 | cells a second that count as moving |
| `BLEND_RATE` | 12 | how fast `move` and `air` follow, a second |
| `FIGURE_DESTRUCTION` / `GEAR_DESTRUCTION` | `Figure.tres` / `Gear.tres` | what `crumbles_as` and `gear_wears_as` are unless set, loaded as it readies (a preload would compile a cycle: section 16) |
| `BELT` | 3 | grenades shown on the belt |

`TerrainDestruction`, how a figure breaks apart (9.8): `FIGURE_KNOCK` 2, `FIGURE_BLAST_KNOCK` 1,
`FIGURE_LIFT` 0.3, `FIGURE_FEET_SHARE` 0.15, `FIGURE_WOUND_PUSH` 2, `FIGURE_WOUND_REACH` 0.4,
`FIGURE_SPREAD` 0.7, `FIGURE_SCATTER` 0.5, `FIGURE_SPIN` 8.

`Unit`: `PICK_RADIUS` 0.3. `MoveAction.seconds_per_step` 0.2 (was 0.12).
`TurnManager.seconds_per_enemy_step` 0.2. Step-outs: `ShootAction` and `Reactions` 0.15 s, enemies 0.2.

### 9.12 Blood on the figure

Blood (`Scripts/Blood/`, described in full in `CLAUDE.md`) is the one thing besides the animations that
reads the figure's voxels while the game runs. It does so through **`FigureVoxels`**
(`Scripts/Characters/FigureVoxels.gd`), which `CharacterModel.voxels()` makes the first time it is
asked (the combat map's `Blood` node asks for every figure as the map loads):

- **The rig, read again at run time.** `FigureVoxels` reads the `.vox` the figure was baked from
  (`CharacterModel.voxel_model`, which the bake sets) with the layout in `VoxelRig.LAYOUTS`, once per
  model (about 10 ms for the base figure), and keeps each bone's voxels as a part of its own.
- **Posed as the skeleton is.** A bone's voxels stand where `skeleton.get_bone_global_pose()` puts
  the bone, less its joint (bones rest unrotated at their joints, section 5), grown from 0.0625 to
  0.063 a voxel. That is what drops of blood and wounds are traced against (`FigureVoxels.march()`),
  so they meet the figure as it is drawn this frame: aiming, crouched or mid-stride.
- **Stains are skinned like the body.** The blood on a figure is drawn by a second skinned mesh,
  `Skeleton3D/Stains`, with the body's own `Skin`, each red square weighted wholly to the bone its
  voxel follows, so it moves with every pose. This is one more thing that relies on the rig being
  rigid, one bone a voxel (section 12, decision 1). As the figure breaks apart (9.8), every voxel
  with a stained face goes into its lump blood red.
- **The calls blood makes:** `pick_wound(from)` (a point on the side facing `from`, mostly the
  torso; a shot's tracer is drawn to it), `swing()` (the way the blade moves as `strike_sword`
  lands) and `gear()` (the props it carries, which blood stains as models of their own, and which
  drop whole when it dies). None of them change what the figure does.

`swing()` is written for `strike_sword` as it is: at the `impact` key the blade sweeps down across the
figure's front, from its right to its left (`Vector3(0.75, -0.45, 0.3)` in its own space). Re-author
the swing and that vector wants changing with it (section 13.11).

---

## 10. Catalogue of every animation

38 clips. "Rot tracks" is how many bones are keyed (18 means all); "pos" the position tracks; "keys"
the total after `optimize()`. Coordinates are rig voxels. "Chest" and "hip" positions are in that
bone's own space (section 6.3).

### Overview

| Clip | Kind | Length | Loop | Keyed | Keys | Meta |
|---|---|---|---|---|---|---|
| `stand_rifle` | base | 2.40 | loop | all + Root, Hips | 672 | |
| `stand_melee` | base | 2.40 | loop | all + Root, Hips | 696 | |
| `stand_unarmed` | base | 2.40 | loop | all + Root, Hips | 753 | |
| `crouch_rifle` | base | 2.80 | loop | all + Root, Hips | 296 | |
| `crouch_melee` | base | 2.80 | loop | all + Root, Hips | 297 | |
| `crouch_unarmed` | base | 2.80 | loop | all + Root, Hips | 222 | |
| `wall_rifle` | base | 2.60 | loop | all + Root, Hips | 382 | |
| `wall_melee` | base | 2.60 | loop | all + Root, Hips | 380 | |
| `wall_unarmed` | base | 2.60 | loop | all + Root, Hips | 474 | |
| `ready_throw_rifle` | base | 2.00 | loop | all + Root, Hips | 521 | |
| `ready_throw_melee` | base | 2.00 | loop | all + Root, Hips | 399 | |
| `ready_throw_unarmed` | base | 2.00 | loop | all + Root, Hips | 474 | |
| `cheer_rifle` | base | 1.00 | loop | all + Root, Hips | 338 | |
| `cheer_melee` | base | 1.00 | loop | all + Root, Hips | 321 | |
| `cheer_unarmed` | base | 1.00 | loop | all + Root, Hips | 308 | |
| `aim_rifle` | base | 3.00 | loop | all + Root, Hips | 303 | |
| `overwatch_rifle` | base | 4.00 | loop | all + Root, Hips | 1040 | |
| `overwatch_crouch_rifle` | base | 4.00 | loop | all + Root, Hips | 709 | |
| `ready_melee` | base | 2.00 | loop | all + Root, Hips | 498 | |
| `run_rifle` | run | 0.40 | loop | all + Root, Hips | 221 | `speed` 5 |
| `run_melee` | run | 0.40 | loop | all + Root, Hips | 215 | `speed` 5 |
| `run_unarmed` | run | 0.40 | loop | all + Root, Hips | 206 | `speed` 5 |
| `back_rifle` | run (blend point) | 0.40 | loop | all + Root, Hips | 90 | |
| `strafe_left_rifle` | run (blend point) | 0.40 | loop | all + Root, Hips | 93 | |
| `strafe_right_rifle` | run (blend point) | 0.40 | loop | all + Root, Hips | 92 | |
| `hop` | blend pose (legs) | 0.50 | loop | all + Root, Hips | 108 | |
| `fall` | blend pose | 0.60 | loop | all + Root, Hips | 249 | |
| `strike_sword` | act | 0.75 | once | all + Root, Hips | 401 | `impact` 0.27 |
| `throw_rifle` | act | 0.80 | once | all + Root, Hips | 426 | `release` 0.36 |
| `throw_melee` | act | 0.80 | once | all + Root, Hips | 403 | `release` 0.36 |
| `throw_unarmed` | act | 0.80 | once | all + Root, Hips | 402 | `release` 0.36 |
| `draw_sword` | act | 0.45 | once | all + Root, Hips | 221 | `swap` 0.17 |
| `stow_sword` | act | 0.45 | once | all + Root, Hips | 221 | `swap` 0.2 |
| `fire_rifle` | react (additive) | 0.30 | once | Spine, Chest, Neck, Head | 40 | |
| `hit_front` | react (additive) | 0.42 | once | Spine, Chest, Neck, Head | 56 | |
| `hit_back` | react (additive) | 0.42 | once | Spine, Chest, Neck, Head | 56 | |
| `dodge` | react (additive) | 0.40 | once | Spine, Chest, Neck, Head | 52 | |
| `land` | react (additive) | 0.50 | once | Hips, Spine, Chest, Neck, Head, both legs and feet; Hips position | 177 | |

### Base poses: standing (`stand_rifle`, `stand_melee`, `stand_unarmed`)

- **Function:** `_stand(time, stance)`, 2.4 s loop.
- **When:** idle in the open (no cover facing the nearest foe, no readiness, not on overwatch).
- **Body:**
  - breath period 2.4 s, weight drift 4.8 s;
  - hips at (0.2 drift, -0.5 + 0.15 breath, 0), turned -8° (+2 drift);
  - torso lean 4° + 1.2 breath, turned back 8° (- 2 drift), head steadied by half;
  - head pitch -2°, wandering ±6°.
- **Feet:** left at (2, 0, 1.2) turned out 8°; right at (-2, 0, -0.8) turned out 14°.
- **Hands (`_carry`):**
  - rifle at low ready (chest (-1.5, -0.5, 3), muzzle down-left), rocking ±2° with the breath;
  - sword low at the right hip, hip (-4.8, 2, 2), blade forward and down, left hand hanging by the
    left hip;
  - unarmed: both hands hanging by the hips, hip (±4.6, 1.8, 1).

### Base poses: kneeling behind low cover (`crouch_rifle`, `crouch_melee`, `crouch_unarmed`)

- **Function:** `_crouch(time, stance, false)`, 2.8 s loop.
- **When:** idle with low (one-cell) cover on the side facing the nearest foe; the figure faces the
  cover.
- **Body:**
  - hips down to y 5 (offset (-0.4, -4 + 0.12 breath, -1.2)), turned -6°;
  - torso lean 10° + breath, turn 6°.
- **Legs:**
  - right knee on the floor: ankle at (-2.2, 1.4, -6.2), foot pitched 55° toes down, knee pole
    (0, -1, 0.7);
  - left foot planted ahead at (2, 0, 2.6), turned 6°.
- **Hands:**
  - rifle held across the chest, muzzle up and to the left (chest (-1, -0.5, 3), direction
    (0.45, 0.35, 0.8));
  - sword upright in front (hip (-3.5, 3, 4), blade (0.1, 0.9, 0.35)), left hand on the front knee;
  - unarmed: both hands on and by the front knee.
- **Notes:** the head clears a one-cell crate; from the three-quarter view the kneeling leg hides
  behind the other, so check it from the side.

### Base poses: up against high cover (`wall_rifle`, `wall_melee`, `wall_unarmed`)

- **Function:** `_wall(time, stance)`, 2.6 s loop.
- **When:** idle with high (two-cell) cover facing the nearest foe, and on overwatch in high cover.
- **Body:** hips (0, -1 + 0.12 breath, 0.6), turned -4°; torso lean 9° + breath, turn 4°; head -6°.
  It faces the wall, leaning into it.
- **Feet:** left (2.2, 0, 0.6) turned 6°; right (-2.2, 0, -1.4) turned 10°.
- **Hands:**
  - rifle upright in front of the chest, muzzle up, its top toward the wall (chest (-1.2, 0.2, 3.2),
    direction (0.15, 1, 0.25));
  - sword upright in front, left hand by it;
  - unarmed: both hands raised in front of the chest (chest (±1.4, 1.8, 3.6)), bracing.

### Base pose: aiming (`aim_rifle`)

- **Function:** `_aim(time, 0)`, 3.0 s loop.
- **When:** while a shot is lined up (readiness `AIM`), through the shot, and for reaction and enemy
  fire.
- **Body:**
  - hips (0, -1.2 + 0.1 breath, -0.3), turned -12°;
  - torso lean 6° + 0.5 breath, turned back 12°, head unsteadied (0), neck (-2, -4), head (-4, -6);
  - a bladed shooter's stance.
- **Feet:** staggered: left forward (2.2, 0, 2.6) turned 4°; right back (-2.2, 0, -2.6) turned 22°.
- **Rifle:** shouldered under the chin (chest (0, 2, 4.3), straight ahead); the right elbow out
  (pole (-1.2, -1, 0)).
- **Plus:** the aim modifier pitches the spine and chest to the target's eye.

### Base pose: overwatch (`overwatch_rifle`)

- **Function:** `_aim(time, 1)`, 4.0 s loop.
- **When:** on overwatch in the open.
- **Difference from the aim:** the rifle lowered 6° (`rotated_local` about its x); lean +6°; a slow
  sweep: torso turn ±14°, hips ±4°, head ±6°, over 4 s.

### Base pose: overwatch behind low cover (`overwatch_crouch_rifle`)

- **Function:** `_crouch(time, &"rifle", true)`, 4.0 s loop.
- **When:** on overwatch with low cover.
- **Pose:** the kneel's legs; torso lean 8°, sweep ±10°, steadied 0.2; rifle shouldered, lowered 5°,
  over the cover; head -6° pitch, ±6° sweep.

### Base pose: sword guard (`ready_melee`)

- **Function:** `_strike(time, -1)`, 2.0 s loop: the strike's first keys, held, with breathing.
- **When:** while a strike is lined up (readiness `MELEE`), and between strikes.
- **Body:** hips (0, -1.6 + 0.12 breath, 0); twist 12° left (hips 35%, torso 65%); lean 6°.
- **Feet:** left forward (2.4, 0, 2.6) turned 8°; right back (-2.2, 0, -2.4) turned 24°.
- **Sword:** grip at chest (-4.2, 4, 2.5), blade up and back (-0.15, 0.85, -0.5), edge forward. The
  blade stands beside the right of the head, clear of it.
- **Left hand:** a guard in front, chest (3, -0.5, 4.5).

### Base poses: grenade ready (`ready_throw_rifle`, `ready_throw_melee`, `ready_throw_unarmed`)

- **Function:** `_throw(time, stance, -1)`, 2.0 s loop: the throw's first key, held, with breathing.
- **When:** while a throw is lined up (readiness `THROW`).
- **Body:** twist 10° (left shoulder back), weight -0.3, lean 2° + breath.
- **Feet:** right forward (-2.2, 0, 2.6) turned -6°; left back (2.4, 0, -2.4) turned 18°: a
  left-handed thrower's stance.
- **Left hand:** the grenade up by the shoulder, chest (3.2, 1.5, 3.4).
- **Right hand (`_carry` with `left_free`):**
  - rifle one-handed, hanging by the hip muzzle down (hip (-4.6, 2.5, 2), direction (-0.1, -0.5, 0.86),
    30° below level: steeper, the 18-voxel rifle's muzzle went into the floor);
  - sword low at the side;
  - unarmed: hanging.

### Base poses: victory (`cheer_rifle`, `cheer_melee`, `cheer_unarmed`)

- **Function:** `_cheer(time, stance)`, 1.0 s loop.
- **When:** the winning side, as `TurnManager` decides the battle, while the banner is up.
- **Body:** a 1 s beat, bounce up to 1.2 voxels on the toes (feet pitch up to 20°); lean 2°, turn ±6°;
  head up 8°.
- **Feet:** left (2.4, bounce × 0.8, 0.8) turned 10°; right (-2.4, bounce × 0.8, -0.4) turned 12°.
- **Right hand:**
  - rifle thrust overhead, grip at chest (-6.5, 8 + 1.5 pump, 1), pointing up and forward;
  - sword overhead the same way;
  - unarmed: a fist overhead at chest (-6.5, 8 + 1.5 pump, 1.5).
- **Left fist:** pumping, chest (6.5, 7 + 2 (1 - pump), 1.5).
- **Note:** the fists are at ±6.5 because the head is wider than the shoulders.

### Runs (`run_rifle`, `run_melee`, `run_unarmed`)

- **Function:** `_run(time, stance)`, 0.4 s loop: two strides of one tile at `RUN_SPEED` 5 tiles a
  second; meta `speed` 5.
- **When:** whenever the unit moves, played at actual speed ÷ 5, so 1× at the normal pace and slower in
  a reaction's slow motion.
- **Legs:** `_stride()` (6.5), feet at x ±1.6 turned ∓4°, half a cycle apart, knees over the toes.
- **Body:** hips (0, -1.4 + 0.55 bob, 0.6), pitched 4°, turned ±9° with the stride; torso lean 10° +
  1.5 bob, counter-turned ∓16°, head steadied 0.8.
- **Hands:**
  - rifle at low ready, bouncing ±2°;
  - sword in the right hand trailing low behind (hip (-4.8, 3 + 0.6 pump, -1 + 1.5 pump), blade back
    and down), left arm pumping;
  - unarmed: both fists pumping, chest (±3.8, -2 ± 0.8 pump, ∓3 pump).

### Step-outs (`back_rifle`, `strafe_left_rifle`, `strafe_right_rifle`)

- **Function:** `_step(time, way)`, 0.4 s loop; `way` (0, -1) back, (1, 0) toward the figure's left,
  (-1, 0) toward its right.
- **When:** a rifleman walking while keeping its facing: stepping out of cover to shoot and back,
  through the `run_rifle` blend space at the direction of travel in its own space.
- **Legs:** shuffled steps that never cross: feet at x ±2.4, z ±1.6, each shifting ±2.6 along the
  way and lifting up to 2.2.
- **Body:** a small hop (hips -1.6 + 0.5 |sin|); hips turned -12°; torso lean 8°, turn 12°, tilt
  -4 × way.x.
- **Rifle:** shouldered: they keep the gun on the target.
- **Note:** tuned for a one-tile sidestep in 0.15-0.2 s; a long strafe would look like shuffling.

### Hop (`hop`)

- **Function:** `_hop(time)`, 0.5 s loop.
- **When:** blended in by `sin(π along)` on a step that climbs or drops a level, legs only (the `hop`
  node's filter), while the figure is lifted by its arc.
- **Pose:** hips +0.5, pitched -6°; torso lean 14°.
  - Left foot tucked forward at (1.8, 5 + 0.3 flutter, 3), pitched -10°.
  - Right foot tucked back at (-1.8, 4 - 0.3 flutter, -2.5), pitched 30°.
  - Arms as `_carry` unarmed, but filtered out.

### Fall (`fall`)

- **Function:** `_fall(time)`, 0.6 s loop.
- **When:** `Unit.drop_to()` (the floor broke), blended in by `air` until the unit lands.
- **Pose:** hips pitched -10°, rolling ±4°; torso leaning back 12°, turning ±8°; head -10°.
  - Legs kicking: feet at (±2.4, 2.6 ± 1.5, 2 ± 1.5).
  - Arms flung up: palms at chest (±6.5, 7 ± 1, 1).
  - The rifle goes up with the right hand.

### Strike (`strike_sword`)

- **Function:** `_strike(time, 1)`, 0.75 s, once; meta `impact` 0.27.
- **When:** `Unit.strike()`; the blow lands at the impact.
- **Body keys** `[time, (lunge forward, twist left, lean)]`:

  | Time | Lunge | Twist | Lean | |
  |---|---|---|---|---|
  | 0.00 | 0 | 12 | 6 | guard |
  | 0.14 | -1.5 | 30 | 0 | wind-up: drawn back, twisted right |
  | **0.27** | 5 | -28 | 20 | **impact**: lunge, twisted through |
  | 0.42 | 5.5 | -38 | 24 | follow-through |
  | 0.75 | 0 | 12 | 6 | back to the guard |

- **Sword keys** `[time, grip in chest space, blade direction, edge facing]`:

  | Time | Grip | Blade | Edge |
  |---|---|---|---|
  | 0.00 | (-4.2, 4, 2.5) | (-0.15, 0.85, -0.5) | (0, 0.5, 1) |
  | 0.14 | (-5.5, 7, -1.5) | (0.1, 0.4, -0.91) | (0, 1, 0.4) |
  | 0.27 | (0, -0.5, 6) | (0.55, -0.45, 0.7) | (0.5, -0.8, -0.1) |
  | 0.42 | (1, -2.5, 3.5) | (0.75, -0.6, 0.25) | (0.3, -0.6, -0.7) |
  | 0.75 | as 0.00 | | |

- **The lunge** moves `Root` forward (z), up to 5.5 voxels. The planted feet are placed at their spots
  minus the root, so they stay put while the body goes over them. The front (left) foot steps in by
  0.4 × the lunge. The hips drop 0.15 × the lunge. The left hand keeps a guard at chest
  (3, -0.5, 4.5 - 0.05 × twist).
- **Reach:** the sword tip at impact reaches about a tile ahead, enough for an adjacent target,
  diagonals included.

### Throws (`throw_rifle`, `throw_melee`, `throw_unarmed`)

- **Function:** `_throw(time, stance, 1)`, 0.8 s, once; meta `release` 0.36.
- **When:** `Unit.throw_at()`; the grenade leaves the hand at release.
- **Keys** `[time, (twist, weight forward, lean), left hand in chest space]`. Twist is degrees with
  the left shoulder back as positive; weight is the hips' forward shift in voxels.

  | Time | Twist | Weight | Lean | Hand | |
  |---|---|---|---|---|---|
  | 0.00 | 10 | -0.3 | 2 | (3.2, 1.5, 3.4) | ready |
  | 0.22 | 42 | -1.6 | -6 | (5, 7.5, -4.2) | wound back behind the head, weight back |
  | **0.36** | -18 | 1.2 | 12 | (2.6, 9.5, 4) | **release**, over the head, in front |
  | 0.50 | -30 | 1.8 | 18 | (-0.5, -1.5, 6) | follow-through across the body |
  | 0.80 | 10 | -0.3 | 2 | (3.2, 1.5, 3.4) | back to ready |

- **Body:** hips 40% of the twist, torso 60%, head counter-turned 30%; hips lowered 0.3 × |weight|.
- **Feet:** as the ready pose.
- **Right hand:** keeps its weapon one-handed (`_carry` with `left_free`); the three clips differ
  only in that.
- **Release height:** the hand is about 1.6 cells up, below the 1.9 the rules' arc starts from, so
  the flying grenade eases on to the arc (section 9.10).

### Draw and stow (`draw_sword`, `stow_sword`)

- **Function:** `_draw(time, drawing)`, 0.45 s, once; meta `swap` 0.17 (draw) and 0.2 (stow).
- **When:** a rifleman carrying a sword: drawn as a strike is readied, stowed as the readiness ends.
- **Pose:**
  - every bone slerped from `stand_rifle` at 0 to `ready_melee` at 0 (the reverse to stow) by
    smoothstep over 0.45 s, the root and hips lerped the same way;
  - the right palm pulled toward the hilt over the right shoulder, chest (-2.8, 5.5, -1.5), by
    `sin(π t / 0.38)`, keeping the hand turned as the blend has it.
- **The swap** of the props happens at the hand's highest point, in `CharacterModel`, not in the clip.
- **For a swordsman without a gun** (the sword is always in hand), neither plays.

### Fire (`fire_rifle`)

- **Function:** `_fire(time)`, 0.3 s, once; additive on `UPPER_BODY`.
- **When:** `CharacterModel.fire()`, from `Unit.shoot_at()` as the round goes.
- **Shape:** a kick that rises in 0.03 s and settles by 0.28 s: spine -2.5°, chest -7° (and 1.5°
  yaw), neck -2°, head -3°. The chest jolts back, and the rifle with it.

### Hits (`hit_front`, `hit_back`)

- **Function:** `_hit(time, way)`, 0.42 s, once; additive on `UPPER_BODY`; `way` -1 thrown back (hit
  from in front), +1 thrown forward (from behind).
- **When:** a hit that does not kill (`Unit.take_damage()`, including one the defense stops
  entirely). Front or back by where the hit came from against the figure's facing.
- **Shape:** a jolt rising in 0.05 s, easing off by 0.42 s.
  - Spine 16 × way (and 6° roll).
  - Chest 22 × way (and 9° yaw).
  - Neck 12 × way.
  - Head 24 × way (-12° yaw, 9° roll).
- **Note:** still subtle at the default zoom.

### Dodge (`dodge`)

- **Function:** `_dodge(time)`, 0.4 s, once; additive on `UPPER_BODY`.
- **When:** the target of a shot or strike that missed.
- **Shape:** a duck rising in 0.08 s, easing off from 0.1 to 0.4 s.
  - Spine forward 10°, rolled -10°.
  - Chest forward 10°, yaw -6°, roll -6°.
  - Neck 6°.
  - Head 10° down, 10° yaw, -8° roll.

### Land (`land`)

- **Function:** `_land(time)`, 0.5 s, once; additive on `UPPER_BODY + LEGS`, with a `Hips` position.
- **When:** a figure that was falling stops moving.
- **Shape:** a squash rising in 0.06 s, recovering from 0.08 to 0.5 s.
  - Hips down 3.6 and back 0.8, pitched 10°.
  - Spine 12°, chest 8°, head -10°.
  - Thighs -48° (forward), shins +80° (knees bent), feet -38°.
- **Note:** made for landing in a standing pose.

---

## 11. Props

### Conventions

- **Item space** is Godot's axes in voxels: the grip at the **origin**, the item standing along
  **+z** (barrel, blade), its top toward **+y**, +x to its left.
- **The prop scene's `Mesh` puts the grip on the scene's origin.** The importer puts a mesh's origin
  at `floor(size / 2)` of the model box and then adds where the model sits in MagicaVoxel's world
  (its `_t`: `0 21 2` and the like for a model left where MagicaVoxel puts a new one, standing on
  the ground). So a model is drawn however is easiest and the `Mesh` node's transform cancels that
  offset, and turns a model drawn along another axis, rather than the `.vox` being made to fit.
  Editing the voxels in place changes nothing; moving the model in MagicaVoxel's world or resizing
  its box moves the mesh, and the `Mesh` must be placed again.
- **Placing a `Mesh`:** load the imported mesh and print `get_aabb()` divided by 0.063, which gives
  its voxels in Godot's axes: MagicaVoxel x is Godot x, MagicaVoxel z is Godot y, MagicaVoxel y is
  Godot -z. Find the grip there, and give the `Mesh` the basis `turn`, which takes the model's
  barrel or blade to +z and its top to +y, and the origin `-(turn * grip) * 0.063` (have Godot
  print the `Transform3D`, as `CLAUDE.md`'s Gotchas say). A model drawn with its forward along
  MagicaVoxel's -y and its top up its z needs no turn.
- **Import at Scale 0.063**, like the figure. A new prop's `.vox.import` needs the params:

  ```
  [params]

  Scale=0.063
  GreedyMeshGenerator=true
  SnapToGround=false
  FirstKeyframeOnly=true
  ```

  The importer's default is 0.1. Write the `.import` with those params before the first import, or
  fix it after, and Godot fills in the rest.
- **The source `.vox` lives in `MagicaVoxel/`** with a copy in `vcom/Items/`, as the character's does
  (`MagicaVoxel/BaseCharacter.vox` and `vcom/Characters/BaseCharacter.vox`).

### The three props

Drawn in MagicaVoxel (`Rifle2.vox`, `Shortsword2.vox`, `StickGrenade.vox`), replacing the first
placeholders, which a throwaway script had written from box lists. Each was left where MagicaVoxel
put it, so each imports with an offset its scene's `Mesh` cancels. In item space, as the scenes
place them:

| Prop | `.vox` box (MagicaVoxel x, y, z) | Voxels | Item-space design |
|---|---|---|---|
| `Rifle2.vox` | 18 × 1 × 5, barrel along +x | 33 | one voxel thick (x -0.5..0.5); a black grip block under the receiver, z -0.5..0.5 at y -1..1 and z 0.5..1.5 at y 0..1 (the origin at its middle); wooden stock z -4.5..-0.5, dropping to y -2 at the butt; dark receiver bar z -1.5..4.5, y 1..2, under a black top z -2.5..2.5, y 2..3; wooden fore-end z 3.5..12.5, y 2..3; black muzzle cap z 12.5..13.5. 18 long, against the placeholder's 15. |
| `Shortsword2.vox` | 1 × 14 × 4, blade along -y | 30 | one voxel thick (x -0.5..0.5); pommel z -3..-2, y -1..1, and crossguard z 1..2, y -2..2 (dark teal); wooden grip z -2..1, y -1..1, the origin a voxel short of the guard as on the placeholder; pale blade z 2..11, y -1..1. |
| `StickGrenade.vox` | 4 × 4 × 8, standing up its z | 56 | standing up +y: cap y -2.5..-1.5 and a 4 × 4 head with its corners off y 2.5..5.5 (blue-grey), wooden handle 2 × 2 y -1.5..2.5; the origin on the handle, a voxel and a half above its foot. |

### Prop scenes

`vcom/Scenes/Props/<Item>.tscn`, named after the items rather than the models (safe to edit in the
editor):

| Scene | Children | Markers (item voxels) |
|---|---|---|
| `Rifle.tscn` | `Mesh` (`Items/Rifle2.vox`, turned -90° about y, so its +x is +z, and moved (-21.5, -2, 4.5)), `Muzzle`, `Foregrip` | `Muzzle` (0, 2.5, 13.5): the barrel's end, where it flashes and tracers start; `Foregrip` (0, 1, 3): on the underside of the receiver bar, just behind the fore-end, where the left palm holds it (the bake reads this) |
| `Shortsword.tscn` | `Mesh` (`Items/Shortsword2.vox`, moved (-0.5, -2, 25)), `Tip` | `Tip` (0, 0, 11) (not used yet) |
| `FragGrenade.tscn` | `Mesh` (`Items/StickGrenade.vox`, moved (0, -2.5, 21)) | — |

Markers and the `Mesh` offsets are in Godot units in the scene (voxels × 0.063). The root `Node3D`
is the grip.

The foregrip is as far forward as the arms reach. On the underside of the bar the left palm holds
it from below and comes within 0.15 voxels of it in every two-handed clip; at (0, 1.5, 3.5), on the
bar under the fore-end's start, it stopped up to 0.65 short in the aim and on overwatch.

### Linking an item to its prop

`Item.model: PackedScene` (`Scripts/Items/Item.gd`). `Rifle.tres`, `Shortsword.tres` and
`FragGrenade.tres` point at the three scenes. Without a `model` an item is carried unseen. How a prop
is held is decided by its **kind** (gun, melee weapon, grenade): the socket and the poses (section
6.4). A differently shaped item of a known kind (another rifle) needs only a model; a new kind of
hold needs poses too (13.6).

---

## 12. Decisions, with their pros and cons

Every significant choice, why it was made, and what it costs.

### Rigging

1. **Rigid skinning, one bone per voxel.**
   - *Why:* the inspiration art is segmented voxel figures; voxels should stay cubes.
   - *Pros:* crisp blocks that never stretch or shear; trivially correct weights; a bent joint reads
     clearly at 40 pixels.
   - *Cons:* joints open and overlap when they bend (corners poke through or gap); no soft
     deformation (cloth, bellies); each bone must be meshed separately, so the plain importer could
     not be reused.
   - *Alternative:* smooth skinning, which bends voxels like rubber.
2. **One `Skeleton3D` with one skinned mesh** rather than a node per body part.
   - *Pros:* one draw call per figure; standard Godot animation tooling (tracks on bones, the editor's
     bone gizmos, `BoneAttachment3D`, `SkeletonModifier3D`, `PhysicalBone3D` ragdolls); retargetable.
   - *Cons:* needed a custom mesher and skin; a part cannot be swapped by swapping a node.
3. **Godot's `SkeletonProfileHumanoid` bone names.**
   - *Pros:* the rig is a standard humanoid, so retargeting tools (BoneMap) can in principle map other
     humanoid animations onto it.
   - *Cons:* the chibi proportions and rigid limbs would make retargeted motion look off; no
     shoulders, toes or fingers (the profile's optional bones are left out).
4. **The rest pose is the model as drawn (a T-pose), every bone unrotated.**
   - *Pros:* a rotation means the same thing on every bone, so poses can be written by hand; nothing
     to fix up between the art and the rig.
   - *Cons:* a T-pose's shoulders are a poor neutral for lowered arms (the arm's top faces out when
     lowered); a model drawn in an A-pose would need its hand grips worked out again.
5. **Joint placement:** the shoulder pivot one voxel into the arm, joints at segment boundaries
   elsewhere.
   - *Pros:* lowered arms hang flush beside the torso.
   - *Cons:* the arm's inner voxel column rides up above the shoulder line when lowered.
6. **The layout as a dictionary in code** (joints plus region boxes) rather than a resource, a painted
   bone map, separate MagicaVoxel objects per part, or automatic segmentation.
   - *Pros:* simple, exact, reviewable in a diff, needs nothing extra from the artist.
   - *Cons:* a new model needs someone to read its voxels and type numbers; editing it is not
     visual.
7. **A bake script run by hand** rather than an import plugin that rigs on re-import.
   - *Pros:* consistent with `BakeLand.gd`; no addon to maintain; explicit.
   - *Cons:* forgetting to bake after editing the `.vox` leaves the old rig in play.

### Animations

8. **Animations authored in code** rather than keyed in the editor, in Blender or taken from Mixamo.
   - *Why:* no DCC on the machine, no external assets wanted; code is what this workflow edits best.
   - *Pros:*
     - exact and repeatable;
     - easy to change by number ("lunge further", "lower the rifle 5°");
     - regenerates for a new model's proportions;
     - diffable;
     - one function serves three stances.
   - *Cons:* programmer animation, with less nuance than an animator would give (weight, overlap,
     secondary motion); every change needs a bake and a look; not editable in the editor without
     losing it on the next bake.
9. **IK at bake time** (solved into the keys) rather than runtime IK modifiers (`TwoBoneIK3D` and
   friends, available in 4.7).
   - *Pros:* free at run time; deterministic; what is previewed is what plays; hands land on props
     exactly in the authored poses.
   - *Cons:* nothing corrects at run time, so cross-fades drift the hands off the rifle, and nothing
     plants feet on uneven ground (not needed: tiles are flat, and steps are hopped).
10. **Sampled at 30 fps and then optimised** rather than a few hand-placed keys with cubic
    interpolation.
    - *Pros:* any function of time can be expressed (sines, gaits, eased tables); the optimiser removes
      what is redundant.
    - *Cons:* hundreds of keys per clip, so editing a baked clip by hand in the editor is impractical
      (another reason not to).
11. **Binary `.res` for the mesh and library** rather than text `.tres`.
    - *Pros:* small (384 KB library, 28 KB mesh); fast to load.
    - *Cons:* not diffable, so the diff to review is the script's.
12. **Three stances (rifle, melee, unarmed) as variants of shared pose functions.**
    - *Pros:* one body motion per action; the hands differ by `_carry`.
    - *Cons:* the clip count grows with every stance (a new stance adds about seven clips); the run
      Transition and some `match` blocks must be extended by hand.

### The tree and the runtime

13. **A BlendTree with a Transition of base poses**, rather than a state machine or plain
    `AnimationPlayer` cross-fades.
    - *Pros:* every layer in one place; base poses are chosen by name; one-shots layer over anything.
    - *Cons:* the Transition holds every base pose (19 inputs, growing); the tree is generated, so
      it is edited in code.
14. **Reactions are additive** (`MIX_MODE_ADD`, deltas from the rest on the upper body).
    - *Pros:* one flinch, duck, recoil and landing for every pose: standing, kneeling, aiming,
      running, holding anything.
    - *Cons:* a delta tuned on standing can look odd on an extreme pose; additive clips must be
      authored as changes, not poses (easy to get wrong).
15. **The hop blend is filtered to the legs.**
    - *Pros:* the arms keep holding the rifle through a hop.
    - *Cons:* the upper body does not react to the jump.
16. **Run speed follows the unit's actual speed** (`TimeScale` = speed / 5).
    - *Pros:* feet keep up with the ground at any pace; a reaction's slow motion slows the legs, and
      a held walk freezes them mid-stride, for free.
    - *Cons:* one gait for every speed: a very slow walk is a slow-motion run, not a walk.
17. **Movement at 0.2 s a tile for everyone** (the user's choice) and a stride of one tile.
    - *Pros:* about 5 strides a second, a readable run; the squad and enemies match.
    - *Cons:* long squad moves take about 65% longer than at 0.12.
18. **Facing and hops live on the figure, not the unit.**
    - *Pros:* the rules (positions, `tile_at()`, reactions) are untouched; the unit node stays
      unrotated.
    - *Cons:* the click body and debris capsule never turn (they are round, so it does not matter).
19. **Actions ask the figure to get ready** (`aim_at`, `ready_strike`, `ready_throw`, `stand_easy`)
    while a target is lined up, as XCOM does.
    - *Pros:* immediate feedback while choosing; the gun is already up when the shot goes, so no wait
      for the player.
    - *Cons:* a few presentational calls in the action scripts; a deferred stand-easy was needed so
      back-to-back actions do not flicker.
20. **The rules wait for the figure at three moments** (gun up, swing's impact, throw's release).
    - *Pros:* the result is called as it is seen to happen.
    - *Cons:* `Unit.strike()` became a coroutine (callers must `await`); a strike's action now lasts
      about 0.75 s, and a shot can wait up to 0.5 s for the turn.
21. **Tracers drawn from the muzzle** while the path is still flown from the eye.
    - *Pros:* rounds visibly leave the gun.
    - *Cons:* the drawn line differs from the rules' line for its first half cell or so: a slight
      bending of "the tracer draws that path". Recorded in `CLAUDE.md`.
22. **The thrown grenade eases from the hand on to the planned arc**, rather than the arc starting at
    the hand.
    - *Pros:* the rules' arc (and its blocking test, and its preview) is untouched; it looks thrown
      from the hand.
    - *Cons:* the first 30% of the flight is not exactly the previewed arc.
23. **Every throw is left-handed.**
    - *Pros:* the right hand never has to let go of its weapon; one throw for every stance.
    - *Cons:* odd for a right-handed figure, and it shows when unarmed.
24. **The rifle aimed under the chin with the off hand on the magazine** (forced by the 8-voxel
    arms).
    - *Pros:* two-handed holds that the IK can actually reach.
    - *Cons:* the stock sinks into the chest a little; looks chibi rather than realistic.
25. **A sword carried with a gun is slung on the back and drawn per strike**, as XCOM 2's Ranger does.
    - *Pros:* shows both weapons; the draw is clear feedback that Strike is lined up.
    - *Cons:* the gun teleports on to the back at the swap; a strike right after selecting waits for
      the draw (0.45 s).
26. **Grenades tucked into the back of the belt at 0.8 scale**, the outer two fanned out 25°.
    - *Pros:* clear of the legs and of arms hanging at the sides; three fit, and each head shows.
    - *Cons:* small, and mostly hidden from the front; the slung sword's blade and the slung
      rifle's stock cross them.
27. **Props are scenes with markers** (`Item.model: PackedScene`) rather than bare meshes.
    - *Pros:* the muzzle and foregrip are data, and the animations follow the foregrip.
    - *Cons:* each prop has a scene to keep with its `.vox`.
28. **`Postures` as a map node** rather than logic in the figure.
    - *Why:* it needs the grid, which the figure does not know.
    - *Pros:* one place for cover logic; cheap (0.13 ms a run for 15 units).
    - *Cons:* a map without the node has figures that never take cover.
29. **Cover faces the nearest foe by distance**, the squarest side within about 70°, higher cover on
    a tie.
    - *Pros:* simple, stable, XCOM-like most of the time.
    - *Cons:* ignores line of sight and threat; in high cover the figure faces the wall rather than
      XCOM 2's back-to-the-wall; overwatch in high cover looks like no overwatch.

### Death

30. **Ragdoll deaths** (the user's choice), with:
    - 12 bodies (hands, feet and head riding along);
    - cone joints everywhere;
    - masses by share (the head heavy but not to scale);
    - a scripted knock with per-body shares;
    - bodies left on the debris layer, thrown by blasts with `Blast`'s physics, and freed only off
      the map.

    *Pros:* every death different, physical, and consistent with how debris behaves; blasts fling
    bodies; no death clips to author.

    *Cons:*
    - cone joints let elbows and knees bend backwards;
    - a big head makes the chain floppy;
    - bodies pile up for the battle and cost physics while awake;
    - outcomes are less controllable than authored falls;
    - Jolt contact quirks apply (section 16).

    Replaced on 2026-10-02 by 31.
31. **Breaking apart** (the user's choice, replacing 30): the dead break into lumps of voxel debris
    as a worn-out block crumbles (section 9.8). Asked with it, and answered:
    - chunks like a block's, a few voxels each, rather than whole limbs or single voxels;
    - the same with blood off, only without red;
    - gear dropped whole, as debris that later shots and blasts wear down like a crate's boards,
      rather than broken up with the body or left out;
    - the pool of blood where the unit stood, starting about a second after the death.

    *Pros:* of a piece with the destructible world; the killing blow reads in how the pieces fly;
    blood carries into the lumps; nothing to bake, so the ragdoll's joint tuning and its quirks are
    gone.

    *Cons:*
    - no fall is played: the figure bursts where it stands and its pieces drop;
    - some 60 to 90 more bodies for the physics a death, until they sleep;
    - a bent joint's two bones share a little room, so their lumps can start overlapping;
    - lumps are drawn a block's voxels across, a shade smaller than the figure's.
32. **The click body is a cylinder** rather than the T-posed hull.
    - *Pros:* matches the figure with its arms down, whatever it does.
    - *Cons:* clicks between a unit's legs or just beside it count.

### Tooling

33. **A repo preview tool** (`PreviewAnimations.gd`), playing whole clips straight from the player
    and reactions through the tree.
    - *Pros:* anyone can look at a clip with the right props, without the game.
    - *Cons:* needs a window; the figure is shown untinted.

---

## 13. Recipes: adding and changing animations

Each recipe ends with: bake, preview, then check in a map (section 14).

### 13.1 Tweak an existing animation

1. Find its function in `HumanoidAnimations.gd` (`make_library()` maps names to functions; section
   10 lists them).
2. Change the numbers. Positions are rig voxels; angles degrees; see section 4 for signs.
3. If you change a moment the game waits on (impact, release, swap), change its `set_meta` value in
   `make_library()` too.
4. Bake; preview from the side and three-quarters (`--view side`, default); check reach (hands on the
   rifle), feet on the floor, nothing inside the head.

Common tweaks:

- **Lean the run more:** in `_run`, `_torso(pose, 10.0 + bob * 1.5, ...)`, raise 10.
- **Longer stride:** `STRIDE_TILES` (and the run's `speed` follows `RUN_SPEED`).
- **Lower the rifle at low ready:** `_low_ready()`'s direction, more negative y.
- **A bigger flinch:** `_hit`'s degrees.
- **A slower strike:** stretch the times in both key tables and the clip length (0.75), and move
  `impact`.

### 13.2 Add a base pose

A base pose is a loop held between actions. Example: a "wounded" idle for units under a third of
their health.

1. **Write the function**, periodic over its length:

   ```gdscript
   ## Standing hurt: hunched, weight off the right leg, the free hand on the side.
   func _wounded(time: float, stance: StringName) -> Pose:
   	var pose := _pose()
   	var breath := sin(TAU * time / 1.6)       # quicker breathing; 1.6 divides the length
   	pose.move(Vector3.ZERO, Vector3(0.6, -1.2 + 0.2 * breath, 0.0))
   	_torso(pose, 18.0 + breath * 2.0, 0.0, -6.0, 0.6)
   	_foot(pose, &"Left", _ankle(Vector3(2.0, 0, 0.4)), 6.0)
   	_foot(pose, &"Right", _ankle(Vector3(-2.2, 0, 0.8)), -10.0, 10.0)
   	_carry(pose, stance, breath, true)       # the right hand keeps the weapon
   	_hand(pose, &"Left", pose.at(&"Hips") * Vector3(2.6, 3.0, 1.2), Vector3(1, -0.5, -1))
   	return pose
   ```

2. **Register it.**
   - **One per stance:** add `&"wounded"` to `STANCE_POSES` (this names the tree's inputs
     `wounded_rifle`, `wounded_melee`, `wounded_unarmed`), and in `make_library()`'s stance loop:

     ```gdscript
     library.add_animation(StringName("wounded_%s" % stance), _loop(3.2, _wounded.bind(stance)))
     ```

   - **Only one stance** (like `aim_rifle`): add the full name to `RIFLE_POSES` or `MELEE_POSES` (or a
     new list included in `base_poses()`) and add the clip once.

   Every name in `base_poses()` must have a clip of that name, or the tree has an input with nothing
   behind it.
3. **Bake** and **preview**: `-- wounded_rifle wounded_melee wounded_unarmed`.
4. **Make the figure choose it.** In `CharacterModel._base_pose()`, add a condition at the right
   priority (before cover, say):

   ```gdscript
   if wounded:
   	return StringName("wounded_%s" % hands)
   ```

   and a `var wounded := false` the unit sets. In `Unit`, follow the health setter (or
   `health_changed`): `if model != null: model.wounded = health * 3 <= max_health`.
5. **Check `is_idle()`** still means what `Postures` needs. A base pose is not an act, so it is fine.

### 13.3 Add an act: a one-shot played whole

Example: a "reload" one-shot for a future ammo system.

1. **Write the function**, starting and ending close to the base pose it plays over (here `aim_rifle`
   or `stand_rifle`), so the fade in and out is invisible. Use a key table for the timing:

   ```gdscript
   ## Swapping the magazine: the rifle tipped, the left hand down to the belt and back.
   func _reload(time: float) -> Pose:
   	var pose := _stand(0.0, &"rifle")                                 # start from the carry
   	var keys := [[0.0, 0.0], [0.25, 1.0], [0.55, 1.0], [0.8, 0.0]]    # how far into the reload
   	var tip: float = _keyed(keys, time)
   	_rifle(pose, _low_ready().rotated_local(Vector3.FORWARD, deg_to_rad(40.0 * tip)))
   	var belt := pose.at(&"Hips") * Vector3(2.6, 1.5, -1.0)
   	var magwell := pose.at(&"Chest") * Vector3(0.2, -1.5, 5.0)
   	_hand(pose, &"Left", magwell.lerp(belt, sin(PI * clampf(time / 0.55, 0.0, 1.0))), Vector3(1, -1, -0.4))
   	return pose
   ```

2. **Register it** in `make_library()`, with a moment if the game waits on one:

   ```gdscript
   var reload := _once(0.8, _reload)
   reload.set_meta(&"loaded", 0.55)
   library.add_animation(&"reload_rifle", reload)
   ```

   and add `&"reload_rifle"` to `ACTS` (the `act_pick` Transition gets an input for it).
3. **Bake**, **preview** `-- reload_rifle` (to preview an act from the pose it plays over, the preview
   shows the clip whole, which is what plays at full weight).
4. **Play it.** In `CharacterModel`, a method like `strike()`:

   ```gdscript
   ## Reloads, and returns the moment the new magazine is in.
   func reload() -> void:
   	while _acting > 0.0:
   		await get_tree().process_frame
   	_act(&"reload_rifle")
   	await _after(_moment(&"reload_rifle", &"loaded"))
   ```

   `_act()` sets `_acting` to the clip's length, which makes `is_idle()` false (so `Postures` leaves
   the figure alone) and `recover()` wait.
5. **Call it from the game** through a `Unit` wrapper that does nothing without a figure:

   ```gdscript
   func reload() -> void:
   	if model != null:
   		await model.reload()
   ```

6. **Props:** if the act moves a prop between sockets mid-clip, do it at a moment from the metadata,
   as `_draw_or_stow()` does, then `_place_gear()`.

### 13.4 Add a reaction: additive, on top of anything

Example: a "stagger" for a big hit.

1. **Write the function as a change from the rest:** rotations from identity, offsets from zero, only
   on the bones it moves. Shape it with a rise and a decay:

   ```gdscript
   ## Staggered by a heavy blow, added to whatever the body is doing.
   func _stagger(time: float) -> Pose:
   	var pose := _pose()
   	var jolt := (1.0 - smoothstep(0.08, 0.6, time)) * smoothstep(0.0, 0.08, time)
   	pose.move(Vector3.ZERO, Vector3(0, -1.0 * jolt, -1.5 * jolt))
   	pose.turn(&"Spine", Vector3(-14.0 * jolt, 0, 8.0 * jolt))
   	pose.turn(&"Chest", Vector3(-20.0 * jolt, 10.0 * jolt, 0))
   	pose.turn(&"Head", Vector3(-25.0 * jolt, 0, 10.0 * jolt))
   	return pose
   ```

2. **Register it, keying only those bones:**

   ```gdscript
   library.add_animation(&"stagger", _once(0.6, _stagger, [&"Hips", &"Spine", &"Chest", &"Head"]))
   ```

   Include `&"Hips"` in the list if it moves the hips (the position track is added only for keyed
   bones). Add `&"stagger"` to `REACTS`.
3. **Bake**, **preview** `-- stagger` (shown added to standing).
4. **Play it** with `_react(&"stagger")` from a `CharacterModel` method, called from the game.
5. **Rules of thumb:**
   - never key a bone you do not move (a keyed bone at identity *adds nothing*, but a bone keyed by
     mistake to an absolute pose adds that pose on top);
   - keep changes moderate, since they add to whatever the base is doing;
   - only one reaction plays at a time (a new one restarts the one-shot).

### 13.5 Add locomotion

- **Another direction for the rifleman's step-out:** add a point to `run_rifle`'s blend space in
  `make_tree()` (a clip made with `_step(time, way)`), with `sync` on and the same length as the
  others (`_cycle()`).
- **A run for a new stance:** make `run_<stance>` (copy `_run`'s `match` arm) and add it to the `run`
  Transition's inputs in `make_tree()` (the list `[&"run_rifle", &"run_melee", &"run_unarmed"]` and
  its `connect_node` lines). `CharacterModel` asks for `run_<hands>`.
- **A walk (slower gait):** a separate cycle authored at a lower speed, blended with the run in a
  `BlendSpace1D` by speed, in place of `run_scale`. That is a tree change and a `CharacterModel` change
  (`_update_tree()` sets the blend from `_speed`); keep the `speed` meta on each so feet keep pace.

### 13.6 Add a stance

Example: `pistol`, held one-handed.

1. **The prop:** a pistol `.vox` and scene (13.7), and a grip in `HumanoidAnimations._init()`
   (`pistol_grip`, like `rifle_grip`). Add a socket for it in `BakeCharacter._sockets()` (e.g.
   `RightHand/PistolGrip`).
2. **Add `&"pistol"` to `STANCES`.** `base_poses()` then names `stand_pistol`, `crouch_pistol`,
   `wall_pistol`, `ready_throw_pistol`, `cheer_pistol`, and `make_library()`'s stance loop makes
   them, so every per-stance function must handle the new stance. Add `&"pistol"` arms to the
   `match stance` blocks in `_carry`, `_crouch`, `_wall`, `_run`, `_cheer` (and `_throw` through
   `_carry`). A missing arm falls to the unarmed default.
3. **Stance-only poses** (an aim): `aim_pistol` in a list included by `base_poses()`, and its clip.
4. **The run:** add `run_pistol` to the `run` Transition in `make_tree()`.
5. **The figure:** in `CharacterModel.equip()`, decide which item gives the stance (a tag such as
   `Item.PISTOL`, or a property on `Weapon`), create its prop, and in `_place_gear()` put it in its
   socket. In `_base_pose()`, use `aim_pistol` when `AIM`. `muzzle_point()` looks for the prop's
   `Muzzle` marker, so give the pistol scene one.
6. **Bake**, preview every new clip, play it.

### 13.7 Add a prop or an item model

1. **Model it in MagicaVoxel**, any way round and anywhere in its world: its scene lines it up
   (step 3). Save it in `MagicaVoxel/` and copy it to `vcom/Items/`.
2. **Import at 0.063:** create `vcom/Items/<Name>.vox.import` with the params in section 11, then run
   `--headless --path . --import` (or let the open editor import it, then fix the scale in the Import
   dock).
3. **Make its scene** `vcom/Scenes/Props/<Name>.tscn`: a `Node3D` root named after it (the grip), a
   `MeshInstance3D` `Mesh` with the `.vox`, and markers: `Muzzle` for a gun (where it fires from),
   `Foregrip` for a two-handed gun (where the off hand holds it). Place the `Mesh` so the grip is on
   the root's origin, its forward +z and its top +y (section 11, "Placing a `Mesh`"), and check it
   by rendering the scene side-on with a mark on the origin and on each marker.
   Then preview every clip that holds it, from the side and three-quarters, and look for it going
   into the floor or the body: a longer model reaches further than the poses were made for.
4. **Point the item at it:** `model = ExtResource(...)` in its `.tres`, or set **Model** in the
   inspector.
5. **Same kind, different shape** (another rifle): the hands use the kind's grip. If its
   foregrip differs a lot from the rifle's, note that the poses read the foregrip from
   `Scenes/Props/Rifle.tscn` only (`BakeCharacter.RIFLE_SCENE`). Per-gun foregrips would need the
   left hand solved at run time, or one foregrip position shared by every rifle.
6. **A new kind:** a stance (13.6), or at least a socket and a hold.

### 13.8 Add a character model

1. **Draw it in MagicaVoxel**, one model (the reader takes the first model in the file), standing
   upright, facing -y, in a T-pose with straight arms. The base character's 32-cubed template
   (`Ex_Boy.vox`) is a good start.
2. **Copy it** to `vcom/Characters/<Name>.vox`.
3. **Write its layout** in `VoxelRig.gd`, by the base character's (a constant like `BASE_CHARACTER`).
   Dump its voxels as text to find the parts: a front view (x across, z up) and a side view (y across,
   z up) of which voxels are filled. Then:
   - **`"joints"`**, in rig voxels: x is the model's x minus the middle; y is the model's z minus the
     lowest; z is the middle minus the model's y. Shoulders a voxel into the arm; elbows, wrists,
     knees and ankles at segment boundaries; the hip joints at the top of each leg; the head joint at
     the bottom of the head.
   - **`"regions"`**, in model voxels, most specific first, so the head and arms come before the
     torso's full-width boxes.
4. **Add it to `VoxelRig.LAYOUTS`**: `"res://Characters/<Name>.vox": <NAME>`. The bake reads that
   table (`BakeCharacter.LAYOUTS` is the same one), and so does blood while the game runs: a model
   with no entry bakes nowhere and never bleeds.
5. **Bake it to its own scene:**
   `... BakeCharacter.gd -- res://Characters/<Name>.vox res://Scenes/<Name>.tscn`. Check for the
   "in no region" warning.
6. **Preview** with `--scene res://Scenes/<Name>.tscn`. Watch for:
   - arms that cannot reach the rifle (section 6.9; move `_low_ready()` and `_shouldered()` or the
     foregrip, or give the model its own placements);
   - hands inside a wider head (the cheer, the guard);
   - hip heights (`_crouch` puts the hips at y 5, written for these legs).
7. **Use it:** make it a unit's `Model` child (instance the new scene, set `body_material`), or point
   `Scenes/SquadUnit.tscn` at it. The animations were made for its proportions; the tree, the props
   and `CharacterModel` are shared.

### 13.9 Hand-keyed animations (editor, Blender), and what is missing

You can play with the baked clips in the editor: open `Scenes/BaseCharacter.tscn`, turn the
`AnimationTree`'s **Active** off, select the `AnimationPlayer`, pick a clip and play or scrub it.
Props are added at run time, so the editor shows the figure empty-handed.

Keying **new** clips by hand is possible but not yet supported end to end, because the bake replaces
the library, the tree and the scene. To support it:

1. **Keep hand-made clips in their own library**, e.g. `Characters/HandAnimations.tres`, made in the
   editor (`AnimationPlayer` → Animation → Manage Animations → New Library, saved to that file), with
   tracks on `Skeleton3D:<Bone>` (rotations relative to the unrotated rest).
2. **Change `BakeCharacter._bake()`** to load that file if it exists and add it to the
   `AnimationPlayer` under a name (`player.add_animation_library(&"hand", load(...))`), so a bake keeps
   it. Clips are then `hand/<name>`.
3. **Change `make_tree()`** to give those clips nodes: as extra `act_pick`, `react_pick` or `stance`
   inputs, by a naming convention (e.g. `hand/act_*`, `hand/react_*`, `hand/base_*`) read from the
   library at bake time.
4. **Play them** from `CharacterModel` by those names.

Hand-keyed clips will not adapt to other models' proportions, and must key rotations relative to this
rig's unrotated rest. From Blender (if installed), export glTF with an armature named and posed to
match (the same 18 bone names, unrotated rests at the same joints) and import the animations into
that library. Retargeting other humanoid animations is possible in principle through Godot's
`BoneMap` and `SkeletonProfileHumanoid`, but the chibi proportions would need heavy correction.

### 13.10 Play an animation from game code

The pattern every existing animation follows:

1. **Rules code** (an action, `TurnManager`, `Unit`) calls a **`Unit` method**, which does nothing
   when `model` is null (so the rules never depend on the figure):
   - For an instant reaction: `if model != null: model.dodge()`.
   - For something the rules wait on: `if model != null: await model.strike(point)`.
2. **`CharacterModel`** sets state (readiness, flags) that `_base_pose()` turns into a base pose, or
   fires an act or reaction (`_act`, `_react`), and awaits moments from metadata.
3. Anything that should stop `Postures` from moving the figure must make `is_idle()` false (a
   readiness other than `NONE`, a walk, a fall, or `_acting`).

### 13.11 Change a moment the rules wait on

- **Strike impact:** the `0.27` keys in `_strike`'s two tables and `strike.set_meta(&"impact", 0.27)`.
  If the blade's sweep at that moment changes, change `CharacterModel.swing()` too: blood sprays along
  it (section 9.12).
- **Throw release:** the `0.36` key in `_throw` and `throw.set_meta(&"release", 0.36)`.
- **Draw and stow swap:** the `0.38` in `_draw` (the hand's arc) and the `swap` metas.
- **Gun up before a shot:** `CharacterModel.RAISE_SECONDS` and the `stance` Transition's `xfade_time`
  (0.22) in `make_tree()`, together.
- **How long a shot waits for the turn:** `CharacterModel.TURN_TIMEOUT` and `TURN_SPEED`.

### 13.12 After any change

- Bake (if a baked script, the model or the rifle's foregrip changed).
- Preview the clips you touched from the side and three-quarters.
- Run the scenes headless for errors:
  `--headless --path . res://Scenes/BoundaryMap.tscn --quit-after 150` (and `LineOfSightTest.tscn`,
  `CombatMap.tscn`, `WorldMap.tscn`).
- Drive the action in a map and look (section 14).
- If the Godot editor is open, reload `BaseCharacter.tscn` and any open map.

---

## 14. Verifying an animation

Godot cannot be watched from here, so animations are checked by rendering frames to images and
looking at them. Every claim in this file was checked that way.

### 14.1 The preview tool

`vcom/Scripts/Characters/PreviewAnimations.gd` (section 1 has the command):

- Whole clips (base poses, runs, acts, `hop`, `fall`) are shown exactly as baked, through the
  `AnimationPlayer` (`seek(time, true)`).
- Reactions are added to a pose through the figure's `AnimationTree`, run by hand
  (`callback_mode_process = MANUAL`, `advance()`): the aim for `fire_rifle`, standing for the rest.
  This is how the game composes them.
- **Props:**
  - the rifle for clips with `rifle` in the name, and for `hop`, `fall`, `land`, `hit_*` and `dodge`;
  - the sword for `melee` and `sword` clips;
  - a grenade in hand for throws.
- Frames are spread over a loop, or from start to end of a one-shot. Ground lines are one cell
  apart, to read strides and lunges off.
- It needs a window (`--headless` cannot render). Give `--resolution`; 300x340 to 360x400 per frame
  suits a sheet.

### 14.2 In the editor

Open `Scenes/BaseCharacter.tscn`, set the `AnimationTree` inactive, and scrub clips on the
`AnimationPlayer`. No props. Do not save the scene (the bake owns it).

### 14.3 In a map, through the real actions

The best check: a `SceneTree` probe (kept outside the repo, e.g. in a scratch folder) that loads a map,
drives the actions themselves, and captures frames as they play. That tests timing and props too. A
condensed version of the probe used during development:

```gdscript
extends SceneTree
## godot --path . --script /abs/path/probe.gd --resolution 800x500 --fixed-fps 60

var map: Node
var shots := 0


func _initialize() -> void:
	map = load("res://Scenes/LineOfSightTest.tscn").instantiate()
	root.add_child(map)
	current_scene = map
	for i in 20:
		await process_frame                       # let the map's _ready()s run
	var rig = map.get_node("CameraRig")
	var squad = map.get_node("PlayerSquad")       # untyped: a --script probe cannot name
	var controller = map.get_node("ActionController")   # classes that use autoloads
	rig.edge_pan_enabled = false
	var shooting = controller.get_node("Shoot")
	var shooter = squad.members[0]
	squad.select(shooter)
	await process_frame
	controller.activate(shooting)                 # lines up the first target: the figure aims
	var target = shooting.current_shot().target
	_look(rig, (shooter.global_position + target.global_position) * 0.5)
	await create_timer(0.7, false).timeout
	await _shot("aim")
	target.health = 1                             # this shot kills: see it break apart
	shooting._estimate.chance = 100
	shooting._fire()                              # not awaited: capture while it plays
	var t := 0.0
	for at: float in [0.05, 0.12, 0.2, 0.3, 0.5, 0.8, 1.3, 2.5]:
		await create_timer(at - t, false).timeout
		t = at
		await _shot("fire_%d" % int(at * 1000))
	quit()


func _look(rig, at: Vector3) -> void:            # frame a close-up
	rig._pivot = Vector3(at.x, rig._pivot.y, at.z)
	rig._current_pivot = rig._pivot
	rig._yaw = 200.0
	rig._current_yaw = 200.0
	rig._zoom = 0.0
	rig.view_pitch = 45.0
	rig._current_pitch = 45.0


func _shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("C:/some/folder/%02d_%s.png" % [shots, name])
	shots += 1
```

Other drivers used:

| To see | Drive |
|---|---|
| a walk | `controller.activate(moving)`, then `moving._move_to(tile)` (the tile from `moving._reach.steps`) |
| a strike | put a unit next to an enemy (`unit.global_position = ...`); give it a sword (`unit.melee_weapon = sword; unit.equipment.append(sword); unit._dress()`); `controller.activate(strike)`; `strike._estimate.chance = 100`; `strike._strike()` |
| a throw | give grenades (`unit.equipment.append(grenade); unit.grenade = grenade; unit._dress()`); `controller.activate(throwing)`; `throwing.set_process(false)`; `throwing._aim(tile)` (within 10 tiles); `throwing._throw_lined_up()` |
| a drop and landing | stand a unit on a crate (`grid.tile_position(crate + Vector3i.UP)`), then `map.get_node("TerrainDestruction").break_block(crate)` |
| a hop | `unit.walk([grid.tile_position(next_level_tile)], 0.2)` with a typed `Array[Vector3]` |
| an enemy turn with reactions | overwatch the squad (`OverwatchAction.handle_input()` with a pressed `confirm_action` `InputEventAction`), `TurnManager.end_player_turn()`, and when `Reactions.is_open()` call `Reactions._fire(member)` for a member in `Reactions._offers` |
| the cheer | `take_damage(100, ...)` on every enemy |
| cover stances | look at each unit in `LineOfSightTest.tscn` (its lanes put units in the open, behind half cover and at walls), printing `unit.model.cover` and `unit.model._base` |

Rendering a whole battle is slow; for logic, run the same probe `--headless --fixed-fps 60`, which is
deterministic and faster than real time.

### 14.4 The stress test

A headless probe that plays whole battles: each squad member shoots if it can, sometimes throws or
overwatches, else advances; the turn ends; reactions are fired as windows open; until one side is gone.
With seeds 7, 21 and 99 on `BoundaryMap.tscn` every battle was won in 3-4 turns with no script errors
(4, 5 and 4 bodies on the ground). Seeding the global generator replays a battle exactly, so a change
that breaks something shows up as a different result or an error.

---

## 15. Known gaps and limitations

### What is missing

- **Enemies never strike or throw.** Their AI only shoots, so no enemy figure draws a sword or
  readies a grenade, though the same figure can.
- **One figure for every unit.** Only `BaseCharacter.vox` has a layout; armor does not show; a
  character's colour is the only thing that tells the squad apart.
- **No wounded idle, no reload** (there is no ammo), no idle fidgets beyond breathing and drift, no
  turn-in-place steps, no start or stop transitions on the run, no walk gait.
- **No death animations:** deaths are physics only, and the knock is the same for every weapon and
  ignores where the hit landed.
- **Only one way to throw** (left-handed, overhand) and **one strike** (a diagonal slash).
- **Hand-keyed clips are not supported by the bake** (13.9).
- **Props are posed by kind** (rifle grip and foregrip, sword grip). A gun shaped very differently (a
  pistol) needs its own poses, not just a model. The rifle's foregrip comes from `Rifle.tscn` alone.
- **No weapon drop:** a body keeps its gun in its dead hand.
- **The shortsword's `Tip` marker** is unused (no trails or hit sparks).
- **No sound** (out of scope for the project).

### Rough edges

- **Feet slide** when a figure turns on the spot (600° a second, no stepping).
- **Hit flinches and the recoil are subtle** at the default zoom.
- **Hands drift off the rifle** during the 0.22 s base-pose cross-fades, which blend joint rotations.
- **The left palm can stop up to a voxel short** of the foregrip where a pose is out of reach (0.15
  at most in the rifle's clips now).
- **The stock overlaps the chest** in the aim (about a voxel).
- **The slung rifle's muzzle stands above the left shoulder**, level with the top of the head: the
  rifle is 18 voxels long, and slung lower its stock would sink into the grenades on the belt.
- **Joints open or overlap visibly when bent hard**, as rigid parts do: elbows, knees and shoulders
  with the arms raised.
- **The aim modifier bends only the spine and chest.** Steep aims look stiff, and the pitch is
  measured from 1.25 cells above the feet, not from the muzzle, so the rifle points only roughly at a
  target well above or below.
- **The head look** at the nearest foe ignores line of sight, and is limited to 70° and 35°.
- **Step-outs are tuned for a one-tile sidestep**; a diagonal step blends two cycles; a long strafe
  would shuffle.
- **Hops** use the same arc and pose for every height (a two-level drop and a one-level climb look
  alike), and a walk's drop has no landing squash (only a fall does).
- **The hop and fall poses** let the rifle swing with the right hand (the left lets go).
- **The draw and stow** blend two whole poses with the hand re-solved; the gun appears on the back at
  the swap.
- **Cover:**
  - the stance follows the nearest foe by distance, not threat or sight;
  - in high cover the figure faces the wall rather than turning its back to it, as XCOM 2's
    soldiers do;
  - overwatch in high cover looks like no overwatch;
  - a figure readied for an action ignores cover until it stands easy.
- **Breaking apart:**
  - no fall is played: the figure bursts where it stands and its pieces drop;
  - a bent joint's two bones share a little room, so their lumps can start overlapping and push apart
    as they are let go;
  - lumps are drawn a block's voxels across (0.0625), a shade smaller than the figure's (0.063);
  - the lumps and gear stay for the battle and a living unit can stand in them; gear cannot be picked
    up, and armor, which does not show, does not drop;
  - some 60 to 90 lumps a death cost physics until they sleep, in 2 to 3 seconds.
- **The cheer** only plays for the winners while the banner is up, then the battle closes.
- **The editor** shows units in the tree's first base pose (`stand_rifle`) and without props, since
  the tree is active in the scene and props are added at run time.
- **Forgetting to bake** after editing the `.vox` leaves the old rig in play. The plain import of
  `BaseCharacter.vox` still runs on re-export and is unused.
- **A model drawn in an A-pose**, or with hands not running along x, would need new grip bases.
- **The preview tool** shows the figure in its own grey, not a unit colour.
- **The belt shows at most three grenades** (`BELT`).
- **Clipping here and there:** an arm against the head in some poses, belt grenades against the arms,
  the slung sword against the slung rifle (never both at once).

---

## 16. Gotchas and troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Could not find type "CharacterModel"` (or another new class) | a new `class_name` script created outside the editor is not in the class cache | `--headless --path . --import` once |
| My edit to `BaseCharacter.tscn` or the animations vanished | the bake regenerates the scene and both `.res` | change the scripts, not the outputs; for hand-made clips see 13.9 |
| The open editor overwrote the new scene | it held the old one and was saved | reload changed scenes in the editor instead of saving them |
| A new clip never plays | not in the tree (missing from `STANCE_POSES`, `RIFLE_POSES`, `MELEE_POSES`, `ACTS` or `REACTS`), not baked, or never requested by `CharacterModel` | add it, bake, and request it (`_base_pose()`, `_act()`, `_react()`) |
| A tree input plays nothing (the figure snaps to the rest pose) | a name in `base_poses()` with no clip of that name | add the clip in `make_library()` for every stance |
| An arm twists 180° or bends backwards | the IK pole points to the wrong side | flip or rotate the pole (section 6.2's table) |
| A kneeling knee points up | the leg's default pole is forward and up | pass `knee = Vector3(0, -1, 0.7)` (as `_crouch` does) |
| Hands off the rifle in a new pose | out of reach (8-voxel arms) | bring the rifle closer to the shoulders, or check the foregrip; preview from the side and the front |
| A hand inside the head | the head is 7 voxels wide (x ±3.5) and starts at y 20 | keep raised hands at \|x\| ≥ 5.5 to 6.5 |
| A limb flips mid-animation | two keys on opposite quaternion hemispheres | `_sample()` handles it; only a concern if you key by hand |
| The strafe pose flashes during ordinary walks | the run's blend position fed the velocity while turning | it is forward (0, 1) unless the walk keeps its facing; keep it so |
| Forward in a blend space is backwards | `Vector2.UP` is (0, -1) | write `Vector2(0, 1)` |
| Changing a fade or filter at run time changes every figure | the tree resource is shared | only set `parameters/...` per figure |
| Props missing in a probe | `equip()` before the figure was ready (no skeleton yet) | add it to the tree, await a frame, then equip |
| `does not have the same element type as the expected typed array` in a probe | a plain `[]` or literal passed to an `Array[Item]` or `Array[Vector3]` parameter | declare the array typed first |
| A `--script` run hangs | a script error inside `_initialize()` | always use `timeout`, read the error, fix |
| `Identifier not found: Campaign` in a probe | typing a variable as a class that uses an autoload | leave such variables untyped |
| A dying figure's lumps fly too far, or barely move | the knock | the `FIGURE_*` constants on `TerrainDestruction` (9.8); a blast's push is `Blast.IMPULSE` over the lumps' `density` in `Figure.tres` |
| A dead unit's figure just vanishes | no `TerrainDestruction` in the map, or its voxels cannot be read (no layout in `VoxelRig.LAYOUTS`) | add the node; add the layout |
| `Could not resolve external class member` as the game loads, and every script after it fails | a `preload()` of a destruction `.tres` in a script that chain reaches (`CharacterModel`) | load it at run time, as `FIGURE_DESTRUCTION` is |
| Headless runs log `Parameter "material" is null` | the dummy renderer and material overrides | spurious; ignore |
| The preview renders nothing or black | run with `--headless` | the preview needs a window |
| Process-time numbers swing 7-18 ms | windowed runs with the editor open: GPU pacing | measure headless (section 17) |

---

## 17. Performance

Measured on the development machine (RTX 3060 laptop), headless, `LineOfSightTest.tscn` with 15
animated figures:

| What | Cost |
|---|---|
| Process time, everything on | about **1.3 ms a frame** (0.08 ms a figure) |
| Process time before the rig existed | 0.08 ms a frame |
| All 15 `AnimationTree`s | about 0.1 ms |
| All 15 aim modifiers | about 0.05 ms |
| All 15 `CharacterModel._process`es | about 0.25 ms |
| One `Postures` run (every 0.2 s) | 0.13 ms |
| The skinned mesh | 552 vertices a figure |
| The library | 38 clips, 384 KB (binary) |
| A bake | a few seconds (the library itself about 80 ms) |
| A death, breaking apart (`BoundaryMap.tscn`) | about 1.6 ms on its frame: the lumps cut 0.7, made 0.6, the gear 0.1; about 3.8 with blood, which stains the killing wound at once |

Windowed process times are dominated by GPU frame pacing (they swung between 7 and 18 ms even at the
commit before the rig, with the editor open), so measure CPU costs headless, and time a single
suspect call with `Time.get_ticks_usec()` before trusting a toggle-it-off comparison.

---

## 18. Every file involved

### New

| File | What it is |
|---|---|
| `vcom/Scripts/Characters/VoxelRig.gd` | skeleton, layouts, voxel assignment, mesher (and the ragdoll builder, until the dead broke apart) |
| `vcom/Scripts/Characters/HumanoidAnimations.gd` | every animation, the IK, the sampler, the blend tree |
| `vcom/Scripts/Characters/BakeCharacter.gd` | the bake (section 7) |
| `vcom/Scripts/Characters/CharacterModel.gd` | the figure's runtime (`class_name CharacterModel`) |
| `vcom/Scripts/Characters/AimModifier.gd` | aim pitch and head look (`SkeletonModifier3D`) |
| `vcom/Scripts/Characters/Postures.gd` | the cover and facing map node (`class_name Postures`) |
| `vcom/Scripts/Characters/PreviewAnimations.gd` | the preview tool |
| `vcom/Scripts/Characters/FigureVoxels.gd` | the figure's voxels at run time, for blood and breaking apart (sections 9.12, 9.8) |
| `vcom/Resources/Destruction/Figure.tres`, `Gear.tres` | how a figure breaks apart, and how the gear it drops wears (9.8) |
| `vcom/Scripts/Combat/MuzzleFlash.gd` | a gun's flash (`class_name MuzzleFlash`) |
| `vcom/Characters/BaseCharacterBody.res` | **generated**: the skinned mesh |
| `vcom/Characters/BaseCharacterAnimations.res` | **generated**: the animation library |
| `vcom/Items/Rifle2.vox`, `Shortsword2.vox`, `StickGrenade.vox` (+ `.import`) | the props, imported at 0.063 (they replaced the placeholders `Rifle.vox`, `Shortsword.vox`, `FragGrenade.vox`) |
| `MagicaVoxel/Rifle2.vox`, `Shortsword2.vox`, `StickGrenade.vox` | the props' source copies |
| `vcom/Scenes/Props/Rifle.tscn`, `Shortsword.tscn`, `FragGrenade.tscn` | the prop scenes and markers |
| `ANIMATIONS.md` | this file |

(Each new `.gd` has its `.gd.uid` beside it.)

### Changed

| File | Change |
|---|---|
| `vcom/Scenes/BaseCharacter.tscn` | **generated** now: was a plain `MeshInstance3D` of the imported `.vox`; is the rig |
| `vcom/Scenes/SquadUnit.tscn`, `CombatMap.tscn`, `BoundaryMap.tscn`, `LineOfSightTest.tscn` | each unit's `Mesh` child is now `Model`, its `surface_material_override/0` now `body_material`; the three maps gained a `Postures` node |
| `vcom/Scripts/Unit.gd` | `model`; `PICK_RADIUS`; presentational calls (`aim_at`, `aim_point`, `ready_strike`, `ready_throw`, `stand_easy`, `celebrate`, `dodge`, `recover`); `take_damage(amount, from, blasted)`; `shoot_at` takes aim, fires the figure, ducks misses; `strike` is a coroutine landing at the swing's impact; `throw_at` winds up and releases from the hand (`show_flight` gets the release point); `die` leaves the body as a ragdoll (since: the figure breaks apart, 9.8); `walk`/`start_walk` take `keep_facing`; `drop_to` sets the figure falling; `use_up` re-dresses; `_dress`, `_paint`, `_add_bodies` and `color` work through the figure |
| `vcom/Scripts/Items/Item.gd` | `model: PackedScene` |
| `vcom/Resources/Rifle.tres`, `Resources/Items/Shortsword.tres`, `Resources/Items/FragGrenade.tres` | `model` points at the prop scenes |
| `vcom/Scripts/Actions/MoveAction.gd` | `seconds_per_step` 0.12 → 0.2 |
| `vcom/Scripts/Actions/ShootAction.gd` | aims the figure while a target is lined up; steps out and back keeping its facing; stands easy on `end()` |
| `vcom/Scripts/Actions/StrikeAction.gd` | readies the figure; awaits the strike and `recover()`; stands easy on `end()` |
| `vcom/Scripts/Actions/ThrowGrenadeAction.gd` | readies the figure (at `begin()` and on each aimed tile); `_fly` flies from the hand as the grenade's model; stands easy on `end()` |
| `vcom/Scripts/Combat/ShotPlayback.gd` | aims before stepping out; steps keep their facing; stands easy after |
| `vcom/Scripts/Combat/Ballistics.gd` | `Outcome.muzzle` |
| `vcom/Scripts/UI/ShotOverlay.gd` | tracers start at the muzzle |
| `vcom/Scripts/Combat/ThrownGrenade.gd` | `show_model()`, `fly(throw, release)` easing from the hand, tumbling about the model's middle |
| `vcom/Scripts/TurnManager.gd` | the winners celebrate |
| `vcom/Scripts/Terrain/TerrainDestruction.gd` | blasts threw fallen bodies (`CharacterModel.blast()`); `_blast_box()`; since, breaks a dying unit's figure apart (`break_figure()`, 9.8) |
| `CLAUDE.md`, `README.md` | documentation |

### Unchanged but related

- `vcom/Characters/BaseCharacter.vox`: the model, unchanged.
- `vcom/Characters/BaseCharacter.vox.import`: the plain import, now unused.
- `vcom/addons/MagicaVoxel_Importer_with_Extensions/`: its reader is reused by `VoxelRig`.
- `vcom/Scripts/Terrain/Blast.gd`: its `impulse_on` and `contact` were reused for ragdoll bodies.

---

## 19. History: how this was built

The request was: *"Fully rig and animate the character models. Include all relevant animations. Ask
any relevant questions."* The project's todo listed "Characters and animations", and
"Claude Max best-attempt at animations (just to see what it can do)".

1. **Survey.** The model was found to be a single-colour T-pose mannequin, 536 grey voxels, worn by
   every unit. Units never turned, slid between tiles, and shot, struck and threw with no body
   motion. Every place in the code where a unit acts was read (section 2's table). The inspiration
   art, the importer's axis mapping and Godot 4.7's skeleton and animation classes were checked (it
   has `TwoBoneIK3D`, `LookAtModifier3D`, `AimModifier3D`, `PhysicalBoneSimulator3D` and GDScript
   `SkeletonModifier3D`s). The battle was rendered: figures were about 40 pixels tall at default
   zoom, so poses had to be bold.
2. **Questions.** The four in section 2. Answers: placeholder props, 0.2 s a tile, ragdolls, cover
   stances.
3. **The rig.** `VoxelRig` was written, and the first renders showed rigid skinning working (arms
   lowered, an elbow and a knee bent cleanly).
4. **A ragdoll test** in a probe: knocked back against a crate, it slumped and settled in about three
   seconds under Jolt, without exploding.
5. **Props.** Designed in item space and written as `.vox` by a Python script, with the grip at the
   box's centre; imported at 0.063; scenes made with `Muzzle` and `Foregrip` markers.
6. **The animations.** `HumanoidAnimations` was written: pose functions, the two-bone IK, key tables,
   the sampler and the tree. Working out arm reach first showed the 8-voxel arms could only hold the
   rifle two-handed under the chin with the off hand on the magazine.
7. **Contact sheets** of every clip from several views, and fixes:
   - the kneel's knee pole;
   - the cheer's fists in the head;
   - IK targets moved out of the head and into reach for the sword;
   - the run's stride constant;
   - type-inference errors in GDScript.
8. **The bake and the runtime.** `BakeCharacter`, `CharacterModel`, `AimModifier`, `MuzzleFlash`,
   `Postures`; `Item.model`; the `Unit` integration; actions, `ShotPlayback`, `TurnManager`,
   `TerrainDestruction`, `ShotOverlay`, `ThrownGrenade`; the scenes renamed `Mesh` to `Model` and
   gained `Postures`.
9. **In-game checks** in `BoundaryMap.tscn` and `LineOfSightTest.tscn`:
   - idle and walking;
   - a shot that kills (aim, tracer from the muzzle, ragdoll, re-aim at the next target);
   - a rifleman's strike (draw from the back, impact frame, stow);
   - a throw (ready, wind-up, release from the hand, tumbling model, blast, ragdoll);
   - cover stances;
   - an enemy turn with overwatch reactions;
   - a hit, a miss, a drop off a broken crate and a landing;
   - the victory cheer;
   - hops;
   - a step-out from a wall.
10. **Tuning.**
    - The death knock: bodies stood stiffly for a third of a second; a stronger knock with the
      shins kicked the other way made them drop at once.
    - The flinch was made about 1.6 times stronger.
    - A stand-easy deferred to the end of the frame, so a re-begun Shoot never lowers the gun.
    - Paused time no longer counts while waiting for a turn.
    - Each battle's first facing snaps.
    - The corpse clean-up moved to a `Timer` that dies with the body.
11. **Performance** (section 17), **stress tests** (three seeded auto-battles), headless loads of every
    scene, and documentation in `CLAUDE.md` and `README.md`.
12. **This file**, and `PreviewAnimations.gd` so anyone can look at clips.

### The explanation given when asked "How did you create these animations?"

> I wrote them all myself, in code. Nothing came from outside the project: no downloaded packs, no
> Mixamo, no motion capture, and no Blender, which isn't installed here. Every animation is a GDScript
> function in `Scripts/Characters/HumanoidAnimations.gd`, and `BakeCharacter.gd` turns them into an
> ordinary Godot animation library. The motion itself comes from what I know about how these movements
> work: the phases of a run cycle, how a soldier holds a rifle, the wind-up before a throw.
>
> **How I chose which animations:** I read every place in the code where a unit does something and
> listed what it would need to be seen doing (section 2's table). Equipment tags gave the three
> versions (rifle, sword, unarmed). Your answers settled ragdoll deaths, cover stances and props. XCOM
> conventions filled in the rest, like aiming while you pick a target.
>
> **How they're built:**
> 1. **The rig.** I printed the model's voxels as text views from the front and side to see where the
>    legs, torso, arms and head are, then wrote boxes that give each voxel to one bone.
> 2. **Each animation is a function of time that returns a pose.** It places the feet and hands and
>    leans the body, rather than setting joint angles directly.
> 3. **Inverse kinematics fills in the limbs.** Given where a hand or foot must be and which way the
>    elbow or knee should point, a two-bone solver works out both joint rotations. For the rifle, I
>    place the rifle in front of the chest, and the arms are solved to its grip and its `Foregrip`
>    marker. Because limbs are solved for this model's bone lengths, a re-bake for a model with
>    different proportions still lands feet on the floor and hands on the gun.
> 4. **Loops use sine waves; one-off moves use keyframe tables**, eased between.
> 5. **The bake samples each function 30 times a second** into Godot rotation tracks, then strips keys
>    that add nothing. The moments the game waits on are stored as metadata on the clips.
> 6. **Some motion isn't keyframed at all.** Turning, run speed, hops over ledges, the spine bending to
>    aim, the head watching the nearest enemy, and deaths are computed live each frame. The hit, duck,
>    recoil and landing are small changes added on top of whatever the body is doing.
>
> **How I knew they looked right:** I can't watch them play, so I rendered frames to images, laid them
> out in grids, and looked. Several first attempts were wrong and got fixed that way: the "kneel" was
> a squat until I changed which way the knee points, the cheer's fists were inside the head, bodies
> stood stiffly before falling, and the 8-voxel arms decided where the rifle could be held.
>
> **What that means for you:** this is careful programmer animation, not an animator's work. It's
> tuned to read on 40-pixel figures, but a hand-keyed version would have more weight and nuance. The
> numbers are my judgement and easy to change: edit them and re-bake. If you'd rather hand-animate,
> the rig is a standard Godot skeleton, so animations keyed in the editor would work; they'd need a
> second library, since the bake overwrites this one. The bones use Godot's standard humanoid names,
> so retargeting outside animations is possible in principle; the chibi proportions would make that
> rough.

### The summary given when the work was finished

> Every unit is now a rigged, animated figure, verified in renders and in three seeded auto-battles
> played to the end with no script errors.
>
> - **Rig:** a bake tool turns `BaseCharacter.vox` into an 18-bone skeleton (Godot's standard humanoid
>   bone names). Every voxel moves with exactly one bone, so limbs stay solid blocks. Each unit also
>   gets a 12-body ragdoll and sockets for its gear.
> - **Animations (38):** idle, run, kneel behind half cover, brace at full cover, aim, fire, overwatch,
>   step-out strafes, sword draw/strike/stow, grenade ready and throw, flinch, duck, hop up and down
>   ledges, fall and land, and a cheer, in rifle, sword and unarmed versions. They're written in code
>   with inverse kinematics, so a re-bake for differently proportioned models keeps feet on the floor
>   and hands on the rifle.
> - **In play:** figures turn to face where they walk and what they aim at; a unit raises its rifle
>   while you pick a target and follows it as you Tab; a step-out keeps the gun on the target; tracers
>   start at the muzzle, with a flash; the legs follow actual speed, so reaction slow-motion slows them
>   and a held walk freezes them mid-stride; a rifleman draws the sword off his back and the hit lands
>   on the swing's impact frame; a grenade leaves the hand at release; the winners cheer.
> - **Your choices, as applied:** placeholder props; 0.2 s per tile for everyone; ragdolls knocked the
>   way the hit came, staying for the battle, flung by later grenades; cover stances toward the nearest
>   enemy, standing back up if the crate is shot away.
> - **Rules unchanged:** everything is visual; the figure only decides when a shot fires, a blow lands
>   or a grenade leaves the hand, never the outcome.

### Later: the dead break apart (2026-10-02)

With blood in place, the user asked: *"Characters should break apart on death. When a character dies,
whether it is a player character or an enemy, instead of ragdolling the character's voxel model,
break that model apart similarly to how blocks are broken apart dynamically."* Four questions were
put, and the recommended answer taken for each (section 12, decision 31): chunks like a block's; the
same with blood off; gear dropped whole, wearing away later; the pool where the unit stood. Taken as
read too: it breaks the moment it dies, from the pose it is in, with no ragdoll first; the pieces fly
the way the blow went (back from a shot, out from a grenade, along a blade's swing); they are debris
for show only and stay; stained voxels stay red; no global random numbers.

1. **The figure into lumps.** `FigureVoxels.crumble()` cuts the posed figure as `VoxelTerrain`
   crumbles a block, a bone at a time; `TerrainDestruction.break_figure()` knocks the lumps and makes
   them `VoxelDebris`. The killing hit is kept on the unit for it.
2. **The gear dropped whole**, as rigid bodies that wear like a crate's boards. `VoxelBody` learnt the
   props' scale (0.063 against a block's 0.0625) so a worn prop is redrawn, collided and stained where
   its mesh was, and to take over the blood the prop carried.
3. **The ragdoll removed** from the bake, the figure and the blast; the figure rebaked (only the
   `Ragdoll` nodes left the scene).
4. **Blood**: the pool moved to where the unit stood, a second after the death; a killing wound
   stained at once, so the lumps come out red.
5. **Checked** by probes (the lumps, gear and pool for a round, a blade and a blast; the global
   generator untouched; dropped gear shot through and blasted; blood off) and renders of each.
   `crumble()` was cut from 1.6 to 0.7 ms by keeping each bone's cells in the rig.

---

## 20. Glossary

| Term | Meaning here |
|---|---|
| **Act** | a one-shot clip played whole over the base pose (`act` in the tree): strike, throw, draw, stow |
| **Additive** | a clip that is a change from the rest, added on top of other animation (`react`) |
| **Bake** | running `BakeCharacter.gd`: `.vox` → rigged, animated scene |
| **Base pose** | a looping clip held between actions, picked by `stance` (19 of them) |
| **Body material** | the flat-colour material a unit puts over its figure (`CharacterModel.body_material`) |
| **Cell / tile** | one Godot unit: a tile is a cell a unit can stand in; about 15.87 voxels |
| **Chest space** | the `Chest` bone's own frame, turning with the torso; where rifle and sword poses are placed |
| **Lumps** | what a dead unit's figure breaks into, voxel debris (9.8); the dead were ragdolls before |
| **Effector** | the point on the end bone that IK puts on the target (a palm, an ankle) |
| **Figure** | a unit's rigged model, `CharacterModel` (a unit's `Model` child) |
| **Foregrip** | where the off hand holds the rifle (a marker in `Rifle.tscn`) |
| **Grip** | where a hand holds a prop: the prop's origin; also the hand-to-prop transforms (`rifle_grip`…) |
| **Hands (stance)** | the stance the hands are in now: `melee` while a gun carrier's sword is drawn, else its stance |
| **Layout** | a model's joints and voxel regions (`VoxelRig.BASE_CHARACTER`) |
| **Model voxels** | MagicaVoxel's own voxel coordinates (z up, face toward -y) |
| **Pole** | the direction an elbow or knee points, for IK |
| **Pose** | every bone's rotation plus root and hip offsets at one moment (`HumanoidAnimations.Pose`) |
| **Posture** | how an idle figure stands: cover and facing, set by `Postures` |
| **Prop** | a held or carried item's model (`Item.model`) |
| **React** | an additive one-shot (`react` in the tree): fire, hit, dodge, land |
| **Readiness** | what a figure has made ready: `NONE`, `AIM`, `MELEE`, `THROW`, `CHEER` |
| **Rig voxels** | Godot's axes in voxel units, origin under the figure (section 4) |
| **Socket** | a node under a `BoneAttachment3D` where a prop is put |
| **Stance** | what the hands hold: `rifle`, `melee`, `unarmed` |
| **Swap** | the moment in a draw or stow when the sword and gun change places |
