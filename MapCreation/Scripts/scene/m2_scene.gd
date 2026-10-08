extends SceneTree
## Makes the map's scene, res://Scenes/Map.tscn, out of the shapes m1_shapes.py worked out: areas as
## Polygon2D nodes, lines as Line2D nodes, grouped by what they are and in the order they are drawn,
## and settlements as instances of the game's City.tscn and Town.tscn. After them come the game's
## own nodes for the map: its party, its camera and its level of detail.
##
## A Godot unit is 100 m. A pixel of the pictures is 335 m, so a pixel is 3.35 units, and the
## picture's top left corner is the scene's origin.
##
## Run from vcom/:
##   godot --headless --path . --script <this file> -- <shapes .json> [res://Scenes/Map.tscn]
##
## It writes the whole scene afresh: anything changed in it by hand since is lost.

## Godot units to a pixel of the pictures.
const UNITS := 3.35
## A settlement's icon, by the rank of what it is the capital of: a kingdom's and a duchy's is a
## city, a county's a town. Each scene is a Destination, as Village.tscn and Hamlet.tscn are,
## the two lesser kinds of settlement, which the source data has none of.
const ICON_SCENE := {
	"kingdom": "res://Scenes/City.tscn", "duchy": "res://Scenes/City.tscn", "county": "res://Scenes/Town.tscn",
}
## How far the sea reaches beyond the sheet, in units.
const SEA_BEYOND := 30000.0
## Where the party starts, in units: near the middle of county 115, the middle of its area.
const PARTY_START := Vector2(7302.0, 7381.0)

# Line widths, in Godot units: the pictures' widths in pixels times 3.35, to the whole unit.
const COAST_INK := 23.0          # 7 px. The coast's line is twice this, its inner half under the land.
const BORDER_WIDTH := {"kingdom": 17.0, "duchy": 10.0, "county": 7.0}      # 5, 3 and 2 px
const ROAD_WIDTH := 7.0          # 2 px
const HIGHWAY_WIDTH := 10.0      # 3 px
const BRIDGE_WIDER := 7.0        # a bridge is 2 px wider than its road
## The ranks of border, the least first: the order they are drawn in.
const RANKS := ["county", "duchy", "kingdom"]
const RANK_PLURAL := {"county": "Counties", "duchy": "Duchies", "kingdom": "Kingdoms"}

var _sea := Color8(181, 235, 255)
var _land := Color8(255, 255, 255)
var _ink := Color8(0, 0, 0)
var _water := Color8(28, 112, 224)
var _road := Color8(200, 40, 30)
var _bridge := Color8(60, 35, 15)
var _rank_color := {"kingdom": Color8(233, 0, 255), "duchy": Color8(110, 30, 180), "county": Color8(128, 128, 128)}

var _root: Node2D
var _failed := 0
var _points := 0
var _nodes := 0
var _slowest := 0.0
var _cutting := 0.0


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var shapes: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var write_to: String = args[1] if args.size() > 1 else "res://Scenes/Map.tscn"
	var size: Array = shapes["size"]

	_root = Node2D.new()
	_root.name = "Map"
	_root.editor_description = "The island, about the size of Texas. A unit is 100 m: the map is %d by %d units, and its top left corner is the origin. Made by MapCreation/Scripts/scene from MapCreation/SourceData; see README.md, \"The map\"." % [roundi(size[0] * UNITS), roundi(size[1] * UNITS)]
	_root.set_meta(&"metres_per_unit", 100.0)
	_root.set_meta(&"units_per_picture_pixel", UNITS)

	_add_sea(size)
	_add_coast(shapes["coast"])
	_add_land(shapes["counties"], shapes["kingdoms"])
	_add_borders(shapes["borders"], shapes["banks"])
	_add_lakes(shapes["lakes"])
	_add_rivers(shapes["rivers"])
	_add_borders_over_lakes(shapes["across_lakes"])
	_add_roads(shapes["roads"])
	_add_bridges(shapes["bridges"])
	_add_settlements(shapes["settlements"])
	_add_party()
	_add_camera(size)
	_add_detail()

	_own(_root)
	# Made again, the scene keeps the uid other scenes may know it by: read off the file's first line.
	var uid := ResourceUID.INVALID_ID
	if FileAccess.file_exists(write_to):
		var first := FileAccess.open(write_to, FileAccess.READ).get_line()
		var at := first.find("uid=\"")
		if at >= 0:
			uid = ResourceUID.text_to_id(first.substr(at + 5, first.find("\"", at + 5) - at - 5))
	var packed := PackedScene.new()
	var error := packed.pack(_root)
	if error == OK:
		error = ResourceSaver.save(packed, write_to)
	if error == OK and write_to.begins_with("res://"):
		if uid == ResourceUID.INVALID_ID:
			uid = ResourceUID.create_id()
		ResourceSaver.set_uid(write_to, uid)
	print("nodes ", _nodes, "; points ", _points, "; polygons Godot could not cut into triangles: ", _failed,
			"; cutting them all took ", snappedf(_cutting, 0.1), " ms, the slowest ", snappedf(_slowest, 0.1), " ms")
	print("saved ", write_to, ": ", "ok" if error == OK else "FAILED %d" % error, ", ", FileAccess.get_file_as_bytes(write_to).size(), " bytes")
	_root.free()
	quit(0 if error == OK and _failed == 0 else 1)


