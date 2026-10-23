# CLAUDE.md

Working notes for VCOM, a turn-based tactics prototype (XCOM / Star Wars: Zero Company) in Godot
4.7 on a voxel grid. `README.md` has the player-facing rules and controls; this file is about
working in the code.

## Layout

The git root is `VoxelXCOM/`; the Godot project is `vcom/`, which is where commands are run from.
`MagicaVoxel/` holds source `.vox` art outside the project; `MagicaVoxel/Shapes/` holds basic
block-sized models (ladder, stairs, fences, ground blocks, walls, props, plants), made by its
`make_shapes.py` (`Shapes/README.md`), three of them in the game (`vcom/Blocks/`: the fence, the stone
wall, tall grass); `MagicaVoxel/Buildings/` the building pieces drawn by hand, all three in the game
(`SimpleWall1`, `SimpleTruss1`, `SimpleRoof1`: `Docs/LEVELS.md` has their offset and turn). `Images/` holds screenshots of the game
(the old world map and the new, the menus, battles just begun and long fought, clean and with blood, the level
editor), two of them shown in `README.md`, one in `Docs/LEVEL_EDITOR.md`; outside `vcom/`, so Godot does not import them. `Styles/` holds candidate visual styles
(screenshots, exact settings, a render harness); `Styles/APPLYING.md` explains how to apply one.
Style 05, Colour Bounce, is applied: in every combat map's Environment, sky and sun (sun from the
camera's left, blue procedural sky, SSAO and SSIL), plus 4x MSAA in `project.godot`.
`Styles/REVERT.md` restores the original look. `MapStyles/` holds 28 proposals for the
new world map's look, 02, 04, 05 and 10's forests applied, and of 10, 14 and 19 revisited on that look 10b, 14b and 19a
(`Docs/MAP.md`, "Its look"): the harness that renders them from `Map.tscn`, `MapStyles/README.md` on what each changes and
how to apply it, and pictures of the look as it is (`render.sh 0 91` draws them again); 12 (biome ground colours), whose
12b is applied, and 20 (fog of war), still open, are explored there in sub-folders, 25 and 24 variants written up. `ANIMATIONS.md` documents the characters' rig and animations in full: where they came
from, every clip, every decision and gap, and recipes for adding more. Read it before touching them.

