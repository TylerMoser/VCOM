@tool
## Bakes the new map's navigation ([MapNavigationData]) from the map's own
## layers: what the Bake button on [MapNavigation] runs, and
## [code]BakeMapNavigation.gd[/code] without the editor.
##
## Nothing is entered by hand: everything is read from the nodes under the
## layers [MapNavigation] names, wherever a node is moved or however it is
## reshaped (its own transform and its parents' are applied, and a polygon's
## offset). Then:
## [br]1. The map is drawn into a grid of cells of [constant CELL_SIZE] (a
## unit, 100 m), each one [enum MapNavigationData.Ground], in this order: the
## sea; the land (every polygon under Land) as open ground; the forests; the
## sea again outside the land, so that no forest drawn past the coast makes
## land there; the roads, as unbroken lines of cells, only over land; the
## lakes, filled and outlined; the rivers and channels, as unbroken lines of
## cells, except over the sea; the islands in lakes as open ground; and last
## the bridges, as roads over anything, as lines of cells joined side to side
## so that a diagonal step never has to squeeze past the water. Water is
## navigable where its [MapWater] says so.
## [br]2. The grid is cut into blocks of [constant BLOCK_CELLS] cells (16 km).
## Along each edge between two blocks, every run of cells the party can cross
## on both sides gets an entrance every [constant ENTRANCE_SPACING] cells, and
## one wherever a road crosses, so that a route along a road never has to step
## off it at a block's edge (without those, routes came out 11 to 31% slower).
## [br]3. In each block, the best path between every two of its entrances is
## found by [AStarGrid2D] on that block alone, on as many threads as the
## machine has, and kept with its cost and its cells.
## [br]4. The settlements are checked: each must stand on ground the party can
## cross, joined to the land the most entrances are on.
## [br]Nothing random is used, so the same map bakes to the same bytes.
class_name MapNavigationBaker
extends RefCounted

## Raised whenever the bake changes what it makes, so that an older bake is
## stale.
const VERSION := 1
## A cell's side in the map's units: one, 100 m.
const CELL_SIZE := 1.0
## A block's side in cells: 16 km.
const BLOCK_CELLS := 160
## The most cells of border between two entrances along one run.
const ENTRANCE_SPACING := 160
## Cells of sea kept round the land.
const MARGIN := 2
## The most cells one [Image] can hold: a grid larger than this would have to
## be drawn in pieces.
const MOST_CELLS := 268435456
## How many of a kind of problem the report names one by one.
const LISTED := 12

const SEA := MapNavigationData.Ground.SEA
const WATER := MapNavigationData.Ground.WATER
const OPEN := MapNavigationData.Ground.OPEN
const FOREST := MapNavigationData.Ground.FOREST
const ROAD := MapNavigationData.Ground.ROAD
const NAVIGABLE_SEA := MapNavigationData.Ground.NAVIGABLE_SEA
const NAVIGABLE_WATER := MapNavigationData.Ground.NAVIGABLE_WATER

## What a line may be drawn over: anything, only land, or anything but the sea.
enum Over { ANYTHING, LAND, NOT_SEA }

var _navigation: MapNavigation
var _map: Node

# The layers as read, in the map's coordinates.
var _land: Array[PackedVector2Array] = []
var _forests: Array[PackedVector2Array] = []
var _roads: Array[PackedVector2Array] = []
var _bridges: Array[PackedVector2Array] = []
var _bridge_names := PackedStringArray()
var _lakes: Array[PackedVector2Array] = []
var _lake_navigable: Array[bool] = []
var _islands: Array[PackedVector2Array] = []
var _waterways: Array[PackedVector2Array] = []
var _waterway_navigable: Array[bool] = []
var _sea_navigable := false
var _settlements: Array[Vector2] = []
var _settlement_names := PackedStringArray()
## The party's position, or null when there is no party to check.
var _start: Variant = null
var _unflagged := PackedStringArray()
var _missing := PackedStringArray()
var _gathered := false
var _gather_ok := false
## For each bridge, whether it went over water or sea.
var _bridge_crossed: Array[bool] = []
## Every bridge's cells, by the cell's place in the grid.
var _bridge_cells := {}

# The grid as it is drawn.
var _data: MapNavigationData
var _weights := PackedFloat32Array()
var _img: Image
var _sea := SEA
var _land_spans := {}
var _raw_blocks: Array[PackedByteArray] = []

