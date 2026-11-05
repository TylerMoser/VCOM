@tool
## Turns a GridMap into a level: every block a piece of the same name in the
## middle of its cell, turned as the block was. How the combat maps came over
## from the GridMaps they were painted in, and what the level editor's Import
## does with any GridMap still about.
class_name LevelImport
extends RefCounted


## A level holding every block of [param grid] as a piece, named after its
## MeshLibrary item. The cells are taken in order (x, then y, then z), so the
## same grid always gives the same level; a GridMap holds one block a cell, so
## no two pieces overlap.
static func from_grid_map(grid: GridMap) -> LevelData:
	var data := LevelData.new()
	var cells := grid.get_used_cells()
	cells.sort()
	for cell in cells:
		var item := grid.get_cell_item(cell)
		var id := StringName(grid.mesh_library.get_item_name(item))
		data.add(id, LevelData.centre_slot(cell), turn_of(grid, grid.get_cell_item_orientation(cell)))
	return data


## The quarter turns about up that [param grid]'s orientation [param index]
## is. A block turned any other way (on its side) is placed unturned, with a
## warning: a piece only ever turns about up.
static func turn_of(grid: GridMap, index: int) -> int:
	var basis := grid.get_basis_with_orthogonal_index(index)
	for turn in 4:
		if basis.is_equal_approx(Basis(Vector3.UP, turn * PI * 0.5)):
			return turn
	push_warning("LevelImport: a block turned off its base (orientation %d) is placed upright." % index)
	return 0
