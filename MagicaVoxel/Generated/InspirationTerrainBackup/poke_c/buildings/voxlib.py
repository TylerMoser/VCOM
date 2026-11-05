"""VOX reading and writing for the poke_c buildings.

Standard library only. Writes one model per file in the scene layout every VCOM
asset uses (root transform 0 -> group 1 -> transform 2 -> shape 3 -> model 0,
version 200, an explicit 256-entry palette), grounded with the translation
`0 0 floor(height / 2)`, so the importer puts the model's lowest layer at y = 0.

Unlike the earlier voxlib copies in this workspace, it writes a MATL chunk for
each used palette index with that index's own material: diffuse, or MagicaVoxel's
Glass (`_type _glass`, `_trans` its Transparency), which VCOM reads as glass
(Docs/GLASS.md in the game). The keys and values follow the game's own
MagicaVoxel/Buildings/make_windows.py.
"""
import struct
from pathlib import Path

GLASS_KEYS = {"_type": "_glass", "_rough": "0.05", "_ior": "0.5", "_ri": "1.5", "_d": "0.05"}


def _chunk(cid, payload=b"", children=b""):
    return cid.encode() + struct.pack("<ii", len(payload), len(children)) + payload + children


def _string(s):
    data = str(s).encode()
    return struct.pack("<i", len(data)) + data


def _dict(d):
    return struct.pack("<i", len(d)) + b"".join(_string(k) + _string(v) for k, v in d.items())


def material(index, glass=None):
    """The MATL properties of palette [index]: diffuse, or glass [glass] clear (0..1)."""
    if glass is None:
        return {"_type": "_diffuse", "_rough": "1"}
    props = dict(GLASS_KEYS)
    props["_trans"] = "%g" % glass
    return props


def write(path, size, voxels, palette, glass=None, name=None):
    """Writes [voxels] ((x, y, z) -> palette index 1..254) into a .vox at [path].

    [palette] is 256 RGBA tuples, entry i for index i + 1. [glass] maps palette
    indices to their Transparency: those indices are written as Glass."""
    glass = glass or {}
    path = Path(path)
    assert len(palette) == 256, "a palette has 256 entries"
    W, D, H = size
    assert 1 <= W <= 256 and 1 <= D <= 256 and 1 <= H <= 256, size
    ordered = sorted(voxels.items(), key=lambda kv: (kv[0][2], kv[0][1], kv[0][0]))
    xyzi = bytearray(struct.pack("<i", len(ordered)))
    for (x, y, z), c in ordered:
        assert 0 <= x < W and 0 <= y < D and 0 <= z < H, ((x, y, z), size)
        assert 1 <= c <= 254, "index %d: 0 is empty and 255 is the game's blood" % c
        xyzi += bytes((x, y, z, c))
    graph = _chunk("nTRN", struct.pack("<i", 0) + _dict({}) + struct.pack("<iiii", 1, -1, -1, 1) + _dict({}))
    graph += _chunk("nGRP", struct.pack("<i", 1) + _dict({}) + struct.pack("<ii", 1, 2))
    graph += _chunk("nTRN", struct.pack("<i", 2) + _dict({"_name": name or path.stem})
                    + struct.pack("<iiii", 3, -1, 0, 1) + _dict({"_t": "0 0 %d" % (H // 2)}))
    graph += _chunk("nSHP", struct.pack("<i", 3) + _dict({}) + struct.pack("<ii", 1, 0) + _dict({}))
    body = _chunk("SIZE", struct.pack("<iii", W, D, H)) + _chunk("XYZI", bytes(xyzi)) + graph
    body += _chunk("LAYR", struct.pack("<i", 0) + _dict({"_name": "Building"}) + struct.pack("<i", -1))
    body += _chunk("RGBA", b"".join(bytes(c) for c in palette))
    for c in sorted(set(voxels.values()) | set(glass)):
        body += _chunk("MATL", struct.pack("<i", c) + _dict(material(c, glass.get(c))))
    path.write_bytes(b"VOX " + struct.pack("<i", 200) + _chunk("MAIN", children=body))


def read(path):
    """(size, voxels, palette, materials) of the first model of the .vox at [path]."""
    data = Path(path).read_bytes()
    assert data[:4] == b"VOX ", path
    pos, size, voxels, palette, materials = 20, None, None, None, {}
    while pos < len(data):
        cid, n, m = struct.unpack_from("<4sii", data, pos)
        p = data[pos + 12:pos + 12 + n]
        if cid == b"SIZE" and size is None:
            size = struct.unpack("<iii", p)
        elif cid == b"XYZI" and voxels is None:
            voxels = {tuple(r[:3]): r[3] for r in struct.iter_unpack("BBBB", p[4:])}
        elif cid == b"RGBA":
            palette = [tuple(c) for c in struct.iter_unpack("BBBB", p)]
        elif cid == b"MATL":
            index = struct.unpack_from("<i", p)[0]
            off, props = 8, {}
            for _ in range(struct.unpack_from("<i", p, 4)[0]):
                k = struct.unpack_from("<i", p, off)[0]
                key = p[off + 4:off + 4 + k].decode()
                off += 4 + k
                v = struct.unpack_from("<i", p, off)[0]
                props[key] = p[off + 4:off + 4 + v].decode()
                off += 4 + v
            materials[index] = props
        pos += 12 + n + m
    assert size and voxels is not None and palette and len(palette) == 256, path
    return size, voxels, palette, materials


def components(cells):
    """Sizes of the six-connected components of [cells], largest first."""
    left = set(cells)
    sizes = []
    while left:
        todo = [left.pop()]
        size = 0
        while todo:
            x, y, z = todo.pop()
            size += 1
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in left:
                    left.remove(q)
                    todo.append(q)
        sizes.append(size)
    return sorted(sizes, reverse=True)
