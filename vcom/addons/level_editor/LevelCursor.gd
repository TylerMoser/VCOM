@tool
## What the level editor shows under the mouse in the 3D view: a grid on the
## floor being painted, round the cursor; a ghost of every piece a click would
## place, in its own colours; and the box of every slot it would paint or
## erase, red to erase. Only ever in the editor: it is no part of the scene,
## and is never saved.
extends Node3D

## How many cells across the floor's grid shows.
const GRID_CELLS := 12

var _grid: MeshInstance3D
var _ghosts: Array[MeshInstance3D] = []
var _boxes: Array[MeshInstance3D] = []
var _ghost_material: StandardMaterial3D
var _paint_box: StandardMaterial3D
var _erase_box: StandardMaterial3D
var _box_mesh: BoxMesh


func _init() -> void:
	name = &"LevelCursor"
	_ghost_material = StandardMaterial3D.new()
	_ghost_material.vertex_color_use_as_albedo = true
	_ghost_material.vertex_color_is_srgb = true
	_ghost_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_ghost_material.albedo_color = Color(1, 1, 1, 0.6)
	_paint_box = _box_material(Color(0.35, 0.75, 1.0, 0.18))
	_erase_box = _box_material(Color(1.0, 0.25, 0.2, 0.3))
	_box_mesh = BoxMesh.new()
	_box_mesh.size = Vector3.ONE * 1.02
	_grid = MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * GRID_CELLS
	_grid.mesh = plane
	var lines := ShaderMaterial.new()
	lines.shader = _grid_shader()
	_grid.material_override = lines
	_grid.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_grid)


## Shows [param placements] (as [method LevelEditing.placements] gives them)
## ghosted in [param level], from [param library], or with [param erasing]
## the boxes of [param slots] in red; the grid on the floor [param floor] round
## [param at], in the level's space.
func show_at(level: VoxelLevel, library: PieceLibrary, placements: Array, slots: Array[Vector3i], erasing: bool, floor_level: int, at: Vector3) -> void:
	visible = true
	_grid.position = Vector3(floorf(at.x) + 0.5, floor_level + 0.003, floorf(at.z) + 0.5)
	(_grid.material_override as ShaderMaterial).set_shader_parameter(&"origin", _grid.position)
	var used := 0
	var boxes := 0
	if not erasing:
		for placed: Array in placements:
			var kind := library.find(placed[0]) if library != null else null
			if kind == null or kind.model == null:
				continue
			var ghost := _ghost(used)
			used += 1
			ghost.mesh = kind.model
			var turn := Basis(Vector3.UP, int(placed[2]) * PI * 0.5)
			ghost.transform = Transform3D(turn, LevelData.box_center(placed[1])) * kind.model_transform
			ghost.visible = true
			var box := _box(boxes)
			boxes += 1
			box.material_override = _paint_box
			box.position = LevelData.box_center(placed[1])
			box.visible = true
	else:
		for slot in slots:
			var box := _box(boxes)
			boxes += 1
			box.material_override = _erase_box
			box.position = LevelData.box_center(slot)
			box.visible = true
	for index in range(used, _ghosts.size()):
		_ghosts[index].visible = false
	for index in range(boxes, _boxes.size()):
		_boxes[index].visible = false


func _ghost(index: int) -> MeshInstance3D:
	while _ghosts.size() <= index:
		var ghost := MeshInstance3D.new()
		ghost.material_override = _ghost_material
		ghost.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(ghost)
		_ghosts.append(ghost)
	return _ghosts[index]


func _box(index: int) -> MeshInstance3D:
	while _boxes.size() <= index:
		var box := MeshInstance3D.new()
		box.mesh = _box_mesh
		box.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(box)
		_boxes.append(box)
	return _boxes[index]


static func _box_material(color: Color) -> StandardMaterial3D:
	var made := StandardMaterial3D.new()
	made.albedo_color = color
	made.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	made.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	made.cull_mode = BaseMaterial3D.CULL_DISABLED
	made.no_depth_test = false
	return made


## A line on every cell boundary, where the pieces on edges stand, fading out
## toward the grid's rim. Counted in the level's space ([code]origin[/code],
## the grid's place in it), so the lines fall on the cells wherever the level is.
static func _grid_shader() -> Shader:
	var shader := Shader.new()
	shader.code = """
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled;
uniform vec3 origin;
varying vec3 local;
void vertex() {
	local = VERTEX + origin;
}
void fragment() {
	vec2 at = local.xz;
	vec2 cell = abs(fract(at) - 0.5);
	vec2 fw = max(fwidth(at), vec2(1e-4));
	float edge = 1.0 - smoothstep(0.0, 1.5, min((0.5 - cell.x) / fw.x, (0.5 - cell.y) / fw.y));
	vec2 from_middle = abs(UV - 0.5) * 2.0;
	float fade = 1.0 - smoothstep(0.3, 1.0, length(from_middle));
	ALBEDO = vec3(1.0);
	ALPHA = edge * 0.35 * fade;
}
"""
	return shader
