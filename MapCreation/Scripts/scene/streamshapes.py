"""The streams of SourceData/Streams.json as the scene wants them: shapes in m1_shapes.py's measure
(pixels from the pictures' top left corner, the middle of pixel (x, y) at (x + 0.5, y + 0.5)),
for m2_scene.gd to make into nodes. Used by m1_shapes.py, which makes the whole map's shapes,
and by ../streams/t2_shapes.py, which makes the streams' alone to add them to the scene as it is.
"""
import numpy as np

FLAT = 0.08              # px: a stream's width curve tells its width to within this
WIDENS = 0.3             # px: a stream that widens by less is drawn at its widest throughout
MARGIN = {"kingdom": 2.5, "duchy": 1.5, "county": 1.0}       # px: half each border's width, as m1_shapes.py's
RANK_OF = {"Kingdoms": "kingdom", "Duchies": "duchy", "Counties": "county"}


def _walked(p):
    return np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])


def _flat(points):
    return [round(float(v), 3) for v in np.asarray(points).ravel()]


def _profile(along, widths):
    """A stream's width along it in as few points as tell it to within FLAT: [[share of the way,
    width], ...], or nothing if it widens by less than WIDENS."""
    if float(np.max(widths) - np.min(widths)) <= WIDENS:
        return []
    t = along / along[-1]
    keep = np.zeros(len(t), dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(t) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        guess = widths[a] + (widths[b] - widths[a]) * (t[a + 1: b] - t[a]) / max(t[b] - t[a], 1e-12)
        off = np.abs(widths[a + 1: b] - guess)
        worst = int(np.argmax(off))
        if off[worst] > FLAT:
            k = a + 1 + worst
            keep[k] = True
            stack.append((a, k))
            stack.append((k, b))
    return [[round(float(t[i]), 5), round(float(widths[i]), 3)] for i in np.flatnonzero(keep)]


def stream(record):
    """One stream of Streams.json as a shape: its points, its width at its widest and how it
    narrows toward its source, and the group it goes in."""
    p = np.asarray(record["points"], dtype=np.float64) + 0.5
    w = np.asarray(record["width_px"], dtype=np.float64)
    along = _walked(p)
    return {"id": record["id"], "kingdom": record["kingdom"], "ends_in": record["ends_in"], "px": round(float(along[-1]), 1),
            "widest": round(float(w.max()), 3), "widths": _profile(along, w), "points": _flat(p)}


def bank(record):
    """One of Streams.json's along_borders as a bank of m1_shapes.py's: a line of the border's colour
    under the stream, as wide as the stream and the border on both sides of it."""
    p = np.asarray(record["points"], dtype=np.float64) + 0.5
    digits = "".join(ch if ch.isdigit() else " " for ch in record["border"]).split()
    return {"rank": record["rank"], "between": [int(digits[0]), int(digits[1])], "along": "stream", "id": record["stream"],
            "px": round(float(_walked(p)[-1]), 1), "widest": round(float(record["stream_width_px"]) + 2.0 * MARGIN[record["rank"]], 3),
            "widths": [], "points": _flat(p)}


def shapes(data):
    """The streams of a loaded Streams.json, and the banks laid under them where they run on a border."""
    return [stream(s) for s in data["streams"]], [bank(b) for b in data.get("along_borders", [])]
