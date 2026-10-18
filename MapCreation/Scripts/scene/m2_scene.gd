extends SceneTree
## Makes the map's scene, res://Scenes/Map.tscn, out of the shapes m1_shapes.py worked out: areas as
## Polygon2D nodes, lines as Line2D nodes, grouped by what they are and in the order they are drawn,
## settlements as instances of the game's City.tscn and Town.tscn (and Village.tscn and
## Hamlet.tscn), and the forests' pieces as instances of their kinds' scenes, which are Forests
## (ConiferForest.tscn and the rest), right after the land. After them come the game's
## own nodes for the map: its party, its camera, the gamepad's reticle, the menu of the settlement
## the party is in, the menu that picks who fights a battle, the game's end, and its level of detail.
##
## A Godot unit is 100 m. A pixel of the pictures is 335 m, so a pixel is 3.35 units, and the
## picture's top left corner is the scene's origin.
##
## Run from vcom/:
##   godot --headless --path . --script <this file> -- <shapes .json> [res://Scenes/Map.tscn]
##
## It writes the whole scene afresh: anything changed in it by hand since is lost.
##
## Given "villages" after the scene to write, it makes only the villages and hamlets, the lanes
## and the bridges on them and the channels, from shapes that hold nothing else
## (../villages/v2_shapes.py), each under the group it belongs in: a scene of those alone, to be
## spliced into the scene as it is (../villages/v3_splice.py), where nothing else is touched.
## Given "forests", likewise the forests alone (../forests/f2_shapes.py, ../forests/f3_splice.py).

## Godot units to a pixel of the pictures.
const UNITS := 3.35
## A settlement's icon, by the rank of what it is the capital of: a kingdom's and a duchy's is a
## city, a county's a town; and the two lesser kinds, villages and hamlets, the capitals of
## nothing. Each scene is a Destination.
const ICON_SCENE := {
	"kingdom": "res://Scenes/City.tscn", "duchy": "res://Scenes/City.tscn", "county": "res://Scenes/Town.tscn",
	"village": "res://Scenes/Village.tscn", "hamlet": "res://Scenes/Hamlet.tscn",
}
## How far the sea reaches beyond the sheet, in units.
const SEA_BEYOND := 30000.0
## Where the party starts, in units: near the middle of county 115, the middle of its area.
const PARTY_START := Vector2(7302.0, 7381.0)
## What there is to use in a settlement, by the number of the county it is the capital of: the
## game's Location resources, in the order its tooltip and its menu show them. Only county 115's
## capital has any yet, the hiring board and the market of the old world map's village.
const LOCATIONS := {
	115: ["res://Resources/Locations/Village1HiringBoard.tres", "res://Resources/Locations/Village1Market.tres"],
}

