# Roster

The squad between battles and in them, in full: who the characters are (`Character`, `Roster`), how
each becomes a unit for a battle and what the battle writes back, experience and the gold a battle
pays, the six equipment slots, and items and the inventory: `Campaign.roster` and `inventory`,
`PlayerSquad`, and the Roster tab. It was split out of `CLAUDE.md`, which keeps a summary and the
rules a change must keep (the rules read the unit, never the character; every item in the inventory
or in one slot). The skills a character learns are `Docs/SKILLS.md`'s, and the hiring boards and
markets `Docs/CAMPAIGN.md`'s. A section named here that is not in this file (Gotchas, Verification,
Known gaps, another subsystem's notes) is `CLAUDE.md`'s.

## How it works

### Characters, and the units they become

**Squad units are roster characters, spawned for each battle.** A `Character`
(`Resources/Characters/*.tres`) is who someone is between battles. `Campaign.roster` is a copy of
`Resources/StartingRoster.tres` whose list is its own but whose characters are the loaded `.tres`. A
combat map has no squad of its own: it has `SquadStart` markers under a `SquadStarts` node, and
`PlayerSquad` (its `starts_path`) spawns a `Scenes/SquadUnit.tscn` (a `Unit` in `players` with a
`Model`) on the tile under each, for each character `Campaign.squad(markers.size())` sends: those
chosen on the `SquadMenu`, in roster order. It sets `Unit.character` before adding the unit, then
gathers `players`, so the squad panel, the reaction keys and everything else reading
`PlayerSquad.members` follow roster order. It does this in its own `_ready`, which runs after
`CombatGrid`'s (for `tile_at`) and before anything that reads the members. A marker's order among its
siblings is its number; in the editor it draws an orange square on the tile it counts as over, and
nothing in game. So they are linked: a unit takes its `display_name`, colour and the character's stats
(`max_health`, `defense`, `move_range`, `aim`, `melee_accuracy`, `strength`, `evasion`) from its
character in `_ready` (painting its figure). Each is `Character.total(stat)`, not the character's own
property: their own with what their learned skills add (`Docs/SKILLS.md`) and, for defense, their
armor's (`Character.total_defense` is `total(&"defense")`). They are copied once, when the unit enters
the map: the rules read the unit, never the character. The unit's other stats (actions, sight, height
bonus, distance penalty) are still its own, set in `SquadUnit.tscn`. A stat that should differ per
character moves to `Character`, gets copied in `Unit._take_character()` through `total()`, gets a row
in `DetailsPage.STATS`, and a name in `StatBonus`'s list, so a skill can add to it.
`Character.experience` (out of `Character.EXPERIENCE_TO_LEVEL`, 100) is the character's alone and
never copied to the unit. It only goes up through `Character.gain_experience()`, where every 100
becomes a `skill_points` and the rest carries over (97 + 10 is 7 and a point; a big award gives
several); any new way to earn experience calls that. So far the one way is surviving a battle: as
`TurnManager` decides the battle it calls `PlayerSquad.award_survivors()`, which gives every member
still standing `survival_experience` (50), and adds to `Campaign.gold` whatever gold each one's skills
find after a combat (`Character.combat_gold()`, `Docs/SKILLS.md`), emitting `found_gold(unit, gold)`,
on which `TurnManager` calls "+N Gold" over that unit's head as a coin it picked up would be
(`ShotOverlay.flash_pickup()`). A win also adds `TurnManager.victory_gold` (10) to `Campaign.gold`, at
the same moment, and has `Coins.sweep()` pay for every coin still lying on the map (`CLAUDE.md`,
"Coins are rolled as blocks break and go by tiles").

What happens in battle goes the other way, through `PlayerSquad` as it happens, not at the end: every
change to a member's health is written to `Character.wounds` (health missing, so a character is whole
by default and stays as hurt if `max_health` grows; `Character.health` is what is left), and a unit
starts at its character's `health`. A grenade a member throws is gone for good: `Unit.use_up()` emits
`used_up`, and `PlayerSquad` calls `Campaign.use_up()`, which empties the first slot holding it and
puts nothing back in the inventory. A member who dies is taken off the roster by `Campaign.lose()`,
which returns everything they still had equipped to the inventory. Those two are the only ways gear
leaves a character mid-battle. The gear a dying member is seen to drop on the map (`ANIMATIONS.md`,
9.8) is only for show: it is in the inventory already. Wounds mend on the road: every step the party
travels (`Party.step_length`, the same step the encounters are rolled on) calls
`Campaign.heal(heal_per_step)` (1), which takes that off every roster character's `wounds`, down to
none, before that step's roll. Unlike an `Item`, a character is state and changes in play; nothing
writes it back to disk, and save/load will need to store it. Enemies and `LineOfSightTest`'s units
have no character and keep the scene's name and tint; the harness has no `SquadStarts` (`starts_path`
is empty), so its eight fixed units are its squad and spawn nothing.

### Items and the inventory

