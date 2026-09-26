// Stylised material for the MagicaVoxel block meshes (vertex-coloured, 1 m
// blocks on integer boundaries). Every feature defaults to "off", so a variant
// only sets what it uses.
shader_type spatial;
render_mode cull_back;

// --- Colour remap, done on the sRGB vertex colours -------------------------
uniform float saturation = 1.0;
uniform float brightness = 1.0;
// Extra control for greens only (hues ~55-145 deg), for the grass tops.
uniform float green_saturation = 1.0;
uniform float green_value = 1.0;
// Degrees; negative pulls green toward yellow, positive toward teal.
uniform float green_hue_shift = 0.0;

// --- Hand-shading by face direction (linear multipliers) -------------------
uniform vec3 top_tint = vec3(1.0);
uniform vec3 side_x_tint = vec3(1.0);
uniform vec3 side_z_tint = vec3(1.0);

// --- Readability -----------------------------------------------------------
// Albedo gain per metre above the floor, so raised ground reads as higher.
uniform float height_gain = 0.0;
uniform float floor_y = 1.0;
// Darkens walls just above the floor, a cheap stand-in for baked voxel AO.
uniform float contact_ao = 0.0;
uniform float contact_ao_height = 0.6;
// Darkens the map's outer skirt toward its base.
uniform float skirt_darken = 0.0;
// World-space lines on block boundaries (tile grid + block edges).
uniform float edge_darken = 0.0;
uniform float edge_width = 0.025;

// --- Lighting --------------------------------------------------------------
// 0 = smooth; 1 = one hard terminator; 2+ = that many bands.
uniform float toon_bands = 0.0;
uniform float toon_softness = 0.04;
// Light wrap: 0 = Lambert, 0.5 = soft half-wrap.
uniform float wrap = 0.0;
// Colour added where the sun does not reach, as a fraction of the sun. This
// is multiplied by the albedo, so it tints but cannot turn green grass blue.
uniform vec3 shade_color : source_color = vec3(0.35, 0.4, 0.9);
uniform float shade_strength = 0.0;
// Added on top in shade WITHOUT the albedo multiply, so shadows on any
// colour pick up this hue (painterly cool shadows). Linear, scaled by the sun.
uniform vec3 shade_glow = vec3(0.0);
uniform float rim_strength = 0.0;
uniform float rim_power = 4.0;
uniform float sheen = 0.0;
uniform float sheen_power = 24.0;
uniform float roughness = 1.0;

varying vec3 world_pos;
varying vec3 world_normal;

vec3 rgb2hsv(vec3 c) {
	vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
	vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
	float d = q.x - min(q.w, q.y);
	float e = 1.0e-10;
	return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c) {
	vec3 p = abs(fract(c.xxx + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
	return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}

vec3 srgb_to_linear(vec3 c) {
	return mix(pow((c + 0.055) / 1.055, vec3(2.4)), c / 12.92, lessThan(c, vec3(0.04045)));
}

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	vec3 hsv = rgb2hsv(COLOR.rgb);
	float hue = hsv.x * 360.0;
	float green = 1.0 - smoothstep(0.0, 45.0, abs(mod(hue - 100.0 + 180.0, 360.0) - 180.0));
	hsv.x = fract(hsv.x + green_hue_shift / 360.0 * green + 1.0);
	hsv.y = clamp(hsv.y * saturation * mix(1.0, green_saturation, green), 0.0, 1.0);
	hsv.z = clamp(hsv.z * brightness * mix(1.0, green_value, green), 0.0, 1.0);
	vec3 albedo = srgb_to_linear(hsv2rgb(hsv));

	vec3 n = world_normal;
	bool is_top = n.y > 0.5;
	bool is_wall = abs(n.y) < 0.5;
	if (is_top) {
		albedo *= top_tint;
	} else if (is_wall) {
		albedo *= abs(n.x) > 0.5 ? side_x_tint : side_z_tint;
	}

	albedo *= 1.0 + height_gain * max(world_pos.y - floor_y, 0.0);

	if (is_wall) {
		if (world_pos.y >= floor_y - 0.001) {
			float above = world_pos.y - floor_y;
			albedo *= 1.0 - contact_ao * (1.0 - smoothstep(0.0, contact_ao_height, above));
		} else {
			albedo *= mix(1.0 - skirt_darken, 1.0, clamp(world_pos.y / floor_y, 0.0, 1.0));
		}
	}

	if (edge_darken > 0.0) {
		// Distance to the nearest block boundary along the face's two in-plane axes.
		vec3 d = abs(fract(world_pos + 0.5) - 0.5);
		vec3 fw = fwidth(world_pos);
		float dist;
		float aa;
		if (is_top || n.y < -0.5) {
			dist = min(d.x, d.z);
			aa = max(fw.x, fw.z);
		} else if (abs(n.x) > 0.5) {
			dist = min(d.y, d.z);
			aa = max(fw.y, fw.z);
		} else {
			dist = min(d.x, d.y);
			aa = max(fw.x, fw.y);
		}
		float line = 1.0 - smoothstep(edge_width - aa, edge_width + aa, dist);
		albedo *= 1.0 - edge_darken * line;
	}

	ALBEDO = albedo;
	ROUGHNESS = roughness;
	SPECULAR = 0.5 * (1.0 - roughness);
}

void light() {
	float ndl = dot(NORMAL, LIGHT);
	float lit = clamp((ndl + wrap) / (1.0 + wrap), 0.0, 1.0) * ATTENUATION;
	if (toon_bands >= 1.0) {
		float x = lit * toon_bands;
		float band = floor(x);
		lit = (band + smoothstep(0.5 - toon_softness, 0.5 + toon_softness, x - band)) / toon_bands;
		lit = min(lit, 1.0);
	}
	vec3 sun = LIGHT_COLOR / PI;
	DIFFUSE_LIGHT += sun * lit;
	DIFFUSE_LIGHT += sun * shade_color * shade_strength * (1.0 - lit);
	SPECULAR_LIGHT += sun * shade_glow * (1.0 - lit);
	if (rim_strength > 0.0) {
		float rim = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), rim_power);
		DIFFUSE_LIGHT += sun * rim * rim_strength * max(lit, 0.3);
	}
	if (sheen > 0.0) {
		vec3 h = normalize(LIGHT + VIEW);
		SPECULAR_LIGHT += sun * pow(clamp(dot(NORMAL, h), 0.0, 1.0), sheen_power) * sheen * ATTENUATION;
	}
}
