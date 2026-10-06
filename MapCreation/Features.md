# Features of the world map images

This folder holds VCOM's new world map as a stack of pictures of one island. `WorldMapV1.png` is
the coast. Each later picture adds one kind of thing to an earlier one: kingdoms, heights, water,
duchies, counties, settlements, roads. `All.png` shows everything together. This file says what
each picture holds, what every colour and mark means, and how big everything is.

Every picture is 3100 × 4000 pixels and lines up with every other pixel for pixel, so a place has
the same (x, y) in all of them.

This is the island's new shape. It is to replace the map in `vcom/WorldMap/`, which the game
still uses.

![Everything on one map](All.png)

## Contents

1. [Legend](#legend)
2. [The pictures](#the-pictures)
3. [Size and scale](#size-and-scale)
4. [Colours](#colours)
5. [What each picture holds](#what-each-picture-holds)
6. [How the layers sit on each other](#how-the-layers-sit-on-each-other)
7. [Reading the pictures back](#reading-the-pictures-back)
8. [Decisions and assumptions](#decisions-and-assumptions)
9. [What the maps do not show](#what-the-maps-do-not-show)
10. [The 44 duchies](#the-44-duchies)
11. [The 220 counties and their capitals](#the-220-counties-and-their-capitals)

## Legend

What you see on `All.png`, and on the pictures that hold only part of it.

| Mark | Colour | Meaning |
|---|---|---|
| Flat pale blue | `(181, 235, 255)` `#B5EBFF` | The sea |
| White | `(255, 255, 255)` `#FFFFFF` | Land |
| Black line round the land, about 5 px, with thin ripple lines beside it | black and greys | The coast, as drawn by hand |
| Line 5 px wide | pink `(233, 0, 255)` `#E900FF` | Border between two kingdoms |
| Line 3 px wide | purple `(110, 30, 180)` `#6E1EB4` | Border between two duchies of one kingdom |
| Line 2 px wide | grey `(128, 128, 128)` `#808080` | Border between two counties of one duchy |
| Disc 27 px across | pink, as the kingdom borders | Capital of a kingdom (also capital of its duchy and county) |
| Disc 19 px across | purple, as the duchy borders | Capital of a duchy (also capital of its county) |
| Disc 13 px across | grey, as the county borders | Capital of a county |
| Winding line 2 to 7 px wide | blue `(28, 112, 224)` `#1C70E0` | River, wider the more water it carries |
| Filled shape | the same blue | Lake |
| Line 3 px wide | red `(200, 40, 30)` `#C8281E` | Highway: a road on the way between two kingdoms' capitals |
| Line 2 px wide | the same red | Any other road |
| Short bar across a road, 2 px wider than the road | dark brown `(60, 35, 15)` `#3C230F` | Bridge, where a road crosses a river |
| Dashed line at sea | the roads' red | Ferry (there is one, to the island town) |
| Line 3 px wide, on `Rivers.png` only | brown `(196, 118, 44)` `#C4762C` | Watershed: the line between the land draining to one river mouth and to the next |

Nothing is named on any picture, and none has a key, compass or scale bar drawn on it.

## The pictures

| File | Shows | Starts from | Adds |
|---|---|---|---|
| `WorldMapV1.png` | The coast: sea, land and the inked shoreline | drawn by hand | |
| `WorldMapRegions.png` | The coast with nine numbered regions sketched on it | `WorldMapV1.png`, by hand | thin pink lines and the numerals 1 to 9 |
| `Kingdoms.png` | The nine kingdoms | `WorldMapV1.png` | kingdom borders |
| `Elevation.png` | How high the land is | nothing: a picture of its own, in greys | |
| `Rivers.png` | Rivers, lakes and watersheds | `WorldMapV1.png` | water and watershed lines |
| `Water.png` | Rivers and lakes | `WorldMapV1.png` | water (it is `Rivers.png` without the watershed lines) |
| `Duchies.png` | Kingdoms and their 44 duchies | `Kingdoms.png` | duchy borders |
| `Counties.png` | Kingdoms, duchies and the 220 counties | `Duchies.png` | county borders |
| `Settlements.png` | The same with the 220 capitals | `Counties.png` | a dot for each capital |
| `Roads.png` | The same with the roads | `Settlements.png` | roads, bridges and the ferry |
| `All.png` | Everything but heights and watersheds | `Roads.png` and `Water.png` | nothing new: the water is laid under `Roads.png` |

The first two were drawn by hand and are where everything starts. The rest were worked out from
them by program, in the order kingdoms, heights and water, duchies, counties, settlements, roads,
each built on the ones before it ([Decisions and assumptions](#decisions-and-assumptions) says
how).

| File | Pixels | Kind | Size on disk |
|---|---|---|---:|
| `WorldMapV1.png` | 3100 × 4000 | 8-bit RGBA PNG | 1,020,782 bytes |
| `WorldMapRegions.png` | 3100 × 4000 | 8-bit RGBA PNG | 1,053,529 bytes |
| `Kingdoms.png` | 3100 × 4000 | 8-bit RGBA PNG | 1,027,967 bytes |
| `Elevation.png` | 3100 × 4000 | 16-bit greyscale PNG | 6,601,202 bytes |
| `Rivers.png` | 3100 × 4000 | 8-bit RGBA PNG | 1,213,639 bytes |
| `Water.png` | 3100 × 4000 | 8-bit RGBA PNG | 1,146,242 bytes |
| `Duchies.png` | 3100 × 4000 | 8-bit RGBA PNG | 1,080,041 bytes |
| `Counties.png` | 3100 × 4000 | 8-bit RGBA PNG | 1,187,898 bytes |
| `Settlements.png` | 3100 × 4000 | 8-bit RGBA PNG | 1,201,674 bytes |
| `Roads.png` | 3100 × 4000 | 8-bit RGBA PNG | 1,315,331 bytes |
| `All.png` | 3100 × 4000 | 8-bit RGBA PNG | 1,440,693 bytes |

## Size and scale

**One pixel is 335 m on the ground**, and a square pixel is 0.1122 km². That follows from one
decision, that the island is the size of Texas (695,662 km²): its land is 6,199,855 pixels, which
at 335 m a pixel is 695,779 km².

- **The sheet** is 3100 px wide and 4000 px tall: 1,038.5 km by 1,340 km.
- **The land** runs from x = 63 to x = 3057 and from y = 8 to y = 3991: 1,003 km from west to east
  and 1,335 km from north to south, about 12 degrees of latitude.
- **The land is almost exactly half the sheet:** 6,199,855 px of land, 6,200,145 px of sea and
  ink.
- **North is at the top.** The prevailing wind blows from the west, the left edge.
- **Coordinates** in this file are (x, y) in pixels from the top-left corner of the picture, x to
  the right (east) and y down (south).
- **The furthest points of land** are north (1562, 8), south (2689, 3991), west (63, 1200) and
  east (3057, 3597).
- **The mainland** is 6,169,342 px, 692,354 km². There are **14 islands** off its south-west,
  30,513 px, 3,424 km² in all.
- **The mainland's coast** is about 8,300 km long, measured along the pixels. (A coast has no one
  length: measured more finely it would be longer.)

To turn pixels into kilometres multiply by 0.335; kilometres into pixels, by 2.985.

| On the ground | In the picture |
|---|---|
| 1 km | 3 px |
| 10 km | 30 px |
| 30 km, a day on foot | 90 px |
| 50 km, a day on horseback | 149 px |
| 100 km | 299 px |
| 1,000 km | 2,985 px |
| 100 km² | 891 px, a square 30 px on a side |
| A county, 3,163 km² on average | 28,180 px, a square 168 px (56 km) on a side |
| A duchy, 15,800 km² on average | 140,900 px, a square 375 px (126 km) on a side |
| A kingdom, 77,309 km² | 688,873 px, a square 830 px (278 km) on a side |

**The marks are symbols, not to scale.** At 335 m a pixel nothing narrower than a few hundred
metres could be drawn at its true width, so lines and dots are drawn to be seen:

| Mark | In the picture | That would be, on the ground |
|---|---|---|
| The coast's ink | about 5 px | 1.7 km |
| Kingdom border | 5 px | 1.7 km |
| Duchy border | 3 px | 1 km |
| County border | 2 px | 0.7 km |
| River | 2 to 7 px | 0.7 to 2.3 km (a real river carrying as much is 20 to 500 m wide) |
| Watershed line | 3 px | 1 km |
| Highway | 3 px | 1 km |
| Other road | 2 px | 0.7 km |
| Bridge mark | 4 or 5 px wide, 8 to 18 px long | 1.3 to 1.7 km wide, 2.7 to 6 km long |
| Kingdom capital's dot | 27 px across (radius 13) | 9 km |
| Duchy capital's dot | 19 px across (radius 9) | 6.4 km |
| County capital's dot | 13 px across (radius 6) | 4.4 km |
| Ferry's dashes | 2 px wide, 5 px on and 4 px off | |

The middle of a line is where the thing is: a border's middle is the border, a road's middle the
road, a dot's middle the settlement. Lakes are the exception: a lake is drawn at its true size.

## Colours

Every colour added to the coast map is one flat colour with hard edges and no transparency (alpha
255), so anything can be picked out of a picture by its exact colour.

| Colour | Red, green, blue | Hex | Used for | In which pictures |
|---|---|---|---|---|
| Sea blue | 181, 235, 255 | `#B5EBFF` | The sea | all but `Elevation.png` |
| White | 255, 255, 255 | `#FFFFFF` | Land with nothing drawn on it | all but `Elevation.png` |
| Black and greys | 0, 0, 0 and in between | | The coast's ink, soft-edged, and the ripple lines in the sea | all but `Elevation.png` |
| Pink | 233, 0, 255 | `#E900FF` | Kingdom borders; kingdom capitals; in the sketch, the region lines and numerals | `WorldMapRegions`, `Kingdoms`, `Duchies`, `Counties`, `Settlements`, `Roads`, `All` |
| Purple | 110, 30, 180 | `#6E1EB4` | Duchy borders; duchy capitals | `Duchies`, `Counties`, `Settlements`, `Roads`, `All` |
| Grey | 128, 128, 128 | `#808080` | County borders; county capitals | `Counties`, `Settlements`, `Roads`, `All` |
| Blue | 28, 112, 224 | `#1C70E0` | Rivers and lakes | `Rivers`, `Water`, `All` |
| Brown | 196, 118, 44 | `#C4762C` | Watershed lines | `Rivers` only |
| Red | 200, 40, 30 | `#C8281E` | Roads; the ferry | `Roads`, `All` |
| Dark brown | 60, 35, 15 | `#3C230F` | Bridges | `Roads`, `All` |

A border and the capital of the same rank share a colour: pink for kingdoms, purple for duchies,
grey for counties. A line is the border; a disc is the capital.

Three things to know when picking colours out by program:

- **The coast map is soft-edged.** Its ink is black with in-between greys along its edges and pale
  blues where it meets the sea, about 199,500 pixels in all, some of them a little transparent
  (alpha 229 to 254). Those are the only pixels in any picture that are not one of the colours
  above.
- **101 of those pixels happen to be exactly the county grey** `(128, 128, 128)`. All lie in the
  ink's edge, off the land, so grey on land is always a county border or a county capital.
- **Land is every pixel of `WorldMapV1.png` whose red, green and blue are all 250 or more**
  (6,199,855 pixels, of which 6,197,155 are pure white). The ink and the sea are everything else.

How many pixels of each colour each picture holds:

| File | Sea | White | Pink | Purple | Grey | Blue | Brown | Red | Dark brown | Other shades |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `WorldMapV1.png` | 5,877,528 | 6,197,155 |  |  | 101 |  |  |  |  | 325,216 |
| `WorldMapRegions.png` | 5,877,518 | 6,160,613 | 32,575 |  | 101 |  |  |  |  | 329,193 |
| `Kingdoms.png` | 5,877,528 | 6,141,198 | 56,170 |  | 101 |  |  |  |  | 325,003 |
| `Rivers.png` | 5,877,528 | 5,671,097 |  |  | 101 | 415,040 | 112,382 |  |  | 323,852 |
| `Water.png` | 5,877,528 | 5,783,338 |  |  | 101 | 415,040 |  |  |  | 323,993 |
| `Duchies.png` | 5,877,528 | 6,067,485 | 56,170 | 74,000 | 101 |  |  |  |  | 324,716 |
| `Counties.png` | 5,877,528 | 5,957,187 | 56,170 | 74,000 | 110,813 |  |  |  |  | 324,302 |
| `Settlements.png` | 5,877,528 | 5,919,739 | 61,219 | 83,695 | 133,517 |  |  |  |  | 324,302 |
| `Roads.png` | 5,877,513 | 5,772,921 | 60,090 | 82,320 | 131,378 |  |  | 143,414 | 8,098 | 324,266 |
| `All.png` | 5,877,513 | 5,399,587 | 60,090 | 82,320 | 131,378 | 374,429 |  | 143,414 | 8,098 | 323,171 |

("Other shades" are the coast's ink and its soft edges. The grey column's 101 in the pictures
without counties are the ink pixels mentioned above.)

`Elevation.png` uses no colours. It is one grey value a pixel, and the value is a height:
see [Elevation.png](#elevationpng-the-height-of-the-land).

## What each picture holds

### WorldMapV1.png: the coast

The island as drawn by hand, and the base of every other picture.

- **Sea:** one flat blue, 5,877,528 px.
- **Land:** white, 15 pieces: the mainland and 14 islands.
- **The coast:** a black inked line about 5 px thick round every piece of land, with short thin
  ripple lines in the sea beside it, in the manner of a pen-and-ink map.
- **Shapes worth knowing:**
  - a comb of narrow inlets and spits on the south-west coast (about x 500 to 1050, y 2080 to
    2370), with the islands off its west end;
  - a deep bay on the south-west coast at about (980, 2580);
  - a lagoon nearly shut in by land on the north-east coast at about (2090, 1060);
  - a cape on the east coast at (3018, 1712);
  - a ragged south-eastern end, whose tip at (3057, 3597) is the furthest east the land reaches.

The islands, largest first. Each belongs to the county named, which is in the Swamp, kingdom 7:

| Island | Area (km²) | Pixels | Middle (x, y) | County | Duchy |
|---:|---:|---:|---|---:|---:|
| 1 | 2,295 | 20,450 | (236, 2201) | 220 | 33 |
| 2 | 841 | 7,495 | (159, 2278) | 220 | 33 |
| 3 | 51 | 453 | (111, 2351) | 220 | 33 |
| 4 | 48 | 431 | (712, 2260) | 158 | 31 |
| 5 | 47 | 420 | (361, 2274) | 163 | 33 |
| 6 | 41 | 365 | (861, 2350) | 161 | 32 |
| 7 | 24 | 218 | (604, 2275) | 163 | 33 |
| 8 | 21 | 188 | (158, 2092) | 220 | 33 |
| 9 | 18 | 160 | (962, 2358) | 161 | 32 |
| 10 | 15 | 138 | (876, 2224) | 157 | 31 |
| 11 | 8 | 69 | (897, 2336) | 161 | 32 |
| 12 | 7 | 64 | (750, 2259) | 155 | 31 |
| 13 | 4 | 37 | (690, 2309) | 158 | 31 |
| 14 | 3 | 25 | (540, 2262) | 163 | 33 |

Islands 1, 2, 3 and 8 together are county 220, the only county that is not on the mainland.

### WorldMapRegions.png: the sketch of the nine regions

The coast with nine regions marked by hand, which the kingdoms were made from.

- **Thin pink lines**, 1 px wide, in five strokes, dividing the mainland into nine regions. The
  strokes have six small gaps (3 to 12 px), two at the coast and four where lines meet.
- **Pink numerals 1 to 9**, each about 65 px wide and 103 px tall, one in each region. These
  numbers are the kingdoms' numbers everywhere in this file.
- The islands are in no region.

The regions are unequal as sketched (the largest, 8, is 2.7 times the smallest, 2). `Kingdoms.png`
keeps their arrangement and the general run of their borders and moves the borders until all nine
are the same size. 79% of the mainland is in the kingdom it was sketched in.

### Kingdoms.png: the nine kingdoms

- **Pink lines 5 px wide** are the borders between kingdoms: 56,170 px, about 4,000 km of border.
  They meet at 7 places inland and reach the coast at 9.
- Each line runs 3 px into the coast's ink, so pink and coast together close every kingdom off.
- The kingdoms' numbers are not drawn here. The middle of each kingdom's white area is at:
  1 (993, 944), 2 (1492, 691), 3 (1698, 1942), 4 (2192, 1315), 5 (2484, 2087), 6 (582, 1454),
  7 (1079, 2254), 8 (1916, 2906), 9 (2409, 3521).

**Each kingdom is also a biome**, one kind of country from border to border, and **all nine are
the same size**: a ninth of the land, 77,296 to 77,320 km² (within 0.02% of each other). The
islands are counted with kingdom 7, the Swamp, which they lie off, so its mainland is 73,889 km².

| Kingdom | Biome | Area (km²) | Duchies | Counties | Capital (x, y) | Borders kingdoms | Heights: lowest, median, highest (m) | Water | Lakes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Tundra Mountains | 77,308 | 4 | 24 | (981, 499) | 2, 3, 6 | 1, 826, 2620 | 7.8% | 247 |
| 2 | Volcanic Mountains / Ruins | 77,304 | 4 | 24 | (1487, 835) | 1, 3, 4 | 0, 552, 2794 | 3.8% | 41 |
| 3 | Temperate Mountains | 77,296 | 6 | 24 | (1487, 1935) | 1, 2, 4, 5, 6, 7, 8 | 24, 900, 3352 | 4.7% | 23 |
| 4 | Desert | 77,319 | 4 | 24 | (2031, 1515) | 2, 3, 5 | 0, 172, 1529 | 2.6% | 7 |
| 5 | Grassland | 77,312 | 5 | 25 | (2685, 2143) | 3, 4, 8 | 0, 66, 656 | 3.6% | 55 |
| 6 | Evergreen Temperate Rainforest | 77,320 | 5 | 25 | (379, 1633) | 1, 3, 7 | 0, 103, 1017 | 8.2% | 48 |
| 7 | Swamp | 77,313 | 6 | 24 | (1102, 2596) | 3, 6, 8 | 0, 1, 271 | 16.9% | 161 |
| 8 | Deciduous Forest | 77,301 | 5 | 25 | (1865, 2765) | 3, 5, 7, 9 | 0, 188, 1051 | 5.5% | 36 |
| 9 | Tropical Rainforest | 77,306 | 5 | 25 | (2565, 3326) | 8 | 0, 162, 842 | 7.1% | 82 |

Kingdom 3 is the only one with no coast, and it touches every kingdom but 9. Kingdom 9 touches
only kingdom 8. The cold kingdoms are in the north and the tropical one in the south; the wet
ones (6, 7, 9) face the west wind or the warm south, and the dry ones (4, 5) lie east of the
central mountains, in their rain shadow.

How each kingdom is divided, and the numbers this file gives its duchies and counties:

| Kingdom | Duchies | Duchy sizes (km²) | Counties in each duchy | County sizes (km²) | Duchy numbers | County numbers |
|---:|---:|---|---:|---|---|---|
| 1 | 4 | 18,129 to 20,322 | 6 | 2,956 to 3,440 | 1 to 4 | 1 to 24 |
| 2 | 4 | 18,818 to 20,001 | 6 | 3,076 to 3,428 | 5 to 8 | 25 to 48 |
| 3 | 6 | 11,973 to 13,892 | 4 | 2,933 to 3,561 | 9 to 14 | 49 to 72 |
| 4 | 4 | 18,738 to 20,226 | 6 | 3,072 to 3,424 | 15 to 18 | 73 to 96 |
| 5 | 5 | 15,142 to 15,773 | 5 | 2,961 to 3,222 | 19 to 23 | 97 to 121 |
| 6 | 5 | 15,089 to 15,849 | 5 | 2,931 to 3,257 | 24 to 28 | 122 to 146 |
| 7 | 6 | 12,313 to 13,190 | 4 | 3,056 to 3,356 | 29 to 34 | 147 to 169, and 220 |
| 8 | 5 | 14,793 to 16,068 | 5 | 2,899 to 3,307 | 35 to 39 | 170 to 194 |
| 9 | 5 | 14,455 to 16,444 | 5 | 2,830 to 3,353 | 40 to 44 | 195 to 219 |

### Elevation.png: the height of the land

A picture with no colours: 16-bit greyscale, one value a pixel.

- **The value is the height above the sea in tenths of a metre.** 12,345 means 1,234.5 m.
- **0 is everything off the land.** On land the values run from 1 (0.1 m) to 33,521 (3,352.1 m).
- **Under a lake the value is the lake's bed**, not its surface.
- Most picture viewers show a 16-bit picture badly (nearly black, or banded). Read it by program:
  with Python's Pillow, `Image.open("Elevation.png")` gives mode `I;16`, and dividing its values
  by 10 gives metres.

The land is low on the whole: its mean height is 364 m and its median 175 m. 24% lies below 50 m,
25% above 500 m, 11% above 1,000 m and under 1% above 2,000 m. The highest point is 3,352 m at
(1947, 2157), in the Temperate Mountains.

| Kingdom | Biome | Lowest (m) | Median (m) | Highest (m) | Highest point (x, y) |
|---:|---|---:|---:|---:|---|
| 1 | Tundra Mountains | 1 | 826 | 2,620 | (905, 876) |
| 2 | Volcanic Mountains / Ruins | 0 | 552 | 2,794 | (1320, 510) |
| 3 | Temperate Mountains | 24 | 900 | 3,352 | (1947, 2157) |
| 4 | Desert | 0 | 172 | 1,529 | (1774, 1507) |
| 5 | Grassland | 0 | 66 | 656 | (2098, 1861) |
| 6 | Evergreen Temperate Rainforest | 0 | 103 | 1,017 | (802, 1320) |
| 7 | Swamp | 0 | 1 | 271 | (1290, 1855) |
| 8 | Deciduous Forest | 0 | 188 | 1,051 | (1933, 3225) |
| 9 | Tropical Rainforest | 0 | 162 | 842 | (2759, 3415) |

The shape of the land, kingdom by kingdom:

- **1, 2 and 3 are one high country** in the north and middle of the island.
  - 1 is a fell plateau, highest in its middle.
  - 2 is a lava plateau with volcanic cones standing on it and one flooded caldera.
  - 3 is the steep central range.
- **7 is flat and within a few metres of the sea** almost everywhere (its median height is 1 m).
- **4 and 5 are long aprons** falling east from the central range to the sea.
- **6 is foothills and lowland** falling west to the sea.
- **8 and 9 are hill country**, to about 1,000 m.

The volcanoes of kingdom 2, by the height of their tops: 2,794 m at (1320, 511), 2,744 m at
(1387, 697), 2,543 m at (1553, 1242), 2,347 m at (1360, 324), 2,242 m at (1556, 1066), 2,067 m at
(1652, 933), 1,994 m at (1388, 976) and 1,497 m at (1521, 555). The caldera is the round lake at
(1549, 266), 492 km², its bed at 818 m inside a rim that rises to 1,478 m.

These heights were invented for this map: nothing in the game set them. The rivers were made on
them, and every river on the map runs downhill on this picture.

### Rivers.png and Water.png: rivers, lakes and watersheds

`Water.png` is the coast with the rivers and lakes. `Rivers.png` is the same with the watershed
lines as well. The blue is identical in the two: 415,040 px.

**Water covers 6.68% of the land**: lakes 4.56%, rivers 2.12%. (The rivers' share is of the map,
not of the ground: they are drawn far wider than they are.) Kingdom by kingdom, with the yearly
run-off and the slope of the land each was given when the water was worked out:

| Kingdom | Biome | Under water | Lakes | Rivers | Number of lakes | Run-off assumed (m a year) | Slope aimed at (m per km) |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Tundra Mountains | 7.8% | 6.4% | 1.4% | 247 | 0.52 | 21 |
| 2 | Volcanic Mountains / Ruins | 3.8% | 2.2% | 1.6% | 41 | 0.33 | 10 |
| 3 | Temperate Mountains | 4.7% | 3.0% | 1.7% | 23 | 1.05 | 33 |
| 4 | Desert | 2.6% | 1.8% | 0.7% | 7 | 0.006 | 3.6 |
| 5 | Grassland | 3.6% | 2.0% | 1.6% | 55 | 0.06 | 2.3 |
| 6 | Evergreen Temperate Rainforest | 8.2% | 4.6% | 3.6% | 48 | 2.1 | 4.4 |
| 7 | Swamp | 16.9% | 12.6% | 4.3% | 161 | 0.65 | 0.05 |
| 8 | Deciduous Forest | 5.5% | 4.1% | 1.4% | 36 | 0.42 | 12 |
| 9 | Tropical Rainforest | 7.1% | 4.4% | 2.7% | 82 | 1.35 | 6.5 |
| all | | 6.68% | 4.56% | 2.12% | 700 | | |

**Rivers**

- **305 river lines.** 80 reach the sea, 223 are tributaries that join another river, and 2 end
  in the desert's salt lake.
- **A river is drawn only where it carries 15 m³/s or more**, so each line starts some way below
  its true source. The largest carries 1,878 m³/s at its mouth.
- **Width shows size:** 1.3 + 1.25 × (flow ÷ 40)^0.36 pixels, a quarter more in the Swamp and the
  Tropical Rainforest. That is 2 px at 15 m³/s, 3 px at 100, 4 px at 300, 5 px at 1,000 and 6 to 7
  px for the largest.
- **About 15,000 km of river** in all. The longest single line is 496 km; half are under 24 km.
- **Rivers wander where their bed is nearly level** and run straighter where it is steep.
- **No river splits.** There are no deltas with several mouths.
- A river mouth runs 3 px into the coast's ink, so the river is seen to reach the sea. Those are
  1,186 of the blue pixels; the other 413,854 are on land.
- Islands have no rivers.

The largest rivers, by the water they bring to their mouths. "Drawn from" is where the line
begins, at 15 m³/s:

| River | Flow at its mouth (m³/s) | Length of its main line (km) | Drawn from (x, y) | Starts in kingdom | Mouth (x, y) | Ends in kingdom |
|---:|---:|---:|---|---:|---|---:|
| 1 | 1,878 | 391 | (839, 1365) | 1 | (187, 1677) | 6 |
| 2 | 1,515 | 493 | (1325, 1123) | 2 | (1025, 2127) | 7 |
| 3 | 1,263 | 496 | (1215, 1221) | 1 | (195, 1247) | 6 |
| 4 | 1,203 | 387 | (1853, 1909) | 3 | (1055, 2267) | 7 |
| 5 | 1,090 | 376 | (1953, 2773) | 8 | (1099, 2615) | 7 |
| 6 | 611 | 206 | (2651, 3593) | 9 | (2607, 3159) | 9 |
| 7 | 452 | 222 | (2109, 3301) | 9 | (2575, 3141) | 9 |
| 8 | 370 | 141 | (2269, 3481) | 9 | (2357, 3795) | 9 |
| 9 | 326 | 272 | (1101, 823) | 1 | (1669, 747) | 2 |
| 10 | 294 | 167 | (787, 925) | 1 | (431, 809) | 6 |
| 11 | 275 | 310 | (1655, 1659) | 3 | (2023, 1125) | 4 |
| 12 | 267 | 262 | (2069, 3011) | 8 | (2499, 2887) | 8 |
| 13 | 256 | 131 | (2113, 3381) | 9 | (1823, 3479) | 9 |
| 14 | 233 | 245 | (1047, 787) | 1 | (941, 245) | 1 |

The five largest all reach the west and south-west coasts: rivers 1 and 3 through the Rainforest,
rivers 2 and 4 through the Swamp to the comb of inlets, and river 5 to the bay where the Swamp's
capital stands. The dry east has few and small rivers; the largest there, river 11, runs from the
central mountains through the Desert to the lagoon.

**Lakes**

- **700 lakes**, 31,710 km² in all, from 3 km² to 1,909 km². Half are under 11 km²; 61 are over
  100 km² and 6 over 500 km².
- **A lake is a flooded valley**: it follows its valley's shape, runs up side valleys as arms, and
  has one outlet.
- **The kinds differ by kingdom:**
  - 1, Tundra Mountains: a few large ribbon lakes on the main rivers and hundreds of small tarns,
    gathered into lake districts with bare country between.
  - 2, Volcanic Mountains: crater lakes and the flooded caldera.
  - 3, Temperate Mountains: long lakes where rivers leave the mountains, and small high tarns
    above 1,500 m.
  - 4, Desert: a handful of small lakes, and the salt lake.
  - 5, Grassland: a few broad steppe lakes and scattered pools.
  - 6, Evergreen Temperate Rainforest: lakes on its big rivers.
  - 7, Swamp: three great shallow sheets, the largest lakes on the island, and hundreds of pools.
  - 8, Deciduous Forest: lakes on its rivers.
  - 9, Tropical Rainforest: lowland lakes and many pools.
- **The salt lake** at (2098, 1509), 1,050 km², is the only lake with no outlet. Two rivers end in
  it, and it is as big as they can keep full against the desert sun.
- The islands carry a few small lakes (102 km² in all).

The twelve largest lakes:

| Lake | Area (km²) | Middle (x, y) | Kingdom | Note |
|---:|---:|---|---:|---|
| 1 | 1,909 | (1339, 2360) | 7 |  |
| 2 | 1,316 | (1559, 2519) | 7 |  |
| 3 | 1,145 | (1273, 2085) | 7 |  |
| 4 | 1,050 | (2098, 1509) | 4 | the desert's salt lake: no outlet |
| 5 | 690 | (2543, 3374) | 9 |  |
| 6 | 593 | (2070, 2999) | 8 |  |
| 7 | 492 | (1549, 266) | 2 | the flooded caldera among the volcanoes |
| 8 | 471 | (2609, 3278) | 9 |  |
| 9 | 462 | (866, 2074) | 7 |  |
| 10 | 410 | (820, 1102) | 1 |  |
| 11 | 409 | (1766, 2899) | 8 |  |
| 12 | 408 | (1152, 817) | 1 |  |

**Watersheds** (on `Rivers.png` only)

- **Brown lines 3 px wide**, 112,382 px, divide the mainland into **51 watersheds**. All the rain
  that falls inside one leaves the land at the same river mouth.
- They run from 1,789 km² to 61,803 km²; half are under 7,700 km², and 10 are over 20,000 km².
- One is the desert's closed basin, which drains to the salt lake and not to the sea.
- A river system gathering less than 1,500 km² has no watershed of its own: it is counted with the
  one beside it.
- No watershed line is drawn on any island.

### Duchies.png: the 44 duchies

- **Purple lines 3 px wide** are the borders between duchies of the same kingdom: 74,000 px, about
  7,400 km of border. Where two duchies of different kingdoms meet, the pink kingdom border is
  their border.
- A purple line stops at the pink and runs 3 px into the coast's ink, so every duchy is closed
  off.
- **Kingdoms 1, 2 and 4 have 4 duchies each; 5, 6, 8 and 9 have 5; 3 and 7 have 6.** Empty country
  (tundra, lava, desert) has few, large duchies; broken country (mountain valleys, swamp) has
  many, small ones.
- **A duchy is 11,973 to 20,322 km².** Within a kingdom the duchies are roughly equal: none is
  more than 7.8% from its kingdom's average.

Where the borders run: 13% of their length along rivers (down the middle of the stream), 7% along
or across lakes, 28% along the watershed lines of `Rivers.png`, 15% along lesser ridges between
neighbouring rivers (ridges that are in `Elevation.png` but drawn on no picture), and 37% across
open country.

Every duchy is listed under [The 44 duchies](#the-44-duchies).

### Counties.png: the 220 counties

- **Grey lines 2 px wide** are the borders between counties of the same duchy: 110,712 px, about
  17,200 km of border. Where two counties of different duchies meet, the purple or pink line is
  their border.
- A grey line stops at the purple and the pink and runs 3 px into the coast's ink, so every
  county is closed off.
- **Each duchy has 4, 5 or 6 counties**: 6 in the large duchies of kingdoms 1, 2 and 4, 4 in the
  small duchies of 3 and 7, and 5 in the rest. So every kingdom has 24 or 25 counties.
- **A county is 2,830 to 3,561 km², 3,163 km² on average**, much the same everywhere on the
  island: about 56 km across, so all of it is within a day's ride of its capital. Within a duchy
  no county is more than 4% from the duchy's average.
- **219 counties are on the mainland. The 220th is islands:** the two great islands off the Swamp
  and two islets beside them, 3,208 km², part of duchy 33. Every other islet belongs to the
  mainland county nearest it. No line is drawn on any island.

Where the borders run: 12% along rivers, 8% along or across lakes, 19% along the watershed lines,
21% along lesser ridges, and 41% across open country.

Every county is listed under
[The 220 counties and their capitals](#the-220-counties-and-their-capitals).

### Settlements.png: the 220 capitals

One dot for each county: its capital. These are the largest settlements; no smaller place is on
any picture.

| Dot | Colour | Radius | Pixels in each | How many |
|---|---|---:|---:|---:|
| Kingdom capital | pink | 13 px | 561 | 9 |
| Duchy capital | purple | 9 px | 277 | 35 |
| County capital | grey | 6 px | 129 | 176 |

- **The ranks nest.** A kingdom's capital is also the capital of its own duchy and of its own
  county, and a duchy's capital is also the capital of its own county. Each settlement has one
  dot, in the colour of the highest thing it is the capital of. So there are 220 dots, not 273:
  9 + 35 = 44 of them are duchy capitals, and all 220 are county capitals.
- **A dot is a filled disc** with hard edges. Its middle is the settlement.
- **Every dot lies wholly on the white of its own county**, with at least 2 px of white round it.
  To keep that, 12 dots stand a little off their settlement's true site, the furthest by 12 px
  (4 km).

Where the capitals stand:

- 150 of the 220 are within 4 km of a river on the map, 67 within 4 km of a lake, and 28 within
  6 km of the sea.
- They are low: half stand below 121 m. The highest is at 1,443 m.
- Neighbours are 43 km apart at the median. The closest pair is 13 km apart, and the loneliest
  capital is 67 km from its nearest neighbour.

The kingdoms' capitals:

| Kingdom | Capital (x, y) | Duchy | County | Stands on | River there (m³/s) | Height (m) | To the sea (km) |
|---:|---|---:|---:|---|---:|---:|---:|
| 1 | (981, 499) | 3 | 13 | the largest river any of its duchy capitals has, in the north of the kingdom | 167 | 538 | 64 |
| 2 | (1487, 835) | 6 | 31 | the middle of the kingdom, on the largest river any of its duchy capitals has | 239 | 172 | 68 |
| 3 | (1487, 1935) | 11 | 57 | the main valley: its lowest duchy capital, on its biggest river | 585 | 273 | 168 |
| 4 | (2031, 1515) | 17 | 85 | where the desert's river reaches the salt lake | 47 | 140 | 124 |
| 5 | (2685, 2143) | 19 | 97 | its main river, in the lowlands | 202 | 18 | 63 |
| 6 | (379, 1633) | 24 | 122 | the island's greatest river, a little above its mouth | 1,646 | 26 | 31 |
| 7 | (1102, 2596) | 29 | 147 | the harbour at the mouth of the swamp's main river | 1,090 | 0 | 4 |
| 8 | (1865, 2765) | 37 | 180 | the middle of the kingdom, on a mid-sized river | 64 | 160 | 168 |
| 9 | (2565, 3326) | 40 | 195 | its main river | 370 | 68 | 57 |

Every capital is listed under
[The 220 counties and their capitals](#the-220-counties-and-their-capitals).

### Roads.png: roads, bridges and the ferry

- **Red lines** are roads: 143,414 px. **Highways are 3 px wide**, every other road 2 px.
- **Dark brown bars** are bridges: 8,098 px in 146 marks. A bar is 2 px wider than its road, lies
  over the river and reaches 2 px on to each bank.
- **Red dashes at sea** are the ferry, 2 px wide, from the island town at (217, 2104) to the
  mainland, about 10 km (x 224 to 248, y 2082 to 2098). It is the only thing drawn on the sea in
  any picture.

**The network**

- **Every one of the 220 capitals is on it**, and any can be reached from any other.
- **About 19,600 km of road**: 5,300 km of highway and 14,300 km of other road. That is 28 m of
  road for every km² of land.
- **351 roads between neighbouring settlements**, from 13 to 125 km long, 62 km at the median,
  which share stretches where they run together. They meet at 221 forks outside the settlements.
- **A settlement has 3 roads on average**, a kingdom's capital 3.6, the busiest 6.
- **Four settlements are dead ends:** the island town and (349, 989), (2856, 2103), (2679, 1214).
- **Highways** are the cheapest ways by road between the capitals of kingdoms that share a
  border: the 15 pairs 1–2, 1–3, 1–6, 2–3, 2–4, 3–4, 3–5, 3–6, 3–7, 3–8, 4–5, 5–8, 6–7, 7–8 and
  8–9. They pass through the settlements on the way.
- Roads cross kingdom borders in about 57 places, duchy borders in about 102 and county borders
  in about 243.

**How roads treat the land**

- A road is the cheapest way over the ground between its two settlements, where steep ground,
  climbing, swamp, forest and high country all cost more. So roads keep to valleys and cross
  ranges at low passes.
- Set against straight lines between the same settlements, the roads are 12% longer, climb and
  drop 23% less, and meet a third as much water.
- Half the length of road rises less than 0.3 in 100, 99% less than 4.3 in 100, and the steepest
  stretch anywhere 10.5 in 100.
- A road that would pass within 10 km of a third settlement goes through it.
- No road touches a lake, and no road touches a river except on a bridge.

**Bridges**

- **147 bridges** (two stand so close that their marks run together, which is why there are 146
  marks).
- **103 of them, 70%, are within 4 km of a settlement.** A bridge costs more the bigger the river
  and less beside a settlement, so roads make for a town's bridge.
- By the river's size: 51 over rivers of less than 40 m³/s, 40 over 40 to 100, 37 over 100 to
  300, 13 over 300 to 800, and 6 over the largest rivers, 5 of those at a settlement.
- 51 bridges are on highways.
- **A town's bridge is drawn just outside its dot**, never hidden under it.
- A bridge crosses its river squarely. No road forks on a bridge.
- Every crossing is marked as a bridge: none is marked as a ford or a ferry.

### All.png: everything on one map

`Roads.png` with the rivers and lakes of `Water.png` laid under it. It holds the coast, the water,
the three ranks of border, the capitals, the roads, the bridges and the ferry. It does not hold
the watershed lines or the heights.

Nothing in it is new, and nothing in it is moved: every mark is where it is in the picture it
came from.

## How the layers sit on each other

From the bottom up, in `All.png`:

1. The sea, the land and the coast's ink.
2. Rivers and lakes.
3. Kingdom borders, then duchy borders, then county borders. (They never overlap each other: a
   lesser border stops where it meets a greater one.)
4. Roads.
5. Bridges.
6. The capitals' dots.

What that hides:

- **Borders hide some water.** A border that follows a river runs down the middle of it, with the
  river showing on both sides where it is wide enough. A border that crosses a lake is a line
  across the lake.
- **Bridges cover their rivers**, so in `All.png` a river is broken by each bridge over it.
- **Dots hide the water under them**, where a capital stands on a bank or a shore.
- In all, 374,429 of the water's 415,040 px show in `All.png` (90.2%). Of the rest, 19,882 are
  under grey (county borders and capitals), 13,103 under purple, 4,362 under pink and 3,264 under
  bridges.
- **Roads hide a little of the borders** where they cross them: 1,129 px of kingdom line, 1,375 px
  of duchy line and 2,139 px of county line.
- **Nothing hides a dot.** Roads run up to a dot's rim and stop.

## Reading the pictures back

- **To get a kingdom, duchy or county as a region**, fill the white from a point inside it:
  - `Kingdoms.png`: 9 pieces of mainland, and the 14 islands.
  - `Duchies.png`: 44 pieces of mainland.
  - `Counties.png` or `Settlements.png`: 219 pieces of mainland.
  The lines are closed whether a fill spreads to four neighbours or to eight. A region's area is
  its pixels times 0.1122 km², plus half the lines round it.
- **Do not fill regions in `Roads.png` or `All.png`.** Roads cut each county's white into several
  pieces, and in `All.png` so does the water.
- **To find the capitals**, take `Settlements.png` and remove what is the same in `Counties.png`:
  220 discs are left. A disc's middle is the average of its pixels, and its rank is its colour, or
  its size (561, 277 or 129 px).
- **To find the roads**, take every pixel of the roads' red or the bridges' dark brown in
  `Roads.png`. With the dots they make one connected network (join the ferry's dashes first).
- **To find the water**, take the blue of `Water.png`. Rivers and lakes are the same blue and
  cannot be told apart by colour: a river is a line 2 to 7 px wide, a lake a filled shape (the
  smallest are about 6 px across).
- **To get a height**, read `Elevation.png` at the same (x, y) and divide by 10.
- **To know which kingdom a point is in**, fill `Kingdoms.png` from it and compare with the middles
  given under [Kingdoms.png](#kingdomspng-the-nine-kingdoms).

## Decisions and assumptions

What was decided for the map before any of it was worked out:

1. The island is the size of Texas.
2. The wind comes from the west.
3. The nine regions of the sketch are each both a kingdom and a biome. That is a choice made for
   the game, not a claim about how countries form.
4. The nine kingdoms cover equal areas, keeping the sketch's arrangement.
5. Each kingdom is divided into 4 to 6 duchies of roughly equal size, and each duchy into 4 to 6
   counties of roughly equal size.
6. Between 5 and 10 percent of the land is under water, spread to suit each kingdom's biome.
7. Pink for kingdoms, purple for duchies, grey for counties, in borders and capitals alike, and
   blue for water.
8. Roads that join every settlement, follow the land and cross rivers where a road would.

What was chosen in working it out, and could be chosen otherwise:

- **The exact shades** of purple, grey and blue (the pink is the sketch's own), and the colours
  of the roads, the bridges and the watershed lines.
- **The heights.** All of `Elevation.png` is invented: the high country, the volcanoes, the flat
  swamp. The rivers, the ridges the borders follow and the roads all depend on it.
- **The rain.** The yearly run-off given to each kingdom, which sets how big its rivers are.
- **Rivers drawn from 15 m³/s up**, and the widths they are drawn at.
- **How many duchies each kingdom has**, and how many counties each duchy has (chosen so that
  counties are the same size everywhere).
- **How equal "roughly equal" is:** duchies within 8% of their kingdom's average, counties within
  4% of their duchy's.
- **Where borders run.** Each duchy and county is the land cheapest to reach from its capital,
  where crossing a river, a lake, a watershed or a ridge costs extra; that is what puts borders on
  those lines. The kingdoms' borders follow the sketch, not the land.
- **Which duchy capital is its kingdom's capital**: the one that does best on the size of its
  river, a sea harbour, and how near the kingdom's land is to it.
- **The islands as one county**, and all islands as part of the Swamp.
- **Which roads exist** (a pair of neighbouring settlements gets a road of its own unless going
  round by other roads is nearly as short), which are highways, and that every river crossing is a
  bridge.
- **Every line's width and every dot's size.**

The sizes are meant to be believable. A county of 3,163 km² is about the size of an English
county (3,300 km² on average) and what a rider can cross in a day; a duchy is five of them; a
kingdom of 77,309 km² is a little smaller than Scotland.

## What the maps do not show

- **Names.** Nothing is named: no kingdom, duchy, county, settlement, river, lake or road.
- **Smaller settlements.** Only the 220 capitals are drawn: no towns, villages, castles or ports.
- **The biomes themselves.** A kingdom's biome is known from its number; no forest, marsh, dune or
  mountain is drawn.
- **Relief.** The heights are in `Elevation.png` only; no picture draws mountains or hills.
- **Small streams.** Rivers carrying less than 15 m³/s are not drawn, so many valleys look dry.
- **Sea routes, ports and anything else at sea** but the one ferry.
- **A key, a compass, a scale bar or a grid.**

Things that may look like mistakes and are not:

- A lake with a border drawn across it is shared between the counties on its shores.
- A border that seems to vanish where it meets a river in `All.png` is running down the river.
- The duchies are less equal (within 8%) than the counties (within 4%).
- Some counties are long strips: land between a ridge and a border, or between two rivers.
- Kingdom 7's mainland is smaller than the other kingdoms' because the islands are counted with
  it.
- The grey of the county borders is also found in 101 pixels of the coast's ink.

## The 44 duchies

Duchies are numbered 1 to 44 for this file, kingdom by kingdom; the numbers are drawn on no
picture. A duchy's capital is the purple dot inside it, or the pink one if it is also its
kingdom's capital. The counties' numbers are those of the next table. Duchy 33's fourth county,
220, is the islands.

| Duchy | Kingdom | Capital (x, y) | Its dot | Area (km²) | Counties | Counties' numbers | Height at capital (m) |
|---:|---:|---|---|---:|---:|---|---:|
| 1 | 1 | (795, 919) | purple | 18,129 | 6 | 1 to 6 | 1,092 |
| 2 | 1 | (1153, 1433) | purple | 20,322 | 6 | 7 to 12 | 479 |
| 3 | 1 | (981, 499) | pink: also the kingdom's capital | 19,688 | 6 | 13 to 18 | 538 |
| 4 | 1 | (997, 1049) | purple | 19,169 | 6 | 19 to 24 | 762 |
| 5 | 2 | (1257, 433) | purple | 19,168 | 6 | 25 to 30 | 706 |
| 6 | 2 | (1487, 835) | pink: also the kingdom's capital | 18,818 | 6 | 31 to 36 | 172 |
| 7 | 2 | (1599, 271) | purple | 19,316 | 6 | 37 to 42 | 612 |
| 8 | 2 | (1545, 1181) | purple | 20,001 | 6 | 43 to 48 | 1,211 |
| 9 | 3 | (1713, 1589) | purple | 12,819 | 4 | 49 to 52 | 760 |
| 10 | 3 | (1865, 2447) | purple | 12,961 | 4 | 53 to 56 | 474 |
| 11 | 3 | (1487, 1935) | pink: also the kingdom's capital | 13,892 | 4 | 57 to 60 | 273 |
| 12 | 3 | (1743, 1971) | purple | 11,973 | 4 | 61 to 64 | 697 |
| 13 | 3 | (1337, 1693) | purple | 12,563 | 4 | 65 to 68 | 457 |
| 14 | 3 | (2017, 2023) | purple | 13,088 | 4 | 69 to 72 | 395 |
| 15 | 4 | (1837, 1108) | purple | 18,869 | 6 | 73 to 78 | 128 |
| 16 | 4 | (2557, 1277) | purple | 18,738 | 6 | 79 to 84 | 414 |
| 17 | 4 | (2031, 1515) | pink: also the kingdom's capital | 20,226 | 6 | 85 to 90 | 140 |
| 18 | 4 | (2301, 1367) | purple | 19,486 | 6 | 91 to 96 | 317 |
| 19 | 5 | (2685, 2143) | pink: also the kingdom's capital | 15,466 | 5 | 97 to 101 | 18 |
| 20 | 5 | (2235, 2485) | purple | 15,773 | 5 | 102 to 106 | 37 |
| 21 | 5 | (2769, 1796) | purple | 15,529 | 5 | 107 to 111 | 8 |
| 22 | 5 | (2301, 2269) | purple | 15,142 | 5 | 112 to 116 | 80 |
| 23 | 5 | (2335, 1905) | purple | 15,401 | 5 | 117 to 121 | 79 |
| 24 | 6 | (379, 1633) | pink: also the kingdom's capital | 15,849 | 5 | 122 to 126 | 26 |
| 25 | 6 | (997, 1791) | purple | 15,342 | 5 | 127 to 131 | 32 |
| 26 | 6 | (349, 989) | purple | 15,089 | 5 | 132 to 136 | 2 |
| 27 | 6 | (709, 1591) | purple | 15,691 | 5 | 137 to 141 | 87 |
| 28 | 6 | (441, 1195) | purple | 15,349 | 5 | 142 to 146 | 64 |
| 29 | 7 | (1102, 2596) | pink: also the kingdom's capital | 13,162 | 4 | 147 to 150 | 0 |
| 30 | 7 | (1293, 2023) | purple | 12,313 | 4 | 151 to 154 | 3 |
| 31 | 7 | (795, 2073) | purple | 13,063 | 4 | 155 to 158 | 0 |
| 32 | 7 | (1153, 2241) | purple | 12,552 | 4 | 159 to 162 | 0 |
| 33 | 7 | (475, 2118) | purple | 13,034 | 4 | 163 to 165, and 220 | 0 |
| 34 | 7 | (1464, 2528) | purple | 13,190 | 4 | 166 to 169 | 1 |
| 35 | 8 | (2201, 2741) | purple | 15,699 | 5 | 170 to 174 | 114 |
| 36 | 8 | (1527, 2755) | purple | 16,068 | 5 | 175 to 179 | 79 |
| 37 | 8 | (1865, 2765) | pink: also the kingdom's capital | 15,684 | 5 | 180 to 184 | 160 |
| 38 | 8 | (1751, 3107) | purple | 14,793 | 5 | 185 to 189 | 96 |
| 39 | 8 | (2251, 3063) | purple | 15,058 | 5 | 190 to 194 | 122 |
| 40 | 9 | (2565, 3326) | pink: also the kingdom's capital | 16,444 | 5 | 195 to 199 | 68 |
| 41 | 9 | (2545, 3805) | purple | 15,419 | 5 | 200 to 204 | 149 |
| 42 | 9 | (2081, 3615) | purple | 14,455 | 5 | 205 to 209 | 100 |
| 43 | 9 | (2829, 3529) | purple | 14,966 | 5 | 210 to 214 | 104 |
| 44 | 9 | (1925, 3363) | purple | 16,022 | 5 | 215 to 219 | 68 |

## The 220 counties and their capitals

Counties are numbered 1 to 220 for this file, duchy by duchy; the first county listed in each
duchy is the one that holds the duchy's capital. The numbers are drawn on no picture.

- **Capital (x, y)** is the middle of the county's dot.
- **Dot** is its colour: pink for a kingdom's capital, purple for a duchy's, grey for a county's.
- **Area** counts the county's share of the lines round it and any islets that belong to it.
- **Height** is the ground's at the capital.
- **Roads** is how many of the 351 roads between settlements end at the capital.
- **Sea** and **Nearest river** are straight-line distances from the capital.

| County | Duchy | Kingdom | Capital (x, y) | Dot | Area (km²) | Height (m) | Roads | Sea (km) | Nearest river (km) |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | (795, 919) | purple | 2,993 | 1,092 | 3 | 91 | 3 |
| 2 | 1 | 1 | (1008, 773) | grey | 3,000 | 1,120 | 4 | 114 | 3 |
| 3 | 1 | 1 | (681, 890) | grey | 2,956 | 880 | 3 | 69 | 21 |
| 4 | 1 | 1 | (679, 684) | grey | 3,060 | 108 | 3 | 4 | 3 |
| 5 | 1 | 1 | (778, 1074) | grey | 3,016 | 221 | 4 | 137 | 2 |
| 6 | 1 | 1 | (831, 760) | grey | 3,104 | 1,405 | 4 | 61 | 36 |
| 7 | 2 | 1 | (1153, 1433) | purple | 3,422 | 479 | 4 | 235 | 2 |
| 8 | 2 | 1 | (1291, 1503) | grey | 3,411 | 358 | 4 | 227 | 0 |
| 9 | 2 | 1 | (1025, 1478) | grey | 3,387 | 438 | 3 | 205 | 2 |
| 10 | 2 | 1 | (1149, 1252) | grey | 3,440 | 698 | 3 | 244 | 0 |
| 11 | 2 | 1 | (938, 1386) | grey | 3,319 | 356 | 3 | 177 | 3 |
| 12 | 2 | 1 | (1290, 1293) | grey | 3,343 | 775 | 3 | 223 | 22 |
| 13 | 3 | 1 | (981, 499) | pink | 3,287 | 538 | 4 | 64 | 1 |
| 14 | 3 | 1 | (946, 328) | grey | 3,266 | 238 | 2 | 24 | 1 |
| 15 | 3 | 1 | (1097, 330) | grey | 3,223 | 303 | 3 | 40 | 12 |
| 16 | 3 | 1 | (977, 661) | grey | 3,329 | 877 | 3 | 89 | 1 |
| 17 | 3 | 1 | (1115, 558) | grey | 3,249 | 1,350 | 4 | 113 | 33 |
| 18 | 3 | 1 | (809, 515) | grey | 3,334 | 1,053 | 2 | 27 | 31 |
| 19 | 4 | 1 | (997, 1049) | purple | 3,100 | 762 | 2 | 166 | 0 |
| 20 | 4 | 1 | (1187, 997) | grey | 3,211 | 1,058 | 4 | 182 | 17 |
| 21 | 4 | 1 | (1023, 1197) | grey | 3,190 | 539 | 4 | 210 | 0 |
| 22 | 4 | 1 | (1078, 1011) | grey | 3,270 | 1,318 | 4 | 177 | 18 |
| 23 | 4 | 1 | (1152, 779) | grey | 3,193 | 1,006 | 3 | 158 | 2 |
| 24 | 4 | 1 | (849, 1201) | grey | 3,206 | 1,204 | 3 | 166 | 29 |
| 25 | 5 | 2 | (1257, 433) | purple | 3,274 | 706 | 4 | 77 | 3 |
| 26 | 5 | 2 | (1244, 661) | grey | 3,119 | 1,032 | 4 | 140 | 3 |
| 27 | 5 | 2 | (1463, 617) | grey | 3,115 | 730 | 3 | 69 | 2 |
| 28 | 5 | 2 | (1223, 215) | grey | 3,196 | 20 | 3 | 4 | 3 |
| 29 | 5 | 2 | (1474, 476) | grey | 3,268 | 467 | 4 | 83 | 2 |
| 30 | 5 | 2 | (1331, 372) | grey | 3,195 | 1,197 | 2 | 65 | 28 |
| 31 | 6 | 2 | (1487, 835) | pink | 3,076 | 172 | 3 | 68 | 1 |
| 32 | 6 | 2 | (1720, 772) | grey | 3,129 | 13 | 4 | 4 | 19 |
| 33 | 6 | 2 | (1308, 795) | grey | 3,132 | 669 | 3 | 120 | 3 |
| 34 | 6 | 2 | (1297, 920) | grey | 3,143 | 771 | 2 | 137 | 3 |
| 35 | 6 | 2 | (1543, 895) | grey | 3,202 | 188 | 3 | 66 | 3 |
| 36 | 6 | 2 | (1577, 704) | grey | 3,136 | 67 | 4 | 28 | 2 |
| 37 | 7 | 2 | (1599, 271) | purple | 3,148 | 612 | 3 | 51 | 2 |
| 38 | 7 | 2 | (1475, 182) | grey | 3,200 | 225 | 2 | 32 | 3 |
| 39 | 7 | 2 | (1652, 493) | grey | 3,228 | 71 | 2 | 30 | 3 |
| 40 | 7 | 2 | (1567, 116) | grey | 3,215 | 98 | 3 | 23 | 32 |
| 41 | 7 | 2 | (1736, 158) | grey | 3,247 | 85 | 2 | 21 | 21 |
| 42 | 7 | 2 | (1535, 376) | grey | 3,279 | 336 | 2 | 71 | 2 |
| 43 | 8 | 2 | (1545, 1181) | purple | 3,269 | 1,211 | 3 | 150 | 47 |
| 44 | 8 | 2 | (1528, 1056) | grey | 3,262 | 1,204 | 4 | 114 | 29 |
| 45 | 8 | 2 | (1621, 1409) | grey | 3,428 | 465 | 3 | 165 | 1 |
| 46 | 8 | 2 | (1694, 1023) | grey | 3,344 | 456 | 3 | 88 | 28 |
| 47 | 8 | 2 | (1329, 1129) | grey | 3,310 | 912 | 3 | 172 | 2 |
| 48 | 8 | 2 | (1442, 1265) | grey | 3,387 | 668 | 5 | 189 | 2 |
| 49 | 9 | 3 | (1713, 1589) | purple | 3,210 | 760 | 4 | 187 | 2 |
| 50 | 9 | 3 | (1890, 1624) | grey | 3,286 | 881 | 3 | 173 | 3 |
| 51 | 9 | 3 | (1548, 1507) | grey | 3,205 | 932 | 4 | 204 | 13 |
| 52 | 9 | 3 | (1663, 1746) | grey | 3,118 | 1,081 | 4 | 241 | 3 |
| 53 | 10 | 3 | (1865, 2447) | purple | 3,238 | 474 | 4 | 194 | 2 |
| 54 | 10 | 3 | (2005, 2360) | grey | 3,236 | 1,112 | 3 | 157 | 21 |
| 55 | 10 | 3 | (1767, 2399) | grey | 3,325 | 361 | 3 | 217 | 1 |
| 56 | 10 | 3 | (1749, 2283) | grey | 3,163 | 490 | 4 | 233 | 3 |
| 57 | 11 | 3 | (1487, 1935) | pink | 3,561 | 273 | 3 | 168 | 2 |
| 58 | 11 | 3 | (1589, 2185) | grey | 3,473 | 746 | 4 | 182 | 2 |
| 59 | 11 | 3 | (1519, 2045) | grey | 3,371 | 462 | 4 | 168 | 3 |
| 60 | 11 | 3 | (1510, 1827) | grey | 3,487 | 986 | 3 | 192 | 3 |
| 61 | 12 | 3 | (1743, 1971) | purple | 2,933 | 697 | 3 | 246 | 0 |
| 62 | 12 | 3 | (1668, 1896) | grey | 2,977 | 650 | 4 | 229 | 2 |
| 63 | 12 | 3 | (1717, 2080) | grey | 3,068 | 812 | 4 | 231 | 3 |
| 64 | 12 | 3 | (1822, 1804) | grey | 2,994 | 1,443 | 2 | 237 | 3 |
| 65 | 13 | 3 | (1337, 1693) | purple | 3,107 | 457 | 3 | 180 | 2 |
| 66 | 13 | 3 | (1413, 1506) | grey | 3,115 | 791 | 3 | 241 | 2 |
| 67 | 13 | 3 | (1469, 1689) | grey | 3,152 | 982 | 3 | 210 | 1 |
| 68 | 13 | 3 | (1163, 1660) | grey | 3,189 | 139 | 3 | 162 | 1 |
| 69 | 14 | 3 | (2017, 2023) | purple | 3,264 | 395 | 2 | 220 | 1 |
| 70 | 14 | 3 | (1889, 2173) | grey | 3,254 | 1,200 | 4 | 221 | 15 |
| 71 | 14 | 3 | (1923, 2029) | grey | 3,249 | 906 | 4 | 241 | 2 |
| 72 | 14 | 3 | (2019, 1847) | grey | 3,321 | 1,098 | 4 | 234 | 12 |
| 73 | 15 | 4 | (1837, 1108) | purple | 3,148 | 128 | 3 | 54 | 4 |
| 74 | 15 | 4 | (1872, 863) | grey | 3,156 | 46 | 3 | 29 | over 60 |
| 75 | 15 | 4 | (1865, 1153) | grey | 3,099 | 114 | 3 | 51 | 2 |
| 76 | 15 | 4 | (2031, 983) | grey | 3,138 | 9 | 2 | 4 | 47 |
| 77 | 15 | 4 | (1816, 1298) | grey | 3,200 | 118 | 5 | 90 | 1 |
| 78 | 15 | 4 | (2014, 1131) | grey | 3,126 | 8 | 3 | 4 | 3 |
| 79 | 16 | 4 | (2557, 1277) | purple | 3,123 | 414 | 4 | 49 | over 60 |
| 80 | 16 | 4 | (2413, 1020) | grey | 3,107 | 45 | 2 | 4 | over 60 |
| 81 | 16 | 4 | (2539, 1500) | grey | 3,072 | 370 | 3 | 91 | over 60 |
| 82 | 16 | 4 | (2679, 1214) | grey | 3,144 | 16 | 1 | 4 | over 60 |
| 83 | 16 | 4 | (2678, 1429) | grey | 3,184 | 530 | 2 | 38 | over 60 |
| 84 | 16 | 4 | (2458, 1190) | grey | 3,108 | 252 | 3 | 60 | over 60 |
| 85 | 17 | 4 | (2031, 1515) | pink | 3,338 | 140 | 5 | 124 | 3 |
| 86 | 17 | 4 | (2217, 1626) | grey | 3,379 | 178 | 4 | 160 | 46 |
| 87 | 17 | 4 | (1941, 1324) | grey | 3,424 | 95 | 3 | 73 | 3 |
| 88 | 17 | 4 | (1798, 1445) | grey | 3,338 | 465 | 3 | 131 | 31 |
| 89 | 17 | 4 | (2120, 1480) | grey | 3,369 | 87 | 3 | 109 | 28 |
| 90 | 17 | 4 | (2136, 1731) | grey | 3,378 | 598 | 3 | 193 | 27 |
| 91 | 18 | 4 | (2301, 1367) | purple | 3,180 | 317 | 3 | 85 | over 60 |
| 92 | 18 | 4 | (2400, 1619) | grey | 3,253 | 197 | 3 | 137 | over 60 |
| 93 | 18 | 4 | (2213, 1114) | grey | 3,197 | 12 | 3 | 4 | 60 |
| 94 | 18 | 4 | (2144, 1306) | grey | 3,304 | 65 | 5 | 51 | 45 |
| 95 | 18 | 4 | (2333, 1244) | grey | 3,272 | 133 | 3 | 61 | over 60 |
| 96 | 18 | 4 | (2375, 1469) | grey | 3,279 | 375 | 3 | 127 | over 60 |
| 97 | 19 | 5 | (2685, 2143) | pink | 3,060 | 18 | 4 | 63 | 1 |
| 98 | 19 | 5 | (2529, 2114) | grey | 3,045 | 38 | 3 | 107 | 1 |
| 99 | 19 | 5 | (2856, 2103) | grey | 3,088 | 8 | 1 | 4 | 34 |
| 100 | 19 | 5 | (2688, 2007) | grey | 3,169 | 58 | 4 | 53 | 32 |
| 101 | 19 | 5 | (2699, 2303) | grey | 3,104 | 44 | 2 | 25 | 44 |
| 102 | 20 | 5 | (2235, 2485) | purple | 3,124 | 37 | 4 | 70 | 3 |
| 103 | 20 | 5 | (2499, 2455) | grey | 3,101 | 2 | 3 | 4 | 2 |
| 104 | 20 | 5 | (2431, 2605) | grey | 3,190 | 2 | 3 | 5 | 1 |
| 105 | 20 | 5 | (2128, 2406) | grey | 3,136 | 70 | 2 | 113 | 0 |
| 106 | 20 | 5 | (2219, 2587) | grey | 3,222 | 27 | 4 | 72 | 2 |
| 107 | 21 | 5 | (2769, 1796) | purple | 3,106 | 8 | 2 | 4 | 11 |
| 108 | 21 | 5 | (2597, 1765) | grey | 3,147 | 65 | 4 | 56 | 47 |
| 109 | 21 | 5 | (2863, 1588) | grey | 3,106 | 12 | 2 | 4 | over 60 |
| 110 | 21 | 5 | (2664, 1612) | grey | 3,083 | 198 | 4 | 68 | over 60 |
| 111 | 21 | 5 | (2740, 1830) | grey | 3,088 | 3 | 3 | 4 | 2 |
| 112 | 22 | 5 | (2301, 2269) | purple | 3,014 | 80 | 3 | 95 | 3 |
| 113 | 22 | 5 | (2393, 2162) | grey | 2,979 | 80 | 5 | 108 | 30 |
| 114 | 22 | 5 | (2530, 2328) | grey | 3,078 | 31 | 4 | 44 | 31 |
| 115 | 22 | 5 | (2214, 2068) | grey | 2,961 | 105 | 5 | 165 | 2 |
| 116 | 22 | 5 | (2204, 2213) | grey | 3,110 | 108 | 2 | 131 | 3 |
| 117 | 23 | 5 | (2335, 1905) | purple | 3,128 | 79 | 4 | 141 | 3 |
| 118 | 23 | 5 | (2441, 1748) | grey | 3,007 | 102 | 3 | 108 | over 60 |
| 119 | 23 | 5 | (2516, 1897) | grey | 3,043 | 69 | 6 | 81 | 56 |
| 120 | 23 | 5 | (2186, 1920) | grey | 3,166 | 116 | 3 | 191 | 3 |
| 121 | 23 | 5 | (2379, 2022) | grey | 3,057 | 57 | 4 | 138 | 3 |
| 122 | 24 | 6 | (379, 1633) | pink | 3,176 | 26 | 5 | 31 | 2 |
| 123 | 24 | 6 | (427, 1859) | grey | 3,169 | 23 | 4 | 55 | 0 |
| 124 | 24 | 6 | (489, 1631) | grey | 3,257 | 39 | 3 | 50 | 1 |
| 125 | 24 | 6 | (207, 1578) | grey | 3,109 | 7 | 2 | 4 | 30 |
| 126 | 24 | 6 | (265, 1786) | grey | 3,138 | 11 | 4 | 4 | 26 |
| 127 | 25 | 6 | (997, 1791) | purple | 3,107 | 32 | 4 | 110 | 3 |
| 128 | 25 | 6 | (1125, 1805) | grey | 2,986 | 94 | 3 | 112 | 12 |
| 129 | 25 | 6 | (885, 1802) | grey | 3,110 | 147 | 3 | 108 | 1 |
| 130 | 25 | 6 | (756, 1831) | grey | 3,019 | 123 | 3 | 93 | 2 |
| 131 | 25 | 6 | (935, 1624) | grey | 3,120 | 142 | 4 | 166 | 1 |
| 132 | 26 | 6 | (349, 989) | purple | 3,020 | 2 | 1 | 4 | 0 |
| 133 | 26 | 6 | (516, 910) | grey | 2,931 | 72 | 3 | 44 | 1 |
| 134 | 26 | 6 | (476, 752) | grey | 3,025 | 14 | 2 | 4 | 1 |
| 135 | 26 | 6 | (412, 1085) | grey | 3,031 | 100 | 5 | 41 | 13 |
| 136 | 26 | 6 | (224, 1177) | grey | 3,081 | 14 | 2 | 25 | 3 |
| 137 | 27 | 6 | (709, 1591) | purple | 3,081 | 87 | 2 | 107 | 2 |
| 138 | 27 | 6 | (634, 1429) | grey | 3,065 | 174 | 4 | 74 | 0 |
| 139 | 27 | 6 | (585, 1611) | grey | 3,197 | 52 | 4 | 74 | 2 |
| 140 | 27 | 6 | (655, 1721) | grey | 3,147 | 93 | 3 | 113 | 2 |
| 141 | 27 | 6 | (840, 1479) | grey | 3,201 | 242 | 4 | 143 | 3 |
| 142 | 28 | 6 | (441, 1195) | purple | 3,144 | 64 | 4 | 65 | 2 |
| 143 | 28 | 6 | (614, 1126) | grey | 3,071 | 112 | 3 | 102 | 2 |
| 144 | 28 | 6 | (482, 1397) | grey | 3,043 | 173 | 6 | 27 | 3 |
| 145 | 28 | 6 | (290, 1285) | grey | 3,077 | 44 | 3 | 13 | 3 |
| 146 | 28 | 6 | (644, 1225) | grey | 3,014 | 210 | 5 | 102 | 2 |
| 147 | 29 | 7 | (1102, 2596) | pink | 3,356 | 0 | 2 | 5 | 5 |
| 148 | 29 | 7 | (1006, 2519) | grey | 3,290 | 0 | 2 | 4 | 17 |
| 149 | 29 | 7 | (1248, 2693) | grey | 3,276 | 1 | 2 | 40 | 2 |
| 150 | 29 | 7 | (1182, 2578) | grey | 3,239 | 0 | 4 | 31 | 3 |
| 151 | 30 | 7 | (1293, 2023) | purple | 3,125 | 3 | 3 | 97 | 2 |
| 152 | 30 | 7 | (1094, 2023) | grey | 3,056 | 0 | 3 | 42 | 0 |
| 153 | 30 | 7 | (1366, 2135) | grey | 3,062 | 4 | 4 | 114 | 3 |
| 154 | 30 | 7 | (1166, 1930) | grey | 3,070 | 1 | 3 | 82 | 3 |
| 155 | 31 | 7 | (795, 2073) | purple | 3,257 | 0 | 2 | 22 | 1 |
| 156 | 31 | 7 | (784, 1982) | grey | 3,191 | 2 | 3 | 51 | 2 |
| 157 | 31 | 7 | (929, 2030) | grey | 3,349 | 1 | 3 | 30 | 2 |
| 158 | 31 | 7 | (611, 2036) | grey | 3,267 | 1 | 2 | 21 | 1 |
| 159 | 32 | 7 | (1153, 2241) | purple | 3,061 | 0 | 4 | 35 | 0 |
| 160 | 32 | 7 | (1399, 2316) | grey | 3,190 | 2 | 4 | 117 | 2 |
| 161 | 32 | 7 | (1058, 2279) | grey | 3,134 | 0 | 2 | 3 | 3 |
| 162 | 32 | 7 | (1204, 2323) | grey | 3,167 | 1 | 3 | 54 | 2 |
| 163 | 33 | 7 | (475, 2118) | purple | 3,234 | 0 | 2 | 4 | 2 |
| 164 | 33 | 7 | (441, 1998) | grey | 3,324 | 1 | 3 | 41 | 2 |
| 165 | 33 | 7 | (308, 2004) | grey | 3,267 | 1 | 3 | 20 | 3 |
| 166 | 34 | 7 | (1464, 2528) | purple | 3,317 | 1 | 3 | 122 | 3 |
| 167 | 34 | 7 | (1651, 2464) | grey | 3,294 | 5 | 3 | 175 | 2 |
| 168 | 34 | 7 | (1434, 2356) | grey | 3,352 | 3 | 3 | 131 | 3 |
| 169 | 34 | 7 | (1502, 2534) | grey | 3,227 | 1 | 2 | 127 | 1 |
| 170 | 35 | 8 | (2201, 2741) | purple | 3,126 | 114 | 4 | 94 | 3 |
| 171 | 35 | 8 | (2389, 2870) | grey | 3,190 | 35 | 2 | 37 | 3 |
| 172 | 35 | 8 | (2086, 2656) | grey | 3,134 | 180 | 4 | 121 | 3 |
| 173 | 35 | 8 | (2331, 2752) | grey | 3,054 | 91 | 3 | 57 | 14 |
| 174 | 35 | 8 | (2129, 2912) | grey | 3,194 | 352 | 5 | 120 | 25 |
| 175 | 36 | 8 | (1527, 2755) | purple | 3,235 | 79 | 3 | 74 | 12 |
| 176 | 36 | 8 | (1407, 2964) | grey | 3,169 | 36 | 2 | 4 | over 60 |
| 177 | 36 | 8 | (1598, 2711) | grey | 3,149 | 85 | 4 | 102 | 3 |
| 178 | 36 | 8 | (1610, 2928) | grey | 3,208 | 171 | 4 | 72 | 3 |
| 179 | 36 | 8 | (1351, 2799) | grey | 3,307 | 96 | 3 | 25 | 34 |
| 180 | 37 | 8 | (1865, 2765) | pink | 3,103 | 160 | 4 | 168 | 3 |
| 181 | 37 | 8 | (1843, 2583) | grey | 3,119 | 142 | 2 | 193 | 15 |
| 182 | 37 | 8 | (1873, 2910) | grey | 3,153 | 261 | 5 | 125 | 3 |
| 183 | 37 | 8 | (1951, 2767) | grey | 3,149 | 193 | 3 | 175 | 0 |
| 184 | 37 | 8 | (1740, 2731) | grey | 3,160 | 116 | 2 | 138 | 3 |
| 185 | 38 | 8 | (1751, 3107) | purple | 2,972 | 96 | 3 | 47 | 2 |
| 186 | 38 | 8 | (1682, 3151) | grey | 2,950 | 69 | 2 | 27 | 1 |
| 187 | 38 | 8 | (1610, 3031) | grey | 3,040 | 180 | 2 | 48 | 24 |
| 188 | 38 | 8 | (1936, 3106) | grey | 2,932 | 400 | 3 | 91 | 21 |
| 189 | 38 | 8 | (1842, 3208) | grey | 2,899 | 378 | 4 | 47 | 29 |
| 190 | 39 | 8 | (2251, 3063) | purple | 2,985 | 122 | 3 | 83 | 3 |
| 191 | 39 | 8 | (2436, 3056) | grey | 3,030 | 154 | 2 | 23 | 28 |
| 192 | 39 | 8 | (2094, 3045) | grey | 2,960 | 222 | 3 | 134 | 3 |
| 193 | 39 | 8 | (2339, 2949) | grey | 2,987 | 66 | 4 | 49 | 3 |
| 194 | 39 | 8 | (2186, 3216) | grey | 3,096 | 189 | 3 | 123 | 4 |
| 195 | 40 | 9 | (2565, 3326) | pink | 3,237 | 68 | 2 | 56 | 0 |
| 196 | 40 | 9 | (2415, 3409) | grey | 3,347 | 168 | 4 | 104 | 3 |
| 197 | 40 | 9 | (2540, 3428) | grey | 3,205 | 118 | 2 | 84 | 1 |
| 198 | 40 | 9 | (2649, 3283) | grey | 3,353 | 74 | 3 | 26 | 14 |
| 199 | 40 | 9 | (2469, 3179) | grey | 3,301 | 69 | 3 | 37 | 2 |
| 200 | 41 | 9 | (2545, 3805) | purple | 3,108 | 149 | 3 | 25 | 2 |
| 201 | 41 | 9 | (2421, 3754) | grey | 3,125 | 166 | 2 | 23 | 23 |
| 202 | 41 | 9 | (2750, 3864) | grey | 3,023 | 63 | 2 | 4 | 20 |
| 203 | 41 | 9 | (2617, 3666) | grey | 3,066 | 407 | 4 | 72 | 20 |
| 204 | 41 | 9 | (2391, 3656) | grey | 3,097 | 90 | 5 | 48 | 0 |
| 205 | 42 | 9 | (2081, 3615) | purple | 2,924 | 100 | 3 | 24 | 1 |
| 206 | 42 | 9 | (2230, 3724) | grey | 2,877 | 120 | 3 | 22 | 1 |
| 207 | 42 | 9 | (2279, 3522) | grey | 2,971 | 208 | 4 | 90 | 1 |
| 208 | 42 | 9 | (2072, 3494) | grey | 2,854 | 200 | 3 | 56 | 2 |
| 209 | 42 | 9 | (2066, 3722) | grey | 2,830 | 23 | 2 | 5 | 2 |
| 210 | 43 | 9 | (2829, 3529) | purple | 2,927 | 104 | 4 | 4 | 0 |
| 211 | 43 | 9 | (2874, 3344) | grey | 3,050 | 160 | 2 | 13 | 3 |
| 212 | 43 | 9 | (2898, 3692) | grey | 2,996 | 77 | 2 | 16 | 2 |
| 213 | 43 | 9 | (2787, 3687) | grey | 2,955 | 112 | 5 | 33 | 2 |
| 214 | 43 | 9 | (2674, 3510) | grey | 3,038 | 228 | 5 | 49 | 3 |
| 215 | 44 | 9 | (1925, 3363) | purple | 3,148 | 68 | 4 | 51 | 3 |
| 216 | 44 | 9 | (1721, 3339) | grey | 3,160 | 4 | 2 | 4 | 2 |
| 217 | 44 | 9 | (2207, 3369) | grey | 3,201 | 196 | 4 | 116 | 2 |
| 218 | 44 | 9 | (2239, 3289) | grey | 3,235 | 144 | 2 | 122 | 2 |
| 219 | 44 | 9 | (1898, 3430) | grey | 3,277 | 55 | 2 | 27 | 3 |
| 220 | 33 | 7 | (217, 2104) | grey | 3,208 | 0 | 1 | 3 | 35 |
