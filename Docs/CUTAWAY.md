# Cutaway

Seeing inside buildings, in full: the floor selector (`Scripts/UI/FloorSelector.gd`, its art in
`vcom/UI/`), what a cut takes away (`Scripts/Level/LevelCutaway.gd`), how the level draws it
(`LevelRenderer.cut()`), what is hidden with it (`Scripts/Combat/Cutaway.gd`, `VoxelDebris`), and the
parts of `VoxelLevel`, `CombatGrid`, `TileHighlights`, `TileCursor`, `Unit`, `CameraRig`,
`ActionController`, `TurnManager`, `ShootAction`, `StrikeAction` and `UseMedkitAction` that know of it. Written as it was built (2026-10-22); `CLAUDE.md` keeps a summary
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
8. The game changes the floor too: when an enemy hidden by the floor chosen takes an action, or the
   player tries to target a hidden enemy, ranged or melee, the floor becomes the one that enemy is on,
   so it is seen.
9. The same for squad members: one selected, however, or targeted, is shown on the floor they are on.
10. The d-pad's up / down control the floors and nothing else: they zoom nowhere, the world map
    included.
11. Whenever an enemy or a squad member is given the focus (all of the above), and they cannot be
    seen because they are inside a house, and changing the floor would show them, the floor changes
    to theirs.

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
A hidden unit's figure still counts what it carries as shown: `CharacterModel.gear()` reads a prop's
visibility only as far up as the figure (`_is_shown_on_figure()`), so blood still lands on its gear
and a unit dying hidden still drops it, where it hides in turn while over what is cut away (as
`is_visible_in_tree()` had it, a unit hidden dropped nothing and its gear went with it).
The lumps of debris have no nodes: `VoxelDebris.hides` (the level's `is_cut_away`) and `hide_above`
(the world height of the cut, below which no lump is asked) are set from `Cutaway`, a lump hidden
draws its voxels shrunk to nothing (`_draw_lump()`), it is asked again each time the physics moves
it, and `rehide()` asks every lump as the cut changes. It still moves and collides as ever.

**The game changes the floor** as it gives a unit its focus, through
`CombatGrid.show_floor_of(feet)`, for the units standing with their feet at each point given, all
at once. It does two things, and returns whether either changed the floor; the selector follows
through `cut_changed`, and the floor is left where it was brought to, for the player to choose again
from there.

- **None hidden with the cut.** `VoxelLevel.reveal(world)` cuts the view from the lowest of the
  level's floors (`floor_heights()`: `cutaway_heights` each once, lowest first) above the height cut
  now that leaves the point shown (`cutaway_from(height)`, a `LevelCutaway` made to ask, not cut), or
  from none (`UNCUT`) if none does. That is the floor the unit is on, and it only ever cuts away less.
- **None lost inside a house.** A unit is inside one when a building piece still stands above its
  tile in its column, to the rules, cut away or not (`VoxelLevel.is_under_building()`). One inside
  that the camera cannot see (`_is_seen()`: a line from its feet, its middle and its head, 0.3, 1.0
  and 1.7 over its feet, back along the camera's view as far as the camera's height, meets a solid
  piece not cut away) has the view cut from its floor, the lowest of the floors above the tile it
  stands on, or failing that from each floor below that in turn: the first that shows it and hides
  none of the units given (`_hides_any()`). The view's way, not the camera's place, is used, as the
  camera is about to turn its focus there; sight is traced through whole cells and edges, as
  `cast()` does. A unit outside a house, one already seen, and one no floor shows (behind a tree)
  leave the floor be.

`TurnManager._take_enemy_turn()` shows an enemy before the camera comes to it, for any turn it does
more than end; `_move_enemy()` the enemy and every tile it will walk, before it sets off; a shot the
enemy, the tile it steps out to and the squad member it is aimed at, before the camera frames it; a
reload the enemy; and `_start_player_turn()` the squad member selected. `ShootAction._show_shot()`,
`StrikeAction._show_target()` and `UseMedkitAction._show_target()` show the one each lines up, and
the unit acting with it, however a target is lined up: as the action begins, cycled, clicked or
reached by the cursor. `ActionController._on_selection_changed()` shows the squad member selected,
however they were: Tab, LB / RB, a click on them or their card, A on the cursor, the selection moving
on after a death. Units given together are never split by a floor: a shooter on a roof is not cut
away to show a target inside below it.

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
`_unhandled_input` and marked handled, at the ends too; nothing else is bound to the d-pad's up and
down, so on a map without floors, and on the world map, they do nothing.
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
over the frames after. The game's own changes: move an enemy and a squad member on to two roof tiles
side by side (`Tactics.is_next_to()`; TestMap's roof has 20 tiles at y 7), cut from 5, then
`controller.activate()` Shoot, or set Strike's `_unit`, `_targets` (a typed `Array[Unit]`) and
`_index` and call `_show_target()`, or start `TurnManager._take_enemy_turn(enemy)` through a lambda
(Gotchas) and read `cut_level()` a frame later; an enemy inside on the ground floor acting leaves it.
`level.reveal(point)` alone, with heights set before calling it, shows which height it comes up to.
For a unit inside, put a squad member on tile (24, 2, -22), under the roof, with the view whole, and
select it (`squad.select()`): the floor becomes 5, or 3 with heights 3, 4, 5 set before the map
loads; `grid._is_seen(feet, camera, level.cutaway)` says whether the camera's view reaches them, the
camera being `get_viewport().get_camera_3d()` once the rig has run a few frames. A tile outside out
of sight behind the house (one `_is_seen()` with null says is not seen, not `is_under_building()`)
changes nothing; `grid.show_floor_of([roof_tile_feet, inside_feet])` (a typed `Array[Vector3]`)
leaves the view whole. An enemy's turn can kill the squad members a probe goes on to select: load
the map afresh for each.
To see it, render in a window: set the camera rig's `_pivot`,
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
- The selector stops at either end rather than wrapping.
- Every combat map has a `Cutaway` node and a `FloorSelector`, hidden where the map has no heights,
  so a map only needs heights to have floors.
- The cut is redrawn by meshing chunks again (above), the whole meshes casting the shadows.
- The floor the game changes to for a unit hidden with the cut is the lowest that shows it, not the
  top; an enemy's walk shows every tile it will walk, and its shot the tile it steps out to, before
  either starts; a target lined up as Shoot, Strike or Use Medkit begins counts as one the player
  targets; and once changed, the floor stays where the game brought it.
- "Targeted", for a squad member, is an enemy's shot at them (enemies only shoot) and Use Medkit
  lining them up; the camera settling on the squad member selected as the player's turn starts
  counts as a focus too.
- For a unit inside a house: "inside" is under a building piece in its column (a roof, or a floor
  above), so walls alone, a roofless ruin, are not; "cannot be seen" is three lines from its body
  back along the camera's view, traced through whole cells, any one clear being enough; "their
  floor" is the lowest floor above the tile they stand on, and failing that the floors below it,
  most first. The unit acting stays seen with its target (Shoot, Strike and Use Medkit pass both),
  and an enemy with its whole walk or its shot.

## Known gaps

- The game changes the floor only as it gives a unit its focus, and never back to the floor the
  player had. A squad member firing a reaction shot from a roof cut away, or from inside a house,
  does so unseen, as one stepping out on to a hidden tile to shoot does; nothing follows the cursor,
  the camera turning or a unit walking once the walk has begun; and a grenade's target tile is not
  shown. An enemy's walk in and out of a house is shown as far as one floor can show all of it.
- Whether a unit can be seen is judged along the camera's view, not from where the camera will
  stop, and through whole cells: a roof's cell blocks the line even where its slope would not, and
  a camera so close that it is lower than the roof is taken to see under it.
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
