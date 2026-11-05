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
// (roughness 0.55, specular 0.35). Each face is drawn a fraction of a pixel
// past its edges (grow_pixels), so faces that meet overlap rather than leave a
// crack; the colour is still read within its own extent.
//
// What each corner of a face carries, as ChunkMesher.arrays() lays it out:
// CUSTOM0 its place in voxels within its box, and its box's layer of the
// texture times 8 plus which way the face looks (0 +x, 1 -x, 2 +y, 3 -y, 4 +z,
// 5 -z); CUSTOM1 the face's extent across its two axes, within the box. So the
// voxel behind a pixel is found from what the mesh was made with, never from
// where its corner is drawn, and a mesh skinned to a skeleton (a figure) is
// coloured as one standing still.
shader_type spatial;
// StandardMaterial3D's lighting, named outright: a shader left to its own
// defaults in Godot 4.7 is not lit the same.
render_mode diffuse_burley, specular_schlick_ggx;

global uniform float tile_grid;

// Every voxel's place in the palette, a box of voxels a layer: x across, z +
// y times the box's depth (z) down, as VoxelVolume and VoxelModel keep them.
uniform sampler2DArray voxels : filter_nearest, repeat_disable;
// Each place's colour (sRGB) and flags (alpha, as a byte).
uniform vec4 palette[256];
// Voxels along each axis of a layer's box: a chunk's, a scenery kind's block,
// or a model's own.
uniform ivec3 box_size = ivec3(32);
// Voxels to a unit of the mesh's own space: sixteen to a cell, a shade fewer
// for a model drawn bigger (a prop, at 0.063 a voxel).
uniform float voxels_per_unit = 16.0;
// How much a tile grid line darkens the surface under it, and its half-width
// in metres: as the ground's own grid shader had them before levels.
uniform float line_darken : hint_range(0.0, 1.0) = 0.18;
uniform float line_width = 0.02;
// How far, in pixels, each face is drawn past its edges along its own plane.
// Merged faces of different sizes meet at T-junctions (a corner of one partway
// along the edge of the next), and rasterising them can leave a gap a fraction
// of a pixel wide, a sparkle of whatever is behind, which is the sky once the
// hidden faces are gone. A fiftieth of a pixel, at every distance, closes
// those gaps (they are at most about a 128th) and is too little to see; it
// never moves a face along its normal. Measured on BoundaryMap: the sparkles
// the merged faces brought are gone, and a convex edge stands out a fiftieth of
// a pixel further, which darkens a sample of a few edge pixels. On a mesh
// skinned to a skeleton the growth is along the face's axes as it rests, so on
// a turned bone part of it is out of the face's plane: a fiftieth of a pixel,
// still too little to see.
uniform float grow_pixels = 0.02;
// And never more than this, in metres, should a view give no size to go by.
uniform float grow_most = 0.005;
// The sun's shadow (orthographic, its pass given no viewport size) grows faces
// by this, in metres, instead: a fiftieth of its texels, so no light leaks
// through a gap there, and no shadow's edge shifts to be seen.
uniform float grow_shadow = 0.0002;

// The corner's place in voxels within its box, interpolated across the face;
// the face's way out, its layer and its extent across, the same at every
// corner.
varying vec3 local_voxel;
varying flat vec3 facing;
varying flat float layer;
varying flat vec4 extent;

void vertex() {
	int packed = int(CUSTOM0.w + 0.5);
	int face = packed & 7;
	int axis = face >> 1;
	layer = float(packed >> 3);
	facing = vec3(0.0);
	facing[axis] = (face & 1) == 0 ? 1.0 : -1.0;
	extent = CUSTOM1;
	vec3 at = CUSTOM0.xyz;
	// Out from the face's middle along its two axes: which corner this is.
	int s_axis = axis == 0 ? 1 : 0;
	int t_axis = axis == 2 ? 1 : 2;
	vec3 out_from_middle = vec3(0.0);
	out_from_middle[s_axis] = sign(at[s_axis] - 0.5 * (CUSTOM1.x + CUSTOM1.z));
	out_from_middle[t_axis] = sign(at[t_axis] - 0.5 * (CUSTOM1.y + CUSTOM1.w));
	// A pixel's size here, in the mesh's units (metres): clip w is the distance
	// in a perspective view.
	float grow = grow_shadow;
	if (PROJECTION_MATRIX[3][3] < 0.5) {
		vec4 clip = PROJECTION_MATRIX * (MODELVIEW_MATRIX * vec4(VERTEX, 1.0));
		float pixel = 2.0 * abs(clip.w) / max(abs(PROJECTION_MATRIX[1][1]) * max(VIEWPORT_SIZE.y, 360.0), 1e-4);
		grow = min(pixel * grow_pixels, grow_most);
	}
	VERTEX += out_from_middle * grow;
	local_voxel = at + out_from_middle * grow * voxels_per_unit;
}

