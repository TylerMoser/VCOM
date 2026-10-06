# Blood

Blood in full: `Scripts/Blood/`, `VoxelStains`, and the parts of `VoxelTerrain`, `VoxelBody`,
`VoxelDebris` and `FigureVoxels` that carry stains. It was split out of `CLAUDE.md`, which keeps a
summary and the rule that must not drift ("Blood is only for show"). A section named here that is
not in this file (Gotchas, Verification, Known gaps, another subsystem's notes) is `CLAUDE.md`'s.

## How it works

**Blood is painted on voxel faces, and only for show.** `Unit.take_damage()` emits
`hurt(taken, from, at, blasted, sweep)` for every hit that takes health (none for one defense stops),
before the unit can die of it. `Blood`, a node in each combat map after `Coins`, connects to every
unit as it readies and does the rest; it reads each figure's rig as the map loads (about 10 ms for
the base figure, and its gear's `.vox`), not on the first hit.

**The player can play clean.** **Blood** on the pause menu's System tab, just under **Tile Grid**,
turns it all off: `Blood.enabled`, a static like `TileGrid.shown`, so it holds from battle to battle
until the game closes and is never saved. It only changes between battles, on the world map: while
`Campaign.in_mission` the menu greys the button out and shows a note under it saying so
(`SystemTab.show_blood_state()`, called as the menu opens, since the menu is made before `Campaign`
is), and each map's `Blood` reads `enabled` once, in `_ready`, so a battle keeps what it began with
and nothing has to be cleaned off or added mid-fight. Off, `Blood` still reads every figure's rig as
the map loads, since a shot still draws its tracer on to the body (`pick_wound()`), then stops: it
connects to no unit and never processes, so no wound, drop, stain or pool is made, and no lump turns
red. The lock is the menu's alone: `Blood` must not name `Campaign`, or no probe could name `Blood`
(see Gotchas).

- **A hit is drawn landing on the body, not at the eye.** The round still flies eye to eye
  (`Ballistics`), but as it is fired `Unit.shoot_at()` asks the target's figure where it is seen to
  land: `CharacterModel.pick_wound()` picks a voxel by bone, mostly the torso
  (`FigureVoxels.WOUND_WEIGHTS`), and traces from the muzzle to it, so the point is the first voxel
  facing the gun. It goes in `Ballistics.Path.wound`, which `ShotOverlay` draws the tracer to
  (`Path.drawn_to()`), as the muzzle moved its start, and `take_damage()` passes it on as `at`. A
  strike picks one from the striker's chest (`Unit.STRIKE_HEIGHT`) and passes its figure's `swing()`
  as `sweep`; a blast passes neither, and `Blood` picks two to four wounds facing it. On landing
  `FigureVoxels.hit_near()` finds the spot on the figure as it stands then.
- **The figure bleeds and sprays.** A wound stains `WOUND_FACES` and 4 more a point of damage (counting
  at most `MOST_DAMAGE`) round where it landed. It leans a little downward rather than running down:
  the even splash round a wound (`FigureVoxels.WOUND_SPLAT`, 2 voxels) wraps round a torso only 5
  voxels wide and 2 deep and takes most of the stain. Over 40 wounds its middle sat 0.8 voxels below
  the wound and its lowest face 3.6 below, against 0.1 and 2.4 with downhill costing no less. In the
  standing pose the arms cover the chest, so many wounds land on a forearm, where blood cannot go
  lower without crossing the arm's underside. Every hit sprays `DROPS` and 8 more a point: a round's
  mostly out of an exit wound, found by tracing back through the figure along the round's flight
  (`FigureVoxels.exit()`), which bleeds too, and the rest back toward the gun; a blade's along its
  swing; a blast's away from it. A drop leaving a figure passes through it for `CLEAR_SECONDS`.
- **A drop is a voxel under gravity**, a cube one or two voxels across in one MultiMesh, stepped every
  physics frame and traced along its step: through the terrain voxel by voxel, every `.vox` block,
  crates' slats and gaps too (`CombatGrid.cast()`'s `every_block`, which only blood uses); against
  every living unit's figure whose ball it passes near (`FigureVoxels.march()`: each bone's voxels are
  a part in its bone's posed frame, culled by a sphere, and so is the gear in its sockets); and against
  debris, by a physics ray on the debris layer (a lump by its RID, a dead figure's among them; a piece
  that wears away, dropped gear among them, taken on and traced through its voxels; falling blocks
  passed). It
  lands on the first it meets, and is forgotten once below the map. **Coins are the one exception:**
  blood never looks for them, so a drop flies straight through a coin to whatever is behind it, and
  no coin is ever stained. Keep it so.
