## Helpers the map styles share. Each style is handed one of these, holding the
## new map (Scenes/Map.tscn) as instantiated but not yet in the tree, and
## changes the map through it.
##
## Changing the scene before it enters the tree is the same as editing the
## .tscn: MapDetail and BorderSwitch read every width, width curve and alpha in
## their _ready, so whatever a style sets here they scale and fade as they do
## the scene's own values. That is also how to apply a style for real: set the
## same properties in the scene (or in a kind's scene, such as ConiferForest.tscn).
extends RefCounted

## A mile in the map's units (MapCamera.UNITS_A_MILE).
const UNITS_A_MILE := 16.09344
## The MapCreation pictures' sheet, 3100 by 4000 pixels of 3.35 units each.
const SHEET := Vector2(10385.0, 13400.0)
## The four kinds of forest, by the scene each piece is an instance of.
const FOREST_KINDS := ["Conifer", "Broadleaf", "Swamp", "Tropical"]
## The ranks of border, the lesser first, as under Borders and BordersOverLakes.
const RANKS := ["Counties", "Duchies", "Kingdoms"]

## The map, not yet in the tree while a style's apply() runs.
var map: Node2D
## The probe, which owns the map: runtime nodes that are not part of the map
## (screen-space overlays) go under it.
var probe: Node
## The harness's data folder, as an absolute path: pictures made from the
## MapCreation data (relief) are read from there at run time, so nothing has
## to be imported.
var data_dir := ""
## The harness folder as copied into the project for the run.
var root := "res://_probe"

var _white: ImageTexture
var _data := {}
var _lifted := false


func _init(the_map: Node2D, the_probe: Node, the_data_dir: String) -> void:
	map = the_map
	probe = the_probe
	data_dir = the_data_dir


# -- finding things ---------------------------------------------------------------------------

func at(path: String) -> Node:
	return map.get_node_or_null(path)


## Every Line2D under [param path], however deep.
func lines_in(path: String) -> Array[Line2D]:
	var found: Array[Line2D] = []
	var node := at(path)
	if node == null:
		push_error("StyleKit: nothing at '%s'" % path)
		return found
	if node is Line2D:
		found.append(node)
	for child in node.find_children("*", "Line2D", true, false):
		found.append(child)
	return found


## Every Polygon2D under [param path], however deep.
func polygons_in(path: String) -> Array[Polygon2D]:
	var found: Array[Polygon2D] = []
	var node := at(path)
	if node == null:
		push_error("StyleKit: nothing at '%s'" % path)
		return found
	if node is Polygon2D:
		found.append(node)
	for child in node.find_children("*", "Polygon2D", true, false):
		found.append(child)
	return found


## The counties' polygons: the land.
func counties() -> Array[Polygon2D]:
	return polygons_in("Land")


## The islands in lakes, which are land drawn over the water.
func lake_islands() -> Array[Polygon2D]:
	var found: Array[Polygon2D] = []
	for lake in polygons_in("Lakes"):
		if str(lake.name).contains("Island"):
			found.append(lake)
	return found


## The lakes themselves, without their islands.
func lakes() -> Array[Polygon2D]:
	var found: Array[Polygon2D] = []
	for lake in polygons_in("Lakes"):
		if not str(lake.name).contains("Island"):
			found.append(lake)
	return found


## Every piece of forest, or only those of one kind ("Conifer", "Broadleaf",
## "Swamp", "Tropical").
func forests(kind := "") -> Array[Polygon2D]:
	var found: Array[Polygon2D] = []
	for piece in polygons_in("Forests"):
		if kind.is_empty() or piece.scene_file_path.ends_with("/%sForest.tscn" % kind):
			found.append(piece)
	return found


## The kind of a piece of forest, from the scene it is an instance of.
func forest_kind(piece: Polygon2D) -> String:
	for kind: String in FOREST_KINDS:
		if piece.scene_file_path.ends_with("/%sForest.tscn" % kind):
			return kind
	return ""


