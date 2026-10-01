## How every figure on the combat map stands between actions: which way it
## faces, and whether it kneels behind low cover or braces against high. Only
## for show: nothing in the rules reads it, and a figure busy with anything
## (walking, aiming, swinging, falling) is left alone.
##
## A figure takes the cover beside it that faces its nearest foe, the way XCOM
## soldiers do: down on one knee behind low cover, up close to high cover. With
## nothing to hide behind on that side it stands in the open, turned to that
## foe, and keeps an eye on them as they move. Cover that is shot away stands
## it back up. Once no foe is left it stays as it was.
class_name Postures
extends Node

## Seconds between looks at where everyone is.
@export var interval := 0.2
## How squarely a side's cover has to face the nearest foe to be taken, as the
## cosine of the angle between them: 0.3 is anything within about 70 degrees.
@export var facing_enough := 0.3
@export var player_group := &"players"
@export var enemy_group := &"enemies"
@export var grid_path: NodePath = ^"../CombatGrid"

var _grid: CombatGrid
var _sight: LineOfSight
var _wait := 0.0
## True until the first look round, which turns everyone straight to where
## they face, so a battle does not open with the whole map turning round.
var _first := true


func _ready() -> void:
	_grid = get_node_or_null(grid_path) as CombatGrid
	if _grid == null:
		push_error("Postures: no CombatGrid at '%s'." % grid_path)
		set_process(false)
		return
	_sight = LineOfSight.new(_grid)


func _process(delta: float) -> void:
	_wait -= delta
	if _wait > 0.0:
		return
	_wait = interval
	var players := _living(player_group)
	var enemies := _living(enemy_group)
	for unit in players:
		_settle(unit, enemies)
	for unit in enemies:
		_settle(unit, players)
	_first = false


## Settles [param unit] for [param foes]: into the cover facing the nearest of
## them, or out in the open turned to them.
func _settle(unit: Unit, foes: Array[Unit]) -> void:
	var body := unit.model
	if body == null or not body.is_idle():
		return
	var nearest: Unit = null
	for foe in foes:
		if nearest == null or unit.global_position.distance_squared_to(foe.global_position) < unit.global_position.distance_squared_to(nearest.global_position):
			nearest = foe
	var tile := _grid.tile_at(unit.global_position)
	if nearest == null:
		body.settle(body.cover, body.rotation.y, null)
		return
	var toward := Vector2(nearest.global_position.x - unit.global_position.x, nearest.global_position.z - unit.global_position.z)
	if toward.is_zero_approx():
		return
	toward = toward.normalized()
	var best := LineOfSight.Cover.NONE
	var best_side := Vector2i.ZERO
	var best_facing := facing_enough
	var sides := _sight.cover_at(tile)
	for side: Vector2i in sides:
		var facing := Vector2(side).normalized().dot(toward)
		var cover: LineOfSight.Cover = sides[side]
		# The squarest side wins; between two as square, the higher cover.
		if facing > best_facing + 0.01 or (facing > best_facing - 0.01 and cover > best):
			best = cover
			best_side = side
			best_facing = facing
	var yaw := atan2(toward.x, toward.y)
	if best_side != Vector2i.ZERO:
		yaw = atan2(float(best_side.x), float(best_side.y))
	body.settle(best, yaw, unit.aim_point(nearest, _grid), _first)


func _living(group: StringName) -> Array[Unit]:
	var units: Array[Unit] = []
	for node in get_tree().get_nodes_in_group(group):
		var unit := node as Unit
		if unit != null and unit.health > 0:
			units.append(unit)
	return units
