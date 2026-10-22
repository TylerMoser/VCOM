@tool
## Finds the party's way over the new map's baked navigation
## ([MapNavigationData]), in the map's own coordinates.
##
## A route is searched over the bake's network of entrances, not over the
## grid's 139 million cells: the start is joined to the entrances of its own
## block and the destination to those of its block, each by a search of that
## block alone ([AStarGrid2D]); the network is searched from one to the other
## (A*, the estimate the straight distance at a road's pace, which no route
## beats); and the cells of each link it takes, stored by the bake, are laid
## end to end. That gives the grid's path, cell by cell, within a few in a
## hundred of the best one over the whole grid (Docs/MAP.md, "Navigation").
##
## The grid's path is then pulled straight: from each point, on to the
## furthest later one it can reach in a straight line that meets no cell the
## party cannot cross, cuts no corner between two such cells, and is no slower
## than the grid's path between them. So the route is never slower than the
## grid's, and it keeps to the roads wherever leaving them would be slower.
## Last, each straight stretch is cut into legs by the ground under it, so
## that the party's pace follows it.
##
## One route at a time: [MapNavigation] keeps one router for its worker thread
## and others for the main thread, never sharing one between threads.
class_name MapRouter
extends RefCounted

## A leg shorter than this many cells takes the pace of the leg beside it on
## the same straight stretch, so that where the line clips the ragged edge of
## a forest's cells the party does not slow down and speed up for a few steps.
const SHORTEST_LEG := 3.0
## The most points of the grid's path one straight stretch may pass over, so
## that pulling a long route straight stays quick.
const LONGEST_PULL := 512
## How near two crossings of a cell's sides must be to count as going through
## its corner, as a share of the stretch.
const CORNER := 1e-9

var _data: MapNavigationData
var _weights: PackedFloat32Array
var _speeds: PackedFloat32Array
var _cache_limit := 256
## Decoded blocks, by block.
var _blocks := {}
## The block last read, to skip the lookup while a line stays in one block.
var _last_block := -1
var _last_cells := PackedByteArray()
var _last_rect := Rect2i()
## The grid one block is searched on, and the block it holds.
var _grid := MapNavigationData.new_block_grid()
var _filled := -1
## What [method _pieces] found: each piece's ground and length in cells.
var _piece_ground := PackedByteArray()
var _piece_length := PackedFloat64Array()


func _init(data: MapNavigationData, cache_limit := 256) -> void:
	_data = data
	_weights = data.weights()
	_speeds = data.speeds
	_cache_limit = cache_limit


## The cell [param point] is in.
func cell_of(point: Vector2) -> Vector2i:
	return Vector2i(((point - _data.origin) / _data.cell_size).floor())


## The middle of cell [param cell], in the map.
func centre_of(cell: Vector2i) -> Vector2:
	return _data.origin + (Vector2(cell) + Vector2(0.5, 0.5)) * _data.cell_size


## The ground at [param point]: sea off the grid.
func ground_at(point: Vector2) -> int:
	return _ground(cell_of(point))


## Whether the party may stand at [param point].
func is_passable(point: Vector2) -> bool:
	return _weights[ground_at(point)] > 0.0


## Miles a day over the ground at [param point]: 0 where the party cannot go.
func miles_per_day_at(point: Vector2) -> float:
	return _speeds[ground_at(point)]


## The way from [param from] to [param to], or null when [param to] is
## somewhere the party cannot stand or cannot reach from [param from].
func find_route(from: Vector2, to: Vector2) -> MapRoute:
	var goal := cell_of(to)
	if _weights[_ground(goal)] <= 0.0:
		return null
	var start := cell_of(from)
	if _weights[_ground(start)] <= 0.0:
		# Only after the map has changed under it can the party stand where
		# it cannot go: it sets off from the nearest cell it can.
		var near: Variant = _passable_near(start, 3)
		if near == null:
			return null
		start = near
	var cells: Array[Vector2i] = []
	if start == goal:
		cells.append(start)
	else:
		cells = _cell_path(start, goal)
	if cells.is_empty():
		return null
	return _legs(_pull(from, cells, to))


# -- the grid's path --------------------------------------------------------------------------

