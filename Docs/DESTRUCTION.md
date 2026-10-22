# Destruction

Adding a breakable block, and voxel wear, in full: the two recipes, how a level's pieces wear away
(`VoxelTerrain` over the level's `VoxelVolume`, `VoxelDebris`) and how a crate's pieces do, as loose
models (`VoxelBody`), and what `CLAUDE.md` only summarises: stacks falling, how coins are drawn and
the physics of debris. It was split out of `CLAUDE.md`, which keeps a summary and what every block
shares ("Breakable blocks are data", "Stacks fall, then break", the coins, the physics layers, how
pieces are found), the rules that must not drift, and how to probe destruction (Verification). The
level itself (its pieces, volume, edges and editor) is `Docs/LEVELS.md`'s. A section named here that
is not in this file (Gotchas, Verification, Known gaps, another subsystem's notes) is `CLAUDE.md`'s.

A "block" here is any piece of a level, in the middle of a cell or on an edge, 16 voxels a side.

## A block that breaks into cut pieces

To make another object break like the crate:

1. Model the pieces in MagicaVoxel in the same frame as the block's own model, as separate models.
2. Import the `.vox` as a Scene at **Scale 0.0625**, the blocks' scale, or the pieces will not line
   up with the block they replace. Make an inherited scene of it in `Scenes/` to add to.
3. Make a `ScriptedDestruction` `.tres` in `Resources/Destruction/` naming the block and that scene,
   and make it the `destruction` of the block's `PieceKind` in `Blocks/Pieces.tres` (a new kind as
   `Docs/LEVEL_EDITOR.md`, "Adding kinds and brushes", says). It shatters where its kind's model is drawn
   (`VoxelLevel.frame_of()` times the kind's `model_transform`). Set its **Mass** to what the block weighs whole, if it is not
   about a crate's 300 kg; that is only felt while it falls. Set its **Coin Chance** (0 to 1) if it
   should leave coins, as a crate does three times in four. Set its **Wear** (see below) if blood on
   the block should go to its pieces when it breaks: only pieces that wear can carry it.

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

**Some pieces wear away instead, a few voxels at a time.** A kind whose destruction is a
`VoxelDestruction` (`BrightGrass1`, both `SkinnyTree1` kinds, `FenceStraight`, `StoneWall`,
`TallGrass`, `SimpleWall1`, `SimpleTruss1`, `SimpleRoof1`) is the second kind of breakable piece: a strike or a blast breaks voxels off it rather
than breaking it whole. Every piece is 16 voxels a side, and its voxels are part of the level's one
grid of voxels (`VoxelVolume`, see `Docs/LEVELS.md`), stamped from its kind's `.vox` as the level is
built (`VoxelShape.read()`, with the importer's own reader, so they sit exactly where the imported mesh
draws them). `TerrainDestruction` makes a `VoxelTerrain` node, which wears them, and a `VoxelDebris`
node, which keeps what is broken off, and hands the grid the terrain (`CombatGrid.voxels`).

- **A worn piece is drawn by the level; the rules see it whole.** Wear takes voxels out of the volume
  and the level draws what is left (`LevelRenderer`): a bite at once (`VoxelLevel.redraw_now()`), a
  blast's chunks over the next frames, `VoxelLevel.redraw_budget` (4 ms) a frame, under the fireball.
  `LevelRules` reads pieces, never voxels, so sight, cover, paths, throws, coins and units see the
  whole piece, however little is left, until it breaks. It collides as the level does, a trimesh a
  chunk, made again ahead of the next physics step once worn.
- **A round takes a bite.** `terrain_struck` on such a piece calls `VoxelTerrain.chip()`: the
  `damage * voxels_per_damage` voxels nearest where it struck (12 a point for grass and trees; 60 for
  a rifle's 5), roughened with noise, from whichever pieces and chunks they are in, out to
  `BITE_SPREAD` times the bite's own radius. They fly out of the struck face in lumps up to
  `DEBRIS_CLUMP` (2) voxels across.
- **A blast blows a crater.** `terrain_blasted` calls `VoxelTerrain.crater()` first: every voxel within
  its own piece's `crater_radius(damage)` of where it goes off (a ball of `crater_per_damage` cubic
  cells a point, a radius of about 1.06 cells for a frag grenade's 10 on grass), roughened, but only
  in the blast's cells. Up to `CRATER_DEBRIS` (150) lumps are thrown up and out, the ground throwing
  back what the blast drives into it; the rest is dust. They are chosen before any is made: what wear
  breaks off comes back grouped into lumps (`Batch`), and `_scatter()` makes only those it keeps,
  since making a lump costs about three times what grouping its voxels does (a grenade on raised
  ground breaks off some 1,600 lumps).
- **What is cut loose drops.** After any wear, a voxel joined to nothing that holds it breaks off too
  (`_drop_loose()`): from each voxel next to one just lost, a search through the solid voxels round
  it, downward first, ends held at the floor below `FLOOR_DEPTH`, at a standing piece that does not
  wear (`_anchored()`: a crate holds what touches it), or after `HOLD_SEARCH` (1,024) voxels, and
  otherwise drops all it found. It runs across pieces and chunks, reading the chunks' arrays itself,
  so a lump held only by a piece that is itself cut loose drops with it.
- **Worn past standing, it breaks.** A piece left with less than `collapse_below` (half) of its
  voxels, or one holding something up that nothing of its own joins from the bottom of its box to the
  top any more (`holds_up()`: the trees' trunk is one 4x4 layer of voxels at its narrowest, so a couple
  of rounds through it fell the tree), is in `Wear.broken`, and `TerrainDestruction` breaks it as it
  breaks a crate: out of the rules at once, `block_broken`, stacks and edge pieces above fall, units
  drop. What is left is taken out of the volume (`take_piece()`) and crumbles (`crumble()`) into lumps
  `crumble_size` (3) across, and `roughen_hole()` wears a rim `RIM_DEPTH` (1.5) voxels into every
  wearing piece round the hole, wandering by `RIM_WANDER`, so the hole is ragged, not a clean cube of
  the grid. One that fell whole (`_drop_whole()`, a `FallingBlock` built from what is left of its
  voxels, coloured as they were) crumbles where it lands.
- **What it lays bare is earth.** A voxel of a kind that wears away, buried until the wear and on
  the edge of its own block with a block of its kind across, takes the colour just inside its block
  (`VoxelVolume.lay_bare()`, queued to the next redraw), so a crater never shows the turf the grass
  model hangs down its sides where blocks meet (`Docs/LEVELS.md`, "Destruction on the level").
- **The bottom layer never breaks,** and is only worn `FLOOR_DEPTH` (4) voxels deep, since a unit
  stands at the top of its block whatever is left of it. A crater there is a flattened bowl centred
  under the blast, as wide as the ball is where it meets the ground.
- **Rounds are traced voxel by voxel.** `CombatGrid.cast(..., by_voxel)`, which of the rules only
  `Ballistics` passes, traces the level's voxels (`_trace_cell()`) in each cell whose standing pieces
  all wear away, and across an edge whose pieces do, and carries on if the ray meets none of them; the
  hit's `point` and `face` are then the voxel's, `voxel` the voxel in the level's grid and `piece` the
  piece it is of. A piece that does not wear (a crate) is met whole. Sight (`is_line_clear()`), throws
  (`Throwing.plan()`) and clicks (`pick_tile()`) stop at whole cells and edges. Blood passes
  `every_block` as well, which traces every piece so, crates and decoration included; rounds never do.
- **The debris is lean.** `VoxelDebris` makes each lump a rigid body straight on the `PhysicsServer3D`,
  with no node, on the debris layer, and draws every voxel as a cube instance of a few MultiMeshes,
  coloured as it was. A lump's voxels move only from the server's state-sync callback, so a lump at
  rest costs nothing a frame. Blasts push it (`burst()`), a chunk drawn again wakes what lay on it
  (`wake()`, on `LevelRenderer.chunk_redrawn`), `TerrainDestruction` tidies it with the rest
  (`tidy()`), and units dropping through a collapse pass through it, which is why `Unit.pass_through()`
  and `drop_to()` take body RIDs. New lumps are held until the next physics step, which the worn
  chunks' collision is made again ahead of.
- **Lumps stay for good; their bodies do not.** The moment the lumps' bodies reach
  `VoxelDebris.MOST` (20,000), `_make_room()` stills the lumps at rest furthest from `focus` (the
  middle of the tile the camera is looking at, `TerrainDestruction._looked_at()`: where the middle of
  its view first meets the ground) until fewer than `KEEP` (5,000) have bodies. A stilled lump loses
  its body but stays drawn where it lies, so nothing leaves the board, and the bodies go to what the
  player is watching and to everything broken off from then on. A lump that moved in the last
  `RESTING_STEPS` physics steps is never stilled, so nothing freezes in mid-air. A stilled lump gets
  its body back, lying as it lay, the moment anything disturbs it: a blast reaching it (`burst()`), a
  chunk under it being drawn again or a broken piece going (`wake()`, `LYING_ON` round it, the whole
  column above a broken one), or a unit on the move coming within its cell
  (`TerrainDestruction._wake_in_the_way()`). Lumps are filed by the world cell their middle was last
  in (`_by_cell`), so those calls look only at the cells they reach. Clearing 15,000 bodies takes
  about 30 ms, on the frame that reaches the limit.
- **It is deterministic.** Which voxels go, and so which pieces break, comes from the global random
  generator, one number a round, blast or broken piece's rim, so a seeded fight replays exactly, as
  long as no piece falls whole (see Known gaps). How the lumps fly, and which a blast keeps, draws on
  `VoxelTerrain`'s own generator, and how they fall is physics: only for show.

To make another kind of piece wear away, give its `PieceKind` (in `Blocks/Pieces.tres`) a
`VoxelDestruction` `.tres` from `Resources/Destruction/`, with its `mass` whole (what it weighs
falling), its voxels' `density`, and `voxels_per_damage` / `crater_per_damage` for how soft it is. Its
model must be imported from a `.vox` at Scale 0.0625, one cell to sixteen voxels.

## Loose models

**A broken crate's pieces wear away as well, as loose models.** The crate still breaks into its
pieces as cut, and bursts as before; only then do they break down further, as a block does. Any
voxel model loose in the world can be worn this way: a `RigidBody3D` drawn by a MagicaVoxel model in a
`MeshInstance3D` among its children, taken on with `VoxelTerrain.take_on_body()`, which puts a
`VoxelBody` node under it, the body of the model, its voxels and colours being the `VoxelModel` that
draws it (`Docs/VOXELS.md`). So far a `ScriptedDestruction`'s pieces are, and the gear a dying figure
drops.

- **A piece is taken on the first time something reaches it.** A `ScriptedDestruction` with a `wear`
  (a `VoxelDestruction`; `BrightCrate1.tres` has `CrateBoards.tres`: 3 voxels a point of damage, lumps
  of 2) only notes each piece as `shatter()` makes it (`VoxelTerrain.take_on_later()`, a `Wearable`),
  with the bodies `_pass_overlaps()` found it overlapping. A round's line or a blast's crater reaching
  it takes it on (`_model_of()` calls `take_on_body()`): its voxels come from the `.vox` the pieces
  scene inherits (`VoxelShape.source_of()`), the model whose `magica_voxel_model_id` the importer put
  on its `MeshInstance3D`, cropped to its voxels (`read_model()`): each of the crate's models is a
  whole crate's frame with only that piece in it, 36 to 64 voxels. From then on it is drawn by the
  voxel shader, from its model's shared mesh and texture until it wears or bleeds
  (`VoxelModel.take_over()`), which looks as the importer's mesh did. Most pieces are never hit, and
  taking one on (copying its voxels, a node, its bounds) cost a crate 1.7 ms of its 3.6. A blast takes
  on only the pieces whose box its crater reaches. `Destruction.prepare()` reads every piece's model
  as the map loads (about 10 ms for the crate), so the first crate to break does not catch on it.
- **A round tears through them and flies on.** `Unit.shoot_at()` reports every round's line, from the
  muzzle (where its tracer starts) to where it landed, through `CombatGrid.fly()`, whose `round_flown`
  calls `VoxelTerrain.tear()`. Every loose model the line passes through (ray queries on
  `PIECE_LAYER`, nearest first, at most `MOST_TORN`, 8) loses the `damage * voxels_per_damage` voxels
  nearest where the line first meets one of its voxels (`VoxelTerrain.march()`, the static voxel walk
  blood uses on figures and props too; 15 for a rifle's 5), which fly out of the face it went in by. `fly()` comes before
  `strike()`, so a crate a round breaks is not torn by the same round.
- **A blast craters them.** `crater()` craters every loose model reaching into the blast's box
  (`TerrainDestruction.pieces_in()`) as it does blocks: the voxels within its `crater_radius()` and
  inside the box. The burst a physics step later throws them, as it throws every piece.
- **What is left settles** (`_settle()`). A model left with fewer than `SMALLEST_PART` (8) voxels, or
  under its destruction's `collapse_below` of `VoxelBody.whole`, crumbles into lumps `crumble_size`
  across, carrying on as it moved, and its body goes. Otherwise every part no longer joined face to
  face to the biggest (`_parts()`) is cut off: as a model of its own if it has `SMALLEST_PART` voxels
  (`_split_off()`: a new `RigidBody3D` and `VoxelBody` beside it, in the same frame, moving as that
  part moved; `VoxelModel.split()`, its voxels with their colours, blood and all), as lumps if not,
  each lump its voxels' colours. What is left is drawn again (`VoxelModel.rebuild()`: its faces merged
  by shape alone, coloured from its texture), its box collider fitted to it (shrunk by
  `ScriptedDestruction.SLACK`), and it weighs its share. After a cut each
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

A crate breaks in about 9 ms (7.2 to 9.5 over twelve on BoundaryMap, headless; 2.2 ms on a GridMap,
before its voxels were the level's); a round
through boards costs 1 to 3 ms, taking on those it hits, and
a blast among a crate's boards 14-20 ms more than the blast alone, about 2 ms of it taking on the
boards its crater reaches. To have
another `ScriptedDestruction`'s pieces wear, set its `wear`: its pieces scene must inherit a `.vox`
imported as a Scene at 0.0625. A body made some other way can be taken on directly, its `source` the
`.vox` its model came from, or none if the mesh was imported straight from a `.vox`.

## Stacks falling

A `FallingBlock` has landed once something takes more than half its speed away after it has got
going (0.5 cells a second), once it has sat still for a quarter of a second, or three seconds after
it was let go; it reports where it was two physics steps earlier (see "Its traps" below). Where
the wreck under a falling block can get out of the way (a stack in the open, blasted apart) the
blocks fall nearly a whole cell and smash; in a one-cell slot between two columns the columns hold
the wreck in place, and the blocks drop on to it (see Known gaps). An edge piece left with nothing
under either side of it falls the same way, as heavy as its destruction's `mass`.

## Coins

`CLAUDE.md` has the rules of coins ("Coins are rolled as blocks break and go by tiles"). How one is
drawn: the `Coin` node is only for show. It is spun and bobbed on a child, so its own position is
where it rests, and the model is centred on its box, since `Coin2.vox` is drawn well off its origin.
It is nine voxels across at the props' 0.063, a little over half a cell, so it is not scaled;
`Coins.STACK_STEP` (0.7) must stay more than its height plus its bob, or a stack's coins touch.

## The physics of debris

**Physics is only for debris, the dead's included.** (`CLAUDE.md` keeps a summary of this section.) Layers: 1 terrain, 2 unit clicks
(`Unit.PICK_LAYER`), 3 debris, 4 unit bodies (`Unit.BODY_LAYER`), 5 pieces
(`TerrainDestruction.PIECE_LAYER`: debris that is a body with a node of its own, a broken block's
pieces and the parts cut from them, and dropped gear, which are on 3 as well; nothing collides with 5,
it is only searched). Blood's drops are no bodies: they find debris
with a ray on 3 (a lump by its RID, a piece through `VoxelTerrain.model_of()`, falling blocks
passed), and meet figures by their voxels, never by a unit's bodies.
What a dead unit breaks into is debris among debris: its lumps on layer 3, its dropped gear on 3 and
5, landing on terrain and other debris and shoved aside by the living. The level collides as a
trimesh a chunk on layer 1, as exact as it is drawn (`LevelRenderer`, `Docs/LEVELS.md`).
Debris stays live for good and sleeps when still. Jolt's limits on bodies, body pairs, contacts and
scratch memory are raised in `project.godot` for the voxel debris.

**Pieces are found by the physics, never by walking the scene.** Every piece is made one by
`TerrainDestruction.make_piece()` (`ScriptedDestruction._make_pieces()`, `VoxelTerrain._split_off()`):
on `PIECE_LAYER` and in the `PIECES` group. Whatever looks for the pieces in a box (waking those lying
on what wore away, the ones a blast throws, the ones its crater wears) asks `pieces_in()`, a shape query
on that layer, and the tidy looks over the group. A battle that has broken every crate leaves some 2,700
pieces, and walking the scene for them took 11-14 ms on every bite, crate and blast, and 5-6 ms every
second; a query takes 0.1-0.5 ms, and the tidy under 1 ms. A block falling whole is no piece: it lands,
or gives up after 3 seconds, by itself. Each unit carries a frictionless
`AnimatableBody3D` capsule, starting `Unit.BODY_CLEARANCE` above its feet, that shoves debris aside and
is never pushed back.
A `FallingBlock` is on the debris layer but never collides with units: nobody can stand in its
column but units dropping with it. It is 1 cm narrower than its cell on each side
(`FallingBlock.CLEARANCE`), cannot turn, and is frictionless, so it slides down between the blocks
either side of it instead of wedging between them. Debris knocked off the map, or wedged inside a
block, is removed. The rules never look at debris.

### Its traps

Jolt's and Godot's, each met while the debris was built, and each the reason something above is as
it is. `CLAUDE.md`'s Gotchas names them, and keeps the one that binds every map: `Level` before
`TerrainDestruction`.

**`AnimatableBody3D.sync_to_physics` leaves a body behind when its parent moves.** It hands the body's
transform to the physics server, and a parent moving underneath does not tell it. A unit's body moves
with the unit's tweens, so it is not synced. Jolt still moves a kinematic body with velocity when its
transform is set, so it pushes debris properly.

**New debris is held a physics step, and the level's collision catches up ahead of it.** A chunk worn
since its collision was made gets it again in `VoxelLevel._physics_process`, before `VoxelDebris`
(after it in the tree) lets that step's new lumps go, and `ScriptedDestruction` holds its pieces
frozen until the next `physics_frame` the same way. Keep `Level` before `TerrainDestruction` in each
map, or a bite's lumps start out inside the voxels they were.

**A kinematic body driven into a heap grinds thin pieces into whatever is under them.** That is why a
unit dropping into its own rubble passes through it (`drop_to`'s `rubble`), and why its body starts
above its feet.

**A board landing on a round top with friction balances there and never comes to rest.** Jolt has no
rolling resistance, so a blasted board on top of a unit's capsule kept rocking and turning, and kept
every piece it touched awake: a whole heap creeping for as long as it was watched. That is why unit
bodies are frictionless; the board slides off instead.

**Contact is only found within 2 cm, so a fast body can end a step well inside what it hit.** Jolt
makes contacts within its speculative distance (0.02); a block falling 6 cells a second moves 10 cm a
step, so the step that reaches the floor can carry it 8 cm in, still at full speed, and only the next
stops it. That is why a `FallingBlock` reports where it was two steps before it was seen to stop, and
why its pieces are let go at once with continuous collision rather than held a step.

**Anything cut exactly as wide as a gap wedges in it and shivers for good.** A board one cell long
lying across the one-cell gap a broken block leaves between two others jams at the slightest turn, and
Jolt pushes it out of both walls every step, feeding energy into every piece it touches. That is why
debris boxes are 3.5% smaller than their meshes (`ScriptedDestruction.SLACK`) and a falling block is 1
cm narrower than its cell.

**Bodies made on the `PhysicsServer3D` outlive their node.** The voxel debris has no nodes, and a
battle shares the root viewport's `World3D` with the next one, so `VoxelDebris` takes its bodies out
of the world on `_exit_tree` and frees them (and its box shapes) on `NOTIFICATION_PREDELETE`. Anything
else made on the server must do the same.

**`get_collision_exceptions()` fails on bodies since freed.** The physics server keeps a freed body in
the exception list of every body that passed through it, and
`PhysicsBody3D.get_collision_exceptions()` errors on each (`Parameter "body" is null`) and returns
null in its place. That is why a `VoxelBody` keeps its own list (`passes`), never read from the
server: `ScriptedDestruction._pass_overlaps()`, which makes the pairs, hands each piece its list, and
a cut hands the part its model's.

**Jolt has hard limits.** 10,240 bodies by default, and contact and pair buffers that overflow with a
few thousand lumps settling at once ("contacts were ignored", lumps sinking into each other).
`project.godot` raises them, and `VoxelDebris.MOST` keeps the lumps' bodies well under the body limit;
lumps rather than single voxels (`DEBRIS_CLUMP`, `crumble_size`) keep the count down. Raising the
contact or pair limits much further needs a bigger `temporary_memory_buffer_size`.

## Its scripts

`CLAUDE.md`'s Layout lists every script in a line or two; here are `Terrain/`'s in full, but for
`VoxelShape` and `VoxelModel` (`Docs/VOXELS.md`) and `SceneryGround` (`Docs/LEVELS.md`).

```
  Terrain/
    TerrainDestruction.gd  breaks struck and blasted pieces (break_piece(), break_block()), drops what they held and
                           edge pieces and stacks left on nothing, drops stranded units, throws a
                           blast's debris about, tidies debris; block_broken(cell, destruction); make_piece() /
                           pieces_in() (pieces: PIECE_LAYER, the PIECES group, found by physics queries); hands a
                           breaking block's blood on to what it becomes (_break, _on_landed, _pieces_since());
                           break_figure() (a dying unit's figure into lumps, knocked by the killing blow:
                           FIGURE_*, _figure_knock()), _drop_gear() (its props whole, as pieces that wear)
    Destruction.gd         Resource base: how a kind of block comes apart, shatter(); prepare() (as a map loads);
                           mass; coin_chance; Motion
    ScriptedDestruction.gd pieces cut in advance, swapped in and left to fall or blasted apart; wear (then each piece
                           wears away as a loose model from the first time something reaches it)
    FallingBlock.gd        a block whose support broke, falling whole until it lands
    Blast.gd               a burst from a point: impulse by distance and the area a piece shows
    VoxelDestruction.gd    Destruction: a block that wears away a few voxels at a time (the second kind), or how a
                           ScriptedDestruction's pieces wear; collapse_below, voxels_per_damage, crater_per_damage /
                           crater_radius(), density, crumble_size
    VoxelTerrain.gd        made by TerrainDestruction: wears the level's volume: chip() (a round's bite), crater()
                           (a blast's), _drop_loose() (cut loose, across pieces), holds_up() (cut through),
                           take_piece() / crumble() / roughen_hole() (a piece breaking, its ragged rim),
                           is_solid_at(); loose models: take_on_later() (taken on at the first hit), take_on_body(),
                           tear() (rounds through them), _settle() (split off, crumble); lumps chosen before they are
                           made (Batch, _scatter()); carry_blood() (a crate's blood on to its pieces);
                           march() (a ray through a model's voxels)
    VoxelBody.gd           a loose model as a body (a crate's piece, dropped gear), a node under its RigidBody3D: its
                           VoxelModel, box collider and mass; passes (the bodies it passes through)
    VoxelDebris.gd         every voxel broken off: lumps as PhysicsServer bodies with no nodes, drawn by MultiMeshes;
                           add(), burst(), wake(), tidy(); at MOST bodies, stills those at rest furthest from focus
                           (the tile the camera looks at) down to KEEP, drawn but bodiless until disturbed;
                           stain(body, point) (a drop of blood colours the voxel it met)
```

## Known gaps

`CLAUDE.md`'s Known gaps keeps those a rule or a probe meets: crates breaking whole on any hit, a unit
floating over a crater, a worn block's full cover, what a seeded fight replays, and what an export
needs.

- Rounds fly straight through debris: the trace only sees the level's pieces, and the voxels of those
  that wear away. They tear the loose models they pass through, but are never stopped by one.
- Only a crate's pieces and the gear a dying figure drops wear away as loose models so far. A loose
  model must be a `RigidBody3D` drawn by a MagicaVoxel model in a `MeshInstance3D` among its children,
  and no more than 62 voxels along any axis (`VoxelShape.WIDEST`, and the mesher's rows); static
  props, units' figures and the gear they still carry cannot be worn, and a `FallingBlock` is not one
  until it lands.
- A loose model collides as the box round what is left of it, so a board shot into an L lies as its
  box, and a part cut off one passes through its whole family of parts for good.
- A bite costs about 2.5-4.5 ms on the frame it lands, and the collision of each chunk it wore 1.4 ms
  ahead of the next physics step; a grenade's crater about 21 ms, a whole blast up to about 40 among
  crates on raised ground (gathering and removing voxels, the search for what is cut loose, cutting
  lumps and meshing in GDScript), more for each piece it brings down; the blast's redraws spread over
  the next few frames.
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
