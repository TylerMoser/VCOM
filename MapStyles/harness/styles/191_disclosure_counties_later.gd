## 19a · County borders at the County tier. The county borders, and those over lakes, come in at
## 100 miles with the villages instead of at 240 with the Duchy tier, so a view 240 to 100 miles
## tall has the kingdoms' and duchies' borders alone. Measured, the county borders now weigh a
## tenth of any other line there (dots 1.3 px across at 180 miles, half see-through): this takes
## a faint texture of some 80 lines out of the Duchy tier's views rather than a strong line.
##
## For real: two lines of MapDetail.SHOWN_FROM move from Tier.DUCHY to Tier.COUNTY, as they did
## when it was applied on 2026-10-19.
extends RefCounted

const NAME := "County borders at the County tier"
const LABEL := "19a"
const Now := preload("res://_probe/styles/190_disclosure_now.gd")


func apply(kit) -> void:
	var detail: Node = kit.as_revisited()
	detail.set("shown_from", kit.tiers_as_revisited({
		^"Borders/Counties": MapDetail.Tier.COUNTY,
		^"BordersOverLakes/Counties": MapDetail.Tier.COUNTY,
	}))


func panels(_kit) -> Array:
	return Now.VIEWS
