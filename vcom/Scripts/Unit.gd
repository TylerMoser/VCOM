## A character on the combat map: its health and its per-turn action budget.
##
## The unit's colour comes from the material on its Mesh child, so the scene
## stays the single place it is set. UI reads [member color] until real
## portraits exist.
class_name Unit
extends Node3D

signal health_changed(health: int, max_health: int)
signal actions_changed(remaining: int, per_turn: int)

## Physics layer holding the bodies that mouse clicks on units are tested
## against. Nothing collides with it, so it never affects movement.
const PICK_LAYER := 1 << 1
## Every unit, whichever side it is on.
const GROUP := &"units"

@export var display_name := "Unit"
@export var max_health := 10
@export var actions_per_turn := 3
## Tiles the unit can walk for each action point spent moving.
@export var move_range := 4

var health := 0:
	set(value):
		health = clampi(value, 0, max_health)
		health_changed.emit(health, max_health)

var actions_remaining := 0:
	set(value):
		actions_remaining = clampi(value, 0, actions_per_turn)
		actions_changed.emit(actions_remaining, actions_per_turn)

## Placeholder identity colour, taken from the Mesh child's material.
var color: Color:
	get:
		var mesh := get_node_or_null(^"Mesh") as MeshInstance3D
		if mesh != null:
			var material := mesh.get_active_material(0) as BaseMaterial3D
			if material != null:
				return material.albedo_color
		return Color.WHITE


func _ready() -> void:
	add_to_group(GROUP)
	health = max_health
	actions_remaining = actions_per_turn
	_add_pick_body()


## Refills the action budget at the start of this unit's turn.
func start_turn() -> void:
	actions_remaining = actions_per_turn


## Spends [param cost] actions. Returns false, spending nothing, if there are
## not enough left.
func spend_actions(cost: int = 1) -> bool:
	if cost > actions_remaining:
		return false
	actions_remaining -= cost
	return true


## Gives the unit a clickable body shaped like its Mesh child.
func _add_pick_body() -> void:
	var mesh := get_node_or_null(^"Mesh") as MeshInstance3D
	if mesh == null or mesh.mesh == null:
		return

	var shape := CollisionShape3D.new()
	shape.shape = mesh.mesh.create_convex_shape()

	var body := StaticBody3D.new()
	body.name = &"PickBody"
	body.collision_layer = PICK_LAYER
	body.collision_mask = 0
	body.transform = mesh.transform
	body.add_child(shape)
	add_child(body)
