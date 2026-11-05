## The switch for the new map's borders (Scenes/Map.tscn): B, or the gamepad's
## R3 (toggle_borders), hides every border, the kingdoms', the duchies' and
## the counties', and shows them again. They start shown.
##
## It fades the two groups the borders are drawn in, Borders and
## BordersOverLakes, by their modulate, and hides nothing: at nothing the
## renderer skips them, where showing a hidden Line2D builds it again (some
## 50 ms for the borders' 730 lines). The map's level of detail ([MapDetail])
## fades the ranks under those groups by their own modulate, so the two never
## meet: a rank out of its tier stays out when the borders come back, and the
## borders' widths are kept up with the zoom while they are hidden, so they
## come back right.
class_name BorderSwitch
extends Node

## The groups the borders are drawn in, under the map. A border's line along
## a river, a lake or a road is in these too, and goes with them.
const GROUPS: Array[NodePath] = [^"Borders", ^"BordersOverLakes"]

## The map: the node the groups are under.
@export var map_path: NodePath = ^".."

## Whether the borders show.
var shown := true:
	set(value):
		shown = value
		_apply()

var _groups: Array[CanvasItem] = []
# Each group's alpha as the scene has it, to go back to.
var _alpha: Array[float] = []


func _ready() -> void:
	var map := get_node_or_null(map_path)
	if map == null:
		push_error("BorderSwitch: no map at '%s'; the borders cannot be hidden." % map_path)
		return
	for path in GROUPS:
		var group := map.get_node_or_null(path) as CanvasItem
		if group == null:
			push_error("BorderSwitch: nothing at '%s' under the map." % path)
			continue
		_groups.append(group)
		_alpha.append(group.modulate.a)
	_apply()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"toggle_borders"):
		shown = not shown
		get_viewport().set_input_as_handled()


func _apply() -> void:
	for i in _groups.size():
		_groups[i].modulate.a = _alpha[i] if shown else 0.0
