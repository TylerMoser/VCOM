## 12b · Whisper. 12's hues at 40% of their strength, the forests as the map has them now: the biome
## is a hint under everything, felt more than seen. The cheapest change to the map's look that still
## says "desert here, tundra there", and the one least likely to cost a line its contrast.
extends RefCounted

const NAME := "Whisper"
const LABEL := "12b"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {"strength": 0.4})


func panels(_kit) -> Array:
	return Now.VIEWS