# -- the layers ------------------------------------------------------------------------------------------

func _add_sea(size: Array) -> void:
	# The sheet, and far enough beyond it on every side that the view never runs off the sea: with
	# the whole island in view and the camera at the sheet's edge, a wide window sees 17,000 units past it.
	var w: float = size[0] * UNITS
	var h: float = size[1] * UNITS
	var sea := _polygon(_root, "Sea", PackedVector2Array([Vector2(-SEA_BEYOND, -SEA_BEYOND), Vector2(w + SEA_BEYOND, -SEA_BEYOND), Vector2(w + SEA_BEYOND, h + SEA_BEYOND), Vector2(-SEA_BEYOND, h + SEA_BEYOND)]), _sea)
	sea.editor_description = "The sea: the map's sheet and %d units (%d km) more on every side, so that the camera never sees past it." % [int(SEA_BEYOND), int(SEA_BEYOND / 10.0)]


func _add_coast(coast: Array) -> void:
	var group := _group(_root, "Coast", "The coast's black line, %d units wide, all of it outside the land. Each stretch is named for the county whose shore it is (CoastOfCounty003; a county with several has CoastOfCounty003b and so on). It is a line twice that wide along the land's edge, with the same points as that county's polygon, and the land is drawn over its inner half." % int(COAST_INK))
	var names := {}
	for stretch: Dictionary in coast:
		# Named apart from the county's own polygon, County003, so that a search by name finds one thing.
		var line := _line(group, _numbered(names, "CoastOfCounty%03d" % int(stretch["county"])), stretch["points"], 2.0 * COAST_INK, _ink)
		line.closed = stretch["closed"]
		line.begin_cap_mode = Line2D.LINE_CAP_ROUND
		line.end_cap_mode = Line2D.LINE_CAP_ROUND


func _add_land(counties: Array, realms: Array) -> void:
	var group := _group(_root, "Land", "The land, a Polygon2D for each county, grouped by kingdom and duchy. Counties that touch have the same points along the border they share. A kingdom is also a biome, named in its description and in its metadata.")
	var biomes := {}
	for realm: Dictionary in realms:
		biomes[int(realm["number"])] = realm["biome"]
	var kingdoms := {}
	var duchies := {}
	for county: Dictionary in counties:
		var k := int(county["kingdom"])
		var d := int(county["duchy"])
		if not kingdoms.has(k):
			kingdoms[k] = _group(group, "Kingdom%d" % k, biomes[k])
			kingdoms[k].set_meta(&"biome", biomes[k])
		if not duchies.has(d):
			duchies[d] = _group(kingdoms[k], "Duchy%02d" % d, "")
		var pieces: Array = county["pieces"]
		for i in pieces.size():
			# A county's further pieces are islands off its shore.
			var piece_name := "County%03d" % int(county["number"]) + ("" if i == 0 else "Island%d" % i)
			_polygon(duchies[d], piece_name, _to_points(pieces[i]), _land)


