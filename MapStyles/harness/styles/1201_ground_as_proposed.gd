## 12a · As proposed, on today's look. Proposal 12 as it was pictured (12_biome_ground.gd), on the map
## as it now is: each kingdom's open land a pale ground in its biome's colour, flat, meeting its
## neighbour's exactly on the kingdoms' border; the forests a shade deeper and more solid than the
## map's 0.38, so they still stand out on a ground that is no longer white.
extends RefCounted

const NAME := "As proposed, on today's look"
const LABEL := "12a"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit)
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
