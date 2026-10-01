# VCOM

A turn-based tactics prototype in the vein of XCOM and Star Wars: Zero Company, built in Godot 4.7
on a voxel grid.

Squad members take on a map of enemies, a tile at a time: spend action points to move, take
cover behind terrain, lean out around it to find a firing angle, and roll against a percentage
chance to hit.

## Controls

Letter keys go by where they sit on the keyboard, not what is printed on them, so `WASD` is `ZQSD`
on an AZERTY keyboard. `Enter` and the number keys work on the number pad too.

`Esc` backs out one step at a time, on the world map and in combat alike: a path being previewed,
then the action that is up, then a village's menu. Only once there is nothing left to back out of
does it open the pause menu, and pressed again it closes it.

### World map

| | |
|---|---|
| Pan the map | `WASD` / arrow keys, push the cursor to a screen edge, or drag with the middle mouse button |
| Zoom | Mouse wheel, toward the point under the cursor |
| Send the party | Right-click anywhere on land. Right-click again on the way to send it somewhere else instead |
| Go to a village | Right-click its icon. The party goes to the village itself, wherever on the icon was clicked |
| See what is in a village | Hover over its icon |
| Use a village | Left-click its icon once the party is there, to open its menu |
| Open the pause menu | `Esc` |

The party is the only thing on the map that moves, so there is nothing to select first. A right-click
on the sea, or on land the party cannot reach, does nothing. The party has only arrived at a village
when it was sent there by a right-click on the icon, not somewhere near it.

#### Menus

The pause menu (its Campaign, Roster, Inventory and System tabs), a village's menu (a tab for each
place in it, such as the Hiring Board and the Market) and the roster that comes up before a battle
all pause the game behind them, and all work the same way.

| | |
|---|---|
| Change tab | Click it, or `←` / `→` while its row of tabs has the keyboard |
| Move between rows | `↓` / `↑`: from the tabs to any sub-tabs under them, to what is selected under those, and back |
| Move within a row or a grid | Arrow keys. Characters, items, slots and skills are selected as the keyboard reaches them |
| Press a button | Click it, or `Enter` / `Space` |
| Buy, sell, hire, or start a battle | Hold the button for 2 seconds, with the mouse or `Enter` / `Space`. One per press: let go and hold again for the next |
| Equip | On the Roster's Equipment page, pick a slot, then double-click an item under it, press `Enter` / `Space` on one, or press **Equip**. **Unequip** puts back what the slot holds |
| Choose who fights | Before a battle, double-click a character, or press `Enter` / `Space` on one, to tick or untick them (up to four), then hold **Start**. A single click only shows their pages |
| Close | `Esc`, or **Return to Game** on the pause menu's System tab. The roster before a battle cannot be closed: only **Start** leaves it |
| Quit the game | **Exit to Desktop** on the pause menu's System tab |

### Combat

| | |
|---|---|
| Pan the camera | `WASD` / arrow keys, or push the cursor to a screen edge |
| Turn the camera | Hold `Q` / `E` |
| Zoom | Mouse wheel |
| Select a squad member | `Tab` / `Shift+Tab`, left-click them, or click their card on the squad panel (bottom left) |
| Choose an action | Click its button on the action bar (bottom middle). Click it again, or press `Esc`, to put it away. **Move** is taken up whenever a squad member is selected |
| Move | Hold right-click to preview the path to the tile under the cursor, and let go to walk it. Let go off the tinted tiles, or press `Esc` while holding, to call it off |
| Shoot / Strike | `Tab` / `Shift+Tab` cycle targets, `Enter` / `Space` fires or strikes |
| Overwatch | `Enter` / `Space` goes on overwatch, for every action the squad member has left |
| Throw Grenade | Point at a tile to see the arc and the blast. Right-click it, or press `Enter` / `Space`, to throw |
| Show the hit breakdown | Hold `Ctrl` while a shot or a strike is lined up |
| React | During a reaction window, `1`–`4` fires the squad member with that number beside them (their place on the squad panel), and `0` lets the move carry on |
| End the turn early | Hold `Shift` for a second. Letting go, or pressing any other key, calls it off |
| Open the pause menu | `Esc`, with no action up |

While Shoot or Strike is up, `Tab` cycles targets rather than squad members. During the enemies'
turn only the camera, the reaction keys and the pause menu answer. The pause menu works as on the
world map, but equipment cannot be changed until the battle is over.

## The campaign

