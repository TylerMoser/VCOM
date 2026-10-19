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
## Whether as_revisited() has put the map back already.
var _as_revisited := false


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


# -- on the applied look (revisited on 2026-10-19) ----------------------------------------------------
#
# The helpers above were written for the scene as it was before 02, 04, 05 and 10 were applied
# (render.sh's BEFORE=1). These are for the variants of 10, 14 and 19 revisited on 2026-10-19,
# which start from the scene as it was then (commit c2e885c): borders patterned by their kind's
# material, a border's band along a river or road patterned on both banks by a band material of
# its rank, roads cased, AlongLake lines in BordersOverLakes. 10b, 14b and 19a were applied the
# same day, so as_revisited() takes them back out first. Every material here is the shared .tres
# the scene loads: a change is in memory for the run alone, and nothing is ever saved.

## Puts the map back as it was when 10, 14 and 19 were revisited, the map every variant was
## pictured against, by taking out in memory what was applied from them on 2026-10-19: 10b's
## roads, 14b's borders and 19a's tiers, and 12b's ground, applied later that day. Every revisited
## style calls it first. It acts once, so that 200's picks, applied one after another, each add
## their part to the others'. Returns the map's Detail node, given RevisitedDetail.
func as_revisited() -> Node:
	var detail := revisited_detail()
	if _as_revisited:
		return detail
	_as_revisited = true
	without_ground()
	# 10b: the roads 14 and the lanes 7 wide, their bridges and the bands along them with them,
	# and the roads' casing 0.3 of them, from 4.5 px across.
	reweight_roads("Roads", 14.0)
	reweight_roads("Lanes", 7.0)
	var road := lines_in("Roads/Roads")[0].material as ShaderMaterial
	road.set_shader_parameter(&"casing_share", 0.3)
	road.set_shader_parameter(&"casing_min_px", 4.5)
	# 14b: every border as wide as MapDetail's one factor has it, and none fainter closing in.
	detail.set("border_growth", 0.0)
	detail.set("kingdom_border_faintest", 1.0)
	detail.set("duchy_border_faintest", 1.0)
	# 19a: the county borders with the Duchy tier.
	detail.set("shown_from", tiers_as_revisited())
	return detail


## MapDetail.SHOWN_FROM as it was when 19 was revisited, the county borders with the Duchy tier
## (19a has them with the County tier now), with some groups moved to another tier
## ({NodePath: MapDetail.Tier}).
func tiers_as_revisited(moves := {}) -> Dictionary:
	var to := {^"Borders/Counties": MapDetail.Tier.DUCHY, ^"BordersOverLakes/Counties": MapDetail.Tier.DUCHY}
	to.merge(moves, true)
	var table := {}
	for tier: int in MapDetail.SHOWN_FROM:
		table[tier] = []
	for tier: int in MapDetail.SHOWN_FROM:
		for path: NodePath in MapDetail.SHOWN_FROM[tier]:
			table[to.get(path, tier)].append(path)
	return table


## The map's Detail node given the harness's RevisitedDetail (14c's roads, 19's tiers, lakes and
## ramps, each off until set), before the map enters the tree. Returns it, to be set. Given it
## already, it is left as it is, so that several variants can be applied one after another and
## each set its own part (200_revisited_together.gd).
func revisited_detail() -> Node:
	var detail := at("Detail")
	var script := runtime("RevisitedDetail.gd")
	if detail.get_script() != script:
		detail.set_script(script)
	return detail


## The shared material of a rank's plain borders, or of its bands along rivers.
func border_material(rank: String, band := false) -> ShaderMaterial:
	for line in lines_in("Borders/" + rank):
		if str(line.name).contains("AlongRiver") == band and (band or not str(line.name).contains("Along")):
			return line.material as ShaderMaterial
	return null


## The middle width of a rank's bands along rivers (21.7, 20.1 and 16.6 units for kingdoms,
## duchies and counties as applied), by which its band material's pattern was shortened.
func middle_band(rank: String) -> float:
	var widths: Array[float] = []
	for line in lines_in("Borders/" + rank):
		if str(line.name).contains("AlongRiver"):
			widths.append(line.width)
	widths.sort()
	return widths[widths.size() / 2] if not widths.is_empty() else 0.0


