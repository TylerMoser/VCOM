## Level of detail for the new map (Scenes/Map.tscn): what the map shows, and
## how wide its lines are, follow how far the view is zoomed.
##
## The view is in one of four tiers by how tall it is in miles, each named for
## what about fills the window then, and each adds to the one before it:
##
##   Realm   - the island: the coast, the kingdoms' borders and capitals, the
##             greatest rivers and lakes.
##   Kingdom - under [member kingdom_view_miles]: the duchies' borders and
##             capitals, the highways, more rivers and lakes.
##   Duchy   - under [member duchy_view_miles]: the counties' borders and
##             capitals, the other roads, the bridges, every river and lake.
##   County  - under [member county_view_miles]: the villages and hamlets.
##
## What a tier brings fades in over [member fade_time] as the view crosses
## into it, and out as it leaves. Lines and lakes are only ever faded, by
## their modulate, never hidden: at nothing the renderer skips them, where
## showing a hidden Line2D builds it again (0.07 ms a line, 70 ms for a tier's
## worth). Whatever holds no lines, the settlements, is hidden outright once
## faded out, so that a [Destination] out of sight is not pointed at and stops
## its own work.
##
## A Line2D's width is in the map's units, so left alone it is thin and faint
## far out and thick close in. Here every line is as wide as its node says at
## one height of the view, [member true_width_view_miles], and from there its
## width on the screen follows only [member width_growth] of the zoom. All of
## them are scaled by the one factor, since some are sized to others: a
## border's line along a river is as wide as the river and the border on both
## its banks. Setting a width builds the line again, so it is done in steps of
## [member width_step], only for lines in view and showing, and a few a frame
## ([member points_per_frame]); the rest wait until they come into view. A
## tier's lines have waited since it last showed, at some other zoom: as it
## comes in they are set first, and it fades in once they are near right.
##
## Nothing here changes the scene as it is edited: the editor shows every node
## at the width it was given.
class_name MapDetail
extends Node

enum Tier { REALM, KINGDOM, DUCHY, COUNTY }

## What comes into view with each tier, by its place under the map. Whatever
## is not named here, nor sorted by its own size (the rivers and lakes), shows
## at every zoom.
const SHOWN_FROM := {
	Tier.KINGDOM: [
		^"Borders/Duchies", ^"BordersOverLakes/Duchies", ^"Roads/Highways", ^"Settlements/DuchyCapitals",
	],
	Tier.DUCHY: [
		^"Borders/Counties", ^"BordersOverLakes/Counties", ^"Roads/Roads", ^"Bridges",
		^"Settlements/CountyCapitals",
	],
	Tier.COUNTY: [^"Settlements/Villages", ^"Settlements/Hamlets"],
}
const RIVERS := ^"Rivers"
const LAKES := ^"Lakes"
const ROADS := ^"Roads"
## In the name of a border's line that lies under a river, a lake's shore or a
## road it follows, wide enough to show on both sides: "Kingdoms1And2AlongRiver173".
const ALONG := "Along"
## In the name of an island in a lake, after the lake's own: "Lake001Island1".
const ISLAND := "Island"
## How far round the view lines are kept at the right width, as a share of its
## height, so that one panned into view is already right.
const VIEW_MARGIN := 0.15
## A line's box is grown by this many of its widths: its points are its middle,
## and far out it is drawn wider than its node says.
const BOX_MARGIN := 1.5
## Lines are set the furthest off their width first: those more than
## [constant FAR_STEPS] steps off (one that has just come into view, or a
## tier's as it comes in, last given a width when they last showed, at some
## other zoom), then those more than [constant READY_STEPS] off, then the
## rest. A tier starts to fade in once its lines in view are within
## [constant READY_STEPS], or after [constant MOST_WAIT] seconds whatever
## they are.
const FAR_STEPS := 8
const READY_STEPS := 3
const MOST_WAIT := 0.5

@export_group("Nodes")
## The map: the node the layers of [constant SHOWN_FROM] are under.
@export var map_path: NodePath = ^".."

