# VCOM

A turn-based tactics prototype in the vein of XCOM and Star Wars: Zero Company, built in Godot 4.7
on a voxel grid.

Squad members take on a map of enemies, a tile at a time: spend action points to move, take
cover behind terrain, lean out around it to find a firing angle, and roll against a percentage
chance to hit.

## Controls

| | |
|---|---|
| Pan camera | `WASD` / arrow keys, or push the cursor to a screen edge |
| Rotate / tilt | Hold `Q` / `E`, or drag with the middle mouse button |
| Zoom | Mouse wheel |
| Select a squad member | `Tab` / `Shift+Tab`, or left-click one |
| Move | Select **Move**, hold right-click to preview the path, release to walk |
| Shoot | Select **Shoot**, `Tab` / `Shift+Tab` to cycle targets, `Enter` or `Space` to fire |
| Show the hit breakdown | Hold `Ctrl` while aiming |
| Cancel the current action | `Esc` |
| End the turn early | Hold `Shift` |

While Shoot is active, `Tab` cycles targets rather than squad members.

## Combat rules

### Action points

Every unit gets **3 actions** a turn. Moving costs one action per `move_range` (4) tiles of path,
so a long walk can cost two or three. Shooting costs one. The player's turn ends when every member
has spent their budget, or early by holding `Shift`.

### The grid

The map is a `GridMap` of 1×1×1 cells. A tile is an empty cell with solid ground beneath it and two
cells of headroom — a unit fills its tile and the cell above. Units step to any of the eight
neighbours, climbing at most 1 level and dropping at most 2. Diagonal steps cost the same as
straight ones but cannot cut a corner.

### Line of sight and cover

Cover is whatever is solid beside a tile, on any of its four cardinal sides:

- **1 cell tall → half cover.** A unit sights from the centre of the cell above its own tile, so
  sight lines pass clean over anything only one cell high. Half cover costs the shooter aim but
  never blocks the shot.
- **2+ cells tall → full cover.** Tall enough to sit in the sight line and stop it dead.

**Stepping out.** A unit behind cover leans out to either side of it to shoot around it, exactly as
in XCOM, and the tile it leans to is marked on the map while you aim. The lean is played out: the
unit walks out, fires, and settles back into cover. Cover is what makes the lean possible — a unit
caught in the open has nothing to lean out from and fires from where it stands.

**Flanking** means the target is in cover but none of it faces your shot. A target standing in the
open is *not* flanked: there was nothing to get around.

Units never block line of sight; only terrain does. Sight is also slightly more permissive than
movement — a shot can thread a diagonal gap between two blocks that touch at a corner, which a unit
cannot walk through.

### Chance to hit

```
Aim − Evasion − Cover + Flanking + Height − Distance
```

clamped to 0–100. Every term is whole percentage points, and all of it is measured from **where the
shot is actually taken** — a unit leaning out of cover has its height and distance reckoned from the
tile it leans to.

| Term | Source | Default |
|---|---|---|
| **Aim** | shooter's stat | 90 |
| **Evasion** | target's stat | 0 |
| **Cover** | half cover / full cover | −20 / −40 |
| **Flanking** | target in cover that does not face the shot | +20 |
| **Height** | shooter's stat, per tile of elevation difference | ±5 per tile |
| **Distance** | shooter's stat, per *full* 4 tiles to the target | −5 per step |

Height tells both ways: shooting uphill costs exactly what shooting down gains. Distance is stepped
rather than continuous, so the number holds still while you shuffle about within a step — 0–3 tiles
is free, 4–7 costs one step, and so on.

Hold `Ctrl` while aiming to see the sum itself, one line per term that mattered.

Every shot that lands deals its weapon's damage (a rifle does 4 against 10 health). There are no
critical hits yet, and damage does not vary.

## Notable decisions

**Cover is read off whole cells, not thin walls.** XCOM puts cover on tile edges; here every
obstacle is a full voxel. Mapping "1 cell tall" to half cover and "2+ cells" to full cover means the
eye-height sight line reproduces XCOM's behaviour for free, with no separate cover data to author —
build terrain and the cover falls out of it.

**Sight lines are symmetric by construction.** Where a shot crosses two cell boundaries at once — a
diagonal — it cuts the corner rather than clipping the cells to either side. This is verified across
every pair of tiles on the test map: if A can see B, B can see A, with no exceptions.

**The number you are shown is the number that is rolled.** The hit chance is worked out once, when
the shot is lined up, and kept until the trigger goes.

**Death removes a unit at once.** A fallen unit leaves its groups immediately rather than when the
node is freed, so nothing shoots at it or paths around it in the meantime.

**A wiped squad stops the clock rather than looping.** With no one left to give orders to, nothing
ends the turn either, so the turn loop simply holds still. A proper defeat state comes later.

## Layout

```
vcom/                     the Godot project
  Scripts/
    Unit.gd               health, actions, movement, taking a shot
    PlayerSquad.gd        the squad and which member is selected
    TurnManager.gd        turn order, and the placeholder enemy AI
    CameraRig.gd          orbiting tactical camera
    Combat/
      CombatGrid.gd       tile queries, pathfinding, the sight-line ray
      LineOfSight.gd      cover, stepping out, who can see whom
      HitChance.gd        the to-hit sum, and the roll
      Weapon.gd           what a shot does when it lands
      TileHighlights.gd   coloured squares over tiles
    Actions/              the action bar's actions: Move, Shoot
    UI/                   HUD, built in code rather than scenes
  Scenes/
    CombatMap.tscn        the playable map
    LineOfSightTest.tscn  harness for the sight rules
MagicaVoxel/              source .vox art
```

## Credits

Voxel models are imported with
[MagicaVoxel Importer with Extensions](vcom/Addons/MagicaVoxel_Importer_with_Extensions).
