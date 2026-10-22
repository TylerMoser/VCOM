extends SceneTree
## Makes parts of the map's scene, res://Scenes/Map.tscn, out of shapes, each under the group it
## belongs in and nothing else: a scene of those alone, to be spliced into the map's scene as it is,
## where nothing else is touched. Given "villages", the villages and hamlets (instances of the
## game's Village.tscn and Hamlet.tscn), their lanes, the bridges on those and the Swamp's channels,
## from ../villages/v2_shapes.py's shapes, for ../villages/v3_splice.py; given "forests", the
## forests' pieces as instances of their kinds' scenes, which are Forests (ConiferForest.tscn and
## the rest), from ../forests/f2_shapes.py's, for ../forests/f3_splice.py.
##
## It made the whole scene once, on 2026-10-07, out of the shapes m1_shapes.py worked out. The
## scene has been changed by hand since, and on 2026-10-18 it was given a new look (Docs/MAP.md,
## "Its look"), so the part of this program that made the whole scene was taken out: run again, it
## would have written the scene afresh in the old look, over every change. It is in git's history,
## last at commit d8b5ec7.
##
## What it makes is drawn as the map draws it now: the lanes and the bridges on them with their
## kinds' materials (Resources/MapLines/), at their widths and in their colours, and the channels in
## the rivers' blue. A Godot unit is 100 m. A pixel of the pictures is 335 m, so a pixel is 3.35
## units, and the picture's top left corner is the scene's origin.
##
## Run from vcom/:
##   godot --headless --path . --script <this file> -- <shapes .json> <a scene to write> villages
##   godot --headless --path . --script <this file> -- <shapes .json> <a scene to write> forests

## Godot units to a pixel of the pictures.
const UNITS := 3.35
## The map's own scene, which this never writes: what it makes is spliced into it.
const MAP := "res://Scenes/Map.tscn"
## A village's or a hamlet's icon. Each scene is a Destination.
const ICON_SCENE := {"village": "res://Scenes/Village.tscn", "hamlet": "res://Scenes/Hamlet.tscn"}

# The lines, as the map draws them (Docs/MAP.md, "Its look"): widths in Godot units, and a lane's
# look its material's, the line's colour the fill.
const LANE_WIDTH := 8.0          # a village's lane, narrower than any road (16)
const LANE_BRIDGE_WIDTH := 11.6  # a lane's bridge, 1.45 times the lane, as a road's is its road
const CHANNEL_WIDTH := 4.0       # a swamp village's channel, narrower than any river
const LANE_MATERIAL := "res://Resources/MapLines/Lane.tres"
const LANE_BRIDGE_MATERIAL := "res://Resources/MapLines/LaneBridge.tres"
const LANE_COLOR := Color(1, 1, 1)

const SETTLEMENTS_ABOUT := "The settlements, an icon each, drawn at one size on the screen whatever the zoom, its middle at the node's position. The 220 capitals, one a county, are cities and towns; the villages and hamlets, about 2,000, are drawn under them. Each stands off the water, where the party can reach it: one by a river is on one bank, and is reached from that side only. The Navigation node's bake checks every one."
## Every node of water in the scene has it (Docs/MAP.md, "Navigation"): the channels too.
const WATER_SCRIPT := "res://Scripts/WorldMap/MapWater.gd"
## A forest's piece, by its kind: each scene a Forest (Scripts/WorldMap/Forest.gd), which inherits
## Forest.tscn's odds of the party being set upon and sets only its colour.
const FOREST_SCENE := {
	"conifer": "res://Scenes/ConiferForest.tscn", "broadleaf": "res://Scenes/BroadleafForest.tscn",
	"tropical": "res://Scenes/TropicalForest.tscn", "swamp": "res://Scenes/SwampForest.tscn",
}
const FORESTS_ABOUT := "The forests (MapCreation/Scripts/forests/f1_forests.py), drawn over the land and under everything else: a Forest for each piece, cut along the counties' borders and the coast and by kind (conifer, broadleaf, tropical, swamp, each a scene of its own colour), named for its county and numbered in it, the largest first. Grouped by the size of the whole forest a piece belongs to (its metadata's forest and forest_km2), so that the Detail node brings the smaller in as the view closes in, and under that by kingdom. Polygon2D draws no holes, so a clearing in a piece is joined to its outline by a cut of no width, there and back. The party may be set upon in any of them, at Forest.tscn's odds, and goes 15 miles a day through them, 20 over the open land between (MapNavigation's constants)."
## The groups of the forests by the size of the whole forest, the order they are drawn in, and what
## each says of itself.
const FOREST_GROUPS := [
	["Great", "Forests of 250 km2 and more, and every piece of them. They show at every zoom."],
	["Large", "Forests of 50 to 250 km2. They show from the Kingdom tier in (see the Detail node)."],
	["Small", "Forests of 10 to 50 km2. They show from the Duchy tier in (see the Detail node)."],
	["Woods", "Woods under 10 km2, the smallest 0.5 km2. They show from the County tier in (see the Detail node)."],
]

