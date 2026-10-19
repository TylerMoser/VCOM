## MapDetail with the parts of 14 and 19 revisited on 2026-10-19 that were not applied, for their
## variants (styles 141 to 143 and 191 to 194), each off until a style sets it: 14c's growth for
## the roads, and 19's tiers, small lakes and ramps. Swapped onto
## the map's Detail node before the map enters the tree, its settings set straight after, before
## its _ready reads the scene (StyleKit.revisited_detail()).
##
## The variants chosen, 14b and 19a, are MapDetail's own since they were applied on 2026-10-19
## (its border_growth and the borders' faintest shares, and SHOWN_FROM): StyleKit.as_revisited()
## sets them back as they were when the variants were pictured, and a variant sets them as it
## would have them. Everything here follows the zoom as the game would, a frame at a time, so it is
## also the sketch of the change to MapDetail itself, as 14b and 19a were.
extends MapDetail

## The kinds of line whose width can follow the zoom on its own. A bridge is its road's.
enum Kind { OTHER, BORDER, ROAD, HIGHWAY }

# -- 19: when things come in --------------------------------------------------------------------

## What comes in with each tier, by place under the map, in place of SHOWN_FROM when not empty
## (the same shape: {Tier: [NodePath, ...]}).
var shown_from := {}
## Lakes under this many units across that MapDetail brings with the Duchy tier come with
## [member small_lake_tier] instead, with any island in them. 0: none.
var small_lake_across := 0.0
var small_lake_tier: int = Tier.COUNTY
## Groups whose alpha ramps in with the zoom inside their tier, instead of coming in whole as the
## tier does: {NodePath: [miles at which it starts, miles at which it is whole]}, by the
## logarithm of the height between.
var ramps := {}

# -- 14c: the roads' widths by the zoom ---------------------------------------------------------------

## How each kind of road's width follows the zoom on top of MapDetail's rule, as MapDetail's
## border_growth does the borders': times (miles / true_width_view_miles) ^ growth, so below 0
## wider close in and narrower far out.
var road_growth := 0.0
var highway_growth := 0.0

var _kind := PackedInt32Array()
## For a border's band along a river or a road: the kind it lies under (OTHER for a river); -1
## for every other line.
var _follows := PackedInt32Array()
## Groups whose alpha a ramp multiplies: {CanvasItem: [its alpha in the scene, the miles at which
## it starts, the miles at which it is whole]}.
var _ramped := {}


func _ready() -> void:
	super()
	if _map == null:
		return
	for path: NodePath in ramps:
		var item := _map.get_node_or_null(path) as CanvasItem
		if item == null:
			push_error("RevisitedDetail: a ramp names nothing at '%s' under the map." % path)
			continue
		var span: Array = ramps[path]
		_ramped[item] = [_alpha[item] if _alpha.has(item) else item.modulate.a, span[0], span[1]]


func _process(delta: float) -> void:
	super(delta)
	if _ramped.is_empty() or _map == null:
		return
	var viewport := _map.get_viewport()
	var view := viewport.get_canvas_transform() * _map.get_global_transform()
	var miles := viewport.get_visible_rect().size.y / view.get_scale().y / MapCamera.UNITS_A_MILE
	for item: CanvasItem in _ramped:
		var entry: Array = _ramped[item]
		var tier_share: float = _shown[_tier_of[item]] if _tier_of.has(item) else 1.0
		var high: float = entry[1]
		var low: float = entry[2]
		var ramp := clampf(log(high / miles) / log(high / low), 0.0, 1.0)
		var alpha: float = entry[0] * tier_share * _faint_share(item) * ramp
		if not is_equal_approx(item.modulate.a, alpha):
			item.modulate.a = alpha


func _gather_groups() -> void:
	if shown_from.is_empty():
		super()
		return
	for tier: int in shown_from:
		for path: NodePath in shown_from[tier]:
			var group := _map.get_node_or_null(path) as CanvasItem
			if group == null:
				push_error("RevisitedDetail: nothing at '%s' under the map." % path)
				continue
			var drawn := not group.find_children("*", "Line2D", true, false).is_empty() \
					or not group.find_children("*", "Polygon2D", true, false).is_empty()
			_bring(group, tier, not drawn)


