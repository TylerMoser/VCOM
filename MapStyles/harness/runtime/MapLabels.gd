## Names on the map, set in a typographic hierarchy as on Google Maps: the
## kingdoms in wide-spaced capitals across their land, the duchies in small
## spaced capitals, each settlement's name beside its icon in a size by its
## rank, the great lakes in blue italics. Each kind shows over its own range of
## zooms, and a name that would run into another, or into an icon, is left out,
## the higher ranks placed first. Sized in screen pixels.
##
## Nothing on the map has a name yet, so the names are made up here from each
## node's name, the same every run: placeholders, to judge the look by. The
## kingdoms go by their biomes, which are their names in the docs.
##
## A runtime node for the map style harness. For real, the placing would be
## worked out once per zoom step rather than every frame it is drawn.
extends Node2D

const START := ["Ash", "Bram", "Cal", "Dun", "Elder", "Fen", "Gar", "Hal", "Iver", "Kel", "Lan", "Mor", "Nor", "Ost",
		"Pen", "Ral", "Sel", "Tarn", "Ul", "Ver", "Wen", "Yar", "Bel", "Cor", "Dal", "Esk", "Fal", "Gil", "Hart", "Lin",
		"Mar", "Ned", "Oak", "Rook", "Stan", "Thorn", "Wil", "Ald", "Brack", "Craig", "Elm", "Frost", "Glen", "Holt",
		"Ken", "Lock", "Mill", "Pike", "Red", "Sage", "Tod", "Wyn", "Har", "Bry", "Cran", "Dor", "Ever", "Gold"]
const END := ["by", "ford", "wick", "ton", "ham", "stead", "mere", "dale", "holm", "thorpe", "bury", "ley", "field",
		"worth", "gate", "moor", "brook", "well", "minster", "haven", "crag", "stow", "fold", "burn", "combe", "den",
		"hurst", "marsh", "ridge", "shaw"]

## Each kind: font size, colour, halo colour, letter spacing, upper case,
## italic, the range of the view's height in miles it shows over (least, most).
var kinds := {
	"kingdom": [19, Color(0.33, 0.25, 0.42, 0.55), Color(1, 1, 1, 0.0), 5, true, false, 200.0, 99999.0],
	"duchy": [11, Color(0.38, 0.31, 0.45, 0.85), Color(1, 1, 1, 0.7), 2, true, false, 90.0, 480.0],
	"capital": [15, Color(0.1, 0.1, 0.12), Color(1, 1, 1, 0.92), 0, false, false, 0.0, 99999.0],
	"city": [13, Color(0.13, 0.13, 0.15), Color(1, 1, 1, 0.92), 0, false, false, 0.0, 480.0],
	"town": [12, Color(0.2, 0.2, 0.22), Color(1, 1, 1, 0.9), 0, false, false, 0.0, 240.0],
	"village": [11, Color(0.27, 0.27, 0.3), Color(1, 1, 1, 0.9), 0, false, false, 0.0, 100.0],
	"hamlet": [10, Color(0.36, 0.36, 0.38), Color(1, 1, 1, 0.85), 0, false, false, 0.0, 40.0],
	"lake": [12, Color(0.13, 0.4, 0.66), Color(1, 1, 1, 0.6), 1, false, true, 0.0, 99999.0],
}
## Draw names over a dark map: halos dark, letters light.
var dark := false
var placeholder_note := true
## Set every name in a serif (an old atlas), and in this ink when its alpha is
## over 0 (the halo then this paper colour).
var serif := false
var ink := Color(0, 0, 0, 0)
var paper := Color(1, 1, 1, 0.85)

var map: Node2D
var _labels: Array = []
var _fonts := {}
var _drawn_view := Transform2D()


func _ready() -> void:
	z_index = 7
	_gather()


## A made-up name, the same every time for the same key.
static func name_for(key: String) -> String:
	var h := absi(key.hash())
	return START[h % START.size()] + END[(h / START.size()) % END.size()]


