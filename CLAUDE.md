# CLAUDE.md

Working notes for VCOM, a turn-based tactics prototype (XCOM / Star Wars: Zero Company) in Godot
4.7 on a voxel grid. `README.md` has the player-facing rules and controls; this file is about
working in the code.

## Layout

The git root is `VoxelXCOM/`; the Godot project is `vcom/`, which is where commands are run from.
`MagicaVoxel/` holds source `.vox` art outside the project; `MagicaVoxel/Shapes/` holds basic
block-sized models (ladder, stairs, fences, ground blocks, walls, props, plants) that nothing in the game
uses yet, made by its `make_shapes.py` (`Shapes/README.md`). `Images/` holds screenshots of the game
(the world map, the menus, battles just begun and long fought, clean and with blood), two of them
shown in `README.md`; outside `vcom/`, so Godot does not import them. `Styles/` holds candidate visual styles
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
subsystem a file, each with how it works in full, how to probe it and its known gaps: `BLOOD.md`,
`DESTRUCTION.md` (adding a breakable block, voxel wear, loose models), `GAMEPAD.md`, `MAP.md` (the
new map: its scene, look, forests and level of detail), `MEDKIT.md` and `SKILLS.md`. This file keeps a summary of each and every rule that must not drift. Read a subsystem's
file before touching it, and put new detail about it there, not here; when this file nears the limit
again, split another subsystem out the same way.

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
  TurnManager.gd       turn order, end-turn hold, carrying out enemy AI decisions; outcome WON / LOST; a win's
                       victory_gold and Coins.sweep(); calls the survivors' skill gold over their heads
  Reactions.gd         reaction window: slow motion, number prompts, reaction fire; the gamepad's focus on one
                       prompt (_focus: A fires it, LB / RB move it)
  CameraRig.gd         orbiting tactical camera; frame() / release_frame() for the reaction view; the right stick
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
    CombatGrid.gd      tiles, pathfinding, is_line_clear(), cast() (by_voxel: through the voxels of blocks that wear
                       away, for rounds; every_block too: of any .vox block, for blood; RayHit.index the voxel met),
                       pick_tile(), terrain_struck, blast() -> terrain_blasted, fly() -> round_flown (every round's
                       line, for the loose models it tears through); voxels (VoxelTerrain)
    LineOfSight.gd     cover, step-out (firing_positions(), lean_tiles()), find_shots() -> Shot (from / stepped_out:
                       where the shooter fires from; seen_at / leaning: where the target is seen, its own tile or
                       one it leans out to); find_shot(..., leans false) for a reaction; watched_tiles()
    HitChance.gd       the to-hit sum (Estimate + Term): for_shot(), for_strike() (melee); roll();
                       hunker_penalty() (HUNKER, 20, off a shot at a hunkered target its cover counts against)
    Ballistics.gd      where a round goes: hits along the sight line, XCOM 2 misses -> Path (wound: where on the
                       target a hit is drawn landing, for show; drawn_to()); a target seen leaning out is shot at
                       where it leans to
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
    ShotPlayback.gd    shots not taken from the action bar: aim, step out, show, shoot_at(), step back; the target
                       leaning out meanwhile if that is where the shot sees it
    Weapon.gd          Item: damage, environment_damage; magazine (shots, 0 for none) and reload (actions), for a
                       gun; has_magazine(); stateless, the rounds left are the unit's
    TileHighlights.gd  named layers of coloured squares; an on_top layer (the cursor) over every other
    TileCursor.gd      the gamepad's pointer in combat, owned by ActionController: a tile the left stick steps
                       (screen-relative, 8 ways, repeating), its `cursor` layer and a bobbing marker; snap_to(),
                       current(), moved
    TileGrid.gd        map node: the optional tile grid (G, or the System tab); gives the ground blocks
                       TileGrid.gdshader as the map loads; static shown, set_shown(), toggle()
  AI/
    EnemyAI.gd         Resource base: choose_action(tactics) -> AIAction
    AssaultAI.gd       reload when empty, close in, point-blank when adjacent, best odds with the last action, top
                       up a part-spent magazine with nothing else to do
    AIAction.gd        MOVE (path) / SHOOT (shot + estimate) / RELOAD (reload_gun()) / END_TURN
    Tactics.gd         shared queries: adjacent_foes, shots_at (none with no round), best_shot, reload(), advance,
                       paths
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
                       tags / has_tag() (GUN, GRENADE, MELEE, MEDKIT), model (its prop scene); Weapon, Armor,
                       BattleItem extend it
    Armor.gd           the Armor slot's kind: defense, added to the wearer's
    BattleItem.gd      grenades, medkits: name and description; a kind's subclass says what it does
    Grenade.gd         BattleItem: damage, blast_size (odd, tiles across), environment_damage, blast_force
    Medkit.gd          BattleItem: heal (4); never used up, each usable once a battle (Unit.medkits)
    ItemStack.gd       an item and how many
    Inventory.gd       stacks in display order; stacks_of(kind), count_of, take, add; emits changed
  Characters/          the rigged figure every unit wears, and how it is baked
    CharacterModel.gd  the figure's runtime (BaseCharacter.tscn's root): drives its AnimationTree from what its unit
                       does, facing, hops, gear in its sockets; lean_out() / lean_back() / leaning / lean_reach()
                       (out round the end of its cover, standing or on one knee, hunkered or not); hunkered;
                       reload() (over the arms and head, _act_upper()); use_medkit() (over the left arm,
                       _act_left(); the medkit from the belt to the hand, or a borrowed one made in it, _borrowed;
                       given null, pressed to its own middle), attend() (faces and looks at an ally, not idle, until
                       stand_easy(); given null, keeps its facing and looks down at itself); break_apart() (hides
                       it once broken apart on death), crumbles_as / gear_wears_as (Figure.tres, Gear.tres); for
                       blood: voxels() (FigureVoxels), pick_wound(), swing(), gear()
    FigureVoxels.gd    a figure's voxels for blood and breaking apart, read from its .vox at run time: each bone's a
                       part posed as the skeleton is; march() (bones and gear), pick_wound(), hit_near(), exit(),
                       bleed(); crumble() (the lumps it breaks into); its stains drawn by a mesh skinned to the
                       skeleton (FigureStains)
    AimModifier.gd     SkeletonModifier3D: bends spine + chest to aim up or down, turns the head to look
    Postures.gd        map node: idle figures kneel behind low cover / brace at high, facing their nearest foe
    BakeCharacter.gd   tool: a .vox -> Scenes/<model>.tscn (skeleton, skinned body, sockets, animations)
    VoxelRig.gd        the humanoid skeleton, each model's layout (joints, voxel regions; LAYOUTS by .vox), per-bone
                       mesher
    HumanoidAnimations.gd  every animation, authored as IK poses in code, and the AnimationNodeBlendTree; UPPER_ACTS
                           (played over ARMS_AND_HEAD alone: the reload), LEFT_ACTS (over LEFT_ARM alone: a medkit)
    PreviewAnimations.gd   tool: renders clips to images, holding the right props, and a contact sheet of them; an
                           arms-and-head or left-arm clip over a base pose (--over)
  Roster/
    Character.gd       Resource: display_name, color, portrait, species / sub_species / main_class / multi_class
                       (TREES), learned (node ids by SkillSource, one for each time taken), learned_of() /
                       times_learned() / can_learn() / learn(), skill_effects(), its own stats and total(stat)
                       (with its skills' bonuses, and armor for defense), combat_gold() (what its skills find
                       after a battle), wounds / health, total_defense,
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
    SkillEffect.gd     Resource base: one thing a level gives; bonus_to(stat) and gold_after_combat() (asked
                       while the level is had), when_taken(character) (done once, as it is learned); nothing
                       unless a kind says
    StatBonus.gd       SkillEffect: amount added to one stat (max_health, defense, move_range, aim, ...)
    CombatGold.gd      SkillEffect: amount of gold for the party after a combat fought in and survived
    SkillPointGrant.gd SkillEffect: amount of skill points handed over as the level is taken
    SkillTreeNode.gd   a place in a tree: id, skill, cell (column, row), requires (ids in the same tree); takes()
    SkillTree.gd       Resource: nodes; find(), extent(), is_open() (everything it requires learned, once)
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
                       LB / RB tabs, LT / RT sub-tabs (_sub_tabs()), the gamepad's prompts along the bottom
                       (_gamepad_hints(), _accept_hint() over gamepad_hint(focused), _close_hints())
    AmmoIndicator.gd   HUD node, bottom-right: the selected squad member's magazine, a rectangle a round, filled
                       while loaded and hollow once fired, edged red when empty; hidden without a magazine
    ButtonGlyph.gd     a gamepad button drawn from shapes (the font has none): A / B / X / Y, LB ... RT, LS / RS,
                       L3 / R3, View, Menu, the d-pad's arms; draw_glyph() on any canvas
    ControlHints.gd    a panel of [buttons, words] rows, a column or a row, shown only with the gamepad
    PauseMenu.gd       autoload TabbedMenu: the one menu for both scenes (Campaign, Roster, Inventory, System)
    VillageMenu.gd     TabbedMenu in WorldMap.tscn: a LocationTab per location of the village the party is in;
                       enterable() (the village a click or A opens)
    SquadMenu.gd       TabbedMenu in WorldMap.tscn, opened by Party.encountered, cannot be closed: one SquadTab
    SquadTab.gd        its Roster tab: a CharacterBrowser with ticks, a footer of the count and a Start HoldButton;
                       focus_start() (the gamepad's Menu)
    LocationTab.gd     placeholder tab for one Location: its description in the middle
    HiringBoardTab.gd  a HiringBoard's tab: read-only CharacterBrowser of who is for hire, a PurchaseBar
    MarketTab.gd       a Market's tab: Buy / Sell SubTabs, InventoryTabs over its stock and the party's; a PurchaseBar
    PurchaseBar.gd     the shop tabs' bottom row: a note, the party's gold, a HoldButton to buy (or sell) the offer;
                       focus_offer() (where A / Enter on what is offered goes), can_take()
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
                       optional action button (Equip), also Enter / double-click on a square; item_activated
    ItemSquare.gd      icon (or name without one), count badge above 1; selected when focused
    FocusChain.gd      left / right through a run of buttons, stopping at the ends
    SystemTab.gd       its last tab: Return to Game, Tile Grid on / off, Blood on / off (greyed out in battle, with a
                       note), Save / Load (not yet), Exit to Desktop
  WorldMap/            the campaign map, Scenes/WorldMap.tscn (2D)
    WorldMapCamera.gd  pan / zoom with the combat camera's input actions; the left stick pans, the right zooms;
                       its limits the map sprite's, behind _has_map(), _map_rect(), _max_zoom() and
                       _clamp_to_map(point, zoom), which MapCamera overrides
    MapCamera.gd       WorldMapCamera for Scenes/Map.tscn: all the way out the land just fits (read off the
                       land's nodes), all the way in the view is closest_view_miles (25) tall, and the view
                       never leaves what is seen all the way out
    MapDetail.gd       Map.tscn's level of detail (its Detail node): four tiers by the view's height in miles
                       (Tier, SHOWN_FROM), what each brings faded in and out, every line's width scaled by one
                       factor of the zoom, a few lines a frame, the borders' by a growth of their own too
                       (border_growth) and the kingdoms' and duchies' fainter closing in (*_border_faintest);
                       settlements far from the view stopped (in_view);
                       forests by the size of the whole forest (Forests/Large, Small, Woods), only ever faded
    MapLine.gdshader   Map.tscn's lines as map symbols: casings (roads, bridges), dashes and dots (borders), a band's
                       pattern on both banks; a material a kind in Resources/MapLines/, and the line in Texture Mode Tile
    MapGround.gdshader Map.tscn's land tinted by its biome: one material, Resources/MapGround.tres, each biome's colour
                       and intensity on it; a county's biome (its kingdom's) set on the county, an instance parameter
    BorderSwitch.gd    Map.tscn's BorderSwitch: B / R3 (toggle_borders) fade Borders and BordersOverLakes to
                       nothing and back (shown); MapDetail fades only the ranks under them
    MapClock.gd        CanvasLayer in Map.tscn (its Clock): the campaign's time, counted down from
                       starting_days in the top left as days:hours:minutes; seconds_per_day; advance()
                       (only the Party calls it, while it moves), elapsed, remaining()
    MapReticle.gd      CanvasLayer in WorldMap.tscn: the gamepad's reticle in the middle of the screen and its
                       prompts (A's words from VillageMenu.enterable() and Party.can_go_to())
    WorldMapTerrain.gd is_land() on the baked collider, routes: straight rays, else navmesh pulled straight
    BakeLand.gd        tool: traces WorldMap/<map>LandMask.png into <map>Land.tscn (collider + navmesh)
    Party.gd           the party dot: sent by any right click, or A at the reticle (no selecting), travels a route
                       (with no terrain_path, as in Map.tscn, a straight line to anywhere);
                       is_at(destination); pointed_at(), can_go_to(); L3 centres it;
                       every step_length map pixels heals the roster by heal_per_step, then rolls a forest's
                       encounter chance; encountered(map)
    Forest.gd          Polygon2D (Scenes/Forest.tscn; on Map.tscn its four kinds' scenes, which inherit it): a
                       forest's outline, encounter_chance per step, encounter_map; find_at() (every forest)
    GameOver.gd        CanvasLayer: once the roster is empty, pauses, shows "Game Over" in a TurnBanner, quits
    Destination.gd     a place to send the party (Scenes/Village.tscn; with City, Town and Hamlet.tscn, the
                       settlements of Map.tscn): icon, hover tooltip listing its locations
                       (under the pointer: is_under_pointer(), find_under_pointer(); not while paused);
                       hidden, it stops its _process; out of view (in_view false) it draws nothing too
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

**Strike is a shot at arm's length.** `StrikeAction` is laid out as `ShootAction`: its targets are the
living enemies next to the unit, as `Tactics.is_next_to()` has it (the AI's point-blank range, so the
two cannot drift), nearest first; Tab / Shift+Tab cycle them, Enter / Space strikes (or a click, as
below), Ctrl opens the breakdown, and `ShotOverlay.show_strike()` draws the same line, reticle and
target panel (its status line reads "Melee" instead of the cover). It costs `StrikeAction.COST` (1, a shot's) and is dimmed
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

**A shot or a strike is confirmed by a key, a click on the target, or the panel's tick.** Enter / Space
is as it was. `ShootAction` and `StrikeAction` also read a click on a unit, with either button
(`UnitAction.clicked_unit()`, over `is_click()`: left, `select_unit`, as the squad is selected;
right, `execute_action`, as Move is carried out), which reaches them through `handle_input()` once
`ActionController` has let clicks on the squad go to `PlayerSquad`. A click on the target lined up
fires or strikes; a click on another target only lines it up (`_click()`), so nothing is ever taken
at odds the player has not been shown; a click on anything else is left alone. While either is up,
the cursor is a hand over any of its targets (`UnitAction.hovered_unit()`, `point_at_target()`,
checked every frame, as the camera moves under a still mouse): `Input.set_default_cursor_shape()`
is set only when it changes, since setting it sends a mouse motion of its own, and is put back to
the arrow as the action ends, as the tree pauses and as it leaves the tree. The target panel
(`TargetPanel`) has a tick box beside the chance, the roster's `UI/black_tick.png` on a pale box
filled with the menus' accent under the mouse, shown only when `ShotOverlay.show_shot()` /
`show_strike()` are told `confirmable`, which only the two actions say: reaction fire playing out
through `ShotPlayback` shows the panel without it. Clicking it emits `TargetPanel.confirmed`, passed
on as `ShotOverlay.confirmed`, which both actions listen to; the one active and not busy takes its
shot or strike. The box never takes the keyboard (`FOCUS_NONE`), or Space would press it as well as
reach the action, and the rest of the panel lets the mouse through, so a target under it can still
be clicked. Three calls were made without asking the user: both mouse buttons, a click on another
target lining it up rather than firing, and the hand cursor. With the gamepad the box gives way to an
A (`TargetPanel._confirm_glyph`, swapped on `InputDevice.changed`), which A, being `confirm_action`,
already did.

**A throw is planned, then flown.** `ThrowGrenadeAction` aims with the mouse, as Move previews: it
follows the tile under the cursor every frame (`ActionController.pointed_tile()`, the tile cursor's
with the gamepad, where A throws), and a click with either button
(`UnitAction.is_click()`, as a shot's target is clicked; the left as well as the right at the user's
request) or Enter / Space throws there; there are no targets to Tab through. A left click on a
squad member's figure is the one click it never sees: `ActionController` hands it to `PlayerSquad`,
which selects them, as during any action, so a throw at a tile a squad member stands on is a right
click or the keys. `begin()` works out every throw the unit can make
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
needs no item, so every unit has it, but it is only available in cover (`HunkerDownAction.is_in_cover()`:
`LineOfSight.cover_at()` of the unit's tile not empty, any side, either height), with an action left
and not hunkered already; out of cover its button is dimmed. Like Overwatch it shows nothing on the map
while it is up, and Enter / Space spends `HunkerDownAction.COST` (1, the user's call, in place of
the rest of the turn it first took) and sets `Unit.hunkered`. The unit carries on with its turn;
shooting, striking, throwing and overwatch leave it hunkered. Moving ends it, also the user's call:
`Unit.start_walk()` clears it for every walk but one that keeps its facing, which is only ever a
step out of cover to shoot and back (`ShootAction`, `ShotPlayback`), and `Unit.drop_to()` clears it
too, since falling when the ground goes is moving (assumed, not asked). So the rule is in `Unit`,
where every move goes through, not in `MoveAction`, and a new kind of walk that should not stand a
unit up has to keep its facing or say so there. `Unit.start_turn()` clears it as well, as it does
overwatch, and a squad member's turn starts with the player's, so short of a move it lasts through
the enemies' turn until the player's next. While it holds, `HitChance.for_shot()` adds a
**Hunkered** term of `-HitChance.HUNKER` (20) just after **Cover**, whenever `Shot.cover` is not
`NONE` (`HitChance.hunker_penalty()`): flanked, or with its cover shot away, a hunkered unit gets
nothing for it. Every shot is lined up through `for_shot()` (the action bar's, reaction fire, the
AI's `Tactics`), so it counts everywhere, and the assault AI's best odds steer it to a target that
is not hunkered. Two calls were made without asking the user: melee counts no cover, so
`for_strike()` counts no hunkering either (no enemy strikes yet); and nothing is drawn on the map
while it is lined up. With nothing to Tab through and nothing to repeat, the action is put away once
taken, as any action no longer available is, so the player picks the next one from the bar. It is
seen two ways: `Unit.hunkered` sets `CharacterModel.hunkered`, which holds `hunker_<stance>` over
every base pose but a readied one (so the figure ducks low behind cover of either height, on
overwatch too, rises to aim a shot and ducks again, and still cheers a win) and a lean out of its
cover: a shot that sees it only leaning out is aimed where it leans, so the figure leans out there
for it, hunkered or not, and ducks again once it draws back (decided in the merge, not asked; the
sight rule is untouched, so hunkering never hides a unit), and `UnitCard` shows a
`HunkerBadge`, a blue shield over its portrait's corner, rather than another pip, which would widen
the card.

**A gun counts its rounds, and the unit holds them.** A `Weapon` has a `magazine` (shots, 5 for the
Rifle; 0 for a gun that never runs dry) and a `reload` (actions, 1 for the Rifle), both the user's
names for them; `has_magazine()` is a gun with one. The weapon stays a stateless shared resource: the
rounds left are `Unit.rounds`, filled to `magazine_size()` in `Unit._ready()`, so every battle starts
full and nothing is kept on the character (the user's call). `Unit.shoot_at()` takes one off as the
trigger is pulled, after the aim and before the roll, so every shot spends a round, hit or miss, the
squad's, the enemies' and reaction fire alike, and a magazine never goes below empty. Nothing lines a
shot up without a round: `Unit.can_fire()` (a round left, or a gun with no magazine) is asked by
`ShootAction.is_available()`, `OverwatchAction.is_available()`, `Reactions._find_offers()` and
`Tactics.shots_at()`, so an empty gun gets no Shoot, no Overwatch, no reaction prompt and no AI shot.
`ReloadAction` is offered to a gun with a magazine (`is_granted`) and available while
`Unit.can_reload()` (rounds short of full) with `reload_cost()` actions left, dimmed otherwise (the
user's: "when the magazine is full, the action is disabled"). Like Hunker Down it marks nothing on the
map; Enter / Space or A spends the cost and plays `Unit.reload()`, a coroutine that awaits the figure's
`CharacterModel.reload()` and fills the magazine at the clip's `seat` moment, then waits out the clip
(`Unit.recover()`) before completing; full again, it is put away. Nothing is called over the unit's
head: a "Reloaded" call came first and was taken out at the user's request, the animation being
enough for now. Enemies have magazines too (the
user's call): the assault AI reloads first when empty (`Tactics.reload(true)`), and with nothing to
shoot and nowhere nearer to go tops up a part-spent one (`Tactics.reload()`) before ending its turn;
`TurnManager` carries an `AIAction.Kind.RELOAD` out as the action does.
`AmmoIndicator`, a HUD node in each map, draws the selected squad member's magazine in the
bottom-right corner, following `PlayerSquad.selection_changed` and the unit's `rounds_changed`;
`ActionController._place_hints()` stands the gamepad's prompt column on top of it while it shows (the
user's choice of corner). The action bar refreshes on the controller's `changed`, as for actions: a
round spent through an action, or on the enemies' turn, is caught then.

**Highlights are named layers.** `TileHighlights.set_layer(name, {tile: Color}, fill)` — each caller
owns a layer, last set draws on top. Current layers: `selected`, `move`, `move_path`,
`shoot_step_out`, `overwatch`, `throw_range`, `throw_blast`, and the gamepad's `cursor`, set
`on_top` so it stays over every layer set after it. A colour's alpha dims a square's fill and
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
or the menu opens on the same press. On the gamepad the two are apart: `Menu` is `pause_menu`, `B`
is `cancel_action`, and the open menu closes on either. Opening sets `get_tree().paused`; the menu alone runs
`PROCESS_MODE_ALWAYS`. A tab is any `Control` added to `PauseMenu.tabs`, titled by its node name.
The menu refills its tabs from `Campaign` each time it opens (`_refresh()`), so it never holds state of its own.

Its frame is `TabbedMenu`, which the world map's **`VillageMenu`** shares. A left click (`select_unit`)
on the icon of the `Destination` the party stands on (`Party.is_at()`: a trip there ends exactly on its
position) opens it with one tab per entry in that destination's `locations`, rebuilt each time, titled by
`Location.display_name`; a destination with none does not open. It is in the scene, so it sees Esc
(`cancel_action`) before the pause menu and takes it, and the gamepad's `Menu` too, which closes it
rather than open the pause menu over it. Being `PROCESS_MODE_ALWAYS` like every menu, it opens on
nothing while the tree is paused, or A on the pause menu's tab row would open it underneath. Down
from either menu's tabs goes to the open tab's `focus_selection()` when it has one.

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

**The new world map is a scene of Godot's own nodes, written once by program and changed by hand
from then on.** `Scenes/Map.tscn` is the island the campaign is moving to (nine kingdoms, 44
duchies, 220 counties; `MapCreation/` holds the pictures and data it was made from). The game does
not use it yet: `WorldMap.tscn` is still the main scene. A unit is 100 m, and pixel (x, y) of the
`MapCreation/` pictures is at ((x + 0.5) * 3.35, (y + 0.5) * 3.35). Its tree is its drawing order:
`Sea`, `Coast`, `Land`, `Forests`, `Borders`, `Lakes`, `Rivers`, `Channels`, `BordersOverLakes`,
`Roads`, `Bridges`, `Settlements`, `Party`, `Clock`, `Camera`, `MapReticle`, `VillageMenu`,
`SquadMenu`, `GameOver`, `BorderSwitch`, `Detail`. Its settlements are `Destination`s, some 2,000
villages and hamlets among them, its party the old map's, with a clock and a speed that are the
user's, and its camera's limits are the user's. Its forests, about half the land at each biome's
share (the user's), are 2,459 `Forest` pieces cut by county and kind, each an instance of
`Scenes/ConiferForest.tscn`, `BroadleafForest.tscn`, `TropicalForest.tscn` or `SwampForest.tscn`,
which inherit `Forest.tscn` and set only a colour, so the party is set upon in them as in the old
map's forest. A `Polygon2D` draws no holes, so a clearing is joined to its piece's outline by a cut
of no width, there and back, and every piece is cut into triangles as it is made, as Godot will cut
it (`MapCreation/Scripts/scene/godotcut.py`), since Godot draws nothing of one it cannot cut.
`Detail`, a `MapDetail`, is its level of detail: four tiers by the view's height in miles, the
user's (Realm; Kingdom under 480; Duchy under 240; County under 100, hamlets under 50), faded by
`modulate`, every line's width scaled by one factor of the zoom (the borders' less, and fainter closing
in), a few lines a frame. A new layer
that should come and go by the zoom goes in `MapDetail.SHOWN_FROM`; one of lines or polygons is
only ever faded, never hidden, since a `Line2D` shown again is built again and a `Polygon2D` cut into
triangles again (only the settlements are hidden outright, and stop their work, as do those far
from the view). Things that share an edge have the same points, each its own copy (two counties and
their border's line; a county and its `CoastOfCounty...`; a border along a river and its
`...Along...` line; a county and the forest pieces along its border and coast), so a hand edit
moves the copies too. The villages and the forests are made by `MapCreation/Scripts/villages/` and
`forests/` and spliced in by their `..._splice.py`; spliced again they are made afresh, and a hand edit
to one is lost. `MapCreation/Scripts/scene/m2_scene.gd`, which wrote the scene, now writes only the
villages and the forests alone, in the map's look, for those splices: its whole-scene part, which would
write the scene afresh in the old look, was taken out (git keeps it, at d8b5ec7). `Docs/MAP.md` has all
of it (settlements, party, clock, camera, look, forests, level of detail) and why; read it before touching the
map. `README.md`, "The new world map", has the decisions and what each node holds.

**Forests are shapes where the party may be set upon.** On the old map each is an instance of
`Scenes/Forest.tscn`, a light-green, half-transparent `Polygon2D` drawn in the editor, under
`WorldMap.tscn`'s `Forests` node, in world coordinates like the destinations (not under the rotated
`Map`). Its outline is its `polygon`, reshaped with the editor's polygon tools and saved as an
override on that instance; the colour is set once in `Forest.tscn`. `Forests` sits before
`Destinations` and `Party` so they draw on top. The new map's were made by program (above), each
piece an instance of its kind's scene, which inherits `Forest.tscn`: its odds and its battle are
both maps' at once.

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
the pause menu, which sees it after the scene, does not open over it, and the gamepad's `B`; the
gamepad's `Menu` takes the keyboard to Start (`SquadTab.focus_start()`). Closing it on Start unpauses the
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
`Grenade`, the `BattleItem` that carries its blast: 5 damage, 3 tiles across) `grenade`, `Shortsword.tres` `melee` (a `Weapon` that is not a gun, so it gives Strike rather than Shoot), `Medkit.tres` (a `Medkit`, the `BattleItem` that carries its `heal`) `medkit`. A new gun is a `Weapon` `.tres` tagged `gun`, and gets Shoot and Overwatch with no code. How many the party holds lives in `ItemStack`s in an `Inventory`, and the live one
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
what their learned skills add (see "Skills are data" below) and, for defense, their armor's
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
`PlayerSquad.award_survivors()`, which gives every member still standing `survival_experience` (50),
and adds to `Campaign.gold` whatever gold each one's skills find after a combat
(`Character.combat_gold()`, see "Skills are data" below), emitting `found_gold(unit, gold)`, on
which `TurnManager` calls "+N Gold" over that unit's head as a coin it picked up would be
(`ShotOverlay.flash_pickup()`).
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
and the debris capsule as before, as thick as the figure's body; neither turns with it. The click
body follows the figure out of its tile while it leans out of its cover (`Unit.lean()`, see "A
target is seen where it leans out" below), so a target is clicked where it is seen.

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

**Animations are poses written in code and baked.** `HumanoidAnimations` authors all 56 for the rig's
proportions: a function of time places the feet, the hands and what they hold, and leans the body,
and two-bone IK solves the limbs between, so a model with other proportions gets animations that fit
it by baking again. The rifle is held through `rifle_grip` and the rifle scene's `Foregrip` marker:
these arms reach only 8 voxels to the palm, which is why the aim holds the rifle under the chin and
the off hand just under the receiver, behind the fore-end. Each is sampled at 30 fps into an `AnimationLibrary`. Every stance
(`rifle`, `melee`, `unarmed`) has stand, crouch (on one knee behind low cover), wall (up close to
high cover), a lean out round either end of each of those two (`wall_lean_left` / `_right`,
`crouch_lean_left` / `_right`: `_wall()` and `_crouch()` with a side), hunker (lower on one knee,
bent over its weapon, behind either: hunkered down), ready_throw, cheer, run and throw; the rifle has
aim, overwatch, overwatch_crouch and
the back / strafe steps a rifleman takes stepping out, still aimed; the sword has ready_melee,
strike_sword, draw_sword and stow_sword, and reload_rifle, keyed on the arms and head alone so it
plays over whatever the legs hold; use_medkit and use_medkit_self (the kit held out to an ally, or
pressed to the figure's own middle) are keyed on the left arm alone, so they play in any stance, the
right hand keeping its weapon; and there are hop, fall, and the reactions fire_rifle,
hit_front, hit_back, dodge and land, which key only what they move and are added to the pose. Clips
carry the moments the game waits on as metadata: `speed` on the runs (5 tiles a second, a stride a
tile), `impact` on the strike, `release` on the throws, `swap` on the draws, `seat` on the reload,
`take`, `apply` and `stow` on the medkit's two; and each lean its `reach`, how far out of the
middle of its tile it puts the head (about 0.7 to 0.76 cells), measured off the pose as it is baked.
The editor's animation
panel can play them; a change made there is lost at the next bake.

**`CharacterModel` plays them through one `AnimationTree`.** Its `AnimationNodeBlendTree`
(`HumanoidAnimations.make_tree()`): `stance` picks the base loop; `move` blends it to `run`, scaled by
`run_scale`, whose `run_rifle` is a 2D blend of the forward, back and strafe runs; `hop` (legs only)
and `air` (falling) blend over that; `act` is a one-shot played whole (strike, throw, draw, stow),
`upper` a one-shot over the arms and head alone, filtered to them (the reload: a kneeling or hunkered
figure stays down; filtered because the tree blends deterministically, and a bone a clip leaves unkeyed
would be pulled toward its rest), `left` the same over the left arm alone (the medkit), and `react` a
one-shot added on top. The tree resource is shared by every figure, so the model sets its
parameters and never its nodes' properties. Most of what it plays it reads off its unit each frame:
it runs while `Unit.is_moving()`, as fast as the unit really goes, so a reaction's slow motion slows
its legs and a held walk freezes them mid-stride; it faces the way it goes, unless the walk keeps its
facing (`Unit.walk(..., keep_facing)`, a step out to shoot); and a step up or down a level lifts it in
a hop, on the figure's own position, so the unit still moves in a straight line and `tile_at()` never
sees it. `Unit.drop_to()` sets it falling until it lands. The rest the unit asks for, through
presentational calls that do nothing without a figure: `aim_at()` (raise the gun to a point, which
`AimModifier` bends the spine and chest to, above or below), `ready_strike()`, `ready_throw()`,
`celebrate()` (the winners, as `TurnManager` decides the battle), `reload()` (through `Unit.reload()`,
returning at the clip's `seat`), `attend()` (turned to an ally and looking at them, nothing readied,
which keeps `Postures` off the figure until `stand_easy()`), `use_medkit()` (through
`Unit.use_medkit()`, returning at the clip's `apply`; both take null for the unit itself: no turn, a
look down in front of it, `CharacterModel.SELF_LOOK`, and `use_medkit_self`), `stand_easy()` (at the end of the
frame, called off if something is readied again at once, so a Shoot that begins again never lowers
the gun), `dodge()`, `take_damage()`'s flinch, and `lean_out()` / `lean_back()` (see "A target is
seen where it leans out" below). Between actions `Postures`, a node in each combat
map, moves only figures that are `is_idle()`.

**Gear hangs in the figure's sockets.** `CharacterModel.equip(gun, melee, grenades, kits)` shows each item's
`Item.model`: a scene whose origin is where the hand grips it, standing along +z with its top up +y;
a gun's `Muzzle` marker is where it fires from and its `Foregrip` where the off hand holds it. The bake
makes the sockets: `RightHand/RifleGrip` and `SwordGrip`, `LeftHand/GrenadeGrip`, `Back/RifleSlot` and
`SwordSlot`, `Belt/Grenade1`..`3`. The gun is in hand; the sword is in hand without a gun, else slung
on the back and drawn for a strike, swapping with the gun at `draw_sword`'s `swap`; grenades hang on
the belt, one in the left hand while a throw is lined up; medkits hang on the belt slots the grenades
leave (three items at most, so there is always one), the first in the left hand from the medkit clip's
`take` to its `stow`, turned a quarter there (`MEDKIT_IN_HAND`) so its cross faces the ally. `Unit._dress()` calls `equip()` as the unit
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
which throws the first one, Item 1 before Item 2 before Item 3 (`Unit.grenade`), and uses it up. A
medkit in any item slot gives it Use Medkit, a use a battle for each, and is never used up.
Armor adds its `Armor.defense` to the wearer's (`Character.total_defense`),
which the unit copies as its own; the Details page shows that total and refreshes as it comes into view, since the
Equipment page may have changed the armor. During a battle `Campaign.in_mission` is true (the `TurnManager` sets it while in the
tree) and both calls refuse, since a unit took its gear when the map loaded; the Equipment page greys
its buttons and says why. This is the menu's first read-only-in-combat rule; the System tab's
**Blood** button is the second (see Blood), and learning a skill the third (see "Skills are data").
`Campaign.use_up()` and `lose()` do not refuse: they follow what the battle did.

The Roster tab is a `CharacterBrowser`, whose sub-tabs are `CharacterPage`s. Whenever the selection
in the strip changes, every page (not just the open one) gets `show_character(character)`, so a page
is never left showing someone else; a page with content overrides `_refresh()`, and
`focus_selection()` if Down from the sub-tabs should land somewhere in it. Changing character keeps
the open page; opening the menu goes back to Details. A page that can change the character hides
the means when `read_only` is set, as it is for characters not on the roster.

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
(`SkillsPage`, `SkillTreeView`, `SkillButton`: its columns, links and rings, holding a node to learn
it, the selection and the arrow keys), the `SkillTooltip`, the skills' gaps and what was decided
with the user. Read it before touching skills, trees or the Skills page.

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

**A target is seen where it leans out, too.** XCOM 2's rule (its visibility record traces "5 source
locations (default + 4 peeks) to 5 target locations (default + 4 peeks)"): the tiles a unit behind
cover can lean out to shoot from (`LineOfSight.lean_tiles()`, which `firing_positions()` adds to its
own tile) are also tiles it can be seen on. `find_shot()` first looks for a firing position that
sees the target's own tile, as it always did, so every shot there was before is unchanged. Only
when none does, it takes the first firing position (the shooter's own tile first) that sees one of
the target's lean tiles, and of those the nearest to it. Such a shot has `Shot.seen_at` on that
tile and `Shot.leaning` true; its cover, flanking, distance and height are still the target's own
tile's against `Shot.from`, so a unit behind a pillar is shot at through Full Cover. Sight
therefore runs both ways: whoever can lean out and shoot can be shot back at. A reaction passes
`leans` false (`Reactions._find_offers`), since a target on the move leans nowhere (XCOM 2's
`bDisablePeeksOnMovement`), and `watched_tiles()` is as it was for the same reason. XCOM 2's other
exceptions (unalerted enemies, units that cannot take cover) have nothing to apply to here.

`Ballistics` shoots at a leaning target where it leans to: a hit flies to the eye over
`Shot.seen_at`, which is the sight line, and a miss is aimed round the body there and kept clear of
the target both where it stands and where it leans; the cover a miss can be aimed at is still the
cover beside its own tile. The rest is for show. The target's figure leans out for as long as the
shot is lined up, and through the shot, as XCOM 2's targeted units hold their peek until the shooter
is back in cover: `Unit.lean_out(tile, watch, grid)`, called by `ShootAction` as the target is lined
up, by `ShotPlayback` as the shooter turns to it, and by `Unit.shoot_at()` itself, which waits until
the target `has_leaned_out()` before it rolls and, for a shot nobody lined up, has it lean back once
the round has landed. It leans from the cover standing square to the way it
leans (of two, the one more toward the shooter), turned to face that cover: `wall_lean_*` at high
cover, `crouch_lean_*` on one knee at low, its head turned to the shooter. `lean_back()` waits for
any flinch or duck to play out, so the hit is seen landing on it out there, and is called off if it
is leaned out again first, so it never bobs back between two shots; walking, falling or readying
anything stands it back at once. `Unit.lean()` is how far out its head is (the lean's `reach` toward
the tile), which `aim_point()` adds, so the shooter's aim, the sight line, the reticle and the
called result all follow the leaning figure, and `Blood` looks for the figure there. A hit on it is
drawn landing on the part of it that is out (`Unit._wound_on()`: a wound its cover hides from the
muzzle is picked again, on the figure's own generator). Only the figure moves: the unit never leaves
its tile, so coins, reactions and everything else that reads `tile_at()` see nothing.

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

**A breakable block is one of two kinds, and adding either is a recipe.** A `ScriptedDestruction`
breaks a block whole into pieces cut in advance, which collapse or, with **Blast** ticked and a
`DestructOrigin` marker in the pieces scene, burst apart (`Blast.burst()`); a `VoxelDestruction`
(`BrightGrass1`, both `SkinnyTree1` blocks) wears a block away a few voxels at a time. Either is a
`.tres` in `Resources/Destruction/` naming the block, added to `Catalog.tres`, and its art must be
imported from a `.vox` at Scale 0.0625, the blocks' scale. `Docs/DESTRUCTION.md` has both recipes
step by step, how wear works in full and its gaps; read it before touching either. What the rest of
the code has to know of wear:

- **A worn block draws itself; the rules see its stand-in.** The first time a block loses a voxel,
  `VoxelTerrain` makes it a `WornBlock` (its own mesh and trimesh collision) and swaps its GridMap
  cell to the block's stand-in, an item with no mesh and no shapes. `CombatGrid.is_solid()` only asks
  whether a cell has an item, so sight, cover, paths, throws, coins and units see the whole block,
  however little is left. Anything that reads a cell's item id must allow for a stand-in
  (`VoxelTerrain.wears_away()`, `shape_at()`, or `kind_of()` for any block drawn from a `.vox`, worn
  or not).
- **A round takes a bite, a blast blows a crater** (`VoxelTerrain.chip()`, `crater()`), and what is
  cut loose drops. A block left with less than `collapse_below` (half) of its voxels, or cut through
  under something it holds up (`_holds_up()`), breaks as a crate does: out of the grid at once,
  `block_broken`, stacks above fall, units drop. The bottom layer never breaks, and is only worn
  `FLOOR_DEPTH` (4) voxels deep, since a unit stands at the top of its block whatever is left of it.
- **Rounds are traced voxel by voxel** (`CombatGrid.cast(..., by_voxel)`, which of the rules only
  `Ballistics` passes); sight, throws and clicks stop at whole cells. Blood passes `every_block` as
  well, which traces every block drawn from a `.vox` so; rounds never do.
- **What breaks off is `VoxelDebris`:** each lump a rigid body straight on the `PhysicsServer3D`,
  with no node, every voxel drawn as an instance of a few MultiMeshes. Units dropping through a
  collapse pass through it, which is why `Unit.pass_through()` and `drop_to()` take body RIDs. At
  `VoxelDebris.MOST` (20,000) bodies the lumps at rest furthest from where the camera looks are
  stilled: drawn where they lie, bodiless until something disturbs them.
- **A broken crate's pieces wear away as well, as loose models,** since its `ScriptedDestruction` has
  a `wear`: a `RigidBody3D` drawn by a MagicaVoxel model, given a `VoxelBody`
  (`VoxelTerrain.take_on_body()`) the first time a round's line or a blast's crater reaches it.
  `Unit.shoot_at()` reports every round's line through `CombatGrid.fly()`, whose `round_flown` calls
  `VoxelTerrain.tear()`. A loose model blocks nothing in the rules.
- **It is deterministic.** Which voxels go, and so which blocks break, comes from the global random
  generator, one number a round or blast, so a seeded fight replays exactly, as long as no block
  falls whole (see Known gaps). Everything only for show (how lumps fly, wearing a loose model) draws
  on `VoxelTerrain`'s own generator (`_show`), never the global one.

**Blood is painted on voxel faces, and only for show.** `Unit.take_damage()` emits
`hurt(taken, from, at, blasted, sweep)` for every hit that takes health (none for one defense stops),
before the unit can die of it. `Blood`, a node in each combat map after `Coins`, connects to every
unit as it readies and does the rest: it wounds the figure and sprays drops, each a voxel under
gravity in one MultiMesh, which stain the first voxel face they meet and run from there
(`BloodFlow`), and a pool spreads where each of the dead stood. A stain is a face, never a voxel's
colour: `VoxelStains` keeps each stained voxel's faces and draws them as an overlay of red squares,
hung from whatever draws the model, so blood never rebuilds a block or a figure, and whatever moves
the model moves its stains. A stain is handed on only when its model becomes others (a block falling
whole, a crate's pieces, a board cut in two, a voxel broken off). A hit is drawn landing on the
body, not at the eye, where the round still flies: `CharacterModel.pick_wound()` picks where, kept in
`Ballistics.Path.wound`, which the tracer is drawn to and `take_damage()` passes on as `at`.

**Blood** on the pause menu's System tab turns it all off: `Blood.enabled`, a static like
`TileGrid.shown`, never saved, changed only between battles (the menu greys the button out while
`Campaign.in_mission`) and read by each map's `Blood` once, in `_ready`. Off, `Blood` still reads
every figure's rig as the map loads, since a shot still draws its tracer on to the body, then stops.
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
  Menus covering every `TabbedMenu`) or Combat, and every gamepad button under Gamepad. A new input
  action, a new use of an existing one, or a widget that reads keys or clicks itself gets a row
  there, and a gamepad binding: the game must stay playable with the pad alone, with what each button
  does on screen (a `confirm_hint()`, a `gamepad_hint()`, or a row in the prompts that list the rest).

## Combat rules that must not drift

- A unit fills **two cells** (`CombatGrid.UNIT_HEIGHT`) and sights from the centre of the upper one
  (`LineOfSight.EYE_HEIGHT`). This is what makes 1-cell blocks half cover (never blocks sight) and
  2-cell blocks full cover (blocks it).
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
a lane there over reasoning about geometry in your head.

The pillar and wall lanes show a target seen leaning out, from the other side: Enemy1 to Enemy5 see
Player3, and Enemy2 to Enemy4 see Player4, only where they lean out, through Full Cover (35 to
40%), and Player5 sees Enemy2 only leaning out of its half cover, past the wall lane. To
watch a squad member take such a shot, swap Player3 and Enemy3's positions in a probe
(`global_position`), select Player3, activate Shoot and cycle to Enemy3 (`ShootAction._cycle()`):
`current_shot()` has `leaning` and `seen_at`, `Enemy3.is_leaning()` and `model._base` say what its
figure is doing (`wall_lean_right_rifle`), and `ShotPlayback.new(grid, overlay).play(enemy, shot,
estimate)` plays one the other way. The rule itself is cheap to check exhaustively: teleport two
units to random pairs of tiles and compare `find_shot(a, b)` with `find_shot(b, a)` and with
`find_shot(a, b, false)`, which is the rule as it was before a target could be seen leaning.

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

The new map's scene is looked at with `MapCreation/Scripts/scene/m3_draw.gd`, in a window: it draws
the whole map at one screen pixel to a pixel of the pictures (`render_full.png`), times it, and
draws close views given as `x,y,w,h,scale,msaa,name` in the pictures' pixels;
`MapCreation/Scripts/scene/m4_compare.py` set it beside `MapCreation/AllSimple.png`, colour by colour, until
the map's look gave its lines colours of their own; `MapStyles/harness/render.sh 0` draws it at four views.

How to probe blood, the gamepad, a medkit and the new map (its look, its forests, its level of detail) is in their `Docs/`
files (`BLOOD.md`, `GAMEPAD.md`, `MEDKIT.md`, `MAP.md`), under "Probing it".

A death is probed headless too: `unit.take_damage(100, from, false, unit.model.pick_wound(from))` kills
with a round (a blast passes `blasted` and no `at`, a blade a `sweep` too), and
`TerrainDestruction.break_figure()` breaks any figure without its unit dying. Its lumps are the
`VoxelDebris` entries from `_state.size()` before it to after (`_centers[piece]` where each is now,
`_moved_at[piece]` the last step it moved, its body asleep once at rest); its gear the `Dropped<prop>`
bodies under `TerrainDestruction`. Seed the global generator and compare the next `randi()` with a
fresh seed's: a death draws nothing from it. Whether the lumps are red can only be seen in a window
(see Gotchas); they come to rest in 2-3 s, a blast's a little later.

Ammo is probed the same way: set `unit.rounds` directly (0 to empty it), read `can_fire()` /
`can_reload()` and the actions' `is_available()`, fire through `ShootAction._fire()` and reload by
activating `Reload` and sending Enter (or `ReloadAction._reload()`); `HUD/AmmoIndicator`'s `_rounds`
and `_magazine` are what it draws. An enemy's choice is `unit.ai.choose_action(Tactics.new(unit, grid,
squad.members))` (its `kind`), and `TurnManager._take_enemy_turn(enemy)` plays a turn out (await it
through a lambda, with the dictionary flag above). The reload clip is seen with `PreviewAnimations.gd
-- reload_rifle --over <base pose>`.

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
to see it. There `root.push_input(event, true)`, a mouse button event at a point in the viewport's
own coordinates (`Camera3D.unproject_position()`, or a control's `get_global_rect()`), clicks units
on the map and HUD buttons alike and leaves the player's cursor where it is; `Input.warp_mouse()` and
`Input.parse_input_event()` do too, moving the real cursor, and `Input.get_current_cursor_shape()`
reads the cursor. Turn off the actions' `_process` first (they follow the real cursor) and the
camera's `edge_pan_enabled`. On a software renderer (a cloud container's, under `xvfb-run`), setting
the root viewport's `scaling_3d_scale` low, and turning off the environment's SSAO and SSIL, makes
such a run several times faster.

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

Blood's, the gamepad's, the medkit's, the skills' and the new map's forests' and level of detail's gaps, and
more of voxel wear's and loose models', are in their `Docs/` files, under "Known gaps".

- A shared `Weapon` resource must stay stateless: per-unit state goes on the unit, as the rounds left
  in its magazine do (`Unit.rounds`), not on the weapon.
- There is one kind of magazine and no ammunition to buy, carry or run out of: a reload always fills
  it. Only the selected squad member's rounds are shown; an enemy's are seen only when it reloads,
  by the animation. The action bar dims and lights its buttons on the controller's `changed`, not on
  `Unit.rounds_changed`, so rounds set from outside an action (a probe) leave it stale until the next
  change. Reload has no key of its own: it is chosen on the bar (or the d-pad) and confirmed, as every
  action is. The reload is the rifle's alone (a pistol would need its own clip), and the rifle prop has
  no magazine to pull, so the hand mimes one. The assault AI tops up a part-spent magazine only when it
  has nothing else to do, never ahead of a fight.
- Crates break whole on any strike or blast, however weak: only blocks that wear away read
  `Weapon.environment_damage` and `Grenade.environment_damage`.
- A unit stands at the top of its tile however worn the block under it is, so it floats over a crater:
  up to 4 voxels on the bottom layer, deeper on a raised block. Tile highlights float with it.
- A worn block gives full cover until it breaks, however holed it looks; nothing reads partial wear.
  Each block holds up what is on it by itself: voxels are only joined across a cell face, not traced
  through several blocks, so a lump held only by a block that is itself cut loose stays put.
- A seeded fight replays exactly only while no block falls whole. A crate that falls draws on the
  global random generator when it lands (its pieces' knocks, its coin), at a moment the physics
  decides, so one that lands before the next round or blast in one run and after it in another
  changes the number that round or blast draws.
- Voxels are read from the `.vox` files at `res://` on ready: an exported build must include `*.vox` as
  non-resource files, and there are no export presets yet.
- `Scenes/Map.tscn` is not in the game. Its party keeps to no land, there being no land test or
  navigation for it: it crosses the sea and the lakes, and can be sent off the sheet. Its reticle's
  prompt says "Go here" over the sea as well,
  and its white ring is faint on the pale land. Only county 115's capital has anything in it, and it
  shares the old village's board and market: with both maps in one game they would be one shop.
  Its settlements are not drawn in the editor (`Destination`
  is no tool script, so the old map's village is not either): there they are nodes with no picture.
  The rest of its gaps, its forests' and its level of detail's, are in `Docs/MAP.md`. It is 13.6 MB
  of text and takes about 2.7 s to open, 1.7 before its 2,459 pieces of forest.
- The world map's land is baked, not live: after editing `WorldMap/WorldMapV1LandMask.png` (white
  land, black water, same size as the art), rerun `BakeLand.gd`. `-- --mask-from-art` regenerates
  the mask from the art and overwrites any edits to it.
- The squad panel does not wrap: past about five members it runs under the action bar, which it does
  in the harness (eight).
- The only experience is for surviving a battle. There are no classes, and Rich Blood, the Minor
  Noble tree's last skill, can be learned but does nothing. Grenades are the only items used up in
  battle. Every encounter is the same `BoundaryMap.tscn`, fresh each time, with its four enemies.
- Enemies never strike, throw or hunker down: their AI only shoots, so no enemy figure draws a sword,
  readies a grenade or ducks, though the same figure can. Nor do they carry medkits, and their AI never
  heals.
- The player never sees the Hunkered term at work: an enemy's shot shows its line but not its odds,
  so only the outcomes tell. Hunker Down marks nothing on the map while it is lined up, and the unit
  hunkers wherever it stands in cover, whichever way its cover faces.
- Every unit wears the one figure, and only `BaseCharacter.vox` has a rig layout. Armor does not show
  on it, and a character's colour is the only thing that tells the squad apart.
- A figure turns on the spot without stepping, so its feet slide round. Every throw is left-handed,
  so the right hand keeps its weapon. There is no wounded idle.
- A target leans out of its cover only for a shot that sees it leaning, while that shot is lined up
  or played. XCOM 2 has more: a unit in cover leans out for a look every few seconds while it has
  enemies in sight, and one that is targeted holds its peek even when it is seen where it stands.
  Neither is here. Nothing but the figure says a target is leaning: the target panel reads its
  cover alone, and the tile it leans out to is not marked as the shooter's step-out tile is.
- The lean is the base pose cross-fading (0.22 s), so the figure slides along its cover to the edge
  rather than stepping there, and its head keeps the tilt of its chest. It leans out about three
  quarters of a tile, which from straight in front of its cover at long range shows its head, a
  shoulder and half its chest past the edge and no more; a hit is drawn landing on what shows.
  The debris capsule stays on its tile; the click body goes out with the figure.
- The enemy AI gains the shots the rule gives it and nothing else: `Tactics.advance()` still walks
  toward the nearest foe, and nothing weighs where a move would leave it seen leaning out.
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
