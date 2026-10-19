## MapDetail with each layer brought in a tier later than the scene's, for
## proposal 19: what a tier brings, and the lakes by their size, from tables of
## its own. Everything else is MapDetail's. Swapped onto the map's Detail node
## before the map enters the tree.
##
## For real, these are MapDetail.SHOWN_FROM and two more sizes in
## _gather_water(); no new code.
extends MapDetail

## What comes in with each tier. Against the scene's: the county borders wait
## for the County tier (100 miles), the lanes, their bridges and the woods for
## the hamlets' step (50 miles); the lesser roads and bridges stay at the
## Duchy tier, the villages at the County tier.
const LATER_SHOWN_FROM := {
	Tier.KINGDOM: [
		^"Borders/Duchies", ^"BordersOverLakes/Duchies", ^"Roads/Highways", ^"Settlements/DuchyCapitals",
		^"Forests/Large",
	],
	Tier.DUCHY: [^"Roads/Roads", ^"Bridges", ^"Settlements/CountyCapitals", ^"Forests/Small"],
	Tier.COUNTY: [^"Borders/Counties", ^"BordersOverLakes/Counties", ^"Settlements/Villages", ^"Channels"],
	Tier.HAMLETS: [^"Settlements/Hamlets", ^"Roads/Lanes", ^"Bridges/Lanes", ^"Forests/Woods"],
}
## A lake under this many units across (2 km) waits for the County tier.
const SMALL_LAKE := 20.0


func _gather_groups() -> void:
	for tier: int in LATER_SHOWN_FROM:
		for path: NodePath in LATER_SHOWN_FROM[tier]:
			var group := _map.get_node_or_null(path) as CanvasItem
			if group == null:
				push_error("ProgressiveDetail: nothing at '%s' under the map." % path)
				continue
			var drawn := not group.find_children("*", "Line2D", true, false).is_empty() \
					or not group.find_children("*", "Polygon2D", true, false).is_empty()
			_bring(group, tier, not drawn)


func _gather_water() -> void:
	super()
	# The smallest lakes, which MapDetail brings with the Duchy tier, wait.
	var lakes := _map.get_node_or_null(LAKES)
	for child in lakes.get_children():
		var lake := child as Polygon2D
		if lake == null or str(lake.name).contains(ISLAND):
			continue
		if _tier_of.get(lake, -1) == Tier.DUCHY and _across(lake) < SMALL_LAKE:
			_brings[Tier.DUCHY].erase(lake)
			_bring(lake, Tier.COUNTY, false)
