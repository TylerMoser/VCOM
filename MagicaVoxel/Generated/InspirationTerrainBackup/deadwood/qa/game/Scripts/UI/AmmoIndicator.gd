## The selected squad member's magazine, in the bottom-right corner: a
## rectangle for every round it holds, filled while loaded and hollow once
## fired, so a glance says how many shots are left before a reload
## ([member Unit.rounds]). Its edge turns red with the magazine empty.
##
## Shown only while the selected unit has a gun with a magazine
## ([method Unit.has_magazine]); it follows the selection and every round
## fired or reloaded. The gamepad's prompts stack above it
## ([ActionController]).
extends Control

## Pixels between it and the corner of the screen.
const MARGIN := 16.0
const PADDING := 10.0
## A round's rectangle, and the gap between two.
const ROUND_SIZE := Vector2(8.0, 26.0)
const ROUND_GAP := 5.0

const BG_COLOR := Color(0.1, 0.11, 0.15, 0.85)
const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const EMPTY_BORDER_COLOR := Color(0.95, 0.35, 0.3)
const LOADED_COLOR := Color(1.0, 0.86, 0.45)
const SPENT_COLOR := Color(0.45, 0.47, 0.53)

@export var squad_path: NodePath = ^"../../PlayerSquad"

var _squad: PlayerSquad
## The unit whose magazine is shown, or null.
var _unit: Unit
var _rounds := 0
var _magazine := 0


func _init() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	visible = false
	set_anchors_preset(PRESET_BOTTOM_RIGHT)
	grow_horizontal = GROW_DIRECTION_BEGIN
	grow_vertical = GROW_DIRECTION_BEGIN
	offset_left = -MARGIN
	offset_right = -MARGIN
	offset_top = -MARGIN
	offset_bottom = -MARGIN


func _ready() -> void:
	_squad = get_node_or_null(squad_path) as PlayerSquad
	if _squad == null:
		push_error("AmmoIndicator: no PlayerSquad at '%s'." % squad_path)
		return
	if not _squad.is_node_ready():
		await _squad.ready
	_squad.selection_changed.connect(_show_unit)
	_show_unit(_squad.selected)


func _show_unit(unit: Unit) -> void:
	if is_instance_valid(_unit) and _unit.rounds_changed.is_connected(_on_rounds_changed):
		_unit.rounds_changed.disconnect(_on_rounds_changed)
	_unit = unit if is_instance_valid(unit) and unit.has_magazine() else null
	if _unit == null:
		visible = false
		return
	_unit.rounds_changed.connect(_on_rounds_changed)
	_on_rounds_changed(_unit.rounds, _unit.magazine_size())


func _on_rounds_changed(rounds: int, magazine: int) -> void:
	_rounds = rounds
	_magazine = magazine
	visible = magazine > 0
	# Sized to the magazine and anchored at the corner: shrunk to nothing at
	# its bottom-right first, then grown up and left by its minimum size.
	custom_minimum_size = Vector2(
		PADDING * 2.0 + magazine * ROUND_SIZE.x + maxi(magazine - 1, 0) * ROUND_GAP,
		PADDING * 2.0 + ROUND_SIZE.y,
	)
	offset_left = offset_right
	offset_top = offset_bottom
	queue_redraw()


func _draw() -> void:
	var panel := StyleBoxFlat.new()
	panel.bg_color = BG_COLOR
	panel.border_color = EMPTY_BORDER_COLOR if _rounds == 0 else BORDER_COLOR
	panel.set_border_width_all(1 if _rounds > 0 else 2)
	panel.set_corner_radius_all(4)
	draw_style_box(panel, Rect2(Vector2.ZERO, size))
	# Spent rounds on the left, loaded ones on the right, as a magazine empties
	# from the top.
	var spent := _magazine - _rounds
	for index in _magazine:
		var at := Vector2(PADDING + index * (ROUND_SIZE.x + ROUND_GAP), (size.y - ROUND_SIZE.y) * 0.5)
		var round_rect := Rect2(at, ROUND_SIZE)
		if index < spent:
			draw_rect(round_rect.grow(-1.0), SPENT_COLOR, false, 2.0)
		else:
			draw_rect(round_rect, LOADED_COLOR)
