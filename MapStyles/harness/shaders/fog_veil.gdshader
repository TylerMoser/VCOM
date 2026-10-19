// The fog of war: polygons over the land (copies of the counties' outlines) or over the whole sheet,
// drawn over the land, forests, borders, water, roads and bridges and under the settlements, the
// party and the lines left known (map_line_fogged.gdshader). For the variants of proposal 20 in
// MapStyles/20-fog-of-war/; the original 20 is fog.gdshader. Where the party has not been
// (fog_common.gdshaderinc), the fog; where it has, clear, or veiled as memory.
shader_type canvas_item;

#include "res://_probe/shaders/fog_common.gdshaderinc"

uniform vec4 veil : source_color = vec4(0.93, 0.9, 0.83, 1.0);
uniform float opacity : hint_range(0.0, 1.0) = 0.93;
// How the fog looks: 0 a veil of [veil]; 1 the land under it in grey, lighter by [grey_light];
// 2 the land under it out of focus ([blur_lod], a mip level of the screen); 3 clouds, [cloud_scale]
// map units across; 4 a veil hatched by an engraver, lines [hatch_px] screen pixels apart in [ink].
uniform int look = 0;
uniform sampler2D screen : hint_screen_texture, filter_linear_mipmap;
uniform float grey_light : hint_range(0.0, 1.0) = 0.35;
uniform float blur_lod = 3.5;
uniform float grain : hint_range(0.0, 0.3) = 0.07;
uniform float cloud_scale = 700.0;
uniform vec4 ink : source_color = vec4(0.42, 0.33, 0.22, 0.45);
uniform float hatch_px = 6.0;
uniform float hatch_width : hint_range(0.05, 0.5) = 0.16;

// Thicker away from what has been seen (distance_lod over 0): near_opacity at the edge, [opacity]
// where the mask blurred to that mip level has nothing.
uniform float distance_lod = 0.0;
uniform float near_opacity : hint_range(0.0, 1.0) = 0.45;
// What is in sight now: within [sight] of [party] (0: none). The rest of what has been explored is
// remembered: veiled by [memory], in grey with memory_look 1.
uniform vec2 party = vec2(0.0);
uniform float sight = 0.0;
uniform float memory : hint_range(0.0, 1.0) = 0.0;
uniform int memory_look = 0;
// The fog comes back: what was seen longest ago (the mask's G) veiled by up to this much.
uniform float age_fade : hint_range(0.0, 1.0) = 0.0;

// A line along the edge (alpha 0: none), [rim_px] screen pixels wide, dashed every rim_dash px.
uniform vec4 rim : source_color = vec4(0.0);
uniform float rim_px = 1.6;
uniform float rim_dash = 0.0;
// A browned band on the fog's side of the edge, as a burnt page has (alpha 0: none).
uniform vec4 burn : source_color = vec4(0.0);
uniform float burn_px = 18.0;

// An old map's hill marks on the fog where the land is high (hills_from in elevation.png's 0 to 1;
// over 1 none), [hills_px] screen pixels apart, in [ink].
uniform sampler2D elevation : filter_linear_mipmap, repeat_disable;
uniform float hills_from = 2.0;
uniform float hills_px = 24.0;
// The forests through the fog as a hatch, where battles are met (alpha 0: none).
uniform sampler2D forests : filter_linear_mipmap, repeat_disable;
uniform vec4 forest_ink : source_color = vec4(0.0);
uniform float forest_px = 6.0;

varying float px_per_unit;

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
	px_per_unit = length((CANVAS_MATRIX * MODEL_MATRIX)[0].xy);
}

float fbm(vec2 p) {
	mat2 turn = mat2(vec2(0.8, 0.6), vec2(-0.6, 0.8));
	float sum = fog_noise(p) * 0.5;
	p = turn * p * 2.03 + 13.7;
	sum += fog_noise(p) * 0.28;
	p = turn * p * 2.01 + 7.1;
	sum += fog_noise(p) * 0.14;
	p = turn * p * 2.02 + 3.3;
	sum += fog_noise(p) * 0.08;
	return sum;
}

// Lines across the screen, [px] pixels apart, at 45 degrees, at the pixel [frag]: their coverage.
float hatch_lines(vec2 frag, float px, float width) {
	float v = (frag.x + frag.y) / px;
	float aa = max(fwidth(v), 1e-5);
	float f = abs(fract(v) - 0.5);
	return 1.0 - smoothstep(width * 0.5 - aa, width * 0.5 + aa, f);
}

