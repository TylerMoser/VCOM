# The new world map

`Scenes/Map.tscn`, the island the campaign is moving to: how its scene is laid out, its streams,
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
nodes), `Borders`, `Lakes`, `Streams` (a `Line2D` a stream, under a `Kingdom` node), `Rivers`,
`BordersOverLakes`, `Roads`, `Bridges`, `Settlements`, `Party`, `Clock` (a `MapClock`), `Camera` (a
`MapCamera`, so the scene runs by itself), `MapReticle`, `VillageMenu`, `SquadMenu`, `GameOver`,
`Detail`.

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
capitals' so that towns and cities draw over them, but there are none on the map yet: one is added
by instancing its scene under its group. `Village.tscn` is the old map's village as well, which
keeps its 32 by setting `icon_height` on its own node in `WorldMap.tscn`.

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
step is still every 5 km, by distance (their call), about eight a day. The old map's party has no
clock and keeps `travel_speed`.

One settlement has something in it, at the user's request: county 115's capital has the old
village's hiring board and market, the same two `.tres` and not copies (my call: a character stays
on one board), and the scene's `VillageMenu` opens them as on the old map, on a left click once the
party is in the town. A town shows from the Duchy tier, so it is sent to and entered only that far
in. `MapReticle`, the gamepad's ring and prompts, is the old map's as well, and so are `SquadMenu`
and `GameOver`, which nothing here sets off yet: no forest sets the party upon.

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
the river that shows the border's colour on both banks; a stream that joins another, which ends on
one of the other's points. A hand edit has to move the copies too. **Never run
`MapCreation/Scripts/scene/m2_scene.gd` over it unasked: it writes the scene afresh, and every
change made by hand is lost.** `MapCreation/Scripts/README.md`, step 11, has how it was made and
checked, and step 13 how the streams were.

## Streams

**The streams are the flowing water too small to be a river**, added on 2026-10-17 at the user's
request: 9,869 of them, 88,900 km, six times the rivers' length, in `Streams`, a `Line2D` each
(`Stream00001`, numbered by the water they carry, as the rivers are) under the kingdom most of each
lies in (`Streams/Kingdom6`). They lie between `Lakes` and `Rivers`, so they are drawn over the
borders and the lakes and under the rivers: a stream ends on the line of the river or stream it
joins, inside the lake it runs into, or 3 px of the pictures into the coast's line. They are in
the source data as lines too, `MapCreation/SourceData/Streams.json`, and on no picture.

**They follow the land.** They were worked out on the drainage the rivers and lakes were drawn
from (`SourceData/DrainageDirection.png` and `DrainageFlow.png`, cells of 670 m), so they run down
the very heights the rivers do, and joined as the rivers are: at each meeting the stream carrying
more goes on. Each is its course smoothed and then made to wander a little, much where its bed is
nearly level, as the rivers were, and never more than three tenths of the way to other water.

**How many, by country, is the user's choice of a medium density**, worked out by me from the
run-off the land was given: a stream begins where the ground it gathers (km²) times the water it
carries (m³/s) reaches 5.3, what 20 km² of the Deciduous Forest gives, and where it carries at
least 0.2 m³/s. So wet country begins its streams on less ground: about 9 km² in the Evergreen
Rainforest, 13 in the Temperate Mountains, 18 in the Tundra, 20 in the Deciduous Forest, 105 in the
Grassland, and in the Desert its own rain makes none. Once begun a stream runs on until it meets
water; in the Desert and the Grassland, where water is lost to the ground, only while it still
carries 0.1 m³/s (none dries up before it meets water). A stream nothing joins, under 1.5 km on
land, is left out. The view all the way in (25 by 44 miles) holds about this many:

| Kingdom | Streams | km | km of stream to a km² | In a view all the way in |
|---|---:|---:|---:|---:|
| 1 Tundra Mountains | 1,254 | 10,969 | 0.14 | 47 |
| 2 Volcanic Mountains | 974 | 11,237 | 0.15 | 36 |
| 3 Temperate Mountains | 1,475 | 12,994 | 0.17 | 55 |
| 4 Desert | 75 | 1,749 | 0.02 | 3 |
| 5 Grassland | 262 | 4,057 | 0.05 | 10 |
| 6 Evergreen Temperate Rainforest | 1,954 | 14,713 | 0.19 | 73 |
| 7 Swamp | 1,110 | 9,776 | 0.13 | 41 |
| 8 Deciduous Forest | 1,066 | 10,582 | 0.14 | 40 |
| 9 Tropical Rainforest | 1,699 | 12,786 | 0.17 | 63 |

**They join the lakes to the rivers.** Every lake that touches no river and has water leaving it
has its outlet drawn, down to the river, lake or sea it reaches (in dry country while it carries
0.1 m³/s); one whose water runs at once into a river, another lake or a stream already passing is
given a short line from its shore to that. Before the streams 150 of the 700 lakes touched a
river; now 665 touch water. The 35 that touch none are the six crater lakes, with no outlet, and
29 lakes of the Grassland that let out 0.03 m³/s at the most: dry country, and the user chose
flowing water only.