`Docs/` holds what was split out of this file to keep it under its 150,000-character limit, a
subsystem a file, each with how it works in full, how to probe it and its known gaps: `AMMO.md` (a
gun's magazine and reloading), `BLOOD.md`, `CAMERA.md` (how the combat camera moves), `CAMPAIGN.md`
(the world map's party, encounters, the squad menu, villages and shops), `CUTAWAY.md` (seeing inside
buildings: the floor selector, cutting the level away from the view), `DESTRUCTION.md` (adding a
breakable block, voxel wear, loose models, the physics of debris), `GAMEPAD.md`, `GRENADES.md`,
`HUNKER.md`, `LEVELS.md` (combat maps as levels of voxel pieces: the volume, drawing it, edges),
`LEVEL_EDITOR.md` (the level editor that paints them: every control, making a map, adding pieces),
`MAP.md` (the new map: its scene, look, forests and level of detail), `MEDKIT.md`, `ROSTER.md`
(characters and the units they become, equipment, items and the inventory), `SHOOTING.md` (sight and
leaning out, lining up, confirming and settling shots and strikes), `SKILLS.md` and `VOXELS.md` (every
voxel model: how it is drawn and recoloured, and adding one). `ANIMATIONS.md`, beside this file, is
the figure's in the same way. This file keeps a summary of each and every rule that must not drift.
Read a subsystem's file before touching it, and put new detail about it there, not here; when this
file nears the limit again, split another subsystem out the same way.

```
vcom/Scripts/
  Unit.gd              health, actions, reaction, walking, shoot_at(), strike(), throw_at(); name, colour, stats, health
                       from its character; equipment (its character's, or just its weapon), carries(tag), melee_weapon,
                       grenade; use_up(item) -> used_up; damage_from() (defense off a hit, as take_damage() takes it);
                       model (its CharacterModel) and the calls that only show things on it: aim_at(), ready_strike(),
                       ready_throw(), stand_easy(), celebrate(), dodge(), recover(), lean_out() / lean_back() (out
                       of its cover, while a shot sees it there); aim_point() (a target's eye, lean() further out
                       while it leans);
                       hurt (every hit that takes health, where it landed and how: for Blood); hit_from,
                       hit_blasted, hit_at, hit_sweep (the last hit: the way the figure breaks apart if it kills);
                       hunkered (HunkerDownAction; until a move, a fall or its next start_turn()) -> hunker_changed;
                       rounds (its gun's magazine, full as it enters the map; one off in shoot_at()) -> rounds_changed,
                       magazine_size(), has_magazine(), can_fire(), can_reload(), reload_cost(), reload() (full at
                       the clip's seat); medkits (those it can still use this battle: one per Medkit carried, full as
                       it enters the map), is_wounded(), heal() (up to max_health), use_medkit(target) (the heal lands
                       at the clip's apply; itself too; use_medkit(target, from) spends from's, a squad member
                       beside it), attend() (turned to an ally a medkit is lined up on; at itself, looking down)
  PlayerSquad.gd       spawns the roster's squad on the SquadStarts; members + selection; drops the dead;
                       writes wounds, used-up grenades and deaths back to the characters; award_survivors()
                       (experience, and the gold their skills find -> found_gold)
  SquadStart.gd        @tool Marker3D: where a squad member starts; draws its tile and number in the editor
  TurnManager.gd       turn order, end-turn hold, carrying out enemy AI decisions, the camera on them; outcome WON / LOST; a win's
                       victory_gold and Coins.sweep(); calls the survivors' skill gold over their heads
  Reactions.gd         reaction window: slow motion, number prompts, reaction fire; the gamepad's focus on one
                       prompt (_focus: A fires it, LB / RB move it)
  CameraRig.gd         orbiting tactical camera; the player's moves ease, the game's glide as XCOM 2's do
                       (Glide): focus_on(), bring_into_view(), follow() (a walk not in view), frame() /
                       release_frame() (reactions, an enemy's shot); is_in_view() / will_be_in_view();
                       pan_to() (the cursor's stick steps); the right stick
  InputDevice.gd       autoload InputDevices (first of them): static gamepad, the device touched last, and changed;
                       use_gamepad() (hides the mouse), watch(), pointer_position() / pointer_on_canvas() (the
                       mouse, or the middle of the screen with the gamepad)
  Campaign.gd          autoload: state that outlives a scene; roster, inventory, gold, equip() / unequip(), learn()
                       (a skill, as Character.learn() but refused in battle), in_mission,
                       for_hire() / hire() (who is still on each HiringBoard), stock_of() / buy() (each Market), sell(),
                       start_battle(map, chosen) / end_battle() (the world map parked out of the tree meanwhile),
                       squad(count) (who fights: the chosen still alive), SQUAD_SIZE, lose() (killed in battle),
                       use_up(character, item) (a thrown grenade, off them for good), heal(amount) (the whole
                       roster's wounds)
  Combat/
    CombatGrid.gd      tiles and pathfinding over the level's LevelRules (level), on a walking graph kept from load
                       (redone round what breaks: Docs/LEVELS.md); edges: has_edge(), stepped over a level high
                       (vault_height(), vaults_along()); is_line_clear(), cast() (by_voxel: through the voxels of
                       pieces that wear away, for rounds; every_block too: of every piece, for blood; RayHit.voxel /
                       piece / on_edge; passing: pieces passed by), cast_seen() and pick_tile() (passing what is
                       cut away from the view), show_floor_of() (the floor changed to show units given the focus),
                       terrain_struck, blast() -> terrain_blasted, fly() ->
                       round_flown (every round's line, for the loose models it tears through); voxels
    LineOfSight.gd     cover, step-out, find_shots() -> Shot (where it is fired from, where the target is
                       seen: its own tile or one it leans out to), watched_tiles() (Docs/SHOOTING.md)
    HitChance.gd       the to-hit sum (Estimate + Term): for_shot(), for_strike() (melee), hunker_penalty(); roll()
    Ballistics.gd      where a round goes: hits along the sight line, XCOM 2 misses -> Path
    Throwing.gd        RANGE; plan() -> Throw (the arc, blocked or not), throws_for(unit); the blast's cells and
                       whom it catches (Docs/GRENADES.md)
    ThrownGrenade.gd   a grenade in flight along a Throw's arc, for show
    Explosion.gd       a grenade going off, for show
    MuzzleFlash.gd     a gun's flash as it fires, under its Muzzle marker, for show; frees itself
    Coins.gd           map node: rolls a breaking block's coin_chance, keeps the coins by tile (stacked), drops a
                       tile's when its ground goes, pays for those on any squad member's tile; count(), sweep()
    Coin.gd            one coin as it is seen (Items/Coin2.vox, as drawn): spins, bobs, pops in, drop_to(),
                       take(); for show
    Cutaway.gd         map node: hides what rests on what the level has cut away from the view (units, loose
                       pieces, falling blocks, coins; debris through VoxelDebris.hides) (Docs/CUTAWAY.md)
    ShotPlayback.gd    shots not taken from the action bar (reactions, the enemies'): aim, step out, shoot_at(), back
    Weapon.gd          Item: damage, environment_damage; magazine (shots, 0 for none) and reload (actions), for a
                       gun; has_magazine(); stateless, the rounds left are the unit's
    TileHighlights.gd  named layers of coloured squares; an on_top layer (the cursor) over every other
    TileCursor.gd      the gamepad's pointer in combat, owned by ActionController: a tile the left stick steps
                       (screen-relative, 8 ways, repeating), its `cursor` layer and a bobbing marker; snap_to(),
                       current(), moved
    TileGrid.gd        map node: the optional tile grid (G, or the System tab), drawn by the level's shader;
                       static shown, set_shown(), toggle()
  AI/
    EnemyAI.gd         Resource base: choose_action(tactics) -> AIAction
    AssaultAI.gd       reload when empty, close in, point-blank when adjacent, best odds with the last action, top
                       up a part-spent magazine with nothing else to do
    AIAction.gd        MOVE (path) / SHOOT (shot + estimate) / RELOAD (reload_gun()) / END_TURN
    Tactics.gd         shared queries: adjacent_foes, shots_at (none with no round), best_shot, reload(), advance,
                       paths
  Level/               combat maps as levels of voxel pieces (Docs/LEVELS.md, its scripts in full)
    VoxelLevel.gd      @tool map node (Level, Scenery): builds rules, volume and renderer; place() / remove();
                       cutaway_heights, cut_away() -> cut_changed, is_cut_away(), reveal(), is_under_building()
                       (Docs/CUTAWAY.md)
    LevelCutaway.gd    what a cut takes away from the view: the pieces, and where things are over them
    LevelData.gd       Resource: pieces in order, each a kind, a slot (a middle or an edge), a turn
    PieceKind.gd       Resource: a kind of piece; PieceBrush.gd, PieceLibrary.gd (Blocks/Pieces.tres)
    LevelRules.gd      what the rules see: the solid pieces standing in each cell and across each edge
    VoxelVolume.gd     every voxel, 32^3 chunks; ChunkMesher.gd (faces by shape, none hidden)
    LevelRenderer.gd   draws the volume a chunk at a time, collision a trimesh a chunk; cut() (pieces cut away
                       from the view, their shadows still cast); SceneryRenderer.gd
    LevelImport.gd     a GridMap as a LevelData; LevelEditing.gd (what an editor click does)
  Terrain/             breaking and wearing pieces, and debris (Docs/DESTRUCTION.md, its scripts in full)
    TerrainDestruction.gd  breaks struck and blasted pieces, drops what they held and units left on nothing;
                           block_broken; make_piece() / pieces_in(); break_figure() (a dying unit's figure)
    Destruction.gd         Resource base: how a kind of block comes apart, shatter(); coin_chance
    ScriptedDestruction.gd pieces cut in advance, swapped in and left to fall or blasted apart; wear
    FallingBlock.gd        a block whose support broke, falling whole until it lands
    Blast.gd               a burst from a point
    VoxelDestruction.gd    Destruction: a block that wears away a few voxels at a time
    VoxelShape.gd          one model's voxels, read from its .vox (Docs/VOXELS.md)
    VoxelModel.gd          a voxel model as drawn, a node under its MeshInstance3D (Docs/VOXELS.md)
    VoxelTerrain.gd        wears the level's volume (chip(), crater()) and the loose models (tear())
    VoxelBody.gd           a loose model as a body (a crate's piece, dropped gear)
    VoxelDebris.gd         every voxel broken off: lumps as PhysicsServer bodies with no nodes, drawn by MultiMeshes
    SceneryGround.gd       BoundaryMap's scenery ground plane (Docs/LEVELS.md)
  Blood/               wounds, drops, stains and pools, all for show (Docs/BLOOD.md, its scripts in full)
    Blood.gd           map node: on every Unit.hurt wounds the figure and sprays drops; static enabled
    BloodFlow.gd       blood running over voxel faces, cheapest first
  Items/
    Item.gd            Resource base: display_name, description, icon, price, sale_price() (half, rounded down),
                       tags / has_tag() (GUN, GRENADE, MELEE, MEDKIT), model (its prop scene); Weapon, Armor,
                       BattleItem extend it
    Armor.gd           the Armor slot's kind: defense, added to the wearer's
    BattleItem.gd      grenades, medkits: name and description; a kind's subclass says what it does
    Grenade.gd         BattleItem: damage, blast_size (odd, tiles across), environment_damage, blast_force
    Medkit.gd          BattleItem: heal (4); never used up, each usable once a battle (Unit.medkits)
    ItemStack.gd       an item and how many
    Inventory.gd       stacks in display order; stacks_of(kind), count_of, take, add; emits changed
  Characters/          the rigged figure every unit wears, and how it is baked (ANIMATIONS.md; its scripts in full in 18)
    CharacterModel.gd  the figure's runtime (BaseCharacter.tscn's root): its AnimationTree, facing, hops, gear in its
                       sockets, leaning out, the calls that only show things; break_apart(); tint / paint()
    FigureVoxels.gd    a figure's voxels, read from its .vox at run time: body, posed bones, pick_wound(), crumble()
    AimModifier.gd     SkeletonModifier3D: bends spine + chest to aim up or down, turns the head to look
    Postures.gd        map node: idle figures kneel behind low cover / brace at high, facing their nearest foe
    BakeCharacter.gd   tool: a .vox -> Scenes/<model>.tscn (skeleton, skinned body, sockets, animations)
    VoxelRig.gd        the humanoid skeleton, each model's layout (LAYOUTS by .vox), per-bone mesher
    HumanoidAnimations.gd  every animation, authored as IK poses in code, and the AnimationNodeBlendTree
    PreviewAnimations.gd   tool: renders clips to images, and a contact sheet of them
  Roster/              who the characters are (Docs/ROSTER.md, its scripts in full; their trees, Docs/SKILLS.md)
    Character.gd       Resource: who someone is: name, colour, stats and total(stat), skills learned, wounds,
                       experience, equipment slots, hire_cost
    Roster.gd          characters in display order
    Species.gd         SkillSource: what someone is born (Human)
    SubSpecies.gd      SkillSource: a kind of one Species (Minor Noble), its species
    CharacterClass.gd  SkillSource: what someone trained as; one tree, as Main Class or Multi-Class
  Skills/              skills, their levels and effects, the trees placing them (Docs/SKILLS.md, its scripts in full)
    Skill.gd           Resource: one ability and its levels (at most MOST_LEVELS, 5); shared by every tree placing it
    SkillLevel.gd      Resource: one level of a skill: its words and its effects
    SkillEffect.gd     Resource base: one thing a level gives; bonus_to(stat), gold_after_combat(), when_taken()
    StatBonus.gd       SkillEffect: amount added to one stat
    CombatGold.gd      SkillEffect: amount of gold for the party after a combat fought in and survived
    SkillPointGrant.gd SkillEffect: amount of skill points handed over as the level is taken
    SkillTreeNode.gd   a place in a tree: id, skill, cell, requires
    SkillTree.gd       Resource: nodes; find(), extent(), is_open()
    SkillSource.gd     Resource base for whatever gives a character a tree: display_name, tree
  Actions/             UnitAction base (required_tag, is_granted; uses_left() (the count on its button),
                       takes_click_on() (a left click on a squad member as its target, not a selection); for the
                       gamepad confirm_hint(), cycles_targets(), shows_odds(), cursor_moved()) + ActionController
                       (the tile cursor, the prompts, pointed_tile(), the d-pad's next / previous action) +
                       Move/Shoot/Overwatch,
                       Strike (melee, at an adjacent enemy), ThrowGrenade (at a tile in reach; uses the grenade up),
                       HunkerDown (in cover only, one action; hunkered until a move or the player's next turn),
                       Reload (a gun with a magazine; dimmed while full; the gun's reload in actions),
                       UseMedkit (a wounded ally next to the unit, or itself, lined up as Strike; once a battle per
                       medkit; supplier(): its own uses first, then a squad member's beside it, _lenders())
  UI/                  every HUD widget, built in code
    TabbedMenu.gd      base CanvasLayer for full-window tab menus: dim, styled tabs, open() / close() pause the tree;
                       LB / RB tabs, LT / RT sub-tabs (_sub_tabs()), the gamepad's prompts in the strip under
                       the frame (_gamepad_hints(), _accept_hint() over gamepad_hint(focused), _close_hints())
    AmmoIndicator.gd   HUD node, bottom-right: the selected squad member's magazine (Docs/AMMO.md)
    FloorSelector.gd   HUD node, left edge: the map's floors as a stack of sheets (UI/floor_top.svg,
                       UI/floor_level.svg); a click, PageUp / PageDown or the d-pad cuts the level away (Docs/CUTAWAY.md)
    ButtonGlyph.gd     a gamepad button drawn from shapes (the font has none): A / B / X / Y, LB ... RT, LS / RS,
                       L3 / R3, View, Menu, the d-pad's arms; draw_glyph() on any canvas; any height (24 unless said)
    ControlHints.gd    a panel of [buttons, words] rows, a column or a row, shown only with the gamepad; compact
                       (smaller, no box) for the menus' row
    PauseMenu.gd       autoload TabbedMenu: the one menu for both scenes (Campaign, Roster, Inventory, System)
    VillageMenu.gd     TabbedMenu in Map.tscn: a tab per location of the settlement the party is in (Docs/CAMPAIGN.md)
    SquadMenu.gd       TabbedMenu in Map.tscn, opened by Party.encountered, cannot be closed: one SquadTab
    SquadTab.gd        its Roster tab: a CharacterBrowser with ticks and a Start HoldButton
    LocationTab.gd     placeholder tab for one Location
    HiringBoardTab.gd  a HiringBoard's tab: who is for hire, a PurchaseBar
    MarketTab.gd       a Market's tab: Buy / Sell, its stock and the party's; a PurchaseBar
    PurchaseBar.gd     the shop tabs' bottom row: the party's gold, a HoldButton to buy (or sell) the offer
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
    SkillsPage.gd      a column per tree, a SkillTreeView each, the trees scrolling under their headings; learns a
                       node once it is held (Docs/SKILLS.md)
    SkillTreeView.gd   one SkillSource's tree: a SkillButton on each node's cell, elbow links to what each requires
    SkillButton.gd     a node: a circle styled locked / available / learned, a ring for each take left
    SkillTooltip.gd    the panel beside a node: the skill's name, flavor, the level taken and the next
    CharacterButton.gd portrait (or colour swatch) with the name under it; ticked (UI/black_tick.png);
                       activated on a double-click or Enter / Space
    SubTabs.gd         the underlined second-level tab row both tabs above use
    InventoryTab.gd    SubTabs: Weapons, Armor, Battle Items, each an ItemBrowser; follows inventory.changed;
                       selected_stack() + selection_changed
    ItemBrowser.gd     split view: grid of ItemSquares left, selected item's name + description right;
                       optional action button (Equip), also Enter / double-click on a square; item_activated
    ItemSquare.gd      icon (or name without one), count badge above 1; selected when focused
    FocusChain.gd      left / right through a run of buttons, stopping at the ends
    SystemTab.gd       its last tab: Return to Game, Tile Grid on / off, Blood on / off (greyed out in battle, with a
                       note), Save / Load (not yet), Exit to Desktop
  WorldMap/            the campaign map, Scenes/Map.tscn (2D; Docs/CAMPAIGN.md, Docs/MAP.md), and the old
                       map's, Scenes/WorldMap.tscn, kept as a reference (WorldMapTerrain, BakeLand)
    WorldMapCamera.gd  pan / zoom with the combat camera's input actions and the sticks; limits MapCamera overrides
    MapCamera.gd       WorldMapCamera for Scenes/Map.tscn: the land just fits all the way out, 25 miles all the way in
    MapDetail.gd       Map.tscn's level of detail (its Detail node): four tiers by the view's height in miles
    MapLine.gdshader   Map.tscn's lines as map symbols (casings, dashes, dots, bands); materials in Resources/MapLines/
    MapGround.gdshader Map.tscn's land tinted by its biome (Resources/MapGround.tres; a county's biome on the county)
    BorderSwitch.gd    Map.tscn's BorderSwitch: B / R3 (toggle_borders) fade the borders out and back
    MapClock.gd        CanvasLayer in Map.tscn: the campaign's time, counted down; advance() while the Party moves
    MapReticle.gd      CanvasLayer in Map.tscn: the gamepad's reticle in the middle of the screen, its prompts
    WorldMapTerrain.gd is_land() on the baked collider, routes: straight rays, else navmesh pulled straight
    BakeLand.gd        tool: traces WorldMap/<map>LandMask.png into <map>Land.tscn (collider + navmesh)
    MapNavigation.gd   @tool, Map.tscn's Navigation node: the speeds (constants), the Bake Navigation button,
                       the stale warning; is_passable(), request_route() (a worker thread), find_route()
    MapNavigationBaker.gd  the bake: the layers into a 100 m grid, entrances and links by 16 km blocks (threads),
                       the settlements checked, the report; signature() for the stale check
    MapNavigationData.gd   Resource, WorldMap/MapNavigation.res: the grid by blocks, the network, the speeds
    MapRouter.gd       a route over the data: A* over the network, the links' cells, pulled straight, legs
    MapRoute.gd        a route: points, miles_per_day a leg, days
    MapWater.gd        on every node of water in Map.tscn: navigable (off)
    BakeMapNavigation.gd   SceneTree script: bakes Map.tscn headless (-- --check: stale?); the hook for baking
    Party.gd           the party dot: sent by a right click or A, travels a route; every step_length heals the
                       roster and rolls a forest's encounter chance; encountered(map)
    Forest.gd          Polygon2D (Scenes/Forest.tscn, and the new map's four kinds): outline, encounter_chance per
                       step, encounter_map; find_at()
    GameOver.gd        CanvasLayer: once the roster is empty, pauses, shows "Game Over" in a TurnBanner, quits
    Destination.gd     a place to send the party (Village, City, Town and Hamlet.tscn): icon, tooltip of locations
    Location.gd        Resource: something to use in a village (Resources/Locations/): make_tab()
    HiringBoard.gd     Location: the characters for hire at one village; one .tres per village
    Market.gd          Location: an Inventory of stock for sale at one village; one .tres per village
```

Art beside the scripts: `vcom/Characters/` holds the figure's `.vox` and what `BakeCharacter.gd` makes
of it (`BaseCharacterBody.res`, the skinned mesh; `BaseCharacterAnimations.res`, the animation
library), `vcom/Items/` the props' `.vox` (copies of `MagicaVoxel/`'s), and `vcom/Scenes/Props/` a scene
for each prop: its mesh, placed so the grip is on the scene's origin, with markers where it fires from
and where it is held. `vcom/Blocks/` holds the level pieces' `.vox` and `Pieces.tres` (every kind and
brush), `vcom/Levels/` each map's pieces, and `vcom/addons/level_editor/` the level editor, a Godot
editor plugin (`LevelEditorPlugin.gd`, its panel `LevelEditorDock.gd`, `LevelCursor.gd`;
`Docs/LEVEL_EDITOR.md`). `vcom/UI/` holds the HUD's few pictures: the ticks and the floor selector's
two sheets, white SVGs it tints (`Docs/CUTAWAY.md`, "The art").

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
(`is_granted(unit)`, which reads `Unit.carries(tag)`): Shoot, Overwatch and Reload need `Item.GUN`
(Reload, overriding `is_granted`, a gun with a magazine as well), Strike `Item.MELEE`, Throw Grenade
`Item.GRENADE`, Use Medkit `Item.MEDKIT` (overriding `is_granted`, or a squad member next to the unit with a
medkit use left: see `Docs/MEDKIT.md`), and Move and Hunker Down, with none, are every unit's. That is a different test from
`is_available`: an action the unit lacks has no button on the bar (the bar shrinks and re-centres),
where one it cannot take right now is dimmed; `ActionController.activate()` checks both. The first
child, the default, must need nothing. What a unit carries is `Unit.equipment`, copied from its
character's slots as it enters the map (see Squad units below), so it changes mid-battle only as the
unit uses something up (`Unit.use_up()`: a thrown grenade); with the last grenade gone, Throw Grenade
leaves the bar, since the bar asks `is_granted` on every `changed`. Use Medkit is the one grant that
also follows where the unit stands, which a move (and its `changed`) brings. A unit with no character (enemies,
the harness) carries just its `weapon`, `Rifle.tres` when the scene sets none. Enemies are not gated:
their AI shoots whatever it carries.

