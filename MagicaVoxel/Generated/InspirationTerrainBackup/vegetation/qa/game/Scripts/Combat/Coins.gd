## The coins lying about the battlefield, for the squad to pick up.
##
## A block may leave a coin as it breaks: each time one does, its
## [member Destruction.coin_chance] is rolled
## ([signal TerrainDestruction.block_broken]). The coin floats at the top of
## the cell the block broke in, where it stood or where it landed after a fall,
## and is on that tile, as a unit standing there would be. Several on one tile
## stack up, each [constant STACK_STEP] over the one below. When the ground
## under a tile goes, its coins drop to the tile below, as a unit there would.
##
## A squad member takes every coin on each tile it passes through, however it
## gets there: along a move's path, stepping out to shoot, or dropping as the
## ground gives way. Each coin is [member value] gold into
## [member Campaign.gold] at once, kept whatever comes of the battle, and what
## they came to is called over the member's head. Enemies pass coins by.
##
## Once the battle is won the [TurnManager] calls [method sweep], which pays the
## party for every coin left on the map, and for any coin a block still falling
## leaves after.
##
## Like the rules for units, these go by tiles: a [Coin] is only for show, and
## nothing waits for it.
class_name Coins
extends Node3D

## How far apart, in cells, the coins stacked on one tile float: more than a
## coin's height (0.567, nine voxels) and its bob up and down, so they never
## touch.
const STACK_STEP := 0.7

## Gold a coin is worth.
@export var value := 1
@export var player_group := &"players"

@export_group("Nodes")
@export var grid_path: NodePath = ^"../CombatGrid"
@export var destruction_path: NodePath = ^"../TerrainDestruction"
@export var overlay_path: NodePath = ^"../HUD/ShotOverlay"

var _grid: CombatGrid
var _overlay: ShotOverlay
## Tile -> the coins on it, bottom first.
var _piles := {}
## Set once the battle is won and every coin on the map paid for: a coin left
## after that is paid for the moment it appears.
var _swept := false


func _ready() -> void:
	_grid = get_node_or_null(grid_path) as CombatGrid
	var destruction := get_node_or_null(destruction_path) as TerrainDestruction
	if _grid == null or destruction == null:
		push_error("Coins: missing CombatGrid or TerrainDestruction, so no coins.")
		set_process(false)
		return
	# Only to call what a pickup came to, so a scene without one still pays.
	_overlay = get_node_or_null(overlay_path) as ShotOverlay
	if _overlay == null:
		push_error("Coins: no ShotOverlay at '%s'." % overlay_path)
	destruction.block_broken.connect(_on_block_broken)


# Every frame, not now and then: a squad member crosses a tile in a fifth of a
# second, and a coin it passed over must not be missed.
func _process(_delta: float) -> void:
	_drop_stranded()
	for node in get_tree().get_nodes_in_group(player_group):
		var unit := node as Unit
		if unit == null or unit.health <= 0:
			continue
		var tile := _grid.tile_at(unit.global_position)
		if _piles.has(tile):
			_pay(tile, _grid.cell_center(LineOfSight.eye_cell(tile)))


## How many coins are lying on the map.
func count() -> int:
	var coins := 0
	for pile: Array in _piles.values():
		coins += pile.size()
	return coins


## Pays the party for every coin left on the map, calling what each tile's came
## to over it, as the battle is won. From then on a coin is paid for as it
## appears.
func sweep() -> void:
	_swept = true
	for tile: Vector3i in _piles.keys():
		_pay(tile, _rest_point(tile, 0))


func _on_block_broken(cell: Vector3i, destruction: Destruction) -> void:
	if randf() >= destruction.coin_chance:
		return
	if _swept:
		_pay_for(1, _rest_point(cell, 0))
		return
	var pile: Array = _piles.get_or_add(cell, [])
	var coin := Coin.new()
	add_child(coin)
	coin.global_position = _rest_point(cell, pile.size())
	pile.append(coin)


## Drops the coins on any tile whose ground has gone to the tile below, on top
## of any already there. Coins with no ground anywhere below stay where they
## are.
func _drop_stranded() -> void:
	for tile: Vector3i in _piles.keys():
		if _grid.is_solid(tile + Vector3i.DOWN):
			continue
		var landing: Variant = _grid.tile_under(tile)
		if landing == null:
			continue
		var below: Array = _piles.get_or_add(landing, [])
		for coin: Coin in _piles[tile]:
			coin.drop_to(_rest_point(landing, below.size()))
			below.append(coin)
		_piles.erase(tile)


## Takes every coin on [param tile] and pays the party for them, calling what
## they came to at [param over].
func _pay(tile: Vector3i, over: Vector3) -> void:
	var pile: Array = _piles[tile]
	_piles.erase(tile)
	for coin: Coin in pile:
		coin.take()
	_pay_for(pile.size(), over)


## Pays the party for [param coins] coins, calling the gold over [param over].
func _pay_for(coins: int, over: Vector3) -> void:
	var gold := coins * value
	Campaign.gold += gold
	if _overlay != null:
		_overlay.flash_pickup(over, "+%d Gold" % gold)


## Where the coin [param index] up the pile on [param tile] rests: the first at
## the top of the tile's cell, each after it [constant STACK_STEP] higher.
func _rest_point(tile: Vector3i, index: int) -> Vector3:
	var middle := _grid.cell_center(tile)
	var top := middle + (middle - _grid.tile_position(tile))
	return top + Vector3.UP * STACK_STEP * index
