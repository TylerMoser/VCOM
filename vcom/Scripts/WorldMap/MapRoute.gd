@tool
## A way for the party across the new map, as [MapNavigation] finds it: the
## points it heads for in turn, the destination last, and its pace on the leg
## to each. A leg is all one kind of ground, or near enough (see
## [constant MapRouter.SHORTEST_LEG]), so the party slows going into a forest
## and speeds up again on the road out of it.
class_name MapRoute
extends RefCounted

## The points the party heads for in turn, the destination last; not where it
## sets off from.
var points := PackedVector2Array()
## Miles a day on the leg to each point of [member points], the same length.
var miles_per_day := PackedFloat32Array()
## Days of the game the whole way takes.
var days := 0.0