**A shot or a strike is lined up, confirmed, then settled as it is fired.** `ShootAction` lines up a
target `LineOfSight.find_shots()` finds and works out its odds once (`HitChance.for_shot()`); Enter /
Space, a click on the target (either button) or the target panel's tick takes the shot, and a click on
another target only lines that one up, so nothing is ever taken at odds the player has not been shown.
`StrikeAction` is laid out the same way at arm's length: its targets are the living enemies next to
the unit, as `Tactics.is_next_to()` has it, its odds `HitChance.for_strike()`, and `Unit.strike()`
lands the melee weapon's damage plus the striker's `Unit.strength` at the swing's `impact`, touching
no terrain. `Unit.shoot_at(shot, chance, grid, show_rounds)` has the figure take aim, spends a round,
rolls, and asks `Ballistics` for the round's `Path` (the sight line for a hit; for a miss, XCOM 2's
placement round the target or on its cover, traced with `CombatGrid.cast()`); it awaits `show_rounds`,
the tracer, and only then damages the target and reports any terrain struck (`terrain_struck`). It is
a coroutine: always `await` it. Shots not taken from the action bar, reaction fire and the enemies',
play through `ShotPlayback`. A target is also seen on a tile it could lean out to (XCOM 2's rule:
`LineOfSight.lean_tiles()`), tried only when no firing position sees its own tile; such a shot has
`Shot.leaning` and `Shot.seen_at`, keeps the target's own cover, and is flown, hit and missed where it
leans, and the target's figure leans out there for it (`Unit.lean_out()`) while the unit stays on its
tile. `Docs/SHOOTING.md` has the rest: the clicks, the tick and the hand cursor, how a miss is placed,
the figure leaning out and hit out there, the harness's lanes for it, its gaps and what was decided
without asking the user. Read it before touching sight, shots or strikes.

**A throw is planned, then flown.** `ThrowGrenadeAction` aims at the tile under the pointer
(`ActionController.pointed_tile()`, the tile cursor's with the gamepad) and throws there on a click
with either button, Enter / Space or A; `begin()` plans every throw the unit can make
(`Throwing.throws_for()`) and tints them, and the tile under the pointer shows its arc and whom the
blast would catch. A `Throwing.Throw` is a parabola from over the thrower's head to the target tile's
lower cell, cut into pieces each cast through the grid with `CombatGrid.cast()`; the first solid cell
any piece meets blocks it, and its constants (`RELEASE_HEIGHT`, `ARC_RISE`, `ARC_MIN_HEIGHT`,
`TRACE_STEP`) decide what a throw gets over, so check them with a probe if they change.
`Unit.throw_at(throw, grid, show_flight)` uses the grenade up as it leaves the hand, at the throw's
`release`, and the blast lands as the grenade arrives: `take_damage()` on everyone `Throwing.caught()`
names, then `CombatGrid.blast()` with the cube's cells. `Docs/GRENADES.md` has the rest: the clicks,
the preview, the flight and the explosion, what the action waits out, how to probe a throw, and its
gaps.

**A medkit heals an ally next to the unit, or the unit itself, once a battle for each one carried,
and the squad members beside its carrier can draw on its uses.** `Medkit.tres` is a `Medkit`
(`BattleItem`, tagged `medkit`, `heal` 4), so it goes in an item slot and gives `UseMedkitAction`,
laid out as `StrikeAction`: its targets are the wounded allies next to the unit, nearest first, then
the unit itself if it is wounded, and it costs `UseMedkitAction.COST` (1). It is never used up, unlike
a grenade: what a battle spends is `Unit.medkits`, filled from the unit's equipment as it enters the
map. Whose use is spent is `UseMedkitAction.supplier(unit)`: the unit's own first, else a squad
member's standing next to it (`_lenders()`), which is why `is_granted()` overrides the tag test.
`Unit.use_medkit(target, from)` is the single place one is used, the heal (`Unit.heal()`, never above
`max_health`) landing at the clip's `apply`. Its targets being squad members, the action takes a left
click on one it offers (`UnitAction.takes_click_on()`), which would otherwise select them.
`Docs/MEDKIT.md` has the rest: the targets and the clicks, the panel, the figure's showing of it,
borrowing, how to probe it, its gaps and what was decided without asking the user. Read it before
touching the medkit.

**Hunkering down is a state on the unit that one term of the hit chance reads.** `HunkerDownAction`
(every unit's, for `HunkerDownAction.COST`, 1, and available only in cover:
`HunkerDownAction.is_in_cover()`) sets `Unit.hunkered`, and while it holds `HitChance.for_shot()` adds
a **Hunkered** term of `-HitChance.HUNKER` (20) just after **Cover**, whenever `Shot.cover` is not
`NONE` (`HitChance.hunker_penalty()`). Moving ends it, and that rule is in `Unit`, where every move
goes through: `Unit.start_walk()` clears it for every walk but one that keeps its facing, which is
only ever a step out of cover to shoot and back, and `Unit.drop_to()` clears it too, so a new kind of
walk that should not stand a unit up has to keep its facing or say so there. `Unit.start_turn()`
clears it as well, so short of a move it lasts until the player's next turn. `Docs/HUNKER.md` has the
rest: what the action shows and does, the figure ducking and the card's badge, its gaps and what was
decided without asking the user.

**A gun counts its rounds, and the unit holds them.** A `Weapon` has a `magazine` (shots, 5 for the
Rifle; 0 for a gun that never runs dry) and a `reload` (actions, 1 for the Rifle); the weapon stays a
stateless shared resource, and the rounds left are `Unit.rounds`, filled as the unit enters the map,
so every battle starts full and nothing is kept on the character. `Unit.shoot_at()` takes one off as
the trigger is pulled, and nothing lines a shot up without a round: `Unit.can_fire()` is asked by
Shoot, Overwatch, `Reactions` and the AI's `Tactics`. `ReloadAction` (a gun with a magazine; dimmed
while it is full) plays `Unit.reload()`, which fills it at the clip's `seat`. Enemies reload too, the
assault AI when empty or with nothing else to do, and `TurnManager` carries an `AIAction.Kind.RELOAD`
out as the action does. `AmmoIndicator`, a HUD node in each map, draws the selected squad member's
magazine. `Docs/AMMO.md` has the rest: the action, the AI's reloads, the indicator and the gamepad's
prompts above it, how to probe it, its gaps and the user's calls.