func _add_borders(borders: Dictionary, banks: Array) -> void:
	var group := _group(_root, "Borders", "Borders, as lines along the edges the counties share: the lesser first, so that a greater is drawn over it. A border that reaches the coast runs on a little into the coast's line. Water and roads are drawn over the borders. So where a border runs along a river, a lake's shore or a road, a second line (named Along...) lies under that river, shore or road, wide enough to show the border's colour on both sides of it.")
	for rank: String in RANKS:
		var of_rank := _group(group, RANK_PLURAL[rank], "")
		var names := {}
		for border: Dictionary in borders[rank]:
			var line := _line(of_rank, _numbered(names, _border_name(rank, border["between"])), border["points"], BORDER_WIDTH[rank], _rank_color[rank])
			line.begin_cap_mode = Line2D.LINE_CAP_NONE if border["from_coast"] else Line2D.LINE_CAP_ROUND
			line.end_cap_mode = Line2D.LINE_CAP_NONE if border["to_coast"] else Line2D.LINE_CAP_ROUND
		for bank: Dictionary in banks:
			if bank["rank"] != rank:
				continue
			var beside := "%sAlong%s%03d" % [_border_name(rank, bank["between"]), String(bank["along"]).capitalize(), int(bank["id"])]
			var line := _line(of_rank, _numbered(names, beside), bank["points"], snappedf(float(bank["widest"]) * UNITS, 0.1), _rank_color[rank])
			line.closed = bank.get("closed", false)
			line.begin_cap_mode = Line2D.LINE_CAP_ROUND
			line.end_cap_mode = Line2D.LINE_CAP_NONE if bank.get("square_end", false) else Line2D.LINE_CAP_ROUND
			_narrow(line, bank["widths"], bank["widest"], bank["px"])


## Where a border crosses a lake broad enough to show on both sides of it, the border is drawn
## again over the water.
func _add_borders_over_lakes(across: Array) -> void:
	var group := _group(_root, "BordersOverLakes", "Where a border crosses a broad lake it is drawn again here, over the water, with the same points as that part of the border's own line.")
	var names := {}
	for rank: String in RANKS:
		var of_rank := _group(group, RANK_PLURAL[rank], "")
		for piece: Dictionary in across:
			if piece["rank"] != rank:
				continue
			var line := _line(of_rank, _numbered(names, "%sOverLake%03d" % [_border_name(rank, piece["between"]), int(piece["lake"])]), piece["points"], BORDER_WIDTH[rank], _rank_color[rank])
			line.begin_cap_mode = Line2D.LINE_CAP_ROUND
			line.end_cap_mode = Line2D.LINE_CAP_ROUND


func _border_name(rank: String, between: Array) -> String:
	var digits: int = {"county": 3, "duchy": 2, "kingdom": 1}[rank]
	return "%s%sAnd%s" % [RANK_PLURAL[rank], str(int(between[0])).pad_zeros(digits), str(int(between[1])).pad_zeros(digits)]


## A line's width along it, as a curve: [[share of the way, width], ...] against its greatest width.
func _narrow(line: Line2D, widths: Array, widest: float, px: float) -> void:
	if widths.is_empty():
		return
	var curve := Curve.new()
	for step: Array in widths:
		curve.add_point(Vector2(step[0], float(step[1]) / widest), 0.0, 0.0, Curve.TANGENT_LINEAR, Curve.TANGENT_LINEAR)
	# Line2D reads the curve at evenly spaced places: one for every two pixels of the line.
	curve.bake_resolution = clampi(int(px / 2.0), 100, 1000)
	line.width_curve = curve


func _add_lakes(lakes: Array) -> void:
	var group := _group(_root, "Lakes", "The 700 lakes, numbered by size as MapCreation/SourceData/Lakes.json has them, drawn over the borders.")
	for lake: Dictionary in lakes:
		var pieces: Array = lake["pieces"]
		for i in pieces.size():
			_polygon(group, "Lake%03d" % int(lake["id"]) + ("" if i == 0 else char(97 + i)), _to_points(pieces[i]), _water)
		var islands: Array = lake["islands"]
		for i in islands.size():
			_polygon(group, "Lake%03dIsland%d" % [int(lake["id"]), i + 1], _to_points(islands[i]), _land)


func _add_rivers(rivers: Array) -> void:
	var group := _group(_root, "Rivers", "The rivers, numbered by the water they carry as MapCreation/SourceData/Rivers.json has them. A river's width is its width at its widest; its width curve narrows it from there toward its source. A river that reaches the sea runs on a little into the coast's line.")
	for river: Dictionary in rivers:
		var line := _line(group, "River%03d" % int(river["id"]), river["points"], snappedf(float(river["widest"]) * UNITS, 0.1), _water)
		line.begin_cap_mode = Line2D.LINE_CAP_ROUND
		line.end_cap_mode = Line2D.LINE_CAP_NONE if river["ends_in"] == "sea" else Line2D.LINE_CAP_ROUND
		_narrow(line, river["widths"], river["widest"], river["px"])


