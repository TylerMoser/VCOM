@tool
## Where a squad member starts a battle: [PlayerSquad] spawns one character
## on the tile each marker is over, the first on the roster at the first
## marker, and so on in the markers' order among their siblings.
##
## In the editor it draws a see-through square on that tile and its number
## over it, so the starts can be seen and dragged about on a map of blocks
## where the marker's own cross is hard to spot. It need not sit exactly on
## the tile: the square shows the tile it counts as over, the one whose floor
## is at or just below it, as [method CombatGrid.tile_at] finds it (a grid of
## 1-metre cells at the origin, as every map has). Nothing is drawn in game.
class_name SquadStart
extends Marker3D

## Orange, a colour none of the game's tile highlights use.
const TILE_COLOR := Color(1.0, 0.5, 0.1, 0.6)
const NUMBER_COLOR := Color(1.0, 0.85, 0.6)
## How far over the floor the square is drawn, to keep it off the block top.
const LIFT := 0.02

var _square: MeshInstance3D
var _number: Label3D


func _ready() -> void:
	set_process(false)
	if Engine.is_editor_hint():
		show_preview()


## Draws the square and the number, and keeps them on the marker's tile as it
## is moved. Called in the editor; nothing calls it in game.
func show_preview() -> void:
	if _square != null:
		return
	var plane := PlaneMesh.new()
	plane.size = Vector2(0.9, 0.9)
	var material := StandardMaterial3D.new()
	material.albedo_color = TILE_COLOR
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	plane.material = material
	_square = MeshInstance3D.new()
	_square.mesh = plane
	_square.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	# Internal and unowned, so the scene never saves them.
	add_child(_square, false, INTERNAL_MODE_BACK)

	_number = Label3D.new()
	_number.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_number.no_depth_test = true
	_number.font_size = 96
	_number.outline_size = 24
	_number.pixel_size = 0.01
	_number.modulate = NUMBER_COLOR
	add_child(_number, false, INTERNAL_MODE_BACK)
	set_process(true)
	_process(0.0)


func _process(_delta: float) -> void:
	if _square == null:
		return
	# Level and square to the grid whatever the marker's own turn.
	var ground := floor_position()
	_square.global_transform = Transform3D(Basis(), ground + Vector3(0.0, LIFT, 0.0))
	_number.global_transform = Transform3D(Basis(), ground + Vector3(0.0, 0.8, 0.0))
	_number.text = str(number())


## Which squad member starts here: 1 for the first [SquadStart] among its
## siblings, and so on.
func number() -> int:
	var count := 1
	if get_parent() == null:
		return count
	for sibling in get_parent().get_children():
		if sibling == self:
			break
		if sibling is SquadStart:
			count += 1
	return count


## The middle of the floor of the tile the marker is over, for the preview.
## The game asks the [CombatGrid] instead.
func floor_position() -> Vector3:
	var at := global_position
	return Vector3(floorf(at.x) + 0.5, floorf(at.y + 0.5), floorf(at.z) + 0.5)
