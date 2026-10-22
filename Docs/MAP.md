# The new world map

`Scenes/Map.tscn`, the island the campaign is moving to: how its scene is laid out, its look, its
forests, and its level of detail, `MapDetail` (`Scripts/WorldMap/MapDetail.gd`, the scene's `Detail`
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
half under the land); a border that follows a river, the river, and the `...AlongRiver` band under
the river that shows the border's pattern on both banks; a county and the pieces of forest along its
border or its coast. A hand edit has to move the copies too. `MapCreation/Scripts/scene/m2_scene.gd`
made the scene, and can no longer: its whole-scene part was taken out on 2026-10-18, when the map
was given its look, since run again it would have written the scene afresh in the old look over
every change made by hand (git keeps it, at commit d8b5ec7). It writes only the villages and the
forests alone now, in the map's look, for their splices, and refuses to write over
`Scenes/Map.tscn`. `MapCreation/Scripts/README.md`, step 11, has how the scene was made and checked,
step 13 how the villages were placed, and step 14 how the forests were made.

## Its look

**Every kind of line says what it is without its colour**, chosen by the user on 2026-10-18 from
the proposals in `MapStyles/` (its README has the reasons, and pictures of the look as it is,
`00-current-look.png` and `91-current-look-close-in.png`): 02's patterned borders, 04's cased
roads, 05's one water in a brighter blue than proposed ("a bit closer to the current ocean color"),
and 10's reweighting where it did not conflict with those, which left it the forests' paler fill
(its widths for the borders, roads and coast gave way to theirs). Before, every line was a plain
solid one, told from the rest by its colour alone.