**A stream is narrower than the narrowest river**: `width_px = 0.7 + 0.396 * flow ** 0.36` of the
pictures' pixels, a quarter more in the Swamp and the Tropical Rainforest as the rivers there,
0.75 to 1.95 px (2.5 to 6.5 units) against a river's 2 at the least; 1.1 to 2.9 screen pixels all
the way in, and 0.7 to 1.8 where streams first show. A stream's node width is its widest; one that
widens by more than 0.3 px has a width curve (1,452 do), the rest are drawn at their widest. They
are the rivers' blue. Their points are thinned to within 0.08 px of the line and given points
where they bend so that none turns more than 10 degrees at one point (the rivers' rule is 6): it
cannot be seen on lines one or two pixels wide, and halves their points, 120,000 in all.

**No line hides another.** A stream is drawn over the borders, as water is, and is narrower than
any of them, so it never hides one. Where one runs along a border for 24 px of the pictures or
more, it is put on the border's own line and a line of the border's colour is laid under it, as
wide as the stream and the border on both sides of it: eight such stretches, 53 km, named as the
rivers' (`Counties210And211AlongStream00335`), at the end of their rank's group under `Borders`.
Roads are drawn over streams: where a road runs along one for 12 px or more, the stream is moved
off beside it, clear of the road as both are drawn where streams first show (366 km of streams).

**They are made by program and spliced in.** `MapCreation/Scripts/streams/` works them out
(`t1_streams.py` into `Streams.json`), makes them into nodes with the scene's own builder
(`t2_shapes.py`, then `m2_scene.gd` with `streams`, which makes only them) and splices those into
the scene as it is (`t3_splice.py`), touching nothing else in it; step 13 of that folder's README.
The builder makes the same nodes when it makes the whole scene (`m1_shapes.py` reads
`Streams.json`), so a scene made afresh has them too. A stream can be changed by hand like any
line, but nothing goes back to `Streams.json`: spliced again (`--replace`), every stream and its
lines along borders are made afresh, and a hand edit to one is lost.

**They show from the County tier**, all of them as the view crosses 100 miles tall (the user's
call: not the larger first), faded in with the tier as the villages are, and their widths follow
the zoom with every other line's. A stream that reaches the sea ends in the coast's line, as a
river does, its end moved with its width (below).

## Level of detail

**The view is in one of four tiers, by how tall it is in miles.** Each is named for what about
fills the window then, and adds to the one before it. Wheel steps are counted from all the way
out, in the game's 1280 by 720 window, where each height sits between two steps:

| Tier | View's height | Wheel steps | Brings |
|---|---|---|---|
| Realm | over 480 mi | 0 to 2 | The coast, the land, the kingdoms' borders and their 9 capitals, the 42 rivers at least 12 units wide, the 79 lakes at least 100 units across |
| Kingdom | 480 to 240 mi | 3 to 5 | The duchies' borders and their 35 capitals, the highways, 92 more rivers (at least 9 wide), 179 more lakes (at least 50 across) |
| Duchy | 240 to 100 mi | 6 to 9 | The counties' borders and their 176 capitals, the other roads, the bridges, every river and lake |
| County | under 100 mi | 10 to 16 | The 9,869 streams, and the villages and hamlets (none on the map yet) |

`MapDetail._process()` reads the height off the viewport's canvas transform, as a `Destination`
reads its scale, so it follows whatever camera the scene has. A tier's groups are in
`MapDetail.SHOWN_FROM`, by their place under the map; the rivers and lakes are sorted one by one
as the scene opens, a river by its `width` (its widest, at the mouth) and a lake by how far across
a circle of its area is, and an island in a lake (`Lake001Island1`) goes with its lake. Anything
neither named nor sorted shows always. A tier holds until the view is `boundary_slack` (5%) past
its height, so a view resting on one does not flicker.

**What a tier brings is faded, and only the settlements are hidden.** Each tier has one amount,
0 to 1, moved over `fade_time` (0.2 s) and multiplied into the `modulate` alpha its things have in
the scene. At nothing the renderer skips them, at no cost either way, where showing a hidden
`Line2D` builds it again: 0.07 ms a line, 70 ms for the Duchy tier's, and some 700 for the
streams. A group with no line under it, which is each rank of settlement, also has `visible` set
false once faded out: a `Destination` out of sight is not under the pointer, and on
`NOTIFICATION_VISIBILITY_CHANGED` it stops its own `_process`, which costs 6 microseconds a frame
for each one there is, on screen or off.

**Every line's width is its node's times one factor,** `(view's height / true_width_view_miles)
^ (1 - width_growth)`: at 220 miles tall a line is as wide as the scene says, and from there its
width on the screen follows only 0.36 of the zoom. A kingdom's border is 2.2 px all the way out
and 7.5 all the way in (0.9 and 30 left alone), a lesser road 1.4 px where it first shows and 3.1
all the way in (12.5 left alone), the coast 3 to 10. It is one factor for all of them because some
are sized to others (below), and it scales a river's `width_curve` with it.

**Widths are set a few lines a frame, the furthest off first.** Setting a `Line2D`'s width builds
it again as it is next drawn: about half a microsecond a point and 21 microseconds a line,
whatever its length (Godot 4.7, an RTX 3060 laptop). So the factor moves in steps of `width_step`
(1.06), and `_refresh_widths()` sets only lines that show at this tier and whose box reaches the
view (and `VIEW_MARGIN` round it), at most `points_per_frame` (4,000) points' worth a frame, each
line counted as `LINE_POINTS` (40) points more than it has: first those more than `FAR_STEPS` (8)
steps off, then those more than `READY_STEPS` (3), then the rest. Without the count of lines, a
frame could be given 650 short streams and take 16 ms. A line out of view, or out of its tier,
keeps the width it had. The first frame sets every line, since all of them are built then anyway:
those that show at the width for this zoom, and those of a tier still to come at the width they
will want as it comes in, so the County tier's streams are ready the moment it does. A tier's
lines can still be off when it comes in again, last set at some other zoom: it waits (`_waits`),
its lines being the furthest off and so set first, and starts to fade in once those in view are
within `READY_STEPS`, or after `MOST_WAIT` (0.5 s) whatever they are.

**A frame looks only at the lines near the view.** As the scene opens, each tier's lines are
sorted into squares of `LINE_SQUARE` (512 units) by the squares their boxes reach (`_squares`), and
`_lines_near()` takes, each line once, those of the tiers showing or still fading out whose
squares the view reaches, found again only when those squares or tiers change. With the streams
there are 11,614 lines, and going through all of them each frame the view moved took 4.4 ms; the
lines near the view take 0.07 ms all the way in (some 450 of them) and 0.45 ms where the County
tier begins (some 4,000).

**A border's line along something is a plain border while that is hidden.** A line named
`...AlongRiver173`, `...AlongLake085`, `...AlongRoad093` or `...AlongStream00335` lies under the
river, shore, road or stream its border follows, as wide as that and the border on both sides.
While the river, lake, road or stream does not show at the view's tier, the line is given the plain
border's width (the middle one of its group's lines that follow nothing: 17, 10 or 7) and no width
curve, so no river has to stay for a border's sake. A river or lake is found by the name
(`Rivers/River173`), a stream by its name among the streams (`Streams/Kingdom3/Stream00335`); a
road's number is in no node's name, so it is the road that shares the line's middle point. Of the
266 such lines, 53 are narrowed at some tier.

