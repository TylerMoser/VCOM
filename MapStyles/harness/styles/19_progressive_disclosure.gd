## 19 · Progressive disclosure. Each layer waits a tier longer before it comes
## in, so every view carries less: the county borders wait for the County tier
## (100 miles) instead of the Duchy tier, the lanes, their bridges and the
## smallest woods for the hamlets' step (50 miles), and lakes under 2 km across
## for the County tier. Google Maps does the same, showing a road or a
## boundary only once there is room for it. The Duchy tier, the busiest view
## today, loses its 300 county borders and its peppering of small lakes; the
## County tier its lanes until the view is close enough to tell them from roads.
##
## For real: MapDetail.SHOWN_FROM, and a size for lakes (ProgressiveDetail.gd
## shows both). The map's look is untouched.
extends RefCounted

const NAME := "Progressive disclosure"


func apply(kit) -> void:
	var detail: Node = kit.at("Detail")
	detail.set_script(kit.runtime("ProgressiveDetail.gd"))
