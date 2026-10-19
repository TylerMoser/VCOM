## 09 · Route planner. The party and where it is going become the loudest
## thing on the map, in a colour nothing else uses: a blue "you are here" dot
## with a halo, the route over a white casing, red where it runs through forest
## (where battles are met) and blue where it does not, a tick at each day's
## travel, and a pin at the end saying how many days the trip takes and its
## chance of a battle, worked out from the steps that end in forest. A dashed
## ring shows what two days' travel reaches. The two questions the clock and
## the forests ask of every trip, how long and how dangerous, are answered on
## the map before the party sets off.
extends RefCounted

const NAME := "Route planner"

## Where the party is sent in this style's pictures: west from its start, over
## the Temperate Mountains' forests.
const DESTINATION := Vector2(6420.0, 7020.0)


func ready(kit) -> void:
	var overlay: Node2D = kit.runtime("RouteOverlay.gd").new()
	overlay.name = "RouteOverlay"
	overlay.party = kit.at("Party")
	overlay.route = PackedVector2Array([Vector2(6900.0, 7230.0), DESTINATION])
	overlay.reach_days = 2.0
	kit.map.add_child(overlay)
