@tool
## Where the party may go on the new map ([code]Scenes/Map.tscn[/code]) and
## the fastest way there: the scene's Navigation node, which the [Party] asks.
##
## The party keeps off the sea, the lakes, the rivers and the channels, and
## crosses water only by a bridge, unless that water is navigable
## ([member MapWater.navigable]). It goes [constant ROAD_MILES_PER_DAY] miles a
## day on a road, [constant OPEN_MILES_PER_DAY] over open ground and
## [constant FOREST_MILES_PER_DAY] through a forest, and each route is the
## fastest one, a few in a hundred at the most from the best there is.
##
## None of it is worked out as the game runs: the map is baked, from its own
## layers, into [member data_path] ([MapNavigationData], made by
## [MapNavigationBaker]). Bake it again after changing the map: the Bake
## Navigation button in this node's inspector, or without the editor
## [code]BakeMapNavigation.gd[/code]. Until then the node carries a warning in
## the editor, and the game warns as the map opens, but routes go on being
## found over the map as it was baked.
##
## Routes are found on a thread of their own ([method request_route]), most
## within a tenth of a second and the longest in a fifth, so the map never
## waits on one; [MapRouter] does the finding.
class_name MapNavigation
extends Node

## Miles a day on a road, a highway, a lane or a bridge: all roads alike.
const ROAD_MILES_PER_DAY := 25.0
## Miles a day over open ground.
const OPEN_MILES_PER_DAY := 20.0
## Miles a day through a forest, any kind.
const FOREST_MILES_PER_DAY := 15.0
## Miles a day across navigable water: a forest's pace.
const NAVIGABLE_MILES_PER_DAY := FOREST_MILES_PER_DAY
## Seconds between the editor's checks that the bake still matches the map,
## each some 40 ms of reading and hashing the layers.
const EDITOR_CHECK_SECONDS := 15.0

## Bakes the navigation from the map as it stands, into [member data_path],
## and prints what it found to the Output panel. It takes a few seconds, and
## the editor waits for it.
@export_tool_button("Bake Navigation", "Bake") var bake_button: Callable = bake
## The baked navigation.
@export_file("*.res") var data_path := "res://WorldMap/MapNavigation.res"

@export_group("Layers")
## The map: what the layers' points are measured in.
@export var map_path: NodePath = ^".."
## Every polygon under it is land.
@export var land_path: NodePath = ^"../Land"
## Every polygon under it is forest.
@export var forests_path: NodePath = ^"../Forests"
## Every line under it is a road.
@export var roads_path: NodePath = ^"../Roads"
## Every line under it is a bridge: a road over whatever is under it.
@export var bridges_path: NodePath = ^"../Bridges"
## Every polygon under it is a lake, except one with "Island" in its name.
@export var lakes_path: NodePath = ^"../Lakes"
## Every line under it is a river.
@export var rivers_path: NodePath = ^"../Rivers"
## Every line under it is a channel.
@export var channels_path: NodePath = ^"../Channels"
## The sea: everything that is not land. Only its [MapWater] is read.
@export var sea_path: NodePath = ^"../Sea"
## The settlements, which the bake checks can be reached.
@export var settlements_path: NodePath = ^"../Settlements"
## The party, whose starting place the bake checks as well.
@export var party_path: NodePath = ^"../Party"

## The navigation, once loaded as the game runs.
var data: MapNavigationData

var _map: Node2D
## The worker thread's router, the main thread's for looking at the ground,
## and the one [method find_route] uses: never one shared between threads.
var _router: MapRouter
var _lookup: MapRouter
var _sync: MapRouter
var _task := -1
## The request being worked out, and the newest one waiting for it, each
## [from, to, done].
var _working: Array = []
var _queued: Array = []
## In the editor: why the bake is stale ("" when it is not), and when it was
## last looked at.
var _stale := ""
var _checked := false
var _since_check := 0.0
## As the game runs: why the bake did not match the map as it opened, or ""
## (null before it is known). Kept, since [MapDetail] moves the rivers' ends
## in the sea as it sets their widths, and the map would no longer match.
var _opened_stale: Variant = null


