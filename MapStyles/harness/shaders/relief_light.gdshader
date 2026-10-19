// The lit half of the shaded relief (see relief.gdshader): adds a warm light on
// the faces turned to the light, by up to [light].
shader_type canvas_item;
render_mode blend_add;

uniform sampler2D relief : filter_linear_mipmap, repeat_disable;
uniform float light : hint_range(0.0, 1.0) = 0.12;
uniform vec4 light_tint : source_color = vec4(1.0, 0.96, 0.85, 1.0);

void fragment() {
	float s = texture(relief, UV).r;
	float lit = clamp((s - 0.5) * 2.0, 0.0, 1.0) * light;
	COLOR = vec4(light_tint.rgb * lit, 1.0);
}
