// A shard of broken glass, the second of its two passes (GlassShard.gdshader's
// next pass): as VoxelGlassShine.gdshader shines a pane, its glint of the sky
// and the sun added on top, and the share of its colour it does not let
// through lit as any voxel is.
shader_type spatial;
render_mode blend_add, cull_back, depth_draw_never, fog_disabled, diffuse_burley, specular_schlick_ggx;

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
	ALBEDO = c * (1.0 - clarity);
	METALLIC = 0.0;
	SPECULAR = 0.5;
	ROUGHNESS = 0.04;
}