# The network as it is found.
var _node_x := PackedInt32Array()
var _node_y := PackedInt32Array()
var _block_nodes: Array[PackedInt32Array] = []
var _node_at := {}
var _adj_to: Array[PackedInt32Array] = []
var _adj_cost: Array[PackedFloat32Array] = []
var _adj_steps: Array[Array] = []
var _found: Array = []
var _lock := Mutex.new()


func _init(navigation: MapNavigation) -> void:
	_navigation = navigation


## A hash of everything the bake reads: what [member MapNavigationData.signature]
## is checked against to tell whether the map has changed since its bake.
func signature() -> String:
	_gather()
	# MD5 is plenty to tell whether anything changed, and twice as quick as
	# SHA-256 on the layers' 4 MB, which the editor hashes every few seconds.
	var hashing := HashingContext.new()
	hashing.start(HashingContext.HASH_MD5)
	hashing.update(var_to_bytes([VERSION, CELL_SIZE, BLOCK_CELLS, ENTRANCE_SPACING, MARGIN,
			MapNavigation.speeds(), _sea_navigable, _lake_navigable, _waterway_navigable]))
	for part: Array[PackedVector2Array] in [_land, _forests, _roads, _bridges, _lakes, _islands, _waterways]:
		hashing.update(var_to_bytes(part.size()))
		for points in part:
			if not points.is_empty():
				hashing.update(points.to_byte_array())
	return hashing.finish().hex_encode()


## Bakes the map: the navigation, with its report, or null after an error
## saying why.
func run() -> MapNavigationData:
	var began := Time.get_ticks_msec()
	if not _gather():
		return null
	_gather_places()
	_data = MapNavigationData.new()
	_data.version = VERSION
	_data.signature = signature()
	_data.cell_size = CELL_SIZE
	_data.block_cells = BLOCK_CELLS
	_data.speeds = MapNavigation.speeds()
	_weights = _data.weights()
	var times := {}

	var step := Time.get_ticks_msec()
	if not _draw_grid():
		return null
	var cuts := _road_cuts()
	_cut_blocks()
	times["drawing the map"] = Time.get_ticks_msec() - step

	step = Time.get_ticks_msec()
	_find_entrances()
	times["entrances"] = Time.get_ticks_msec() - step
	step = Time.get_ticks_msec()
	_link_blocks()
	times["paths inside blocks"] = Time.get_ticks_msec() - step
	step = Time.get_ticks_msec()
	var main := _main_region()
	var placed := _check_places(main)
	times["checking settlements"] = Time.get_ticks_msec() - step
	step = Time.get_ticks_msec()
	_pack()
	times["packing"] = Time.get_ticks_msec() - step
	_data.report = _report(cuts, placed, main, times, Time.get_ticks_msec() - began)
	_raw_blocks.clear()
	return _data


# -- reading the layers -------------------------------------------------------------------------

## Reads the layers, once. False, after an error, when there is nothing to bake.
func _gather() -> bool:
	if _gathered:
		return _gather_ok
	_gathered = true
	_gather_ok = _read_layers()
	return _gather_ok


func _read_layers() -> bool:
	_map = _navigation.get_node_or_null(_navigation.map_path)
	if _map == null:
		push_error("MapNavigation: no map at '%s'; nothing to bake." % _navigation.map_path)
		return false
	for node in _layer(_navigation.land_path, "Polygon2D"):
		_land.append(_points(node))
	for node in _layer(_navigation.forests_path, "Polygon2D"):
		_forests.append(_points(node))
	for node in _layer(_navigation.roads_path, "Line2D"):
		_roads.append(_points(node))
	for node in _layer(_navigation.bridges_path, "Line2D"):
		_bridges.append(_points(node))
		_bridge_names.append(str(_map.get_path_to(node)))
	for node in _layer(_navigation.lakes_path, "Polygon2D"):
		if str(node.name).contains(MapDetail.ISLAND):
			_islands.append(_points(node))
		else:
			_lakes.append(_points(node))
			_lake_navigable.append(_navigable(node))
	for path in [_navigation.rivers_path, _navigation.channels_path]:
		for node in _layer(path, "Line2D"):
			_waterways.append(_points(node))
			_waterway_navigable.append(_navigable(node))
	var sea := _navigation.get_node_or_null(_navigation.sea_path)
	if sea == null:
		_missing.append(str(_navigation.sea_path))
	else:
		_sea_navigable = _navigable(sea)
	if _land.is_empty():
		push_error("MapNavigation: no land polygons under '%s'; nothing to bake." % _navigation.land_path)
		return false
	return true


