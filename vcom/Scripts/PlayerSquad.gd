## The player-controlled units, and which one is currently selected.
##
## In a combat map the squad is the roster's: on entering the map it puts a
## [member unit_scene] on the tile under each [SquadStart] for each character
## [method Campaign.squad] sends, the first at the first marker, and gives it
## that character. The characters are the roster's own resources, so what
## happens to a unit happens to them: every hit is written on its character's
## [member Character.wounds], a grenade it throws comes off its character's
## gear for good ([method Campaign.use_up]), and a member who dies is taken
## off the roster ([method Campaign.lose]). Units the scene places in [member unit_group]
## itself (the test harness's, which have no character) join the squad as
## they are, ahead of the spawned ones.
##
##   Select - Tab / Shift+Tab to cycle, or left-click a unit on the map.
class_name PlayerSquad
extends Node

signal selection_changed(unit: Unit)

## Group whose units make up the squad, in scene-tree order.
@export var unit_group := &"players"
## The [SquadStart] markers' parent. Leave empty to spawn nobody, so the squad
## is only the units the scene places in [member unit_group].
@export var starts_path: NodePath
## What each spawned member is: a [Unit] scene whose root is in
## [member unit_group].
@export var unit_scene: PackedScene
## Where spawned members go in the tree.
@export var units_path: NodePath = ^"../Units"
## Finds the tile under each marker.
@export var grid_path: NodePath = ^"../CombatGrid"
## Experience each member still standing earns as a battle ends
## ([method award_survivors]).
@export var survival_experience := 50

var members: Array[Unit] = []
var selected: Unit
## While true, the selection cannot change. Set while an action plays out.
var locked := false


func _ready() -> void:
	if not starts_path.is_empty():
		_spawn()
	for node in get_tree().get_nodes_in_group(unit_group):
		var unit := node as Unit
		if unit == null:
			push_warning("PlayerSquad: '%s' is in '%s' but is not a Unit." % [node.name, unit_group])
			continue
		members.append(unit)
		unit.died.connect(_on_member_died.bind(unit))
		if unit.character != null:
			unit.health_changed.connect(_on_member_hurt.bind(unit))
			unit.used_up.connect(_on_member_used_up.bind(unit))

	if not members.is_empty():
		select(members[0])


func _unhandled_input(event: InputEvent) -> void:
	if locked:
		return
	# Shift+Tab also matches the plain Tab action, so check it first.
	if event.is_action_pressed(&"select_previous_unit"):
		cycle(-1)
	elif event.is_action_pressed(&"select_next_unit"):
		cycle(1)
	elif event.is_action_pressed(&"select_unit") and event is InputEventMouseButton:
		var unit := unit_at((event as InputEventMouseButton).position)
		# A click on anything else is left for other handlers.
		if unit not in members:
			return
		select(unit)
	else:
		return
	get_viewport().set_input_as_handled()


## Makes [param unit] the selected unit. Units outside the squad are ignored.
func select(unit: Unit) -> void:
	if locked or unit == selected or unit not in members:
		return
	selected = unit
	selection_changed.emit(selected)


## Drops a fallen member, and their character from the roster, and if it was
## the one selected, hands the selection to whoever took its place in the
## line-up.
func _on_member_died(unit: Unit) -> void:
	if unit.character != null:
		Campaign.lose(unit.character)
	var index := members.find(unit)
	if index < 0:
		return
	members.remove_at(index)
	if selected != unit:
		return
	# The lock stops the player switching units mid-action, and this is not
	# the player switching: the selection has nowhere to stay.
	selected = members[index % members.size()] if not members.is_empty() else null
	selection_changed.emit(selected)


## Puts a unit on the map for each character fighting this battle, one per
## [SquadStart] in order, standing on the tile the marker is over. More
## markers than characters leaves the last ones empty; the squad is never
## more than there are markers.
func _spawn() -> void:
	var starts := get_node_or_null(starts_path)
	var units := get_node_or_null(units_path) as Node3D
	var grid := get_node_or_null(grid_path) as CombatGrid
	if starts == null or units == null or grid == null or unit_scene == null:
		push_error("PlayerSquad: cannot spawn the squad without SquadStarts, a Units Node3D, a CombatGrid and a unit_scene.")
		return
	var markers: Array[SquadStart] = []
	for child in starts.get_children():
		if child is SquadStart:
			markers.append(child)
	var characters := Campaign.squad(markers.size())
	for i in characters.size():
		var tile := grid.tile_at(markers[i].global_position)
		if not grid.is_tile(tile):
			push_warning("PlayerSquad: '%s' is not over a tile anyone can stand on." % markers[i].name)
		var node := unit_scene.instantiate()
		var unit := node as Unit
		if unit == null:
			push_error("PlayerSquad: unit_scene is not a Unit.")
			node.free()
			return
		# Given before it enters the tree, where it takes on the character.
		unit.character = characters[i]
		var name_from := characters[i].display_name.validate_node_name()
		unit.name = name_from if not name_from.is_empty() else "SquadMember"
		unit.position = units.to_local(grid.tile_position(tile))
		units.add_child(unit, true)


## Gives every member still standing [member survival_experience], on their
## character. The [TurnManager] calls it as the battle is decided; after a
## defeat there is nobody left to earn it.
func award_survivors() -> void:
	for unit in members:
		if unit.character != null:
			unit.character.gain_experience(survival_experience)


## Writes what [param unit] has lost on its character, as soon as it is hit.
func _on_member_hurt(health: int, max_health: int, unit: Unit) -> void:
	unit.character.wounds = max_health - health


## Takes what [param unit] used up, such as a grenade it threw, off its
## character for good, as soon as it is used.
func _on_member_used_up(item: Item, unit: Unit) -> void:
	Campaign.use_up(unit.character, item)


## Moves the selection [param step] places through the squad, wrapping around.
func cycle(step: int) -> void:
	if members.is_empty():
		return
	var index := members.find(selected)
	select(members[posmod(index + step, members.size())])


## The unit whose pick body is under [param screen_position], if any.
func unit_at(screen_position: Vector2) -> Unit:
	var camera := get_viewport().get_camera_3d()
	if camera == null:
		return null

	var from := camera.project_ray_origin(screen_position)
	var to := from + camera.project_ray_normal(screen_position) * camera.far
	var query := PhysicsRayQueryParameters3D.create(from, to, Unit.PICK_LAYER)
	var hit := get_viewport().find_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return null
	return (hit.collider as Node).get_parent() as Unit
