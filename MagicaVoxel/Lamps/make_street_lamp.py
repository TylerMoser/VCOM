#!/usr/bin/env python3
"""Builds the street lamp in this folder, and the three pieces the game places it as.

    python3 make_street_lamp.py           # build StreetLamp1.vox afresh, then split it
    python3 make_street_lamp.py --split   # only split StreetLamp1.vox, as edited by hand

StreetLamp1.vox is the whole lamp, one MagicaVoxel model 16 x 16 x 48 voxels (three
cells tall): an iron post on a plinth, a brass finial, an arm reaching out over a
lantern of four iron corner posts and glass sides and bottom under an iron cap, and a
bulb inside it. Edit it in MagicaVoxel as one model; the game cannot place a piece
taller than a cell, so the split cuts it into three 16 x 16 x 16 pieces,
StreetLamp1Bottom, StreetLamp1Middle and StreetLamp1Top, written here and copied into
../../vcom/Blocks/, where the game imports them (Docs/LIGHTS.md has the rest, and the
pieces' kinds and brush in Pieces.tres).

Running it with no --split overwrites StreetLamp1.vox, so a lamp edited by hand is lost:
copy it first, or split only.

Its colours sit in palette row 185-192, just above the Apollo palette every piece
takes from ../Plants/LeafCluster1.vox (as the shapes do), with their materials:

    185  iron                     post, plinth, arm, cap         diffuse
    186  iron (casts no lamp's    the lantern's corner posts     diffuse; listed in the
         shadow)                                                 top piece's
                                                                 shadowless_colors
    187  brass                    finial                         diffuse
    188  pale glass               the lantern's sides, bottom    Glass, Transparency 0.85
    189  warm white bulb          the bulb                       Emit, Emission 0.75,
                                                                 Power 2

A colour drawn with the Emit material glows at dusk and at night as brightly as its
Emission says (0.75 is six times its own colour), and casts light as far and as bright
as its Power says (2: brightness 4, reach 7 cells). Colour 186 is the same iron as 185,
apart only so the game can leave the corner posts out of the lamp's own shadow: right
beside the bulb, their shadows would fan out across the map.

MagicaVoxel's axes: x and y across, z up; the game turns them into Godot's x, -z and y.
The arm reaches toward +x.
"""

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "Plants", "LeafCluster1.vox")
LAMP = os.path.join(HERE, "StreetLamp1.vox")
BLOCKS = os.path.join(HERE, "..", "..", "vcom", "Blocks")
N = 16
TALL = 48

IRON = 185
FIXTURE = 186
BRASS = 187
GLASS = 188
BULB = 189
COLORS = {
    IRON: (46, 48, 54, 255),
    FIXTURE: (46, 48, 54, 255),
    BRASS: (122, 98, 60, 255),
    GLASS: (236, 240, 232, 255),
    BULB: (255, 210, 140, 255),
}
MATERIALS = {
    GLASS: {"_type": "_glass", "_trans": "0.85", "_rough": "0.05", "_ior": "0.5", "_ri": "1.5", "_d": "0.05"},
    BULB: {"_type": "_emit", "_emit": "0.75", "_flux": "2", "_ldr": "0"},
}
PIECE_NAMES = {1: [""], 2: ["Bottom", "Top"], 3: ["Bottom", "Middle", "Top"]}


def _chunk(cid, content, children=b""):
    return cid.encode() + struct.pack("<ii", len(content), len(children)) + content + children


def _string(s):
    data = s.encode()
    return struct.pack("<i", len(data)) + data


def _dict(d):
    out = struct.pack("<i", len(d))
    for k, v in d.items():
        out += _string(k) + _string(v)
    return out


def _chunks(data):
    """The chunks inside the MAIN chunk, each as (id, its bytes whole)."""
    assert data[:4] == b"VOX ", "not a .vox"
    found, offset = [], 20
    while offset < len(data):
        cid = data[offset:offset + 4].decode()
        n, m = struct.unpack_from("<ii", data, offset + 4)
        found.append((cid, data[offset:offset + 12 + n + m]))
        offset += 12 + n + m
    return found


def lamp():
    """The lamp's voxels, (x, y, z) -> palette index, in MagicaVoxel's axes, z up.
    Laid out first in Godot's (gx, gy up, gz), as it was drawn for the research."""
    voxels = {}

    def put(gx, gy, gz, color):
        voxels[(gx, 15 - gz, gy)] = color

    for gy in range(TALL):
        for gx in range(N):
            for gz in range(N):
                color = 0
                if gy <= 2 and 6 <= gx <= 9 and 6 <= gz <= 9:
                    color = IRON                                  # plinth
                elif 3 <= gy <= 45 and 7 <= gx <= 8 and 7 <= gz <= 8:
                    color = IRON                                  # post
                elif 46 <= gy <= 47 and 7 <= gx <= 8 and 7 <= gz <= 8:
                    color = BRASS                                 # finial
                elif 43 <= gy <= 44 and 9 <= gx <= 13 and 7 <= gz <= 8:
                    color = IRON                                  # arm
                elif 41 <= gy <= 42 and 12 <= gx <= 13 and 7 <= gz <= 8:
                    color = IRON                                  # hook
                elif 39 <= gy <= 40 and 10 <= gx <= 15 and 5 <= gz <= 10:
                    color = IRON                                  # cap
                elif 32 <= gy <= 38:
                    corner = gx in (10, 15) and gz in (5, 10)
                    side = (gx in (10, 15) and 5 < gz < 10) or (gz in (5, 10) and 10 < gx < 15)
                    inside = 10 < gx < 15 and 5 < gz < 10
                    if corner:
                        color = FIXTURE                           # the lantern's corners
                    elif side and gy >= 33:
                        color = GLASS                             # its sides
                    elif inside and gy == 32:
                        color = GLASS                             # its bottom
                    elif 34 <= gy <= 37 and 12 <= gx <= 13 and 7 <= gz <= 8:
                        color = BULB                              # the bulb
                if color:
                    put(gx, gy, gz, color)
    return voxels


