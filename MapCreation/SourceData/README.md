# The world map's source data

The pictures in the folder above were drawn by program, from data. This folder holds that data,
so that the map can be put into the game, or drawn again some other way, without tracing anything
off a picture: the rivers, the roads and the kingdoms' borders as lines, every region and lake as
a map of numbers, and tables of all of it. `../Features.md` describes the pictures and the map
itself; this file says only what each file here holds and how to read it.

The files were written out on 2026-10-07 from the working data the map was made with, and
checked against the pictures ([How it was checked](#how-it-was-checked)). The programs that made
the map, wrote these files and checked them are in `../Scripts/`. If a picture is changed, the
files here that describe it are out of date until they are made again.

The game's scene of the map, `vcom/Scenes/Map.tscn`, was made from these files on the same day,
by `../Scripts/scene/` (step 11 of that folder's `README.md`). The scene is the map from now on:
it is changed by hand in the Godot editor, and nothing changed there comes back to these files.
It already differs from them a little, by design: where a border follows a river the scene puts
it on the river's own line, and 455 pixels of `CountyMap.png` that stood out of a border as a
tongue or a hook went to the county beside them.

`Streams.json` was added on 2026-10-17: the streams, the flowing water too small to be a river,
worked out on the drainage here by `../Scripts/streams/` (step 13 of that folder's `README.md`)
against the scene, whose rivers, lakes, borders and roads they meet, follow and keep clear of. The
scene draws them; no picture does.

## What is here

| File | Size | Kind | Holds |
|---|---:|---|---|
| `CountyMap.png` | 116 KB | grey map | The county of every pixel of land, 1 to 220 |
| `DuchyMap.png` | 69 KB | grey map | Its duchy, 1 to 44 |
| `KingdomMap.png` | 48 KB | grey map | Its kingdom, 1 to 9 |
| `CountyMapAsDrawn.png` | 116 KB | grey map | The counties on the hand-drawn coast, as the pictures draw them |
| `Regions.json` | 44 KB | table | The kingdoms, duchies and counties: which is in which, their capitals and sizes |
| `Settlements.json` | 49 KB | table | The 220 capitals |
| `KingdomBorders.json` | 225 KB | lines | The kingdoms' 15 borders |
| `Rivers.json` | 1.2 MB | lines | The 291 rivers, with the water each carries and its width at every point |
| `Streams.json` | 7.1 MB | lines | The 9,869 streams, with the water each carries and its width at every point |
| `LakeMap.png` | 100 KB | number map | The lake of every pixel of lake, 1 to 700 |
| `Lakes.json` | 162 KB | table | The 700 lakes |
| `WatershedMap.png` | 67 KB | grey map | The watershed of every pixel of the mainland, 1 to 51 |
| `Watersheds.json` | 7 KB | table | The 51 watersheds |
| `Roads.json` | 1.1 MB | lines | The road network: places, stretches of road, the 351 roads, the 146 bridges |
| `DrainageDirection.png` | 584 KB | grey map, half size | Which way the water runs from every cell of land |
| `DrainageFlow.png` | 819 KB | number map, half size | How much water passes through every cell |
| `DrainageLakes.png` | 52 KB | number map, half size | The lake of every cell of lake, 1 to 1,059 |
| `Drainage.json` | 146 KB | table | How to read those three, and their 1,059 lakes |
| `Ridges.png` | 96 KB | mask | The ridges between neighbouring rivers |
| `Spurs.png` | 234 KB | mask | The low ridges between neighbouring valleys |
| `Brooks.png` | 95 KB | mask | The valleys too small to be drawn as rivers |
| `TerrainMap.png` | 44 KB | grey map | The kind of country every pixel of land was shaped as, 1 to 9 |
| `SketchRegionMap.png` | 43 KB | grey map | The sketch's region of every pixel of the mainland, 1 to 9 |
| `Measurements.json` | 135 KB | table | The measured figures `../Features.md` was written from |

Two things the game will want are not here, because pictures above already hold them exactly: the
land and its coast (`../Continent.png`: white is land, black the coast's line) and the heights
(`../Elevation.png`). [What is not here](#what-is-not-here) lists the rest.

## Reading the files

- **Size.** Every PNG but the three `Drainage` maps is 3100 × 4000 pixels and lines up with the
  pictures pixel for pixel. One pixel is 335 m on the ground; a square pixel is 0.112225 km².
- **Coordinates** are the pictures': (x, y) from the top-left corner, x to the right (east) and y
  down (south). In the JSON files a point is `[x, y]`.
- **A whole number is the middle of a pixel.** Pixel (x, y) reaches from x − 0.5 to x + 0.5 each
  way. So a line laid over a picture whose top-left corner is at (0, 0) wants 0.5 added to both
  its coordinates.
- **Numbers are those of `../Features.md`**: kingdoms 1 to 9, duchies 1 to 44, counties 1 to 220.
  A settlement has its county's number.

There are three kinds of PNG, none with any transparency:

| Kind | PNG | A pixel's value |
|---|---|---|
| grey map | 8-bit greyscale | the number itself; 0 for none |
| number map | 8-bit RGB | red + 256 × green; 0 for none. Blue is always 0 |
| mask | 8-bit greyscale | 255 for yes, 0 for no |

The JSON files are UTF-8. Each begins with `about` and `fields`, which say what it holds in its
own words, and then gives its records one to a line.

In Python:

```python
import json
import numpy as np
from PIL import Image

county = np.asarray(Image.open("CountyMap.png"))                    # county[y, x], 0 to 220
rgb = np.asarray(Image.open("LakeMap.png")).astype(int)
lake = rgb[..., 0] + 256 * rgb[..., 1]                              # lake[y, x], 0 to 700
rivers = json.load(open("Rivers.json", encoding="utf-8"))["rivers"]
```

In Godot (tried in 4.7):

```gdscript
var folder := ProjectSettings.globalize_path("res://").path_join("../MapCreation/SourceData")
var counties := Image.load_from_file(folder.path_join("CountyMap.png"))    # FORMAT_L8
var bytes := counties.get_data()                                            # one byte a pixel
var county := bytes[y * counties.get_width() + x]
var lake_map := Image.load_from_file(folder.path_join("LakeMap.png"))      # FORMAT_RGB8
var lake_bytes := lake_map.get_data()                                       # three bytes a pixel
var at := 3 * (y * lake_map.get_width() + x)
var lake := lake_bytes[at] + 256 * lake_bytes[at + 1]
var rivers: Array = JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("Rivers.json")))["rivers"]
```

- This folder is outside `vcom/`, so Godot imports none of it: a tool script reads the files by
  path, as above.
- Godot's JSON gives every number as a float: put `int()` round ids before using them as keys.
- **Godot reads the 16-bit `../Elevation.png` as 8-bit.** The island's highest point, 3,352.1 m,
  comes out as 3,341 m. Take heights from Python, or convert the picture first.

## Regions

`CountyMap.png` gives every pixel of land its county. `DuchyMap.png` and `KingdomMap.png` are the
same map read through `Regions.json`: a county's duchy, a duchy's kingdom. 0 is everything that is
not land: the sea, and the coast's own line.

- **A border is where the number changes.** The borders of duchies and counties are in no file as
  lines; the kingdoms' are, in `KingdomBorders.json`. Followed pixel by pixel a border is a
  staircase, which wants smoothing before it is drawn large, once for the two regions that share
  it.
- **Lakes and rivers are land here.** A border runs on across a lake, and a lake's pixels have
  their counties like any others.
- **These three maps are on the standard outline**: the land of `../Continent.png`, exactly.
- **A county need not be one piece.** County 220 is four islands: the two great islands off the
  Swamp and two islets beside them. The other ten islets belong to the mainland county nearest
  them: 152, 155, 158, 161 and 163. On the mainland every county is one piece.

`CountyMapAsDrawn.png` is the map the pictures were drawn from, on the land of
`../WorldMapV1.png`: the grey, purple and pink lines of `../Counties.png` lie where it changes.
It differs from `CountyMap.png` in 573 px. At the 13 joins of the hand-drawn coast, which the
standard outline mends, 239 px of new land take the county beside them and 239 px that are land
no more have none. And 95 px of a strip at the join (2686, 2400), which the pictures count with
county 103 and duchy 20, go to county 101 and duchy 19 north of them, as `../AllSimple.png` draws
it.

`Regions.json` holds three lists:

| List | Each record |
|---|---|
| `kingdoms` | `number`, `biome`, `capital_duchy`, `capital_county`, `duchies`, `counties`, `px`, `km2`, `borders_kingdoms`, `has_coast`, `point_inside`, `room_km` |
| `duchies` | `number`, `kingdom`, `capital_county`, `counties`, `px`, `km2`, `point_inside`, `room_km` |
| `counties` | `number`, `duchy`, `kingdom`, `px`, `km2`, `capital_rank`, `capital`, `point_inside`, `room_km` |

- **Capitals.** A county's capital is the settlement with its number. A duchy's capital is the
  capital of its `capital_county`, and a kingdom's the capital of its `capital_county`, which
  lies in its `capital_duchy`.
- **Sizes.** `px` counts the pixels with that number on the maps here, and `km2` is `px` ×
  0.112225. The areas in `../Features.md` were counted on the map as drawn, so they differ by the
  strip (12 km²) and by a few pixels at the joins.
- **`point_inside`** is the pixel of the region furthest from its edge, a place for its name, and
  `room_km` how far that is from the edge.

## Settlements

`Settlements.json` lists the 220 capitals, one a county: 9 of kingdoms, 35 of duchies, 176 of
counties.

| Field | Meaning |
|---|---|
| `county`, `duchy`, `kingdom` | Where it stands. `county` is also its own number |
| `rank` | `kingdom`, `duchy` or `county`: the highest thing it is the capital of |
| `x`, `y` | The middle of its dot on the pictures |
| `site` | Where it was sited. 16 dots stand a little off their sites, clear of a border or the coast |
| `on_island` | True for one, the capital of county 220 |
| `height_m` | The ground's height there, from `../Elevation.png` |
| `sea_km`, `river_km`, `lake_km` | Straight-line distance to the sea, the nearest drawn river, the nearest lake |
| `largest_river_within_4_km_m3s` | The largest flow of any river within 12 px |
| `roads` | How many of the 351 roads end here |

The pictures draw a capital as a disc of radius 13, 9 or 6 px (27, 19 or 13 px across) by its
rank, in the pink, purple or grey of the borders.

## The kingdoms' borders

`KingdomBorders.json` holds the 15 borders between kingdoms as smooth lines: 12,736 points about
a pixel apart, 4,137 km in all. They are the lines the pink of `../Kingdoms.png` was drawn along,
5 px wide.

- **`borders`**: each has its two `kingdoms`, its `km`, its `points`, and `starts_at` and
  `ends_at`, each either `{"meeting_place": id}` or `{"coast": [x, y]}`.
- **`meeting_places`**: the 7 places where three kingdoms meet, with the three.
- **A line that ends at the coast ends on the last pixel of land**, on the hand-drawn coast and
  on the standard outline alike (there are 9 such ends). It is to be carried on from there across
  the coast's own line; the pictures draw it 3 px on.
- The lines run where `KingdomMap.png` changes, nowhere more than a pixel from it.

## Rivers

`Rivers.json` holds the 291 rivers, the largest first. A river here is one line, from where it is
first drawn to where it ends: 67 end in the sea, 222 join a larger river, and 2 end in the
desert's salt lake.

- **Which streams are drawn.** A stream is drawn where it carries 15 m³/s or more. The stream out
  of a lake of 60 km² or more is drawn too, however small, down to the next river or the sea: 32
  rivers begin so, with less than 15 m³/s.
- **A tributary is listed after the river it joins** (`joins` is that river's `id`), and its last
  point is a point of that river's line.
- **A river that reaches the sea runs on some 9 px past the land's edge**, to be cut off where
  the coast is drawn. The pictures with the hand-drawn coast cut it 3 px beyond the land.
- **A river runs through the lakes on its way** (`lakes`), in at one end and out at the outlet.
  Drawn in the lakes' colour, that part does not show.
- **In the Desert and the Grassland a river loses water** to its bed, and a lake to the sun.
  Seven rivers end with less than the most they carried. They are drawn no narrower for it:
  `flow_m3s` and the widths follow the most a river has carried so far.

| Field | Meaning |
|---|---|
| `id` | 1 for the river carrying the most water, and so on down |
| `ends_in` | `sea`, `river` or `salt lake` |
| `joins` | The `id` of the river it joins, if it joins one |
| `sea_rank` | For a river that reaches the sea, its place among those by the most water it carries. 1 to 14 are the rivers of the table in `../Features.md` |
| `largest_flow_m3s` | The most water it carries anywhere along it. The rivers are in the order of this |
| `flow_at_end_m3s` | The water it carries at its end: where it reaches the sea, the river it joins or the salt lake's shore. Less than the most for the seven that lose water |
| `length_km` | Along its line, as far as the land goes |
| `from_kingdom`, `to_kingdom`, `kingdoms` | The kingdoms at its first point, at its last point on land, and all it touches. A river that is itself a border touches both its kingdoms all the way |
| `from_lake` | The lake it flows out of, if its line starts at a lake's outlet |
| `lakes` | The lakes its line passes through, in order |
| `points` | The line: 27,779 points in all, about 1.5 px apart |
| `flow_m3s` | The most water it has carried so far at each point: its flow, but never less than upstream. `DrainageFlow.png` has the flow itself |
| `width_px` | Its width at each point: 1.3 + 1.25 × (flow ÷ 40)^0.36, a quarter more in swamp and tropical rainforest country (7 and 9 on `TerrainMap.png`), and never under 2 |
| `drawn_px` | The width the pictures draw at each point: `width_px` to the nearest whole pixel, 2 to 7 |
| `course` | The river's bed as it was routed over the land, before it was smoothed and made to wander: the middles of the cells of `DrainageDirection.png` it runs through. This is the line that runs downhill on `../Elevation.png` |

**To draw the rivers as the pictures do**, put a disc `drawn_px` across at every point and join
the points. With the lakes of `LakeMap.png` that gives the blue of `../Water.png` exactly.

`left_out` lists the 14 lines the water was worked out as that are too short to draw: 13 streams
that reach the sea within 11 km, and one that joins a larger river after 2 px.

## Streams

`Streams.json` holds the 9,869 streams, the largest first, as `Rivers.json` holds the rivers: the
water below the rivers that still flows, worked out on the drainage (below) by
`../Scripts/streams/t1_streams.py` and drawn in the game's scene, on no picture. Its
`which_are_drawn`, `width_rule`, `wandering` and `meeting_other_lines` say in full how.

- **Which streams are drawn.** A stream begins where the ground it gathers (km²) times the water
  it carries (m³/s) reaches 5.3, what 20 km² of the Deciduous Forest gives, and where it carries
  0.2 m³/s or more, so on less ground the wetter the country. It runs on until it meets a river,
  a lake, the sea or a bigger stream; in the Desert and the Grassland only while it carries 0.1
  m³/s. The outlet of every lake that touches no river is drawn, if water leaves the lake. No dry
  washes are drawn.
- **A stream ends on the line of what it joins as the game's scene draws it**, a river's or a
  stream's (a stream's on one of its points), inside the lake it runs into, or 3 px past the
  land's edge, in the coast's line.
- **Its points are thinned** where it runs straight, and have a point wherever it bends so that
  it nowhere turns more than 10 degrees at one point. A whole number is a pixel's middle, as here.
- **`along_borders`** lists the eight stretches where a stream runs on a border's line, with the
  line of the border's colour the scene lays under it there: the border's own points.

| Field | Meaning |
|---|---|
| `id` | 1 for the stream carrying the most water, and so on down. A stream is listed after the stream it joins |
| `ends_in` | `stream`, `river`, `lake`, `sea`, or `dry` where it runs out of water (none does) |
| `joins` | The `id` of the stream or the river it ends on, or of the lake it runs into |
| `from_lake` | The lake it flows out of, if its line starts at a lake's outlet |
| `kingdom`, `kingdoms` | The kingdom of `KingdomMap.png` most of it lies in (its group in the scene), and all it touches |
| `largest_flow_m3s`, `flow_at_end_m3s` | The most water it carries, and what it carries at its end |
| `length_km` | Along its line |
| `points` | The line: 120,064 points in all |
| `flow_m3s` | The most water it has carried so far, at each point |
| `width_px` | Its width at each point: 0.7 + 0.396 × flow^0.36, a quarter more in swamp and tropical rainforest country (7 and 9 on `TerrainMap.png`), and never under 0.75 or over 1.95, so under the narrowest river's 2 |
| `course` | The middles of the cells of `DrainageDirection.png` its water runs through: the line it was drawn from |

## Lakes

`LakeMap.png` gives every pixel of lake its lake, 1 for the largest down to 700. `Lakes.json`
lists them. A lake's shore is in no file as a line: it is the edge of its patch on the map.

| Field | Meaning |
|---|---|
| `id` | Its number on `LakeMap.png` |
| `px`, `km2` | Its size |
| `middle` | The average of its pixels, which for a crooked lake may lie outside it |
| `point_inside` | The pixel of it furthest from its shore |
| `box` | `[x0, y0, x1, y1]`, the smallest box that holds it |
| `kingdoms` | How many of its pixels lie in each kingdom |
| `kind` | What made it when the water was worked out: `caldera`, `crater`, `salt`, or where on a stream it lies (`trunk` on a main river, `stream`, `head` at a valley's head, `foot` where a river leaves the mountains, `high` a mountain tarn, `low`, `any`) |
| `surface_m` | The height of its surface. `../Elevation.png` holds its bed, which is lower |
| `has_outlet` | False for seven: the salt lake, which two rivers end in, and the six crater lakes of kingdom 2, which no stream enters or leaves |
| `outlet` | Where its water leaves it: the middle of a cell of the drainage |
| `drainage_lakes` | The lakes of `DrainageLakes.png` it was drawn from, the largest first. 15 lakes are drawn from more than one |

## Watersheds

`WatershedMap.png` gives every pixel of the mainland its watershed, 1 to 51, and
`Watersheds.json` lists them, each with its `mouth`, the water reaching it, its size and whether
it reaches the sea (one, the desert's closed basin, does not). All the rain that falls in a
watershed leaves the land at the same river mouth, except that a river system gathering less than
1,500 km² has no watershed of its own and is counted with the one beside it. The islands have
none. The brown lines of `../Rivers.png` are where this map changes.

## Drainage

The rivers, lakes and watersheds were all drawn from one working of how the water runs over the
land, on a grid of half the map's size: 1550 × 2000 cells. Cell (column c, row r) covers the
pixels x = 2c and 2c + 1, y = 2r and 2r + 1, and its middle is (2c + 0.5, 2r + 0.5).

- **`DrainageDirection.png`**: 0 is not land. 1 to 8 name the neighbour the cell's water runs
  to, clockwise from east: 1 east (c + 1), 2 south-east, 3 south (r + 1), 4 south-west, 5 west, 6
  north-west, 7 north, 8 north-east. 9 is a cell where the water leaves the land: into the sea
  at 13,353 cells of the shore, and at one, the salt lake's lowest point, into its floor.
- **`DrainageFlow.png`**: the water passing through each cell, in m³/s × 32. The largest is
  1,877.9 m³/s. In the Desert and the Grassland a river loses water to its bed and a lake to
  the sun, so there the figure can fall downstream; it is 0 in the cells of a lake that has lost
  more than has reached them.
- **`DrainageLakes.png`**: the lake each cell lies in. These are the 1,059 lakes of the working:
  718 are parts of the 700 drawn lakes, and 341, of 0.9 to 6.7 km², are too small to draw.
- **`Drainage.json`** says the same and lists the 1,059 lakes, each with its `kind`, `terrain`,
  size, `surface_m`, `outlet` and `drawn_as`, the drawn lake it is part of, if any.

This is where smaller water is to be had: any stream below the 15 m³/s at which rivers are
drawn can be followed on the first two maps, and the pools are on the third. `Streams.json` holds
the streams drawn from them.

## Roads

`Roads.json` holds the road network as four lists.

| List | Each record |
|---|---|
| `places` | The network's nodes. `id`, `kind`, `x`, `y`. The 220 settlements have their counties' numbers; the 208 forks, where roads part outside a settlement, are numbered from 221 |
| `stretches` | Its edges: road from one place to the next, 549 of them. `id`, `from`, `to`, `highway`, `km`, `bridges` and `points`, the line from the one place to the other, a point a pixel |
| `roads` | The 351 roads between neighbouring settlements. `between` (the two settlements), `km`, `highway`, `over_the_sea`, and `stretches`: the stretches it runs along in order, each as `[id, forward]`, forward being true if the road runs that stretch from its `from` to its `to` |
| `bridges` | The 146 bridges. `id`, `stretch`, `over` (`river` or `sea`), `river` and `river_m3s` (the river of `Rivers.json` crossed and its flow there), `at` (the middle of the water crossed), `from` and `to` (the ends of the mark, 2 px on to each bank), `water_px`, `highway`, `at_settlement` |

- **Roads share stretches** where they run together, so the lines to draw are the stretches: 2
  px wide, or 3 px for a highway. A stretch is a highway if any road over it is; 92 roads are.
- **A stretch ends on the middle of a settlement's dot**, which the pictures draw over it.
- **A bridge** is drawn 2 px wider than its road. 145 cross rivers; one, 29 px over the sea,
  joins the island's settlement (220) to the mainland.
- The stretches come to 5,292 km of highway and 14,020 km of other road.

## The land's own lines, and its kinds

Three masks hold lines of the land that borders follow and no picture draws. They were found on
the half-size grid, so they are made of 2 px squares, and they are of the mainland only.

| File | Pixels set | What it marks |
|---|---:|---|
| `Ridges.png` | 363,777 | The lines between the land that runs down to one river and the land that runs down to the next. Where the two rivers reach the sea apart, that is a watershed's own line, as the grid has it |
| `Brooks.png` | 202,004 | Valleys that gather the water of 60 km² or more and carry less than 15 m³/s, so are not drawn as rivers |
| `Spurs.png` | 834,021 | The lines between the land that runs down to one valley gathering that much and the land that runs down to the next. Rivers' valleys are among those, so most of the ridges are here too |

Two maps hold kinds of country:

- **`TerrainMap.png`**: the kind of country, 1 to 9, that each pixel of land was shaped as when
  the heights and the water were made. The numbers are the kingdoms' and mean their biomes. That
  was before the kingdoms' borders were drawn along the rivers and ridges, so it is the kingdom
  of `KingdomMap.png` on 96.1% of the land and a neighbour's kind on the rest.
- **`SketchRegionMap.png`**: the region of `../WorldMapRegions.png`, 1 to 9, that each pixel of
  the mainland lies in; 0 on the islands, which are in no region. It is the kingdom of
  `KingdomMap.png` on 78.4% of the land.

These five, `CountyMapAsDrawn.png`, `WatershedMap.png` and the drainage are all on the land of
`../WorldMapV1.png`, the hand-drawn coast. It differs from the standard outline by 239 px gained
and 239 px lost at the 13 joins.

## Measurements

`Measurements.json` holds the figures `../Features.md` was written from, in four parts: `facts`
(the land, heights, water, lakes, rivers, watersheds, every kingdom, duchy and county, the
settlements, borders and roads, and what each picture file holds), `layers` (how `../All.png` is
put together), `continent` (`../Continent.png` and the 13 joins) and `allsimple`
(`../AllSimple.png`). Its areas of regions are those of the map as drawn.

## What is not here

- **The land and the coast.** They are `../Continent.png`: white is land, black the coast's
  line, 7 px wide, outside the land.
- **The heights.** They are `../Elevation.png`: tenths of a metre, 16-bit.
- **Lines for the coast, the lakes' shores and the borders of duchies and counties.** They are
  the edges of patches on the maps.
- **Names.** Nothing on the map is named.
- **The working data** the programs kept between steps: grids, drafts and trial pictures. These
  files were written from it and stand in for it. The programs themselves are in `../Scripts/`.

## How it was checked

A program, `../Scripts/duchy/v9_source.py`, read these files and the pictures, and nothing else,
on 2026-10-07. It found:

- **Regions.** `CountyMap.png` covers the land of `../Continent.png` exactly, and
  `CountyMapAsDrawn.png` that of `../WorldMapV1.png`. The three maps and the tables agree. On
  `../Counties.png`, 99.5% of the pixels of every border's line are within 2.2 px of where the
  map as drawn changes: less than half the widest line's width.
- **Settlements.** The 220 are the 220 dots of `../Settlements.png`: each where its dot is, in
  its dot's colour, in its own county; and every kingdom and duchy has its capital.
- **Rivers and lakes.** Drawn again from `Rivers.json` and `LakeMap.png`, the water is the blue
  of `../Water.png`: 0 px differ of 415,040. Every tributary ends on a point of the river it
  joins, and the water each river is given is what `DrainageFlow.png` has along its course.
- **Drainage.** Followed from 3,000 cells taken at random, `DrainageDirection.png` always comes
  to where the water leaves the land.
- **Roads.** The network is one piece, and every road runs stretch by stretch from the one
  settlement to the other. No point of a stretch is more than 1 px from a road, bridge or dot
  of `../Roads.png`, and no pixel of road or bridge more than 3.6 px from a stretch's line. (The
  lines the file was made from, drawn as the picture drew them, gave its red and dark brown
  exactly; the file keeps every second point.) Every bridge lies on a dark brown mark, and every
  river bridge in the water of the river it names.
- **Kingdoms' borders.** Every point of the 15 lines is on the pink of `../Kingdoms.png`, and
  each line has its two kingdoms on its two sides.
- **Godot.** Godot 4.7 reads the maps and the tables as they are written here
  (`g5_read_source.gd` and `g6_readme_snippet.gd`, beside the checking program).

`Streams.json`, added after, was checked as it was made, on 2026-10-17, by the program that made
it: every stream ends on water as the scene draws it, no stream crosses another, and every stream
that joins another ends on one of its points. The scene's streams were then held against a scene
made afresh from the file: the same nodes, point for point.
