// The land's polygons (every county, and the islands in lakes), coloured by
// more than one flat colour. Each part is off at its default:
//
//  - elevation: a colour ramp by the ground's height (elevation.png, the
//    square root of the height's share of 3,352 m), mixed in by [ramp_mix];
//  - band: along the borders between kingdoms (kingdom_edge.png, how far each
//    pixel is from one as the scene draws them, stored as the square root of
//    its share of [edge_reach] pixels), the polygon's own colour shows in a
//    band [band_px] screen pixels wide, fading into [band_base] away from the
//    border, so a county coloured by its kingdom gets its kingdom's colour
//    along the kingdom's edge alone;
//  - paper: a faint mottle and grain, anchored to the map, that keeps about
//    the same size on the screen at every zoom.
//
// The polygon's colour (COLOR) is the base. Pictures are read in the map's own
// space, the MapCreation sheet being 10,385 by 13,400 units.
shader_type canvas_item;

uniform vec2 sheet = vec2(10385.0, 13400.0);

uniform sampler2D elevation : filter_linear_mipmap, repeat_disable;
uniform sampler2D ramp : source_color, filter_linear, repeat_disable;
uniform float ramp_mix : hint_range(0.0, 1.0) = 0.0;

uniform sampler2D edge : filter_linear_mipmap, repeat_disable;
// How far kingdom_edge.png reaches, in its pixels (make_data.py's EDGE_REACH).
uniform float edge_reach = 160.0;
uniform float band_px = 0.0;
uniform vec4 band_base : source_color = vec4(1.0);
uniform float band_strength : hint_range(0.0, 1.0) = 1.0;
// A thin darker rim right at the border, as a share of the band.
uniform float band_rim = 0.0;

uniform float paper : hint_range(0.0, 1.0) = 0.0;
uniform vec4 paper_dark : source_color = vec4(0.55, 0.42, 0.25, 1.0);

// Palette mode: the polygon's colour holds its kingdom's number in red and its
// duchy's in green (n / 255), and the colour drawn is palette[kingdom], every
// other duchy [duchy_shade] darker. Changing the palette recolours the whole
// land for free, where setting 233 polygons' colours rebuilds each: map modes.
uniform bool palette_mode = false;
uniform vec4 palette[10] : source_color;
uniform float duchy_shade : hint_range(0.0, 0.3) = 0.0;

varying vec2 world;
varying float px_per_unit;

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
	px_per_unit = length((CANVAS_MATRIX * MODEL_MATRIX)[0].xy);
}

// A hash of a lattice point, 0 to 1. On integers, so it holds at the large
// coordinates of the map (a float hash's fract() of a product went coarse
// there and drew squares).
float hash(vec2 p) {
	uvec2 q = uvec2(ivec2(floor(p)) + ivec2(65536));
	uint h = (q.x * 1597334677u) ^ (q.y * 3812015801u);
	h = h * 747796405u + 2891336453u;
	h = ((h >> ((h >> 28u) + 4u)) ^ h) * 277803737u;
	h = (h >> 22u) ^ h;
	return float(h) * (1.0 / 4294967295.0);
}

float value_noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

// Three octaves, each turned against the last, so no grid shows.
float fbm(vec2 p) {
	mat2 turn = mat2(vec2(0.8, 0.6), vec2(-0.6, 0.8));
	float sum = value_noise(p) * 0.55;
	p = turn * p * 2.03 + 13.7;
	sum += value_noise(p) * 0.3;
	p = turn * p * 2.01 + 7.1;
	sum += value_noise(p) * 0.15;
	return sum;
}

// Noise whose features keep near [px] screen pixels at any zoom: two scales a
// power of two apart in the map's units, faded across as the zoom moves.
float zoom_noise(vec2 p, float px) {
	float want = px / max(px_per_unit, 1e-6);
	float level = log2(want);
	float l0 = floor(level);
	float t = level - l0;
	float a = fbm(p / exp2(l0) + 17.0 * l0);
	float b = fbm(p / exp2(l0 + 1.0) + 17.0 * (l0 + 1.0));
	return mix(a, b, t);
}

void fragment() {
	vec2 uv = world / sheet;
	vec3 col = COLOR.rgb;
	if (palette_mode) {
		int kingdom = clamp(int(round(COLOR.r * 255.0)), 0, 9);
		int duchy = int(round(COLOR.g * 255.0));
		col = palette[kingdom].rgb;
		if (duchy % 2 == 0) {
			col *= 1.0 - duchy_shade;
		}
	}

	if (ramp_mix > 0.0) {
		float h = texture(elevation, uv).r;
		col = mix(col, texture(ramp, vec2(h, 0.5)).rgb, ramp_mix);
	}

	if (band_px > 0.0) {
		// The square root of the share of edge_reach pixels; a pixel is 3.35 units.
		float stored = texture(edge, uv).r;
		float units = stored * stored * edge_reach * 3.35;
		float px = units * px_per_unit;
		float band = 1.0 - smoothstep(0.0, band_px, px);
		band = band * band * band_strength;
		vec3 tinted = mix(band_base.rgb, col, band);
		if (band_rim > 0.0) {
			float rim = 1.0 - smoothstep(0.0, band_px * band_rim, px);
			tinted = mix(tinted, col * 0.8, rim * band_strength);
		}
		col = tinted;
	}

	if (paper > 0.0) {
		// A broad mottle, and a fine grain over it.
		float mottle = zoom_noise(world, 260.0);
		float grain = zoom_noise(world + 311.0, 9.0);
		float dark = smoothstep(0.42, 0.8, mottle) * 0.85 + (grain - 0.5) * 0.3;
		col = mix(col, col * paper_dark.rgb * 1.25, paper * clamp(dark, 0.0, 1.0));
	}

	COLOR = vec4(col, COLOR.a);
}