@export_group("Tiers")
## The view's height in miles under which each tier shows.
@export_range(1.0, 1000.0, 1.0, "or_greater", "suffix:mi") var kingdom_view_miles := 480.0
@export_range(1.0, 1000.0, 1.0, "or_greater", "suffix:mi") var duchy_view_miles := 240.0
@export_range(1.0, 1000.0, 1.0, "or_greater", "suffix:mi") var county_view_miles := 100.0
## How far past a tier's height the view must go before the tier changes, as
## a share of that height, so that a view resting on one does not flicker.
@export_range(0.0, 0.2, 0.01) var boundary_slack := 0.05
## Seconds a tier's things take to fade in or out.
@export_range(0.0, 2.0, 0.05, "suffix:s") var fade_time := 0.2

@export_group("Rivers and lakes")
## A river at least this wide where it is widest (its Line2D's width, in the
## map's units) shows from the Realm tier, and from the Kingdom tier; every
## river shows from the Duchy tier.
@export var realm_river_width := 12.0
@export var kingdom_river_width := 9.0
## A lake at least this far across (a circle of its area, in the map's units:
## 100 is 10 km) shows from the Realm tier, and from the Kingdom tier; every
## lake shows from the Duchy tier.
@export var realm_lake_across := 100.0
@export var kingdom_lake_across := 50.0

@export_group("Line widths")
## The height of the view, in miles, at which every line is as wide on the map
## as its node says.
@export_range(1.0, 1000.0, 1.0, "or_greater", "suffix:mi") var true_width_view_miles := 220.0
## How much of the zoom a line's width on the screen follows: 0 holds it
## steady, 1 lets it grow with the map, as a Line2D does left alone.
@export_range(0.0, 1.0, 0.01) var width_growth := 0.36
## Widths are set again each time they are off by this much, as a ratio.
@export_range(1.01, 1.5, 0.01) var width_step := 1.06
## The most points' worth of lines given a new width in one frame. Each point
## costs most of a microsecond; a line longer than this takes a frame alone.
@export var points_per_frame := 4000

var _map: Node2D
## The tier the view is in, a [enum Tier].
var _tier: int = Tier.REALM
## False until the first frame, which sets everything at once, with no fade.
var _started := false

# Fading. For each tier: how far in what it brings is (0 to 1), those things,
# and how long it has waited on its lines before fading in (under 0: it is not waiting).
var _shown: Array[float] = [1.0, 0.0, 0.0, 0.0]
var _brings: Array[Array] = [[], [], [], []]
var _waits: Array[float] = [-1.0, -1.0, -1.0, -1.0]
# The tier each of those things comes with, their alpha as the scene has it,
# and which of them are hidden outright once faded out.
var _tier_of := {}
var _alpha := {}
var _outright := {}

# The lines, side by side. For each: its width and width curve as the scene
# has them, the tier it shows from, where it is, and how many points it has.
var _lines: Array[Line2D] = []
var _widths := PackedFloat32Array()
var _curves: Array[Curve] = []
var _line_tier := PackedInt32Array()
var _boxes: Array[Rect2] = []
var _sizes := PackedInt32Array()
# Which lines each tier brings, as places in the lists above.
var _tier_lines: Array[Array] = [[], [], [], []]
# For a border's line along a river, a lake or a road: the tier that one shows
# from, and the plain border's width, which is all it is until then.
var _wide_from := PackedInt32Array()
var _plain := PackedFloat32Array()
# What each line was last set to: the step of the widths' factor, and whether wide.
var _set_step := PackedInt32Array()
var _set_wide := PackedByteArray()

## The widths' factor is [member width_step] to this power.
var _step := 0
var _factor := 1.0
## Whether some line in view may be at an old width, and where to carry on from.
var _stale := false
var _cursor := 0
var _last_view := Transform2D()


func _ready() -> void:
	_map = get_node_or_null(map_path) as Node2D
	if _map == null:
		push_error("MapDetail: no map at '%s'; it shows everything at every zoom." % map_path)
		set_process(false)
		return
	_gather_groups()
	_gather_water()
	_gather_lines()


