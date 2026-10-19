## 19c · 19 in full, its lakes corrected. 19a and 19b, the woods (forests under 10 km²) with the
## hamlets at 50 miles too, and the smallest lakes with the County tier.
##
## 19 as first proposed held back lakes under 20 units (2 km) across, but the map's smallest
## lakes are 2 to 3 km: only 9 of the Duchy tier's 443 are under 2 km. Under 3 km (30 units) are
## 263, and those are what pepper the Duchy tier's far end (81 in one view over the lake country),
## so that is the size here. 05's pale water made them far quieter than when 19 was proposed.
##
## For real: MapDetail.SHOWN_FROM as 19a and 19b with Forests/Woods to Tier.HAMLETS, and a third
## lake size in _gather_water() (lakes under it, and their islands, to Tier.COUNTY).
extends RefCounted

const NAME := "19 in full, small lakes at 3 km"
const LABEL := "19c"
const Now := preload("res://_probe/styles/190_disclosure_now.gd")


func apply(kit) -> void:
	var detail: Node = kit.as_revisited()
	detail.set("shown_from", kit.tiers_as_revisited({
		^"Borders/Counties": MapDetail.Tier.COUNTY,
		^"BordersOverLakes/Counties": MapDetail.Tier.COUNTY,
		^"Roads/Lanes": MapDetail.Tier.HAMLETS,
		^"Bridges/Lanes": MapDetail.Tier.HAMLETS,
		^"Forests/Woods": MapDetail.Tier.HAMLETS,
	}))
	detail.set("small_lake_across", 30.0)
	detail.set("small_lake_tier", MapDetail.Tier.COUNTY)


func panels(_kit) -> Array:
	return Now.VIEWS
