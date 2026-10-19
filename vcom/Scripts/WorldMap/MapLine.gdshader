// Draws a line of the new map (Scenes/Map.tscn) as a map symbol: in its own
// colour, with a darker casing at both edges (the roads and bridges), or
// dashed, dotted or dash-dotted (the borders). Each kind of line has a material
// of its own in Resources/MapLines/, shared by every line of that kind, so a
// change there changes them all.
//
// The line must have texture_mode Tile, which is what gives a Line2D UVs (it
// needs no texture): UV.x then counts the line's widths along it, and UV.y runs
// 0 to 1 across it. Every length here is in widths of the line, so a pattern
// grows and shrinks with it as MapDetail sets its width by the zoom.
//
// The line's colour is the fill, and its alpha multiplies everything: keep it
// at 1, so that the alpha is only the fading MapDetail and BorderSwitch do by
// modulate, which then fades the pattern too.
shader_type canvas_item;

// The casing: this share of the half-width on each side, in its own colour.
// Under [casing_min_px] screen pixels across, a line has no room for a casing
// and a fill, and is drawn solid in [narrow] instead (while narrow's alpha is
// above 0), fading over 2 pixels. The shader works that out from the line's
// own width on the screen, so nothing has to follow the zoom.
uniform vec4 casing : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float casing_share : hint_range(0.0, 1.0) = 0.0;
uniform float casing_min_px = 0.0;
uniform vec4 narrow : source_color = vec4(0.0);

// The whole line dashed: a dash of [dash] widths, then [gap]; with [dot] above
// 0, a round dot that many widths across after each dash, [dot_gap] either side
// of it ([gap] when 0). [dash] 0 is a solid line, or dots alone with a [dot].
uniform float dash = 0.0;
uniform float gap = 1.0;
uniform float dot = 0.0;
uniform float dot_gap = 0.0;
// Rounds the ends of the dashes.
uniform bool round_dashes = false;
// For a band under a river or a road that a border follows (a border's
// "...Along..." line), wider than the river or road by the border's width so
// that the border shows along both its banks: the dots and the dashes' ends are
// drawn square, across the whole width, or the river or road over the band's
// middle would hide all of a dot and round off what shows of a dash.
uniform bool banks = false;

// How much of a pixel an edge is smoothed over.
uniform float softness = 1.0;

// Coverage of [a, b] at t, smoothed over w, for a pattern repeating every period.
float span(float t, float a, float b, float w, float period) {
	float best = 0.0;
	for (int k = -1; k <= 1; k++) {
		float x = t + float(k) * period;
		best = max(best, clamp(min(x - a, b - x) / w + 0.5, 0.0, 1.0));
	}
	return best;
}

// Coverage of a disc of radius r centred at c along the line, on its middle.
float disc(float t, float y, float c, float r, float w, float period) {
	float best = 0.0;
	for (int k = -1; k <= 1; k++) {
		float d = length(vec2(t + float(k) * period - c, y));
		best = max(best, clamp((r - d) / w + 0.5, 0.0, 1.0));
	}
	return best;
}

void fragment() {
	// 0 on the line's middle, 1 at its edges.
	float across = abs(UV.y * 2.0 - 1.0);
	// How many screen pixels the line is across: UV.y runs 0 to 1 across it, so
	// the length of its gradient is one over that, whichever way the line runs.
	float px = 1.0 / max(length(vec2(dFdx(UV.y), dFdy(UV.y))), 1e-5);
	float wa = max(fwidth(across) * softness, 1e-5);
	float wx = max(fwidth(UV.x) * softness, 1e-5);

	vec4 col = vec4(COLOR.rgb, 1.0);
	if (casing_share > 0.0) {
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
				// A capsule: the straight middle, and a half disc at either end.
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
	COLOR = vec4(col.rgb, col.a * shown * COLOR.a);
}
