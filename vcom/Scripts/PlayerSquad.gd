## The player-controlled units, and which one is currently selected.
##
##   Select - Tab / Shift+Tab to cycle, or left-click a unit on the map.
class_name PlayerSquad
extends Node

signal selection_changed(unit: Unit)

## Group whose units make up the squad, in scene-tree order.
@export var unit_group := &"players"

var members: Array[Unit] = []
var selected: Unit
## While true, the selection cannot change. Set while an action plays out.
var locked := false


func _ready() -> void:
	for node in get_tree().get_nodes_in_group(unit_group):
		var unit := node as Unit
		if unit == null:
			push_warning("PlayerSquad: '%s' is in '%s' but is not a Unit." % [node.name, unit_group])
			continue
		members.append(unit)

	if not members.is_empty():
		select(members[0])


func _unhandled_input(event: InputEvent) -> void:
	if locked:
		return
	# Shift+Tab also matches the plain Tab action, so check it first.
	if event.is_action_pressed(&"select_previous_unit"):
		cycle(-1)
	elif event.is_action_pressed(&"select_next_unit"):
		cycle(1)
	elif event.is_action_pressed(&"select_unit") and event is InputEventMouseButton:
		var unit := unit_at((event as InputEventMouseButton).position)
		# A click on anything else is left for other handlers.
		if unit not in members:
			return
		select(unit)
	else:
		return
	get_viewport().set_input_as_handled()


## Makes [param unit] the selected unit. Units outside the squad are ignored.
func select(unit: Unit) -> void:
	if locked or unit == selected or unit not in members:
		return
	selected = unit
	selection_changed.emit(selected)


## Moves the selection [param step] places through the squad, wrapping around.
func cycle(step: int) -> void:
	if members.is_empty():
		return
	var index := members.find(selected)
	select(members[posmod(index + step, members.size())])


## The unit whose pick body is under [param screen_position], if any.
func unit_at(screen_position: Vector2) -> Unit:
	var camera := get_viewport().get_camera_3d()
	if camera == null:
		return null

	var from := camera.project_ray_origin(screen_position)
	var to := from + camera.project_ray_normal(screen_position) * camera.far
	var query := PhysicsRayQueryParameters3D.create(from, to, Unit.PICK_LAYER)
	var hit := get_viewport().find_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return null
	return (hit.collider as Node).get_parent() as Unit