# Line widths, in Godot units: the pictures' widths in pixels times 3.35, to the whole unit.
const COAST_INK := 23.0          # 7 px. The coast's line is twice this, its inner half under the land.
const BORDER_WIDTH := {"kingdom": 17.0, "duchy": 10.0, "county": 7.0}      # 5, 3 and 2 px
const ROAD_WIDTH := 7.0          # 2 px
const HIGHWAY_WIDTH := 10.0      # 3 px
const BRIDGE_WIDER := 7.0        # a bridge is 2 px wider than its road
const LANE_WIDTH := 4.0          # 1.2 px: a village's lane, narrower than any road
const LANE_BRIDGE_WIDER := 5.0   # a lane's bridge is 1.5 px wider than the lane
const CHANNEL_WIDTH := 4.0       # 1.2 px: a swamp village's channel, narrower than any river
const SETTLEMENTS_ABOUT := "The settlements, an icon each, drawn at one size on the screen whatever the zoom, its middle at the node's position. The 220 capitals, one a county, are cities and towns; the villages and hamlets, about 2,000, are drawn under them."
## A forest's piece, by its kind: each scene a Forest (Scripts/WorldMap/Forest.gd), which inherits
## Forest.tscn's odds of the party being set upon and sets only its colour.
const FOREST_SCENE := {
	"conifer": "res://Scenes/ConiferForest.tscn", "broadleaf": "res://Scenes/BroadleafForest.tscn",
	"tropical": "res://Scenes/TropicalForest.tscn", "swamp": "res://Scenes/SwampForest.tscn",
}
const FORESTS_ABOUT := "The forests (MapCreation/Scripts/forests/f1_forests.py), drawn over the land and under everything else: a Forest for each piece, cut along the counties' borders and the coast and by kind (conifer, broadleaf, tropical, swamp, each a scene of its own colour), named for its county and numbered in it, the largest first. Grouped by the size of the whole forest a piece belongs to (its metadata's forest and forest_km2), so that the Detail node brings the smaller in as the view closes in, and under that by kingdom. Polygon2D draws no holes, so a clearing in a piece is joined to its outline by a cut of no width, there and back. The party may be set upon in any of them, at Forest.tscn's odds."
## The groups of the forests by the size of the whole forest, the order they are drawn in, and what
## each says of itself.
const FOREST_GROUPS := [
	["Great", "Forests of 250 km2 and more, and every piece of them. They show at every zoom."],
	["Large", "Forests of 50 to 250 km2. They show from the Kingdom tier in (see the Detail node)."],
	["Small", "Forests of 10 to 50 km2. They show from the Duchy tier in (see the Detail node)."],
	["Woods", "Woods under 10 km2, the smallest 0.5 km2. They show from the County tier in (see the Detail node)."],
]
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
# Nodes whose children are made by their own script as it starts, and so are not the scene's to keep.
var _builds_itself: Array[Node] = []
var _failed := 0
var _points := 0
var _nodes := 0
var _slowest := 0.0
var _cutting := 0.0


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var shapes: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var write_to: String = args[1] if args.size() > 1 else "res://Scenes/Map.tscn"
	if args.size() > 2 and args[2] == "villages":
		_write_villages_alone(shapes, write_to)
		return
	if args.size() > 2 and args[2] == "forests":
		_write_forests_alone(shapes, write_to)
		return
	var size: Array = shapes["size"]

	_root = Node2D.new()
	_root.name = "Map"
	_root.editor_description = "The island, about the size of Texas. A unit is 100 m: the map is %d by %d units, and its top left corner is the origin. Made by MapCreation/Scripts/scene from MapCreation/SourceData; see README.md, \"The map\"." % [roundi(size[0] * UNITS), roundi(size[1] * UNITS)]
	_root.set_meta(&"metres_per_unit", 100.0)
	_root.set_meta(&"units_per_picture_pixel", UNITS)

	_add_sea(size)
	_add_coast(shapes["coast"])
	_add_land(shapes["counties"], shapes["kingdoms"])
	_add_forests(_root, shapes.get("forests", []))
	_add_borders(shapes["borders"], shapes["banks"])
	_add_lakes(shapes["lakes"])
	_add_rivers(shapes["rivers"])
	_add_channels(_root, shapes.get("channels", []))
	_add_borders_over_lakes(shapes["across_lakes"])
	_add_roads(shapes["roads"], shapes.get("lanes", []))
	_add_bridges(shapes["bridges"], shapes.get("lane_bridges", []))
	_add_settlements(shapes["settlements"], shapes.get("villages", []))
	_add_party()
	_add_camera(size)
	_add_reticle()
	_add_village_menu()
	_add_squad_menu()
	_add_game_over()
	_add_border_switch()
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


## The forests, after the land and before the borders: an instance of its kind's scene for each piece
## (forestshapes.py), under the group of its forest's size and, in that, of its kingdom. The pieces'
## points are in the scene's units already, rounded as forestshapes.py checked them against Godot's
## own cutter into triangles, so they are put in as they are.
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


