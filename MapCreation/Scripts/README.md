# The programs that made the world map

The pictures in the folder above, the data in `../SourceData/` and `../Features.md` were all made
by program. This folder holds those programs, and the ones that checked their work, as they
stood when the map was finished on 2026-10-07. They are kept so that how the map was made is not
lost, and so that a part of it can be made again or changed.

They are working programs, not a product:

- **No one command makes the map.** It was made a step at a time over two days, each step run
  by hand, looked at and often run again. [How the map was made](#how-the-map-was-made) gives
  the steps in order, each with what it was given.
- **Most steps read what earlier steps left** in a working folder, which is not in the
  repository. [What the programs need](#what-the-programs-need) says what it held. It can be
  made again: every step, run again from here, gave what it first gave
  ([Run again from this folder](#run-again-from-this-folder)).
- **The checks of the finished pictures need nothing but the pictures**, and run from here as
  they are: [The checks](#the-checks).

## What is here

143 programs and written parts in three groups, as they were kept while the map was made,
with this file and `requirements.txt`. A fourth group of five, `scene/`, was added the same day,
when the finished map was made into a scene for the game.

| Folder | Files | Holds |
|---|---:|---|
| this folder | 20 | The sketch read, and the kingdoms' first lines: nine kingdoms of equal area, on smooth lines close to the sketch's |
| `water/` | 10 | The heights of the land, and the rivers, lakes and watersheds worked out on them |
| `duchy/` | 113 | Everything after that. It is named for the first thing made in it, the duchies, and holds the counties, settlements and roads, the kingdoms' borders as they are now, the picture of everything, the standard outline, the source data and the document as well |
| `scene/` | 5 | The map made into the game's scene, `vcom/Scenes/Map.tscn`: its areas and lines worked out of the source data as shapes, and the scene written from them |
| `icons/` | 6 | Proposals for the settlements' icons, drawn in the manner of the MWM icon pack: added on 2026-10-08, and not part of making the map |

A program finds the others it leans on beside it, so the files of a group have to stay together.
[Every file](#every-file) lists them all.

## What the programs need

- **Python 3.14** with numpy, scipy, Pillow and scikit-image. `requirements.txt` gives the
  versions they were run with, on Windows.
- **Folders, given on the command line.** No program has this machine's folders written into
  it; each says at its top (`Usage:`) what it is given. Below, `<repo>` is the repository,
  `<work>` the working folder, and a program is run as `python <program> <what it is given>`.
- **A working folder**, for all but a few. Each step leaves grids and lists there for the next:

| In `<work>/` | Left by | Holds |
|---|---|---|
| `out/` | this folder's programs | The sketch's regions and the kingdoms' first lines, as grids and curves |
| `out/water/` | `water/` | The land and the kingdoms as grids, the heights, the drainage, the lakes, rivers and watersheds |
| `out/duchy/`, `out/roads/` | step 4 | The first duchies, counties, settlements and roads, on the kingdoms' first lines |
| `out/king30/`, `out/kb30/` | step 5 | The lines of the land a border can follow, and the kingdoms' borders laid along them |
| `out/duchy2/`, `out/roads2/` | step 6 | The duchies, counties, settlements and roads as they are |
| a folder of facts | steps 7, 8 and 10 | The figures measured for the document |
| a staging folder | by hand | A `MapCreation/` of pictures being built, standing in for the repository's until they were checked |

**The working folder is not in the repository.** It ran to 2.8 GB with its drafts and trial
pictures. So a step in the middle cannot be run from the repository alone: everything before
it has to be run first, in order, which takes about an hour and a quarter and gives the same
working data again ([Run again from this folder](#run-again-from-this-folder)). What mattered
in it is also in `../SourceData/`, in other shapes, which a program here would have to be
taught to read before it could start from them.

## How the map was made

Ten steps, and an eleventh that made the game's scene from the finished map. Each table gives a
program, what it was given the last time it was run, and what it left. A name in the last column
with no folder is a file in the working folder named in the step's heading.

### 1. The sketch read

This folder; `<work>/out/`.

| Program | Given | Leaves |
|---|---|---|
| `analyze3.py` | `<repo> <work>/out` | `region_map.npy`: the sketch's region of every pixel of the mainland, with the gaps in its lines closed |

`analyze1.py`, `analyze2.py`, `analyze4.py`, `analyze5.py` and `scale.py` looked at the two
hand-drawn pictures first: how the sketch's lines close, how the new shape lies to the map the
game has now, and what a pixel comes to on an island the size of Texas.

### 2. The kingdoms' first lines

This folder; `<work>/out/`.

| Program | Given | Leaves |
|---|---|---|
| `kingdoms1.py` | `<repo> <work>/out` | `start_map.npy`: the sketched regions, smoothed, to start from |
| `kingdoms2.py` | `<repo> <work>/out` | `kingdom_map_flow.npy`: the land flowed within its own coast until the nine areas are equal, which says where everything should go |
| `net_build.py` | `<repo> <work>/out` | `network.pickle`: the sketch's borders as curves that can be moved |
| `make_kingdoms.py` | `<repo> <work>/out <work>/out/Kingdoms_draft.png 5` | A picture of nine kingdoms of equal area on smooth lines, 5 px wide; `kingdoms_final.npy`, `kingdoms_final_lines.pickle` |

That picture was the folder's `Kingdoms.png` until the borders of step 5 took its place, and it
is what steps 3 and 4 read under that name. Git has it still (commit d62e6e5), and its nine
regions are `../SourceData/TerrainMap.png`.

`kingdoms3.py`, `kingdoms4.py` and `draw_kingdoms.py` are ways of evening the areas that were
tried before `make_kingdoms.py`.

### 3. The heights and the water

`water/`; `<work>/out/water/`.

| Program | Given | Leaves |
|---|---|---|
| `w0_grids.py` | `<repo> <work>/out/water` | `grid1.npz`, `grid2.npz`, `grid4.npz`: the land and the nine kingdoms as grids, at the map's size, a half and a quarter |
| `w2_drain.py` | `<work>/out/water 2` | `drain2.npz`: a height for every cell and the way water leaves it, made together to suit each kingdom's biome |
| `w3_water.py` | `<work>/out/water 2 1.0 15` | `water2.pickle`: the lakes, the water through every cell, the river lines, the watersheds |
| `w4_draw.py` | `<repo> <work>/out/water 2 <work>/out/water/Rivers_draft2.png look` | The rivers' picture as a draft; `drawn2.npz`: rivers, lakes, watershed lines and watersheds at the map's size |
| `w5_finish.py` | `<repo> <work>/out/water 2 <work>/out/water/Rivers_draft2.png` | **Writes `Rivers.png` and `Elevation.png` into `<repo>/MapCreation/`** |
| `w6_water_only.py` | `<repo>` | **Writes `Water.png` into `<repo>/MapCreation/`** |

The 2 is the grid, half the map's size. 1.0 is the lakes' size as designed, and 15 the least
flow drawn as a river, in m³/s. `w1_terrain.py` is how the land was made at first, noise worn
by its own rivers; it gave straight rivers and was dropped.

### 4. Duchies, counties, settlements and roads, the first time

`duchy/`; `<work>/out/duchy/` and `<work>/out/roads/`.

This was done on the kingdoms' first lines. The pictures it made were replaced by step 6's
(git has them still, in commit d62e6e5), but what it left in the working folder still counts:
step 5 moves the kingdoms' borders by the rivers and ridges found here, and step 6 keeps every
duchy's capital and what counties it can.

| Program | Given | Leaves |
|---|---|---|
| `d1_fields.py` | `<repo> <work>/out/water <work>/out/duchy` | `fields1.npz`, `fields2.npz`: the ground as a traveller meets it, at the map's size and at half |
| `d1b_ridges.py` | `<work>/out/water <work>/out/duchy` | Adds the ridges between neighbouring rivers to those two |
| `d2_solve.py` | `<work>/out/duchy` | `duchies_all.pickle`: each kingdom shared out among its duchies |
| `d3_draw.py` | `<repo> <work>/out/duchy <picture>` | The duchies' picture; `duchy_map.npy` |
| `c1_counties.py` | `<work>/out/duchy f3 1.0 0.03` | `counties_f3.pickle`: each duchy shared out among its counties |
| `c2_draw.py` | `<repo> <work>/out/duchy f3 <picture>` | The counties' picture; `county_map_f3.npy`, `county_list_f3.pickle` |
| `s1_candidates.py` | `<work>/out/water <work>/out/duchy` | `capital_candidates.pickle`: what each duchy's capital has going for it as its kingdom's |
| `s2_settlements.py` | `<repo> <work>/out/duchy <picture>` | The settlements' picture; `settlements.pickle` |
| `r1_ground.py`, `r2_candidates.py`, `r3_network.py` | as in step 6, on `<work>/out/duchy` and `<work>/out/roads` | The first road network |

`f3` names the run, the third of its kind. 1.0 is what crossing a river, a lake or a ridge
costs, as a share of the full price, and 0.03 how near to equal a duchy's counties must come.

### 5. The kingdoms' borders moved on to the land's lines

`duchy/`; `<work>/out/king30/` and `<work>/out/kb30/`.

| Program | Given | Leaves |
|---|---|---|
| `k1_fields.py` | `<work>/out/water <work>/out/duchy <work>/out/king30 30` | `fields.npz`: the small lines of the land (brooks and spurs), the foot of the high country, and the band 30 km either side of a first line in which a border may move |
| `kb1_network.py` | `<work>/out/duchy <work>/out/kb30 30 22` | `network.pickle`, `near.npz`: the fifteen borders, the seven places where three kingdoms meet, and the zone each new line may run in. A meeting place may move 22 km |
| `kb2_paths.py` | `<work>/out/duchy <work>/out/king30 <work>/out/kb30 u3 spare=0.0025` | In `king30/`, `lines_u3.pickle` and `kingdoms_u3.npy`: each border the cheapest line through its zone, and no kingdom more than a quarter of a percent from a ninth of the land |
| `k3_draw.py` | `<repo> <work>/out/duchy <work>/out/king30 u3 <picture>` | The kingdoms' picture as it is now |

`u3` names the run. `k2_solve.py`, with `run_kingdoms.sh`, is the method tried before this one,
which shared the land out afresh; it was dropped.

### 6. Everything under the kingdoms, made again

`duchy/`; `<work>/out/duchy2/` and `<work>/out/roads2/`.

| Program | Given | Leaves |
|---|---|---|
| `n1_fields.py` | `<work>/out/duchy <work>/out/king30/kingdoms_u3.npy <work>/out/duchy2` | `fields1.npz`, `fields2.npz` for the kingdoms as they now are |
| `n2_duchies.py` | `<work>/out/duchy <work>/out/duchy2` | `duchies_all.pickle`: each kingdom shared out again, every duchy keeping its capital |
| `d3_draw.py` | `<stage> <work>/out/duchy2 <stage>/MapCreation/Duchies.png` | `Duchies.png`; `duchy_map.npy` |
| `n3_counties.py` | `<work>/out/duchy <work>/out/duchy2 f3` | `counties_f3.pickle`: each duchy shared out again, keeping its counties where they still make good ones |
| `c2_draw.py` | `<stage> <work>/out/duchy2 f3 <stage>/MapCreation/Counties.png` | `Counties.png`; `county_map_f3.npy`, `county_list_f3.pickle` |
| `s1_candidates.py` | `<work>/out/water <work>/out/duchy2` | `capital_candidates.pickle` |
| `s2_settlements.py` | `<stage> <work>/out/duchy2 <stage>/MapCreation/Settlements.png` | `Settlements.png`; `settlements.pickle` |
| `r1_ground.py` | `<work>/out/water <work>/out/duchy2 <work>/out/roads2` | The ground as a road-builder meets it: ten grids (`land.npy`, `river.npy`, `going.npy` and the rest) and `towns.pickle` |
| `r2_candidates.py` | `<work>/out/roads2` | `candidates.pickle`: every pair of neighbouring settlements, and the road between them by itself |
| `r3_network.py` | `<work>/out/duchy2 <work>/out/roads2` | `network.pickle`: which roads there are, and where each runs |

- `<stage>` was a folder with a `MapCreation/` in it that held the pictures under the names the
  programs read, the kingdoms' new picture as `Kingdoms.png` among them. The repository does in
  its place now.
- **`n3_counties.py` was run three times**, and the map's counties are what the three gave
  together:
  1. for every duchy, as in the table;
  2. for the isles' duchy alone, held closer to equal, with `33` as one more thing given and
     `N3_NEAR=0.015` in the environment; then `n3_merge.py <work>/out/duchy2 f3` to fold it in;
  3. for three duchies alone with a longer search, with `22,24,35` given and `N3_FINISHED=12` in
     the environment, after the two rules about capitals that `n3_gates.py` checks were added;
     then `n3_merge.py` again.

  `N3_NEAR` and `N3_FINISHED` are the only things any program here reads from the environment.
  Run for every duchy alone, the program gives the map's counties in 43 of the 44 duchies: the
  isles' duchy, 33, comes out less even (within 3.1%, where the map has 1.1%) until it is run
  again as in 2. The program as it is now gives the three duchies of 3 their counties in the
  first run already, so made again the third run changes nothing.

### 7. The roads drawn, and everything on one map

`duchy/`.

| Program | Given | Leaves |
|---|---|---|
| `r5b_draw.py` | `<stage> <work>/out/duchy2 <work>/out/roads2 <stage>/MapCreation/Roads.png` | `Roads.png`; in `roads2/`, `drawn.pickle`: the bridges and the stretches of road as drawn |
| `a2_all.py` | `<stage>/MapCreation <work>/out/roads2/lake.npy <stage>/MapCreation/All.png <facts>/layers.json` | `All.png`; `layers.json` |

`layers.py`, which both lean on, is the rule that no line hides another.

### 8. The standard outline

`duchy/`. These two read nothing but the pictures.

| Program | Given | Leaves |
|---|---|---|
| `y8_continent.py` | `<repo>/MapCreation <picture> <facts>/continent.json` | `Continent.png`; `continent.json` |
| `z2_allsimple.py` | `<repo>/MapCreation <picture> <facts>/allsimple.json` | `AllSimple.png`; `allsimple.json` |

### 9. The source data

`duchy/`. In this order: each reads what the one before wrote into the folder.

| Program | Given | Leaves in the folder |
|---|---|---|
| `e2_regions.py` | `<repo>/MapCreation <work>/out <folder>` | The four maps of regions, `Regions.json`, `Settlements.json` |
| `e3_water.py` | the same | `Rivers.json`, the lakes, the watersheds, the drainage, the three masks, `TerrainMap.png`, `SketchRegionMap.png` |
| `e4_roads.py` | the same | `Roads.json` |
| `f14_facts6.py` | as in step 10 | Nothing here: it makes the facts the next one copies in |
| `e5_borders.py` | `<repo>/MapCreation <work>/out <folder> <new facts>` | `KingdomBorders.json`, `Measurements.json` |
| `e11_readme.py` | `duchy/SourceData.README.template.md <folder>` | `README.md` |

### 10. The document

`duchy/`.

| Program | Given | Leaves |
|---|---|---|
| `f1_facts.py` | `<repo> <work>/out/water <work>/out/duchy2 <work>/out/roads2 <facts>` | `facts.json`, and the three long tables as Markdown |
| `f2_more.py` | the same | Prints more figures, which were typed into the written part |
| `f14_facts6.py` | `<work>/out <the source data's folder> <facts> <new facts>` | `facts.json` again, the rivers counted and measured as they are drawn |
| `f3_build.py` | `<work>/out/duchy2 <new facts> duchy/Features.template.md <file>` | `Features.md` |
| `f8c_check.py` | `<repo> <work>/out/duchy2 <work>/out/roads2 <new facts> <repo>/MapCreation/Features.md` | Nothing: it holds every figure typed into the written part against what was measured |

`<facts>` also wants `layers.json`, `continent.json` and `allsimple.json` from steps 7 and 8,
which were copied into it by hand.

### 11. The scene

`scene/`. This step needs no working folder: it reads `../SourceData/` and nothing else, and
takes half a minute.

| Program | Given | Leaves |
|---|---|---|
| `m1_shapes.py` | `<repo>/MapCreation <a file>` | The map as shapes, in a `.json` file: the counties' outlines, the coast, the borders, the lakes, rivers, roads, bridges and settlements, in the pictures' own pixels |
| `m2_scene.gd` | by Godot, from `vcom/`: `godot --headless --path . --script ../MapCreation/Scripts/scene/m2_scene.gd -- <that file>` | `vcom/Scenes/Map.tscn`, the scene |

What `m1_shapes.py` does, in the order it does it:

- **Mends the counties' map** (`CountyMap.png`, as it reads it; the file is left alone). Eight
  pixels at about (2685, 2400), where the coast was mended and a strip of land changed county,
  left a hook in a duchy's border at the shore: they are given to the county across it. And a
  tongue of a county one pixel wide, whatever its length, goes to the county it lies longest
  against, unless that would cut its own county in two: 347 of them, 447 pixels. The long ones
  lay where three counties meet, and as shapes would be spikes; the short are single pixels
  standing out of a border, which would be kinks.
- **Takes the rivers** from `Rivers.json`, cuts those that reach the sea off 3 px past the land
  (the pictures cut them there, inside the coast's line), and gives every line a point wherever
  it bends: none turns by more than 6 degrees at one point. A river's width is the rule's
  (`width_px`), not the whole pixels the pictures drew.
- **Traces the counties' map** (`geo.py`). Every edge between two unlike pixels is a step of a
  staircase; the steps between one meeting point of three counties and the next are a chain,
  with one county on each hand. Chains that carry on through a meeting point (a kingdom's border
  past the end of a duchy's) are joined into lines: 15 between kingdoms, 54 between duchies, 299
  between counties, and the coast of each of the 15 pieces of land.
- **Smooths each line.** Each point is put on the cubic fitted to as long a stretch of its
  neighbours as can be fitted without leaving any of them by more than 0.6 px. A staircase of
  long treads comes out a straight slope, a tight one a bend. A meeting point is put where the
  line through it passes, and the lines that end there end at that place.
- **Puts a border that follows a river on the river's line.** Where a border keeps within 3 px
  of one river for 12 px or more, its points there become the river's own: 51 stretches of the
  kingdoms' borders, 38 of the duchies' and 104 of the counties', 10,000 px in all, moved 2.9 px
  at most. A meeting point two borders reach along the same river is put on the river first.
- **Makes the counties' outlines** from the chains round each, so that two counties have the
  very same points along the border between them, and the border's line has them too. It stops
  if an outline crosses or touches itself.
- **Traces and smooths the lakes** the same way, out of `LakeMap.png`. A ring that meets nothing
  (a lake's shore, a small island's) is put back to the area its pixels had, since smoothing a
  small ring draws it in: by 3% on average for the lakes under 50 px, and by 12% for the worst,
  before this.
- **Takes roads, bridges and settlements** from `Roads.json` and `Settlements.json`.
- **Finds where a border lies under water or a road**, so that no line hides another. Where it
  crosses a broad lake (as `duchy/layers.py` has broad), that part is to be drawn again over the
  water. Where it runs under a river, a narrow lake or a road for 12 px or more, a second line is
  made for the scene to draw under that river, shore or road, wide enough for the border's colour
  to show on both sides.

`m2_scene.gd` then makes a node of every shape: a Polygon2D for an area, a Line2D for a line, and
for a settlement an instance of the game's `City.tscn` (a kingdom's or a duchy's capital) or
`Town.tscn` (a county's), which draw its icon. A settlement named in the program's `LOCATIONS`,
by its county's number, is given what there is to use in it: the capital of county 115 the
game's hiring board and market. It leaves two empty groups ahead of them,
`Settlements/Hamlets` and `Settlements/Villages`, for the two lesser kinds of settlement, which
the source data has none of, and ends with the game's own nodes for the map: the party, where it
starts (near the middle of county 115, a place written into the program), the camera, the
gamepad's reticle, the menu of the settlement the party is in, and the `Detail` node,
which shows and hides those groups by the zoom while the game runs and finds them by these names. It
turns pixels into the scene's units (3.35 to a pixel: a unit is 100 m), gives the lines the
pictures' widths in those units, tries every polygon in Godot's own cutter of polygons into
triangles, and saves the scene. `README.md` at the repository's top, under "The new world map",
says what the scene holds and why it is laid out as it is.

Two more programs look at what was made:

| Program | Given | Does |
|---|---|---|
| `m3_draw.gd` | by Godot, from `vcom/`, in a window: `godot --path . --script ../MapCreation/Scripts/scene/m3_draw.gd -- <the scene> <a folder> [views]` | Draws the scene at one screen pixel to a pixel of the pictures (`render_full.png`), times it, and draws any close views asked for |
| `m4_compare.py` | `<repo>/MapCreation/AllSimple.png <render_full.png> <a folder>` | Sets Godot's drawing beside the picture, colour by colour, and lists the places that differ by more than two pixels |

### 12. Proposals for the settlements' icons

`icons/`. Not a step in making the map: these drew icons to choose from, for the settlements the
scene then showed as dots. They need only the icon pack, `<repo>/WorldMapResources/MWM Icons`
(the Modular World Map Asset Pack by Penflower Ink), and write into sub-folders of it. Of what was
looked over, the pack's own Castle was chosen for a city and its Town for a town (`City.png` and
`Town.png` in the pack's folder, which the scene now uses), the pack's own Village for a village,
and two of the proposals were kept for a hamlet (`Hamlet1.png`, `Hamlet2.png`: proposals 9 and 4),
of which the game uses `Hamlet2.png`.

| Program | Given | Leaves |
|---|---|---|
| `build.py` | `<the pack's folder> <a folder to write into> [kind ...]`, run from `icons/` | For each kind, a folder of proposals, `<Kind> NN.png`, 666 x 666 like the pack's icons, and `_<Kind> proposals.png`, a numbered sheet of them all |
| `sheets.py` | the same | The sheets alone, made again from proposals already drawn |

The kinds are Hamlet, Village, Town and City (22 proposals each, in `settlements.py`) and the marks
for a Kingdom Capital, a Duchy Capital and a County Capital (24 each, in `markers.py`). A mark is
drawn by itself, to be put with a settlement's icon: above it, behind it or under it. The marks
come in families: number 7 of each rank belongs with number 7 of the others.

The pack's buildings are black shapes inked by hand, with a white edge round them; its flags and
banners are white with a black outline. `kit.py` draws both. A shape is given as straight-sided
outlines, pushed about a little by a slow random field and then blurred and cut off at half
strength, which gives it a brush's wavering edge and soft corners. Black layers in front keep a
thin white line between them and those behind, as the pack's Town has between its tower and its
house. A proposal that says "the pack's" is built from the pack's own icons, their black taken as
it is and moved or resized; the rest are drawn afresh (`parts.py` has the buildings). Every
proposal has its own seed, so drawn again it comes out the same.

## Things to watch for

- **`scene/m2_scene.gd` writes the game's scene afresh.** The scene is meant to be changed by
  hand from now on, in the Godot editor. Run again without a second name to write to,
  `m2_scene.gd` puts a newly made scene over `vcom/Scenes/Map.tscn`, and everything changed in
  it by hand is lost. Give it another name to write to (`-- <shapes> res://Scenes/MapAgain.tscn`)
  to make one to look at.
- **Two programs write into the repository themselves**: `water/w5_finish.py` and
  `water/w6_water_only.py`. Every other writes where it is told.
- **`water/w0_grids.py` reads the kingdoms' first lines from a picture named `Kingdoms.png`**:
  the one `make_kingdoms.py` writes, which had that name then. The `Kingdoms.png` in the folder
  now holds the borders along the land. Run on the folder as it is, `w0_grids.py` would shape
  the land for the wrong kingdoms; give it a folder with the first lines' picture in it.
- **Some programs call the kingdoms' picture by a name it no longer has.** While its borders
  along the land were new it had a name of its own, and kept it until it took the name
  `Kingdoms.png`. `kv_verify.py` and `kf_facts.py` look for it under the old name and stop for
  want of it; the drafts that `run_paths.sh` and `run_kingdoms.sh` write carry it; a few others
  only speak of it.
- **The road programs call the one road over the sea by its first name**, a boat's. It is drawn
  as a bridge (`r5b_draw.py`), and the pictures and the document know it only as a bridge.
- **A step run again gives what it gave**, with the packages of `requirements.txt`. Random
  draws are seeded, and the four programs that share their work among the machine's processors
  (`c1_counties.py`, `n2_duchies.py`, `n3_counties.py`, `r2_candidates.py`) gave the same bytes
  as before. Another version of numpy or scipy could turn a tie the other way and change all
  that follows.
- **`n3_counties.py` reads two settings from the environment**, and the map's counties need
  both: step 6 says how.
- **Changing a step changes what follows it.** The rivers decide borders, the borders the
  capitals, the capitals the roads. To change a little of the map and keep the rest, start
  from `../SourceData/` and not from a step here.
- **The five runners** (`duchy/run_*.sh`) are kept for the order they ran things in. They read
  the working folder, the repository and Python from `MAP_WORK`, `MAP_REPO` and `MAP_PYTHON`.

## The checks

Each of these prints `ok` or `WRONG` for every thing it looks at, and ends `ALL RIGHT` if nothing
was wrong. Run from this folder on 2026-10-07, on the repository as it stood, they found:

| Program | Given | Looks at | Found |
|---|---|---|---|
| `duchy/v1_capitals.py` | `<repo>/MapCreation` | That every kingdom, duchy and county has its capital, from the pictures alone | 31 ok |
| `duchy/v2b_roads.py` | `<repo>/MapCreation` | The roads and bridges, from the pictures alone | 16 ok |
| `duchy/v6_layers.py` | `<repo>/MapCreation` | That no line hides another | 15 ok |
| `duchy/v7_continent.py` | `<repo>/MapCreation` | `Continent.png` | 14 ok |
| `duchy/v8_allsimple.py` | `<repo>/MapCreation` | `AllSimple.png` | 15 ok |
| `duchy/v9_source.py` | `<repo>/MapCreation` | The source data, against the pictures and against itself | 83 ok |
| `duchy/v3b_network.py` | `<work>/out/duchy2 <work>/out/roads2` | The road network as it was laid | 10 ok |
| `duchy/f8c_check.py` | as in step 10 | Every figure typed into `../Features.md` | 138 ok |

The first six need nothing but the repository. The last two need the working folder.

The scene has checks of its own. `scene/m1_shapes.py` stops if a county's outline crosses or
touches itself, and prints how far each county's and lake's area is from its pixels (no county
by more than 0.5%, no kingdom by more than 0.05%). `scene/m2_scene.gd` tries every polygon in Godot's cutter and says how many
failed: none of 936. And `scene/m4_compare.py`, given Godot's drawing of the scene at the
pictures' scale (`scene/m3_draw.gd`), found the same colour at the same pixel as
`AllSimple.png` over 98.5% of the sheet, and for each of the nine colours at least 99.2% of the
picture's pixels with that colour within a pixel of them in the drawing. What differs by more
is the border colour beside rivers, which the scene puts along both banks evenly, and those of
the kingdoms' borders that were moved on to their rivers. That was measured while the scene's
settlements were dots, as the pictures' are; they are icons now, of one size on the screen, and
`m4_compare.py` would list every one of them.

Two more are run by Godot, from `vcom/`, and show that it reads the source data exactly:

```
godot --headless --path . --script ../MapCreation/Scripts/duchy/g5_read_source.gd -- ../MapCreation/SourceData ../MapCreation
godot --headless --path . --script ../MapCreation/Scripts/duchy/g6_readme_snippet.gd
```

Older checks are here as they ran, and print what they find without a verdict:

- `duchy/c8_final_check.py`, `duchy/s3_final_check.py` and `duchy/r7_final_check.py`, each given
  `<repo>`, look at `Counties.png`, `Settlements.png` and `Roads.png`. They run on the pictures
  as they are.
- `check_picture.py`, given a kingdoms picture and `WorldMapV1.png`, says what the pink cuts the
  land into.
- `duchy/f4_verify.py` and `duchy/n3_gates.py` need the working folder.
- `duchy/kv_verify.py` checked the kingdoms' picture when its borders were new. It stops now,
  for want of the picture under the name it had then.

## Run again from this folder

On 2026-10-07, once these files were here, every step was run again from them. Each program was
given what the step before it had first left in the working folder, wrote into a folder of its
own, and what it wrote was held against what the repository, git and the working folder hold.

| Steps | Programs | Gave |
|---|---|---|
| 1, 2 | `analyze3.py`, `kingdoms1.py`, `kingdoms2.py`, `net_build.py`, `make_kingdoms.py` | The same files, from the two hand-drawn pictures alone. The picture of the first lines is the `Kingdoms.png` of commit d62e6e5 |
| 3 | `w0_grids.py`, `w2_drain.py`, `w3_water.py`, `w4_draw.py`, `w5_finish.py`, `w6_water_only.py` | The same files: the grids, the heights and drainage, the water, and `Rivers.png`, `Elevation.png` and `Water.png` |
| 4 | `d1_fields.py`, `d1b_ridges.py`, `d2_solve.py`, `d3_draw.py`, `c1_counties.py`, `c2_draw.py`, `s1_candidates.py`, `s2_settlements.py`, `r1_ground.py`, `r2_candidates.py`, `r3_network.py` | The same files |
| 5 | `k1_fields.py`, `kb1_network.py`, `kb2_paths.py`, `k3_draw.py` | The same files, `Kingdoms.png` among them |
| 6 | `n1_fields.py`, `n2_duchies.py`, `d3_draw.py`, `c2_draw.py`, `s1_candidates.py`, `s2_settlements.py`, `r1_ground.py`, `r2_candidates.py`, `r3_network.py` | The same files, `Duchies.png`, `Counties.png` and `Settlements.png` among them |
| 6 | `n3_counties.py`, its three runs, with `n3_merge.py` | The same counties in all 44 duchies (land, capitals, sizes), and `Counties.png` drawn from them is the same file. The file of counties itself is not the same: the notes it keeps beside them have grown since the first run |
| 7 | `r5b_draw.py`, `a2_all.py` | The same files: `Roads.png` and `All.png` |
| 8 | `y8_continent.py`, `z2_allsimple.py` | The same files: `Continent.png` and `AllSimple.png` |
| 9 | `e2_regions.py`, `e3_water.py`, `e4_roads.py`, `e5_borders.py`, `e11_readme.py` | The same files: all 24 of `../SourceData/` |
| 10 | `f1_facts.py`, `f2_more.py`, `f14_facts6.py`, `f3_build.py` | The same files: the measured figures, and `../Features.md` |

"The same files" is byte for byte.

So the working folder can be made again from the repository. The two hand-drawn pictures and
these programs give every other picture, the source data and the document, as they are. It
took about an hour and a quarter of computing here, most of it in four programs: `d2_solve.py`,
`c1_counties.py`, `n3_counties.py` and `kb2_paths.py`.

Each step was given what the step before had first left, not what the step before had just
made again. Since every step gave the same bytes, that comes to the same thing; but the chain
has not been run from end to end in one go.

Step 11 was run again from here too. `scene/m1_shapes.py` gave the same file of shapes, byte for
byte, and `scene/m2_scene.gd` the same scene but for the numbers Godot gives nodes and
resources, which it draws afresh each time.

## What was left out

62 files that lay with these are not here:

- 6: not about the map (note-keeping, and reading a PDF).
- 21: one-off edits of other programs, long since applied.
- 9: one-off edits of the document's template, long since applied.
- 7: earlier versions of the document's template.
- 5: copies of programs kept before an edit.
- 8: programs a later version replaced, and the two runners that ran them.
- 2: the two that moved finished files into the repository.
- 4: the trial of line drawing in Godot.

None of them made anything that is in the map as it is.

## What was changed on the way in

- `duchy/e6_look.py`: a list of words to look for lost one, a user's name.
- `duchy/r5b_draw.py`: its line of usage gives its own name.
- `duchy/run_counties.sh`: reads the working folder, the repository and Python from MAP_WORK, MAP_REPO and MAP_PYTHON, and finds the programs beside itself.
- `duchy/run_facts.sh`: reads the working folder, the repository and Python from MAP_WORK, MAP_REPO and MAP_PYTHON, and finds the programs beside itself.
- `duchy/run_kingdoms.sh`: reads the working folder, the repository and Python from MAP_WORK, MAP_REPO and MAP_PYTHON, and finds the programs beside itself.
- `duchy/run_paths.sh`: reads the working folder, the repository and Python from MAP_WORK, MAP_REPO and MAP_PYTHON, and finds the programs beside itself.
- `duchy/run_trials.sh`: reads the working folder, the repository and Python from MAP_WORK, MAP_REPO and MAP_PYTHON, and finds the programs beside itself.
- `duchy/v3b_network.py`: its line of usage gives its own name.

Every other file is as it ran, but that all have plain line ends here: 20 had the two-byte
kind. The runs in [Run again from this folder](#run-again-from-this-folder) were made with the
files as they are here.

## Every file

What a file is for (the files of `scene/` are listed after the rest):

| For | Meaning |
|---|---|
| makes | A step in the making: it leaves a picture, a file of the source data, the document, or working data for the next step |
| leaned on | Other programs use it; it is not run by itself |
| check | Looks for faults in what was made, and says `ok` or `WRONG` |
| measures | Works out figures for the document |
| written part | The words of a document, which a program fills in |
| runner | A shell script that ran several programs in a row |
| tried | A way of doing a step that was tried and not used |
| look | Prints or draws something to look at, and changes nothing |

### This folder

| File | For | What it does |
|---|---|---|
| `analyze3.py` | makes | Where the region lines of WorldMapRegions.png leak: line ends that stop short of the coast or of the line they should meet. Then the nine regions with the gaps closed. |
| `kingdoms1.py` | makes | Shifts the nine regions' borders so each covers the same area, keeping their shapes. What the later steps read from it is `start_map.npy`: the sketched regions, smoothed. |
| `kingdoms2.py` | makes | Even out the nine regions' areas by flowing the land within its own coast. |
| `make_kingdoms.py` | makes | Write MapCreation/Kingdoms.png: the coast map with the nine kingdoms' borders in pink, shifted from the regions sketch so that every kingdom covers the same area. |
| `net_build.py` | makes | Build the border network once and keep it, with the numbers that check it. |
| `kingdom_net.py` | leaned on | The drawn regions as a network of border curves, so the curves themselves can be moved. |
| `net_solve.py` | leaned on | Placing a border network's points so its regions enclose given areas. |
| `check_picture.py` | check | Check a kingdoms picture knowing nothing but the picture: what the pink cuts the land into. |
| `draw_kingdoms.py` | tried | Draw a solved set of kingdom borders on the coast map, and check the picture by itself. |
| `kingdoms3.py` | tried | Even out the nine regions by moving where their borders meet, carrying the drawn curves along. |
| `kingdoms4.py` | tried | Even areas with the drawn curves themselves, laid out as the smooth flow laid the land out. |
| `analyze1.py` | look | First look at the MapCreation images and how they relate to the in-game art. |
| `analyze2.py` | look | The regions drawn on MapCreation/WorldMapRegions.png: what closes them, how big each is, which touch, and how the creation images line up with the in-game art. |
| `analyze4.py` | look | How MapCreation/WorldMapV1.png maps on to the in-game art: fit and check. |
| `analyze5.py` | look | Where the game's present map objects fall among the nine regions, and what sizes the land would have at a few real-world scales. |
| `crop_ends.py` | look | Close-ups of where each border meets the coast, and of the junctions, for two drafts side by side. |
| `crops.py` | look | Close-ups of the region lines' ends and junctions, and of the coast's features, enlarged. |
| `net_debug.py` | look | Times the solving of the border network and prints how its areas come out. |
| `scale.py` | look | The island at Texas's area: kilometres per pixel of the new shape, each kingdom's area, and what 4-6 duchies of 4-6 counties come to. |
| `side_by_side.py` | look | The drawn regions and drafts side by side, lines thickened so they survive the shrinking. |

### water/

| File | For | What it does |
|---|---|---|
| `w0_grids.py` | makes | The land and the nine kingdoms as grids, read from the two pictures in MapCreation, at the picture's own size and at a half and a quarter of it (the water is worked out on the coarser ones and drawn on the full one). |
| `w2_drain.py` | makes | The lie of the land and the way water leaves it, made together to suit the nine kingdoms. |
| `w3_water.py` | makes | Lakes, rivers and watersheds on the land w2_drain.py made. |
| `w4_draw.py` | makes | Draw the rivers, lakes and watersheds w3_water.py worked out on the coast map, at the map's own size. |
| `w5_finish.py` | makes | Put the finished rivers picture in MapCreation, with the heights it was worked out from, and check the picture from the saved file alone. |
| `w6_water_only.py` | makes | Water.png: Rivers.png with the brown watershed lines taken off again, leaving the coast map with its rivers and lakes. Every brown pixel goes back to what the coast map has there; the check then confirms nothing but the blue differs from the coast map, and that the blue is the same. |
| `hydro.py` | leaned on | Water running downhill over a grid of land heights: where each cell drains, how much passes through it, and what ponds on the way. |
| `w1_terrain.py` | tried | The lie of the land: a height for every cell, made to suit the nine kingdoms' biomes and then worn by its own rivers. |
| `crops.py` | look | Full-size crops of a rivers picture, for a close look. |
| `speed.py` | look | How long the drainage of a grid takes at each size, on a made-up bumpy surface. |

### duchy/

| File | For | What it does |
|---|---|---|
| `a2_all.py` | makes | Everything on one map, with no line hiding another. |
| `c1_counties.py` | makes | Share each duchy out among its counties, the way the kingdoms were shared among duchies. |
| `c2_draw.py` | makes | Draw the counties' borders in grey over Duchies.png, and check the picture by itself. |
| `d1_fields.py` | makes | What the ground is like for someone travelling over it, as grids at the map's own size and at half of it: the things that decide where one lord's land ends and the next one's begins. |
| `d1b_ridges.py` | makes | The ridges between neighbouring rivers, as lines a border can follow. |
| `d2_solve.py` | makes | Share each kingdom out among its duchies. |
| `d3_draw.py` | makes | Draw the duchies' borders in purple over Kingdoms.png, and check the picture by itself. |
| `e11_readme.py` | makes | The source data's README.md: the written part, with every file's size put in. |
| `e2_regions.py` | makes | Source data, part 1: which county, duchy and kingdom every pixel of land belongs to, and the tables that tie them together with their capitals. |
| `e3_water.py` | makes | Source data, part 2: the water. The lakes, the rivers as lines with the water they carry, the watersheds, the drainage they were all worked out from, and the lines of the land that are drawn on no picture (ridges, spurs, brooks). |
| `e4_roads.py` | makes | Source data, part 3: the roads as a network. Its places (the 220 settlements and the forks between them), the stretches of road from one place to the next as the lines that were drawn, the 351 roads between neighbouring settlements as runs of stretches, and the bridges. |
| `e5_borders.py` | makes | Source data, part 4: the kingdoms' fifteen borders as the smooth lines they were drawn from, and every figure that was measured off the pictures for Features.md. |
| `f3_build.py` | makes | Put Features.md together: the written part (a template) with the tables made from the figures f1_facts.py measured, so no table is typed by hand. |
| `k1_fields.py` | makes | What a kingdom's border can settle on, beyond the rivers, lakes, watersheds and ridges the duchies used: the small lines of the land, and the foot of the high country. |
| `k3_draw.py` | makes | Draw the kingdoms' new borders in pink over the coast map, and check the picture by itself. |
| `kb1_network.py` | makes | The kingdoms' old borders as a network: the fifteen borders, the seven places three kingdoms meet, the nine places a border reaches the coast, and for each border the zone its new line may run in. |
| `kb2_paths.py` | makes | The kingdoms' new borders, each the cheapest line through its zone. |
| `n1_fields.py` | makes | The fields d1_fields.py and d1b_ridges.py made, again, for the kingdoms with their borders along the land. |
| `n2_duchies.py` | makes | Shares each kingdom, with its borders along the land, out among its duchies, keeping the duchies it had. |
| `n3_counties.py` | makes | Share each duchy out among its counties again, on the duchies as they now are, keeping the counties it had where that still makes good counties. |
| `n3_merge.py` | makes | Put the duchies of a part run of n3_counties.py into the whole run's file. |
| `r1_ground.py` | makes | The ground as a road-builder meets it, at the map's own size. |
| `r2_candidates.py` | makes | Every pair of neighbouring settlements, and what a road between them would cost by itself. |
| `r3_network.py` | makes | Which roads there are, and where each runs. |
| `r5b_draw.py` | makes | Draw the roads and bridges over Settlements.png, and check the picture by itself. |
| `s1_candidates.py` | makes | What each duchy seat has going for it as its kingdom's capital. |
| `s2_settlements.py` | makes | Draw the capitals over Counties.png: a dot for each county's seat, in the colour of the highest thing it is the capital of, and check the picture by itself. |
| `y8_continent.py` | makes | Continent.png: the coast map with a standard outline. |
| `z2_allsimple.py` | makes | AllSimple.png: everything All.png draws, on the standard outline of Continent.png. |
| `layers.py` | leaned on | Lines that run together, drawn so that neither hides the other. |
| `realm.py` | leaned on | One kingdom, or one duchy, as country to be shared out among seats. |
| `roadnet.py` | leaned on | Finding where a road goes: the cheapest way from one cell to another over the ground r1_ground.py made. |
| `sourcefiles.py` | leaned on | How the source data's files are written: plain PNGs that any program reads exactly, and JSON with one record to a line. |
| `tidy.py` | leaned on | Tidy shares as they will be drawn: the same for the solver, which evens out what tidying leaves, and for the picture. |
| `c8_final_check.py` | check | Check Counties.png from the pictures alone, with nothing the scripts kept: what was added to Duchies.png, how many pieces a paint bucket finds, and how big they are within each duchy. |
| `f4_verify.py` | check | Check the statements Features.md makes that f1 and f2 did not measure: the coast's shapes, where the big rivers start, and that every picture's lines hold a fill of either kind. |
| `f8c_check.py` | check | The figures typed into Features.md's written part, each held against what was measured, and the words the document must no longer use. |
| `g5_read_source.gd` | check | Run in Godot: does it read the source data's maps and tables exactly? |
| `g6_readme_snippet.gd` | check | Run in Godot: the lines the source data's README gives for reading it, as they are written there. |
| `kv_verify.py` | check | Checks the kingdoms' picture with its borders along the land, as it was when new, from the saved pictures alone, and says what it does to the pictures made on the first lines. It calls the picture by the name it had then. |
| `n3_gates.py` | check | Two things a duchy's counties must not do, and which of the duchies as solved do them: two seats under MIN_GAP km apart, and the duchy's own seat with less than ROOM px of its own county round it (unless it had less when the counties were first made). |
| `r7_final_check.py` | check | Checks the roads' picture from the pictures alone, as the roads were first drawn. v2b_roads.py is the check for the roads as they are. |
| `s3_final_check.py` | check | Check Settlements.png from the pictures alone, with nothing the scripts kept. |
| `v1_capitals.py` | check | Does every kingdom, duchy and county have its capital? Checked from the pictures alone. |
| `v2b_roads.py` | check | Are the roads and bridges right? Checked from the pictures alone. |
| `v3b_network.py` | check | The road network as it was laid, checked from what the road run kept: every road joins two settlements, every river is crossed on a bridge and squarely, no road runs on a lake, one road alone leaves the land, and the highways are the ways between the capitals of kingdoms that share a border. |
| `v6_layers.py` | check | Does any line hide another? Checked from the pictures alone. |
| `v7_continent.py` | check | Is Continent.png what it should be? Checked from the pictures alone: three colours, no wave lines, a black shoreline of one width with no gaps round every piece of land, and the land of WorldMapV1.png but for the mended joins. |
| `v8_allsimple.py` | check | Is AllSimple.png everything in All.png on the outline of Continent.png? Checked from the pictures alone. |
| `v9_source.py` | check | Is the source data whole, and is it the map? Checked from the source data's own files and the pictures, with nothing else: this reads no working file of the session that made them. |
| `f14_facts6.py` | measures | The measured figures once more, with the rivers counted and measured as they are drawn. |
| `f1_facts.py` | measures | Every figure Features.md states, measured from the pictures in MapCreation and from what the runs that made them kept. Prints them, saves them as JSON, and writes the three long tables (kingdoms, duchies, counties) as Markdown. |
| `f2_more.py` | measures | More figures for Features.md: where the two rivers that do not reach the sea end, what the sketch's pink is, the borders' lengths counted one way, the coast's ink, the peaks, the marks' sizes, and what the lines hide of each other. |
| `kf_facts.py` | measures | The figures the document gives for the kingdoms' borders along the land. It calls the picture by the name it had then. |
| `kl2_lengths.py` | measures | How long the borders of the old kingdoms, the duchies and the counties are, measured as kl_lengths.py measures a kingdom's: the shortest chain of cells along each stretch of border from end to end, smoothed, and its length. A duchy border here is one between two duchies of one kingdom, and a county border one between two... |
| `kl_lengths.py` | measures | How long each border between two kingdoms is, old and new, measured one way: the shortest chain of cells along the border from end to end, smoothed as the new lines were, and its length. |
| `Features.template.md` | written part | The written part of `../Features.md`, with a marker where each table and counted figure goes. |
| `SourceData.README.template.md` | written part | The written part of `../SourceData/README.md`, with a marker for each file's size. |
| `run_counties.sh` | runner | Solve the counties, draw them to a draft and look for oddities. |
| `run_facts.sh` | runner | Measure every figure the document states, as was done after everything was made again. |
| `run_kingdoms.sh` | runner | Solve and draw one variant of the kingdoms' borders by the method that was tried and not used. |
| `run_paths.sh` | runner | Lay and draw one variant of the kingdoms' borders as cheapest lines: the method that was used. |
| `run_trials.sh` | runner | Try several settings of the counties' solver on a sample of duchies. |
| `k2_solve.py` | tried | Move the kingdoms' borders on to the land's own lines. |
| `c0_grey.py` | look | Counts the greys already in Duchies.png, to choose a grey for the counties' borders that the coast's ink does not hold. |
| `c0_look.py` | look | What the county step has to work with: the islands, the greys already in Duchies.png, the duchies' sizes, what the water run kept, and how many processors there are. |
| `c3_oddities.py` | look | Find what looks wrong in a county draft: marks that are not borders, and counties of odd shape. |
| `c4_compare.py` | look | Where tidying moved land from one county to another: the solver's shares against the map drawn. |
| `c5_arms.py` | look | How many counties have arms: parts too narrow for a disc of RADIUS px, yet of some size. |
| `c6_pixels.py` | look | Print a patch of a county draft as letters: what the picture holds, the counties, the duchies. |
| `c7_tidy_test.py` | look | Is what the solver gave back tidy? Tidies each duchy's counties again and counts what changes. |
| `c9_list.py` | look | List the counties' seats by duchy, for the notes. |
| `crops.py` | look | Cuts six set views out of a picture (swamp, range, west, desert, south, north), for a close look. |
| `crops2.py` | look | Cut views out of a picture. |
| `d2_tolerance_test.py` | look | Does holding the duchies nearer to equal pull their borders off rivers and ridges? |
| `e0_inventory.py` | look | What the map's working data holds: the shape of every file that the pictures were drawn from. |
| `e10_look.py` | look | Do all drawn rivers carry 15 m3/s? Where they do not, why. |
| `e12_look.py` | look | How the three masks of the land's lines lie to the watersheds, the rivers and each other. |
| `e13_look.py` | look | Are the brown lines of Rivers.png where WatershedMap.png changes? And what a lake does to the flow. |
| `e14_look.py` | look | Rivers that lose water on the way: the most each carries against what it carries at its end. |
| `e1_details.py` | look | The fine print of the working data, before it is exported: how records are laid out and whether the pieces agree with each other. |
| `e6_look.py` | look | Things the source data's files say about themselves, looked at before they are written down. |
| `e7_look.py` | look | The rivers as Features.md has them against the rivers as drawn, and how the drainage treats lakes. |
| `e8_stub.py` | look | What the river lines that are not drawn are: where each starts and ends, and how long it is. |
| `e8b_stub.py` | look | The one river line under 3 px long: what runs into it, and what the picture shows there. |
| `e9_look.py` | look | Three things the check of the source data tripped on: which counties the islands are, which counties are in more than one piece, and what a river's course carries inside a lake. |
| `kb3_where.py` | look | Where the new borders run far from the old, and what they run along there, border by border. |
| `kb4_features.py` | look | A picture of the lines of the land a border may follow, each kind in its own colour, with one variant's borders over them; and the long ruled runs in those borders, with what they lie on. |
| `n3_probe.py` | look | Why one duchy's counties will not come out even: what the old seats give under larger limits on the head starts, and each scattering's result. |
| `r0_look.py` | look | What the roads have to work with: how steep the land is in each kingdom, how wide the rivers are drawn, how far apart the settlements are, and which colours Settlements.png already uses. |
| `r10_sheet.py` | look | A sheet of close-ups of bridges, the largest marks first (the likeliest to be wrong) or a random lot: 20 to a sheet, each 50 px square shown four times its size. |
| `r4_preview.py` | look | A picture to judge roads by: the land shaded by its relief and tinted by its height, the water, the borders faintly, the settlements, and the roads as laid (cell by cell, unsmoothed). |
| `r6_judge.py` | look | Judge a roads draft: small loops, big-river bridges away from towns, and how the roads treat the terrain against straight lines between the same settlements. |
| `r8_pieces.py` | look | Where the road network of Roads.png falls into pieces, and which bridge marks lack two ends. |
| `r9_near.py` | look | Which roads run near a spot, and how: for looking into an odd bit of the drawing. |
| `v4_changes.py` | look | What making everything again on the kingdoms' new borders changed, old against new: land that keeps its duchy and county, capitals that stay where they were, roads and bridges that are the same. |
| `v5_seats.py` | look | How the seats sit: pairs that are close together, and seats hard against a border. |
| `x1_look.py` | look | Before three changes to the pictures: the crossing to the island town and how wide the strait is, and where one line lay along another (roads on borders, borders on water). |
| `x2_strait.py` | look | The strait at the island town, pixel by pixel, and what the road run kept about the crossing. |
| `x3_overlaps.py` | look | Where a road lies along a border in Roads.png: how long, and how deep the border is hidden. |
| `x5_crops.py` | look | Crops of a picture, enlarged, side by side into one sheet: x5_crops.py <picture> <sheet> <scale> x,y,w,h ... |
| `y1_coast.py` | look | The hand-drawn coast of WorldMapV1.png, measured: what colours it is made of, how thick the ink is, where it is broken, what the wave lines are, and how near the shores come to each other. |
| `y2_try.py` | look | The coast with a standard line, tried at several widths, set beside the hand-drawn one; and where the hand-drawn ink is thin or broken. |
| `y3_seams.py` | look | Where the hand-drawn sheets were joined: rows and columns at which the land's edge jumps sideways, how far it jumps at each place the coast crosses them, and what the picture is like along them. |
| `y4_print.py` | look | Print a patch of WorldMapV1.png as letters: y4_print.py <MapCreation dir> x0 y0 w h |
| `y5_joins.py` | look | Every place the coast crosses a join between the hand-drawn sheets: how far the land's edge jumps there, and whether a join shows in the picture's other marks. |
| `y6_sheet.py` | look | Sheets of the same places from several pictures, enlarged, in a grid: one row a place, one column a picture. |
| `y7_plain.py` | look | The coast map with a plain line: sea, white land exactly as WorldMapV1.png has it, and every pixel within W px of the land black. A trial picture, to look at. |
| `y9_near.py` | look | What the other pictures draw at the places where Continent.png's land differs from WorldMapV1.png's. |
| `z1_marks.py` | look | What All.png draws on the coast map, and how those marks sit against the coast: how far off the land each kind reaches, and what there is at the 13 joins where Continent.png's land differs. |
| `z3_blob.py` | look | The purple patch where a duchy border meets the coast at the join (2686, 2400): what the duchies' own map says is there, pixel by pixel. |
| `z4_labels.py` | look | The duchies' and counties' maps about a place, as letters, with the old land's edge. |
| `z5_thick.py` | look | Places where a border's colour is a patch and not a line: in the borders' own pictures. |

### scene/

| File | For | What it does |
|---|---|---|
| `m1_shapes.py` | makes | The map as shapes: everything the pictures show, worked out of the source data as outlines and lines with points finer than a pixel, ready to be made into a Godot scene. |
| `m2_scene.gd` | makes | Makes the map's scene, `vcom/Scenes/Map.tscn`, out of those shapes: areas as Polygon2D nodes, lines as Line2D nodes, grouped by what they are and in the order they are drawn. |
| `geo.py` | leaned on | Shapes out of a map of numbers: the edges between unlike pixels as chains, the chains joined into lines, and the lines smoothed, given points where they bend and thinned where they run straight. |
| `m4_compare.py` | check | The scene as Godot draws it, set beside the picture it was made from, colour by colour. |
| `m3_draw.gd` | look | Draws the scene in Godot: the whole map at the pictures' scale, close views, and how long it takes to load and to draw. |

### icons/

| File | For | What it does |
|---|---|---|
| `build.py` | makes | Draws every proposal and a sheet of each kind to choose from. |
| `sheets.py` | makes | Makes the sheets again from proposals already drawn. |
| `settlements.py` | leaned on | The proposals for the four kinds of settlement: for each kind a list of what it is and how it is drawn. |
| `markers.py` | leaned on | The proposals for marking a capital, in families across the three ranks, and the sheet that shows a mark with an icon. |
| `parts.py` | leaned on | Buildings and other things to make settlements' icons of: houses, huts, towers, walls, churches, mills. |
| `kit.py` | leaned on | Draws map icons in the manner of the MWM icons: black shapes with a white edge, or white shapes with a black outline. |
