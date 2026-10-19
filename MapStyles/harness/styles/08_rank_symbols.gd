## 08 · Symbols far out, pictures close in. From all the way out to the
## County tier's second step (50 miles), a settlement is a small map symbol by
## its rank: a kingdom's capital a ringed dot, a duchy's a square, a town a
## dot, a village a ring, a hamlet a small dot. Closer in it becomes the pack's
## picture, where there is room to enjoy it. Some 300 drawings of houses at
## the far end of the County tier become 300 dots, and the lines between them
## can be seen again.
extends RefCounted

const NAME := "Symbols far out, pictures close in"
const Symbols := preload("res://_probe/runtime/Symbols.gd")
## Pictures from this view height in, symbols beyond.
const PICTURES_UNDER_MILES := 50.0

var _pictures := {}
var _symbols := {}


func ready(kit) -> void:
	var ink := Color("#2a2a2e")
	var halo := Color(1, 1, 1, 0.95)
	for group: String in Symbols.FOR_GROUP:
		var look: Array = Symbols.FOR_GROUP[group]
		_symbols[group] = [Symbols.texture(look[0], ink, halo), look[1]]
	for place: Node2D in kit.settlements():
		_pictures[place] = [place.get("icon"), place.get("icon_height")]


func before_panel(_kit, _index: int, view: Array) -> void:
	var miles: float = view[3]
	var far := miles <= 0.0 or miles >= PICTURES_UNDER_MILES
	for place: Node2D in _pictures:
		var group := str(place.get_parent().name)
		if far:
			place.set("icon", _symbols[group][0])
			place.set("icon_height", _symbols[group][1])
		else:
			place.set("icon", _pictures[place][0])
			place.set("icon_height", _pictures[place][1])
