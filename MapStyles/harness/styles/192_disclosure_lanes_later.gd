## 19b · Lanes with the hamlets. The villages' lanes, and the bridges on them, come in at 50 miles
## with the hamlets instead of at 100 with the villages, so from 100 to 50 miles the villages
## stand without them. At the far end of the County tier the lanes are 1.9 px solid lines (their
## casing never shows: they are 3.1 px at the most), 78 of them in the County tier's standard
## view. This is the README's open question 4: the lanes at 100 miles or at 50.
##
## For real: two lines of MapDetail.SHOWN_FROM move from Tier.COUNTY to Tier.HAMLETS.
extends RefCounted

const NAME := "Lanes with the hamlets"
const LABEL := "19b"
const Now := preload("res://_probe/styles/190_disclosure_now.gd")


func apply(kit) -> void:
	var detail: Node = kit.as_revisited()
	detail.set("shown_from", kit.tiers_as_revisited({
		^"Roads/Lanes": MapDetail.Tier.HAMLETS,
		^"Bridges/Lanes": MapDetail.Tier.HAMLETS,
	}))


func panels(_kit) -> Array:
	return Now.VIEWS