## The settlements of one group under Settlements ("KingdomCapitals",
## "DuchyCapitals", "CountyCapitals", "Villages", "Hamlets"), or all of them.
func settlements(group := "") -> Array[Node2D]:
	var found: Array[Node2D] = []
	var node := at("Settlements" if group.is_empty() else "Settlements/" + group)
	for child in node.find_children("*", "Node2D", true, false):
		if child.get_script() != null and child.has_method("is_under_pointer"):
			found.append(child)
	return found


## A border's lines along a river, a lake's shore or a road ([param what]:
## "River", "Lake", "Road", or "" for all three) under a rank of borders.
func along_lines(rank: String, what := "") -> Array[Line2D]:
	var found: Array[Line2D] = []
	for line in lines_in("Borders/" + rank):
		var title := str(line.name)
		if title.contains("Along" + what):
			found.append(line)
	return found


## The kind of road ("Highways", "Roads", "Lanes") a border's line along a road
## lies under, or "" when none is found. A road's number is in no node's name,
## so, as MapDetail does, it is the road that has the line's middle point.
func road_under(line: Line2D) -> String:
	var points := line.points
	if points.is_empty():
		return ""
	var middle := line.to_global(points[points.size() / 2])
	for kind: String in ["Highways", "Roads", "Lanes"]:
		for road in lines_in("Roads/" + kind):
			var local := road.to_local(middle)
			for point in road.points:
				if point.distance_squared_to(local) < 0.25:
					return kind
	return ""


## The borders of a rank that follow nothing: the plain lines.
func plain_borders(rank: String) -> Array[Line2D]:
	var found: Array[Line2D] = []
	for line in lines_in("Borders/" + rank):
		if not str(line.name).contains("Along"):
			found.append(line)
	return found


## A plain border's width in a rank, as MapDetail finds it: the middle one of
## the lines that follow nothing.
func plain_width(rank: String) -> float:
	var widths: Array[float] = []
	for line in plain_borders(rank):
		widths.append(line.width)
	widths.sort()
	return widths[widths.size() / 2] if not widths.is_empty() else 0.0


## The kingdom a county polygon is in, from its place under Land/KingdomN/DuchyNN.
func kingdom_of(county: Node) -> int:
	var node := county
	while node != null and node != map:
		var title := str(node.name)
		if title.begins_with("Kingdom") and title.substr(7).is_valid_int():
			return int(title.substr(7))
		node = node.get_parent()
	return 0


## The duchy a county polygon is in.
func duchy_of(county: Node) -> int:
	var node := county
	while node != null and node != map:
		var title := str(node.name)
		if title.begins_with("Duchy") and title.substr(5).is_valid_int():
			return int(title.substr(5))
		node = node.get_parent()
	return 0


# -- whole layers ------------------------------------------------------------------------------

func set_sea(color: Color) -> void:
	(at("Sea") as Polygon2D).color = color


## The land's colour: every county and every island in a lake.
func set_land(color: Color) -> void:
	for county in counties():
		county.color = color
	for island in lake_islands():
		island.color = color


## The coast's line: its colour, and its width as a share of the scene's (23
## units outside the land at 220 miles tall). Its inner half is under the land.
func set_coast(color: Color, width_share := 1.0) -> void:
	for line in lines_in("Coast"):
		line.default_color = color
		line.width *= width_share


## Lakes, rivers and the Swamp's channels (not the sea).
func set_inland_water(color: Color) -> void:
	for lake in lakes():
		lake.color = color
	for line in lines_in("Rivers"):
		line.default_color = color
	for line in lines_in("Channels"):
		line.default_color = color


## Every line under [param path] (however deep) given one colour.
func color_lines(path: String, color: Color) -> void:
	for line in lines_in(path):
		line.default_color = color


## Every line under [param path] made [param share] as wide.
func scale_widths(path: String, share: float) -> void:
	for line in lines_in(path):
		line.width *= share


