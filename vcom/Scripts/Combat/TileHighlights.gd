## Coloured squares laid on top of tiles, Final Fantasy Tactics style.
##
## Callers own named layers, so the move range and the selected-unit marker
## can each be replaced without touching the other. The layer set most
## recently draws on top, except that a layer set [code]on_top[/code] (the
## gamepad's tile cursor) draws over every other whenever they were set.
class_name TileHighlights
extends MultiMeshInstance3D

## Width of a square, as a fraction of a tile.
const SQUARE_SIZE := 0.9
## Height above the floor, to keep the square from z-fighting with it.
const LIFT := 0.02
## Opacity of a square's fill; its border is always near-solid.
const DEFAULT_FILL := 0.55

@export var grid_path: NodePath = ^"../CombatGrid"

var _grid: CombatGrid
## Layer name -> { tile (Vector3i): Color }.
var _layers := {}
## Layer name -> fill opacity.
var _fills := {}
## Layers that draw over the rest, as a set.
var _on_top := {}


func _ready() -> void:
	_grid = get_node_or_null(grid_path) as CombatGrid
	if _grid == null:
		push_error("TileHighlights: no CombatGrid at '%s'." % grid_path)

	var square := PlaneMesh.new()
	square.size = Vector2(SQUARE_SIZE, SQUARE_SIZE)

	var material := ShaderMaterial.new()
	material.shader = preload("res://Scripts/Combat/TileHighlight.gdshader")
	material_override = material
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

	multimesh = MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.use_colors = true
	multimesh.use_custom_data = true
	multimesh.mesh = square


## Replaces the squares in [param layer] with [param tiles], a dictionary
## of tile (Vector3i) -> Color, filled at [param fill] opacity. With
## [param on_top] it stays over every layer set later too.
func set_layer(layer: StringName, tiles: Dictionary, fill := DEFAULT_FILL, on_top := false) -> void:
	# Re-adding the key moves the layer to the end, so it draws on top.
	_layers.erase(layer)
	_layers[layer] = tiles
	_fills[layer] = fill
	if on_top:
		_on_top[layer] = true
	else:
		_on_top.erase(layer)
	_rebuild()


func clear_layer(layer: StringName) -> void:
	_fills.erase(layer)
	_on_top.erase(layer)
	if _layers.erase(layer):
		_rebuild()


func _rebuild() -> void:
	var count := 0
	for tiles: Dictionary in _layers.values():
		count += tiles.size()
	multimesh.instance_count = count

	var index := 0
	var order: Array = _layers.keys().filter(func(layer: StringName) -> bool: return not _on_top.has(layer))
	order.append_array(_layers.keys().filter(func(layer: StringName) -> bool: return _on_top.has(layer)))
	for layer: StringName in order:
		var tiles: Dictionary = _layers[layer]
		var custom := Color(_fills[layer], 0.0, 0.0, 0.0)
		for tile: Vector3i in tiles:
			var position := to_local(_grid.tile_position(tile)) + Vector3.UP * LIFT
			multimesh.set_instance_transform(index, Transform3D(Basis.IDENTITY, position))
			multimesh.set_instance_color(index, tiles[tile])
			multimesh.set_instance_custom_data(index, custom)
			index += 1
