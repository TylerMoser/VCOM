## The optional tile grid: a faint line along every block boundary on the
## ground, for a player who wants to count tiles. Off until the player turns it
## on, with G in combat or Tile Grid on the pause menu's System tab; it then
## stays as they left it, battle after battle, until the game closes. Only for
## show: nothing in the rules reads it.
##
## A node in each combat map. The lines are drawn by the level's own shader
## (Voxels.gdshader) on the voxels of every kind of piece that asks for
## them ([member PieceKind.tile_grid]): the ground's, worn or not. They answer
## to one global shader uniform, [code]tile_grid[/code] (project.godot's
## shader_globals), so turning them on or off reaches every ground voxel at
## once, wherever it is called from.
class_name TileGrid
extends Node

const GLOBAL := &"tile_grid"

## Whether the grid is showing. Kept here rather than read back from the
## RenderingServer, which would have to stop and wait for the render thread.
static var shown := false


## Shows or hides the grid on every ground block.
static func set_shown(on: bool) -> void:
	shown = on
	RenderingServer.global_shader_parameter_set(GLOBAL, 1.0 if on else 0.0)


static func toggle() -> void:
	set_shown(not shown)


func _ready() -> void:
	set_shown(shown)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"toggle_grid"):
		toggle()
		get_viewport().set_input_as_handled()
