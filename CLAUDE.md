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
  Unit.gd              health, actions, reaction, walking, shoot_at(); name, colour, stats, health from its character;
                       equipment (its character's, or just its weapon) and carries(tag)
  PlayerSquad.gd       spawns the roster's squad on the SquadStarts; members + selection; drops the dead;
                       writes wounds and deaths back to the characters; award_survivors() (experience)
  SquadStart.gd        @tool Marker3D: where a squad member starts; draws its tile and number in the editor
  TurnManager.gd       turn order, end-turn hold, carrying out enemy AI decisions; outcome WON / LOST
  Reactions.gd         reaction window: slow motion, number prompts, reaction fire
  CameraRig.gd         orbiting tactical camera; frame() / release_frame() for the reaction view
  Campaign.gd          autoload: state that outlives a scene; roster, inventory, gold, equip() / unequip(), in_mission,
                       for_hire() / hire() (who is still on each HiringBoard), stock_of() / buy() (each Market), sell(),
                       start_battle(map, chosen) / end_battle() (the world map parked out of the tree meanwhile),
                       squad(count) (who fights: the chosen still alive), SQUAD_SIZE, lose() (killed in battle),
                       heal(amount) (the whole roster's wounds)
  Combat/
    CombatGrid.gd      tiles, pathfinding, is_line_clear(), cast(), pick_tile(), terrain_struck
    LineOfSight.gd     cover, step-out, find_shots() -> Shot
    HitChance.gd       the to-hit sum (Estimate + Term), roll()
    Ballistics.gd      where a round goes: hits along the sight line, XCOM 2 misses -> Path
    ShotPlayback.gd    shots not taken from the action bar: lean out, show, shoot_at(), lean back
    Weapon.gd          Item: damage, environment_damage
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
  Items/
    Item.gd            Resource base: display_name, description, icon, price, sale_price() (half, rounded down),
                       tags / has_tag() (GUN, GRENADE); Weapon, Armor, BattleItem extend it
    Armor.gd           the Armor slot's kind: name and description only so far
    BattleItem.gd      grenades, medkits: name and description only so far
    ItemStack.gd       an item and how many
    Inventory.gd       stacks in display order; stacks_of(kind), count_of, take, add; emits changed
  Roster/
    Character.gd       Resource: display_name, color, portrait, stats, wounds / health, experience,
                       skill_points, gain_experience(), equipment slots, hire_cost
    Roster.gd          characters in display order
  Actions/             UnitAction base (required_tag, is_granted) + ActionController + Move/Shoot/Overwatch,
                       ThrowGrenade (placeholder: offered, does nothing)
  UI/                  every HUD widget, built in code
    TabbedMenu.gd      base CanvasLayer for full-window tab menus: dim, styled tabs, open() / close() pause the tree
    PauseMenu.gd       autoload TabbedMenu: the one menu for both scenes (Campaign, Roster, Inventory, System)
    VillageMenu.gd     TabbedMenu in WorldMap.tscn: a LocationTab per location of the village the party is in
    SquadMenu.gd       TabbedMenu in WorldMap.tscn, opened by Party.encountered, cannot be closed: one SquadTab
    SquadTab.gd        its Roster tab: a CharacterBrowser with ticks, a footer of the count and a Start HoldButton
    LocationTab.gd     placeholder tab for one Location: its description in the middle
    HiringBoardTab.gd  a HiringBoard's tab: read-only CharacterBrowser of who is for hire, a PurchaseBar
    MarketTab.gd       a Market's tab: Buy / Sell SubTabs, InventoryTabs over its stock and the party's; a PurchaseBar
    PurchaseBar.gd     the shop tabs' bottom row: a note, the party's gold, a HoldButton to buy (or sell) the offer
    HoldButton.gd      a button that acts only once held for hold_time (2 s), filling left to right
    CampaignTab.gd     the tab it opens on: a placeholder line, the party's gold bottom-right
    CharacterBrowser.gd strip of CharacterButtons across the top; under it SubTabs of CharacterPages;
                       optionally read_only; show_ticks(), character_activated
    RosterTab.gd       the pause menu's CharacterBrowser of Campaign.roster
    CharacterPage.gd   base for Details / Equipment / Skills: show_character() -> _refresh()
    DetailsPage.gd     the character's stats as one name / value list (HP as left / most); experience bar
                       bottom-right
    EquipmentPage.gd   SlotButtons along the top; an ItemBrowser under them to equip into the selected slot
    SlotButton.gd      a slot's name and what is in it
    SkillsPage.gd      skill trees in columns 1:1:3:3: Species, Sub-Species (4-node paths), Main / Multi-Class (empty);
                       titles its sub-tab "Skills (N)" with the character's skill points
    SkillNode.gd       a node styled locked / available / learned; selection ring
    CharacterButton.gd portrait (or colour swatch) with the name under it; ticked (UI/black_tick.png);
                       activated on a double-click or Enter / Space
    SubTabs.gd         the underlined second-level tab row both tabs above use
    InventoryTab.gd    SubTabs: Weapons, Armor, Battle Items, each an ItemBrowser; follows inventory.changed;
                       selected_stack() + selection_changed
    ItemBrowser.gd     split view: grid of ItemSquares left, selected item's name + description right;
                       optional action button (Equip), also Enter / double-click on a square
    ItemSquare.gd      icon (or name without one), count badge above 1; selected when focused
    FocusChain.gd      left / right through a run of buttons, stopping at the ends
    SystemTab.gd       its last tab: Return to Game, Save / Load (not yet), Exit to Desktop
  WorldMap/            the campaign map, Scenes/WorldMap.tscn (2D)
    WorldMapCamera.gd  pan / zoom with the combat camera's input actions
    WorldMapTerrain.gd is_land() on the baked collider, routes: straight rays, else navmesh pulled straight
    BakeLand.gd        tool: traces WorldMap/<map>LandMask.png into <map>Land.tscn (collider + navmesh)
    Party.gd           the party dot: sent by any right click (no selecting), travels a route; is_at(destination);
                       every step_length map pixels heals the roster by heal_per_step, then rolls a forest's
                       encounter chance; encountered(map)
    Forest.gd          Polygon2D (Scenes/Forest.tscn): a forest's outline, encounter_chance per step, encounter_map
    GameOver.gd        CanvasLayer: once the roster is empty, pauses, shows "Game Over" in a TurnBanner, quits
    Destination.gd     a place to send the party (Scenes/Village.tscn): icon, hover tooltip listing its locations
    Location.gd        Resource: something to use in a village (Resources/Locations/): display_name,
                       description, make_tab()
    HiringBoard.gd     Location: the characters for hire at one village; one .tres per village
    Market.gd          Location: an Inventory of stock for sale at one village; one .tres per village
```

## Architecture

**Actions are nodes.** `ActionController` takes its `UnitAction` children as the actions offered on
the action bar; `ActionBar` builds one button per child. The first child is the default activated on
selection. Add an action by writing a `UnitAction` subclass and adding it as a child in the scene —
no UI code changes needed.

An action gets `begin(unit)` / `end()` / `handle_input(event)` / `is_available(unit)`, sets
`controller.busy = true` while it plays out, and emits `completed` when done. The controller then
re-`begin`s it if it is still available, or drops it.

**An action can need an item.** `UnitAction.required_tag`, set in the action's `_init()` beside its
`display_name`, names an `Item` tag the unit must carry for it to have the action at all
(`is_granted(unit)`, which reads `Unit.carries(tag)`): Shoot and Overwatch need `Item.GUN`, Throw
Grenade `Item.GRENADE`, and Move, with none, is every unit's. That is a different test from
`is_available`: an action the unit lacks has no button on the bar (the bar shrinks and re-centres),
where one it cannot take right now is dimmed; `ActionController.activate()` checks both. The first
child, the default, must need nothing. What a unit carries is `Unit.equipment`, copied from its
character's slots as it enters the map (see Squad units below), so it cannot change mid-battle; a
unit with no character (enemies, the harness) carries just its `weapon`, `Rifle.tres` when the scene
sets none. Enemies are not gated: their AI shoots whatever it carries. Throw Grenade is a
placeholder: it can be made active, and nothing more.

**Highlights are named layers.** `TileHighlights.set_layer(name, {tile: Color}, fill)` — each caller
owns a layer, last set draws on top. Current layers: `selected`, `move`, `move_path`,
`shoot_step_out`, `overwatch`.

**The HUD is written in code, not scenes.** Widgets build their children in `_init()` and style
themselves with `StyleBoxFlat` overrides. Follow that rather than adding `.tscn` files for UI.

**The pause menu is an autoload, `PauseMenu`**, so the world map and combat share one menu and any
future scene gets it free. Being ahead of the scene in the tree, it sees `_unhandled_input` last:
Esc (`pause_menu`, bound to the same key as `cancel_action`) opens it only once nothing in the
scene has taken Esc to cancel something. Anything that cancels on Esc must mark the event handled,
or the menu opens on the same press. Opening sets `get_tree().paused`; the menu alone runs
`PROCESS_MODE_ALWAYS`. A tab is any `Control` added to `PauseMenu.tabs`, titled by its node name.
The menu refills its tabs from `Campaign` each time it opens (`_refresh()`), so it never holds state of its own.

Its frame is `TabbedMenu`, which the world map's **`VillageMenu`** shares. A left click (`select_unit`)
on the icon of the `Destination` the party stands on (`Party.is_at()`: a trip there ends exactly on its
position) opens it with one tab per entry in that destination's `locations`, rebuilt each time, titled by
`Location.display_name`; a destination with none does not open. It is in the scene, so it sees Esc
(`cancel_action`) before the pause menu and takes it. Down from either menu's tabs goes to the open
tab's `focus_selection()` when it has one.

**Forests are shapes drawn in the editor.** Each is an instance of `Scenes/Forest.tscn`, a
light-green, half-transparent `Polygon2D`, under `WorldMap.tscn`'s `Forests` node, in world
coordinates like the destinations (not under the rotated `Map`). Its outline is its `polygon`,
reshaped with the editor's polygon tools and saved as an override on that instance; the colour is set
once in `Forest.tscn`. `Forests` sits before `Destinations` and `Party` so they draw on top.

**Random encounters are rolled per step and fought on a battle scene.** The party counts the
distance it travels in steps of `Party.step_length` map pixels; at the end of each it asks
`Forest.find_at()` which forest it is in (the one drawn on top where they overlap) and rolls that
forest's `encounter_chance`, a percentage per step. On a success it emits `encountered(encounter_map)`,
which opens the map's `SquadMenu` (see below) over the paused map; holding its Start calls
`Campaign.start_battle(map, chosen)`, which takes the world map's scene out of the tree, without freeing it, and makes a fresh instance of the
battle scene (`CombatMap.tscn` by default) the current scene; the swap is deferred to the end of the
frame. `TurnManager` listens to every enemy's and squad member's `died`, and once either side is gone
it sets `outcome` (`WON` / `LOST`), disables the `ActionController`, announces "Victory" or "Defeat"
and calls `Campaign.end_battle()`, which frees the battle and puts the same world map node back. A
defeat goes back to the map like a win. If it killed the last of the roster, the map's `GameOver`
layer sees the empty roster on its first frame back: it pauses the tree, shows "Game Over" in its own
`TurnBanner` (laid out as the combat HUD's, over the menus at `TabbedMenu.LAYER + 1`, running through
the pause), and quits on the banner's `fading` signal, the moment its fade-out starts.
Nothing on the map is saved or restored: its `_ready`s do not run
again, so the party is on the spot it was set upon, still on its route, and the camera is where it was.
Anything on the map that must notice a battle has passed (the navigation map re-registering, for one)
sees only `_exit_tree` / `_enter_tree`. `WorldMap.tscn` is the main scene; a battle opened on its own (F6, the harness) has
nothing to go back to, so it is left over and idle after "Victory".

**Who fights is chosen as the battle starts, on a menu that cannot be closed.** `SquadMenu` is a
`TabbedMenu` in `WorldMap.tscn` that `Party.encountered` opens (a party is its `party_path`). Its one tab,
titled Roster, is a `SquadTab`: the pause menu's `CharacterBrowser` over `Campaign.roster` (pages and
equipment work as there, the battle not having begun) above a footer laid out as `PurchaseBar`'s, the
hint and count on the left and a "Start" `HoldButton` on the right. A `CharacterButton` emits `activated`
on a double-click (seen in its `_gui_input`, which runs before the button's own) or Enter / Space;
`CharacterBrowser` passes it on as `character_activated`, and the tab toggles that character's tick, up
to `Campaign.SQUAD_SIZE` (4), refusing another at the cap. A single click only changes whose pages show.
Start is greyed out with nobody ticked. It opens on `Campaign.squad()`, which is whoever was chosen
last and is still on the roster (the first four before any battle, or after a whole squad fell), and
Start passes the ticks to `Campaign.start_battle(map, chosen)`, which keeps them for the battle's
`PlayerSquad` and the next menu. It swallows Esc (`cancel_action` and `pause_menu`, the same key) so
the pause menu, which sees it after the scene, does not open over it; closing it on Start unpauses the
tree, and the deferred swap takes the map out of it before it moves again. Mouse input pushed into a
headless probe does not reach the GUI (see Gotchas): drive this menu's clicks in a windowed run.

**Locations are data; their tabs are what they do.** A `Location` is a stateless `.tres` like an
`Item`, and `make_tab()` gives its tab: a placeholder `LocationTab` unless a subclass overrides it. A
new kind of location is a `Location` subclass plus its tab, as `HiringBoard` + `HiringBoardTab` and
`Market` + `MarketTab`. A kind whose content differs has a `.tres` per village
(`Village1HiringBoard.tres`, `Village1Market.tres`); one the same everywhere could be one shared
`.tres`. What changes in play lives in `Campaign`, keyed by the resource, and the resource is never
changed:

- `Campaign.for_hire(board)` copies the board's `characters` the first time it is asked;
  `Campaign.hire(board, character)` spends `Character.hire_cost` and moves them to the end of
  `Campaign.roster`. A character belongs on one board only.
- `Campaign.stock_of(market)` is a `duplicate_deep()` of the market's `stock` `Inventory`, made the
  first time it is asked; `Campaign.buy(market, item)` spends `Item.price` and moves one from it to
  `Campaign.inventory`. Prices are on the items, the same in every market; stock counts are in the
  market's `.tres`.
- `Campaign.sell(item)` takes one from `Campaign.inventory` for good and adds `Item.sale_price()`
  (half the price, rounded down, so a 1-gold item fetches nothing) to the gold. No market keeps what
  it buys, so it names none. Equipped items are not in the inventory, so they cannot be sold.

The two shop tabs look like the pause menu's tab they mirror: the Hiring Board is the Roster tab's
`CharacterBrowser` made read-only (`CharacterPage.read_only`: the Equipment page shows just the slots)
over who is for hire, and the Market is two `InventoryTab`s under Buy / Sell `SubTabs`, one over the
stock and one over the party's inventory. Both end in a `PurchaseBar` (one under both of the Market's
sides) whose `HoldButton` buys the selected offer, or on Sell sells it, once held for 2 seconds by
mouse or Enter / Space. A sale is never greyed out for want of gold. It
emits `held`, never acts on a click, and empties the moment it is full, then stays empty until it is
let go and pressed again: one purchase per press, so holding on never buys a second, nor the next
item or character that comes up. The bar rechecks the party's gold whenever it is shown, since the
other tab may have spent some.

**Items are shared resources, the inventory is state.** An `Item` (`Weapon`, `BattleItem`) is a
stateless `.tres` like the old `Weapon`: the same `Rifle.tres` is what units shoot with and what the
inventory lists. Its `tags` (`StringName`s, the ones the rules read as constants on `Item`) say what
sort of thing it is, finer than its class: `Rifle.tres` is tagged `gun`, `FragGrenade.tres`
`grenade`. A new gun is a `Weapon` `.tres` tagged `gun`, and gets Shoot and Overwatch with no code. How many the party holds lives in `ItemStack`s in an `Inventory`, and the live one
is `Campaign.inventory`, a `duplicate_deep()` of `Resources/StartingInventory.tres` (its stacks are
copied, its items are not). Change that copy, never the `.tres`. A new kind of item is an `Item`
subclass plus an `ItemBrowser` sub-tab over `inventory.stacks_of(ThatKind)` in `InventoryTab`, which
gives it a sub-tab on both sides of every market too.

**Squad units are roster characters, spawned for each battle.** A `Character`
(`Resources/Characters/*.tres`) is who someone is between battles. `Campaign.roster` is a copy of
`Resources/StartingRoster.tres` whose list is its own but whose characters are the loaded `.tres`. A
combat map has no squad of its own: it has `SquadStart` markers under a `SquadStarts` node, and
`PlayerSquad` (its `starts_path`) spawns a `Scenes/SquadUnit.tscn` (a `Unit` in `players` with a
capsule `Mesh`, the old fixed players' pattern) on the tile under each, for each character
`Campaign.squad(markers)` sends: those chosen on the `SquadMenu`, in roster order. It sets `Unit.character` before adding the unit, then gathers `players` as before, so the squad
panel, the reaction keys and everything else reading `PlayerSquad.members` follow roster order. It
does this in its own `_ready`, which runs after `CombatGrid`'s (for `tile_at`) and before anything that
reads the members. A marker's order among its siblings is its number; in the editor it draws an orange
square on the tile it counts as over, and nothing in game. So they are linked: a unit takes its
`display_name`, colour and the character's stats (`max_health`, `move_range`, `aim`, `evasion`) from
its character in `_ready` (painting its mesh on a copy of the material). They are copied once, when
the unit enters the map: the rules read the unit, never the character. The unit's other stats
(actions, sight, height bonus, distance penalty) are still its own, set in `SquadUnit.tscn`. A stat
that should differ per character moves to `Character`, gets copied in `Unit._take_character()`, and
gets a row in `DetailsPage.STATS`. `Character.experience` (out of `Character.EXPERIENCE_TO_LEVEL`, 100)
is the character's alone and never copied to the unit. It only goes up through
`Character.gain_experience()`, where every 100 becomes a `skill_points` and the rest carries over (97 +
10 is 7 and a point; a big award gives several); any new way to earn experience calls that. So far the
one way is surviving a battle: as `TurnManager` decides the battle it calls
`PlayerSquad.award_survivors()`, which gives every member still standing `survival_experience` (50).
A win also adds `TurnManager.victory_gold` (10) to `Campaign.gold`, at the same moment.

What happens in battle goes the other way, through `PlayerSquad` as it happens, not at the end:
every change to a member's health is written to `Character.wounds` (health missing, so a character is
whole by default and stays as hurt if `max_health` grows; `Character.health` is what is left), and a
unit starts at its character's `health`. A member who dies is taken off the roster by
`Campaign.lose()`, which returns everything they had equipped to the inventory, the one way gear
leaves a character mid-battle. Wounds mend on the road: every step the party travels
(`Party.step_length`, the same step the encounters are rolled on) calls `Campaign.heal(heal_per_step)`
(1), which takes that off every roster character's `wounds`, down to none, before that step's roll.
Unlike an `Item`, a character is state and changes in play; nothing writes it back to disk, and
save/load will need to store it. Enemies and `LineOfSightTest`'s units have no character
and keep the scene's name and material; the harness has no `SquadStarts` (`starts_path` is empty), so
its eight fixed units are its squad and spawn nothing.

**Equipment is on the character, the spares in the inventory.** A character has six typed slots
(`armor`, `weapon_1`, `weapon_2`, `item_1`..`item_3`), listed with their titles and kinds in
`Character.slots` (a `static var`: a `const` cannot hold a class). Every item is either in
`Campaign.inventory` or in one slot, never both, so equipment only changes through
`Campaign.equip()` / `unequip()`, which move one copy across and put a swapped-out item back. What a
character starts with is set in their `.tres`, not counted in `StartingInventory.tres`. What is
equipped decides a squad unit's actions by its tags (see "An action can need an item"): with no gun
it has only Move. It shoots with the first gun in its slots, Weapon 1 before Weapon 2
(`Unit.weapon`, null with none); a grenade in any item slot gives it Throw Grenade, which does nothing
yet, and armor does nothing in combat yet. During a battle `Campaign.in_mission` is true (the `TurnManager` sets it while in the
tree) and both calls refuse, since a unit took its gear when the map loaded; the Equipment page greys
its buttons and says why. This is the menu's first read-only-in-combat rule.

The Roster tab is a `CharacterBrowser`, whose sub-tabs are `CharacterPage`s. Whenever the selection
in the strip changes, every page (not just the open one) gets `show_character(character)`, so a page
is never left showing someone else; a page with content overrides `_refresh()`, and
`focus_selection()` if Down from the sub-tabs should land somewhere in it. Changing character keeps
the open page; opening the menu goes back to Details. A page that can change the character hides
the means when `read_only` is set, as it is for characters not on the roster.

The Skills page titles its own sub-tab in `_refresh()`, "Skills (2)" from `Character.skill_points`, so
the count follows the selection; nothing spends the points yet. The trees are placeholder UI with no
data behind them: `SkillsPage.SECTIONS` sets each column's
title, width share and node count, and every character shows the same `PLACEHOLDER_STATES` (first
node available, the rest locked). Selecting a node only highlights it, and changing character
clears the selection. Skills, trees and a character's progress through them are still to be
designed as resources.

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

**Scenery around a combat map is a second GridMap.** The rules, the camera and the destruction read
only the node at their `grid_map_path` (`GridMap`): the battlefield and the ring of trees walling it
in. `BoundaryMap.tscn` paints the forest beyond that ring into a sibling GridMap, `Boundary`, with
the same MeshLibrary, out to 75 tiles past the battlefield. Nothing in the rules sees it, so it
adds no tiles, cover or collision, and `CameraRig`'s pan bounds stop at the battlefield. Paint
scenery into `Boundary`, never `GridMap`. Debris thrown over the ring falls through it (it has no
collision) and is removed below the map. It costs frame time: every tree in view is drawn, shadow
pass included.

75 tiles is the standard depth for a combat map's scenery ring. The least that hides the ring's
outer edge is 73, found by rendering at 1280×720: zoomed all the way out (`far_distance` at
`view_pitch`) or framed as far as it goes (`max_frame_distance` at `Reactions.camera_pitch`), with
the pivot at its pan limit, facing any way. At 72 a sliver of sky shows past a screen corner; 75
rounds that up. Anything that lets the camera see further (more zoom or framing distance, a lower
pitch, a wider FOV or window, a larger `pan_margin`) needs the standard deepened to match; that is
why `max_frame_distance` is kept to about what the zoomed-out camera sees.

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

**`get_tree().create_timer()` ignores the pause unless told not to.** Its `process_always` defaults
to true, so an enemy's pause between actions or a round in flight would run out behind the pause
menu and the turn would carry on. Game timers pass `false` as the second argument. Tweens bound to
a node, physics, and `_process` all stop with the tree; `await process_frame` does not, so a
polling loop keeps spinning (harmless while what it polls is paused).

**A script's `_init()` does not run its parent script's `_init()`.** Call `super()` first, as
`InventoryTab` does to get `SubTabs`' styling; without it the tabs silently fall back to the default
theme.

**A `Button` ignores a script's `_get_minimum_size()`.** Its native sizing replaces the hook, and a
button does not lay out its children, so a button built from child controls (`CharacterButton`)
sets `custom_minimum_size` from them, again on their `minimum_size_changed`: in `_init()` a label has
no font yet and measures nothing.

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
window reports focus. Mouse button events pushed with `Viewport.push_input` never reach the GUI
there either (keys do), so a probe that clicks buttons has to run in a window, with `--write-movie`
to see it.

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

**`Geometry2D.is_point_in_polygon` is wrong near vertices on big outlines.** It casts a slanted ray
and fudges any crossing within a relative epsilon of a vertex; on the world map's 33k-corner
coastline it misjudged about one coast pixel in a hundred. `WorldMapTerrain._encloses` counts
crossings row by row instead. Do not use the built-in for land tests.

**The 2D navigation server cannot handle long sliver polygons.** Baked whole, the pixel coastline
gave polygons thousands of pixels long and a few wide, and the server found no polygon under
points inside them. `BakeLand.gd` bakes in 256 px tiles, and adds every corner on a tile line to
the edges along it on both sides, or the tiles do not join. The world map's navigation also takes
over a second after the scene opens to be usable (`WorldMapTerrain.is_ready()`), and a
`NavigationPathQueryParameters2D` gives up after 4096 polygons unless `path_search_max_polygons`
is set (0 lifts it).

**A script error does not end a `--script` run.** Godot sits idle after it until killed, so give
scripted runs a `timeout`.

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
- The world map's land is baked, not live: after editing `WorldMap/WorldMapV1LandMask.png` (white
  land, black water, same size as the art), rerun `BakeLand.gd`. `-- --mask-from-art` regenerates
  the mask from the art and overwrites any edits to it.
- The squad panel does not wrap: past about five members it runs under the action bar, which it does
  in the harness (eight).
- Nothing spends skill points, and the only experience is for surviving a battle. Items used in battle
  are never spent. Throw Grenade is only a button: throwing (reach, blast, damage, using the grenade
  up) is still to be written. Every encounter is the same `CombatMap.tscn`, fresh each time, with its one enemy.
