## 14, revisited · The map as it was when 14 was revisited (commit c2e885c; 14b has been applied
## since, and kit.as_revisited() takes it back out), at the views 14's variants are pictured at:
## all the way out and the Kingdom tier, where 14 makes the borders heavier, and the standard
## views' County tier and closest, where it makes them lighter. The Duchy tier's 180 miles is left
## out: it is near the 220 miles at which 14 changes nothing.
extends RefCounted

const NAME := "The map as it is now"
const LABEL := "14 now"
const VIEWS := [
	["A", "Realm: all the way out", null, 0.0],
	["K", "Kingdom tier: 400 miles tall", Vector2(7302, 7381), 400.0],
	["C", "County tier: 80 miles tall", Vector2(6150, 8500), 80.0],
	["D", "Closest: 30 miles tall", Vector2(7302, 7381), 30.0],
]


func apply(kit) -> void:
	kit.as_revisited()


func panels(_kit) -> Array:
	return VIEWS
