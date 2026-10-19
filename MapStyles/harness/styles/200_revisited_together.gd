## The revisited 10, 14 and 19 together: the variant of each that was recommended, applied one
## after another to the map as it was when they were revisited, at the standard views (that map at
## the same views is style 100). 10b's roads cased at every zoom with half their width as casing,
## 14b's borders heavier far out and thinner and fainter close in, and 19a's county borders with
## the County tier.
##
## All three were applied on 2026-10-19, so this draws the map as the scene now has it: the same
## pictures as style 0 (MapStyles/00-current-look.png).
extends RefCounted

const NAME := "10b, 14b and 19a together"
const LABEL := "Revisited"
const PICKS := [
	"res://_probe/styles/102_reweight_roads_hold.gd",
	"res://_probe/styles/142_emphasis_borders.gd",
	"res://_probe/styles/191_disclosure_counties_later.gd",
]


func apply(kit) -> void:
	for path: String in PICKS:
		var style: Object = (load(path) as GDScript).new()
		style.apply(kit)