## The settlements and the party, which only the bake checks: the signature
## leaves them out, so that moving a town asks for no bake.
func _gather_places() -> void:
	for node in _layer(_navigation.settlements_path, "Node2D"):
		if node is Destination:
			_settlements.append(_to_map(node).origin)
			_settlement_names.append(str(node.name))
	var party := _navigation.get_node_or_null(_navigation.party_path) as Node2D
	if party != null:
		_start = _to_map(party).origin


## Every node of [param type] under the layer at [param path], in the order
## the tree has them; none, noted for the report, when the layer is missing.
func _layer(path: NodePath, type: String) -> Array[Node]:
	var layer := _navigation.get_node_or_null(path)
	if layer == null:
		_missing.append(str(path))
		return []
	return layer.find_children("*", type, true, false)


## Whether [param node] is water the party may cross, noting water with no
## [MapWater] to say.
func _navigable(node: Node) -> bool:
	var water := node as MapWater
	if water == null:
		_unflagged.append(str(_map.get_path_to(node)))
		return false
	return water.navigable


## From [param node]'s own coordinates to the map's.
func _to_map(node: Node) -> Transform2D:
	var transform := Transform2D.IDENTITY
	var at := node
	while at != null and at != _map:
		var drawn := at as Node2D
		if drawn != null:
			transform = drawn.transform * transform
		at = at.get_parent()
	return transform


## The points of a polygon or a line, in the map's coordinates; a closed line
## ends where it began.
func _points(node: Node) -> PackedVector2Array:
	var transform := _to_map(node)
	var points: PackedVector2Array
	var polygon := node as Polygon2D
	if polygon != null:
		points = polygon.polygon
		if polygon.offset != Vector2.ZERO:
			transform = transform * Transform2D(0.0, polygon.offset)
	else:
		var line := node as Line2D
		points = line.points
		if line.closed and points.size() > 2:
			points = points.duplicate()
			points.append(points[0])
	return points if transform == Transform2D.IDENTITY else transform * points


# -- drawing the grid ---------------------------------------------------------------------------

func _draw_grid() -> bool:
	var box := Rect2(_land[0][0], Vector2.ZERO)
	for polygon in _land:
		for point in polygon:
			box = box.expand(point)
	for line in _bridges:
		for point in line:
			box = box.expand(point)
	var low := ((box.position / CELL_SIZE).floor() - Vector2(MARGIN, MARGIN)) * CELL_SIZE
	var high := ((box.end / CELL_SIZE).ceil() + Vector2(MARGIN, MARGIN)) * CELL_SIZE
	_data.origin = low
	_data.size = Vector2i(((high - low) / CELL_SIZE).round())
	if _data.size.x * _data.size.y > MOST_CELLS:
		push_error("MapNavigation: a grid of %d by %d cells is more than one image holds; nothing baked." % [
			_data.size.x, _data.size.y])
		return false
	_sea = NAVIGABLE_SEA if _sea_navigable else SEA
	_img = Image.create(_data.size.x, _data.size.y, false, Image.FORMAT_L8)
	_img.fill(_colour(_sea))

	for polygon in _land:
		_fill_polygon(polygon, OPEN, true)
	for polygon in _forests:
		_fill_polygon(polygon, FOREST, false)
	_sea_outside_land()
	for line in _roads:
		_paint_line(line, ROAD, false, Over.LAND)
	for i in _lakes.size():
		var code := NAVIGABLE_WATER if _lake_navigable[i] else WATER
		_fill_polygon(_lakes[i], code, false)
		var outline := _lakes[i].duplicate()
		outline.append(outline[0])
		_paint_line(outline, code, false, Over.ANYTHING)
	for i in _waterways.size():
		_paint_line(_waterways[i], NAVIGABLE_WATER if _waterway_navigable[i] else WATER, false, Over.NOT_SEA)
	for polygon in _islands:
		_fill_polygon(polygon, OPEN, false)
	_bridge_crossed.clear()
	for line in _bridges:
		_bridge_crossed.append(_paint_line(line, ROAD, true, Over.ANYTHING))
		for cell in _line_cells(line, true):
			_bridge_cells[cell.y * _data.size.x + cell.x] = true
	return true


func _colour(code: int) -> Color:
	return Color8(code, code, code)


func _code_at(x: int, y: int) -> int:
	return _img.get_pixel(x, y).r8


