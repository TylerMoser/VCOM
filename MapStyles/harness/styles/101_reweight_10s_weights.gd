## 10a · 10's weights on today's look. Proposal 10 as it was pictured, on the map as it is now
## (02, 04, 05 and 10's forests applied): its borders' widths and alphas, 9, 6 and 4.5 units at
## 0.75, 0.65 and 0.5 (02's are 12, 8 and 6 at 0.85, 0.7 and 0.5), and its roads' gains taken as
## shares of 04's widths (highways 1.3 times, roads 8/7, lanes 1.125), their bridges and the
## borders' bands along them with them. Its coast is left out, 12 units outside the land being
## wider than the shoreline it gave way to, and its forests' 0.38 is applied already.
##
## It shows why 10's widths gave way: a border's pattern is laid in widths of its line, so a
## thinner border's dots and dashes shrink with it, and a county's dots go under a pixel.
extends RefCounted

const NAME := "10's weights on today's look"
const LABEL := "10a"


func apply(kit) -> void:
	kit.as_revisited()
	for rank: String in ["Kingdoms", "Duchies", "Counties"]:
		kit.reweight_rank(rank, {"Kingdoms": 9.0, "Duchies": 6.0, "Counties": 4.5}[rank])
		var alpha: float = {"Kingdoms": 0.75, "Duchies": 0.65, "Counties": 0.5}[rank]
		kit.set_alpha("Borders/" + rank, alpha)
		kit.set_alpha("BordersOverLakes/" + rank, alpha)
	kit.reweight_roads("Highways", 26.0)
	kit.reweight_roads("Roads", 16.0)
	kit.reweight_roads("Lanes", 7.875)
