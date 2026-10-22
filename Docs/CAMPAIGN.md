# Campaign

The campaign between battles in full: the party travelling the world map and set upon in its
forests, the battle that follows and who fights it, a defeat and the end of the game, the villages'
locations, and the hiring boards and markets that spend the party's gold: `Party`, `Forest`,
`SquadMenu`, `VillageMenu`, `Location` and its kinds, the shop tabs, and the parts of `Campaign` (the
autoload holding what outlives a scene) that they use. It was split out of `CLAUDE.md`, which keeps
a summary. The roster the party is made of, their equipment and the items the shops sell are
`Docs/ROSTER.md`'s; the new world map's scene, `Scenes/Map.tscn`, is `Docs/MAP.md`'s, which has the
same party, forests and menus. A section named here that is not in this file (Gotchas,
Verification, Known gaps, another subsystem's notes) is `CLAUDE.md`'s.

## How it works

The campaign is played on `Scenes/WorldMap.tscn`, the main scene. What outlives a scene is
`Campaign`'s, an autoload: the roster, the inventory and the gold, who is still on each hiring board
and what is left in each market, who fought last, and whether a battle is on (`in_mission`).

### Travelling, and being set upon

**Forests are shapes where the party may be set upon.** On the old map each is an instance of
`Scenes/Forest.tscn`, a light-green, half-transparent `Polygon2D` drawn in the editor, under
`WorldMap.tscn`'s `Forests` node, in world coordinates like the destinations (not under the rotated
`Map`). Its outline is its `polygon`, reshaped with the editor's polygon tools and saved as an
override on that instance; the colour is set once in `Forest.tscn`. `Forests` sits before
`Destinations` and `Party` so they draw on top. The new map's were made by program (`Docs/MAP.md`,
"Forests"), each piece an instance of its kind's scene, which inherits `Forest.tscn`: its odds and its
battle are both maps' at once.

