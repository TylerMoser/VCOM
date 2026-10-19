## 14b · Borders follow the zoom. 14a's fade, and the borders' widths given a growth of their own
## on top of MapDetail's rule: times (miles / 220) ^ 0.3, so 1.49 times as wide all the way out
## (a kingdom border 2.3 px across where it is 1.5 now, which the Realm view, all about the
## kingdoms, can barely make out) and 0.52 times all the way in (2.8 px where it is 5.3). A
## border's band along a river or road grows its border part only. The roads keep MapDetail's
## rule.
##
## A pattern is laid in widths of its line, so a thinner border's dashes and dots shrink with it:
## all the way in a county's dots are about a pixel across, and with no fade of their own they
## all but go.
##
## Applied on 2026-10-19: these are MapDetail's own settings now, and its defaults.
extends RefCounted

const NAME := "Borders follow the zoom"
const LABEL := "14b"
const Now := preload("res://_probe/styles/140_emphasis_now.gd")


func apply(kit) -> void:
	var detail: Node = kit.as_revisited()
	detail.set("border_growth", 0.3)
	detail.set("kingdom_border_faintest", 0.55)
	detail.set("duchy_border_faintest", 0.7)
	detail.set("border_whole_view_miles", 240.0)
	detail.set("border_faintest_view_miles", 25.0)


func panels(_kit) -> Array:
	return Now.VIEWS