func _gather_water() -> void:
	super()
	if small_lake_across <= 0.0:
		return
	var lakes := _map.get_node_or_null(LAKES)
	var moved := {}
	for child in lakes.get_children():
		var lake := child as Polygon2D
		if lake == null or str(lake.name).contains(ISLAND):
			continue
		if _tier_of.get(lake, -1) == Tier.DUCHY and _across(lake) < small_lake_across:
			_move(lake, small_lake_tier)
			moved[str(lake.name)] = true
	# An island goes with its lake, or it would show as a patch of land on its own.
	for child in lakes.get_children():
		var title := str(child.name)
		if title.contains(ISLAND) and moved.has(title.left(title.find(ISLAND))):
			_move(child, small_lake_tier)


func _move(item: CanvasItem, tier: int) -> void:
	_brings[_tier_of[item]].erase(item)
	_brings[tier].append(item)
	_tier_of[item] = tier


func _gather_lines() -> void:
	super()
	var borders: Array[Node] = [_map.get_node_or_null(^"Borders"), _map.get_node_or_null(^"BordersOverLakes")]
	var highways := _map.get_node_or_null(^"Roads/Highways")
	var roads: Array[Node] = [_map.get_node_or_null(^"Roads/Roads"), _map.get_node_or_null(^"Roads/Lanes"),
			_map.get_node_or_null(^"Bridges/Lanes")]
	var bridges := _map.get_node_or_null(^"Bridges")
	for i in _lines.size():
		var line := _lines[i]
		var kind: int = Kind.OTHER
		if borders.any(func(n: Node) -> bool: return n != null and n.is_ancestor_of(line)):
			kind = Kind.BORDER
		elif highways != null and highways.is_ancestor_of(line):
			kind = Kind.HIGHWAY
		elif roads.any(func(n: Node) -> bool: return n != null and n.is_ancestor_of(line)):
			kind = Kind.ROAD
		elif line.get_parent() == bridges:
			# 1.45 times its road: 29 over a highway, 20.3 over a road (23.2 since 10b).
			kind = Kind.HIGHWAY if _widths[i] > 25.0 else Kind.ROAD
		_kind.append(kind)
		_follows.append(-1)
	for i in _lines.size():
		if _kind[i] != Kind.BORDER or _widths[i] <= _plain[i]:
			continue
		var title := str(_lines[i].name)
		if title.contains("AlongRiver"):
			_follows[i] = Kind.OTHER
		elif title.contains("AlongRoad"):
			_follows[i] = _road_kind_at(i)


## The kind of the road through the middle point of line [param i], as MapDetail finds a road a
## border follows; a road (not a highway) when none is found.
func _road_kind_at(i: int) -> int:
	var to_map := _map.get_global_transform().affine_inverse()
	var points := _lines[i].points
	var middle := to_map * _lines[i].get_global_transform() * points[points.size() / 2]
	for j in _lines.size():
		if (_kind[j] != Kind.ROAD and _kind[j] != Kind.HIGHWAY) or not _boxes[j].has_point(middle):
			continue
		var local := (to_map * _lines[j].get_global_transform()).affine_inverse() * middle
		for point in _lines[j].points:
			if point.distance_squared_to(local) < 0.25:
				return _kind[j]
	return Kind.ROAD


## The share of its width a kind of line has at the present step: the borders' is MapDetail's.
func _grown(kind: int) -> float:
	match kind:
		Kind.BORDER:
			return _border_share
		Kind.ROAD:
			return 1.0 if road_growth == 0.0 else pow(_step_miles() / true_width_view_miles, road_growth)
		Kind.HIGHWAY:
			return 1.0 if highway_growth == 0.0 else pow(_step_miles() / true_width_view_miles, highway_growth)
	return 1.0


func _set_width(i: int, wide: bool) -> void:
	super(i, wide)
	if road_growth == 0.0 and highway_growth == 0.0:
		return
	var line := _lines[i]
	var own := _grown(_kind[i])
	if _follows[i] >= 0 and wide:
		# A band: the river's or road's part grows as that does, the border's as borders do.
		line.width = ((_widths[i] - _plain[i]) * _grown(_follows[i]) + _plain[i] * own) * _factor
	else:
		line.width = (_widths[i] if wide else _plain[i]) * own * _factor
