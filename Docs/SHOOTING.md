# Shooting

Shots and strikes in full: how a target is seen (on its own tile, or on one it could lean out to),
how a shot or a strike is lined up and confirmed, how it is settled as it is fired and lands as it
arrives, and where its round goes: `LineOfSight`, `HitChance`, `Ballistics`, `ShotPlayback`,
`ShootAction`, `StrikeAction`, and `Unit.shoot_at()` and `strike()`. It was split out of
`CLAUDE.md`, which keeps a summary, the rules that must not drift (sight, cover, flanking, the hit
chance, where rounds go) and the harness they are checked on (`Scenes/LineOfSightTest.tscn`,
Verification). The figure's side of it, aiming and leaning out, is `ANIMATIONS.md`'s (9.13); reaction
fire, which takes the same path once the odds are worked out, is `Reactions`'. A section named here
that is not in this file (Gotchas, Verification, Known gaps, another subsystem's notes) is
`CLAUDE.md`'s.

## How it works

A shot goes through four hands. `LineOfSight` finds it (`find_shots()`: from where the shooter can
fire, a step out of its cover included, to where the target can be seen) as a `Shot`;
`HitChance.for_shot()` works out its odds, once, as it is lined up; the player confirms it; and
`Unit.shoot_at()` settles it, `Ballistics` deciding where the round goes. Shots not taken from the
action bar, reaction fire and the enemies', are played through `ShotPlayback` (aim, step out,
`shoot_at()`, step back) from the same odds on. A strike is a shot at arm's length, with nothing
flying and no terrain touched.

### Seen where it leans out