func _add_roads(roads: Array) -> void:
	var group := _group(_root, "Roads", "Roads, a line for each stretch from one settlement or fork to the next. Settlements go by their county's number.")
	var plain := _group(group, "Roads", "")
	var great := _group(group, "Highways", "Roads on the way between the capitals of two kingdoms that share a border.")
	var names := {}
	for road: Dictionary in roads:
		var road_name := "Road%sTo%s" % [_place(road["from"], road["from_fork"]), _place(road["to"], road["to_fork"])]
		var line := _line(great if road["highway"] else plain, _numbered(names, road_name), road["points"], HIGHWAY_WIDTH if road["highway"] else ROAD_WIDTH, _road)
		line.begin_cap_mode = Line2D.LINE_CAP_ROUND
		line.end_cap_mode = Line2D.LINE_CAP_ROUND


func _add_bridges(bridges: Array) -> void:
	var group := _group(_root, "Bridges", "Bridges: where a road crosses a river, and the one that joins the island town to the mainland. Each lies along its road, a little wider, from bank to bank.")
	for bridge: Dictionary in bridges:
		var line := _line(group, "Bridge%03d" % int(bridge["id"]), bridge["points"], (HIGHWAY_WIDTH if bridge["highway"] else ROAD_WIDTH) + BRIDGE_WIDER, _bridge)
		# Square ends, half the bridge's width past each bank.
		line.begin_cap_mode = Line2D.LINE_CAP_BOX
		line.end_cap_mode = Line2D.LINE_CAP_BOX