## Fills every cell whose middle is inside [param polygon] (even-odd, so a
## clearing joined to its outline by a cut of no width is left out), a run of
## cells at a time; with [param keep_spans], notes the runs as land.
func _fill_polygon(polygon: PackedVector2Array, code: int, keep_spans: bool) -> void:
	var count := polygon.size()
	if count < 3:
		return
	var top := INF
	var bottom := -INF
	for point in polygon:
		top = minf(top, point.y)
		bottom = maxf(bottom, point.y)
	var oy := float(_data.origin.y)
	var ox := float(_data.origin.x)
	var first := maxi(0, ceili((top - oy) / CELL_SIZE - 0.5))
	var last := mini(_data.size.y - 1, floori((bottom - oy) / CELL_SIZE - 0.5))
	if last < first:
		return
	var rows: Array = []
	rows.resize(last - first + 1)
	for i in count:
		var a := polygon[i]
		var b := polygon[(i + 1) % count]
		if a.y == b.y:
			continue
		if a.y > b.y:
			var swap := a
			a = b
			b = swap
		var ax := float(a.x)
		var ay := float(a.y)
		var by := float(b.y)
		var slope := (float(b.x) - ax) / (by - ay)
		var from_row := maxi(first, ceili((ay - oy) / CELL_SIZE - 0.5))
		var to_row := mini(last, ceili((by - oy) / CELL_SIZE - 0.5) - 1)
		for row in range(from_row, to_row + 1):
			var y := oy + (row + 0.5) * CELL_SIZE
			# Half-open in height, so that a corner two edges share counts once.
			if y < ay or y >= by:
				continue
			var crossings = rows[row - first]
			if crossings == null:
				crossings = PackedFloat64Array()
			crossings.append(ax + (y - ay) * slope)
			rows[row - first] = crossings
	var colour := _colour(code)
	for k in rows.size():
		var crossings = rows[k]
		if crossings == null:
			continue
		crossings.sort()
		for j in range(0, crossings.size() - 1, 2):
			var c0 := maxi(0, ceili((crossings[j] - ox) / CELL_SIZE - 0.5))
			var c1 := mini(_data.size.x - 1, floori((crossings[j + 1] - ox) / CELL_SIZE - 0.5))
			if c1 < c0:
				continue
			_img.fill_rect(Rect2i(c0, first + k, c1 - c0 + 1, 1), colour)
			if keep_spans:
				var row := first + k
				var spans: PackedInt32Array = _land_spans.get(row, PackedInt32Array())
				spans.append(c0)
				spans.append(c1)
				_land_spans[row] = spans


## Draws the sea again over every cell outside the land, a run at a time.
func _sea_outside_land() -> void:
	var colour := _colour(_sea)
	for row in _data.size.y:
		var spans: PackedInt32Array = _land_spans.get(row, PackedInt32Array())
		var runs: Array[Vector2i] = []
		for i in range(0, spans.size(), 2):
			runs.append(Vector2i(spans[i], spans[i + 1]))
		runs.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.x < b.x)
		var x := 0
		for run in runs:
			if run.x > x:
				_img.fill_rect(Rect2i(x, row, run.x - x, 1), colour)
			x = maxi(x, run.y + 1)
		if x < _data.size.x:
			_img.fill_rect(Rect2i(x, row, _data.size.x - x, 1), colour)


## The cells a line through [param points] passes, joined corner to corner
## (or with [param four], side to side), each vertex's cell and the cells
## between in a straight line.
func _line_cells(points: PackedVector2Array, four: bool) -> Array[Vector2i]:
	var cells: Array[Vector2i] = []
	var ox := float(_data.origin.x)
	var oy := float(_data.origin.y)
	if points.is_empty():
		return cells
	var c := floori((points[0].x - ox) / CELL_SIZE)
	var r := floori((points[0].y - oy) / CELL_SIZE)
	cells.append(Vector2i(c, r))
	for i in range(1, points.size()):
		var c1 := floori((points[i].x - ox) / CELL_SIZE)
		var r1 := floori((points[i].y - oy) / CELL_SIZE)
		var dc := absi(c1 - c)
		var dr := absi(r1 - r)
		var sc := 1 if c1 > c else -1
		var sr := 1 if r1 > r else -1
		var err := dc - dr
		while c != c1 or r != r1:
			var e2 := 2 * err
			if four:
				if e2 > -dr and (e2 >= dc or dc > dr):
					err -= dr
					c += sc
				else:
					err += dc
					r += sr
			else:
				if e2 > -dr:
					err -= dr
					c += sc
				if e2 < dc:
					err += dc
					r += sr
			cells.append(Vector2i(c, r))
	return cells