// Hill marks (a small arch) on a grid of [cell] map units, where the land is over hills_from.
float hills(float cell) {
	vec2 g = world / cell;
	float aa = max(fwidth(g.x), 1e-5) * 0.8;
	float best = 0.0;
	vec2 base_cell = floor(g);
	for (int y = -1; y <= 1; y++) {
		for (int x = -1; x <= 1; x++) {
			vec2 c = base_cell + vec2(float(x), float(y));
			vec2 centre = c + 0.5 + (vec2(fog_hash(c + 71.0), fog_hash(c + 13.0)) - 0.5) * 0.4;
			float h = texture(elevation, centre * cell / sheet).r;
			if (h < hills_from || fog_hash(c + 5.0) > 0.75) {
				continue;
			}
			float s = 0.55 + (h - hills_from) * 1.2;
			vec2 p = (g - centre) / s;
			float ring = abs(length(p - vec2(0.0, 0.25)) - 0.3) - 0.045;
			float d = max(ring, p.y - 0.1);
			best = max(best, 1.0 - smoothstep(-aa / s, aa / s, d));
		}
	}
	return best;
}

void fragment() {
	vec2 uv = world / sheet;
	float raw = fog_raw(world);
	float explored = fog_explored(raw);
	float fog = 1.0 - explored;

	// The fog's own colour.
	vec3 rgb = veil.rgb;
	float a = opacity;
	if (look == 1 || look == 2 || memory_look == 1) {
		vec3 under = texture(screen, SCREEN_UV).rgb;
		if (look == 1) {
			float grey = dot(under, vec3(0.299, 0.587, 0.114));
			rgb = mix(vec3(grey), vec3(1.0), grey_light) * mix(vec3(1.0), veil.rgb, 0.25);
		} else if (look == 2) {
			rgb = mix(textureLod(screen, SCREEN_UV, blur_lod).rgb, veil.rgb, 0.18);
		}
	}
	if (look == 3) {
		float c = fbm(world / cloud_scale);
		float puff = smoothstep(0.32, 0.72, c);
		rgb = mix(veil.rgb * 0.82, vec3(1.0), puff);
		a = opacity * (0.75 + puff * 0.25);
	}
	float grain_n = fog_noise(world / 23.0) * 0.5 + fog_noise(world / 211.0) * 0.5;
	rgb *= 1.0 - grain + grain_n * grain * 1.6;
	if (look == 4) {
		rgb = mix(rgb, ink.rgb, hatch_lines(FRAGCOORD.xy, hatch_px, hatch_width) * ink.a);
	}
	if (hills_from <= 1.0) {
		float level = log2(hills_px / max(px_per_unit, 1e-6));
		float l0 = floor(level);
		float m = mix(hills(exp2(l0)), hills(exp2(l0 + 1.0)), level - l0);
		rgb = mix(rgb, ink.rgb, m * ink.a * 1.4);
	}
	if (forest_ink.a > 0.0) {
		float f = smoothstep(0.35, 0.65, texture(forests, uv).r);
		rgb = mix(rgb, forest_ink.rgb, f * hatch_lines(FRAGCOORD.xy, forest_px, 0.22) * forest_ink.a);
	}
	if (distance_lod > 0.0) {
		float far = 1.0 - textureLod(mask, uv, distance_lod).r;
		a *= mix(near_opacity / max(opacity, 1e-3), 1.0, smoothstep(0.0, 0.85, far));
	}
	float fog_a = fog * a;

	// What has been explored: clear where in sight, else remembered, and fogged again by age.
	float out_of_sight = sight > 0.0 ? smoothstep(sight * 0.82, sight, distance(world, party)) : 0.0;
	float remembered = explored * max(memory * out_of_sight, age_fade * (1.0 - texture(mask, uv).g));
	vec3 memory_rgb = veil.rgb;
	if (memory_look == 1) {
		vec3 under = texture(screen, SCREEN_UV).rgb;
		float grey = dot(under, vec3(0.299, 0.587, 0.114));
		memory_rgb = mix(vec3(grey), vec3(1.0), 0.15);
	}
	float mem_a = remembered * (memory_look == 1 ? 1.0 : opacity);
	vec3 out_rgb = mix(memory_rgb, rgb, fog_a / max(fog_a + mem_a, 1e-4));
	float out_a = fog_a + mem_a * (1.0 - fog_a);

	// The edge: how many screen pixels from the middle of the mask's edge, either side.
	float px_from_edge = (raw - 0.5) / max(fwidth(raw), 1e-5);
	if (burn.a > 0.0) {
		float b = (1.0 - smoothstep(0.0, burn_px, -px_from_edge)) * step(px_from_edge, 0.0);
		out_rgb = mix(out_rgb, burn.rgb, b * burn.a);
		out_a = max(out_a, b * burn.a);
	}
	if (rim.a > 0.0) {
		float line = 1.0 - smoothstep(rim_px * 0.5 - 0.5, rim_px * 0.5 + 0.5, abs(px_from_edge));
		if (rim_dash > 0.0) {
			float along = (FRAGCOORD.x - FRAGCOORD.y) / rim_dash;
			line *= step(0.5, fract(along * 0.5));
		}
		out_rgb = mix(out_rgb, rim.rgb, line * rim.a);
		out_a = max(out_a, line * rim.a);
	}
	COLOR = vec4(out_rgb, out_a * COLOR.a);
}
