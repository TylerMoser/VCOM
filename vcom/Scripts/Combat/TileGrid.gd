## The optional tile grid: a faint line along every block boundary on the
## ground, for a player who wants to count tiles. Off until the player turns it
## on, with G in combat or Tile Grid on the pause menu's System tab; it then
## stays as they left it, battle after battle, until the game closes. Only for
## show: nothing in the rules reads it.
##
## A node in each combat map. As the map loads it gives the ground blocks
## ([member blocks]) TileGrid.gdshader, which draws them exactly as the
## importer's material does until the grid is on. The lines answer to one
## global shader uniform, [code]tile_grid[/code] (project.godot's
## shader_globals), so turning them on or off reaches every ground block at
## once, worn ones included, wherever it is called from.
##
## It must come before TerrainDestruction in the tree: TerrainDestruction reads
## each wearable block's material as it readies, and draws worn blocks with it.
class_name TileGrid
extends Node

const SHADER := preload("res://Scripts/Combat/TileGrid.gdshader")
const GLOBAL := &"tile_grid"

## Whether the grid is showing. Kept here rather than read back from the
## RenderingServer, which would have to stop and wait for the render thread.
static var shown := false

## The MeshLibrary items the grid is drawn on: the ground.
@export var blocks: PackedStringArray = ["BrightGrass1"]
@export var grid_map_path: NodePath = ^"../GridMap"


## Shows or hides the grid on every ground block.
static func set_shown(on: bool) -> void:
	shown = on
	RenderingServer.global_shader_parameter_set(GLOBAL, 1.0 if on else 0.0)


static func toggle() -> void:
	set_shown(not shown)


func _ready() -> void:
	var map := get_node_or_null(grid_map_path) as GridMap
	if map == null:
		push_error("TileGrid: no GridMap at '%s'." % grid_map_path)
		return
	# The meshes are the imported .vox resources, shared by every map that
	# uses them, so the material goes on the mesh rather than on a node.
	var material := ShaderMaterial.new()
	material.shader = SHADER
	var library := map.mesh_library
	for id in library.get_item_list():
		if library.get_item_name(id) in blocks:
			var mesh := library.get_item_mesh(id)
			for surface in mesh.get_surface_count():
				mesh.surface_set_material(surface, material)
	set_shown(shown)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"toggle_grid"):
		toggle()
		get_viewport().set_input_as_handled()