def _graph(height):
    """The scene MagicaVoxel saves: one model, centred, its bottom on the ground."""
    return (
        _chunk("nTRN", struct.pack("<i", 0) + _dict({}) + struct.pack("<iiii", 1, -1, -1, 1) + _dict({}))
        + _chunk("nGRP", struct.pack("<i", 1) + _dict({}) + struct.pack("<ii", 1, 2))
        + _chunk("nTRN", struct.pack("<i", 2) + _dict({}) + struct.pack("<iiii", 3, -1, 0, 1)
                 + _dict({"_t": "0 0 %d" % (height // 2)}))
        + _chunk("nSHP", struct.pack("<i", 3) + _dict({}) + struct.pack("<i", 1)
                 + struct.pack("<i", 0) + _dict({}))
    )


def write(path, voxels, height, source_chunks, colors=None, materials=None):
    """A .vox of one model, N x N x height, of [voxels], with every other chunk of
    [source_chunks] as it is but for the palette entries and materials given."""
    ordered = sorted(voxels.items(), key=lambda kv: (kv[0][2], kv[0][1], kv[0][0]))
    xyzi = struct.pack("<i", len(ordered))
    for (x, y, z), c in ordered:
        assert 1 <= c <= 255 and 0 <= x < N and 0 <= y < N and 0 <= z < height, (x, y, z, c)
        xyzi += struct.pack("<BBBB", x, y, z, c)
    graph = _graph(height)
    body = b""
    for cid, raw in source_chunks:
        if cid == "SIZE":
            body += _chunk("SIZE", struct.pack("<iii", N, N, height))
        elif cid == "XYZI":
            body += _chunk("XYZI", xyzi)
        elif cid in ("nTRN", "nGRP", "nSHP"):
            if graph:
                body += graph
                graph = b""
        elif cid == "RGBA" and colors:
            # The chunk lists palette entries 1 to 256, entry i at i - 1.
            table = bytearray(raw[12:12 + 1024])
            for index, rgba in colors.items():
                table[(index - 1) * 4:(index - 1) * 4 + 4] = bytes(rgba)
            body += _chunk("RGBA", bytes(table))
        elif cid == "MATL" and materials and struct.unpack_from("<i", raw, 12)[0] in materials:
            index = struct.unpack_from("<i", raw, 12)[0]
            body += _chunk("MATL", struct.pack("<i", index) + _dict(materials[index]))
        else:
            body += raw
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 200) + _chunk("MAIN", b"", body))


def read(path):
    """(voxels, size, chunks) of the one model of the .vox at [path]."""
    chunks = _chunks(open(path, "rb").read())
    size = None
    voxels = {}
    for cid, raw in chunks:
        if cid == "SIZE" and size is None:
            size = struct.unpack_from("<iii", raw, 12)
        elif cid == "XYZI" and not voxels:
            count = struct.unpack_from("<i", raw, 12)[0]
            for at in range(count):
                x, y, z, c = struct.unpack_from("<BBBB", raw, 16 + at * 4)
                voxels[(x, y, z)] = c
    return voxels, size, chunks


def split(path, blocks=True):
    """Cuts the model of the .vox at [path] into pieces a cell tall, bottom up, each
    written beside it and, if [blocks], into ../../vcom/Blocks/."""
    voxels, size, chunks = read(path)
    assert size[0] == N and size[1] == N, "the lamp must be 16 x 16 voxels across, not %s" % (size,)
    count = (size[2] + N - 1) // N
    names = PIECE_NAMES.get(count) or (["Bottom"] + ["Middle%d" % i for i in range(1, count - 1)] + ["Top"])
    base = os.path.splitext(os.path.basename(path))[0]
    for at in range(count):
        part = {(x, y, z - at * N): c for (x, y, z), c in voxels.items() if at * N <= z < (at + 1) * N}
        name = base + names[at]
        targets = [os.path.join(HERE, name + ".vox")]
        if blocks:
            targets.append(os.path.join(BLOCKS, name + ".vox"))
        for target in targets:
            write(target, part, N, chunks)
        print("%-20s %4d voxels" % (name, len(part)))


def main(args):
    if "--split" not in args:
        voxels = lamp()
        write(LAMP, voxels, TALL, _chunks(open(TEMPLATE, "rb").read()), COLORS, MATERIALS)
        print("StreetLamp1          %4d voxels, %d glowing, %d glass" % (
            len(voxels), sum(1 for c in voxels.values() if c == BULB), sum(1 for c in voxels.values() if c == GLASS)))
    split(LAMP)


if __name__ == "__main__":
    main(sys.argv[1:])
