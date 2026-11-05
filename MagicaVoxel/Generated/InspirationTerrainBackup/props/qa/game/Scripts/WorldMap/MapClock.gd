## The campaign's time on the new map ([code]Scenes/Map.tscn[/code]): a count
## down from [member starting_days], shown in the top left corner as
## days:hours:minutes.
##
## Time passes only while the party travels. Nothing here runs by itself: the
## [Party] calls [method advance] with the real seconds it spent moving, and
## reads [member seconds_per_day] to turn its miles a day into a speed, so the
## clock and the party's pace cannot drift apart.
##
## Nothing happens when the time runs out, for now: the count stops at
## nothing left, and [member elapsed] goes on counting.
class_name MapClock
extends CanvasLayer

## Under every menu, over the map, as the [MapReticle].
const LAYER := 10
const HOURS_A_DAY := 24
const MINUTES_AN_HOUR := 60
## Pixels between the panel and the corner of the screen.
const MARGIN := 16.0
const PANEL_COLOR := Color(0.04, 0.04, 0.07, 0.8)
const TEXT_COLOR := Color(0.93, 0.94, 0.97)

## Real seconds of travel one day of the game takes.
@export_range(0.1, 600.0, 0.1, "or_greater") var seconds_per_day := 30.0
## Days on the count as the campaign starts.
@export_range(0.0, 365.0, 1.0, "or_greater") var starting_days := 90.0

## Days of the game gone by since the campaign started.
var elapsed := 0.0

var _label: Label
## The minutes left as last written, to write the label only when they change.
var _shown := -1


func _init() -> void:
	layer = LAYER

	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_TOP_LEFT)
	panel.offset_left = MARGIN
	panel.offset_top = MARGIN
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var box := StyleBoxFlat.new()
	box.bg_color = PANEL_COLOR
	box.set_corner_radius_all(4)
	box.content_margin_left = 12.0
	box.content_margin_right = 12.0
	box.content_margin_top = 4.0
	box.content_margin_bottom = 4.0
	panel.add_theme_stylebox_override(&"panel", box)
	add_child(panel)

	_label = Label.new()
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label.add_theme_font_size_override(&"font_size", 22)
	_label.add_theme_color_override(&"font_color", TEXT_COLOR)
	panel.add_child(_label)


func _ready() -> void:
	_show()


## Passes the time [param seconds] of real travel take.
func advance(seconds: float) -> void:
	if seconds <= 0.0 or seconds_per_day <= 0.0:
		return
	elapsed += seconds / seconds_per_day
	_show()


## Days still on the count, never less than none.
func remaining() -> float:
	return maxf(starting_days - elapsed, 0.0)


## Writes what is left as days:hours:minutes, the minute begun counting as
## gone, so the count leaves its starting figure the moment the party sets off.
func _show() -> void:
	var minutes := floori(remaining() * HOURS_A_DAY * MINUTES_AN_HOUR)
	if minutes == _shown:
		return
	_shown = minutes
	@warning_ignore("integer_division")
	var hours := minutes / MINUTES_AN_HOUR
	@warning_ignore("integer_division")
	_label.text = "%d:%02d:%02d" % [hours / HOURS_A_DAY, hours % HOURS_A_DAY, minutes % MINUTES_AN_HOUR]
