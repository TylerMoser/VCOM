// A piece of forest (a Forest polygon) drawn as an area with a pattern of small
// marks over its fill, the way topographic maps draw woodland, so that it
// reads as "forest here" and never as one more line.
//
// The marks are anchored to the map but keep about [cell_px] screen pixels
// apart at every zoom: their spacing in the map's units is a power of two,
// and as the zoom moves the next power fades in while the last fades out.
//
//   glyph 0  none (fill only)
//         1  conifer: a small upright triangle on a stem
//         2  broadleaf: a small round crown on a stem
//         3  marsh: a short line with three tufts
//         4  dense canopy: three overlapping round crowns
//         5  stipple: dots
//         6  hatch: diagonal lines
//
// The polygon's own colour (COLOR.rgb) is the fill. Keep the polygon's alpha
// at 1 and give the fill's see-through amount in [fill_alpha]: COLOR.a is then
// only MapDetail's fading, which multiplies everything here.
shader_type canvas_item;

uniform int glyph = 1;
uniform vec4 mark : source_color = vec4(0.1, 0.3, 0.15, 0.7);
uniform float fill_alpha : hint_range(0.0, 1.0) = 1.0;
uniform float cell_px = 14.0;
// The mark's size, as a share of a cell.
uniform float mark_size : hint_range(0.1, 1.5) = 0.55;
// The share of cells with a mark.
uniform float density : hint_range(0.0, 1.0) = 0.85;
// How far a mark may wander from its cell's middle, as a share of a cell.
uniform float jitter : hint_range(0.0, 0.5) = 0.22;
// With alpha over 0, the fill's colour instead of the polygon's own: a whole
// kind recoloured for free (map modes).
uniform vec4 fill_override : source_color = vec4(0.0);
// Fades the piece away from [focus] (map units): whole within [focus_inner],
// [focus_floor] beyond [focus_outer]; off while focus_outer is 0.
uniform vec2 focus = vec2(0.0);
uniform float focus_inner = 0.0;
uniform float focus_outer = 0.0;
uniform float focus_floor : hint_range(0.0, 1.0) = 0.0;

varying vec2 world;
varying float px_per_unit;

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
	px_per_unit = length((CANVAS_MATRIX * MODEL_MATRIX)[0].xy);
}

// A hash of a lattice cell, 0 to 1, on integers so it holds at the map's
// large coordinates; [seed] gives each cell further numbers of its own.
float hash(vec2 p, uint seed) {
	uvec2 q = uvec2(ivec2(floor(p)) + ivec2(65536));
	uint h = (q.x * 1597334677u) ^ (q.y * 3812015801u) ^ (seed * 2246822519u);
	h = h * 747796405u + 2891336453u;
	h = ((h >> ((h >> 28u) + 4u)) ^ h) * 277803737u;
	h = (h >> 22u) ^ h;
	return float(h) * (1.0 / 4294967295.0);
}

float sd_circle(vec2 p, float r) {
	return length(p) - r;
}

