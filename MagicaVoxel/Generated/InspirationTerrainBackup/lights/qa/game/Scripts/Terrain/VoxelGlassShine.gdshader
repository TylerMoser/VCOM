// Glass, the second of its two passes (VoxelGlass.gdshader's next pass): what
// it gives off, added over what the first let through. Its surface reflects the
// sky and the sun as smooth glass does, more at a glancing angle; and the share
// of the light it does not let through (one less its clarity) is its own
// colour, lit as any voxel is, so a cloudy pane shows its colour and an opaque
// one, or blood on the glass, is drawn as any other voxel would be.
//
// Added light gives the same whatever order it is added in. Its material has a
// render priority over the first pass's, so every pane's tint is laid down
// before any is lit on top, and no two panes ever sort wrong. Like the first,
// it writes no depth and casts no shadow.
shader_type spatial;
render_mode blend_add, cull_back, depth_draw_never, fog_disabled, diffuse_burley, specular_schlick_ggx;

#include "res://Scripts/Terrain/Voxels.gdshaderinc"

// How smooth glass is: a sharp reflection of the sky.
uniform float glass_roughness = 0.04;

void fragment() {
	vec3 albedo;
	vec4 entry = pixel_entry(local_voxel, facing, extent, layer, fwidth(local_voxel), OUTPUT_IS_SRGB, albedo);
	int flags = flags_of(entry);
	bool wet = (flags & FLAG_WET) != 0;
	// Its own colour only in the share it does not let through; a dielectric's
	// reflection never depends on its colour.
	ALBEDO = albedo * (1.0 - clarity_of(flags));
	METALLIC = 0.0;
	SPECULAR = wet ? 0.35 : 0.5;
	ROUGHNESS = wet ? 0.55 : glass_roughness;
}
