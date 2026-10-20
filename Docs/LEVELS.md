# Levels

Combat maps as levels of voxel pieces, in full: `Scripts/Level/`, `Blocks/Pieces.tres`, `Levels/`,
and the parts of `CombatGrid`, `LineOfSight`, `Ballistics`, `VoxelTerrain`, `TerrainDestruction`,
`Blood` and `CameraRig` that read a level. The level editor that paints them (`addons/level_editor/`)
is `Docs/LEVEL_EDITOR.md`'s. It was written as levels replaced the GridMaps (2026-10-19/20);
`CLAUDE.md` keeps a summary ("A combat map is a level of voxel pieces") and the rules that must not
drift. A section named here that is not in this file (Gotchas, Verification, Known gaps, another
subsystem's notes) is `CLAUDE.md`'s.

## Why levels

The combat maps were GridMaps of 16³-voxel blocks. That made the block the unit of everything: what
was drawn (each block its own imported mesh, every face of it, hidden or not), what the rules saw,
what broke, and where blood could go. BoundaryMap's battlefield was 924k triangles, 546k (59%) of
them faces hidden between blocks, and nothing could stand between two cells, overlap another block,
or be recoloured without an overlay mesh.

The user set nine goals: layering voxel elements in one block (decorations); elements between
blocks (fences, railings, walls); destruction free of the grid; recolouring voxels at run time;
combining part-blocks (water edges, ridges); XCOM 2's plots and parcels; placing groups of blocks
(trees); as few triangles as possible; and, maybe, C++. They all come down to one change: the block
stops being the unit of geometry. A level is still placed a block at a time, but as it loads every
piece is stamped into one grid of voxels, and that grid is what is drawn, worn, traced and
recoloured.

The user's decisions for this step (2026-10-19), which the rest of this file follows:

1. A piece on an edge is cover to both sides of it.
2. A unit steps over an edge piece a level high or less, as it climbs a level, and never over a
   taller one.
3. An edge piece's voxels block sight like any other model's.
4. A piece, centre or edge, is whole to the rules until it breaks; an edge piece is a 16³ box
   offset half a cell, with more empty space.
5. Maps will be built from plots and parcels each time they load, later: not now. Whole maps for
   now.
6. GDScript only: no C++, no GDExtension.
7. Destruction in this step, smooth across chunks, with no visible artefact of the tile grid.
8. Recolouring (blood) in this step, by texture writes rather than more textures or overlay meshes.
9. Edge elements are 16³; the editor places on block centres and block edges only; where two
   overlap, the later wins, voxel by voxel.
10. No auto-tiling yet.
11. Hidden faces removed aggressively, between chunks too: triangles matter, as maps will grow.
12. No multi-model `.vox` files for the editor: those stay for pieces that break apart.
13. The chunk size that measures best.
14. No editor inside the game: a Godot editor plugin or a standalone application, both considered.
15. A basic brush that places several pieces at once (a whole tree).

## What a level is

**A `VoxelLevel` node in place of the GridMap.** Each combat map has a `Level` node (`VoxelLevel`,
a `@tool` `Node3D`) where its `GridMap` was, with three exports: `data`, a `LevelData` (the pieces,
its own `.tres` in `Levels/`), `library`, the `PieceLibrary` every map shares (`Blocks/Pieces.tres`),
and `scenery`. It builds itself afresh every time it enters the tree, in the editor as in the game:
`LevelRules` (what the rules see), `VoxelVolume` (every voxel) and a `LevelRenderer` (what draws it),
both renderers as internal children so they are never saved. BoundaryMap's forest is a second level,
`Scenery`, with `scenery` ticked: drawn by a `SceneryRenderer`, seen by nothing else (see Scenery).
Its space is the grid's: cell (x, y, z) runs from (x, y, z) to (x + 1, y + 1, z + 1), 16 voxels a
side, the floor blocks at y 0 and walkable tiles at y 1, as before.

**A piece is a kind, a slot and a turn** (`LevelData`, five ints a piece in `pieces`: the kind's
place in `kinds`, the slot's x, y and z, the turn). A slot counts across the ground in half cells and
up in cells: x and z both even is the middle of cell (x / 2, y, z / 2), where a block stood; one of
them odd is the edge between two cells side by side, x odd the edge between cells x / 2 and x / 2 + 1
along x, z odd the same along z; both odd, a corner, is no slot. A piece's 16³ box has its least
corner at voxel (sx * 8, y * 16, sz * 8) (`LevelData.voxel_origin()`), so a piece on an edge stands
half in each cell. A turn is quarter turns about up, counterclockwise from above, about the box's
middle (`VoxelVolume.turned()`: one turn takes (x, z) to (z, 15 - x)). Pieces are kept in the order
placed, and may share a slot or overlap: stamped in order, a later piece's voxels replace an
earlier's wherever both have one, and its empty voxels leave what is there. Nothing in play changes a
`LevelData`; what breaks is the battle's.

**A kind is a `PieceKind`** (in `PieceLibrary.kinds`): `id` (what every level calls it, so never
renamed once used), `model` (a mesh imported from a single-model `.vox` at Scale 0.0625, as the blocks
always were; its voxels are read from that `.vox`, `VoxelShape.read()`), `model_transform` (where
the mesh sits in the box, what a MeshLibrary item's mesh transform was: down half a box by default),
`destruction` (a `VoxelDestruction` to wear away, a `ScriptedDestruction` to break into cut pieces,
none to never break), `solid` (off for decoration the rules never see), `tile_grid` (the optional
grid is drawn on its voxels) and `edge_piece` (the editor puts it on an edge to begin with).

**A brush is a `PieceBrush`** (in `PieceLibrary.brushes`): a few kinds, each with a slot offset (half
cells across, cells up) and a turn, placed together in one click and turned together.

`Blocks/Pieces.tres` holds, as of 2026-10-20:

| Kind | What it is | Destruction | Notes |
|---|---|---|---|
| `BrightGrass1` | the ground block | `VoxelDestruction`, wears | `tile_grid` |
| `BrightCrate1` | the crate | `ScriptedDestruction` (cut pieces, blast, coins, `wear`) | `model_transform` z 1.3125, as its MeshLibrary item had |
| `SkinnyTree1Bottom`, `SkinnyTree1Top` | a tree's trunk and crown | `VoxelDestruction`, wears | |
| `FenceStraight` | a two-rail fence | `FenceStraight.tres`: wears, mass 60, density 600, 8 voxels a point, crumbles in 2s | edge piece |
| `StoneWall` | a course of masonry, 4 voxels thick | `StoneWall.tres`: wears, mass 900, density 2400, 6 voxels a point, crater 0.35 | edge piece, from `make_shapes.py`'s `stone_wall()` |
| `TallGrass` | tufts of grass | `TallGrass.tres` | not solid: decoration |

and two brushes: **SkinnyTree1** (trunk at (0, 0, 0), crown at (0, 1, 0)) and **StoneWall2** (two
courses, one over the other). `FenceStraight`, `StoneWall` and `TallGrass` are copies of
`MagicaVoxel/Shapes/`' models in `vcom/Blocks/`, imported at 0.0625.

`Levels/` holds `BoundaryMap.tres` (2,084 pieces), `BoundaryMapScenery.tres` (37,118),
`CombatMap.tres` (562) and `LineOfSightTest.tres` (634, 30 of them on edges: the edge lanes, see
Probing it). They are text resources holding packed arrays: BoundaryMap.tscn went from 666,729 bytes to
12,868, its pieces now in their own file.

## The volume

**Every voxel of a level is one grid** (`VoxelVolume`), in chunks of 32³ (`SIZE`, `SHIFT` 5), made
only where a piece puts voxels. A chunk keeps two bytes a voxel, at `x + z * 32 + y * 1024`:
`colors`, the voxel's place in the level's palette (0 for none), and `slots`, 1 + its owner's place in
the chunk's `owners` (the pieces with voxels there); and the same voxels as rows of bits, `rows_x`
(bit x, at `z + y * 32`) and `rows_z` (bit z, at `x + y * 32`), which the mesher works from. That is
80 KB a chunk: BoundaryMap's 470 chunks are 36.7 MB, CombatMap's 109 8.5 MB, LineOfSightTest's 162
12.7 MB.

**Pieces are stamped as images.** Each kind is read once (`VoxelShape.read()`) and turned into a
`Stamp` for each turn it is placed at: its colours laid out as a 16 x 256 image and a mask, so a piece
goes into a chunk with `Image.blit_rect_mask()`, the engine's work rather than the script's, and its
rows OR in a row at a time. `build()` stamps every piece in order; `restamp(keys)` rebuilds only the
chunks an edit touched; `piece_removed()` / `piece_inserted()` renumber owners as the editor takes a
piece out or puts one back in the middle of the order.

**The palette** (`palette`, `flags`) is the level's: every colour its kinds' models use, a place a
colour and set of flags, shared across kinds, at most 254 (BoundaryMap uses 15). Place 255 is
`BLOOD`, `VoxelShape.BLOOD_COLOR`, flagged `FLAG_WET` (glossier), as in every voxel model's palette. `FLAG_GRID` marks a colour of a kind
with `tile_grid`. Past 254 colours, the nearest there is stands in, with an error.

Queries: `is_solid()`, `color_at()`, `owner_at()`, `voxels_of(piece)`, `counts[piece]` (voxels left;
`whole[piece]`, voxels once stamped), `cell_has_voxels()` (a count per cell made as it is built, never
fewer than are there), `voxel_under()` / `center_of()`. Changes: `remove()` and `remove_many()` (wear),
`recolor()` (blood); each marks the chunks it touched `dirty` (and the neighbours across a face it
touched) or `dirty_colors`.

### The chunk size

Measured on BoundaryMap's battlefield with the prototype mesher, stamping and meshing everything:

| Chunk | Chunks | Triangles | Meshing all | Meshing one |
|---|---|---|---|---|
| 16³ | 2,084 | 274,588 | 459 ms | 0.22 ms |
| **32³** | **470** | **268,772** | **412 ms** | **0.88 ms** |
| 48³ | 165 | 255,814 | 333 ms | 2.02 ms |

A bite or an edit meshes again the one to eight chunks it reaches, so the cost of one chunk is what
the player feels; the number of chunks is what draw calls, texture layers and collision shapes come
to. 32³ costs a quarter of 48³'s 2 ms a chunk for 5% more triangles, and has a fifth of 16³'s chunks
for 2% fewer triangles. It also keeps a row of a chunk in 32 bits of a 64-bit int, with room for the
next chunk's bit on either side, and a chunk's colours one 32 x 1024 R8 texture layer.

## Drawing it

**Faces are found by shape alone, and merged greedily** (`ChunkMesher.rectangles()`). A face looking
along y or z is a bit of a row along x whose neighbour row (up, down, across) lacks it; one looking
along x a bit of a row along z; so a whole row's faces are one sum of bits. The neighbour rows of the
next chunk are read too, so no face is drawn against a voxel anywhere: not inside a block, not
between two blocks, not between two chunks. The floor's underside is never drawn. Each slice's faces
are merged a row at a time (a run of bits grown down while every row below has the same run, `_merge`
over a bit table modulo 67), whatever their colours, since colour comes from a texture: a grass
block's top is one quad however its voxels are coloured. A quad never crosses into the next chunk.
Seven ints a quad (axis, side, slice, along, down, width, height); `arrays()` makes the vertices and
normals, with each corner's place in voxels within its chunk, and the chunk's texture layer times 8
plus the way its face looks, in `CUSTOM0`, and the quad's extent in `CUSTOM1`. A corner carries its
own place, rather than the chunk's origin once for the whole chunk, so the one shader colours a mesh
whose corners move, a figure skinned to its skeleton (`Docs/VOXELS.md`): it costs 0.35 ms a chunk
against 0.27, about 40 ms on BoundaryMap's 520 ms build.

BoundaryMap's battlefield is 268,772 triangles, 71% fewer than the GridMap's 924k (CombatMap 5,668,
LineOfSightTest 19,362).

**One material draws every chunk** (`Scripts/Terrain/Voxels.gdshader`, which draws every voxel
model, `Docs/VOXELS.md`; `render_mode diffuse_burley`, as the importer's materials drew). Every
chunk's colours are one layer of a `Texture2DArray` (32 x 1024 R8, point sampled; `box_size` 32³),
and the palette is a `uniform vec4 palette[256]`, passed as a `PackedVector4Array`: a
`PackedColorArray` uniform is converted to linear on the way, which drew everything far too dark. A
fragment finds its voxel from the place its corners carry (`local_voxel`, half a voxel back from its
face), clamped to its quad's extent, and reads the voxel's place there and the palette's colour.
Since a texture is not multisampled, a colour edge inside a merged face would be jagged beside the
geometry's MSAA'd edges: `neighbour_share()` blends a texel with its neighbour over about a pixel at
the boundary ("sharp bilinear"), never past the quad's edge. Colours go to linear unless the output is
sRGB. The tile grid (`FLAG_GRID`, the global uniform `tile_grid`) darkens along every cell boundary,
as `TileGrid.gdshader` did; a wet colour (`FLAG_WET`) is glossier (specular 0.35, roughness 0.55,
against 0.5 and 1.0).

**Faces are drawn a fiftieth of a pixel past their edges.** Merged faces of different sizes meet at
T-junctions, a corner of one partway along the edge of the next, and rasterising them leaves rare gaps
a fraction of a pixel wide. A block of the GridMap was a closed mesh, so a gap showed the block's own
hidden faces in the same colour; with every hidden face gone, the sky showed through, a sparkle. Seven
views against a magenta background had 123 isolated magenta pixels, against the GridMap's 98, the extra
ones at crates' feet, along ledges' edges and in the forest's crowns. The vertex shader grows each face
along its own plane by `grow_pixels` (0.02) of a pixel at its distance (from `clip.w`, the projection
and `VIEWPORT_SIZE`), never more than `grow_most` (5 mm), and by a fixed `grow_shadow` (0.2 mm,
a fiftieth of a texel) in the sun's orthographic shadow pass, which gives no viewport size: growing
by a fraction of a pixel of nothing there covered the shadow map with every face, at a second a
frame. Faces that meet then overlap, and the colour is still read within each face's own extent.
Afterwards the same views had 81, every one on the horizon or in the GridMap's renders too. A convex
edge stands out a fiftieth of a pixel further, which flips one MSAA sample of a few edge pixels (as
many lighter as darker); two renders side by side at 2x look the same. Growing the faces in the mesh
by a fixed 2 mm instead thickened edges a fifth of a pixel up close, and splitting edges at every
T-junction would add triangles.

**Chunks are drawn in sections** of 2 x 2 x 2 (`SECTION_SHIFT` 1): one `ArrayMesh` and one draw call
a section, BoundaryMap 99, CombatMap 25, LineOfSightTest 36. A redraw meshes the chunks again, then
merges their sections again (`refresh(budget)`): 0.62 ms to find a chunk's quads, 0.28 to make its
arrays, 0.45 to merge its section. Recolouring uploads only the chunks' layers, once a frame. The
editor keeps `SPARE_LAYERS` (32) layers free so painting into new chunks does not remake the
texture.

**Collision is a trimesh a chunk** on the terrain layer (1), as exact as what is drawn, made only in
the game, never in the editor. It is the dearest part (1.43 ms a chunk, the physics working each
trimesh out as it gets it), so a level is drawn at once and given its collision over the frames
after, `collision_budget` (2 ms) a frame (`stream_collision()`), BoundaryMap's in about 670 ms of work,
5-6 s at 60 fps. Anything about to put debris somewhere has the chunks round it given theirs first
(`VoxelLevel.ensure_collision(box)`: bites, craters, a piece breaking or falling, a death's lumps and
gear). A chunk worn since its collision was made gets it again in `VoxelLevel._physics_process`,
ahead of the next physics step and of `VoxelDebris`, which lets new lumps go in its own
`_physics_process` later in the tree: so the collision is off the bite's frame, and no lump starts out
inside the voxels it was (without that, 6 bites in 12 let their lumps go into the old collision). The
rules never wait on collision, nor does the camera's drag, which takes hold of the ground through
`CombatGrid.cast()` (`CameraRig.grid_path`).

**The look matches the GridMap's.** Rendered from the same cameras, the units and HUD hidden:
BoundaryMap's start view differs in 3.7% of pixels, all along colour edges, and four fixed views in
0.1-3.2% (the most in a high wide one, where distant crates' colour edges blend a little differently).
With the faces grown past their edges, 6.6% and 1.2-12%, the extra pixels on edges, most of them in
the forest's crowns, each a sample's worth lighter or darker. A frame at the start of a battle draws
3.75M primitives in 386 draw calls in 3.8 ms of GPU time (an RTX 3060 laptop), against the GridMap's
5.67M, 417 and 4.7 ms.

### Scenery

**Scenery is instanced, not stamped** (`SceneryRenderer`): nothing breaks it or stains it, and 37,118
pieces would be some 8,000 chunks. Each kind is meshed once as a 16³ chunk of its own
(`ChunkMesher.rectangles(16, ..., no_down)`, its downward faces left out, since scenery is only seen
from above), its colours a layer of a texture of every kind, and drawn by one `MultiMesh` for each
kind in each 16 x 16-cell region (`REGION`), so the view culls a region at a time as a GridMap's
octants did, with shadows off as the scenery's library had them (drawn into the sun's shadow map, the
forest cost more than the rest of a frame). BoundaryMap's forest: 170 regions, 22.8M triangles (29.6M
as a GridMap), built in about 100 ms.

It is built to be cheap because it is most of what is drawn: painted like the battlefield, as a
GridMap, the forest took about 50 ms of GPU time a frame (an RTX 3060 laptop), nearly all of it trees
drawn into the sun's shadow map, on and off screen, and without shadows about 3 ms at most (not
measured again since it was instanced). Without their shadows the forest's trees look a little paler
and flatter than the battlefield's, most visibly zoomed in right beside them; they still receive the
battlefield's.

- **It has no ground blocks.** `Scenery/Ground` is one plane in the grass block's top colour, 2 cm
  below the top of the ground blocks and covering the ring's whole outer rectangle; it fills the
  corners the battlefield leaves out too. Resize it with the ring, or the sky shows between the
  trees. Its `SceneryGround` script cuts every column of the battlefield's bottom layer (the level's
  rules' `solid_cells()` at `bottom`) out of it as it readies, or a crater in the floor would show the
  plane running through it 2 cm down.
- **Only the 6 rows nearest the battlefield have trunks** (`SkinnyTree1Bottom`); past them the crowns
  hide where the trunks would be.
- **75 tiles is the standard depth for a combat map's scenery ring.** The least that hides the ring's
  outer edge is 73, found by rendering at 1280x720: zoomed all the way out (`far_distance` at
  `view_pitch`) or framed as far as it goes (`max_frame_distance` at `Reactions.camera_pitch`), with
  the pivot at its pan limit, facing any way. At 72 a sliver of sky shows past a screen corner; 75
  rounds that up. Anything that lets the camera see further (more zoom or framing distance, a lower
  pitch, a wider FOV or window, a larger `pan_margin`) needs the standard deepened to match; that is
  why `max_frame_distance` is kept to about what the zoomed-out camera sees. Debris thrown over the
  ring falls through it, having no collision, and is removed below the map.

## What the rules see

**`LevelRules`, made from the pieces, never their voxels.** Two tables of the solid pieces still
standing: `cells` (a cell to the pieces in its middle) and `edges` (an edge slot to the pieces across
it), with `bounds_min` / `bounds_max` and `bottom`. A piece is whole until it breaks
(`TerrainDestruction` calls `remove()`), however worn. Decoration (`solid` off) is left out
altogether. `CombatGrid` asks it where it asked the GridMap: `is_solid(cell)`, `has_edge(cell,
direction)` (a piece across the edge of `cell` toward `direction`, at the cell's own level),
`pieces_in()`, `pieces_across()` (both return the table's own array: duplicate before changing the
rules while going through it), `solid_cells()`, `is_standing()`. `CombatGrid.level` is the
`VoxelLevel` (`level_path`, `^"../Level"`), and `tile_at()` / `tile_position()` / `cell_center()` go
through its transform.

With no piece on an edge, the rules are the GridMap's: every tile, path, cover, sight line and shot
on the three maps compared line for line with the last GridMap commit (6891af0) came out the same,
but for 7 lines of BoundaryMap's printed floats differing in their last digit.

**Edges, by the user's answers:**

- **Cover to both sides.** `LineOfSight.cover_at()` counts a side covered if the cell beside is solid
  or a piece stands across that edge, and high if there is more of either a level up: a fence is
  low cover, a wall two courses high is full cover, on either side.
- **Stepped over a level high, never taller.** `CombatGrid._step()` / `_crossing_top()`: crossing an
  edge, a unit's feet are on the higher of the two tiles, a level higher still for a piece a level
  high across the edge there, which only a unit climbing no more than `MAX_CLIMB` can; a piece at
  any level from there to the top of the unit blocks the edge. It costs a step, as a climb does. No
  diagonal step passes a piece across any of the four edges round the corner it goes through
  (`_corner_blocked()`). The figure hops over it: `vault_height()` / `vaults_along()` give each step's
  height, which `Unit.walk(..., vaults)` hands `CharacterModel.begin_walk()`, whose `_hop` rises
  `along * (1 - along) * 4 * (vault + HOP_UP)` over the step (`MoveAction`, `TurnManager`,
  `Reactions.walk()` pass it).
- **Blocks sight.** `is_line_clear()` blocks a line crossing an edge at a level a piece stands across
  it. A line through a corner, or exactly along a boundary, could have gone either side, so it is
  blocked only if every order of its crossings is (`_edges_block()`, `_orders()`): it slips past the
  end of a wall, not through the joint between two lengths of one.
- **Whole until it breaks.** `cast()` meets an edge piece whole, at the edge (`RayHit.on_edge`),
  unless the ray is a round's (`by_voxel`) and every piece there wears away, when the cell's voxels
  are traced and a round can pass between a fence's rails or through a hole; a cell is traced only if
  every piece standing in it wears (`_stops_rounds()`). Throws and clicks meet edges whole.
- **No peeking through an edge.** `LineOfSight.lean_tiles()` skips a lean through an edge with a piece
  across it at the unit's level or the one above.
- **A miss can be aimed at edge cover.** `Ballistics._cover_faces()` adds the target's edge pieces, at
  the edge (`_cover_point()` with depth 0), and a miss aimed there counts as striking it if it struck
  that piece (`RayHit.piece`).
- **Blasts** break every breakable piece in the blast's cells and on edges with either side inside.
- **An edge piece stands** while the cell below it on either side is solid or the edge below has a
  piece (`TerrainDestruction._unsupported()`), and falls as a stack does otherwise.

## Destruction on the level

How a piece wears and breaks is `Docs/DESTRUCTION.md`'s; what changed with the volume:

- **One grid, so no seams.** A bite (`VoxelTerrain.chip()`) or a crater (`crater()`) is one roughened
  ball in the level's voxels, across however many pieces and chunks it reaches, and what it cuts loose
  is found across them too. A crater keeps to the blast's cells, a ball above the floor and a flattened
  bowl in the bottom layer, as before.
- **What is cut loose drops** (`_drop_loose()`): from every voxel next to one just lost, a search
  through solid voxels, down first, for an anchor: the floor below its `FLOOR_DEPTH`, or a standing
  piece that does not wear (a crate holds what touches it, `_anchored()`), or more than
  `HOLD_SEARCH` (1,024) voxels, which is held too. A lump hanging off one piece, held only by another
  that is itself cut loose, drops with it.
- **A piece is worn past standing** below its `collapse_below` of `whole`, or by `holds_up()` (a run
  of its own voxels joining the bottom of its box to the top, if anything stands on it). It breaks
  (`TerrainDestruction._break()`): out of the rules at once, `take_piece()` takes its voxels, which
  crumble, and `roughen_hole()` wears a rim `RIM_DEPTH` (1.5) voxels into every wearing piece round
  the hole, wandering by `RIM_WANDER` (1.2), so a broken block leaves a ragged hole, not a clean cube.
  A crate (`ScriptedDestruction`) shatters at `frame_of(piece) * model_transform`, where its model
  was drawn.
- **Stacks and edges fall.** A piece left on nothing falls whole as a `FallingBlock` built from what
  is left of its voxels (a `VoxelModel` of them in the level's palette, `_drop_whole()`), and breaks
  where it lands (`_on_landed()`).
- **Lumps wake.** `LevelRenderer.chunk_redrawn` wakes the debris lying on a chunk drawn again.
- **What wear lays bare is the inside of the ground.** A kind's model is coloured as a block standing
  alone: the grass's turf hangs down all four of its sides (darker rows 11 to 14 of its edge columns).
  Where two blocks meet those skins are buried against each other, and a crater four voxels deep
  showed every block's outline, a cross where four blocks (and four chunks) met; a broken block's hole
  showed its neighbours' skins. `VoxelVolume.lay_bare()` recolours a voxel of a kind that wears away
  (never a crate: a lid stays a lid when the crate on it goes) that was buried on every side until
  now, sits on the edge of its own piece's box, and has a piece of its own kind placed in the slot
  across that edge: it takes the colour its own model gives the voxel just inside. It is queued and
  done all at once (`flush_bare()`) as the level is next drawn, before any chunk is meshed again: a
  bite's at once, a blast's the next frame (about 8 ms for a frag grenade's crater), off the blast's
  own frame. A whole piece breaking looks only at the voxels just outside its box
  (`lay_bare_box()`). Nothing that could be seen before changes, and nothing in the rules reads a
  colour.

Costs on BoundaryMap, headless, against the GridMap's in `DESTRUCTION.md` before this step:

| | Level | GridMap |
|---|---|---|
| A round's bite in a ledge | 4.7 ms (gather 0.6, wear 1.1, redraw 2.7, lumps 0.3; the redraw 2.2 before corners carried their places) | 4-6 ms |
| A round's bite in the floor | 2.4 ms | |
| A frag grenade's crater | 21 ms; then 8 ms laying bare and 3.4 ms of redraws over the next frames | 15-50 ms with the rest of the blast |
| A whole blast among crates on raised ground | 38 ms | up to 50 ms |
| A crate breaking | 9 ms (7.2 to 9.5 over twelve, measured again after every voxel model came to be drawn one way; 7.3 before, 1.8 of it looking round its box for what it lays bare) | 2.2 ms |
| The collision of a worn chunk | 1.43 ms, ahead of the next physics step | on the bite's frame |

## Blood on the level

**Blood recolours the level's voxels**, by the user's choice: `BloodFlow.VolumeSurface` runs a stain
over the volume's faces and `stain()` is `VoxelVolume.recolor(voxel, BLOOD)`, so the next frame
uploads that chunk's layer and nothing is rebuilt. A stained voxel's every open face shows red, where a
stain used to be a face. Wherever the voxel goes its colour goes: its lump is red, a piece falling
whole is drawn as a `VoxelModel` of its voxels in the level's palette, and crumbling keeps it. A
crate is the one hand-off: its pieces are models of their own, so `VoxelTerrain.carry_blood()`
recolours every voxel of each piece that sat in a voxel blood reached. Since 2026-10-20 every other
voxel model is recoloured the same way, by the user's choice (`Docs/VOXELS.md`): loose models,
props on figures and the figures themselves no longer have overlays.

## The level editor

The level editor is a Godot editor plugin (`addons/level_editor/`): select a map's `Level` (or
`Scenery`) and paint pieces from the **Level** panel beside the 3D view, in the middles of cells and on
the edges between them, a stroke one undo step, the pieces saved to the level's own file with the
scene. It goes through the level's own edits (`VoxelLevel.place()`, `insert()`, `remove()`, batched by
`begin_edit()` / `end_edit()`), which draw again only the chunks the changed pieces reach, by way of
`LevelEditing`, which holds what a click does apart from the editor, so a probe can do the same.
`Docs/LEVEL_EDITOR.md` has all of it: every control, how painting behaves, making a map, adding
kinds and brushes, how it works, how to probe it, its gaps and what was decided.

## How the maps came over

`LevelImport.from_grid_map()` read each GridMap, cells sorted, every block a piece of the same name in
the middle of its cell, turned as the block was (all were 0); a script then swapped each scene's
`GridMap` for a `Level` and BoundaryMap's `Boundary` for `Scenery`, its `Ground` under it, and pointed
`CombatGrid`, `CameraRig`, `TerrainDestruction` and `SceneryGround` at them. The GridMap scenes are in
git at 6891af0. The editor's **Import GridMap** does the same for any GridMap still about.

## Probing it

Everything here runs headless unless it renders (Verification).

- **A level's numbers:** `level.data.count()`, `level.volume.chunks.size()`,
  `level.renderer.section_count()`, `level.renderer.triangles`, `level.build_times` (voxels, drawing,
  in microseconds), `level.renderer.is_collided()`, `level.scenery_renderer.region_count()`.
- **The rules against a reference:** dump every tile, its neighbours, cover, reachable steps, sight
  and `find_shot()` for a grid of pairs, from this tree and from a checkout of 6891af0, and diff the
  two (how the conversion was checked).
- **Edges:** LineOfSightTest's lanes, north of the old ones (z -29 to -36): a fence across x 3 to 12
  between z -31 and -30; a wall two courses high between z -35 and -34 with a gap at x 8; a turned
  length of wall between x 13 and 14 at z -33. The checks made there: cover each side, stepping over
  the fence and back (`vault_height` 1), no diagonal past it but past its end, sight over it, no step
  or sight through the wall, sight along it, through the gap and past its end, none through a joint,
  the turned wall's cover, a whole ray meeting the fence at its edge and a round meeting its voxels,
  leaning beside the wall, a shot at the fence's cover and none through the wall, sight both ways
  over 6,000 random pairs, a fence shot away losing its cover, the lower course broken and the upper
  falling and landing, and stepping where the wall was.
- **Edits:** apply random edits through `LevelEditing.apply()` to a level and undo and redo some, then
  compare every chunk's `colors`, `slots` and rows with a level built afresh from the same
  `LevelData`: 96 edits, none differing.
- **The editor** is probed headless through `LevelEditing`, and in a running editor through the
  plugin's own hook for a probe (`VCOM_LEVEL_EDITOR_PROBE`): `Docs/LEVEL_EDITOR.md`, "Probing it".
- **Wear and blood** are probed as before (`CLAUDE.md`'s Verification, `Docs/BLOOD.md`): a hit from
  `grid.cast(origin, direction, distance, true)` has `voxel` and `piece` (`has_voxel()`);
  `level.volume.counts[piece]` is what a piece has left; blood is the voxels whose
  `volume.color_at()` is `VoxelVolume.BLOOD` (in a chunk, `chunk.colors.count(VoxelVolume.BLOOD)`).
- **Collision in time:** after a bite, await `physics_frame` and then `process_frame`:
  `level.renderer.has_worn_collision()` should be false, and the lumps no faster than they were
  thrown (`VoxelTerrain.CHIP_SPEED_MAX` and what they carry).

Made in a second pass (2026-10-20), and worth running again after a change to the volume, the mesher
or the shader:

- **Every face drawn, and nothing else:** for every chunk, mark each of `renderer._quads[key]`'s
  rectangles (`ChunkMesher`'s fields: axis, side, slice, along, down, width, height) in six masks of
  32-bit rows, and compare them with the faces open to the air found from the chunk's `rows_x` /
  `rows_z` and its six neighbours' (the floor's underside left out): every open face drawn exactly
  once, no hidden face drawn, none missing at a chunk's edge, no chunk stale; check each chunk's rows
  against its `colors`, and each section's mesh (four corners a rectangle) against its chunks'. On
  BoundaryMap fresh, after 24 bites, 4 blasts and 6 broken blocks, and after 47 edits straddling
  chunks: exact every time (917k open faces in 134k rectangles), in about 3.4 s each.
- **Later wins:** two kinds in one slot, each turned, in both orders, then the later erased: every
  voxel of the box is the later's where its model has one, else the earlier's, in owner and colour.
- **Cracks:** render views with the environment's background a flat magenta (`BG_COLOR`), the units,
  HUD and highlights hidden, and count the isolated magenta pixels (at most 2 of their 8 neighbours
  magenta), here and in the GridMap tree; crop each one the old tree lacks and look. The horizon
  makes a few.
- **Old against new:** one probe script, run in this tree and in a checkout of 6891af0, writes the tile
  `pick_tile()` gives at every 40th screen point through the map's own camera, every throw each squad
  member can make and where each arc ends, and 296 seeded rounds between random tiles, hit and miss,
  where each stops and the cell and face it strikes: the two files came out identical, 2,098 lines.
- **Gameplay:** a soldier stood on a crate drops to the ground when it breaks; an enemy walked past a
  soldier on overwatch opens the window, the reaction is fired (`Reactions._fire()`) and the walk goes
  on; a whole AI turn plays out.
- **Edge pieces on raised ground,** placed at run time on LineOfSightTest's open ground (then
  `grid._ready()` takes up the new rules): a fence at a raised block's foot is cleared by the climb;
  one on its rim stops the climb up but not the hop down off it, and is half cover up there; one at
  head height stops the step under it and the eye line, and is no cover; one course of wall is stepped
  over and is half cover. The hop over the lanes' fence rises to 1.35 and ends on the far tile.
- **Laid bare:** set a crater off at a corner where four chunks meet (cell (16, 1, -28)'s least corner
  on BoundaryMap) and look at its floor from close, and break a ledge block and look into the hole
  from in front: no lines where blocks met. `flush_bare()` returns how many it recoloured.

## Known gaps

- Maps are still whole, painted levels: plots and parcels (the user's next step) are not built, and
  nothing yet places a level's pieces at load from parts.
- No auto-tiling: a fence's or a wall's ends, corners and joints are placed piece by piece, and a
  corner, which is no slot, is two lengths meeting end to end, with no post of its own.
- A piece stands a whole level; nothing is half a level. The rules know only where a piece stands,
  never its shape: a fence is low cover however open its rails, and a wall worn through is still a
  wall until it breaks.
- The level is built in full every time a map loads (about 0.75 s for BoundaryMap's battlefield,
  collision after), in GDScript; nothing is cached between loads, and an exported build will need the
  `.vox` files (Known gaps).
- The volume keeps 80 KB a chunk in memory whether a chunk is full or nearly empty; a level many
  times BoundaryMap's will want sparse chunks or a smaller palette byte.
- Collision streams in over the first seconds; what lands before a chunk has it is given it first,
  but a physics query on the terrain layer from anything else (none today) would miss it.
- The editor's gaps are `Docs/LEVEL_EDITOR.md`'s ("Known gaps: what it does not do").
- Decoration (`solid` off, `TallGrass`) is drawn into the volume, so debris lands on it, blood
  stains it and a blast's crater blows it away (its kind wears), but a round passes through it, and
  it never breaks whole: not being in the rules, it has nothing to break out of
  (`TerrainDestruction._break()` takes only standing pieces).
- A crate breaking costs about 9 ms against the GridMap's 2.2 (its voxels taken out of the volume, what it
  lays bare, and its chunks drawn again), and a crater about the same as before, with 8 ms of laying
  bare on the next frame; all are GDScript loops over voxels.
- A block broken outright leaves a square hole the block's size: its rim worn ragged and its walls and
  floor laid bare as earth, but the grid still shows in its outline, as a block being whole until it
  breaks has it.
- The hop over a fence rises as over a whole level (1.35 at its peak), whatever the piece's own
  height: a fence 0.75 high is cleared with room to spare.
- What wear lays bare takes the colour just inside its own block; a kind whose inside is not one
  colour, or two kinds of ground side by side, would want a colour of their own for it.
- Scenery is never drawn into the volume, so it cannot break or take blood, as before.

## Decided without asking

The user's decisions are listed under "Why levels". Made along the way without asking:

- The editor is a Godot editor plugin, not a standalone application (`Docs/LEVEL_EDITOR.md`, "Why a
  plugin", with the editor's other calls).
- 32³ chunks (measured, see "The chunk size"); sections of 2 x 2 x 2 chunks for draw calls.
- Faces merged by shape alone, their colours read from a texture, and the in-face "sharp bilinear"
  blend so colour edges stay as smooth as geometry's under MSAA.
- The palette: 254 colours a level, the nearest standing in past that; blood one place, 255.
- Collision as a trimesh a chunk, streamed after the level is drawn, and a worn chunk's made again
  ahead of the next physics step rather than on the bite's frame.
- Scenery instanced by kind and region rather than stamped, its downward faces dropped.
- A ragged rim worn round the hole a wearing piece leaves as it breaks, so holes do not show the grid.
- What holds a voxel up: the floor, or a piece that does not wear, or a search too long to finish.
- Edge rules beyond the user's: stepping over a fence costs a step, as a climb; no diagonal past any
  edge piece; a sight line at a corner blocked only if blocked whichever way round; no lean through an
  edge; an edge piece stands while either cell below it, or the edge below, is solid; a blast breaks
  edges with either side inside it; a round can pass between a fence's rails.
- Blood recolours only the level's voxels; loose models, props and figures keep their overlays,
  being no part of the volume (recolouring them would mean a texture each, which the user wanted to
  avoid, or rebuilding their meshes). Undone at the user's asking the next step (2026-10-20): every
  voxel model is recoloured by texture writes, a texture each model blood reaches
  (`Docs/VOXELS.md`).
- New kinds: `FenceStraight`, `StoneWall` (a new model, `make_shapes.py`'s `stone_wall()`) and
  `TallGrass`, their destructions' numbers, and the brushes; LineOfSightTest's edge lanes.
- `TileGrid.gdshader`, `BlockLibrary.tres`, `SceneryLibrary.tres`, `Catalog.tres`, `WornBlock` and
  `DestructionCatalog` are gone: the level's shader draws the grid, `Pieces.tres` is the one library,
  and a kind holds its own destruction. The style harness (`Styles/harness/`) warns rather than
  previews a block material on a level.
- The camera's drag takes hold of the ground through the grid rather than the physics.
- Faces grown a fiftieth of a pixel past their edges in the shader, to close the T-junctions' cracks,
  rather than split at every T-junction (more triangles) or grown a fixed size in the mesh.
- What wear lays bare inside the ground takes the colour inside its own block, for kinds that wear
  away, where the same kind is placed across; queued to the next redraw.
