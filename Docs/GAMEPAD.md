# Gamepad

The gamepad in full: `InputDevice`, every binding, the `TileCursor`, `MapReticle`, and the prompts
(`ControlHints`, `ButtonGlyph`). It was split out of `CLAUDE.md`, which keeps a summary and the
convention that the game must stay playable with the pad alone (Conventions). A section named here
that is not in this file (Gotchas, Verification, Known gaps, another subsystem's notes) is
`CLAUDE.md`'s.

## How it works

**The gamepad plays everything, and the screen says how.** `InputDevice` (the autoload
`InputDevices`, first of the three so it is there when the pause menu's widgets ready) watches every
event in `_input`, paused or not, and sets the static `InputDevice.gamepad` to whichever was touched
last: a pad button, or a stick or trigger past `STICK_THRESHOLD`, for the gamepad; a key, a mouse
button, or the mouse moved `MOUSE_THRESHOLD` pixels in one event (the game moves it itself as it
changes the cursor's shape) for the keyboard and mouse. It hides the mouse while the gamepad is in
use and emits `changed`; everything else reads the static by the class's name, so a probe can still
name them (see Gotchas), and `InputDevice.watch()` connects to the signal. Being last to see `_input`,
it never sees an event another `_input` handled, so new gamepad handling goes in `_unhandled_input`.
The layout is an Xbox controller's (a Steam Deck's), bound in `project.godot` beside the keys: most
actions gained a button (A `confirm_action` and `ui_accept`, B `cancel_action`, `ui_cancel` and
`reaction_continue`, Menu `pause_menu`, View `end_turn`, LB / RB the squad and the targets, LT
`show_shot_details`, R3 `toggle_grid` in combat and `toggle_borders` on the new map (`BorderSwitch`,
whose state `MapReticle._rows()` words as "Hide borders" or "Show borders"), the right stick's x `camera_rotate_*`, the d-pad's up / down
`floor_up` / `floor_down` as PageUp / PageDown, and nothing else: the user's choice, so they change the floor on a
combat map with floors (`FloorSelector`, `Docs/CUTAWAY.md`) and do nothing anywhere else; the zoom actions,
`camera_zoom_*`, had them until the user had them taken off), and the pad has actions of its own: `cursor_*` (the left stick), `next_action` /
`previous_action` (d-pad right / left), `recenter` (L3), `camera_zoom_stick_*` (the right stick's y),
`menu_next_tab` / `menu_previous_tab` (RB / LB), `menu_next_subtab` / `menu_previous_subtab` (RT / LT),
and `reaction_fire` / `reaction_next` / `reaction_previous` (A, RB, LB). Godot's own `ui_*` already
had the d-pad and the left stick, so the menus' focus moves as with the arrow keys, and the Skills
page's trees, where they scroll, scroll to follow it (`Docs/SKILLS.md`).

Where the mouse points, the gamepad has a pointer of its own. In combat it is the `TileCursor`, which
`ActionController` makes and shows on the player's turn, not busy, with someone selected, and puts on
whoever is selected as the selection changes, the turn starts, or L3 is pressed: the left stick steps
it a tile at a time in eight ways relative to the camera (up the screen is away from it), finding
the tile nearest its height in the next column with one (a tile hidden with what the floor selector
has cut away counts as none, and a cursor left on one as it is cut comes down to the nearest shown in
its column), and the camera follows it: easing after a step,
as the player's own panning does, and gliding to wherever it is put, on the player's turn only
(`Docs/CAMERA.md`). Actions ask
`ActionController.pointed_tile()` (the cursor's tile with the gamepad, the mouse's tile without),
which is how Move previews and walks and Throw Grenade aims; `cursor_moved()` tells the active action
it moved, which is how Shoot and Strike line up the target the cursor reaches, and they snap the
cursor to each target `LB` / `RB` line up. A, being `confirm_action`, already fired, struck, threw,
went on overwatch, hunkered or reloaded; on Move it walks to the cursor, or selects the squad member standing
there. Switching device begins the active action again, so it starts from the new pointer. On the
world map it is the middle of the screen, where `MapReticle` draws a ring:
`InputDevice.pointer_position()` / `pointer_on_canvas()` give it, or the mouse, so `Destination`'s
hover, `Party`'s sending and `VillageMenu`'s opening take one path for both, and the map's camera
slides under it on the left stick and zooms toward it.

The prompts are `ControlHints` panels of rows, a `ButtonGlyph` or two and the words: down the right in
combat (`ActionController._show_hints()`, A's words from the active action's `confirm_hint()`, and a
"Floor" row for the d-pad's up / down on a map with floors) and on
the map (`MapReticle._rows()`), along the bottom of every `TabbedMenu` (`_gamepad_hints()`), shown only
with the gamepad. A menu's row is compact (`ControlHints.new(false, true)`), as its frame leaves it a
strip only 3.8% of the window high under it (`TabbedMenu.MARGIN`), 27 px at the least, a window 720
high: its glyphs are drawn 20 px high rather than 24 (`ButtonGlyph`'s height scales its pills, its
letters and the d-pad's arms, the edge staying 2 px), its words 14 px rather than 15, outlined in the
box's colour, as it has no box, and it is centred in the strip, clear of the frame and the window's
edge by 3.7 px at 720 (anchored at the strip's middle, growing every way, as `_collapse()` keeps it).
Done at the user's request, as the box ran over the frame's edge once the frame grew; the sizes, the
outline and dropping the box were not asked about.

A menu's A words come from the focused control: its own `gamepad_hint(focused)` if it
has one (a `SkillButton`: "Hold: Learn" while learnable, else nothing), else the first ancestor's that
says something (`ItemBrowser`'s action, the shops' "Choose", `SquadTab`'s "Tick" / "Untick"), else
"Hold" and the caption on a `HoldButton`, the text on any other button A presses, and nothing on a
toggle the focus alone selects. Elsewhere the HUD swaps a key for a glyph: the target panel's tick
becomes an A, the action bar gains d-pad arrows at its ends, and a reaction window picks out one
prompt with an A (`Reactions._focus`, first in squad order, moved by LB / RB) instead of numbering
them all. In the shops A on an item or a character goes on to the buy or hire button
(`PurchaseBar.focus_offer()`), to be held there. Decided without asking the user: the Xbox layout and
its labels; the d-pad choosing actions rather than moving the cursor (its up / down, which zoomed,
are the floor selector's alone since, at the user's asking); A on a squad member
with Move up selecting them; LB / RB, not the d-pad, moving a reaction's pick; `Menu` going to Start
on the squad menu; R3 switching the new map's borders, as it switches the tile grid in combat (the
user asked for `B` on the keyboard); and the cursor's marker, a pyramid bobbing over the tile, over a unit's head when
one stands there.

## Probing it

The gamepad is probed headless: `Input.parse_input_event()` of an `InputEventJoypadButton` (press,
a frame or two, release) or an `InputEventJoypadMotion` (an axis value, then 0 to let go) reaches the
game, the menus' focus included, as a key does, and switches `InputDevice.gamepad` on as a real pad
would; `InputDevice.use_gamepad(true)` switches it without an event. A stick held for a while steps
the tile cursor (`ActionController.cursor`, `current()`) on its repeat; `cursor.snap_to(tile)` puts
it anywhere. Read the prompts off the `ControlHints` panels (`ctrl.hints`, `MapReticle._hints`, a
menu's `_hints`): each row is an `HBoxContainer` whose last child is the words' `Label`. Hold a
`HoldButton` by pressing A on it and waiting past 2 s before letting go. To see the glyphs and the
cursor, render in a window as for any frame.

## Known gaps

- The gamepad's buttons are drawn and named as an Xbox controller's (a Steam Deck's), whatever pad is
  plugged in: a PlayStation or Nintendo pad works, as the same buttons by place, but its prompts name
  the Xbox ones. Nothing can be rebound, from the pad or the keyboard, and there is no rumble. It has
  only been driven by simulated input (`Input.parse_input_event()`), never a real pad or a Deck.
- The tile cursor steps whole tiles, and never on to one more than `HIGHEST_STEP` (4) cells above the
  one it is on: a tile atop a taller stack than that, which no map has, would be the mouse's alone.
  The world map's reticle does not snap to a village: it has to be put on the icon. The move path is
  drawn only a shade bluer than the range round it, with the pad as with the mouse.
- With the gamepad a reaction window's prompts lose their numbers (one has an A, the others none), so
  the numbers' order is not shown, and the combat prompts' ten rows (eleven on a map with floors) are
  a tall column: a player who knows the pad has no way to hide them.
- The d-pad's up / down do nothing on the world map nor on a combat map without floors; the camera
  zooms on the right stick alone, smoothly, with no step at a time on the pad.
- A menu's row of prompts is small, its glyphs' letters 11 px and Menu's and View's 9, and it fits
  under the frame only while `TabbedMenu.MARGIN.y` leaves 20 px or more there: a frame grown further,
  or rows of prompts made taller, would run them over its edge again.