**A border's, a river's or a stream's end in the sea moves with its width.** Where one reaches the
sea it ends past the land's edge, in the coast's black line: about 10 units out, the coast's line
being 23 wide outside the land. Left there, the end came out of the far side of the coast's line
once that narrowed: all the way in the coast's line is under 6 units, and the ends showed 4 units
(8 pixels) out over the sea. So `_gather_sea_ends()` finds, as the scene opens, every line under
`Borders`, `Rivers` or `Streams` (`ENDS_IN_COAST`) that, followed back from an end, crosses a
coast's line within the coast's width outside the land (890 lines), and `_set_width()` moves the
points out there as it sets the width: how far each is past the crossing is scaled by the widths'
factor. The end is then as deep in the coast's line at every zoom as the scene has it, and at 220
miles tall the points are the scene's. It costs nothing more, the width having built the line
again anyway; finding them takes about 75 ms as the scene opens, an end with no coast within a
square of `COAST_CELL` of it being passed over at once. Roads and bridges are left out: the road
over the sea to the island town crosses the land's edge and ends on land.

**Nothing in the scene as saved changes.** `MapDetail` is no tool script: the editor shows every
node, at the width it was given, and those widths are the ones the map has at 220 miles tall.

## What it costs

Measured in a window at 60 frames a second with vsync off (an RTX 3060 laptop), on 2026-10-17 with
the streams in, with the Godot editor open beside it; before the streams in brackets.

- Opening the scene: 1.1 s to load the file (0.7) and 1.7 s to the second frame (0.7), most of the
  difference the streams' 9,869 lines being built for the first time.
- A frame at rest all the way in: 3.3 ms (2.4); where the County tier begins, 4.5 ms (2.6).
- A wheel step: 3 to 6 ms a frame on average out of the County tier, as before; 4.4 to 7.2 ms in
  it (2.9 to 5.3), the worst frame under 10 ms. Frames of 20 to 30 ms came now and then in every
  tier, at rest too, with nothing to set: the machine, not the map.
- Panning all the way in: 3.6 ms a frame on average (2.5), 7 at the worst.
- Not measured again: the right stick from one end to the other, which took 5 ms a frame on
  average and caught up 0.6 s after it stopped before the streams.

## Probing it

Run the scene in a window (`--fixed-fps 60 --disable-vsync` to time frames) from a `--script`
probe. The wheel is `camera._target_zoom = camera._min_zoom() * pow(1.25, steps)`; wait until
`camera.zoom.x` is there, the `Detail` node's `_stale` is false and nothing is fading. On that
node `_tier` is the tier (a `MapDetail.Tier`), `_shown[tier]` how far in what it brings is,
`_brings[tier]` those things, `_outright` the ones hidden outright, `_waits[tier]` how long it has
waited on its lines (under 0 when it is not); and for line `i` of `_lines`, `_line_tier[i]` is the
tier it shows from, `_wide_from[i]` the tier from which a line along something is wide, and
`_set_step[i]` against `_step` how far off this zoom's width it is. `_lines_near(seen)` gives the
lines a frame looks at for a view `seen` in the map's own space. A line's width on the screen is
its `width * camera.zoom.x`: look only at lines in view (`_boxes[i]`), since the rest are left
behind on purpose. A settlement out of its tier has `is_processing()` and `is_under_pointer()`
false. To time the node's own work, turn its processing off and call `_process(delta)` from the
probe each frame between two `Time.get_ticks_usec()`; the rebuilding of the lines it set happens
as they are drawn, later in the frame.