## The grid's path from [param start] to [param goal], cell by cell, both
## included; empty when there is none.
func _cell_path(start: Vector2i, goal: Vector2i) -> Array[Vector2i]:
	var nodes := _data.node_x.size()
	var START := nodes
	var GOAL := nodes + 1
	var start_block := _data.block_of(start)
	var goal_block := _data.block_of(goal)

	# The start joined to its block's entrances, the goal to its block's,
	# each with the cells of the way, and straight to each other when they
	# share a block.
	var from_start := {}
	_fill(start_block)
	for i in range(_data.block_node_offsets[start_block], _data.block_node_offsets[start_block + 1]):
		var node := _data.block_nodes[i]
		var path := _grid.get_id_path(start, Vector2i(_data.node_x[node], _data.node_y[node]))
		if not path.is_empty():
			from_start[node] = path
	var direct: Array[Vector2i] = []
	if start_block == goal_block:
		direct = _grid.get_id_path(start, goal)
	var to_goal := {}
	_fill(goal_block)
	for i in range(_data.block_node_offsets[goal_block], _data.block_node_offsets[goal_block + 1]):
		var node := _data.block_nodes[i]
		var path := _grid.get_id_path(Vector2i(_data.node_x[node], _data.node_y[node]), goal)
		if not path.is_empty():
			to_goal[node] = path

	var costs := PackedFloat64Array()
	costs.resize(nodes + 2)
	costs.fill(INF)
	var came := PackedInt32Array()
	came.resize(nodes + 2)
	came.fill(-1)
	var came_link := PackedInt32Array()
	came_link.resize(nodes + 2)
	came_link.fill(-1)
	var closed := PackedByteArray()
	closed.resize(nodes + 2)
	var heap_f := PackedFloat64Array()
	var heap_n := PackedInt32Array()
	var gx := float(goal.x)
	var gy := float(goal.y)
	costs[START] = 0.0
	_push(heap_f, heap_n, Vector2(start).distance_to(Vector2(goal)), START)
	while not heap_n.is_empty():
		var at := heap_n[0]
		_pop(heap_f, heap_n)
		if closed[at]:
			continue
		closed[at] = 1
		if at == GOAL:
			break
		var cost := costs[at]
		if at == START:
			for node: int in from_start:
				_relax(node, cost + _cells_cost(from_start[node]), at, -1, costs, came, came_link, heap_f, heap_n, gx, gy)
			if not direct.is_empty():
				_relax(GOAL, cost + _cells_cost(direct), at, -1, costs, came, came_link, heap_f, heap_n, gx, gy)
			continue
		for link in range(_data.link_offsets[at], _data.link_offsets[at + 1]):
			_relax(_data.link_to[link], cost + _data.link_cost[link], at, link, costs, came, came_link,
					heap_f, heap_n, gx, gy)
		if to_goal.has(at):
			_relax(GOAL, cost + _cells_cost(to_goal[at]), at, -1, costs, came, came_link, heap_f, heap_n, gx, gy)
	if came[GOAL] == -1:
		return []

	# The chain of entrances, then its cells laid end to end.
	var chain := PackedInt32Array()
	var node_at := GOAL
	while node_at != -1:
		chain.append(node_at)
		node_at = came[node_at]
	chain.reverse()
	var cells: Array[Vector2i] = [start]
	for i in range(1, chain.size()):
		var node := chain[i]
		var before := chain[i - 1]
		var stretch: Array[Vector2i]
		if before == START and node == GOAL:
			stretch = direct
		elif before == START:
			stretch = from_start[node]
		elif node == GOAL:
			stretch = to_goal[before]
		else:
			var link := came_link[node]
			var cell: Vector2i = cells[cells.size() - 1]
			for k in range(_data.link_step_offsets[link], _data.link_step_offsets[link + 1]):
				cell += MapNavigationData.STEPS[_data.link_steps[k]]
				cells.append(cell)
			continue
		for k in range(1, stretch.size()):
			cells.append(stretch[k])
	return cells


