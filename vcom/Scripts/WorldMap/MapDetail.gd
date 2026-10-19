## Level of detail for the new map (Scenes/Map.tscn): what the map shows, and
## how wide its lines are, follow how far the view is zoomed.
##
## The view is in one of four tiers by how tall it is in miles, each named for
## what about fills the window then, and each adds to the one before it:
##
##   Realm   - the island: the coast, the kingdoms' borders and capitals, the
##             greatest rivers and lakes, the great forests.
##   Kingdom - under [member kingdom_view_miles]: the duchies' borders and
##             capitals, the highways, more rivers and lakes, large forests.
##   Duchy   - under [member duchy_view_miles]: the counties' borders and
##             capitals, the other roads, the bridges, every river and lake,
##             small forests.
##   County  - under [member county_view_miles]: the villages, their lanes
##             and the Swamp's channels, the woods; and in a second step,
##             under [member hamlet_view_miles], the hamlets.
##
## What a tier brings fades in over [member fade_time] as the view crosses
## into it, and out as it leaves. Lines, lakes and forests are only ever
## faded, by their modulate, never hidden: at nothing the renderer skips them,
## where showing a hidden Line2D builds it again (0.07 ms a line, 70 ms for a
## tier's worth) and a hidden Polygon2D is cut into triangles again. What
## holds neither, the settlements, is hidden outright once faded out, so that
## a [Destination] out of sight is not pointed at and stops its own work. So
## does one far from the view ([member Destination.in_view]): of some 2,200,
## only those in and round the view do any work a frame.
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
## A border or a river that reaches the sea ends a little past the land's
## edge, inside the coast's line as the scene has it. The coast's line narrows
## with the rest as the view closes in, so an end left where it is would come
## out of the far side of it and lie over the sea. Each such end is therefore
## moved with its width: how far it goes past the land's edge is scaled by the
## same factor, which keeps it as deep in the coast's line at every zoom as it
## is in the scene.
##
## Nothing here changes the scene as it is edited: the editor shows every node
## at the width it was given.
class_name MapDetail
extends Node

## HAMLETS is the County tier's second step rather than a tier of its own,
## kept as one here since it comes and goes as a tier does.
enum Tier { REALM, KINGDOM, DUCHY, COUNTY, HAMLETS }

## What comes into view with each tier, by its place under the map. Whatever
## is not named here, nor sorted by its own size (the rivers and lakes), shows
## at every zoom: the great forests, Forests/Great, among them. The forests'
## groups are by the size of the whole forest each piece is part of, so a
## forest comes in whole.
const SHOWN_FROM := {
	Tier.KINGDOM: [
		^"Borders/Duchies", ^"BordersOverLakes/Duchies", ^"Roads/Highways", ^"Settlements/DuchyCapitals",
		^"Forests/Large",
	],
	Tier.DUCHY: [
		^"Borders/Counties", ^"BordersOverLakes/Counties", ^"Roads/Roads", ^"Bridges",
		^"Settlements/CountyCapitals", ^"Forests/Small",
	],
	Tier.COUNTY: [^"Settlements/Villages", ^"Roads/Lanes", ^"Bridges/Lanes", ^"Channels", ^"Forests/Woods"],
	Tier.HAMLETS: [^"Settlements/Hamlets"],
}
## The settlements, by their place under the map: the [Destination]s kept
## from working while far from the view.
const SETTLEMENTS := ^"Settlements"
## The side of the squares the settlements are sorted into to be found
## quickly, in the map's units.
const PLACE_SQUARE := 512.0
const RIVERS := ^"Rivers"
const LAKES := ^"Lakes"
const ROADS := ^"Roads"
const COAST := ^"Coast"
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
## The layers whose lines end in the coast's line where they reach the sea.
## Not the roads or the bridges: the one road over the sea, to the island
## town, crosses the land's edge on its way and ends on land, where it is to
## stay.
const ENDS_IN_COAST: Array[NodePath] = [^"Borders", ^"Rivers"]
## The side of the squares the coast's pieces are sorted into to be found
## quickly, in the map's units.
const COAST_CELL := 64.0
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
## The view's height in miles under which the hamlets come in: the County
## tier's second step.
@export_range(1.0, 1000.0, 1.0, "or_greater", "suffix:mi") var hamlet_view_miles := 50.0
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
var _shown: Array[float] = [1.0, 0.0, 0.0, 0.0, 0.0]
var _brings: Array[Array] = [[], [], [], [], []]
var _waits: Array[float] = [-1.0, -1.0, -1.0, -1.0, -1.0]
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
var _tier_lines: Array[Array] = [[], [], [], [], []]
# For a border's line along a river, a lake or a road: the tier that one shows
# from, and the plain border's width, which is all it is until then.
var _wide_from := PackedInt32Array()
var _plain := PackedFloat32Array()
# What each line was last set to: the step of the widths' factor, and whether wide.
var _set_step := PackedInt32Array()
var _set_wide := PackedByteArray()

