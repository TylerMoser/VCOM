@tool
## The new map's navigation as baked from its layers ([MapNavigationBaker]):
## what [MapNavigation] loads and [MapRouter] finds routes over. Nothing in it
## is worked out as the game runs.
##
## It holds the map drawn into a grid of cells, each one kind of ground
## ([enum Ground]), kept a square block at a time, each block compressed on
## its own so that a route decodes only the blocks it passes through. And it
## holds the network a route is searched over: the entrances, cells where a
## route may pass from one block into the next, and the links between them,
## each the best path between two entrances of one block (or a single step
## across the edge between two blocks), with its cost and its cells.
##
## A cost is in cells of road: a step of one cell costs its length times
## each cell's weight, half of it the weight of the cell it leaves and half
## the weight of the cell it enters, a weight being how many times slower
## than a road that ground is ([method weights]). So it is the same both
## ways, and [member cell_size] and the road's speed turn it into time.
##
## The file is written whole by every bake and never by hand: see
## Docs/MAP.md, "Navigation".
class_name MapNavigationData
extends Resource

## What a cell is. The sea and the inland water (lakes, rivers, channels) are
## kept apart, each with a kind of its own for water the party may cross.
enum Ground { SEA, WATER, OPEN, FOREST, ROAD, NAVIGABLE_SEA, NAVIGABLE_WATER }

## The eight steps from a cell to its neighbours, by the codes in
## [member link_steps].
const STEPS: Array[Vector2i] = [
	Vector2i(1, 0), Vector2i(1, 1), Vector2i(0, 1), Vector2i(-1, 1),
	Vector2i(-1, 0), Vector2i(-1, -1), Vector2i(0, -1), Vector2i(1, -1),
]

## The version of [MapNavigationBaker] that made it: an older one is stale.
@export var version := 0
## A hash of everything the bake read (the layers, the speeds, the bake's own
## settings), to tell whether the map has changed since.
@export var signature := ""
## What the bake found, as it printed it.
@export_multiline var report := ""
## A cell's side, in the map's units.
@export var cell_size := 1.0
## Where in the map the corner of cell (0, 0) is.
@export var origin := Vector2.ZERO
## Cells across and down.
@export var size := Vector2i.ZERO
## A block's side, in cells.
@export var block_cells := 160
## Miles a day over each [enum Ground], as baked; 0 where the party cannot go.
@export var speeds := PackedFloat32Array()

## Every block's cells, row by row, a byte of [enum Ground] each, compressed
## with Zstandard: block [code]k[/code] is the bytes from
## [code]block_offsets[k][/code] to [code]block_offsets[k + 1][/code].
@export_storage var blocks := PackedByteArray()
@export_storage var block_offsets := PackedInt32Array()
## Each entrance's cell.
@export_storage var node_x := PackedInt32Array()
@export_storage var node_y := PackedInt32Array()
## The entrances in each block: those from [code]block_node_offsets[k][/code]
## to [code]block_node_offsets[k + 1][/code] of [member block_nodes].
@export_storage var block_node_offsets := PackedInt32Array()
@export_storage var block_nodes := PackedInt32Array()
## Each entrance's links: those from [code]link_offsets[n][/code] to
## [code]link_offsets[n + 1][/code], each to [member link_to] at
## [member link_cost], its cells the steps from
## [code]link_step_offsets[i][/code] to [code]link_step_offsets[i + 1][/code]
## of [member link_steps], taken from the entrance it leaves.
@export_storage var link_offsets := PackedInt32Array()
@export_storage var link_to := PackedInt32Array()
@export_storage var link_cost := PackedFloat32Array()
@export_storage var link_step_offsets := PackedInt32Array()
@export_storage var link_steps := PackedByteArray()


## Blocks across.
func blocks_across() -> int:
	return ceili(float(size.x) / block_cells)


## Blocks down.
func blocks_down() -> int:
	return ceili(float(size.y) / block_cells)


## The cells of block [param block]: a whole block, or less along the grid's
## right and bottom edges.
func block_rect(block: int) -> Rect2i:
	var across := blocks_across()
	@warning_ignore("integer_division")
	var corner := Vector2i(block % across, block / across) * block_cells
	return Rect2i(corner, Vector2i(mini(block_cells, size.x - corner.x), mini(block_cells, size.y - corner.y)))


## The block cell [param cell] is in, or -1 off the grid.
func block_of(cell: Vector2i) -> int:
	if cell.x < 0 or cell.y < 0 or cell.x >= size.x or cell.y >= size.y:
		return -1
	@warning_ignore("integer_division")
	return (cell.y / block_cells) * blocks_across() + cell.x / block_cells


## Block [param block]'s cells, row by row, a byte of [enum Ground] each.
func decode_block(block: int) -> PackedByteArray:
	var rect := block_rect(block)
	var packed := blocks.slice(block_offsets[block], block_offsets[block + 1])
	return packed.decompress(rect.size.x * rect.size.y, FileAccess.COMPRESSION_ZSTD)


## How many times slower than the fastest ground each [enum Ground] is, from
## [param miles_per_day] by ground: 0 where the party cannot go. The fastest,
## the road, is 1, so that no step costs less than its length and the search's
## estimate of what is left never says too much.
static func weights_of(miles_per_day: PackedFloat32Array) -> PackedFloat32Array:
	var fastest := 0.0
	for speed in miles_per_day:
		fastest = maxf(fastest, speed)
	var out := PackedFloat32Array()
	out.resize(miles_per_day.size())
	for ground in miles_per_day.size():
		out[ground] = fastest / miles_per_day[ground] if miles_per_day[ground] > 0.0 else 0.0
	return out


## [method weights_of] the speeds this was baked with.
func weights() -> PackedFloat32Array:
	return weights_of(speeds)


## The code of the step from a cell to its neighbour [param offset] away.
static func step_code(offset: Vector2i) -> int:
	return STEPS.find(offset)


## A grid that searches one block at a time: eight ways, a diagonal step only
## past two open cells, so that a river drawn as a line of cells touching only
## at their corners still stops it.
static func new_block_grid() -> AStarGrid2D:
	var grid := AStarGrid2D.new()
	grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	grid.default_compute_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	grid.default_estimate_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	return grid


## Sets [param grid] to the cells of [param rect], whose grounds are
## [param cells] row by row: the ones the party cannot cross solid, the rest
## weighted by [param weights]. One call a run of one ground along a row.
static func fill_block_grid(grid: AStarGrid2D, rect: Rect2i, cells: PackedByteArray,
		weights: PackedFloat32Array) -> void:
	grid.region = rect
	grid.update()
	var width := rect.size.x
	for row in rect.size.y:
		var start := row * width
		var x := 0
		while x < width:
			var ground := cells[start + x]
			var run := 1
			while x + run < width and cells[start + x + run] == ground:
				run += 1
			var weight := weights[ground]
			var span := Rect2i(rect.position.x + x, rect.position.y + row, run, 1)
			if weight <= 0.0:
				grid.fill_solid_region(span, true)
			elif weight != 1.0:
				grid.fill_weight_scale_region(span, weight)
			x += run
