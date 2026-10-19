## 15 · Labels. Names, which are most of what makes Google Maps
## self-explanatory: a kingdom's name across its land in wide-spaced capitals
## far out, the duchies' in small spaced capitals as the view closes in, each
## settlement's beside its icon at a size by its rank, the great lakes in blue
## italics, all with a white halo so they read over any line. Each rank shows
## over its own zooms, and a name that would collide with another or with an
## icon is left out, the higher ranks placed first. The names are made up from
## the nodes' names (nothing is named yet); the kingdoms go by their biomes.
extends RefCounted

const NAME := "Labels"


func ready(kit) -> void:
	var labels: Node2D = kit.runtime("MapLabels.gd").new()
	labels.name = "MapLabels"
	labels.map = kit.map
	kit.map.add_child(labels)
