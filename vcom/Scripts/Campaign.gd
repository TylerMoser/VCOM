## The state of the campaign that outlives any one scene: what the party
## holds, and later who is in it. An autoload, so the world map and combat
## read and change the same thing, and so saving has one place to look.
extends Node

const STARTING_INVENTORY := preload("res://Resources/StartingInventory.tres")

## A copy of [constant STARTING_INVENTORY]: its stacks are the campaign's to
## change, its items are the shared resources.
var inventory: Inventory = STARTING_INVENTORY.duplicate_deep()