## A group's alpha, which MapDetail and BorderSwitch multiply theirs into.
func set_alpha(path: String, alpha: float) -> void:
	var node := at(path) as CanvasItem
	node.modulate.a = alpha


## A forest kind's colour, set on every piece of it (for real: on the root of
## the kind's scene, Scenes/<Kind>Forest.tscn).
func set_forest(kind: String, color: Color) -> void:
	for piece in forests(kind):
		piece.color = color


## Puts a group, and everything under it, over or under others in the drawing
## order without moving it in the tree. A child's z is its parent's plus its own.
func set_z(path: String, z: int) -> void:
	(at(path) as CanvasItem).z_index = z


# -- lines drawn twice --------------------------------------------------------------------------

## Draws every line of [param path] (the lines directly under it) a second time
## under itself, [param extra] units wider (at 220 miles tall) in [param color]:
## a casing, or a halo in the land's colour. The copies go in a group of their
## own at the head of [param path], so they are drawn first, and MapDetail gives
## them the tier of [param path] and scales their widths with the rest.
## Returns the group.
func add_casing(path: String, color: Color, extra: float, title := "Casing") -> Node2D:
	var parent := at(path)
	var group := Node2D.new()
	group.name = title
	for child in parent.get_children():
		var line := child as Line2D
		if line == null:
			continue
		var copy := line.duplicate() as Line2D
		copy.name = "%s%s" % [line.name, title]
		copy.width = line.width + extra
		copy.default_color = color
		copy.material = null
		copy.texture = null
		group.add_child(copy)
	parent.add_child(group)
	parent.move_child(group, 0)
	return group


## A new group of copies of every line of [param path] (directly under it),
## [param share] as wide, in [param color], added after [param path]'s own lines
## so drawn over them: a centre line, the white of a cased road. Returns it.
func add_inner(path: String, color: Color, share: float, title := "Inner") -> Node2D:
	var parent := at(path)
	var group := Node2D.new()
	group.name = title
	for child in parent.get_children():
		var line := child as Line2D
		if line == null:
			continue
		var copy := line.duplicate() as Line2D
		copy.name = "%s%s" % [line.name, title]
		copy.width = line.width * share
		copy.default_color = color
		group.add_child(copy)
	parent.add_child(group)
	return group


# -- patterned lines -----------------------------------------------------------------------------

## A 1 by 1 white texture. With texture_mode TILE, UV.x counts a line's widths
## along it and UV.y runs 0 to 1 across it, which map_line.gdshader draws its
## patterns by. That needs no texture after all (a line without this one draws
## the same, to the pixel), but the pictures were taken with it.
func white_texture() -> ImageTexture:
	if _white == null:
		var image := Image.create(1, 1, false, Image.FORMAT_RGBA8)
		image.fill(Color.WHITE)
		_white = ImageTexture.create_from_image(image)
	return _white


## A ShaderMaterial of map_line.gdshader with [param params] (see the shader).
func line_material(params: Dictionary) -> ShaderMaterial:
	var material := ShaderMaterial.new()
	material.shader = load(root + "/shaders/map_line.gdshader")
	for key: String in params:
		material.set_shader_parameter(key, params[key])
	return material


## Gives every line under [param path] the pattern of [param material]: the
## white texture for its UVs, tiled along it, and the material.
func pattern_lines(path: String, material: Material) -> void:
	for line in lines_in(path):
		pattern_line(line, material)


func pattern_line(line: Line2D, material: Material) -> void:
	line.texture = white_texture()
	line.texture_mode = Line2D.LINE_TEXTURE_TILE
	line.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	line.material = material


# -- adding layers -------------------------------------------------------------------------------

## Adds [param node] to the map just after the top-level node [param after] in
## the drawing order (or first, with an empty name).
func insert_after(after: String, node: Node) -> void:
	map.add_child(node)
	if after.is_empty():
		map.move_child(node, 0)
	else:
		map.move_child(node, at(after).get_index() + 1)