# For a line that ends past the land's edge (its place in the lists above):
# each of its points out there as [which point, where the line crosses the
# land's edge, where the scene has the point], the last two in the line's own
# space. See _gather_sea_ends() for why they are moved.
var _sea_ends := {}

# The settlements, by the group they are in: for each, all of them and those
# in each square of PLACE_SQUARE, each as [Destination, where it is in the
# map's space]. Those now in view, as keys; and whether a group has come or
# gone since that was worked out.
var _places := {}
var _squares := {}
var _awake := {}
var _places_stale := false

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
	_gather_sea_ends()
	_gather_places()


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
		_wake_places(_seen_from(view, viewport))
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
	var seen := _seen_from(view, viewport)
	if view != _last_view:
		_last_view = view
		_stale = true
		_wake_places(seen)

	if _stale:
		_refresh_widths(seen)
	_fade(delta, seen)
	if _places_stale:
		_wake_places(seen)


## What is on screen in the map's own space, and a little round it.
func _seen_from(view: Transform2D, viewport: Viewport) -> Rect2:
	var seen := view.affine_inverse() * viewport.get_visible_rect()
	return seen.grow(seen.size.y * VIEW_MARGIN)


## Lets the settlements in [param seen] work and stops the rest, which are too
## far off to be pointed at or to need drawing again. Only the groups showing
## are looked through: far out, where the view holds the whole island, the
## villages and hamlets are hidden, and looking through them every frame the
## view moved took 1.8 ms.
func _wake_places(seen: Rect2) -> void:
	_places_stale = false
	var now := {}
	var low := Vector2i((seen.position / PLACE_SQUARE).floor())
	var high := Vector2i((seen.end / PLACE_SQUARE).floor())
	var squares_seen := (high.x - low.x + 1) * (high.y - low.y + 1)
	for group: CanvasItem in _places:
		if not group.is_visible_in_tree():
			continue
		# A few places are quicker looked at one by one than square by square.
		if _places[group].size() <= squares_seen:
			for entry: Array in _places[group]:
				if seen.has_point(entry[1]):
					now[entry[0]] = true
			continue
		var squares: Dictionary = _squares[group]
		for x in range(low.x, high.x + 1):
			for y in range(low.y, high.y + 1):
				var square := Vector2i(x, y)
				if not squares.has(square):
					continue
				for entry: Array in squares[square]:
					if seen.has_point(entry[1]):
						now[entry[0]] = true
	for place: Destination in _awake:
		if not now.has(place):
			place.in_view = false
	for place: Destination in now:
		place.in_view = true
	_awake = now


## The tier a view [param miles] tall is in. With [param slack], the tier it
## is in already holds until the view is that share past its boundary.
func _tier_at(miles: float, slack: float) -> int:
	var under: Array[float] = [kingdom_view_miles, duchy_view_miles, county_view_miles, hamlet_view_miles]
	var tier := _tier if slack > 0.0 else int(Tier.REALM)
	while tier < Tier.HAMLETS and miles < under[tier] * (1.0 - slack):
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
	if _outright.has(item) and item.visible != (amount > 0.0):
		item.visible = amount > 0.0
		# A rank of settlements come or gone: which of them work follows.
		_places_stale = true
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
	# An end out past the land's edge keeps its depth in the coast's line, which
	# has just been scaled by the same factor: left where the scene has it, it
	# would stick out over the sea once the coast's line is narrower than that.
	# Done here because the width just set builds the line again anyway, so
	# moving a point with it costs nothing more.
	if _sea_ends.has(i):
		for end: Array in _sea_ends[i]:
			var edge: Vector2 = end[1]
			var drawn: Vector2 = end[2]
			line.set_point_position(end[0], edge + (drawn - edge) * _factor)
	_set_step[i] = _step
	_set_wide[i] = 1 if wide else 0


# -- reading the scene ------------------------------------------------------------------------

## The groups each tier brings, from [constant SHOWN_FROM]. One that holds
## no line and no polygon, a rank of settlements, is hidden outright once
## faded out; the rest are only ever faded, since a Line2D shown again is
## built again and a Polygon2D cut into triangles again.
func _gather_groups() -> void:
	for tier: int in SHOWN_FROM:
		for path: NodePath in SHOWN_FROM[tier]:
			var group := _map.get_node_or_null(path) as CanvasItem
			if group == null:
				push_error("MapDetail: nothing at '%s' under the map; it is left as it is." % path)
				continue
			var drawn := not group.find_children("*", "Line2D", true, false).is_empty() \
					or not group.find_children("*", "Polygon2D", true, false).is_empty()
			_bring(group, tier, not drawn)


