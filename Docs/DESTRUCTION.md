# Destruction

Adding a breakable block, and voxel wear, in full: the two recipes, how a block wears away
(`VoxelTerrain`, `WornBlock`, `VoxelDebris`) and how a crate's pieces do, as loose models
(`VoxelBody`). It was split out of `CLAUDE.md`, which keeps a summary and what every block shares
("Breakable blocks are data", "Stacks fall, then break", the coins, the physics layers, how pieces
are found), the rules that must not drift, and how to probe destruction (Verification). A section
named here that is not in this file (Gotchas, Verification, Known gaps, another subsystem's notes)
is `CLAUDE.md`'s.

## A block that breaks into cut pieces

To make another object break like the crate:

1. Model the pieces in MagicaVoxel in the same frame as the block's own model, as separate models.
2. Import the `.vox` as a Scene at **Scale 0.0625**, the blocks' scale, or the pieces will not line
   up with the block they replace. Make an inherited scene of it in `Scenes/` to add to.
3. Make a `ScriptedDestruction` `.tres` in `Resources/Destruction/` naming the block and that scene,
   and add it to `Catalog.tres`. Set its **Mass** to what the block weighs whole, if it is not
   about a crate's 300 kg; that is only felt while it falls. Set its **Coin Chance** (0 to 1) if it
   should leave coins, as a crate does three times in four. Set its **Wear** (see below) if blood on
   the block should go to its pieces when it breaks: only pieces that wear can carry stains.

Every bare mesh in the scene becomes a rigid body with a box collider, 3.5% smaller than the mesh
(`ScriptedDestruction.SLACK`, see Gotchas); a `RigidBody3D` you author is used as it is, and other
nodes are left alone. A new way of breaking is a `Destruction` subclass that overrides `shatter()`,
the same shape as a new enemy being an `EnemyAI` subclass; it should honour `motion` when given
one, adding `motion.at(point)` to what it throws each part of the block at.

That block just collapses, which is the default. To have it burst apart instead, as the crate does:

4. In the pieces scene, add a `Marker3D` named **`DestructOrigin`** where the blast goes off, with a
   `float` metadata entry **`force`**: 1 is a moderate blast (a crate's boards land about a cell and
   a half out, nine in ten within three), 2 is twice as hard, 0 is none; left out, it is 1.
5. Tick **Blast** on the block's `ScriptedDestruction` `.tres`.

Untick Blast to go back to the plain collapse; the marker is then ignored, so it can stay in the
scene. The blast goes off every time the block breaks, including when it comes down because the
block under it broke. Blast on with no marker warns and collapses. Where the marker sits shapes the
burst: the crate's is at the bottom centre, like a charge underneath, so it throws up and out; one
at the middle of the block throws evenly every way.

`Blast.burst(pieces, origin, force)` works on any `RigidBody3D`s, so a new `Destruction` can use it
too. Each piece gets an impulse away from the origin of `force * Blast.IMPULSE / (r² + Blast.CORE²)`
times the area it turns toward the origin (from its box colliders), applied at its point nearest the
origin. So the push falls off with the square of the distance, as a real blast's does, but stays
finite at the origin; a board facing the blast is thrown harder than one edge-on to it, a light
piece further than a heavy one, and pieces tumble as they fly. `IMPULSE` is what force 1 means, and
is the only thing to retune if every blast is too strong or too weak.

## A block that wears away

**Some blocks wear away instead, a few voxels at a time.** A block whose catalog entry is a
`VoxelDestruction` (`BrightGrass1`, both `SkinnyTree1` blocks) is the second kind of breakable block:
a strike or a blast breaks voxels off it rather than breaking it whole. Every block is 16 voxels a
side, and its voxels are read on ready from the `.vox` its MeshLibrary mesh was imported from
(`VoxelShape.read()`, with the importer's own reader, so they sit exactly where the imported mesh
draws them). `TerrainDestruction` makes a `VoxelTerrain` node, which keeps them, and a `VoxelDebris`
node, which keeps what is broken off, and hands the grid the terrain (`CombatGrid.voxels`).

- **A worn block draws itself; the rules see its stand-in.** The first time a block loses a voxel,
  `VoxelTerrain` makes it a `WornBlock` (its own mesh and trimesh collision, rebuilt as it wears) and
  swaps its GridMap cell to the block's stand-in, an item `take_on()` added to the map's library copy
  with no mesh and no shapes. `CombatGrid.is_solid()` only asks whether a cell has an item, so sight,
  cover, paths, throws, coins and units see the whole block, however little is left. Anything that
  reads a cell's item id must allow for a stand-in (`VoxelTerrain.wears_away()`, `shape_at()`, or
  `kind_of()` for any block drawn from a `.vox`, worn or not).
  Unworn, a block that does not fill its cell (a tree) collides as its voxels, a trimesh from
  `VoxelMesher.faces()`; a full one keeps the cube.
