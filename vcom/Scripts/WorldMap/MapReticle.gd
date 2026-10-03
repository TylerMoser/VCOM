## The world map's pointer for the gamepad: a reticle in the middle of the
## screen, which the left stick moves the map under ([WorldMapCamera]), and a
## column of prompts down the right saying what each button does. Shown only
## while the gamepad is in use ([InputDevice]); with the mouse, the mouse
## points instead.
##
## A acts on what the reticle is over, as the mouse's buttons act on what is
## under the pointer: it enters the village the party is in ([VillageMenu]),
## or sends the party to a village, or to that spot of land ([Party]). The
## prompt for A says which, and is left out over the sea.
##
## Hidden while a menu pauses the map, whose own prompts take over.
class_name MapReticle
extends CanvasLayer

## Under every menu, over the map.
const LAYER := 10
## Across the reticle's ring, in screen pixels.
const RADIUS := 13.0
const GAP := 5.0
const ARM := 7.0
const LINE := 2.0
const COLOR := Color(1.0, 1.0, 1.0, 0.95)
const OUTLINE_COLOR := Color(0.04, 0.04, 0.07, 0.8)
## Pixels between the prompts and the corner of the screen.
const HINTS_MARGIN := 16.0

@export var party_path: NodePath = ^"../Party"
## Which village A enters. Optional.
@export var village_menu_path: NodePath = ^"../VillageMenu"

var _party: Party
var _village_menu: VillageMenu
var _cross: Control
var _hints: ControlHints


func _init() -> void:
	layer = LAYER
	# Hides itself when a menu pauses the map, which it cannot notice paused.
	process_mode = PROCESS_MODE_ALWAYS

	_cross = Control.new()
	_cross.set_anchors_preset(Control.PRESET_FULL_RECT)
	_cross.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_cross.draw.connect(_draw_cross)
	add_child(_cross)

	_hints = ControlHints.new()
	_hints.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	_hints.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_hints.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_hints.offset_left = -HINTS_MARGIN
	_hints.offset_right = -HINTS_MARGIN
	_hints.offset_top = -HINTS_MARGIN
	_hints.offset_bottom = -HINTS_MARGIN
	add_child(_hints)


func _ready() -> void:
	_party = get_node_or_null(party_path) as Party
	if _party == null:
		push_error("MapReticle: no Party at '%s'; A sends nobody." % party_path)
	_village_menu = get_node_or_null(village_menu_path) as VillageMenu


func _process(_delta: float) -> void:
	visible = InputDevice.gamepad and not get_tree().paused
	if not visible:
		return
	_cross.queue_redraw()
	_hints.show_hints(_rows())


## The prompts for what each button does now.
func _rows() -> Array:
	var rows := []
	var accept := _accept_words()
	if not accept.is_empty():
		rows.append([[&"A"], accept])
	rows.append([[&"LS"], "Move map"])
	rows.append([[&"RS"], "Zoom"])
	rows.append([[&"L3"], "Find the party"])
	rows.append([[&"Menu"], "Menu"])
	return rows


## What A does with the reticle where it is, or nothing.
func _accept_words() -> String:
	if _party == null:
		return ""
	if _village_menu != null:
		var village := _village_menu.enterable()
		if village != null and not village.locations.is_empty():
			return "Enter %s" % village.display_name
	var destination := Destination.find_under_pointer(get_tree())
	if destination != null:
		return "Go to %s" % destination.display_name
	return "Go here" if _party.can_go_to(_party.pointed_at()) else ""


## A ring with a gap all round, and a short arm out of it each way.
func _draw_cross() -> void:
	var middle := _cross.size * 0.5
	for pass_index in 2:
		var outline := pass_index == 0
		var color := OUTLINE_COLOR if outline else COLOR
		var width := LINE + (2.0 if outline else 0.0)
		_cross.draw_arc(middle, RADIUS, 0.0, TAU, 40, color, width, true)
		for direction: Vector2 in [Vector2.LEFT, Vector2.RIGHT, Vector2.UP, Vector2.DOWN]:
			_cross.draw_line(middle + direction * GAP, middle + direction * (GAP + ARM), color, width, true)