func _relax(node: int, cost: float, from: int, link: int, costs: PackedFloat64Array, came: PackedInt32Array,
		came_link: PackedInt32Array, heap_f: PackedFloat64Array, heap_n: PackedInt32Array, gx: float, gy: float) -> void:
	if cost >= costs[node]:
		return
	costs[node] = cost
	came[node] = from
	came_link[node] = link
	var left := 0.0
	if node < _data.node_x.size():
		var dx := _data.node_x[node] - gx
		var dy := _data.node_y[node] - gy
		left = sqrt(dx * dx + dy * dy)
	_push(heap_f, heap_n, cost + left, node)


func _push(heap_f: PackedFloat64Array, heap_n: PackedInt32Array, f: float, node: int) -> void:
	heap_f.append(f)
	heap_n.append(node)
	var i := heap_f.size() - 1
	while i > 0:
		var parent := (i - 1) >> 1
		if heap_f[parent] <= f:
			break
		heap_f[i] = heap_f[parent]
		heap_n[i] = heap_n[parent]
		i = parent
	heap_f[i] = f
	heap_n[i] = node


func _pop(heap_f: PackedFloat64Array, heap_n: PackedInt32Array) -> void:
	var last := heap_f.size() - 1
	var f := heap_f[last]
	var node := heap_n[last]
	heap_f.resize(last)
	heap_n.resize(last)
	if last == 0:
		return
	var i := 0
	while true:
		var child := 2 * i + 1
		if child >= last:
			break
		if child + 1 < last and heap_f[child + 1] < heap_f[child]:
			child += 1
		if heap_f[child] >= f:
			break
		heap_f[i] = heap_f[child]
		heap_n[i] = heap_n[child]
		i = child
	heap_f[i] = f
	heap_n[i] = node


## The cost of a path of cells, each a neighbour of the last.
func _cells_cost(path: Array[Vector2i]) -> float:
	var total := 0.0
	for i in range(1, path.size()):
		var a := path[i - 1]
		var b := path[i]
		var length := 1.4142135623730951 if a.x != b.x and a.y != b.y else 1.0
		total += length * 0.5 * (_weights[_ground(a)] + _weights[_ground(b)])
	return total


## The nearest cell to [param cell] the party may stand on, no more than
## [param reach] cells away, or null.
func _passable_near(cell: Vector2i, reach: int) -> Variant:
	for ring in range(1, reach + 1):
		for dx in range(-ring, ring + 1):
			for dy in range(-ring, ring + 1):
				if maxi(absi(dx), absi(dy)) != ring:
					continue
				var near := cell + Vector2i(dx, dy)
				if _weights[_ground(near)] > 0.0:
					return near
	return null


# -- the grid ---------------------------------------------------------------------------------

func _ground(cell: Vector2i) -> int:
	if not _last_rect.has_point(cell):
		var block := _data.block_of(cell)
		if block == -1:
			return MapNavigationData.Ground.SEA
		_use_block(block)
	return _last_cells[(cell.y - _last_rect.position.y) * _last_rect.size.x + cell.x - _last_rect.position.x]


func _use_block(block: int) -> void:
	if block == _last_block:
		return
	if not _blocks.has(block):
		if _blocks.size() >= _cache_limit:
			_blocks.clear()
		_blocks[block] = _data.decode_block(block)
	_last_block = block
	_last_cells = _blocks[block]
	_last_rect = _data.block_rect(block)


## Sets the search grid to block [param block].
func _fill(block: int) -> void:
	if block == _filled:
		return
	_use_block(block)
	MapNavigationData.fill_block_grid(_grid, _last_rect, _last_cells, _weights)
	_filled = block


# -- pulling straight ---------------------------------------------------------------------------

