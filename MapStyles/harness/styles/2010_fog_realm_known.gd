## 20j · The realm is known. What every traveller knows is the realm itself, drawn whole and in its own
## look over the fog, not sketched: the coast, the kingdoms' borders with their dash-dots, the great
## rivers, the great lakes, the nine capitals; exactly what the map shows all the way out (its Realm
## tier). The rest, the duchies, counties, roads, forests and lesser places, waits to be seen.
extends RefCounted

const NAME := "The realm is known"
const LABEL := "20j"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var veil := {"veil": Now.PAPER, "opacity": 0.9, "ragged": 0.25, "ragged_scale": 90.0}
	_mask = Now.fog(kit, [Now.journey()], veil, ["coast", "kingdoms", "rivers", "lakes"], Color(0, 0, 0, 0), 1.0)


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
