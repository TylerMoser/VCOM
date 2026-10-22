# Camera

The combat camera in full: how `CameraRig` moves, the player's way and the game's; what it does on the
enemies' turn, `TurnManager` bringing each enemy into view, following its walks and showing its shots,
and `Reactions` framing a reaction window; how far it may see; and the gamepad cursor's part in it. It
was split out of `CLAUDE.md`, which keeps a summary. A section named here that is not in this file
(Gotchas, Verification, another subsystem's notes) is `CLAUDE.md`'s.

## How it works

**The player's moves ease; the game's glide.** What the player does to the camera answers at once,
eased exponentially as it always was: the pan keys, the screen edge and the drag (`pan_smoothing`),
Q / E (`rotate_smoothing`), the wheel and the right stick (`zoom_smoothing`), and the gamepad's stick
stepping the tile cursor, which carries the camera through `CameraRig.pan_to()`. What the game does to
it glides, as XCOM 2's camera moves (its `X2Camera_LookAt`: `InterpolateLocation`, `InterpolateZoom`,
`InterpolateRotation`), ported as `CameraRig.Glide`: from rest the speed ramps up to a top speed over a
ramp, and once the goal is closer than the ramp's seconds times the top speed times a brake share, the
speed is held to that share of the top speed in proportion to what is left, never below a least share,
so it eases to a stop. How far up the ramp it is carries over while it is on the move, so a goal that
moves mid-glide (a followed walker, a reaction view framed again) is chased without a jolt; arriving puts
it back at rest. The numbers are XCOM 2's (`DefaultCamera.ini`'s `[XComGame.X2Camera_LookAt]` and the
code's shares), the user's call ("for now, match XCOM 2's pacing"):

| | Top speed | Ramp | Brake share | Least share |
|---|---|---|---|---|
| Pan (`glide_speed`, `glide_ramp`) | 31.25 tiles/s (3000 units over its 96-unit tile) | 0.35 s | 0.4 (the last 4.4 tiles) | 0.01 |
| Zoom (`glide_zoom_speed`, `glide_zoom_ramp`) | 3 zoom ranges a second (48 units/s here) | 0.25 s | 0.4 | 0.001 |
| Tilt (`glide_tilt_speed`, `glide_tilt_ramp`) | 400 degrees a second | 0.4 s | 0.25 | 0.005 |

A pan gets 90% of the way across 4 tiles in 0.43 s, 17 in 0.70 s and 39 in 1.32 s, and settles in about
0.7, 1.2 and 1.9 s. The speed is in tiles, not scaled with the zoom, as XCOM 2's is not, so a glide takes
as long however far in the camera is, and shows faster on screen zoomed in: at most 41 px a frame at
1280 x 720 zoomed all the way in, 16 at the maps' starting zoom, 11 all the way out.

