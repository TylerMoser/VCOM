"""The drawn regions as a network of border curves, so the curves themselves can be moved.

Read from a label map (0 off the mainland, 1-9 the regions): each border between two regions as
an ordered line of points, the points where three borders meet (junctions), the points where a
border meets the coast, the coast itself as one closed line, and each region as the ring of
borders and stretches of coast that encloses it. Borders that run on through a junction without
turning are chained into strokes, as the lines were drawn.

Coordinates are (row, column) in pixels throughout, pixel centres on whole numbers.
"""
import numpy as np
from scipy import ndimage
from scipy.interpolate import PchipInterpolator
from skimage import measure

SMOOTH = 6.0            # points: smoothing of each traced border along its length
SPACING = 3.0           # pixels between the points kept on a border
COAST_SMOOTH = 3.0      # points: smoothing of the traced coast


def outline(mask):
    """The longest closed outline of [mask], traced between its pixels and the rest."""
    rows = np.flatnonzero(mask.any(axis=1)); cols = np.flatnonzero(mask.any(axis=0))
    r0, r1, c0, c1 = max(rows[0] - 2, 0), rows[-1] + 3, max(cols[0] - 2, 0), cols[-1] + 3
    contours = measure.find_contours(mask[r0:r1, c0:c1].astype(np.float32), 0.5)
    longest = max(contours, key=len)
    if np.allclose(longest[0], longest[-1]):
        longest = longest[:-1]
    return longest + np.array([r0, c0], dtype=np.float64)


def across(points, labels, own):
    """For each outline point of region [own], the label on the far side of the outline there."""
    r, c = points[:, 0], points[:, 1]
    a = labels[np.floor(r).astype(int), np.floor(c).astype(int)]
    b = labels[np.ceil(r).astype(int), np.ceil(c).astype(int)]
    return np.where(a == own, b, a).astype(np.int64)


def runs_of(other):
    """Runs of equal values round a ring: (value, first index, length)."""
    n = len(other)
    starts = np.flatnonzero(other != np.roll(other, 1))
    if len(starts) == 0:
        return [(int(other[0]), 0, n)]
    found = []
    for k, a in enumerate(starts):
        b = starts[(k + 1) % len(starts)]
        found.append((int(other[a]), int(a), int((b - a) % n) or n))
    return found


def cleaned(other, shortest=4):
    """[other] with runs under [shortest] points taken into the run before them."""
    other = other.copy()
    for _ in range(20):
        runs = runs_of(other)
        short = [run for run in runs if run[2] < shortest]
        if not short or len(runs) == 1:
            break
        n = len(other)
        for value, a, length in short:
            other[(a + np.arange(length)) % n] = other[(a - 1) % n]
    return other


def smoothed(points, sigma):
    """An open line smoothed along its length, its two ends left exactly where they were."""
    if len(points) < 5:
        return points.copy()
    soft = ndimage.gaussian_filter1d(points, sigma, axis=0, mode="nearest")
    t = np.linspace(0.0, 1.0, len(points))[:, None]
    return soft + (1 - t) * (points[0] - soft[0]) + t * (points[-1] - soft[-1])


def resampled(points, spacing):
    lengths = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(points, axis=0).T))])
    count = max(int(round(lengths[-1] / spacing)), 2)
    at = np.linspace(0.0, lengths[-1], count + 1)
    return np.column_stack([np.interp(at, lengths, points[:, 0]), np.interp(at, lengths, points[:, 1])])


def length_of(points):
    return float(np.hypot(*np.diff(points, axis=0).T).sum())


def area_of(points):
    """Area enclosed by a ring of points (always positive)."""
    r, c = points[:, 0], points[:, 1]
    return 0.5 * abs(float(np.dot(r, np.roll(c, -1)) - np.dot(c, np.roll(r, -1))))