## Draws a line of [param code] over what [param over] allows. Whether it
## went over any water or sea, which is what a bridge is for.
func _paint_line(points: PackedVector2Array, code: int, four: bool, over: int) -> bool:
	var colour := _colour(code)
	var crossed := false
	for cell in _line_cells(points, four):
		if cell.x < 0 or cell.y < 0 or cell.x >= _data.size.x or cell.y >= _data.size.y:
			continue
		var before := _code_at(cell.x, cell.y)
		var wet := before == SEA or before == WATER or before == NAVIGABLE_SEA or before == NAVIGABLE_WATER
		crossed = crossed or wet
		match over:
			Over.LAND:
				if before != OPEN and before != FOREST and before != ROAD:
					continue
			Over.NOT_SEA:
				if before == SEA or before == NAVIGABLE_SEA:
					continue
		_img.set_pixel(cell.x, cell.y, colour)
	return crossed


## Where water cuts a road, as the grid has it: road cells the party cannot
## cross with no bridge within two cells of them (a road's own cells beside
## its bridge may be water: the bridge is the way across), a road's first and
## last cells apart (a road may end at the water's edge). Each place once:
## cut cells along one road less than ten cells apart are one place.
func _road_cuts() -> Dictionary:
	var places: Array[Vector2i] = []
	var ends := 0
	for line in _roads:
		var cells := _line_cells(line, false)
		var last_cut := -100
		for i in cells.size():
			var cell := cells[i]
			if cell.x < 0 or cell.y < 0 or cell.x >= _data.size.x or cell.y >= _data.size.y:
				continue
			if _weights[_code_at(cell.x, cell.y)] > 0.0 or _near_bridge(cell):
				continue
			if i == 0 or i == cells.size() - 1:
				ends += 1
				continue
			var same_place := i - last_cut < 10
			last_cut = i
			if same_place:
				continue
			for place in places:
				if absi(place.x - cell.x) <= 3 and absi(place.y - cell.y) <= 3:
					same_place = true
					break
			if not same_place:
				places.append(cell)
	return {"places": places, "ends": ends}


func _near_bridge(cell: Vector2i) -> bool:
	for dy in range(-2, 3):
		for dx in range(-2, 3):
			if _bridge_cells.has((cell.y + dy) * _data.size.x + cell.x + dx):
				return true
	return false


## Cuts the grid into blocks, row by row, and lets the image go.
func _cut_blocks() -> void:
	var count := _data.blocks_across() * _data.blocks_down()
	_raw_blocks.resize(count)
	for block in count:
		_raw_blocks[block] = _img.get_region(_data.block_rect(block)).get_data()
	_img = null
	_land_spans.clear()


# -- the network --------------------------------------------------------------------------------

func _find_entrances() -> void:
	var across := _data.blocks_across()
	var down := _data.blocks_down()
	_block_nodes.resize(across * down)
	for block in _block_nodes.size():
		_block_nodes[block] = PackedInt32Array()
	for row in down:
		for column in across:
			var block := row * across + column
			if column + 1 < across:
				_border(block, block + 1, true)
			if row + 1 < down:
				_border(block, block + across, false)


## The entrances along the edge between block [param near] and the block
## [param far] to its right ([param beside]) or below it.
func _border(near: int, far: int, beside: bool) -> void:
	var near_rect := _data.block_rect(near)
	var far_rect := _data.block_rect(far)
	var near_cells := _raw_blocks[near]
	var far_cells := _raw_blocks[far]
	var length := near_rect.size.y if beside else near_rect.size.x
	var near_codes := PackedByteArray()
	var far_codes := PackedByteArray()
	near_codes.resize(length)
	far_codes.resize(length)
	for t in length:
		if beside:
			near_codes[t] = near_cells[t * near_rect.size.x + near_rect.size.x - 1]
			far_codes[t] = far_cells[t * far_rect.size.x]
		else:
			near_codes[t] = near_cells[(near_rect.size.y - 1) * near_rect.size.x + t]
			far_codes[t] = far_cells[t]
	var start := -1
	for t in length + 1:
		var open := t < length and _weights[near_codes[t]] > 0.0 and _weights[far_codes[t]] > 0.0
		if open and start == -1:
			start = t
		elif not open and start != -1:
			_run_entrances(start, t - 1, near_codes, far_codes, near_rect, beside)
			start = -1


