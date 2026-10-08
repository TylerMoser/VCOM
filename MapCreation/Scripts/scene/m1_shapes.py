"""The map as shapes: everything the pictures show, worked out of the source data as outlines and
lines with points finer than a pixel, ready to be made into a Godot scene.

Out of the maps of numbers come the areas: the counties (and with them the land, the duchies and
the kingdoms), and the lakes. Their edges are smoothed once and shared: two counties that touch
have the very same points along their border, and so has the border's line. Out of the tables come
the lines that are lines already: rivers, roads and bridges, and the settlements.

Three things are put right on the way, where the pictures' pixels hid them:
- a border that follows a river is put on the river's own line (the two were drawn a pixel or two
  apart, the river swinging from side to side of its bed);
- lines get a point wherever they bend, so that none turns sharply at any one point however far
  the map is enlarged;
- a few pixels of the counties' map, left crooked where the coast was mended, are straightened (MENDS).

Everything is written in the picture's own measure (pixels from its top left corner, so the middle
of pixel (x, y) is (x + 0.5, y + 0.5)); m2_scene.gd turns that into the scene's.

Usage: m1_shapes.py <MapCreation dir> <shapes .json to write>
"""
import json
import sys
import time
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree
import geo

Image.MAX_IMAGE_PIXELS = None
MC, WRITE_TO = sys.argv[1:3]
SRC = MC + "/SourceData"
GIVE = 0.6               # px a smoothed edge may leave the staircase it is smoothed from
TURN = 6.0               # degrees: no line turns more than this at any one of its points
SPARE = 0.015            # px: a point of an edge made here is left out if the edge moves less than this without it
INTO_INK = 3.0           # px a river or a border runs on past the land's edge, into the coast's line
SPECK = 2                # px: a piece of a lake smaller than this, joined only by a corner, is left out
TONGUE = 1               # px: a tongue of a county one pixel wide and this long or longer is given to the county beside it
BODY, CORE = 4.0, 8.0    # a lake is broad where a disc of radius BODY fits in it, joined to where one of radius CORE fits
FLAT = 0.04              # px: a river's width is taken as even where it changes by less than this
FOLLOW = 12.0            # px a border keeps to a river, a lake or a road before it is said to run along it...
FOLLOW_WIDTHS = 1.5      # ...or this many times the water's width, if that is more
NEAR_RIVER = 3.0         # px: a border that keeps this close to a river for FOLLOW px is following it
ON_RIVER = 0.75          # px: a border this close to a river's line is on it
EASE = 6.0               # px over which a border that was beside a river is brought on to its line
SAMPLE = 0.5             # px between the places a river or road is tried at
BESIDE = 0.75            # px: a border this close to a river's or road's edge still counts as under it
BANK_SLACK = 0.75        # px a smoothed shore may lie beyond where the pixels put it
BANK_GAP = 6.0           # px: a shorter break in a border's colour along a lake's shore is closed
REACH = 10               # px: half the widest narrow water, and one more
LOOK, LOOK_REACH = 48, 4.6   # how many of the places sampled along the rivers are looked at round a point, and within how many px
CHANGE = 6.0             # px: a border changes from keeping to one river to another only if staying would put it this much further off
KINGDOM, DUCHY, COUNTY, COAST = 3, 2, 1, 4
RANK_NAMES = {KINGDOM: "kingdom", DUCHY: "duchy", COUNTY: "county"}
MARGIN = {"kingdom": 2.5, "duchy": 1.5, "county": 1.0}       # px: half each border's width
# Pixels of CountyMap.png given to another county: (first x, last x, y, from, to). Where the coast
# was mended at the join of two of its hand-drawn sheets (about 2685, 2400) a strip of land changed
# county, and the border was left with a hook three pixels deep at the shore. These run it straight.
MENDS = [(2681, 2684, 2401, 103, 101), (2682, 2684, 2400, 103, 101), (2678, 2678, 2402, 101, 103)]


def load_json(name):
    with open(SRC + "/" + name, encoding="utf-8") as handle:
        return json.load(handle)


def flat(points):
    return [round(float(v), 3) for v in np.asarray(points).ravel()]


def tidy(points, closed=False):
    """Points rounded to a thousandth of a pixel, with none twice running."""
    p = np.round(np.asarray(points, dtype=np.float64), 3)
    keep = np.ones(len(p), dtype=bool)
    keep[1:] = (np.abs(np.diff(p, axis=0)) > 1e-9).any(axis=1)
    p = p[keep]
    if closed and len(p) > 1 and (np.abs(p[0] - p[-1]) < 1e-9).all():
        p = p[:-1]
    return p


def joined(parts, closed):
    """Runs of points end to end as one, the shared point between two of them kept once."""
    out = [parts[0]]
    for part in parts[1:]:
        out.append(part[1:] if (np.abs(out[-1][-1] - part[0]) < 1e-9).all() else part)
    p = np.concatenate(out)
    if closed and (np.abs(p[0] - p[-1]) < 1e-9).all():
        p = p[:-1]
    return p


def signed_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def length_of(p, closed=False):
    q = np.concatenate([p, p[:1]]) if closed else p
    return float(np.hypot(*np.diff(q, axis=0).T).sum())


def walked(p):
    """How far along a line each of its points is."""
    return np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])


def runs_of(flags):
    """[first, last] of every run of True."""
    f = np.concatenate([[False], np.asarray(flags, dtype=bool), [False]])
    change = np.flatnonzero(f[1:] != f[:-1])
    return [(int(a), int(b) - 1) for a, b in zip(change[::2], change[1::2])]


