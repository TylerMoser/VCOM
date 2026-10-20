# Blood

Blood in full: `Scripts/Blood/`, and the parts of `VoxelModel`, `VoxelVolume`, `VoxelTerrain`,
`VoxelDebris` and `FigureVoxels` that recolour voxels and carry their colours on. It was split out of
`CLAUDE.md`, which keeps a summary and the rule that must not drift ("Blood is only for show"). How
every voxel model is drawn and recoloured, the texture blood writes into, is `Docs/VOXELS.md`'s. A section named here that is
not in this file (Gotchas, Verification, Known gaps, another subsystem's notes) is `CLAUDE.md`'s.

## How it works

**Blood recolours voxels, every voxel model's alike, and is only for show.** `Unit.take_damage()`
emits `hurt(taken, from, at, blasted, sweep)` for every hit that takes health (none for one defense
stops), before the unit can die of it. `Blood`, a node in each combat map after `Coins`, connects to
every unit as it readies and does the rest. Each figure has read its rig and its gear's `.vox` as it
readied, to be drawn from them (`Docs/VOXELS.md`; about 10 ms the first time for the base figure), so
the first hit does not catch on them.

**The player can play clean.** **Blood** on the pause menu's System tab, just under **Tile Grid**,
turns it all off: `Blood.enabled`, a static like `TileGrid.shown`, so it holds from battle to battle
until the game closes and is never saved. It only changes between battles, on the world map: while
`Campaign.in_mission` the menu greys the button out and shows a note under it saying so
(`SystemTab.show_blood_state()`, called as the menu opens, since the menu is made before `Campaign`
is), and each map's `Blood` reads `enabled` once, in `_ready`, so a battle keeps what it began with
and nothing has to be cleaned off or added mid-fight. Off, every figure still reads its rig, since
it is drawn from it and a shot still draws its tracer on to the body (`pick_wound()`), but `Blood`
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
  voxels wide and 2 deep and takes most of the stain. Over 40 wounds of 24 faces its red faces sat
  0.5 voxels below the wound on average and the lowest 2.8 below, against 0.0 and 2.0 with downhill
  costing no less (with stains on faces, 0.8 and 3.6 against 0.1 and 2.4: a voxel is red on every
  side now, its sides counting at its middle). In the standing pose the arms cover the chest, so many
  wounds land on a forearm, where blood cannot go lower without crossing the arm's underside. Every hit sprays `DROPS` and 8 more a point: a round's
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
- **Where blood lands, it runs** (`BloodFlow`): it reaches face after face, always the one cheapest
  to reach next (Dijkstra over voxel faces: across each edge of a face to the face beside it, up the
  wall rising there, or round on to the voxel's own side), and recolours the voxel of each it reaches,
  until it has stained its volume of faces: every face of the voxel open to the air turns red, and
  each costs one (`Surface.open_faces()`), so a unit of blood is a face of red on anything, the
  ground or a board's edge, as it was when blood stained faces one at a time. A flat step costs the
  same every way, roughened by smooth noise and a speckle, so a pool is a blob with lobes; downhill
  is cheap, so blood runs over an edge and down before it spreads far on top; sideways along a wall
  dear, so it streaks down; climbing dearer, so it barely climbs; undersides never, though a voxel it
  recolours shows red underneath if its underside is open. Within `splat` voxels of where it landed it
  spreads every way alike. A face whose voxel is red already costs little and no blood, so a drop
  landing in a pool runs out to its edge, looking at most `VISITS` + 3 a face. The level is one grid
  of voxels across every piece and chunk (`VolumeSurface`, over its `VoxelVolume`), so a pool crosses
  from block to block, and on to a fence or a wall; any other model is its own (`ModelSurface`, over
  its `VoxelModel`: a board, a prop), and so is a figure, standing as drawn with down taken from each
  voxel's bone (`FigureVoxels.FigureSurface`, a `ModelSurface` of its body).
- **The dead bleed out.** `died` hands `Blood` where the unit stood; `POOL_DELAY` (1 s) later, once
  the lumps its figure broke into have mostly landed, a flow of `DEATH_FACES` (800, about two tiles
  across on flat ground) starts on the ground under its feet, or below them if it died falling, and
  spreads over `DEATH_SECONDS` (3), quickly at first, under the heap.
- **A killing wound is stained at once.** A hit that kills (`taken` at least the unit's health as
  `hurt` goes out, before it is taken) stains its wounds there and then (`_wound(..., now)`), not
  queued with the landings, since the figure breaks apart a moment later in the same call and its
  lumps take their colours from its voxels (about 2 ms).
- **Landings wait their turn.** Wounds and landed drops are queued and settled oldest first for up to
  `SPLASH_BUDGET` microseconds a physics step, the rest the next: a stain a frame late is not seen.
  A landing on a voxel of the level worn or broken away while it waited is dropped (`_splash()` asks
  the volume first): the cover of someone hit leaning out of it often goes to the very next round.

**A stain is a voxel's colour, on everything.** Every voxel model is drawn by one shader from a
texture of its voxels' places in its palette, and place 255 of every palette is blood's
(`VoxelShape.BLOOD`, `BLOOD_COLOR`, flagged wet, so the shader draws it glossier). So a stain is a
write: on the level `VolumeSurface.stain()` is `VoxelVolume.recolor(voxel, BLOOD)`, and the chunk's
layer of the level's texture is uploaded once that frame (`LevelRenderer.refresh()`); on any other
model `ModelSurface.stain()` is `VoxelModel.recolor(index, BLOOD)`, which gives the model a texture of
its own the first time (its shape's is every such model's) and uploads it at the end of the frame.
Nothing is rebuilt, nothing more is drawn, and every open face of the voxel shows red. A spreading
pool under a body costs about 0.06 ms a frame in uploads (0.15 at worst), a figure's texture 4 KB.
The user chose texture writes on 2026-10-19 for the level, rather than more textures or overlay
meshes, and on 2026-10-20 asked for every voxel model to be recoloured so "instead of utilizing
overlays": figures, props and crate boards had faces stained by an overlay of red squares 2 mm proud
of them until then (`VoxelStains`, `FigureStains`; git has them).

**Nothing moves a stain on its own.** It is the colour of a voxel, and goes wherever the voxel goes:
whatever moves a model moves its colours (the scene tree for boards and gear, the skeleton for a
figure, whose mesh carries each corner's voxel so the shader colours it however it is posed). Only
when a model becomes others is its blood handed on, by these rules:

- **The level:** each voxel's colour in its `VoxelVolume`, every piece's alike, crates and decoration
  included. Worn off, a voxel's lump is its colour, blood red; a piece falling whole is drawn as a
  `VoxelModel` of the voxels it left, in the level's palette (`TerrainDestruction._drop_whole()`), and
  crumbles where it lands in them; a piece breaking crumbles in them. A crate's go to its pieces,
  which are models of their own: `VoxelTerrain.carry_blood()` finds the voxels it left blood red, as
  voxels of the crate's own model (turned back by the piece's turn), and recolours every voxel of
  each piece that sat in one, taking the piece on as a loose model first, only if its
  `ScriptedDestruction` has a `wear`. Pieces cut to overlap at a crate's corners both take a corner's
  blood.
- **Loose models:** their `VoxelBody.model`'s colours; a part cut off takes its voxels with theirs
  and shares its model's texture (`VoxelModel.split()`).
- **Figures:** `FigureVoxels.body`, a `VoxelModel` of the figure as drawn, standing (its rig's
  shape, read from the `.vox` the figure was baked from, `CharacterModel.voxel_model`, by its layout in
  `VoxelRig.LAYOUTS`, once a model), colouring its baked skinned mesh. As it breaks apart each voxel
  goes into its lump in its colour, blood red where blood reached it (`FigureVoxels.crumble()`).
- **Gear:** each prop's own `VoxelModel`, made as the figure makes the prop
  (`CharacterModel._make_prop()`), a node under its mesh. Dropped, the mesh goes into a body of its
  own with its model, and once it wears its `VoxelBody` takes that model, blood and all.
- **Lumps:** a voxel's `MultiMesh` colour (`VoxelDebris.stain()`), the whole voxel, as everywhere.

Decided with the user when blood was made, so not to be "fixed": blood is as exaggerated as Fat
Princess's, one bright red (`VoxelShape.BLOOD_COLOR`); a stain is per face, not per voxel (superseded
by the user: on the level on 2026-10-19, on every voxel model on 2026-10-20, blood recolours voxels;
it still spends a unit for each face it turns red, so a wound is as big as it was); only damage
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
through a pool) at the top of `BloodFlow.gd`; the colour in `VoxelShape.gd` (`BLOOD_COLOR`), the gloss
of a voxel it recolours in `Voxels.gdshader` (a wet place's roughness 0.55 and specular 0.35, softened
from 0.35 and 0.5 so the sun's glint on a pool no longer washed it white) and of a drop in flight in
`Blood._make_drops()`, the same; where wounds land and how wide they splash in `FigureVoxels.gd`
(`WOUND_WEIGHTS`, `WOUND_SPLAT`).

Adding things blood should stain:

- **A kind of piece** needs nothing: every piece of the level is in its volume, breakable or not,
  decoration too, so drops meet its voxels and pools run across it on to its neighbours. One that
  wears away colours its lumps and falls with its blood. One that breaks into cut pieces hands its blood to them only if its `ScriptedDestruction` has
  a `wear`; without one, its blood goes as it breaks, and drops pass its pieces.
- **A new kind of destruction** (a `Destruction` subclass) has to hand a breaking block's blood on
  itself: `TerrainDestruction._break()` and `_on_landed()` only know a block that wears away (crumbled
  in its colours) or one that breaks at once into rigid pieces that wear (`carry_blood()`). Passing
  what the block left (`VoxelTerrain.Taken`, its voxels' places) into `shatter()`, so each kind
  decides where its blood goes as it does its pieces, would be the clean way.
- **A destructible thing that is not a piece of the level** (a prop placed as a scene) is recoloured
  as any voxel model is (`Docs/VOXELS.md`, "Adding a voxel model": `VoxelModel.take_over()`, and
  `BloodFlow.ModelSurface` over it), but `Blood` has to find it: `_first_met()` and `_splash()` know
  the level, figures and their gear, debris taken on as loose models, and lumps. As debris, a
  `RigidBody3D` on the debris layer taken on with `VoxelTerrain.take_on_body()`, it needs nothing
  more; anything else, a branch in `_first_met()`.
- **A material that should take blood differently** (water, glass, sand) has nowhere to say so: every
  surface takes it alike, and only breakable blocks have a resource to put a setting on.
- **A turned piece** is stamped turned, so its blood is its voxels' like anything else's; only a
  turned crate's hand-off turns voxels back to its model (`carry_blood()`), and no map has one yet, so
  probe the first.

Headless on BoundaryMap a hit costs 0.2-0.4 ms; a shot's 50-odd drops about 1-2 ms a physics step in
flight; landing them is held to the 2 ms budget, and a wound's flow on a figure (24 faces) takes
about 1 ms of it; the level's colours upload in under 0.2 ms a frame, and a model's whole texture, a
few kilobytes at most, at the end of the frame it changed in. A death with blood costs about 4.2 ms on
its frame. Before the rig was read at load and the gear cached a frame, the first hit took 10 ms and a
frame of drops near a figure up to 9.

## Probing it

Blood is probed headless, as debris is (`CLAUDE.md`'s Verification).
`unit.take_damage(5, from, false, unit.model.pick_wound(from))` stands
in for a round's hit, with `from` the muzzle; `blood.drops_in_flight()` counts drops still flying or
landed but not yet settled, and `blood.pools_to_come()` the dead yet to bleed out. Count the level's
stained voxels with `chunk.colors.count(VoxelVolume.BLOOD)` over `level.volume.chunks` (or ask
`volume.color_at(voxel)`), and a model's with `model.voxels.count(VoxelModel.BLOOD)`: a figure's body
is `unit.model.voxels().body`, its props `unit.model.gear()`, a loose model `voxels._loose[body].model`;
drop blood anywhere with `BloodFlow.new(blood._terrain, hit.voxel, BloodFlow.FACES.find(hit.face),
faces, rng).spread(faces)` on a hit from `grid.cast(origin, direction, distance, true, true)`. Lumps' colours can only be checked
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
  whose splash covers the whole figure, so every step costs the same, each on a fresh body
  (`figure.body = VoxelModel.new(figure.rig.shape)`, shown on the figure's `Body` with its mesh); compare
  how far below the wound the red voxels' open faces sit (the numbers under "The figure bleeds and
  sprays" above), and how many there are to the wound's faces: about 1.02 a face.
- **Coins stay clean.** `blood._spray()` drops straight at a coin: they should land beyond it, and
  its `MeshInstance3D` should get no `VoxelModel` child.

## Known gaps

- Blood never dries, fades or soaks in: every stain stays bright red for the battle, and every battle
  starts clean; nothing is kept on the character. Figures do not leave trails or drip, and blood on a
  figure stays on it rather than dripping on to the ground.
- The Blood on / off choice is not saved: every launch starts with blood on, as every launch starts
  with the tile grid off. It cannot be changed in a battle, so a battle opened on its own (F6, the
  harness) always has blood unless a probe sets `Blood.enabled` before the map loads.
- Drops pass through what has no voxels to them or no body: stilled lumps, pieces that do not wear,
  blocks falling whole, and the scenery beyond the battlefield (lost below the map). Everything is
  stained a whole voxel at a time, every face of it, an open underside too.
- A crate whose `ScriptedDestruction` has no `wear` loses its blood as it breaks: only pieces taken on
  as loose models can carry it.
- Blood runs over one surface at a time: from a figure's wound it never runs on to its gear or the
  ground, and a small drop stains so few voxels that it is mostly a cross or a bar.
- The move range's tile highlights draw over blood, which shows pink through their fill, and blood in
  shade takes the sky's blue light, so it looks a dark purple-red there.
- Blood on the grenades on a belt goes when any grenade is used up: `equip()` builds them all afresh.
- Every model blood has reached has a texture and a material of its own (`Docs/VOXELS.md`), a draw
  call each as any model is: fine for the few dozen a battle makes. See "Adding things blood should
  stain" for what a new kind of breakable, a destructible outside the grid, or a material that sheds
  blood would need.