## A texture read straight from the harness's data folder (nothing imported),
## with mipmaps, so that it can be drawn small without shimmering.
func data_texture(file: String) -> ImageTexture:
	if _data.has(file):
		return _data[file]
	var image := Image.load_from_file(data_dir.path_join(file))
	if image == null or image.is_empty():
		push_error("StyleKit: could not read %s" % data_dir.path_join(file))
		return null
	image.generate_mipmaps()
	var texture := ImageTexture.create_from_image(image)
	_data[file] = texture
	return texture


## A Polygon2D covering the MapCreation sheet, its UVs the sheet's 0 to 1, for
## a shader that reads a picture of the whole map (relief, heights).
func sheet_polygon(material: Material) -> Polygon2D:
	var polygon := Polygon2D.new()
	polygon.polygon = PackedVector2Array([Vector2.ZERO, Vector2(SHEET.x, 0.0), SHEET, Vector2(0.0, SHEET.y)])
	polygon.uv = PackedVector2Array([Vector2.ZERO, Vector2(1.0, 0.0), Vector2.ONE, Vector2(0.0, 1.0)])
	polygon.texture = white_texture()
	polygon.material = material
	return polygon


## A ShaderMaterial of one of the harness's shaders, by file name.
func shader_material(file: String, params := {}) -> ShaderMaterial:
	var material := ShaderMaterial.new()
	material.shader = load(root + "/shaders/" + file)
	for key: String in params:
		material.set_shader_parameter(key, params[key])
	return material


## Loads one of the harness's runtime scripts (labels, overlays) by file name.
func runtime(file: String) -> GDScript:
	return load(root + "/runtime/" + file)


# -- borders ---------------------------------------------------------------------------------------

## Styles a rank of borders ("Counties", "Duchies", "Kingdoms"): every line of it
## under Borders and BordersOverLakes gets [param color], a plain border's
## [param width] (in units at 220 miles tall), and [param material] if given.
##
## A border along a river, a lake's shore or a road (its "...Along..." line) is
## drawn by [param along]:
##   "onto" - along a river or a lake, as a plain border drawn over the water,
##            the way most maps draw a border that follows a river; along a road
##            it stays a band under the road, as wide as the road and the border.
##   "keep" - as the scene has it, a band under the river, shore or road wide
##            enough to show the border on both banks, made to the new width.
##   "hide" - not drawn: the river, shore or road stands for the border.
func style_rank(rank: String, color: Color, width: float, material: Material = null, along := "onto") -> void:
	var old_plain := plain_width(rank)
	for line in lines_in("Borders/" + rank):
		var title := str(line.name)
		line.default_color = color
		if material != null:
			pattern_line(line, material)
		if not title.contains("Along"):
			line.width = width
			continue
		var on_water := title.contains("AlongRiver") or title.contains("AlongLake")
		match along:
			"hide":
				line.modulate.a = 0.0
			"onto" when on_water:
				line.width = width
				line.width_curve = null
				line.z_index = 1
				lift_over_borders()
			_:
				if title.contains("AlongLake"):
					line.width = width
				else:
					line.width = maxf(line.width - old_plain + width, width)
	for line in lines_in("BordersOverLakes/" + rank):
		line.default_color = color
		line.width = width
		if material != null:
			pattern_line(line, material)


## The coast's lines drawn in map_line.gdshader's coast mode ([param params]
## are the shader's: shore, shore_share, ring, rings, ring_share, ring_min_px),
## [param width_share] as wide as the scene has them.
func style_coast(params: Dictionary, width_share := 1.0) -> void:
	var settings := params.duplicate()
	settings["coast_mode"] = true
	var material := line_material(settings)
	for line in lines_in("Coast"):
		line.width *= width_share
		pattern_line(line, material)


