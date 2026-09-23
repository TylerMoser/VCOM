## What a unit shoots with.
##
## Only damage for now. Hit chance, critical hits, range falloff and ammo
## belong here too, so that what a shot does is a property of the gun rather
## than of the action that pulls the trigger.
##
## A weapon resource shared between units has to stay stateless. Give it
## [member Resource.resource_local_to_scene] once it holds something a single
## unit owns, such as rounds left in the magazine.
class_name Weapon
extends Resource

@export var display_name := "Rifle"
@export var damage := 4
