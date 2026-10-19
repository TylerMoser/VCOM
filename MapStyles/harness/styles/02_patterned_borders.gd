## 02 · Patterned borders. Every border in one dark ink, its rank told by its
## pattern, as printed maps have done for centuries: a kingdom's a dash and a
## dot, a duchy's long dashes, a county's dots. A pattern reads as "border" at
## a glance, where a solid line could be a road, a river or a border, and it
## reads in greyscale and to the colour-blind. Borders along rivers and lake
## shores are drawn on the water.
extends RefCounted

const NAME := "Patterned borders"

const INK := Color(0.25, 0.2, 0.31)


func apply(kit) -> void:
	kit.style_rank("Kingdoms", INK, 12.0,
			kit.line_material({"dash": 3.2, "gap": 1.0, "dot": 0.85, "dot_gap": 0.9}), "onto")
	kit.style_rank("Duchies", INK, 8.0,
			kit.line_material({"dash": 2.4, "gap": 1.3, "round_dashes": true}), "onto")
	kit.style_rank("Counties", INK, 6.0,
			kit.line_material({"dot": 0.85, "gap": 1.15}), "onto")
	for rank: String in ["Kingdoms", "Duchies", "Counties"]:
		var alpha: float = {"Kingdoms": 0.85, "Duchies": 0.7, "Counties": 0.5}[rank]
		kit.set_alpha("Borders/" + rank, alpha)
		kit.set_alpha("BordersOverLakes/" + rank, alpha)