The game opens on the world map. Send the party anywhere on land, and open the village it is
standing in to use it (see [Controls](#world-map)). A village's Hiring Board has fighters for hire,
who join the end of the roster, and its Market sells its stock and, on its Sell tab, buys anything
in the inventory (not equipped) for half its price, rounded down. Every hire, purchase and sale
takes holding its button for two seconds, so a stray click never spends anything. Travelling
through a forest (the green areas) risks an ambush: every short stretch of the way has a chance to
start a battle.

Before it starts, the roster comes up to choose who fights: tick up to four, then hold **Start** for
two seconds (see [Menus](#menus)). It opens with the last battle's squad ticked, less anyone who
fell, and it cannot be closed any other way.
What happens to them in the battle lasts. Wounds carry into the next battle unless they heal first:
everyone on the roster heals a little (1 HP) for every short stretch the party travels, and a
character who dies is gone from the roster for good, their gear back in the inventory. The battle
ends when either side is wiped out: **Victory** or **Defeat**, then back to the world map where the
party was, still on its way. If a defeat took the last character on the roster, the campaign is
lost: **Game Over** comes up on the world map and the game closes.

Everyone still standing at the end of a battle earns 50 experience, and a victory earns the party 10
gold, plus a gold for every coin still lying on the field (see Coins, below). Every 100 experience
becomes a skill point (the rest carries over), shown on the Roster's Skills tab as "Skills (1)";
nothing spends them yet.

## Combat rules

### Actions and gear

Which actions a squad member has depends on what they have equipped. Everyone can **Move**.
**Shoot** and **Overwatch** need a gun (the Rifle) in a weapon slot. **Strike** needs a melee weapon
(the Shortsword) in a weapon slot, and is greyed out until an enemy stands next to the squad member.
A squad member with neither can only move. **Throw Grenade** needs a grenade (the Frag Grenade) in an
item slot. A thrown grenade is gone for good: its slot is empty after the battle, and the Market
sells more.

What a squad member carries shows on them: the gun in their hands, a sword slung across their back
(drawn when they line up a Strike), and their grenades on their belt until thrown. While you line up a
shot they turn to the target with their gun raised, and they run, hop up and down ledges, kneel behind
half cover and press up to full cover, facing the nearest enemy. The fallen go limp where they drop and
stay there, and a grenade throws them about. None of it changes the rules: a shot, strike or throw is
settled exactly as below, the moment the gun fires, the blade lands or the grenade leaves the hand.

### Action points

Every unit gets **3 actions** a turn. Moving costs one action per `move_range` (4) tiles of path,
so a long walk can cost two or three. Shooting costs one, and so do striking and throwing a grenade. The player's turn ends when every member
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

Every shot that lands deals its weapon's damage (a rifle does 4 against 10 health), less the
target's **Defense**, down to nothing: a rifle does 3 to a target with 1 Defense, and none to one
with 4. Everyone's own Defense is 0 for now; armor adds to it, Light Armor by 1. There are no
critical hits yet, and damage does not vary.

### Melee

**Strike** hits an enemy on one of the eight tiles around the striker, up to a level above or below.
Its chance to hit is the same sum with **Melee Accuracy** (90 by default, shown on the Roster's
Details page) in place of Aim, and nothing about the ground counting:

```
Melee Accuracy − Evasion
```

Cover, flanking, height and distance are all worth nothing in melee for now, and a strike is never a
reaction. The target panel reads **Melee** where a shot's shows the target's cover, and `Ctrl` shows
the sum as it does for a shot. A strike that lands deals its weapon's damage (the Shortsword does 4)
plus the striker's **Strength** (0 by default, also on the Details page), and only then is the
target's Defense taken off, as it is from a shot: a Shortsword swung with 3 Strength does 7, or 6
to a target with 1 Defense. Strength adds nothing to shots. A strike lands at once, with its damage
or **MISS** called over the target, and never touches the terrain.

### Grenades

**Throw Grenade** throws the first grenade a squad member carries (Item 1, then Item 2, then Item 3)
at a tile up to **10 tiles** away across the ground, for one action. While it is selected, every tile
it can reach is tinted faintly. Point at one to see the throw: its arc, the ground the blast covers,
and a bracket on everyone it would catch, with the damage each would take, red on enemies and gold on
the squad. Right-click the tile, or press `Enter` / `Space`, to throw.

- **The arc must be clear.** The grenade flies in an arc from over the thrower's head to the target,
  higher the further it goes. If anything solid stands in its way the arc turns red up to where it
  is stopped, with a cross there, and the throw cannot be made. Units never block it. It clears the
  thrower's own full cover, and drops behind half cover from the full 10 tiles, but it can never land
  right behind full cover: throw it a tile past whoever is hiding there and the blast still catches
  them.
- **Nothing is rolled.** A grenade always goes off where it is thrown.
- **The blast catches everyone in it**, friend or foe, the thrower included. It is a cube as tall as
  it is wide, centred on the target: the Frag Grenade's is **3×3** tiles across and reaches from the
  floor to head height, so it also catches anyone standing a level up or down. Anyone with any part
  of them inside it takes the grenade's damage (**5** for the Frag Grenade) less their Defense, as
  from a shot. Walls inside the blast shelter nobody.
- **It breaks every crate in the blast**, blows a crater in the grass and the trees there (see
  [Destructible terrain](#destructible-terrain)), and throws the debris there about. Crates stacked
  above the blast fall, and anyone left standing on nothing drops.
- **It is gone for good.** A thrown grenade is used up for the rest of the campaign; the Market
  sells more. With none left, the button leaves the action bar.

The throw range is the same for every squad member and every grenade (`Throwing.RANGE` in
`Scripts/Combat/Throwing.gd`); each kind of grenade sets its own blast size and damage.

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
environmental damage (5 for a rifle). Grass and trees are hit where the round actually meets them,
voxel by voxel: a miss that passes beside a tree's trunk, or through a hole blown in a wall, flies on.

### Destructible terrain

**Crates break.** A crate struck by a stray round, or caught in a grenade's blast, is gone the
moment the round arrives or the grenade goes off: sight, cover and paths change at once, so an enemy
crouched behind it is in the open for the next shot. What is left of it bursts apart, throwing its
boards a cell or two, and further when a grenade did it.

- **Stacks fall, then break.** A crate stacked on a broken one drops whole and breaks where it
  lands, bursting apart just the same, and so does everything breakable above it. They are gone
  from the fight the moment the crate under them is struck; the fall is only for show.
  Unbreakable blocks stay where they are, and so does whatever stands on them.
- **A soldier on a crate falls.** Anyone left standing on nothing drops to the ground below.
- **The pieces are only for show.** They are real physics debris that stays for the rest of the
  fight and bumps off soldiers, but they never block sight, give cover or get in anyone's way.
- **The boards break down further.** Once the crate has come apart, each of its boards wears away
  as a block does: a round flying through one tears a bite out of it, three voxels for each point of
  environmental damage, and flies on as if it were not there; a grenade's blast craters the boards
  within its reach. A board shot in two becomes two boards, a splinter too small to stand on its own
  falls as lumps, and a board worn below half of itself crumbles.

**Grass and trees wear away, a few voxels at a time.** Every block is 16 voxels to a side, and these
come apart into them:

- **A round takes a bite** where it strikes: about a dozen voxels for each point of the weapon's
  environmental damage (60 for a rifle), knocked out of the face it hit in small lumps that fall and
  stay where they land.
- **A grenade blows a crater**: every voxel in a ball round where it goes off, as big as its
  environmental damage makes it (a little over two tiles across for the Frag Grenade), but only within its
  blast. Its earth is thrown up and out round the crater.
- **Worn is not gone.** However chewed up it looks, a block still counts as the whole block for sight,
  cover and movement until it is **worn below half** of its voxels. Then it collapses: it is gone from
  the fight at once, what is left of it crumbles into lumps, blocks stacked on it fall, and anyone on
  it drops.
- **Cut through, it falls.** A block holding something up collapses as soon as nothing joins its bottom
  to its top: a tree's thin trunk, shot through, brings its crown down with it.
- **The ground never gives way.** The bottom of the map only craters, and only a quarter of a tile
  deep. Soldiers still stand at the ground's full height, so they float a little over a crater.
- **What falls off hanging** - a lump of earth left holding on to nothing - drops with the rest.

As with crates, the debris is only for show and stays for the rest of the fight. After a great deal of
destruction, the debris furthest from where the camera is looking stops moving, though it stays where
it lies; a blast, the ground going from under it, or a soldier walking into it sets it moving again.

### Coins

**Three crates in four leave a coin** where they broke, spinning in the air at the height of the
crate's top, or where a falling crate landed. Coins on the same tile stack up, and a coin whose
ground is shot away drops to the ground below.

- **Walk through a coin to take it.** A soldier takes every coin on each tile they pass through,
  ending their move there or not: along a path, stepping out of cover to shoot, or dropping when the
  crate under them breaks. Each is 1 gold for the party at once, "+1 Gold" over their head, and is
  kept even if the battle is lost. Enemies ignore coins.
- **A victory sweeps up the rest.** Every coin still on the field is the party's the moment the
  last enemy falls.

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
has the tracer play it back. The path is traced through the voxel grid, with no physics, so it is
decided before anything is drawn and can be tested headless. It goes through grass and trees voxel by
voxel, so a round hits the trunk it is drawn hitting, but sight and cover still read whole blocks.

**Blocks wear away, the rules see whole blocks.** A block losing voxels is drawn as what is left of it,
but sight, cover and movement still read whole cells, so the fight stays as predictable as XCOM's:
a wall is cover until it collapses, and it collapses at a clear point (half gone, or cut through),
decided the moment the round or grenade lands.

**The rules never wait on physics.** A broken block leaves the grid the instant it is struck, and
so does everything breakable stacked on it, even while those blocks are still to be seen falling;
its debris is physics for the eye only. The fight stays exactly as predictable as before, however
the pieces happen to fall.

**Breakable blocks are data.** How a block breaks is a resource naming it, and a new breakable
object is a pre-cut MagicaVoxel model plus one of those. A block that wears away a voxel at a time
needs only the resource: its voxels are read from the model it is drawn with. No code changes are
needed. By default the
pieces simply collapse; whether they burst apart instead is a tick box on the resource, and where
the blast goes off and how hard is a marker placed in the model's scene. Whether the pieces then wear
away themselves is one more setting on it, how soft they are: their voxels are read from the models
they are drawn with, as a block's are.

**Any voxel model can wear away, not just blocks.** A crate's boards are the first loose models to:
pieces of debris that rounds and blasts eat into a few voxels at a time, which split in two when cut
through and crumble when worn down. Like all debris they are only for show, so a round tears through
them and flies on, and the rules never see them.

**A blast pushes like a real one.** Its push fades with the square of the distance, and each piece
catches it in proportion to the area it turns toward the blast. So the boards nearest and facing it
fly furthest, one edge-on to it far less, and every piece tumbles as it goes.

**A blocked throw is not thrown.** In XCOM 2 a grenade whose arc meets a wall goes off where it hits.
Here an arc that meets anything before its target cannot be thrown at all, so the blast the preview
shows is always where the grenade goes. The arc is traced through the same voxel grid as a round, and
the preview and the blast ask the same question of who is caught, so the two cannot disagree.

**Death removes a unit at once.** A fallen unit leaves its groups immediately rather than when the
node is freed, so nothing shoots at it or paths around it in the meantime.

**Enemy AI only decides.** An AI looks at the fight and names one action at a time — walk here,
shoot that — and the turn manager carries it out and charges for it. Walking, shooting, reactions
and the camera are the same code for every kind of enemy, so a new enemy type is a new decision
routine and nothing else.

## Layout

```
vcom/                     the Godot project
  Scripts/
    Campaign.gd           what outlives a battle: roster, inventory, gold, villages' stock, starting battles
    Unit.gd               health, actions, reaction, movement, taking a shot, striking, throwing a grenade
    PlayerSquad.gd        the squad spawned from the roster, and which member is selected
    TurnManager.gd        turn order, carrying out what enemy AI decides, victory and defeat
    Reactions.gd          the reaction window: slow motion, prompts, reaction fire
    CameraRig.gd          orbiting tactical camera, and the framed reaction view
    Combat/               the grid, sight and cover, hit chance, where rounds and grenades go, coins
    AI/                   enemy AI: the base, the assault AI, and the queries they share
    Terrain/              destructible terrain: what breaks, how, and what it brings down; blocks and
                          loose models (a crate's boards) that wear away voxel by voxel, and the voxels
                          broken off them
    Actions/              the action bar's actions: Move, Shoot, Strike, Overwatch, Throw Grenade
    Characters/           the rigged voxel figure every unit wears: its rig, animations and how it is baked
    Items/                items: weapons, armor, grenades, and the inventory
    Roster/               characters and the roster
    WorldMap/             the campaign map: its camera, land, party, forests and villages
    UI/                   HUD and menus, built in code rather than scenes
  Resources/              shared resources: weapons and items, characters, AI, villages' locations
    Destruction/          what breaks and how: one resource per breakable block, and the catalog
  Scenes/
    WorldMap.tscn         the campaign map, where the game opens
    BoundaryMap.tscn      the map random encounters are fought on, in a ring of forest
    CombatMap.tscn        the same battlefield without the forest, and one enemy
    LineOfSightTest.tscn  harness for the sight and shot rules
    BaseCharacter.tscn    the figure every unit wears, baked from Characters/BaseCharacter.vox
    Destruct_*.tscn       the pieces a breakable block breaks into
MagicaVoxel/              source .vox art
Styles/                   candidate visual styles, not yet applied
ANIMATIONS.md             the figure's rig and animations, in full
```

## Credits

Map assets by Penflower Ink, 2025, www.penflower-ink.com

Voxel models are imported with [MagicaVoxel Importer with Extensions](vcom/addons/MagicaVoxel_Importer_with_Extensions).

Placeholder icons: nieobie.itch.io/free-icons
