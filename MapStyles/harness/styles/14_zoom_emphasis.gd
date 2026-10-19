## 14 · Emphasis follows the zoom. Far out the map is about the realm: the
## kingdoms' borders are its strongest lines and the roads thin threads. Close
## in it is about the road ahead: the roads widen and the borders thin and
## pale, as on Google Maps, where a country's border all but vanishes at street
## level. Today one factor scales every line alike, so borders are heaviest
## exactly where the player is choosing a road. Here each kind of line has its
## own growth with the zoom: borders shrink toward the closest view (and fade),
## roads grow, water and the coast keep MapDetail's rule.
##
## For real: MapDetail's one factor becomes one per kind (a width_growth for
## borders, one for roads), and an alpha curve per border rank. The "...Along"
## lines, sized to their river or road and their border, take the border's
## factor for their border part.
extends RefCounted

const NAME := "Emphasis follows the zoom"
const MILE := 16.09344

## How a kind's width follows the zoom against MapDetail's own rule: its
## widths times (view's miles / 220) ^ this. Above 0, thinner close in.
const BORDER_GROWTH := 0.35
const ROAD_GROWTH := -0.3

var _detail: Node
var _base := PackedFloat32Array()
var _base_plain := PackedFloat32Array()
var _kind := PackedInt32Array()


func ready(kit) -> void:
	_detail = kit.at("Detail")
	var lines: Array = _detail.get("_lines")
	_base = (_detail.get("_widths") as PackedFloat32Array).duplicate()
	_base_plain = (_detail.get("_plain") as PackedFloat32Array).duplicate()
	var borders: Array[Node] = [kit.at("Borders"), kit.at("BordersOverLakes")]
	var roads: Array[Node] = [kit.at("Roads"), kit.at("Bridges")]
	for line: Line2D in lines:
		var kind := 0
		if borders.any(func(n: Node) -> bool: return n.is_ancestor_of(line)):
			kind = 1
		elif roads.any(func(n: Node) -> bool: return n.is_ancestor_of(line)):
			kind = 2
		_kind.append(kind)


func before_panel(kit, _index: int, view: Array) -> void:
	var miles: float = view[3]
	if miles <= 0.0:
		var camera := kit.at("Camera") as Camera2D
		miles = kit.map.get_viewport().get_visible_rect().size.y / camera.zoom.y / MILE
	var border := pow(miles / 220.0, BORDER_GROWTH)
	var road := pow(miles / 220.0, ROAD_GROWTH)
	var widths: PackedFloat32Array = _detail.get("_widths")
	var plain: PackedFloat32Array = _detail.get("_plain")
	var set_step: PackedInt32Array = _detail.get("_set_step")
	for i in _kind.size():
		var k: float = [1.0, border, road][_kind[i]]
		widths[i] = _base[i] * k
		plain[i] = _base_plain[i] * k
		set_step[i] = -9999
	_detail.set("_widths", widths)
	_detail.set("_plain", plain)
	_detail.set("_set_step", set_step)
	_detail.set("_stale", true)
	# The borders fade as the view closes in: whole at 400 miles and over,
	# about half at the closest.
	var fade := clampf(0.45 + 0.55 * (log(miles / 25.0) / log(16.0)), 0.45, 1.0)
	for rank: String in ["Kingdoms", "Duchies", "Counties"]:
		var most: float = {"Kingdoms": 1.0, "Duchies": 0.9, "Counties": 0.75}[rank]
		for group: String in ["Borders/", "BordersOverLakes/"]:
			var node := kit.at(group + rank) as CanvasItem
			var alphas: Dictionary = _detail.get("_alpha")
			if alphas.has(node):
				alphas[node] = most * fade
				node.modulate.a = most * fade if node.modulate.a > 0.0 else 0.0
			else:
				node.modulate.a = most * fade
