// Glass, the first of its two passes: what shows through it, tinted. Every
// voxel model's glass is meshed apart (ChunkMesher) and drawn by this, with
// VoxelGlassShine.gdshader as its next pass, never by Voxels.gdshader.
//
// A glass voxel's colour is the colour it lets through: whatever is behind it
// is multiplied by it, so a white pane is clear and a coloured one stained. How
// much it lets through at all is its colour's clarity (the palette entry's
// flags, from MagicaVoxel's Transparency): clarity 1 is all tint, and below
// that the light behind is dimmed in step while the shine pass draws that
// share of the voxel's own colour, lit, until at 0 it is as opaque as any
// other voxel. Blood on glass is no glass colour, clarity 0: opaque, wet red.
//
// Multiplying by a colour gives the same whatever order panes are drawn in, so
// glass seen through glass never sorts wrong. It is unshaded (the tint is not
// lit: it filters the light behind), writes no depth and casts no shadow, as
// every see-through surface in Godot: sunlight falls through it untinted.
shader_type spatial;
render_mode blend_mul, unshaded, cull_back, depth_draw_never, fog_disabled;

#include "res://Scripts/Terrain/Voxels.gdshaderinc"

void fragment() {
	vec3 albedo;
	vec4 entry = pixel_entry(local_voxel, facing, extent, layer, fwidth(local_voxel), OUTPUT_IS_SRGB, albedo);
	ALBEDO = albedo * clarity_of(flags_of(entry));
}