func _gather() -> void:
	var land := map.get_node("Land")
	for kingdom in land.get_children():
		var biome := str(kingdom.get_meta("biome", kingdom.name))
		_labels.append(_area_label("kingdom", biome, kingdom))
		for duchy in kingdom.get_children():
			_labels.append(_area_label("duchy", name_for(str(duchy.name) + "D"), duchy))
	var groups := {
		"KingdomCapitals": "capital", "DuchyCapitals": "city", "CountyCapitals": "town",
		"Villages": "village", "Hamlets": "hamlet",
	}
	for group: String in groups:
		for place in map.get_node("Settlements/" + group).get_children():
			var icon: Texture2D = place.get("icon")
			var height: float = place.get("icon_height")
			var half := height * icon.get_width() / icon.get_height() * 0.5 if icon != null else 6.0
			_labels.append({"kind": groups[group], "text": name_for(str(place.name)), "at": place.position,
					"icon": place, "half": half, "area": false})
	for lake in map.get_node("Lakes").get_children():
		var polygon := lake as Polygon2D
		if polygon == null or str(polygon.name).contains("Island"):
			continue
		var across := _across(polygon.polygon)
		if across >= 60.0:
			_labels.append({"kind": "lake", "text": "Lake " + name_for(str(polygon.name)), "at": _centre(polygon.polygon),
					"area": true, "across": across})
	var order := ["kingdom", "capital", "city", "lake", "duchy", "town", "village", "hamlet"]
	_labels.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return order.find(a["kind"]) < order.find(b["kind"]))


func _area_label(kind: String, text: String, node: Node) -> Dictionary:
	var sum := Vector2.ZERO
	var area := 0.0
	for child in node.find_children("*", "Polygon2D", true, false):
		var points: PackedVector2Array = child.polygon
		var a := absf(_area(points))
		sum += _centre(points) * a
		area += a
	return {"kind": kind, "text": text, "at": sum / maxf(area, 1.0), "area": true}


func _process(_delta: float) -> void:
	# Every frame: the ranks of settlement come and go as MapDetail fades
	# them, without the view moving.
	queue_redraw()


func _font(kind: String) -> Font:
	if _fonts.has(kind):
		return _fonts[kind]
	var look: Array = kinds[kind]
	var base: Font = ThemeDB.fallback_font
	if look[5] or serif:
		var face := SystemFont.new()
		face.font_names = PackedStringArray(["Palatino Linotype", "Georgia", "Times New Roman", "serif"])
		face.font_italic = look[5]
		face.font_weight = 400 if look[5] else 600
		base = face
	var font := FontVariation.new()
	font.base_font = base
	font.spacing_glyph = look[3]
	_fonts[kind] = font
	return font