- **Where blood lands, it runs** (`BloodFlow`): it stains up to its volume of faces, always the one
  cheapest to reach next (Dijkstra over voxel faces: across each edge of a face to the face beside
  it, up the wall rising there, or round on to the voxel's own side). A flat step costs the same every
  way, roughened by smooth noise and a speckle, so a pool is a blob with lobes; downhill is cheap, so
  blood runs over an edge and down before it spreads far on top; sideways along a wall dear, so it
  streaks down; climbing dearer, so it barely climbs; undersides never. Within `splat` voxels of
  where it landed it spreads every way alike. Faces already stained cost little and no blood, so a
  drop landing in a pool runs out to its edge, looking at most `VISITS` + 3 a face. The terrain is one
  grid of voxels across every block (`TerrainSurface`), so a pool crosses from block to block; a
  loose model or prop is its own (`ModelSurface`), and so is a figure, standing as drawn with
  down taken from each voxel's bone (`FigureVoxels.FigureSurface`).
- **The dead bleed out.** `died` hands `Blood` where the unit stood; `POOL_DELAY` (1 s) later, once
  the lumps its figure broke into have mostly landed, a flow of `DEATH_FACES` (800, about two tiles
  across on flat ground) starts on the ground under its feet, or below them if it died falling, and
  spreads over `DEATH_SECONDS` (3), quickly at first, under the heap.
- **A killing wound is stained at once.** A hit that kills (`taken` at least the unit's health as
  `hurt` goes out, before it is taken) stains its wounds there and then (`_wound(..., now)`), not
  queued with the landings, since the figure breaks apart a moment later in the same call and its
  lumps take their colour from its stains (about 2 ms).
- **Landings wait their turn.** Wounds and landed drops are queued and settled oldest first for up to
  `SPLASH_BUDGET` microseconds a physics step, the rest the next: a stain a frame late is not seen.
  A landing whose block has broken or fallen while it waited is dropped (`_splash()` asks
  `kind_of()` first): the cover of someone hit leaning out of it often goes to the very next round.

A stain is a face, never a voxel's colour: `VoxelStains` keeps each stained voxel's faces as six bits
(+x, -x, +y, -y, +z, -z), by its place in its model's array, and draws them by an overlay, a
`MeshInstance3D` of red squares `PROUD` (2 mm) off each face along its normal, rebuilt once at the end
of the frame (`changed()`), so blood never rebuilds a block or a figure. A face shows only while its
voxel is there (each rebuild reads the model's voxels as they are now), and is only stained while open
to the air (voxels are never added, so it stays open).

Overlays rather than recolouring the models, because rebuilding a block's own mesh
(`VoxelMesher.surface()`) costs 1.5 ms for grass, 2 for a tree and 3.3 for a crate, and a burst of
drops lands on dozens of blocks at once, where a stained cell's overlay rebuilds in about 0.1-0.3 ms;
and the GridMap goes on drawing the block, so staining one needs no stand-in.

Nothing moves a stain on its own. It is recorded by which voxel of which model it is on, and its
overlay is built in that model's own space and hangs from whatever draws the model, so whatever moves
the model moves its stains: the scene tree for blocks, boards and gear, the skeleton for a figure. Only
when a model becomes others (a block falling whole, a crate's pieces, a board cut in two, a voxel
broken off) is a stain handed on, by these rules. Where they live:

- **Blocks:** `VoxelTerrain`, by cell, for every block drawn from a `.vox` (`kind_of()`, crates
  included, which do not wear), the overlay under `VoxelTerrain` in the cell's frame. Wear hands the
  cell's stains to its debris, so a stained voxel's lump is blood red (`VoxelTerrain._make()`), and
  redraws the overlay. A breaking block's stains go with it (`take_stains()`): a worn block crumbling
  colours its lumps, a block falling whole carries its overlay under the `FallingBlock` and hands the
  stains on as it lands, and a crate's go to its pieces (`carry_stains()`: each piece holding a
  stained voxel is taken on as a loose model and stained where the crate was, its faces turned to the
  piece's frame), only if its `ScriptedDestruction` has a `wear`.
- **Loose models:** `VoxelBody.stains` (`stained()`), the overlay under its mesh; a part cut off takes
  a copy (`carry_stains()`).
- **Figures:** `FigureVoxels.stains`, over the figure as drawn, drawn by a mesh skinned to its skeleton
  with the body's `Skin`, each square weighted to its voxel's bone (`FigureStains`), so it moves with
  every pose. The rig is read from the `.vox` the figure was baked from (`CharacterModel.voxel_model`, a
  layout from `VoxelRig.LAYOUTS`), once a model. As the figure breaks apart, a voxel with any face
  stained goes into its lump blood red (`FigureVoxels.crumble()`).
- **Gear:** `VoxelStains.on(mesh_instance)`, kept in its metadata, the overlay under it. Props are
  imported at 0.063 a voxel, so `scale` grows the shape's frame to the mesh's. Dropped, the mesh takes
  its overlay into its body, and once it is worn its `VoxelBody` adopts the stains
  (`adopt_stains()`), reading what is left of it.
- **Lumps:** a voxel's MultiMesh colour (`VoxelDebris.stain()`), the whole voxel rather than a face.

Decided with the user when blood was made, so not to be "fixed": blood is as exaggerated as Fat
Princess's, one bright red (`VoxelStains.COLOR`); a stain is per face, not per voxel; only damage
actually taken bleeds, more with more damage; where blood lands it runs, rather than splatting round;
a hit's wound is anywhere on the body facing the shooter, mostly the torso, with the tracer drawn to
it, rather than always at the head, where the round flies; the pool under a body is about two tiles
across, spreading over three seconds once it rests (since the dead break apart, from a second after
death, where the unit stood); stains last the battle and nothing carries over to
the roster; the enemies went from red to slate grey (bone and khaki were too near the white and yellow
squad members, and charcoal read navy, with blood dark in its shade). Two came later: a wound on a
figure leans a little downward rather than running, and is kept so (a smaller splash with drip trails
that creep down and drip off the body was offered and turned down); and coins never take blood.

To tune it: how much a hit bleeds, how its blood flies, and the pool under a body are the constants at
the top of `Blood.gd`; how blood spreads (the cost of each step, the noise, how far a drop looks
through a pool) at the top of `BloodFlow.gd`; the colour and gloss in `VoxelStains.gd` (`COLOR`; the
material's roughness 0.55 and specular 0.35, softened from 0.35 and 0.5 so the sun's glint on a pool no
longer washed it white); where wounds land and how wide they splash in `FigureVoxels.gd`
(`WOUND_WEIGHTS`, `WOUND_SPLAT`).

Adding things blood should stain:

- **A block** needs nothing more than destruction asks: drawn from a `.vox` at 0.0625, one block a
  cell. Every such block is read as the map loads, breakable or not, so drops meet its voxels and
  pools run across it on to its neighbours. One that wears away colours its lumps and falls with its
  blood. One that breaks into cut pieces hands its blood to them only if its `ScriptedDestruction` has
  a `wear`; without one, its blood goes as it breaks, and drops pass its pieces.
- **A new kind of destruction** (a `Destruction` subclass) has to hand a breaking block's stains on
  itself: `TerrainDestruction._break()` and `_on_landed()` only know a block that wears away (crumbled
  with its stains) or one that breaks at once into rigid pieces that wear (`carry_stains()`). Passing
  the stains into `shatter()`, so each kind decides where its blood goes as it does its pieces, would
  be the clean way.
- **A destructible thing that is not a grid cell** (a prop placed as a scene) needs `Blood` to find
  it: `_first_met()` and `_splash()` know blocks, figures and their gear, pieces that wear, and lumps,
  a branch each. A common interface for anything stainable (trace a ray against its voxels, give a
  surface to run over), found by a group, would let new kinds plug in; it would come with destruction
  outside the grid, which does not exist yet either.
- **A material that should take blood differently** (water, glass, sand) has nowhere to say so: every
  surface takes it alike, and only breakable blocks have a resource to put a setting on.
- **A turned block** (a GridMap orientation) should work, `TerrainSurface` and `carry_stains()`
  turning voxels and faces, but no map has one yet, so probe the first.

Headless on BoundaryMap a hit costs 0.2-0.4 ms; a shot's 50-odd drops about 1-2 ms a physics step in
flight; landing them is held to the 2 ms budget; overlays redraw in up to about 1 ms a frame, 2 ms
while a pool under a body spreads. Before the rig was read at load and the gear cached a frame, the
first hit took 10 ms and a frame of drops near a figure up to 9.

## Probing it

Blood is probed headless, as debris is (`CLAUDE.md`'s Verification).
`unit.take_damage(5, from, false, unit.model.pick_wound(from))` stands
in for a round's hit, with `from` the muzzle; `blood.drops_in_flight()` counts drops still flying or
landed but not yet settled, and `blood.pools_to_come()` the dead yet to bleed out. Count stained faces
over `VoxelStains.faces` (`voxels.stains_at(cell)`, a model's `stains`, a figure's
`model.voxels().stains`), and drop blood anywhere with `BloodFlow.new(blood._terrain,
blood._terrain.voxel_of(hit.cell, hit.index), VoxelStains.FACES.find(hit.face), faces, rng).spread(faces)`
on a hit from `grid.cast(origin, direction, distance, true, true)`. Lumps' colours can only be checked
in a window (see Gotchas). Hide `HUD` and `TileHighlights` to look at blood: the move range's squares
draw over it. To look at a figure's wounds, turn it to the camera (`model.face()`) and paint it a
colour blood shows on; the shot itself is best driven through `Unit.shoot_at()` with a shot from
`LineOfSight.new(grid).find_shot()`, which plays the tracer to the wound.

Three checks blood was made with, worth repeating after changing it:

- **It draws nothing from the global generator.** Seed, fire the same volley through
  `Unit.shoot_at()` on a map with its `Blood` node and on one with it freed before the map enters the
  tree, and compare the outcomes and the next `randi()`: they matched.
- **How much a wound leans.** Flow the same wounds with `figure.bleed()` and with
  `BloodFlow.new(FigureVoxels.FigureSurface.new(figure), hit.voxel, hit.face, faces, rng, 1000.0)`,
  whose splash covers the whole figure, so every step costs the same; compare how far below the wound
  each stain's faces sit (the numbers under "The figure bleeds and sprays" above).
- **Coins stay clean.** `blood._spray()` drops straight at a coin: they should land beyond it, and
  its `MeshInstance3D` should get no `stains` metadata and no `Stains` child.

## Known gaps

- Blood never dries, fades or soaks in: every stain stays bright red for the battle, and every battle
  starts clean; nothing is kept on the character. Figures do not leave trails or drip, and blood on a
  figure stays on it rather than dripping on to the ground.
- The Blood on / off choice is not saved: every launch starts with blood on, as every launch starts
  with the tile grid off. It cannot be changed in a battle, so a battle opened on its own (F6, the
  harness) always has blood unless a probe sets `Blood.enabled` before the map loads.
- Drops pass through what has no voxels to them or no body: stilled lumps, pieces that do not wear,
  blocks falling whole, and the scenery beyond the battlefield (lost below the map). A lump is stained
  a whole voxel at a time.
- A crate whose `ScriptedDestruction` has no `wear` loses its blood as it breaks: only pieces taken on
  as loose models can carry stains.
- Blood runs over one surface at a time: from a figure's wound it never runs on to its gear or the
  ground, and a small drop stains so few faces that it is mostly a cross or a bar.
- The move range's tile highlights draw over blood, which shows pink through their fill, and blood in
  shade takes the sky's blue light, so it looks a dark purple-red there.
- A blast's worn blocks are redrawn over the next frames, but their stains' overlays at the end of the
  blast's own, so for a frame or two, under the fireball, a voxel about to go shows without its stain.
- Blood on the grenades on a belt goes when any grenade is used up: `equip()` builds them all afresh.
- Every block in the map's library drawn from a `.vox` is read as the map loads, used on the map or
  not, and every stained cell is an overlay and a draw call of its own. Fine for four kinds and a few
  hundred stained cells; with dozens of kinds, read only those the map uses, and with thousands of
  stained cells, gather the overlays by area. See "Adding things blood should stain" for what a new
  kind of breakable, a destructible outside the grid, or a material that sheds blood would need.
