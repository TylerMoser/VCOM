## 05 · One water. The sea, the lakes, the rivers and the Swamp's channels in
## one family of light blue, as on Google Maps, where the scene has a pale sea
## and lakes three times darker. Rivers are a shade deeper than standing water,
## so the thinnest stay visible. The black coast becomes a thin darker-blue
## shoreline: the land's edge is the change from land to water, and needs no
## line of its own.
extends RefCounted

const NAME := "One water"

const WATER := "#a6d2f1"
const RIVER := "#78b6e6"
const SHORE := "#6f9fca"
## The coast's line as a share of the scene's (23 units outside the land), and
## the shoreline's share of that.
const COAST_SHARE := 0.35
const SHORE_SHARE := 0.5


func apply(kit) -> void:
	var water: Color = kit.hex(WATER)
	kit.set_sea(water)
	for lake in kit.lakes():
		lake.color = water
	kit.color_lines("Rivers", kit.hex(RIVER))
	kit.color_lines("Channels", kit.hex(RIVER))
	kit.style_coast({"shore": kit.hex(SHORE), "shore_share": SHORE_SHARE, "rings": 0}, COAST_SHARE)


func ready(kit) -> void:
	# The borders that run out into the coast's line end inside the narrower one.
	kit.trim_sea_ends(COAST_SHARE * SHORE_SHARE * 0.9)
