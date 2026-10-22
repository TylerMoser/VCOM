# Cutaway

Seeing inside buildings, in full: the floor selector (`Scripts/UI/FloorSelector.gd`, its art in
`vcom/UI/`), what a cut takes away (`Scripts/Level/LevelCutaway.gd`), how the level draws it
(`LevelRenderer.cut()`), what is hidden with it (`Scripts/Combat/Cutaway.gd`, `VoxelDebris`), and the
parts of `VoxelLevel`, `CombatGrid`, `TileHighlights`, `TileCursor`, `Unit`, `CameraRig` and
`ActionController` that know of it. Written as it was built (2026-10-22); `CLAUDE.md` keeps a summary
("The view can be cut away") and the rule that must not drift. A section named here that is not in this
file (Gotchas, Verification, another subsystem's notes) is `CLAUDE.md`'s.

## What the user decided

1. A building piece is marked as one by its kind: `PieceKind.cutaway`, on `SimpleWall1`,
   `SimpleTruss1` and `SimpleRoof1` (`Blocks/Pieces.tres`).
2. The heights a map can be cut away from are a list on its `Level` node,
   `VoxelLevel.cutaway_heights` (cell y, any number of them); `TestMap.tscn` has one, 5.
3. A floor selector, drawn after the user's sketch (a stack of sheets: a whole one on top, the edges
   of more under it): one icon on top, which shows everything, and a floor icon under it for each
   height in the list. The top is chosen to begin with; clicking a floor chooses it and hides every
   building piece at that height or higher.
4. It sits centred top to bottom on the left edge of the screen.
5. `PageUp` / `PageDown` on the keyboard, the d-pad's up / down on the gamepad.
6. A hidden roof still casts its shadow: the light is unchanged.
7. Anything on top of what is hidden is hidden too.

The approach, rebuilding the chunks' meshes rather than discarding pixels in the shader, was proposed
before building and not objected to (see "Why meshes, not the shader").

## How it works

**What is cut away** is a `LevelCutaway`, made by `VoxelLevel.cut_away(from_level)` from the level's
pieces as the rules see them then. Its `pieces` (a set of indices into the `LevelData`) are every
piece of a `cutaway` kind with its slot at `from_level` or above, broken or not, and every other piece
resting on one of those: a piece is resting on one if, in its column (a centre piece) or across its
edge or in either column beside it (an edge piece), a building piece cut away stands at its level or
below (`covers_slot()`). Only building pieces still standing to the rules (`LevelRules.is_standing()`)
count for what rests on them, so a roof shot through stops hiding what falls in.

It also says where things are hidden (`covers_point()`, `covers_cell()`): a point is hidden if a
building piece cut away stands at its cell's level or below in its column, or across an edge within
`LevelCutaway.STRIP` (0.2 cells) of it at that level or below. So a unit standing on a roof tile is
hidden and one on the floor under the roof is not; the test for a tile is the same as for a unit's
feet on it. `VoxelLevel.is_cut_away(world)` and `is_tile_cut_away(tile)` ask it, false with nothing
cut away.

**`VoxelLevel`** keeps it (`cutaway`, null with nothing cut away; `cut_level()`, `UNCUT` -1 then),
hands its pieces to the renderer and emits `cut_changed`. `UNCUT` shows everything again. As a piece
leaves the rules (`LevelRules.removed`) while anything is cut away, it works the cut out again at the
end of the frame (`_recut()`), redrawing only if the pieces cut changed, and emits `cut_changed` for
what hides by place. Nothing is cut away in the editor.

