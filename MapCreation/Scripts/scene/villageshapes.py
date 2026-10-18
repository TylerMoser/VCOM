"""The villages and hamlets as shapes for m2_scene.gd: worked out of SourceData/Villages.json
(../villages/v1_villages.py) the same way whether for the whole map's shapes (m1_shapes.py) or for
them alone (../villages/v2_shapes.py), so that villages spliced into the scene as it is are the
very nodes a scene made afresh would have.

Each place is a point; its lane, its channel and the bridges on its lane are lines, put through
geo.rounded as the roads are, so that none turns more than TURN degrees at one of its points.
Everything is in the picture's own measure, the middle of pixel (x, y) being (x + 0.5, y + 0.5).
"""
import numpy as np
import geo

TURN = 6.0               # degrees, as m1_shapes.py has it


def _line(points):
    p = np.round(np.asarray(points, dtype=np.float64) + 0.5, 3)
    keep = np.ones(len(p), dtype=bool)
    keep[1:] = (np.abs(np.diff(p, axis=0)) > 1e-9).any(axis=1)
    return geo.rounded(p[keep], False, TURN)[0]


def _flat(points):
    return [round(float(v), 3) for v in np.asarray(points).ravel()]


def _along_to(line, point):
    """How far along a line the point of it nearest [point] lies, in px."""
    a, b = line[:-1], line[1:]
    d = b - a
    length2 = np.maximum((d * d).sum(axis=1), 1e-12)
    t = np.clip(((point - a) * d).sum(axis=1) / length2, 0.0, 1.0)
    near = a + d * t[:, None]
    k = int(np.argmin(np.hypot(*(near - point).T)))
    return float(np.hypot(*d[:k].T).sum() + t[k] * np.sqrt(length2[k]))


def _piece(line, start, stop):
    """The part of a line between two distances along it."""
    travelled = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(line, axis=0).T))])
    inner = (travelled > start + 1e-6) & (travelled < stop - 1e-6)
    at = np.concatenate([[start], travelled[inner], [stop]])
    return np.stack([np.interp(at, travelled, line[:, 0]), np.interp(at, travelled, line[:, 1])], axis=1)


def shapes(villages):
    """(places, lanes, lane bridges, channels) out of Villages.json's contents."""
    by_id = {p["id"]: p for p in villages["places"]}
    places = []
    for p in villages["places"]:
        places.append({"name": p["name"], "kind": p["kind"], "county": p["county"], "duchy": p["duchy"], "kingdom": p["kingdom"],
                       "at": [round(p["x"] + 0.5, 3), round(p["y"] + 0.5, 3)]})
    lanes, bridges = [], []
    for lane in villages["lanes"]:
        line = _line(lane["points"])
        village = by_id[lane["village"]]["name"]
        lanes.append({"name": village + "Lane", "village": village, "px": round(float(np.hypot(*np.diff(line, axis=0).T).sum()), 1),
                      "points": _flat(line)})
        for i, bridge in enumerate(lane["bridges"]):
            ends = sorted(_along_to(line, np.asarray(bridge[key], dtype=np.float64) + 0.5) for key in ("from", "to"))
            name = village + "LaneBridge" + ("" if len(lane["bridges"]) == 1 else str(i + 1))
            bridges.append({"name": name, "over": bridge["over"], "points": _flat(_piece(line, ends[0], ends[1]))})
    channels = []
    for channel in villages["channels"]:
        line = _line(channel["points"])
        channels.append({"name": by_id[channel["village"]]["name"] + "Channel", "ends_in": channel["ends_in"]["kind"],
                         "px": round(float(np.hypot(*np.diff(line, axis=0).T).sum()), 1), "points": _flat(line)})
    return places, lanes, bridges, channels
