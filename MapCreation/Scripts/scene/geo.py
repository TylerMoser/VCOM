"""Shapes out of a map of numbers.

A map of numbers (CountyMap.png, LakeMap.png) gives every pixel the number of the thing it belongs
to. The edges between unlike pixels are the outlines of those things, but as staircases. This module
takes them apart into chains (an edge from one meeting point to the next, with one number on its left
and one on its right all the way), joins the chains that carry on through a meeting point into lines,
and smooths each line, so that two things that share an edge get the very same points for it.

Coordinates are the picture's, measured from its top left corner: pixel (x, y) is the square from
(x, y) to (x + 1, y + 1), and its middle is (x + 0.5, y + 0.5). x runs right and y runs down.
"""
import numpy as np

EAST, SOUTH, WEST, NORTH = 0, 1, 2, 3
MOVED = 0.75        # px: a meeting point further than this from its pixel corner has been moved
STEP = ((1, 0), (0, 1), (-1, 0), (0, -1))
LEFT_FIRST = (3, 0, 1)          # a left turn, straight on, a right turn: added to the way we are going


class Chain:
    """An edge between two numbers, from one meeting point to the next, or a closed ring that
    meets nothing. [nodes] are the corners of pixels it runs through, in order (a ring's first is
    not repeated at its end); [left] and [right] the numbers on either hand, going that way."""

    def __init__(self, nodes, left, right, closed):
        self.nodes = nodes
        self.left = left
        self.right = right
        self.closed = closed
        self.rank = 0
        self.points = None       # smoothed: from its first node's place to its last's (a ring: once round)

    def ends(self):
        return (self.nodes[0], self.nodes[-1])


