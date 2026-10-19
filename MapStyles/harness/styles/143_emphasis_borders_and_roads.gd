## 14c · Borders and roads follow the zoom. 14b, and every road (highways, roads, lanes and their
## bridges) growing as the view closes in: times (miles / 220) ^ -0.1, so 1.24 times as wide all
## the way in (a highway 11.1 px across where it is 8.9 now, a road 7.7 where it is 6.2, a lane
## 3.9 where it is 3.1) and 0.94 times at 400 miles. All three kinds grow alike so that they keep
## their proportions: grown alone, a road comes within a few per cent of a highway's width.
##
## 14 as first pictured grew the roads by -0.3; on top of 04's doubled widths that would make a
## highway 15 px across all the way in, so the growth here is a third of it. A road grown reaches
## its casing's 4.5 px sooner, so the dip in its weight as the casing comes in (10b) comes sooner
## too, at about 60 miles rather than 45: grown roads want 10b's casing with them.
extends RefCounted

const NAME := "Borders and roads follow the zoom"
const LABEL := "14c"
const Now := preload("res://_probe/styles/140_emphasis_now.gd")


func apply(kit) -> void:
	var detail: Node = kit.as_revisited()
	detail.set("border_growth", 0.3)
	detail.set("road_growth", -0.1)
	detail.set("highway_growth", -0.1)
	detail.set("kingdom_border_faintest", 0.55)
	detail.set("duchy_border_faintest", 0.7)
	detail.set("border_whole_view_miles", 240.0)
	detail.set("border_faintest_view_miles", 25.0)


func panels(_kit) -> Array:
	return Now.VIEWS