## The path from [param from] through the middles of [param cells] to
## [param to], pulled straight: from each point on to the furthest later one
## a straight stretch reaches no slower than the path does (looked for by
## doubling, then halving, so that a long route stays quick).
func _pull(from: Vector2, cells: Array[Vector2i], to: Vector2) -> PackedVector2Array:
	var points := PackedVector2Array([from])
	for cell in cells:
		points.append(centre_of(cell))
	points.append(to)
	var count := points.size()
	# The cost along the path to each point: a step between two cells'
	# middles costs what the grid says, the stretches in from the start and
	# out to the goal what crossing them costs.
	var along := PackedFloat64Array()
	along.resize(count)
	along[1] = _cost_or_length(points[0], points[1])
	for i in range(1, cells.size()):
		var a := cells[i - 1]
		var b := cells[i]
		var length := 1.4142135623730951 if a.x != b.x and a.y != b.y else 1.0
		along[i + 1] = along[i] + length * 0.5 * (_weights[_ground(a)] + _weights[_ground(b)])
	along[count - 1] = along[count - 2] + _cost_or_length(points[count - 2], points[count - 1])
	var out := PackedVector2Array([points[0]])
	var at := 0
	while at < count - 1:
		var best := at + 1
		var bad := -1
		var span := 2
		while best < count - 1:
			var reach := mini(at + mini(span, LONGEST_PULL), count - 1)
			if reach <= best:
				break
			if _no_slower(points, along, at, reach):
				best = reach
				if reach == count - 1 or span >= LONGEST_PULL:
					break
				span *= 2
			else:
				bad = reach
				break
		if bad != -1:
			var low := best
			var high := bad
			while high - low > 1:
				@warning_ignore("integer_division")
				var middle := (low + high) / 2
				if _no_slower(points, along, at, middle):
					low = middle
				else:
					high = middle
			best = low
		out.append(points[best])
		at = best
	return out


func _no_slower(points: PackedVector2Array, along: PackedFloat64Array, from: int, to: int) -> bool:
	var budget := (along[to] - along[from]) * (1.0 + 1e-9) + 1e-6
	return _pieces(points[from], points[to], budget)


## The cost of a straight stretch within one cell or two, by its length where
## it cannot be crossed, which on a path of cells the party can take is never.
func _cost_or_length(a: Vector2, b: Vector2) -> float:
	if _pieces(a, b):
		var total := 0.0
		for i in _piece_ground.size():
			total += _piece_length[i] * _weights[_piece_ground[i]]
		return total
	return a.distance_to(b) / _data.cell_size


## Walks the cells a straight stretch from [param a] to [param b] passes
## through, putting each one's ground and how far through it the stretch
## goes, in cells, in [member _piece_ground] and [member _piece_length].
## False where it meets a cell the party cannot cross, or passes through a
## corner with such a cell on either side of it, as the grid's own diagonal
## steps may not; or, given a [param budget], as soon as it costs more.
func _pieces(a: Vector2, b: Vector2, budget := INF) -> bool:
	_piece_ground.clear()
	_piece_length.clear()
	var u0 := (a - _data.origin) / _data.cell_size
	var u1 := (b - _data.origin) / _data.cell_size
	var x0 := float(u0.x)
	var y0 := float(u0.y)
	var dx := float(u1.x) - x0
	var dy := float(u1.y) - y0
	var length := sqrt(dx * dx + dy * dy)
	var cx := floori(x0)
	var cy := floori(y0)
	if length < 1e-12:
		var still := _ground(Vector2i(cx, cy))
		if _weights[still] <= 0.0:
			return false
		_piece_ground.append(still)
		_piece_length.append(0.0)
		return true
	var step_x := 0
	var step_y := 0
	var next_x := INF
	var next_y := INF
	var delta_x := INF
	var delta_y := INF
	if dx > 0.0:
		step_x = 1
		next_x = (cx + 1 - x0) / dx
		delta_x = 1.0 / dx
	elif dx < 0.0:
		step_x = -1
		next_x = (cx - x0) / dx
		delta_x = -1.0 / dx
	if dy > 0.0:
		step_y = 1
		next_y = (cy + 1 - y0) / dy
		delta_y = 1.0 / dy
	elif dy < 0.0:
		step_y = -1
		next_y = (cy - y0) / dy
		delta_y = -1.0 / dy
	var t := 0.0
	var spent := 0.0
	var guard := ceili(absf(dx)) + ceili(absf(dy)) + 4
	while guard > 0:
		guard -= 1
		var ground := _ground(Vector2i(cx, cy))
		var leave := minf(minf(next_x, next_y), 1.0)
		var piece := (leave - t) * length
		var weight := _weights[ground]
		if piece > 1e-9 and weight <= 0.0:
			return false
		spent += piece * weight
		if spent > budget:
			return false
		_piece_ground.append(ground)
		_piece_length.append(piece)
		if leave >= 1.0:
			return true
		if absf(next_x - next_y) <= CORNER:
			if _weights[_ground(Vector2i(cx + step_x, cy))] <= 0.0 \
					or _weights[_ground(Vector2i(cx, cy + step_y))] <= 0.0:
				return false
			cx += step_x
			cy += step_y
			t = leave
			next_x += delta_x
			next_y += delta_y
		elif next_x < next_y:
			cx += step_x
			t = next_x
			next_x += delta_x
		else:
			cy += step_y
			t = next_y
			next_y += delta_y
	# More cells than the stretch can cross: never, but not to be trusted.
	return false