**Drawing it** (`LevelRenderer.cut(pieces)`). For each chunk a cut piece reaches
(`VoxelVolume.keys_of()`), `_cut_chunk()` copies its rows of bits without the voxels those pieces
still own (`Chunk.slots`, so a later piece's voxels over them stay), a row at a time across each
piece's box (`ChunkMesher.BIT` finds each bit). Every such chunk, and each chunk beside one, is meshed
again from those rows (`_mesh_cut()`, the neighbours' faces read through `_shown_rows()`), so what the
cut pieces hid gets faces: the top of the wall course under a cut one, the ground under a cut wall.
A section with any chunk so drawn (`_build_section()`) draws the cut meshes, casting no shadow, and
under them, as `Shadow`, its whole mesh, `SHADOWS_ONLY`: every shadow falls as it did, and the inside
of a house stays in its roof's shadow. Collision is always the whole level's. Wear while cut
(`refresh()`) cuts each chunk changed again before any is meshed, then meshes it both ways. Cutting
TestMap's house from 5 (32 pieces) redraws 26 chunks and adds 12 shadow sections in about 21 ms;
showing it whole again takes about 1.5 ms.

**What is hidden with it.** A `Cutaway` node in each combat map, after `Blood`, follows
`cut_changed`. While anything is cut away it looks every frame at every unit (`Unit.GROUP`), every
loose piece (`TerrainDestruction.PIECES`: a crate's pieces, parts cut off them, dropped gear), every
`FallingBlock` under `TerrainDestruction` and every coin under `Coins`, and hides each whose position
`is_cut_away()`, showing it again once it is not. A unit is hidden by `Unit.set_cut_away()`, which
also takes its pick body off the click layer, so a click goes through it to what is seen; anything
else by `visible`. It only ever shows what it hid itself, so a node something else hid stays hidden.
The lumps of debris have no nodes: `VoxelDebris.hides` (the level's `is_cut_away`) and `hide_above`
(the world height of the cut, below which no lump is asked) are set from `Cutaway`, a lump hidden
draws its voxels shrunk to nothing (`_draw_lump()`), it is asked again each time the physics moves
it, and `rehide()` asks every lump as the cut changes. It still moves and collides as ever.

**The pointer** sees what is shown. `CombatGrid.cast()` takes `passing`, a set of pieces it treats as
not there, cell or edge; `cast_seen()` passes the level's cut pieces, and `pick_tile()` (every mouse
tile) and `CameraRig._start_drag()` use it. Sight, shots, throws and blood use `cast()` as ever and
meet every piece. `TileHighlights` draws no square on a tile `is_tile_cut_away()` and rebuilds on
`cut_changed`, every layer keeping its tiles; `TileCursor` passes such tiles by when it steps and when
it finds its tile again, and comes down off one as it is cut.

**The floor selector** (`FloorSelector`, in each map's HUD, after `AmmoIndicator`) is built in code
as the HUD is: a `Control` anchored centre-left, `MARGIN` (16) from the edge, sized to its sheets plus
`PADDING`, on a panel styled as the ammo indicator's. It reads `cutaway_heights` once, as it readies,
drops repeats and sorts them highest first; with none it never shows and takes no input. It draws
`UI/floor_top.svg` at the top and `UI/floor_level.svg` for each floor, `STEP` (16) apart from
`FIRST_FLOOR` (25) down, lowest first, tinted: `CHOSEN_COLOR` gold for the chosen sheet,
`HOVER_COLOR` for the one under the pointer, `CUT_COLOR` (faint) above the chosen, `SHOWN_COLOR`
below. `_sheet_at()` tells a sheet by bands as deep as `STEP` sloping as the sheets do, so a floor's
whole band clicks, not just its thin edge. A left click chooses; any click on it is taken, so none
reaches the map. `floor_up` / `floor_down` (`PageUp` / `PageDown`, the d-pad's up / down) are read in
`_unhandled_input` and always marked handled, at the ends too: the HUD is after `CameraRig` in the
tree, so the selector sees them first and the d-pad never zooms on a map with floors.
`choose(sheet)` cuts the level (`UNCUT` for the top); it follows a cut made from elsewhere through
`cut_changed`. `ActionController._show_hints()` adds a "Floor" row for the d-pad's up and down on such
a map.

**The art.** Both icons are white, so the tint is their colour, with a dark outline 2.5 px wide that
the tint barely changes. `floor_top.svg` (64 x 38) is a rhombus, corners at (2, 19), (32, 2), (62, 19)
and (32, 36). `floor_level.svg` (64 x 28) is the front edges of the same sheet, a band 8 px deep whose
upper edge runs parallel to the top sheet's lower edges 8 px under them once drawn `FIRST_FLOOR` down.
`FloorSelector`'s `ART_WIDTH`, `SIDE_Y`, `BOTTOM_Y`, `SIDE_INSET`, `STEP` and `FIRST_FLOOR` are those
shapes' numbers: change one, and the other with it.

## Why meshes, not the shader

Discarding the cut voxels' pixels in `Voxels.gdshader` would have been instant, but the level is
meshed with every face between two voxels left out, so a cut wall would show an open slit along its
top and a cut wall on the ground a hole into the ground, and the shader could only tell a building's
voxel by a palette flag, which a blood stain replaces (`VoxelVolume.recolor()`). Meshing the few
chunks a building is in again gives the cut real faces and reads ownership, not colour.

## Probing it

Headless: load a map, wait a few frames, then `level.cut_away(5)` (or the selector's `choose(1)`, or
push an `InputEventKey` with `physical_keycode = KEY_PAGEDOWN`, press and release). Read
`level.cutaway.pieces` (by `data.kind_id()` and `data.slot_at()`), `level.renderer.cut_counts()`
(chunks drawn cut, shadow sections) and `level.renderer.triangles`; `level.is_cut_away(point)` and
`is_tile_cut_away(tile)`; `grid.pick_tile(from, Vector3.DOWN)` against `grid.cast(...)` to see the
pointer pass the roof and the rules meet it. TestMap's house spans cells (22, 2, -25) to (27, 6, -19):
tile (24, 2, -22) is inside on the ground floor, (24, 7, -22) on the roof. With `--fixed-fps 60`, wear
a level-4 wall (`grid.cast(from, dir, 30, true)` then `grid.strike(hit, 5)`) or
`terrain.break_piece()` a roof piece cut away, and count `voxel_debris._cut` (1 for each lump hidden)
over the frames after. To see it, render in a window: set the camera rig's `_pivot`,
`_current_pivot`, `_yaw`, `_current_yaw` and `_zoom` on the house, move a unit there by its
`global_position`, and save `root.get_texture().get_image()` after `RenderingServer.frame_post_draw`,
whole and cut.

## Decided without asking

- What rests on a piece cut away is found by column and edge, not by physics or by what touches it:
  a centre piece's column, an edge piece's edge and both columns beside it, at the cut piece's level
  or above; and a point within 0.2 cells of a cut edge piece counts as on it.
- A unit hidden is hidden whole, figure and gear, and takes no clicks; it can still be lined up from
  the action bar's target cycling and the shot panel, as it is still there to the rules.
- Small things hidden (units, pieces, coins, lumps) are hidden outright, their shadows with them;
  only the level's own pieces keep casting theirs. The cut tops of walls are drawn and lit like any
  face.
- The icons' shapes, sizes, outline and the gap between sheets; the panel; the colours (gold chosen,
  faint above, grey below, lighter under the pointer); a floor's whole band clicking; the pointing
  hand over it.
- On a map without floors the d-pad's up / down still zoom, as they always did; on one with floors
  they only change the floor. The selector stops at either end rather than wrapping.
- Every combat map has a `Cutaway` node and a `FloorSelector`, hidden where the map has no heights,
  so a map only needs heights to have floors.
- The cut is redrawn by meshing chunks again (above), the whole meshes casting the shadows.

## Known gaps

- The floor never changes by itself: it stays as chosen through turns, and an enemy acting on a roof
  cut away does so unseen, the camera framing nothing. Nothing switches floors to follow the
  selection, the cursor or the camera.
- Shots, tracers, muzzle flashes, grenades in flight, explosions and blood drops in the air are not
  hidden, and a round still stops on a roof that is cut away, as the rules see it: it is seen
  stopping in the air. A bite out of a hidden piece throws lumps that hide while over it.
- A roof overhanging the walls hides what is under the overhang outside the house too, and an edge
  piece only hides what is within its strip: something on a cut wall's top that sits further off
  the edge shows.
- Screen-space light (SSAO, SSIL) reads only what is drawn, so the inside of a house is lit a shade
  differently once its roof is not in the depth buffer, though every shadow is as it was.
- A cut costs about 21 ms on TestMap's small house, all of it GDScript meshing; a big building, or
  many, costs more, on the frame it is chosen. Each section drawn cut keeps a second, whole mesh for
  its shadow.
- The heights are read once, as the map loads: changing `cutaway_heights` mid-battle changes nothing.
  TestMap has one; three (3, 4, 5, set before it loads) were rendered and clicked by probe, not
  played.
