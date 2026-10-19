## 06 · Coast with water lines. The heaviest line on the map, the coast's 23
## black units, becomes a fine dark shoreline with three faint rings of water
## lines off it, each fainter than the last: the old engravers' way of framing
## land (and the hand-drawn regions sketch's, MapCreation/WorldMapRegions.png).
## It all comes from the coast's own lines, drawn by map_line.gdshader's coast
## mode: no new nodes. The rings show only once the view is close enough for
## them to stand a few pixels apart.
extends RefCounted

const NAME := "Coast with water lines"

## The coast's line as a share of the scene's width: wider, for the rings' room.
const COAST_SHARE := 2.2


func apply(kit) -> void:
	kit.style_coast({
		"shore": kit.hex("#29425c"), "shore_share": 0.16,
		"ring": kit.hex("#47739b", 0.6), "rings": 3, "ring_share": 0.08, "ring_min_px": 2.5,
	}, COAST_SHARE)


func ready(kit) -> void:
	# Ends of borders and rivers kept inside the shoreline.
	kit.trim_sea_ends(0.7)


## The standard views show little coast close in: the Swamp's fjords instead.
func panels(_kit) -> Array:
	return [
		["A", "Realm: all the way out", null, 0.0],
		["B", "Duchy tier: 180 miles tall", Vector2(7302, 7381), 180.0],
		["C", "County tier: 80 miles tall, the Swamp's fjords", Vector2(2750, 7500), 80.0],
		["D", "Closest: 30 miles tall, the Swamp's fjords", Vector2(2600, 7700), 30.0],
	]
