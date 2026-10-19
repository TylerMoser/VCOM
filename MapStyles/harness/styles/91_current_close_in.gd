## 91 · Not a proposal: the map as it is, close in, where its lines meet: borders along rivers and
## roads, a border along a river to the sea, borders and a river ending at the coast. Six views
## of 25 and 30 miles, where the borders are at their thinnest and faintest and the roads at their
## widest (MapStyles/91-current-look-close-in.png, beside 00's four standard views). The same
## places pictured the look as first applied, on 2026-10-18.
extends RefCounted

const NAME := "Current look, close in"
## The views, but for I, which is found from its band (panels()).
const VIEWS := [
	["E", "A kingdom border along a river, 30 miles", Vector2(5715, 8450), 30.0],
	["F", "A kingdom border along a river to the sea, 25 miles", Vector2(8330, 9120), 25.0],
	["G", "A duchy border along a river, 30 miles", Vector2(7870, 6842), 30.0],
	["H", "County borders along a river, 30 miles", Vector2(7850, 8450), 30.0],
	["J", "Borders and a river ending at the coast, 25 miles", Vector2(8330, 9700), 25.0],
]
## A duchy border's band along a road: view I is centred on its middle point.
const ALONG_ROAD := "Borders/Duchies/Duchies32And34AlongRoad364"


func apply(_kit) -> void:
	pass


func panels(kit) -> Array:
	var views: Array = VIEWS.slice(0, 4)
	var band := kit.at(ALONG_ROAD) as Line2D
	var middle := Vector2(4900, 7690)
	if band != null:
		middle = kit.to_map_space(band, band.points[band.points.size() / 2])
	views.append(["I", "A duchy border along a road, 25 miles", middle, 25.0])
	views.append(VIEWS[4])
	return views
