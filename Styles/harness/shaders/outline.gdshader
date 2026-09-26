// Full-screen outline pass for a quad placed anywhere in the scene.
//
// Silhouettes: a neighbouring pixel that lies well BEHIND this pixel's surface
// plane means this pixel is the near side of an edge, so the line lands on the
// object and stays one pixel wide. Measuring against the plane (not raw depth)
// keeps flat floors seen at grazing angles from lighting up.
//
// Creases: neighbours on a different plane. Convex ones (the neighbour falls
// away behind the plane, like the top edge of a block) can get a light
// highlight; concave ones (floor meeting wall) can get a soft dark line.
//
// Needs the normal-roughness buffer, so Forward+ only. Use SMAA/FXAA/TAA
// rather than MSAA: MSAA resolves averaged normals along edges and the
// crease tests stop firing.
shader_type spatial;
render_mode unshaded, depth_draw_never, depth_test_disabled, cull_disabled, fog_disabled, shadows_disabled;

uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;
uniform sampler2D depth_tex : hint_depth_texture, filter_nearest;
uniform sampler2D normal_tex : hint_normal_roughness_texture, filter_nearest;

uniform vec3 line_color : source_color = vec3(0.07, 0.05, 0.10);
uniform float line_opacity : hint_range(0.0, 1.0) = 0.85;
// 0 = paint line_color; 1 = darken the colour underneath by line_darken.
uniform float line_tint_mix : hint_range(0.0, 1.0) = 0.0;
uniform float line_darken : hint_range(0.0, 1.0) = 0.35;
// Pixel offsets used to find silhouettes and creases.
uniform float line_width = 1.0;
uniform float crease_width = 1.0;
// A neighbour this far behind the plane (metres, plus a fraction of depth) is an edge.
uniform float depth_threshold = 0.25;
uniform float depth_threshold_scale = 0.01;

uniform float crease_opacity : hint_range(0.0, 1.0) = 0.0;
uniform float highlight_opacity : hint_range(0.0, 1.0) = 0.0;
uniform vec3 highlight_color : source_color = vec3(1.0, 0.97, 0.88);
// Only highlight crease pixels whose surface faces up at least this much (world).
uniform float highlight_min_up = -1.0;
// Tuning aid: paints the masks instead (red silhouette, green convex, blue concave).
uniform bool debug_masks = false;

void vertex() {
	POSITION = vec4(VERTEX.xy, 1.0, 1.0);
}

vec3 view_pos(vec2 uv, mat4 inv_proj) {
	float d = texture(depth_tex, uv).r;
	vec4 v = inv_proj * vec4(uv * 2.0 - 1.0, d, 1.0);
	return v.xyz / v.w;
}

vec3 view_normal(vec2 uv) {
	return normalize(texture(normal_tex, uv).xyz * 2.0 - 1.0);
}

void fragment() {
	vec2 uv = SCREEN_UV;
	vec3 colour = texture(screen_tex, uv).rgb;
	float raw_depth = texture(depth_tex, uv).r;

	float silhouette = 0.0;
	float convex = 0.0;
	float concave = 0.0;

	// Reverse-Z: 0 is the far plane, i.e. background. Draw nothing on it.
	if (raw_depth > 0.0000001) {
		vec3 p = view_pos(uv, INV_PROJECTION_MATRIX);
		vec3 n = view_normal(uv);
		float threshold = depth_threshold + depth_threshold_scale * -p.z;
		vec2 dirs[4] = vec2[](vec2(1.0, 0.0), vec2(-1.0, 0.0), vec2(0.0, 1.0), vec2(0.0, -1.0));
		vec2 texel = 1.0 / VIEWPORT_SIZE;

		for (int i = 0; i < 4; i++) {
			vec2 uv2 = uv + dirs[i] * texel * line_width;
			if (texture(depth_tex, uv2).r <= 0.0000001) {
				silhouette = 1.0;
				continue;
			}
			if (dot(p - view_pos(uv2, INV_PROJECTION_MATRIX), n) > threshold) {
				silhouette = 1.0;
			}
		}

		if (silhouette < 0.5 && (crease_opacity > 0.0 || highlight_opacity > 0.0)) {
			for (int i = 0; i < 4; i++) {
				vec2 uv2 = uv + dirs[i] * texel * crease_width;
				if (texture(depth_tex, uv2).r <= 0.0000001) {
					continue;
				}
				float behind = dot(p - view_pos(uv2, INV_PROJECTION_MATRIX), n);
				if (behind > threshold) {
					continue;
				}
				if (1.0 - dot(n, view_normal(uv2)) > 0.4) {
					if (behind > 0.0) {
						convex = 1.0;
					} else {
						concave = 1.0;
					}
				}
			}
			float up = (INV_VIEW_MATRIX * vec4(n, 0.0)).y;
			if (up < highlight_min_up) {
				convex = 0.0;
			}
		}
	}

	vec3 line = mix(line_color, colour * line_darken, line_tint_mix);
	// Additive, so the highlight survives the tonemapper's shoulder on bright surfaces.
	vec3 lit_edge = colour + highlight_color * (0.1 + 0.6 * dot(colour, vec3(1.0 / 3.0)));
	colour = mix(colour, lit_edge, convex * highlight_opacity);
	colour = mix(colour, line, concave * crease_opacity);
	colour = mix(colour, line, silhouette * line_opacity);
	if (debug_masks) {
		colour = vec3(silhouette, convex, concave) + texture(screen_tex, uv).rgb * 0.15;
	}
	ALBEDO = colour;
}