func _add_settlements(settlements: Array) -> void:
	var group := _group(_root, "Settlements", "The settlements, an icon each, drawn at one size on the screen whatever the zoom, its middle at the node's position. The 220 capitals, one a county, are cities and towns; villages and hamlets, drawn under them, have groups here and none in them yet.")
	# Hamlets and villages first, so that towns and cities are drawn over them. The source data
	# has neither: the two groups are where instances of Hamlet.tscn and Village.tscn go.
	_group(group, "Hamlets", "Instances of Scenes/Hamlet.tscn go here. None yet.")
	_group(group, "Villages", "Instances of Scenes/Village.tscn go here. None yet.")
	var of_rank := {
		"county": _group(group, "CountyCapitals", "Towns."),
		"duchy": _group(group, "DuchyCapitals", "Cities. A duchy's capital is the capital of one of its counties too."),
		"kingdom": _group(group, "KingdomCapitals", "Cities. A kingdom's capital is the capital of one of its duchies and of one of its counties too."),
	}
	for settlement: Dictionary in settlements:
		var rank: String = settlement["rank"]
		var icon_name := ""
		# Nothing on the map is named yet, so the tooltip says what the place is the capital of.
		var shown := ""
		match rank:
			"kingdom":
				icon_name = "Kingdom%dCapital" % int(settlement["kingdom"])
				shown = "Capital of Kingdom %d" % int(settlement["kingdom"])
			"duchy":
				icon_name = "Duchy%02dCapital" % int(settlement["duchy"])
				shown = "Capital of Duchy %d" % int(settlement["duchy"])
			_:
				icon_name = "County%03dCapital" % int(settlement["county"])
				shown = "Capital of County %d" % int(settlement["county"])
		# As the editor instances a scene: packed, the node then keeps only what differs from its
		# scene (where it is, its name, its numbers), so a change to City.tscn reaches every city.
		var icon: Node2D = (load(ICON_SCENE[rank]) as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
		icon.name = icon_name
		icon.position = _to_point(settlement["at"][0], settlement["at"][1])
		icon.set(&"display_name", shown)
		icon.set_meta(&"county", int(settlement["county"]))
		icon.set_meta(&"duchy", int(settlement["duchy"]))
		icon.set_meta(&"kingdom", int(settlement["kingdom"]))
		of_rank[rank].add_child(icon)
		_nodes += 1


## The player's party (Scripts/WorldMap/Party.gd), as on the old world map, drawn over the
## settlements. It starts at PARTY_START, and with no terrain to ask (the map has no land collider
## or navigation mesh yet) it goes wherever it is sent in a straight line.
func _add_party() -> void:
	var party := Node2D.new()
	party.name = "Party"
	party.set_script(load("res://Scripts/WorldMap/Party.gd"))
	party.set(&"terrain_path", NodePath(""))
	party.position = PARTY_START
	party.editor_description = "The player's party, the red dot, drawn over the settlements. Where it is here is where it starts: near the middle of county 115. A right click sends it there (on a settlement's icon, to the settlement), and it goes in a straight line, over water as over land: this map has no land for it to keep to yet, which is why its Terrain Path is empty. Its speed and its steps are in the map's units, 100 m each."
	_root.add_child(party)
	_nodes += 1


## The map's own camera, so that the scene can be run by itself and looked over. It pans and
## zooms as the world map's does and takes its limits from the land (Scripts/WorldMap/MapCamera.gd):
## all the way out the whole land just fits the window, all the way in the view is just large
## enough for any one county's outline, and the view never leaves what is seen all the way out.
func _add_camera(size: Array) -> void:
	var camera := Camera2D.new()
	camera.name = "Camera"
	camera.set_script(load("res://Scripts/WorldMap/MapCamera.gd"))
	camera.set(&"map_path", NodePath(""))
	camera.set(&"fit_margin", 1.0)
	camera.position = Vector2(size[0], size[1]) * UNITS * 0.5
	camera.editor_description = "Pans and zooms as on the world map (WASD, the screen's edges, the middle mouse button, the wheel). All the way out, the whole land just fits the window, and nothing can be panned. All the way in, the view is 25 miles tall (this node's Closest View Miles). The view never leaves what is seen all the way out. The land's extent is read off the Land and Coast nodes as the scene opens."
	_root.add_child(camera)
	_nodes += 1


## The map's level of detail (Scripts/WorldMap/MapDetail.gd): while the game runs it shows and hides
## the layers by how far the view is zoomed, and sets the lines' widths. It reads the layers by the
## names they are given above, and changes nothing in the scene as it is saved.
func _add_detail() -> void:
	var detail := Node.new()
	detail.name = "Detail"
	detail.set_script(load("res://Scripts/WorldMap/MapDetail.gd"))
	detail.editor_description = "Level of detail by the zoom, while the game runs: what shows and how wide the lines are follow how tall the view is in miles. Realm (the whole island): the coast, the kingdoms' borders and capitals, the greatest rivers and lakes. Kingdom (under 480 miles): the duchies' borders and capitals, the highways, more rivers and lakes. Duchy (under 240): the counties' borders and capitals, the other roads, the bridges, every river and lake. County (under 100): the villages and hamlets. A line is as wide as its node says when the view is 220 miles tall, and grows only a little with the zoom from there. The editor shows everything, at the widths given."
	_root.add_child(detail)
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


func _polygon(parent: Node, polygon_name: String, points: PackedVector2Array, color: Color, check := true) -> Polygon2D:
	var polygon := Polygon2D.new()
	polygon.name = polygon_name
	polygon.polygon = points
	polygon.color = color
	parent.add_child(polygon)
	_nodes += 1
	_points += points.size()
	if check:
		var start := Time.get_ticks_usec()
		var cut := Geometry2D.triangulate_polygon(points)
		var took := (Time.get_ticks_usec() - start) / 1000.0
		_cutting += took
		_slowest = maxf(_slowest, took)
		if cut.is_empty():
			_failed += 1
			print("   could not be cut into triangles: ", polygon_name, " (", points.size(), " points)")
	return polygon


func _line(parent: Node, line_name: String, flat: Array, width: float, color: Color) -> Line2D:
	var line := Line2D.new()
	line.name = line_name
	line.points = _to_points(flat)
	line.width = width
	line.default_color = color
	line.joint_mode = Line2D.LINE_JOINT_ROUND
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


## A name, with b, c and so on after it the second and later times it is asked for.
func _numbered(names: Dictionary, wanted: String) -> String:
	var count: int = names.get(wanted, 0)
	names[wanted] = count + 1
	return wanted if count == 0 else wanted + char(97 + count)


func _place(id: float, fork: bool) -> String:
	return "Fork%03d" % int(id) if fork else "%03d" % int(id)


func _own(node: Node) -> void:
	for child in node.get_children():
		child.owner = _root
		_own(child)
