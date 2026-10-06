# Skills

Skills in full: `Scripts/Skills/`, the trees a `Character` holds and learns from, and the Skills
page (`SkillsPage`, `SkillTreeView`, `SkillButton`, `SkillTooltip`). It was split out of
`CLAUDE.md`, which keeps a summary and how a unit takes its character's stats ("Squad units are
roster characters"). A section named here that is not in this file (Gotchas, Verification, Known
gaps, another subsystem's notes) is `CLAUDE.md`'s.

## How they work

**Skill trees are data, and any shape.** A `Skill` (`Resources/Skills/`) is a stateless `.tres` like
an `Item`: a name, a line of flavour text, an icon and its levels, each with its words and what it
gives. A `SkillTree` places skills as
`SkillTreeNode`s, each with an `id` unique in its tree, a `cell` on the tree's grid (column, row,
from 0 at the top left) and `requires`, the ids of nodes in the same tree that must all be learned
before it can be (`SkillTree.is_open()`). A tree's shape is nothing more than where its nodes sit and what
they require: a column of nodes each requiring the one above is a path, two requiring one node a
fork, one requiring two a join. A skill is kept apart from where it sits so one can sit in several
trees (decided with the user), though no skill sits in two yet. A node's `id` is what a character's
progress keys on, and saves will, so never rename one once in play.

A tree belongs to a `SkillSource`, the base of `Species` (`Resources/Species/`), `SubSpecies`
(`Resources/SubSpecies/`) and `CharacterClass`, each with its tree as a sub-resource in its `.tres`.
A sub-species is a kind of exactly one species (`SubSpecies.species`; decided with the user); a class
has one tree, shown the same whether it is the Main Class or the Multi-Class (also decided). A
`Character` holds one of each, `species`, `sub_species`, `main_class` and `multi_class`, any of them
unset, listed with their titles in `Character.TREES`. Every character is a Human Minor Noble, and no
class exists yet. Nothing checks that a character's sub-species is one of their species' kinds: keep
them agreeing.

