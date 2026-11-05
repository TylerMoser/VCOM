"""Reading and writing MagicaVoxel .vox files for the character generator.

Every file is written from Character_Bigger.vox as a template: its chunks are kept in order
(META, the scene graph, the layers, the render and camera settings, the note) and only the
model's SIZE and XYZI, the palette (RGBA) and the materials (MATL) are replaced, so a
generated model opens and imports exactly as the base figure does. The scene graph's model
translation is set to stand the model on the ground, centred: "0 0 <height / 2>".
"""
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, '..', 'Character_Bigger.vox')

BLOOD = 255  # the game keeps palette place 255 for blood: never paint with it


def _chunks(data, start, end):
    i = start
    out = []
    while i < end:
        cid = data[i:i + 4]
        n, m = struct.unpack('<II', data[i + 4:i + 12])
        out.append((cid, data[i + 12:i + 12 + n], data[i + 12 + n:i + 12 + n + m]))
        i += 12 + n + m
    return out


def _string(s):
    b = s.encode('latin1')
    return struct.pack('<I', len(b)) + b


def _dict(d):
    out = struct.pack('<I', len(d))
    for k, v in d.items():
        out += _string(k) + _string(str(v))
    return out


def _read_string(b, i):
    n = struct.unpack('<I', b[i:i + 4])[0]
    return b[i + 4:i + 4 + n].decode('latin1'), i + 4 + n


def _read_dict(b, i):
    n = struct.unpack('<I', b[i:i + 4])[0]
    i += 4
    out = {}
    for _ in range(n):
        k, i = _read_string(b, i)
        v, i = _read_string(b, i)
        out[k] = v
    return out, i


def read(path):
    """The first model's size and voxels {(x, y, z): place}, the palette (256 RGBA, place 1
    first) and the materials {place: dict}."""
    data = open(path, 'rb').read()
    assert data[:4] == b'VOX '
    main = _chunks(data, 8, len(data))[0]
    children = _chunks(main[2], 0, len(main[2]))
    size, voxels, palette, materials = None, None, None, {}
    for cid, body, _ in children:
        if cid == b'SIZE' and size is None:
            size = struct.unpack('<III', body[:12])
        elif cid == b'XYZI' and voxels is None:
            count = struct.unpack('<I', body[:4])[0]
            voxels = {}
            for k in range(count):
                x, y, z, c = body[4 + 4 * k:8 + 4 * k]
                voxels[(x, y, z)] = c
        elif cid == b'RGBA':
            palette = [tuple(body[4 * k:4 * k + 4]) for k in range(256)]
        elif cid == b'MATL':
            mid = struct.unpack('<I', body[:4])[0]
            props, _ = _read_dict(body, 4)
            materials[mid] = props
    return size, voxels, palette, materials


_template_cache = None


def _template():
    global _template_cache
    if _template_cache is None:
        data = open(TEMPLATE, 'rb').read()
        main = _chunks(data, 8, len(data))[0]
        _template_cache = (data[:8], _chunks(main[2], 0, len(main[2])))
    return _template_cache


def write(path, size, voxels, palette, materials=None):
    """Writes a model. [voxels] maps (x, y, z) to a palette place 1..254; [palette] is a list
    of up to 255 RGBA tuples for places 1.. (padded with grey); [materials] maps a place to
    the MATL properties replacing the template's for it (glass, emit)."""
    materials = materials or {}
    header, chunks = _template()
    sx, sy, sz = size
    for (x, y, z), c in voxels.items():
        if not (0 <= x < sx and 0 <= y < sy and 0 <= z < sz):
            raise ValueError('voxel %s outside the canvas %s in %s' % ((x, y, z), size, path))
        if not 1 <= c <= 254:
            raise ValueError('palette place %d at %s in %s' % (c, (x, y, z), path))
    rgba = list(palette) + [(128, 128, 128, 255)] * (256 - len(palette))
    rgba = rgba[:256]
    out = b''
    for cid, body, kids in chunks:
        if cid == b'SIZE':
            body = struct.pack('<III', sx, sy, sz)
        elif cid == b'XYZI':
            items = sorted(voxels.items(), key=lambda kv: (kv[0][2], kv[0][1], kv[0][0]))
            body = struct.pack('<I', len(items)) + b''.join(struct.pack('<BBBB', x, y, z, c) for (x, y, z), c in items)
        elif cid == b'RGBA':
            body = b''.join(struct.pack('<BBBB', *e) for e in rgba)
        elif cid == b'MATL':
            mid = struct.unpack('<I', body[:4])[0]
            if mid in materials:
                body = struct.pack('<I', mid) + _dict(materials[mid])
        elif cid == b'nTRN':
            nid = struct.unpack('<I', body[:4])[0]
            if nid == 2:
                attrs, j = _read_dict(body, 4)
                child, reserved, layer, nframes = struct.unpack('<iiiI', body[j:j + 16])
                body = struct.pack('<I', nid) + _dict(attrs) + struct.pack('<iiiI', child, reserved, layer, 1) + _dict({'_t': '0 0 %d' % (sz // 2)})
        out += cid + struct.pack('<II', len(body), len(kids)) + body + kids
    data = header + b'MAIN' + struct.pack('<II', 0, len(out)) + out
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)
    return data


def glass_material(clarity=0.6):
    return {'_type': '_glass', '_trans': '%.2f' % clarity, '_rough': '0.1', '_ior': '0.3', '_ri': '1.3', '_d': '0.05'}


def emit_material(emission=0.8, power=1):
    return {'_type': '_emit', '_emit': '%.2f' % emission, '_flux': str(power), '_ldr': '0'}
