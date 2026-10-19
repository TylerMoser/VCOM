## 23 · Colour only for play. Everything that is only geography is drawn in
## quiet greys and grey-blues: the land, water, coast, borders, roads, rivers,
## and the settlements' pictures. Colour is kept for what the player acts on:
## the forests, where battles are met, in a clear green with a hatch; the party
## and its route in blue, red through forest; and gold round any settlement
## with something in it (here the town with the hiring board and the market).
## The eye goes straight to the few things that matter, the way XCOM's
## Geoscape keeps its world dark and its mission markers bright.
extends RefCounted

const NAME := "Colour only for play"


func apply(kit) -> void:
	kit.set_land(Color("#f2f2f0"))
	kit.set_sea(Color("#dfe5ea"))
	for lake: Polygon2D in kit.lakes():
		lake.color = Color("#c6d2dc")
	kit.color_lines("Rivers", Color("#a7b8c6"))
	kit.color_lines("Channels", Color("#a7b8c6"))
	kit.style_coast({"shore": Color("#aab6c1"), "shore_share": 0.4, "rings": 0}, 0.3)
	for rank: String in ["Kingdoms", "Duchies", "Counties"]:
		var width: float = {"Kingdoms": 9.0, "Duchies": 6.0, "Counties": 4.5}[rank]
		kit.style_rank(rank, Color("#8a8a8a"), width, null, "onto")
		var alpha: float = {"Kingdoms": 0.6, "Duchies": 0.45, "Counties": 0.3}[rank]
		kit.set_alpha("Borders/" + rank, alpha)
		kit.set_alpha("BordersOverLakes/" + rank, alpha)
	kit.color_lines("Roads/Highways", Color("#9c978f"))
	kit.color_lines("Roads/Roads", Color("#b3aea6"))
	kit.color_lines("Roads/Lanes", Color("#c4c0b9"))
	kit.color_lines("Bridges", Color("#8f8a83"))
	kit.scale_widths("Roads/Highways", 1.3)
	kit.style_forests("", Color("#52b060", 0.3), {
		"glyph": 6, "mark": Color("#2f8a3e", 0.4), "cell_px": 8.0, "mark_size": 0.45,
	})


func ready(kit) -> void:
	kit.trim_sea_ends(0.12)
	kit.tint_settlements("", Color(0.42, 0.43, 0.45, 1.0))
	var highlights: Node2D = kit.runtime("Highlights.gd").new()
	highlights.map = kit.map
	kit.map.add_child(highlights)
	var route: Node2D = kit.runtime("RouteOverlay.gd").new()
	route.party = kit.at("Party")
	route.route = PackedVector2Array([Vector2(6900.0, 7230.0), Vector2(6420.0, 7020.0)])
	kit.map.add_child(route)
