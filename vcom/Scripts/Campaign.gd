## The state of the campaign that outlives any one scene: who is on the
## roster, what the party holds, and what each of them has equipped. An
## autoload, so the world map and combat read and change the same thing, and
## so saving has one place to look.
##
## Equipment moves only through [method equip] and [method unequip], which
## keep every item either in the inventory or on a character, never both.
extends Node

const STARTING_ROSTER := preload("res://Resources/StartingRoster.tres")
const STARTING_INVENTORY := preload("res://Resources/StartingInventory.tres")

## Who is on the roster is the campaign's to change; the characters in it are
## the same resources the combat maps' units point at, so they stay linked.
var roster: Roster = _copy_roster(STARTING_ROSTER)
## A copy of [constant STARTING_INVENTORY]: its stacks are the campaign's to
## change, its items are the shared resources.
var inventory: Inventory = STARTING_INVENTORY.duplicate_deep()
## Whether a battle is being fought. Set by the combat scene's [TurnManager]
## while it is in the tree. Equipment cannot change during one: a unit took
## its gear when the map loaded, and would not see the change.
var in_mission := false


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


static func _copy_roster(from: Roster) -> Roster:
	var copy := Roster.new()
	copy.characters = from.characters.duplicate()
	return copy
