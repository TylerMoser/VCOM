## What a unit shoots with.
##
## Only damage for now, to units and to terrain. Hit chance, critical hits,
## range falloff and ammo belong here too, so that what a shot does is a
## property of the gun rather than of the action that pulls the trigger.
##
## A weapon resource shared between units has to stay stateless. Give it
## [member Resource.resource_local_to_scene] once it holds something a single
## unit owns, such as rounds left in the magazine.
class_name Weapon
extends Resource

@export var display_name := "Rifle"
@export var damage := 4
## How hard a round that strikes terrain hits it, on XCOM 2's scale: its
## conventional rifle does 5, its magnetic and beam rifles 10.
@export var environment_damage := 5
