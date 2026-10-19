## 14a · Borders fade closing in. The least of 14: no width changes, only the borders' alpha by
## the zoom. Whole at and over 240 miles tall (the Duchy tier's top), then fading by the
## logarithm of the height to 0.55 of their alpha all the way in for the kingdoms (0.85 to 0.47)
## and 0.7 for the duchies (0.7 to 0.49); the counties, the faintest already, keep theirs. Close
## in, where the map is about the road ahead, the kingdom border is no longer the darkest line
## on it; far out nothing changes.
##
## For real: an alpha share by the zoom on the rank groups, multiplied in where MapDetail fades
## them by tier. Applied with 14b on 2026-10-19, it is MapDetail's own: its borders' faintest
## shares, with border_growth 0 for 14a alone.
extends RefCounted

const NAME := "Borders fade closing in"
const LABEL := "14a"
const Now := preload("res://_probe/styles/140_emphasis_now.gd")


func apply(kit) -> void:
	var detail: Node = kit.as_revisited()
	detail.set("kingdom_border_faintest", 0.55)
	detail.set("duchy_border_faintest", 0.7)
	detail.set("border_whole_view_miles", 240.0)
	detail.set("border_faintest_view_miles", 25.0)


func panels(_kit) -> Array:
	return Now.VIEWS