vec3 to_linear(vec3 c) {
	return mix(
			pow((c + vec3(0.055)) * (1.0 / (1.0 + 0.055)), vec3(2.4)),
			c * (1.0 / 12.92),
			lessThan(c, vec3(0.04045)));
}

// The palette entry of the voxel at [v], within the box.
vec4 entry_at(ivec3 v) {
	v = clamp(v, ivec3(0), box_size - ivec3(1));
	float raw = texelFetch(voxels, ivec3(v.x, v.z + v.y * box_size.z, int(layer + 0.5)), 0).r;
	return palette[int(raw * 255.0 + 0.5)];
}

vec3 albedo_of(vec4 entry) {
	return OUTPUT_IS_SRGB ? entry.rgb : to_linear(entry.rgb);
}

// How much of a pixel [width] voxels across, centred at [at] along one axis,
// lies over the voxel next to the one it is centred on (toward the nearer edge
// of that voxel), and which way that voxel is: the coverage a pixel's samples
// would give each, worked out rather than sampled. Never past [low] and
// [high], the face's own extent.
vec2 neighbour_share(float at, float width, float low, float high) {
	float cell = floor(at);
	float within = at - cell;
	float toward = within > 0.5 ? 1.0 : -1.0;
	float edge = within > 0.5 ? cell + 1.0 : cell;
	float share = clamp((0.5 * width - abs(at - edge)) / max(width, 1e-4), 0.0, 1.0);
	// No neighbour beyond the face: its own voxel covers the whole pixel.
	if (cell + toward < low || cell + toward >= high) {
		share = 0.0;
	}
	return vec2(share, toward);
}

void fragment() {
	// Half a voxel in from the face is the voxel it belongs to. A pixel on the
	// rim of a face can be shaded from a point just off it (multisampling), so
	// the point is kept within the face's own extent.
	vec3 p = local_voxel - facing * 0.5;
	vec3 along = abs(facing);
	const float IN = 0.001;
	// The two axes across the face, as indices into a vec3.
	int s_axis = along.x > 0.5 ? 1 : 0;
	int t_axis = along.z > 0.5 ? 1 : 2;
	p[s_axis] = clamp(p[s_axis], extent.x + IN, extent.z - IN);
	p[t_axis] = clamp(p[t_axis], extent.y + IN, extent.w - IN);
	ivec3 v = ivec3(floor(p));
	vec4 entry = entry_at(v);
	// Where a pixel lies across the edge between two voxels of different
	// colours, it takes each in the share it covers, as the face would if each
	// colour were drawn on its own and multisampled.
	vec2 ss = neighbour_share(p[s_axis], fwidth(local_voxel[s_axis]), extent.x, extent.z);
	vec2 ts = neighbour_share(p[t_axis], fwidth(local_voxel[t_axis]), extent.y, extent.w);
	vec3 albedo = albedo_of(entry);
	if (ss.x > 0.0 || ts.x > 0.0) {
		ivec3 vs = v;
		vs[s_axis] += int(ss.y);
		ivec3 vt = v;
		vt[t_axis] += int(ts.y);
		ivec3 vst = vs;
		vst[t_axis] += int(ts.y);
		vec3 a_s = albedo_of(entry_at(vs));
		vec3 a_t = albedo_of(entry_at(vt));
		vec3 a_st = albedo_of(entry_at(vst));
		albedo = mix(mix(albedo, a_s, ss.x), mix(a_t, a_st, ss.x), ts.x);
	}
	int flags = int(entry.a * 255.0 + 0.5);
	if ((flags & 1) != 0 && tile_grid > 0.0) {
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
	bool wet = (flags & 2) != 0;
	SPECULAR = wet ? 0.35 : 0.5;
	ROUGHNESS = wet ? 0.55 : 1.0;
}