**On 2026-10-19 the user took three more**, from 10, 14 and 19 revisited on this look with variants
(`MapStyles/README.md`, "Revisited on the applied look", measured by
`MapStyles/harness/tools/line_weights.py`, which gives every line's weight on the screen): 10b,
roads that keep their weight close in (a casing of half the road
from 3 px across, and the roads and lanes a little wider); 14b, borders that lead far out and give
way close in ([Level of detail](#level-of-detail)); and 19a, the county borders with the County
tier. With them a road outweighs every border wherever roads show.

**Later that day the open land took its biome's colour**: 12b, the whisper, from the variants of
proposal 12 explored in `MapStyles/12-biome-ground-colours/`, 12's pale palette at 40% of its
strength, so that the biome is a hint under everything and every line keeps nearly all its contrast.
The user means to tune the colours further, and asked for each biome's colour and intensity to be
easy to change: they are on one material (below, "The land takes its biome's colour").

**A line's look is its kind's material.** `Scripts/WorldMap/MapLine.gdshader` draws a `Line2D` as
a map symbol: in its own colour with a darker casing at both edges, or dashed, dotted or
dash-dotted, every length in widths of the line, so that a pattern scales with the width MapDetail
sets. Each kind has one `ShaderMaterial` in `Resources/MapLines/`, shared by all its lines, so a
change there (its Shader Parameters, in the inspector) changes every line of the kind, in the editor
too. A line drawn by it needs three things: its kind's `material`; `texture_mode` Tile, which is
what gives a `Line2D` UVs (it needs no texture); and its colour in `default_color` at alpha 1 (the
fill, or a border's ink), so that the alpha reaching the shader is only the fading MapDetail and
BorderSwitch do. **To draw a new line by hand, duplicate one of its kind** (Ctrl+D), which carries
all three and its width.

| Lines | Material | Width | Colour | Drawn as |
|---|---|---|---|---|
| `Borders/Kingdoms`, `BordersOverLakes/Kingdoms` | `KingdomBorder` | 12 | Ink, (0.25, 0.2, 0.31) | Dashes of 3.2 widths, a dot 0.85 across after each, 1.0 after the dash and 0.9 before the next |
| The same under `Duchies` | `DuchyBorder` | 8 | Ink | Dashes of 2.4 with round ends, gaps of 1.3 |
| The same under `Counties` | `CountyBorder` | 6 | Ink | Dots 0.85 across, 2.3 apart: the material's `gap` of 1.15 falls on both sides of each dot |
| A border's band along a river or a road | `KingdomBorderBand`, `DuchyBorderBand`, `CountyBorderBand` | The river's or road's and a border's | Ink | Its rank's pattern along both banks |
| `Roads/Highways` | `Highway` | 20 | Amber #ffc451 | Edges #b5761a, 0.28 of the half-width each; solid #e09a2a under 4 px across |
| `Roads/Roads` | `Road` | 16 | Cream #fffaf0 | Edges #9c8f7d, 0.5; solid #a3958a under 3 px |
| `Roads/Lanes` | `Lane` | 8 | White | Edges #b5aa9a, 0.34; solid #b8ad9d under 5 px |
| `Bridges` | `Bridge` | 29 on a highway, 23.2 on a road | Its road's fill | Parapets #4b4038, 0.42; solid #4b4038 under 3 px |
| `Bridges/Lanes` | `LaneBridge` | 11.6 | White | Parapets #4b4038, 0.45; solid under 3 px |

The roads were 14 wide, their casing 0.3 from 4.5 px, the lanes 7, until 10b (2026-10-19): a road's
cream fill is all but the land's white, so once its casing showed it was two thin edges where it had
been a solid line, and it grew *lighter* closing in, all the way in no heavier than a lane. With half
of it casing, from 3 px, it is cased wherever it is more than a hairline and only grows heavier. A
lane is never cased: 3.6 px across at the most, under its 5.

A rank of border is see-through by its groups' alpha, on `Borders/<rank>` and
`BordersOverLakes/<rank>` alike: 0.85, 0.7 and 0.5, which MapDetail fades by the tier under that and
BorderSwitch over it; MapDetail also makes the kingdoms' and duchies' fainter closing in ([Level of
detail](#level-of-detail)). The shader works out a road's width on the screen from its own UVs, so a road
goes solid as it narrows with no help from MapDetail.

**A border along a river or a road is a band under it, patterned on both banks.** Its
`...AlongRiver` or `...AlongRoad` line lies under the river or road as before, as wide as that plus
a plain border (a river's band keeps the river's width curve), so the border shows half its width
on either bank and a river is never under a border, as the user asked of the map from the start.
The band's material is its rank's pattern with every length shortened by how much wider than a
plain border the rank's middle band under a river is (x0.553, x0.398 and x0.361 for kingdoms,
duchies and counties), and `banks` on, which draws the dots and the dashes' ends square, across the
whole width: a round dot under a river's middle would be hidden whole. 02 itself drew these borders
on the water, a plain border over the river; on a thin river its ink hid the river, so the bands
were kept (my call, in the balancing). A border along a lake's shore is drawn over it, as 02 had
it: its `...AlongLake` line, a plain border with no width curve, is in `BordersOverLakes/<rank>` (40,
moved there from `Borders` on 2026-10-18), where it shows whole across the shore and hides nothing,
a lake being an area. The seven bands along roads were widened by what their road gained, the five
along roads (not highways) by 2 more with 10b.

**The water is one family of blue.** The sea and the lakes #a4ddfd; the rivers and channels a shade
deeper, #6dc2f3; the coast a thin shoreline, #68aad7: each `CoastOfCounty...` line is 8 units wide,
centred on the land's edge with the land over its inner half, so 4 show (the black line was 46, 23
showing). The island in a lake is land, and takes its county's ground (below). The blues are 05's (#a6d2f1, #78b6e6 and
#6f9fca) moved toward the sea the map had, (0.71, 0.92, 1): in OKLCH 0.4 of the way in lightness and
hue, with 15% more chroma, keeping 05's steps from water to river to shore.

**The ends in the sea were moved in with the coast.** A border or a river that reaches the sea ran
on about 10 units past the land's edge, into the black line; over a 4-unit shoreline the end would
have lain out over the sea. The points out there, on 138 lines, were moved toward where the line
crosses the land's edge, to 0.16 of their distance (about 1.6 units out, 3.7 at the most), and the
five such ends that were round made square, so nothing reaches past the shoreline. MapDetail finds
and scales them as before ([Level of detail](#level-of-detail)). A line given an end in the sea by
hand should end inside the shoreline, square, or MapDetail will not find it: it looks back from an
end only as far as the coast's line reaches outside the land.

**The forests are a little paler**: each kind's colour at 0.38 alpha, from 0.5, on its scene's root
(`Scenes/ConiferForest.tscn` and the other three), which every piece takes.

**The land takes its biome's colour, from one material.** Every county
(`Land/KingdomN/DuchyNN/County...`, its islands in the sea with it) and the island in a lake share
`Resources/MapGround.tres`, drawn by `Scripts/WorldMap/MapGround.gdshader`, which mixes the
polygon's own colour, the land's white, toward its biome's. **To change a biome's colour, or how
strongly it shows, select `Resources/MapGround.tres` and change its Shader Parameters**: each biome
is a group of two, its Color and its Intensity, and the editor shows a change at once over the whole
map, as the game will. A colour is its biome's land at intensity 1; below that the white shows
through, so at 0.4, every biome's now, the land is 40% of the way from white to the colour. Overall
Intensity, above the nine, scales them all at once: 1 leaves each as set, 0 turns the ground off,
and over 1 strengthens them all, none past its colour. The colours are kept on the material alone:
the shader's own defaults are no tint, so a revert arrow in the inspector turns a biome white.

Which biome a polygon is in is set on the polygon: `biome`, under Instance Shader Parameters in its
inspector, a list of the nine. A county's is its kingdom's, a kingdom being a biome (`Land/KingdomN`
is biome N, named in its node's description and metadata). A county duplicated by hand keeps its
biome and the material; one moved to another kingdom needs its biome set, and a polygon of land
drawn afresh needs both. `Lakes/Lake001Island1`, the one island in a lake, lies wholly in county 167
and is the Swamp's.

| Biome | Kingdom | Color | Intensity | The land on the screen |
|---|---|---|---|---|
| Tundra Mountains | 1 | #e9ecef | 0.4 | #f6f7f9 |
| Volcanic Mountains / Ruins | 2 | #e3dcd5 | 0.4 | #f4f1ee |
| Temperate Mountains | 3 | #e5e8dc | 0.4 | #f5f6f1 |
| Desert | 4 | #f4e4c4 | 0.4 | #fbf4e7 |
| Grassland | 5 | #eef0cf | 0.4 | #f8f9ec |
| Evergreen Temperate Rainforest | 6 | #dcebd8 | 0.4 | #f1f7ef |
| Swamp | 7 | #e2e6cf | 0.4 | #f3f5ec |
| Deciduous Forest | 8 | #e6efd6 | 0.4 | #f5f9ef |
| Tropical Rainforest | 9 | #d9ecce | 0.4 | #f0f7eb |

The colours are proposal 12's own, and the forests were left as they were, as 12b has them; under a
forest the ground shows through its see-through fill, so a forest takes a little of its biome's
colour too. The shader picks a polygon's colour and intensity once a vertex, its biome being the
same all over it, and only mixes them in a pixel. **Keep it so**: picked in each pixel, from a table
of the nine made in every pixel, the ground tripled the map's GPU time (0.32 to 0.90 ms at 200 miles
tall). As it is it costs nothing measurable ([What it costs](#what-it-costs)). It was applied as a
text edit of the scene, the material and the biome on each of the 234 polygons, and the scene then
drew the same as the harness's picture of 12b, but for a shade on 22 pixels.
`MapStyles/12-biome-ground-colours/README.md` has 12's other variants, several of which would build
on this material: a palette is only its nine colours and intensities.

It costs nothing measurable: 0.29, 0.22 and 0.13 ms of GPU a frame at 180, 80 and 30 miles tall,
before and after, with the same draw calls; the scene grew by 91 KB, to 13.6 MB. It was applied as
a text edit of the scene (every one of its 2,597 lines given new values, 40 of them moved; the sea and
701 lakes recoloured; no node added), and the scene then drawn the same as the harness's prototype of
it to within a dozen pixels a view. `MapStyles/README.md`, "The problem, measured", has the values
it replaced.

**Nothing writes the old look now.** The scene generator's whole-scene part, which did, was taken
out as the look was applied, and what is left of it draws the lanes, the bridges on them and the
channels in the map's look, materials and all, so the villages' splice (`v3_splice.py --replace`)
puts them back as they are: spliced afresh into a copy of the scene, they came out the same as the
scene's to the last property (2,805 nodes, 2026-10-18). The forests' splice keeps the kinds'
scenes, and so their look. Neither touches the land, so the ground stays: each keeps every resource
it does not own, `MapGround.tres` among them, and `f2_shapes.py` reads a county's outline past the
material's lines in front of it. The harness in `MapStyles/` only draws pictures, and with `BEFORE=1` it
draws a proposal on a copy of the scene as it was before, never on the scene. The streams on the
`map2` branch were made in the rivers' old blue, by a streams part of `m2_scene.gd` this branch's
never had: merged in, that part wants joining to what is left of the program here, and the streams
the rivers' colour.

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
  map's forest, so its odds and its battle) and sets only its colour, see-through at 0.38 alpha (half,
  until the look of 2026-10-18) over the land's pale ground: `ConiferForest.tscn` a cool blue-green, in
  the Tundra and the Volcanic Mountains, the Evergreen Rainforest and high up in the other kingdoms
  (over 1,000 m in the Temperate Mountains, 900 in the Desert and the Grassland, 1,100 in the
  Deciduous Forest, 600 in the Swamp); `BroadleafForest.tscn` a soft yellow-green, below those
  heights; `SwampForest.tscn` an olive green, in the Swamp's own low country; and
  `TropicalForest.tscn` a deep green. A colour is changed for every piece of its kind on its scene's
  root.
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
| Duchy | 240 to 100 mi | 6 to 9 | The counties' 176 capitals, the other roads, the bridges, every river and lake, the 203 forests of 10 to 50 km² |
| County | under 100 mi | 10 to 16 | The counties' borders, the villages, their lanes and the bridges on them, the Swamp's channels, the 806 woods under 10 km²; and in a second step, under 50 mi (steps 13 to 16), the hamlets |

The county borders came with the Duchy tier until 2026-10-19 (19a): there they were some 80 faint
lines of dots in every view, a tenth of any other line's weight, and the Duchy tier is the busiest
for lines.

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
width on the screen follows only 0.36 of the zoom. A lesser road is 3.2 px where it first shows and
7.1 all the way in (29 left alone), the coast's shoreline 0.5 to 1.7; by this rule alone a kingdom's
border would be 1.5 px all the way out and 5.3 all the way in (0.6 and 21 left alone), which is why
the borders have a rule of their own on top of it. It is one factor for all of them because some
are sized to others (below), and it scales a river's `width_curve` with it.

**The borders lead far out and give way close in** (14b, 2026-10-19). Far out the map is about the
realm, close in about the road ahead, and by the one factor alone the kingdom border was faint where
it mattered most and the darkest line on the map where it mattered least. So a border's width is
also times `(view's height / true_width_view_miles) ^ border_growth` (0.3), taken at the height the
present width step stands for (`_step_miles()`), so that every border set at one step takes the same
share (`_border_share`). At 220 miles a border is as wide as its node says, as every line is; all
the way out 1.49 times that and all the way in 0.52 times: a kingdom's border 2.3 px across all the
way out and 2.8 all the way in, a duchy's 1.9 and a county's 1.4 all the way in. A band along a river
or a road takes the share on its border's part alone (its plain width, `_plain`), the river's or
road's part staying that one's width. And the kingdoms' and duchies' groups grow fainter closing in:
whole at `border_whole_view_miles` (240) and over, down to `kingdom_border_faintest` (0.55) and
`duchy_border_faintest` (0.7) of their alpha at `border_faintest_view_miles` (25), by the logarithm
of the height between, so that each wheel step takes off about as much (`_faint_at()`,
`_show_faint()`). That share multiplies in where the tiers fade the groups, and BorderSwitch fades
their parents over both, so `B` still hides them at any zoom and they come back as faint as the zoom
has them. The counties keep theirs (`county_border_faintest` 1), faint already. All of it is set on
the `Detail` node, and `border_growth` 0 with the three shares at 1 is the one factor alone.

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

**A border's band along something is a plain border while that is hidden.** A line named
`...AlongRiver173` or `...AlongRoad093` lies under the river or road its border follows, as wide as
that and a border ([Its look](#its-look)). While the river or road does not show at the view's
tier, the line is given the plain border's width (the middle one of its group's lines that follow
nothing: 12, 8 or 6) and no width curve, so no river has to stay for a border's sake. A river is
found by the name (`Rivers/River173`); a road's number is in no node's name, so it is the road
that shares the line's middle point. Of the 218 bands, 37 are narrowed at some tier. A
`...AlongLake085` line, in `BordersOverLakes`, is found by its lake (`Lakes/Lake085`) the same way,
but is a plain border's width either way.

**A border's or a river's end in the sea moves with its width.** Where one reaches the sea it
ends past the land's edge, inside the coast's line: about 1.6 units out, the shoreline being 4
wide outside the land (until 2026-10-18, 10 units out in a black line 23 wide: [Its
look](#its-look)). Left there, the end would come out of the far side of the coast's line once that
narrowed: all the way in the shoreline is 1 unit outside the land. (In the black line's day the
ends showed 4 units, 8 pixels, out over the sea.) So `_gather_sea_ends()` finds, as the scene opens, every line under
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

**The look (2026-10-18)** costs nothing measurable ([Its look](#its-look)).

**10b, 14b and 19a (2026-10-19)** cost nothing measurable either: the widths are set at the same
steps as before and a `modulate` is free, and at view B the Duchy tier draws 833 times where it drew
914, the county borders gone from it. Stepping the wheel into the County tier, which brings the
county borders now, at four places: the tier waits 0 to 2 frames on its lines (0 to 1 before), and
the frames are as long as before, 3 to 5 ms on average and 7 to 11 at the worst, going in and out.

**The ground (2026-10-19)** costs nothing measurable: 0.32, 0.22 and 0.19 ms of GPU at 200, 90 and
40 miles tall with it and without, over 120 frames a view, and the same draw calls (1,058, 370 and
100), every polygon sharing the one material, its biome a value set on the node. Its colour picked
in each pixel, as it was first written, it took 0.90, 0.68 and 0.59 ms. The scene grew by 17 KB.

**The forests (2026-10-17)** made the scene 13.5 MB, from 9.1, and it opens in 2.7 s, from 1.7:
0.65 s more reading the file, and some 0.35 s more on the first frame, mostly Godot cutting the
2,459 pieces into triangles (0.22 s; 0.6 s before the larger were cut down to 500 points). A frame
at rest all the way out takes 3.7 ms, from 1.4 to 2.4 (1,715 draw calls, from 533: each piece in
view is one), and 1.3 to 2.9 ms from the Duchy tier in. `Forest.find_at()`, which the party asks at
each step's end, tries every piece: 4 to 5 ms, once every 3.75 s of travel.

## Its scripts

`CLAUDE.md`'s Layout lists every script in a line or two; here are the new map's own in full (the
party, forests, settlements and menus it shares with the old map are `Docs/CAMPAIGN.md`'s).

```
  WorldMap/
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
```

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
behind on purpose. `_border[i]` says whether line `i` is a border, `_border_share` is the borders'
share of their width at this step, `_faint` how far toward their faintest they are (0 to 1), and
`_faintest` holds the groups that grow fainter, each with its least share. A settlement out of its tier, or out of view, has `is_processing()` and
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

The look: `MapStyles/harness/render.sh 0 91` draws the scene as it is, in a window, at the four
standard views and at six close in, as `MapStyles/00-current-look.png` and
`91-current-look-close-in.png` (`OUT_DIR=` puts them elsewhere), which is how it was checked; draw
them again after changing the look. And with the borders off
(`BorderSwitch.shown` false) nothing of them may show, the bands and the lake shores included.
`MapDetail`'s `_sea_ends` holds the 138 lines that end in the sea.

The ground: a polygon's `material` must be `Resources/MapGround.tres`, and
`get_instance_shader_parameter(&"biome")` is its biome, its kingdom's number; the material's
`get_shader_parameter(&"desert_color")`, `&"desert_intensity"` and the rest are what its inspector
shows. On the screen a polygon is its `color` mixed toward its biome's colour by the intensity times
`overall_intensity`, which a probe can read back off the viewport's image in a window: all nine came
out within a shade of that. `MapStyles/harness/render.sh 1200` draws the map without the ground
(`StyleKit.without_ground()`), at the views 12's variants are pictured at.

The whole scene is looked at with `MapCreation/Scripts/scene/m3_draw.gd`, in a window: it draws the
whole map at one screen pixel to a pixel of the pictures (`render_full.png`), times it, and draws
close views given as `x,y,w,h,scale,msaa,name` in the pictures' pixels;
`MapCreation/Scripts/scene/m4_compare.py` set it beside `MapCreation/AllSimple.png`, colour by colour,
until the map's look gave its lines colours of their own; `MapStyles/harness/render.sh 0` draws it at
four views.

## Decided with the user

The four tiers and their heights; bridges with the lesser roads, in the Duchy tier; no fifth,
closer tier, the villages and hamlets coming with the County tier; only the nine kingdoms'
capitals in the Realm tier. Then, once there were some 2,000 (2026-10-17): the villages at 100
miles and the hamlets at 50, a second step inside the County tier. And every border switched off
and on with `B`, on to begin with.

The look (2026-10-18), from the proposals in `MapStyles/`: 02's patterned borders, 04's cased
roads, 05's one water "but use a slightly more vibrant color, a bit closer to the current ocean
color outside of the continent", and 10's reweighting where it does not conflict with those, all
balanced where they did; more tweaks to follow. Then (2026-10-19), from 10, 14 and 19 revisited on
that look with variants: 10b, 14b and 19a, the variant recommended in each. And the same day 12b,
the whisper, from the variants of 12, each biome's colour and intensity to be "easily
adjustable/configurable", since the user will tune them further.

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

Without asking, for the look: the blues; borders along rivers and roads kept as bands under them
(02 drew them over the water), with their patterns shortened and `banks`; those along lakes'
shores over the water, moved into `BordersOverLakes`; 10 giving way to the others on every width it
set; the sea ends at 0.16 of their distance and square; the materials as files, one a kind; no
texture on the lines. Applying 14b: the height at which a border is as wide as its node tied to
`true_width_view_miles` (the harness's sketch had a setting of its own, at the same 220), and the
bands' patterns not laid again as the borders thin.

Without asking, for the ground: one material for all nine biomes, each a group of its Color and
Intensity, rather than a material a biome or colours set on the 234 polygons; the biome named on
each polygon, from a list, rather than read off a picture of the kingdoms, so that the colours meet
exactly on the borders as drawn and a hand edit is followed; 0.4 on each biome rather than once
overall, Overall Intensity staying at 1, so that a biome's intensity is what shows; no tint as the
shader's defaults, so that the colours are in one place; the lake's island the Swamp's, by its
county.

## Known gaps

- `Scenes/Map.tscn` is not in the game. Its party keeps to no land, there being no land test or
  navigation for it: it crosses the sea and the lakes, and can be sent off the sheet. Its reticle's
  prompt says "Go here" over the sea as well, and its white ring is faint on the pale land. Only
  county 115's capital has anything in it, and it shares the old village's board and market: with both
  maps in one game they would be one shop. Its settlements are not drawn in the editor (`Destination`
  is no tool script, so the old map's village is not either): there they are nodes with no picture. It
  is 13.6 MB of text and takes about 2.7 s to open, 1.7 before its 2,459 pieces of forest.
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
- The open land is one colour a biome: fields, meadow, marsh, heath and bare rock alike are their
  kingdom's ground, which changes at the kingdom's border, sharply, not where the country does.
- At 0.4 the biomes are only just told apart: the Swamp and the Deciduous Forest are 1.2 apart
  (CIEDE2000; about 1 to 2 is the least an eye tells side by side), the Tundra 1.7 from white, and to
  a red-green colour-blind eye three pairs of neighbours are one colour (0.6: the Temperate
  Mountains and the Evergreen Rainforest, the Deciduous and Tropical forests, the Swamp and the
  Deciduous Forest). The border between them tells them apart. Stronger, 12's palette keeps the last
  three as close to that eye (1.3 to 1.6 at full strength); 12d's lightness steps keep every
  neighbour apart for every eye, and are only nine colours on the material.
- A polygon's biome is set on it by hand: a county moved to another kingdom keeps its old one until
  it is set.
- The gallery forests of the Grassland and the Desert follow the drainage's streams too, which
  the map does not draw, so some ribbons of forest follow no water it shows.
- The forests' see-through colours were chosen on the white land. Over the ground each takes a
  little of its biome's colour, which at 0.4 hardly shows; a stronger ground would want them looked
  at again (12a and 12c made them deeper).
- A dash pattern is laid along each line from its start, in widths of the line: as MapDetail
  changes a width while zooming the dashes slide along a little, and where two borders meet their
  patterns need not line up.
- A road's casing is drawn with it, so where two roads join, the one drawn later lays its edges
  across the other's fill. Google draws every casing first and every fill after, which here would
  take a second line a road.
- A band's marks are shortened for its rank's middle band, so along a much wider or narrower river
  they are a little longer or shorter than a plain border's. And since the borders' own growth thins
  a band's border part alone, its marks, laid in widths of the whole band, come out some 1.4 times
  a plain border's all the way in and 0.85 times all the way out; MapDetail could lay the three band
  materials' lengths again at each width step. The seven bands along roads show their border in
  strips 2.7 units wide at 220 miles (3.9 for the duchies'), which the growth narrows to 1.3 and 2
  all the way in, half a pixel and nine tenths.
- From 240 to 100 miles the counties' 176 capitals show with no county drawn round them, the county
  borders coming with the County tier.
- The shoreline is under a pixel wide far out (0.5 px all the way out): there the land's edge is
  only the change from land to water. A county's dots are faint wherever they show, and all the way
  in, thinned with the other borders, 1.4 px across. 10c, revisited with the look, would make them
  plainer: `MapStyles/harness/render.sh 103` draws it.
- The look is in the scene, and the splices' lines carry it: a new kind of line written by a
  program has to be given its material, `texture_mode` and colour there too ([Its look](#its-look)).
