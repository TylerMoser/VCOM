# Grenades

Throwing a grenade in full: `ThrowGrenadeAction`, `Throwing` (the arc and the blast), `Unit.throw_at()`,
`ThrownGrenade` and `Explosion`. It was split out of `CLAUDE.md`, which keeps a summary and the rules
that must not drift ("A throw is never rolled, and a blocked arc is never thrown", "The blast is
what the preview shows"). What a blast breaks and throws about is `Docs/DESTRUCTION.md`'s, and the
throw's clips `ANIMATIONS.md`'s. A section named here that is not in this file (Gotchas,
Verification, Known gaps, another subsystem's notes) is `CLAUDE.md`'s.

## How it works

**A throw is planned, then flown.** `ThrowGrenadeAction` aims with the mouse, as Move previews: it
follows the tile under the cursor every frame (`ActionController.pointed_tile()`, the tile cursor's
with the gamepad, where A throws), and a click with either button (`UnitAction.is_click()`, as a
shot's target is clicked; the left as well as the right at the user's request) or Enter / Space throws
there; there are no targets to Tab through. A left click on a squad member's figure is the one click
it never sees: `ActionController` hands it to `PlayerSquad`, which selects them, as during any action,
so a throw at a tile a squad member stands on is a right click or the keys. `begin()` works out every
throw the unit can make (`Throwing.throws_for()`: tiles within `Throwing.RANGE` whose arc is clear,
about 16 ms on BoundaryMap) and tints them (`throw_range`); the tile under the cursor gets the
`throw_blast` layer and `ShotOverlay.show_throw()`: the arc's points, a cross where a blocked arc
stops, and an outlined bracket with the damage (`Unit.damage_from()`) on everyone `Throwing.caught()`
names, gold on the squad. A `Throwing.Throw` is a parabola from `RELEASE_HEIGHT` over the thrower's
floor to the centre of the target tile's lower cell, rising `ARC_RISE` per tile (at least
`ARC_MIN_HEIGHT`) above the straight line, cut into `TRACE_STEP` pieces each cast through the grid
with `CombatGrid.cast()`; the first solid cell any piece meets blocks it, and `points` then ends
there. Those constants decide what a throw gets over (half cover in front of the target from the full
range, the thrower's own full cover; never the tile right behind full cover), so check them with a
probe if they change. The throw costs `ThrowGrenadeAction.COST` (1) and goes through
`Unit.throw_at()`. While the action is up the figure holds a grenade ready, turned to the tile under
the cursor (`Unit.ready_throw()`). The throw winds up and lets go at its `release` moment, where the
grenade is used up as it leaves the hand; `_fly` gets where the hand was and shows a `ThrownGrenade`
from there, easing on to the arc in its first `EASE_IN` of the flight (timed as a fall under
`ThrownGrenade.GRAVITY`), and an `Explosion` where it goes off, and the blast lands as the grenade
arrives: `take_damage()` on everyone caught, then `CombatGrid.blast()` with the cube's cells. Results
are called together (`ShotOverlay.flash_results()`, over the heads). The action stays busy
`AFTERMATH_SECONDS` and until no unit is moving, so anyone the blast dropped has landed before the
next throw is worked out. The 3D effects go under `effects_path`, the map root.

A grenade is a `Grenade` (`Items/Grenade.gd`, a `BattleItem`): its `damage`, `blast_size` (odd, tiles
across), `environment_damage` and `blast_force`. `FragGrenade.tres` is the one there is: 5 damage, 3
tiles across.

## Its scripts

`CLAUDE.md`'s Layout lists every script in a line or two; here are this subsystem's in full.

```
  Combat/
    Throwing.gd        RANGE (10, every throw's); plan() -> Throw (the arc, blocked or not), throws_for(unit);
                       the blast: blast_cells(), is_caught(), caught(), blast_tiles()
    ThrownGrenade.gd   a grenade in flight along a Throw's arc, from the thrower's hand, as the grenade's
                       model tumbling about its middle; for show; frees itself as it arrives
    Explosion.gd       a grenade going off: fireball, flash, smoke, for show; go_off(), frees itself
```

## Probing it

A throw is probed headless, as the rest is (`CLAUDE.md`'s Verification). The rules need no action:
`Throwing.new(grid)` plans a throw from one tile at another (`plan(from, target)`, a `Throw`: its
arc's `points`, `is_clear()`, and `blocked`, the `CombatGrid.RayHit` that stops it), lists every
throw a unit can make by the tile it is thrown at (`throws_for(unit)`), and says whom a blast catches
(`caught(target, size)`); `Throwing.blast_cells(target, size)` is the cells it takes. To throw, give
the unit a grenade (`unit.equipment.append(grenade); unit.grenade = grenade; unit._dress()`),
activate `ThrowGrenade`, stop its `_process` (it follows the real cursor), then `_aim(tile)` (within
`Throwing.RANGE`) and `_throw_lined_up()`: the blast lands as the grenade arrives, and the action
stays busy until nobody is moving. After changing `RELEASE_HEIGHT`, `ARC_RISE`, `ARC_MIN_HEIGHT` or
`TRACE_STEP`, plan throws over half cover from the full range, out of the thrower's own full cover,
and at the tile right behind full cover, which must stay out of reach.

## Known gaps

- There is one kind of grenade, and a unit throws the first it carries: with several kinds there is no
  way yet to pick which. Grenades do not bounce or roll, and a blocked arc is simply not thrown; walls
  inside a blast shelter nobody. Only the player sees the throw: no reaction or camera move follows
  it.
- `Throwing.throws_for()` plans every tile in range each time Throw Grenade begins, about 16 ms on
  BoundaryMap; a bigger range or map may want it spread over frames.