class Cracks:
    """Every edge between unlike pixels of a map of numbers, as chains."""

    def __init__(self, labels):
        self.h, self.w = labels.shape
        self.L = np.pad(labels.astype(np.int64), 1)
        L = self.L
        h, w = self.h, self.w
        # An edge going east from corner (cx, cy) lies between pixel (cx, cy - 1) above and (cx, cy) below.
        self.east = L[0: h + 1, 1: w + 2] != L[1: h + 2, 1: w + 2]            # [cy, cx] for cx in 0..w (the last column never)
        # An edge going south from corner (cx, cy) lies between pixel (cx - 1, cy) and (cx, cy).
        self.south = L[1: h + 2, 0: w + 1] != L[1: h + 2, 1: w + 2]           # [cy, cx] for cy in 0..h (the last row never)
        self.east[:, w] = False
        self.south[h, :] = False
        degree = self.east.astype(np.int8) + self.south.astype(np.int8)
        degree[:, 1:] += self.east[:, :-1]
        degree[1:, :] += self.south[:-1, :]
        self.degree = degree
        self.chains = []
        self._trace()

    def has(self, cx, cy, way):
        if way == EAST:
            return bool(self.east[cy, cx])
        if way == SOUTH:
            return bool(self.south[cy, cx])
        if way == WEST:
            return cx > 0 and bool(self.east[cy, cx - 1])
        return cy > 0 and bool(self.south[cy - 1, cx])

    def sides(self, cx, cy, way):
        """The numbers on the left and on the right of the edge leaving corner (cx, cy) that way."""
        L = self.L
        if way == EAST:
            return int(L[cy, cx + 1]), int(L[cy + 1, cx + 1])
        if way == WEST:
            return int(L[cy + 1, cx]), int(L[cy, cx])
        if way == SOUTH:
            return int(L[cy + 1, cx + 1]), int(L[cy + 1, cx])
        return int(L[cy, cx]), int(L[cy, cx + 1])

    def _trace(self):
        used_east = np.zeros_like(self.east)
        used_south = np.zeros_like(self.south)

        def use(cx, cy, way):
            if way == EAST:
                used_east[cy, cx] = True
            elif way == SOUTH:
                used_south[cy, cx] = True
            elif way == WEST:
                used_east[cy, cx - 1] = True
            else:
                used_south[cy - 1, cx] = True

        def used(cx, cy, way):
            if way == EAST:
                return used_east[cy, cx]
            if way == SOUTH:
                return used_south[cy, cx]
            if way == WEST:
                return used_east[cy, cx - 1]
            return used_south[cy - 1, cx]

        def walk(cx, cy, way):
            left, right = self.sides(cx, cy, way)
            nodes = [(cx, cy)]
            start = (cx, cy)
            while True:
                use(cx, cy, way)
                cx, cy = cx + STEP[way][0], cy + STEP[way][1]
                if (cx, cy) == start:
                    return Chain(nodes, left, right, True)
                nodes.append((cx, cy))
                if self.degree[cy, cx] != 2:
                    return Chain(nodes, left, right, False)
                for turn in LEFT_FIRST:
                    onward = (way + turn) % 4
                    if self.has(cx, cy, onward):
                        way = onward
                        break

        meets = np.argwhere(self.degree > 2)
        for cy, cx in meets:
            for way in range(4):
                if self.has(cx, cy, way) and not used(cx, cy, way):
                    self.chains.append(walk(int(cx), int(cy), way))
        # What is left meets nothing: rings.
        for mask, way in ((self.east, EAST), (self.south, SOUTH)):
            rest = np.argwhere(mask & ~(used_east if way == EAST else used_south))
            for cy, cx in rest:
                if not used(cx, cy, way):
                    self.chains.append(walk(int(cx), int(cy), way))

    # -- rings round one number --------------------------------------------------------------------
    def rings(self):
        """Every closed outline, as a list of (chain index, forward) with the same number on the
        left all the way round: {number: [ring, ...]}. Pixels that touch only at a corner are not
        joined."""
        leaving = {}
        for i, chain in enumerate(self.chains):
            if chain.closed:
                continue
            a, b = chain.nodes[0], chain.nodes[1]
            leaving[(a, self._way(a, b))] = (i, True)
            a, b = chain.nodes[-1], chain.nodes[-2]
            leaving[(a, self._way(a, b))] = (i, False)
        out = {}
        done = set()
        for i, chain in enumerate(self.chains):
            for forward in (True, False):
                if (i, forward) in done:
                    continue
                number = chain.left if forward else chain.right
                ring = []
                at = (i, forward)
                while at not in done:
                    done.add(at)
                    ring.append(at)
                    c = self.chains[at[0]]
                    if c.closed:
                        break
                    nodes = c.nodes if at[1] else c.nodes[::-1]
                    here, came = nodes[-1], self._way(nodes[-2], nodes[-1])
                    for turn in LEFT_FIRST:
                        onward = (came + turn) % 4
                        if self.has(here[0], here[1], onward) and self.sides(here[0], here[1], onward)[0] == number:
                            at = leaving[(here, onward)]
                            break
                    else:
                        raise AssertionError("an outline that does not close at %s" % (here,))
                out.setdefault(number, []).append(ring)
        return out

    @staticmethod
    def _way(a, b):
        return STEP.index((b[0] - a[0], b[1] - a[1]))


# -- lines: chains that carry on through a meeting point ----------------------------------------------
def lines_of(chains):
    """Joins chains into lines. At a meeting point, the two chains of the highest rank there, if
    there are just two of it, are one line running through; every other chain ends there. Returns
    lines as lists of (chain index, forward), highest rank first, and for each whether it is a ring."""
    at_node = {}
    for i, chain in enumerate(chains):
        if chain.closed:
            continue
        at_node.setdefault(chain.nodes[0], []).append((i, True))       # leaves this node going forward
        at_node.setdefault(chain.nodes[-1], []).append((i, False))     # leaves this node going backward
    through = {}                                                       # (chain, leaves forward) -> the other (chain, leaves forward)
    for node, ends in at_node.items():
        top = max(chains[i].rank for i, _ in ends)
        of_top = [e for e in ends if chains[e[0]].rank == top]
        if len(of_top) == 2 and of_top[0][0] != of_top[1][0]:
            through[(node, of_top[0])] = of_top[1]
            through[(node, of_top[1])] = of_top[0]
    lines = []
    seen = set()
    order = sorted(range(len(chains)), key=lambda i: -chains[i].rank)
    for i in order:
        if i in seen:
            continue
        chain = chains[i]
        if chain.closed:
            seen.add(i)
            lines.append(([(i, True)], True))
            continue
        # Walk back from this chain's start to where the line begins, then forward to its end.
        def onward(index, forward):
            """The chain that carries the line on past the far end of (index, forward), or None."""
            c = chains[index]
            node = c.nodes[-1] if forward else c.nodes[0]
            arriving = (index, not forward)                # as an end at that node, it leaves the node the other way
            nxt = through.get((node, arriving))
            return nxt
        first = (i, True)
        ring = False
        while True:
            back = onward(first[0], not first[1])
            if back is None:
                break
            first = (back[0], not back[1])
            if first[0] == i:
                ring = True
                break
        line = [first]
        seen.add(first[0])
        while True:
            nxt = onward(line[-1][0], line[-1][1])
            if nxt is None or nxt[0] == line[0][0]:
                break
            line.append(nxt)
            seen.add(nxt[0])
        lines.append((line, ring))
    return lines