# -- legs -------------------------------------------------------------------------------------

## The route along [param turns]: each straight stretch cut where the ground
## under it changes pace, a run shorter than [constant SHORTEST_LEG] cells
## taking the pace of the run beside it on the same stretch, with every
## leg's miles a day and the whole way's days.
func _legs(turns: PackedVector2Array) -> MapRoute:
	var route := MapRoute.new()
	var cell_miles := _data.cell_size / MapCamera.UNITS_A_MILE
	for i in range(1, turns.size()):
		var a := turns[i - 1]
		var b := turns[i]
		if not _pieces(a, b):
			# A turn of the pulled path is always crossable; kept whole at the
			# pace of where it ends should the cells say otherwise.
			_piece_ground.clear()
			_piece_length.clear()
			_piece_ground.append(_ground(cell_of(b)))
			_piece_length.append(a.distance_to(b) / _data.cell_size)
		# Runs of one pace along the stretch: their lengths in cells and days.
		var lengths := PackedFloat64Array()
		var days := PackedFloat64Array()
		var paces := PackedFloat64Array()
		for k in _piece_ground.size():
			var speed := _speeds[_piece_ground[k]]
			var piece := _piece_length[k]
			if speed <= 0.0 or piece <= 0.0:
				continue
			if not paces.is_empty() and paces[paces.size() - 1] == speed:
				lengths[lengths.size() - 1] += piece
				days[days.size() - 1] += piece * cell_miles / speed
			else:
				paces.append(speed)
				lengths.append(piece)
				days.append(piece * cell_miles / speed)
		if lengths.is_empty():
			continue
		_merge_short_runs(lengths, days, paces, cell_miles)
		var total := 0.0
		for length in lengths:
			total += length
		var walked := 0.0
		for k in lengths.size():
			walked += lengths[k]
			var end := b if k == lengths.size() - 1 else a.lerp(b, walked / total)
			route.points.append(end)
			route.miles_per_day.append(lengths[k] * cell_miles / days[k])
			route.days += days[k]
	if route.points.is_empty() or not route.points[route.points.size() - 1].is_equal_approx(turns[turns.size() - 1]):
		# A destination in the very cell the party stands in.
		route.points.append(turns[turns.size() - 1])
		var speed := maxf(_speeds[ground_at(turns[turns.size() - 1])], 0.001)
		route.miles_per_day.append(speed)
		route.days += turns[0].distance_to(turns[turns.size() - 1]) / MapCamera.UNITS_A_MILE / speed
	return route


## Folds each run shorter than [constant SHORTEST_LEG] cells into the run
## before it (or after it, for the first), at that run's pace: a sliver where
## a straight stretch along a road clips the cells beside it is road, so that
## a leg's pace is always one of the grounds' own.
func _merge_short_runs(lengths: PackedFloat64Array, days: PackedFloat64Array, paces: PackedFloat64Array,
		cell_miles: float) -> void:
	var i := 0
	while lengths.size() > 1 and i < lengths.size():
		if lengths[i] >= SHORTEST_LEG:
			i += 1
			continue
		var into := i - 1 if i > 0 else 1
		lengths[into] += lengths[i]
		days[into] = lengths[into] * cell_miles / paces[into]
		lengths.remove_at(i)
		days.remove_at(i)
		paces.remove_at(i)
		if into > i:
			continue
		i = maxi(into, 0)
	# Neighbours of one pace once the slivers between them are gone.
	var k := 1
	while k < lengths.size():
		if paces[k] == paces[k - 1]:
			lengths[k - 1] += lengths[k]
			days[k - 1] += days[k]
			lengths.remove_at(k)
			days.remove_at(k)
			paces.remove_at(k)
		else:
			k += 1