func _add_roads(roads: Array, lanes: Array) -> void:
	var group := _group(_root, "Roads", "Roads, a line for each stretch from one settlement or fork to the next. Settlements go by their county's number.")
	# The lanes first, so that the roads are drawn over where they join them.
	_add_lanes(group, lanes)
	var plain := _group(group, "Roads", "")
	var great := _group(group, "Highways", "Roads on the way between the capitals of two kingdoms that share a border.")
	var names := {}
	for road: Dictionary in roads:
		var road_name := "Road%sTo%s" % [_place(road["from"], road["from_fork"]), _place(road["to"], road["to_fork"])]
		var line := _line(great if road["highway"] else plain, _numbered(names, road_name), road["points"], HIGHWAY_WIDTH if road["highway"] else ROAD_WIDTH, _road)
		line.begin_cap_mode = Line2D.LINE_CAP_ROUND
		line.end_cap_mode = Line2D.LINE_CAP_ROUND


func _add_bridges(bridges: Array, lane_bridges: Array) -> void:
	var group := _group(_root, "Bridges", "Bridges: where a road crosses a river, and the one that joins the island town to the mainland. Each lies along its road, a little wider, from bank to bank.")
	for bridge: Dictionary in bridges:
		var line := _line(group, "Bridge%03d" % int(bridge["id"]), bridge["points"], (HIGHWAY_WIDTH if bridge["highway"] else ROAD_WIDTH) + BRIDGE_WIDER, _bridge)
		# Square ends, half the bridge's width past each bank.
		line.begin_cap_mode = Line2D.LINE_CAP_BOX
		line.end_cap_mode = Line2D.LINE_CAP_BOX
	_add_lane_bridges(group, lane_bridges)


## The villages' lanes (see MapCreation/Scripts/villages/v1_villages.py), each named for its village.
func _add_lanes(roads: Node, lanes: Array) -> void:
	if lanes.is_empty():
		return
	var group := _group(roads, "Lanes", "The villages' lanes: a line from each village not on a road to the nearest road, lane, joined village or capital, laid by the roads' own rules, and named for its village. Narrower than any road, and drawn under them. They show with the villages, from the County tier in (see the Detail node).")
	for lane: Dictionary in lanes:
		var line := _line(group, lane["name"], lane["points"], LANE_WIDTH, _road)
		line.begin_cap_mode = Line2D.LINE_CAP_ROUND
		line.end_cap_mode = Line2D.LINE_CAP_ROUND


## The bridges where a lane crosses a river or a channel, under the bridges' group, so that they
## are drawn over the rivers and the lanes; their own group shows with the lanes.
func _add_lane_bridges(bridges: Node, lane_bridges: Array) -> void:
	if lane_bridges.is_empty():
		return
	var group := _group(bridges, "Lanes", "Bridges where a village's lane crosses a river or a channel, named for the village, as a road's are drawn but narrower. They show with the lanes, from the County tier in (see the Detail node).")
	for bridge: Dictionary in lane_bridges:
		var line := _line(group, bridge["name"], bridge["points"], LANE_WIDTH + LANE_BRIDGE_WIDER, _bridge)
		line.begin_cap_mode = Line2D.LINE_CAP_BOX
		line.end_cap_mode = Line2D.LINE_CAP_BOX


## The channels dug from the swamp's villages to its rivers, lakes and the sea, after the rivers so
## that one ends unseen in the water it reaches.
func _add_channels(parent: Node, channels: Array) -> void:
	if channels.is_empty():
		return
	var group := _group(parent, "Channels", "Channels dug from the Swamp's villages that stand away from the water to the nearest river, lake or the sea, named for the village: their way to the rest of the map, in place of a lane. Narrower than any river. They show with the villages, from the County tier in (see the Detail node).")
	for channel: Dictionary in channels:
		var line := _line(group, channel["name"], channel["points"], CHANNEL_WIDTH, _water)
		line.begin_cap_mode = Line2D.LINE_CAP_ROUND
		# One that reaches the sea stops at the land's edge.
		line.end_cap_mode = Line2D.LINE_CAP_NONE if channel["ends_in"] == "sea" else Line2D.LINE_CAP_ROUND


