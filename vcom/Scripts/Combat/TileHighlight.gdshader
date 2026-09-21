// Flat tile marker: a translucent fill with a solid border, tinted by the
// MultiMesh instance colour.
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never;

uniform float fill_alpha : hint_range(0.0, 1.0) = 0.55;
uniform float border_alpha : hint_range(0.0, 1.0) = 0.95;
// Border thickness as a fraction of the square's width.
uniform float border_width : hint_range(0.0, 0.5) = 0.09;

void fragment() {
	vec2 from_center = abs(UV - 0.5) * 2.0;
	float edge = max(from_center.x, from_center.y);
	float border = step(1.0 - border_width * 2.0, edge);
	ALBEDO = COLOR.rgb;
	ALPHA = COLOR.a * mix(fill_alpha, border_alpha, border);
}