func _draw() -> void:
	var view := get_viewport().get_canvas_transform()
	_drawn_view = view
	var s := view.get_scale().x
	var screen := get_viewport().get_visible_rect()
	var miles := screen.size.y / s / MapCamera.UNITS_A_MILE
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE / s)
	# This node's own pixels are the map's units times the zoom; the screen's
	# rectangle in them is the screen moved back by the view's offset.
	var seen := Rect2(-view.origin, screen.size)
	var taken: Array[Rect2] = []
	for label: Dictionary in _labels:
		if label.has("icon"):
			var place: CanvasItem = label["icon"]
			if place.is_visible_in_tree() and seen.has_point(label["at"] * s):
				var half: float = label["half"]
				taken.append(Rect2(label["at"] * s - Vector2(half, half), Vector2(half, half) * 2.0))
	for label: Dictionary in _labels:
		var kind: String = label["kind"]
		var look: Array = kinds[kind]
		if miles < look[6] or miles > look[7]:
			continue
		if label.has("icon") and not (label["icon"] as CanvasItem).is_visible_in_tree():
			continue
		var at: Vector2 = label["at"] * s
		if not seen.grow(200.0).has_point(at):
			continue
		var text: String = label["text"].to_upper() if look[4] else label["text"]
		var font := _font(kind)
		var size: int = look[0]
		if kind == "kingdom":
			size = int(clampf(14.0 + 1100.0 / miles * 2.0, 15.0, 24.0))
		# A long name over an area goes on two lines, split at the middle space.
		var lines := PackedStringArray([text])
		if label["area"] and text.length() > 14 and text.contains(" "):
			var middle := text.length() / 2
			var split := text.rfind(" ", middle)
			var after := text.find(" ", middle)
			if split < 0 or (after >= 0 and after - middle < middle - split):
				split = after
			lines = PackedStringArray([text.left(split), text.substr(split + 1)])
		var extent := Vector2.ZERO
		for line in lines:
			extent.x = maxf(extent.x, font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1.0, size).x)
		if kind == "lake" and float(label["across"]) * s < extent.x * 0.9:
			continue
		var line_height := font.get_height(size)
		var height := line_height * lines.size()
		var spots: Array[Vector2] = []
		if label["area"]:
			# The middle, then a little above or below it, should an icon be there.
			var middle := at - Vector2(extent.x * 0.5, height * 0.5)
			for shift: float in [0.0, -1.3, 1.3, -2.4, 2.4]:
				spots.append(middle + Vector2(0.0, shift * line_height))
		else:
			var half: float = label["half"]
			spots.append(at + Vector2(half + 3.0, -height * 0.5))
			spots.append(at + Vector2(-half - 3.0 - extent.x, -height * 0.5))
			spots.append(at + Vector2(-extent.x * 0.5, -half - height - 1.0))
			spots.append(at + Vector2(-extent.x * 0.5, half + 1.0))
		for spot in spots:
			var box := Rect2(spot, Vector2(extent.x, height)).grow(2.0)
			if not seen.encloses(box) and kind != "kingdom":
				continue
			if taken.any(func(other: Rect2) -> bool: return other.intersects(box)):
				continue
			taken.append(box)
			var ink: Color = look[1]
			var halo: Color = look[2]
			if self.ink.a > 0.0 and kind != "lake":
				ink = Color(self.ink, ink.a)
				halo = Color(paper, halo.a)
			if dark:
				ink = Color(1.0 - ink.r * 0.4, 1.0 - ink.g * 0.4, 1.0 - ink.b * 0.3, ink.a)
				halo = Color(0.05, 0.07, 0.1, halo.a)
			for n in lines.size():
				var line_width := font.get_string_size(lines[n], HORIZONTAL_ALIGNMENT_LEFT, -1.0, size).x
				var indent := (extent.x - line_width) * 0.5 if label["area"] else 0.0
				var baseline := spot + Vector2(indent, font.get_ascent(size) + line_height * n)
				if halo.a > 0.0:
					draw_string_outline(font, baseline, lines[n], HORIZONTAL_ALIGNMENT_LEFT, -1.0, size, 4, halo)
				draw_string(font, baseline, lines[n], HORIZONTAL_ALIGNMENT_LEFT, -1.0, size, ink)
			break
	if placeholder_note:
		var note := "Names are placeholders"
		var font: Font = ThemeDB.fallback_font
		var spot := -view.origin + screen.size - Vector2(font.get_string_size(note, HORIZONTAL_ALIGNMENT_LEFT, -1, 12).x + 14, 12)
		draw_string_outline(font, spot, note, HORIZONTAL_ALIGNMENT_LEFT, -1.0, 12, 4, Color(1, 1, 1, 0.8) if not dark else Color(0, 0, 0, 0.8))
		draw_string(font, spot, note, HORIZONTAL_ALIGNMENT_LEFT, -1.0, 12, Color(0.35, 0.35, 0.38) if not dark else Color(0.75, 0.78, 0.82))


static func _area(points: PackedVector2Array) -> float:
	var twice := 0.0
	for i in points.size():
		var a := points[i]
		var b := points[(i + 1) % points.size()]
		twice += a.x * b.y - b.x * a.y
	return twice * 0.5


static func _centre(points: PackedVector2Array) -> Vector2:
	var area := _area(points)
	if absf(area) < 1e-6:
		var sum := Vector2.ZERO
		for p in points:
			sum += p
		return sum / maxf(points.size(), 1)
	var c := Vector2.ZERO
	for i in points.size():
		var a := points[i]
		var b := points[(i + 1) % points.size()]
		var cross := a.x * b.y - b.x * a.y
		c += (a + b) * cross
	return c / (6.0 * area)


static func _across(points: PackedVector2Array) -> float:
	return 2.0 * sqrt(absf(_area(points)) / PI)
