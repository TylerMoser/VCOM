## A gamepad button as the prompts show it, drawn from shapes rather than a
## font's symbols, which the game's font has none of: the face buttons as
## circles with their letter in the colour an Xbox pad (and a Steam Deck) gives
## it, the shoulder buttons, triggers, View and Menu as labelled pills, the
## sticks as rings, and the d-pad as a cross with the arm or arms that matter
## lit.
##
## As a [Control] it is one glyph, sized to fit; [method draw_glyph] draws one
## on any canvas, for something that draws its own prompts
## ([ReactionPrompts]).
##
## The names: A, B, X, Y; LB, RB, LT, RT; LS, RS (moved), L3, R3 (pressed);
## View, Menu; dpad, dpad_left, dpad_right, dpad_up, dpad_down,
## dpad_horizontal, dpad_vertical.
class_name ButtonGlyph
extends Control

const HEIGHT := 24.0
const FONT_SIZE := 13
const BG_COLOR := Color(0.08, 0.09, 0.12, 0.95)
const EDGE_COLOR := Color(0.78, 0.8, 0.85)
const TEXT_COLOR := Color(0.95, 0.96, 0.98)
## The d-pad's arms, lit and not.
const ARM_COLOR := Color(0.4, 0.42, 0.48)
const LIT_COLOR := Color(1.0, 0.9, 0.55)
## Each face button's own colour.
const FACE_COLORS := {
	&"A": Color(0.42, 0.8, 0.32),
	&"B": Color(0.95, 0.33, 0.3),
	&"X": Color(0.32, 0.6, 0.98),
	&"Y": Color(0.98, 0.8, 0.25),
}
## Widths of the pills, by name; everything else is round, [constant HEIGHT]
## across.
const PILL_WIDTHS := {
	&"LB": 32.0, &"RB": 32.0, &"LT": 30.0, &"RT": 30.0, &"View": 44.0, &"Menu": 46.0,
}
## Which arms of the d-pad each name lights, as directions on screen.
const DPAD_ARMS := {
	&"dpad": [],
	&"dpad_left": [Vector2.LEFT],
	&"dpad_right": [Vector2.RIGHT],
	&"dpad_up": [Vector2.UP],
	&"dpad_down": [Vector2.DOWN],
	&"dpad_horizontal": [Vector2.LEFT, Vector2.RIGHT],
	&"dpad_vertical": [Vector2.UP, Vector2.DOWN],
}

var button: StringName


func _init(for_button: StringName = &"A") -> void:
	button = for_button
	custom_minimum_size = Vector2(width_of(button), HEIGHT)
	mouse_filter = MOUSE_FILTER_IGNORE


func _draw() -> void:
	draw_glyph(self, button, Vector2(0.0, (size.y - HEIGHT) * 0.5))


## How wide [param name]'s glyph is drawn, in pixels.
static func width_of(name: StringName) -> float:
	return PILL_WIDTHS.get(name, HEIGHT)


## Draws [param name]'s glyph on [param canvas] with its top-left corner at
## [param corner], [constant HEIGHT] tall. Returns how wide it was.
static func draw_glyph(canvas: CanvasItem, name: StringName, corner: Vector2) -> float:
	var width := width_of(name)
	var box := Rect2(corner, Vector2(width, HEIGHT))
	var middle := box.get_center()
	if DPAD_ARMS.has(name):
		_draw_dpad(canvas, middle, DPAD_ARMS[name])
		return width
	var edge: Color = FACE_COLORS.get(name, EDGE_COLOR)
	if PILL_WIDTHS.has(name):
		var pill := StyleBoxFlat.new()
		pill.bg_color = BG_COLOR
		pill.border_color = edge
		pill.set_border_width_all(2)
		pill.set_corner_radius_all(int(HEIGHT * 0.5) if name in [&"LB", &"RB"] else 5)
		canvas.draw_style_box(pill, box)
	else:
		var radius := HEIGHT * 0.5 - 1.0
		canvas.draw_circle(middle, radius, BG_COLOR, true, -1.0, true)
		canvas.draw_circle(middle, radius, edge, false, 2.0, true)
	var text := String(name)
	var font := ThemeDB.fallback_font
	var size := FONT_SIZE - (2 if text.length() > 2 else 0)
	var text_width := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, size).x
	var baseline := middle.y + (font.get_ascent(size) - font.get_descent(size)) * 0.5
	var color: Color = FACE_COLORS.get(name, TEXT_COLOR)
	canvas.draw_string(
		font, Vector2(middle.x - text_width * 0.5, baseline), text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, size, color
	)
	return width


## A cross, its arms [constant ARM_COLOR] but the [param lit] ones.
static func _draw_dpad(canvas: CanvasItem, middle: Vector2, lit: Array) -> void:
	var arm := HEIGHT * 0.34
	var reach := HEIGHT * 0.5 - 1.0
	var outline := Rect2(middle - Vector2(arm * 0.5 + 1.5, reach + 1.0), Vector2(arm + 3.0, reach * 2.0 + 2.0))
	canvas.draw_rect(outline, BG_COLOR)
	canvas.draw_rect(Rect2(middle - Vector2(reach + 1.0, arm * 0.5 + 1.5), Vector2(reach * 2.0 + 2.0, arm + 3.0)), BG_COLOR)
	for direction: Vector2 in [Vector2.LEFT, Vector2.RIGHT, Vector2.UP, Vector2.DOWN]:
		var color := LIT_COLOR if direction in lit else ARM_COLOR
		var far := middle + direction * reach
		var near := middle + direction * arm * 0.5
		var rect := Rect2(near.min(far), (far - near).abs())
		rect = rect.grow_side(SIDE_TOP if direction.x != 0.0 else SIDE_LEFT, arm * 0.5)
		rect = rect.grow_side(SIDE_BOTTOM if direction.x != 0.0 else SIDE_RIGHT, arm * 0.5)
		canvas.draw_rect(rect, color)
	canvas.draw_rect(Rect2(middle - Vector2(arm, arm) * 0.5, Vector2(arm, arm)), ARM_COLOR)
