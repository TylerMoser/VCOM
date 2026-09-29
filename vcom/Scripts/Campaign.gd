## The state of the campaign that outlives any one scene: who is on the
## roster, what the party holds and what each of them has equipped, the
## party's gold, and who and what is left at each village's hiring board and
## market. An autoload, so the world map and combat read and change the same
## thing, and so saving has one place to look.
##
## Equipment moves only through [method equip] and [method unequip], which
## keep every item either in the inventory or on a character, never both.
extends Node

const STARTING_ROSTER := preload("res://Resources/StartingRoster.tres")
const STARTING_INVENTORY := preload("res://Resources/StartingInventory.tres")
const STARTING_GOLD := 100

## Who is on the roster is the campaign's to change; the characters in it are
## the same resources the combat maps' units point at, so they stay linked.
var roster: Roster = _copy_roster(STARTING_ROSTER)
## A copy of [constant STARTING_INVENTORY]: its stacks are the campaign's to
## change, its items are the shared resources.
var inventory: Inventory = STARTING_INVENTORY.duplicate_deep()
## The whole party's gold, one purse. Nothing earns or spends it yet.
var gold := STARTING_GOLD
## Whether a battle is being fought. Set by the combat scene's [TurnManager]
## while it is in the tree. Equipment cannot change during one: a unit took
## its gear when the map loaded, and would not see the change.
var in_mission := false
## Who is still for hire at each [HiringBoard], by board: a copy of the board's
## own list made the first time it is asked about, so the board's resource is
## never changed. Holding the board keeps it loaded, so the world map gets
## the same one back each time it opens.
var _for_hire := {}
## What is still for sale at each [Market], by market: a copy of the market's
## stock made the first time it is asked about, as [member inventory] is of
## the starting one (its stacks are copied, its items are not).
var _stock := {}


## Takes one [param item] out of the inventory and puts it in [param slot]
## (a name from [member Character.slots]) on [param character], returning
## whatever was there to the inventory. False, changing nothing, during a
## mission, when there is none in the inventory, or when the slot does not
## take that kind of item.
func equip(character: Character, slot: StringName, item: Item) -> bool:
	if in_mission or item == null or not is_instance_of(item, Character.slot_kind(slot)):
		return false
	if not inventory.take(item):
		return false
	var old: Item = character.get(slot)
	if old != null:
		inventory.add(old)
	character.set(slot, item)
	return true


## Returns what is in [param slot] on [param character] to the inventory and
## leaves the slot empty. False, changing nothing, during a mission or when
## the slot is already empty.
func unequip(character: Character, slot: StringName) -> bool:
	var old: Item = character.get(slot)
	if in_mission or old == null:
		return false
	inventory.add(old)
	character.set(slot, null)
	return true


## Who is still for hire at [param board], in the order it lists them.
func for_hire(board: HiringBoard) -> Array[Character]:
	if not _for_hire.has(board):
		_for_hire[board] = board.characters.duplicate()
	var available: Array[Character] = _for_hire[board]
	return available.duplicate()


## Pays [param character]'s [member Character.hire_cost] and moves them from
## [param board] to the end of the roster. False, changing nothing, when they
## are not for hire there or the party cannot afford them.
func hire(board: HiringBoard, character: Character) -> bool:
	if character == null or not for_hire(board).has(character) or gold < character.hire_cost:
		return false
	gold -= character.hire_cost
	(_for_hire[board] as Array).erase(character)
	roster.characters.append(character)
	return true


## What [param market] still has for sale. It changes only through
## [method buy], and emits [signal Resource.changed] when it does, so a view
## of it can keep up.
func stock_of(market: Market) -> Inventory:
	if not _stock.has(market):
		_stock[market] = market.stock.duplicate_deep() if market.stock != null else Inventory.new()
	return _stock[market]


## Pays [param item]'s [member Item.price] and moves one of it from
## [param market]'s stock into the party's inventory. False, changing
## nothing, when the market has none left or the party cannot afford it.
func buy(market: Market, item: Item) -> bool:
	if item == null or gold < item.price or not stock_of(market).take(item):
		return false
	gold -= item.price
	inventory.add(item)
	return true


static func _copy_roster(from: Roster) -> Roster:
	var copy := Roster.new()
	copy.characters = from.characters.duplicate()
	return copy
