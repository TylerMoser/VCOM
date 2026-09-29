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

@export var display_name := ""
## Placeholder identity colour: the unit's body in combat, and the portrait
## while the character has none.
@export var color := Color.WHITE
@export var portrait: Texture2D

@export_group("Stats")
## The unit's [member Unit.max_health]: what it can take before it falls.
@export var max_health := 10
## The unit's [member Unit.move_range]: tiles walked per action spent moving.
@export var move_range := 4
## The unit's [member Unit.aim]: its chance to hit before anything about the
## shot counts.
@export var aim := 90
## The unit's [member Unit.evasion]: taken off the chance of anyone shooting
## at it.
@export var evasion := 0
## Earned in play, out of [constant EXPERIENCE_TO_LEVEL], only through
## [method gain_experience]; for now surviving a battle is the one way (see
## [PlayerSquad]). Not copied onto the unit: it is the character's, not the
## battle's.
@export var experience := 0
## Points to spend on the skill trees, one for every
## [constant EXPERIENCE_TO_LEVEL] experience earned. They stack while unspent;
## nothing spends them yet.
@export var skill_points := 0
## Health lost in battle and not yet healed. Kept as what is missing rather
## than what is left, so a character is whole by default and stays as hurt if
## [member max_health] ever grows. Written by the squad as its unit is hit
## (see [PlayerSquad]), and brought down as the party travels
## ([method Campaign.heal]).
@export var wounds := 0

## What is left of [member max_health]: the health the character's unit
## starts a battle with.
var health: int:
	get:
		return maxi(max_health - wounds, 0)

@export_group("Hiring")
## Gold the party pays to take the character on from a [HiringBoard].
## Nothing once they are on the roster.
@export var hire_cost := 0

@export_group("Equipment")
## Changed only through [method Campaign.equip] and [method Campaign.unequip]
## once the game is running, so an item is never both carried and in the
## inventory. What a character starts with is set here, and is not in the
## starting inventory.
@export var armor: Armor
## The gun the character's unit shoots with in combat.
@export var weapon_1: Weapon
## Carried but not used in combat yet.
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


## The kind of item [param slot] takes, from [member slots]. Null for a name
## that is not a slot.
static func slot_kind(slot: StringName) -> Script:
	for entry in slots:
		if entry[1] == slot:
			return entry[2]
	return null
