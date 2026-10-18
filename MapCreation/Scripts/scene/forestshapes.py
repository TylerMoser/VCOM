"""The forests as shapes for m2_scene.gd: SourceData/Forests.json (../forests/f1_forests.py) cut into the
pieces the scene draws, the same way whether for the whole map's shapes (m1_shapes.py) or for them
alone (../forests/f2_shapes.py), so that forests spliced into the scene as it is are the very nodes a
scene made afresh would have.

- **By county.** Each forest is cut by the counties' own outlines, so that a piece belongs to one
  county and stops exactly at the coast's line (Forests.json runs a forest on a little over the sea for
  this). Two pieces either side of a border have the very same points along it.
- **By kind,** in each county by its kingdom's rule (Forests.json "kinds"): the kingdom's own kind, or
  conifer over a height, or in the Swamp's kingdom swamp forest in the swamp country.
- **Holes bridged.** Godot's Polygon2D draws one outline and no holes, so each clearing in a piece is
  joined to its outline by a bridge: a cut of no width from a point of the clearing to the nearest
  point of the outline (or of a clearing joined before) that can be reached without crossing anything,
  out and back along the same line. The outline goes round the clearing on the way.
- **Known to draw, and quickly.** Every piece is cut into triangles here as Godot will cut it
  (godotcut.py), on the very float32 points the scene will hold. One that Godot could not cut, or
  one of more than MOST_POINTS points, which Godot would take long over as the scene opens, is cut
  in two, through the middle of its largest clearing, and each half tried again; a sliver under
  MIN_PIECE is dropped.
- **Grouped by size,** by the whole forest's area on land: Great (GROUPS), Large, Small, and Woods,
  the smallest, which the scene's Detail node brings in as the view closes in.

Points are given in the scene's units (100 m), rounded to the hundredth, ready to be put in the scene
as they are: the counties are given in those units too, as the scene has them.
"""
import numpy as np
import shapely
from shapely.geometry import LineString, Polygon, box
from shapely.geometry.polygon import orient
from shapely.strtree import STRtree
from scipy.spatial import cKDTree
import godotcut

UNITS = 3.35                     # units to a pixel of the pictures
UNITS2_KM2 = 0.01                # km2 in a square unit
# By the whole forest's area on land, km2 and more: its group, in the order the scene lists them.
GROUPS = [("Great", 250.0), ("Large", 50.0), ("Small", 10.0), ("Woods", 0.0)]
MIN_PIECE = 0.05                 # km2: a smaller piece (a sliver where a forest's edge runs along a county's) is left out
MOST_CUTS = 12                   # how many times a piece may be cut in two
# A piece with more points is cut in two. Godot cuts a polygon into triangles as the scene opens, in a
# time that grows with the square of its points: 125 pieces of 600 to 2,000 points took 0.55 s of the
# 0.6 s all 1,980 took (2026-10-17).
MOST_POINTS = 500


def _units(points):
    return (np.asarray(points, dtype=np.float64) + 0.5) * UNITS


def _shape(record):
    return Polygon(_units(record["outline"]), [_units(hole) for hole in record["holes"]])


def _parts(geometry):
    return [g for g in getattr(geometry, "geoms", [geometry]) if g.geom_type == "Polygon" and not g.is_empty]


def bridged(polygon):
    """One outline for a polygon with holes, each hole joined by a bridge of no width: [(x, y), ...], or
    None if a hole could not be joined."""
    polygon = orient(polygon, 1.0)
    ring = [tuple(c) for c in polygon.exterior.coords[:-1]]
    if not polygon.interiors:
        return ring
    holes = [[tuple(c) for c in r.coords[:-1]] for r in polygon.interiors]
    outline = cKDTree(np.asarray(ring))
    # The nearest the outline first, so that one further in can be joined to one joined before.
    order = sorted(range(len(holes)), key=lambda i: outline.query(np.asarray(holes[i]))[0].min())
    bridges = []
    ends = set()
    for i in order:
        hole = holes[i]
        targets = np.asarray(ring)
        near, which = cKDTree(targets).query(np.asarray(hole), k=min(8, len(targets)))
        near, which = np.atleast_2d(near), np.atleast_2d(which)
        pairs = sorted((float(near[a, b]), a, int(which[a, b])) for a in range(near.shape[0]) for b in range(near.shape[1]))
        for _, a, b in pairs[:600]:
            target = tuple(targets[b])
            if target in ends or hole[a] in ends:
                continue
            bridge = LineString([hole[a], target])
            # Through the forest only, touching nothing on its way, and crossing no bridge made before.
            if not shapely.relate_pattern(bridge, polygon, "1FF******"):
                continue
            if any(bridge.crosses(other) or bridge.overlaps(other) for other in bridges):
                continue
            ring = ring[:b + 1] + hole[a:] + hole[:a + 1] + ring[b:]
            bridges.append(bridge)
            ends.update((target, hole[a]))
            break
        else:
            return None
    return ring


def _snapped(ring):
    """The points rounded to the hundredth of a unit, with none twice running (a bridge's two visits to a
    point are never running)."""
    p = np.round(np.asarray(ring, dtype=np.float64), 2)
    keep = np.ones(len(p), dtype=bool)
    keep[1:] = (np.abs(np.diff(p, axis=0)) > 1e-9).any(axis=1)
    p = p[keep]
    if len(p) > 1 and (np.abs(p[0] - p[-1]) < 1e-9).all():
        p = p[:-1]
    return p


