## The party and its route, drawn the way a route planner draws them: the line
## over a white casing, red where it runs through forest (where battles are
## met) and blue where it does not, a tick and a day's number at each day's
## travel, and a pin at the end saying how long the trip takes and what its
## odds of a battle are. Everything is sized in screen pixels, as the party's
## own drawing is. Optionally a ring round the party at a number of days'
## travel: what it can reach.
##
## A runtime node for the map style harness. For real, this is Party._draw()
## (and the forests sampled once when a route is set, not every frame).
extends Node2D

## The party. Its own drawing is hidden while this one draws it.
var party: Node2D
## Where the route goes after the party's position, in the map's units.
var route := PackedVector2Array()
var miles_per_day := 25.0
## A step, which rolls a forest's odds, every this many units (Party.step_length).
var step_units := 50.0
## The odds of a battle at a step taken in forest (Forest.tscn's).
var chance := 0.1

var safe_color := Color("#1a73e8")
var danger_color := Color("#d93a2b")
var casing_color := Color.WHITE
var party_color := Color("#1a73e8")
var tick_color := Color("#202124")
var line_px := 4.5
var casing_px := 2.0
var show_ticks := true
var show_summary := true
## A ring at this many days' travel round the party; none at 0.
var reach_days := 0.0
var reach_color := Color(0.08, 0.36, 0.8, 0.8)

var _segments: Array = []
var _forest_steps := 0
var _steps := 0
var _length := 0.0
var _drawn_scale := 0.0
var _font: Font


func _ready() -> void:
	z_index = 8
	_font = ThemeDB.fallback_font
	if party != null:
		party.visible = false
	_measure()


## Walks the route a little at a time and asks which stretches are in forest,
## and counts the steps that end in one.
func _measure() -> void:
	_segments.clear()
	_forest_steps = 0
	_steps = 0
	var points := PackedVector2Array([party.position])
	points.append_array(route)
	var sample := 10.0
	var walked := 0.0
	var next_step := step_units
	for n in points.size() - 1:
		var a := points[n]
		var b := points[n + 1]
		var length := a.distance_to(b)
		var at := 0.0
		while at < length:
			var to := minf(at + sample, length)
			var middle := a.lerp(b, (at + to) * 0.5 / length)
			var in_forest := Forest.find_at(get_tree(), middle) != null
			var p0 := a.lerp(b, at / length)
			var p1 := a.lerp(b, to / length)
			if not _segments.is_empty() and _segments[-1][2] == in_forest:
				_segments[-1][1] = p1
			else:
				_segments.append([p0, p1, in_forest])
			walked += to - at
			while walked >= next_step:
				_steps += 1
				if in_forest:
					_forest_steps += 1
				next_step += step_units
			at = to
	_length = walked


func _process(_delta: float) -> void:
	if not is_equal_approx(_screen_scale(), _drawn_scale):
		queue_redraw()


func _draw() -> void:
	var s := _screen_scale()
	_drawn_scale = s
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE / s)
	var from := party.position * s

	if reach_days > 0.0:
		var radius := reach_days * miles_per_day * MapCamera.UNITS_A_MILE * s
		var pieces := 96
		for i in pieces:
			if i % 2 == 1:
				continue
			draw_arc(from, radius, TAU * i / pieces, TAU * (i + 1) / pieces, 6, reach_color, 2.0)
		_label(from + Vector2(0, -radius - 6), "%d days' travel" % roundi(reach_days), 13, reach_color.darkened(0.3), true)

	if not route.is_empty():
		for segment: Array in _segments:
			_capsule(segment[0] * s, segment[1] * s, line_px + casing_px * 2.0, casing_color)
		for segment: Array in _segments:
			_capsule(segment[0] * s, segment[1] * s, line_px, danger_color if segment[2] else safe_color)
		if show_ticks:
			_draw_ticks(s)
		var end: Vector2 = route[route.size() - 1] * s
		draw_circle(end, 8.0, casing_color)
		draw_circle(end, 5.5, tick_color)
		# The summary only once the route is long enough on the screen to be
		# what the view is about.
		if show_summary and _length * s > 140.0:
			var days := _length / (miles_per_day * MapCamera.UNITS_A_MILE)
			var odds := 1.0 - pow(1.0 - chance, _forest_steps)
			_panel(end + Vector2(12, -30), [
				"%.1f days" % days,
				"%d of %d steps in forest · %d%% chance of a battle" % [_forest_steps, _steps, roundi(odds * 100.0)],
			])

	draw_circle(from, 15.0, Color(party_color, 0.18))
	draw_circle(from, 8.5, casing_color)
	draw_circle(from, 6.0, party_color)


func _draw_ticks(s: float) -> void:
	var day_units := miles_per_day * MapCamera.UNITS_A_MILE
	var points := PackedVector2Array([party.position])
	points.append_array(route)
	var walked := 0.0
	var next := day_units
	var day := 1
	for n in points.size() - 1:
		var a := points[n]
		var b := points[n + 1]
		var length := a.distance_to(b)
		var along := (b - a).normalized()
		var across := Vector2(-along.y, along.x)
		while walked + length >= next:
			var p := a.lerp(b, (next - walked) / length) * s
			draw_line(p - across * 8.0, p + across * 8.0, casing_color, 5.0)
			draw_line(p - across * 7.0, p + across * 7.0, tick_color, 2.0)
			_label(p + across * 18.0 + Vector2(-8, 5), "%dd" % day, 12, tick_color, true)
			day += 1
			next += day_units
		walked += length


func _capsule(a: Vector2, b: Vector2, width: float, color: Color) -> void:
	draw_line(a, b, color, width)
	draw_circle(a, width * 0.5, color)
	draw_circle(b, width * 0.5, color)


func _label(at: Vector2, text: String, size: int, color: Color, halo: bool) -> void:
	if halo:
		draw_string_outline(_font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, size, 4, Color(1, 1, 1, 0.9))
	draw_string(_font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, size, color)


func _panel(at: Vector2, lines: Array) -> void:
	var size := 13
	var height := _font.get_height(size)
	var width := 0.0
	for line: String in lines:
		width = maxf(width, _font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1.0, size).x)
	var box := Rect2(at, Vector2(width + 16.0, height * lines.size() + 8.0))
	draw_rect(box, Color(1, 1, 1, 0.94))
	draw_rect(box, Color(0, 0, 0, 0.25), false, 1.0)
	var baseline := at + Vector2(8.0, 4.0 + _font.get_ascent(size))
	for i in lines.size():
		draw_string(_font, baseline + Vector2(0, height * i), lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1.0, size,
				Color("#202124") if i == 0 else Color("#5f6368"))


func _screen_scale() -> float:
	return (get_viewport().get_canvas_transform() * get_global_transform()).get_scale().x
