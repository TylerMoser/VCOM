## Writes the per-style sections of VISUAL_VARIANTS.md, straight from the same
## data the renderer uses, so the listed settings cannot drift from the renders.
## The header and index of that file are hand-written; paste these sections in.
##
## Run from vcom/ with the harness copied into res://_probe/ (render.sh does
## the copy), then delete _probe/ afterwards:
##   godot --headless --path . --script <abs path>/dump_notes.gd -- --out=<abs path>/sections.md [--all]
## Only the styles in VariantNotes.KEPT are written unless --all is given.
extends SceneTree

var _enums := {}


func _initialize() -> void:
	var out_path := ""
	var everything := false
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--out="):
			out_path = arg.get_slice("=", 1)
		elif arg == "--all":
			everything = true
	if out_path == "":
		push_error("dump_notes: pass --out=<file>")
		quit(1)
		return

	var VariantList = load("res://_probe/VariantList.gd")
	var VariantNotes = load("res://_probe/VariantNotes.gd")
	var Variants = load("res://_probe/Variants.gd")
	for cls in ["Environment", "Viewport", "BaseMaterial3D", "Light3D", "DirectionalLight3D"]:
		_collect_enums(cls)

	var all: Dictionary = VariantList.variants()
	var notes: Dictionary = VariantNotes.notes()
	var ids: Array = all.keys() if everything else VariantNotes.KEPT.duplicate()
	ids.sort()
	var out := PackedStringArray()
	for id: int in ids:
		var v: Dictionary = all[id]
		var n: Array = notes.get(id, ["", "", ""])
		var file := "%02d-%s.png" % [id, Variants.slug(v.get("name", ""))]
		out.append("## %02d · %s" % [id, v["name"]])
		out.append("")
		out.append("![%02d %s](%s)" % [id, v["name"], file])
		out.append("")
		out.append(n[0])
		out.append("")
		out.append("*Cost:* %s  ·  *Applying it changes:* %s" % [n[1], n[2]])
		out.append("")
		if id == 0:
			out.append("Settings: see **Current settings** at the top.")
		else:
			out.append_array(_settings(v))
		out.append("")
		out.append("---")
		out.append("")
	var f := FileAccess.open(out_path, FileAccess.WRITE)
	f.store_string("\n".join(out))
	f.close()
	print("wrote ", out_path)
	quit()


func _settings(v: Dictionary) -> PackedStringArray:
	var lines := PackedStringArray()
	if v.has("env"):
		lines.append("- **Environment:** " + _props(v["env"], "Environment"))
	if v.has("sky"):
		lines.append("- **Sky (ProceduralSkyMaterial):** " + _props(v["sky"], ""))
	if v.has("sun"):
		lines.append("- **Sun (DirectionalLight3D):** " + _light(v["sun"]))
	var index := 1
	for light: Dictionary in v.get("extra_lights", []):
		lines.append("- **Extra DirectionalLight3D %d:** %s" % [index, _light(light)])
		index += 1
	if v.has("camera"):
		lines.append("- **Camera attributes (CameraAttributesPractical, on WorldEnvironment):** " + _props(v["camera"], ""))
	if v.has("camera_b"):
		lines.append("- **Same, for the close view only:** " + _props(v["camera_b"], ""))
	if v.has("fov"):
		lines.append("- **Camera3D:** `fov` %s, with CameraRig `near_distance`/`far_distance` scaled ×%.2f to keep the framing" % [_val(v["fov"]), tan(deg_to_rad(37.5)) / tan(deg_to_rad(float(v["fov"]) * 0.5))])
	if v.has("viewport"):
		lines.append("- **Viewport / project rendering:** " + _props(v["viewport"], "Viewport"))
	if v.has("blocks"):
		var b: Dictionary = v["blocks"]
		if b.has("standard"):
			lines.append("- **Block materials (StandardMaterial3D, on top of the importer's vertex-colour material):** " + _props(b["standard"], "BaseMaterial3D"))
		elif b.has("shader"):
			var text := "`voxel_block.gdshader`, " + _props(b.get("params", {}), "")
			if b.has("crate_params"):
				text += "; crate overrides: " + _props(b["crate_params"], "")
			lines.append("- **Block material (custom shader):** " + text)
	if v.has("units"):
		lines.append("- **Unit capsule materials:** " + _props(v["units"], "BaseMaterial3D"))
	if v.has("outline"):
		lines.append("- **Outline pass (`outline.gdshader` on a full-screen quad, render priority −128):** " + _props(v["outline"], ""))
	if v.has("lut"):
		var l: Dictionary = v["lut"].duplicate()
		var kind: String = l["kind"]
		l.erase("kind")
		if kind == "split":
			var stops := PackedStringArray()
			for i in l["offsets"].size():
				stops.append("%s → %s" % [_val(l["offsets"][i]), _val(l["colors"][i])])
			lines.append("- **Colour correction (1D LUT, GradientTexture1D, per-channel curves):** " + ", ".join(stops))
		else:
			lines.append("- **Colour correction (generated 33³ 3D LUT):** " + _props(l, ""))
	return lines


