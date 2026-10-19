## 01 · Quiet borders. The borders step back: thinner, low-contrast,
## see-through lines in one muted violet-grey family, darkest for the kingdoms
## and lightest for the counties, so that roads, water and settlements come
## forward. A border that follows a river or a lake's shore is drawn on the
## water as a plain border, instead of a band of its colour on both banks.
extends RefCounted

const NAME := "Quiet borders"

## Each rank: colour, width in units at 220 miles tall (the scene has 17, 10
## and 7), and alpha.
const RANKS := {
	"Kingdoms": [Color(0.36, 0.28, 0.45), 10.0, 0.7],
	"Duchies": [Color(0.46, 0.4, 0.55), 6.5, 0.55],
	"Counties": [Color(0.5, 0.48, 0.55), 5.0, 0.38],
}


func apply(kit) -> void:
	for rank: String in RANKS:
		var look: Array = RANKS[rank]
		kit.style_rank(rank, look[0], look[1], null, "onto")
		kit.set_alpha("Borders/" + rank, look[2])
		kit.set_alpha("BordersOverLakes/" + rank, look[2])
