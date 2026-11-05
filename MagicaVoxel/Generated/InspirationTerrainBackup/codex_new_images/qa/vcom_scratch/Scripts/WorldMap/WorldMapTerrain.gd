## Where the party can go on the world map, and the way there.
##
## The land is the collider [code]BakeLand.gd[/code] traced from the map art:
## a [StaticBody2D] of [CollisionPolygon2D] outlines following the edge of the
## land pixel for pixel, made a child of the map sprite so it turns and moves
## with it. A point is land when an odd number of those outlines surround it,
## which is inside a shore and not inside a lake on it.
##
## That is counted here rather than with [method Geometry2D.is_point_in_polygon],
## which casts a slanted ray and misjudges it where the ray grazes a vertex:
## on a coastline of tens of thousands of pixel corners it got about one coast
## pixel in a hundred wrong. Instead each outline's edges are sorted by the row
## of map pixels they pass through, and a point counts the edges of its own row
## that cross the horizontal line to its right, each counted on a half-open
## span of height so a vertex is never counted twice.
##
## A route is a straight line when a ray along it meets none of the collider's
## segments. When one does, the way comes from the navigation mesh baked beside
## the outlines, which covers exactly the same land, pulled straight with the
## same rays: from each turn, on to the furthest turn in clear sight. The
## server's own search picks a chain of polygons and straightens only inside
## it, and with the thousands of small polygons a pixel coastline makes it
## often went the long way round, over a thousand pixels off a clear line.
## The navigation server takes the mesh in on a thread of its own, over a
## second after the map opens; until it has, [method is_ready] is false and
## only straight routes are found.
class_name WorldMapTerrain
extends Node

## The land collider. Leave empty to let the party go anywhere, in straight
## lines.
@export var land_path: NodePath = ^"../Map/Land"

## How close, in map pixels, a route has to end to the point asked for to
## count as reaching it. Anything further means the point is on land the
## route cannot get to, such as an island.
const ARRIVAL_TOLERANCE := 0.5
## How far, in map pixels, a point on a route may sit off the straight line
## between its neighbours and still be dropped as no real turn.
const SIMPLIFY_EPSILON := 0.01

var _land: Node2D
var _navigation: NavigationRegion2D
## A point inside the navigation mesh, in the region's own coordinates, that
## [method is_ready] asks the server about.
var _mesh_point := Vector2.ZERO
var _outlines: Array[CollisionPolygon2D] = []
## Per outline, in the same order: the first row its edges reach, and for each
## row from there the edges passing through it, packed as x1, y1, x2, y2.
var _first_rows: PackedInt32Array = []
var _rows: Array[Array] = []
var _query := NavigationPathQueryParameters2D.new()
var _result := NavigationPathQueryResult2D.new()
var _ray := PhysicsRayQueryParameters2D.new()


func _ready() -> void:
	if land_path.is_empty():
		return
	_land = get_node_or_null(land_path) as Node2D
	if _land == null:
		push_error("WorldMapTerrain: no land collider at '%s'; the party can go anywhere." % land_path)
		return
	for child in _land.get_children():
		if child is CollisionPolygon2D:
			_outlines.append(child)
			_index_rows(child.polygon)
		elif child is NavigationRegion2D:
			_navigation = child
	var body := _land as CollisionObject2D
	if body != null:
		_ray.collision_mask = body.collision_layer
	if _outlines.is_empty():
		push_error("WorldMapTerrain: '%s' has no CollisionPolygon2D outlines." % land_path)
	# The land is traced from a mask centred as the art is, so the two must be
	# the same size or the coast lands in the wrong place.
	var art := _land.get_parent() as Sprite2D
	if art != null and art.texture != null and _land.has_meta(&"mask_size") \
			and Vector2i(art.texture.get_size()) != _land.get_meta(&"mask_size"):
		push_warning("WorldMapTerrain: the land was baked from a %s mask, but the map art is %s; the coast will not line up." % [
			_land.get_meta(&"mask_size"), Vector2i(art.texture.get_size())])
	# A pixel-exact coastline makes a mesh of tens of thousands of polygons,
	# and by default a search gives up after 4096 of them and settles for the
	# nearest point it found, which would turn a long trip down.
	_query.path_search_max_polygons = 0
	# The funnel leaves a point on every polygon edge a straight stretch
	# crosses, and this mesh has one every few pixels along the coast and at
	# every tile line. Only the turns matter.
	_query.simplify_path = true
	_query.simplify_epsilon = SIMPLIFY_EPSILON
	if _navigation == null or _navigation.navigation_polygon == null \
			or _navigation.navigation_polygon.get_polygon_count() == 0:
		push_error("WorldMapTerrain: '%s' has no baked navigation mesh; there will be no routes." % land_path)
		_navigation = null
		return
	var mesh := _navigation.navigation_polygon
	for index in mesh.get_polygon(0):
		_mesh_point += mesh.vertices[index]
	_mesh_point /= mesh.get_polygon(0).size()


