## What a computer-controlled unit can find out about the fight, for an
## [EnemyAI] to choose its next action with: who it is up against, which of
## them are next to it, the shots it has and their odds, and the way to the
## nearest of them.
##
## These are the building blocks every kind of enemy shares. Where a query is
## really a candidate action it answers with a ready-made [AIAction], so an AI
## reads as a list of priorities. A new one is made for every decision, so it
## always sees the board as it stands.
class_name Tactics
extends RefCounted

## How many steps a search for the way to a foe looks ahead: enough to cross
## any map.
const SEARCH_STEPS := 200

## The unit deciding.
var unit: Unit
## The living units it is fighting.
var foes: Array[Unit] = []

var _grid: CombatGrid
var _line_of_sight: LineOfSight
var _tile: Vector3i
## Everywhere the unit can walk, found the first time it is needed.
var _reach: CombatGrid.Reach


func _init(deciding: Unit, grid: CombatGrid, against: Array[Unit]) -> void:
	unit = deciding
	_grid = grid
	_line_of_sight = LineOfSight.new(grid)
	_tile = grid.tile_at(deciding.global_position)
	for foe in against:
		if is_instance_valid(foe) and foe.health > 0:
			foes.append(foe)


## Whether units on [param a] and [param b] stand next to each other: one tile
## apart across the ground in any of the eight directions, and no more than a
## level up or down.
static func is_next_to(a: Vector3i, b: Vector3i) -> bool:
	var across := maxi(absi(a.x - b.x), absi(a.z - b.z))
	return across == 1 and absi(a.y - b.y) <= 1


## The foes standing next to the unit.
func adjacent_foes() -> Array[Unit]:
	var adjacent: Array[Unit] = []
	for foe in foes:
		if is_next_to(_tile, _grid.tile_at(foe.global_position)):
			adjacent.append(foe)
	return adjacent


## Every shot the unit has at [param targets], each as an action with its
## odds, nearest target first.
func shots_at(targets: Array[Unit]) -> Array[AIAction]:
	var shots: Array[AIAction] = []
	for shot in _line_of_sight.find_shots(unit, targets):
		shots.append(AIAction.shoot(shot, HitChance.for_shot(unit, shot)))
	return shots


## The shot with the best odds at any of [param targets], or null if the unit
## cannot see any of them. Even odds go to the nearer target.
func best_shot(targets: Array[Unit]) -> Variant:
	var best: AIAction = null
	for option in shots_at(targets):
		if best == null or option.estimate.chance > best.estimate.chance:
			best = option
	return best


## A move of up to [param max_steps] tiles along the shortest way to the
## nearest foe, stopping next to them if they are that close. If no foe can
## be walked to at all, it gets as near to one as the ground allows. Null if
## the unit cannot get any closer.
func advance(max_steps: int) -> Variant:
	var path := path_to_nearest_foe()
	if path.is_empty() and adjacent_foes().is_empty():
		path = _path_closer_as_the_crow_flies(max_steps)
	if path.is_empty():
		return null
	return AIAction.move(path.slice(0, max_steps))


## The shortest walk to a tile next to the nearest foe, nearest counted in
## steps rather than as the crow flies. Empty if the unit is already next to
## a foe, or cannot walk to any of them.
func path_to_nearest_foe() -> Array[Vector3i]:
	var reach := _reachable()
	var goal: Variant = null
	for foe in foes:
		for tile in _tiles_next_to(_grid.tile_at(foe.global_position)):
			if not reach.steps.has(tile):
				continue
			if goal == null or reach.steps[tile] < reach.steps[goal]:
				goal = tile
	if goal == null:
		return []
	return reach.path_to(goal)


## The walk, of at most [param max_steps] tiles, to wherever is nearest a foe
## as the crow flies. For when no foe can be walked to. Empty if nowhere in
## reach is any nearer than where the unit stands.
func _path_closer_as_the_crow_flies(max_steps: int) -> Array[Vector3i]:
	var reach := _reachable()
	var best := _tile
	var best_distance := _distance_to_nearest_foe(_tile)
	for tile: Vector3i in reach.steps:
		if reach.steps[tile] > max_steps:
			continue
		var distance := _distance_to_nearest_foe(tile)
		if distance < best_distance:
			best = tile
			best_distance = distance
	return reach.path_to(best)


func _distance_to_nearest_foe(tile: Vector3i) -> float:
	var nearest := INF
	for foe in foes:
		var foe_tile := _grid.tile_at(foe.global_position)
		nearest = minf(nearest, Vector2(tile.x - foe_tile.x, tile.z - foe_tile.z).length())
	return nearest


## Everywhere the unit can walk to, around the other units in the way.
func _reachable() -> CombatGrid.Reach:
	if _reach == null:
		_reach = _grid.find_reachable(_tile, SEARCH_STEPS, _grid.occupied_tiles(unit))
	return _reach


## The tiles a unit would be next to one on [param center] from, whether or
## not anyone can stand there.
static func _tiles_next_to(center: Vector3i) -> Array[Vector3i]:
	var tiles: Array[Vector3i] = []
	for dx in [-1, 0, 1]:
		for dz in [-1, 0, 1]:
			if dx == 0 and dz == 0:
				continue
			for dy in [-1, 0, 1]:
				tiles.append(center + Vector3i(dx, dy, dz))
	return tiles
