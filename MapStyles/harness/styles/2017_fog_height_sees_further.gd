## 20q · Height sees further. How far the party sees depends on the ground it stands on: 6 miles plus
## 60 times the height's value in elevation.png (the square root of its share of 3,352 m), so about
## 12 miles at the sea's edge, 25 at 300 m and 36 at 830 m, worked out every 2 miles along the way. A
## climb is worth making, the corridor swells over hills and narrows along valleys, and the map's own
## heights decide it with no new data.
extends RefCounted

const NAME := "Height sees further"
const LABEL := "20q"
const Now := preload("res://_probe/styles/2000_fog_now.gd")

var _mask: Image


func apply(kit) -> void:
	var heights := Image.load_from_file(kit.data_dir.path_join("elevation.png"))
	var points := Now.journey_points(2.0 * Now.MILE)
	var radii := PackedFloat32Array()
	var least := 1e9
	var most := 0.0
	for point in points:
		var x := clampi(int(point.x / 3.35), 0, heights.get_width() - 1)
		var y := clampi(int(point.y / 3.35), 0, heights.get_height() - 1)
		var miles := 6.0 + 60.0 * heights.get_pixel(x, y).r
		least = minf(least, miles)
		most = maxf(most, miles)
		radii.append(miles * Now.MILE)
	_mask = Now.fog(kit, [[points, radii, 0.0, 1.0]])
	print("MapStyleProbe: 20q: sight from %.1f to %.1f miles along the way" % [least, most])


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
