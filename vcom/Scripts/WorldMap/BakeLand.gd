## Traces a world map's land mask into a scene of colliders and a navigation
## mesh, so the game never reads an image to know where land is.
##
## The land mask is a greyscale image the same size as the map art, one mask
## pixel to one map pixel: white is land, black is water. It is what says
## where the party can go, so the art is free to draw anything on the land.
## Paint it in any image editor; a pixel counts as land when it is more than
## half white (after its opacity, so transparent is water too). Then run, from
## vcom/:
##
##   godot --headless --path . --script res://Scripts/WorldMap/BakeLand.gd
##   godot --headless --path . --script res://Scripts/WorldMap/BakeLand.gd -- <mask> <scene>
##
## (defaults: res://WorldMap/WorldMapV1LandMask.png -> res://WorldMap/WorldMapV1Land.tscn).
##
## To start a mask from the art, when the coastline is redrawn, or to throw
## away the edits to one:
##
##   godot --headless --path . --script res://Scripts/WorldMap/BakeLand.gd -- --mask-from-art [<art> <mask>]
##
## (defaults: res://WorldMap/WorldMapV1.png -> res://WorldMap/WorldMapV1LandMask.png). That applies
## the same rule to the art: the island's interior is drawn white, and the
## black coastline, the ripples off it and the transparent sea are all water,
## so the land ends at the inside edge of the coastline ink. It overwrites the
## mask.
##
## Tracing follows pixel edges exactly, with no simplification: the polygons
## enclose precisely the land pixels.
##
## The scene it writes is a [StaticBody2D] named Land, in the map sprite's
## own coordinates (centred, as a [Sprite2D] draws its texture), to be made a
## child of that sprite. It holds one [CollisionPolygon2D] per boundary, as
## segments: a "Shore" around each piece of land and a "Lake" around each
## stretch of water land encloses. A point is land when an odd number of them
## surround it. Beside them is a [NavigationRegion2D] baked from the same
## outlines, which [WorldMapTerrain] routes the party over, so a route can
## never cross the collider. The Land node carries the mask's size as
## [code]mask_size[/code] metadata, which [WorldMapTerrain] checks against the
## art, since a mask of another size would put the coast in the wrong place.
##
## A script error does not end a --script run: Godot sits idle after it, so
## give the run a timeout when scripting it.
extends SceneTree

const DEFAULT_ART := "res://WorldMap/WorldMapV1.png"
const DEFAULT_MASK := "res://WorldMap/WorldMapV1LandMask.png"
const DEFAULT_SCENE := "res://WorldMap/WorldMapV1Land.tscn"
## Side, in map pixels, of the squares the navigation mesh is baked in.
const TILE := 256


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if not args.is_empty() and args[0] == "--mask-from-art":
		var art_path: String = args[1] if args.size() > 1 else DEFAULT_ART
		var out_path: String = args[2] if args.size() > 2 else DEFAULT_MASK
		quit(_mask_from_art(art_path, out_path))
		return
	var mask_path: String = args[0] if args.size() > 0 else DEFAULT_MASK
	var scene_path: String = args[1] if args.size() > 1 else DEFAULT_SCENE
	quit(_bake(mask_path, scene_path))


## Writes the land of the map art at [param art_path] as a mask at
## [param mask_path]: white where the art is more than half white, black
## everywhere else. Returns the exit code.
func _mask_from_art(art_path: String, mask_path: String) -> int:
	var art := _read_image(art_path)
	if art == null:
		return 1
	var land := _land_mask(art)
	var mask := land.convert_to_image()
	var error := mask.save_png(ProjectSettings.globalize_path(mask_path))
	if error != OK:
		push_error("BakeLand: could not save '%s' (%s)." % [mask_path, error_string(error)])
		return 1
	print("BakeLand: %s -> %s: %dx%d, %d land pixels." % [
		art_path, mask_path, mask.get_width(), mask.get_height(), land.get_true_bit_count(),
	])
	return 0


## Reads the image at [param path] straight from its file, not through the
## import system, so a mask just painted or just written can be baked without
## opening the editor to import it first. Null, with an error, if it cannot.
func _read_image(path: String) -> Image:
	var image := Image.new()
	var error := image.load(ProjectSettings.globalize_path(path))
	if error != OK:
		push_error("BakeLand: cannot read '%s' as an image (%s)." % [path, error_string(error)])
		return null
	if image.is_compressed():
		image.decompress()
	image.clear_mipmaps()
	return image