def nearest_on(line, point):
    """The point of a line nearest a point: (place, distance, how far along the line in px)."""
    a, b = line[:-1], line[1:]
    d = b - a
    length2 = np.maximum((d * d).sum(axis=1), 1e-12)
    t = np.clip(((point - a) * d).sum(axis=1) / length2, 0.0, 1.0)
    near = a + d * t[:, None]
    off = np.hypot(*(near - point).T)
    k = int(np.argmin(off))
    along = float(np.hypot(*d[:k].T).sum() + t[k] * np.sqrt(length2[k]))
    return near[k], float(off[k]), along


def stretch_of(line, values, start, stop):
    """The part of a line between two distances along it, with a value carried along: (points, values)."""
    travelled = walked(line)
    inner = (travelled > start + 1e-6) & (travelled < stop - 1e-6)
    at = np.concatenate([[start], travelled[inner], [stop]])
    points = np.stack([np.interp(at, travelled, line[:, 0]), np.interp(at, travelled, line[:, 1])], axis=1)
    return points, (np.interp(at, travelled, values) if np.ndim(values) else np.full(len(at), float(values)))


def sampled(lines, halves):
    """Places all along some lines, [SAMPLE] apart: (points, half the line's width there, which line, how far along it)."""
    pts, half, which, along = [], [], [], []
    for key, line in lines.items():
        travelled = walked(line)
        at = np.arange(0.0, travelled[-1] + SAMPLE, SAMPLE).clip(max=travelled[-1])
        pts.append(np.stack([np.interp(at, travelled, line[:, 0]), np.interp(at, travelled, line[:, 1])], axis=1))
        hw = halves[key]
        half.append(np.interp(at, travelled, hw) if np.ndim(hw) else np.full(len(at), float(hw)))
        which.append(np.full(len(at), key))
        along.append(at)
    return np.concatenate(pts), np.concatenate(half), np.concatenate(which), np.concatenate(along)


def profile(along, widths):
    """A line's width along it in as few points as tell it to within [FLAT]: [[share of the way, width], ...],
    or nothing if it is even."""
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
    shape = [[round(float(t[i]), 5), round(float(widths[i]), 3)] for i in np.flatnonzero(keep)]
    return shape if max(v for _, v in shape) - min(v for _, v in shape) > FLAT else []


def disc(radius):
    r = int(np.floor(radius))
    y, x = np.ogrid[-r: r + 1, -r: r + 1]
    return x * x + y * y <= radius * radius


started = time.time()
out = {"about": "The map as shapes, in pixels of the pictures measured from the top left corner (the middle of pixel (x, y) is (x + 0.5, y + 0.5)). Made by m1_shapes.py from MapCreation/SourceData.",
       "size": [3100, 4000], "km_per_px": 0.335}

# == the counties' map, mended ============================================================================
county = np.array(Image.open(SRC + "/CountyMap.png")).astype(np.int32)
for x0, x1, y, was, now in MENDS:
    assert (county[y, x0: x1 + 1] == was).all(), "CountyMap.png is not as the mends expect at row %d" % y
    county[y, x0: x1 + 1] = now
land = county > 0
h, w = county.shape
regions = load_json("Regions.json")
duchy_of = {c["number"]: c["duchy"] for c in regions["counties"]}
kingdom_of = {c["number"]: c["kingdom"] for c in regions["counties"]}


def without_tongues(numbers):
    """Gives away every tongue of a county that is one pixel wide and TONGUE or more long: the
    pixels no 2 x 2 block of their own county covers, in groups. Each goes to the other county it
    lies longest against, unless that would cut its own county in two. The long ones are left
    where three counties meet, a pixel's width of one running on between the other two; as a shape
    such a tongue would be a spike. The short ones are single pixels standing out of a border,
    which as a shape would be a kink in it. Returns (tongues, pixels)."""
    tongues = pixels = 0
    for _ in range(4):
        right = numbers[:, :-1] == numbers[:, 1:]
        down = numbers[:-1, :] == numbers[1:, :]
        block = right[:-1, :] & right[1:, :] & down[:, :-1] & down[:, 1:]
        covered = np.zeros(numbers.shape, dtype=bool)
        covered[:-1, :-1] |= block
        covered[:-1, 1:] |= block
        covered[1:, :-1] |= block
        covered[1:, 1:] |= block
        groups, n = ndimage.label((numbers > 0) & ~covered, structure=np.ones((3, 3)))
        given = 0
        for k, box in enumerate(ndimage.find_objects(groups), start=1):
            ys, xs = np.nonzero(groups[box] == k)
            ys, xs = ys + box[0].start, xs + box[1].start
            own = int(np.bincount(numbers[ys, xs]).argmax())
            mine = numbers[ys, xs] == own
            ys, xs = ys[mine], xs[mine]
            if len(ys) < TONGUE:
                continue
            beside = {}
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                for v in numbers[np.clip(ys + dy, 0, numbers.shape[0] - 1), np.clip(xs + dx, 0, numbers.shape[1] - 1)]:
                    if v != own and v > 0:
                        beside[int(v)] = beside.get(int(v), 0) + 1
            if not beside:
                continue
            # Not if it is a neck: its county must stay in as many pieces as it was.
            around = (slice(max(ys.min() - 2, 0), ys.max() + 3), slice(max(xs.min() - 2, 0), xs.max() + 3))
            before = ndimage.label(numbers[around] == own)[1]
            numbers[ys, xs] = max(beside, key=beside.get)
            if ndimage.label(numbers[around] == own)[1] > before:
                numbers[ys, xs] = own
                continue
            given += 1
            pixels += len(ys)
        tongues += given
        if not given:
            break
    return tongues, pixels


