## 20p · Towns sell their maps. The party sees 15 miles about it as it goes, and in each duchy's
## capital it visits it gets the duchy's map: every county of that duchy revealed whole. The journey
## passes two (counties 112 and 69), so two duchies are known besides the road through them. A town
## becomes a place to go for what it knows, and a Location could sell the map (a Market's stock).
extends RefCounted

const NAME := "Towns sell their maps"
const LABEL := "20p"
const Now := preload("res://_probe/styles/2000_fog_now.gd")
## The duchies' capitals the journey visits, by their county.
const CAPITALS := [112, 69]

var _mask: Image


func apply(kit) -> void:
	var duchies := {}
	for county: Polygon2D in kit.counties():
		if CAPITALS.has(int(str(county.name).substr(6))):
			duchies[kit.duchy_of(county)] = true
	var revealed := {}
	for county: Polygon2D in kit.counties():
		if duchies.has(kit.duchy_of(county)):
			revealed[int(str(county.name).substr(6))] = true
	_mask = Now.fog(kit, [Now.journey(15.0 * Now.MILE)], Now.VEIL, ["coast", "kingdoms", "rivers"], Now.SKETCH, 0.6,
			false, revealed)
	print("MapStyleProbe: 20p: duchies %s, counties %s" % [str(duchies.keys()), str(revealed.keys())])


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
