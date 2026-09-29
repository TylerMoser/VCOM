## A place on the world map the party can be sent to, such as a village.
##
## It is only a target: a right click on its icon sends the party to the
## destination's own position rather than to the pixel clicked, so every trip
## there ends in the same spot. Hovering over the icon shows [member display_name] in a tooltip
## above it.
##
## Like the party dot, the icon and tooltip are drawn at a fixed size on
## screen, whatever the camera's zoom, and the icon is centred on the node.
## Place destinations on land: the party warns at the start about any it
## could never reach.
class_name Destination
extends Node2D

const GROUP := &"destinations"

## Shown in the tooltip when the icon is hovered.
@export var display_name := "Village"
@export var icon: Texture2D:
	set(value):
		icon = value
		queue_redraw()

@export_group("Look")
## Sizes are in screen pixels. The icon's width follows the texture's shape.
@export var icon_height := 32.0
@export var tooltip_font_size := 14
## Space between the top of the icon and the bottom of the tooltip.
@export var tooltip_gap := 4.0

const TOOLTIP_BG_COLOR := Color(0.1, 0.11, 0.15, 0.88)
const TOOLTIP_BORDER_COLOR := Color(0.78, 0.8, 0.85, 0.6)
const TOOLTIP_TEXT_COLOR := Color(0.92, 0.93, 0.95)

var hovered := false:
	set(value):
		if value == hovered:
			return
		hovered = value
		# Over any destination drawn after it.
		z_index = 1 if hovered else 0
		queue_redraw()

var _tooltip_style := StyleBoxFlat.new()
## Screen pixels per map pixel as last drawn, to redraw when the zoom changes.
var _drawn_scale := 0.0


func _init() -> void:
	_tooltip_style.bg_color = TOOLTIP_BG_COLOR
	_tooltip_style.border_color = TOOLTIP_BORDER_COLOR
	_tooltip_style.set_border_width_all(1)
	_tooltip_style.set_corner_radius_all(4)
	_tooltip_style.content_margin_left = 8
	_tooltip_style.content_margin_right = 8
	_tooltip_style.content_margin_top = 4
	_tooltip_style.content_margin_bottom = 4


func _enter_tree() -> void:
	# Joined on entering rather than when ready, so the party finds every
	# destination from its own _ready wherever it sits in the tree.
	add_to_group(GROUP)


func _ready() -> void:
	if icon == null:
		push_warning("Destination '%s': no icon, so it cannot be seen or clicked." % name)


func _process(_delta: float) -> void:
	hovered = is_under_mouse()
	if not is_equal_approx(_screen_scale(), _drawn_scale):
		queue_redraw()


func _draw() -> void:
	_drawn_scale = _screen_scale()
	if icon == null:
		return
	# Draw in screen pixels from here on.
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE / _drawn_scale)
	var box := _icon_rect()
	draw_texture_rect(icon, box, false)

	if hovered and not display_name.is_empty():
		var font := ThemeDB.fallback_font
		var text_size := font.get_string_size(
			display_name, HORIZONTAL_ALIGNMENT_LEFT, -1.0, tooltip_font_size
		)
		var panel_size := text_size + _tooltip_style.get_minimum_size()
		var panel := Rect2(
			Vector2(-panel_size.x * 0.5, box.position.y - tooltip_gap - panel_size.y), panel_size
		)
		draw_style_box(_tooltip_style, panel)
		# Text is drawn from its baseline, which sits the ascent below the
		# top of the text.
		var baseline := panel.position + Vector2(
			_tooltip_style.content_margin_left,
			_tooltip_style.content_margin_top + font.get_ascent(tooltip_font_size),
		)
		draw_string(
			font,
			baseline,
			display_name,
			HORIZONTAL_ALIGNMENT_LEFT,
			-1.0,
			tooltip_font_size,
			TOOLTIP_TEXT_COLOR,
		)


## Whether the mouse is over the icon.
func is_under_mouse() -> bool:
	if icon == null or not is_visible_in_tree():
		return false
	var offset := get_global_mouse_position() - global_position
	return _icon_rect().has_point(offset * _screen_scale())


## The destination whose icon is under the mouse, or null when there is none.
## Where icons overlap, the one whose centre is nearest the mouse.
static func find_under_mouse(tree: SceneTree) -> Destination:
	var found: Destination = null
	var best := INF
	for node in tree.get_nodes_in_group(GROUP):
		var destination := node as Destination
		if destination == null or not destination.is_under_mouse():
			continue
		var distance := destination.global_position.distance_squared_to(
			destination.get_global_mouse_position()
		)
		if distance < best:
			found = destination
			best = distance
	return found


## The icon's rectangle in screen pixels, centred on the destination.
func _icon_rect() -> Rect2:
	var texture_size := icon.get_size()
	var icon_size := Vector2(icon_height * texture_size.x / texture_size.y, icon_height)
	return Rect2(-icon_size * 0.5, icon_size)


## Screen pixels per map pixel under the current camera.
func _screen_scale() -> float:
	return (get_viewport().get_canvas_transform() * get_global_transform()).get_scale().x
