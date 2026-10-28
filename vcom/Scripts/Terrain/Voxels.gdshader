// Every voxel model the game draws: the level a chunk at a time
// (LevelRenderer), the scenery a kind at a time (SceneryRenderer), and each
// model of its own (VoxelModel: a figure, a prop, a crate's board, a block
// falling whole). Faces are merged by their shape alone, and each pixel is drawn
// the colour of the voxel behind it, read from a texture of every voxel's
// place in a palette, a layer a box of voxels. Recolouring a voxel - blood -
// is a write to that texture and no new mesh.
//
// Lit as the MagicaVoxel importer's material lights a model (vertex colours as
// sRGB albedo, roughness 1, Godot's standard lighting), so a model looks as
// its imported mesh did. A palette entry's alpha holds flags: 1 draws the tile
// grid's lines over it (TileGrid.gd), 2 makes it wet, as blood is, glossier
// (roughness 0.55, specular 0.35), 4 makes it glass, which this never draws:
// glass is meshed apart and drawn by VoxelGlass.gdshader and
// VoxelGlassShine.gdshader (ChunkMesher). Each face is drawn a fraction of a
// pixel past its edges (grow_pixels), so faces that meet overlap rather than
// leave a crack; the colour is still read within its own extent.
//
// Voxels.gdshaderinc holds what the three share: the uniforms, the vertex
// function and the lookups, and what each corner of a face carries.
shader_type spatial;
// StandardMaterial3D's lighting, named outright: a shader left to its own
// defaults in Godot 4.7 is not lit the same.
render_mode diffuse_burley, specular_schlick_ggx;

#include "res://Scripts/Terrain/Voxels.gdshaderinc"

global uniform float tile_grid;

// How much a tile grid line darkens the surface under it, and its half-width
// in metres: as the ground's own grid shader had them before levels.
uniform float line_darken : hint_range(0.0, 1.0) = 0.18;
uniform float line_width = 0.02;

void fragment() {
	vec3 albedo;
	vec4 entry = pixel_entry(local_voxel, facing, extent, layer, fwidth(local_voxel), OUTPUT_IS_SRGB, albedo);
	int flags = flags_of(entry);
	if ((flags & FLAG_GRID) != 0 && tile_grid > 0.0) {
		// Blocks are 1 m with their faces on whole metres, so a boundary is
		// wherever a coordinate is whole. A face's lines run along its own two
		// axes: x and z on a top, the vertical and one horizontal on a wall.
		vec3 world_pos = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
		vec3 n = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
		vec3 d = abs(fract(world_pos + 0.5) - 0.5);
		vec3 fw = fwidth(world_pos);
		float dist;
		float aa;
		if (abs(n.y) > 0.5) {
			dist = min(d.x, d.z);
			aa = max(fw.x, fw.z);
		} else if (abs(n.x) > 0.5) {
			dist = min(d.y, d.z);
			aa = max(fw.y, fw.z);
		} else {
			dist = min(d.x, d.y);
			aa = max(fw.x, fw.y);
		}
		float line = 1.0 - smoothstep(line_width - aa, line_width + aa, dist);
		albedo *= 1.0 - line_darken * tile_grid * line;
	}
	ALBEDO = albedo;
	METALLIC = 0.0;
	bool wet = (flags & FLAG_WET) != 0;
	SPECULAR = wet ? 0.35 : 0.5;
	ROUGHNESS = wet ? 0.55 : 1.0;
}
