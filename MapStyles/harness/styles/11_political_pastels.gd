## 11 · Political pastels. Each kingdom's land a soft pastel of its own, as
## in a political atlas, its duchies a shade apart; the kingdom is then the
## area itself and its border only where two colours meet, so the heavy lines
## go: a thin dark kingdom border, fainter duchy and county lines. The forests
## become a fine stipple of darker dots over a light green wash, which keeps
## them readable over any of the pastels.
extends RefCounted

const NAME := "Political pastels"

const PASTEL := {
	1: "#d6e0f3", 2: "#f3d6de", 3: "#ebe4c9", 4: "#f6dfc6", 5: "#e2d8f3",
	6: "#d0ebe4", 7: "#e4eac9", 8: "#f3d9d0", 9: "#d6ebcc",
}


func apply(kit) -> void:
	for county: Polygon2D in kit.counties():
		var tint: Color = kit.hex(PASTEL[kit.kingdom_of(county)])
		# Every other duchy a shade darker.
		if kit.duchy_of(county) % 2 == 0:
			tint = tint.darkened(0.05)
		county.color = tint
	for island: Polygon2D in kit.lake_islands():
		var at: Vector2 = island.polygon[0]
		for county: Polygon2D in kit.counties():
			if Geometry2D.is_point_in_polygon(at, county.polygon):
				island.color = county.color
				break
	kit.style_forests("", kit.hex("#7fae7a", 0.22), {
		"glyph": 5, "mark": kit.hex("#2f5f35", 0.55), "cell_px": 7.0, "mark_size": 0.9, "density": 0.7, "jitter": 0.3,
	})
	kit.style_rank("Kingdoms", kit.hex("#463b52"), 7.0, null, "onto")
	kit.style_rank("Duchies", kit.hex("#6a6075"), 4.5, null, "onto")
	kit.style_rank("Counties", kit.hex("#857e8e"), 3.5, null, "onto")
	for rank: String in ["Kingdoms", "Duchies", "Counties"]:
		var alpha: float = {"Kingdoms": 0.9, "Duchies": 0.6, "Counties": 0.35}[rank]
		kit.set_alpha("Borders/" + rank, alpha)
		kit.set_alpha("BordersOverLakes/" + rank, alpha)
