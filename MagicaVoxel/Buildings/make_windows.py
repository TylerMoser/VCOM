#!/usr/bin/env python3
"""Builds the window pieces in this folder from SimpleWall1.vox, which was drawn by hand.

    python3 make_windows.py

SimpleWindow1.vox is SimpleWall1 (a plain wall two voxels thick, a level high) with a
window in it: a white frame a voxel wide round a 12 x 12 opening, a mullion and a
transom two voxels wide across it, so four panes of 5 x 5, a white sill standing a voxel
proud of either face along its foot, and a voxel of wall all round. The panes are a
voxel thick, in the wall's second layer (x 8), so from one face they sit a voxel back
in the frame. Their colour is MagicaVoxel's Glass material: a pale palette entry
(GLASS_INDEX) whose material says _type _glass and how clear it is (_trans), which the
game reads as glass (Docs/GLASS.md).

Everything else of SimpleWall1 is kept: its palette, materials, layers, render
settings and its model's place (translation 0 21 8), so the window lines up with the
wall in the game under the same model_transform. Running it again overwrites
SimpleWindow1.vox, so a window edited by hand in MagicaVoxel is lost: copy it first.

MagicaVoxel's axes: x and y across, z up. The wall runs along y, its two layers at
x 7 and 8.
"""

import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "SimpleWall1.vox")

WALL = 237         # SimpleWall1's own colour, a pale tan
FRAME = 196        # off-white, the Apollo palette's lightest grey
GLASS_INDEX = 191  # a palette entry no piece uses, made pale glass
GLASS_RGBA = (226, 240, 244, 255)
GLASS_MATERIAL = {
    "_type": "_glass",
    "_trans": "0.9",
    "_rough": "0.05",
    "_ior": "0.5",
    "_ri": "1.5",
    "_d": "0.05",
}


def _string(s):
    data = s.encode()
    return struct.pack("<i", len(data)) + data


def _dict(d):
    out = struct.pack("<i", len(d))
    for k, v in d.items():
        out += _string(k) + _string(v)
    return out


def _chunk(cid, content, children=b""):
    return cid.encode() + struct.pack("<ii", len(content), len(children)) + content + children


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


def window():
    """SimpleWindow1's voxels, (x, y, z) -> palette index."""
    voxels = {}
    for y in range(16):
        for z in range(16):
            for x in (7, 8):
                voxels[(x, y, z)] = WALL
    # The frame and its opening, a voxel in from every side of the piece.
    for y in range(1, 15):
        for z in range(1, 15):
            for x in (7, 8):
                del voxels[(x, y, z)]
            ring = y in (1, 14) or z in (1, 14)
            bar = y in (7, 8) or z in (7, 8)
            for x in (7, 8):
                if ring or bar:
                    voxels[(x, y, z)] = FRAME
            if not (ring or bar):
                voxels[(8, y, z)] = GLASS_INDEX
    # The sill, proud of both faces.
    for y in range(1, 15):
        voxels[(6, y, 1)] = FRAME
        voxels[(9, y, 1)] = FRAME
    return voxels


def write(path, voxels):
    ordered = sorted(voxels.items(), key=lambda kv: (kv[0][2], kv[0][1], kv[0][0]))
    xyzi = struct.pack("<i", len(ordered))
    for (x, y, z), c in ordered:
        assert 1 <= c <= 255 and 0 <= x < 16 and 0 <= y < 16 and 0 <= z < 16
        xyzi += struct.pack("<BBBB", x, y, z, c)
    body = b""
    for cid, raw in _chunks(open(SOURCE, "rb").read()):
        if cid == "XYZI":
            body += _chunk("XYZI", xyzi)
        elif cid == "RGBA":
            # The chunk lists palette entries 1 to 256, entry i at i - 1.
            colors = bytearray(raw[12:12 + 1024])
            at = (GLASS_INDEX - 1) * 4
            colors[at:at + 4] = bytes(GLASS_RGBA)
            body += _chunk("RGBA", bytes(colors))
        elif cid == "MATL" and struct.unpack_from("<i", raw, 12)[0] == GLASS_INDEX:
            body += _chunk("MATL", struct.pack("<i", GLASS_INDEX) + _dict(GLASS_MATERIAL))
        else:
            body += raw
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 200) + _chunk("MAIN", b"", body))


def main():
    voxels = window()
    path = os.path.join(HERE, "SimpleWindow1.vox")
    write(path, voxels)
    glass = sum(1 for c in voxels.values() if c == GLASS_INDEX)
    print("SimpleWindow1  %d voxels, %d of them glass" % (len(voxels), glass))


if __name__ == "__main__":
    main()
