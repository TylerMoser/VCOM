## Dresses blocks with scenery the rules never see: a tree's leaves on the top
## block of its trunk.
##
## The rules read only the grid, so a tree's trunk is blocks stacked in the
## GridMap like any other, and that is what gives cover and stops sight. Its
## leaves are for show. On ready, every block named in [member scenes] gets an
## instance of its scene under this node, standing where the grid draws the
## block and turned the way the block is turned. A scene is built around its
## block the way the block's own model is: its origin in the middle of the
## block's base.
##
## Scenery is placed once. A block that leaves the grid later keeps it; none
## of the blocks dressed so far can break.
class_name BlockDecorations
extends Node3D

## MeshLibrary item name -> the scene placed on every block of that name.
@export var scenes: Dictionary[String, PackedScene] = {}

@export_group("Nodes")
@export var grid_map_path: NodePath = ^"../GridMap"


func _ready() -> void:
	var map := get_node_or_null(grid_map_path) as GridMap
	if map == null:
		push_error("BlockDecorations: no GridMap at '%s'." % grid_map_path)
		return
	for block in scenes:
		var scene := scenes[block]
		if scene == null:
			continue
		var item := map.mesh_library.find_item_by_name(block)
		if item < 0:
			push_error("BlockDecorations: no block named '%s' in the MeshLibrary." % block)
			continue
		for cell in map.get_used_cells_by_item(item):
			var decoration := scene.instantiate() as Node3D
			add_child(decoration)
			decoration.global_transform = TerrainDestruction.mesh_transform(map, cell)
