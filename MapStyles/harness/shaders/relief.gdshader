// Shaded relief over the land and its forests: one Polygon2D over the whole
// MapCreation sheet (StyleKit.sheet_polygon), its texture hillshade.png (128
// for flat ground and the sea). Multiplied into what is under it, so it only
// darkens: the faces turned from the light, by up to [shadow]. Its companion
// relief_light.gdshader adds the light on the faces turned to it.
shader_type canvas_item;
render_mode blend_mul;

uniform sampler2D relief : filter_linear_mipmap, repeat_disable;
// How dark the steepest face turned from the light gets, 0 to 1.
uniform float shadow : hint_range(0.0, 1.0) = 0.45;
// Tints the shade (a cool blue-grey reads as shade; black reads as dirt).
uniform vec4 shade_tint : source_color = vec4(0.25, 0.28, 0.4, 1.0);

void fragment() {
	float s = texture(relief, UV).r;
	float dark = clamp((0.5 - s) * 2.0, 0.0, 1.0) * shadow;
	COLOR = vec4(mix(vec3(1.0), shade_tint.rgb, dark), 1.0);
}
