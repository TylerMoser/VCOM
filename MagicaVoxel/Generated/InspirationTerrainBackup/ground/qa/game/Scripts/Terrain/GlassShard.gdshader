// A shard of broken glass (GlassShards), the first of its two passes: as
// VoxelGlass.gdshader tints what shows through a pane, multiplied by its
// colour as clear as it is. A shard's colour is its instance's (COLOR) and its
// clarity the first number of its custom data (INSTANCE_CUSTOM.x). Its shine,
// GlassShardShine.gdshader, is its next pass.
shader_type spatial;
render_mode blend_mul, unshaded, cull_back, depth_draw_never, fog_disabled;

varying flat vec4 tint;
varying flat float clarity;

void vertex() {
	tint = COLOR;
	clarity = INSTANCE_CUSTOM.x;
}

void fragment() {
	vec3 c = tint.rgb;
	if (!OUTPUT_IS_SRGB) {
		c = mix(pow((c + vec3(0.055)) * (1.0 / 1.055), vec3(2.4)), c * (1.0 / 12.92), lessThan(c, vec3(0.04045)));
	}
	ALBEDO = c * clarity;
}
