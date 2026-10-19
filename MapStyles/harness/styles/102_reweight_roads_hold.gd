## 10b · Roads keep their weight close in. Measured on the map as it is
## (tools/line_weights.py), a road loses some 40% of its weight as its casing comes in, between
## about 55 and 30 miles tall: its cream fill is all but the white land's colour, so once cased
## it is two thin edges where it was a solid line, and all the way in it weighs no more than a
## lane and half what a kingdom border does. Here its casing takes half its width (from 0.3) and
## comes in from 3 px across (from 4.5), so a road is cased wherever it is more than a hairline
## and only grows heavier closing in; and it is a little wider, 16 units (from 14), with its
## bridges and the bands along it. The lanes, whose casing never shows (they are 3.1 px at the
## most, under its 5), are 8 units (from 7). No colour changes.
##
## Applied on 2026-10-19: the scene and Road.tres have these values now.
extends RefCounted

const NAME := "Roads keep their weight close in"
const LABEL := "10b"


func apply(kit) -> void:
	kit.as_revisited()
	kit.reweight_roads("Roads", 16.0)
	kit.reweight_roads("Lanes", 8.0)
	var road := kit.lines_in("Roads/Roads")[0].material as ShaderMaterial
	road.set_shader_parameter(&"casing_share", 0.5)
	road.set_shader_parameter(&"casing_min_px", 3.0)
