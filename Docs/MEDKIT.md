# Medkit

The medkit in full: `Medkit`, `UseMedkitAction`, `Unit.medkits` and `use_medkit()`, and the figure's
showing of it. It was split out of `CLAUDE.md`, which keeps a summary and the rule that must not
drift ("A medkit is never rolled, never used up, and heals only its user or an ally next to it"). A
section named here that is not in this file (Gotchas, Verification, Known gaps, another subsystem's
notes) is `CLAUDE.md`'s.

## How it works

**A medkit heals an ally next to the unit, or the unit itself, once a battle for each one carried,
and the squad members beside its carrier can draw on its uses.** `Medkit.tres` is a
`Medkit` (`BattleItem`, tagged `medkit`, `heal` 4, price 10, one in `Village1Market.tres`'s stock), so it
goes in an item slot and gives `UseMedkitAction`. It is never used up, unlike a grenade: what a battle
spends is `Unit.medkits`, the `Medkit`s the unit can still use, filled from its equipment as it enters
the map (one per medkit carried, so two give two uses) and popped by `Unit.use_medkit()`; the item stays
in `Unit.equipment`, on the figure's belt and on the character, and the next battle fills the list
again. Nothing is kept on the character (the user's: "only once per mission, per Medkit given to a
character"). The action is laid out as `StrikeAction` (the user's: "similarly to how a character with a
melee weapon chooses the target"): its targets are the living allies in `ally_group` (`players`) that
`Unit.is_wounded()` (health short of `max_health`), next to the unit as `Tactics.is_next_to()` has it,
nearest first, then the unit itself if it is wounded (`UseMedkitAction._patients()`; the user's "let the
Medkit heal the character holding it as well"; last, so an ally beside comes up first, as my call); Tab /
Shift+Tab, LB / RB and the tile cursor cycle them (the cursor on the unit's own tile lines itself up);
Enter / Space, A, a click on the one lined up (either button) or the panel's tick heals; a click on another
lines it up. It costs `UseMedkitAction.COST` (1) and is available with a use left, an action left and
someone to treat: itself wounded, or a wounded ally beside. `ShotOverlay.show_heal()` draws a strike's line, reticle and panel in green
(`TargetPanel.bind_heal()`: the ally's health now and after, and "+N HP" where the odds go, with no
breakdown, so the prompts drop LT's row: `UnitAction.shows_odds()`). `Unit.use_medkit(target)` is the
single place one is used: it spends the use, has the figure play `CharacterModel.use_medkit()` (turn to
the ally, the medkit off the belt and held out, returning at the clip's `apply`; on itself, `Unit._chest_of()`
passes null and the figure keeps its facing and presses the medkit to its own middle,
`use_medkit_self`), then
`target.heal(kit.heal)`: `Unit.heal()` adds to `health`, which clamps at `max_health`, so an ally 2 short
gains 2, and `PlayerSquad` writes the new health on the character's `wounds` as it does every change.
The action calls the gain over the ally in green (`ShotOverlay.flash_heal()`), waits `Unit.recover()`
and completes. Its button counts the uses left in its corner (`UnitAction.uses_left()`, drawn by
`ActionButton.uses`, -1 for the actions with no count). Since its targets are squad members, a left
click on one would select them (`PlayerSquad`); `ActionController` asks the active action first
(`UnitAction.takes_click_on()`), and Use Medkit takes a left click on any ally it offers, so selecting
one of them means Tab, the squad panel or putting the action away first; a left click on the unit
itself, while it is on offer, lines it up or heals it too. Lined up on itself, `ShotOverlay.show_heal()`
gets one point for both ends and draws no line, only the reticle and panel over it. Decided without
asking the user: one action; never above the most health; nothing rolled; the left click taken; the
count on the button; the green; the figure's showing of it, the kit on the belt and a clip over the
left arm alone; and, once healing itself was asked for, itself offered last, no line to itself, and
the figure pressing the kit to its own middle without turning. Enemies carry none, and their AI
never heals.

A use can be borrowed (the user's: "allow allies next to a character holding a Medkit to use the 'Use
Medkit' action, even if they are not equipped with one"; their own uses first; "it should still use 1
usage ... for the unit equipped with the Medkit", so a carrier whose last use a neighbour spent has none
left). Whose use the action spends is `UseMedkitAction.supplier(unit)`: the unit itself while its
`Unit.medkits` has one, else the first of `_lenders(unit)`, the living squad members in `ally_group`
next to it (`Tactics.is_next_to()`) with a use left, in the group's order, which is the squad's. So the
action is granted (`is_granted()`, overriding the tag test) to a carrier always and to anyone else only
while `_lenders()` has someone, and available only with a supplier; its targets are the unit's own, as
before (the wounded next to the *user*, and itself), and `uses_left()` counts the unit's uses and every
lender's. `_heal()` passes the supplier to `Unit.use_medkit(target, from)`, which pops `from.medkits`;
the user spends the action. The panel's status line names a borrowed kit ("Blue's Medkit · 7 → 10 HP",
`TargetPanel.bind_heal(..., kit)`, through `ShotOverlay.show_heal()`), and the figure, given the kit
(`CharacterModel.use_medkit(point, borrowed)`), makes a prop of it in the left hand from `take` to
`stow` (`_borrowed`, one of `_medkits` meanwhile) when it has none of its own on its belt, or takes its
own spent one otherwise. Decided without asking: the squad's order picking among several lenders, and
the player not choosing; the count on the button including the neighbours'; the panel's naming; a kit
appearing in the borrower's hand while the lender's figure does nothing and keeps its own on its belt;
and a carrier's spent use being taken before a neighbour's whenever it has one left, as "use their
usages first" reads.

## Probing it

A medkit is probed headless, as the rest is (`CLAUDE.md`'s Verification).
Buy and equip one before the map loads (`Campaign.buy(market, item)`,
`Campaign.equip(character, &"item_1", item)`), or give a unit uses directly (`unit.medkits.append()`,
with the item in `unit.equipment` too). Wound an ally by setting its `health` (its character's `wounds`
follow), stand it next to the medic, activate `UseMedkit` and send Enter, A, LB / RB, or call
`_click(unit)`; wound the medic too and it is offered last, or alone; stand a squad member with no
medkit next to the medic to borrow (`use.supplier(unit)`, `_lenders(unit)`; a Move's `changed` puts the
button on the bar, `ActionBar`'s button for it `visible`); `_targets` is what is on offer, `current_target()` what is lined up, and the overlay's
`_panel._chance_label.text` the "+N HP" shown. Mouse clicks on an ally have to be driven in a window,
where `Input.warp_mouse()` and a parsed `InputEventMouseButton` reach `ActionController` as a player's
would. The clips are seen with `PreviewAnimations.gd -- use_medkit --over <base pose>` (or
`use_medkit_self`), which moves the medkit to the hand between the clip's `take` and `stow` as the game
does; which one a figure plays is `model._tree.get(&"parameters/left_pick/current_state")`.

## Known gaps

- A medkit heals a fixed 4 HP, its user or an ally beside it; nothing heals out of battle but the road.
  A borrower cannot choose whose medkit to draw on (the first lender in the squad's order lends), the
  lender's figure takes no part, and the borrower's hand reaches to its own belt for a kit that is not
  there and appears in its hand; the button's count includes uses that walking away would lose.
  Its uses are counted only on the action's button, and a medkit's prop does not show whether it has
  been used. With Use Medkit up, a left click on a wounded ally beside the medic heals or lines them up
  rather than selecting them. Treating itself, the figure keeps facing whoever it last turned to. The medkit hangs at the back of the belt, so the left hand's reach for it
  falls a little short of a slot on the right, as a grenade's does at a throw.