**A target is seen where it leans out, too.** XCOM 2's rule (its visibility record traces "5 source
locations (default + 4 peeks) to 5 target locations (default + 4 peeks)"): the tiles a unit behind
cover can lean out to shoot from (`LineOfSight.lean_tiles()`, which `firing_positions()` adds to its
own tile) are also tiles it can be seen on. `find_shot()` first looks for a firing position that sees
the target's own tile, as it always did, so every shot there was before is unchanged. Only when none
does, it takes the first firing position (the shooter's own tile first) that sees one of the target's
lean tiles, and of those the nearest to it. Such a shot has `Shot.seen_at` on that tile and
`Shot.leaning` true; its cover, flanking, distance and height are still the target's own tile's
against `Shot.from`, so a unit behind a pillar is shot at through Full Cover. Sight therefore runs
both ways: whoever can lean out and shoot can be shot back at. A reaction passes `leans` false
(`Reactions._find_offers`), since a target on the move leans nowhere (XCOM 2's
`bDisablePeeksOnMovement`), and `watched_tiles()` is as it was for the same reason. XCOM 2's other
exceptions (unalerted enemies, units that cannot take cover) have nothing to apply to here.

### Lined up and confirmed

**A shot or a strike is confirmed by a key, a click on the target, or the panel's tick.** Enter /
Space is as it was. `ShootAction` and `StrikeAction` also read a click on a unit, with either button
(`UnitAction.clicked_unit()`, over `is_click()`: left, `select_unit`, as the squad is selected; right,
`execute_action`, as Move is carried out), which reaches them through `handle_input()` once
`ActionController` has let clicks on the squad go to `PlayerSquad`. A click on the target lined up
fires or strikes; a click on another target only lines it up (`_click()`), so nothing is ever taken at
odds the player has not been shown; a click on anything else is left alone. While either is up, the
cursor is a hand over any of its targets (`UnitAction.hovered_unit()`, `point_at_target()`, checked
every frame, as the camera moves under a still mouse): `Input.set_default_cursor_shape()` is set only
when it changes, since setting it sends a mouse motion of its own, and is put back to the arrow as the
action ends, as the tree pauses and as it leaves the tree. The target panel (`TargetPanel`) has a tick
box beside the chance, the roster's `UI/black_tick.png` on a pale box filled with the menus' accent
under the mouse, shown only when `ShotOverlay.show_shot()` / `show_strike()` are told `confirmable`,
which only the two actions say: reaction fire playing out through `ShotPlayback` shows the panel
without it. Clicking it emits `TargetPanel.confirmed`, passed on as `ShotOverlay.confirmed`, which
both actions listen to; the one active and not busy takes its shot or strike. The box never takes the
keyboard (`FOCUS_NONE`), or Space would press it as well as reach the action, and the rest of the
panel lets the mouse through, so a target under it can still be clicked. Three calls were made without
asking the user: both mouse buttons, a click on another target lining it up rather than firing, and
the hand cursor. With the gamepad the box gives way to an A (`TargetPanel._confirm_glyph`, swapped on
`InputDevice.changed`), which A, being `confirm_action`, already did.

### Settled as it is fired, landing as it arrives

**A shot is settled when it is fired and lands when it arrives.** `Unit.shoot_at(shot, chance, grid,
show_rounds)` first has the shooter's figure take aim at the target's eye (turned to it, gun up: at
once if the shot was lined up with `aim_at()`, as `ShootAction` and `ShotPlayback` both do before
anything else), then rolls, then asks `Ballistics` for the round's `Path`: the sight line for a hit;
for a miss, XCOM 2's placement, an aim point on a ring around the target's body (or, `COVER_SHARE` of
the time, on the target's cover) traced with `CombatGrid.cast()` until something stops it or it leaves
the map. The figure kicks and flashes, and `Outcome.muzzle` says where its muzzle was, which
`ShotOverlay` draws the tracer from: only the drawing, as every path is still flown from the eye. For
a hit the target's figure then picks where the round is seen to land (`Path.wound`, `Docs/BLOOD.md`),
which the tracer is drawn to (`Path.drawn_to()`). It then awaits `show_rounds`
(`ShotOverlay.show_rounds`, which draws the tracer and returns as it lands), and only then damages the
target (or has it duck a miss), the muzzle as where the hit came from and the wound as where it
landed, and reports any terrain the round struck through `CombatGrid.strike()` as `terrain_struck`.
`shoot_at` is a coroutine; always `await` it. A step out walks with `keep_facing`, so the shooter
sidesteps out and back with its gun on the target.

`Ballistics` shoots at a leaning target where it leans to: a hit flies to the eye over `Shot.seen_at`,
which is the sight line, and a miss is aimed round the body there and kept clear of the target both
where it stands and where it leans; the cover a miss can be aimed at is still the cover beside its own
tile. The rest is for show. The target's figure leans out for as long as the shot is lined up, and
through the shot, as XCOM 2's targeted units hold their peek until the shooter is back in cover:
`Unit.lean_out(tile, watch, grid)`, called by `ShootAction` as the target is lined up, by
`ShotPlayback` as the shooter turns to it, and by `Unit.shoot_at()` itself, which waits until the
target `has_leaned_out()` before it rolls and, for a shot nobody lined up, has it lean back once the
round has landed. It leans from the cover standing square to the way it leans (of two, the one more
toward the shooter), turned to face that cover: `wall_lean_*` at high cover, `crouch_lean_*` on one
knee at low, its head turned to the shooter. `lean_back()` waits for any flinch or duck to play out,
so the hit is seen landing on it out there, and is called off if it is leaned out again first, so it
never bobs back between two shots; walking, falling or readying anything stands it back at once.
`Unit.lean()` is how far out its head is (the lean's `reach` toward the tile), which `aim_point()`
adds, so the shooter's aim, the sight line, the reticle and the called result all follow the leaning
figure, and `Blood` looks for the figure there. A hit on it is drawn landing on the part of it that is
out (`Unit._wound_on()`: a wound its cover hides from the muzzle is picked again, on the figure's own
generator). Only the figure moves: the unit never leaves its tile, so coins, reactions and everything
else that reads `tile_at()` see nothing.

### A strike

**Strike is a shot at arm's length.** `StrikeAction` is laid out as `ShootAction`: its targets are the
living enemies next to the unit, as `Tactics.is_next_to()` has it (the AI's point-blank range, so the
two cannot drift), nearest first; Tab / Shift+Tab cycle them, Enter / Space strikes (or a click, as
above), Ctrl opens the breakdown, and `ShotOverlay.show_strike()` draws the same line, reticle and
target panel (its status line reads "Melee" instead of the cover). It costs `StrikeAction.COST` (1, a
shot's) and is dimmed without an action left or an enemy next to the unit. The odds are
`HitChance.for_strike()`, worked out once as the target is lined up; `Unit.strike()` rolls them and
deals `Unit.melee_weapon`'s damage plus the striker's `Unit.strength` through `take_damage()`, so
defense comes off that sum as it does off a shot's damage. Nothing flies, and the blow touches no
terrain. Lining a target up has the figure square up to it with its sword out (`Unit.ready_strike()`;
a rifleman draws it off his back), and `Unit.strike()` is a coroutine: it plays the swing, rolls and
deals the damage at the swing's `impact` moment (`strike_sword`'s metadata), and returns then, so the
result is called as the blade lands; `StrikeAction` then awaits `Unit.recover()`, the follow-through,
before it completes. It is busy throughout, so a kill that wins the battle finds the action mid-play
and leaves it to be put away as it completes.

## Its scripts

`CLAUDE.md`'s Layout lists every script in a line or two; here are this subsystem's in full.

```
  Combat/
    LineOfSight.gd     cover, step-out (firing_positions(), lean_tiles()), find_shots() -> Shot (from / stepped_out:
                       where the shooter fires from; seen_at / leaning: where the target is seen, its own tile or
                       one it leans out to); find_shot(..., leans false) for a reaction; watched_tiles(), watches()
    HitChance.gd       the to-hit sum (Estimate + Term): for_shot(), for_strike() (melee); roll();
                       hunker_penalty() (HUNKER, 20, off a shot at a hunkered target its cover counts against)
    Ballistics.gd      where a round goes: hits along the sight line, XCOM 2 misses -> Path (wound: where on the
                       target a hit is drawn landing, for show; drawn_to()); a target seen leaning out is shot at
                       where it leans to
    ShotPlayback.gd    shots not taken from the action bar: aim, step out, show, shoot_at(), step back; the target
                       leaning out meanwhile if that is where the shot sees it
```

## Probing it

The sight and shot rules are checked on `Scenes/LineOfSightTest.tscn`, the harness `CLAUDE.md`'s
Verification describes: its lanes, and how its crates break as a probe shoots there.

The pillar and wall lanes show a target seen leaning out, from the other side: Enemy1 to Enemy5 see
Player3, and Enemy2 to Enemy4 see Player4, only where they lean out, through Full Cover (35 to 40%),
and Player5 sees Enemy2 only leaning out of its half cover, past the wall lane. To watch a squad
member take such a shot, swap Player3 and Enemy3's positions in a probe (`global_position`), select
Player3, activate Shoot and cycle to Enemy3 (`ShootAction._cycle()`): `current_shot()` has `leaning`
and `seen_at`, `Enemy3.is_leaning()` and `model._base` say what its figure is doing
(`wall_lean_right_rifle`), and `ShotPlayback.new(grid, overlay).play(enemy, shot, estimate)` plays one
the other way. The rule itself is cheap to check exhaustively: teleport two units to random pairs of
tiles and compare `find_shot(a, b)` with `find_shot(b, a)` and with `find_shot(a, b, false)`, which is
the rule as it was before a target could be seen leaning.

A shot from the action bar is driven as the player takes it: select the shooter
(`squad.select(unit)`), `controller.activate()` the `Shoot` action, cycle its targets
(`_cycle(1)`) until `current_shot()` is the one wanted, and `_fire()`; its `_estimate` is the
`HitChance.Estimate` it rolls (`terms`, `chance`), which a probe can set to 100 to see a hit. A
strike is the same through `StrikeAction` (`_strike()`), with its target next to the striker and a
melee weapon given it (`unit.melee_weapon`, and in its `equipment`). `ANIMATIONS.md` (14.3) has a
probe that renders both as they play.

## Known gaps

- A target leans out of its cover only for a shot that sees it leaning, while that shot is lined up or
  played. XCOM 2 has more: a unit in cover leans out for a look every few seconds while it has enemies
  in sight, and one that is targeted holds its peek even when it is seen where it stands. Neither is
  here. Nothing but the figure says a target is leaning: the target panel reads its cover alone, and
  the tile it leans out to is not marked as the shooter's step-out tile is.
- The lean is the base pose cross-fading (0.22 s), so the figure slides along its cover to the edge
  rather than stepping there, and its head keeps the tilt of its chest. It leans out about three
  quarters of a tile, which from straight in front of its cover at long range shows its head, a
  shoulder and half its chest past the edge and no more; a hit is drawn landing on what shows. The
  debris capsule stays on its tile; the click body goes out with the figure.
- The enemy AI gains the shots the rule gives it and nothing else: `Tactics.advance()` still walks
  toward the nearest foe, and nothing weighs where a move would leave it seen leaning out.
