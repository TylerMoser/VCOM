## A forest on a world map: an area where the party may be set upon as it
## travels.
##
## Its outline is the [member Polygon2D.polygon], moved and reshaped in the
## editor, and drawn as a see-through fill. The [Party] rolls
## [member encounter_chance] each step it ends inside it, and on a success
## the game goes to a battle on [member encounter_map].
##
## On the old map (WorldMap.tscn) it is a shape drawn by hand, an instance of
## Scenes/Forest.tscn, light green. On the new map (Scenes/Map.tscn) the
## forests were made by program (MapCreation/Scripts/forests/) and cut into
## some 2,500 pieces, by county and by kind, each an instance of its kind's
## scene (ConiferForest.tscn, BroadleafForest.tscn, TropicalForest.tscn,
## SwampForest.tscn), which inherits Forest.tscn's odds and sets only its
## colour. A Polygon2D draws no holes, so a clearing in a piece is joined to
## its outline by a cut of no width, there and back: the outline goes round
## the clearing, and a point in the clearing is outside it.
##
## Whether a point is inside is left to [method Geometry2D.is_point_in_polygon],
## unlike the land (see [WorldMapTerrain]): that misjudges points almost on a
## corner, which on the coast's tens of thousands of corners added up, but on
## a forest's few hundred at the most only ever puts a point a hair from an
## edge on the other side of it.
class_name Forest
extends Polygon2D

const GROUP := &"forests"

## The chance, in 100, that a step the party ends in this forest starts a
## random encounter. How long a step is is the party's
## [member Party.step_length].
@export_range(0.0, 100.0, 0.1, "suffix:%") var encounter_chance := 10.0
## The battle fought when one starts.
@export var encounter_map: PackedScene


func _enter_tree() -> void:
	# Joined on entering, as destinations are, so the party finds every
	# forest wherever it sits in the tree.
	add_to_group(GROUP)


func _ready() -> void:
	if encounter_map == null and encounter_chance > 0.0:
		push_warning("Forest '%s': no encounter_map, so nothing is ever met in it." % name)


## Whether [param point], in global map coordinates, is inside the forest.
func encloses(point: Vector2) -> bool:
	if polygon.size() < 3:
		return false
	return Geometry2D.is_point_in_polygon(to_local(point) - offset, polygon)


## Rolls [member encounter_chance] for one step: true when an encounter
## starts. Never with no [member encounter_map] to fight it on.
func roll_encounter() -> bool:
	return encounter_map != null and randf() * 100.0 < encounter_chance


## The forest that [param point] is in, or null when it is in none. Where
## forests overlap, the one drawn on top. Every forest is tried, which on the
## new map's 2,459 pieces takes 4 to 5 ms: the party asks once a step.
static func find_at(tree: SceneTree, point: Vector2) -> Forest:
	var found: Forest = null
	for node in tree.get_nodes_in_group(GROUP):
		var forest := node as Forest
		if forest != null and forest.encloses(point):
			found = forest
	return found
