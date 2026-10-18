# The new world map

`Scenes/Map.tscn`, the island the campaign is moving to: how its scene is laid out, its forests,
and its level of detail, `MapDetail` (`Scripts/WorldMap/MapDetail.gd`, the scene's `Detail`
node), which shows less far out and more close in and holds the lines near a width on the screen.
`CLAUDE.md` keeps a summary; `README.md`, "The new world map", has the decisions and what each
node holds. A section named here that is not in this file (Gotchas, Verification) is `CLAUDE.md`'s.

## The scene

**The new world map is a scene of Godot's own nodes, written once by program and changed by hand
from then on.** `Scenes/Map.tscn` is the island the campaign is moving to (nine kingdoms, 44
duchies, 220 counties; `MapCreation/` holds the pictures and data it was made from, and
`MapCreation/Features.md` describes them). The game does not use it yet: `WorldMap.tscn` is still
the main scene. A unit is 100 m. A pixel of the `MapCreation/` pictures is 3.35 units, the sheet's
top left corner is the origin, and pixel (x, y) is at ((x + 0.5) * 3.35, (y + 0.5) * 3.35). Its tree
is its drawing order: `Sea`, `Coast`, `Land` (a `Polygon2D` a county, under `Kingdom` and `Duchy`
nodes), `Forests` (a `Forest` a piece, under groups by size and kingdom: see
[Forests](#forests)), `Borders`, `Lakes`, `Rivers`, `Channels`, `BordersOverLakes`, `Roads`,
`Bridges`, `Settlements`, `Party`, `Clock` (a `MapClock`), `Camera` (a `MapCamera`, so the scene
runs by itself), `MapReticle`, `VillageMenu`, `SquadMenu`, `GameOver`, `BorderSwitch`, `Detail`.

A settlement is a `Destination`, as the old map's village (the user's call): an instance of
`Scenes/City.tscn` (a kingdom's or a duchy's capital) or `Scenes/Town.tscn` (a county's), the
pack's Castle and Town cropped into `vcom/WorldMap/` as the village's art was, so an icon of one
height on the screen at any zoom with its `display_name` in a tooltip under the pointer.
`icon_height` is on each scene's root (26 and 20, not the village's 32, which with 220 on screen
hides the map: my call), and an instance keeps only its position, its `display_name` (a
placeholder, "Capital of County 103": nothing is named yet) and its county's, duchy's and
kingdom's numbers as metadata. Villages and hamlets have their scenes too (`Scenes/Village.tscn`,
16, the pack's Village; `Scenes/Hamlet.tscn`, 12, `Hamlet2.png` of the pack's folder as
`WorldMap/Hamlet.png`) and their groups, `Settlements/Hamlets` and `Villages`, ahead of the
capitals' so that towns and cities draw over them: 1,102 hamlets and 898 villages, with the
villages' `Roads/Lanes`, `Bridges/Lanes` and the Swamp's `Channels`, placed by program
(`MapCreation/Scripts/villages/`, spliced in; `README.md` has the user's calls). `Village.tscn` is
the old map's village as well, which keeps its 32 by setting `icon_height` on its own node in
`WorldMap.tscn`.

`Party` is the old map's `Party`, brought over at the user's request (the old map keeps its own):
it starts near the middle of county 115, at (7302, 7381), the outline's centroid, as they asked,
and is drawn over the settlements. Its `terrain_path` is empty, this map having no land collider or
navigation mesh, so it goes wherever it is sent in a straight line, over water too; a right click
on a settlement's icon sends it to the settlement. Keeping it to the land is not built: what stops
it (lakes, rivers but for their bridges) is the user's to say. Its speed is the user's: 25 miles a
day (`Party.miles_per_day`), a day taking 30 real seconds (`MapClock.seconds_per_day`, on the
scene's `Clock`, which the party's `clock_path` names), so 13.4 units a second. Time passes only
while the party moves: `Party` calls `MapClock.advance()` with the seconds it spent travelling, and
nothing else moves the clock. The clock counts down from `starting_days` (90) in the top left
corner, as days:hours:minutes, and nothing happens yet when it runs out (the user's: "for now"). A
step is still every 5 km, by distance (their call), about eight a day, and one that ends in a
forest rolls that forest's odds of a battle. The old map's party has no clock and keeps
`travel_speed`.

One settlement has something in it, at the user's request: county 115's capital has the old
village's hiring board and market, the same two `.tres` and not copies (my call: a character stays
on one board), and the scene's `VillageMenu` opens them as on the old map, on a left click once the
party is in the town. A town shows from the Duchy tier, so it is sent to and entered only that far
in. `MapReticle`, the gamepad's ring and prompts, is the old map's as well, and so are `SquadMenu`
and `GameOver`, which the forests set off: a battle met in one opens the squad menu, and a battle
lost with the last of the roster ends the game.

The camera's limits are the user's: all the way out the whole land just fits the window and
nothing pans; all the way in the view is 25 miles tall (`MapCamera.closest_view_miles`, a mile
being `UNITS_A_MILE`, 16.09344, of the map's units: 56 m to a pixel at 1280 by 720, 33 times all
the way out; it was first just large enough for any one outline of the land, 186 m to a pixel,
which they then replaced); and the view never leaves what is seen all the way out (that view's
edges, not the land's own box, as they chose, so in a wide window it can slide out over the sea
either side). `MapCamera` reads the land's extent off `Land` and `Coast` as the scene opens.

Areas are `Polygon2D` and lines `Line2D` with a width in units. Last in the tree is `Detail`, a
`MapDetail`, the map's level of detail while the game runs (the editor shows every node, at the
width it was given): see [Level of detail](#level-of-detail). Lines are thin far out, which is why
`project.godot` has 4x 2D MSAA (`anti_aliasing/quality/msaa_2d`), for the whole game: nothing else
in Godot 4.7 smooths a `Line2D` or a `Polygon2D`, whose own `antialiased` does nothing.

Things that share an edge have the same points, each its own copy: two counties and the line of
the border between them; a county and its stretch of `Coast` (`CoastOfCounty163` for `County163`,
named apart so that a search by name finds one thing; a line twice the coast's width, its inner
half under the land); a border that follows a river, the river, and the `...AlongRiver` line under
the river that shows the border's colour on both banks; a county and the pieces of forest along its
border or its coast. A hand edit has to move the copies too. **Never run
`MapCreation/Scripts/scene/m2_scene.gd` over it unasked: it writes the scene afresh, and every
change made by hand is lost.** `MapCreation/Scripts/README.md`, step 11, has how it was made and
checked, step 13 how the villages were placed, and step 14 how the forests were made.

## Forests

**The forests cover about half the land, each kingdom's share by its biome**, made on 2026-10-17
at the user's request: realistic forests for the whole map, scaled to each biome and fitted to the
terrain. Of three amounts put to them they chose the wild one, little cleared and that round the
settlements the map shows, at these shares of each kingdom's land, its lakes left out: the
Tropical Rainforest 92%, the Evergreen Temperate Rainforest 88%, the Deciduous Forest 80%, the
Swamp and the Temperate Mountains 60%, the Volcanic Mountains 30%, the Tundra Mountains 20%, the
Grassland 9% and the Desert 1.5%; 48.7% of the land, 336,575 km² in 1,101 forests. They are in the
source data too, `MapCreation/SourceData/Forests.json`, made by
`MapCreation/Scripts/forests/f1_forests.py`, whose step in that folder's README gives every rule.
In short: a forest grows under its kingdom's tree line, higher on a south face and along water;
in the dry country only by water or high enough on the mountains to catch the rain; in the cold
country in its valleys; not on cliffs, windswept coasts, high ridges, the wet floors of the great
rivers' valleys, the Swamp's open marsh, or the volcanoes and their lava; and people have cleared
it round every settlement, the farther along a flat valley floor or a road and the less up a slope.

**In the scene they are `Forests`, after `Land` and before `Borders`,** so they are drawn over the
land and under everything else: borders, water, roads, settlements and the party. They are cut
into 2,459 pieces, each a `Forest` (`Scripts/WorldMap/Forest.gd`, the old map's), by
`MapCreation/Scripts/scene/forestshapes.py`:

- **By county:** a piece belongs to one county, and is cut by the county's own outline, so it stops
  exactly on the coast and two pieces either side of a border share its points. Its name is its
  county's, numbered in it, the largest first: `County125Forest3`. Its metadata holds its
  `county`, `duchy` and `kingdom`, and the `forest` it is a piece of (its `id` in `Forests.json`)
  with that forest's area, `forest_km2`.
- **By kind,** each an instance of its kind's scene, which inherits `Scenes/Forest.tscn` (the old
  map's forest, so its odds and its battle) and sets only its colour, see-through at half
  strength over the white land: `ConiferForest.tscn` a cool blue-green, in the Tundra and the
  Volcanic Mountains, the Evergreen Rainforest and high up in the other kingdoms (over 1,000 m in
  the Temperate Mountains, 900 in the Desert and the Grassland, 1,100 in the Deciduous Forest, 600
  in the Swamp); `BroadleafForest.tscn` a soft yellow-green, below those heights;
  `SwampForest.tscn` an olive green, in the Swamp's own low country; and `TropicalForest.tscn` a
  deep green. A colour is changed for every piece of its kind on its scene's root.
- **Grouped by the size of the whole forest,** so that a forest comes and goes whole:
  `Forests/Great` (250 km² and more: 1,182 pieces), `Large` (50 to 250: 111), `Small` (10 to 50:
  269) and `Woods` (0.5 to 10: 897), each by kingdom under that (`Forests/Great/Kingdom8`).
- **Their clearings joined to their outlines.** A `Polygon2D` draws no holes, so each clearing in a
  piece is joined to its outline by a bridge: a cut of no width from a point of the clearing to a
  point of the outline, out and back along the same line, so that the outline goes round the
  clearing and has the bridge's two points twice. 1,471 bridges, in 457 pieces. Drawn, a bridge
  shows nothing at any zoom: the triangles either side of it share its line.
- **Known to draw.** Godot cuts every `Polygon2D` into triangles as it first draws it, and fails
  ("Invalid polygon data, triangulation failed") on an outline it cannot cut, which then draws
  nothing. `forestshapes.py` cuts every piece as Godot will (`godotcut.py`, Godot 4.7's own cutter
  done again in Python) and cuts in two any it could not, and any of more than 500 points: that
  cutter takes a time that grows with the square of an outline's points.

**A step in a forest may meet a battle, as in the old map's forest.** Every piece is a `Forest` at
`Forest.tscn`'s odds, 10% a step (the user's choice), and the party asks `Forest.find_at()` at each
step's end, as on the old map: tried on 2,000 steps taken in forests, 205 met a battle (10.3%),
and on 2,000 taken at villages, which stand in their clearings, none did. A piece's own
`encounter_chance` overrides its scene's, should a forest need other odds.

**Changed by hand,** a piece is an ordinary `Polygon2D`: its points move with the editor's polygon
tools. Its points along a county's border or the coast are copies of the county's, so a border
moved by hand leaves the forest's edge where it was until the forests are cut again (below). A
bridge is two points of the outline lying on two others: dragged apart, it opens a sliver of no
forest into the clearing. A piece moved to another size group comes and goes with that group. To
make them again, after a change to the rules or the land: `MapCreation/Scripts/README.md`, step 14
(`f1_forests.py`, `f2_shapes.py`, `m2_scene.gd ... forests`, then `f3_splice.py ... --replace`);
after a change to the land alone the last three do, and cut the same forests by the land as it
stands. Either way, every change made to the forests by hand is lost.

## Level of detail

**The view is in one of four tiers, by how tall it is in miles.** Each is named for what about
fills the window then, and adds to the one before it. Wheel steps are counted from all the way
out, in the game's 1280 by 720 window, where each height sits between two steps:

| Tier | View's height | Wheel steps | Brings |
|---|---|---|---|
| Realm | over 480 mi | 0 to 2 | The coast, the land, the kingdoms' borders and their 9 capitals, the 42 rivers at least 12 units wide, the 79 lakes at least 100 units across, the 34 forests of 250 km² and more |
| Kingdom | 480 to 240 mi | 3 to 5 | The duchies' borders and their 35 capitals, the highways, 92 more rivers (at least 9 wide), 179 more lakes (at least 50 across), the 58 forests of 50 to 250 km² |
| Duchy | 240 to 100 mi | 6 to 9 | The counties' borders and their 176 capitals, the other roads, the bridges, every river and lake, the 203 forests of 10 to 50 km² |
| County | under 100 mi | 10 to 16 | The villages, their lanes and the bridges on them, the Swamp's channels, the 806 woods under 10 km²; and in a second step, under 50 mi (steps 13 to 16), the hamlets |

The County tier's second step is a tier of its own in the code (`Tier.HAMLETS`, from
`hamlet_view_miles`), since it comes and goes as a tier does; everything said of tiers here holds
for it.