## The entrances along one run of open cells, from [param a] to [param b]
## along the edge: spread [constant ENTRANCE_SPACING] apart at the most, and
## one in the middle of every stretch where a road crosses.
func _run_entrances(a: int, b: int, near_codes: PackedByteArray, far_codes: PackedByteArray,
		near_rect: Rect2i, beside: bool) -> void:
	var length := b - a + 1
	var count := ceili(float(length) / ENTRANCE_SPACING)
	var spots := PackedInt32Array()
	for i in count:
		spots.append(a + int((i + 0.5) * length / count))
	var crossing_from := -1
	for t in range(a, b + 2):
		var crossing := false
		if t <= b and near_codes[t] == ROAD:
			for u in [t - 1, t, t + 1]:
				if u >= a and u <= b and far_codes[u] == ROAD:
					crossing = true
		if crossing and crossing_from == -1:
			crossing_from = t
		elif not crossing and crossing_from != -1:
			@warning_ignore("integer_division")
			spots.append((crossing_from + t - 1) / 2)
			crossing_from = -1
	spots.sort()
	var last := -1
	for t in spots:
		if t == last:
			continue
		last = t
		var near_cell: Vector2i
		var far_cell: Vector2i
		if beside:
			near_cell = Vector2i(near_rect.end.x - 1, near_rect.position.y + t)
			far_cell = near_cell + Vector2i(1, 0)
		else:
			near_cell = Vector2i(near_rect.position.x + t, near_rect.end.y - 1)
			far_cell = near_cell + Vector2i(0, 1)
		var near_node := _node_for(near_cell)
		var far_node := _node_for(far_cell)
		var cost := 0.5 * (_weights[near_codes[t]] + _weights[far_codes[t]])
		var step := MapNavigationData.step_code(far_cell - near_cell)
		_link(near_node, far_node, cost, PackedByteArray([step]))
		_link(far_node, near_node, cost, PackedByteArray([(step + 4) % 8]))


## The entrance at [param cell], made the first time it is asked for.
func _node_for(cell: Vector2i) -> int:
	var key := cell.y * _data.size.x + cell.x
	if _node_at.has(key):
		return _node_at[key]
	var node := _node_x.size()
	_node_at[key] = node
	_node_x.append(cell.x)
	_node_y.append(cell.y)
	_block_nodes[_data.block_of(cell)].append(node)
	_adj_to.append(PackedInt32Array())
	_adj_cost.append(PackedFloat32Array())
	_adj_steps.append([])
	return node


func _link(from: int, to: int, cost: float, steps: PackedByteArray) -> void:
	_adj_to[from].append(to)
	_adj_cost[from].append(cost)
	_adj_steps[from].append(steps)


## Every block's links between its own entrances, the blocks shared among the
## machine's threads, each searching on a grid of its own.
func _link_blocks() -> void:
	_found.clear()
	_found.resize(_block_nodes.size())
	var group := WorkerThreadPool.add_group_task(_link_block, _block_nodes.size(), -1, true, "Navigation paths")
	WorkerThreadPool.wait_for_group_task_completion(group)
	for block in _found.size():
		if _found[block] == null:
			continue
		for link: Array in _found[block]:
			var steps: PackedByteArray = link[3]
			_link(link[0], link[1], link[2], steps)
			_link(link[1], link[0], link[2], _reversed(steps))
	_found.clear()


func _link_block(block: int) -> void:
	var nodes := _block_nodes[block]
	if nodes.size() < 2:
		return
	var rect := _data.block_rect(block)
	var cells := _raw_blocks[block]
	var grid := MapNavigationData.new_block_grid()
	MapNavigationData.fill_block_grid(grid, rect, cells, _weights)
	var links := []
	for i in nodes.size():
		var a := nodes[i]
		var from := Vector2i(_node_x[a], _node_y[a])
		for j in range(i + 1, nodes.size()):
			var b := nodes[j]
			var path := grid.get_id_path(from, Vector2i(_node_x[b], _node_y[b]))
			if path.is_empty():
				continue
			links.append([a, b, _path_cost(path, rect, cells), _steps_of(path)])
	_lock.lock()
	_found[block] = links
	_lock.unlock()


## The cost of a path of cells inside one block, as [MapNavigationData] counts
## it: each step its length times the mean of its two cells' weights.
func _path_cost(path: Array[Vector2i], rect: Rect2i, cells: PackedByteArray) -> float:
	var total := 0.0
	var width := rect.size.x
	var corner := rect.position
	for i in range(1, path.size()):
		var a := path[i - 1] - corner
		var b := path[i] - corner
		var length := 1.4142135623730951 if a.x != b.x and a.y != b.y else 1.0
		total += length * 0.5 * (_weights[cells[a.y * width + a.x]] + _weights[cells[b.y * width + b.x]])
	return total


func _steps_of(path: Array[Vector2i]) -> PackedByteArray:
	var steps := PackedByteArray()
	steps.resize(path.size() - 1)
	for i in range(1, path.size()):
		steps[i - 1] = MapNavigationData.step_code(path[i] - path[i - 1])
	return steps


