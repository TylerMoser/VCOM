## The prompts for a reaction window: beside each squad member who could fire,
## the key that fires them and the odds of their shot, and along the bottom a
## reminder that 0 lets the enemy carry on.
##
## Screen space and redrawn every frame from the units' positions, like
## [ShotOverlay], so the prompts keep up with the units and the camera.
class_name ReactionPrompts
extends Control

## One squad member's prompt: the key that fires them, and their odds.
class Prompt:
	var unit: Unit
	var key: String
	var chance: int

	func _init(prompt_unit: Unit, prompt_key: String, prompt_chance: int) -> void:
		unit = prompt_unit
		key = prompt_key
		chance = prompt_chance


const KEY_SIZE := Vector2(26, 26)
const FONT_SIZE := 16
## Where a prompt sits: this far up the unit, and this many pixels to its
## right on screen, clear of the unit itself.
const ANCHOR_HEIGHT := 1.0
const OFFSET_X := 18.0
## Pixels between a key and the text beside it.
const GAP := 6.0
## Pixels from the bottom of the screen to the continue reminder, which puts
## it just above the action bar.
const HINT_BOTTOM := 112.0
const HINT_KEY := "0"
const HINT_TEXT := "Continue"

const KEY_BG_COLOR := Color(0.1, 0.11, 0.15, 0.92)
const KEY_BORDER_COLOR := Color(1.0, 0.9, 0.55)
const TEXT_COLOR := Color(1.0, 1.0, 1.0)
## Text lands straight on the map, which is as bright as it is, so it is
## outlined like the hit and miss calls.
const OUTLINE_COLOR := Color(0.04, 0.04, 0.07)
const OUTLINE_WIDTH := 4

var _prompts: Array[Prompt] = []
var _key_style: StyleBoxFlat


func _init() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	visible = false
	set_process(false)

	_key_style = StyleBoxFlat.new()
	_key_style.bg_color = KEY_BG_COLOR
	_key_style.border_color = KEY_BORDER_COLOR
	_key_style.set_border_width_all(2)
	_key_style.set_corner_radius_all(4)


# The camera moves under still units, so redraw every frame.
func _process(_delta: float) -> void:
	queue_redraw()


## Shows [param prompts] in place of whatever was showing.
func show_prompts(prompts: Array[Prompt]) -> void:
	_prompts = prompts
	visible = true
	set_process(true)
	queue_redraw()


func clear() -> void:
	_prompts = []
	visible = false
	set_process(false)


## The prompts showing, in the order they were given.
func prompts() -> Array[Prompt]:
	return _prompts


func _draw() -> void:
	var camera := get_viewport().get_camera_3d()
	if camera == null:
		return

	for prompt in _prompts:
		if not is_instance_valid(prompt.unit):
			continue
		var anchor := prompt.unit.global_position + Vector3.UP * ANCHOR_HEIGHT
		if camera.is_position_behind(anchor):
			continue
		var at := camera.unproject_position(anchor) + Vector2(OFFSET_X, -KEY_SIZE.y * 0.5)
		var odds := "%d%%" % prompt.chance
		_draw_labelled_key(at, prompt.key, odds, TargetPanel.chance_color(prompt.chance))

	var font := get_theme_default_font()
	var width := KEY_SIZE.x + GAP + font.get_string_size(
		HINT_TEXT, HORIZONTAL_ALIGNMENT_LEFT, -1.0, FONT_SIZE
	).x
	_draw_labelled_key(
		Vector2((size.x - width) * 0.5, size.y - HINT_BOTTOM), HINT_KEY, HINT_TEXT, TEXT_COLOR
	)


## A key cap with its top-left corner at [param corner], showing
## [param key], and [param text] in [param color] beside it.
func _draw_labelled_key(corner: Vector2, key: String, text: String, color: Color) -> void:
	var font := get_theme_default_font()
	# Text is drawn from its baseline. Centring the text, ascent above the
	# baseline and descent below it, in the key puts the baseline here.
	var ascent := font.get_ascent(FONT_SIZE)
	var descent := font.get_descent(FONT_SIZE)
	var baseline := corner.y + (KEY_SIZE.y + ascent - descent) * 0.5

	draw_style_box(_key_style, Rect2(corner, KEY_SIZE))
	var key_width := font.get_string_size(key, HORIZONTAL_ALIGNMENT_LEFT, -1.0, FONT_SIZE).x
	draw_string(
		font,
		Vector2(corner.x + (KEY_SIZE.x - key_width) * 0.5, baseline),
		key,
		HORIZONTAL_ALIGNMENT_LEFT,
		-1.0,
		FONT_SIZE,
		TEXT_COLOR,
	)

	var text_at := Vector2(corner.x + KEY_SIZE.x + GAP, baseline)
	draw_string_outline(
		font, text_at, text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, FONT_SIZE, OUTLINE_WIDTH, OUTLINE_COLOR
	)
	draw_string(font, text_at, text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, FONT_SIZE, color)
