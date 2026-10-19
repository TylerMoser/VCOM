## 10 · Reweighted, same colours. Every colour stays as it is; only widths and
## transparency change, to give the map a hierarchy: the network (roads) and the
## water a little heavier, the borders much lighter, the coast half as heavy,
## the forests a little paler. The smallest change that answers "too busy",
## and a measure of how much of the problem is weight rather than colour.
extends RefCounted

const NAME := "Reweighted, same colours"


func apply(kit) -> void:
	# Borders: widths from 17, 10, 7; see-through.
	for rank: String in ["Kingdoms", "Duchies", "Counties"]:
		var width: float = {"Kingdoms": 9.0, "Duchies": 6.0, "Counties": 4.5}[rank]
		var alpha: float = {"Kingdoms": 0.75, "Duchies": 0.65, "Counties": 0.5}[rank]
		var color: Color = kit.lines_in("Borders/" + rank)[0].default_color
		kit.style_rank(rank, color, width, null, "keep")
		kit.set_alpha("Borders/" + rank, alpha)
		kit.set_alpha("BordersOverLakes/" + rank, alpha)
	# The coast: 23 units outside the land down to 12.
	kit.set_coast(Color.BLACK, 12.0 / 23.0)
	# Roads: highways from 10 to 13, roads from 7 to 8, lanes from 4 to 4.5,
	# and their bridges with them (7 wider than the road, 9 on a lane).
	kit.scale_widths("Roads/Highways", 1.3)
	kit.scale_widths("Roads/Roads", 8.0 / 7.0)
	kit.scale_widths("Roads/Lanes", 1.125)
	for bridge in kit.lines_in("Bridges"):
		bridge.width += 3.0 if bridge.width > 15.0 else 1.0
	# Forests a little paler.
	for piece in kit.forests():
		piece.color.a = 0.38


func ready(kit) -> void:
	kit.trim_sea_ends(12.0 / 23.0)