func _process(delta: float) -> void:
	var viewport := _map.get_viewport()
	var view := viewport.get_canvas_transform() * _map.get_global_transform()
	var miles := viewport.get_visible_rect().size.y / view.get_scale().y / MapCamera.UNITS_A_MILE
	var step := roundi(log(pow(miles / true_width_view_miles, 1.0 - width_growth)) / log(width_step))

	if not _started:
		_started = true
		_tier = _tier_at(miles, 0.0)
		_set_step_to(step)
		for tier in _brings.size():
			_shown[tier] = 1.0 if tier <= _tier else 0.0
			for item: CanvasItem in _brings[tier]:
				_show(item, _shown[tier])
		# Every line is built for the first time this frame whatever it is
		# given, so all of them start out right, in view or not.
		for i in _lines.size():
			_set_width(i, _wide_from[i] <= _tier)
		_last_view = view
		return

	var tier := _tier_at(miles, boundary_slack)
	if tier != _tier:
		# A tier that comes in from nothing waits on its lines; one that
		# leaves before it has come in stops waiting.
		for coming in range(_tier + 1, tier + 1):
			if _shown[coming] <= 0.0:
				_waits[coming] = 0.0
		for leaving in range(tier + 1, _tier + 1):
			_waits[leaving] = -1.0
		_tier = tier
		# A border along a river is as wide as the river only while that shows.
		_stale = true
	if step != _step:
		_set_step_to(step)
		_stale = true
	if view != _last_view:
		_last_view = view
		_stale = true

	# What is on screen in the map's own space, and a little round it.
	var seen := view.affine_inverse() * viewport.get_visible_rect()
	seen = seen.grow(seen.size.y * VIEW_MARGIN)
	if _stale:
		_refresh_widths(seen)
	_fade(delta, seen)


## The tier a view [param miles] tall is in. With [param slack], the tier it
## is in already holds until the view is that share past its boundary.
func _tier_at(miles: float, slack: float) -> int:
	var under: Array[float] = [kingdom_view_miles, duchy_view_miles, county_view_miles]
	var tier := _tier if slack > 0.0 else int(Tier.REALM)
	while tier < Tier.COUNTY and miles < under[tier] * (1.0 - slack):
		tier += 1
	while tier > Tier.REALM and miles > under[tier - 1] * (1.0 + slack):
		tier -= 1
	return tier


## Moves what each tier brings toward shown or not, by a frame's worth. A
## tier waiting on its lines in [param seen] stays out until they are ready.
func _fade(delta: float, seen: Rect2) -> void:
	for tier in range(1, _brings.size()):
		var wanted := 1.0 if tier <= _tier else 0.0
		if _waits[tier] >= 0.0:
			_waits[tier] += delta
			if _waits[tier] < MOST_WAIT and not _lines_ready(tier, seen):
				continue
			_waits[tier] = -1.0
		if is_equal_approx(_shown[tier], wanted):
			continue
		_shown[tier] = wanted if fade_time <= 0.0 else move_toward(_shown[tier], wanted, delta / fade_time)
		for item: CanvasItem in _brings[tier]:
			_show(item, _shown[tier])


func _show(item: CanvasItem, amount: float) -> void:
	if _outright.has(item):
		item.visible = amount > 0.0
	item.modulate.a = _alpha[item] * amount


func _set_step_to(step: int) -> void:
	_step = step
	_factor = pow(width_step, step)


## Whether the lines a tier brings that are in [param seen] are near enough
## the width for this zoom to be shown.
func _lines_ready(tier: int, seen: Rect2) -> bool:
	for i: int in _tier_lines[tier]:
		var wide := _wide_from[i] <= _tier
		if absi(_set_step[i] - _step) <= READY_STEPS and (_set_wide[i] == 1) == wide:
			continue
		if seen.intersects(_boxes[i]):
			return false
	return true


## Gives the lines in [param seen] (the view, in the map's own space) that
## show at this tier their width for this zoom, as many as a frame allows,
## the furthest off it first.
func _refresh_widths(seen: Rect2) -> void:
	var left := points_per_frame
	for within: int in [FAR_STEPS, READY_STEPS, 0]:
		left = _set_widths(seen, left, within)
		if left <= 0:
			break
	_stale = left <= 0


