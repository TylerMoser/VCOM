## A character on the combat map: its health and its per-turn action budget.
##
## The unit's colour comes from the material on its Mesh child, so the scene
## stays the single place it is set. UI reads [member color] until real
## portraits exist.
class_name Unit
extends Node3D

signal health_changed(health: int, max_health: int)
signal actions_changed(remaining: int, per_turn: int)
## Emitted as the unit leaves the map, while it is still whole enough to be
## read from. Whoever was holding on to it should let go.
signal died

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
## How far the unit can see, and so shoot, in tiles.
@export var sight_range := 20
## The gun this unit shoots with. A plain rifle if the scene leaves it unset.
@export var weapon: Weapon

@export_group("Marksmanship")
## Chance to hit before anything about the shot is taken into account.
@export var aim := 90
## Taken off the chance of anyone shooting at this unit.
@export var evasion := 0
## Added per tile this unit stands above what it is shooting at, and taken
## off per tile below it.
@export var height_bonus := 5
## Taken off per full [constant HitChance.DISTANCE_STEP] tiles to the target.
@export var distance_penalty := 5

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
	if weapon == null:
		weapon = Weapon.new()
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


## Takes [param amount] off the unit's health, and takes the unit off the map
## if that finishes it.
func take_damage(amount: int) -> void:
	health -= amount
	if health <= 0:
		die()


## Fires at [param target] with [param chance] in 100 of landing. Returns
## whether it hit. Both the player's [ShootAction] and the enemy turn come
## through here, so a shot means the same thing whoever takes it.
func shoot_at(target: Unit, chance: int) -> bool:
	if not HitChance.roll(chance):
		return false
	target.take_damage(weapon.damage)
	return true


## Removes the unit from play. It leaves its groups at once rather than when
## the node is freed, so nothing shoots at it or walks around it in the
## meantime.
func die() -> void:
	died.emit()
	for group in get_groups():
		remove_from_group(group)
	queue_free()


## Walks through [param points] in order, taking [param seconds_per_step]
## for each. Await it to wait until the unit arrives.
func walk(points: Array[Vector3], seconds_per_step: float) -> void:
	if points.is_empty():
		return
	var tween := create_tween()
	for point in points:
		tween.tween_property(self, ^"global_position", point, seconds_per_step)
	await tween.finished


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
