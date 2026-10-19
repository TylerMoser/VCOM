## 20, explored · The map as it is now, at the views the variants of 20 (fog of war) are pictured at
## (MapStyles/20-fog-of-war/now.png), with the party where the journey every variant shows has brought
## it: all the way out; the Duchy tier at 180 miles round the journey; the County tier at 70 miles
## round the party; and 35 miles across the edge of what it has seen, north of its last leg.
##
## The journey: from county 115's town, the party's start, by straight lines (as the Party travels)
## to the towns of counties 112 (a duchy's capital), 116, 113 and 121, and on to 69's (a duchy's
## capital), where it is now, some 160 miles in all; it is heading north for county 72's.
##
## Its constants and static helpers serve every variant (styles 2001 to 2024).
extends RefCounted

const NAME := "The map as it is now"
const LABEL := "20 now"
const Kit := preload("res://_probe/StyleKit.gd")
const MILE := 16.09344
const START := Vector2(7302, 7381)
const JOURNEY := [
	Vector2(7385, 7415), Vector2(7710, 7603), Vector2(8062, 7281), Vector2(7546, 6876), Vector2(7445, 6605),
	Vector2(6759, 6779),
]
const NEXT := Vector2(6765, 6189)
## How far the party sees about it on the way, in map units: 20 miles.
const SIGHT := 20.0 * MILE
const VIEWS := [
	["A", "Realm: all the way out", null, 0.0],
	["B", "Duchy tier: 180 miles, the journey", Vector2(7410, 7104), 180.0],
	["C", "County tier: 70 miles, where the party is", Vector2(6759, 6779), 70.0],
	["D", "35 miles: the edge of what it has seen", Vector2(7023, 6380), 35.0],
]
## Proposal 20's paper and the ink of its sketch.
const PAPER := Color(0.93, 0.9, 0.83)
const SKETCH := Color(0.47, 0.41, 0.33)
## 20's veil and edge: paper at 0.93, soft over the outer 30% of the sight, ragged.
const VEIL := {"veil": PAPER, "opacity": 0.93, "ragged": 0.25, "ragged_scale": 90.0}


func panels(_kit) -> Array:
	return VIEWS


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([NEXT])


func ready(kit) -> void:
	place_party(kit)


static func place_party(kit) -> void:
	(kit.at("Party") as Node2D).position = JOURNEY[JOURNEY.size() - 1]


## The journey as a path for StyleKit.fog_mask(): its points, [radius] at each, recency 0 to 1.
static func journey(radius := SIGHT) -> Array:
	var points := PackedVector2Array(JOURNEY)
	var radii := PackedFloat32Array()
	radii.resize(points.size())
	radii.fill(radius)
	return [points, radii, 0.0, 1.0]


## The journey cut into points [step] map units apart, for anything that changes along it.
static func journey_points(step := 32.0) -> PackedVector2Array:
	var points := PackedVector2Array()
	for i in JOURNEY.size() - 1:
		var a: Vector2 = JOURNEY[i]
		var b: Vector2 = JOURNEY[i + 1]
		var count := maxi(int(ceil(a.distance_to(b) / step)), 1)
		for k in count:
			points.append(a.lerp(b, float(k) / count))
	points.append(JOURNEY[JOURNEY.size() - 1])
	return points


## The lines (and lakes) the fog leaves known, by name: "coast"; "kingdoms" (their borders, bands
## along rivers and lines over lakes); "rivers" (the great ones, 12 units or wider, which show all the
## way out); "lakes" (100 units or more across, which do too); "roads" (the highways and roads, and
## the bridges on them).
static func known(kit, which: Array) -> Array:
	var nodes := []
	if which.has("coast"):
		nodes.append_array(kit.lines_in("Coast"))
	if which.has("kingdoms"):
		nodes.append_array(kit.lines_in("Borders/Kingdoms"))
		nodes.append_array(kit.lines_in("BordersOverLakes/Kingdoms"))
	if which.has("rivers"):
		for line: Line2D in kit.lines_in("Rivers"):
			if line.width >= 12.0:
				nodes.append(line)
	if which.has("lakes"):
		for lake: Polygon2D in kit.lakes():
			if across(lake.polygon) >= 100.0:
				nodes.append(lake)
	if which.has("roads"):
		nodes.append_array(kit.lines_in("Roads/Highways"))
		nodes.append_array(kit.lines_in("Roads/Roads"))
		for child in kit.at("Bridges").get_children():
			if child is Line2D:
				nodes.append(child)
	return nodes


## How far across a polygon is: the width of a circle of its area (as MapDetail measures a lake).
static func across(points: PackedVector2Array) -> float:
	var twice := 0.0
	for i in points.size():
		var a := points[i]
		var b := points[(i + 1) % points.size()]
		twice += a.x * b.y - b.x * a.y
	return 2.0 * sqrt(absf(twice) * 0.5 / PI)


## A variant's fog, as 20 had it unless told otherwise: the mask painted from [paths] (and the
## counties in [reveal] seen whole), the veil with [veil], and the lines in [which] known over it,
## drawn in [sketch] (alpha 0: their own look) at [share] of their width. Returns the mask.
static func fog(kit, paths: Array, veil := VEIL, which := ["coast", "kingdoms", "rivers"], sketch := SKETCH,
		share := 0.6, over_sea := false, reveal := {}, soft := 0.3) -> Image:
	var mask: Image = kit.fog_mask(paths, soft)
	kit.reveal_counties(mask, reveal)
	kit.add_fog(mask, veil, over_sea, reveal)
	var edge := {}
	for key: String in ["edge_soft", "ragged", "ragged_scale"]:
		if veil.has(key):
			edge[key] = veil[key]
	if not which.is_empty():
		kit.add_known(known(kit, which), mask, edge, sketch, share)
	return mask


## The counties the journey passes through, by number, as CountyMap.png has them.
static func journey_counties(kit) -> Dictionary:
	var ids := Image.load_from_file(kit.source_dir().path_join("CountyMap.png"))
	var found := {}
	for point in journey_points(16.0):
		var x := clampi(int(point.x / 3.35), 0, ids.get_width() - 1)
		var y := clampi(int(point.y / 3.35), 0, ids.get_height() - 1)
		var id := int(round(ids.get_pixel(x, y).r * 255.0))
		if id > 0:
			found[id] = true
	return found
