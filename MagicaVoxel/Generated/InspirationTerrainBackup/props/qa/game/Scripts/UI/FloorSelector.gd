## The map's floors, as a stack of sheets halfway down the left edge of the
## screen: on top a whole sheet, the whole map (UI/floor_top.svg), and under it
## the front edge of a sheet for each height its buildings can be cut away from
## ([member VoxelLevel.cutaway_heights]), highest first (UI/floor_level.svg).
## The top is chosen as the battle begins, and everything shows. Choosing a
## floor cuts away every building piece at that height and above, and whatever
## rests on them, to see inside ([method VoxelLevel.cut_away]); choosing the top
## shows them again. Only for show: nothing in the rules changes.
##
## The sheet chosen is drawn gold, those above it, cut away, faint, and those
## below it grey; the one under the mouse pointer lighter. A click on a sheet
## chooses it; PageUp / PageDown (floor_up / floor_down), the d-pad's up / down
## on the gamepad, go up or down a floor, stopping at either end; nothing else
## takes them. On a map with no heights to cut away from it never shows, and
## they do nothing there.
##
## The game changes the floor as well, when it must show a unit it gives its
## focus to, hidden with the cut or inside a house
## ([method CombatGrid.show_floor_of]): the sheet chosen follows the cut.
class_name FloorSelector
extends Control

## Pixels between it and the edge of the screen, and round the sheets inside.
const MARGIN := 16.0
const PADDING := 10.0
## The sheets' art: white, outlined, tinted as they are drawn.
const TOP_ART := preload("res://UI/floor_top.svg")
const FLOOR_ART := preload("res://UI/floor_level.svg")
## How far each floor is drawn below the one over it, and how far the first
## floor's art is below the top's: so its edge lies parallel to the top
## sheet's, a gap away.
const STEP := 16.0
const FIRST_FLOOR := 25.0
## The top sheet's art: how wide it is, and how far down its side corners and
## its bottom corner are, which the sheets under the pointer are told by.
const ART_WIDTH := 64.0
const SIDE_Y := 19.0
const BOTTOM_Y := 36.0
## How far in from either side of the art its side corners are.
const SIDE_INSET := 2.0

const BG_COLOR := Color(0.1, 0.11, 0.15, 0.85)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const CHOSEN_COLOR := Color(1.0, 0.86, 0.45)
const HOVER_COLOR := Color(0.88, 0.9, 0.95)
const SHOWN_COLOR := Color(0.6, 0.62, 0.68)
const CUT_COLOR := Color(0.6, 0.62, 0.68, 0.3)

@export var level_path: NodePath = ^"../../Level"

var _level: VoxelLevel
## The heights the level can be cut away from, highest first.
var _heights := PackedInt32Array()
## The sheet chosen, and the one under the pointer (-1 for none): 0 is the top,
## 1 the highest floor.
var _chosen := 0
var _hovered := -1


func _init() -> void:
	visible = false
	mouse_filter = MOUSE_FILTER_STOP
	mouse_default_cursor_shape = CURSOR_POINTING_HAND
	set_anchors_preset(PRESET_CENTER_LEFT)
	grow_vertical = GROW_DIRECTION_BOTH
	offset_left = MARGIN
	offset_right = MARGIN
	offset_top = 0.0
	offset_bottom = 0.0


func _ready() -> void:
	_level = get_node_or_null(level_path) as VoxelLevel
	if _level == null:
		push_error("FloorSelector: no VoxelLevel at '%s'." % level_path)
		set_process_unhandled_input(false)
		return
	var heights := {}
	for height in _level.cutaway_heights:
		heights[height] = true
	_heights = PackedInt32Array(heights.keys())
	_heights.sort()
	_heights.reverse()
	if _heights.is_empty():
		set_process_unhandled_input(false)
		return
	visible = true
	custom_minimum_size = Vector2(ART_WIDTH, _art_height()) + Vector2.ONE * PADDING * 2.0
	_level.cut_changed.connect(_on_cut_changed)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"floor_up"):
		choose(_chosen - 1)
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed(&"floor_down"):
		choose(_chosen + 1)
		get_viewport().set_input_as_handled()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		_hover(_sheet_at((event as InputEventMouseMotion).position))
	elif event is InputEventMouseButton and event.is_pressed():
		var button := event as InputEventMouseButton
		if button.button_index == MOUSE_BUTTON_LEFT:
			var sheet := _sheet_at(button.position)
			if sheet >= 0:
				choose(sheet)
		accept_event()


func _notification(what: int) -> void:
	if what == NOTIFICATION_MOUSE_EXIT:
		_hover(-1)


## Chooses sheet [param sheet] (0 the top, 1 the highest floor), kept within the
## stack, and cuts the level away to match.
func choose(sheet: int) -> void:
	sheet = clampi(sheet, 0, _heights.size())
	if sheet == _chosen or _level == null:
		return
	_chosen = sheet
	_level.cut_away(VoxelLevel.UNCUT if sheet == 0 else _heights[sheet - 1])
	queue_redraw()


## The sheet chosen: 0 the top, 1 the highest floor.
func chosen() -> int:
	return _chosen


func _draw() -> void:
	var panel := StyleBoxFlat.new()
	panel.bg_color = BG_COLOR
	panel.border_color = BORDER_COLOR
	panel.set_border_width_all(1)
	panel.set_corner_radius_all(4)
	draw_style_box(panel, Rect2(Vector2.ZERO, size))
	var corner := Vector2.ONE * PADDING
	# Lowest first, so a sheet's outline is drawn over the edge of the one below.
	for sheet in range(_heights.size(), 0, -1):
		var at := corner + Vector2(0.0, FIRST_FLOOR + (sheet - 1) * STEP)
		draw_texture(FLOOR_ART, at, _color_of(sheet))
	draw_texture(TOP_ART, corner, _color_of(0))


## The colour [param sheet] is tinted.
func _color_of(sheet: int) -> Color:
	if sheet == _chosen:
		return CHOSEN_COLOR
	if sheet == _hovered:
		return HOVER_COLOR
	return CUT_COLOR if sheet < _chosen else SHOWN_COLOR


## How tall the stack of sheets is drawn.
func _art_height() -> float:
	return FIRST_FLOOR + (_heights.size() - 1) * STEP + FLOOR_ART.get_height()


## The sheet under [param point], in its own space, or -1 for none: the top
## down to its lower edges, and each floor down to its own, each a band
## [constant STEP] deep sloping as the sheets do.
func _sheet_at(point: Vector2) -> int:
	var local := point - Vector2.ONE * PADDING
	if local.x < 0.0 or local.x > ART_WIDTH:
		return -1
	var half := ART_WIDTH * 0.5 - SIDE_INSET
	var toward_middle := 1.0 - clampf(absf(local.x - ART_WIDTH * 0.5) / half, 0.0, 1.0)
	var lower_edge := SIDE_Y + (BOTTOM_Y - SIDE_Y) * toward_middle
	if local.y <= lower_edge:
		return 0
	var sheet := ceili((local.y - lower_edge) / STEP)
	return sheet if sheet <= _heights.size() else -1


func _hover(sheet: int) -> void:
	if sheet != _hovered:
		_hovered = sheet
		queue_redraw()


## Something else cut the level away: the sheet chosen follows.
func _on_cut_changed() -> void:
	var at := _heights.find(_level.cut_level())
	var sheet := 0 if at < 0 else at + 1
	if sheet != _chosen:
		_chosen = sheet
		queue_redraw()