`MapDetail._process()` reads the height off the viewport's canvas transform, as a `Destination`
reads its scale, so it follows whatever camera the scene has. A tier's groups are in
`MapDetail.SHOWN_FROM`, by their place under the map (the forests' by the size of the whole forest:
`Forests/Large`, `Small` and `Woods`; `Forests/Great` always shows); the rivers and lakes are sorted one by one
as the scene opens, a river by its `width` (its widest, at the mouth) and a lake by how far across
a circle of its area is, and an island in a lake (`Lake001Island1`) goes with its lake. Anything
neither named nor sorted shows always. A tier holds until the view is `boundary_slack` (5%) past
its height, so a view resting on one does not flicker.

**What a tier brings is faded, and only the settlements are hidden.** Each tier has one amount,
0 to 1, moved over `fade_time` (0.2 s) and multiplied into the `modulate` alpha its things have in
the scene. At nothing the renderer skips them, at no cost either way, where showing a hidden
`Line2D` builds it again (0.07 ms a line, 70 ms for the Duchy tier's) and a hidden `Polygon2D` is
cut into triangles again (2 to 4 ms for a tier's forests; 215 ms for the great forests, which
always show). A group with no line and no
polygon under it, which is each rank of settlement, also has `visible` set false once faded out: a `Destination`
out of sight is not under the pointer, and on `NOTIFICATION_VISIBILITY_CHANGED` it stops its own
`_process`, which costs 6 microseconds a frame for each one there is, on screen or off.

**A settlement far from the view does no work either.** There are 2,220, and the 1,118 that show
from the County tier until its second step would cost some 7 ms a frame in their own `_process`
at 6 microseconds each, wherever the view was. So
`MapDetail` sorts them as the scene opens by their group and the square of `PLACE_SQUARE` (512
units) they are in, and every frame the view moves, or a rank of them comes or goes, it sets
`Destination.in_view` on those of the groups showing that lie in the view and `VIEW_MARGIN`
round it, and clears it on the rest (`_wake_places()`): those work, the rest stop their
`_process` and are not pointed at. At most some 300 work at once (95 miles over the Deciduous
Forest), 40 all the way in, and finding them costs 0.2 ms at the most; only the groups showing
are looked through, as looking through all 2,220 every frame took 1.8 ms all the way out. A
settlement out of view also **draws nothing**, and draws itself afresh as it comes into view. Its
icon is drawn for the zoom it last saw, so left as it was it would grow with the map as the view
closed in: a city put away all the way out, just off the view, came back half the window high
over the Swamp once the view was in close.

**Every line's width is its node's times one factor,** `(view's height / true_width_view_miles)
^ (1 - width_growth)`: at 220 miles tall a line is as wide as the scene says, and from there its
width on the screen follows only 0.36 of the zoom. A kingdom's border is 2.2 px all the way out
and 7.5 all the way in (0.9 and 30 left alone), a lesser road 1.4 px where it first shows and 3.1
all the way in (12.5 left alone), the coast 3 to 10. It is one factor for all of them because some
are sized to others (below), and it scales a river's `width_curve` with it.

**Widths are set a few lines a frame, the furthest off first.** Setting a `Line2D`'s width builds
it again, about 0.7 microseconds a point, 130 ms for all 1,796 at once. So the factor moves in
steps of `width_step` (1.06), and `_refresh_widths()` sets only lines that show at this tier and
whose box reaches the view (and `VIEW_MARGIN` round it), at most `points_per_frame` (4,000)
points' worth a frame: first those more than `FAR_STEPS` (8) steps off, then those more than
`READY_STEPS` (3), then the rest, each pass carrying on from where the last frame stopped. A line
out of view, or out of its tier, keeps the width it had; the first frame sets every line, since
all of them are built then anyway. So a tier's lines are far off when it comes in again: it waits
(`_waits`), its lines being the furthest off and so set first, and starts to fade in once those
in view are within `READY_STEPS`, or after `MOST_WAIT` (0.5 s) whatever they are.

**A border's line along something is a plain border while that is hidden.** A line named
`...AlongRiver173`, `...AlongLake085` or `...AlongRoad093` lies under the river, shore or road its
border follows, as wide as that and the border on both sides. While the river, lake or road does
not show at the view's tier, the line is given the plain border's width (the middle one of its
group's lines that follow nothing: 17, 10 or 7) and no width curve, so no river has to stay for a
border's sake. A river or lake is found by the name (`Rivers/River173`); a road's number is in no
node's name, so it is the road that shares the line's middle point. Of the 258 such lines, 45 are
narrowed at some tier.

**A border's or a river's end in the sea moves with its width.** Where one reaches the sea it
ends past the land's edge, in the coast's black line: about 10 units out, the coast's line being
23 wide outside the land. Left there, the end came out of the far side of the coast's line once
that narrowed: all the way in the coast's line is under 6 units, and the ends showed 4 units (8
pixels) out over the sea. So `_gather_sea_ends()` finds, as the scene opens, every line under
`Borders` or `Rivers` (`ENDS_IN_COAST`) that, followed back from an end, crosses a coast's line
within the coast's width outside the land (138 lines), and `_set_width()` moves the points out
there as it sets the width: how far each is past the crossing is scaled by the widths' factor.
The end is then as deep in the coast's line at every zoom as the scene has it, and at 220 miles
tall the points are the scene's. It costs nothing more, the width having built the line again
anyway; finding them takes about 35 ms as the scene opens. Roads and bridges are left out: the
road over the sea to the island town crosses the land's edge and ends on land.

**The player can switch every border off, on top of all this.** The scene's `BorderSwitch` node
(`Scripts/WorldMap/BorderSwitch.gd`) answers `toggle_borders` (`B`, the gamepad's `R3`) by
setting the `modulate` alpha of the two groups the borders are in, `Borders` and
`BordersOverLakes`, to nothing and back. `MapDetail` never touches those two, only the ranks
under them, so the two multiply and never meet: while the borders are off, the tiers go on
coming and going under them and their lines are given their widths as ever, and switched on again
at any zoom they show as that tier has them, at once (the switch's frame takes no longer than
another, about 2 ms). It hides nothing outright, since showing the borders' 730 hidden lines
again would build each anew, some 50 ms. It starts on, and is not saved.

**Nothing in the scene as saved changes.** `MapDetail` is no tool script: the editor shows every
node, at the width it was given, and those widths are the ones the map has at 220 miles tall.

## What it costs

Measured in a window at 60 frames a second (an RTX 3060 laptop). A frame at rest takes about 1 ms
all the way out, 3 at the far end of the Duchy tier, and 2 all the way in. With the villages
(2026-10-17): about 1.1 ms all the way out and all the way in, and 3.6 ms at the far end of the
County tier over the Deciduous Forest, where the most is drawn and the most settlements work.

Sixteen wheel steps all the way in over the Swamp's capital, 0.2 s a step, a pan there, and
sixteen steps out, with and without the villages (the same run on the scene as it was before
them):

| | Zooming in | Panning all the way in | Zooming out |
|---|---|---|---|
| Without the villages: a frame on average, at the worst | 5.0 ms, 8.9 ms | 3.8 ms, 5.7 ms | 5.3 ms, 9.1 ms |
| With them | 3.9 ms, 9.3 ms | 2.4 ms, 3.1 ms | 4.6 ms, 9.6 ms |

Less on average, since the capitals out of view now stop too; the worst frames, where a tier comes
or goes, half a millisecond more.

- A wheel step: the worst frame 6 to 8 ms; the steps into and through the Duchy tier average 5
  to 6 ms a frame while they last.
- The right stick from one end to the other (3.2 s): the worst frame 9 ms, 5 on average. Up to
  700 lines are behind at once, by 5 steps at most going in and 7 coming out, and all are right
  0.6 s after it stops. A tier waits up to 0.3 s on its lines.
- Panning in the Duchy tier: no line in view is ever behind.

**The forests (2026-10-17)** made the scene 13.5 MB, from 9.1, and it opens in 2.7 s, from 1.7:
0.65 s more reading the file, and some 0.35 s more on the first frame, mostly Godot cutting the
2,459 pieces into triangles (0.22 s; 0.6 s before the larger were cut down to 500 points). A frame
at rest all the way out takes 3.7 ms, from 1.4 to 2.4 (1,715 draw calls, from 533: each piece in
view is one), and 1.3 to 2.9 ms from the Duchy tier in. `Forest.find_at()`, which the party asks at
each step's end, tries every piece: 4 to 5 ms, once every 3.75 s of travel.

## Probing it

Run the scene in a window (`--fixed-fps 60 --disable-vsync` to time frames) from a `--script`
probe. The wheel is `camera._target_zoom = camera._min_zoom() * pow(1.25, steps)`; wait until
`camera.zoom.x` is there, the `Detail` node's `_stale` is false and nothing is fading. On that
node `_tier` is the tier (a `MapDetail.Tier`), `_shown[tier]` how far in what it brings is,
`_brings[tier]` those things, `_outright` the ones hidden outright, `_waits[tier]` how long it has
waited on its lines (under 0 when it is not); and for line `i` of `_lines`, `_line_tier[i]` is the
tier it shows from, `_wide_from[i]` the tier from which a line along something is wide, and
`_set_step[i]` against `_step` how far off this zoom's width it is. A line's width on the screen
is its `width * camera.zoom.x`: look only at lines in view (`_boxes[i]`), since the rest are left
behind on purpose. A settlement out of its tier, or out of view, has `is_processing()` and
`is_under_pointer()` false; `in_view` says which, `_awake` holds those working, and
`_wake_places(seen)` can be timed by calling it from the probe with the view moved a little each
time (`_seen_from()` gives the view's rectangle).

The forests: `_tier_of[map.get_node("Forests/Woods")]` is the tier a size group comes in at, and
`_outright` must not hold one (a polygon shown again is cut into triangles again).
`get_nodes_in_group(&"forests")` is every piece, and `Forest.find_at(tree, point)` the one at a
point in the map's own space (a clearing, a village, the sea: null). An encounter is probed
without walking: disconnect the squad menu from the party's `encountered` (it would open and stop
the map), connect a counter, then set `party.global_position` and call
`party._take_steps(party.step_length)`, one step a call. A piece edited by hand is tried with
`Geometry2D.triangulate_polygon(piece.polygon)`: empty, and Godot draws nothing of it. Seams show,
if anywhere, with the borders hidden (`Borders` and `BordersOverLakes` faded to nothing) all the
way in, as single pixels a shade lighter than the forest in a line: none did (2026-10-17).

## Decided with the user

The four tiers and their heights; bridges with the lesser roads, in the Duchy tier; no fifth,
closer tier, the villages and hamlets coming with the County tier; only the nine kingdoms'
capitals in the Realm tier. Then, once there were some 2,000 (2026-10-17): the villages at 100
miles and the hamlets at 50, a second step inside the County tier. And every border switched off
and on with `B`, on to begin with.

The forests (2026-10-17), each out of three choices: the wild amount, about half the land, at
each biome's share; battles met in them as in the old map's forest, 10% a step; a colour for each
kind; and the smaller coming in as the view closes in, as the lakes do, by size: 250, 50 and 10 km²
the bounds between the four groups, as the question gave them.

Without asking, for the forests: every rule `f1_forests.py` grows and clears them by (tree lines,
the dry and the cold country, what is bare, the clearings' reach and how it runs along valleys and
roads); the four kinds and the heights over which forests are conifer; the colours; woods under
0.5 km² dropped and clearings under 0.8 km² filled; a forest running on under the lakes; the
pieces cut by county and kind, named for their county, grouped by size and then by kingdom; the
clearings bridged rather than cut out; no piece of more than 500 points; the kinds' scenes
inheriting `Forest.tscn`; forests faded and never hidden by the tiers.

Without asking: no highways in the Realm tier; the rivers' and lakes' sizes for each tier; the
width rule's two numbers; a fade of 0.2 s; a tier waiting on its lines; settlements hidden
outright, and a hidden `Destination` stopping its `_process`, which the old map's village does as
well; the villages' lanes and the bridges on them and the Swamp's channels with the villages;
the hamlets' step as a tier in the code; settlements far from the view stopped and drawing
nothing; `R3` for the borders' switch on the gamepad, a node of its own for it, and the borders
going and coming at once rather than fading.

## Known gaps

- For the 0.2 s of a fade, lines of one colour that overlap (roads at a fork) show darker where
  they do, each being blended in by itself.
- While the zoom moves fast, lines in view are some steps behind (a step is 6% of a width; 7
  steps at the worst seen), and catch up within 0.6 s of it stopping. `points_per_frame` trades
  that against the frame's time.
- From the Duchy tier every lake shows, and at its far end the smallest pepper the lake country in
  the west. Lakes come by tier, not by their size on the screen.
- In the Kingdom tier a highway crosses a river with no bridge drawn, the bridges coming a tier
  later.
- Only the settlements under `Settlements` are kept from working while far off. A `Destination`
  anywhere else on the map would run its own `_process` whenever it shows.
- The scene is read once, as it opens: a node added, removed, moved or resized while the game
  runs is not followed, a settlement no more than a line.
- At the far end of the County tier (100 miles) over the Deciduous Forest close to 300
  settlements are in and round the view, a village every 70 pixels or so, and the lanes between
  them are a little over a pixel wide: busy, though no two icons touch.
- The tiers go by the view's height in miles, so in a window taller than the game's 720 the same
  tier has more pixels to a mile.
- The forests run on under the lakes, so where a small lake is out of its tier the forest shows
  where it is, and the party crossing a lake within a forest rolls that forest's odds. An island in
  a lake is drawn over the forests: a forest on one would not show (the one there is, 0.6 km² of
  marsh, has none).
- A forest's tier is the size of the whole forest when it was made: reshaped by hand, a piece keeps
  its group. Hand edits to the forests are lost when they are made again.
- 223 slivers under 0.05 km², where a forest's edge runs along a county's border, and one piece of
  0.09 km² that could not be cut into triangles were left out: gaps too small to see.
- `Forest.find_at()` tries all 2,459 pieces at every step, 4 to 5 ms; an index by squares, as the
  settlements have, would make it nothing.
- The open land is all one: fields, meadow, marsh, heath and bare rock alike are the land's white.
- The gallery forests of the Grassland and the Desert follow the drainage's streams too, which
  the map does not draw, so some ribbons of forest follow no water it shows.
- The see-through colours suit the white land; a land tinted later would change them.
