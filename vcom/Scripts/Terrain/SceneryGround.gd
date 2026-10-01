## The ground of the scenery round a combat map: one plane in the grass's
## colour, a hair below the top of the battlefield's ground, under the trees
## the scenery's GridMap paints round the battlefield.
##
## It covers the battlefield too, where the battlefield's own ground hides it,
## and on ready it has that part cut out of it: every column the bottom of the
## battlefield's GridMap fills. A crater worn into the battlefield's floor
## ([VoxelTerrain]) then shows the crater, not this plane a hair below the top
## of the floor running through it. Anywhere the battlefield leaves empty, its
## corners, it still covers.
##
## Its mesh is a [PlaneMesh] in the scene, sized and placed as the scenery
## needs, and is rebuilt from it with the same material.
class_name SceneryGround
extends MeshInstance3D

## The battlefield, whose bottom layer is cut out of the plane.
@export var grid_map_path: NodePath = ^"../../GridMap"


func _ready() -> void:
	var map := get_node_or_null(grid_map_path) as GridMap
	if map == null:
		push_error("SceneryGround: no GridMap at '%s', so the plane is left whole." % grid_map_path)
		return
	var plane := mesh as PlaneMesh
	if plane == null:
		push_error("SceneryGround: needs a PlaneMesh to cut the battlefield out of.")
		return
	var cells := map.get_used_cells()
	if cells.is_empty():
		return
	var bottom := cells[0].y
	for cell in cells:
		bottom = mini(bottom, cell.y)
	# Every column the battlefield's floor fills, by where its least corner is
	# across the ground, in the world.
	var holes := {}
	for cell in cells:
		if cell.y == bottom:
			var corner := map.to_global(map.map_to_local(cell) - map.cell_size * 0.5)
			holes[Vector2i(roundi(corner.x), roundi(corner.z))] = true

	var middle := global_position
	var least := Vector2i(roundi(middle.x - plane.size.x * 0.5), roundi(middle.z - plane.size.y * 0.5))
	var most := Vector2i(roundi(middle.x + plane.size.x * 0.5), roundi(middle.z + plane.size.y * 0.5))
	# Each row of cells across the plane is cut into the runs between holes,
	# and rows cut the same way are merged into one rectangle.
	var rectangles: Array[Rect2i] = []
	var runs := _runs(least.y, least.x, most.x, holes)
	var start := least.y
	for z in range(least.y + 1, most.y + 1):
		var next := _runs(z, least.x, most.x, holes) if z < most.y else PackedInt32Array()
		if z < most.y and next == runs:
			continue
		for run in range(0, runs.size(), 2):
			rectangles.append(Rect2i(runs[run], start, runs[run + 1] - runs[run], z - start))
		runs = next
		start = z

	var built := ArrayMesh.new()
	if not rectangles.is_empty():
		built.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, _arrays(rectangles, middle.y))
		built.surface_set_material(0, plane.material)
	mesh = built


## The runs of row [param z] from [param from] to [param to] with no hole, as
## pairs: where each starts and where it ends.
static func _runs(z: int, from: int, to: int, holes: Dictionary) -> PackedInt32Array:
	var runs := PackedInt32Array()
	var x := from
	while x < to:
		if holes.has(Vector2i(x, z)):
			x += 1
			continue
		var end := x
		while end < to and not holes.has(Vector2i(end, z)):
			end += 1
		runs.append_array([x, end])
		x = end
	return runs


## The arrays of a surface of [param rectangles] across the ground, at the
## height [param y] in the world, facing up, in this node's own space.
func _arrays(rectangles: Array[Rect2i], y: float) -> Array:
	var to_local := global_transform.affine_inverse()
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	for rectangle in rectangles:
		var a := to_local * Vector3(rectangle.position.x, y, rectangle.position.y)
		var b := to_local * Vector3(rectangle.end.x, y, rectangle.position.y)
		var c := to_local * Vector3(rectangle.end.x, y, rectangle.end.y)
		var d := to_local * Vector3(rectangle.position.x, y, rectangle.end.y)
		# Clockwise seen from above, Godot's front.
		vertices.append_array([a, b, c, a, c, d])
	normals.resize(vertices.size())
	normals.fill(Vector3.UP)
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	return arrays