## Lays a rank's band pattern anew from its plain pattern, shortened by the plain border's width
## over the middle band's, as applied, so a dash along a river is as long as a plain border's.
## Call it after changing the plain material or the rank's width.
func sync_band_pattern(rank: String) -> void:
	var plain := border_material(rank)
	var band := border_material(rank, true)
	var share := plain_width(rank) / middle_band(rank)
	var defaults := {"dash": 0.0, "gap": 1.0, "dot": 0.0, "dot_gap": 0.0}
	for key: String in defaults:
		var value: Variant = plain.get_shader_parameter(key)
		band.set_shader_parameter(key, (defaults[key] if value == null else float(value)) * share)


## Gives a rank of borders a new plain width: its bands along rivers and roads as much wider or
## narrower (each is its river's or road's width and a plain border's), its lines over lakes the
## plain width, and its band pattern laid anew.
func reweight_rank(rank: String, width: float) -> void:
	var old := plain_width(rank)
	for line in lines_in("Borders/" + rank):
		var title := str(line.name)
		if title.contains("AlongRiver") or title.contains("AlongRoad"):
			line.width += width - old
		else:
			line.width = width
	for line in lines_in("BordersOverLakes/" + rank):
		line.width = width
	sync_band_pattern(rank)


## A point of a node's in the map's space, from the node's own transforms: works before the map
## is in the tree, where to_global() does not.
func to_map_space(node: Node2D, point: Vector2) -> Vector2:
	var at_point := point
	var current: Node = node
	while current != null and current != map:
		if current is Node2D:
			at_point = (current as Node2D).transform * at_point
		current = current.get_parent()
	return at_point


## The kind of road ("Highways", "Roads", "Lanes") a border's band along a road lies under, as
## road_under() finds it, but before the map is in the tree.
func road_kind_under(line: Line2D) -> String:
	var points := line.points
	if points.is_empty():
		return ""
	var middle := to_map_space(line, points[points.size() / 2])
	for kind: String in ["Highways", "Roads", "Lanes"]:
		for road in lines_in("Roads/" + kind):
			for point in road.points:
				if to_map_space(road, point).distance_squared_to(middle) < 0.25:
					return kind
	return ""


## Gives a kind of road ("Highways", "Roads", "Lanes") a new width, as a share of its own: its
## bridges with it (1.45 times their road: 29 over a highway, and over a road 20.3 as revisited,
## 23.2 since 10b) and the borders' bands along it as much wider.
func reweight_roads(kind: String, width: float) -> void:
	var roads := lines_in("Roads/" + kind)
	var widths: Array[float] = []
	for road in roads:
		widths.append(road.width)
	widths.sort()
	var old: float = widths[widths.size() / 2]
	var share := width / old
	for road in roads:
		road.width *= share
	if kind == "Lanes":
		for bridge in lines_in("Bridges/Lanes"):
			bridge.width *= share
	else:
		for child in at("Bridges").get_children():
			var bridge := child as Line2D
			if bridge != null and is_equal_approx(snappedf(bridge.width, 0.05), snappedf(old * 1.45, 0.05)):
				bridge.width *= share
	for rank: String in RANKS:
		for line in lines_in("Borders/" + rank):
			if str(line.name).contains("AlongRoad") and road_kind_under(line) == kind:
				line.width += width - old


# -- the ground's colours (12's variants, 2026-10-19) ---------------------------------------------------
#
# For the variants in MapStyles/12-biome-ground-colours/, on the map as it is: the land given
# ground.gdshader, which reads the biome of every pixel from an id map and the land's own pictures.
# 12b, the whisper, was applied the same day (Resources/MapGround.tres on every county), after the
# variants were pictured on the white land: a variant's ground replaces that material, and the
# styles that draw no ground of their own take it off first (without_ground()).

## The land as it was before 12b's ground was applied: every county and the island in a lake without
## a material, so the land's own white shows. In memory, for the run alone.
func without_ground() -> void:
	for county in counties():
		county.material = null
	for island in lake_islands():
		island.material = null


## The repository's MapCreation/SourceData, where the map's data lies. Godot imports none of it, so
## it is read by path.
func source_dir() -> String:
	return data_dir.path_join("../../../MapCreation/SourceData").simplify_path()