What glides: `focus_on()` (the selected squad member as the player's turn starts, and the gamepad
cursor's jumps: L3, a new selection, the next target lined up), `bring_into_view()`, which goes through
`focus_on()` when it has to move, `follow()`, and `frame()` / `release_frame()` for a reaction window and
an enemy's shot, which glide the pivot, the distance and the pitch together. The pitch always glides,
since only the game tilts it; the distance glides when framing or unframing moved it, and eases when the
player zooms. A `focus_on()` of the spot the camera is on its way to already, gliding or easing, is left
to it, which is what keeps a gamepad stick step easing when it lands the cursor on a target that the
action then lines up, snapping the cursor to it: the cursor sends the camera (`pan_to()`) before it tells
the action it moved. The player panning or dragging mid-glide takes the camera back (`_take_back()`):
the glide stops where it has got to, anything followed is let go, and the pan goes on from there; the
wheel or the right stick takes the distance back the same way. A stick step of the cursor during a glide
glides on to the cursor's tile rather than stopping it, so a step right after a jump goes on smoothly.

**In view.** A unit is in view when its feet and the top of its head (two cells up,
`CameraRig.standing(feet)`) are inside the framing margins (`frame_margin_x` and `frame_margin_top` 0.8
of the way to the edge, `frame_margin_bottom` 0.55, for the squad panel and action bar), worked out as
framing is: `_distance_to_fit()` says how far back the camera would have to be to hold them, against how
far back it is (`_holds()`). Tested against the view now, it is `is_in_view(points)` (`has_in_view(unit)`
for a unit); tested against the view the camera is settling on (`_pivot`, the distance and pitch it is
going to), `will_be_in_view(points)`, which decides whether to move at all.

**How far it sees.** The scenery ring around a combat map is deep enough to hide its outer edge from the
camera zoomed all the way out (`far_distance` at `view_pitch`) and from the reaction view as far back as
it goes (`max_frame_distance` at `Reactions.camera_pitch`, 62 degrees), and no further (`Docs/LEVELS.md`,
"Scenery"). The player's zoom stops at the first. A framed view looking down no more steeply than
`view_pitch`, as an enemy's shot is, goes no further back than `far_distance`, and a steeper one, the
reaction view, may go to `max_frame_distance` (`_furthest_frame()`, which `frame()` and the wheel while
framed both keep to). Rendered with the sky turned magenta, the pivot at the middle of each edge of the
pan bounds and the camera turned through 15 headings facing out, 60 views in all, the sky shows past the
ring in none of them at 22 and 55 degrees or at 28 and 62, but in 32 at 25 and 55 degrees and in 40 at
28 and 55, which an enemy's shot could be framed at before the cap.

**The enemies' turn.** Before an enemy acts, `TurnManager._bring_into_view()` has
`CameraRig.bring_into_view()` glide to it, unless the view the camera is settling on holds it already,
and waits a frame at a time until the view now holds it, the camera stops gliding (arrived, or taken
back by the player) or the unit is gone. That is XCOM 2's `X2Action_CameraLookAt` with
`BlockUntilActorOnScreen`, which waits for the camera's `HasArrived`: set once the look-at point is
inside its tether, not once it is centred. The turn then pauses `enemy_action_pause` (0.35 s) and the
enemy acts while the camera finishes settling. Its first action is chosen before the camera moves
(`TurnManager._next_action()`), and a turn that opens with a shot skips this: the shot's framing (below)
has the enemy in it, so it brings the enemy into view in one move, where bringing it into view first
would send the camera toward the enemy and then off to the shot. The same pause comes once the shot's
framing has them in view, before the shot. Nothing the AI reads changes while the camera moves, and it
draws nothing at random, so choosing early changes nothing it does.

Each walk is followed as XCOM 2's `X2Camera_FollowMovingUnit` follows one: `TurnManager._move_enemy()`
calls `CameraRig.follow(enemy, points)` as the walk starts and `stop_following()` once it is over. If
every point of the way, from where the enemy stands, head and all, is in the view the camera is settling
on, the camera does not move (XCOM 2's `SkipIfPathAlreadyInSafeZone`; a 2016 change widened its
`TetherScreenPercentage` to "roughly the edges of the screen" for exactly that). Otherwise it glides
each frame after the point `follow_lead` (1) tiles further along the way than the enemy
(`_ahead_on_path()`; XCOM 2's `TilesToPlaceCameraAheadOfUnit`), which stops at the way's end, so the
camera ends on the last tile. At walking speed (5 tiles a second) the glide's brake keeps it about 0.7
tiles behind that point, so the walker sits a little behind the middle of the screen. The stretch of the
way the walker is on only moves forward, so a way that doubles back is never read from the wrong
stretch. A framed view holds the camera over a follow: the follow waits while `frame()` holds it, and a
reaction view let go mid-walk hands the camera back to it.

A squad member falling on the enemies' turn moves the selection on; with the gamepad the cursor goes to
the new selection, but the camera follows it there only on the player's turn
(`ActionController._put_cursor_on_selected()`), so it stays with the enemies.

**The reaction view** (`Reactions`, see `CLAUDE.md`'s "Enemies walk through `Reactions.walk()`") is
framed once, as a window opens: `Reactions._frame_view()` frames the mover where it is, the rest of its
walk, and everyone ready to react (on overwatch, holding their reaction, with a round and a key to fire
them) who will see it on a tile of the rest of the walk (`_watchers()`, through `LineOfSight.watches()`,
the test `_find_offers()` makes as the mover reaches each tile), at `Reactions.camera_pitch` (62),
pulled back to fit, no nearer than `min_frame_distance` and no further than `max_frame_distance`. So the
camera has no need to move again as the enemy goes, nor as prompts come and go. Every point framed is
kept in a set (`_framed`), and the view is framed again only when a point is added, so it only ever
widens: for someone with a shot it did not foresee, cover having been shot away on the way, say. Once
the window has been shut `Reactions.release_delay` (0.5 s) with the walk still going
(`_release_when_shut()`), or the walk is over, `release_view()` lets it go: `CameraRig.release_frame()`
glides back to the point ahead of the walker if the walk is followed, or else to where the camera looked
before it took up the view, and gives the zoom and the pitch back. The delay keeps a tile out of sight
from sending the camera away and straight back; a window that opens again within it keeps the view, and
only widens it. `TurnManager` still calls `release_view()` at the end of each enemy's turn, which by
then finds nothing to let go.

**An enemy's shot** is shown as XCOM 2 frames an ability's shooter and target (its `X2Camera_Midpoint`).
Before `ShotPlayback` plays it, `TurnManager._show_shot()` takes the shooter where it stands and where
it steps out to (`Shot.from`), and the target where it stands and where it is seen leaning out
(`Shot.seen_at`), feet and heads. If the view the camera is settling on holds them all, nothing moves (a
shot at point blank never does); otherwise it frames them (`frame(points, view_pitch, false)`): over
their middle, at the usual pitch, as near as the player's zoom or pulled back as far as it must be, up to
`far_distance` (see "How far it sees"). The shot waits until they are all in view or the glide is over,
then plays, and the frame is let go where it is (`release_frame(false)`): the zoom comes back and the
camera stays over the shot, since whatever it shows next would only undo a glide back. The squad's
reaction shots are inside the reaction view already, and their shots on their own turn are the player's
to look at, so neither is framed.

**Measured** on BoundaryMap's first enemy turn, all four enemies, nobody on overwatch, at the starting
zoom: before the glide, 15 camera moves in 16.6 s (one per enemy, one per hop of each walk, one back to
the squad), the long ones at up to 428 tiles/s in their first frame (the middle of the view 242 px in
that one frame, 724 zoomed all the way in), every move 90% done in 12 frames whatever its length, and
the walker yanked backwards on screen at the start of every hop. With it, 5 moves in 17.75 s, each
starting at 1.5 tiles/s and never above 31.25, the middle of the view at most 16 px a frame, and no
walker ever off screen. Turns take longer: 1.1 s at the starting zoom, 3 s zoomed all the way in, where
enemies come into view later. Framing that turn's two shots as well (below) makes it 7 moves in 18.85 s.

Over three enemy turns with the whole squad on overwatch and nobody answering, every one of 13 reaction
windows moved the camera once at most, as it opened, and held one framing distance throughout, where
the first turn's two windows had made 9 moves between them, their distance pumping from 21.7 to 17.2
and out to 19.3; with 0 pressed each time, the view was let go 0.5 s after each window closed, unless
another opened first. Of the 8 enemy shots over three turns with nobody on overwatch, 3 came with the
shooter and the target not both in view, and all three were framed, as was one more with both in view
but not, from head to foot, inside the margins; the 4 at close range needed nothing, every shot was in
view as it went off, and none needed the camera further back than the player's zoom. An enemy out of
view whose turn opens with a long shot (four such set-ups, one action each, 16 to 19 tiles from its
target) had the camera travel about three times as far as it ended up from where it started (24.9
tiles for 8.5) and the shot show 1.7 s into the turn, when the turn brought the enemy into view first;
framing the shot alone, it travels the straight 8.5 and the shot shows at 0.6 s.

## Probing it

The camera is probed headless with `--fixed-fps 60`, as the rest is (`CLAUDE.md`'s Verification). Set
`root.size = Vector2i(1280, 720)` and await a frame before anything else: headless, the root is square
(1280 x 1280), and every in-view test, framing distance and `Camera3D.unproject_position()` is off until
it has the game's shape. Settle the rig where it should start (`rig.focus_on(point)`, then
`rig._current_pivot = rig._pivot`), start the enemies' turn with `turn_manager.end_player_turn()`, not
awaited, and log a frame at a time until `turn_manager.side` is 0 again: `rig._pivot` is where the
camera is going and `_current_pivot`, `_current_distance` and `_current_pitch` where it is,
`is_gliding()`, `_follow_unit` (check it with `is_instance_valid()`) and `_framing` what it is doing,
`has_in_view(unit)` and `is_in_view(points)` whether it holds them, and the camera's
`unproject_position()` of a unit's head where that is on screen. The pivot's speed a frame and how far
the ground at the middle of the screen moves on screen in one (`unproject_position()` of last frame's
pivot) say how smooth it is better than pictures do. A glide sent somewhere else mid-way never stops,
so count where the camera is sent (`_pivot` changing) and how far it travels against how far it ends up
from where it started, not runs of motion. The whole squad on overwatch (`member.overwatching = true`
before the turn) opens reaction windows; `reactions._passed.merge(reactions._offers)` then
`reactions._set_open(false)` is pressing 0; `reactions._viewing` says whether the reaction view holds
the camera, `_framed` what it has framed and `_shut_for` how long the window has been shut. The
overlay's `_incoming` and `_aiming` are true while an enemy's sight line shows, `_from` and `_to` its
ends. For more than one enemy turn, set overwatch again and call `end_player_turn()` again each time
`side` comes back to 0: the enemies close in, and shoot more as the turns go on (on BoundaryMap two
shoot on the first). A turn that opens with a shot is set up by giving one enemy `actions_per_turn` 1
and a shot from out of view, and played with `turn_manager._take_enemy_turn(enemy)`. An
`InputEventJoypadMotion` past `InputDevice.STICK_THRESHOLD` (0.5) switches to the gamepad and steps the
cursor in the same frame; `Input.action_press(&"camera_pan_right")` pans as D does.

`frame()` points far apart up and down the screen to see the limit (`_frame_distance` stops at
`far_distance` at `view_pitch`, at `max_frame_distance` at 62 degrees), and `_step_zoom(1.0)` while
framed to see the wheel stop there too. Whether a view sees past the scenery is seen in a window: turn
the `WorldEnvironment`'s background to flat magenta (`background_mode` `BG_COLOR`), hide the map's
`CanvasLayer`s, stop the rig's `_process` and pose it by its own transform (`position`,
`rotation_degrees`, the `Camera3D`'s `position.z`), then count magenta pixels in the top two rows of the
root's texture after two `RenderingServer.frame_post_draw`s: the sky reaches the top row first, and the
worst headings are about 55 degrees either side of facing an edge. To see the camera as the player does,
render in a window and save the root's texture on `RenderingServer.frame_post_draw`.

## Known gaps

- The reaction view frames, as it opens, everyone who will get a shot somewhere along the rest of the
  walk, so it can be wider at first than the shots on offer need. It is worked out from sight as it is
  then: cover shot away later in the window widens it, a glide in the middle of the player's choice.
- A window opening mid-walk glides the camera across to the framed view, the walker sliding over the
  screen as it goes (up to 18 px a frame on BoundaryMap, 54 before the glide).
- A shooter and target too far apart to fit by `far_distance` are framed as far back as that, some of
  them outside the margins; so is a reaction view too wide for `max_frame_distance`.
- Only a turn's first shot is shown in one move: an enemy that walks and then shoots is followed, or
  left in view, and its shot framed after, as the two actions they are.
- The first stick step after switching from the mouse to the gamepad eases the camera from wherever the
  mouse left it to the cursor, which can be across the map, at the player's own rate, not a glide.
- The player taking the camera back stops a glide dead, from up to 31 tiles a second to the pan's speed
  in one frame. A mouse left at the edge of the screen pans, so on the enemies' turn it takes the camera
  back every frame and the camera never goes to them.
- Nothing the game does turns the camera, so the yaw never glides.
- The follow's lead is a flat tile; XCOM 2's grows as its camera pulls back.
- A unit that cannot be held inside the margins at all (none can yet) is glided to and centred, and the
  turn goes on once the glide is over.

Decided without asking the user: the glide is not scaled with the zoom (scaled from the starting zoom, a
pan across the map zoomed all the way in would take over 3 s); an enemy counts as arrived on once it is
inside the framing margins, as XCOM 2 waits, not once centred; the framing margins are the in-view zone
for both tests, tighter than XCOM 2's screen edges, the HUD running along the bottom; the follow's lead is
a flat tile; the cursor's jumps glide while its stick steps keep the player's rate; the player panning
stops a glide dead and lets go of a follow; a squad member falling on the enemies' turn no longer moves
the camera with the gamepad. The reaction view and the enemy's shot were the user's two fixes after
those, as offered; within them, also without asking: the view frames everyone who will see the mover
along the rest of its walk, not only those with a shot as it opens, and afterwards only widens; it is
let go half a second after the window shuts (`release_delay`), back to the walker if the walk is
followed; an enemy's shot is framed at the usual pitch, no nearer than the player's zoom, its step-out
and lean tiles included, waits until it is in view, and is let go where it is; the squad's own shots
are not framed. Then, the user asking for a turn that opens with a shot to move the camera once: its
first action is chosen before the camera moves, and the pause an enemy gets as the camera arrives on it
is kept, coming before that shot. Found in the documentation pass the user asked for after, and fixed,
the scenery's rule being older: an enemy's shot could be framed back to `max_frame_distance` at the
usual pitch, and the wheel take a frame there, past what the ring hides. The limit chosen is the zoom's
own, `far_distance`, for any frame no steeper than `view_pitch`, and `max_frame_distance` for a steeper
one, rather than a furthest worked out for each pitch, which would have moved the reaction view's 28.