func _add_settlements(settlements: Array, villages: Array) -> void:
	var group := _group(_root, "Settlements", SETTLEMENTS_ABOUT)
	# Hamlets and villages first, so that towns and cities are drawn over them.
	_add_villages(group, villages)
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
		if LOCATIONS.has(int(settlement["county"])):
			icon.set(&"locations", _locations(LOCATIONS[int(settlement["county"])]))
		icon.set_meta(&"county", int(settlement["county"]))
		icon.set_meta(&"duchy", int(settlement["duchy"]))
		icon.set_meta(&"kingdom", int(settlement["kingdom"]))
		of_rank[rank].add_child(icon)
		_nodes += 1


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
	_own(_root)
	var packed := PackedScene.new()
	var error := packed.pack(_root)
	if error == OK:
		error = ResourceSaver.save(packed, write_to)
	print("nodes ", _nodes, "; points ", _points)
	print("saved ", write_to, ": ", "ok" if error == OK else "FAILED %d" % error, ", ", FileAccess.get_file_as_bytes(write_to).size(), " bytes")
	_root.free()
	quit(0 if error == OK else 1)


## The forests alone, under their groups, and nothing else: for ../forests/f3_splice.py to splice into
## the scene as it is.
func _write_forests_alone(shapes: Dictionary, write_to: String) -> void:
	_root = Node2D.new()
	_root.name = "Map"
	_add_forests(_root, shapes["forests"])
	_own(_root)
	var packed := PackedScene.new()
	var error := packed.pack(_root)
	if error == OK:
		error = ResourceSaver.save(packed, write_to)
	print("nodes ", _nodes, "; points ", _points, "; polygons Godot could not cut into triangles: ", _failed,
			"; cutting them all took ", snappedf(_cutting, 0.1), " ms, the slowest ", snappedf(_slowest, 0.1), " ms")
	print("saved ", write_to, ": ", "ok" if error == OK else "FAILED %d" % error, ", ", FileAccess.get_file_as_bytes(write_to).size(), " bytes")
	_root.free()
	quit(0 if error == OK and _failed == 0 else 1)


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


## The gamepad's pointer (Scripts/WorldMap/MapReticle.gd), as on the old world map: a ring in the
## middle of the screen and the prompts for what each button does, shown only with the gamepad. It
## finds the party and the menu below by their names. Like that menu it makes what it shows as its
## script starts, so none of that is kept in the scene.
func _add_reticle() -> void:
	var reticle := CanvasLayer.new()
	reticle.name = "MapReticle"
	reticle.set_script(load("res://Scripts/WorldMap/MapReticle.gd"))
	reticle.layer = 1
	reticle.process_mode = Node.PROCESS_MODE_INHERIT
	reticle.editor_description = "The gamepad's pointer, as on the world map: a ring in the middle of the screen, which the left stick moves the map under, and prompts in the bottom right corner for what each button does. A acts on what is under the ring: it enters the settlement the party is in, or sends the party to a settlement, or to that spot. Shown only while the gamepad is in use."
	_root.add_child(reticle)
	_builds_itself.append(reticle)
	_nodes += 1


## The menu of the settlement the party is in (Scripts/UI/VillageMenu.gd), as on the old world map:
## a left click on the settlement's icon opens it, with a tab for each of its locations. The menu
## makes its own frame as its script starts, and sets its own layer and process mode, which is why
## none of that is kept in the scene: kept, it would be made twice, and hold against a later change
## to the script.
func _add_village_menu() -> void:
	var menu := CanvasLayer.new()
	menu.name = "VillageMenu"
	menu.set_script(load("res://Scripts/UI/VillageMenu.gd"))
	menu.layer = 1
	menu.process_mode = Node.PROCESS_MODE_INHERIT
	menu.editor_description = "The menu of the settlement the party is in, as on the world map: a left click on the settlement's icon opens it, with a tab for each of the settlement's Locations, and a settlement with none does not open. Only the capital of county 115 has any yet: the hiring board and the market of the world map's village."
	_root.add_child(menu)
	_builds_itself.append(menu)
	_nodes += 1