## The rivers' blue, which the channels are drawn in.
var _river_color := Color8(109, 194, 243)

var _root: Node2D
var _failed := 0
var _points := 0
var _nodes := 0
var _slowest := 0.0
var _cutting := 0.0


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var what: String = args[2] if args.size() > 2 else ""
	if what != "villages" and what != "forests":
		push_error("m2_scene.gd: give <shapes .json> <a scene to write> villages|forests; it makes no whole scene any more.")
		quit(1)
		return
	var write_to: String = args[1]
	if ProjectSettings.globalize_path(write_to).simplify_path() == ProjectSettings.globalize_path(MAP).simplify_path():
		push_error("m2_scene.gd: it never writes %s itself: write a scene of the %s alone, and splice that in." % [MAP, what])
		quit(1)
		return
	var shapes: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if what == "villages":
		_write_villages_alone(shapes, write_to)
	else:
		_write_forests_alone(shapes, write_to)


## The villages and hamlets, their lanes, the bridges on those and the swamp's channels alone, each
## under the group it belongs in (Settlements/Villages, Roads/Lanes, Bridges/Lanes, Channels), and
## nothing else: for ../villages/v3_splice.py to splice into the scene as it is.
func _write_villages_alone(shapes: Dictionary, write_to: String) -> void:
	_root = Node2D.new()
	_root.name = "Map"
	_add_channels(_root, shapes["channels"])
	_add_lanes(_group(_root, "Roads", ""), shapes["lanes"])
	_add_lane_bridges(_group(_root, "Bridges", ""), shapes["lane_bridges"])
	_add_villages(_group(_root, "Settlements", SETTLEMENTS_ABOUT), shapes["villages"])
	_save(write_to)
	print("nodes ", _nodes, "; points ", _points)


## The forests alone, under their groups, and nothing else: for ../forests/f3_splice.py to splice into
## the scene as it is.
func _write_forests_alone(shapes: Dictionary, write_to: String) -> void:
	_root = Node2D.new()
	_root.name = "Map"
	_add_forests(_root, shapes["forests"])
	_save(write_to)
	print("nodes ", _nodes, "; points ", _points, "; polygons Godot could not cut into triangles: ", _failed,
			"; cutting them all took ", snappedf(_cutting, 0.1), " ms, the slowest ", snappedf(_slowest, 0.1), " ms")


func _save(write_to: String) -> void:
	_own(_root)
	var packed := PackedScene.new()
	var error := packed.pack(_root)
	if error == OK:
		error = ResourceSaver.save(packed, write_to)
	print("saved ", write_to, ": ", "ok" if error == OK else "FAILED %d" % error, ", ", FileAccess.get_file_as_bytes(write_to).size(), " bytes")
	_root.free()
	quit(0 if error == OK and _failed == 0 else 1)


# -- the layers ------------------------------------------------------------------------------------------