## Whether the navigation server has the land yet, and so whether
## [method find_route] can find anything. Always true with no land collider.
func is_ready() -> bool:
	if _outlines.is_empty():
		return true
	if _navigation == null:
		return false
	var map := _land.get_world_2d().navigation_map
	# Asking before the map's first update is an error rather than a no.
	if NavigationServer2D.map_get_iteration_id(map) == 0:
		return false
	return NavigationServer2D.map_get_closest_point_owner(map, _navigation.to_global(_mesh_point)) != RID()


## Whether [param point], in global map coordinates, is land the party can
## stand on. With no land collider every point is.
func is_land(point: Vector2) -> bool:
	if _outlines.is_empty():
		return true
	var inside := false
	for i in _outlines.size():
		if _encloses(i, _outlines[i].to_local(point)):
			inside = not inside
	return inside


## The turns the party makes going from [param from] to [param to], in global
## map coordinates: the points it heads for in order, ending at [param to].
## Empty when [param to] is not land or cannot be reached from [param from]
## over land, and, unless the way is straight, until [method is_ready].
func find_route(from: Vector2, to: Vector2) -> PackedVector2Array:
	if _outlines.is_empty():
		return PackedVector2Array([to])
	if not is_land(to):
		return PackedVector2Array()
	if is_line_clear(from, to):
		return PackedVector2Array([to])
	if _navigation == null or not is_ready():
		return PackedVector2Array()
	_query.map = _land.get_world_2d().navigation_map
	_query.start_position = from
	_query.target_position = to
	NavigationServer2D.query_path(_query, _result)
	var path := _result.path
	# The server heads for the nearest point it can reach, so a path that
	# stops short of the point means the point is out of reach.
	if path.is_empty() or path[path.size() - 1].distance_to(to) > ARRIVAL_TOLERANCE:
		return PackedVector2Array()
	path[path.size() - 1] = to
	return _pulled_straight(path)


## Whether a straight line from [param from] to [param to], in global map
## coordinates, stays on the land: whether it crosses none of the collider's
## outlines. A line that only touches the coast at a corner counts as
## crossing it, which only ever keeps a turn a route could have done without.
func is_line_clear(from: Vector2, to: Vector2) -> bool:
	if _outlines.is_empty():
		return true
	_ray.from = from
	_ray.to = to
	return _land.get_world_2d().direct_space_state.intersect_ray(_ray).is_empty()


## [param path], starting where the party stands, cut down to the turns it
## needs: from each turn it heads for the furthest later point it can see,
## leaving out the ones in between. Leaves out the starting point.
func _pulled_straight(path: PackedVector2Array) -> PackedVector2Array:
	var route := PackedVector2Array()
	var at := 0
	while at < path.size() - 1:
		var next := at + 1
		for further in range(path.size() - 1, at + 1, -1):
			if is_line_clear(path[at], path[further]):
				next = further
				break
		route.append(path[next])
		at = next
	return route


## Whether outline [param index] surrounds [param point], in the outline's own
## coordinates: whether an odd number of its edges cross the line running
## right from the point.
func _encloses(index: int, point: Vector2) -> bool:
	var row := floori(point.y) - _first_rows[index]
	var rows: Array = _rows[index]
	if row < 0 or row >= rows.size():
		return false
	var edges: PackedFloat32Array = rows[row]
	var inside := false
	for i in range(0, edges.size(), 4):
		var y1 := edges[i + 1]
		var y2 := edges[i + 3]
		# Half-open in height: an edge counts when the point is at or below
		# one end and above the other, so where two edges meet at a vertex
		# exactly one of them counts, and a flat edge never does.
		if (y1 <= point.y) == (y2 <= point.y):
			continue
		var x1 := edges[i]
		var x := x1 + (point.y - y1) * (edges[i + 2] - x1) / (y2 - y1)
		if x > point.x:
			inside = not inside
	return inside


## Files each edge of [param polygon] under every row of pixels it reaches,
## for [method _encloses].
func _index_rows(polygon: PackedVector2Array) -> void:
	var rows: Array = []
	var first := 0
	if not polygon.is_empty():
		var top := INF
		var bottom := -INF
		for point in polygon:
			top = minf(top, point.y)
			bottom = maxf(bottom, point.y)
		first = floori(top)
		for i in floori(bottom) - first + 1:
			rows.append(PackedFloat32Array())
	for i in polygon.size():
		var a := polygon[i]
		var b := polygon[(i + 1) % polygon.size()]
		if a.y == b.y:
			continue
		for row in range(floori(minf(a.y, b.y)) - first, floori(maxf(a.y, b.y)) - first + 1):
			var edges: PackedFloat32Array = rows[row]
			edges.append_array([a.x, a.y, b.x, b.y])
			rows[row] = edges
	_first_rows.append(first)
	_rows.append(rows)