## Traces the mask at [param mask_path] into the land scene at
## [param scene_path]. Returns the exit code.
func _bake(mask_path: String, scene_path: String) -> int:
	var image := _read_image(mask_path)
	if image == null:
		return 1
	var size := image.get_size()
	var bounds := Rect2i(Vector2i.ZERO, size)

	var land := _land_mask(image)
	var water := _inverse(land, size)

	# BitMap traces the outside of each region and ignores its holes, so the
	# land's holes are found as water regions instead: each boundary is the
	# outside of exactly one of the two sides. The sea's own outside is the
	# frame of the image, which is no boundary at all.
	var shores := land.opaque_to_polygons(bounds, 0.0)
	var lakes: Array[PackedVector2Array] = []
	for outline in water.opaque_to_polygons(bounds, 0.0):
		if not _touches_frame(outline, size):
			lakes.append(outline)
	shores.sort_custom(func(a, b): return _area(a) > _area(b))
	lakes.sort_custom(func(a, b): return _area(a) > _area(b))

	# Centre on the image, as the sprite draws it.
	var centre := Vector2(size) * 0.5
	shores.assign(shores.map(func(outline): return _shifted(outline, -centre)))
	lakes.assign(lakes.map(func(outline): return _shifted(outline, -centre)))

	var root := StaticBody2D.new()
	root.name = "Land"
	root.set_meta(&"mask_size", size)
	for i in shores.size():
		_add_outline(root, "Shore%d" % (i + 1), shores[i])
	for i in lakes.size():
		_add_outline(root, "Lake%d" % (i + 1), lakes[i])

	if shores.is_empty():
		push_error("BakeLand: '%s' has no land in it: nothing more than half white." % mask_path)
		root.free()
		return 1
	var navigation := _bake_navigation(shores, lakes)
	if navigation == null:
		root.free()
		return 1
	var region := NavigationRegion2D.new()
	region.name = "Navigation"
	region.navigation_polygon = navigation
	root.add_child(region)
	region.owner = root

	var packed := PackedScene.new()
	var error := packed.pack(root)
	if error == OK:
		error = ResourceSaver.save(packed, scene_path)
	root.free()
	if error != OK:
		push_error("BakeLand: could not save '%s' (%s)." % [scene_path, error_string(error)])
		return 1

	var vertices := 0
	for outline in shores + lakes:
		vertices += outline.size()
	print("BakeLand: %s -> %s: %d shores, %d lakes, %d vertices, %d land pixels." % [
		mask_path, scene_path, shores.size(), lakes.size(), vertices, land.get_true_bit_count(),
	])
	return 0


## The land pixels of [param image], art or mask: more than half white after
## its opacity.
## Done with whole-image operations, as a pixel loop over a map this size
## would take minutes in GDScript.
func _land_mask(image: Image) -> BitMap:
	var grey := image.duplicate() as Image
	grey.premultiply_alpha()
	grey.convert(Image.FORMAT_LA8)
	var mask := BitMap.new()
	mask.create_from_image_alpha(_luminance_as_alpha(grey), 0.5)
	return mask


## Every bit of [param mask] flipped.
func _inverse(mask: BitMap, size: Vector2i) -> BitMap:
	var set_bits := mask.convert_to_image()
	set_bits.convert(Image.FORMAT_LA8)
	var flipped := Image.create(size.x, size.y, false, Image.FORMAT_LA8)
	flipped.fill(Color.WHITE)
	# Clear the pixels the mask has set, leaving the rest opaque.
	var clear := Image.create(size.x, size.y, false, Image.FORMAT_LA8)
	flipped.blit_rect_mask(clear, _luminance_as_alpha(set_bits), Rect2i(Vector2i.ZERO, size), Vector2i.ZERO)
	var inverse := BitMap.new()
	inverse.create_from_image_alpha(flipped, 0.5)
	return inverse


## An LA8 image whose alpha is [param image]'s luminance. LA8 stores each
## pixel as luminance then alpha, so moving every byte along by one puts each
## pixel's luminance where its alpha is read from.
func _luminance_as_alpha(image: Image) -> Image:
	var bytes := PackedByteArray([0])
	bytes.append_array(image.get_data().slice(0, -1))
	return Image.create_from_data(image.get_width(), image.get_height(), false, Image.FORMAT_LA8, bytes)


func _touches_frame(outline: PackedVector2Array, size: Vector2i) -> bool:
	for point in outline:
		if point.x <= 0.0 or point.y <= 0.0 or point.x >= size.x or point.y >= size.y:
			return true
	return false


func _add_outline(root: Node, outline_name: String, outline: PackedVector2Array) -> void:
	var shape := CollisionPolygon2D.new()
	shape.name = outline_name
	# Segments, not solids: a solid would be cut into convex pieces, which a
	# coastline of thousands of points does not survive well, and the rules
	# only ever ask which side of the line a point is on.
	shape.build_mode = CollisionPolygon2D.BUILD_SEGMENTS
	shape.polygon = outline
	root.add_child(shape)
	shape.owner = root


