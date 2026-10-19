## 03 · Kingdom edge bands. A kingdom's border is a thin dark line with a soft
## band of the kingdom's own colour on its side, fading inward, as Paradox's
## strategy maps and hand-tinted atlases draw realms. Which kingdom a place is
## in reads at a glance at any zoom, without colouring whole kingdoms or
## drawing a heavy line. The duchy and county borders are 01's quiet lines.
##
## The band is the land's own shader (land.gdshader): each county is coloured
## by its kingdom, and shows that colour only within band_px screen pixels of a
## kingdom border, read from a distance field made from KingdomMap.png
## (harness/data/kingdom_edge.png), fading to the land's white beyond.
extends RefCounted

const NAME := "Kingdom edge bands"

const KINGDOM := {
	1: "#6f86c7", 2: "#c76f8e", 3: "#b8962e", 4: "#d9824a", 5: "#8f6fc7",
	6: "#3f9a9c", 7: "#8f8c3f", 8: "#c75a50", 9: "#4f9e5c",
}
const QUIET := preload("res://_probe/styles/01_quiet_borders.gd")


func apply(kit) -> void:
	for county: Polygon2D in kit.counties():
		county.color = kit.hex(KINGDOM[kit.kingdom_of(county)])
	kit.style_land({"band_px": 26.0, "band_base": Color.WHITE, "band_strength": 0.75, "band_rim": 0.0})
	kit.style_rank("Kingdoms", kit.hex("#3d3448"), 6.0, null, "onto")
	kit.set_alpha("Borders/Kingdoms", 0.9)
	kit.set_alpha("BordersOverLakes/Kingdoms", 0.9)
	for rank: String in ["Duchies", "Counties"]:
		var look: Array = QUIET.RANKS[rank]
		kit.style_rank(rank, look[0], look[1], null, "onto")
		kit.set_alpha("Borders/" + rank, look[2])
		kit.set_alpha("BordersOverLakes/" + rank, look[2])
