## The visual variants. Each is a set of changes on top of the current scene.
extends RefCounted

const VOXEL := "res://_probe/shaders/voxel_block.gdshader"


static func variants() -> Dictionary:
	var v := {}
	v[0] = {"name": "Current look (reference)"}

	# --- Lighting and grading only -----------------------------------------
	v[1] = _merge(_sunlit(), {"name": "Sunlit Diorama"})

	v[2] = {
		"name": "Warm Sun, Cool Shade",
		"env": {
			"background_mode": Environment.BG_COLOR,
			"background_color": Color(0.18, 0.20, 0.36),
			"ambient_light_source": Environment.AMBIENT_SOURCE_COLOR,
			"ambient_light_color": Color(0.42, 0.52, 1.0),
			"ambient_light_energy": 0.6,
			"tonemap_mode": Environment.TONE_MAPPER_FILMIC,
			"adjustment_enabled": true,
			"adjustment_saturation": 1.08,
		}.merged(_ssao(1.2, 1.6)),
		"sun": {"elevation": 45.0, "azimuth": -40.0, "light_color": Color(1.0, 0.86, 0.68), "light_energy": 1.5, "shadow_blur": 1.0},
		"viewport": _msaa(),
	}

	v[3] = _merge(_sunlit(), {
		"name": "AgX Punch",
		"env": {
			"tonemap_mode": Environment.TONE_MAPPER_AGX,
			"tonemap_agx_contrast": 1.4,
			"tonemap_exposure": 1.15,
			"adjustment_enabled": true,
			"adjustment_saturation": 1.3,
			"adjustment_contrast": 1.06,
			"ambient_light_energy": 1.0,
			"ssao_intensity": 2.0,
		},
		"sun": {"light_energy": 2.4},
	})

	v[4] = {
		"name": "Soft GI Render (SDFGI)",
		"env": {
			"background_mode": Environment.BG_SKY,
			"ambient_light_source": Environment.AMBIENT_SOURCE_SKY,
			"ambient_light_energy": 0.3,
			"tonemap_mode": Environment.TONE_MAPPER_FILMIC,
			"tonemap_exposure": 0.9,
			"sdfgi_enabled": true,
			"sdfgi_use_occlusion": true,
			"sdfgi_read_sky_light": true,
			"sdfgi_bounce_feedback": 0.4,
			"sdfgi_cascades": 4,
			"sdfgi_min_cell_size": 0.15,
			"sdfgi_energy": 0.8,
		}.merged(_ssao(1.0, 1.8)),
		"sky": _sky_studio(),
		"sun": {"elevation": 55.0, "azimuth": -35.0, "light_color": Color(1.0, 0.97, 0.92), "light_energy": 1.7, "light_angular_distance": 3.0},
		"viewport": _msaa(),
	}

	v[5] = _merge(_sunlit(), {
		"name": "Colour Bounce (SSIL)",
		"env": {
			"ssil_enabled": true,
			"ssil_radius": 5.0,
			"ssil_intensity": 3.0,
			"ssil_sharpness": 0.98,
			"ssil_normal_rejection": 1.0,
			"ambient_light_energy": 0.6,
		},
		"sun": {"light_energy": 1.6},
	})

	v[6] = {
		"name": "Golden Hour",
		"env": {
			"background_mode": Environment.BG_SKY,
			"ambient_light_source": Environment.AMBIENT_SOURCE_SKY,
			"ambient_light_energy": 0.75,
			"tonemap_mode": Environment.TONE_MAPPER_FILMIC,
			"tonemap_exposure": 1.05,
			"glow_enabled": true,
			"glow_intensity": 0.5,
			"glow_bloom": 0.05,
			"glow_hdr_threshold": 1.0,
			"glow_blend_mode": Environment.GLOW_BLEND_MODE_SOFTLIGHT,
			"adjustment_enabled": true,
			"adjustment_saturation": 1.1,
		}.merged(_ssao(1.2, 1.6)),
		"sky": {
			"sky_top_color": Color(0.30, 0.32, 0.62),
			"sky_horizon_color": Color(1.0, 0.64, 0.44),
			"ground_horizon_color": Color(0.78, 0.52, 0.46),
			"ground_bottom_color": Color(0.28, 0.20, 0.34),
			"ground_curve": 0.1,
		},
		"sun": {"elevation": 22.0, "azimuth": -65.0, "light_color": Color(1.0, 0.72, 0.46), "light_energy": 2.0, "shadow_blur": 1.5},
		"viewport": _msaa(),
	}

	v[7] = {
		"name": "Soft Pastel",
		"env": {
			"background_mode": Environment.BG_SKY,
			"ambient_light_source": Environment.AMBIENT_SOURCE_SKY,
			"ambient_light_energy": 1.1,
			"tonemap_mode": Environment.TONE_MAPPER_FILMIC,
			"tonemap_exposure": 1.0,
		}.merged(_ssao(1.5, 2.2)),
		"sky": {
			"sky_top_color": Color(0.70, 0.78, 0.95),
			"sky_horizon_color": Color(0.98, 0.90, 0.90),
			"ground_horizon_color": Color(0.94, 0.86, 0.90),
			"ground_bottom_color": Color(0.76, 0.76, 0.92),
			"ground_curve": 0.1,
		},
		"sun": {"elevation": 58.0, "azimuth": -30.0, "light_color": Color(1.0, 0.98, 0.95), "light_energy": 0.9, "light_angular_distance": 6.0, "shadow_opacity": 0.8},
		"blocks": {"shader": VOXEL, "params": {"saturation": 0.78, "brightness": 1.1}},
		"viewport": _msaa(),
	}

	v[8] = {
		"name": "High-Contrast Tactical",
		"env": {
			"background_mode": Environment.BG_COLOR,
			"background_color": Color(0.12, 0.14, 0.2),
			"ambient_light_source": Environment.AMBIENT_SOURCE_COLOR,
			"ambient_light_color": Color(0.4, 0.46, 0.6),
			"ambient_light_energy": 0.6,
			"tonemap_mode": Environment.TONE_MAPPER_ACES,
			"tonemap_exposure": 0.85,
			"adjustment_enabled": true,
			"adjustment_contrast": 1.1,
			"adjustment_saturation": 1.15,
		}.merged(_ssao(1.0, 2.8)),
		"sun": {"elevation": 60.0, "azimuth": -30.0, "light_color": Color(1.0, 0.97, 0.92), "light_energy": 1.4, "shadow_blur": 0.3},
		"viewport": _msaa(),
	}

	v[9] = _merge(_sunlit(), {
		"name": "Vibrance Grade (3D LUT)",
		"lut": {"kind": "grade", "vibrance": 0.7, "green_saturation": 0.75, "green_hue_shift": -8.0, "warm_highlights": 1.0, "cool_shadows": 1.0},
	})

	v[10] = _merge(_sunlit(), {
		"name": "Split-Tone Grade (1D LUT)",
		"sun": {"light_color": Color(1, 1, 1)},
		"lut": {
			"kind": "split",
			"offsets": [0.0, 0.5, 1.0],
			"colors": [Color(0.04, 0.08, 0.15), Color(0.53, 0.5, 0.46), Color(1.0, 0.96, 0.88)],
		},
	})

	v[11] = _merge(_sunlit(), {
		"name": "Tilt-Shift Miniature",
		"env": {"adjustment_enabled": true, "adjustment_saturation": 1.2, "adjustment_contrast": 1.06},
		"camera": {
			"dof_blur_far_enabled": true, "dof_blur_far_distance": 27.0, "dof_blur_far_transition": 10.0,
			"dof_blur_near_enabled": true, "dof_blur_near_distance": 15.0, "dof_blur_near_transition": 5.0,
			"dof_blur_amount": 0.12,
		},
		"camera_b": {"dof_blur_far_distance": 17.0, "dof_blur_far_transition": 8.0, "dof_blur_near_distance": 7.0, "dof_blur_near_transition": 3.0},
	})

	v[12] = _merge(_sunlit(), {
		"name": "Height Haze (fog)",
		"env": {
			"fog_enabled": true,
			"fog_mode": Environment.FOG_MODE_EXPONENTIAL,
			"fog_light_color": Color(0.64, 0.74, 0.87),
			"fog_density": 0.004,
			"fog_height": 1.0,
			"fog_height_density": 2.5,
			"fog_sky_affect": 0.0,
			"fog_aerial_perspective": 0.3,
			"fog_sun_scatter": 0.2,
		},
	})

	v[13] = {
		"name": "Dreamy Bloom",
		"env": {
			"background_mode": Environment.BG_SKY,
			"ambient_light_source": Environment.AMBIENT_SOURCE_SKY,
			"ambient_light_energy": 0.85,
			"tonemap_mode": Environment.TONE_MAPPER_FILMIC,
			"tonemap_exposure": 1.0,
			"glow_enabled": true,
			"glow_intensity": 0.7,
			"glow_strength": 1.1,
			"glow_bloom": 0.08,
			"glow_hdr_threshold": 0.85,
			"glow_blend_mode": Environment.GLOW_BLEND_MODE_SCREEN,
			"glow_levels/2": 0.6,
			"glow_levels/3": 1.0,
			"glow_levels/4": 0.8,
			"glow_levels/5": 1.0,
			"volumetric_fog_enabled": true,
			"volumetric_fog_density": 0.006,
			"volumetric_fog_albedo": Color(1.0, 0.97, 0.92),
			"volumetric_fog_anisotropy": 0.6,
			"volumetric_fog_length": 60.0,
			"adjustment_enabled": true,
			"adjustment_saturation": 1.15,
		}.merged(_ssao(1.2, 1.4)),
		"sky": {
			"sky_top_color": Color(0.52, 0.66, 0.92),
			"sky_horizon_color": Color(0.96, 0.86, 0.9),
			"ground_horizon_color": Color(0.9, 0.8, 0.88),
			"ground_bottom_color": Color(0.55, 0.56, 0.8),
			"ground_curve": 0.1,
		},
		"sun": {"elevation": 45.0, "azimuth": -40.0, "light_color": Color(1.0, 0.93, 0.82), "light_energy": 1.9, "shadow_blur": 1.5},
		"viewport": _msaa(),
	}

	# --- Material changes on the voxel blocks ------------------------------
	v[14] = _merge(_sunlit(), {
		"name": "Toy Plastic (gloss + clearcoat)",
		"env": {"ssr_enabled": true, "ssr_max_steps": 64},
		"blocks": {"standard": {"roughness": 0.2, "metallic_specular": 0.7, "clearcoat_enabled": true, "clearcoat": 1.0, "clearcoat_roughness": 0.1}},
		"units": {"roughness": 0.2, "clearcoat_enabled": true, "clearcoat": 1.0, "clearcoat_roughness": 0.1},
	})

	v[15] = _merge(_sunlit(), {
		"name": "Toon Shading (built-in)",
		"env": {"ambient_light_source": Environment.AMBIENT_SOURCE_COLOR, "ambient_light_color": Color(0.55, 0.6, 0.95), "ambient_light_energy": 0.6},
		"blocks": {"standard": {"diffuse_mode": BaseMaterial3D.DIFFUSE_TOON, "specular_mode": BaseMaterial3D.SPECULAR_DISABLED, "roughness": 0.15}},
		"units": _toon_units(),
		"sun": {"light_energy": 1.5, "shadow_blur": 0.3},
	})

	v[16] = _merge(_sunlit(), {
		"name": "Cel Bands + Violet Shadows",
		"env": {"ambient_light_source": Environment.AMBIENT_SOURCE_COLOR, "ambient_light_color": Color(0.5, 0.55, 0.9), "ambient_light_energy": 0.45},
		"blocks": {"shader": VOXEL, "params": {"toon_bands": 2.0, "toon_softness": 0.03, "shade_glow": Vector3(0.05, 0.035, 0.12)}},
		"units": _toon_units(),
		"sun": {"light_energy": 1.6, "shadow_blur": 0.3},
	})

	v[17] = _merge(_sunlit(), {
		"name": "Hand-Shaded Faces",
		"env": {"ambient_light_energy": 0.85},
		"blocks": {"shader": VOXEL, "params": {
			"top_tint": Vector3(1.08, 1.06, 0.97),
			"side_z_tint": Vector3(0.86, 0.86, 1.0),
			"side_x_tint": Vector3(0.62, 0.64, 0.92),
			"contact_ao": 0.45,
			"skirt_darken": 0.5,
		}},
		"sun": {"light_energy": 1.15},
	})

	v[18] = _merge(_sunlit(), {
		"name": "Tamed Greens (palette remap)",
		"blocks": {"shader": VOXEL, "params": {"green_saturation": 0.72, "green_value": 1.06, "green_hue_shift": -10.0}},
	})

	v[19] = _merge(_sunlit(), {
		"name": "Tactical Readability (grid, AO, height)",
		"blocks": {"shader": VOXEL, "params": {
			"edge_darken": 0.18, "edge_width": 0.02,
			"contact_ao": 0.55, "contact_ao_height": 0.7,
			"height_gain": 0.08, "skirt_darken": 0.6,
			"green_saturation": 0.85,
		}, "crate_params": {"edge_darken": 0.0}},
	})

	v[20] = {
		"name": "Flat Colour (Crossy Road style)",
		"env": {
			"background_mode": Environment.BG_COLOR,
			"background_color": Color(0.55, 0.8, 0.95),
			"ambient_light_source": Environment.AMBIENT_SOURCE_COLOR,
			"ambient_light_color": Color(0.95, 0.97, 1.0),
			"ambient_light_energy": 0.6,
			"tonemap_mode": Environment.TONE_MAPPER_LINEAR,
			"adjustment_enabled": true,
			"adjustment_saturation": 1.1,
		},
		"blocks": {"shader": VOXEL, "params": {
			"top_tint": Vector3(1.0, 1.0, 0.95),
			"side_z_tint": Vector3(0.86, 0.86, 0.92),
			"side_x_tint": Vector3(0.70, 0.72, 0.86),
			"shade_glow": Vector3(0.02, 0.05, 0.14),
		}},
		"sun": {"elevation": 60.0, "azimuth": -30.0, "light_energy": 0.8, "light_color": Color(1, 1, 1), "shadow_blur": 0.2},
		"viewport": _msaa(),
	}

	# --- Outline and pixel post-processing ---------------------------------
	# MSAA averages normals along edges and hides creases from the outline
	# pass, so these use SMAA instead.
	v[21] = _merge(_sunlit(), {
		"name": "Ink Outlines",
		"viewport": _smaa(),
		"outline": {"line_color": Color(0.10, 0.07, 0.14), "line_opacity": 0.9, "line_width": 1.0},
	})

	v[22] = _merge(v[15], {
		"name": "Cartoon (toon + bold outlines)",
		"viewport": _smaa(),
		"env": {"adjustment_enabled": true, "adjustment_saturation": 1.15},
		"outline": {"line_color": Color(0.08, 0.05, 0.1), "line_opacity": 1.0, "line_width": 2.0, "crease_opacity": 0.6},
	})

	v[23] = _merge(_sunlit(), {
		"name": "Bevelled Edge Highlights",
		"viewport": _smaa(),
		"outline": {
			"line_tint_mix": 1.0, "line_darken": 0.5, "line_opacity": 0.7,
			"crease_width": 2.0, "highlight_opacity": 0.7, "highlight_min_up": 0.5,
			"crease_opacity": 0.4,
		},
	})

	v[24] = _merge(_sunlit(), {
		"name": "3D Pixel Art (nearest scaling)",
		"viewport": {"msaa_3d": Viewport.MSAA_DISABLED, "scaling_3d_mode": 5, "scaling_3d_scale": 0.33},
		"sun": {"shadow_blur": 0.0},
		"outline": {
			"line_tint_mix": 1.0, "line_darken": 0.4, "line_opacity": 1.0, "line_width": 1.0,
			"highlight_opacity": 0.6, "highlight_min_up": 0.5, "crease_opacity": 0.4,
		},
	})

	# --- Themed palettes ----------------------------------------------------
	v[25] = {
		"name": "Twin Suns (desert world)",
		"env": {
			"background_mode": Environment.BG_SKY,
			"ambient_light_source": Environment.AMBIENT_SOURCE_SKY,
			"ambient_light_energy": 0.7,
			"tonemap_mode": Environment.TONE_MAPPER_FILMIC,
			"adjustment_enabled": true,
			"adjustment_saturation": 1.05,
		}.merged(_ssao(1.2, 1.6)),
		"sky": {
			"sky_top_color": Color(0.45, 0.62, 0.85),
			"sky_horizon_color": Color(0.98, 0.86, 0.7),
			"ground_horizon_color": Color(0.92, 0.78, 0.6),
			"ground_bottom_color": Color(0.7, 0.52, 0.36),
			"ground_curve": 0.1,
		},
		"sun": {"elevation": 40.0, "azimuth": -50.0, "light_color": Color(1.0, 0.78, 0.5), "light_energy": 1.3},
		"extra_lights": [{"elevation": 30.0, "azimuth": 20.0, "light_color": Color(1.0, 0.92, 0.7), "light_energy": 0.9, "shadow_enabled": true}],
		"blocks": {"shader": VOXEL, "params": {"green_hue_shift": -25.0, "green_saturation": 0.75}},
		"viewport": _msaa(),
	}

	v[26] = {
		"name": "Alien Twilight (sci-fi)",
		"env": {
			"background_mode": Environment.BG_SKY,
			"ambient_light_source": Environment.AMBIENT_SOURCE_COLOR,
			"ambient_light_color": Color(0.2, 0.75, 0.8),
			"ambient_light_energy": 0.5,
			"tonemap_mode": Environment.TONE_MAPPER_ACES,
			"glow_enabled": true,
			"glow_intensity": 0.6,
			"adjustment_enabled": true,
			"adjustment_saturation": 1.15,
		}.merged(_ssao(1.2, 1.8)),
		"sky": {
			"sky_top_color": Color(0.10, 0.12, 0.35),
			"sky_horizon_color": Color(0.55, 0.3, 0.6),
			"ground_horizon_color": Color(0.3, 0.2, 0.45),
			"ground_bottom_color": Color(0.06, 0.08, 0.2),
			"ground_curve": 0.1,
		},
		"sun": {"elevation": 35.0, "azimuth": -40.0, "light_color": Color(1.0, 0.55, 0.75), "light_energy": 1.6},
		"viewport": _msaa(),
	}

	# --- Camera ---------------------------------------------------------------
	v[27] = _merge(_sunlit(), {
		"name": "Long-Lens Diorama (FOV 40)",
		"fov": 40.0,
	})

	# --- A blend of the strongest ideas -------------------------------------
	v[28] = _merge(_sunlit(), {
		"name": "Recommended Blend",
		"viewport": _smaa(),
		"sun": {"light_angular_distance": 1.0},
		"blocks": {"shader": VOXEL, "params": {
			"green_saturation": 0.82, "green_value": 1.03,
			"top_tint": Vector3(1.04, 1.03, 0.98),
			"side_z_tint": Vector3(0.92, 0.92, 1.0),
			"side_x_tint": Vector3(0.78, 0.8, 0.95),
			"contact_ao": 0.4, "skirt_darken": 0.5, "height_gain": 0.05,
		}},
		"outline": {
			"line_tint_mix": 1.0, "line_darken": 0.45, "line_opacity": 0.8,
			"crease_width": 2.0, "highlight_opacity": 0.55, "highlight_min_up": 0.5, "crease_opacity": 0.3,
		},
		"lut": {"kind": "grade", "vibrance": 0.45, "cool_shadows": 0.8},
	})
	return v


