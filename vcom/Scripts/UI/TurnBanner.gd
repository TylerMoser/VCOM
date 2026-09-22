## Large "Player Turn" / "Enemy Turn" banner that fades in and out.
class_name TurnBanner
extends PanelContainer

@export var fade_seconds := 0.25
@export var hold_seconds := 0.9

var _label: Label
var _tween: Tween


func _init() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	modulate.a = 0.0

	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.11, 0.15, 0.85)
	style.border_color = Color(1.0, 0.9, 0.55)
	style.border_width_top = 2
	style.border_width_bottom = 2
	style.content_margin_left = 48
	style.content_margin_right = 48
	style.content_margin_top = 10
	style.content_margin_bottom = 10
	add_theme_stylebox_override(&"panel", style)

	_label = Label.new()
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.add_theme_font_size_override(&"font_size", 32)
	add_child(_label)


## Shows [param text], then fades it out. Await it to wait for the banner to
## finish; a newer announcement replaces one still showing.
func announce(text: String) -> void:
	_label.text = text
	if _tween != null:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(self, ^"modulate:a", 1.0, fade_seconds)
	_tween.tween_interval(hold_seconds)
	_tween.tween_property(self, ^"modulate:a", 0.0, fade_seconds)
	await _tween.finished
