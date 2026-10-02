## Someone on the player's roster, who they are between battles. A squad
## [Unit] in a combat map points at one ([member Unit.character]) and takes
## its name, colour and stats from it.
##
## Unlike an [Item] a character is state: it gathers experience, wounds and
## gear. The roster and the units share the loaded [code].tres[/code], so a
## change to one shows in the other. Nothing writes it back to disk.
class_name Character
extends Resource

## What [member experience] counts up to: reaching it turns it into a skill
## point (see [method gain_experience]). The Details page's bar fills to it.
const EXPERIENCE_TO_LEVEL := 100
## Every equipment slot, in the order shown: its title, the property holding
## it, and the kind of [Item] it takes. Static rather than a constant, which
## cannot hold a class. Not to be changed.
static var slots := [
	["Armor", &"armor", Armor],
	["Weapon 1", &"weapon_1", Weapon],
	["Weapon 2", &"weapon_2", Weapon],
	["Item 1", &"item_1", BattleItem],
	["Item 2", &"item_2", BattleItem],
	["Item 3", &"item_3", BattleItem],
]
## Every skill tree a character has, in the order the Skills page shows them:
## its title, which heads its column while the character has none, and the
## property holding the [SkillSource] that gives it. A new kind of tree is a
## row here and a property.
const TREES := [
	["Species", &"species"],
	["Sub-Species", &"sub_species"],
	["Main Class", &"main_class"],
	["Multi-Class", &"multi_class"],
]

@export var display_name := ""
## Placeholder identity colour: the unit's body in combat, and the portrait
## while the character has none.
@export var color := Color.WHITE
@export var portrait: Texture2D

@export_group("Species and Classes")
## Each gives the character a skill tree, a column of their Skills page headed
## by its name. While one is unset, its column keeps its plain title
## ("Species", "Main Class") and shows no tree.
@export var species: Species
## One of [member species]'s kinds: see [member SubSpecies.species].
@export var sub_species: SubSpecies
@export var main_class: CharacterClass
## A second class, its tree the same as it would be as a Main Class.
@export var multi_class: CharacterClass
## What the character has learned of each tree, by the [SkillSource] that
## gives it: the [member SkillTreeNode.id]s, in the order learned, a node's
## once for every time it has been taken. Changed only
## through [method learn] once the game is running; what a character starts
## with is set here.
@export var learned: Dictionary[SkillSource, Array] = {}

@export_group("Stats")
## The character's own stats, before anything adds to them. What their unit
## takes into battle, and what the Details page shows, is each one's
## [method total]: read that, not these, wherever the character's skills and
## gear should count.
##
## The unit's [member Unit.max_health]: what it can take before it falls.
@export var max_health := 10
## The unit's [member Unit.move_range]: tiles walked per action spent moving.
@export var move_range := 4
## The unit's [member Unit.aim]: its chance to hit before anything about the
## shot counts.
@export var aim := 90
## The unit's [member Unit.melee_accuracy]: what [member aim] is to a shot,
## this is to a melee strike.
@export var melee_accuracy := 90
## The unit's [member Unit.strength]: added to the damage of every melee
## strike they land.
@export var strength := 0
## The unit's [member Unit.evasion]: taken off the chance of anyone shooting
## at it, or striking at it.
@export var evasion := 0
## The character's own defense, before their [member armor] adds to it: see
## [member total_defense], which is what their unit takes into battle.
@export var defense := 0
## Earned in play, out of [constant EXPERIENCE_TO_LEVEL], only through
## [method gain_experience]; for now surviving a battle is the one way (see
## [PlayerSquad]). Not copied onto the unit: it is the character's, not the
## battle's.
@export var experience := 0
## Points to spend on the skill trees, one for every
## [constant EXPERIENCE_TO_LEVEL] experience earned, and one spent on every
## skill learned ([method learn]). They stack while unspent.
@export var skill_points := 0
## Health lost in battle and not yet healed. Kept as what is missing rather
## than what is left, so a character is whole by default and stays as hurt if
## [member max_health] ever grows. Written by the squad as its unit is hit
## (see [PlayerSquad]), and brought down as the party travels
## ([method Campaign.heal]).
@export var wounds := 0

## What is left of the most health they can have ([member max_health] in
## [method total]): the health the character's unit starts a battle with.
var health: int:
	get:
		return maxi(total(&"max_health") - wounds, 0)

## [member defense] in [method total], the worn [member armor]'s added: the
## unit's [member Unit.defense], taken off the damage of every hit it takes.
var total_defense: int:
	get:
		return total(&"defense")

@export_group("Hiring")
## Gold the party pays to take the character on from a [HiringBoard].
## Nothing once they are on the roster.
@export var hire_cost := 0

