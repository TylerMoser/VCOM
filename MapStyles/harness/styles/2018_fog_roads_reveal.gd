## 20r · Roads lead on. The party sees 15 miles about it, and every road it meets is known for 40
## miles either way from where it met it, 4 miles to each side: the road ahead, asked about at the
## last inn. The known land reaches out along the network in long fingers, so the map shows where a
## road goes before the party takes it.
extends RefCounted

const NAME := "Roads lead on"
const LABEL := "20r"
const Now := preload("res://_probe/styles/2000_fog_now.gd")
const TOUCH := 3.0
const REACH := 40.0
const WIDE := 4.0

var _mask: Image


func apply(kit) -> void:
	var paths := [Now.journey(15.0 * Now.MILE)]
	var touched := 0
	for kind: String in ["Highways", "Roads"]:
		for road: Line2D in kit.lines_in("Roads/" + kind):
			var pts := PackedVector2Array()
			for p in road.points:
				pts.append(kit.to_map_space(road, p))
			var along := PackedFloat32Array([0.0])
			for i in range(1, pts.size()):
				along.append(along[i - 1] + pts[i - 1].distance_to(pts[i]))
			var keep := PackedByteArray()
			keep.resize(pts.size())
			var any := false
			for i in pts.size():
				if _to_journey(pts[i]) < TOUCH * Now.MILE:
					any = true
					for j in pts.size():
						if absf(along[j] - along[i]) <= REACH * Now.MILE:
							keep[j] = 1
			if not any:
				continue
			touched += 1
			var run := PackedVector2Array()
			for i in pts.size() + 1:
				if i < pts.size() and keep[i] == 1:
					run.append(pts[i])
				elif run.size() > 0:
					var radii := PackedFloat32Array()
					radii.resize(run.size())
					radii.fill(WIDE * Now.MILE)
					paths.append([run, radii, 1.0, 1.0])
					run = PackedVector2Array()
	_mask = Now.fog(kit, paths)
	print("MapStyleProbe: 20r: %d roads met on the way" % touched)


static func _to_journey(p: Vector2) -> float:
	var best := 1e12
	for i in Now.JOURNEY.size() - 1:
		var a: Vector2 = Now.JOURNEY[i]
		var b: Vector2 = Now.JOURNEY[i + 1]
		var ab := b - a
		var u := clampf((p - a).dot(ab) / ab.length_squared(), 0.0, 1.0)
		best = minf(best, p.distance_to(a + ab * u))
	return best


func ready(kit) -> void:
	kit.hide_unseen(_mask, ["KingdomCapitals"])
	Now.place_party(kit)


func route(_kit) -> PackedVector2Array:
	return PackedVector2Array([Now.NEXT])


func panels(_kit) -> Array:
	return Now.VIEWS
