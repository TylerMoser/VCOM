var properties = null;
var material: StandardMaterial3D = null;

# A palette entry's material, as MagicaVoxel saves it: a dictionary of strings.
# Since its extended materials (0.99.5 on) every key has a leading underscore:
# _type (_diffuse, _metal, _glass, _emit, _blend, _media), _rough, _metal,
# _spec, _trans, _emit, _flux, _ior / _ri and more. A file from before them
# kept a single _weight for every kind, which is read where a newer key is
# missing. An entry with no _type is diffuse.

var type:
	get:
		return properties.get("_type", "_diffuse");

var weight:
	get:
		return _number(["_weight"], 0.0);

## How metallic a metal material is, 0 to 1.
var metalness:
	get:
		return _number(["_metal", "_weight"], 1.0);

var specular:
	get:
		return _number(["_spec"], 0.5);

var roughness:
	get:
		return _number(["_rough"], 1.0);

## How strongly an emissive material glows, 0 to 1, and its power, MagicaVoxel's
## exponent of it.
var emission:
	get:
		return _number(["_emit", "_weight"], 1.0);

var flux:
	get:
		return _number(["_flux"], 0.0);

## How much of the light a glass material lets through, 0 to 1: MagicaVoxel's
## Transparency. At 1 it is clear glass, tinted by its colour; lower, more of
## it is drawn as a plain diffuse voxel would be, until at 0 it is opaque.
var transparency:
	get:
		return clampf(_number(["_trans", "_weight"], 1.0), 0.0, 1.0);

## Its index of refraction: _ri, or one more than _ior, which holds it so.
var refraction:
	get:
		return _number(["_ri"], 1.0 + _number(["_ior"], 0.0));

func _init(properties):
	self.properties = properties;

func is_glass():
	return self.type == "_glass";

## The first of [param keys] the material has, as a number, or [param fallback].
func _number(keys: Array, fallback: float) -> float:
	for key in keys:
		if properties.has(key):
			return float(str(properties[key]));
	return fallback;

func get_material(color: Color):
	if (material != null): return material;

	material = StandardMaterial3D.new();
	material.vertex_color_is_srgb = true;
	material.vertex_color_use_as_albedo = true;

	match (self.type):
		"_metal":
			material.metallic = self.metalness;
			material.metallic_specular = self.specular;
			material.roughness = self.roughness;
		"_emit":
			material.emission_enabled = true;
			material.emission = Color(color.r, color.g, color.b);
			# MagicaVoxel's power is a step up in brightness for each point.
			material.emission_energy_multiplier = self.emission * (1.0 + self.flux);
		"_glass":
			# Its colour, from the vertices, tints what shows through it.
			material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA;
			material.albedo_color = Color(1, 1, 1, 1.0 - self.transparency);
			material.roughness = self.roughness;
		"_diffuse", _:
			material.roughness = 1;
	return material;