## A picture from MapCreation/SourceData read straight from disk, with no mipmaps: an id map, which a
## shader reads nearest (an id blended with its neighbour is no id).
func source_texture(file: String) -> ImageTexture:
	var key := "source:" + file
	if _data.has(key):
		return _data[key]
	var image := Image.load_from_file(source_dir().path_join(file))
	if image == null or image.is_empty():
		push_error("StyleKit: could not read %s" % source_dir().path_join(file))
		return null
	var texture := ImageTexture.create_from_image(image)
	_data[key] = texture
	return texture


## Gives the land (every county and every island in a lake) ground.gdshader with [param params], its
## pictures filled in: the biomes from KingdomMap.png unless [param regions] names another id map
## (TerrainMap.png), and the heights, rivers, settlements, sea and kingdoms' edges from data/.
## Returns the material.
func style_ground(params: Dictionary, regions := "KingdomMap.png") -> ShaderMaterial:
	var material := shader_material("ground.gdshader", params)
	material.set_shader_parameter(&"region_map", source_texture(regions))
	for picture: String in ["elevation", "wetness", "farmland", "coast"]:
		if not params.has(picture):
			material.set_shader_parameter(picture, data_texture(picture + ".png"))
	if not params.has("edge"):
		material.set_shader_parameter(&"edge", data_texture("kingdom_edge.png"))
	for county in counties():
		county.material = material
	for island in lake_islands():
		island.material = material
	return material


## A palette for ground.gdshader from {biome: "#rrggbb"}: ten colours, the 0th (the sea, and any
## biome left out) white.
static func palette_of(colours: Dictionary) -> PackedColorArray:
	var palette := PackedColorArray()
	palette.resize(10)
	palette.fill(Color.WHITE)
	for biome: int in colours:
		palette[biome] = hex(colours[biome])
	return palette


## The kingdom (and so the biome) of every county, by its number: {115: 5, ...}.
func county_kingdoms() -> Dictionary:
	var found := {}
	for county in counties():
		var title := str(county.name)
		if title.begins_with("County") and title.substr(6).is_valid_int():
			found[int(title.substr(6))] = kingdom_of(county)
	return found


## The county a piece of forest lies in, from its name ("County125Forest3"), or 0.
static func county_of_piece(piece: Node) -> int:
	var title := str(piece.name)
	var at := title.find("Forest")
	if not title.begins_with("County") or at < 0:
		return 0
	return int(title.substr(6, at - 6))


# -- the fog of war (20's variants, 2026-10-19) -------------------------------------------------------
#
# For the variants in MapStyles/20-fog-of-war/, on the map as it is. What the party has seen is a
# mask the size of the sheet, painted along its journey (fog_mask()); the fog is fog_veil.gdshader on
# copies of the counties' outlines (add_fog()); what the fog leaves known is copies of lines over it
# with map_line_fogged.gdshader (add_known()); both read the mask through fog_common.gdshaderinc.

## The fog's mask: [constant FOG_CELLS] pixels over the sheet, about 10 map units (1 km) each.
const FOG_CELLS := Vector2i(1039, 1340)

## Every material that reads the fog's mask: the veil's and the known lines'. set_fog() sets them all.
var fog_materials: Array[ShaderMaterial] = []


