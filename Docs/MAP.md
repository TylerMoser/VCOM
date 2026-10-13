# The new map's level of detail

How `Scenes/Map.tscn` shows less far out and more close in, and holds its lines near a width on
the screen: `MapDetail` (`Scripts/WorldMap/MapDetail.gd`), the scene's `Detail` node. `CLAUDE.md`
keeps a summary; the rest of the new map (its nodes, its camera) is described there and in
`README.md`, "The new world map". A section named here that is not in this file (Gotchas,
Verification, Known gaps) is `CLAUDE.md`'s.

## How it works

**The view is in one of four tiers, by how tall it is in miles.** Each is named for what about
fills the window then, and adds to the one before it. Wheel steps are counted from all the way
out, in the game's 1280 by 720 window, where each height sits between two steps:

| Tier | View's height | Wheel steps | Brings |
|---|---|---|---|
| Realm | over 480 mi | 0 to 2 | The coast, the land, the kingdoms' borders and their 9 capitals, the 42 rivers at least 12 units wide, the 79 lakes at least 100 units across |
| Kingdom | 480 to 240 mi | 3 to 5 | The duchies' borders and their 35 capitals, the highways, 92 more rivers (at least 9 wide), 179 more lakes (at least 50 across) |
| Duchy | 240 to 100 mi | 6 to 9 | The counties' borders and their 176 capitals, the other roads, the bridges, every river and lake |
| County | under 100 mi | 10 to 16 | The villages and hamlets (none on the map yet) |

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
`Line2D` builds it again: 0.07 ms a line, 70 ms for the Duchy tier's. A group with no line under
it, which is each rank of settlement, also has `visible` set false once faded out: a `Destination`
out of sight is not under the pointer, and on `NOTIFICATION_VISIBILITY_CHANGED` it stops its own
`_process`, which costs 6 microseconds a frame for each one there is, on screen or off.

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

**Nothing in the scene as saved changes.** `MapDetail` is no tool script: the editor shows every
node, at the width it was given, and those widths are the ones the map has at 220 miles tall.

## What it costs

Measured in a window at 60 frames a second (an RTX 3060 laptop). A frame at rest takes about 1 ms
all the way out, 3 at the far end of the Duchy tier, where the most is drawn, and 2 all the way
in.

- A wheel step: the worst frame 6 to 8 ms; the steps into and through the Duchy tier average 5
  to 6 ms a frame while they last.
- The right stick from one end to the other (3.2 s): the worst frame 9 ms, 5 on average. Up to
  700 lines are behind at once, by 5 steps at most going in and 7 coming out, and all are right
  0.6 s after it stops. A tier waits up to 0.3 s on its lines.
- Panning in the Duchy tier: no line in view is ever behind.

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
behind on purpose. A settlement out of its tier has `is_processing()` and `is_under_pointer()`
false.

## Decided with the user

The four tiers and their heights; bridges with the lesser roads, in the Duchy tier; no fifth,
closer tier, the villages and hamlets coming with the County tier; only the nine kingdoms'
capitals in the Realm tier.

Without asking: no highways in the Realm tier; the rivers' and lakes' sizes for each tier; the
width rule's two numbers; a fade of 0.2 s; a tier waiting on its lines; settlements hidden
outright, and a hidden `Destination` stopping its `_process`, which the old map's village does as
well.

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
- A shown `Destination` still runs its own `_process`, wherever on the map it is: thousands of
  hamlets in the County tier would cost a frame 6 microseconds each.
- The scene is read once, as it opens: a node added, removed or resized while the game runs is
  not followed.
- The tiers go by the view's height in miles, so in a window taller than the game's 720 the same
  tier has more pixels to a mile.
