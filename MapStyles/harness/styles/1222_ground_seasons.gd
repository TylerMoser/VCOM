## 12v · The seasons. The ground follows the campaign's clock (the map's MapClock): spring greener and
## fresher, summer 12's grounds, autumn golden with the broadleaf forests turned, winter with snow
## over the north and the heights (the snowline from 840 m in the far south down to 130 m in the far
## north: a third of the land, 93% of the Tundra), the land browned, the lakes frozen pale and the
## broadleaf woods bare. One view, all the way out, in each of the four.
extends RefCounted

const NAME := "The seasons"
const LABEL := "12v"
const Now := preload("res://_probe/styles/1200_ground_now.gd")
const Kit := preload("res://_probe/StyleKit.gd")
const SEASONS := [
	["Spring", {1: "#edf0ee", 2: "#e4ded5", 3: "#e2ecd8", 4: "#f2e6c8", 5: "#e3efc8", 6: "#d4ebd1", 7: "#dce9c8",
			8: "#dbefca", 9: "#d1ecc4"}, 0.82, 0.08, "#a8d885"],
	["Summer", Now.GROUND_12, 0.9, 0.0, "#acd085"],
	["Autumn", {1: "#ebe9e4", 2: "#e6d8cc", 3: "#e9e2cf", 4: "#f4e0bc", 5: "#f1e4bd", 6: "#dfe6cd", 7: "#e8e1c2",
			8: "#f1dfbe", 9: "#dce8c4"}, 0.8, 0.1, "#d9a65a"],
	["Winter", {1: "#f2f4f6", 2: "#e5e1dd", 3: "#ebece7", 4: "#f0e4cd", 5: "#e9e5d3", 6: "#dfe6e0", 7: "#e0e1d3",
			8: "#e6e8dc", 9: "#d9e6d0"}, 0.5, 0.3, "#c4bba4"],
]

var _ground: ShaderMaterial
var _lakes: Array = []


func apply(kit) -> void:
	_ground = Now.ground(kit, {"snow_from": 0.9, "line_ragged": 0.04})
	Now.forests(kit, Now.FORESTS_12)
	_lakes = kit.lakes()


func panels(_kit) -> Array:
	var views := []
	for season: Array in SEASONS:
		views.append([season[0].left(2).to_upper(), season[0] + ": all the way out", null, 0.0])
	return views


func before_panel(kit, index: int, _view: Array) -> void:
	var season: Array = SEASONS[index]
	Now.colour_counties(kit, season[1])
	_ground.set_shader_parameter(&"palette", Kit.palette_of(season[1]))
	_ground.set_shader_parameter(&"snow_from", season[2])
	_ground.set_shader_parameter(&"snow_north", season[3])
	kit.set_forest("Broadleaf", Kit.hex(season[4], 0.7))
	var frozen: bool = season[0] == "Winter"
	for lake: Polygon2D in _lakes:
		lake.color = Color("#e4eff4") if frozen else Color(0.6431373, 0.8666667, 0.99215686)
