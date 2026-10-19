## 16 · Map key and inspect. The map explains itself, in its present colours:
## a key in the corner (toggled with K) shows every kind of line, area and
## icon, its samples read off the map's own nodes so it stays true to any
## style; and the line under the pointer lights up, with a tooltip saying what
## it is ("Kingdom border · Kingdom 3 | Kingdom 5", "River 40", "Lane to a
## village in County 115"). Nothing on the map changes: this is the cheapest
## way to make every line identifiable, and it suits any of the other
## proposals.
extends RefCounted

const NAME := "Map key and inspect"

## Where the pretend pointer is in each panel, as a share of the screen.
const POINTERS := [Vector2(-1, -1), Vector2(0.588, 0.59), Vector2(0.6, 0.53), Vector2(0.65, 0.77)]

var _legend: CanvasLayer


func ready(kit) -> void:
	_legend = kit.runtime("Legend.gd").new()
	_legend.map = kit.map
	_legend.rows = [
		["Sea", "area", "Sea"],
		["Lake, river", "area", "Lakes/Lake001"],
		["Coast", "line", "Coast/CoastOfCounty002", 4.0],
		["Kingdom border", "line", "Borders/Kingdoms/Kingdoms1And2", 5.0],
		["Duchy border", "line", "Borders/Duchies/Duchies01And03", 3.0],
		["County border", "line", "Borders/Counties/Counties001And002", 2.0],
		["Highway", "line", "Roads/Highways/Road013ToFork227", 3.5],
		["Road", "line", "Roads/Roads/Road040To038", 2.5],
		["Lane", "line", "Roads/Lanes/County025Village3Lane", 1.5],
		["Bridge", "line", "Bridges/Bridge001", 5.0],
	]
	for kind: String in ["Conifer", "Broadleaf", "Swamp", "Tropical"]:
		var piece: Polygon2D = kit.forests(kind)[0]
		_legend.rows.append(["%s forest" % kind, "area", kit.map.get_path_to(piece)])
	_legend.rows.append_array([
		["City (capital)", "icon", "Settlements/KingdomCapitals/Kingdom1Capital"],
		["Town", "icon", "Settlements/CountyCapitals/County002Capital"],
		["Village", "icon", "Settlements/Villages/County002Village1"],
		["Hamlet", "icon", "Settlements/Hamlets/County002Hamlet1"],
		["Your party", "party", null],
	])
	kit.probe.add_child(_legend)


func before_panel(_kit, index: int, _view: Array) -> void:
	_legend.pointer = POINTERS[index] if index < POINTERS.size() else Vector2(-1, -1)
	_legend.pick()