float sd_box(vec2 p, vec2 b) {
	vec2 d = abs(p) - b;
	return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

// An isosceles triangle with its apex at the origin and its base [q.y] below
// it (the screen's y runs down), [q.x] either side: Inigo Quilez's distance.
float sd_triangle(vec2 p, vec2 q) {
	p.x = abs(p.x);
	vec2 a = p - q * clamp(dot(p, q) / dot(q, q), 0.0, 1.0);
	vec2 b = p - q * vec2(clamp(p.x / q.x, 0.0, 1.0), 1.0);
	float s = -sign(q.y);
	vec2 d = min(vec2(dot(a, a), s * (p.x * q.y - p.y * q.x)), vec2(dot(b, b), s * (p.y - q.y)));
	return -sqrt(d.x) * sign(d.y);
}

// Coverage of one mark at p (cell-local, -0.5 to 0.5 across), smoothed over aa.
float glyph_at(vec2 p, float s, float aa) {
	float d = 1e3;
	if (glyph == 1) {
		float crown = sd_triangle(p - vec2(0.0, -0.42 * s), vec2(0.3 * s, 0.68 * s));
		float stem = sd_box(p - vec2(0.0, 0.32 * s), vec2(0.05 * s, 0.1 * s));
		d = min(crown, stem);
	} else if (glyph == 2) {
		float crown = sd_circle(p - vec2(0.0, -0.1 * s), 0.27 * s);
		float stem = sd_box(p - vec2(0.0, 0.25 * s), vec2(0.05 * s, 0.14 * s));
		d = min(crown, stem);
	} else if (glyph == 3) {
		float base = sd_box(p - vec2(0.0, 0.18 * s), vec2(0.32 * s, 0.04 * s));
		float t1 = sd_box(p - vec2(0.0, 0.02 * s), vec2(0.04 * s, 0.17 * s));
		float t2 = sd_box(p - vec2(-0.16 * s, 0.07 * s), vec2(0.035 * s, 0.11 * s));
		float t3 = sd_box(p - vec2(0.16 * s, 0.07 * s), vec2(0.035 * s, 0.11 * s));
		d = min(base, min(t1, min(t2, t3)));
	} else if (glyph == 4) {
		d = min(sd_circle(p - vec2(-0.14, 0.02) * s, 0.25 * s), sd_circle(p - vec2(0.15, -0.04) * s, 0.23 * s));
		d = min(d, sd_circle(p - vec2(0.02, -0.2) * s, 0.21 * s));
	} else if (glyph == 5) {
		d = sd_circle(p, 0.12 * s);
	}
	return 1.0 - smoothstep(-aa, aa, d);
}

// The marks' coverage at a spacing of [cell] map units.
float marks(float cell) {
	vec2 g = world / cell;
	float aa = max(fwidth(g.x), 1e-5) * 0.75;
	float best = 0.0;
	vec2 base = floor(g);
	// This cell and its neighbours, since a jittered mark can spill over.
	for (int y = -1; y <= 1; y++) {
		for (int x = -1; x <= 1; x++) {
			vec2 c = base + vec2(float(x), float(y));
			if (hash(c, 0u) > density) {
				continue;
			}
			vec2 offset = (vec2(hash(c, 1u), hash(c, 2u)) - 0.5) * 2.0 * jitter;
			best = max(best, glyph_at(g - (c + 0.5 + offset), mark_size, aa));
		}
	}
	return best;
}

float hatch(float cell) {
	float v = (world.x + world.y) / cell;
	float aa = max(fwidth(v), 1e-5);
	float f = abs(fract(v) - 0.5);
	float half_width = 0.5 * mark_size * 0.5;
	return 1.0 - smoothstep(half_width - aa, half_width + aa, f);
}

void fragment() {
	float fade = COLOR.a;
	if (focus_outer > 0.0) {
		fade *= mix(1.0, focus_floor, smoothstep(focus_inner, focus_outer, distance(world, focus)));
	}
	vec3 own = fill_override.a > 0.0 ? fill_override.rgb : COLOR.rgb;
	float cover = 0.0;
	if (glyph > 0) {
		float want = cell_px / max(px_per_unit, 1e-6);
		float level = log2(want);
		float l0 = floor(level);
		float t = level - l0;
		if (glyph == 6) {
			cover = mix(hatch(exp2(l0)), hatch(exp2(l0 + 1.0)), t);
		} else {
			cover = mix(marks(exp2(l0)), marks(exp2(l0 + 1.0)), t);
		}
	}
	float m = cover * mark.a;
	float a = m + fill_alpha * (1.0 - m);
	vec3 rgb = (mark.rgb * m + own * fill_alpha * (1.0 - m)) / max(a, 1e-4);
	COLOR = vec4(rgb, a * fade);
}
