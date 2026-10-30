# Glass

Glass and windows in full: how a voxel is glass, how glass is meshed and drawn, how blood stains it,
what a window is to the rules, how a pane shatters and what its shards do, the window piece, the
importer's part, what it costs, how to probe it, its gaps and what was decided without asking. It
was written as glass came in (2026-10-27); `CLAUDE.md` keeps a summary ("Glass is a colour
MagicaVoxel draws as glass...") and the rules that must not drift. `Docs/VOXELS.md` has the rest of
how every voxel model is drawn, `Docs/LEVELS.md` the rest of what a level is to the rules, and
`Docs/DESTRUCTION.md` the rest of breaking and wear. A section named here that is not in this file
(Gotchas, Verification, Known gaps, another subsystem's notes) is `CLAUDE.md`'s.

## What the user decided

The user asked (2026-10-27) for "nicer and larger buildings for combat maps. This includes windows in
buildings", and to research the options for glass, "especially adding glass to voxel models". The
research (MagicaVoxel's own Glass material read as a flag, glass meshed apart and drawn as a tint over
what is behind it plus a pass of reflections; nine ways of drawing it rendered on TestMap and
compared) ended in six questions, and the user answered "Go with your recommendations for all 6
decisions. Implement the glass functionality completely":

1. **Units see and shoot through windows**: the one exception to the rule that a piece on an edge
   blocks a sight line crossing it.
2. **Cover at a window is low, from the sill only**: the window gives none, and the piece under it,
   a cell high, gives half.
3. **Units vault through windows, breaking the glass**, as XCOM 2's do.
4. **Grenades are thrown through windows.**
5. **Glass is for show only**: a window is the same to the rules whole or broken, and whole glass
   stops nothing.
6. **The look is a tint multiplied over what is behind, with reflections**, rather than neutral grey
   glass or an opaque gloss.

And as the work began:

- **"Relax every vault"**: a vault over a piece a cell high needs only the level just above it open
  across that edge, nothing higher, so a unit vaults through a window with wall over it (its lintel)
  into a room as low as itself; every vault follows the new rule, not only a window's. (Checked
  first: no step changed on any of the four maps.)
- **Shards "stay for good"**: they lie where they land for the rest of the battle, as lumps of debris
  do, and fall again if the floor under them goes.
- **"TestMap + harness"**: windows in TestMap's house, and a lane of windows in `LineOfSightTest` for
  the probes.

XCOM 2, read in its scripts and settings, gave the rest of the shape: a window breaks from any damage,
vaulting through one breaks it, a grenade breaks glass within three tiles, and sight passes through
one.

## How it works

### A voxel of glass

**Glass is a colour MagicaVoxel draws as glass.** Paint it with a palette entry whose material is
Glass. `VoxelShape._paint(vox)` reads each entry's material from the importer's reader
(`vox.materials`: the material of palette place p is at p - 1) and gives a glass entry's place the
flag `VoxelShape.FLAG_GLASS` (4), with its clarity, how much of the light it lets through, in the top
five bits of the same byte: MagicaVoxel's Transparency (`_trans`), in 31 steps (`glass_flags()`,
`clarity_of()`). A glowing colour keeps its glow in those same five bits (`Docs/LIGHTS.md`): a colour
has one material in MagicaVoxel, so it is glass or glowing, never both, and a glow reads 0 on glass.
Its colour is its tint: white is clear glass, a colour is stained glass. The rest of
the material (roughness, refraction, density) is read by the importer (below) and not by the game.
The flags are the fourth number of every palette entry the voxel shaders read: 1 draws the tile grid
over it, 2 makes it wet (blood's), 4 makes it glass. `find_glass()`, run as every shape is read (a
block, a mesh, a model of a scene, and a figure's rig in `VoxelRig.make_shape()`), marks each voxel
holding a glass colour in `VoxelShape.glass` (a byte a voxel) and `glass_rows` (rows of bits laid out
as `rows`); a shape with none leaves both empty, and everything below passes it by.

**A voxel stays glass whatever colour it is given.** Which voxels are glass is kept apart from their
colours: a model's `VoxelModel.glass_rows`, and in the level each chunk's `glass_x` / `glass_z`
(`VoxelVolume.Chunk`, made the first time a chunk has glass, `make_glass()`), stamped with the piece's
voxels (`_place_glass()`: where a later piece puts a voxel, it is glass if that piece's is, whatever
was there) and taken away with them. So recolouring a voxel never changes whether it is glass, and
blood on glass is drawn on the glass (below). The level's palette keys a place on its colour and its
flags together (`VoxelVolume._map()` takes the shape's flags in), so a glass colour and an opaque one
of the same RGB get places of their own. `VoxelVolume.is_glass(voxel)` says whether a voxel is glass,
`is_opaque()` whether one is there and not glass, `glass_of(piece)` where a piece's glass is,
`pieces_with_glass()` which pieces have any; `glass_whole` and `glass_counts` count each piece's
glass, as `whole` and `counts` its voxels.

### Meshed apart

**A face of anything else shows through glass; a face of glass shows only against nothing.**
`ChunkMesher.faces()` finds a cube's faces in sets, `[the rest's, the glass's, ...]` (a third, for
the voxels that cast no lamp's shadow, came with lamps: `Docs/LIGHTS.md`). The rest's are
the faces of every voxel that is not glass with nothing but glass, or nothing at all, against them, in
the cube or beside it: glass is air to them (`Near`'s `*_glass` rows say which of each neighbour's
voxels are glass). The glass's are the faces of every glass voxel with nothing at all against them,
glass or not (`glass_rectangles()`). So the wall behind a pane, the frame round it and a figure's
head behind a visor all show through it, two panes side by side make one sheet, and a pane in its
frame shows only its two broad faces. A cube with no glass is meshed by `rectangles()` exactly as
before (the same faces on every map: Probing it).

**Every drawer makes the glass a second surface of its mesh**, the last, named
`VoxelModel.GLASS_SURFACE` (`"glass"`), with a material of its own: the level a section at a time
(`LevelRenderer._section_mesh()`, its `glass_material`), the scenery a kind at a time
(`SceneryRenderer`), and each `VoxelModel` (a prop, a crate's board, a block falling whole, a part cut
off: `_mesh_of()`, through `faces_of()`), which gives its `MeshInstance3D` a material for each surface
when its mesh has a glass one (`_apply_materials()`) and its `material_override`, as before, when it
has none. A figure's glass is a second surface of its baked mesh (`VoxelRig.make_mesh()`, each bone
meshed on its own as ever), so a figure with a visor needs only the bake. The level's collision is
built of both surfaces' faces (`LevelRenderer._collide()`): debris bounces off a whole pane, and goes
through once it has shattered and its chunk is drawn again.

### Drawn in two passes

**What is behind is multiplied by the glass's colour, then its shine is added on top** (the user's
look, 6). `VoxelGlass.gdshader` (`blend_mul`, unshaded) multiplies whatever has been drawn behind the
pane by its colour times its clarity. `VoxelGlassShine.gdshader`, its `next_pass` (`blend_add`, lit
as `Voxels.gdshader` lights a voxel), adds the sky's and the sun's reflection off smooth glass
(roughness 0.04, brighter at a glancing angle) and the share of its own colour it does not let
through, one less its clarity, lit. At clarity 1 a pane is all tint and reflection; lower, it is
cloudier; at 0 the first pass blacks out what is behind and the second draws the voxel lit, as
opaque as any other. Both find each pixel's voxel and palette entry exactly as `Voxels.gdshader`
does: the uniforms, the vertex function and the lookups are in `Voxels.gdshaderinc`, which all three
include (`Voxels.gdshader` was rewritten on it; it draws the same, the maps' renders within noise).

Why so:

- **Panes never sort wrong.** Godot sorts see-through surfaces by object, not by triangle, and a
  section of the level holds all the glass of 64 cells in one surface. A multiply gives the same
  whatever order panes are drawn in, and so does an add; the shine's material has a
  `render_priority` of 1 (`VoxelModel.SHINE_PRIORITY`) over the tint's 0, so every pane's tint is laid
  down before any shine is added. Glass seen through glass is right from any side.
- **Sunlight falls through.** In Godot a see-through surface writes no depth and casts no shadow, so
  the sun lights a room through its windows (squares of light on the floor) and SSAO and SSIL shade
  the room behind a pane, not the pane. The light comes through untinted: a stained pane casts no
  coloured light. So does a lamp's: a lantern glazed with glass lets its bulb's light out, and a lamp
  outside lights a room through its windows (`Docs/LIGHTS.md`).
- **Not plain alpha blending:** a pale colour lit by the sun washed out to a haze, and a figure behind
  it all but vanished (the research's renders). Not `PREMUL_ALPHA_FACTOR`: in 4.7 it scales the whole
  fragment, its specular too, and its tint can only be grey. Not refraction: it costs a copy of the
  screen, shows no glass behind glass and pulled in pixels from round the pane, all for panes a few
  pixels wide at the game's zoom.

### Blood on glass

**A drop stains glass as it stains anything** (blood's trace passes `every_block`, which meets
glass: `CombatGrid.cast()`), recolouring the voxel to blood's place, 255. The voxel stays glass, so
the glass shaders draw it, but blood's flags are wet with no clarity: it is drawn opaque, wet and red,
a smear on the pane. Its shard, when the pane shatters, is red and opaque too. A glass voxel given
any other colour is drawn at that colour's clarity.

### What a window is to the rules

**A window is decoration to the fight wherever it stands, as a piece on a corner is**
(`PieceKind.window`, ticked on `SimpleWindow1`). `LevelRules` keeps windows in a table of their own
(`_windows`; `is_window()`, `window_slots()`), which `is_solid()`, `has_edge()`, `pieces_in()` and
`pieces_across()`, what the fight asks, never read; `pieces_at()` and `has_slot()`, what holds pieces
up and breaks them asks, read them as any piece. So:

- **Sight and shots pass through it** (decision 1). `is_line_clear()` and every whole `cast()` pass a
  window: a target behind one is seen and shot, sight running both ways as ever, and a walker seen
  through one opens a reaction window.
- **It is no cover** (2). `LineOfSight.cover_at()` reads edges, and the window is none; the piece
  under it is, `SimpleWall1`, a cell high: half cover to both sides, as a fence is. A window standing
  on the ground (the harness's glass door) is no cover at all, and nobody leans out round one.
- **Throws pass through it** (4). An arc is cast whole, so it passes a window and is stopped by the
  wall round it as by any wall: a throw through a window under a lintel clears only where the arc
  crosses at the window's height, coming down steeply from across a room.
- **Clicks pass through it**: `pick_tile()` lands on the tile beyond.
- **A round traced voxel by voxel meets its frame and never its glass** (`CombatGrid._trace_cell()`
  passes a glass voxel unless `every_block`): a miss can strike the frame, the mullion or the sill and
  bite them, a window wearing away as a wall does, or fly on through a pane. A miss is never aimed at
  a window (`Ballistics._cover_faces()` reads edges), only at its sill. Blood's trace meets glass.
- **It stands, holds up and breaks as any piece does.** It stands on what is under it and holds up
  the course of wall resting on it (`TerrainDestruction._unsupported()` asks `has_slot()`), breaks in a
  blast with a side of it in the blast's cells, and wears away, falling when worn past standing and
  bringing down what it held.
- **Nothing reads its glass.** Whole or shattered, the rules see a window the same (5), and its going
  changes no step (`CombatGrid._on_piece_removed()` passes a window, as a corner).

A piece with glass that is not a window, a block of glass, is whole to the rules like any other: it
blocks sight, throws and steps and gives cover. Only a round, traced voxel by voxel, passes its glass.

### Vaulting through

**A vault needs only the level above the low piece open** (the user's "Relax every vault").
`CombatGrid._crossing()` gives the level a step crosses an edge at and the highest level it fills, as
`Vector2i(level, highest)`: a plain step crosses at the higher of the two tiles and fills that level
and the next (`UNIT_HEIGHT`); a vault, over a piece a cell high across the edge at that level, climbs
no more than `MAX_CLIMB`, crosses a level higher and fills only that level, which must be open across
the edge; `_is_clear()` then asks both columns to be open up to the highest level. Before, a vault
needed that level and the one over it open (`_crossing_top()`, renamed), so the wall over a window, or
a room as low as a unit, stopped it. Every vault reads the new rule. A window's sill is such a piece,
and the window over it is no edge, so a unit vaults through, the figure hopping it as it hops a fence
(`vaults_along()`), and the glass shatters as it passes (below). A window on the ground, a glass door,
is walked through.

### Shattering

**A pane shatters whole: all of a piece's glass at once.** `VoxelTerrain.shatter(pieces, motion)`
takes every voxel of glass the pieces have left out of the level (`glass_of()`, `remove_many()`),
breaks them into shards (`_burst_glass()` -> `GlassShards.burst()`) and draws the level again, at once,
or over the next frames for a blast (`now` false), as its craters are. It is only for show: nothing
the rules see changes, and none of it draws on the global generator. What shatters glass:

- **A round's flight, hit or miss** (`CombatGrid.fly()` -> `round_flown` ->
  `TerrainDestruction._on_round_flown()` -> `shatter_along(from, to)`): every window whose slot the
  line crosses at the window's own level (`_crosses_slot()`: the face between an edge's two cells, a
  level high, or into a middle's cell), through its frame or its glass, and every other piece whose
  glass voxels it goes through (`_meets_glass()`, voxel by voxel). Its shards fly on along the round
  at `SHARD_ROUND_SPEED` (2.5 cells a second, and half a cell up). A hit flies eye to eye, through a
  window like any line.
- **A grenade's flight**: every `ThrownGrenade` is in `ThrownGrenade.GROUP`, and
  `TerrainDestruction._shatter_passing()` traces each, every frame, from where it was to where it is
  (`shatter_along()`).
- **A unit passing a window** (3): every frame, for every unit whose tile changed,
  `shatter_passing(from, to)` shatters every window across the edge between the two tiles' columns
  (all four round the corner, for a diagonal step), from the lower tile's level up to a level over
  the higher one's head, and any in the cells it walks into. So a vault shatters the window as the
  unit crosses, whatever moved it (a move, an enemy's walk, a fall); its shards fly on the way it
  went at `SHARD_PASS_SPEED` (1.5).
- **A blast**: every pane within `VoxelTerrain.GLASS_BLAST_REACH` (3) cells of where it goes off,
  measured to the piece's cell, whatever stands between (XCOM 2's three tiles: `shatter_near()`, from
  `TerrainDestruction._on_terrain_blasted()`), its shards thrown out from the blast as a
  crater's lumps are. A window with a side in the blast's cells breaks whole besides, as every
  breakable piece there does.
- **Losing any of it**: a bite or a crater that takes a voxel of a piece's glass shatters the rest of
  its glass with it (`_wear_away()`), and a piece crumbling, broken whole or landing after a fall,
  shatters its glass as the rest crumbles (`crumble()`). A window falling whole keeps its panes,
  drawn as glass on its `FallingBlock` (`TerrainDestruction._drop_whole()` hands its glass on), until it
  lands.
- **A loose model's glass**, the same ways: a round tearing through it (`tear()` ->
  `_shatter_model()`), a crater reaching it, the model crumbling (`_crumble_model()`, `_break_up()`).
- **A dying unit's figure**: its glass (a visor) is left out of its lumps (`FigureVoxels.crumble()`)
  and bursts with the killing blow's knock (`FigureVoxels.glass_points()`, from
  `TerrainDestruction.break_figure()`).

**Glass holds nothing up.** What keeps a piece standing is its voxels but its glass
(`VoxelVolume.held_count()` / `held_whole()`, against `collapse_below`); `holds_up()` never runs
through glass; `_drop_loose()` never searches through it, so nothing hangs on a pane; glass is never
laid bare as earth nor buries what is behind it (`lay_bare()`), and a hole's rim is never roughened
into it (`roughen_hole()`). A window's frame stands or falls by its own voxels, panes or none.

### Shards

**`GlassShards`, a node under `TerrainDestruction` (its `glass_shards`), draws every shard.** About one
for every `VOXELS_PER_SHARD` (3) voxels of glass, each made where one of them was, in its colour and
as clear as it was: a thin plate `SIZE_MIN` to `SIZE_MAX` (0.6 to 1.7) voxels across and `THICKNESS`
(0.25) thick, drawn by `GlassShard.gdshader` and `GlassShardShine.gdshader`, the panes' two passes
again, its colour the instance's colour and its clarity its custom data. A shard is no body and no
node, but an instance of a `MultiMesh` of `CHUNK` (1,024); there are at most `MOST` (8,192), the
oldest taken up for each past that.

- **It falls.** It sets off as its cause says, plus a scatter (`SCATTER`, 0.8 cells a second),
  tumbling at 6 to 18 radians a second under the project's gravity, and lands on the first voxel of
  the level straight under it (`floor_under`: `VoxelTerrain.floor_under()`, through
  `VoxelVolume.solid_below()`, a row of bits at a time), looked for again whenever it falls into a new
  column of voxels; a column with something solid where it would go is a wall, which stops it going
  across. It bounces (`BOUNCE` 0.3 of its fall back up, `SLIDE` 0.4 of its speed across, its spin
  halved) until it lands slower than `REST_SPEED` (0.7), then lies flat at a turn of its own. One that
  falls below the map (`lowest`) is gone.
- **It stays for good** (the user's), costing nothing a frame: lying, it is filed by cell and never
  moved again unless what it lies on goes. Each chunk of the level drawn again wakes the shards round
  it (`VoxelTerrain._on_chunk_redrawn()` -> `wake(box)`), and one whose floor has gone falls again.
- **It is hidden over what is cut away from the view** (`Cutaway` sets its `hides` and `hide_above`
  and calls `rehide()` as the cut changes): every frame it falls, as it lands, and every shard lying
  still as the view is cut again.
- **Its chances are its own** (`_show`, seeded at random), never the global generator's.

## The window piece

**`SimpleWindow1`** (`Blocks/SimpleWindow1.vox`, made by `MagicaVoxel/Buildings/make_windows.py` from
`SimpleWall1.vox`) is `SimpleWall1` with a window in it: a white frame a voxel wide round a 12 by 12
opening, a mullion and a transom two voxels wide across it, so four panes of 5 by 5, 100 voxels of
glass a voxel thick in the wall's second layer, and a sill standing a voxel proud of either face along
its foot. Its glass is palette entry 191, (226, 240, 244), Transparency 0.9 (clarity 28 steps of 31).
Its kind in `Pieces.tres` is an edge piece, `cutaway` (cut away with the walls) and `window`, with
`SimpleWall1`'s `model_transform`, so it lines up with the wall it stands in, and wears away as the
wall does (`Resources/Destruction/SimpleWindow1.tres`, `SimpleWall1.tres` but for its mass, 50 for
75). The brush **SimpleWindowWall2** places it on a `SimpleWall1`, its sill: a window at a unit's eye,
half cover under it. The level editor's palette calls the kind "(edge, window)". Running the script
again overwrites the `.vox`, so copy one edited by hand first.

**In the maps:** TestMap's house has seven, each in place of a course of wall at level 3, between the
course under it, its sill, and the one over it: two in each gable end (slots (48, 3, -49) and
(50, 3, -49); (48, 3, -39) and (50, 3, -39)), one in the side wall toward -x ((45, 3, -44)) and two in
the side wall toward +x ((53, 3, -46), (53, 3, -42)). `LineOfSightTest`'s window lane is under Probing it.

**Glass in another model** is painting it with a Glass material in MagicaVoxel (Transparency for how
clear, its colour for its tint) and importing it as ever: the game reads it as glass wherever it is
drawn, a block, a prop, a board or a figure (bake a figure again). **A new window** is a kind with
`window` ticked, its glass painted so; a piece with glass and `window` off is solid to the rules,
glass and all, as a block of glass or a display case should be.

## The importer

The MagicaVoxel importer (`addons/MagicaVoxel_Importer_with_Extensions/`, now 1.3.1: its
`CHANGELOG.md`) was mended and taught glass, for the meshes it still draws: coins, a grenade in flight
and the editor's previews of a `.vox`; the game's own drawing never uses its materials. It looked for
`rough`, `flux` and `ior`, where MagicaVoxel writes `_rough`, `_flux` and `_ior`, which stopped a glass
or emissive material with a script error, and it made glass see-through with Godot 3's flag, which
does nothing in 4. Now `VoxMaterial` reads each key with its underscore (falling back to the old
`_weight`), a glass material is `TRANSPARENCY_ALPHA` with an alpha of one less its Transparency, an
emissive one glows in its voxels' colour as bright as its emission and power, the greedy mesh
generator meshes glass as a second, see-through surface by `ChunkMesher`'s face rule (a model without
glass meshes exactly as it did), and the culled one draws a palette entry with no material as diffuse
rather than failing. `MagicaVoxel/Shapes/README.md` said the importer already read glass; it did not.

## What it costs

Measured on TestMap (seven windows) on this laptop (a Ryzen 7 5800H), headless:

- **Nothing where there is no glass.** A chunk with none is meshed as before, and a model with none is
  one surface under its `material_override`, as before. With glass, a section of the level or a model
  has one more surface, drawn in two passes: two draw calls more. A pane is a handful of rectangles.
- **A round's check for glass along its line**: 0.05 ms, meeting none. **A unit's step**: 0.05 ms. A
  unit is checked only as its tile changes, a grenade in flight each frame.
- **Shattering a pane**, its chunks drawn again at once: 1.7 to 3.5 ms.
- **Shards:** 2,000 made at once (6,000 voxels of glass, sixty windows' worth) 13 ms; falling, 2 ms a
  frame until the last lies still (175 frames, from 6 cells up); lying, nothing; waking every one in
  a big box, 3 ms. A shard for every two voxels, as first written, cost 92 ms to make 2,000 and 13 ms
  a frame to move them; one for every three, the spin kept as an axis and a speed, and the floor under
  a shard read a row of bits at a time brought them to these.

## Its scripts

```
  Terrain/
    VoxelShape.gd          flags (FLAG_GRID, FLAG_WET, FLAG_GLASS, clarity in the top bits), glass and glass_rows,
                           find_glass(), glass_flags(), clarity_of(); _paint() reads the .vox's materials
    VoxelModel.gd          glass_rows; its glass a second surface (GLASS_SURFACE) with a material of its own
                           (glass_material(): GLASS_SHADER, SHINE_SHADER its next pass, SHINE_PRIORITY), faces_of(),
                           glass_surface_of(), set_parameter(), is_glass(), glass_indices(), _apply_materials()
    Voxels.gdshaderinc     what the three voxel shaders share: the uniforms, the vertex function, the lookups, the flags
    Voxels.gdshader        every voxel but glass
    VoxelGlass.gdshader    glass, its first pass: what is behind multiplied by its colour, as clear as it is
    VoxelGlassShine.gdshader  its second: its shine and the share of its colour it does not let through, added
    GlassShards.gd         every shard of broken glass: MultiMesh instances that fall and lie for good; burst(),
                           wake(), rehide(), count(), falling_count()
    GlassShard.gdshader, GlassShardShine.gdshader  a shard's two passes
    VoxelTerrain.gd        shatter(), shatter_along(), shatter_near(), shatter_passing(), floor_under(); glass in
                           wear (bites, craters, collapse, loose models), held counts, holds_up(), _drop_loose()
    TerrainDestruction.gd  glass_shards; _shatter_passing() every frame (units, grenades in flight); a round's
                           line, a blast and a dying figure shatter; windows held up and holding up
  Level/
    ChunkMesher.gd         faces(): the rest's and the glass's; glass_rectangles(), without(); Near's *_glass
    VoxelVolume.gd         each chunk's glass_x / glass_z; glass_whole, glass_counts; is_glass(), is_opaque(),
                           glass_of(), pieces_with_glass(), held_count() / held_whole(), solid_below()
    LevelRenderer.gd       glass_material; each section's glass a second surface; the collision with it
    SceneryRenderer.gd     a scenery kind's glass, a second surface
    LevelRules.gd          windows apart (is_window(), window_slots()); pieces_at() and has_slot() with them
    PieceKind.gd           window
    VoxelLevel.gd          is_under_building(): a glass roof shelters too
  Combat/
    CombatGrid.gd          _crossing(): the vault through the level above alone; a round's trace passes glass
    ThrownGrenade.gd       GROUP: a grenade in flight, for what it passes through
    Cutaway.gd             hides the shards over what is cut away
  Characters/
    VoxelRig.gd            a figure's flags and glass, its glass a second surface of the bake
    FigureVoxels.gd        glass_points(): a visor to shatter; crumble() leaves glass out of the lumps
```

Beside them: `MagicaVoxel/Buildings/make_windows.py` (and its `SimpleWindow1.vox`, copied to
`vcom/Blocks/`), `Resources/Destruction/SimpleWindow1.tres`, the kind and brush in `Blocks/Pieces.tres`,
the level editor's palette note (`LevelEditorDock._note_of()`) and the importer's `VoxMaterial.gd`,
`GreedyMeshGenerator.gd` and `CulledMeshGenerator.gd`.

## Probing it

Headless, as everything else (`CLAUDE.md`'s Verification), but glass is only seen in a window: render
it (`--write-movie` or a `--script` driver saving the viewport, never `--headless`). The headless
renderer keeps no `MultiMesh` instance data, so read a shard from `GlassShards`' own arrays
(`_state`, `_positions`, `_cut`), never its MultiMeshes.

- **What is glass:** `level.volume.glass_counts[piece]` (100 for a whole `SimpleWindow1`),
  `glass_of(piece)`, `is_glass(voxel)`, `pieces_with_glass()`; a model's `glass_count`,
  `VoxelModel.glass_surface_of(drawn.mesh)` (-1 for none) and the shader of
  `drawn.get_surface_override_material(at)`; a shape's `glass_count` and
  `VoxelShape.clarity_of(shape.flags[place])`.
- **The rules:** `level.rules.is_window(piece)`; `has_edge()` false at a window and true at its sill;
  `grid.is_line_clear()` through it; `LineOfSight.cover_at()` low over a sill, none at a glass door;
  `grid.neighbours()` across it and `grid.vault_height()` 1; `Throwing.plan()` through it
  (`is_clear()`); `grid.cast(origin, direction, distance, true)` (a round's: passes the glass, meets
  the mullion) and with `every_block` too (blood's: meets the glass); `grid.pick_tile()`.
- **Shattering:** `terrain.voxels.shatter(PackedInt32Array([piece]), func(_at): return Vector3.UP)`;
  `grid.fly(from, to, 5)` (a round's line); `grid.blast(origin, cells, 10, 1.0)`; a unit walked
  through with `MoveAction._move_to()`; a throw with `ThrowGrenadeAction._aim(tile)` and
  `_throw_lined_up()`. Then `terrain.glass_shards.count()` and `falling_count()`: how many shards a
  pane makes is fixed, where they go is random, the shards' own generator being seeded at random.
- **The lane** in `LineOfSightTest`: eight rows of ground past the harness's old end (cells x 0 to 15,
  z -44 to -37), and along the edge between z -41 and -40, from x 2: two columns of plain wall two
  courses high (x 2, 3), four windows over a sill under a lintel (x 4 to 7), four over a sill with
  nothing over them (x 8 to 11), a plain wall (x 12), and a glass door, two windows stacked on the
  ground (x 13). The probe places the units.

The probes made for this were in a session's scratchpad, and went with it; each is quick to write
again from the calls above. They checked: the lane, 144 things, three runs (every window's sight,
low cover, vault and support; the walls beside it not seen through or crossed; the door walked through
and no cover; whole rays, rounds and blood at the frame and the glass; clicks; a throw under a lintel
and the same through a wall; shots through windows; a round, a blast, a vault, a grenade's flight and a
bite each shattering what they should and nothing else; a window broken whole and its lintel falling;
a window falling whole drawn with its glass and shattering as it lands; every shard lying on its
floor); the faces of a random level of windows, walls, crates and ground, overlapping, turned and
across chunks, checked against the voxels face by face, fresh, worn, bloodied and cut away (10.3
million checks); the importer, models, the bake and paint (38); a figure with a visor (a `.vox` of the
figure with 21 voxels of glass at Transparency 0.6), baked, drawn and shattering as it dies (6); a
loose model with glass (6); TestMap through the game's own actions (a shot through a window, a move
vaulting in through another, an enemy's turn inside: 7); a seeded fight with glass replaying exactly
(the same voxels, glass, pieces standing and next random number, twice); shards hidden over a cut
(7); and a dump of every map's steps, cover, sight, rays, throws, misses, shots and every chunk's
voxels and faces, the same with the code for glass as without it, before any window went into a map.
Renders checked the look: the house's windows close up in sun and shade, from inside and from above
with the roof cut away (the sun's squares on the floor), a pane shattering frame by frame, blood on a
pane, and the lane.

## Known gaps

- Glass hides nothing: a unit behind a whole window is seen as through an empty frame. There is no
  concealment in the game to break, as XCOM 2's vault through a window does.
- A pane shatters whole: no cracks, no holes, and a round through one of a window's four panes
  shatters all four, the piece's glass being one.
- Debris never breaks glass: a lump or a crate's board flying into a pane bounces off it, the
  level's collision holding the pane until it shatters by a round, a blast, a unit, a grenade or wear.
- Shards are no bodies: they fall through units, debris, loose pieces and falling blocks and lie only
  on the level's voxels; a unit walking over them leaves them be; blood flies through them, and no
  shard is stained after it is made.
- Glass casts no shadow at all: a stained pane lets the sun through white, and a pane smeared with
  blood lets it through as if clean.
- A pane's shine is added after every other see-through thing (its render priority), so a tile
  highlight or a tracer in front of a window has the pane's faint shine over it; and Godot sorts
  see-through things by object, so one behind a pane can draw after its tint, untinted.
- Clarity is in 31 steps. MagicaVoxel's other materials (metal, emissive, cloud) are read by the
  importer alone: on a block, a prop or a figure they draw as plain colours, and nothing glows.
- A window in the middle of a cell or on a corner is decoration too, so nothing stands on one: a
  floor of glass is no floor to the fight. A roof of glass counts as a building's for the cutaway
  (`is_under_building()`) and nothing else.
- The figure hops a window as it hops a fence: it passes through the frame and the lintel, with no
  dive or climb fitted to the opening.
- A blast shatters every pane within three cells whatever stands between, a thick wall included,
  XCOM 2's way.
- Past 8,192 shards the oldest is taken up for each new one, wherever it lies.
- The AI knows nothing of windows beyond the rules: it shoots and walks through them as through any
  open line and vault, and never breaks glass for its own sake.
- No figure in the game has glass yet; a visor was probed on a copy of the figure. No crate's pieces
  have any either, though a loose model's glass shatters as a pane's does.
- Scenery's glass is drawn and never shatters, as nothing of the scenery breaks.

## Decided without asking

- Glass is MagicaVoxel's Glass material, its clarity its Transparency and its tint its colour, in the
  palette's flags beside the tile grid and wet, clarity in their top five bits; the rest of the
  material is the importer's alone.
- A voxel stays glass whatever colour it is given, and blood on glass is opaque, wet red, not red
  glass (blood's place, shared by everything, has no clarity), its shard red and opaque too.
- An opaque face shows through glass and a glass face only against nothing, as Zylann's voxel module
  for Godot meshes see-through blocks.
- The look's numbers: the shine's roughness 0.04 and specular 0.5 (0.55 and 0.35 for blood), the tint
  unshaded, fog off on both passes; the shine drawn after every tint by its render priority.
- The level's collision includes glass, so debris bounces off a whole pane.
- Windows are decoration to the fight as corners are, kept in a table of their own, rather than a new
  kind of slot or a flag read by each rule.
- A round shatters a window whose slot it crosses at its level, through the frame as through the glass
  (to the rules it went through the window); a unit by the tiles it passes between, up to a level over
  its head; a grenade in flight by its line each frame; a blast every pane within three cells of it,
  measured to the piece's cell, whatever stands between; any glass lost shatters all of its piece's.
- The shards: one for every three voxels of glass (after measuring two), their size, thickness,
  scatter, spin, bounce and the speeds they set off at; lying flat; stopped by walls; hidden over
  what is cut away as debris is; their own generator.
- The window piece: four panes in a white frame, the glass a voxel thick in the wall's second layer, a
  sill a voxel proud of each face; its glass Transparency 0.9 and palette entry 191; worn as the wall
  is, at a lighter mass; the brush on a `SimpleWall1`; made by a script from `SimpleWall1.vox`.
- Where TestMap's seven windows went, and the lane's layout.
- The importer's fixes and its version, 1.3.1, the emissive fix included; the figure's bake giving
  its glass a pale see-through material for the editor's view.
- `Voxels.gdshader` rewritten on a shared include, so the glass shaders read voxels the same way.
- `CombatGrid._crossing_top()` became `_crossing()`, giving the highest level a step fills, for the
  relaxed vault.