## The settlements, by the group they are in and the square they are in, every
## one out of view until the first frame says which are in it.
func _gather_places() -> void:
	var settlements := _map.get_node_or_null(SETTLEMENTS)
	if settlements == null:
		push_error("MapDetail: no '%s' under the map; every settlement works whether in view or not." % SETTLEMENTS)
		return
	var to_map := _map.get_global_transform().affine_inverse()
	for node in settlements.find_children("*", "Node2D", true, false):
		var place := node as Destination
		if place == null:
			continue
		var group := place.get_parent() as CanvasItem
		var at := to_map * place.global_position
		var square := Vector2i((at / PLACE_SQUARE).floor())
		if not _places.has(group):
			_places[group] = []
			_squares[group] = {}
		_places[group].append([place, at])
		if not _squares[group].has(square):
			_squares[group][square] = []
		_squares[group][square].append([place, at])
		place.in_view = false


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


## Finds the lines that end past the land's edge, and which of their points
## are out there.
##
## Why: the borders and rivers that reach the sea end inside the coast's line,
## some 1.6 units past the land's edge (3.7 at the most), the coast's line
## being 4 wide outside the land. That holds only at the widths the scene has.
## All the way in, every width is a quarter of the scene's, the coast's line
## 1 unit outside the land, and the ends would show out over the sea; all the
## way out they would stop short in it. (They were drawn 10 units out, in the
## middle of a black line 23 wide outside the land, until a thin shoreline took
## its place on 2026-10-18 and the ends were moved in with it.)
## So [method _set_width] moves these points as it sets a width, scaling how
## far each is past the land's edge by the widths' factor. The scene is left
## as it is, and at the height the scene's widths are true the points are
## where it has them.
##
## The land's edge is the middle of the coast's lines, whose inner half lies
## under the land. An end is out past it when, followed back from the end,
## the line crosses a coast's line before it has gone as far as the coast's
## line is wide outside the land: the end is then within that line as the
## scene has it. Only the layers of [constant ENDS_IN_COAST] are looked at.
func _gather_sea_ends() -> void:
	var coast := _map.get_node_or_null(COAST)
	if coast == null:
		push_error("MapDetail: no '%s' under the map; lines that end in the sea are left where they are." % COAST)
		return
	var to_map := _map.get_global_transform().affine_inverse()

	# The coast's pieces by the square they are in, each as its two ends one
	# after the other, so that an end is tried against only the few near it.
	var cells := {}
	var outside := 0.0
	for i in _lines.size():
		if not coast.is_ancestor_of(_lines[i]):
			continue
		outside = maxf(outside, _widths[i] * 0.5)
		var in_map := to_map * _lines[i].get_global_transform()
		var points := _lines[i].points
		for n in points.size() - 1:
			var a := in_map * points[n]
			var b := in_map * points[n + 1]
			for cell in _cells_of(a, b):
				if not cells.has(cell):
					cells[cell] = PackedVector2Array()
				cells[cell].append(a)
				cells[cell].append(b)

	var layers: Array[Node] = []
	for path in ENDS_IN_COAST:
		var layer := _map.get_node_or_null(path)
		if layer != null:
			layers.append(layer)
	for i in _lines.size():
		var points := _lines[i].points
		if points.size() < 2 or not layers.any(func(layer: Node) -> bool: return layer.is_ancestor_of(_lines[i])):
			continue
		var in_map := to_map * _lines[i].get_global_transform()
		for from_start: bool in [true, false]:
			var gone := 0.0
			for n in points.size() - 1:
				var at := n if from_start else points.size() - 1 - n
				var a := in_map * points[at]
				var b := in_map * points[at + (1 if from_start else -1)]
				var crossing: Variant = _coast_crossing(cells, a, b)
				if crossing != null:
					var edge: Vector2 = in_map.affine_inverse() * (crossing as Vector2)
					if not _sea_ends.has(i):
						_sea_ends[i] = []
					for back in n + 1:
						var which := back if from_start else points.size() - 1 - back
						_sea_ends[i].append([which, edge, points[which]])
					break
				gone += a.distance_to(b)
				if gone > outside:
					break


## Where the stretch from [param a] to [param b] crosses the coast, nearest
## [param a], or null when it does not. [param cells] is the coast's pieces
## by square, as [method _gather_sea_ends] sorts them.
func _coast_crossing(cells: Dictionary, a: Vector2, b: Vector2) -> Variant:
	var nearest: Variant = null
	for cell in _cells_of(a, b):
		if not cells.has(cell):
			continue
		var pieces: PackedVector2Array = cells[cell]
		for n in range(0, pieces.size(), 2):
			var hit: Variant = Geometry2D.segment_intersects_segment(a, b, pieces[n], pieces[n + 1])
			if hit != null and (nearest == null or a.distance_squared_to(hit) < a.distance_squared_to(nearest)):
				nearest = hit
	return nearest


## The squares of [constant COAST_CELL] the box round two points lies over.
func _cells_of(a: Vector2, b: Vector2) -> Array[Vector2i]:
	var low := Vector2i((a.min(b) / COAST_CELL).floor())
	var high := Vector2i((a.max(b) / COAST_CELL).floor())
	var found: Array[Vector2i] = []
	for x in range(low.x, high.x + 1):
		for y in range(low.y, high.y + 1):
			found.append(Vector2i(x, y))
	return found


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