**Highlights are named layers.** `TileHighlights.set_layer(name, {tile: Color}, fill)` — each caller
owns a layer, last set draws on top. Current layers: `selected`, `move`, `move_path`,
`shoot_step_out`, `overwatch`, `throw_range`, `throw_blast`, and the gamepad's `cursor`, set
`on_top` so it stays over every layer set after it. A colour's alpha dims a square's fill and
border together, which is how `throw_range` stays faint.

**The tile grid is drawn by the level's shader, and off until the player turns it on.** Style 19's
grid lines alone (Styles/): a faint darkening along every block boundary on the ground, tops and
walls, drawn by `Voxels.gdshader` on the voxels of each kind with `PieceKind.tile_grid` (the
grass), worn or not. The lines answer to the global shader uniform `tile_grid` (`project.godot`'s
`[shader_globals]`), which only `TileGrid.set_shown()` / `toggle()` set; `TileGrid.shown` is static,
so the choice holds from battle to battle until the game closes, and is never read back from the
RenderingServer. `G` (`toggle_grid`) toggles it in combat, as does **Tile Grid** on the System tab
anywhere, which the pause menu relabels as it opens. A style that changes the level's look has to
carry the grid with it (Styles/APPLYING.md section 3).

**The HUD is written in code, not scenes.** Widgets build their children in `_init()` and style
themselves with `StyleBoxFlat` overrides. Follow that rather than adding `.tscn` files for UI.

**The pause menu is an autoload, `PauseMenu`**, so the world map and combat share one menu and any
future scene gets it free. Being ahead of the scene in the tree, it sees `_unhandled_input` last:
Esc (`pause_menu`, bound to the same key as `cancel_action`) opens it only once nothing in the
scene has taken Esc to cancel something. Anything that cancels on Esc must mark the event handled,
or the menu opens on the same press. On the gamepad the two are apart: `Menu` is `pause_menu`, `B`
is `cancel_action`, and the open menu closes on either. Opening sets `get_tree().paused`; the menu alone runs
`PROCESS_MODE_ALWAYS`. A tab is any `Control` added to `PauseMenu.tabs`, titled by its node name.
The menu refills its tabs from `Campaign` each time it opens (`_refresh()`), so it never holds state of its own.

Its frame is `TabbedMenu`, which the world map's `VillageMenu` and `SquadMenu` share
(`Docs/CAMPAIGN.md`). Being in the scene, they see Esc (`cancel_action`) and the gamepad's `Menu`
before the pause menu does, and take them; being `PROCESS_MODE_ALWAYS` like every menu, the village
menu opens on nothing while the tree is paused, or A on the pause menu's tab row would open it
underneath. Down from a menu's tabs goes to the open tab's `focus_selection()` when it has one.