## What the party has seen, as an image of FOG_CELLS (RG8): R how far explored, soft for the outer
## [param soft] of each radius, G how recently (1 the newest). [param paths] are its journeys and
## anything else that shows it land: each [points (map units), radii (one a point, map units), the
## recency at its first point, at its last], explored within each point's radius, and between two
## points within the radius between theirs.
func fog_mask(paths: Array, soft := 0.3) -> Image:
	var w := FOG_CELLS.x
	var h := FOG_CELLS.y
	var size := Vector2(SHEET.x / w, SHEET.y / h)
	var bytes := PackedByteArray()
	bytes.resize(w * h * 2)
	for path: Array in paths:
		var points: PackedVector2Array = path[0]
		var radii: PackedFloat32Array = path[1]
		var t0: float = path[2]
		var t1: float = path[3]
		var total := 0.0
		for i in points.size() - 1:
			total += points[i].distance_to(points[i + 1])
		var gone := 0.0
		for i in maxi(points.size() - 1, 1):
			var a := points[i]
			var b := points[mini(i + 1, points.size() - 1)]
			var ra := radii[i]
			var rb := radii[mini(i + 1, points.size() - 1)]
			var reach := maxf(ra, rb)
			var low := Vector2i(clampi(floori((minf(a.x, b.x) - reach) / size.x), 0, w - 1),
					clampi(floori((minf(a.y, b.y) - reach) / size.y), 0, h - 1))
			var high := Vector2i(clampi(floori((maxf(a.x, b.x) + reach) / size.x), 0, w - 1),
					clampi(floori((maxf(a.y, b.y) + reach) / size.y), 0, h - 1))
			var ab := b - a
			var length2 := ab.length_squared()
			var leg := sqrt(length2)
			for y in range(low.y, high.y + 1):
				var py := (y + 0.5) * size.y
				for x in range(low.x, high.x + 1):
					var p := Vector2((x + 0.5) * size.x, py)
					var u := 0.0 if length2 <= 0.0 else clampf((p - a).dot(ab) / length2, 0.0, 1.0)
					var r := lerpf(ra, rb, u)
					var d := p.distance_to(a + ab * u)
					if d >= r:
						continue
					var k := (y * w + x) * 2
					var e := int(round((1.0 - smoothstep(r * (1.0 - soft), r, d)) * 255.0))
					if e > bytes[k]:
						bytes[k] = e
					var along := (gone + u * leg) / total if total > 0.0 else 1.0
					var t := int(round(lerpf(t0, t1, along) * 255.0))
					if t > bytes[k + 1]:
						bytes[k + 1] = t
			gone += leg
	return Image.create_from_data(w, h, false, Image.FORMAT_RG8, bytes)


## Marks every county in [param counties] (by number) explored whole in [param mask], with a
## recency of [param recency]: as CountyMap.png has it, pixel by pixel.
func reveal_counties(mask: Image, counties: Dictionary, recency := 1.0) -> void:
	if counties.is_empty():
		return
	var ids := Image.load_from_file(source_dir().path_join("CountyMap.png"))
	var id_bytes := ids.get_data()
	var id_w := ids.get_width()
	var w := mask.get_width()
	var h := mask.get_height()
	var size := Vector2(SHEET.x / w, SHEET.y / h)
	var bytes := mask.get_data()
	var t := int(round(recency * 255.0))
	for y in h:
		var py := clampi(int(((y + 0.5) * size.y) / 3.35), 0, ids.get_height() - 1)
		for x in w:
			var px := clampi(int(((x + 0.5) * size.x) / 3.35), 0, id_w - 1)
			if counties.has(id_bytes[py * id_w + px]):
				var k := (y * w + x) * 2
				bytes[k] = 255
				bytes[k + 1] = maxi(bytes[k + 1], t)
	mask.set_data(w, h, false, Image.FORMAT_RG8, bytes)


## How far explored [param mask] has a point of the map (map units), 0 to 1.
static func explored_at(mask: Image, point: Vector2) -> float:
	var x := clampi(int(point.x / (SHEET.x / mask.get_width())), 0, mask.get_width() - 1)
	var y := clampi(int(point.y / (SHEET.y / mask.get_height())), 0, mask.get_height() - 1)
	return mask.get_pixel(x, y).r