tongues, tongue_px = without_tongues(county)
print("the counties' map: %d px given to another county to straighten a border's end; %d tongues a pixel wide (%d px in all) given to the county beside them" % (
    sum(x1 - x0 + 1 for x0, x1, _, _, _ in MENDS), tongues, tongue_px))

# == the rivers =============================================================================================
# First, since a border that follows a river is put on the river's line.
to_land = ndimage.distance_transform_edt(~land)


def past_land(p):
    """How far beyond the land's edge each point lies (0 on land)."""
    d = ndimage.map_coordinates(to_land, [p[:, 1] - 0.5, p[:, 0] - 0.5], order=1, mode="nearest")
    return np.maximum(d - 0.5, 0.0)


rivers_table = load_json("Rivers.json")["rivers"]
river_lines, river_widths = {}, {}
rivers = []
cut_short, put_on, worst_join = 0, 0, 0.0
for river in rivers_table:
    p = np.asarray(river["points"], dtype=np.float64) + 0.5
    wide = np.asarray(river["width_px"], dtype=np.float64)
    if river["ends_in"] == "sea":
        # The line runs out to sea: it is cut off where the pictures cut it, a little into the coast's line.
        beyond = past_land(p)
        last = int(np.flatnonzero(beyond <= 0.0)[-1])
        stop = next((k for k in range(last + 1, len(p)) if beyond[k] >= INTO_INK), None)
        if stop is not None:
            f = (INTO_INK - beyond[stop - 1]) / max(beyond[stop] - beyond[stop - 1], 1e-9)
            p = np.concatenate([p[:stop], [p[stop - 1] + f * (p[stop] - p[stop - 1])]])
            wide = np.concatenate([wide[:stop], [wide[stop - 1] + f * (wide[stop] - wide[stop - 1])]])
            cut_short += 1
    elif river["ends_in"] == "river":
        near, off, _ = nearest_on(river_lines[river["joins"]], p[-1])
        worst_join = max(worst_join, off)
        if off > 1e-6:
            p[-1] = near
            put_on += 1
    p = tidy(p)
    if len(p) != len(wide):                      # a point fell on its neighbour when rounded
        wide = wide[:len(p)]
    p, _, placed = geo.rounded(p, False, TURN)
    p = np.round(p, 3)
    wide = np.interp(placed, np.arange(len(wide)), wide)
    assert (np.abs(np.diff(p, axis=0)) > 1e-9).any(axis=1).all()
    river_lines[river["id"]] = p
    river_widths[river["id"]] = wide
    along = walked(p)
    rivers.append({"id": river["id"], "ends_in": river["ends_in"], "joins": river["joins"], "from_lake": river["from_lake"], "px": round(float(along[-1]), 1),
                   "widest": round(float(wide.max()), 3), "narrowest": round(float(wide.min()), 3), "widths": profile(along, wide), "points": flat(p)})
out["rivers"] = rivers
gaps = np.concatenate([np.hypot(*np.diff(p, axis=0).T) for p in river_lines.values()])
print("rivers: %d, %d points (%d as they came, the rest added on bends), %.0f px; to the sea %d (cut off %.0f px past the land: %d); joining another %d (the furthest any ended from the river it joins: %.2f px; put on it: %d)" % (
    len(rivers), sum(len(p) for p in river_lines.values()), sum(len(r["points"]) for r in rivers_table), sum(r["px"] for r in rivers), sum(r["ends_in"] == "sea" for r in rivers), INTO_INK, cut_short,
    sum(r["ends_in"] == "river" for r in rivers), worst_join, put_on))
print("   widths %.2f to %.2f px; of even width %d, the rest told in %d points at most; a point every %.2f px, the longest gap %.2f" % (
    min(r["narrowest"] for r in rivers), max(r["widest"] for r in rivers), sum(not r["widths"] for r in rivers), max(len(r["widths"]) for r in rivers), gaps.mean(), gaps.max()))
river_ends = {r["id"]: r["ends_in"] for r in rivers}
river_at, river_half, river_of, river_along = sampled(river_lines, {k: 0.5 * v for k, v in river_widths.items()})
river_tree = cKDTree(river_at)


def kept_to(points, limit):
    """Which river each point of a line keeps to: (river, or 0 for none; how far off its line; which
    of the places sampled along it is nearest). A point keeps to a river if it is within
    limit(place) of it. Where two rivers are near enough at once (at the mouth of one that joins
    the other) the line stays with the river it was keeping to, changing over only when it must:
    by the nearest river alone it would change back and forth there and be cut in pieces."""
    n = len(points)
    off, index = river_tree.query(points, k=LOOK, distance_upper_bound=LOOK_REACH)
    near = [dict() for _ in range(n)]                     # river -> (how far off, which place), the nearest place of each
    for i in range(n):
        for d, j in zip(off[i], index[i]):
            if not np.isfinite(d):
                break
            river = int(river_of[j])
            if river not in near[i] and d <= limit(j):
                near[i][river] = (float(d), int(j))
    which = np.zeros(n, dtype=np.int64)
    how_far = np.full(n, np.inf)
    place = np.zeros(n, dtype=np.int64)
    for a, b in runs_of([bool(c) for c in near]):
        choice = sorted(set().union(*[set(c) for c in near[a: b + 1]]))
        if len(choice) == 1:
            path = [choice[0]] * (b - a + 1)
        else:
            # The cheapest way through: a point's cost is how far it is off the river, and changing river costs CHANGE.
            cost = np.array([[near[i][r][0] if r in near[i] else 1e6 for r in choice] for i in range(a, b + 1)])
            total = cost.copy()
            back = np.zeros(cost.shape, dtype=np.int64)
            for i in range(1, len(cost)):
                step = total[i - 1][None, :] + CHANGE * (1.0 - np.eye(len(choice)))
                back[i] = step.argmin(axis=1)
                total[i] += step.min(axis=1)
            k = int(total[-1].argmin())
            path = [0] * len(cost)
            for i in range(len(cost) - 1, -1, -1):
                path[i] = choice[k]
                k = int(back[i][k])
        for i, river in zip(range(a, b + 1), path):
            if river in near[i]:
                which[i], (how_far[i], place[i]) = river, near[i][river]
    return which, how_far, place