## Clear day, sun from the camera's left, sky ambient, soft AO. The base for
## most variants that only change one thing.
static func _sunlit() -> Dictionary:
	return {
		"env": {
			"background_mode": Environment.BG_SKY,
			"ambient_light_source": Environment.AMBIENT_SOURCE_SKY,
			"ambient_light_energy": 0.8,
			"tonemap_mode": Environment.TONE_MAPPER_FILMIC,
			"tonemap_exposure": 1.0,
		}.merged(_ssao(1.2, 1.6)),
		"sky": _sky_day(),
		"sun": {"elevation": 50.0, "azimuth": -35.0, "light_color": Color(1.0, 0.95, 0.86), "light_energy": 1.3, "shadow_blur": 1.0},
		"viewport": _msaa(),
	}


static func _sky_day() -> Dictionary:
	return {
		"sky_top_color": Color(0.28, 0.50, 0.85),
		"sky_horizon_color": Color(0.70, 0.80, 0.92),
		"sky_curve": 0.15,
		"ground_horizon_color": Color(0.62, 0.72, 0.84),
		"ground_bottom_color": Color(0.32, 0.46, 0.66),
		"ground_curve": 0.1,
	}


static func _sky_studio() -> Dictionary:
	return {
		"sky_top_color": Color(0.74, 0.79, 0.88),
		"sky_horizon_color": Color(0.92, 0.93, 0.95),
		"ground_horizon_color": Color(0.82, 0.84, 0.88),
		"ground_bottom_color": Color(0.60, 0.64, 0.73),
		"ground_curve": 0.1,
	}


static func _toon_units() -> Dictionary:
	return {"diffuse_mode": BaseMaterial3D.DIFFUSE_TOON, "specular_mode": BaseMaterial3D.SPECULAR_TOON, "roughness": 0.3, "rim_enabled": true, "rim": 0.5, "rim_tint": 0.3}


static func _ssao(radius: float, intensity: float) -> Dictionary:
	return {"ssao_enabled": true, "ssao_radius": radius, "ssao_intensity": intensity, "ssao_power": 1.6, "ssao_detail": 0.5}


static func _msaa() -> Dictionary:
	return {"msaa_3d": Viewport.MSAA_4X}


static func _smaa() -> Dictionary:
	return {"msaa_3d": Viewport.MSAA_DISABLED, "screen_space_aa": Viewport.SCREEN_SPACE_AA_SMAA}


## Deep merge: nested dictionaries merge, everything else is replaced.
static func _merge(base: Dictionary, over: Dictionary) -> Dictionary:
	var out := base.duplicate(true)
	for key in over:
		if out.has(key) and out[key] is Dictionary and over[key] is Dictionary:
			out[key] = _merge(out[key], over[key])
		else:
			out[key] = over[key]
	return out