# -- smoothing ------------------------------------------------------------------------------------------
_HATS = {}


def _hat(k, degree=3):
    """For 2k + 1 points evenly spaced: the matrix that gives, from their values, the values at the
    same places of the curve of that degree that fits them best."""
    if (k, degree) not in _HATS:
        j = np.arange(-k, k + 1, dtype=np.float64) / max(k, 1)
        v = np.vander(j, min(degree + 1, 2 * k + 1), increasing=True)
        _HATS[(k, degree)] = v @ np.linalg.pinv(v)
    return _HATS[(k, degree)]


def smoothed(samples, closed, tolerance=0.5, widest=32, degree=3):
    """A staircase's points, smoothed as far as the staircase allows.

    [samples] are points along an edge between pixels, about a pixel apart. The true line might be
    any that keeps within half a pixel of them: a staircase of long treads may be a straight line
    seen through the pixels, a tight one a real bend. So each point is put on the cubic fitted to
    as long a stretch of its neighbours, the same number either side, as can be fitted without the
    curve leaving any of them by more than [tolerance]. Long straights come out straight, bends
    keep their shape and small rings their size. An open line's two ends stay where they are.

    The stretch a point is fitted over is never more than one point longer, either side, than its
    neighbours' stretches: two neighbours fitted over very different stretches would be put on
    curves that differ, and the line would have a kink between them."""
    samples = np.asarray(samples, dtype=np.float64)
    n = len(samples)
    if n < 3:
        return samples.copy()
    if closed:
        most = min(widest, (n - 1) // 2)
        padded = np.concatenate([samples[-most:], samples, samples[:most]]) if most > 0 else samples
    else:
        most = min(widest, n - 1)
        head = 2.0 * samples[0] - samples[most:0:-1]
        tail = 2.0 * samples[-1] - samples[-2:-most - 2:-1]
        padded = np.concatenate([head, samples, tail])
    fits = [samples]                                   # fits[k][i]: point i as fitted over k points either side, where that fits
    reach = np.zeros(n, dtype=np.int64)                # the longest stretch that fits, for each point
    alive = np.arange(n)
    for k in range(1, most + 1):
        if len(alive) == 0:
            break
        index = alive[:, None] + most + np.arange(-k, k + 1)[None, :]
        window = padded[index]                                    # (alive, 2k + 1, 2)
        fitted = np.einsum("ij,njc->nic", _hat(k, degree), window)
        off = np.hypot(fitted[..., 0] - window[..., 0], fitted[..., 1] - window[..., 1])
        # A sample may lie along the curve from where its turn falls: measure to the curve's two
        # stretches beside it as well.
        d = fitted[:, 1:] - fitted[:, :-1]
        length2 = np.maximum((d * d).sum(axis=-1), 1e-12)
        for s, target in ((window[:, 1:], slice(1, None)), (window[:, :-1], slice(0, -1))):
            t = np.clip(((s - fitted[:, :-1]) * d).sum(axis=-1) / length2, 0.0, 1.0)
            near = fitted[:, :-1] + d * t[..., None]
            off[:, target] = np.minimum(off[:, target], np.hypot(near[..., 0] - s[..., 0], near[..., 1] - s[..., 1]))
        ok = off.max(axis=1) <= tolerance
        alive = alive[ok]
        at_k = np.full((n, 2), np.nan)
        at_k[alive] = fitted[ok, k]
        fits.append(at_k)
        reach[alive] = k
    # No stretch more than one longer than its neighbours'. (An open line's ends are held anyway,
    # and are left out of this: the line is mirrored through them, so stretches may be long beside them.)
    lo, hi = (0, n) if closed else (1, n - 1)
    for _ in range(2 if closed else 1):
        for i in range(lo + (0 if closed else 1), hi):
            reach[i] = min(reach[i], reach[i - 1] + 1)
        for i in range(hi - 2, lo - 1, -1):
            reach[i] = min(reach[i], reach[(i + 1) % n] + 1)
    out = samples.copy()
    for k in range(1, len(fits)):
        mine = np.flatnonzero(reach == k)
        out[mine] = fits[k][mine]
    if not closed:
        out[0], out[-1] = samples[0], samples[-1]
    assert not np.isnan(out).any()
    return out


def rounded(points, closed, most_turn=6.0, most_cuts=24):
    """A line with points enough that it nowhere turns by more than [most_turn] degrees at one of
    them. Every point given is kept; between two of them, where the line bends, points are added
    along the smooth curve through them all (a cubic from each point to the next, leaving each
    point the way the points either side of it lie). Returns the points, where each of the given
    points now is in them, and for each point how far along the given points it lies (3.25 is a
    quarter of the way from the fourth to the fifth)."""
    p = np.asarray(points, dtype=np.float64)
    n = len(p)
    if n < 3:
        return p.copy(), np.arange(n), np.arange(n, dtype=np.float64)
    nxt = np.roll(p, -1, axis=0) if closed else p[1:]
    seg = (nxt - p) if closed else (p[1:] - p[:-1])            # from each point to the next
    step = np.maximum(np.hypot(seg[:, 0], seg[:, 1]), 1e-9)
    slope = seg / step[:, None]
    if closed:
        before, after = np.roll(slope, 1, axis=0), slope
        h0, h1 = np.roll(step, 1), step
        lean = (before * h1[:, None] + after * h0[:, None]) / (h0 + h1)[:, None]
    else:
        lean = np.empty_like(p)
        lean[1:-1] = (slope[:-1] * step[1:, None] + slope[1:] * step[:-1, None]) / (step[:-1] + step[1:])[:, None]
        lean[0] = 2.0 * slope[0] - lean[1]
        lean[-1] = 2.0 * slope[-1] - lean[-2]
    lean_to = np.roll(lean, -1, axis=0) if closed else lean[1:]
    lean_from = lean if closed else lean[:-1]
    start_at = p if closed else p[:-1]
    # How far the curve swings between one point and the next: from its lean at the first to the
    # stretch between them, and from that to its lean at the second.
    def angle(a, b):
        cross = a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
        dot = (a * b).sum(axis=1)
        return np.abs(np.degrees(np.arctan2(cross, dot)))
    swing = angle(lean_from, slope) + angle(slope, lean_to)
    cuts = np.clip(np.ceil(swing / most_turn).astype(int), 1, most_cuts)
    total = int(cuts.sum()) + (0 if closed else 1)
    out = np.empty((total, 2), dtype=np.float64)
    along = np.empty(total, dtype=np.float64)
    where = np.empty(n, dtype=np.int64)
    at = 0
    for i in range(len(cuts)):
        where[i] = at
        k = int(cuts[i])
        out[at] = start_at[i]
        along[at] = i
        if k > 1:
            u = np.arange(1, k, dtype=np.float64)[:, None] / k
            h = step[i]
            out[at + 1: at + k] = ((2 * u ** 3 - 3 * u ** 2 + 1) * start_at[i] + (u ** 3 - 2 * u ** 2 + u) * h * lean_from[i]
                                   + (-2 * u ** 3 + 3 * u ** 2) * nxt[i] + (u ** 3 - u ** 2) * h * lean_to[i])
            along[at + 1: at + k] = i + u[:, 0]
        at += k
    if not closed:
        where[n - 1] = at
        out[at] = p[-1]
        along[at] = n - 1
    return out, where, along


def thinned(points, tolerance, closed=False):
    """A line without the points it does not need: none left out lies further than [tolerance]
    from the line through the points kept either side of it. An open line keeps its ends."""
    p = np.asarray(points, dtype=np.float64)
    n = len(p)
    if tolerance <= 0.0 or n < 3:
        return p
    if closed:
        # Hold the ring at its first point and at the point furthest from it.
        far = int(np.argmax(np.hypot(*(p - p[0]).T)))
        if far == 0:
            return p
        first = thinned(p[: far + 1], tolerance)
        second = thinned(np.concatenate([p[far:], p[:1]]), tolerance)
        return np.concatenate([first[:-1], second[:-1]])
    keep = np.zeros(n, dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        d = p[b] - p[a]
        length = float(np.hypot(d[0], d[1]))
        inner = p[a + 1: b]
        if length < 1e-12:
            off = np.hypot(inner[:, 0] - p[a, 0], inner[:, 1] - p[a, 1])
        else:
            off = np.abs(d[0] * (inner[:, 1] - p[a, 1]) - d[1] * (inner[:, 0] - p[a, 0])) / length
        worst = int(np.argmax(off))
        if off[worst] > tolerance:
            k = a + 1 + worst
            keep[k] = True
            stack.append((a, k))
            stack.append((k, b))
    return p[keep]


def smooth_lines(chains, lines, tolerance=0.5, widest=32, most_turn=6.0, spare=0.0, adjust=None, placed=None):
    """Smooths every line (highest rank first, as lines_of gives them) and gives each chain its
    points. A meeting point is put where the line running through it passes; lines that end there
    end at that place. A meeting point nothing runs through stays on its pixel corner. A ring that
    meets nothing (a lake's shore, a small island's) is smoothed with a curve of one degree more,
    which follows a tight bend better, and is then put back to the size its pixels had, since
    smoothing a small ring draws it in.

    The smoothed line has a point for every edge between two pixels. Points are then added where it
    bends, so that it turns no more than [most_turn] degrees at any one (see rounded), and taken
    out where it runs so straight that they move it by less than [spare] (see thinned). Both are
    done to a line as a whole, so it runs as smoothly through a meeting point as anywhere, and a
    chain keeps one set of points whichever of the things either side of it asks.

    [adjust], if given, is asked about every open line once it is smoothed and before points are
    added: adjust(points, pinned, rank) returns the points changed as it sees fit, and for each of
    the [pinned] ones (the line's two ends, which must stay put, and the meeting points along it,
    which may be moved along with the line) where it now is among them. [placed], if given, puts
    meeting points that no line runs through somewhere other than their pixel corner. Returns {node: place}."""
    place = dict(placed or {})
    for line, ring in lines:
        mids, cuts = [], []
        for index, forward in line:
            chain = chains[index]
            nodes = np.asarray(chain.nodes if forward else chain.nodes[::-1], dtype=np.float64)
            if chain.closed:
                mids.append(0.5 * (nodes + np.roll(nodes, -1, axis=0)))
            else:
                mids.append(0.5 * (nodes[:-1] + nodes[1:]))
            cuts.append(len(mids[-1]))
        mids = np.concatenate(mids)
        lone = ring and len(line) == 1 and chains[line[0][0]].closed
        if lone:
            smooth = smoothed(mids, True, tolerance, widest, 4)
            true = area_of(np.asarray(chains[line[0][0]].nodes, dtype=np.float64))
            middle = smooth.mean(axis=0)
            smooth = middle + (smooth - middle) * np.sqrt(true / area_of(smooth))
            fine, _, _ = rounded(smooth, True, most_turn)
            fine = thinned(fine, spare, True)
            # Rounding the bends lets the ring out a little: put its size back once more.
            middle = fine.mean(axis=0)
            fine = middle + (fine - middle) * np.sqrt(true / area_of(fine))
            chain = chains[line[0][0]]
            chain.points = fine if line[0][1] else fine[::-1]
            continue
        if ring:
            smooth = smoothed(mids, True, tolerance, widest)
        else:
            first_chain, first_forward = line[0]
            last_chain, last_forward = line[-1]
            a = chains[first_chain].nodes[0 if first_forward else -1]
            b = chains[last_chain].nodes[-1 if last_forward else 0]
            pa = place.setdefault(a, (float(a[0]), float(a[1])))
            pb = place.setdefault(b, (float(b[0]), float(b[1])))
            # An end that has been moved off its pixel corner (on to a line it meets) has left the
            # staircase's last steps behind it: they are dropped, or the line would run on past
            # where it now ends and come back.
            for end, corner, where in ((0, a, pa), (-1, b, pb)):
                gone = float(np.hypot(where[0] - corner[0], where[1] - corner[1]))
                if gone <= MOVED:
                    continue
                away = np.hypot(mids[:, 0] - corner[0], mids[:, 1] - corner[1])
                drop = 0
                while drop < cuts[end] - 1 and away[drop if end == 0 else -1 - drop] <= gone + 0.25:
                    drop += 1
                if drop:
                    mids = mids[drop:] if end == 0 else mids[:-drop]
                    cuts[end] -= drop
            smooth = smoothed(np.concatenate([[pa], mids, [pb]]), False, tolerance, widest)[1:-1]
        # Where the line runs through a meeting point: half way between the points either side.
        total = len(smooth)
        bounds = []
        at = 0
        for count in cuts:
            bounds.append((at, at + count))
            at += count
        knots, marks, node_at = [], [], {}                     # the line's points in order; where each chain starts and ends in them; the meeting point at each such place
        for k, (index, forward) in enumerate(line):
            chain = chains[index]
            lo, hi = bounds[k]
            first_node = chain.nodes[0 if forward else -1]
            last_node = chain.nodes[-1 if forward else 0]
            if k > 0 or ring:
                place[first_node] = tuple(0.5 * (smooth[lo] + smooth[(lo - 1) % total]))
            if k < len(line) - 1 or ring:
                place[last_node] = tuple(0.5 * (smooth[hi - 1] + smooth[hi % total]))
            if k == 0:
                knots.append(np.asarray([place[first_node]]))
            begin = sum(len(part) for part in knots) - 1
            node_at[begin] = first_node
            knots.append(smooth[lo:hi])
            if k < len(line) - 1 or not ring:
                knots.append(np.asarray([place[last_node]]))
                marks.append((begin, sum(len(part) for part in knots) - 1))
                node_at[marks[-1][1]] = last_node
            else:
                marks.append((begin, -1))                      # a ring's last chain ends where its first began
        knots = np.concatenate(knots)
        if adjust is not None and not ring:
            knots, moved = adjust(knots, sorted(node_at), chains[line[0][0]].rank)
            marks = [(moved[a], moved[b]) for a, b in marks]
            for old, node in node_at.items():
                place[node] = (float(knots[moved[old]][0]), float(knots[moved[old]][1]))
        fine, where, _ = rounded(knots, ring, most_turn)
        for k, (index, forward) in enumerate(line):
            a, b = marks[k]
            points = fine[where[a]: where[b] + 1] if b >= 0 else np.concatenate([fine[where[a]:], fine[:1]])
            points = thinned(points, spare)
            chains[index].points = points if forward else points[::-1]
    return place


def ring_points(chains, ring):
    """The points of a closed outline made of chains (chain index, forward), once round."""
    parts = []
    for index, forward in ring:
        chain = chains[index]
        points = chain.points if forward else chain.points[::-1]
        parts.append(points if chain.closed else points[:-1])
    return np.concatenate(parts)


def area_of(points):
    """The area a ring of points encloses (positive whichever way it runs)."""
    p = np.asarray(points, dtype=np.float64)
    x, y = p[:, 0], p[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def crossings(points, closed=True):
    """How many pairs of a line's stretches cross each other (neighbours aside)."""
    p = np.asarray(points, dtype=np.float64)
    a = p if closed else p[:-1]
    b = np.roll(p, -1, axis=0) if closed else p[1:]
    n = len(a)
    if n < 4:
        return 0
    count = 0
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    order = np.argsort(lo[:, 0])
    lo_s, hi_s = lo[order], hi[order]
    for ii in range(n):
        i = order[ii]
        # candidates start before this one ends, in x
        stop = np.searchsorted(lo_s[:, 0], hi_s[ii, 0], side="right")
        cand = order[ii + 1: stop]
        if len(cand) == 0:
            continue
        cand = cand[(lo[cand, 1] <= hi[i, 1]) & (hi[cand, 1] >= lo[i, 1])]
        for j in cand:
            gap = abs(int(i) - int(j))
            if gap <= 1 or (closed and gap == n - 1):
                continue
            if _cross(a[i], b[i], a[j], b[j]):
                count += 1
    return count


def _cross(p, q, r, s):
    def side(u, v, t):
        return (v[0] - u[0]) * (t[1] - u[1]) - (v[1] - u[1]) * (t[0] - u[0])
    d1, d2 = side(r, s, p), side(r, s, q)
    d3, d4 = side(p, q, r), side(p, q, s)
    return (d1 * d2 < 0) and (d3 * d4 < 0)
