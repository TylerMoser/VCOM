# CLAUDE.md

Working notes for VCOM, a turn-based tactics prototype (XCOM / Star Wars: Zero Company) in Godot
4.7 on a voxel grid. `README.md` has the player-facing rules and controls; this file is about
working in the code.

## Layout

The git root is `VoxelXCOM/`; the Godot project is `vcom/`, which is where commands are run from.
`MagicaVoxel/` holds source `.vox` art outside the project. `Styles/` holds candidate visual styles
(screenshots, exact settings, a render harness); `Styles/APPLYING.md` explains how to apply one.
Style 05, Colour Bounce, is applied: in every combat map's Environment, sky and sun (sun from the
camera's left, blue procedural sky, SSAO and SSIL), plus 4x MSAA in `project.godot`.
`Styles/REVERT.md` restores the original look. `ANIMATIONS.md` documents the characters' rig and animations in full: where they came
from, every clip, every decision and gap, and recipes for adding more. Read it before touching them.

```
vcom/Scripts/
  Unit.gd              health, actions, reaction, walking, shoot_at(), strike(), throw_at(); name, colour, stats, health
                       from its character; equipment (its character's, or just its weapon), carries(tag), melee_weapon,
                       grenade; use_up(item) -> used_up; damage_from() (defense off a hit, as take_damage() takes it);
                       model (its CharacterModel) and the calls that only show things on it: aim_at(), ready_strike(),
                       ready_throw(), stand_easy(), celebrate(), dodge(), recover(); aim_point() (a target's eye);
                       hurt (every hit that takes health, where it landed and how: for Blood); hit_from,
                       hit_blasted, hit_at, hit_sweep (the last hit: the way the figure breaks apart if it kills)
  PlayerSquad.gd       spawns the roster's squad on the SquadStarts; members + selection; drops the dead;
                       writes wounds, used-up grenades and deaths back to the characters; award_survivors() (experience)
  SquadStart.gd        @tool Marker3D: where a squad member starts; draws its tile and number in the editor
  TurnManager.gd       turn order, end-turn hold, carrying out enemy AI decisions; outcome WON / LOST; a win's
                       victory_gold and Coins.sweep()
  Reactions.gd         reaction window: slow motion, number prompts, reaction fire
  CameraRig.gd         orbiting tactical camera; frame() / release_frame() for the reaction view
  Campaign.gd          autoload: state that outlives a scene; roster, inventory, gold, equip() / unequip(), learn()
                       (a skill, as Character.learn() but refused in battle), in_mission,
                       for_hire() / hire() (who is still on each HiringBoard), stock_of() / buy() (each Market), sell(),
                       start_battle(map, chosen) / end_battle() (the world map parked out of the tree meanwhile),
                       squad(count) (who fights: the chosen still alive), SQUAD_SIZE, lose() (killed in battle),
                       use_up(character, item) (a thrown grenade, off them for good), heal(amount) (the whole
                       roster's wounds)
  Combat/
    CombatGrid.gd      tiles, pathfinding, is_line_clear(), cast() (by_voxel: through the voxels of blocks that wear
                       away, for rounds; every_block too: of any .vox block, for blood; RayHit.index the voxel met),
                       pick_tile(), terrain_struck, blast() -> terrain_blasted, fly() -> round_flown (every round's
                       line, for the loose models it tears through); voxels (VoxelTerrain)
    LineOfSight.gd     cover, step-out, find_shots() -> Shot
    HitChance.gd       the to-hit sum (Estimate + Term): for_shot(), for_strike() (melee); roll()
    Ballistics.gd      where a round goes: hits along the sight line, XCOM 2 misses -> Path (wound: where on the
                       target a hit is drawn landing, for show; drawn_to())
    Throwing.gd        RANGE (10, every throw's); plan() -> Throw (the arc, blocked or not), throws_for(unit);
                       the blast: blast_cells(), is_caught(), caught(), blast_tiles()
    ThrownGrenade.gd   a grenade in flight along a Throw's arc, from the thrower's hand, as the grenade's
                       model tumbling about its middle; for show; frees itself as it arrives
    Explosion.gd       a grenade going off: fireball, flash, smoke, for show; go_off(), frees itself
    MuzzleFlash.gd     a gun's flash as it fires, under its Muzzle marker, for show; frees itself
    Coins.gd           map node: rolls a breaking block's coin_chance, keeps the coins by tile (stacked), drops a
                       tile's when its ground goes, pays for those on any squad member's tile; count(), sweep()
    Coin.gd            one coin as it is seen (Items/Coin2.vox, as drawn): spins, bobs, pops in, drop_to(),
                       take(); for show
    ShotPlayback.gd    shots not taken from the action bar: aim, lean out, show, shoot_at(), lean back
    Weapon.gd          Item: damage, environment_damage
    TileHighlights.gd  named layers of coloured squares
    TileGrid.gd        map node: the optional tile grid (G, or the System tab); gives the ground blocks
                       TileGrid.gdshader as the map loads; static shown, set_shown(), toggle()
  AI/
    EnemyAI.gd         Resource base: choose_action(tactics) -> AIAction
    AssaultAI.gd       close in, point-blank when adjacent, best odds with the last action
    AIAction.gd        MOVE (path) / SHOOT (shot + estimate) / END_TURN
    Tactics.gd         shared queries: adjacent_foes, shots_at, best_shot, advance, paths
  Terrain/
    TerrainDestruction.gd  breaks struck and blasted blocks, drops what they held, drops stranded units, throws a
                           blast's debris about, tidies debris; block_broken(cell, destruction); make_piece() /
                           pieces_in() (pieces: PIECE_LAYER, the PIECES group, found by physics queries); hands a
                           breaking block's blood on to what it becomes (_break, _on_landed, _pieces_since());
                           break_figure() (a dying unit's figure into lumps, knocked by the killing blow:
                           FIGURE_*, _figure_knock()), _drop_gear() (its props whole, as pieces that wear)
    Destruction.gd         Resource base: how a kind of block comes apart, shatter(); prepare() (as a map loads);
                           mass; coin_chance; Motion
    ScriptedDestruction.gd pieces cut in advance, swapped in and left to fall or blasted apart; wear (then each piece
                           wears away as a loose model from the first time something reaches it)
    FallingBlock.gd        a block whose support broke, falling whole until it lands
    Blast.gd               a burst from a point: impulse by distance and the area a piece shows
    DestructionCatalog.gd  Resource: every breakable block, shared by every map
    VoxelDestruction.gd    Destruction: a block that wears away a few voxels at a time (the second kind), or how a
                           ScriptedDestruction's pieces wear; collapse_below, voxels_per_damage, crater_per_damage /
                           crater_radius(), density, crumble_size
    VoxelShape.gd          one model's voxels, read from its .vox with the importer's reader: a block's (read(), 16^3),
                           one model of a .vox imported as a scene (read_model(), source_of()) or a mesh imported from
                           one (read_mesh()), cropped to its voxels; a padded array of palette places, a row of bits
                           per (y, z) (so at most WIDEST, 62, along x), colors, the mesh's material
    VoxelMesher.gd         surface() / faces() / mesh() from a shape and a voxel array: faces open to the air, merged
                           greedily, found a row at a time from the rows
    VoxelTerrain.gd        made by TerrainDestruction: worn blocks by cell, the stand-in items, trace() (rounds),
                           chip() (a round's bite), crater() (a blast's), crumble(), take(), is_solid_at(); loose
                           voxels, _holds_up() (cut through), deferred redraws after a blast; loose models:
                           take_on_later() (taken on at the first hit), take_on_body(), tear() (rounds through
                           them), _settle() (split off, crumble); lumps chosen before they are made (Batch, _scatter());
                           blood on any .vox block: kind_of(), voxels_of(), stain(), take_stains(), carry_stains()
                           (on to a crate's pieces); march() (a ray through a model's voxels)
    WornBlock.gd           one block that has lost voxels: what is left, its mesh and trimesh collision
    VoxelBody.gd           one loose model (a crate's piece), a node under its RigidBody3D: what is left, its mesh,
                           box collider and mass; passes (the bodies it passes through); stains (stained(),
                           adopt_stains()); scale (a prop's voxels, a shade bigger than a block's)
    VoxelDebris.gd         every voxel broken off: lumps as PhysicsServer bodies with no nodes, drawn by MultiMeshes;
                           add(), burst(), wake(), tidy(); at MOST bodies, stills those at rest furthest from focus
                           (the tile the camera looks at) down to KEEP, drawn but bodiless until disturbed;
                           stain(body, point) (a drop of blood colours the voxel it met)
    VoxelStains.gd         the faces of one voxel model blood has stained (6 bits a voxel, by its place), drawn by an
                           overlay of red squares 2 mm proud of them, rebuilt at the end of the frame; on() (a prop's,
                           kept on its MeshInstance3D); COLOR, the material blood is drawn with
    SceneryGround.gd       BoundaryMap's scenery ground plane, with the battlefield's floor cut out of it
  Blood/
    Blood.gd           map node: on every Unit.hurt wounds the figure and sprays drops the way the blow went; drops (one
                       MultiMesh) stain the first voxel face they meet and run; a pool under each body once it rests;
                       landings settled on a budget a physics step; drops_in_flight(), pools_to_come(); static
                       enabled (the System tab's Blood on / off, read as each map loads)
    BloodFlow.gd       blood running over voxel faces, cheapest first (downhill cheap, climbing dear, undersides never):
                       spread(); the Surface it runs over: TerrainSurface (every block as one grid), ModelSurface
  Items/
    Item.gd            Resource base: display_name, description, icon, price, sale_price() (half, rounded down),
                       tags / has_tag() (GUN, GRENADE, MELEE), model (its prop scene); Weapon, Armor, BattleItem
                       extend it
    Armor.gd           the Armor slot's kind: defense, added to the wearer's
    BattleItem.gd      grenades, medkits: name and description; a kind's subclass says what it does
    Grenade.gd         BattleItem: damage, blast_size (odd, tiles across), environment_damage, blast_force
    ItemStack.gd       an item and how many
    Inventory.gd       stacks in display order; stacks_of(kind), count_of, take, add; emits changed
  Characters/          the rigged figure every unit wears, and how it is baked
    CharacterModel.gd  the figure's runtime (BaseCharacter.tscn's root): drives its AnimationTree from what its unit
                       does, facing, hops, gear in its sockets; break_apart() (hides it once broken apart on
                       death), crumbles_as / gear_wears_as (Figure.tres, Gear.tres); for blood: voxels()
                       (FigureVoxels), pick_wound(), swing(), gear()
    FigureVoxels.gd    a figure's voxels for blood and breaking apart, read from its .vox at run time: each bone's a
                       part posed as the skeleton is; march() (bones and gear), pick_wound(), hit_near(), exit(),
                       bleed(); crumble() (the lumps it breaks into); its stains drawn by a mesh skinned to the
                       skeleton (FigureStains)
    AimModifier.gd     SkeletonModifier3D: bends spine + chest to aim up or down, turns the head to look
    Postures.gd        map node: idle figures kneel behind low cover / brace at high, facing their nearest foe
    BakeCharacter.gd   tool: a .vox -> Scenes/<model>.tscn (skeleton, skinned body, sockets, animations)
    VoxelRig.gd        the humanoid skeleton, each model's layout (joints, voxel regions; LAYOUTS by .vox), per-bone
                       mesher
    HumanoidAnimations.gd  every animation, authored as IK poses in code, and the AnimationNodeBlendTree
    PreviewAnimations.gd   tool: renders clips to images, holding the right props, and a contact sheet of them
  Roster/
    Character.gd       Resource: display_name, color, portrait, species / sub_species / main_class / multi_class
                       (TREES), learned (node ids by SkillSource, one for each time taken), learned_of() /
                       times_learned() / can_learn() / learn(), skill_effects(), its own stats and total(stat)
                       (with its skills' bonuses, and armor for defense), wounds / health, total_defense,
                       experience, skill_points, gain_experience(), equipment slots, hire_cost
    Roster.gd          characters in display order
    Species.gd         SkillSource: what someone is born (Human)
    SubSpecies.gd      SkillSource: a kind of one Species (Minor Noble), its species
    CharacterClass.gd  SkillSource: what someone trained as; one tree, as Main Class or Multi-Class
  Skills/
    Skill.gd           Resource: one ability, display_name, flavor, icon, levels (a SkillLevel for each time
                       it can be taken, at most MOST_LEVELS, 5), takes(), level(), describe(); shared by every
                       tree placing it
    SkillLevel.gd      Resource: one level of a skill: description (its words), effects (what it adds)
    SkillEffect.gd     Resource base: one thing a level gives; bonus_to(stat), nothing unless a kind says
    StatBonus.gd       SkillEffect: amount added to one stat (max_health, defense, move_range, aim, ...)
    SkillTreeNode.gd   a place in a tree: id, skill, cell (column, row), requires (ids in the same tree); takes()
    SkillTree.gd       Resource: nodes; find(), extent(), is_open() (everything it requires learned, once)
    SkillSource.gd     Resource base for whatever gives a character a tree: display_name, tree
  Actions/             UnitAction base (required_tag, is_granted) + ActionController + Move/Shoot/Overwatch,
                       Strike (melee, at an adjacent enemy), ThrowGrenade (at a tile in reach; uses the grenade up)
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
    SkillsPage.gd      a column per Character.TREES entry (SHARES: widths 1:1:3:3), headed by the character's
                       SkillSource or the plain title, rebuilt per character; learns a node once it is held;
                       the selection; arrow keys to the nearest node; the SkillTooltip beside the node under
                       the mouse or the keyboard, whichever was used last; titles its sub-tab "Skills (N)"
                       with the character's skill points
    SkillTreeView.gd   one SkillSource's tree: a SkillButton on each node's cell (columns as wide as their
                       widest, rows as tall as row_heights() says), elbow links to the nodes each requires;
                       show_learned() restyles both
    SkillButton.gd     a circle styled locked / available / learned, a ring round it for each time its skill
                       can be taken again (size_of()); its skill's icon or its rank; held for HOLD_TIME while
                       learnable, the circle fills like a clock, or once taken the next ring out, and it emits
                       held; selected (its circle filled a shade lighter)
    SkillTooltip.gd    the panel beside a node: the skill's name, its flavor, "Current:" the level taken,
                       "Next:" the level to come; show_skill(skill, taken)
    CharacterButton.gd portrait (or colour swatch) with the name under it; ticked (UI/black_tick.png);
                       activated on a double-click or Enter / Space
    SubTabs.gd         the underlined second-level tab row both tabs above use
    InventoryTab.gd    SubTabs: Weapons, Armor, Battle Items, each an ItemBrowser; follows inventory.changed;
                       selected_stack() + selection_changed
    ItemBrowser.gd     split view: grid of ItemSquares left, selected item's name + description right;
                       optional action button (Equip), also Enter / double-click on a square
    ItemSquare.gd      icon (or name without one), count badge above 1; selected when focused
    FocusChain.gd      left / right through a run of buttons, stopping at the ends
    SystemTab.gd       its last tab: Return to Game, Tile Grid on / off, Blood on / off (greyed out in battle, with a
                       note), Save / Load (not yet), Exit to Desktop
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

Art beside the scripts: `vcom/Characters/` holds the figure's `.vox` and what `BakeCharacter.gd` makes
of it (`BaseCharacterBody.res`, the skinned mesh; `BaseCharacterAnimations.res`, the animation
library), `vcom/Items/` the props' `.vox` (copies of `MagicaVoxel/`'s), and `vcom/Scenes/Props/` a scene
for each prop: its mesh, placed so the grip is on the scene's origin, with markers where it fires from
and where it is held.

## Architecture

**Actions are nodes.** `ActionController` takes its `UnitAction` children as the actions offered on
the action bar; `ActionBar` builds one button per child. The first child is the default activated on
selection. Add an action by writing a `UnitAction` subclass and adding it as a child in the scene —
no UI code changes needed.

An action gets `begin(unit)` / `end()` / `handle_input(event)` / `is_available(unit)`, sets
`controller.busy = true` while it plays out, and emits `completed` when done. The controller then
re-`begin`s it if it is still available, or drops it. If the unit that took it is no longer the one
selected (it fell to its own grenade and the selection moved on while the action was busy), the new
selection gets the default action instead.

**An action can need an item.** `UnitAction.required_tag`, set in the action's `_init()` beside its
`display_name`, names an `Item` tag the unit must carry for it to have the action at all
(`is_granted(unit)`, which reads `Unit.carries(tag)`): Shoot and Overwatch need `Item.GUN`, Strike
`Item.MELEE`, Throw Grenade `Item.GRENADE`, and Move, with none, is every unit's. That is a different test from
`is_available`: an action the unit lacks has no button on the bar (the bar shrinks and re-centres),
where one it cannot take right now is dimmed; `ActionController.activate()` checks both. The first
child, the default, must need nothing. What a unit carries is `Unit.equipment`, copied from its
character's slots as it enters the map (see Squad units below), so it changes mid-battle only as the
unit uses something up (`Unit.use_up()`: a thrown grenade); with the last grenade gone, Throw Grenade
leaves the bar, since the bar asks `is_granted` on every `changed`. A unit with no character (enemies,
the harness) carries just its `weapon`, `Rifle.tres` when the scene sets none. Enemies are not gated:
their AI shoots whatever it carries.

**Strike is a shot at arm's length.** `StrikeAction` is laid out as `ShootAction`: its targets are the
living enemies next to the unit, as `Tactics.is_next_to()` has it (the AI's point-blank range, so the
two cannot drift), nearest first; Tab / Shift+Tab cycle them, Enter / Space strikes, Ctrl opens the
breakdown, and `ShotOverlay.show_strike()` draws the same line, reticle and target panel (its status
line reads "Melee" instead of the cover). It costs `StrikeAction.COST` (1, a shot's) and is dimmed
without an action left or an enemy next to the unit. The odds are `HitChance.for_strike()`, worked out
once as the target is lined up; `Unit.strike()` rolls them and deals `Unit.melee_weapon`'s damage
plus the striker's `Unit.strength` through `take_damage()`, so defense comes off that sum as it does
off a shot's damage. Nothing flies, and the blow touches no terrain. Lining a target up has the
figure square up to it with its sword out (`Unit.ready_strike()`; a rifleman draws it off his back),
and `Unit.strike()` is a coroutine: it plays the swing, rolls and deals the damage at the swing's
`impact` moment (`strike_sword`'s metadata), and returns then, so the result is called as the blade
lands; `StrikeAction` then awaits `Unit.recover()`, the follow-through, before it completes. It is
busy throughout, so a kill that wins the battle finds the action mid-play and leaves it to be put
away as it completes.

**A throw is planned, then flown.** `ThrowGrenadeAction` aims with the mouse, as Move previews: it
follows the tile under the cursor every frame, and right-click (`execute_action`) or Enter / Space
throws there; there are no targets to Tab through. `begin()` works out every throw the unit can make
(`Throwing.throws_for()`: tiles within `Throwing.RANGE` whose arc is clear, about 16 ms on
BoundaryMap) and tints them (`throw_range`); the tile under the cursor gets the `throw_blast` layer and
`ShotOverlay.show_throw()`: the arc's points, a cross where a blocked arc stops, and an outlined
bracket with the damage (`Unit.damage_from()`) on everyone `Throwing.caught()` names, gold on the
squad. A `Throwing.Throw` is a parabola from `RELEASE_HEIGHT` over the thrower's floor to the centre of
the target tile's lower cell, rising `ARC_RISE` per tile (at least `ARC_MIN_HEIGHT`) above the straight
line, cut into `TRACE_STEP` pieces each cast through the grid with `CombatGrid.cast()`; the first solid
cell any piece meets blocks it, and `points` then ends there. Those constants decide what a throw
gets over (half cover in front of the target from the full range, the thrower's own full cover; never
the tile right behind full cover), so check them with a probe if they change. The throw costs
`ThrowGrenadeAction.COST` (1) and goes through `Unit.throw_at()`. While the action is up the figure
holds a grenade ready, turned to the tile under the cursor (`Unit.ready_throw()`). The throw winds up
and lets go at its `release` moment, where the grenade is used up as it leaves the hand; `_fly` gets
where the hand was and shows a `ThrownGrenade` from there, easing on to the arc in its first
`EASE_IN` of the flight (timed as a fall under `ThrownGrenade.GRAVITY`), and an `Explosion` where it
goes off, and the blast lands as the grenade arrives: `take_damage()` on
everyone caught, then `CombatGrid.blast()` with the cube's cells. Results are called together
(`ShotOverlay.flash_results()`, over the heads). The action stays busy `AFTERMATH_SECONDS` and until no
unit is moving, so anyone the blast dropped has landed before the next throw is worked out. The
3D effects go under `effects_path`, the map root.

**Highlights are named layers.** `TileHighlights.set_layer(name, {tile: Color}, fill)` — each caller
owns a layer, last set draws on top. Current layers: `selected`, `move`, `move_path`,
`shoot_step_out`, `overwatch`, `throw_range`, `throw_blast`. A colour's alpha dims a square's fill and
border together, which is how `throw_range` stays faint.

**The tile grid is the ground's own material, and off until the player turns it on.** Style 19's
grid lines alone (Styles/): a faint darkening along every block boundary on the ground blocks, tops
and walls. `TileGrid`, a node in each combat map, gives the `BrightGrass1` mesh
`TileGrid.gdshader` as the map loads, on the mesh itself, since the imported mesh is shared. With
the grid off that shader draws exactly as the importer's `StandardMaterial3D` (its
`render_mode diffuse_burley` is what makes it so: Godot 4.7's default diffuse differs). The lines
answer to the global shader uniform `tile_grid` (`project.godot`'s `[shader_globals]`), which only
`TileGrid.set_shown()` / `toggle()` set; `TileGrid.shown` is static, so the choice holds from battle
to battle until the game closes, and is never read back from the RenderingServer. `G`
(`toggle_grid`) toggles it in combat, as does **Tile Grid** on the System tab anywhere, which the
pause menu relabels as it opens. `TileGrid` must stay before `TerrainDestruction` in each map: that
copies each wearable block's material as it readies (`VoxelShape.read()`) and draws worn blocks with
it, so worn grass keeps the grid. A block style that changes the ground's material has to carry the
grid with it (Styles/APPLYING.md section 3).

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
battle scene (`BoundaryMap.tscn`, the `encounter_map` every forest gets from `Forest.tscn`) the current scene; the swap is deferred to the end of the
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
stateless `.tres`: the same `Rifle.tres` is what units shoot with and what the
inventory lists. Its `tags` (`StringName`s, the ones the rules read as constants on `Item`) say what
sort of thing it is, finer than its class: `Rifle.tres` is tagged `gun`, `FragGrenade.tres` (a
`Grenade`, the `BattleItem` that carries its blast: 5 damage, 3 tiles across) `grenade`, `Shortsword.tres` `melee` (a `Weapon` that is not a gun, so it gives Strike rather than Shoot). A new gun is a `Weapon` `.tres` tagged `gun`, and gets Shoot and Overwatch with no code. How many the party holds lives in `ItemStack`s in an `Inventory`, and the live one
is `Campaign.inventory`, a `duplicate_deep()` of `Resources/StartingInventory.tres` (its stacks are
copied, its items are not). Change that copy, never the `.tres`. A new kind of item is an `Item`
subclass plus an `ItemBrowser` sub-tab over `inventory.stacks_of(ThatKind)` in `InventoryTab`, which
gives it a sub-tab on both sides of every market too.

**Squad units are roster characters, spawned for each battle.** A `Character`
(`Resources/Characters/*.tres`) is who someone is between battles. `Campaign.roster` is a copy of
`Resources/StartingRoster.tres` whose list is its own but whose characters are the loaded `.tres`. A
combat map has no squad of its own: it has `SquadStart` markers under a `SquadStarts` node, and
`PlayerSquad` (its `starts_path`) spawns a `Scenes/SquadUnit.tscn` (a `Unit` in `players` with a
`Model`) on the tile under each, for each character `Campaign.squad(markers.size())` sends: those
chosen on the `SquadMenu`, in roster order. It sets `Unit.character` before adding the unit, then
gathers `players`, so the squad
panel, the reaction keys and everything else reading `PlayerSquad.members` follow roster order. It
does this in its own `_ready`, which runs after `CombatGrid`'s (for `tile_at`) and before anything that
reads the members. A marker's order among its siblings is its number; in the editor it draws an orange
square on the tile it counts as over, and nothing in game. So they are linked: a unit takes its
`display_name`, colour and the character's stats (`max_health`, `defense`, `move_range`, `aim`,
`melee_accuracy`, `strength`, `evasion`) from its character in `_ready` (painting its figure on a copy
of the material). Each is `Character.total(stat)`, not the character's own property: their own with
what their learned skills add (see "What a skill gives" below) and, for defense, their armor's
(`Character.total_defense` is `total(&"defense")`). They are copied once, when
the unit enters the map: the rules read the unit, never the character. The unit's other stats
(actions, sight, height bonus, distance penalty) are still its own, set in `SquadUnit.tscn`. A stat
that should differ per character moves to `Character`, gets copied in `Unit._take_character()` through
`total()`, gets a row in `DetailsPage.STATS`, and a name in `StatBonus`'s list, so a skill can add to
it. `Character.experience` (out of `Character.EXPERIENCE_TO_LEVEL`, 100)
is the character's alone and never copied to the unit. It only goes up through
`Character.gain_experience()`, where every 100 becomes a `skill_points` and the rest carries over (97 +
10 is 7 and a point; a big award gives several); any new way to earn experience calls that. So far the
one way is surviving a battle: as `TurnManager` decides the battle it calls
`PlayerSquad.award_survivors()`, which gives every member still standing `survival_experience` (50).
A win also adds `TurnManager.victory_gold` (10) to `Campaign.gold`, at the same moment, and has
`Coins.sweep()` pay for every coin still lying on the map (see Coins below).

What happens in battle goes the other way, through `PlayerSquad` as it happens, not at the end:
every change to a member's health is written to `Character.wounds` (health missing, so a character is
whole by default and stays as hurt if `max_health` grows; `Character.health` is what is left), and a
unit starts at its character's `health`. A grenade a member throws is gone for good: `Unit.use_up()`
emits `used_up`, and `PlayerSquad` calls `Campaign.use_up()`, which empties the first slot holding it
and puts nothing back in the inventory. A member who dies is taken off the roster by
`Campaign.lose()`, which returns everything they still had equipped to the inventory. Those two are
the only ways gear leaves a character mid-battle. The gear a dying member is seen to drop on the map
(see "The dead break apart" below) is only for show: it is in the inventory already. Wounds mend on
the road: every step the party travels (`Party.step_length`, the same step the encounters are rolled
on) calls `Campaign.heal(heal_per_step)` (1), which takes that off every roster character's `wounds`,
down to none, before that step's roll.
Unlike an `Item`, a character is state and changes in play; nothing writes it back to disk, and
save/load will need to store it. Enemies and `LineOfSightTest`'s units have no character
and keep the scene's name and material; the harness has no `SquadStarts` (`starts_path` is empty), so
its eight fixed units are its squad and spawn nothing.

**Every unit wears one rigged voxel figure for now.** A unit's `Model` child, squad or enemy, is an
instance of `Scenes/BaseCharacter.tscn`, which `Scripts/Characters/BakeCharacter.gd` makes from
`Characters/BaseCharacter.vox`. After editing the `.vox` (or the rig or the animations' scripts) bake
again: `--headless --path . --script res://Scripts/Characters/BakeCharacter.gd`. It overwrites the scene
and the two `.res` beside the model, so never edit those by hand or in the editor. The rules never read
the figure, as they never read debris: shots take a unit's body from `Ballistics`' constants and its
two cells. Each unit sets the figure's `body_material`, a plain `StandardMaterial3D` that ignores the
model's vertex colours, so it shows one flat colour: the scene's for enemies and the harness, the
character's `color` for the squad (`Unit._paint()` gives `CharacterModel.paint()` a copy). The enemies'
(`Mat_enemy1` in each combat map) is slate grey, `Color(0.32, 0.35, 0.4)`: they were red until blood,
which barely showed on them, so keep every unit's colour off red. The figure
shapes the unit's bodies (`Unit._add_bodies()`): an upright cylinder `PICK_RADIUS` round for clicks,
and the debris capsule as before, as thick as the figure's body; neither turns with it.

**The rig is rigid, one bone per voxel.** `VoxelRig` shares the model's voxels out between 18 bones,
named as Godot's `SkeletonProfileHumanoid` names them, by the layout's regions (boxes in the model's
own voxel coordinates, first match wins; a voxel in none goes to the nearest joint, with a warning),
and weights each wholly to its bone, so limbs move as solid blocks and never stretch. Each bone is
meshed on its own, keeping the faces where two bones meet, so a bent joint shows block ends, not a
hole. The rest pose is the model as drawn (a T-pose) with every bone unrotated, at 0.063 a voxel, centred on its footprint and stood on its lowest voxel. A new model needs a layout
(joints in rig voxels: x to the figure's left, y up, z forward) in `VoxelRig` and an entry in
`VoxelRig.LAYOUTS`, by its `.vox`, or can share `BASE_CHARACTER` if drawn to its proportions. The bake
reads that table (`BakeCharacter.LAYOUTS` is the same one) and writes the model's path into the figure
(`CharacterModel.voxel_model`); blood reads the figure's voxels by the two while the game runs
(`FigureVoxels`), and a model with no entry never bleeds, with an error. Blood relies on the rig being
rigid too: its stains are weighted wholly to their voxel's bone.

**Animations are poses written in code and baked.** `HumanoidAnimations` authors all 38 for the rig's
proportions: a function of time places the feet, the hands and what they hold, and leans the body,
and two-bone IK solves the limbs between, so a model with other proportions gets animations that fit
it by baking again. The rifle is held through `rifle_grip` and the rifle scene's `Foregrip` marker:
these arms reach only 8 voxels to the palm, which is why the aim holds the rifle under the chin and
the off hand just under the receiver, behind the fore-end. Each is sampled at 30 fps into an `AnimationLibrary`. Every stance
(`rifle`, `melee`, `unarmed`) has stand, crouch (on one knee behind low cover), wall (up close to
high cover), ready_throw, cheer, run and throw; the rifle has aim, overwatch, overwatch_crouch and
the back / strafe steps a rifleman takes stepping out, still aimed; the sword has ready_melee,
strike_sword, draw_sword and stow_sword; and there are hop, fall, and the reactions fire_rifle,
hit_front, hit_back, dodge and land, which key only what they move and are added to the pose. Clips
carry the moments the game waits on as metadata: `speed` on the runs (5 tiles a second, a stride a
tile), `impact` on the strike, `release` on the throws, `swap` on the draws. The editor's animation
panel can play them; a change made there is lost at the next bake.

**`CharacterModel` plays them through one `AnimationTree`.** Its `AnimationNodeBlendTree`
(`HumanoidAnimations.make_tree()`): `stance` picks the base loop; `move` blends it to `run`, scaled by
`run_scale`, whose `run_rifle` is a 2D blend of the forward, back and strafe runs; `hop` (legs only)
and `air` (falling) blend over that; `act` is a one-shot played whole (strike, throw, draw, stow) and
`react` a one-shot added on top. The tree resource is shared by every figure, so the model sets its
parameters and never its nodes' properties. Most of what it plays it reads off its unit each frame:
it runs while `Unit.is_moving()`, as fast as the unit really goes, so a reaction's slow motion slows
its legs and a held walk freezes them mid-stride; it faces the way it goes, unless the walk keeps its
facing (`Unit.walk(..., keep_facing)`, a step out to shoot); and a step up or down a level lifts it in
a hop, on the figure's own position, so the unit still moves in a straight line and `tile_at()` never
sees it. `Unit.drop_to()` sets it falling until it lands. The rest the unit asks for, through
presentational calls that do nothing without a figure: `aim_at()` (raise the gun to a point, which
`AimModifier` bends the spine and chest to, above or below), `ready_strike()`, `ready_throw()`,
`celebrate()` (the winners, as `TurnManager` decides the battle), `stand_easy()` (at the end of the
frame, called off if something is readied again at once, so a Shoot that begins again never lowers
the gun), `dodge()`, and `take_damage()`'s flinch. Between actions `Postures`, a node in each combat
map, moves only figures that are `is_idle()`.

**Gear hangs in the figure's sockets.** `CharacterModel.equip(gun, melee, grenades)` shows each item's
`Item.model`: a scene whose origin is where the hand grips it, standing along +z with its top up +y;
a gun's `Muzzle` marker is where it fires from and its `Foregrip` where the off hand holds it. The bake
makes the sockets: `RightHand/RifleGrip` and `SwordGrip`, `LeftHand/GrenadeGrip`, `Back/RifleSlot` and
`SwordSlot`, `Belt/Grenade1`..`3`. The gun is in hand; the sword is in hand without a gun, else slung
on the back and drawn for a strike, swapping with the gun at `draw_sword`'s `swap`; grenades hang on
the belt, one in the left hand while a throw is lined up. `Unit._dress()` calls `equip()` as the unit
enters the map and as it uses something up. A prop scene's `Mesh` is placed to put the grip on the
scene's origin: the importer carries where a model sits in MagicaVoxel's world into the mesh (`0 21 2`
for one left where MagicaVoxel put it), so the `Mesh`'s transform cancels that, and turns a model
drawn along another axis (`Rifle2.vox` lies along MagicaVoxel's x). Props import at 0.063, as the
figure does. Belt grenades are tucked in by their handles, the outer two fanned out so the heads stand
apart. A longer model reaches further than the poses were made for: preview its clips for it going
into the floor or the body (`ANIMATIONS.md` sections 11 and 13.7). Blood stains a prop as a voxel model
of its own (`CharacterModel.gear()`, `VoxelStains.on()`), drawn over it in its socket; a prop swapped
for another takes its stains with it, and since `equip()` builds the belt afresh whenever a grenade is
used up, every grenade left on it comes back clean.

**The dead break apart, and what they break into stays.** As a unit dies (`Unit.die()` emits `died`),
`TerrainDestruction`, which watches every unit's `died` (`_watch_units()`, deferred until the squad
has spawned), breaks its figure apart where it stands (`break_figure()`), as a block that wears away
crumbles: every voxel of the figure, posed as it was, goes into lumps of `VoxelDebris`
`crumbles_as.crumble_size` (3) across, cut on a grid set at random within each bone, so a lump is one
bone's (`FigureVoxels.crumble()`; the base figure's 536 voxels make some 60-90 lumps). A lump is the
unit's colour (`CharacterModel.tint()`), and a voxel blood stained is blood red. Each is knocked the way
the killing blow went, which `take_damage()` keeps on the unit (`Unit.hit_from`, `hit_blasted`,
`hit_at`, `hit_sweep`): along a round's way or a blade's swing (`FIGURE_KNOCK`), or away from a blast
(`FIGURE_BLAST_KNOCK`; the blast's own push then throws the lumps, held until the next physics step as
all new debris is, as it throws all debris), lifted a little and shared out by height, so the head
flies furthest and the feet hardly move, harder near where a round or blade landed
(`FIGURE_WOUND_PUSH`), and every lump bursts out from the body's upright middle, scatters and tumbles
(`TerrainDestruction.FIGURE_*`, drawn on its own generator, `_show`). The gear drops whole
(`_drop_gear()`): each prop shown in its sockets (`CharacterModel.gear()`) becomes a `RigidBody3D` piece
under `TerrainDestruction`, named `Dropped<prop>`, its mesh moved into it with whatever blood is on it,
colliding as a box round it and weighing `gear_wears_as.density` (`Gear.tres`, a crate board's) a cubic
cell of its voxels (a rifle is 4 kg), knocked as the lumps round it are. It passes through the rest of
the gear and the lumps it started out overlapping (a hand round a grip), as a crate's pieces pass
through those they were cut to overlap, and wears away as a crate's boards do once a round or a blast
first reaches it (`VoxelTerrain.take_on_later()`; `VoxelBody.scale` is the prop's 0.063 over a block's
0.0625). Then the figure hides (`CharacterModel.break_apart()`), to be freed with its unit. Lumps and
gear come to rest in 2-3 s and stay for the battle, debris like any other: blasts throw them, the
living shove them aside, the tidy takes any that fall off the map, and the rules never see them. With
blood off it breaks apart the same, with no red. A death costs about 1.6 ms on its frame, about 3.8 with
blood, which stains a killing wound at once rather than in its turn, so it is on the figure to break
apart (see Blood below).

Decided with the user, replacing the ragdolls the dead were before (`ANIMATIONS.md` 9.8): lumps like a
crumbling block's, not a body falling whole or in a few limbs; the same with blood off; gear dropped
whole as debris that wears, not broken up with the body; the pool under the dead where the unit stood.

**Equipment is on the character, the spares in the inventory.** A character has six typed slots
(`armor`, `weapon_1`, `weapon_2`, `item_1`..`item_3`), listed with their titles and kinds in
`Character.slots` (a `static var`: a `const` cannot hold a class). Every item is either in
`Campaign.inventory` or in one slot, never both, so equipment only changes through
`Campaign.equip()` / `unequip()`, which move one copy across and put a swapped-out item back. What a
character starts with is set in their `.tres`, not counted in `StartingInventory.tres`. What is
equipped decides a squad unit's actions by its tags (see "An action can need an item"): with no gun
it has only Move. It shoots with the first gun in its slots, Weapon 1 before Weapon 2
(`Unit.weapon`, null with none), and strikes with the first melee weapon, the same way
(`Unit.melee_weapon`), which gives it Strike. A grenade in any item slot gives it Throw Grenade,
which throws the first one, Item 1 before Item 2 before Item 3 (`Unit.grenade`), and uses it up.
Armor adds its `Armor.defense` to the wearer's (`Character.total_defense`),
which the unit copies as its own; the Details page shows that total and refreshes as it comes into view, since the
Equipment page may have changed the armor. During a battle `Campaign.in_mission` is true (the `TurnManager` sets it while in the
tree) and both calls refuse, since a unit took its gear when the map loaded; the Equipment page greys
its buttons and says why. This is the menu's first read-only-in-combat rule; the System tab's
**Blood** button is the second (see Blood), and learning a skill the third (see Skill trees).
`Campaign.use_up()` and `lose()` do not refuse: they follow what the battle did.

The Roster tab is a `CharacterBrowser`, whose sub-tabs are `CharacterPage`s. Whenever the selection
in the strip changes, every page (not just the open one) gets `show_character(character)`, so a page
is never left showing someone else; a page with content overrides `_refresh()`, and
`focus_selection()` if Down from the sub-tabs should land somewhere in it. Changing character keeps
the open page; opening the menu goes back to Details. A page that can change the character hides
the means when `read_only` is set, as it is for characters not on the roster.

**Skill trees are data, and any shape.** A `Skill` (`Resources/Skills/`) is a stateless `.tres` like
an `Item`: a name, a line of flavour text, an icon and its levels, each with its words and what it
gives. A `SkillTree` places skills as
`SkillTreeNode`s, each with an `id` unique in its tree, a `cell` on the tree's grid (column, row,
from 0 at the top left) and `requires`, the ids of nodes in the same tree that must all be learned
before it can be (`SkillTree.is_open()`). A tree's shape is nothing more than where its nodes sit and what
they require: a column of nodes each requiring the one above is a path, two requiring one node a
fork, one requiring two a join. A skill is kept apart from where it sits so one can sit in several
trees (decided with the user): `Placeholder.tres` sits in seven of the eight nodes of the Human and
Minor Noble trees. A node's `id` is what a character's progress keys on, and saves will, so never rename
one once in play.

A tree belongs to a `SkillSource`, the base of `Species` (`Resources/Species/`), `SubSpecies`
(`Resources/SubSpecies/`) and `CharacterClass`, each with its tree as a sub-resource in its `.tres`.
A sub-species is a kind of exactly one species (`SubSpecies.species`; decided with the user); a class
has one tree, shown the same whether it is the Main Class or the Multi-Class (also decided). A
`Character` holds one of each, `species`, `sub_species`, `main_class` and `multi_class`, any of them
unset, listed with their titles in `Character.TREES`. Every character is a Human Minor Noble, and no
class exists yet. Nothing checks that a character's sub-species is one of their species' kinds: keep
them agreeing.

**Skills are learned by holding a node.** What a character has learned is theirs, like their wounds:
`Character.learned`, the node ids of each tree in the order learned, keyed by the `SkillSource`
resource (not by the column, so a tree's progress follows the species or class, wherever it shows).
It only changes through `Character.learn()`, which spends one skill point a node, every node the
same, and refuses, changing nothing, unless `can_learn()`: the tree is one of the character's own
(`TREES`), the node is in it and not yet taken as often as it can be, everything it requires is
learned, and there is a point to spend. The page learns through `Campaign.learn()`, which refuses
first during a mission, as `equip()` does: a unit will take what its character has learned when the
map loads.

**A skill has a level for each time it can be taken.** `Skill.levels` is a list of `SkillLevel`s
(sub-resources of the skill's `.tres`) in the order they are taken: the first is what learning the
skill gives, each after it what taking it again adds, for more or different benefits each time. A
level has its `description`, the words its tooltip shows, and its `effects`. How often a skill can
be taken is how many levels it has (`Skill.takes()`: at least once, with none, and at most
`Skill.MOST_LEVELS`, 5, the first and four more), so there is no separate count to disagree with
them: a level is added by adding one. They are the skill's, so the
same in every tree that places it, and `SkillTreeNode.takes()` is its node's count. Every take is a
`learn()` of its own, a skill point each, and
`Character.learned` lists the node's id once for each (`times_learned()` counts them), so the list is
still the order things were learned in. A requirement is met by taking the node once, however often
it can be taken (`is_open()` only asks whether the id is there): assumed, not asked of the user, as
is a press of the button taking it once at most, as every hold does. `Ambition.tres` (five levels)
is the Human tree's first node, `ambition`; the other seven are still `Placeholder.tres` (one level,
no effects).

**What a skill gives is its levels' effects, and a character has those of every level taken.** An
effect is a `SkillEffect` resource in a level's `effects`, and a kind of effect is a subclass, as a
kind of enemy is an `EnemyAI` subclass: `StatBonus` (a `stat` from its list, an `amount`) is the only
one so far. Levels add up: a character has the effects of each level they have taken, the earlier
with the later, so a level holds only what it adds (Ambition's five are +1, +1, +1, +2 and +5
`max_health`, +10 in all, as their words say: "An additional +2 HP (for a total of +5 HP)").
`Character.skill_effects()` gathers them, from every node of the character's own trees (`TREES`) by
how often `learned` has it; what was learned of a tree no longer theirs gives nothing.

Nothing is applied when a skill is learned, and nothing stored but `learned`: the rules ask the
effects when they need an answer, which `SkillEffect`'s methods are, each answering nothing unless
a kind overrides it. So far the one question is `bonus_to(stat)`, asked by `Character.total(stat)`:
the character's own stat (the exported property, never changed by a skill or by gear) plus every
effect's bonus to it, plus the armor's for defense. Everything that wants a character's stat reads
`total()`: `Unit._take_character()` for all seven, so a bonus goes into battle with the unit;
`Character.health` (`total(&"max_health")` less `wounds`), so a level of Ambition raises the most
health and what is left alike, and a wounded character stays as wounded; and the Details page, which
refreshes as it comes into view. A unit copies its stats as the map loads, which is why learning is
refused during a mission. A new skill of a kind that exists is only a `.tres`. A new kind of effect
(an action granted, a rule bent) is a `SkillEffect` subclass, a method on the base class asking what
the rules need to know of it, and a call where they need it, over `skill_effects()`.

The Skills page has a column per `Character.TREES` entry, its share of the width from
`SkillsPage.SHARES`, and is rebuilt for every character, a column headed by its source's
`display_name` ("Human"), or by its plain title ("Species") with no tree under it while the
character has none. A new kind of tree is a `SkillSource` subclass, a `Character` property and a
row in `TREES` (and in `SHARES`, unless 1 will do). Each tree is a `SkillTreeView`,
which places its `SkillButton`s itself by their cells (`GAP` apart) rather than in containers, and
draws every link as an elbow: down from the node required, across just above the row of the node
requiring it, and down into it, so a path is a straight line; lit once the node required is learned.
A button with rings is bigger (`SkillButton.size_of()`: `RING_GAP` + `RING_WIDTH` more each side a
ring, 84 across with four against 44), so cells are not all one size: a column is as wide as its
widest button, and a row as tall as its tallest button in any tree on the page
(`SkillTreeView.row_heights()`, which the page works out over every tree it is about to show and
hands to each view), so the trees' rows stay level across the columns. Each button sits in the
middle of its cell, and a link runs from the bottom of one button to the top of the other, outside
their rings.
A link to a node on the same row or higher, which a tree should not need, is a straight line between
them. It warns of two nodes with one id, and of a requirement the tree lacks; nothing stops two
nodes sharing a cell. A button is a circle (it takes the mouse only inside it, `_has_point()`) that
draws itself, its theme's boxes all empty, so the fill can go under its face: its skill's icon,
dimmed while locked, or its rank (its row, from 1). The arrow keys are pointed from a button as
it takes focus, once the trees are laid out, at the nearest button that way (`_nearest()`): up and
down within its own tree, left and right on across the trees. With none to the left or right it stays
put; with none above or below, the key is left to Godot, which takes up back to the sub-tabs and down
to whatever lies under the page: the squad menu's Start, a hiring board's Hire (as Down from the
sub-tabs of the Details page reaches them), and nowhere in the pause menu, which has nothing there.
Up from those buttons goes to the sub-tabs, and Down from the sub-tabs back to the selected node.

A node is learned by holding it down, with the mouse or Enter / Space, as a `HoldButton` is held
(its `HOLD_TIME`, 2 s, its `DRAIN_SPEED` and its fill colour, decided with the user): it fills like a
clock's face, from the top round clockwise, a sector drawn under its face. That is the first time it
is taken. A skill that can be taken again has a ring round the circle for each further time, drawn
dim from the start, and once it is taken a hold draws the innermost ring not yet lit round instead,
the same way, from the top clockwise (decided with the user: the circle first, then the rings from
the inside out); `SkillButton.taken`, which `show_learned()` sets, says which. The rings are part of
the button, so a press on them counts. Let go early it drains;
full, it emits `held`, empties and stays empty until let go, so a press learns one skill at most. It
fills only while the page has set it `learnable`, which `_show_progress()` sets for every node from
`can_learn()`, and never in a mission or read only; any other node can still be pressed and selected,
and nothing happens. On `held` the page calls `Campaign.learn()` and `_show_progress()` again, which
restyles every tree (`SkillTreeView.show_learned()`: learned, open or locked, links lit) in place,
rather than rebuilding, so the selection and the keyboard stay where they were. Nothing on the page
says how to learn, or why a node will not fill (a mission, no points): a help line under the trees
was taken out at the user's request, for now.

A button is not a toggle: holding a toggle button reads as pressed whether it is held or not
(`get_draw_mode()`), which the fill depends on. So the page keeps the selection itself, `_selected`,
moved as a button takes focus (a click or the arrow keys), and sets the button's `selected`, which
fills its circle a shade lighter: blended toward `SELECTED_COLOR`, a near white, by `SELECTED_BLEND`
on a dark circle and by `SELECTED_LEARNED_BLEND` on a learned one's gold, where as little would not
show. That fill is all that shows where the keyboard is (asked for by the user in place of a white
ring round the node, which they had taken out), and it is not the accent, which is kept for what is
learned and being learned. It stays on the selected node while the keyboard is up on the tabs, as a
selected character's frame does, since Down comes back to it. Changing character clears
it. The page also titles its own sub-tab, "Skills (2)" from
`Character.skill_points`, again after every skill learned. It reads `Campaign` only once a character
is shown: the pause menu builds its pages before that autoload exists.

**A skill's tooltip is the page's own panel, not Godot's.** A built-in tooltip only follows the mouse,
and a skill's has to show for the keyboard too, so `SkillsPage` owns one `SkillTooltip`, a child added
after the columns so it draws over the trees, and a `SkillButton` has no `tooltip_text`. Its parts,
from the top, are the user's: the skill's name; its `flavor`; "Current:" and `Skill.describe(taken)`,
once the character has taken it; "Next:" and `Skill.describe(taken + 1)`, while a level is left to take,
whether or not it can be taken now (locked, or no points). A part with nothing to say is left out.
It is `WIDTH` (300) wide and as tall as its text: every label has its wrap width as its minimum
width, so it knows its height the moment its text is set and `reset_size()` fits the panel there and
then, with no frame's wait for a container. It never takes the mouse, so a node under it can still
be hovered and held.

Whose it is: the node with the keyboard (`_focused`, kept from the buttons' `focus_entered` /
`focus_exited`) when a key was pressed more recently than the mouse did anything, else the node under
the mouse (`_hovered`), else nobody and it hides. The page's `_input()` notes which was used last
(`_by_keyboard`), before either moves anything, so arrowing about with the mouse left lying on a node
shows the keyboard's node, and a nudge of the mouse hands it back. It hides once the keyboard goes up
to the tabs, though the node stays selected. `_show_tooltip()` places it to the node's right, top to
top, `TOOLTIP_GAP` off, or to its left where that would run off the page, and never below the page's
bottom; `_show_progress()` calls it again, since a level just taken changes what it says.

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
turn to hand the camera back. A window only exists during a walk; nothing else opens one. The
walker's figure runs at whatever speed the tween goes, so it slows with the window and freezes
mid-stride while held, and nothing here has to tell it.

**A shot is settled when it is fired and lands when it arrives.** `Unit.shoot_at(shot, chance,
grid, show_rounds)` first has the shooter's figure take aim at the target's eye (turned to it, gun up:
at once if the shot was lined up with `aim_at()`, as `ShootAction` and `ShotPlayback` both do before
anything else), then rolls, then asks `Ballistics` for the round's `Path`: the sight line for a hit;
for a miss, XCOM 2's placement, an aim point on a ring around the target's body (or, `COVER_SHARE`
of the time, on the target's cover) traced with `CombatGrid.cast()` until something stops it or it
leaves the map. The figure kicks and flashes, and `Outcome.muzzle` says where its muzzle was, which
`ShotOverlay` draws the tracer from: only the drawing, as every path is still flown from the eye. For
a hit the target's figure then picks where the round is seen to land (`Path.wound`, see Blood), which
the tracer is drawn to (`Path.drawn_to()`). It then awaits `show_rounds` (`ShotOverlay.show_rounds`,
which draws the tracer and returns as it lands), and only then damages the target (or has it duck a
miss), the muzzle as where the hit came from and the wound as where it landed, and reports any
terrain the round struck through `CombatGrid.strike()` as `terrain_struck`. `shoot_at` is a
coroutine; always `await` it. A step out walks with `keep_facing`, so the shooter sidesteps out and
back with its gun on the target.

**Breakable blocks are data.** `TerrainDestruction` (a node in each map) listens to
`terrain_struck` and looks the struck block up in `Resources/Destruction/Catalog.tres`, a
`DestructionCatalog` of `Destruction` resources each naming a block by its MeshLibrary item name.
A block with no entry never breaks. A breaking block leaves the grid at once, then its destruction's
`shatter(site, at, hit, motion)` plays out what is left under the `TerrainDestruction` node, `at`
being where the grid drew the block's mesh.

It listens to `terrain_blasted` too (`CombatGrid.blast()`, a grenade going off): every breakable block
among the blast's cells breaks, from the top down, so each is blasted apart where it stands rather
than first falling on to the one below it (blocks stacked above the blast still fall, as usual). It
passes no `hit`, so the pieces get no knock from a round; instead, once they are let go a physics step
later, `Blast.burst()` throws every loose piece inside the blast (new and old, not a `FallingBlock`)
from the grenade's centre with its `blast_force`, on top of the crate's own burst.

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

**Coins are rolled as blocks break and go by tiles.** `TerrainDestruction` emits
`block_broken(cell, destruction)` for every block that breaks: from `_break` with the cell it stood
in, and from `_on_landed` with the cell a `FallingBlock` landed in (from `Motion.center`). `Coins`, a
node in each combat map, rolls that destruction's `coin_chance` (0 unless set; `BrightCrate1.tres`
has 0.75) and on a success puts a `Coin` on that cell, as a tile: floating with its centre at the top
of the cell, `Coins.STACK_STEP` over any already there. Every frame it moves the coins of any tile
whose ground has gone (`is_solid(tile + DOWN)`) to `CombatGrid.tile_under()`, on top of what is
there, and takes every coin on the `tile_at()` of each living unit in `players`. That is every frame,
not on a timer, so a tile crossed in a fifth of a second is not missed, and it is by position, so
walking a path, stepping out to shoot and dropping when the ground goes all pick up. Each coin is
`Coins.value` (1) gold into `Campaign.gold` the moment it is taken, so it is kept whatever comes of
the battle, and `ShotOverlay.flash_pickup()` calls "+N Gold" over the taker's eye. That call, unlike
`flash_results()`, replaces nothing: each pickup fades on its own time, so a shot's damage is never
lost to it. A blast top-down leaves its coins in the cells the crates stood in, so the upper ones
fall a frame later on to the bottom one's tile. `sweep()`, on a win, pays for every pile, calling
each over it, and sets `_swept`, after which a block that breaks (one still falling as the battle
ends) pays at once and leaves no coin. The `Coin` node is only for show: it is spun and bobbed on a
child, so its own position is where it rests, and the model is centred on its box, since
`Coin2.vox` is drawn well off its origin. It is nine voxels across at the props' 0.063, a little over
half a cell, so it is not scaled; `Coins.STACK_STEP` (0.7) must stay more than its height plus its
bob, or a stack's coins touch.

To make another object break like the crate:

1. Model the pieces in MagicaVoxel in the same frame as the block's own model, as separate models.
2. Import the `.vox` as a Scene at **Scale 0.0625**, the blocks' scale, or the pieces will not line
   up with the block they replace. Make an inherited scene of it in `Scenes/` to add to.
3. Make a `ScriptedDestruction` `.tres` in `Resources/Destruction/` naming the block and that scene,
   and add it to `Catalog.tres`. Set its **Mass** to what the block weighs whole, if it is not
   about a crate's 300 kg; that is only felt while it falls. Set its **Coin Chance** (0 to 1) if it
   should leave coins, as a crate does three times in four. Set its **Wear** (see below) if blood on
   the block should go to its pieces when it breaks: only pieces that wear can carry stains.

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

**Some blocks wear away instead, a few voxels at a time.** A block whose catalog entry is a
`VoxelDestruction` (`BrightGrass1`, both `SkinnyTree1` blocks) is the second kind of breakable block:
a strike or a blast breaks voxels off it rather than breaking it whole. Every block is 16 voxels a
side, and its voxels are read on ready from the `.vox` its MeshLibrary mesh was imported from
(`VoxelShape.read()`, with the importer's own reader, so they sit exactly where the imported mesh
draws them). `TerrainDestruction` makes a `VoxelTerrain` node, which keeps them, and a `VoxelDebris`
node, which keeps what is broken off, and hands the grid the terrain (`CombatGrid.voxels`).

- **A worn block draws itself; the rules see its stand-in.** The first time a block loses a voxel,
  `VoxelTerrain` makes it a `WornBlock` (its own mesh and trimesh collision, rebuilt as it wears) and
  swaps its GridMap cell to the block's stand-in, an item `take_on()` added to the map's library copy
  with no mesh and no shapes. `CombatGrid.is_solid()` only asks whether a cell has an item, so sight,
  cover, paths, throws, coins and units see the whole block, however little is left. Anything that
  reads a cell's item id must allow for a stand-in (`VoxelTerrain.wears_away()`, `shape_at()`, or
  `kind_of()` for any block drawn from a `.vox`, worn or not).
  Unworn, a block that does not fill its cell (a tree) collides as its voxels, a trimesh from
  `VoxelMesher.faces()`; a full one keeps the cube.
- **A round takes a bite.** `terrain_struck` on such a block calls `VoxelTerrain.chip()`: the
  `damage * voxels_per_damage` voxels nearest where it struck (12 a point; 60 for a rifle's 5),
  roughened with noise, from whichever blocks they are in, out to `BITE_SPREAD` times the bite's own
  radius. They fly out of the struck face in lumps up to `DEBRIS_CLUMP` (2) voxels across, and the
  block is redrawn at once.
- **A blast blows a crater.** `terrain_blasted` calls `VoxelTerrain.crater()` first: every voxel within
  `crater_radius(damage)` of where it goes off (a ball of `crater_per_damage` cubic cells a point,
  a radius of about 1.06 cells for a frag grenade's 10), roughened, but only in the blast's
  cells. Up to `CRATER_DEBRIS` (150) lumps are thrown up and out, the ground throwing back what the
  blast drives into it; the rest is dust. They are chosen before any is made: what wear breaks off
  comes back grouped into lumps (`Batch`), and `_scatter()` makes only those it keeps, since making a
  lump costs about three times what grouping its voxels does (a grenade on raised ground breaks off
  some 1,600 lumps). Its blocks are redrawn over the next frames, no more than `REBUILD_BUDGET`
  microseconds a frame, under the fireball.
- **What is cut loose drops.** After any wear, a voxel left joined to nothing that holds it (a voxel
  or block across a face of its cell, or the ground under the bottom layer) breaks off too
  (`_loose_voxels()`, searched from the voxels next to those just lost, which the rows find).
- **Worn past standing, it breaks.** A block left with less than `collapse_below` (half) of its voxels,
  or one holding something up that nothing joins from its bottom to its top any more (`_holds_up()`:
  the trees' trunk is one 4x4 layer of voxels at its narrowest, so a couple of rounds through it fell
  the tree), is in `Wear.broken`, and `TerrainDestruction` breaks it as it breaks a crate: out of the
  grid at once, `block_broken`, stacks above fall, units drop. What is left crumbles
  (`VoxelTerrain.crumble()`) into lumps `crumble_size` (3) across; one that fell whole
  (`_drop_worn_block()`, a `FallingBlock` showing what is left of it) crumbles where it lands.
- **The bottom layer never breaks,** and is only worn `FLOOR_DEPTH` (4) voxels deep, since a unit
  stands at the top of its block whatever is left of it. A crater there is a flattened bowl centred
  under the blast, as wide as the ball is where it meets the ground.
- **Rounds are traced voxel by voxel.** `CombatGrid.cast(..., by_voxel)`, which of the rules only
  `Ballistics` passes, asks `VoxelTerrain.trace()` in each solid cell that wears away and carries on
  through the cell if the ray meets none of its voxels; the hit's `point` and `face` are then the
  voxel's, and its `index` the voxel's place in its block. Sight (`is_line_clear()`), throws
  (`Throwing.plan()`) and clicks (`pick_tile()`) stop at whole cells. Blood passes `every_block` as
  well, which traces every block drawn from a `.vox` so, crates included; rounds never do.
- **The debris is lean.** `VoxelDebris` makes each lump a rigid body straight on the `PhysicsServer3D`,
  with no node, on the debris layer, and draws every voxel as a cube instance of a few MultiMeshes,
  coloured as it was. A lump's voxels move only from the server's state-sync callback, so a lump at
  rest costs nothing a frame. Blasts push it (`burst()`), a redrawn block wakes what lay on it
  (`wake()`), `TerrainDestruction` tidies it with the rest (`tidy()`), and units dropping through a
  collapse pass through it, which is why `Unit.pass_through()` and `drop_to()` take body RIDs.
- **Lumps stay for good; their bodies do not.** The moment the lumps' bodies reach
  `VoxelDebris.MOST` (20,000), `_make_room()` stills the lumps at rest furthest from `focus` (the
  middle of the tile the camera is looking at, `TerrainDestruction._looked_at()`: where the middle of
  its view first meets the ground) until fewer than `KEEP` (5,000) have bodies. A stilled lump loses
  its body but stays drawn where it lies, so nothing leaves the board, and the bodies go to what the
  player is watching and to everything broken off from then on. A lump that moved in the last
  `RESTING_STEPS` physics steps is never stilled, so nothing freezes in mid-air. A stilled lump gets
  its body back, lying as it lay, the moment anything disturbs it: a blast reaching it (`burst()`), a
  worn block under it being redrawn or a broken one going (`wake()`, `LYING_ON` round the block, the
  whole column above a broken one), or a unit on the move coming within its cell
  (`TerrainDestruction._wake_in_the_way()`). Lumps are filed by the world cell their middle was last
  in (`_by_cell`), so those calls look only at the cells they reach. Clearing 15,000 bodies takes
  about 30 ms, on the frame that reaches the limit.
- **It is deterministic.** Which voxels go, and so which blocks break, comes from the global random
  generator, one number a round or blast, so a seeded fight replays exactly, as long as no block
  falls whole (see Known gaps). How the lumps fly, and which a blast keeps, draws on `VoxelTerrain`'s
  own generator, and how they fall is physics: only for show.

To make another block wear away, add a `VoxelDestruction` `.tres` naming it in
`Resources/Destruction/` to `Catalog.tres`, with its `mass` whole (what it weighs falling), its
voxels' `density`, and `voxels_per_damage` / `crater_per_damage` for how soft it is. Its mesh must be
imported from a `.vox` at Scale 0.0625, one cell to sixteen voxels.

**A broken crate's pieces wear away as well, as loose models.** The crate still breaks into its
pieces as cut, and bursts as before; only then do they break down further, as a block does. Any
voxel model loose in the world can be worn this way: a `RigidBody3D` drawn by a MagicaVoxel model in a
`MeshInstance3D` among its children, taken on with `VoxelTerrain.take_on_body()`, which puts a
`VoxelBody` node under it. So far only a `ScriptedDestruction`'s pieces are.

- **A piece is taken on the first time something reaches it.** A `ScriptedDestruction` with a `wear`
  (a `VoxelDestruction`; `BrightCrate1.tres` has `CrateBoards.tres`: 3 voxels a point of damage, lumps
  of 2) only notes each piece as `shatter()` makes it (`VoxelTerrain.take_on_later()`, a `Wearable`),
  with the bodies `_pass_overlaps()` found it overlapping. A round's line or a blast's crater reaching
  it takes it on (`_model_of()` calls `take_on_body()`): its voxels come from the `.vox` the pieces
  scene inherits (`VoxelShape.source_of()`), the model whose `magica_voxel_model_id` the importer put
  on its `MeshInstance3D`, cropped to its voxels (`read_model()`): each of the crate's models is a
  whole crate's frame with only that piece in it, 36 to 64 voxels. Most pieces are never hit, and
  taking one on (copying its voxels, a node, its bounds) cost a crate 1.7 ms of its 3.6. A blast takes
  on only the pieces whose box its crater reaches. `Destruction.prepare()` reads every piece's model
  as the map loads (about 10 ms for the crate), so the first crate to break does not catch on it.
- **A round tears through them and flies on.** `Unit.shoot_at()` reports every round's line, from the
  muzzle (where its tracer starts) to where it landed, through `CombatGrid.fly()`, whose `round_flown`
  calls `VoxelTerrain.tear()`. Every loose model the line passes through (ray queries on
  `PIECE_LAYER`, nearest first, at most `MOST_TORN`, 8) loses the `damage * voxels_per_damage` voxels
  nearest where the line first meets one of its voxels (`VoxelTerrain.march()`, the static voxel walk
  `trace()` uses on blocks and blood uses on figures and props; 15 for a rifle's 5), which fly out of
  the face it went in by. `fly()` comes before
  `strike()`, so a crate a round breaks is not torn by the same round.
- **A blast craters them.** `crater()` craters every loose model reaching into the blast's box
  (`TerrainDestruction.pieces_in()`) as it does blocks: the voxels within its `crater_radius()` and
  inside the box. The burst a physics step later throws them, as it throws every piece.
- **What is left settles** (`_settle()`). A model left with fewer than `SMALLEST_PART` (8) voxels, or
  under its destruction's `collapse_below` of `VoxelBody.whole`, crumbles into lumps `crumble_size`
  across, carrying on as it moved, and its body goes. Otherwise every part no longer joined face to
  face to the biggest (`_parts()`) is cut off: as a model of its own if it has `SMALLEST_PART` voxels
  (`_split_off()`: a new `RigidBody3D` and `VoxelBody` beside it, in the same frame, moving as that
  part moved), as lumps if not. What is left is redrawn (`VoxelMesher.surface()`), its box collider
  fitted to it (shrunk by `ScriptedDestruction.SLACK`), and it weighs its share. After a cut each
  part's `whole` starts again from what it has, so a board shot in two is two boards, each worn down
  from its own size.
- **A part cut off passes through what its model did.** Their boxes overlap wherever the cut ran, so
  a part passes through the model it came from, everything that model passed through (a crate's
  pieces cut to overlap), and every part cut from it since; `VoxelBody.passes` keeps the list on both
  sides, and a piece not yet taken on keeps its own in its `Wearable` (see Gotchas).
- **It does not touch the rules.** A loose model blocks nothing (sight, cover, rounds, throws), and
  everything random about wearing one draws on `VoxelTerrain`'s own generator (`_show`), never the
  global one, so tearing boards never changes what a seeded fight rolls next. Blocks still take one
  global number per round or blast.

A crate breaks in about 2.2 ms; a round through boards costs 1 to 3 ms, taking on those it hits, and
a blast among a crate's boards 14-20 ms more than the blast alone, about 2 ms of it taking on the
boards its crater reaches. To have
another `ScriptedDestruction`'s pieces wear, set its `wear`: its pieces scene must inherit a `.vox`
imported as a Scene at 0.0625. A body made some other way can be taken on directly, its `source` the
`.vox` its model came from, or none if the mesh was imported straight from a `.vox`.

**Blood is painted on voxel faces, and only for show.** `Unit.take_damage()` emits
`hurt(taken, from, at, blasted, sweep)` for every hit that takes health (none for one defense stops),
before the unit can die of it. `Blood`, a node in each combat map after `Coins`, connects to every
unit as it readies and does the rest; it reads each figure's rig as the map loads (about 10 ms for
the base figure, and its gear's `.vox`), not on the first hit.

**The player can play clean.** **Blood** on the pause menu's System tab, just under **Tile Grid**,
turns it all off: `Blood.enabled`, a static like `TileGrid.shown`, so it holds from battle to battle
until the game closes and is never saved. It only changes between battles, on the world map: while
`Campaign.in_mission` the menu greys the button out and shows a note under it saying so
(`SystemTab.show_blood_state()`, called as the menu opens, since the menu is made before `Campaign`
is), and each map's `Blood` reads `enabled` once, in `_ready`, so a battle keeps what it began with
and nothing has to be cleaned off or added mid-fight. Off, `Blood` still reads every figure's rig as
the map loads, since a shot still draws its tracer on to the body (`pick_wound()`), then stops: it
connects to no unit and never processes, so no wound, drop, stain or pool is made, and no lump turns
red. The lock is the menu's alone: `Blood` must not name `Campaign`, or no probe could name `Blood`
(see Gotchas).

- **A hit is drawn landing on the body, not at the eye.** The round still flies eye to eye
  (`Ballistics`), but as it is fired `Unit.shoot_at()` asks the target's figure where it is seen to
  land: `CharacterModel.pick_wound()` picks a voxel by bone, mostly the torso
  (`FigureVoxels.WOUND_WEIGHTS`), and traces from the muzzle to it, so the point is the first voxel
  facing the gun. It goes in `Ballistics.Path.wound`, which `ShotOverlay` draws the tracer to
  (`Path.drawn_to()`), as the muzzle moved its start, and `take_damage()` passes it on as `at`. A
  strike picks one from the striker's chest (`Unit.STRIKE_HEIGHT`) and passes its figure's `swing()`
  as `sweep`; a blast passes neither, and `Blood` picks two to four wounds facing it. On landing
  `FigureVoxels.hit_near()` finds the spot on the figure as it stands then.
- **The figure bleeds and sprays.** A wound stains `WOUND_FACES` and 4 more a point of damage (counting
  at most `MOST_DAMAGE`) round where it landed. It leans a little downward rather than running down:
  the even splash round a wound (`FigureVoxels.WOUND_SPLAT`, 2 voxels) wraps round a torso only 5
  voxels wide and 2 deep and takes most of the stain. Over 40 wounds its middle sat 0.8 voxels below
  the wound and its lowest face 3.6 below, against 0.1 and 2.4 with downhill costing no less. In the
  standing pose the arms cover the chest, so many wounds land on a forearm, where blood cannot go
  lower without crossing the arm's underside. Every hit sprays `DROPS` and 8 more a point: a round's
  mostly out of an exit wound, found by tracing back through the figure along the round's flight
  (`FigureVoxels.exit()`), which bleeds too, and the rest back toward the gun; a blade's along its
  swing; a blast's away from it. A drop leaving a figure passes through it for `CLEAR_SECONDS`.
- **A drop is a voxel under gravity**, a cube one or two voxels across in one MultiMesh, stepped every
  physics frame and traced along its step: through the terrain voxel by voxel, every `.vox` block,
  crates' slats and gaps too (`CombatGrid.cast()`'s `every_block`, which only blood uses); against
  every living unit's figure whose ball it passes near (`FigureVoxels.march()`: each bone's voxels are
  a part in its bone's posed frame, culled by a sphere, and so is the gear in its sockets); and against
  debris, by a physics ray on the debris layer (a lump by its RID, a dead figure's among them; a piece
  that wears away, dropped gear among them, taken on and traced through its voxels; falling blocks
  passed). It
  lands on the first it meets, and is forgotten once below the map. **Coins are the one exception:**
  blood never looks for them, so a drop flies straight through a coin to whatever is behind it, and
  no coin is ever stained. Keep it so.
- **Where blood lands, it runs** (`BloodFlow`): it stains up to its volume of faces, always the one
  cheapest to reach next (Dijkstra over voxel faces: across each edge of a face to the face beside
  it, up the wall rising there, or round on to the voxel's own side). A flat step costs the same every
  way, roughened by smooth noise and a speckle, so a pool is a blob with lobes; downhill is cheap, so
  blood runs over an edge and down before it spreads far on top; sideways along a wall dear, so it
  streaks down; climbing dearer, so it barely climbs; undersides never. Within `splat` voxels of
  where it landed it spreads every way alike. Faces already stained cost little and no blood, so a
  drop landing in a pool runs out to its edge, looking at most `VISITS` + 3 a face. The terrain is one
  grid of voxels across every block (`TerrainSurface`), so a pool crosses from block to block; a
  loose model or prop is its own (`ModelSurface`), and so is a figure, standing as drawn with
  down taken from each voxel's bone (`FigureVoxels.FigureSurface`).
- **The dead bleed out.** `died` hands `Blood` where the unit stood; `POOL_DELAY` (1 s) later, once
  the lumps its figure broke into have mostly landed, a flow of `DEATH_FACES` (800, about two tiles
  across on flat ground) starts on the ground under its feet, or below them if it died falling, and
  spreads over `DEATH_SECONDS` (3), quickly at first, under the heap.
- **A killing wound is stained at once.** A hit that kills (`taken` at least the unit's health as
  `hurt` goes out, before it is taken) stains its wounds there and then (`_wound(..., now)`), not
  queued with the landings, since the figure breaks apart a moment later in the same call and its
  lumps take their colour from its stains (about 2 ms).
- **Landings wait their turn.** Wounds and landed drops are queued and settled oldest first for up to
  `SPLASH_BUDGET` microseconds a physics step, the rest the next: a stain a frame late is not seen.

A stain is a face, never a voxel's colour: `VoxelStains` keeps each stained voxel's faces as six bits
(+x, -x, +y, -y, +z, -z), by its place in its model's array, and draws them by an overlay, a
`MeshInstance3D` of red squares `PROUD` (2 mm) off each face along its normal, rebuilt once at the end
of the frame (`changed()`), so blood never rebuilds a block or a figure. A face shows only while its
voxel is there (each rebuild reads the model's voxels as they are now), and is only stained while open
to the air (voxels are never added, so it stays open).

Overlays rather than recolouring the models, because rebuilding a block's own mesh
(`VoxelMesher.surface()`) costs 1.5 ms for grass, 2 for a tree and 3.3 for a crate, and a burst of
drops lands on dozens of blocks at once, where a stained cell's overlay rebuilds in about 0.1-0.3 ms;
and the GridMap goes on drawing the block, so staining one needs no stand-in.

Nothing moves a stain on its own. It is recorded by which voxel of which model it is on, and its
overlay is built in that model's own space and hangs from whatever draws the model, so whatever moves
the model moves its stains: the scene tree for blocks, boards and gear, the skeleton for a figure. Only
when a model becomes others (a block falling whole, a crate's pieces, a board cut in two, a voxel
broken off) is a stain handed on, by these rules. Where they live:

- **Blocks:** `VoxelTerrain`, by cell, for every block drawn from a `.vox` (`kind_of()`, crates
  included, which do not wear), the overlay under `VoxelTerrain` in the cell's frame. Wear hands the
  cell's stains to its debris, so a stained voxel's lump is blood red (`VoxelTerrain._make()`), and
  redraws the overlay. A breaking block's stains go with it (`take_stains()`): a worn block crumbling
  colours its lumps, a block falling whole carries its overlay under the `FallingBlock` and hands the
  stains on as it lands, and a crate's go to its pieces (`carry_stains()`: each piece holding a
  stained voxel is taken on as a loose model and stained where the crate was, its faces turned to the
  piece's frame), only if its `ScriptedDestruction` has a `wear`.
- **Loose models:** `VoxelBody.stains` (`stained()`), the overlay under its mesh; a part cut off takes
  a copy (`carry_stains()`).
- **Figures:** `FigureVoxels.stains`, over the figure as drawn, drawn by a mesh skinned to its skeleton
  with the body's `Skin`, each square weighted to its voxel's bone (`FigureStains`), so it moves with
  every pose. The rig is read from the `.vox` the figure was baked from (`CharacterModel.voxel_model`, a
  layout from `VoxelRig.LAYOUTS`), once a model. As the figure breaks apart, a voxel with any face
  stained goes into its lump blood red (`FigureVoxels.crumble()`).
- **Gear:** `VoxelStains.on(mesh_instance)`, kept in its metadata, the overlay under it. Props are
  imported at 0.063 a voxel, so `scale` grows the shape's frame to the mesh's. Dropped, the mesh takes
  its overlay into its body, and once it is worn its `VoxelBody` adopts the stains
  (`adopt_stains()`), reading what is left of it.
- **Lumps:** a voxel's MultiMesh colour (`VoxelDebris.stain()`), the whole voxel rather than a face.

Decided with the user when blood was made, so not to be "fixed": blood is as exaggerated as Fat
Princess's, one bright red (`VoxelStains.COLOR`); a stain is per face, not per voxel; only damage
actually taken bleeds, more with more damage; where blood lands it runs, rather than splatting round;
a hit's wound is anywhere on the body facing the shooter, mostly the torso, with the tracer drawn to
it, rather than always at the head, where the round flies; the pool under a body is about two tiles
across, spreading over three seconds once it rests (since the dead break apart, from a second after
death, where the unit stood); stains last the battle and nothing carries over to
the roster; the enemies went from red to slate grey (bone and khaki were too near the white and yellow
squad members, and charcoal read navy, with blood dark in its shade). Two came later: a wound on a
figure leans a little downward rather than running, and is kept so (a smaller splash with drip trails
that creep down and drip off the body was offered and turned down); and coins never take blood.

To tune it: how much a hit bleeds, how its blood flies, and the pool under a body are the constants at
the top of `Blood.gd`; how blood spreads (the cost of each step, the noise, how far a drop looks
through a pool) at the top of `BloodFlow.gd`; the colour and gloss in `VoxelStains.gd` (`COLOR`; the
material's roughness 0.55 and specular 0.35, softened from 0.35 and 0.5 so the sun's glint on a pool no
longer washed it white); where wounds land and how wide they splash in `FigureVoxels.gd`
(`WOUND_WEIGHTS`, `WOUND_SPLAT`).

Adding things blood should stain:

- **A block** needs nothing more than destruction asks: drawn from a `.vox` at 0.0625, one block a
  cell. Every such block is read as the map loads, breakable or not, so drops meet its voxels and
  pools run across it on to its neighbours. One that wears away colours its lumps and falls with its
  blood. One that breaks into cut pieces hands its blood to them only if its `ScriptedDestruction` has
  a `wear`; without one, its blood goes as it breaks, and drops pass its pieces.
- **A new kind of destruction** (a `Destruction` subclass) has to hand a breaking block's stains on
  itself: `TerrainDestruction._break()` and `_on_landed()` only know a block that wears away (crumbled
  with its stains) or one that breaks at once into rigid pieces that wear (`carry_stains()`). Passing
  the stains into `shatter()`, so each kind decides where its blood goes as it does its pieces, would
  be the clean way.
- **A destructible thing that is not a grid cell** (a prop placed as a scene) needs `Blood` to find
  it: `_first_met()` and `_splash()` know blocks, figures and their gear, pieces that wear, and lumps,
  a branch each. A common interface for anything stainable (trace a ray against its voxels, give a
  surface to run over), found by a group, would let new kinds plug in; it would come with destruction
  outside the grid, which does not exist yet either.
- **A material that should take blood differently** (water, glass, sand) has nowhere to say so: every
  surface takes it alike, and only breakable blocks have a resource to put a setting on.
- **A turned block** (a GridMap orientation) should work, `TerrainSurface` and `carry_stains()`
  turning voxels and faces, but no map has one yet, so probe the first.

Headless on BoundaryMap a hit costs 0.2-0.4 ms; a shot's 50-odd drops about 1-2 ms a physics step in
flight; landing them is held to the 2 ms budget; overlays redraw in up to about 1 ms a frame, 2 ms
while a pool under a body spreads. Before the rig was read at load and the gear cached a frame, the
first hit took 10 ms and a frame of drops near a figure up to 9.

**Physics is only for debris, the dead's included.** Layers: 1 terrain, 2 unit clicks
(`Unit.PICK_LAYER`), 3 debris, 4 unit bodies (`Unit.BODY_LAYER`), 5 pieces
(`TerrainDestruction.PIECE_LAYER`: debris that is a body with a node of its own, a broken block's
pieces and the parts cut from them, and dropped gear, which are on 3 as well; nothing collides with 5,
it is only searched). Blood's drops are no bodies: they find debris
with a ray on 3 (a lump by its RID, a piece through `VoxelTerrain.model_of()`, falling blocks
passed), and meet figures by their voxels, never by a unit's bodies.
What a dead unit breaks into is debris among debris: its lumps on layer 3, its dropped gear on 3 and
5, landing on terrain and other debris and shoved aside by the living. Blocks have no collision in the
MeshLibrary, so
`TerrainDestruction` gives the map a copy of it with a cube on every shapeless block (a tree that
wears away gets its voxels' trimesh instead, and a worn block collides through its `WornBlock`).
Debris stays live for good and sleeps when still. Jolt's limits on bodies, body pairs, contacts and
scratch memory are raised in `project.godot` for the voxel debris.

**Pieces are found by the physics, never by walking the scene.** Every piece is made one by
`TerrainDestruction.make_piece()` (`ScriptedDestruction._make_pieces()`, `VoxelTerrain._split_off()`):
on `PIECE_LAYER` and in the `PIECES` group. Whatever looks for the pieces in a box (waking those lying
on what wore away, the ones a blast throws, the ones its crater wears) asks `pieces_in()`, a shape query
on that layer, and the tidy looks over the group. A battle that has broken every crate leaves some 2,700
pieces, and walking the scene for them took 11-14 ms on every bite, crate and blast, and 5-6 ms every
second; a query takes 0.1-0.5 ms, and the tidy under 1 ms. A block falling whole is no piece: it lands,
or gives up after 3 seconds, by itself. Each unit carries a frictionless
`AnimatableBody3D` capsule, starting `Unit.BODY_CLEARANCE` above its feet, that shoves debris aside and
is never pushed back.
A `FallingBlock` is on the debris layer but never collides with units: nobody can stand in its
column but units dropping with it. It is 1 cm narrower than its cell on each side
(`FallingBlock.CLEARANCE`), cannot turn, and is frictionless, so it slides down between the blocks
either side of it instead of wedging between them. Debris knocked off the map, or wedged inside a
block, is removed. The rules never look at debris.

**Scenery around a combat map is a second GridMap.** The rules, the camera and the destruction read
only the node at their `grid_map_path` (`GridMap`): the battlefield and the ring of trees walling it
in. `BoundaryMap.tscn` paints the forest beyond that ring into a sibling GridMap, `Boundary`, out
to 75 tiles past the battlefield. Nothing in the rules sees it, so it adds no tiles, cover or
collision, and `CameraRig`'s pan bounds stop at the battlefield. Paint scenery into `Boundary`,
never `GridMap`. Debris thrown over the ring falls through it (it has no collision) and is removed
below the map.

The scenery is built to be cheap, because it is most of what is drawn: painted like the
battlefield, the forest took about 50 ms of GPU time a frame (an RTX 3060 laptop), nearly all of it
trees drawn into the sun's shadow map, on and off screen. Now it costs about 3 ms at most:

- `Boundary` uses `Blocks/SceneryLibrary.tres`, `BlockLibrary.tres`'s blocks with the same ids and
  shadow casting off. The scenery still receives the battlefield's shadows. A block added to
  `BlockLibrary` that scenery should use goes in both, shadows off in this one.
- It has no ground blocks. `Boundary/Ground` is one plane in the grass block's top colour, 2 cm
  below the top of the ground blocks and covering the ring's whole outer rectangle; it fills the
  corners the battlefield leaves out too. Resize it with the ring, or the sky shows between the
  trees. Its `SceneryGround` script cuts every column of the battlefield's bottom layer out of it on
  ready, or a crater in the floor would show the plane running through it 2 cm down.
- Only the 6 rows nearest the battlefield have trunks (`SkinnyTree1Bottom`); past them the tree
  tops hide where the trunks would be.

Without their shadows the forest's trees look a little paler and flatter than the battlefield's,
most visibly zoomed in right beside them.

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
- Every key, click and hold the player can use is in `README.md`'s Controls, under World map (its
  Menus covering every `TabbedMenu`) or Combat. A new input action, a new use of an existing one,
  or a widget that reads keys or clicks itself gets a row there.

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
- **Defense comes off every hit, down to 0**, in `Unit.take_damage()`, which every hit goes
  through and which returns what was taken; the called result (`Ballistics.Outcome.damage`) is that,
  not the weapon's damage. Defense never touches the hit chance. Anything added to a hit's damage,
  such as a strike's `Unit.strength`, is added before the damage reaches `take_damage()`, so defense
  always comes off last.
- `Unit.shoot_at(shot, chance, grid, show_rounds)` is the single place a shot is resolved.
  `ShootAction`, the enemy AI and reaction fire all go through it; keep it that way so they cannot
  diverge. `Unit.strike(target, chance)` is the same for a melee strike, and
  `Unit.throw_at(throw, grid, show_flight)` for a grenade.
- **A throw is never rolled, and a blocked arc is never thrown.** Unlike XCOM 2, where a grenade goes
  off wherever its arc meets something, an arc that meets anything solid before its target cannot be
  thrown (`Throwing.Throw.is_clear()`), so the blast always goes off where the preview showed it.
  Units never block an arc. Its range is `Throwing.RANGE` across the ground, as sight range is
  measured, the same for every unit and grenade.
- **The blast is what the preview shows.** `Throwing.caught()` and `blast_cells()` say whom a blast
  hurts and what it breaks, for the preview and the blast alike: a cube `Grenade.blast_size` cells on a
  side centred on the target tile's lower cell; anyone with either cell inside is caught, friend, foe
  and thrower, and nothing inside it shelters them. Its damage goes through `take_damage()`, so
  defense comes off as from a shot.
- **A strike's odds are the shot's sum with Melee Accuracy for Aim**: `HitChance.for_strike()`,
  Melee Accuracy − Evasion. Cover, flanking, height and distance count for nothing in melee for now,
  and a strike is never a reaction. Like a shot's, they are computed once, when the target is lined
  up (`StrikeAction._estimate`), and that is what gets rolled.
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
- **A block that wears away is a whole block to the rules until it is worn past standing**: below
  `collapse_below` of its voxels, or cut through under something it holds up, decided as the round
  or blast lands, when it leaves the grid as any broken block does. How worn it looks never changes
  sight, cover, paths or throws, and the bottom layer never leaves the grid.
- **Rounds alone are traced voxel by voxel**, and only through blocks that wear away
  (`CombatGrid.cast(..., by_voxel)`): a miss strikes the voxel it meets, or flies on through the
  empty part of the cell. Sight lines, throw arcs and clicks read whole cells.
- **Rounds tear through loose models and fly on.** Where a round goes is still decided against the
  grid alone; `round_flown` reports its line only once it has landed, and the loose models along it
  lose voxels. No loose model, nor any lump, ever stops a round or shelters anyone.
- **Reactions are Pathfinder's:** one per unit, refilled in `Unit.start_turn()`. Overwatch spends all
  remaining actions to hold it, and its shot takes `HitChance.REACTION_PENALTY` via
  `for_shot(..., reaction = true)`.
- **Enemy shots roll the odds their AI chose them by.** `Tactics` builds each `AIAction.shoot` with
  its `HitChance` estimate, and the turn manager rolls that one; it never recomputes.
- **Reactions are the player's call, never automatic.** Only an enemy *walking* in sight opens a
  window (not leaning out to shoot). Keys `1`-`4` follow `PlayerSquad.members`, which is the squad
  panel's order; `0` passes on the current move only, and the next move is a new trigger.
- Units never block line of sight. Only terrain does.
- **A coin is on a tile, and only the squad takes it.** Whether a coin is there, and who takes it,
  is `Coins`' tiles and units' `tile_at()`, never the `Coin` node; enemies pass coins by. Its gold
  goes into `Campaign.gold` the moment it is taken, not at the end, and a win pays for the rest.
- **Blood is only for show.** Nothing in the rules reads it: wounds, drops, stains and pools change no
  sight, cover, path or roll, and everything random in them draws on `Blood`'s or the figure's own
  generator, never the global one, so a seeded fight replays the same with it. Where a hit is drawn
  landing (`Path.wound`) is presentational, as the muzzle is: the round still flies eye to eye.
- **A unit's figure is only for show.** Nothing in the rules reads `Unit.model`, its pose, facing,
  hop or what it breaks into: sight, shots and blasts take a unit as its tile and two cells, and a dead
  one's lumps and gear are debris, in no group, scattered on `TerrainDestruction`'s own generator,
  never the global one. The figure decides only *when* a few things happen, never what: a shot is
  fired once the gun is up, a strike lands at the swing's impact, a grenade leaves at the throw's
  release. Every rule above still holds at that moment, and a unit with no figure plays the same,
  at once.

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
`RayHit`, then wait on `physics_frame`. To wear a block that wears away, get the hit from
`grid.cast(origin, direction, distance, true)` so it lands on a voxel, then `grid.strike(hit, 5)`; a
blast is `grid.blast(origin, cells, 10, 1.0)`. `TerrainDestruction.voxels.count_at(cell)` says how much
is left, and `voxel_debris.count()` how many lumps there are. Seed the global generator first and the
same wear comes out every run. To tear loose models, break a crate (`terrain.break_block(cell)`), let
its pieces settle, and fly a round through them with `grid.fly(from, to, 5)`; `voxels.loose_count()`
says how many have been taken on, `voxels._loose` maps each body to its `VoxelBody`, and
`voxels._wearable` holds the pieces still waiting to be (`_model_of(body)` takes one on).

Blood is probed the same way. `unit.take_damage(5, from, false, unit.model.pick_wound(from))` stands
in for a round's hit, with `from` the muzzle; `blood.drops_in_flight()` counts drops still flying or
landed but not yet settled, and `blood.pools_to_come()` the dead yet to bleed out. Count stained faces
over `VoxelStains.faces` (`voxels.stains_at(cell)`, a model's `stains`, a figure's
`model.voxels().stains`), and drop blood anywhere with `BloodFlow.new(blood._terrain,
blood._terrain.voxel_of(hit.cell, hit.index), VoxelStains.FACES.find(hit.face), faces, rng).spread(faces)`
on a hit from `grid.cast(origin, direction, distance, true, true)`. Lumps' colours can only be checked
in a window (see Gotchas). Hide `HUD` and `TileHighlights` to look at blood: the move range's squares
draw over it. To look at a figure's wounds, turn it to the camera (`model.face()`) and paint it a
colour blood shows on; the shot itself is best driven through `Unit.shoot_at()` with a shot from
`LineOfSight.new(grid).find_shot()`, which plays the tracer to the wound.

Three checks blood was made with, worth repeating after changing it:

- **It draws nothing from the global generator.** Seed, fire the same volley through
  `Unit.shoot_at()` on a map with its `Blood` node and on one with it freed before the map enters the
  tree, and compare the outcomes and the next `randi()`: they matched.
- **How much a wound leans.** Flow the same wounds with `figure.bleed()` and with
  `BloodFlow.new(FigureVoxels.FigureSurface.new(figure), hit.voxel, hit.face, faces, rng, 1000.0)`,
  whose splash covers the whole figure, so every step costs the same; compare how far below the wound
  each stain's faces sit (the numbers under Blood above).
- **Coins stay clean.** `blood._spray()` drops straight at a coin: they should land beyond it, and
  its `MeshInstance3D` should get no `stains` metadata and no `Stains` child.

A death is probed the same way: `unit.take_damage(100, from, false, unit.model.pick_wound(from))` kills
with a round (a blast passes `blasted` and no `at`, a blade a `sweep` too), and
`TerrainDestruction.break_figure()` breaks any figure without its unit dying. Its lumps are the
`VoxelDebris` entries from `_state.size()` before it to after (`_centers[piece]` where each is now,
`_moved_at[piece]` the last step it moved, its body asleep once at rest); its gear the `Dropped<prop>`
bodies under `TerrainDestruction`. Seed the global generator and compare the next `randi()` with a
fresh seed's: a death draws nothing from it. Whether the lumps are red can only be seen in a window
(see Gotchas); they come to rest in 2-3 s, a blast's a little later.

A `--script` probe's scene is not ready during `_initialize()`: its nodes' `_ready` runs once the
main loop starts, so await a frame after `root.add_child()` before reading anything `_ready` sets up.

The figure is checked the same way, by its frames. Bake it, then look:

```bash
# Rebuild Scenes/BaseCharacter.tscn, its mesh and its animations from the .vox (a few seconds).
"$G" --headless --path . --script res://Scripts/Characters/BakeCharacter.gd
```

To see an animation, render it (in a window; `--headless` cannot):

```bash
"$G" --path . --script res://Scripts/Characters/PreviewAnimations.gd --resolution 360x400 -- stand_rifle strike_sword --view side
```

It plays whole clips through the figure's `AnimationPlayer` and adds reactions to a pose through its
`AnimationTree`, with the stance's props, and saves each frame and a `sheet.png` (a row per clip) to
`user://animation_preview` (it prints the folder). Look from the side and from three-quarters. In a
map, drive the actions themselves (`controller.activate()`, then `ShootAction._fire()`,
`StrikeAction._strike()`, `ThrowGrenadeAction._aim(tile)` + `_throw_lined_up()`, `MoveAction._move_to()`)
and capture frames as they play: that tests the timing too. The camera rig's `_pivot`, `_yaw`, `_zoom`
and `view_pitch` can be set directly to frame a close-up.

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

**Bodies made on the `PhysicsServer3D` outlive their node.** The voxel debris has no nodes, and a
battle shares the root viewport's `World3D` with the next one, so `VoxelDebris` takes its bodies out
of the world on `_exit_tree` and frees them (and its box shapes) on `NOTIFICATION_PREDELETE`.
Anything else made on the server must do the same.

**A packed array is passed by reference.** A `PackedByteArray` read off an object, out of a
dictionary or passed to a function is the same array, not a copy, so writing into it writes into the
original. A `VoxelShape`'s `voxels` and `rows` are shared by every block and model of its kind, which
is why `WornBlock` and `VoxelBody` `duplicate()` them before wearing anything.

**`get_collision_exceptions()` fails on bodies since freed.** The physics server keeps a freed body in
the exception list of every body that passed through it, and `PhysicsBody3D.get_collision_exceptions()`
errors on each (`Parameter "body" is null`) and returns null in its place. That is why a `VoxelBody`
keeps its own list (`passes`), never read from the server: `ScriptedDestruction._pass_overlaps()`,
which makes the pairs, hands each piece its list, and a cut hands the part its model's.

**Jolt has hard limits.** 10,240 bodies by default, and contact and pair buffers that overflow with a
few thousand lumps settling at once ("contacts were ignored", lumps sinking into each other).
`project.godot` raises them, and `VoxelDebris.MOST` keeps the lumps' bodies well under the body limit;
lumps rather than single voxels (`DEBRIS_CLUMP`, `crumble_size`) keep the count down. Raising the contact or pair
limits much further needs a bigger `temporary_memory_buffer_size`.

**A fresh checkout imported headless has no `.vox` meshes.** `--headless --import` in a new git worktree
imported no MagicaVoxel meshes, so every block was invisible and the map rendered almost nothing.
Open it in the editor once, or copy `.godot/` from a working copy, before measuring or rendering
there.

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

**A `--script` probe cannot name a class that names an autoload.** Its typed references are compiled
before the autoloads' names exist, so typing a variable as `PlayerSquad` (which calls `Campaign`), or
anything that reaches it (`ActionController`, every `UnitAction`, `ActionButton`, `Coins`), fails with
`Identifier not found: Campaign`. Leave those variables untyped and use string literals for their
constants; `Unit`, `CombatGrid` and `Throwing` are safe. The autoloads themselves are there at run
time (`root.get_node("Campaign")`).

**`get_meta(name, null)` errors when there is no such metadata.** A null default counts as none, so
the call fails rather than returning null. Ask `has_meta()` first, as `VoxelStains.on()` does.

**The headless renderer keeps no MultiMesh instance data.** `get_instance_color()` reads black there
whatever was set, so whether a lump is blood red can only be checked in a window.

**A typed loop variable fails on a freed object before any check.** `for unit: Unit in units` stops
with `Trying to assign invalid previously freed instance` the moment it reaches one that has died, so
the `is_instance_valid()` inside the loop never runs. Loop untyped and check first, as
`CharacterModel.gear()` does; a probe that keeps a list of units across a fight needs the same.

**Map coordinates:** floor blocks sit at `y=0` and walkable tiles at `y=1` in both current maps.
`CombatGrid.tile_position(tile)` is the floor surface (where units stand);
`CombatGrid.cell_center(cell)` is the middle of a cell (used for eye positions).

**`LineOfSightTest.tscn` is generated**, by a throwaway script that instantiates `CombatMap.tscn`,
rebuilds the GridMap and repositions units. That script is not in the repo, so edit the scene
directly or write a fresh generator.

**`BaseCharacter.tscn` is generated too**, by `BakeCharacter.gd`, with its mesh and animations. Change
the scripts and bake; anything edited into the scene or its `.res` is lost at the next bake.

**An `AnimationTree`'s `tree_root` is one resource shared by every figure.** Setting a node's property
on it (a one-shot's fade, a transition's cross-fade) changes it for all of them; per-figure state goes
through `tree.set("parameters/...")` only.

**`Vector2.UP` is (0, -1).** It is screen up. A blend space's forward, +y in the figure's own space,
has to be written `Vector2(0, 1)`.

**A rotation key must be on the same side as the one before it.** A quaternion and its negative are
the same turn, but a track blended between keys of opposite sign swings the long way round;
`HumanoidAnimations._sample()` flips each key to match the last.

**A figure's sockets exist only once it is ready.** `CharacterModel.equip()` before its `_ready` finds
no skeleton and hangs nothing; a probe that instantiates the scene has to add it to the tree and wait a
frame first, as `Unit._ready()` does by running after its child's.

**A typed array parameter refuses a plain array literal from untyped code.** A `--script` probe that
passes `[]` to `CharacterModel.equip()`'s `Array[Item]`, or a literal list of points to
`Unit.walk()`, fails at run time; declare the array typed (`var points: Array[Vector3] = [...]`) first.

**A `preload()` in a member's default compiles what it loads there and then.** `CharacterModel`
preloading `Figure.tres` compiled `VoxelDestruction`, whose base `Destruction` names
`TerrainDestruction`, which reads `CharacterModel`'s members, still mid-compile: "Could not resolve
external class member", and every script after it failed to load. The figure loads its two
destructions as it readies instead (`FIGURE_DESTRUCTION`, `GEAR_DESTRUCTION`). Nothing that chain
reaches may preload a destruction.

## Known gaps

- A shared `Weapon` resource must stay stateless; give it `resource_local_to_scene` before adding
  per-unit state like rounds remaining.
- Crates break whole on any strike or blast, however weak: only blocks that wear away read
  `Weapon.environment_damage` and `Grenade.environment_damage`.
- Rounds fly straight through debris: the trace only sees the grid, and the voxels of blocks that wear
  away. They tear the loose models they pass through, but are never stopped by one.
- Only a crate's pieces wear away as loose models so far. A loose model must be a `RigidBody3D` drawn by
  a MagicaVoxel model in a `MeshInstance3D` among its children, and no more than 62 voxels along its x
  (`VoxelShape.WIDEST`); static props, units' figures and their gear cannot be worn yet, and a
  `FallingBlock` is not one until it lands.
- A loose model collides as the box round what is left of it, so a board shot into an L lies as its
  box, and a part cut off one passes through its whole family of parts for good.
- A unit stands at the top of its tile however worn the block under it is, so it floats over a crater:
  up to 4 voxels on the bottom layer, deeper on a raised block. Tile highlights float with it.
- A worn block gives full cover until it breaks, however holed it looks; nothing reads partial wear.
  Each block holds up what is on it by itself: voxels are only joined across a cell face, not traced
  through several blocks, so a lump held only by a block that is itself cut loose stays put.
- A bite costs about 4-6 ms on the frame it lands and a grenade 15-50 ms, the most among crates and on
  raised ground (gathering and removing voxels, cutting lumps and meshing in GDScript), more for each
  block it brings down; the blast's redraws spread over the next few frames.
- A seeded fight replays exactly only while no block falls whole. A crate that falls draws on the
  global random generator when it lands (its pieces' knocks, its coin), at a moment the physics
  decides, so one that lands before the next round or blast in one run and after it in another
  changes the number that round or blast draws.
- Voxels are read from the `.vox` files at `res://` on ready: an exported build must include `*.vox` as
  non-resource files, and there are no export presets yet.
- A lump of debris collides as the box round its voxels, so one that is not a full box rests a little
  proud of what it lies on.
- A stilled lump is woken only by a blast, the block under it being worn or broken, or a unit walking
  into it. A crate's board, dropped gear or a falling block coming down on one passes through it, and a
  lump still on the move can come to rest inside it.
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
- The only experience is for surviving a battle. Ambition is the one skill that does anything, and a
  stat bonus the one kind of effect; every take costs one skill point, and nothing unlearns one. The
  other seven nodes of the Human and Minor Noble trees are one `Placeholder` skill, and there are no
  classes. Nothing shows where a stat's total comes from: the Details page gives the total alone. A
  level's words and its effects are written separately, so nothing keeps them agreeing. A pie's
  straight edges are not antialiased. A skill's tooltip lies over whatever is beside its node, the
  next tree's nodes among them, for as long as the keyboard is on the node. The Skills page does not
  scroll: its trees have about 296 px of height, which four rows with one ringed row fit (270) but a
  fifth row, or rings on three rows of four, run out of the panel's bottom. Grenades are the
  only items used up in battle. Every encounter is the same `BoundaryMap.tscn`, fresh each time, with
  its four enemies.
- Enemies never strike or throw: their AI only shoots, so no enemy figure draws a sword or readies
  a grenade, though the same figure can.
- Every unit wears the one figure, and only `BaseCharacter.vox` has a rig layout. Armor does not show
  on it, and a character's colour is the only thing that tells the squad apart.
- A figure turns on the spot without stepping, so its feet slide round. Every throw is left-handed,
  so the right hand keeps its weapon. There is no wounded idle, and no reload since there is no ammo.
- Props are posed by kind: the rifle's grip and foregrip, the sword's grip. A gun shaped very
  differently (a pistol) needs its own poses in `HumanoidAnimations`, not just a model.
- What the dead break into stays for the rest of the battle, and a living unit can stand in it.
  Dropped gear is only for show: it cannot be picked up, and a squad member's is back in the inventory
  already. Armor does not show, so it does not drop.
- A figure breaks apart from the pose it is in, where a bent joint's two bones share a little room, so
  their lumps can start overlapping and push apart as they are let go. Dropped gear passes for good
  through the lumps it started inside. A lump is turned as its bone was but drawn a block's voxels
  across, 0.0625 against the figure's 0.063, so a heap is a shade smaller than the figure was.
- There is one kind of grenade, and a unit throws the first it carries: with several kinds there is
  no way yet to pick which. Grenades do not bounce or roll, and a blocked arc is simply not thrown;
  walls inside a blast shelter nobody. Only the player sees the throw: no reaction or camera move
  follows it.
- Blood never dries, fades or soaks in: every stain stays bright red for the battle, and every battle
  starts clean; nothing is kept on the character. Figures do not leave trails or drip, and blood on a
  figure stays on it rather than dripping on to the ground.
- The Blood on / off choice is not saved: every launch starts with blood on, as every launch starts
  with the tile grid off. It cannot be changed in a battle, so a battle opened on its own (F6, the
  harness) always has blood unless a probe sets `Blood.enabled` before the map loads.
- Drops pass through what has no voxels to them or no body: stilled lumps, pieces that do not wear,
  blocks falling whole, and the scenery beyond the battlefield (lost below the map). A lump is stained
  a whole voxel at a time.
- A crate whose `ScriptedDestruction` has no `wear` loses its blood as it breaks: only pieces taken on
  as loose models can carry stains.
- Blood runs over one surface at a time: from a figure's wound it never runs on to its gear or the
  ground, and a small drop stains so few faces that it is mostly a cross or a bar.
- The move range's tile highlights draw over blood, which shows pink through their fill, and blood in
  shade takes the sky's blue light, so it looks a dark purple-red there.
- A blast's worn blocks are redrawn over the next frames, but their stains' overlays at the end of the
  blast's own, so for a frame or two, under the fireball, a voxel about to go shows without its stain.
- Blood on the grenades on a belt goes when any grenade is used up: `equip()` builds them all afresh.
- Every block in the map's library drawn from a `.vox` is read as the map loads, used on the map or
  not, and every stained cell is an overlay and a draw call of its own. Fine for four kinds and a few
  hundred stained cells; with dozens of kinds, read only those the map uses, and with thousands of
  stained cells, gather the overlays by area. See "Adding things blood should stain" for what a new
  kind of breakable, a destructible outside the grid, or a material that sheds blood would need.
- `TurnManager._take_enemy_turn()` reads its enemy again after each pause, so anything that kills an
  enemy during its own turn other than a reaction (which it checks for) leaves it reading a freed unit.
  Only a probe does so far.
- `Throwing.throws_for()` plans every tile in range each time Throw Grenade begins, about 16 ms on
  BoundaryMap; a bigger range or map may want it spread over frames.
- Only crates leave coins, each worth 1 gold; enemies drop nothing. A coin in a cell with no ground
  anywhere below it, or under a block that cannot break, floats there out of reach until a win
  sweeps it up. A collapsed stack's coins can sit half buried in its boards. Combat has no gold
  readout: the "+N Gold" calls are all it shows.
- The tile grid is drawn on grass blocks only, not on crate tops a unit can stand on, and its choice
  is not saved: every launch starts with it off. It is world-space, so a grass block falling whole
  shows its horizontal lines slide past as it drops. Giving the grass a material of its own changed
  7 pixels of BoundaryMap's start frame (out of 1.8 million; one at a crate's corner on a grass
  block, six by one level). Likely Godot's drawing order, which sorts by material, settling a depth
  tie the other way; CombatMap and LineOfSightTest came out identical.