# == the counties, the coast and the borders ==============================================================
followed = {name: {"runs": 0, "px": 0.0, "moved": 0.0} for name in RANK_NAMES.values()}


def onto_rivers(knots, pinned, rank):
    """A border's points, put on a river's line wherever it follows one: where it keeps within
    NEAR_RIVER of the same river for FOLLOW px or more. The run begins and ends where the border
    is on the river (within ON_RIVER) if it is so near its ends; otherwise it is eased on to the
    river over EASE px. In between, its points are the river's own. A meeting point within the run
    is put on the river's line too. A line's two ends are never moved."""
    n = len(knots)
    which, off, nearest = kept_to(knots, lambda place: NEAR_RIVER)
    along = river_along[nearest]
    travelled = walked(knots)
    near = which > 0
    # An end stays where it is: the run reaches it only if it is on the river already (on_river_first).
    near[0] = near[0] and off[0] <= SAMPLE
    near[-1] = near[-1] and off[-1] <= SAMPLE
    parts, moved = [], {}
    cursor, count = 0, 0

    def carry(upto):
        """Copy the points before [upto] as they are."""
        nonlocal cursor, count
        for i in pinned:
            if cursor <= i < upto:
                moved[i] = count + i - cursor
        parts.append(knots[cursor: upto])
        count += upto - cursor
        cursor = upto

    for a, b in runs_of(near):
        first = a
        for k in range(a, b + 2):
            if k <= b and which[k] == which[first]:
                continue
            i0, i1, river = first, k - 1, int(which[first])
            first = k
            if travelled[i1] - travelled[i0] < FOLLOW:
                continue
            # The run's core, where the border's points become the river's: from c0 to c1.
            on = np.flatnonzero(off[i0: i1 + 1] <= ON_RIVER) + i0
            starts_on = len(on) > 0 and travelled[on[0]] - travelled[i0] <= EASE
            ends_on = len(on) > 0 and travelled[i1] - travelled[on[-1]] <= EASE
            c0 = int(on[0]) if starts_on else int(np.searchsorted(travelled, travelled[i0] + EASE))
            c1 = int(on[-1]) if ends_on else int(np.searchsorted(travelled, travelled[i1] - EASE, side="right")) - 1
            if starts_on:
                i0 = c0
            if ends_on:
                i1 = c1
            if c1 <= c0 or travelled[c1] - travelled[c0] < 0.5 * FOLLOW:
                continue
            s0, s1 = float(along[c0]), float(along[c1])
            if not 0.5 <= abs(s1 - s0) / (travelled[c1] - travelled[c0]) <= 2.0:
                continue                         # the river doubles back: not a border keeping to its line
            core, _ = stretch_of(river_lines[river], 0.0, min(s0, s1), max(s0, s1))
            if s0 > s1:
                core = core[::-1]
            if c0 == 0:
                core[0] = knots[0]
            if c1 == n - 1:
                core[-1] = knots[-1]
            carry(i0)
            # Easing on: each point drawn toward the river, more and more.
            ease_in = []
            for i in range(i0, c0):
                weight = (travelled[i] - travelled[i0]) / max(travelled[c0] - travelled[i0], 1e-9)
                ease_in.append(knots[i] + weight * (river_at[nearest[i]] - knots[i]))
                if i in pinned:
                    moved[i] = count + len(ease_in) - 1
            ease_out = []
            for i in range(c1 + 1, i1 + 1):
                weight = (travelled[i1] - travelled[i]) / max(travelled[i1] - travelled[c1], 1e-9)
                ease_out.append(knots[i] + weight * (river_at[nearest[i]] - knots[i]))
            # Meeting points within the core: on the river's line, as points of it.
            inside = [i for i in pinned if c0 <= i <= c1]
            if inside:
                at = walked(core)
                extra = sorted((nearest_on(core, knots[i])[2], i) for i in inside)
                merged, where = [], {}
                j = 0
                for s, i in extra:
                    while j < len(core) and at[j] < s - 1e-6:
                        merged.append(core[j])
                        j += 1
                    if j < len(core) and abs(at[j] - s) <= 1e-6:
                        where[i] = len(merged)
                        continue
                    where[i] = len(merged)
                    merged.append(nearest_on(core, knots[i])[0])
                merged.extend(core[j:])
                core = np.asarray(merged)
                for i, k2 in where.items():
                    moved[i] = count + len(ease_in) + k2
            new = [np.asarray(ease_in).reshape(-1, 2), core, np.asarray(ease_out).reshape(-1, 2)]
            base = count + len(ease_in) + len(core)
            for i in pinned:
                if c1 < i <= i1:
                    moved[i] = base + i - c1 - 1
            shift = float(np.hypot(*(river_at[nearest[c0: c1 + 1]] - knots[c0: c1 + 1]).T).max())
            tally = followed[RANK_NAMES[rank]]
            tally["runs"] += 1
            tally["px"] += travelled[i1] - travelled[i0]
            tally["moved"] = max(tally["moved"], shift)
            parts.extend(new)
            count += sum(len(part) for part in new)
            cursor = i1 + 1
    carry(n)
    points = np.concatenate(parts)
    # Points that fell together (a border's own point and the river's) are one.
    keep = np.ones(len(points), dtype=bool)
    keep[1:] = np.hypot(*np.diff(points, axis=0).T) > 1e-6
    if not keep.all():
        index = np.cumsum(keep) - 1
        moved = {i: int(index[k]) for i, k in moved.items()}
        points = points[keep]
    return points, moved


