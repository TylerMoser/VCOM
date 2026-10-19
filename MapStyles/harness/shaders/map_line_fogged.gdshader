// The game's MapLine.gdshader (vcom/Scripts/WorldMap/), drawing only where the fog of war is: for
// copies of the lines the fog leaves known, drawn over it (the coast, the kingdoms' borders, the
// great rivers, the roads, by variant), so that they show in the fog and not twice where it is
// clear. With no pattern and no casing it is a plain line, or a plain polygon (a lake). For the
// variants of proposal 20 in MapStyles/20-fog-of-war/. Keep its drawing in step with the game's.
shader_type canvas_item;

#include "res://_probe/shaders/fog_common.gdshaderinc"

// How much of the line shows in the fog, and with alpha over 0, the colour it is drawn in there
// instead of its own: a sketch in the fog's ink.
uniform float in_fog : hint_range(0.0, 1.0) = 1.0;
uniform vec4 sketch : source_color = vec4(0.0);

// -- MapLine.gdshader's own --------------------------------------------------------------------------
uniform vec4 casing : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float casing_share : hint_range(0.0, 1.0) = 0.0;
uniform float casing_min_px = 0.0;
uniform vec4 narrow : source_color = vec4(0.0);
uniform float dash = 0.0;
uniform float gap = 1.0;
uniform float dot = 0.0;
uniform float dot_gap = 0.0;
uniform bool round_dashes = false;
uniform bool banks = false;
uniform float softness = 1.0;

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

float span(float t, float a, float b, float w, float period) {
	float best = 0.0;
	for (int k = -1; k <= 1; k++) {
		float x = t + float(k) * period;
		best = max(best, clamp(min(x - a, b - x) / w + 0.5, 0.0, 1.0));
	}
	return best;
}

float disc(float t, float y, float c, float r, float w, float period) {
	float best = 0.0;
	for (int k = -1; k <= 1; k++) {
		float d = length(vec2(t + float(k) * period - c, y));
		best = max(best, clamp((r - d) / w + 0.5, 0.0, 1.0));
	}
	return best;
}

void fragment() {
	float across = abs(UV.y * 2.0 - 1.0);
	float px = 1.0 / max(length(vec2(dFdx(UV.y), dFdy(UV.y))), 1e-5);
	float wa = max(fwidth(across) * softness, 1e-5);
	float wx = max(fwidth(UV.x) * softness, 1e-5);

	vec4 col = vec4(sketch.a > 0.0 ? sketch.rgb : COLOR.rgb, 1.0);
	if (casing_share > 0.0 && sketch.a <= 0.0) {
		float room = casing_min_px > 0.0 ? smoothstep(casing_min_px, casing_min_px + 2.0, px) : 1.0;
		float edge = smoothstep(1.0 - casing_share - wa, 1.0 - casing_share + wa, across) * room;
		col = mix(col, casing, edge);
		if (narrow.a > 0.0) {
			col = mix(narrow, col, room);
		}
	}

	float shown = 1.0;
	if (dash > 0.0 || dot > 0.0) {
		float g2 = dot_gap > 0.0 ? dot_gap : gap;
		float period = dash + gap + (dot > 0.0 ? dot + g2 : 0.0);
		float t = mod(UV.x, period);
		float y = UV.y - 0.5;
		shown = 0.0;
		if (dash > 0.0) {
			if (round_dashes && !banks) {
				float r = 0.5;
				float b = max(dash - r, r);
				shown = max(span(t, r, b, wx, period), max(disc(t, y, r, r, wx, period), disc(t, y, b, r, wx, period)));
			} else {
				shown = span(t, 0.0, dash, wx, period);
			}
		}
		if (dot > 0.0) {
			float c = dash + gap + dot * 0.5;
			float r = dot * 0.5;
			shown = max(shown, banks ? span(t, c - r, c + r, wx, period) : disc(t, y, c, r, wx, period));
		}
	}
	float fogged = 1.0 - fog_explored(fog_raw(world));
	COLOR = vec4(col.rgb, col.a * shown * COLOR.a * fogged * in_fog * (sketch.a > 0.0 ? sketch.a : 1.0));
}
