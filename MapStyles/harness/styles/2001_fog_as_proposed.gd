## 20a · As proposed, on today's look. Proposal 20 as it was pictured (20_fog_of_war.gd), on the map as
## it now is: the land the party has seen is a ring of 30 miles round its start; the rest lies under
## a paper-coloured veil (93%) with a faint grain and a ragged edge, through which only what everyone
## would know shows, sketched in a brown ink: the coast, the kingdoms' borders (in their own pattern)
## and the great rivers, and the nine kingdoms' capitals. The party at its start, as there.
extends RefCounted

const NAME := "As proposed, on today's look"
const LABEL := "20a"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var ring := [PackedVector2Array([Now.START]), PackedFloat32Array([30.0 * Now.MILE]), 1.0, 1.0]
	_mask = Now.fog(kit, [ring])


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])


func panels(_kit) -> Array:
	return [Now.VIEWS[0], ["B", "Duchy tier: 180 miles round the start", Now.START, 180.0],
			["C", "County tier: 70 miles round the start", Now.START, 70.0],
			["D", "35 miles: the edge of what it has seen", Now.START + Vector2(0, -30.0 * Now.MILE), 35.0]]