**The gamepad plays everything, and the screen says how.** `InputDevice` (the autoload
`InputDevices`, first of the three so it is there when the pause menu's widgets ready) watches every
event in `_input`, paused or not, and sets the static `InputDevice.gamepad` to whichever device was
touched last; it hides the mouse while the gamepad is in use and emits `changed`
(`InputDevice.watch()` connects to it). Being last to see `_input`, it never sees an event another
`_input` handled, so new gamepad handling goes in `_unhandled_input`. The layout is an Xbox
controller's, bound in `project.godot` beside the keys. Where the mouse points, the gamepad has a
pointer of its own: in combat the `TileCursor` the left stick steps, which actions read through
`ActionController.pointed_tile()` (the mouse's tile without the pad) and hear of through
`cursor_moved()`; on the world map the middle of the screen (`InputDevice.pointer_position()` /
`pointer_on_canvas()`, where `MapReticle` draws a ring). Switching device begins the active action
again, so it starts from the new pointer. The prompts are `ControlHints` panels of `ButtonGlyph`s and
words, shown only with the gamepad: A's words come from the active action's `confirm_hint()` in
combat, and from the focused control's `gamepad_hint(focused)`, or the first ancestor's that says
something, in a menu. `Docs/GAMEPAD.md` has the rest: every binding, how the cursor steps, where
each prompt's words come from, what the HUD swaps for a glyph, how to probe the pad headless, its
gaps and what was decided without asking the user. Read it before touching input.

**The world map is a scene of Godot's own nodes, written once by program and changed by hand from
then on.** `Scenes/Map.tscn` is the island the campaign is played on, and the main scene (nine
kingdoms, 44 duchies, 220 counties; `MapCreation/` holds the pictures and data it was made from). The
old map, `WorldMap.tscn`, is kept only as a reference: nothing leads to it. A unit is 100 m. Its
tree is its drawing order; its settlements are `Destination`s, its party the old map's, and its
forests 2,459 `Forest` pieces, each an instance of its kind's scene, which inherits `Forest.tscn`. `Detail`, a `MapDetail`, is its level
of detail: four tiers by the view's height in miles, the user's. A layer of lines or polygons that
comes and goes by the zoom (`MapDetail.SHOWN_FROM`) is only ever faded, never hidden, since a `Line2D`
shown again is built again and a `Polygon2D` cut into triangles again. Things that share an edge have
the same points, each its own copy, so a hand edit moves the copies too. The villages and the forests
are made by `MapCreation/Scripts/villages/` and `forests/` and spliced in by their `..._splice.py`;
spliced again they are made afresh, and a hand edit to one is lost.
`MapCreation/Scripts/scene/m2_scene.gd` now writes only those, its whole-scene part, which would write
the scene afresh in the old look, having been taken out (git keeps it, at d8b5ec7). `Docs/MAP.md` has
all of it (settlements, party, clock, camera, look, forests, level of detail, navigation, its scripts,
how to probe it, its gaps) and why; read it before touching the map. `README.md`, "The new world map",
has the decisions and what each node holds.

**The new map's party keeps off the water and takes the fastest way, over a bake of the map's own
layers.** The scene's `Navigation` node (`MapNavigation`, `@tool`) is the party's terrain: the sea,
lakes, rivers and channels stop it but for the lines under `Bridges`, unless that water's `MapWater`
(a script on every node of water) is navigable, off on all of it for now; it goes
`MapNavigation.ROAD_MILES_PER_DAY` (25), `OPEN_` (20) and `FOREST_MILES_PER_DAY` (15), the user's,
constants to tweak; a click on water or on land it cannot reach is ignored; a town on a river is no
crossing, so every settlement stands off the water, on one bank. Nothing is kept up by hand:
`MapNavigationBaker` draws the layers into a grid of 100 m cells and finds a network of entrances
between 16 km blocks, written to `vcom/WorldMap/MapNavigation.res`, which `MapRouter` searches (A*
over the network, the blocks' own paths, pulled straight, cut into legs by ground) on a worker thread
while the party waits. **After any change to the land, forests, roads, bridges or water, bake again**:
the **Bake Navigation** button on the `Navigation` node, or headless
`--script res://Scripts/WorldMap/BakeMapNavigation.gd` (`-- --check` says whether it is stale, exit 1).
A stale bake is warned of in the editor and as the game opens, and still used. Read
`Docs/MAP.md`, "Navigation", before touching it.

**The campaign is a world map the party travels, set upon in its forests and fighting on a battle
scene.** The party counts its travel in steps of `Party.step_length` map pixels; each step heals the
roster (`Campaign.heal(heal_per_step)`) and rolls the `encounter_chance` of the `Forest` it is in
(`Forest.find_at()`; a forest is a `Polygon2D`, its kind's scene, which inherits
`Scenes/Forest.tscn`). On a success it emits `encountered(encounter_map)`, which opens the
`SquadMenu`, a `TabbedMenu` that cannot be closed, over the paused map: the player ticks up to
`Campaign.SQUAD_SIZE` (4) of the roster, and holding Start calls `Campaign.start_battle(map, chosen)`.
That takes the world map's scene out of the tree without freeing it and makes a fresh battle scene
current, the swap deferred to the end of the frame; as `TurnManager` decides the battle, won or lost,
`Campaign.end_battle()` frees it and puts the same map node back, and the map's `GameOver` ends the
game if the roster is empty. Nothing on the map is saved or restored: its `_ready`s do not run again,
so anything on it that must notice a battle has passed sees only `_exit_tree` / `_enter_tree`. A
battle opened on its own (F6, the harness) has nothing to go back to. A left click on the
`Destination` the party stands on opens its `VillageMenu`, a tab per `Location` (only county 115's
capital has any: `Resources/Locations/County115*.tres`). A `Location` is a
stateless `.tres` like an `Item`, whose `make_tab()` gives its tab (`HiringBoard`, `Market`); what
changes in play lives in `Campaign`, keyed by the resource, and the resource is never changed.
`Docs/CAMPAIGN.md` has the rest: travel and encounters, the squad menu, the defeat and Game Over, the
village menu, the hiring boards, markets and selling, the old map's land and its traps, how to probe
it and its gaps. Read it before touching the campaign's flow, the world map's menus or a location.

**Squad units are roster characters, spawned for each battle; items are shared resources and the
inventory is state.** A `Character` (`Resources/Characters/*.tres`) is who someone is between battles,
and `Campaign.roster` is a copy of `Resources/StartingRoster.tres` whose list is its own but whose
characters are the loaded `.tres`. Unlike an `Item`, a character is state and changes in play: nothing
writes it back to disk, and save/load will need to store it. A combat map has no squad of its own:
`PlayerSquad` spawns a `Scenes/SquadUnit.tscn` on each of its `SquadStart` markers for the characters
`Campaign.squad()` sends, in roster order, setting `Unit.character` before it adds the unit. The unit
takes its character's name, colour and stats once, as it enters the map, each through
`Character.total(stat)` (their own, plus what their skills add and, for defense, their armor's): the
rules read the unit, never the character. What happens in battle goes back as it happens, through
`PlayerSquad`: health to `Character.wounds`, a thrown grenade off the character for good
(`Campaign.use_up()`), a death off the roster (`Campaign.lose()`, their gear back to the inventory).
Experience only goes up through `Character.gain_experience()`, every 100 a skill point; surviving a
battle is the one way to earn it so far (`PlayerSquad.award_survivors()`, which also adds the gold the
survivors' skills find). An `Item` (`Weapon`, `Armor`, `BattleItem`) is a stateless `.tres`, the same
`Rifle.tres` for every unit and the inventory, whose `tags` say what sort of thing it is; how many the
party holds is `Campaign.inventory`, a `duplicate_deep()` of `Resources/StartingInventory.tres`:
change that copy, never the `.tres`. Every item is in the inventory or in one of a character's six
slots, never both, so equipment changes only through `Campaign.equip()` / `unequip()`, which refuse
during a battle (`Campaign.in_mission`). `Docs/ROSTER.md` has the rest: the stats a unit takes and how
to add one, wounds and deaths, experience and the gold a battle pays, the slots and which item a unit
uses, items and the inventory, the Roster tab, how to probe them and their gaps. Read it before
touching characters, equipment or items.

**Every unit wears the one rigged voxel figure for now, and it is only for show.** A unit's `Model`
child, squad or enemy, is an instance of `Scenes/BaseCharacter.tscn`, which
`Scripts/Characters/BakeCharacter.gd` makes from `Characters/BaseCharacter.vox`, with its skinned mesh
and its animation library (the two `.res` beside the model). After editing the `.vox`, the rig
(`VoxelRig`: rigid, one bone per voxel, a layout per model in `VoxelRig.LAYOUTS`) or the animations
(`HumanoidAnimations`: all 56 written as IK poses in code), bake again (Verification has the command),
and never edit the scene or its `.res` by hand or in the editor. `CharacterModel` plays the clips
through one `AnimationTree`, whose tree resource every figure shares, so it sets only
`parameters/...`; most of what it plays it reads off its unit each frame (running while
`Unit.is_moving()`, facing the way it goes, hopping a level), and the rest the unit asks for through
calls that do nothing without a figure (`aim_at()`, `ready_strike()`, `ready_throw()`, `reload()`,
`use_medkit()`, `lean_out()`, `celebrate()` and the rest). Clips carry the moments the game waits on
as metadata (`impact`, `release`, `swap`, `seat`, `take` / `apply` / `stow`, a lean's `reach`). Gear
hangs in the figure's sockets (`CharacterModel.equip()`): each item's `Item.model`, a scene whose
origin is where the hand grips it, a gun's `Muzzle` and `Foregrip` markers on it. Each unit paints its
figure one flat colour (`CharacterModel.tint`), its character's `color` or the enemies' slate grey:
keep every unit's colour off red, on which blood barely shows. As a unit dies
`TerrainDestruction.break_figure()` breaks its figure into lumps of `VoxelDebris`, knocked the way the
killing blow went, and drops its gear whole as pieces that wear; both stay for the battle, debris like
any other (decided with the user, in place of the ragdolls the dead were). `ANIMATIONS.md` has all of
it: the rig, every clip and its moments, the tree, the runtime and its calls, the sockets and props,
breaking apart, recipes for adding more, how to bake, preview and drive them, the figure's gotchas and
its gaps. Read it before touching the figure.

**Skills are data: a skill's levels, placed in a tree, give effects.** A `Skill`
(`Resources/Skills/`) is a stateless `.tres` like an `Item`, with a `SkillLevel` for each time it can
be taken (`Skill.takes()`, at most `Skill.MOST_LEVELS`, 5), each with its words and its `effects`. A
`SkillTree` places skills as `SkillTreeNode`s (an `id` unique in its tree, a `cell` on the tree's
grid, the ids it `requires`), so a tree's shape is only where its nodes sit and what they require,
and belongs to a `SkillSource`: a `Species`, a `SubSpecies` or a `CharacterClass`. A `Character`
holds one of each (`Character.TREES`); every character is a Human Minor Noble, and no class exists
yet. A node's `id` is what a character's progress keys on, and saves will, so never rename one once
in play.

What a character has learned is theirs, like their wounds: `Character.learned`, the node ids of each
tree keyed by its `SkillSource`, once for each time taken. It only changes through
`Character.learn()`, one skill point a take, which refuses unless `can_learn()`; a requirement is met
by taking the node once. The Skills page learns through `Campaign.learn()`, which refuses first
during a mission, since a unit copies its stats as the map loads. A character has the effects of
every level taken (`Character.skill_effects()`), so a level holds only what it adds, and an effect is
a `SkillEffect` subclass of one of two sorts. One lasts while the level is had, and nothing is
applied or stored for it: the rules ask the effects when they need an answer, `bonus_to(stat)`
(`StatBonus`) through `Character.total(stat)`, which everything wanting a character's stat reads, and
`gold_after_combat()` (`CombatGold`) through `Character.combat_gold()`, which
`PlayerSquad.award_survivors()` asks of the squad's members still standing. The other happens once,
as `learn()` takes the level: `when_taken(character)` (`SkillPointGrant`). A new skill of a kind of
effect that exists is only its `.tres` and its node in a tree; a new kind is a `SkillEffect`
subclass and, if neither sort fits, a new method on the base class and a call where the rules need
it.

`Docs/SKILLS.md` has the rest: each skill in the two trees and what it gives, the Skills page
(`SkillsPage`, `SkillTreeView`, `SkillButton`: its columns and their scrolling, links and rings,
holding a node to learn it, the selection and the arrow keys), the `SkillTooltip`, the skills' gaps
and what was decided with the user. Read it before touching skills, trees or the Skills page.

**Node wiring is `@export var *_path: NodePath` + `get_node_or_null` + `push_error`.** Keep that
pattern. Something optional (like `ShotOverlay` in `ShootAction` and `TurnManager`) errors but
carries on behind `if x != null`; something essential bails.

**Enemy AI is a `Resource` that only decides.** Each enemy has `Unit.ai` (like `Unit.weapon`), set in
the scene to a shared `.tres` such as `Resources/AI/Assault.tres`. `TurnManager._take_enemy_turn`
asks `ai.choose_action(Tactics.new(...))` once per action and carries out the `AIAction`, charging
squad costs: `ceil(tiles / move_range)` for a move (at least 1, and cut to what the unit can afford),
`ShootAction.COST` for a shot, `Unit.reload_cost()` for a reload. So a new enemy type is an `EnemyAI` subclass plus a `.tres`; no turn,
reaction or camera code changes. Put reusable queries on `Tactics`, not in one AI. AI resources are
shared between units, so they must stay stateless (the same rule as `Weapon`). An enemy with no `ai`
sits its turn out with a warning.

**Enemies walk through `Reactions.walk()`.** It starts the walk with `Unit.start_walk()` so it holds
the tween, then polls it each frame: on every new tile it works out who on overwatch could fire
(`_find_offers`), opens or closes the window, slows the tween (`slow_motion_scale`), and holds it at
speed 0 while a reaction shot plays out. It lets the camera go once the window stays shut or the
walk ends (`Docs/CAMERA.md`). A window only exists during a walk; nothing else opens one. The
walker's figure runs at whatever speed the tween goes, so it slows with the window and freezes
mid-stride while held, and nothing here has to tell it.

**A combat map is a level of voxel pieces, painted in the level editor.** Its `Level` node
(`VoxelLevel`, `@tool`) holds a `LevelData` (`Levels/<Map>.tres`: every piece placed, in order, as a
kind, a slot and a turn) and the `PieceLibrary` every map shares (`Blocks/Pieces.tres`: the kinds, each
a 16³ `.vox` model at 0.0625 with its destruction, and the brushes). A slot is the middle of a cell,
where a block stood, or the edge between two cells side by side, where a fence or a wall stands. As
the map loads, the level stamps every piece into one grid of voxels (`VoxelVolume`, 32³ chunks, a
later piece winning voxel by voxel), draws it a chunk at a time with every hidden face left out,
across chunks too, its colours from a texture (`LevelRenderer`: BoundaryMap's battlefield is 269k
triangles, the GridMap's 924k), gives it collision over the frames after (whatever puts debris
somewhere asks `ensure_collision()` first), and gives the rules `LevelRules`: the solid pieces
standing in each cell and across each edge, whole until they break, which `CombatGrid` reads
(`level_path`). Nothing in the rules reads a voxel but a round's trace. The editor is a Godot editor
plugin (`addons/level_editor/`): select a `Level` and paint from the panel beside the 3D view, its
keys its own while a level is selected. `Docs/LEVELS.md` has all of the level (the data, the volume
and why 32³, the mesher and shader, collision, scenery, the edge rules, destruction and blood on the
volume, how the maps came over, how to probe it, its gaps and what was decided without asking), and
`Docs/LEVEL_EDITOR.md` all of the editor (every control, how painting behaves, making a map, adding
kinds and brushes, how it works, probing it, its gaps); read them before touching a level or the
editor.

**Breakable blocks are data.** `TerrainDestruction` (a node in each map) listens to
`terrain_struck` and breaks or wears the struck piece (`RayHit.piece`) as its kind says: its
`PieceKind.destruction`, a `Destruction` resource. A kind with none never breaks. A breaking piece
leaves the rules at once, then its destruction's `shatter(site, at, hit, motion)` plays out what is
left under the `TerrainDestruction` node, `at` being where the level drew its model
(`VoxelLevel.frame_of()` times the kind's `model_transform`).

It listens to `terrain_blasted` too (`CombatGrid.blast()`, a grenade going off): every breakable piece
in the blast's cells, or across an edge with a side in them, breaks, from the top down, so each is
blasted apart where it stands rather
than first falling on to the one below it (blocks stacked above the blast still fall, as usual). It
passes no `hit`, so the pieces get no knock from a round; instead, once they are let go a physics step
later, `Blast.burst()` throws every loose piece inside the blast (new and old, not a `FallingBlock`)
from the grenade's centre with its `blast_force`, on top of the crate's own burst.

**Stacks fall, then break.** Every breakable piece stacked on a broken one, up to the first that
cannot break, and every edge piece left with nothing under either side of it, leaves the rules in
the same moment but does not break yet: it becomes a `FallingBlock` (a mesh of what is left of its
voxels, and collision, as heavy as its destruction's `mass`) that drops
straight down its column and breaks where it lands, calling `shatter` with a `Destruction.Motion`
so its pieces carry on its fall. A unit left standing on nothing drops (`Unit.drop_to`) through the
rubble, and `TerrainDestruction.Collapse` lets it pass through the pieces the falling blocks leave
later too (`Unit.pass_through`). When a falling block has landed, and how a slot between two columns
holds a wreck, are `Docs/DESTRUCTION.md`'s ("Stacks falling").

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
ends) pays at once and leaves no coin. The `Coin` node is only for show (how it is drawn:
`Docs/DESTRUCTION.md`, "Coins"); `Coins.STACK_STEP` (0.7) must stay more than its height plus its
bob, or a stack's coins touch.

**A breakable block is one of two kinds, and adding either is a recipe.** A `ScriptedDestruction`
breaks a block whole into pieces cut in advance, which collapse or, with **Blast** ticked and a
`DestructOrigin` marker in the pieces scene, burst apart (`Blast.burst()`); a `VoxelDestruction`
(the grass, the trees, the fence, the wall) wears a block away a few voxels at a time. Either is a
`.tres` in `Resources/Destruction/`, its kind's `destruction` in `Pieces.tres`, and its art must be
imported from a `.vox` at Scale 0.0625, the blocks' scale. `Docs/DESTRUCTION.md` has both recipes
step by step, how wear works in full and its gaps; read it before touching either. What the rest of
the code has to know of wear:

- **Wear is the level's voxels; the rules see whole pieces.** A bite or a crater takes voxels out of
  the `VoxelVolume`, one grid across pieces and chunks, and the level draws what is left (a bite at
  once, a blast's chunks over the next frames); `LevelRules` keeps the piece, so sight, cover, paths,
  throws, coins and units see it whole, however little is left.
- **A round takes a bite, a blast blows a crater** (`VoxelTerrain.chip()`, `crater()`), and what is
  cut loose drops (`_drop_loose()`, across pieces). A piece left with less than `collapse_below`
  (half) of its voxels, or cut through under something it holds up (`holds_up()`), breaks as a crate
  does: out of the rules at once, `block_broken`, stacks and edges above fall, units drop, and its
  hole gets a ragged rim (`roughen_hole()`); what it lays bare inside the ground is recoloured as
  earth (`VoxelVolume.lay_bare()`), so no block's outline shows. The bottom layer never breaks, and is only worn
  `FLOOR_DEPTH` (4) voxels deep, since a unit stands at the top of its block whatever is left of it.
- **Rounds are traced voxel by voxel** (`CombatGrid.cast(..., by_voxel)`, which of the rules only
  `Ballistics` passes); sight, throws and clicks stop at whole cells and edges. Blood passes
  `every_block` as well, which traces every piece so; rounds never do.
- **What breaks off is `VoxelDebris`:** each lump a body straight on the `PhysicsServer3D`, no node,
  drawn by MultiMeshes, which is why `Unit.pass_through()` and `drop_to()` take body RIDs; past
  `VoxelDebris.MOST` (20,000) bodies, those at rest furthest from the camera's focus are stilled.
- **A broken crate's pieces wear away as well, as loose models** (`VoxelBody`, its
  `ScriptedDestruction`'s `wear`), from the first round's line (`CombatGrid.fly()` ->
  `round_flown` -> `VoxelTerrain.tear()`) or crater to reach them. A loose model blocks nothing.
- **It is deterministic.** Which voxels go, and so which pieces break, comes from the global random
  generator, one number a round, blast or broken piece, so a seeded fight replays exactly, as long
  as no block falls whole (see Known gaps). Everything only for show (how lumps fly, wearing a loose
  model) draws on `VoxelTerrain`'s own generator (`_show`), never the global one.

**Every voxel model is drawn and recoloured one way** (`Docs/VOXELS.md`, the user's call): faces
merged by shape alone (`ChunkMesher`), each pixel its voxel's colour, read by one shader
(`Voxels.gdshader`) from a texture of the voxels' palette places, 255 blood's. The level is drawn so a
chunk at a time; every other model by a `VoxelModel` under its `MeshInstance3D` (a figure, a prop, a
crate's board, a part cut off, a block falling whole), sharing its shape's mesh, texture and material
until it changes. Coins and a grenade in flight stay the importer's.

**Blood recolours voxels, and is only for show.**
`Unit.take_damage()` emits `hurt(taken, from, at, blasted, sweep)` for every hit that takes health
(none for one defense stops), before the unit can die of it. `Blood`, a node in each combat map
after `Coins`, connects to every unit as it readies and does the rest: it wounds the figure and
sprays drops, each a voxel under gravity in one MultiMesh, which stain the first voxel they meet and
run from there (`BloodFlow`), and a pool spreads where each of the dead stood. A stain is the voxel's
colour (`VoxelVolume.recolor(voxel, BLOOD)` on the level, `VoxelModel.recolor()` on any other model:
the user's choice of texture writes over overlays), a unit of blood for each face it turns red, and
goes wherever the voxel goes, handed on only when a model becomes others (a crate's pieces,
`carry_blood()`; a board cut in two). A hit is drawn landing on the body, not at the eye, where the round still flies:
`CharacterModel.pick_wound()` picks where, kept in `Ballistics.Path.wound`, which the tracer is drawn
to and `take_damage()` passes on as `at`.

**Blood** on the pause menu's System tab turns it all off: `Blood.enabled`, a static like
`TileGrid.shown`, never saved, changed only between battles (the menu greys the button out while
`Campaign.in_mission`) and read by each map's `Blood` once, in `_ready`. Off, every figure still reads
its rig, which draws it and which a shot draws its tracer on to, but `Blood` stops.
The lock is the menu's alone: `Blood` must not name `Campaign`, or no probe could name `Blood` (see
Gotchas). And blood never looks for coins: a drop flies straight through one, and no coin is ever
stained. Keep it so.

`Docs/BLOOD.md` has the rest: how a hit bleeds and sprays, what a drop meets, how blood runs, where
stains live and how each is handed on, what was decided with the user (so not to be "fixed"), what
to tune, what a new block, destruction or material needs for blood to stain it, what it costs, how
to probe it and its gaps. Read it before touching blood, or anything that turns one voxel model into
others.

**Physics is only for debris, the dead's included.** Layers: 1 terrain, 2 unit clicks
(`Unit.PICK_LAYER`), 3 debris, 4 unit bodies (`Unit.BODY_LAYER`), 5 pieces
(`TerrainDestruction.PIECE_LAYER`: debris that is a body with a node of its own, a broken block's
pieces and the parts cut from them, and dropped gear, which are on 3 as well; nothing collides with 5,
it is only searched). Blood's drops are no bodies: they find debris with a ray on 3 and meet figures
by their voxels, never by a unit's bodies. A dead unit's lumps and gear are debris among debris. The
level collides as a trimesh a chunk on layer 1 (`LevelRenderer`). Debris stays live for good and
sleeps when still; the rules never look at it. **Pieces are found by the physics, never by walking
the scene:** every piece is made by `TerrainDestruction.make_piece()`, on `PIECE_LAYER` and in the
`PIECES` group, and whatever looks for pieces in a box asks `pieces_in()`, a shape query. Each unit's
frictionless capsule shoves debris aside, and a `FallingBlock` never collides with units.
`Docs/DESTRUCTION.md`, "The physics of debris", has the rest (what each body is, what it costs,
Jolt's raised limits, its traps); read it before touching debris's bodies.

**Scenery around a combat map is a second level, only drawn.** The rules, the camera and the
destruction read only the `Level`: the battlefield and the ring of trees walling it in.
`BoundaryMap.tscn` places the forest beyond that ring in a sibling `VoxelLevel`, `Scenery`
(`scenery` ticked), out to 75 tiles past the battlefield: no rules, no collision, nothing breaks or
stains it, and `CameraRig`'s pan bounds stop at the battlefield. Put scenery there, never in
`Level`. 75 tiles is the standard depth for a ring: anything that lets the camera see further (zoom,
framing distance, pitch, FOV, window, `pan_margin`) needs it deepened, which is why
`max_frame_distance` is kept to about what the zoomed-out camera sees. How it is kept cheap (no
shadows, a `MultiMesh` a kind a region, coarser copies further out by `SceneryRenderer`'s constants, a
ground plane, trunks only near the battlefield) and how 75 was found are `Docs/LEVELS.md`'s ("Scenery").

**The view can be cut away to see inside buildings, and only the view.** A kind marked
`PieceKind.cutaway` (the walls, gables and roofs) is a building piece, and a map's `Level` lists the
heights it can be cut away from (`VoxelLevel.cutaway_heights`, cell y). Each is a floor on the
`FloorSelector`, a HUD node halfway down the left edge drawn as a stack of sheets (`UI/floor_top.svg`
on top, which shows everything, `UI/floor_level.svg` for each floor, highest first): a click on one,
`PageUp` / `PageDown` (`floor_up` / `floor_down`) or the d-pad's up / down calls
`VoxelLevel.cut_away(height)`. That makes a `LevelCutaway` (every building piece at that height or
above, and every piece resting on one by column or edge) and has `LevelRenderer.cut()` mesh the
chunks they are in, and those beside them, again without their voxels, each such section's whole mesh
kept under it `SHADOWS_ONLY`, so every shadow falls as before; the collision stays whole. The map's
`Cutaway` node hides whatever stands over a piece cut away (units, which take no clicks then, loose
pieces, falling blocks, coins, and debris through `VoxelDebris.hides`); `CombatGrid.pick_tile()` and
the camera's drag pass the cut pieces by (`cast_seen()`), and the tile highlights and the gamepad's
cursor skip tiles over them. The d-pad's up / down are the selector's alone: nothing zooms on them,
the world map included. Every combat map has both nodes, hidden without heights. The game changes
the floor as it gives a unit its focus, through `CombatGrid.show_floor_of(feet)` (the selector
follows): it cuts away less for one hidden with the cut (`VoxelLevel.reveal()`, the lowest listed
height above the cut that shows it), and down to their floor for one inside a house the camera's view
cannot reach (`is_under_building()`, `_is_seen()`), never hiding another unit given with it.
`TurnManager` calls it before an enemy acts, for every tile it will walk or step out to, the squad
member it shoots at, and the one selected as the player's turn starts; `ActionController` for the
squad member selected, however; and Shoot, Strike and Use Medkit for the target they line up and the
unit acting.
`Docs/CUTAWAY.md` has the rest: the user's decisions, how a cut is worked out and drawn, the art and
the constants tied to it, why meshes and not the shader, how to probe it, its gaps and what was
decided without asking. Read it before touching the floor selector or anything a cut hides.

## Conventions

- `##` doc comments on every class and non-obvious method, written in plain prose explaining *why*,
  not restating the signature.
- `&"name"` StringNames for groups and input actions; `^"path"` NodePaths.
- Nullable returns use `Variant` with a `null` check (`find_shot`, `current_shot`, `pick_tile`), so
  callers need an explicit type annotation to unpack them.
- Units are in group `units` plus `players` or `enemies`.
- Every key, click and hold the player can use is in `README.md`'s Controls, under World map (its
  Menus covering every `TabbedMenu`) or Combat, and every gamepad button under Gamepad. A new input
  action, a new use of an existing one, or a widget that reads keys or clicks itself gets a row
  there, and a gamepad binding: the game must stay playable with the pad alone, with what each button
  does on screen (a `confirm_hint()`, a `gamepad_hint()`, or a row in the prompts that list the rest).

## Combat rules that must not drift

- A unit fills **two cells** (`CombatGrid.UNIT_HEIGHT`) and sights from the centre of the upper one
  (`LineOfSight.EYE_HEIGHT`). This is what makes 1-cell blocks half cover (never blocks sight) and
  2-cell blocks full cover (blocks it).
- **A piece on the edge between two cells is cover to both sides of it**, half or, with more of it a
  level up, full (`LineOfSight.cover_at()`); it **blocks a sight line crossing that edge at its level**
  (one through a corner only if blocked whichever way round it went), a throw's arc and a whole
  cast; and a unit **steps over it only if it is a level high or less**, as it climbs a level,
  never diagonally past it and never leaning out through it. Like a block, it is whole until it
  breaks (`LevelRules`).
- **Step-out requires cover.** A unit in the open fires from its own tile only.
- **A target is seen on its own tile, or on a tile it could lean out to** (`LineOfSight.lean_tiles()`,
  the same tiles it could step out to shoot from), as in XCOM 2, so sight runs both ways: with the
  same sight range, `find_shot(a, b)` finds a shot exactly when `find_shot(b, a)` does. Its lean
  tiles are only tried when no firing position sees its own tile, so they add shots and never
  change one. A target in the open has none.
- **A reaction never sees its target leaning.** `Reactions` finds its shots with `leans` false, and
  `watched_tiles()` counts a tile only if someone standing on it would be seen there: the target is
  on the move.
- **Flanked ≠ uncovered.** `Shot.flanked` is true only when the target has cover that does not face
  the shot. A target in the open is "In the Open" and gets no flanking bonus.
- Everything about a shot — cover, height, distance — is measured from `Shot.from`, the tile the
  shot is *taken* from, which may be a step-out tile, to `Shot.target_tile`, the tile the target
  stands on, wherever it is seen: a target caught leaning out keeps its cover. Only the sight line,
  and so the round's path, runs to `Shot.seen_at`.
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
  `Unit.throw_at(throw, grid, show_flight)` for a grenade, and `Unit.use_medkit(target)` for a medkit.
- **A medkit is never rolled, never used up, and heals only its user or an ally next to it**, to at most
  their `max_health`: `Medkit.heal` through `Unit.heal()`. Its carrier has one use a battle for each
  medkit it carries (`Unit.medkits`, filled as it enters the map, so every battle starts with them
  all). Its user is its carrier, or a squad member standing next to the carrier, as
  `Tactics.is_next_to()` has it, drawing on the carrier's uses once it has none of its own: a use is
  spent from whoever's medkit it is, and the user's action pays. It is offered
  (`UseMedkitAction.is_available()`) only with a use to draw on, an action left and someone wounded to
  treat: the user itself, or an ally standing next to the user.
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
- **Hunkering down adds to cover, never stands in for it.** `HitChance.HUNKER` comes off a shot only
  while the target is `hunkered` and `Shot.cover` is not `NONE`, worked out as the shot is lined up
  like every other term. It lasts until the unit moves (any walk but a step out to shoot and back,
  or a fall) or its next `start_turn()`, for the squad the start of the player's turn, and is only
  ever taken in cover.
- **A strike's odds are the shot's sum with Melee Accuracy for Aim**: `HitChance.for_strike()`,
  Melee Accuracy − Evasion. Cover, flanking, height and distance count for nothing in melee for now,
  and a strike is never a reaction. Like a shot's, they are computed once, when the target is lined
  up (`StrikeAction._estimate`), and that is what gets rolled.
- **Where a round goes is decided once, after the roll, when it is fired** (XCOM 2's order), by
  `Ballistics`, and nothing recomputes it: the tracer draws that path and the terrain it ends on is
  what `terrain_struck` reports. One path per shot, as in XCOM 2.
- **A hit flies the sight line**, eye to eye, so it never touches terrain. Only misses strike it.
  The far eye is the one over `Shot.seen_at`: a target caught leaning out is hit, and missed, where
  it leans to.
- **Stray rounds never wound anyone and never pass through a unit**, the target included, except a
  unit standing in the line of fire itself, which every round passes through since units never block
  sight. A miss never stops on terrain more than `Ballistics.SHORT_OF_TARGET` short of the target.
  A leaning target is kept clear of both where it stands and where it leans.
- **Damage and terrain strikes land when the round does**, inside `shoot_at`, not when it is fired.
- **A broken block leaves the rules the moment the round strikes it**, before any debris moves, so
  sight, cover and paths never wait on physics, and so does every breakable piece stacked on it and
  every edge piece left on nothing, though it is still to be seen falling. Debris, and a falling block, is for show: nothing in the
  rules reads it.
- **A block that wears away is a whole block to the rules until it is worn past standing**: below
  `collapse_below` of its voxels, or cut through under something it holds up, decided as the round
  or blast lands, when it leaves the rules as any broken block does. How worn it looks never changes
  sight, cover, paths or throws, and the bottom layer never leaves them.
- **Rounds alone are traced voxel by voxel**, and only through pieces that wear away
  (`CombatGrid.cast(..., by_voxel)`): a miss strikes the voxel it meets, or flies on through the
  empty part of the cell, between a fence's rails. Sight lines, throw arcs and clicks read whole cells
  and edges.
- **Rounds tear through loose models and fly on.** Where a round goes is still decided against the
  grid alone; `round_flown` reports its line only once it has landed, and the loose models along it
  lose voxels. No loose model, nor any lump, ever stops a round or shelters anyone.
- **Every shot spends a round, in `Unit.shoot_at()`, as the trigger is pulled,** hit or miss, the
  squad's, the enemies' and reaction fire alike, and nothing offers a shot (Shoot, Overwatch, a
  reaction prompt, the AI's `Tactics`) unless `Unit.can_fire()`. A reload fills the magazine, costs
  the gun's `Weapon.reload` in actions, and is never offered with the magazine full. Every battle
  starts with every magazine full.
- **Reactions are Pathfinder's:** one per unit, refilled in `Unit.start_turn()`. Overwatch spends all
  remaining actions to hold it, and its shot takes `HitChance.REACTION_PENALTY` via
  `for_shot(..., reaction = true)`.
- **Enemy shots roll the odds their AI chose them by.** `Tactics` builds each `AIAction.shoot` with
  its `HitChance` estimate, and the turn manager rolls that one; it never recomputes.
- **Reactions are the player's call, never automatic.** Only an enemy *walking* in sight opens a
  window (not leaning out to shoot). Keys `1`-`4` follow `PlayerSquad.members`, which is the squad
  panel's order; `0` passes on the current move only, and the next move is a new trigger.
- Units never block line of sight. Only terrain does.
- **Cutting the view away is only for show.** A piece cut away from the view is whole to the rules:
  it blocks sight, rounds and throws, gives cover, holds up what is on it and can be shot and worn;
  a unit hidden on it sees, shoots and is shot as ever. Only the pointer (`CombatGrid.cast_seen()`)
  passes what is cut away; sight, shots, throws and blood use `cast()`, which meets every piece.
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
  fired once the gun is up and its target, if the shot sees it leaning out, has leaned out, a strike
  lands at the swing's impact, a grenade leaves at the throw's release, a magazine is full at the
  reload's seat and a medkit heals at its apply. Every rule above still holds
  at that moment, and a unit with no figure plays the same, at once. A figure leaning out of its
  cover is one of those things: the unit is on its own tile throughout, and whether it is seen
  leaning was `LineOfSight`'s to say, from the tiles alone.

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
a lane there over reasoning about geometry in your head. Its lanes for a target seen
leaning out, and how to watch such a shot, are `Docs/SHOOTING.md`'s.

Physics runs headless, and with `--fixed-fps 60` every physics step is exactly 1/60 s, so debris
can be tested without rendering: break a block with `terrain.break_block(cell)` (or `break_piece()`),
then wait on `physics_frame`. To wear a piece that wears away, get the hit from
`grid.cast(origin, direction, distance, true)` so it lands on a voxel (`hit.voxel`, `hit.piece`), then
`grid.strike(hit, 5)`; a blast is `grid.blast(origin, cells, 10, 1.0)`. `level.volume.counts[piece]`
says how much of a piece is left, and `voxel_debris.count()` how many lumps there are. Seed the global generator first and the
same wear comes out every run. To tear loose models, break a crate (`terrain.break_block(cell)`), let
its pieces settle, and fly a round through them with `grid.fly(from, to, 5)`; `voxels.loose_count()`
says how many have been taken on, `voxels._loose` maps each body to its `VoxelBody`, and
`voxels._wearable` holds the pieces still waiting to be (`_model_of(body)` takes one on).

How to probe a subsystem split out into `Docs/` is in its file, under "Probing it", where it has one.

The new map's navigation is baked, and checked, headless (a few seconds; a minute on one thread):

```bash
"$G" --headless --path . --script res://Scripts/WorldMap/BakeMapNavigation.gd             # bake; prints the report
"$G" --headless --path . --script res://Scripts/WorldMap/BakeMapNavigation.gd -- --check  # exit 1 when stale
```

Bake after changing the map's land, forests, roads, bridges or water, and read the report: a
"PROBLEM:" line names a settlement on water or cut off, or water cutting a road. The command reads
`Map.tscn` as saved, so it bakes for the user only once their changes are saved.

A death is probed headless too, with or without its unit dying: how, and how to read its lumps and
dropped gear, is `ANIMATIONS.md`'s (14.5).

An enemy's choice is `unit.ai.choose_action(Tactics.new(unit, grid, squad.members))` (its `kind`), and
`TurnManager._take_enemy_turn(enemy)` plays a turn out (await it through a lambda, sharing a
dictionary flag: see Gotchas). Ammo is probed as `Docs/AMMO.md` has it.

A `--script` probe's scene is not ready during `_initialize()`: its nodes' `_ready` runs once the
main loop starts, so await a frame after `root.add_child()` before reading anything `_ready` sets up.

The figure is checked the same way, by its frames. Bake it after any change to its `.vox`, its rig
or its animations' scripts:

```bash
# Rebuild Scenes/BaseCharacter.tscn, its mesh and its animations from the .vox (a few seconds).
"$G" --headless --path . --script res://Scripts/Characters/BakeCharacter.gd
```

`ANIMATIONS.md` has the command that renders its clips to images (section 1) and how to check an
animation (14). In a map, drive the actions themselves (`controller.activate()`, then
`ShootAction._fire()`, `StrikeAction._strike()`, `ThrowGrenadeAction._aim(tile)` +
`_throw_lined_up()`, `MoveAction._move_to()`) and capture frames as they play: that tests the timing
too. The camera rig's `_pivot`, `_yaw`, `_zoom` and `view_pitch` can be set directly to frame a
close-up.

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

**Do not hand-write `Transform3D` or `project.godot` input events.** The text
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
to see it. There `root.push_input(event, true)`, a mouse button event at a point in the viewport's
own coordinates (`Camera3D.unproject_position()`, or a control's `get_global_rect()`), clicks units
on the map and HUD buttons alike and leaves the player's cursor where it is; `Input.warp_mouse()` and
`Input.parse_input_event()` do too, moving the real cursor, and `Input.get_current_cursor_shape()`
reads the cursor. Turn off the actions' `_process` first (they follow the real cursor) and the
camera's `edge_pan_enabled`. On a software renderer (a cloud container's, under `xvfb-run`), setting
the root viewport's `scaling_3d_scale` low, and turning off the environment's SSAO and SSIL, makes
such a run several times faster.

**Debris's bodies have traps of their own, Jolt's and Godot's**: a body synced to physics left behind
as its parent moves, a kinematic body grinding thin pieces into what is under them, a board balancing
for good on a round top, contact found only within 2 cm, anything cut exactly as wide as a gap wedging
there, bodies made on the `PhysicsServer3D` outliving their node, `get_collision_exceptions()` failing
on freed bodies, and Jolt's limits on bodies, contacts and pairs. `Docs/DESTRUCTION.md`, "Its traps"
under "The physics of debris", has each and what was done about it; read it before touching debris's
bodies. One is a rule for every map: new debris is held a physics step while the level's collision
catches up ahead of it, so keep `Level` before `TerrainDestruction`, or a bite's lumps start out
inside the voxels they were.

**A `PackedColorArray` shader uniform arrives converted to linear.** The level's palette drew
everything far too dark that way; `VoxelModel.palette_entries()` passes a `PackedVector4Array`, which
arrives as it is. And `VIEWPORT_SIZE` is no size in a sun's shadow pass: `Voxels.gdshader` grows
faces by a fraction of a pixel only in perspective, a fixed 0.2 mm in the shadow.

**A texture made by a headless run has nothing to save.** The dummy renderer keeps no texture's data:
saved, a `Texture2DArray` a `--headless` script made has no layers and fails to load (`img.is_null()`).

**A packed array is passed by reference.** A `PackedByteArray` read off an object, out of a
dictionary or passed to a function is the same array, not a copy, so writing into it writes into the
original. A `VoxelShape`'s `voxels` and `rows` are shared by every block and model of its kind, which
is why a `VoxelModel` `duplicate()`s them before it changes anything. `LevelRules.pieces_in()` and
`pieces_across()` hand out the rules' own arrays: duplicate one before breaking pieces while going
through it.

**The MagicaVoxel addon's `.import` files must stay in git.** Its `plugin.gd` preloads
`framed_mesh_instance.png`, and the editor starts plugins before it scans for files to import, so on
a checkout without that PNG's `.import` file the plugin fails to load: no `.vox` importer, no block,
figure or prop imported, and a map that renders almost nothing. The addon came with a `.gitignore`
of its own ignoring `*.import`, which left every fresh checkout (a new clone or git worktree)
needing a second `--import`, to find the PNG the first had imported. That `.gitignore` is gone and
the addon's three `.import` files are committed, so one `--headless --path . --import` imports
everything; an update of the addon must not bring the `.gitignore` back. The first import of a
fresh checkout still logs four errors, and they are expected: as the autoloads compile, before the
plugin starts, `Campaign.gd`'s preloads of the starting roster and inventory reach `Rifle2.vox` (the
roster's rifles) and `StickGrenade.vox` (the inventory's grenades). The scan imports both a moment
later, and the next run logs none.

**Probe runs in parallel can log `Jolt Physics job system exceeded the maximum number of jobs`.**
That is several Godot processes fighting over the CPU, not the scene; it does not appear run alone.

**The old world map's land met two of Godot's limits**: `Geometry2D.is_point_in_polygon` misjudges
points near the vertices of a big outline, and the 2D navigation server cannot handle long sliver
polygons. `Docs/CAMPAIGN.md`, "Traps", has both and what `WorldMapTerrain` and `BakeLand.gd` do
instead: do not use the built-in for land tests.

**The game's font has no arrows and no shapes.** Open Sans SemiBold, the default, draws `←`, `▲` or
`⏵` as nothing at all, so a gamepad button is drawn from shapes and its letters (`ButtonGlyph`), and
anything else that wants a symbol has to draw it too.

**`Control.reset_size()` keeps the top-left corner, whatever the grow direction.** A panel anchored
to the bottom right and growing up and left grows off the screen after one. `ControlHints._collapse()`
shrinks the offsets to the edge it grows from instead, and lets the minimum size grow it back the
right way.

**A `TabbedMenu` subclass that handles `_unhandled_input` must call `super(event)` first**, and stop
if the event was handled: the base reads the gamepad's tab and sub-tab buttons there, and a GDScript
override replaces the base's method rather than adding to it.

**A static method on a `class_name` script must not share a name with a `Script` method.** Called on
the class (`AIAction.reload()`), the name reaches the class's own `Script` object first, so
`Script.reload()` ran and returned an error code where an action was wanted ("Trying to return a value
of type int"). That is why the constructor is `AIAction.reload_gun()`; keep clear of `reload`, `new`,
`get_class` and the rest of `Script`'s and `Resource`'s methods. Instance methods (`Unit.reload()`,
`Tactics.reload()`) are fine.

**A lambda captures a local variable's value, not the variable.** A probe's `var done := false` set
to true inside a lambda it awaits never changes outside it, so a wait on it times out. Share a
dictionary (`var turn := {"done": false}`) and set its key instead.

**A script error does not end a `--script` run.** Godot sits idle after it until killed, so give
scripted runs a `timeout`.

**A `--script` probe cannot name a class that names an autoload.** Its typed references are compiled
before the autoloads' names exist, so typing a variable as `PlayerSquad` (which calls `Campaign`), or
anything that reaches it (`ActionController`, every `UnitAction`, `ActionButton`, `Coins`), fails with
`Identifier not found: Campaign`. Leave those variables untyped and use string literals for their
constants; `Unit`, `CombatGrid` and `Throwing` are safe. The autoloads themselves are there at run
time (`root.get_node("Campaign")`).

**`get_meta(name, null)` errors when there is no such metadata.** A null default counts as none, so
the call fails rather than returning null. Ask `has_meta()` first, as `VoxelModel.take_over()` does.

**The headless renderer keeps no MultiMesh instance data.** `get_instance_color()` reads black there
whatever was set, so whether a lump is blood red can only be checked in a window.

**A typed loop variable fails on a freed object before any check.** `for unit: Unit in units` stops
with `Trying to assign invalid previously freed instance` the moment it reaches one that has died, so
the `is_instance_valid()` inside the loop never runs. Loop untyped and check first, as
`CharacterModel.gear()` does; a probe that keeps a list of units across a fight needs the same.

**Map coordinates:** floor blocks sit at `y=0` and walkable tiles at `y=1` in both current maps.
`CombatGrid.tile_position(tile)` is the floor surface (where units stand);
`CombatGrid.cell_center(cell)` is the middle of a cell (used for eye positions).

**`LineOfSightTest.tscn`'s units were placed by a throwaway script**, not in the repo; its level is
`Levels/LineOfSightTest.tres`, painted like any other (its edge lanes added by another script). Edit
the scene and the level directly, or write a fresh generator.

**The figure has gotchas of its own**: its scene and both `.res` are made by the bake (edit the
scripts, never them), an `AnimationTree`'s `tree_root` is shared by every figure (set only
`parameters/...`), `Vector2.UP` is screen up, a rotation key must be on the same side as the one
before it, its sockets exist only once it is ready, and a destruction preloaded anywhere
`CharacterModel` reaches breaks every script after it. `ANIMATIONS.md`, section 16, has each with its
fix.

**A typed array parameter refuses a plain array literal from untyped code.** A `--script` probe that
passes `[]` to `CharacterModel.equip()`'s `Array[Item]`, or a literal list of points to
`Unit.walk()`, fails at run time; declare the array typed (`var points: Array[Vector3] = [...]`) first.

## Known gaps

The gaps of each subsystem split out into `Docs/` are in its file, under "Known gaps", voxel wear's and
loose models' among them, and the figure's are `ANIMATIONS.md`'s (section 15); the rest are here.

- A shared `Weapon` resource must stay stateless: per-unit state goes on the unit, as the rounds left
  in its magazine do (`Unit.rounds`), not on the weapon.
- Crates break whole on any strike or blast, however weak: only blocks that wear away read
  `Weapon.environment_damage` and `Grenade.environment_damage`.
- A unit stands at the top of its tile however worn the block under it is, so it floats over a crater:
  up to 4 voxels on the bottom layer, deeper on a raised block. Tile highlights float with it.
- A worn block gives full cover until it breaks, however holed it looks; nothing reads partial wear.
  A voxel counts as held once the search from it passes `VoxelTerrain.HOLD_SEARCH` voxels, so a big
  overhang cut loose far from what holds it stays up.
- A seeded fight replays exactly only while no block falls whole. A crate that falls draws on the
  global random generator when it lands (its pieces' knocks, its coin), at a moment the physics
  decides, so one that lands before the next round or blast in one run and after it in another
  changes the number that round or blast draws.
- Voxels are read from the `.vox` files at `res://` on ready: an exported build must include `*.vox` as
  non-resource files, and there are no export presets yet.
- The squad panel does not wrap: past about five members it runs under the action bar, which it does
  in the harness (eight).
- Enemies never strike, throw or hunker down: their AI only shoots, so no enemy figure draws a sword,
  readies a grenade or ducks, though the same figure can. Nor do they carry medkits, and their AI never
  heals.
- `TurnManager._take_enemy_turn()` reads its enemy again after each pause, so anything that kills an
  enemy during its own turn other than a reaction (which it checks for) leaves it reading a freed unit.
  Only a probe does so far.
- Only crates leave coins, each worth 1 gold; enemies drop nothing. A coin in a cell with no ground
  anywhere below it, or under a block that cannot break, floats there out of reach until a win
  sweeps it up. A collapsed stack's coins can sit half buried in its boards. Combat has no gold
  readout: the "+N Gold" calls are all it shows.
- The tile grid is drawn on the grass only (`PieceKind.tile_grid`), not on crate tops a unit can stand
  on nor on a block falling whole, and its choice is not saved: every launch starts with it off.
