## 19d · Ramps, not steps. Nothing moves to another tier; instead the county borders and the lanes
## come in faint and strengthen as the view closes in, so a view never gains a whole layer at
## once. The county borders show from 240 miles as now, at nothing there and whole by 120, by the
## logarithm of the height; the lanes, and the bridges on them, from 100 miles as now, whole by
## 60. At 180 miles the county borders are at 41% of their alpha (0.21), at 80 the lanes at 44%.
##
## For real: an alpha share by the zoom on those groups, multiplied in where MapDetail fades them
## by tier (RevisitedDetail._process()), as 14b fades the borders the other way.
extends RefCounted

const NAME := "Ramps, not steps"
const LABEL := "19d"
const Now := preload("res://_probe/styles/190_disclosure_now.gd")


func apply(kit) -> void:
	var detail: Node = kit.as_revisited()
	detail.set("ramps", {
		^"Borders/Counties": [240.0, 120.0],
		^"BordersOverLakes/Counties": [240.0, 120.0],
		^"Roads/Lanes": [100.0, 60.0],
		^"Bridges/Lanes": [100.0, 60.0],
	})


func panels(_kit) -> Array:
	return Now.VIEWS