## Sets the lines in [param seen] more than [param within] steps off their
## width, from where the last frame stopped, until [param budget] points'
## worth are done. Returns what is left of the budget.
func _set_widths(seen: Rect2, budget: int, within: int) -> int:
	var count := _lines.size()
	for n in count:
		var i := (_cursor + n) % count
		# Not one out of its tier, unless it is still fading out.
		if _line_tier[i] > _tier and _shown[_line_tier[i]] <= 0.0:
			continue
		var wide := _wide_from[i] <= _tier
		if absi(_set_step[i] - _step) <= within and (_set_wide[i] == 1) == wide:
			continue
		if not seen.intersects(_boxes[i]):
			continue
		if budget <= 0:
			_cursor = i
			return 0
		_set_width(i, wide)
		budget -= _sizes[i]
	return maxi(budget, 0)


func _set_width(i: int, wide: bool) -> void:
	var line := _lines[i]
	var curve: Curve = _curves[i] if wide else null
	line.width = (_widths[i] if wide else _plain[i]) * _factor
	if line.width_curve != curve:
		line.width_curve = curve
	_set_step[i] = _step
	_set_wide[i] = 1 if wide else 0


# -- reading the scene ------------------------------------------------------------------------

## The groups each tier brings, from [constant SHOWN_FROM].
func _gather_groups() -> void:
	for tier: int in SHOWN_FROM:
		for path: NodePath in SHOWN_FROM[tier]:
			var group := _map.get_node_or_null(path) as CanvasItem
			if group == null:
				push_error("MapDetail: nothing at '%s' under the map; it is left as it is." % path)
				continue
			_bring(group, tier, group.find_children("*", "Line2D", true, false).is_empty())


## The rivers and lakes, each brought by the tier its size earns it. An island
## in a lake is land drawn over the water: it comes and goes with its lake.
func _gather_water() -> void:
	var rivers := _map.get_node_or_null(RIVERS)
	if rivers == null:
		push_error("MapDetail: no '%s' under the map." % RIVERS)
	else:
		for child in rivers.get_children():
			var river := child as Line2D
			if river != null:
				_bring(river, _tier_for(river.width, realm_river_width, kingdom_river_width), false)

	var lakes := _map.get_node_or_null(LAKES)
	if lakes == null:
		push_error("MapDetail: no '%s' under the map." % LAKES)
		return
	var islands: Array[Polygon2D] = []
	for child in lakes.get_children():
		var lake := child as Polygon2D
		if lake == null:
			continue
		if str(lake.name).contains(ISLAND):
			islands.append(lake)
		else:
			_bring(lake, _tier_for(_across(lake), realm_lake_across, kingdom_lake_across), false)
	for island in islands:
		var title := str(island.name)
		var lake := lakes.get_node_or_null(title.left(title.find(ISLAND)))
		_bring(island, _tier_of.get(lake, Tier.DUCHY), false)


func _bring(item: CanvasItem, tier: int, outright: bool) -> void:
	_brings[tier].append(item)
	_tier_of[item] = tier
	_alpha[item] = item.modulate.a
	if outright:
		_outright[item] = true


## The tier something of [param size] shows from, given the least size for
## the Realm tier and for the Kingdom tier.
func _tier_for(size: float, realm: float, kingdom: float) -> int:
	if size >= realm:
		return Tier.REALM
	return Tier.KINGDOM if size >= kingdom else Tier.DUCHY


## How far across a lake is: the width of a circle of its area.
func _across(lake: Polygon2D) -> float:
	var points := lake.polygon
	var twice := 0.0
	for i in points.size():
		var a := points[i]
		var b := points[(i + 1) % points.size()]
		twice += a.x * b.y - b.x * a.y
	return 2.0 * sqrt(absf(twice) * 0.5 / PI)


