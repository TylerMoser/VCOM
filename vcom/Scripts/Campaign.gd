## The state of the campaign that outlives any one scene: who is on the
## roster and what the party holds. An autoload, so the world map and combat
## read and change the same thing, and so saving has one place to look.
extends Node

const STARTING_ROSTER := preload("res://Resources/StartingRoster.tres")
const STARTING_INVENTORY := preload("res://Resources/StartingInventory.tres")

## Who is on the roster is the campaign's to change; the characters in it are
## the same resources the combat maps' units point at, so they stay linked.
var roster: Roster = _copy_roster(STARTING_ROSTER)
## A copy of [constant STARTING_INVENTORY]: its stacks are the campaign's to
## change, its items are the shared resources.
var inventory: Inventory = STARTING_INVENTORY.duplicate_deep()


static func _copy_roster(from: Roster) -> Roster:
	var copy := Roster.new()
	copy.characters = from.characters.duplicate()
	return copy