## Miles a day over each [enum MapNavigationData.Ground], from the constants
## above: 0 where the party cannot go.
static func speeds() -> PackedFloat32Array:
	var out := PackedFloat32Array()
	out.resize(MapNavigationData.Ground.size())
	out[MapNavigationData.Ground.OPEN] = OPEN_MILES_PER_DAY
	out[MapNavigationData.Ground.FOREST] = FOREST_MILES_PER_DAY
	out[MapNavigationData.Ground.ROAD] = ROAD_MILES_PER_DAY
	out[MapNavigationData.Ground.NAVIGABLE_SEA] = NAVIGABLE_MILES_PER_DAY
	out[MapNavigationData.Ground.NAVIGABLE_WATER] = NAVIGABLE_MILES_PER_DAY
	return out


func _ready() -> void:
	if Engine.is_editor_hint():
		_check_in_editor()
		return
	set_process(false)
	_map = get_node_or_null(map_path) as Node2D
	if _map == null:
		push_error("MapNavigation: no map at '%s'; the party goes in straight lines." % map_path)
		return
	if not ResourceLoader.exists(data_path):
		push_error("MapNavigation: no navigation baked at '%s'; the party goes in straight lines. Bake it: the Bake Navigation button on the Navigation node, or BakeMapNavigation.gd." % data_path)
		return
	data = load(data_path) as MapNavigationData
	if data == null or data.version != MapNavigationBaker.VERSION:
		push_error("MapNavigation: '%s' is not navigation this version can read; the party goes in straight lines. Bake it again." % data_path)
		data = null
		return
	_router = MapRouter.new(data)
	_lookup = MapRouter.new(data, 64)
	# Before the first frame, while the layers are as saved: the Detail node
	# moves some of the rivers' points from its first frame on.
	if OS.is_debug_build():
		_opened_stale = stale_reason()
		if not _opened_stale.is_empty():
			push_warning("MapNavigation: %s, so routes follow the map as it was then. Bake it again: the Bake Navigation button on the Navigation node, or BakeMapNavigation.gd." % _opened_stale)


func _process(delta: float) -> void:
	if not Engine.is_editor_hint():
		return
	_since_check += delta
	if _since_check >= EDITOR_CHECK_SECONDS:
		_check_in_editor()


func _notification(what: int) -> void:
	# A route still being worked out uses the router: let it finish first.
	if what == NOTIFICATION_PREDELETE and _task != -1:
		WorkerThreadPool.wait_for_task_completion(_task)
		_task = -1


func _get_configuration_warnings() -> PackedStringArray:
	if not _checked:
		_stale = stale_reason()
		_checked = true
	if _stale.is_empty():
		return PackedStringArray()
	var sentence := _stale.left(1).to_upper() + _stale.substr(1)
	return PackedStringArray(["%s. Press Bake Navigation in the inspector to bake it again." % sentence])


## Why the baked navigation does not match the map: "" when it does. As the
## game runs, it is the answer from the moment the map opened.
func stale_reason() -> String:
	if _opened_stale != null:
		return _opened_stale
	if not ResourceLoader.exists(data_path):
		return "the navigation has not been baked (no %s)" % data_path
	var baked := data if data != null else load(data_path) as MapNavigationData
	if baked == null:
		return "%s is not navigation" % data_path
	if baked.version != MapNavigationBaker.VERSION:
		return "the navigation was baked by an older version of the bake"
	if baked.signature != MapNavigationBaker.new(self).signature():
		return "the map has changed since the navigation was baked"
	return ""