## Every line under the map, with what its width follows.
func _gather_lines() -> void:
	var to_map := _map.get_global_transform().affine_inverse()
	for node in _map.find_children("*", "Line2D", true, false):
		var line: Line2D = node
		_lines.append(line)
		_widths.append(line.width)
		_curves.append(line.width_curve)
		var shows_from := _tier_above(line)
		_line_tier.append(shows_from)
		_tier_lines[shows_from].append(_lines.size() - 1)
		_boxes.append((to_map * line.get_global_transform() * _box_of(line.points)).grow(line.width * BOX_MARGIN))
		_sizes.append(line.points.size())
		_wide_from.append(Tier.REALM)
		_plain.append(line.width)
		_set_step.append(0)
		_set_wide.append(1)

	# The lines that lie under something a border follows, now that every
	# road is among the lines to be looked for.
	var plain_widths := {}
	var unmatched := 0
	for i in _lines.size():
		var title := str(_lines[i].name)
		var at := title.find(ALONG)
		if at < 0:
			continue
		var group := _lines[i].get_parent()
		if not plain_widths.has(group):
			plain_widths[group] = _plain_width_in(group)
		if plain_widths[group] <= 0.0:
			continue
		var follows := _followed_tier(i, title.substr(at + ALONG.length()))
		if follows < 0:
			unmatched += 1
			continue
		_wide_from[i] = follows
		_plain[i] = plain_widths[group]
	if unmatched > 0:
		push_warning("MapDetail: %d lines named '...%s...' follow nothing found; they keep their width." % [unmatched, ALONG])


## The tier a line shows from: its own (a river's), or that of the nearest
## group over it that a tier brings; the Realm's, which always shows, if none.
func _tier_above(line: Node) -> int:
	var node := line
	while node != null and node != _map:
		if _tier_of.has(node):
			return _tier_of[node]
		node = node.get_parent()
	return Tier.REALM


## A plain border's width in a group of borders: the middle one of its lines
## that follow nothing. 0 when it has none.
func _plain_width_in(group: Node) -> float:
	var found: Array[float] = []
	for child in group.get_children():
		var line := child as Line2D
		if line != null and not str(line.name).contains(ALONG):
			found.append(line.width)
	if found.is_empty():
		return 0.0
	found.sort()
	return found[found.size() / 2]


## The tier from which what line [param i] follows shows, or -1 when that
## cannot be found. [param named] is the rest of its name: "River173",
## "Lake085b", "Road093". A river or a lake is the node of that name; a road's
## number is in no node's name, so it is the road that shares the line's points.
func _followed_tier(i: int, named: String) -> int:
	var split := 0
	while split < named.length() and not named[split].is_valid_int():
		split += 1
	var digits := ""
	for c in named.substr(split):
		if not c.is_valid_int():
			break
		digits += c
	match named.left(split):
		"River":
			var river := _map.get_node_or_null(NodePath("%s/River%s" % [RIVERS, digits]))
			return _tier_of.get(river, -1)
		"Lake":
			var lake := _map.get_node_or_null(NodePath("%s/Lake%s" % [LAKES, digits]))
			return _tier_of.get(lake, -1)
		"Road":
			return _road_tier_at(i)
	return -1


## The tier of the road that runs through the middle point of line [param i],
## or -1 when none does.
func _road_tier_at(i: int) -> int:
	var roads := _map.get_node_or_null(ROADS)
	var points := _lines[i].points
	if roads == null or points.is_empty():
		return -1
	var to_map := _map.get_global_transform().affine_inverse()
	var middle := to_map * _lines[i].get_global_transform() * points[points.size() / 2]
	for j in _lines.size():
		if not _boxes[j].has_point(middle) or not roads.is_ancestor_of(_lines[j]):
			continue
		var local := (to_map * _lines[j].get_global_transform()).affine_inverse() * middle
		for point in _lines[j].points:
			if point.distance_squared_to(local) < 0.25:
				return _line_tier[j]
	return -1


## The smallest upright rectangle that holds some points.
func _box_of(points: PackedVector2Array) -> Rect2:
	if points.is_empty():
		return Rect2()
	var low := points[0]
	var high := points[0]
	for point in points:
		low = low.min(point)
		high = high.max(point)
	return Rect2(low, high - low)
