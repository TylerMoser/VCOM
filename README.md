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
| Overwatch | Select **Overwatch** to see the ground it covers, `Enter` or `Space` to go on overwatch |
| React | During a reaction window: `1`–`4` fires that squad member, `0` lets the move carry on |
| Show the hit breakdown | Hold `Ctrl` while aiming |
| Cancel the current action | `Esc` |
| End the turn early | Hold `Shift` |

While Shoot is active, `Tab` cycles targets rather than squad members.

## Combat rules

### Action points

Every unit gets **3 actions** a turn. Moving costs one action per `move_range` (4) tiles of path,
so a long walk can cost two or three. Shooting costs one. The player's turn ends when every member
has spent their budget, or early by holding `Shift`.

### Reactions and overwatch

As in Pathfinder, every unit also gets **one reaction**, shown as the triangle beside its action
circles. Reactions are taken outside the unit's own turn, in answer to something another unit does,
and the unit gets its reaction back at the start of its turn.

**Overwatch** spends all the actions a unit has left and holds its reaction, for a shot at an enemy
moving across the ground it can see (marked in gold while the action is selected). The triangle has
a pale rim while it is held, and overwatch ends when it fires or when the unit's next turn starts.

**Reactions never go off by themselves.** When an enemy moves where squad members on overwatch can
see it, a *reaction window* opens:

- The move drops to **slow motion** (10% speed) and the camera pulls up to an angled top-down view
  of the enemy and everyone who could fire at it.
- Beside each of them is a number, `1`–`4`, their place on the squad panel, and the odds of their
  shot. The odds move as the enemy does; the number shown when the key goes down is the one rolled.
- Pressing a number fires that squad member: the enemy freezes while the shot plays out, then carries
  on. Their reaction is spent and their prompt goes.
- Pressing `0` lets the move play out at normal speed without firing.

Prompts come and go as the enemy moves in and out of sight, and the window closes when no one has a
shot left or the enemy stops moving; a standing enemy cannot be fired on. Every move is a new
trigger with the prompts back up, so the player can let an enemy come closer, or out of cover,
before choosing to fire. The camera goes back to its normal view when that enemy's turn is over.

A reaction shot costs **15 aim** (the **Reaction** term below), for being snapped off at a moving
target. Only walking sets off a window; leaning out of cover to shoot does not.

### Enemies

Enemies play by the squad's rules: an action per 4 tiles walked, one per shot, and they walk into
overwatch the same way. What each one does with its actions is its AI's call. Every enemy so far
uses the **assault** AI, which takes, for each action, the first of these it can do:

1. **Next to a squad member it can shoot:** shoots them. Once it gets there, every action it has
   left goes on them.
2. **Any action but its last:** moves as close as it can get to the nearest squad member, up to 4
   tiles. Nearest counts steps walked, not distance as the crow flies.
3. **Its last action:** shoots whoever it has the best odds on, or moves closer if it cannot see
   anyone.

"Next to" means one tile away in any of the eight directions, at most a level up or down. An enemy
that cannot get any closer shoots rather than waste the action.

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
Aim − Evasion − Cover + Flanking + Height − Distance − Reaction
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
| **Reaction** | the shot is a reaction, such as overwatch fire | −15 |

Height tells both ways: shooting uphill costs exactly what shooting down gains. Distance is stepped
rather than continuous, so the number holds still while you shuffle about within a step — 0–3 tiles
is free, 4–7 costs one step, and so on.

Hold `Ctrl` while aiming to see the sum itself, one line per term that mattered.

Every shot that lands deals its weapon's damage (a rifle does 4 against 10 health). There are no
critical hits yet, and damage does not vary.

### Where shots go

Every shot is drawn as a tracer, and its result, damage included, is called when the round arrives.
A hit flies straight along the sight line into the target, so it never touches terrain.

A miss still goes somewhere, as in XCOM 2. Once the roll has said it misses, the round is aimed at a
point near the target (above or beside its body, never through it) and flies on until it strikes
something solid or leaves the map. When the target has cover facing the shot, about a third of misses
are aimed at that cover instead. With the misses that clip it anyway, around half of all misses
against a target in cover strike the cover.