## The forests: an instance of its kind's scene for each piece (forestshapes.py), under the group of
## its forest's size and, in that, of its kingdom. The pieces' points are in the scene's units
## already, rounded as forestshapes.py checked them against Godot's own cutter into triangles, so
## they are put in as they are.
func _add_forests(parent: Node, forests: Array) -> void:
	if forests.is_empty():
		return
	var group := _group(parent, "Forests", FORESTS_ABOUT)
	var sizes := {}
	for entry: Array in FOREST_GROUPS:
		sizes[entry[0]] = _group(group, entry[0], entry[1])
	var kingdoms := {}
	for piece: Dictionary in forests:
		var size: String = piece["group"]
		var k := int(piece["kingdom"])
		if not kingdoms.has(size + str(k)):
			kingdoms[size + str(k)] = _group(sizes[size], "Kingdom%d" % k, "")
		var flat: Array = piece["points"]
		var points := PackedVector2Array()
		points.resize(flat.size() / 2)
		for i in points.size():
			points[i] = Vector2(flat[2 * i], flat[2 * i + 1])
		# As the editor instances a scene: packed, the node keeps only its outline and its numbers, so a
		# change to its kind's scene (a colour) or to Forest.tscn (the odds) reaches every piece.
		var forest: Polygon2D = (load(FOREST_SCENE[piece["kind"]]) as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
		forest.name = piece["name"]
		forest.polygon = points
		forest.set_meta(&"county", int(piece["county"]))
		forest.set_meta(&"duchy", int(piece["duchy"]))
		forest.set_meta(&"kingdom", k)
		forest.set_meta(&"forest", int(piece["forest"]))
		forest.set_meta(&"forest_km2", float(piece["forest_km2"]))
		kingdoms[size + str(k)].add_child(forest)
		_nodes += 1
		_points += points.size()
		_check_cut(piece["name"], points)
	# Groups no piece fell in are left out.
	for size: String in sizes:
		if sizes[size].get_child_count() == 0:
			group.remove_child(sizes[size])
			sizes[size].free()


## The villages' lanes (see MapCreation/Scripts/villages/v1_villages.py), each named for its village.
func _add_lanes(roads: Node, lanes: Array) -> void:
	if lanes.is_empty():
		return
	var group := _group(roads, "Lanes", "The villages' lanes: a line from each village not on a road to the nearest road, lane, joined village or capital, laid by the roads' own rules, and named for its village. Narrower than any road, and drawn under them. They show with the villages, from the County tier in (see the Detail node).")
	var material := load(LANE_MATERIAL) as Material
	for lane: Dictionary in lanes:
		var line := _line(group, lane["name"], lane["points"], LANE_WIDTH, LANE_COLOR, material)
		line.begin_cap_mode = Line2D.LINE_CAP_ROUND
		line.end_cap_mode = Line2D.LINE_CAP_ROUND


## The bridges where a lane crosses a river or a channel, under the bridges' group, so that they
## are drawn over the rivers and the lanes; their own group shows with the lanes.
func _add_lane_bridges(bridges: Node, lane_bridges: Array) -> void:
	if lane_bridges.is_empty():
		return
	var group := _group(bridges, "Lanes", "Bridges where a village's lane crosses a river or a channel, named for the village, as a road's are drawn but narrower. They show with the lanes, from the County tier in (see the Detail node).")
	var material := load(LANE_BRIDGE_MATERIAL) as Material
	for bridge: Dictionary in lane_bridges:
		var line := _line(group, bridge["name"], bridge["points"], LANE_BRIDGE_WIDTH, LANE_COLOR, material)
		line.begin_cap_mode = Line2D.LINE_CAP_BOX
		line.end_cap_mode = Line2D.LINE_CAP_BOX


## The channels dug from the swamp's villages to its rivers, lakes and the sea, after the rivers so
## that one ends unseen in the water it reaches. Each is water to the map's navigation, so it has
## the water's script (MapWater: whether the party may cross it, no by default).
func _add_channels(parent: Node, channels: Array) -> void:
	if channels.is_empty():
		return
	var group := _group(parent, "Channels", "Channels dug from the Swamp's villages that stand away from the water to the nearest river, lake or the sea, named for the village: their way to the rest of the map, in place of a lane. Narrower than any river. They show with the villages, from the County tier in (see the Detail node). Each stops the party as a river does, unless its MapWater script's Navigable box is ticked (off for now), and its village stands on the land by its first point.")
	var water := load(WATER_SCRIPT) as Script
	for channel: Dictionary in channels:
		var line := _line(group, channel["name"], channel["points"], CHANNEL_WIDTH, _river_color)
		line.set_script(water)
		line.begin_cap_mode = Line2D.LINE_CAP_ROUND
		# One that reaches the sea stops at the land's edge.
		line.end_cap_mode = Line2D.LINE_CAP_NONE if channel["ends_in"] == "sea" else Line2D.LINE_CAP_ROUND


## The hamlets' and the villages' groups, hamlets first so that villages are drawn over them, with
## an instance of Hamlet.tscn or Village.tscn for each (MapCreation/Scripts/villages/v1_villages.py),
## numbered in its county, the nearest its capital first.
func _add_villages(settlements: Node, villages: Array) -> void:
	var of_kind := {
		"hamlet": _group(settlements, "Hamlets", "Hamlets, instances of Scenes/Hamlet.tscn: a few farms or herders' steadings, named for their county and numbered in it, the nearest its capital first. No lane leads to them. They show from the County tier's second step in, under 50 miles (see the Detail node)."),
		"village": _group(settlements, "Villages", "Villages, instances of Scenes/Village.tscn, named for their county and numbered in it, the nearest its capital first. Each is on a road, or has a lane to the network (Roads/Lanes), or in the Swamp stands by the water or has a channel to it (Channels). They show from the County tier in (see the Detail node)."),
	}
	for village: Dictionary in villages:
		var kind: String = village["kind"]
		var icon: Node2D = (load(ICON_SCENE[kind]) as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
		icon.name = village["name"]
		icon.position = _to_point(village["at"][0], village["at"][1])
		# Nothing is named yet, so the tooltip says what it is and where.
		icon.set(&"display_name", "%s in County %d" % [kind.capitalize(), int(village["county"])])
		icon.set_meta(&"county", int(village["county"]))
		icon.set_meta(&"duchy", int(village["duchy"]))
		icon.set_meta(&"kingdom", int(village["kingdom"]))
		of_kind[kind].add_child(icon)
		_nodes += 1


# -- nodes -------------------------------------------------------------------------------------------------

func _group(parent: Node, group_name: String, description: String) -> Node2D:
	var group := Node2D.new()
	group.name = group_name
	if description != "":
		group.editor_description = description
	parent.add_child(group)
	_nodes += 1
	return group


## Tries a polygon in Godot's own cutter into triangles, which Polygon2D uses as it draws, and counts
## the time it took and any it could not cut.
func _check_cut(polygon_name: String, points: PackedVector2Array) -> void:
	var start := Time.get_ticks_usec()
	var cut := Geometry2D.triangulate_polygon(points)
	var took := (Time.get_ticks_usec() - start) / 1000.0
	_cutting += took
	_slowest = maxf(_slowest, took)
	if cut.is_empty():
		_failed += 1
		print("   could not be cut into triangles: ", polygon_name, " (", points.size(), " points)")


## A line, drawn by its kind's [param material] where it has one, which Scripts/WorldMap/MapLine.gdshader
## draws by the line's UVs: those it has only with texture_mode Tile.
func _line(parent: Node, line_name: String, flat: Array, width: float, color: Color, material: Material = null) -> Line2D:
	var line := Line2D.new()
	line.name = line_name
	line.points = _to_points(flat)
	line.width = width
	line.default_color = color
	line.joint_mode = Line2D.LINE_JOINT_ROUND
	if material != null:
		line.material = material
		line.texture_mode = Line2D.LINE_TEXTURE_TILE
	parent.add_child(line)
	_nodes += 1
	_points += line.points.size()
	return line


## The picture's pixels to the scene's units, to the hundredth of a unit (a metre).
func _to_point(x: float, y: float) -> Vector2:
	return Vector2(snappedf(x * UNITS, 0.01), snappedf(y * UNITS, 0.01))


func _to_points(flat: Array) -> PackedVector2Array:
	var points := PackedVector2Array()
	points.resize(flat.size() / 2)
	for i in points.size():
		points[i] = _to_point(flat[2 * i], flat[2 * i + 1])
	return points


func _own(node: Node) -> void:
	for child in node.get_children():
		child.owner = _root
		_own(child)