**Items are shared resources, the inventory is state.** An `Item` (`Weapon`, `BattleItem`) is a
stateless `.tres`: the same `Rifle.tres` is what units shoot with and what the inventory lists. Its
`tags` (`StringName`s, the ones the rules read as constants on `Item`) say what sort of thing it is,
finer than its class: `Rifle.tres` is tagged `gun`, `FragGrenade.tres` (a `Grenade`, the `BattleItem`
that carries its blast: 5 damage, 3 tiles across) `grenade`, `Shortsword.tres` `melee` (a `Weapon`
that is not a gun, so it gives Strike rather than Shoot), `Medkit.tres` (a `Medkit`, the `BattleItem`
that carries its `heal`) `medkit`. A new gun is a `Weapon` `.tres` tagged `gun`, and gets Shoot and
Overwatch with no code. How many the party holds lives in `ItemStack`s in an `Inventory`, and the live
one is `Campaign.inventory`, a `duplicate_deep()` of `Resources/StartingInventory.tres` (its stacks
are copied, its items are not). Change that copy, never the `.tres`. A new kind of item is an `Item`
subclass plus an `ItemBrowser` sub-tab over `inventory.stacks_of(ThatKind)` in `InventoryTab`, which
gives it a sub-tab on both sides of every market too.

### Equipment

**Equipment is on the character, the spares in the inventory.** A character has six typed slots
(`armor`, `weapon_1`, `weapon_2`, `item_1`..`item_3`), listed with their titles and kinds in
`Character.slots` (a `static var`: a `const` cannot hold a class). Every item is either in
`Campaign.inventory` or in one slot, never both, so equipment only changes through `Campaign.equip()`
/ `unequip()`, which move one copy across and put a swapped-out item back. What a character starts
with is set in their `.tres`, not counted in `StartingInventory.tres`. What is equipped decides a
squad unit's actions by its tags (`CLAUDE.md`, "An action can need an item"): with no gun it has only
Move. It shoots with the first gun in its slots, Weapon 1 before Weapon 2 (`Unit.weapon`, null with
none), and strikes with the first melee weapon, the same way (`Unit.melee_weapon`), which gives it
Strike. A grenade in any item slot gives it Throw Grenade, which throws the first one, Item 1 before
Item 2 before Item 3 (`Unit.grenade`), and uses it up. A medkit in any item slot gives it Use Medkit,
a use a battle for each, and is never used up. Armor adds its `Armor.defense` to the wearer's
(`Character.total_defense`), which the unit copies as its own; the Details page shows that total and
refreshes as it comes into view, since the Equipment page may have changed the armor. During a battle
`Campaign.in_mission` is true (the `TurnManager` sets it while in the tree) and both calls refuse,
since a unit took its gear when the map loaded; the Equipment page greys its buttons and says why.
This is the menu's first read-only-in-combat rule; the System tab's **Blood** button is the second
(`Docs/BLOOD.md`), and learning a skill the third (`Docs/SKILLS.md`). `Campaign.use_up()` and `lose()`
do not refuse: they follow what the battle did.

The Roster tab is a `CharacterBrowser`, whose sub-tabs are `CharacterPage`s. Whenever the selection in
the strip changes, every page (not just the open one) gets `show_character(character)`, so a page is
never left showing someone else; a page with content overrides `_refresh()`, and `focus_selection()`
if Down from the sub-tabs should land somewhere in it. Changing character keeps the open page; opening
the menu goes back to Details. A page that can change the character hides the means when `read_only`
is set, as it is for characters not on the roster.

## Its scripts

`CLAUDE.md`'s Layout lists every script in a line or two; here are `Roster/`'s in full. The Roster
tab's widgets are listed there in full already.

```
  Roster/
    Character.gd       Resource: display_name, color, portrait, species / sub_species / main_class / multi_class
                       (TREES), learned (node ids by SkillSource, one for each time taken), learned_of() /
                       times_learned() / can_learn() / learn(), skill_effects(), its own stats and total(stat)
                       (with its skills' bonuses, and armor for defense), combat_gold() (what its skills find
                       after a battle), wounds / health, total_defense,
                       experience, skill_points, gain_experience(), equipment slots, hire_cost
    Roster.gd          characters in display order
    Species.gd         SkillSource: what someone is born (Human)
    SubSpecies.gd      SkillSource: a kind of one Species (Minor Noble), its species
    CharacterClass.gd  SkillSource: what someone trained as; one tree, as Main Class or Multi-Class
```

## Probing it

The roster is probed headless, as the rest is (`CLAUDE.md`'s Verification). `Campaign` is there at
run time (`root.get_node("Campaign")`), but a `--script` probe cannot name `PlayerSquad`, or anything
else that reaches `Campaign`, in a type (`CLAUDE.md`'s Gotchas). Change a character before a map
loads and its `PlayerSquad` spawns what it finds: equip it (`Campaign.equip(character, &"item_1",
item)`), wound it (`wounds`), and `Campaign.squad(count)` says who would fight. In battle
`squad.members` are the units, each with its `character`: a hit on one is on the character's
`wounds` at once, and as the battle is decided `award_survivors()` puts `survival_experience` on each
survivor's `experience`, a skill point for every 100. The Roster tab's clicks have to be driven in
a window (`CLAUDE.md`'s Gotchas, "Headless quirks").

## Known gaps

- The only experience is for surviving a battle. There are no classes, and Rich Blood, the Minor
  Noble tree's last skill, can be learned but does nothing. Grenades are the only items used up in
  battle.
- Dropped gear is only for show: it cannot be picked up, and a squad member's is back in the
  inventory already.
