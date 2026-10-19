## 07 · Forest symbols. Forests are where the party is set upon, so they
## should read as "woodland" and nothing else. Each piece keeps a light green
## fill, the four greens drawn closer together so the land is less blotchy, and
## gets a scatter of small tree marks, the topographic map's woodland symbol:
## a conifer's triangle, a broadleaf's round crown, the marsh tuft in the
## Swamp's own forest, the tropical forest's packed crowns. The kind is in the
## mark, not only the shade. The marks are anchored to the map and keep about
## 15 pixels apart at every zoom (forest.gdshader).
extends RefCounted

const NAME := "Forest symbols"

## Each kind: fill colour and alpha, glyph, mark colour and alpha, mark size.
const KINDS := {
	"Conifer": ["#c3dfc6", 0.65, 1, "#2f6b47", 0.75, 0.62],
	"Broadleaf": ["#d5e8bf", 0.65, 2, "#4f7a28", 0.7, 0.6],
	"Swamp": ["#d6dcb8", 0.65, 3, "#636b26", 0.8, 0.62],
	"Tropical": ["#bfdfba", 0.7, 4, "#2a6b33", 0.6, 0.62],
}


func apply(kit) -> void:
	for kind: String in KINDS:
		var look: Array = KINDS[kind]
		kit.style_forests(kind, kit.hex(look[0], look[1]), {
			"glyph": look[2], "mark": kit.hex(look[3], look[4]), "cell_px": 15.0, "mark_size": look[5] * 1.12,
			"density": 0.8, "jitter": 0.22,
		})
