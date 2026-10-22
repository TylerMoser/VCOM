# Hunker Down

Hunkering down in full: `HunkerDownAction`, `Unit.hunkered`, the Hunkered term of the hit chance,
and how the figure and the HUD show it. It was split out of `CLAUDE.md`, which keeps a summary,
where in `Unit` a move ends it, and the rule that must not drift ("Hunkering down adds to cover,
never stands in for it"). A section named here that is not in this file (Gotchas, Verification,
Known gaps, another subsystem's notes) is `CLAUDE.md`'s.

## How it works

**Hunkering down is a state on the unit that one term of the hit chance reads.** `HunkerDownAction`
needs no item, so every unit has it, but it is only available in cover
(`HunkerDownAction.is_in_cover()`: `LineOfSight.cover_at()` of the unit's tile not empty, any side,
either height), with an action left and not hunkered already; out of cover its button is dimmed. Like
Overwatch it shows nothing on the map while it is up, and Enter / Space spends `HunkerDownAction.COST`
(1, the user's call, in place of the rest of the turn it first took) and sets `Unit.hunkered`. The
unit carries on with its turn; shooting, striking, throwing and overwatch leave it hunkered. Moving
ends it, also the user's call: `Unit.start_walk()` clears it for every walk but one that keeps its
facing, which is only ever a step out of cover to shoot and back (`ShootAction`, `ShotPlayback`), and
`Unit.drop_to()` clears it too, since falling when the ground goes is moving (assumed, not asked). So
the rule is in `Unit`, where every move goes through, not in `MoveAction`, and a new kind of walk that
should not stand a unit up has to keep its facing or say so there. `Unit.start_turn()` clears it as
well, as it does overwatch, and a squad member's turn starts with the player's, so short of a move it
lasts through the enemies' turn until the player's next. While it holds, `HitChance.for_shot()` adds a
**Hunkered** term of `-HitChance.HUNKER` (20) just after **Cover**, whenever `Shot.cover` is not
`NONE` (`HitChance.hunker_penalty()`): flanked, or with its cover shot away, a hunkered unit gets
nothing for it. Every shot is lined up through `for_shot()` (the action bar's, reaction fire, the AI's
`Tactics`), so it counts everywhere, and the assault AI's best odds steer it to a target that is not
hunkered. Two calls were made without asking the user: melee counts no cover, so `for_strike()` counts
no hunkering either (no enemy strikes yet); and nothing is drawn on the map while it is lined up. With
nothing to Tab through and nothing to repeat, the action is put away once taken, as any action no
longer available is, so the player picks the next one from the bar. It is seen two ways:
`Unit.hunkered` sets `CharacterModel.hunkered`, which holds `hunker_<stance>` over every base pose but
a readied one (so the figure ducks low behind cover of either height, on overwatch too, rises to aim a
shot and ducks again, and still cheers a win) and a lean out of its cover: a shot that sees it only
leaning out is aimed where it leans, so the figure leans out there for it, hunkered or not, and ducks
again once it draws back (decided in the merge, not asked; the sight rule is untouched, so hunkering
never hides a unit), and `UnitCard` shows a `HunkerBadge`, a blue shield over its portrait's corner,
rather than another pip, which would widen the card.

`Unit.hunkered` emits `hunker_changed` as it changes, which the unit's `UnitCard` follows to show or
hide its badge.

## Probing it

Hunkering is probed headless, as the rest is (`CLAUDE.md`'s Verification). Stand a squad member in
cover (`HunkerDownAction.is_in_cover(unit, grid)` says whether it is), activate `HunkerDown` and send
Enter, or set `unit.hunkered` directly. Then line a shot up at it,
`HitChance.for_shot(shooter, LineOfSight.new(grid).find_shot(shooter, unit))`, and read the
estimate's `terms`: one labelled "Hunkered", worth `-HitChance.HUNKER`, while the shot's `cover` is
not `NONE`, and none once it is (a flanking shooter, or the cover shot away). A walk that does not
keep its facing (`unit.walk(points, seconds)`), a drop (`drop_to()`) and `unit.start_turn()` each
clear it. The figure's pose is `unit.model._base` (`hunker_rifle` with a rifle, behind cover of
either height).

## Known gaps

- The player never sees the Hunkered term at work: an enemy's shot shows its line but not its odds, so
  only the outcomes tell. Hunker Down marks nothing on the map while it is lined up, and the unit
  hunkers wherever it stands in cover, whichever way its cover faces.
