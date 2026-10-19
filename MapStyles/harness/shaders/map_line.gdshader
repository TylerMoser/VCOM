// Draws a Line2D as a map symbol: a fill with a casing at its edges, a stripe
// down its middle, and dashes or dash-dots along it, each edge anti-aliased;
// or, in coast mode, a shoreline with rings of water lines off it; and
// optionally faded with the distance from a point (a focus).
//
// The line must have texture_mode TILE, which is what gives a Line2D UVs (the
// harness gives it a 1 by 1 white texture as well, which turned out not to be
// needed). UV.x then counts the line's widths along it, and UV.y runs 0 to 1 across it,
// so every length here is in widths of the line: the pattern grows and shrinks
// with the line, which MapDetail holds near a width on the screen.
//
// The line's default_color (as COLOR) gives the fill's colour when
// fill_from_line is on, and its alpha always multiplies the result: keep the
// line's own alpha at 1 and give see-through amounts here, so that COLOR.a is
// only the fading MapDetail and BorderSwitch do by modulate.
shader_type canvas_item;

uniform bool fill_from_line = true;
uniform vec4 fill : source_color = vec4(1.0);
uniform float fill_alpha : hint_range(0.0, 1.0) = 1.0;

// The casing: this share of the half-width on each side, in its own colour.
// Below [casing_min_px] screen pixels across, a line is too thin to show a
// casing and a fill: it is drawn solid in [narrow] instead (when narrow's
// alpha is above 0), fading across 2 pixels.
uniform vec4 casing : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float casing_share : hint_range(0.0, 1.0) = 0.0;
uniform float casing_min_px = 0.0;
uniform vec4 narrow : source_color = vec4(0.0);

// A stripe down the middle, this share of the whole width, solid or dashed.
uniform vec4 stripe : source_color = vec4(1.0);
uniform float stripe_share : hint_range(0.0, 1.0) = 0.0;
uniform float stripe_dash = 0.0;
uniform float stripe_gap = 1.0;

// The whole line dashed: a dash of [dash] widths, then [gap]; with [dot] > 0,
// a round dot of that diameter after each dash, [dot_gap] either side of it
// ([gap] when 0). [dash] 0 is a solid line; [dash] 0 with [dot] > 0 is dots.
uniform float dash = 0.0;
uniform float gap = 1.0;
uniform float dot = 0.0;
uniform float dot_gap = 0.0;
// Round the ends of the dashes.
uniform bool round_dashes = false;

// Coast mode, for the coast's lines, which are centred on the land's edge with
// their inner half under the land: nothing is drawn but a shoreline of
// [shore_share] of the half-width in [shore], and [rings] thin rings of
// [ring] out over the water, each fainter than the last. Rings closer than
// [ring_min_px] on the screen fade away.
uniform bool coast_mode = false;
uniform vec4 shore : source_color = vec4(0.2, 0.35, 0.5, 1.0);
uniform float shore_share : hint_range(0.0, 1.0) = 0.15;
uniform vec4 ring : source_color = vec4(0.3, 0.5, 0.7, 0.6);
uniform int rings = 3;
uniform float ring_share : hint_range(0.0, 0.3) = 0.05;
uniform float ring_min_px = 3.0;

// Fades the line away from [focus] (in the map's units): whole within
// [focus_inner], down to [focus_floor] beyond [focus_outer]. Off while
// focus_outer is 0.
uniform vec2 focus = vec2(0.0);
uniform float focus_inner = 0.0;
uniform float focus_outer = 0.0;
uniform float focus_floor : hint_range(0.0, 1.0) = 0.0;

// How much of a pixel an edge is smoothed over.
uniform float softness = 1.0;

varying vec2 world;

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

// Coverage of [a, b] at t, smoothed over w, for a pattern repeating every period.
float span(float t, float a, float b, float w, float period) {
	float best = 0.0;
	for (int k = -1; k <= 1; k++) {
		float x = t + float(k) * period;
		best = max(best, clamp(min(x - a, b - x) / w + 0.5, 0.0, 1.0));
	}
	return best;
}

// Coverage of a disc of radius r centred at (c, middle of the line).
float disc(float t, float y, float c, float r, float w, float period) {
	float best = 0.0;
	for (int k = -1; k <= 1; k++) {
		float d = length(vec2(t + float(k) * period - c, y));
		best = max(best, clamp((r - d) / w + 0.5, 0.0, 1.0));
	}
	return best;
}

