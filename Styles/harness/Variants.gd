## Applies a visual variant (a plain Dictionary of settings) to a CombatMap.
##
## Keys, all optional:
##   env      Environment properties
##   sky      ProceduralSkyMaterial properties (the scene's existing sky)
##   sun      DirectionalLight3D properties, plus elevation/azimuth in degrees
##   fill     a second, shadowless DirectionalLight3D, same keys as sun
##   camera   CameraAttributesPractical properties (DOF), set on WorldEnvironment
##   fov      Camera3D fov; distance scaled so the framing stays the same
##   viewport root Viewport properties (AA, 3D scaling)
##   blocks   {"standard": {BaseMaterial3D props}} or {"shader": path, "params": {}, "crate_params": {}}
##   units    BaseMaterial3D props for the unit capsules
##   outline  params for the post-process outline shader
##   lut      {"kind": "vibrance"/"split", ...} generated colour-correction LUT
extends RefCounted

const VariantList := preload("res://_probe/VariantList.gd")
const OUTLINE_SHADER := "res://_probe/shaders/outline.gdshader"


static func get_variant(id: int) -> Dictionary:
	var all: Dictionary = VariantList.variants()
	return all.get(id, {})


## "Tilt-Shift Miniature (DOF)" -> "tilt-shift-miniature-dof".
static func slug(name: String) -> String:
	var out := ""
	for c in name.to_lower():
		out += c if (c >= "a" and c <= "z") or (c >= "0" and c <= "9") else "-"
	while out.contains("--"):
		out = out.replace("--", "-")
	return out.trim_prefix("-").trim_suffix("-")


static func apply(v: Dictionary, map: Node, viewport: Viewport) -> void:
	var world_env := map.get_node(^"WorldEnvironment") as WorldEnvironment
	var env := world_env.environment
	var sky_mat := env.sky.sky_material as ProceduralSkyMaterial
	var sun := map.get_node(^"DirectionalLight3D") as DirectionalLight3D

	_set_all(env, v.get("env", {}))
	_set_all(sky_mat, v.get("sky", {}))
	_apply_light(sun, v.get("sun", {}))

	var extra_index := 0
	for props: Dictionary in v.get("extra_lights", []):
		var light := DirectionalLight3D.new()
		light.name = "ExtraLight%d" % extra_index
		light.shadow_enabled = false
		# Do not draw a second sun disc in the sky.
		light.sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_ONLY
		map.add_child(light)
		_apply_light(light, props)
		extra_index += 1

	if v.has("camera"):
		var attributes := CameraAttributesPractical.new()
		_set_all(attributes, v["camera"])
		world_env.camera_attributes = attributes

	if v.has("fov"):
		var cam := map.get_node(^"CameraRig/Camera3D") as Camera3D
		var rig := map.get_node(^"CameraRig")
		var scale := tan(deg_to_rad(cam.fov) * 0.5) / tan(deg_to_rad(float(v["fov"])) * 0.5)
		cam.fov = v["fov"]
		rig.set("near_distance", float(rig.get("near_distance")) * scale)
		rig.set("far_distance", float(rig.get("far_distance")) * scale)
		rig.set("_current_distance", float(rig.get("_current_distance")) * scale)
		cam.far = 4000.0

	_set_all(viewport, v.get("viewport", {}))

	if v.has("blocks"):
		_apply_blocks(map, v["blocks"])
	if v.has("units"):
		_apply_units(map, v["units"])
	if v.has("outline"):
		_add_outline(map, v["outline"])
	if v.has("lut"):
		env.adjustment_enabled = true
		env.adjustment_color_correction = _make_lut(v["lut"])


static func _set_all(target: Object, props: Dictionary) -> void:
	for key: String in props:
		if not key in target:
			push_error("Variants: %s has no property '%s'" % [target.get_class(), key])
			continue
		target.set(key, props[key])


static func _apply_light(light: DirectionalLight3D, props: Dictionary) -> void:
	var rest := props.duplicate()
	if rest.has("elevation") or rest.has("azimuth"):
		var elevation: float = rest.get("elevation", 50.0)
		var azimuth: float = rest.get("azimuth", 0.0)
		# Azimuth is the compass direction the light comes FROM: 0 = +Z (south),
		# 90 = +X (east), -90 = -X (west), 180 = -Z (north).
		light.rotation_degrees = Vector3(-elevation, azimuth, 0.0)
		rest.erase("elevation")
		rest.erase("azimuth")
	_set_all(light, rest)


static func _block_meshes(map: Node) -> Dictionary:
	var grid := map.get_node(^"GridMap") as GridMap
	var lib := grid.mesh_library
	var meshes := {}
	for id in lib.get_item_list():
		meshes[lib.get_item_name(id)] = lib.get_item_mesh(id)
	return meshes


## Close-view overrides: DOF distances that suit the nearer camera.
static func apply_view_b(v: Dictionary, map: Node) -> void:
	if v.has("camera_b"):
		var world_env := map.get_node(^"WorldEnvironment") as WorldEnvironment
		_set_all(world_env.camera_attributes, v["camera_b"])


