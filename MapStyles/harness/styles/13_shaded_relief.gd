## 13 · Shaded relief. Hills and mountains shaded from the map's own heights
## (MapCreation/Elevation.png), lit from the north-west as maps have been since
## the Swiss school: the faces turned from the light a cool shade, those
## turned to it a touch warmer. It adds no line, yet says where the ranges,
## valleys and plains are, why the rivers and roads run where they do, and
## gives the eye landmarks to find its way back to. Laid over the land and the
## forests, under the borders, the water and everything else.
extends RefCounted

const NAME := "Shaded relief"


func apply(kit) -> void:
	kit.add_relief(0.55, 0.12)