The streams are looked at by `MapCreation/Scripts/streams/t1_streams.py` with `look` (pictures of
views as the game shows them all the way in), and checked as it runs: every stream ends on water,
none crosses another, and how much still runs under a road.

## Decided with the user

The four tiers and their heights; bridges with the lesser roads, in the Duchy tier; no fifth,
closer tier, the villages and hamlets coming with the County tier; only the nine kingdoms'
capitals in the Realm tier.

For the streams (2026-10-17): streams as a new kind of water, following the land, joining the
lakes to the rivers and spreading up from the rivers into their watersheds, as real as can be;
as many as suits each kingdom's biome, for a map this size; at least whatever Google Maps shows
with a view 25 miles tall; shown in the County tier only, all of them from 100 miles; a medium
density, of those put to them; flowing water only, no dry washes; and in `Map.tscn` itself,
grouped by kingdom, not a scene of their own.

Without asking: no highways in the Realm tier; the rivers' and lakes' sizes for each tier; the
width rule's two numbers; a fade of 0.2 s; a tier waiting on its lines; settlements hidden
outright, and a hidden `Destination` stopping its `_process`, which the old map's village does as
well. For the streams: the rule a stream begins by (ground times water, from 20 km² of the
Deciduous Forest) and what "flowing" is (0.2 m³/s to begin, 0.1 to go on in dry country); the
lakes' outlets drawn whatever they carry in wet country, and the short lines from a lake to water
just below it; streams under 1.5 km with nothing joining them left out; the width rule and the
rivers' blue; a stream on a border's line with the border's colour under it, and moved off a road
that runs along it; 10 degrees, not 6, between a stream's points; width curves only where a
stream widens by 0.3 px; streams on the islands as well; the lines found by squares, the cost of a line
counted in the budget, and the County tier's lines set at the first frame to the width they will
want.

## Known gaps

- For the 0.2 s of a fade, lines of one colour that overlap (roads at a fork) show darker where
  they do, each being blended in by itself.
- While the zoom moves fast, lines in view are some steps behind (a step is 6% of a width; 7
  steps at the worst seen before the streams), and catch up within a second of it stopping.
  `points_per_frame` trades that against the frame's time.
- From the Duchy tier every lake shows, and at its far end the smallest pepper the lake country in
  the west. Lakes come by tier, not by their size on the screen.
- In the Kingdom tier a highway crosses a river with no bridge drawn, the bridges coming a tier
  later.
- A shown `Destination` still runs its own `_process`, wherever on the map it is: thousands of
  hamlets in the County tier would cost a frame 6 microseconds each.
- The scene is read once, as it opens: a node added, removed or resized while the game runs is
  not followed.
- The tiers go by the view's height in miles, so in a window taller than the game's 720 the same
  tier has more pixels to a mile.
- The streams' density is my estimate of what Google Maps shows with a view 25 miles tall (about
  its zoom 11 or 12, by the screen); it was not set beside Google Maps itself.
- Where the County tier begins, 100 miles tall, the streams are hairlines under two pixels, a fine
  web over the wet kingdoms: all come in at once, as chosen, where Google adds them zoom by zoom.
- Streams branch as the rivers do and never part again: no braided channels, no bayous joining two
  waters, no deltas, even in the Swamp. They follow cells of 670 m smoothed, so on an even slope
  many run side by side (the Volcanic Mountains' plateau most of all), and none is narrower than a
  valley of that size.
- The 341 pools of the drainage too small to be drawn are still not drawn, and a stream passes
  through one as if it were land. 35 lakes touch no water (above).
- One stream, `Stream00387` in the Volcanic Mountains, still runs 16 px under the road
  `Road016ToFork231` just before it meets its river, where its end is held on the river.
- The scene is 12.9 MB, from 8, and takes about 2.8 s to open, from 1.4; the editor has 9,900 more
  nodes to show.
