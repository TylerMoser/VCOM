## 19, revisited · The map as it was when 19 was revisited (commit c2e885c; 19a has been applied
## since, and kit.as_revisited() takes it back out), at the views 19's variants are pictured at:
## the Duchy tier at 180 miles, as the standard view B, and at 110 miles over the lake country in
## the north-west, where the most lakes under 3 km across are in one view (81); the County tier at
## 80 miles, as the standard view C, and at 60 miles over the same place, above the hamlets' step.
## All the way out and all the way in nothing of 19's changes, so neither is pictured. Its
## variants move groups between tiers with kit.tiers_as_revisited().
extends RefCounted

const NAME := "The map as it is now"
const LABEL := "19 now"
const VIEWS := [
	["B", "Duchy tier: 180 miles tall", Vector2(7302, 7381), 180.0],
	["L", "Duchy tier: 110 miles tall, the lake country", Vector2(3450, 3750), 110.0],
	["C", "County tier: 80 miles tall", Vector2(6150, 8500), 80.0],
	["E", "County tier: 60 miles tall", Vector2(6150, 8500), 60.0],
]


func apply(kit) -> void:
	kit.as_revisited()


func panels(_kit) -> Array:
	return VIEWS