def on_river_first(chains):
    """Meeting points where two or more borders arrive along the same river: {node: the place on
    that river's line nearest it}. Put there before the borders are smoothed, they let each border
    keep to the river right up to its end; left on their pixel corners, a pixel or two off the
    river, the borders' last steps to them could cross."""
    arriving = {}
    on_coast = set()
    for i, c in enumerate(chains):
        if c.closed:
            continue
        if c.rank == COAST:
            on_coast.update(c.ends())
            continue
        arriving.setdefault(c.nodes[0], []).append(np.asarray(c.nodes[1:9], dtype=np.float64))
        arriving.setdefault(c.nodes[-1], []).append(np.asarray(c.nodes[-2:-10:-1], dtype=np.float64))
    placed = {}
    for node, ways in arriving.items():
        if node in on_coast:
            continue
        along = {}
        for steps in ways:
            if len(steps) < 4:
                continue
            off, nearest = river_tree.query(steps)
            rivers_near = river_of[nearest]
            if (off <= NEAR_RIVER).all() and (rivers_near == rivers_near[0]).all():
                along[int(rivers_near[0])] = along.get(int(rivers_near[0]), 0) + 1
        for river, count in along.items():
            if count >= 2:
                near, off, _ = nearest_on(river_lines[river], np.asarray(node, dtype=np.float64))
                if off <= NEAR_RIVER:
                    placed[node] = (float(near[0]), float(near[1]))
    return placed


cracks = geo.Cracks(county)
chains = cracks.chains
assert int((cracks.degree == 4).sum()) == 0, "four edges meet at a point: the tracing does not handle it"
for c in chains:
    a, b = c.left, c.right
    c.rank = COAST if (a == 0 or b == 0) else KINGDOM if kingdom_of[a] != kingdom_of[b] else DUCHY if duchy_of[a] != duchy_of[b] else COUNTY
lines = geo.lines_of(chains)
on_river = on_river_first(chains)
place = geo.smooth_lines(chains, lines, GIVE, 32, TURN, SPARE, onto_rivers, on_river)
print("meeting points put on a river's line before the borders were smoothed, two borders arriving along it: %d" % len(on_river))
for c in chains:
    c.points = tidy(c.points, c.closed)
coast_nodes = set()
for c in chains:
    if c.rank == COAST and not c.closed:
        coast_nodes.update(c.ends())
print("counties: %d edges between meeting points, %d meeting points (%d of them on the coast); smoothed with %.1f px of give, a point for every %.0f degrees of bend, none that moves an edge less than %.3f px  [%.0f s]" % (
    len(chains), len(place), len(coast_nodes), GIVE, TURN, SPARE, time.time() - started))
for name in ("kingdom", "duchy", "county"):
    t = followed[name]
    print("   %s borders put on a river's line: %d stretches, %.0f px in all; the furthest any point was moved: %.2f px" % (name, t["runs"], t["px"], t["moved"]))

rings = cracks.rings()
px = np.bincount(county.ravel(), minlength=221)
counties, errors, crossed = [], [], []
touching = 0                     # points an outline passes through twice
for number in range(1, 221):
    pieces = []
    for ring in rings[number]:
        p = joined([chains[i].points if f else chains[i].points[::-1] for i, f in ring], True)
        assert signed_area(p) < 0, "county %d has a hole in it" % number      # the county on the left all the way round: every ring runs the same way
        if geo.crossings(p):
            crossed.append(number)
        touching += len(p) - len(set(map(tuple, p)))
        pieces.append(p)
    pieces.sort(key=lambda p: -geo.area_of(p))
    errors.append(sum(geo.area_of(p) for p in pieces) - px[number])
    counties.append({"number": number, "duchy": duchy_of[number], "kingdom": kingdom_of[number], "px": int(px[number]),
                     "pieces": [flat(p) for p in pieces]})
