## A character on the combat map: its health and its per-turn action budget.
##
## The unit's colour comes from the material on its Mesh child, so the scene
## stays the single place it is set. UI reads [member color] until real
## portraits exist.
class_name Unit
extends Node3D

signal health_changed(health: int, max_health: int)
signal actions_changed(remaining: int, per_turn: int)

@export var display_name := "Unit"
@export var max_health := 10
@export var actions_per_turn := 3

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
	health = max_health
	actions_remaining = actions_per_turn


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