- **A stray round never hurts anyone.** It never passes through another unit, friend or foe, unless
  that unit is standing right in the line of fire, where any round passes through it because units
  never block sight.
- **A miss never lands well short of the target**, no more than 2 tiles in front of it.

Where a miss strikes terrain it leaves a mark and is reported to the map with the weapon's
environmental damage (5 for a rifle).

### Destructible terrain

**Crates break.** A crate struck by a stray round is gone the moment the round arrives: sight,
cover and paths change at once, so an enemy crouched behind it is in the open for the next shot.
What is left of it collapses to the ground in pieces.

- **Stacks come down together.** Anything breakable stacked on a broken crate breaks too.
  Unbreakable blocks stay where they are.
- **A soldier on a crate falls.** Anyone left standing on nothing drops to the ground below.
- **The pieces are only for show.** They are real physics debris that stays for the rest of the
  fight and bumps off soldiers, but they never block sight, give cover or get in anyone's way.

Grass and the ground do not break.

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

**Where a miss goes is settled when it is fired, XCOM 2's way.** XCOM: Enemy Unknown flew a real
projectile and damaged whatever it bumped into on the way; XCOM 2 works the whole path out first and
has the tracer play it back. The path is traced through the same voxel grid as sight, with no
physics, so it is decided before anything is drawn, can be tested headless, and can never pass
through a block the grid says is solid.

**The rules never wait on physics.** A broken block leaves the grid the instant it is struck, and
its debris is physics for the eye only. The fight stays exactly as predictable as before, however
the pieces happen to fall.

**Breakable blocks are data.** How a block breaks is a resource naming it, and a new breakable
object is a pre-cut MagicaVoxel model plus one of those. No code changes are needed.

**Death removes a unit at once.** A fallen unit leaves its groups immediately rather than when the
node is freed, so nothing shoots at it or paths around it in the meantime.

**Enemy AI only decides.** An AI looks at the fight and names one action at a time — walk here,
shoot that — and the turn manager carries it out and charges for it. Walking, shooting, reactions
and the camera are the same code for every kind of enemy, so a new enemy type is a new decision
routine and nothing else.

**A wiped squad stops the clock rather than looping.** With no one left to give orders to, nothing
ends the turn either, so the turn loop simply holds still. A proper defeat state comes later.

## Layout

```
vcom/                     the Godot project
  Scripts/
    Unit.gd               health, actions, reaction, movement, taking a shot
    PlayerSquad.gd        the squad and which member is selected
    TurnManager.gd        turn order, and carrying out what enemy AI decides
    Reactions.gd          the reaction window: slow motion, prompts, reaction fire
    CameraRig.gd          orbiting tactical camera, and the framed reaction view
    Combat/
      CombatGrid.gd       tile queries, pathfinding, the sight-line ray, ray casts, terrain strikes
      LineOfSight.gd      cover, stepping out, who can see whom
      HitChance.gd        the to-hit sum, and the roll
      Ballistics.gd       where a round goes, hit or miss
      ShotPlayback.gd     plays out enemy fire and reaction fire
      Weapon.gd           what a shot does when it lands, to units and to terrain
      TileHighlights.gd   coloured squares over tiles
    AI/                   enemy AI: the base, the assault AI, and the queries they share
    Terrain/              destructible terrain: what breaks, how, and what it brings down
    Actions/              the action bar's actions: Move, Shoot, Overwatch
    UI/                   HUD, built in code rather than scenes
  Resources/              shared weapon and AI resources units are given
    Destruction/          what breaks and how: one resource per breakable block, and the catalog
  Scenes/
    CombatMap.tscn        the playable map
    LineOfSightTest.tscn  harness for the sight and shot rules
    Destruct_*.tscn       the pieces a breakable block breaks into
MagicaVoxel/              source .vox art
```

## Credits

Map assets  by Penflower Ink, 2025, www.penflower-ink.com

Voxel models are imported with [MagicaVoxel Importer with Extensions](vcom/Addons/MagicaVoxel_Importer_with_Extensions).