## Once the map is ready (from a style's ready()): brings the ends of the
## borders and rivers that run out into the coast's line back toward the
## land's edge, to [param share] of how far past it the scene has them. Wanted
## when the coast's line is drawn narrower than the scene's 23 units outside
## the land, or the ends would show past it over the sea. For real, this is a
## factor in MapDetail._set_width(), or the points moved in the scene.
func trim_sea_ends(share: float) -> void:
	var detail := at("Detail")
	var ends: Dictionary = detail.get("_sea_ends")
	for i in ends:
		for end: Array in ends[i]:
			end[2] = end[1] + (end[2] - end[1]) * share
	var tier: int = detail.get("_tier")
	var wide_from: PackedInt32Array = detail.get("_wide_from")
	for i in ends:
		detail.call("_set_width", i, wide_from[i] <= tier)


## Lifts the roads, bridges, settlements and party over anything given a z of
## 1 (the borders drawn onto the water), keeping their order: z 2, 2, 3 and 4.
func lift_over_borders() -> void:
	if _lifted:
		return
	_lifted = true
	set_z("Roads", 2)
	set_z("Bridges", 2)
	set_z("Settlements", 3)
	set_z("Party", 4)


# -- relief, land and forests -------------------------------------------------------------------------

## Shaded relief over the land and the forests, under the borders and the
## water: two Polygon2Ds over the sheet, one multiplying in the shade (up to
## [param shadow] dark), one adding the light (up to [param light]).
func add_relief(shadow := 0.45, light := 0.1, shade_tint := Color(0.25, 0.28, 0.4), after := "Forests") -> void:
	var relief := data_texture("hillshade.png")
	var dark := sheet_polygon(shader_material("relief.gdshader", {
		"relief": relief, "shadow": shadow, "shade_tint": shade_tint,
	}))
	dark.name = "ReliefShade"
	insert_after(after, dark)
	if light > 0.0:
		var lit := sheet_polygon(shader_material("relief_light.gdshader", {"relief": relief, "light": light}))
		lit.name = "ReliefLight"
		insert_after("ReliefShade", lit)


## Gives the land (every county and lake island) land.gdshader with
## [param params], the height and edge pictures filled in. Returns the material.
func style_land(params: Dictionary) -> ShaderMaterial:
	var material := shader_material("land.gdshader", params)
	if not params.has("elevation"):
		material.set_shader_parameter(&"elevation", data_texture("elevation.png"))
	if not params.has("edge"):
		material.set_shader_parameter(&"edge", data_texture("kingdom_edge.png"))
	for county in counties():
		county.material = material
	for island in lake_islands():
		island.material = material
	return material


## A colour ramp as a texture, from [offset, Color] pairs.
func ramp(stops: Array) -> GradientTexture1D:
	var gradient := Gradient.new()
	gradient.offsets = PackedFloat32Array(stops.map(func(s: Array) -> float: return s[0]))
	gradient.colors = PackedColorArray(stops.map(func(s: Array) -> Color: return s[1]))
	var texture := GradientTexture1D.new()
	texture.gradient = gradient
	texture.width = 256
	return texture


## Gives every piece of a kind of forest ("" for all) a colour and
## forest.gdshader with [param params]. The piece's own alpha goes to 1 and its
## see-through amount into the shader's fill_alpha (from [param color]'s alpha).
func style_forests(kind: String, color: Color, params: Dictionary) -> ShaderMaterial:
	var material := shader_material("forest.gdshader", params)
	material.set_shader_parameter(&"fill_alpha", color.a)
	var opaque := Color(color, 1.0)
	for piece in forests(kind):
		piece.color = opaque
		piece.material = material
	return material


## Tints the icons of a group of settlements ("" for all) toward [param tint]
## (its alpha is how far), through icon_tint.gdshader. Once the map is ready.
func tint_settlements(group: String, tint: Color) -> void:
	var material := shader_material("icon_tint.gdshader", {"tint": tint})
	for place in settlements(group):
		place.material = material


# -- colour helpers --------------------------------------------------------------------------------

## A colour from a hex string, with an alpha.
static func hex(code: String, alpha := 1.0) -> Color:
	var color := Color.html(code)
	color.a = alpha
	return color