func _reversed(steps: PackedByteArray) -> PackedByteArray:
	var back := PackedByteArray()
	back.resize(steps.size())
	var count := steps.size()
	for i in count:
		back[count - 1 - i] = (steps[i] + 4) % 8
	return back


## Which entrances are joined to the most others, the land a route can cross
## between: each entrance's region, and the largest's number.
func _main_region() -> Dictionary:
	var region := PackedInt32Array()
	region.resize(_node_x.size())
	region.fill(-1)
	var sizes := PackedInt32Array()
	for seed_node in _node_x.size():
		if region[seed_node] != -1:
			continue
		var number := sizes.size()
		var count := 0
		var stack := PackedInt32Array([seed_node])
		region[seed_node] = number
		while not stack.is_empty():
			var node := stack[stack.size() - 1]
			stack.resize(stack.size() - 1)
			count += 1
			for next in _adj_to[node]:
				if region[next] == -1:
					region[next] = number
					stack.append(next)
		sizes.append(count)
	var main := 0
	for i in sizes.size():
		if sizes[i] > sizes[main]:
			main = i
	return {"region": region, "main": main, "regions": sizes.size()}


## Each settlement (and the party, last) checked: on what ground it stands,
## and whether a path joins it to the main land's entrances.
func _check_places(main: Dictionary) -> Dictionary:
	var places: Array[Vector2] = _settlements.duplicate()
	var names := _settlement_names.duplicate()
	if _start != null:
		places.append(_start)
		names.append("the party")
	var by_block := {}
	for i in places.size():
		var block := _data.block_of(_cell_of(places[i]))
		if not by_block.has(block):
			by_block[block] = PackedInt32Array()
		var list: PackedInt32Array = by_block[block]
		list.append(i)
		by_block[block] = list
	var blocks: Array = by_block.keys()
	var results := []
	results.resize(places.size())
	var task := func(k: int) -> void:
		var block: int = blocks[k]
		var checked := {}
		if block == -1:
			for i in by_block[block]:
				checked[i] = "off the map"
		else:
			var rect := _data.block_rect(block)
			var cells := _raw_blocks[block]
			var grid := MapNavigationData.new_block_grid()
			MapNavigationData.fill_block_grid(grid, rect, cells, _weights)
			var mains := PackedInt32Array()
			for node in _block_nodes[block]:
				if main.region[node] == main.main:
					mains.append(node)
			for i: int in by_block[block]:
				var cell := _cell_of(places[i])
				var ground := cells[(cell.y - rect.position.y) * rect.size.x + cell.x - rect.position.x]
				if _weights[ground] <= 0.0:
					checked[i] = "on the sea" if ground == SEA else "on water"
					continue
				var joined := false
				for node in mains:
					if not grid.get_id_path(cell, Vector2i(_node_x[node], _node_y[node])).is_empty():
						joined = true
						break
				checked[i] = "" if joined else "cut off from the rest of the land"
		_lock.lock()
		for i: int in checked:
			results[i] = checked[i]
		_lock.unlock()
	var group := WorkerThreadPool.add_group_task(task, blocks.size(), -1, true, "Navigation settlements")
	WorkerThreadPool.wait_for_group_task_completion(group)
	var bad := []
	for i in places.size():
		if results[i] != "":
			bad.append([names[i], places[i], results[i]])
	return {"count": _settlements.size(), "bad": bad}


func _cell_of(point: Vector2) -> Vector2i:
	return Vector2i(((point - _data.origin) / CELL_SIZE).floor())


# -- packing ----------------------------------------------------------------------------------

func _pack() -> void:
	var offsets := PackedInt32Array([0])
	var packed := PackedByteArray()
	for raw in _raw_blocks:
		packed.append_array(raw.compress(FileAccess.COMPRESSION_ZSTD))
		offsets.append(packed.size())
	_data.blocks = packed
	_data.block_offsets = offsets
	_data.node_x = _node_x
	_data.node_y = _node_y
	var block_offsets := PackedInt32Array([0])
	var block_nodes := PackedInt32Array()
	for nodes in _block_nodes:
		block_nodes.append_array(nodes)
		block_offsets.append(block_nodes.size())
	_data.block_node_offsets = block_offsets
	_data.block_nodes = block_nodes
	var link_offsets := PackedInt32Array([0])
	var link_to := PackedInt32Array()
	var link_cost := PackedFloat32Array()
	var step_offsets := PackedInt32Array([0])
	var steps := PackedByteArray()
	for node in _node_x.size():
		link_to.append_array(_adj_to[node])
		link_cost.append_array(_adj_cost[node])
		for path: PackedByteArray in _adj_steps[node]:
			steps.append_array(path)
			step_offsets.append(steps.size())
		link_offsets.append(link_to.size())
	_data.link_offsets = link_offsets
	_data.link_to = link_to
	_data.link_cost = link_cost
	_data.link_step_offsets = step_offsets
	_data.link_steps = steps


