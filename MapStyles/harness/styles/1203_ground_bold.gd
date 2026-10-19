## 12c · Bold atlas. The same hues as 12, about twice as strong, as a school atlas's biome map: the
## realm reads as nine countries at a glance, all the way out. The forests a shade deeper again, so
## they keep their edge on a ground this strong.
extends RefCounted

const NAME := "Bold atlas"
const LABEL := "12c"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {}, Now.BOLD)
	Now.forests(kit, Now.FORESTS_BOLD)


func panels(_kit) -> Array:
	return Now.VIEWS