**Random encounters are rolled per step and fought on a battle scene.** The party counts the distance
it travels in steps of `Party.step_length` map pixels; at the end of each it asks `Forest.find_at()`
which forest it is in (the one drawn on top where they overlap) and rolls that forest's
`encounter_chance`, a percentage per step. On a success it emits `encountered(encounter_map)`, which
opens the map's `SquadMenu` (see below) over the paused map; holding its Start calls
`Campaign.start_battle(map, chosen)`, which takes the world map's scene out of the tree, without
freeing it, and makes a fresh instance of the battle scene (`BoundaryMap.tscn`, the `encounter_map`
every forest gets from `Forest.tscn`) the current scene; the swap is deferred to the end of the frame.
`TurnManager` listens to every enemy's and squad member's `died`, and once either side is gone it sets
`outcome` (`WON` / `LOST`), disables the `ActionController`, announces "Victory" or "Defeat" and calls
`Campaign.end_battle()`, which frees the battle and puts the same world map node back. A defeat goes
back to the map like a win. If it killed the last of the roster, the map's `GameOver` layer sees the
empty roster on its first frame back: it pauses the tree, shows "Game Over" in its own `TurnBanner`
(laid out as the combat HUD's, over the menus at `TabbedMenu.LAYER + 1`, running through the pause),
and quits on the banner's `fading` signal, the moment its fade-out starts. Nothing on the map is saved
or restored: its `_ready`s do not run again, so the party is on the spot it was set upon, still on its
route, and the camera is where it was. Anything on the map that must notice a battle has passed (the
navigation map re-registering, for one) sees only `_exit_tree` / `_enter_tree`. `WorldMap.tscn` is the
main scene; a battle opened on its own (F6, the harness) has nothing to go back to, so it is left over
and idle after "Victory".

### Choosing who fights

**Who fights is chosen as the battle starts, on a menu that cannot be closed.** `SquadMenu` is a
`TabbedMenu` in `WorldMap.tscn` that `Party.encountered` opens (a party is its `party_path`). Its one
tab, titled Roster, is a `SquadTab`: the pause menu's `CharacterBrowser` over `Campaign.roster` (pages
and equipment work as there, the battle not having begun) above a footer laid out as `PurchaseBar`'s,
the hint and count on the left and a "Start" `HoldButton` on the right. A `CharacterButton` emits
`activated` on a double-click (seen in its `_gui_input`, which runs before the button's own) or Enter
/ Space; `CharacterBrowser` passes it on as `character_activated`, and the tab toggles that
character's tick, up to `Campaign.SQUAD_SIZE` (4), refusing another at the cap. A single click only
changes whose pages show. Start is greyed out with nobody ticked. It opens on `Campaign.squad()`,
which is whoever was chosen last and is still on the roster (the first four before any battle, or
after a whole squad fell), and Start passes the ticks to `Campaign.start_battle(map, chosen)`, which
keeps them for the battle's `PlayerSquad` and the next menu. It swallows Esc (`cancel_action` and
`pause_menu`, the same key) so the pause menu, which sees it after the scene, does not open over it,
and the gamepad's `B`; the gamepad's `Menu` takes the keyboard to Start (`SquadTab.focus_start()`).
Closing it on Start unpauses the tree, and the deferred swap takes the map out of it before it moves
again. Mouse input pushed into a headless probe does not reach the GUI (`CLAUDE.md`'s Gotchas): drive
this menu's clicks in a windowed run.

### Villages, and what is in them

The pause menu's frame is `TabbedMenu`, which the world map's **`VillageMenu`** shares. A left click
(`select_unit`) on the icon of the `Destination` the party stands on (`Party.is_at()`: a trip there
ends exactly on its position) opens it with one tab per entry in that destination's `locations`,
rebuilt each time, titled by `Location.display_name`; a destination with none does not open. It is in
the scene, so it sees Esc (`cancel_action`) before the pause menu and takes it, and the gamepad's
`Menu` too, which closes it rather than open the pause menu over it. Being `PROCESS_MODE_ALWAYS` like
every menu, it opens on nothing while the tree is paused, or A on the pause menu's tab row would open
it underneath. Down from either menu's tabs goes to the open tab's `focus_selection()` when it has
one.

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
mouse or Enter / Space. A sale is never greyed out for want of gold. It emits `held`, never acts on a
click, and empties the moment it is full, then stays empty until it is let go and pressed again: one
purchase per press, so holding on never buys a second, nor the next item or character that comes up.
The bar rechecks the party's gold whenever it is shown, since the other tab may have spent some.

## Traps

Two of Godot's limits met on the old map's land, and what is done instead:

**The 2D navigation server cannot handle long sliver polygons.** Baked whole, the pixel coastline gave
polygons thousands of pixels long and a few wide, and the server found no polygon under points inside
them. `BakeLand.gd` bakes in 256 px tiles, and adds every corner on a tile line to the edges along it
on both sides, or the tiles do not join. The world map's navigation also takes over a second after the
scene opens to be usable (`WorldMapTerrain.is_ready()`), and a `NavigationPathQueryParameters2D` gives
up after 4096 polygons unless `path_search_max_polygons` is set (0 lifts it).

**`Geometry2D.is_point_in_polygon` is wrong near vertices on big outlines.** It casts a slanted ray
and fudges any crossing within a relative epsilon of a vertex; on the world map's 33k-corner coastline
it misjudged about one coast pixel in a hundred. `WorldMapTerrain._encloses` counts crossings row by
row instead. Do not use the built-in for land tests.

## Its scripts

`CLAUDE.md`'s Layout lists every script in a line or two; here are this subsystem's in full.

```
  WorldMap/            the campaign map, Scenes/WorldMap.tscn (2D)
    WorldMapCamera.gd  pan / zoom with the combat camera's input actions; the left stick pans, the right zooms;
                       its limits the map sprite's, behind _has_map(), _map_rect(), _max_zoom() and
                       _clamp_to_map(point, zoom), which MapCamera overrides
    MapReticle.gd      CanvasLayer in WorldMap.tscn: the gamepad's reticle in the middle of the screen and its
                       prompts (A's words from VillageMenu.enterable() and Party.can_go_to())
    WorldMapTerrain.gd is_land() on the baked collider, routes: straight rays, else navmesh pulled straight
    BakeLand.gd        tool: traces WorldMap/<map>LandMask.png into <map>Land.tscn (collider + navmesh)
    Party.gd           the party dot: sent by any right click, or A at the reticle (no selecting), travels a route
                       found by its terrain_path: a WorldMapTerrain on the old map, a MapNavigation on Map.tscn
                       (worked out on a thread while it waits, each leg at its ground's pace: Docs/MAP.md,
                       "Navigation"), or with none a straight line to anywhere;
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
  UI/
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
```

## Probing it

The campaign is probed headless, as the rest is (`CLAUDE.md`'s Verification). `Campaign` is there
at run time (`root.get_node("Campaign")`), though a `--script` probe cannot name it, or anything that
reaches it, in a type (`CLAUDE.md`'s Gotchas). An encounter is probed without walking, as
`Docs/MAP.md` has it for the new map: disconnect the squad menu from the party's `encountered` (it
would open and stop the map), connect a counter, then set `party.global_position` and call
`party._take_steps(party.step_length)`, one step a call. A battle starts as the menu's Start starts
it, `Campaign.start_battle(map, chosen)` with the battle's `PackedScene` and a typed
`Array[Character]`, the swap coming at the end of the frame; the shops are `Campaign.for_hire(board)`
and `stock_of(market)`, and `hire()`, `buy()` and `sell()` do what the hold buttons do. Clicks on the
menus have to be driven in a window (`CLAUDE.md`'s Gotchas, "Headless quirks").

## Known gaps

- The world map's land is baked, not live: after editing `WorldMap/WorldMapV1LandMask.png` (white
  land, black water, same size as the art), rerun `BakeLand.gd`. `-- --mask-from-art` regenerates the
  mask from the art and overwrites any edits to it.
- Every encounter is the same `BoundaryMap.tscn`, fresh each time, with its four enemies.