@export_group("Equipment")
## Changed only through [method Campaign.equip] and [method Campaign.unequip]
## once the game is running, so an item is never both carried and in the
## inventory. What a character starts with is set here, and is not in the
## starting inventory. What is equipped decides the unit's actions in combat
## by its tags (see [member Item.tags]): Shoot and Overwatch need a gun, Throw
## Grenade a grenade.
@export var armor: Armor
## The character's unit shoots with the first gun of the two, this one first.
@export var weapon_1: Weapon
@export var weapon_2: Weapon
@export var item_1: BattleItem
@export var item_2: BattleItem
@export var item_3: BattleItem


## Adds [param amount] experience. Every [constant EXPERIENCE_TO_LEVEL] of it
## becomes a skill point and the rest carries over: 10 more at 97 leaves 7 and
## a point more, and enough for several gives several. Every way of earning
## experience comes through here, so the rule is kept in one place.
func gain_experience(amount: int) -> void:
	if amount <= 0:
		return
	experience += amount
	while experience >= EXPERIENCE_TO_LEVEL:
		experience -= EXPERIENCE_TO_LEVEL
		skill_points += 1


## [param stat] (one of the stats above, by its property's name, such as
## [code]&"max_health"[/code]) as the character has it now: their own, with
## what every skill level they have taken adds to it
## ([method SkillEffect.bonus_to]) and, for defense, their [member armor]'s.
## Worked out each time it is asked, so it follows what is learned and worn,
## and the character's own stat is never changed by either.
func total(stat: StringName) -> int:
	var own: Variant = get(stat)
	if not (own is int):
		push_error("Character has no stat '%s'." % stat)
		return 0
	var value: int = own
	for effect in skill_effects():
		value += effect.bonus_to(stat)
	if stat == &"defense" and armor != null:
		value += armor.defense
	return value


## Every effect the character's skills give them: those of each level they
## have taken ([member SkillLevel.effects]), of every node in their own trees
## ([constant TREES]). What they learned of a tree that is no longer theirs
## gives nothing.
func skill_effects() -> Array[SkillEffect]:
	var effects: Array[SkillEffect] = []
	var sources: Array[SkillSource] = []
	for entry in TREES:
		var source: SkillSource = get(entry[1])
		# Once each, should two of the four ever be the same.
		if source == null or source.tree == null or sources.has(source):
			continue
		sources.append(source)
		var ids := learned_of(source)
		for node in source.tree.nodes:
			if node.skill == null:
				continue
			for number in range(1, mini(ids.count(node.id), node.takes()) + 1):
				var level := node.skill.level(number)
				if level == null:
					continue
				for effect in level.effects:
					if effect != null:
						effects.append(effect)
	return effects


## The ids of the nodes of [param source]'s tree the character has learned, in
## the order learned, a node's once for every time it has been taken. A copy:
## learning goes through [method learn].
func learned_of(source: SkillSource) -> Array[StringName]:
	var ids: Array[StringName] = []
	if learned.has(source):
		ids.assign(learned[source])
	return ids


## How many times the character has taken [param node] of [param source]'s
## tree.
func times_learned(source: SkillSource, node: SkillTreeNode) -> int:
	return learned_of(source).count(node.id)


## Whether the character can learn [param node] of [param source]'s tree now,
## for the first time or again: the tree is one of their own
## ([constant TREES]), the node is in it and not yet taken as often as it can
## be ([method SkillTreeNode.takes]), everything it requires is learned, and
## they have a skill point to spend.
func can_learn(source: SkillSource, node: SkillTreeNode) -> bool:
	if skill_points < 1 or source == null or source.tree == null or not source.tree.nodes.has(node):
		return false
	if not TREES.any(func(entry: Array) -> bool: return get(entry[1]) == source):
		return false
	var ids := learned_of(source)
	return ids.count(node.id) < node.takes() and source.tree.is_open(node, ids)


## Learns [param node] of [param source]'s tree for a skill point, or takes
## it once more. False, changing nothing, when [method can_learn] says it
## cannot be. Every way of
## learning a skill comes through here, so the rule is kept in one place;
## during a battle [code]Campaign.learn()[/code] refuses first.
func learn(source: SkillSource, node: SkillTreeNode) -> bool:
	if not can_learn(source, node):
		return false
	skill_points -= 1
	if not learned.has(source):
		learned[source] = []
	learned[source].append(node.id)
	return true


## The kind of item [param slot] takes, from [member slots]. Null for a name
## that is not a slot.
static func slot_kind(slot: StringName) -> Script:
	for entry in slots:
		if entry[1] == slot:
			return entry[2]
	return null
