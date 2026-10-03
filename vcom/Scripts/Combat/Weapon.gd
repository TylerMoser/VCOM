## What a unit shoots with.
##
## Damage, to units and to terrain, and for a gun its magazine: how many
## rounds it holds ([member magazine]) and how many actions it takes to load a
## fresh one ([member reload]). Hit chance, critical hits and range falloff
## belong here too, so that what a shot does is a property of the gun rather
## than of the action that pulls the trigger.
##
## An [Item], so the party's weapons are listed in the inventory with its name
## and description. A weapon resource is shared between units, so it stays
## stateless: the rounds a unit has left are the unit's
## ([member Unit.rounds]), not the weapon's.
class_name Weapon
extends Item

@export var damage := 4
## How hard a round that strikes terrain hits it, on XCOM 2's scale: its
## conventional rifle does 5, its magnetic and beam rifles 10.
@export var environment_damage := 5

@export_group("Magazine")
## Shots a full magazine holds, each one fired spending one, a reaction shot
## too. Only a gun ([constant Item.GUN]) has one; 0 is a gun that never runs
## dry, with nothing to reload.
@export_range(0, 99, 1) var magazine := 5
## Actions it takes to load a fresh magazine ([ReloadAction]).
@export_range(1, 3, 1) var reload := 1


## Whether a unit shooting this counts its rounds: a gun with a magazine.
func has_magazine() -> bool:
	return has_tag(Item.GUN) and magazine > 0