- **A round takes a bite.** `terrain_struck` on such a block calls `VoxelTerrain.chip()`: the
  `damage * voxels_per_damage` voxels nearest where it struck (12 a point; 60 for a rifle's 5),
  roughened with noise, from whichever blocks they are in, out to `BITE_SPREAD` times the bite's own
  radius. They fly out of the struck face in lumps up to `DEBRIS_CLUMP` (2) voxels across, and the
  block is redrawn at once.
- **A blast blows a crater.** `terrain_blasted` calls `VoxelTerrain.crater()` first: every voxel within
  `crater_radius(damage)` of where it goes off (a ball of `crater_per_damage` cubic cells a point,
  a radius of about 1.06 cells for a frag grenade's 10), roughened, but only in the blast's
  cells. Up to `CRATER_DEBRIS` (150) lumps are thrown up and out, the ground throwing back what the
  blast drives into it; the rest is dust. They are chosen before any is made: what wear breaks off
  comes back grouped into lumps (`Batch`), and `_scatter()` makes only those it keeps, since making a
  lump costs about three times what grouping its voxels does (a grenade on raised ground breaks off
  some 1,600 lumps). Its blocks are redrawn over the next frames, no more than `REBUILD_BUDGET`
  microseconds a frame, under the fireball.
- **What is cut loose drops.** After any wear, a voxel left joined to nothing that holds it (a voxel
  or block across a face of its cell, or the ground under the bottom layer) breaks off too
  (`_loose_voxels()`, searched from the voxels next to those just lost, which the rows find).
- **Worn past standing, it breaks.** A block left with less than `collapse_below` (half) of its voxels,
  or one holding something up that nothing joins from its bottom to its top any more (`_holds_up()`:
  the trees' trunk is one 4x4 layer of voxels at its narrowest, so a couple of rounds through it fell
  the tree), is in `Wear.broken`, and `TerrainDestruction` breaks it as it breaks a crate: out of the
  grid at once, `block_broken`, stacks above fall, units drop. What is left crumbles
  (`VoxelTerrain.crumble()`) into lumps `crumble_size` (3) across; one that fell whole
  (`_drop_worn_block()`, a `FallingBlock` showing what is left of it) crumbles where it lands.
- **The bottom layer never breaks,** and is only worn `FLOOR_DEPTH` (4) voxels deep, since a unit
  stands at the top of its block whatever is left of it. A crater there is a flattened bowl centred
  under the blast, as wide as the ball is where it meets the ground.
- **Rounds are traced voxel by voxel.** `CombatGrid.cast(..., by_voxel)`, which of the rules only
  `Ballistics` passes, asks `VoxelTerrain.trace()` in each solid cell that wears away and carries on
  through the cell if the ray meets none of its voxels; the hit's `point` and `face` are then the
  voxel's, and its `index` the voxel's place in its block. Sight (`is_line_clear()`), throws
  (`Throwing.plan()`) and clicks (`pick_tile()`) stop at whole cells. Blood passes `every_block` as
  well, which traces every block drawn from a `.vox` so, crates included; rounds never do.
- **The debris is lean.** `VoxelDebris` makes each lump a rigid body straight on the `PhysicsServer3D`,
  with no node, on the debris layer, and draws every voxel as a cube instance of a few MultiMeshes,
  coloured as it was. A lump's voxels move only from the server's state-sync callback, so a lump at
  rest costs nothing a frame. Blasts push it (`burst()`), a redrawn block wakes what lay on it
  (`wake()`), `TerrainDestruction` tidies it with the rest (`tidy()`), and units dropping through a
  collapse pass through it, which is why `Unit.pass_through()` and `drop_to()` take body RIDs.
- **Lumps stay for good; their bodies do not.** The moment the lumps' bodies reach
  `VoxelDebris.MOST` (20,000), `_make_room()` stills the lumps at rest furthest from `focus` (the
  middle of the tile the camera is looking at, `TerrainDestruction._looked_at()`: where the middle of
  its view first meets the ground) until fewer than `KEEP` (5,000) have bodies. A stilled lump loses
  its body but stays drawn where it lies, so nothing leaves the board, and the bodies go to what the
  player is watching and to everything broken off from then on. A lump that moved in the last
  `RESTING_STEPS` physics steps is never stilled, so nothing freezes in mid-air. A stilled lump gets
  its body back, lying as it lay, the moment anything disturbs it: a blast reaching it (`burst()`), a
  worn block under it being redrawn or a broken one going (`wake()`, `LYING_ON` round the block, the
  whole column above a broken one), or a unit on the move coming within its cell
  (`TerrainDestruction._wake_in_the_way()`). Lumps are filed by the world cell their middle was last
  in (`_by_cell`), so those calls look only at the cells they reach. Clearing 15,000 bodies takes
  about 30 ms, on the frame that reaches the limit.
- **It is deterministic.** Which voxels go, and so which blocks break, comes from the global random
  generator, one number a round or blast, so a seeded fight replays exactly, as long as no block
  falls whole (see Known gaps). How the lumps fly, and which a blast keeps, draws on `VoxelTerrain`'s
  own generator, and how they fall is physics: only for show.

To make another block wear away, add a `VoxelDestruction` `.tres` naming it in
`Resources/Destruction/` to `Catalog.tres`, with its `mass` whole (what it weighs falling), its
voxels' `density`, and `voxels_per_damage` / `crater_per_damage` for how soft it is. Its mesh must be
imported from a `.vox` at Scale 0.0625, one cell to sixteen voxels.

## Loose models

**A broken crate's pieces wear away as well, as loose models.** The crate still breaks into its
pieces as cut, and bursts as before; only then do they break down further, as a block does. Any
voxel model loose in the world can be worn this way: a `RigidBody3D` drawn by a MagicaVoxel model in a
`MeshInstance3D` among its children, taken on with `VoxelTerrain.take_on_body()`, which puts a
`VoxelBody` node under it. So far only a `ScriptedDestruction`'s pieces are.

- **A piece is taken on the first time something reaches it.** A `ScriptedDestruction` with a `wear`
  (a `VoxelDestruction`; `BrightCrate1.tres` has `CrateBoards.tres`: 3 voxels a point of damage, lumps
  of 2) only notes each piece as `shatter()` makes it (`VoxelTerrain.take_on_later()`, a `Wearable`),
  with the bodies `_pass_overlaps()` found it overlapping. A round's line or a blast's crater reaching
  it takes it on (`_model_of()` calls `take_on_body()`): its voxels come from the `.vox` the pieces
  scene inherits (`VoxelShape.source_of()`), the model whose `magica_voxel_model_id` the importer put
  on its `MeshInstance3D`, cropped to its voxels (`read_model()`): each of the crate's models is a
  whole crate's frame with only that piece in it, 36 to 64 voxels. Most pieces are never hit, and
  taking one on (copying its voxels, a node, its bounds) cost a crate 1.7 ms of its 3.6. A blast takes
  on only the pieces whose box its crater reaches. `Destruction.prepare()` reads every piece's model
  as the map loads (about 10 ms for the crate), so the first crate to break does not catch on it.
- **A round tears through them and flies on.** `Unit.shoot_at()` reports every round's line, from the
  muzzle (where its tracer starts) to where it landed, through `CombatGrid.fly()`, whose `round_flown`
  calls `VoxelTerrain.tear()`. Every loose model the line passes through (ray queries on
  `PIECE_LAYER`, nearest first, at most `MOST_TORN`, 8) loses the `damage * voxels_per_damage` voxels
  nearest where the line first meets one of its voxels (`VoxelTerrain.march()`, the static voxel walk
  `trace()` uses on blocks and blood uses on figures and props; 15 for a rifle's 5), which fly out of
  the face it went in by. `fly()` comes before
  `strike()`, so a crate a round breaks is not torn by the same round.
- **A blast craters them.** `crater()` craters every loose model reaching into the blast's box
  (`TerrainDestruction.pieces_in()`) as it does blocks: the voxels within its `crater_radius()` and
  inside the box. The burst a physics step later throws them, as it throws every piece.
- **What is left settles** (`_settle()`). A model left with fewer than `SMALLEST_PART` (8) voxels, or
  under its destruction's `collapse_below` of `VoxelBody.whole`, crumbles into lumps `crumble_size`
  across, carrying on as it moved, and its body goes. Otherwise every part no longer joined face to
  face to the biggest (`_parts()`) is cut off: as a model of its own if it has `SMALLEST_PART` voxels
  (`_split_off()`: a new `RigidBody3D` and `VoxelBody` beside it, in the same frame, moving as that
  part moved), as lumps if not. What is left is redrawn (`VoxelMesher.surface()`), its box collider
  fitted to it (shrunk by `ScriptedDestruction.SLACK`), and it weighs its share. After a cut each
  part's `whole` starts again from what it has, so a board shot in two is two boards, each worn down
  from its own size.
- **A part cut off passes through what its model did.** Their boxes overlap wherever the cut ran, so
  a part passes through the model it came from, everything that model passed through (a crate's
  pieces cut to overlap), and every part cut from it since; `VoxelBody.passes` keeps the list on both
  sides, and a piece not yet taken on keeps its own in its `Wearable` (see Gotchas).
- **It does not touch the rules.** A loose model blocks nothing (sight, cover, rounds, throws), and
  everything random about wearing one draws on `VoxelTerrain`'s own generator (`_show`), never the
  global one, so tearing boards never changes what a seeded fight rolls next. Blocks still take one
  global number per round or blast.

A crate breaks in about 2.2 ms; a round through boards costs 1 to 3 ms, taking on those it hits, and
a blast among a crate's boards 14-20 ms more than the blast alone, about 2 ms of it taking on the
boards its crater reaches. To have
another `ScriptedDestruction`'s pieces wear, set its `wear`: its pieces scene must inherit a `.vox`
imported as a Scene at 0.0625. A body made some other way can be taken on directly, its `source` the
`.vox` its model came from, or none if the mesh was imported straight from a `.vox`.

## Known gaps

`CLAUDE.md`'s Known gaps keeps those a rule or a probe meets: crates breaking whole on any hit, a unit
floating over a crater, a worn block's full cover, what a seeded fight replays, and what an export
needs.

- Rounds fly straight through debris: the trace only sees the grid, and the voxels of blocks that wear
  away. They tear the loose models they pass through, but are never stopped by one.
- Only a crate's pieces wear away as loose models so far. A loose model must be a `RigidBody3D` drawn by
  a MagicaVoxel model in a `MeshInstance3D` among its children, and no more than 62 voxels along its x
  (`VoxelShape.WIDEST`); static props, units' figures and their gear cannot be worn yet, and a
  `FallingBlock` is not one until it lands.
- A loose model collides as the box round what is left of it, so a board shot into an L lies as its
  box, and a part cut off one passes through its whole family of parts for good.
- A bite costs about 4-6 ms on the frame it lands and a grenade 15-50 ms, the most among crates and on
  raised ground (gathering and removing voxels, cutting lumps and meshing in GDScript), more for each
  block it brings down; the blast's redraws spread over the next few frames.
- A lump of debris collides as the box round its voxels, so one that is not a full box rests a little
  proud of what it lies on.
- A stilled lump is woken only by a blast, the block under it being worn or broken, or a unit walking
  into it. A crate's board, dropped gear or a falling block coming down on one passes through it, and a
  lump still on the move can come to rest inside it.
- A column of crates broken between two standing columns mostly heaps up in its own one-cell slot.
  The columns either side hold the struck crate's wreck in place, so the crates above only drop a
  fifth of a cell on to it before breaking, and their pieces take more room loose than as crates.
  Stood in the open the same stack clears its column. Clearing a slot would need debris that can
  be crushed, or thinned out once it settles.