**Skills are learned by holding a node.** What a character has learned is theirs, like their wounds:
`Character.learned`, the node ids of each tree in the order learned, keyed by the `SkillSource`
resource (not by the column, so a tree's progress follows the species or class, wherever it shows).
It only changes through `Character.learn()`, which spends one skill point a node, every node the
same, and refuses, changing nothing, unless `can_learn()`: the tree is one of the character's own
(`TREES`), the node is in it and not yet taken as often as it can be, everything it requires is
learned, and there is a point to spend. The page learns through `Campaign.learn()`, which refuses
first during a mission, as `equip()` does: a unit will take what its character has learned when the
map loads.

**A skill has a level for each time it can be taken.** `Skill.levels` is a list of `SkillLevel`s
(sub-resources of the skill's `.tres`) in the order they are taken: the first is what learning the
skill gives, each after it what taking it again adds, for more or different benefits each time. A
level has its `description`, the words its tooltip shows, and its `effects`. How often a skill can
be taken is how many levels it has (`Skill.takes()`: at least once, with none, and at most
`Skill.MOST_LEVELS`, 5, the first and four more), so there is no separate count to disagree with
them: a level is added by adding one. They are the skill's, so the
same in every tree that places it, and `SkillTreeNode.takes()` is its node's count. Every take is a
`learn()` of its own, a skill point each, and
`Character.learned` lists the node's id once for each (`times_learned()` counts them), so the list is
still the order things were learned in. A requirement is met by taking the node once, however often
it can be taken (`is_open()` only asks whether the id is there): assumed, not asked of the user, as
is a press of the button taking it once at most, as every hold does. `Ambition.tres` (five levels)
is the Human tree's first node, `ambition`, and `Hardiness.tres` (one level, so no rings: +1
`defense`) its second, `hardiness`, which requires it, and `Dexterity.tres` (one level with two
effects, +1 `move_range` and +5 `evasion`) its third, `dexterity`, which requires that, and
`Adaptability.tres` (one level, a `SkillPointGrant` of 5) its last, `adaptability`. That is the whole
Human tree. The Minor Noble tree starts with `MoneyGrubbing.tres` (five levels, each a `CombatGold`:
1, 1, 3, 5 and 5, 15 in all), `money_grubbing`, then `BallisticsSkill.tres` (one level, +10 `aim`),
`ballistics_skill`, which requires it, then `WeaponSkill.tres` (two levels, so one ring: +10
`melee_accuracy`, then +1 `strength`, a level giving a different stat from the one before it),
`weapon_skill`, and last `RichBlood.tres`, `rich_blood`: one level with its words and no effects,
so it shows, and can be learned for a skill point, but does nothing. Its logic was left out at the
user's request until there are more items: it is to unlock rare goods at markets, at twice their
usual price, while a character with it is in the party, which will want a new question on
`SkillEffect` for `Campaign.stock_of()` / `buy()` and the Market tab to ask, and a way to mark an item
rare. Hardiness, Dexterity, Ballistics Skill and Weapon Skill took no code: a skill of a kind of
effect that exists is its `.tres` and its node in the tree. With every node a real skill, the
`Placeholder.tres` they started as is gone.

**What a skill gives is its levels' effects, and a character has those of every level taken.** An
effect is a `SkillEffect` resource in a level's `effects`, and a kind of effect is a subclass, as a
kind of enemy is an `EnemyAI` subclass: `StatBonus` (a `stat` from its list, an `amount`),
`CombatGold` and `SkillPointGrant` (an `amount` each) so far. Levels add up: a character has the
effects of each level they have taken, the earlier
with the later, so a level holds only what it adds (Ambition's five are +1, +1, +1, +2 and +5
`max_health`, +10 in all, as their words say: "An additional +2 HP (for a total of +5 HP)").
`Character.skill_effects()` gathers them, from every node of the character's own trees (`TREES`) by
how often `learned` has it; what was learned of a tree no longer theirs gives nothing.

An effect is one of two sorts, and `SkillEffect` has a method for each, doing nothing unless a kind
overrides it. One sort lasts for as long as the level is had. For it nothing is applied when the
skill is learned, and nothing stored but `learned`: the rules ask the effects when they need an
answer. So far the one question is `bonus_to(stat)`, asked by `Character.total(stat)`:
the character's own stat (the exported property, never changed by a skill or by gear) plus every
effect's bonus to it, plus the armor's for defense. Everything that wants a character's stat reads
`total()`: `Unit._take_character()` for all seven, so a bonus goes into battle with the unit;
`Character.health` (`total(&"max_health")` less `wounds`), so a level of Ambition raises the most
health and what is left alike, and a wounded character stays as wounded; and the Details page, which
refreshes as it comes into view. A unit copies its stats as the map loads, which is why learning is
refused during a mission.

The second question is `gold_after_combat()`, which `CombatGold` answers with its `amount` and
`Character.combat_gold()` adds up. `PlayerSquad.award_survivors()` asks it of each member's character
as the battle is decided, beside their experience, and pays it into `Campaign.gold` at once. Who it
asks is the whole rule, decided with the user: only the squad's members, so a character left on the
roster finds nothing however many levels they have, and only those still in `members`, which the
fallen have left, so the character must come through the battle. A defeat leaves nobody standing, so
it only ever pays on a win, and it is on top of `victory_gold` and the coins. It reads the character
as the battle ends rather than a copy on the unit: nothing can be learned in between.

The other sort happens once, as the level is taken: `Character.learn()`, having spent the point and
recorded the take, calls `when_taken(character)` on each effect of that level, and what it does is
the character's from then on, with nothing to ask later. `SkillPointGrant` is it: Adaptability's
`skill_points += 5`, so learning it with one point left leaves five (the page's sub-tab count follows,
since it shows progress again after every skill learned). It is not done for a level a character
starts out with in their `.tres`, which goes through no `learn()`: set what it would have given there
too. Nothing undoes it, as nothing unlearns a skill.

A new skill of a kind that exists is only a `.tres`. A new kind of effect (an action granted, a rule
bent) is a `SkillEffect` subclass and, if neither method fits it, a new method on the base class
asking what the rules need to know of it, and a call where they need it, over `skill_effects()`.

The Skills page has a column per `Character.TREES` entry, its share of the width from
`SkillsPage.SHARES`, and is rebuilt for every character, a column headed by its source's
`display_name` ("Human"), or by its plain title ("Species") with no tree under it while the
character has none. A new kind of tree is a `SkillSource` subclass, a `Character` property and a
row in `TREES` (and in `SHARES`, unless 1 will do). Each tree is a `SkillTreeView`,
which places its `SkillButton`s itself by their cells (`GAP` apart) rather than in containers, and
draws every link as an elbow: down from the node required, across just above the row of the node
requiring it, and down into it, so a path is a straight line; lit once the node required is learned.
A button with rings is bigger (`SkillButton.size_of()`: `RING_GAP` + `RING_WIDTH` more each side a
ring, 84 across with four against 44), so cells are not all one size: a column is as wide as its
widest button, and a row as tall as its tallest button in any tree on the page
(`SkillTreeView.row_heights()`, which the page works out over every tree it is about to show and
hands to each view), so the trees' rows stay level across the columns. Each button sits in the
middle of its cell, and a link runs from the bottom of one button to the top of the other, outside
their rings.
A link to a node on the same row or higher, which a tree should not need, is a straight line between
them. It warns of two nodes with one id, and of a requirement the tree lacks; nothing stops two
nodes sharing a cell. A button is a circle (it takes the mouse only inside it, `_has_point()`) that
draws itself, its theme's boxes all empty, so the fill can go under its face: its skill's icon,
dimmed while locked, or its rank (its row, from 1). The arrow keys are pointed from a button as
it takes focus, once the trees are laid out, at the nearest button that way (`_nearest()`): up and
down within its own tree, left and right on across the trees. With none to the left or right it stays
put; with none above or below, the key is left to Godot, which takes up back to the sub-tabs and down
to whatever lies under the page: the squad menu's Start, a hiring board's Hire (as Down from the
sub-tabs of the Details page reaches them), and nowhere in the pause menu, which has nothing there.
Up from those buttons goes to the sub-tabs, and Down from the sub-tabs back to the selected node.

A node is learned by holding it down, with the mouse or Enter / Space, as a `HoldButton` is held
(its `HOLD_TIME`, 2 s, its `DRAIN_SPEED` and its fill colour, decided with the user): it fills like a
clock's face, from the top round clockwise, a sector drawn under its face. That is the first time it
is taken. A skill that can be taken again has a ring round the circle for each further time, drawn
dim from the start, and once it is taken a hold draws the innermost ring not yet lit round instead,
the same way, from the top clockwise (decided with the user: the circle first, then the rings from
the inside out); `SkillButton.taken`, which `show_learned()` sets, says which. The rings are part of
the button, so a press on them counts. Let go early it drains;
full, it emits `held`, empties and stays empty until let go, so a press learns one skill at most. It
fills only while the page has set it `learnable`, which `_show_progress()` sets for every node from
`can_learn()`, and never in a mission or read only; any other node can still be pressed and selected,
and nothing happens. On `held` the page calls `Campaign.learn()` and `_show_progress()` again, which
restyles every tree (`SkillTreeView.show_learned()`: learned, open or locked, links lit) in place,
rather than rebuilding, so the selection and the keyboard stay where they were. Nothing on the page
says how to learn, or why a node will not fill (a mission, no points): a help line under the trees
was taken out at the user's request, for now.

A button is not a toggle: holding a toggle button reads as pressed whether it is held or not
(`get_draw_mode()`), which the fill depends on. So the page keeps the selection itself, `_selected`,
moved as a button takes focus (a click or the arrow keys), and sets the button's `selected`, which
fills its circle a shade lighter: blended toward `SELECTED_COLOR`, a near white, by `SELECTED_BLEND`
on a dark circle and by `SELECTED_LEARNED_BLEND` on a learned one's gold, where as little would not
show. That fill is all that shows where the keyboard is (asked for by the user in place of a white
ring round the node, which they had taken out), and it is not the accent, which is kept for what is
learned and being learned. It stays on the selected node while the keyboard is up on the tabs, as a
selected character's frame does, since Down comes back to it. Changing character clears
it. The page also titles its own sub-tab, "Skills (2)" from
`Character.skill_points`, again after every skill learned. It reads `Campaign` only once a character
is shown: the pause menu builds its pages before that autoload exists.

**A skill's tooltip is the page's own panel, not Godot's.** A built-in tooltip only follows the mouse,
and a skill's has to show for the keyboard too, so `SkillsPage` owns one `SkillTooltip`, a child added
after the columns so it draws over the trees, and a `SkillButton` has no `tooltip_text`. Its parts,
from the top, are the user's: the skill's name; its `flavor`; "Current:" and `Skill.describe(taken)`,
once the character has taken it; "Next:" and `Skill.describe(taken + 1)`, while a level is left to take,
whether or not it can be taken now (locked, or no points). A part with nothing to say is left out.
It is `WIDTH` (300) wide and as tall as its text: every label has its wrap width as its minimum
width, so it knows its height the moment its text is set and `reset_size()` fits the panel there and
then, with no frame's wait for a container. It never takes the mouse, so a node under it can still
be hovered and held.

Whose it is: the node with the keyboard (`_focused`, kept from the buttons' `focus_entered` /
`focus_exited`) when a key was pressed more recently than the mouse did anything, else the node under
the mouse (`_hovered`), else nobody and it hides. The page's `_input()` notes which was used last
(`_by_keyboard`), before either moves anything, so arrowing about with the mouse left lying on a node
shows the keyboard's node, and a nudge of the mouse hands it back. It hides once the keyboard goes up
to the tabs, though the node stays selected. `_show_tooltip()` places it to the node's right, top to
top, `TOOLTIP_GAP` off, or to its left where that would run off the page, and never below the page's
bottom; `_show_progress()` calls it again, since a level just taken changes what it says.

## Known gaps

- The Human tree's four skills and the Minor Noble tree's first three are the only ones that do
  anything, and a stat bonus, gold after a combat and a grant of skill points the only kinds of
  effect; every take costs one skill point, and nothing unlearns one. Rich Blood, the Minor Noble
  tree's last, can be learned but does nothing: no market has rare goods, no item is marked rare, and
  no price is doubled. There are no classes.
- Nothing shows where a stat's total comes from: the Details page gives the total alone. A level's
  words and its effects are written separately, so nothing keeps them agreeing.
- A pie's straight edges are not antialiased. A skill's tooltip lies over whatever is beside its
  node, the next tree's nodes among them, for as long as the keyboard is on the node.
- The Skills page does not scroll: its trees have about 296 px of height, which the two trees as they
  are fit (280: a row of four rings, a row of one and two plain rows) but a fifth row, or rings on
  three rows of four, run out of the panel's bottom.