## The fog: fog_veil.gdshader with [param params] and the mask, on copies of the counties' outlines
## (the land; the sea stays clear) or, with [param over_sea], on one polygon over the sheet and the
## sea round it, in a group drawn just after the bridges. A county numbered in [param clear] gets no
## fog at all (seen whole). Returns the material.
func add_fog(mask: Image, params: Dictionary, over_sea := false, clear := {}) -> ShaderMaterial:
	var material := shader_material("fog_veil.gdshader", params)
	var texture := mask_texture(mask)
	material.set_shader_parameter(&"mask", texture)
	if not params.has("elevation"):
		material.set_shader_parameter(&"elevation", data_texture("elevation.png"))
	if not params.has("forests"):
		material.set_shader_parameter(&"forests", data_texture("forest_mask.png"))
	fog_materials.append(material)
	var fog := Node2D.new()
	fog.name = "Fog"
	insert_after("Bridges", fog)
	if over_sea:
		var all := Polygon2D.new()
		all.polygon = PackedVector2Array([Vector2(-30000, -30000), Vector2(40385, -30000), Vector2(40385, 43400),
				Vector2(-30000, 43400)])
		all.material = material
		fog.add_child(all)
	else:
		for county in counties():
			var title := str(county.name)
			if title.substr(6).is_valid_int() and clear.has(int(title.substr(6))):
				continue
			var copy := Polygon2D.new()
			copy.name = title + "Fog"
			copy.polygon = county.polygon
			copy.transform = transform_in_map(county)
			copy.material = material
			fog.add_child(copy)
	# The settlements and the party over the fog and over the known lines (z 2).
	set_z("Settlements", 3)
	set_z("Party", 4)
	return material


## A node's transform in the map's space, from its own and its parents' (works before the map is in
## the tree).
func transform_in_map(node: Node2D) -> Transform2D:
	var result := Transform2D.IDENTITY
	var current: Node = node
	while current != null and current != map:
		if current is Node2D:
			result = (current as Node2D).transform * result
		current = current.get_parent()
	return result


## The mask as a texture, with the mipmaps fog_veil.gdshader's distance_lod reads.
func mask_texture(mask: Image) -> ImageTexture:
	var copy := mask.duplicate() as Image
	copy.generate_mipmaps()
	return ImageTexture.create_from_image(copy)


## Copies of [param nodes] (lines, or lake polygons) drawn over the fog where it is, each beside its
## own as a sibling, so that MapDetail gives it the same tier and width, at z 2. Each keeps its own
## pattern and casing through map_line_fogged.gdshader, or with [param sketch] given (alpha over 0) is
## drawn in that colour instead, [param width_share] as wide. The fog's mask and [param fog] (its
## edge settings) are set on their materials.
func add_known(nodes: Array, mask: Image, fog: Dictionary, sketch := Color(0, 0, 0, 0), width_share := 1.0) -> void:
	var texture := mask_texture(mask)
	var fogged := load(root + "/shaders/map_line_fogged.gdshader") as Shader
	var made := {}
	for node: CanvasItem in nodes:
		var copy := node.duplicate() as CanvasItem
		copy.name = str(node.name) + "Known"
		copy.z_index = 2
		var own: Material = node.material
		if not made.has(own):
			var material: ShaderMaterial
			if own is ShaderMaterial:
				material = (own as ShaderMaterial).duplicate() as ShaderMaterial
				material.shader = fogged
			else:
				material = ShaderMaterial.new()
				material.shader = fogged
			material.set_shader_parameter(&"mask", texture)
			material.set_shader_parameter(&"sketch", sketch)
			for key: String in fog:
				material.set_shader_parameter(key, fog[key])
			fog_materials.append(material)
			made[own] = material
		copy.material = made[own]
		if copy is Line2D:
			var line := copy as Line2D
			line.texture_mode = Line2D.LINE_TEXTURE_TILE
			line.width *= width_share
		node.get_parent().add_child(copy)


## Sets the same parameters on every material that reads the fog's mask.
func set_fog(params: Dictionary) -> void:
	for material in fog_materials:
		for key: String in params:
			material.set_shader_parameter(key, params[key])


## Hides every settlement the party has not seen, but those of the groups in [param keep]
## ("KingdomCapitals", ...). Returns where those hidden are, by group: {group: [Vector2, ...]}.
## Once the map is ready.
func hide_unseen(mask: Image, keep: Array = []) -> Dictionary:
	var hidden := {}
	for place in settlements():
		var group := str(place.get_parent().name)
		var at_point := to_map_space(place, Vector2.ZERO)
		if keep.has(group) or explored_at(mask, at_point) >= 0.5:
			continue
		place.visible = false
		if not hidden.has(group):
			hidden[group] = []
		hidden[group].append(at_point)
	return hidden


# -- colour helpers --------------------------------------------------------------------------------

## A colour from a hex string, with an alpha.
static func hex(code: String, alpha := 1.0) -> Color:
	var color := Color.html(code)
	color.a = alpha
	return color
