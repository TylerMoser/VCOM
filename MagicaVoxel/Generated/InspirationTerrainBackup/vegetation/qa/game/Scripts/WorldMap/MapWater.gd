@tool
## Water on the new map ([code]Scenes/Map.tscn[/code]): the sea, a lake, a
## river or one of the Swamp's channels, on the polygon or line that draws it.
## It only says whether the party may cross it; how it looks is its node's own.
##
## [MapNavigation] bakes the water into the map's navigation, where it stops
## the party, which crosses it only by a bridge, unless it is
## [member navigable]. Every water node has this script (it extends Node2D,
## so it goes on a [Polygon2D] or a [Line2D] alike), and duplicating one to
## draw new water keeps it. Water drawn afresh without it blocks all the same,
## and the bake's report names it; it needs the script to be made navigable.
## An island in a lake (a polygon under Lakes with "Island" in its name) is
## land, and has none.
class_name MapWater
extends Node2D

## Whether the party may cross this water, at a forest's pace
## ([constant MapNavigation.NAVIGABLE_MILES_PER_DAY]). Off, as all the water is
## for now, it stops the party. Bake the navigation again after changing it.
@export var navigable := false