# -- the report -------------------------------------------------------------------------------

func _report(cuts: Dictionary, placed: Dictionary, main: Dictionary, times: Dictionary, took: int) -> String:
	var lines := PackedStringArray()
	var spent := PackedStringArray()
	for key: String in times:
		spent.append("%s %.1f s" % [key, times[key] / 1000.0])
	lines.append("Navigation baked from %s in %.1f s (%s)." % [_map.name, took / 1000.0, ", ".join(spent)])
	var counts := PackedInt64Array()
	counts.resize(MapNavigationData.Ground.size())
	for raw in _raw_blocks:
		for ground in counts.size():
			counts[ground] += raw.count(ground)
	var km2 := (CELL_SIZE * 0.1) * (CELL_SIZE * 0.1)
	lines.append("Grid: %d by %d cells of %d m from (%d, %d), in %d blocks of %d km." % [
		_data.size.x, _data.size.y, roundi(CELL_SIZE * 100.0), roundi(_data.origin.x), roundi(_data.origin.y),
		_raw_blocks.size(), roundi(BLOCK_CELLS * CELL_SIZE * 0.1)])
	lines.append("Ground: open %d km², forest %d km², road %d km²; water %d km² blocking, %d km² navigable; the sea %s." % [
		roundi(counts[OPEN] * km2), roundi(counts[FOREST] * km2), roundi(counts[ROAD] * km2),
		roundi(counts[WATER] * km2), roundi(counts[NAVIGABLE_WATER] * km2),
		"navigable" if _sea_navigable else "blocking"])
	lines.append("Speeds: road %s, open %s, forest %s, navigable water %s miles a day." % [
		MapNavigation.ROAD_MILES_PER_DAY, MapNavigation.OPEN_MILES_PER_DAY, MapNavigation.FOREST_MILES_PER_DAY,
		MapNavigation.NAVIGABLE_MILES_PER_DAY])
	lines.append("Network: %d entrances, %d links, in %d regions." % [_node_x.size(), _data.link_to.size(), main.regions])
	var bad: Array = placed.bad
	if bad.is_empty():
		lines.append("Settlements: all %d stand on land joined to the rest%s." % [placed.count,
			", and so does the party" if _start != null else ""])
	else:
		lines.append("PROBLEM: %d of %d settlements (or the party) cannot be reached:" % [bad.size(), placed.count])
		for item: Array in bad:
			var at: Vector2 = item[1]
			lines.append("    %s at (%.1f, %.1f): %s" % [item[0], at.x, at.y, item[2]])
	var places: Array = cuts.places
	var ends := "; the last cell of %d %s is water, which is no matter" % [cuts.ends, "road" if cuts.ends == 1 else "roads"]
	if places.is_empty():
		lines.append("Roads: none cut by water%s." % (ends if cuts.ends > 0 else ""))
	else:
		lines.append("PROBLEM: water cuts a road in %d places, each wanting a bridge or the road moved%s:" % [
			places.size(), ends if cuts.ends > 0 else ""])
		for i in mini(places.size(), LISTED):
			var cell: Vector2i = places[i]
			var at := _data.origin + (Vector2(cell) + Vector2(0.5, 0.5)) * CELL_SIZE
			lines.append("    near (%.0f, %.0f)" % [at.x, at.y])
		if places.size() > LISTED:
			lines.append("    and %d more" % (places.size() - LISTED))
	var dry := PackedStringArray()
	for i in _bridges.size():
		if not _bridge_crossed[i]:
			dry.append(_bridge_names[i])
	if not dry.is_empty():
		lines.append("Note: %d bridges cross no water: %s." % [dry.size(), ", ".join(dry.slice(0, LISTED))])
	if not _unflagged.is_empty():
		lines.append("Note: %d water nodes have no MapWater script, so are not navigable and cannot be made so: %s%s." % [
			_unflagged.size(), ", ".join(_unflagged.slice(0, LISTED)), "..." if _unflagged.size() > LISTED else ""])
	if not _missing.is_empty():
		lines.append("PROBLEM: no layer at %s." % ", ".join(_missing))
	return "\n".join(lines)