## Who fights, chosen as a battle starts (Scripts/UI/SquadMenu.gd), as on the old world map: the
## party's random encounters open it, and holding its Start begins the battle. It finds the party by
## its name, and like the menu above makes its own frame as its script starts.
func _add_squad_menu() -> void:
	var menu := CanvasLayer.new()
	menu.name = "SquadMenu"
	menu.set_script(load("res://Scripts/UI/SquadMenu.gd"))
	menu.layer = 1
	menu.process_mode = Node.PROCESS_MODE_INHERIT
	menu.editor_description = "Who fights, chosen as a battle starts, as on the world map: the party's random encounters open it, it cannot be closed, and holding its Start begins the battle with whoever is ticked. The map waits as it stands and is come back to once the battle is over. The party is set upon in the forests (Forests), as on the world map: a step it ends in one rolls that forest's odds."
	_root.add_child(menu)
	_builds_itself.append(menu)
	_nodes += 1


## The game's end (Scripts/WorldMap/GameOver.gd), as on the old world map: once nobody is left on the
## roster the map stops, "Game Over" comes up and the game quits. It makes its banner as its script
## starts, as the menu above makes its frame, so none of that is kept in the scene.
func _add_game_over() -> void:
	var game_over := CanvasLayer.new()
	game_over.name = "GameOver"
	game_over.set_script(load("res://Scripts/WorldMap/GameOver.gd"))
	game_over.layer = 1
	game_over.process_mode = Node.PROCESS_MODE_INHERIT
	game_over.editor_description = "Ends the game once nobody is left on the roster, as on the world map: the map stops, \"Game Over\" comes up in the battles' banner, over any menu, and the game quits as the banner starts to fade. Only a battle, met in the forests, can empty the roster."
	_root.add_child(game_over)
	_builds_itself.append(game_over)
	_nodes += 1


## The borders' switch (Scripts/WorldMap/BorderSwitch.gd): B, or the gamepad's R3, hides every border
## and shows it again. It finds the Borders and BordersOverLakes groups by those names.
func _add_border_switch() -> void:
	var border_switch := Node.new()
	border_switch.name = "BorderSwitch"
	border_switch.set_script(load("res://Scripts/WorldMap/BorderSwitch.gd"))
	border_switch.editor_description = "Hides every border, the kingdoms', the duchies' and the counties', and shows them again: B, or the gamepad's R3, while the game runs. They start shown. It fades the Borders and BordersOverLakes groups as a whole; the Detail node still fades their ranks by the zoom under that."
	_root.add_child(border_switch)
	_nodes += 1


## The map's level of detail (Scripts/WorldMap/MapDetail.gd): while the game runs it shows and hides
## the layers by how far the view is zoomed, and sets the lines' widths. It reads the layers by the
## names they are given above, and changes nothing in the scene as it is saved.
func _add_detail() -> void:
	var detail := Node.new()
	detail.name = "Detail"
	detail.set_script(load("res://Scripts/WorldMap/MapDetail.gd"))
	detail.editor_description = "Level of detail by the zoom, while the game runs: what shows and how wide the lines are follow how tall the view is in miles. Realm (the whole island): the coast, the kingdoms' borders and capitals, the greatest rivers and lakes, the great forests. Kingdom (under 480 miles): the duchies' borders and capitals, the highways, more rivers and lakes, the large forests. Duchy (under 240): the counties' borders and capitals, the other roads, the bridges, every river and lake, the small forests. County (under 100): the villages, their lanes and the Swamp's channels, the woods; and in a second step, under 50, the hamlets. A line is as wide as its node says when the view is 220 miles tall, and grows only a little with the zoom from there. The editor shows everything, at the widths given."
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
		_check_cut(polygon_name, points)
	return polygon


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


## The Location resources at some paths, as the typed list a Destination keeps its locations in.
func _locations(paths: Array) -> Array:
	var locations := Array([], TYPE_OBJECT, &"Resource", load("res://Scripts/WorldMap/Location.gd"))
	for path: String in paths:
		locations.append(load(path))
	return locations


func _own(node: Node) -> void:
	for child in node.get_children():
		child.owner = _root
		if not _builds_itself.has(child):
			_own(child)
