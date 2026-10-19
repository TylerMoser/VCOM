## 20 · Fog of war (todo.txt: "Map fog of war on unvisited areas"), as a style.
## Land the party has not seen lies under a paper-coloured veil, through which
## only what everyone would know shows, drawn as a sketch: the coast, the
## kingdoms' borders, the great rivers and the nine capitals. Around the party,
## the land it has seen is drawn in full. Early in a campaign almost all of the
## island is fog, so the map is calm by itself, and every journey fills it in.
## Here the seen land is a ring of 30 miles round the party's start.
extends RefCounted

const NAME := "Fog of war"

const PARTY := Vector2(7302.0, 7381.0)
const CLEAR := 30.0 * 16.09344
const EDGE := 140.0
const SKETCH := Color(0.47, 0.41, 0.33)


func apply(kit) -> void:
	var fog := Polygon2D.new()
	fog.name = "Fog"
	fog.polygon = PackedVector2Array([Vector2(-30000, -30000), Vector2(40385, -30000), Vector2(40385, 43400),
			Vector2(-30000, 43400)])
	fog.material = kit.shader_material("fog.gdshader", {
		"centre": PARTY, "clear_radius": CLEAR, "edge": EDGE, "fog": Color(0.93, 0.9, 0.83), "opacity": 0.93,
	})
	kit.insert_after("Bridges", fog)

	# The sketch over the fog: thin copies of the coast, the kingdoms' borders
	# and the rivers that show all the way out.
	var sketch := Node2D.new()
	sketch.name = "Sketch"
	kit.insert_after("Fog", sketch)
	for line: Line2D in kit.lines_in("Coast"):
		var copy := _copy(line, SKETCH, line.width * 0.16)
		sketch.add_child(copy)
	var dashed: ShaderMaterial = kit.line_material({"dash": 2.2, "gap": 1.4, "fill_alpha": 0.75})
	for line: Line2D in kit.plain_borders("Kingdoms"):
		var copy := _copy(line, SKETCH, 7.0)
		kit.pattern_line(copy, dashed)
		sketch.add_child(copy)
	for line: Line2D in kit.lines_in("Rivers"):
		if line.width >= 12.0:
			sketch.add_child(_copy(line, Color(0.42, 0.52, 0.6, 0.8), line.width * 0.45))


func ready(kit) -> void:
	for place: Node2D in kit.settlements():
		var group := str(place.get_parent().name)
		if group != "KingdomCapitals" and place.position.distance_to(PARTY) > CLEAR + EDGE * 0.5:
			place.visible = false


func _copy(line: Line2D, color: Color, width: float) -> Line2D:
	var copy := Line2D.new()
	copy.name = "%sSketch" % line.name
	copy.points = line.points
	copy.closed = line.closed
	copy.width = width
	copy.width_curve = line.width_curve
	copy.default_color = color
	copy.joint_mode = Line2D.LINE_JOINT_ROUND
	copy.begin_cap_mode = Line2D.LINE_CAP_ROUND
	copy.end_cap_mode = Line2D.LINE_CAP_ROUND
	return copy
