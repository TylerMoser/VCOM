## 04 · Cased roads. Roads drawn as roads are on every road map: a light fill
## between two darker edges, a casing. Highways amber, roads cream, lanes white;
## bridges are the road carried over the water between dark parapets. A cased
## line can only be a road, so roads stop being confused with borders and
## rivers, and the red they were is left to the party alone.
##
## A casing needs room: below a few pixels across a road is drawn as one solid
## line of a darker tone (casing_min_px and narrow), which the shader works
## out from the line's own width on the screen, so nothing has to follow the zoom.
extends RefCounted

const NAME := "Cased roads"

## Each kind: how much wider than the scene, fill, casing, the share of the
## half-width each side that is casing, the least width in pixels for a
## casing, and the solid colour below that.
const KINDS := {
	"Highways": [2.0, "#ffc451", "#b5761a", 0.28, 4.0, "#e09a2a"],
	"Roads": [2.0, "#fffaf0", "#9c8f7d", 0.3, 4.5, "#a3958a"],
	"Lanes": [1.75, "#ffffff", "#b5aa9a", 0.34, 5.0, "#b8ad9d"],
}
## The dark parapets of a bridge.
const PARAPET := "#4b4038"


func apply(kit) -> void:
	# A border along a road is a band under it, as wide as the road and the
	# border on both sides: it widens with its road, by what that road gains.
	var bands := {}
	for rank: String in ["Counties", "Duchies", "Kingdoms"]:
		for line: Line2D in kit.along_lines(rank, "Road"):
			bands[line] = kit.road_under(line)
	var fills := {}
	for kind: String in KINDS:
		var look: Array = KINDS[kind]
		var path := "Roads/" + kind
		var before: float = kit.lines_in(path)[0].width
		kit.scale_widths(path, look[0])
		fills[kind] = look[1]
		kit.pattern_lines(path, kit.line_material({
			"fill_from_line": false, "fill": kit.hex(look[1]), "casing": kit.hex(look[2]),
			"casing_share": look[3], "casing_min_px": look[4], "narrow": kit.hex(look[5]),
		}))
		for line: Line2D in bands:
			if bands[line] == kind:
				line.width += before * (look[0] - 1.0)

	# Bridges lie along their road, 7 units wider (9 on a lane): 17 over a
	# highway, 14 over a road. Each is drawn as its road's fill, wider again,
	# with dark edges.
	var parapet: Color = kit.hex(PARAPET)
	var over := {
		"Highways": kit.line_material({"fill_from_line": false, "fill": kit.hex(fills["Highways"]), "casing": parapet,
				"casing_share": 0.42, "casing_min_px": 3.0, "narrow": parapet}),
		"Roads": kit.line_material({"fill_from_line": false, "fill": kit.hex(fills["Roads"]), "casing": parapet,
				"casing_share": 0.42, "casing_min_px": 3.0, "narrow": parapet}),
		"Lanes": kit.line_material({"fill_from_line": false, "fill": kit.hex(fills["Lanes"]), "casing": parapet,
				"casing_share": 0.45, "casing_min_px": 3.0, "narrow": parapet}),
	}
	for bridge: Line2D in kit.lines_in("Bridges"):
		var on_lane: bool = bridge.get_parent().name == &"Lanes"
		var kind: String = "Lanes" if on_lane else ("Highways" if bridge.width > 15.0 else "Roads")
		var road: float = {"Lanes": 4.0, "Highways": 10.0, "Roads": 7.0}[kind] * KINDS[kind][0]
		bridge.width = road * 1.45
		kit.pattern_line(bridge, over[kind])