errors = np.array(errors)
out["counties"] = counties
out["kingdoms"] = [{"number": k["number"], "biome": k["biome"]} for k in regions["kingdoms"]]
print("   %d counties in %d pieces, %d points; their areas against their pixels: %.1f px off on average, %.1f at most, %+.1f in all" % (
    len(counties), sum(len(c["pieces"]) for c in counties), sum(len(p) // 2 for c in counties for p in c["pieces"]), np.abs(errors).mean(), np.abs(errors).max(), errors.sum()))
of_kingdom = np.array([c["kingdom"] for c in counties])
print("   as a share of its pixels, no county is off by more than %.2f%%, and no kingdom by more than %.3f%%" % (
    100.0 * np.abs(errors / px[1:]).max(), 100.0 * max(abs(errors[of_kingdom == k].sum()) / px[1:][of_kingdom == k].sum() for k in range(1, 10))))
assert not crossed, "counties whose outline crosses itself: %s" % crossed
assert touching == 0, "counties' outlines touch themselves at %d points" % touching

coast = []
for c in chains:
    if c.rank != COAST:
        continue
    coast.append({"county": c.left or c.right, "closed": bool(c.closed), "points": flat(c.points)})
coast.sort(key=lambda e: (e["county"], -len(e["points"])))
out["coast"] = coast
print("   coast: %d stretches (%d of them rings round an island with one county on it), %d points, %.0f px long" % (
    len(coast), sum(e["closed"] for e in coast), sum(len(e["points"]) // 2 for e in coast),
    sum(length_of(c.points, c.closed) for c in chains if c.rank == COAST)))


def run_on(p, at_end):
    """A line's end carried on [INTO_INK] px the way it was going over its last 2 px."""
    q = p[::-1] if at_end else p
    tip = q[0]
    back = q[min(int(np.argmax(np.hypot(*(q - tip).T) >= 2.0)) or len(q) - 1, len(q) - 1)]
    way = tip - back
    way = way / max(np.hypot(*way), 1e-9)
    return np.round(tip + INTO_INK * way, 3)


borders = {name: [] for name in RANK_NAMES.values()}
border_lines = []                # (rank, between, points) of every border as it runs on the land
for line, ring in lines:
    rank = chains[line[0][0]].rank
    if rank == COAST:
        continue
    assert not ring
    p = joined([chains[i].points if f else chains[i].points[::-1] for i, f in line], False)
    first = chains[line[0][0]]
    a, b = first.left, first.right
    if rank == KINGDOM:
        between = sorted((kingdom_of[a], kingdom_of[b]))
    elif rank == DUCHY:
        between = sorted((duchy_of[a], duchy_of[b]))
    else:
        between = sorted((a, b))
    start = first.nodes[0 if line[0][1] else -1]
    last = chains[line[-1][0]]
    end = last.nodes[-1 if line[-1][1] else 0]
    entry = {"between": between, "from_coast": start in coast_nodes, "to_coast": end in coast_nodes, "px": round(length_of(p), 1)}
    border_lines.append((RANK_NAMES[rank], between, p))
    if entry["from_coast"]:
        p = np.concatenate([[run_on(p, False)], p])
    if entry["to_coast"]:
        p = np.concatenate([p, [run_on(p, True)]])
    entry["points"] = flat(p)
    borders[RANK_NAMES[rank]].append(entry)
for name in borders:
    borders[name].sort(key=lambda e: (e["between"], -e["px"]))
    print("   %s borders: %d lines, %d points, %.0f px (%.0f km); ends at the coast %d" % (
        name, len(borders[name]), sum(len(e["points"]) // 2 for e in borders[name]), sum(e["px"] for e in borders[name]), 0.335 * sum(e["px"] for e in borders[name]),
        sum(e["from_coast"] + e["to_coast"] for e in borders[name])))
out["borders"] = borders
kb = load_json("KingdomBorders.json")
mine = sampled({k: p for k, (name, _, p) in enumerate(border_lines) if name == "kingdom"}, {k: 0.0 for k in range(len(border_lines))})[0]
theirs = np.concatenate([np.asarray(b["points"], dtype=np.float64) + 0.5 for b in kb["borders"]])
d = cKDTree(mine).query(theirs)[0]
print("   the kingdoms' borders as designed (KingdomBorders.json) lie %.2f px from these on average, %.2f at most (they were drawn a pixel or two off the rivers they follow; these are on them)" % (d.mean(), d.max()))

# == the lakes ==============================================================================================
rgb = np.array(Image.open(SRC + "/LakeMap.png").convert("RGB")).astype(np.int32)
lake = rgb[..., 0] + 256 * rgb[..., 1]
lakes_table = {l["id"]: l for l in load_json("Lakes.json")["lakes"]}
specks = 0
for i, box in enumerate(ndimage.find_objects(lake), start=1):
    mine = lake[box] == i
    parts, n = ndimage.label(mine)
    if n > 1:
        sizes = ndimage.sum_labels(mine, parts, index=np.arange(1, n + 1))
        small = np.isin(parts, np.flatnonzero(sizes < SPECK) + 1)
        lake[box][small] = 0
        specks += int(small.sum())
water = lake > 0
body = ndimage.binary_opening(water, structure=disc(BODY))
core = ndimage.binary_opening(water, structure=disc(CORE)) & body
broad = ndimage.binary_propagation(core, structure=np.ones((3, 3), dtype=bool), mask=body)
with_body = set(int(v) for v in np.unique(lake[broad])) - {0}

lake_cracks = geo.Cracks(lake)
lake_chains = lake_cracks.chains
shared_shores = sum(1 for c in lake_chains if c.left and c.right)
for c in lake_chains:
    c.rank = 1
geo.smooth_lines(lake_chains, geo.lines_of(lake_chains), GIVE, 32, TURN, SPARE)
for c in lake_chains:
    c.points = tidy(c.points, c.closed)
lake_rings = lake_cracks.rings()
lake_px = np.bincount(lake.ravel(), minlength=701)
lakes, lake_outlines, lake_errors = [], {}, []
for i in range(1, 701):
    outlines, holes = [], []
    for ring in lake_rings[i]:
        p = joined([lake_chains[k].points if f else lake_chains[k].points[::-1] for k, f in ring], True)
        assert geo.crossings(p) == 0, "lake %d's outline crosses itself" % i
        (outlines if signed_area(p) < 0 else holes).append(p)
    outlines.sort(key=lambda p: -geo.area_of(p))
    area = sum(geo.area_of(p) for p in outlines) - sum(geo.area_of(p) for p in holes)
    lake_errors.append((area - lake_px[i]) / lake_px[i])
    lake_outlines[i] = outlines
    lakes.append({"id": i, "px": int(lake_px[i]), "broad": i in with_body, "kind": lakes_table[i]["kind"], "pieces": [flat(p) for p in outlines], "islands": [flat(p) for p in holes]})
lake_errors = np.array(lake_errors)
small = np.array([l["px"] < 50 for l in lakes])
out["lakes"] = lakes
print("lakes: %d in %d pieces, %d points; broad enough somewhere for a border to be drawn across %d; with an island %d; single pixels joined by a corner left out: %d; edges shared by two lakes: %d  [%.0f s]" % (
    len(lakes), sum(len(l["pieces"]) for l in lakes), sum(len(p) // 2 for l in lakes for p in l["pieces"]), len(with_body),
    sum(bool(l["islands"]) for l in lakes), specks, shared_shores, time.time() - started))
print("   their areas against their pixels: %+.2f%% on average, between %+.2f%% and %+.2f%%; the %d lakes under 50 px: %+.2f%% on average" % (
    100 * lake_errors.mean(), 100 * lake_errors.min(), 100 * lake_errors.max(), int(small.sum()), 100 * lake_errors[small].mean()))

# == roads and bridges ======================================================================================
roads_table = load_json("Roads.json")
kinds = {p["id"]: p["kind"] for p in roads_table["places"]}
stretch_lines = {}
roads = []
for stretch in roads_table["stretches"]:
    p = np.round(geo.rounded(tidy(np.asarray(stretch["points"], dtype=np.float64) + 0.5), False, TURN)[0], 3)
    stretch_lines[stretch["id"]] = p
    roads.append({"id": stretch["id"], "from": stretch["from"], "to": stretch["to"], "from_fork": kinds[stretch["from"]] != "settlement", "to_fork": kinds[stretch["to"]] != "settlement",
                  "highway": bool(stretch["highway"]), "px": round(length_of(p), 1), "points": flat(p)})
out["roads"] = roads
gaps = np.concatenate([np.hypot(*np.diff(p, axis=0).T) for p in stretch_lines.values()])
print("roads: %d stretches (%d highway), %d points (%d as they came), %.0f px; a point every %.2f px, the longest gap %.2f" % (
    len(roads), sum(r["highway"] for r in roads), sum(len(r["points"]) // 2 for r in roads), sum(len(s["points"]) for s in roads_table["stretches"]), sum(r["px"] for r in roads), gaps.mean(), gaps.max()))
bridges = []
off_road = 0.0
for bridge in roads_table["bridges"]:
    line = stretch_lines[bridge["stretch"]]
    ends = []
    for key in ("from", "to"):
        near, off, along = nearest_on(line, np.asarray(bridge[key], dtype=np.float64) + 0.5)
        off_road = max(off_road, off)
        ends.append(along)
    p = tidy(stretch_of(line, 0.0, min(ends), max(ends))[0])
    bridges.append({"id": bridge["id"], "stretch": bridge["stretch"], "over": bridge["over"], "river": bridge.get("river"), "highway": bool(bridge["highway"]),
                    "px": round(length_of(p), 1), "points": flat(p)})
out["bridges"] = bridges
print("bridges: %d (%d over the sea), %.1f to %.1f px long; their ends lie within %.2f px of their roads' lines" % (
    len(bridges), sum(b["over"] != "river" for b in bridges), min(b["px"] for b in bridges), max(b["px"] for b in bridges), off_road))

# == settlements ============================================================================================
settlements = []
for s in load_json("Settlements.json")["settlements"]:
    settlements.append({"county": s["county"], "duchy": s["duchy"], "kingdom": s["kingdom"], "rank": s["rank"], "at": [s["x"] + 0.5, s["y"] + 0.5]})
ends = [line[0] for line in stretch_lines.values()] + [line[-1] for line in stretch_lines.values()]
far = cKDTree(np.asarray(ends)).query(np.asarray([s["at"] for s in settlements]))[0].max()
out["settlements"] = settlements
print("settlements: %d (%s); every one has a road's end within %.2f px of its middle" % (
    len(settlements), ", ".join("%d %s" % (sum(s["rank"] == r for s in settlements), r) for r in ("kingdom", "duchy", "county")), far))

# == borders under water and beside roads ===================================================================
# No line is to hide another. Water is drawn over the borders, so a border that only crosses a river
# passes under it and that is all. But where a border runs along water (its line under the water for
# FOLLOW px or more on end) it would be lost: there its colour is put along both banks, half the
# border's width on each. A road that runs along a border is treated the same way. And where a
# border crosses a lake that is broad (BODY, CORE), it is drawn again over the water, as a line
# across the lake.
narrow_lake = water & ~broad
inside = ndimage.distance_transform_edt(narrow_lake)
half_here = ndimage.maximum_filter(inside, size=2 * REACH + 1)
road_width = {s["id"]: (3.0 if s["highway"] else 2.0) for s in roads_table["stretches"]}
road_at, road_half, road_of, road_along = sampled(stretch_lines, {k: 0.5 * v for k, v in road_width.items()})
road_tree = cKDTree(road_at)
across, banks = [], []
tally = {name: {"across": 0, "along": 0, "crossings": 0, "river": 0, "lake": 0, "road": 0, "px": 0.0} for name in MARGIN}
for rank, between, p in border_lines:
    n = len(p)
    travelled = walked(p)
    ix = np.clip(np.floor(p[:, 0]).astype(int), 0, w - 1)
    iy = np.clip(np.floor(p[:, 1]).astype(int), 0, h - 1)
    in_lake = lake[iy, ix]
    # Over the water: where the lake is broad, and any short narrow bit between there and the shore.
    over = broad[iy, ix].copy()
    for a, b in runs_of(in_lake > 0):
        if not over[a: b + 1].any():
            continue
        for c, d in runs_of(~over[a: b + 1]):
            c, d = c + a, d + a
            if travelled[d] - travelled[c] < FOLLOW:
                over[c: d + 1] = True
    for a, b in runs_of(over):
        if b > a:
            across.append({"rank": rank, "between": between, "lake": int(in_lake[a: b + 1].max()), "points": flat(p[a: b + 1])})
            tally[rank]["across"] += 1
    # Under the water: in a lake where the border is not drawn across it, or under a river's line.
    which_river, off, nearest = kept_to(p, lambda place: river_half[place] + BESIDE)
    under_river = (which_river > 0) & ~over
    under_lake = (in_lake > 0) & ~over
    under = under_river | under_lake
    wide_here = np.where(under_lake, 2.0 * half_here[iy, ix] - 1.0, np.where(under_river, 2.0 * river_half[nearest], 0.0))
    for a, b in runs_of(under):
        long = travelled[b] - travelled[a]
        if long < max(FOLLOW, FOLLOW_WIDTHS * wide_here[a: b + 1].max()):
            tally[rank]["crossings"] += 1
            continue
        tally[rank]["along"] += 1
        tally[rank]["px"] += long
        # Which water, point by point: a lake's, or else the river's.
        what = np.where(under_lake[a: b + 1], -in_lake[a: b + 1], which_river[a: b + 1])
        start = a
        for k in range(a, b + 2):
            if k <= b and what[k - a] == what[start - a]:
                continue
            first, last, key = start, k - 1, int(what[start - a])
            start = k
            if key > 0:
                s0, s1 = float(river_along[nearest[first: last + 1]].min()), float(river_along[nearest[first: last + 1]].max())
                if s1 - s0 < 1.0:
                    continue
                points, wide = stretch_of(river_lines[key], river_widths[key], s0, s1)
                points = tidy(points)
                wide = wide[:len(points)] + 2.0 * MARGIN[rank]
                # Where the river ends at the sea, so does this, and as squarely.
                at_mouth = river_ends[key] == "sea" and s1 >= walked(river_lines[key])[-1] - SAMPLE
                banks.append({"rank": rank, "between": between, "along": "river", "id": key, "px": round(length_of(points), 1), "widest": round(float(wide.max()), 3),
                              "widths": profile(walked(points), wide), "square_end": bool(at_mouth), "points": flat(points)})
                tally[rank]["river"] += 1
            else:
                mine = p[first: last + 1]
                qx, qy = ix[first: last + 1], iy[first: last + 1]
                limit = 2.0 * half_here[qy, qx] - inside[qy, qx] + 0.5 + BANK_SLACK
                tree = cKDTree(mine)
                for outline in lake_outlines[-key]:
                    away, which = tree.query(outline)
                    marked = away <= limit[which]
                    if not marked.all():
                        # Start the count where the shore is unmarked, so that no run is cut in two by the ring's seam.
                        shift = int(np.argmin(marked))
                        marked = np.roll(marked, -shift)
                        outline = np.roll(outline, -shift, axis=0)
                        # A short break in the marking (a little cove) is closed, so that the colour runs on.
                        for c, d in runs_of(~marked)[1:]:
                            if length_of(outline[c - 1: d + 2]) < BANK_GAP:
                                marked[c: d + 1] = True
                    for c, d in runs_of(marked):
                        whole = d - c + 1 == len(outline)
                        shore = outline if whole else outline[c: d + 1]
                        if length_of(shore, whole) >= 3.0:
                            banks.append({"rank": rank, "between": between, "along": "lake", "id": -key, "closed": whole, "px": round(length_of(shore, whole), 1),
                                          "widest": 2.0 * MARGIN[rank], "widths": [], "points": flat(shore)})
                            tally[rank]["lake"] += 1
    # Beside a road: where the border lies under a road's line, and not under water.
    off, nearest = road_tree.query(p)
    under_road = (off <= road_half[nearest] + BESIDE) & ~under & ~over
    for a, b in runs_of(under_road):
        if travelled[b] - travelled[a] < FOLLOW:
            continue
        key = int(np.bincount(road_of[nearest[a: b + 1]]).argmax())
        mine = road_of[nearest[a: b + 1]] == key
        s0, s1 = float(road_along[nearest[a: b + 1]][mine].min()), float(road_along[nearest[a: b + 1]][mine].max())
        if s1 - s0 < 1.0:
            continue
        points = tidy(stretch_of(stretch_lines[key], 0.0, s0, s1)[0])
        banks.append({"rank": rank, "between": between, "along": "road", "id": key, "px": round(s1 - s0, 1), "widest": road_width[key] + 2.0 * MARGIN[rank], "widths": [],
                      "points": flat(points)})
        tally[rank]["road"] += 1
out["across_lakes"] = across
out["banks"] = banks
for name in ("kingdom", "duchy", "county"):
    t = tally[name]
    print("%s borders: drawn across a lake in %d places; under water for %.0f px or more on end in %d places (%.0f px), shorter (crossings) in %d; their colour put along a river's banks %d times, a lake's shore %d, beside a road %d" % (
        name, t["across"], FOLLOW, t["along"], t["px"], t["crossings"], t["river"], t["lake"], t["road"]))

with open(WRITE_TO, "w", encoding="utf-8", newline="\n") as handle:
    json.dump(out, handle, separators=(",", ":"))
print("wrote %s  [%.0f s]" % (WRITE_TO, time.time() - started))