class Network:
    def __init__(self, labels, mainland):
        self.labels = labels
        self.regions = [int(v) for v in np.unique(labels) if v > 0]
        # The coast, one closed line with distance along it.
        coast = outline(mainland)
        coast = ndimage.gaussian_filter1d(coast, COAST_SMOOTH, axis=0, mode="wrap")
        self.coast = coast
        steps = np.hypot(*(np.roll(coast, -1, axis=0) - coast).T)
        self.coast_at = np.concatenate([[0.0], np.cumsum(steps)])        # one longer: closes the ring
        self.coast_length = float(self.coast_at[-1])
        self.coast_ring = np.vstack([coast, coast[:1]])

        rings = {}
        for i in self.regions:
            ring = outline(labels == i)
            other = cleaned(across(ring, labels, i))
            rings[i] = (ring, runs_of(other))

        # Borders, each traced once, from the lower-numbered region's outline.
        self.borders = {}            # (i, j) -> points, first to last as region i's outline runs
        ends = {}                    # (i, j) -> [start name, end name]
        for i in self.regions:
            ring, runs = rings[i]
            for k, (j, a, length) in enumerate(runs):
                if j <= i:
                    continue
                before = runs[(k - 1) % len(runs)][0]
                after = runs[(k + 1) % len(runs)][0]
                points = ring[(a + np.arange(length)) % len(ring)]
                if (i, j) in self.borders:
                    raise ValueError("regions %d and %d share more than one border" % (i, j))
                self.borders[(i, j)] = points
                ends[(i, j)] = [
                    ("coast", i, j, 0) if before == 0 else ("junction",) + tuple(sorted((i, j, before))),
                    ("coast", i, j, 1) if after == 0 else ("junction",) + tuple(sorted((i, j, after))),
                ]
        self.ends = ends

        # Where each junction and coast point is: junctions at the mean of the three ends that meet.
        gathered = {}
        for key, points in self.borders.items():
            for which, name in enumerate(ends[key]):
                gathered.setdefault(name, []).append(points[0] if which == 0 else points[-1])
        self.home = {}               # name -> position as drawn
        self.coast_home = {}         # coast name -> distance along the coast as drawn
        for name, places in gathered.items():
            if name[0] == "junction":
                if len(places) != 3:
                    raise ValueError("junction %s has %d borders" % (name, len(places)))
                self.home[name] = np.mean(places, axis=0)
            else:
                nearest = int(np.argmin(((coast - places[0]) ** 2).sum(axis=1)))
                self.coast_home[name] = float(self.coast_at[nearest])
                self.home[name] = coast[nearest].copy()
        for key in self.borders:
            points = np.vstack([self.home[ends[key][0]], self.borders[key][2:-2], self.home[ends[key][1]]])
            self.borders[key] = resampled(smoothed(points, SMOOTH), SPACING)
        self.length = {key: length_of(points) for key, points in self.borders.items()}

        # Each region's ring: borders (and which way round) and stretches of coast between them.
        self.rings = {}
        for i in self.regions:
            ring, runs = rings[i]
            pieces = []
            for j, a, length in runs:
                if j == 0:
                    pieces.append(("coast",))
                else:
                    key = (min(i, j), max(i, j))
                    pieces.append(("border", key, i > j))
            self.rings[i] = pieces

        self._find_strokes()

    def _leaving(self, key, which):
        """Unit direction a border sets off in from one of its ends."""
        points = self.borders[key]
        reach = min(14, len(points) - 1)
        step = points[reach] - points[0] if which == 0 else points[-1 - reach] - points[-1]
        return step / np.hypot(*step)

    def _find_strokes(self):
        at = {}
        for key, names in self.ends.items():
            for which, name in enumerate(names):
                if name[0] == "junction":
                    at.setdefault(name, []).append((key, which))
        # At each junction the two borders most nearly in line carry on into each other.
        onward = {}
        for name, meeting in at.items():
            best = None
            for a in range(3):
                for b in range(a + 1, 3):
                    dot = float(np.dot(self._leaving(*meeting[a]), self._leaving(*meeting[b])))
                    if best is None or dot < best[0]:
                        best = (dot, meeting[a], meeting[b])
            onward[(best[1], name)] = best[2]
            onward[(best[2], name)] = best[1]
        self.through = {name: None for name in at}
        used = set()
        self.strokes = []            # each a list of (border, reversed)
        def grow(key, which_end):
            """Borders onward from [key] leaving by its end [which_end] (0 start, 1 end)."""
            chain = []
            while True:
                name = self.ends[key][which_end]
                step = onward.get(((key, which_end), name))
                if step is None:
                    return chain
                key, entered = step
                if key in used:
                    return chain
                used.add(key)
                chain.append((key, entered == 1))          # entered by its end: runs backwards
                which_end = 1 - entered
        for key in sorted(self.borders):
            if key in used:
                continue
            used.add(key)
            forward = grow(key, 1)
            backward = grow(key, 0)
            stroke = [(k, not rev) for k, rev in reversed(backward)] + [(key, False)] + forward
            self.strokes.append(stroke)

    # -- moving it --------------------------------------------------------------------------

    def names(self):
        junctions = sorted(n for n in self.home if n[0] == "junction")
        coasts = sorted(n for n in self.home if n[0] == "coast")
        return junctions, coasts

    def unpack(self, x):
        """Positions of every junction and coast point for the variables [x]."""
        junctions, coasts = self.names()
        where = {}
        for k, name in enumerate(junctions):
            where[name] = np.array(x[2 * k: 2 * k + 2], dtype=np.float64)
        along = {}
        for k, name in enumerate(coasts):
            along[name] = float(x[2 * len(junctions) + k]) % self.coast_length
            where[name] = self.on_coast(along[name])
        return where, along

    def home_x(self):
        junctions, coasts = self.names()
        return np.concatenate([np.concatenate([self.home[n] for n in junctions]),
                               np.array([self.coast_home[n] for n in coasts])])

    def on_coast(self, along):
        along = along % self.coast_length
        return np.array([np.interp(along, self.coast_at, self.coast_ring[:, 0]),
                         np.interp(along, self.coast_at, self.coast_ring[:, 1])])

    def coast_between(self, a, b):
        """The coast from distance [a] on to distance [b], the way the coast is numbered."""
        a %= self.coast_length; b %= self.coast_length
        first = int(np.searchsorted(self.coast_at, a, side="right"))
        last = int(np.searchsorted(self.coast_at, b, side="left"))
        n = len(self.coast)
        if b >= a:
            inner = self.coast[first:last]
        else:
            inner = np.vstack([self.coast[first:n], self.coast[0:last]])
        return np.vstack([self.on_coast(a), inner, self.on_coast(b)])

    def moved_borders(self, where):
        """Every border with its ends at [where], the rest of each stroke carried smoothly."""
        moved = {}
        for stroke in self.strokes:
            lines, marks, shifts, offset = [], [0.0], [], 0.0
            first_key, first_rev = stroke[0]
            name = self.ends[first_key][1 if first_rev else 0]
            shifts.append(where[name] - self.home[name])
            for key, rev in stroke:
                points = self.borders[key][::-1] if rev else self.borders[key]
                steps = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(points, axis=0).T))])
                lines.append((key, rev, points, offset + steps))
                offset += steps[-1]
                marks.append(offset)
                name = self.ends[key][0 if rev else 1]
                shifts.append(where[name] - self.home[name])
            carry = PchipInterpolator(np.array(marks), np.array(shifts), axis=0)
            for key, rev, points, at in lines:
                new = points + carry(at)
                moved[key] = new[::-1] if rev else new
        return moved

    def polygons(self, x):
        where, along = self.unpack(x)
        moved = self.moved_borders(where)
        rings = {}
        for i in self.regions:
            pieces = self.rings[i]
            parts = []
            for k, piece in enumerate(pieces):
                if piece[0] == "border":
                    _, key, rev = piece
                    parts.append(moved[key][::-1] if rev else moved[key])
                else:
                    _, key_a, rev_a = pieces[(k - 1) % len(pieces)]
                    _, key_b, rev_b = pieces[(k + 1) % len(pieces)]
                    start = self.ends[key_a][0 if rev_a else 1]
                    stop = self.ends[key_b][1 if rev_b else 0]
                    parts.append(self.coast_between(along[start], along[stop])[1:-1])
            rings[i] = np.vstack(parts)
        return rings, moved

    def areas(self, x):
        rings, _ = self.polygons(x)
        return np.array([area_of(rings[i]) for i in self.regions])

    def strain(self, x):
        """How much the borders are stretched or turned: for each, the squared difference between
        the shifts of its two ends over its length. Nought when everything shifts together."""
        where, _ = self.unpack(x)
        total = 0.0
        for key, names in self.ends.items():
            a = where[names[0]] - self.home[names[0]]
            b = where[names[1]] - self.home[names[1]]
            total += float(((b - a) ** 2).sum()) / self.length[key]
        return total