def drawable(polygon, tally, cuts=0):
    """A piece as outlines Godot can cut into triangles, none of more than MOST_POINTS: one, or more
    where it had to be cut."""
    ring = bridged(polygon)
    too_many = False
    if ring is not None:
        points = _snapped(ring)
        too_many = len(points) > MOST_POINTS and cuts < MOST_CUTS
        if not too_many and len(points) >= 3 and godotcut.triangulate(points) is not None:
            return [points]
    if not too_many and (polygon.area * UNITS2_KM2 < 4 * MIN_PIECE or cuts >= MOST_CUTS):
        tally["dropped"] += 1
        tally["dropped_km2"] += polygon.area * UNITS2_KM2
        return []
    tally["split" if too_many else "cut"] += 1
    # Through the middle of its largest clearing, or of the piece, across its longer side; so a cut
    # takes a bridge or two away as it goes.
    middle = (max(polygon.interiors, key=lambda r: Polygon(r).area).centroid if polygon.interiors else polygon.centroid)
    x0, y0, x1, y1 = polygon.bounds
    if x1 - x0 >= y1 - y0:
        halves = [box(x0 - 1, y0 - 1, middle.x, y1 + 1), box(middle.x, y0 - 1, x1 + 1, y1 + 1)]
    else:
        halves = [box(x0 - 1, y0 - 1, x1 + 1, middle.y), box(x0 - 1, middle.y, x1 + 1, y1 + 1)]
    out = []
    for half in halves:
        for part in _parts(polygon.intersection(half)):
            if part.area * UNITS2_KM2 >= MIN_PIECE:
                out.extend(drawable(part, tally, cuts + 1))
    return out


def shapes(forests, counties):
    """The pieces out of Forests.json's contents, cut by [counties]: a list of {"number", "duchy", "kingdom",
    "pieces": [[(x, y), ...], ...]} in the scene's units. Returns (pieces, figures)."""
    county_shapes, county_of = [], []
    for c in counties:
        for piece in c["pieces"]:
            county_shapes.append(shapely.make_valid(Polygon(np.round(np.asarray(piece, dtype=np.float64), 2))))
            county_of.append(c)
    county_tree = STRtree(county_shapes)
    kinds = forests["kinds"]
    base = {int(k): v for k, v in kinds["base"].items()}
    conifer_above = {int(k): float(v) for k, v in kinds["conifer_above_m"].items()}
    swamp_kingdom = int(kinds["swamp"]["kingdom"])
    regions = {}
    for name, polygons in kinds["regions"].items():
        regions[name] = shapely.make_valid(shapely.union_all([shapely.make_valid(_shape(p)) for p in polygons]))
        shapely.prepare(regions[name])
    swamp_country = regions[kinds["swamp"]["region"]]

    tally = {"cut": 0, "split": 0, "dropped": 0, "dropped_km2": 0.0, "slivers": 0}
    found = []                   # (points, county record, forest id, kind, km2)
    for record in forests["forests"]:
        forest = shapely.make_valid(_shape(record))
        for j in county_tree.query(forest, predicate="intersects"):
            c = county_of[j]
            part = forest.intersection(county_shapes[j])
            if part.is_empty:
                continue
            k = int(c["kingdom"])
            by_kind = []
            if k in conifer_above:
                high = regions["above_%d" % int(conifer_above[k])]
                by_kind.append((part.intersection(high), "conifer"))
                rest = part.difference(high)
                if k == swamp_kingdom:
                    by_kind.append((rest.intersection(swamp_country), "swamp"))
                    by_kind.append((rest.difference(swamp_country), "broadleaf"))
                else:
                    by_kind.append((rest, base[k]))
            else:
                by_kind.append((part, base[k]))
            for geometry, kind in by_kind:
                for piece in _parts(geometry):
                    if piece.area * UNITS2_KM2 < MIN_PIECE:
                        tally["slivers"] += 1
                        continue
                    for points in drawable(piece, tally):
                        found.append((points, c, int(record["id"]), kind, Polygon(points).area * UNITS2_KM2))

    forest_km2 = {}
    for points, c, f, kind, km2 in found:
        forest_km2[f] = forest_km2.get(f, 0.0) + km2
    # Named in their county, the largest first.
    found.sort(key=lambda e: (int(e[1]["number"]), -e[4]))
    counted = {}
    pieces = []
    for points, c, f, kind, km2 in found:
        number = int(c["number"])
        counted[number] = counted.get(number, 0) + 1
        group = next(name for name, least in GROUPS if forest_km2[f] >= least)
        pieces.append({"name": "County%03dForest%d" % (number, counted[number]), "group": group, "kind": kind,
                       "county": number, "duchy": int(c["duchy"]), "kingdom": int(c["kingdom"]), "forest": f,
                       "forest_km2": round(forest_km2[f], 1), "km2": round(km2, 3), "points": [float(v) for v in points.ravel()]})
    order = {name: i for i, (name, _) in enumerate(GROUPS)}
    pieces.sort(key=lambda p: (order[p["group"]], p["kingdom"], p["county"], int(p["name"].rsplit("Forest", 1)[1])))
    figures = {"pieces": len(pieces), "points": sum(len(p["points"]) // 2 for p in pieces), "cut_in_two": tally["cut"], "split_for_size": tally["split"],
               "dropped": tally["dropped"], "dropped_km2": round(tally["dropped_km2"], 2), "slivers": tally["slivers"],
               "by_group": {name: sum(p["group"] == name for p in pieces) for name, _ in GROUPS},
               "by_kind_km2": {}}
    for p in pieces:
        figures["by_kind_km2"][p["kind"]] = round(figures["by_kind_km2"].get(p["kind"], 0.0) + p["km2"], 1)
    return pieces, figures
