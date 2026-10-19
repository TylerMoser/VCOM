// Shows the screen as someone with a colour vision deficiency would see it:
// Machado, Oliveira and Fernandes (2009), "A Physiologically-based Model for
// Simulation of Color Vision Deficiency", at full severity, applied in linear
// light. Put on a full-screen ColorRect in a CanvasLayer over the map.
shader_type canvas_item;

// 0 deuteranopia (no green cones; with the milder deuteranomaly, about 1 man
// in 17), 1 protanopia (no red cones), 2 tritanopia (no blue cones, rare),
// 3 greyscale (relative luminance alone: what is left when hue is taken away,
// the test of whether a map's kinds differ by more than hue).
uniform int kind = 0;
uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;

vec3 to_linear(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

vec3 to_srgb(vec3 c) {
	c = clamp(c, 0.0, 1.0);
	return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(vec3(0.0031308), c));
}

void fragment() {
	vec3 c = to_linear(texture(screen_tex, SCREEN_UV).rgb);
	vec3 r0;
	vec3 r1;
	vec3 r2;
	if (kind == 1) {
		r0 = vec3(0.152286, 1.052583, -0.204868);
		r1 = vec3(0.114503, 0.786281, 0.099216);
		r2 = vec3(-0.003882, -0.048116, 1.051998);
	} else if (kind == 2) {
		r0 = vec3(1.255528, -0.076749, -0.178779);
		r1 = vec3(-0.078411, 0.930809, 0.147602);
		r2 = vec3(0.004733, 0.691367, 0.303900);
	} else if (kind == 3) {
		r0 = vec3(0.2126, 0.7152, 0.0722);
		r1 = r0;
		r2 = r0;
	} else {
		r0 = vec3(0.367322, 0.860646, -0.227968);
		r1 = vec3(0.280085, 0.672501, 0.047413);
		r2 = vec3(-0.011820, 0.042940, 0.968881);
	}
	COLOR = vec4(to_srgb(vec3(dot(r0, c), dot(r1, c), dot(r2, c))), 1.0);
}
