## 27 · Physical map. The land coloured by its height, as school atlases and
## the Swiss school's maps do: green lowlands rising through straw and tan to
## brown uplands, grey heights and white peaks (land.gdshader's colour ramp
## over MapCreation/Elevation.png), with shaded relief over it. Forests are a
## soft green veil, water one blue, and every line is thin and quiet (red-brown
## roads, violet-grey borders), so the island itself is the picture: where
## the mountains, valleys and plains are reads before anything else.
extends RefCounted

const NAME := "Physical map"
const QUIET := preload("res://_probe/styles/01_quiet_borders.gd")
const WATER := preload("res://_probe/styles/05_one_water.gd")

var _water := WATER.new()


func apply(kit) -> void:
	# Heights are the square root of their share of 3,352 m: 0.24 is 200 m,
	# 0.39 500 m, 0.55 1,000 m, 0.67 1,500 m, 0.77 2,000 m, 0.86 2,500 m.
	var ramp: GradientTexture1D = kit.ramp([
		[0.0, Color("#a9cf94")], [0.2, Color("#c4dc9c")], [0.36, Color("#e2e2a8")], [0.5, Color("#e8d3a0")],
		[0.62, Color("#d6b68a")], [0.74, Color("#bf9c7c")], [0.84, Color("#b0a59c")], [0.93, Color("#dedad6")],
		[1.0, Color("#ffffff")],
	])
	kit.set_land(Color.WHITE)
	kit.style_land({"ramp": ramp, "ramp_mix": 1.0})
	kit.add_relief(0.6, 0.16)
	kit.style_forests("", Color("#3f8a46", 0.3), {"glyph": 0})
	_water.apply(kit)
	for rank: String in QUIET.RANKS:
		var look: Array = QUIET.RANKS[rank]
		kit.style_rank(rank, look[0], look[1] * 0.85, null, "onto")
		kit.set_alpha("Borders/" + rank, look[2] + 0.1)
		kit.set_alpha("BordersOverLakes/" + rank, look[2] + 0.1)
	kit.color_lines("Roads/Highways", Color("#8f2f1f"))
	kit.color_lines("Roads/Roads", Color("#9c4a33"))
	kit.color_lines("Roads/Lanes", Color("#a8664d"))
	kit.set_alpha("Roads/Lanes", 0.7)
	kit.color_lines("Bridges", Color("#5a2a1a"))


func ready(kit) -> void:
	_water.ready(kit)
