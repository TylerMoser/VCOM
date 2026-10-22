# Ammo

A gun's magazine in full: `Weapon.magazine` and `reload`, `Unit.rounds`, `ReloadAction`, the
enemies' reloads and the `AmmoIndicator`. It was split out of `CLAUDE.md`, which keeps a summary and
the rule that must not drift ("Every shot spends a round, in `Unit.shoot_at()`, as the trigger is
pulled"). The reload's clip is `ANIMATIONS.md`'s. A section named here that is not in this file
(Gotchas, Verification, Known gaps, another subsystem's notes) is `CLAUDE.md`'s.

## How it works

**A gun counts its rounds, and the unit holds them.** A `Weapon` has a `magazine` (shots, 5 for the
Rifle; 0 for a gun that never runs dry) and a `reload` (actions, 1 for the Rifle), both the user's
names for them; `has_magazine()` is a gun with one. The weapon stays a stateless shared resource: the
rounds left are `Unit.rounds`, filled to `magazine_size()` in `Unit._ready()`, so every battle starts
full and nothing is kept on the character (the user's call). `Unit.shoot_at()` takes one off as the
trigger is pulled, after the aim and before the roll, so every shot spends a round, hit or miss, the
squad's, the enemies' and reaction fire alike, and a magazine never goes below empty. Nothing lines a
shot up without a round: `Unit.can_fire()` (a round left, or a gun with no magazine) is asked by
`ShootAction.is_available()`, `OverwatchAction.is_available()`, `Reactions._find_offers()` and
`Tactics.shots_at()`, so an empty gun gets no Shoot, no Overwatch, no reaction prompt and no AI shot.
`ReloadAction` is offered to a gun with a magazine (`is_granted`) and available while
`Unit.can_reload()` (rounds short of full) with `reload_cost()` actions left, dimmed otherwise (the
user's: "when the magazine is full, the action is disabled"). Like Hunker Down it marks nothing on the
map; Enter / Space or A spends the cost and plays `Unit.reload()`, a coroutine that awaits the
figure's `CharacterModel.reload()` and fills the magazine at the clip's `seat` moment, then waits out
the clip (`Unit.recover()`) before completing; full again, it is put away. Nothing is called over the
unit's head: a "Reloaded" call came first and was taken out at the user's request, the animation being
enough for now. Enemies have magazines too (the user's call): the assault AI reloads first when empty
(`Tactics.reload(true)`), and with nothing to shoot and nowhere nearer to go tops up a part-spent one
(`Tactics.reload()`) before ending its turn; `TurnManager` carries an `AIAction.Kind.RELOAD` out as
the action does. `AmmoIndicator`, a HUD node in each map, draws the selected squad member's magazine
in the bottom-right corner, following `PlayerSquad.selection_changed` and the unit's `rounds_changed`;
`ActionController._place_hints()` stands the gamepad's prompt column on top of it while it shows (the
user's choice of corner). The action bar refreshes on the controller's `changed`, as for actions: a
round spent through an action, or on the enemies' turn, is caught then.

## Its scripts

`CLAUDE.md`'s Layout lists every script in a line or two; here is the indicator's in full (the
rounds themselves are `Unit.gd`'s, the gun's `Weapon.gd`'s, and the action is `ReloadAction.gd`).

```
  UI/
    AmmoIndicator.gd   HUD node, bottom-right: the selected squad member's magazine, a rectangle a round, filled
                       while loaded and hollow once fired, edged red when empty; hidden without a magazine
```

## Probing it

Ammo is probed headless, as the rest is (`CLAUDE.md`'s Verification): set `unit.rounds` directly (0 to
empty it), read `can_fire()` / `can_reload()` and the actions' `is_available()`, fire through
`ShootAction._fire()` and reload by activating `Reload` and sending Enter (or
`ReloadAction._reload()`); `HUD/AmmoIndicator`'s `_rounds` and `_magazine` are what it draws. An
enemy's choice is `unit.ai.choose_action(Tactics.new(unit, grid, squad.members))` (its `kind`), and
`TurnManager._take_enemy_turn(enemy)` plays a turn out (await it through a lambda, sharing a
dictionary flag, as `CLAUDE.md`'s Gotchas say of lambdas). The reload clip is seen with
`PreviewAnimations.gd -- reload_rifle --over <base pose>`.

## Known gaps

- There is one kind of magazine and no ammunition to buy, carry or run out of: a reload always fills
  it. Only the selected squad member's rounds are shown; an enemy's are seen only when it reloads, by
  the animation. The action bar dims and lights its buttons on the controller's `changed`, not on
  `Unit.rounds_changed`, so rounds set from outside an action (a probe) leave it stale until the next
  change. Reload has no key of its own: it is chosen on the bar (or the d-pad) and confirmed, as every
  action is. The reload is the rifle's alone (a pistol would need its own clip), and the rifle prop
  has no magazine to pull, so the hand mimes one. The assault AI tops up a part-spent magazine only
  when it has nothing else to do, never ahead of a fight.