// The line as a symbol (fill, casing, stripe, dashes) at [uv], its own colour
// [line_color]: everything but coast mode.
vec4 draw_line_symbol(vec2 uv, vec4 line_color, float across, float px, float wa, float wx, float fade) {
	vec4 col = fill_from_line ? vec4(line_color.rgb, fill_alpha) : vec4(fill.rgb, fill.a * fill_alpha);
	if (casing_share > 0.0) {
		float wide = casing_min_px > 0.0 ? smoothstep(casing_min_px, casing_min_px + 2.0, px) : 1.0;
		float edge = smoothstep(1.0 - casing_share - wa, 1.0 - casing_share + wa, across) * wide;
		col = mix(col, casing, edge);
		if (narrow.a > 0.0) {
			col = mix(narrow, col, wide);
		}
	}
	if (stripe_share > 0.0) {
		float s = 1.0 - smoothstep(stripe_share - wa, stripe_share + wa, across);
		if (stripe_dash > 0.0) {
			float period = stripe_dash + stripe_gap;
			s *= span(mod(uv.x, period), 0.0, stripe_dash, wx, period);
		}
		col = mix(col, stripe, s * stripe.a);
	}

	float shown = 1.0;
	if (dash > 0.0 || dot > 0.0) {
		float g2 = dot_gap > 0.0 ? dot_gap : gap;
		float period = dash + gap + (dot > 0.0 ? dot + g2 : 0.0);
		float t = mod(uv.x, period);
		float y = uv.y - 0.5;
		shown = 0.0;
		if (dash > 0.0) {
			if (round_dashes) {
				// A capsule: the straight middle, and a half disc at either end.
				float r = 0.5;
				float a = r;
				float b = max(dash - r, r);
				shown = max(span(t, a, b, wx, period), max(disc(t, y, a, r, wx, period), disc(t, y, b, r, wx, period)));
			} else {
				shown = span(t, 0.0, dash, wx, period);
			}
		}
		if (dot > 0.0) {
			shown = max(shown, disc(t, y, dash + gap + dot * 0.5, dot * 0.5, wx, period));
		}
	}
	return vec4(col.rgb, col.a * shown * fade);
}

void fragment() {
	float across = abs(UV.y * 2.0 - 1.0);
	// How many screen pixels the line is across: UV.y runs 0 to 1 across it, so
	// the length of its gradient is one over that, whichever way the line runs.
	float px = 1.0 / max(length(vec2(dFdx(UV.y), dFdy(UV.y))), 1e-5);
	float wa = max(fwidth(across) * softness, 1e-5);
	float wx = max(fwidth(UV.x) * softness, 1e-5);
	float fade = COLOR.a;
	if (focus_outer > 0.0) {
		float d = distance(world, focus);
		fade *= mix(1.0, focus_floor, smoothstep(focus_inner, focus_outer, d));
	}

	if (coast_mode) {
		// across: 0 at the land's edge, 1 at the line's outer edge.
		float s = 1.0 - smoothstep(shore_share - wa, shore_share + wa, across);
		vec4 c = vec4(shore.rgb, shore.a * s);
		float room = (1.0 - shore_share) / float(max(rings, 1));
		// The rings show only once they are far enough apart on the screen.
		float spaced = smoothstep(ring_min_px, ring_min_px + 2.0, room * px * 0.5);
		for (int k = 1; k <= 8; k++) {
			if (k > rings) {
				break;
			}
			float centre = shore_share + room * (float(k) - 0.35);
			float half_w = max(ring_share * 0.5, wa * 0.75);
			float r = 1.0 - smoothstep(half_w - wa, half_w + wa, abs(across - centre));
			float a = ring.a * r * spaced * (1.0 - float(k - 1) / float(rings + 1));
			c.rgb = mix(c.rgb, ring.rgb, a * (1.0 - c.a) / max(a * (1.0 - c.a) + c.a, 1e-4));
			c.a = c.a + a * (1.0 - c.a);
		}
		COLOR = vec4(c.rgb, c.a * fade);
	} else {
		COLOR = draw_line_symbol(UV, COLOR, across, px, wa, wx, fade);
	}
}