func _light(props: Dictionary) -> String:
	var rest := props.duplicate()
	var parts := PackedStringArray()
	if rest.has("elevation"):
		var az: float = rest.get("azimuth", 0.0)
		parts.append("%s° above the horizon, coming from azimuth %s° (%s)" % [_val(rest["elevation"]), _val(az), _compass(az)])
		rest.erase("elevation")
		rest.erase("azimuth")
	if not rest.is_empty():
		parts.append(_props(rest, "Light3D"))
	return " · ".join(parts)


func _props(props: Dictionary, cls: String) -> String:
	var parts := PackedStringArray()
	for key: String in props:
		parts.append("`%s` %s" % [key, _val(props[key], cls, key)])
	return " · ".join(parts)


func _val(value, cls := "", key := "") -> String:
	if value is bool:
		return "on" if value else "off"
	if value is int:
		var names: Dictionary = _enums.get(cls + "." + key, {})
		if names.is_empty() and cls == "Light3D":
			names = _enums.get("DirectionalLight3D." + key, {})
		if names.has(value):
			return "%s (%d)" % [names[value], value]
		return str(value)
	if value is float:
		return _num(value)
	if value is Color:
		return "#%s (%s, %s, %s)" % [value.to_html(false), _num(value.r), _num(value.g), _num(value.b)]
	if value is Vector3:
		return "(%s, %s, %s)" % [_num(value.x), _num(value.y), _num(value.z)]
	return str(value)


func _num(x: float) -> String:
	var s := "%.3f" % x
	s = s.rstrip("0").rstrip(".")
	return s if s != "-0" else "0"


## Azimuth is where the light comes FROM: 0 = south (+Z), 90 = east (+X).
## The default camera looks from the south-east toward the north-west.
func _compass(az: float) -> String:
	var names := {0: "south", 45: "south-east", 90: "east", 135: "north-east", 180: "north", -45: "south-west", -90: "west", -135: "north-west", -180: "north"}
	var best := 0
	var best_d := 999.0
	for a: int in names:
		var d := absf(wrapf(az - a, -180.0, 180.0))
		if d < best_d:
			best_d = d
			best = a
	var side := ""
	# Relative to the default camera, which sits at azimuth 45.
	var rel := wrapf(az - 45.0, -180.0, 180.0)
	if absf(rel) < 25.0:
		side = ", nearly behind the camera"
	elif rel < 0.0 and rel > -135.0:
		side = ", camera-left"
	elif rel > 0.0 and rel < 135.0:
		side = ", camera-right"
	return names[best] + side


func _collect_enums(cls: String) -> void:
	for p in ClassDB.class_get_property_list(cls, false):
		if p.hint != PROPERTY_HINT_ENUM:
			continue
		var names := {}
		var next := 0
		for item: String in String(p.hint_string).split(","):
			var name := item
			var value := next
			if item.contains(":"):
				name = item.get_slice(":", 0)
				value = int(item.get_slice(":", 1))
			names[value] = name.get_slice(" (", 0).strip_edges()
			next = value + 1
		_enums[cls + "." + String(p.name)] = names