## A navigation mesh covering exactly the land: every shore, less every lake,
## with no margin kept from the edge, so it keeps the outlines' own vertices.
## Returns null if nothing came of it.
##
## It is baked a [constant TILE] square at a time and the pieces put together.
## Baked whole, a coastline this detailed comes out as a few huge polygons
## fanned out to thousands of pixel corners, and the navigation server, which
## works in single precision, cannot tell which of those long slivers a point
## is in: it found no polygon at all under the middle of the island. Tiles keep
## every polygon small, and bake in half a second where the whole took
## fifteen. Their pieces meet along the tile lines on shared vertices, as the
## bake adds none of its own, so the server joins them edge to edge.
func _bake_navigation(shores: Array[PackedVector2Array], lakes: Array[PackedVector2Array]) -> NavigationPolygon:
	var source := NavigationMeshSourceGeometryData2D.new()
	var bounds := Rect2(shores[0][0], Vector2.ZERO)
	for outline in shores:
		source.add_traversable_outline(outline)
		for point in outline:
			bounds = bounds.expand(point)
	for outline in lakes:
		source.add_obstruction_outline(outline)

	# Every polygon of every tile, as its corners, and every corner that lies
	# on a tile line, by the line it lies on.
	var polygons: Array[PackedVector2Array] = []
	var on_columns := {}
	var on_rows := {}
	var top_left := Vector2i((bounds.position / TILE).floor() * TILE)
	for y in range(top_left.y, ceili(bounds.end.y), TILE):
		for x in range(top_left.x, ceili(bounds.end.x), TILE):
			var tile := NavigationPolygon.new()
			tile.agent_radius = 0.0
			tile.baking_rect = Rect2(x, y, TILE, TILE)
			NavigationServer2D.bake_from_source_geometry_data(tile, source)
			for i in tile.get_polygon_count():
				var corners := PackedVector2Array()
				for index in tile.get_polygon(i):
					var corner := tile.vertices[index]
					corners.append(corner)
					if posmod(int(corner.x) - top_left.x, TILE) == 0:
						_file_under(on_columns, int(corner.x), corner.y)
					if posmod(int(corner.y) - top_left.y, TILE) == 0:
						_file_under(on_rows, int(corner.y), corner.x)
				polygons.append(corners)
	if polygons.is_empty():
		push_error("BakeLand: baking the navigation mesh gave no polygons.")
		return null

	# The server joins polygons along edges they share end to end. Along a
	# tile line, one tile's bake can leave out a corner the tile across the
	# line keeps, where the coast runs straight along the line on one side,
	# and then nothing joins there: whole stretches of land were cut off. So
	# every corner on a tile line goes into every edge along that line.
	var navigation := NavigationPolygon.new()
	navigation.agent_radius = 0.0
	var vertices := PackedVector2Array()
	var index_of := {}
	for corners in polygons:
		var polygon := PackedInt32Array()
		for i in corners.size():
			var a := corners[i]
			var b := corners[(i + 1) % corners.size()]
			polygon.append(_index(a, vertices, index_of))
			var between := PackedFloat32Array()
			if a.x == b.x and on_columns.has(int(a.x)):
				between = _between(on_columns[int(a.x)], a.y, b.y)
				for along in between:
					polygon.append(_index(Vector2(a.x, along), vertices, index_of))
			elif a.y == b.y and on_rows.has(int(a.y)):
				between = _between(on_rows[int(a.y)], a.x, b.x)
				for along in between:
					polygon.append(_index(Vector2(along, a.y), vertices, index_of))
		navigation.add_polygon(polygon)
	navigation.vertices = vertices
	return navigation


func _file_under(lines: Dictionary, line: int, along: float) -> void:
	if not lines.has(line):
		lines[line] = PackedFloat32Array()
	var points: PackedFloat32Array = lines[line]
	points.append(along)
	lines[line] = points


## The values in [param points] strictly between [param from] and [param to],
## in order going from one to the other.
func _between(points: PackedFloat32Array, from: float, to: float) -> PackedFloat32Array:
	var found := PackedFloat32Array()
	for along in points:
		if along > minf(from, to) and along < maxf(from, to) and not found.has(along):
			found.append(along)
	found.sort()
	if from > to:
		found.reverse()
	return found


## The index of [param point] in [param vertices], adding it if it is new.
func _index(point: Vector2, vertices: PackedVector2Array, index_of: Dictionary) -> int:
	if not index_of.has(point):
		index_of[point] = vertices.size()
		vertices.append(point)
	return index_of[point]


func _shifted(outline: PackedVector2Array, by: Vector2) -> PackedVector2Array:
	var moved := outline.duplicate()
	for i in moved.size():
		moved[i] += by
	return moved


func _area(outline: PackedVector2Array) -> float:
	var twice := 0.0
	for i in outline.size():
		twice += outline[i].cross(outline[(i + 1) % outline.size()])
	return absf(twice) * 0.5
