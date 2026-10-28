// What every voxel shader shares: Voxels.gdshader, which draws every voxel but
// glass, and VoxelGlass.gdshader and VoxelGlassShine.gdshader, which draw the
// glass. Where each corner of a face is, which voxel each pixel shows, and
// that voxel's palette entry and colour. Voxels.gdshader says how it all works.
//
// What each corner of a face carries, as ChunkMesher.arrays() lays it out:
// CUSTOM0 its place in voxels within its box, and its box's layer of the
// texture times 8 plus which way the face looks (0 +x, 1 -x, 2 +y, 3 -y, 4 +z,
// 5 -z); CUSTOM1 the face's extent across its two axes, within the box. So the
// voxel behind a pixel is found from what the mesh was made with, never from
// where its corner is drawn, and a mesh skinned to a skeleton (a figure) is
// coloured as one standing still.

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

// The flags a palette entry's alpha holds (VoxelShape.FLAG_*): the tile grid
// is drawn over it, it is wet, it is glass; and a glass colour's clarity, in
// steps of a 31st, from the fourth bit up.
const int FLAG_GRID = 1;
const int FLAG_WET = 2;
const int FLAG_GLASS = 4;
const int CLARITY_SHIFT = 3;
const int CLARITY_STEPS = 31;

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

// The palette entry of the voxel at [v], within the box, in the layer
// [of_layer].
vec4 entry_at(ivec3 v, float of_layer) {
	v = clamp(v, ivec3(0), box_size - ivec3(1));
	float raw = texelFetch(voxels, ivec3(v.x, v.z + v.y * box_size.z, int(of_layer + 0.5)), 0).r;
	return palette[int(raw * 255.0 + 0.5)];
}

// An entry's colour as the output wants it: linear, unless [srgb].
vec3 albedo_of(vec4 entry, bool srgb) {
	return srgb ? entry.rgb : to_linear(entry.rgb);
}

// The flags of a palette entry, as a whole number.
int flags_of(vec4 entry) {
	return int(entry.a * 255.0 + 0.5);
}

// How clear a palette entry is, 0 to 1: a glass colour's clarity, 0 for any
// other (blood on glass among them).
float clarity_of(int flags) {
	if ((flags & FLAG_GLASS) == 0) {
		return 0.0;
	}
	return float((flags >> CLARITY_SHIFT) & CLARITY_STEPS) / float(CLARITY_STEPS);
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

// The palette entry of the voxel a pixel shows, and in [albedo] its colour
// (linear unless [srgb]), blended with its neighbours' where the pixel lies
// across the edge between them. [at] is the pixel's place in voxels within its
// box (local_voxel), [face] the way its face looks (facing), [face_extent] the
// face's extent (extent), [of_layer] its box's layer (layer) and [widths] how
// many voxels a pixel spans along each axis (fwidth of local_voxel): each
// passed in, as only the fragment function can read them.
vec4 pixel_entry(vec3 at, vec3 face, vec4 face_extent, float of_layer, vec3 widths, bool srgb, out vec3 albedo) {
	// Half a voxel in from the face is the voxel it belongs to. A pixel on the
	// rim of a face can be shaded from a point just off it (multisampling), so
	// the point is kept within the face's own extent.
	vec3 p = at - face * 0.5;
	vec3 along = abs(face);
	const float IN = 0.001;
	// The two axes across the face, as indices into a vec3.
	int s_axis = along.x > 0.5 ? 1 : 0;
	int t_axis = along.z > 0.5 ? 1 : 2;
	p[s_axis] = clamp(p[s_axis], face_extent.x + IN, face_extent.z - IN);
	p[t_axis] = clamp(p[t_axis], face_extent.y + IN, face_extent.w - IN);
	ivec3 v = ivec3(floor(p));
	vec4 entry = entry_at(v, of_layer);
	// Where a pixel lies across the edge between two voxels of different
	// colours, it takes each in the share it covers, as the face would if each
	// colour were drawn on its own and multisampled.
	vec2 ss = neighbour_share(p[s_axis], widths[s_axis], face_extent.x, face_extent.z);
	vec2 ts = neighbour_share(p[t_axis], widths[t_axis], face_extent.y, face_extent.w);
	albedo = albedo_of(entry, srgb);
	if (ss.x > 0.0 || ts.x > 0.0) {
		ivec3 vs = v;
		vs[s_axis] += int(ss.y);
		ivec3 vt = v;
		vt[t_axis] += int(ts.y);
		ivec3 vst = vs;
		vst[t_axis] += int(ts.y);
		vec3 a_s = albedo_of(entry_at(vs, of_layer), srgb);
		vec3 a_t = albedo_of(entry_at(vt, of_layer), srgb);
		vec3 a_st = albedo_of(entry_at(vst, of_layer), srgb);
		albedo = mix(mix(albedo, a_s, ss.x), mix(a_t, a_st, ss.x), ts.x);
	}
	return entry;
}