static func _apply_blocks(map: Node, spec: Dictionary) -> void:
	var meshes := _block_meshes(map)
	for item_name: String in meshes:
		var mesh: Mesh = meshes[item_name]
		var is_crate := item_name.to_lower().contains("crate")
		for s in mesh.get_surface_count():
			var original := mesh.surface_get_material(s)
			if spec.has("shader"):
				var mat := ShaderMaterial.new()
				mat.shader = load(spec["shader"])
				var params: Dictionary = spec.get("params", {}).duplicate()
				if is_crate:
					params.merge(spec.get("crate_params", {}), true)
				for p: String in params:
					mat.set_shader_parameter(p, params[p])
				mesh.surface_set_material(s, mat)
			elif spec.has("standard"):
				var mat := (original as BaseMaterial3D).duplicate() as BaseMaterial3D
				_set_all(mat, spec["standard"])
				mesh.surface_set_material(s, mat)


static func _apply_units(map: Node, props: Dictionary) -> void:
	for unit in map.get_node(^"Units").get_children():
		var mesh := unit.get_node_or_null(^"Mesh") as MeshInstance3D
		if mesh == null:
			continue
		var mat := mesh.get_surface_override_material(0) as BaseMaterial3D
		if mat == null:
			continue
		mat = mat.duplicate() as BaseMaterial3D
		_set_all(mat, props)
		mesh.set_surface_override_material(0, mat)


static func _add_outline(map: Node, params: Dictionary) -> void:
	var quad := MeshInstance3D.new()
	quad.name = "OutlinePost"
	var mesh := QuadMesh.new()
	mesh.size = Vector2(2.0, 2.0)
	quad.mesh = mesh
	quad.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	quad.extra_cull_margin = 16384.0
	quad.ignore_occlusion_culling = true
	var mat := ShaderMaterial.new()
	mat.shader = load(OUTLINE_SHADER)
	# Draw before the translucent tile highlights so they stay on top.
	mat.render_priority = -128
	for p: String in params:
		mat.set_shader_parameter(p, params[p])
	quad.material_override = mat
	map.add_child(quad)


## Builds a colour-correction LUT. Godot applies it after tonemapping, in
## display (sRGB) space, so these functions work on sRGB values.
static func _make_lut(spec: Dictionary) -> Texture:
	match spec.get("kind", ""):
		"split":
			var gradient := Gradient.new()
			gradient.offsets = PackedFloat32Array(spec["offsets"])
			gradient.colors = PackedColorArray(spec["colors"])
			var tex := GradientTexture1D.new()
			tex.gradient = gradient
			tex.width = 256
			return tex
		"grade":
			return _make_lut_3d(spec)
	push_error("Variants: unknown LUT kind")
	return null


static func _make_lut_3d(spec: Dictionary) -> ImageTexture3D:
	const N := 33
	var vibrance: float = spec.get("vibrance", 0.0)
	var saturation: float = spec.get("saturation", 1.0)
	var green_sat: float = spec.get("green_saturation", 1.0)
	var green_hue: float = spec.get("green_hue_shift", 0.0)
	var warm: float = spec.get("warm_highlights", 0.0)
	var cool: float = spec.get("cool_shadows", 0.0)
	var slices: Array[Image] = []
	for bi in N:
		var img := Image.create(N, N, false, Image.FORMAT_RGBAH)
		for gi in N:
			for ri in N:
				# The LUT is sampled with no half-texel offset, so texel i
				# stands for the input at its centre.
				var c := Color((ri + 0.5) / N, (gi + 0.5) / N, (bi + 0.5) / N)
				var h := c.h
				var s := c.s
				var val := c.v
				# Vibrance lifts muted colours and leaves strong ones nearly alone.
				s = clampf(s * saturation + vibrance * s * (1.0 - s) * (1.0 - s), 0.0, 1.0)
				# Then pull greens toward the given hue and saturation, last so
				# the vibrance boost cannot undo it.
				var green_w := _hue_weight(h * 360.0, 100.0, 45.0)
				h = fposmod(h + green_hue / 360.0 * green_w, 1.0)
				s *= lerpf(1.0, green_sat, green_w)
				var out := Color.from_hsv(h, s, val)
				var luma := out.get_luminance()
				out.r += warm * luma * luma * 0.06 - cool * (1.0 - luma) * (1.0 - luma) * 0.02
				out.b += cool * (1.0 - luma) * (1.0 - luma) * 0.05 - warm * luma * luma * 0.05
				img.set_pixel(ri, gi, Color(clampf(out.r, 0, 1), clampf(out.g, 0, 1), clampf(out.b, 0, 1)))
		slices.append(img)
	var tex := ImageTexture3D.new()
	tex.create(Image.FORMAT_RGBAH, N, N, N, false, slices)
	return tex


## 1 at [param center] degrees, falling smoothly to 0 at +/- [param width].
static func _hue_weight(hue: float, center: float, width: float) -> float:
	var d := absf(fposmod(hue - center + 180.0, 360.0) - 180.0)
	return 1.0 - smoothstep(0.0, width, d)