## Bakes the navigation from the map as it stands, saves it to
## [member data_path] and prints its report: what the Bake Navigation button
## runs, and [code]BakeMapNavigation.gd[/code]. The navigation, or null after
## an error.
func bake() -> MapNavigationData:
	print("MapNavigation: baking the navigation, which takes a few seconds...")
	var baked := MapNavigationBaker.new(self).run()
	if baked == null:
		push_error("MapNavigation: nothing was baked; see the errors above.")
		return null
	baked.take_over_path(data_path)
	var error := ResourceSaver.save(baked, data_path, ResourceSaver.FLAG_COMPRESS)
	if error != OK:
		push_error("MapNavigation: could not save '%s' (%s)." % [data_path, error_string(error)])
		return null
	print(baked.report)
	print("MapNavigation: saved to %s." % data_path)
	if baked.report.contains("PROBLEM"):
		push_warning("MapNavigation: the bake found problems; see its report in the Output.")
	if Engine.is_editor_hint():
		var editor := Engine.get_singleton(&"EditorInterface")
		if editor != null:
			editor.get_resource_filesystem().update_file(data_path)
		_stale = ""
		_checked = true
		_since_check = 0.0
		update_configuration_warnings()
	return baked


## Whether the navigation is loaded. Without it the party goes anywhere, in
## straight lines.
func is_ready() -> bool:
	return _router != null


## Whether the party may stand at [param point], in the map's global
## coordinates: anywhere when the navigation is not loaded.
func is_passable(point: Vector2) -> bool:
	return _lookup == null or _lookup.is_passable(_to_map(point))


## Miles a day over the ground at [param point]: 0 where the party cannot go.
func miles_per_day_at(point: Vector2) -> float:
	return 0.0 if _lookup == null else _lookup.miles_per_day_at(_to_map(point))


## The way from [param from] to [param to], in global coordinates, found
## while the caller waits; null when there is none. For probes: the party
## asks [method request_route].
func find_route(from: Vector2, to: Vector2) -> MapRoute:
	if data == null:
		return null
	if _sync == null:
		_sync = MapRouter.new(data, 64)
	return _to_global(_sync.find_route(_to_map(from), _to_map(to)))


## Works out the way from [param from] to [param to], in global coordinates,
## on a thread of its own, then calls [param done] with the [MapRoute], or
## with null when [param to] cannot be reached. A request made while another
## is being worked out waits for it, and only the newest waiting one is
## worked out next: [param done] is not called for one passed over.
func request_route(from: Vector2, to: Vector2, done: Callable) -> void:
	if _router == null:
		done.call(null)
		return
	var request := [_to_map(from), _to_map(to), done]
	if _task != -1:
		_queued = request
		return
	_start(request)


func _start(request: Array) -> void:
	_working = request
	_task = WorkerThreadPool.add_task(_work.bind(request[0], request[1]), false, "Party route")


## On the worker thread.
func _work(from: Vector2, to: Vector2) -> void:
	_finish.call_deferred(_router.find_route(from, to))


func _finish(route: MapRoute) -> void:
	WorkerThreadPool.wait_for_task_completion(_task)
	_task = -1
	var done: Callable = _working[2]
	_working = []
	if not _queued.is_empty():
		var next := _queued
		_queued = []
		_start(next)
		return
	if done.is_valid():
		done.call(_to_global(route))


func _to_map(point: Vector2) -> Vector2:
	return _map.get_global_transform().affine_inverse() * point if _map != null else point


func _to_global(route: MapRoute) -> MapRoute:
	if route != null and _map != null and _map.get_global_transform() != Transform2D.IDENTITY:
		route.points = _map.get_global_transform() * route.points
	return route


## Looks again whether the bake matches the map, warning in the Output the
## moment it stops matching.
func _check_in_editor() -> void:
	_since_check = 0.0
	var reason := stale_reason()
	_checked = true
	if reason == _stale:
		return
	_stale = reason
	if not reason.is_empty():
		push_warning("MapNavigation: %s. Press Bake Navigation on the Navigation node to bake it again." % reason)
	update_configuration_warnings()
