"""One kingdom, or one duchy, as country to be shared out among seats.

Each seat claims the land that is cheapest to reach from it. Reaching costs the distance, more
in the empty country away from water, more for every metre climbed or dropped, and a lump for
each river, lake shore or watershed line crossed, so the line where two seats' claims meet
settles on those where it can: a border on a river stays on it until one seat's claim is pushed
further than the river costs to cross. Each seat also has a head start, in kilometres, which is
what is adjusted to make the shares come out the same size.
"""
import numpy as np
from scipy import ndimage, sparse
from scipy.sparse import csgraph

from tidy import tidy

CLIMB = 0.008            # km of going for each metre climbed or dropped
LAKE_CROSS = 15.0        # km to put out on a lake and land again
DIVIDE_CROSS = 22.0      # km more to cross a line between whole watersheds
RIDGE_CROSS = 10.0       # km to cross the ridge between one river's country and the next's
MOST_SEATS = 8


class Realm:
    def __init__(self, mask, fields, km, islands=None, ease=1.0, to_sides=False):
        """[mask]: the realm's mainland cells. [fields]: the grids d1_fields.py made, at the
        same size. [km]: a cell's size. [islands]: offshore cells that go with whatever mainland
        is nearest them. [ease]: what every crossing costs, as a share of the full price.
        [to_sides]: count each cell of water, and of the lines of ridge, with the share the
        nearest plain cell is in, so a border on a river or a ridge runs down its middle as it
        will be drawn; left to themselves, a seat that has paid to step on to a ridge claims it
        for as far as it runs."""
        self.mask, self.km = mask, km
        h, w = mask.shape
        self.n = n = int(mask.sum())
        self.index = -np.ones((h, w), dtype=np.int64)
        self.index[mask] = np.arange(n)
        self.rows, self.cols = np.nonzero(mask)
        z = fields["height"][mask].astype(np.float64)
        going = fields["going"][mask].astype(np.float64)
        river, lake, divide = fields["river"][mask], fields["lake"][mask], fields["divide"][mask]
        ridge = fields["ridge"][mask] | divide
        self.feature = river | lake | ridge
        self.wet = river | lake
        cross = fields["cross"][mask].astype(np.float64)
        self.seat_worth = fields["seat"][mask].astype(np.float64)
        a_parts, b_parts, cost_parts = [], [], []
        for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
            if dx >= 0:
                a = self.index[: h - dy, : w - dx]; b = self.index[dy:, dx:]
            else:
                a = self.index[: h - dy, -dx:]; b = self.index[dy:, : w + dx]
            both = (a >= 0) & (b >= 0)
            a, b = a[both], b[both]
            cost = np.hypot(dy, dx) * km * 0.5 * (going[a] + going[b]) + CLIMB * np.abs(z[a] - z[b])
            lump = 0.5 * np.where(river[a] != river[b], np.maximum(cross[a], cross[b]), 0.0)
            lump += 0.5 * LAKE_CROSS * (lake[a] != lake[b]) + 0.5 * DIVIDE_CROSS * (divide[a] != divide[b])
            lump += 0.5 * RIDGE_CROSS * (ridge[a] != ridge[b])
            cost += ease * lump
            a_parts.append(a); b_parts.append(b); cost_parts.append(cost)
        a, b, cost = np.concatenate(a_parts), np.concatenate(b_parts), np.concatenate(cost_parts)
        order = np.argsort(a, kind="stable")
        a, b, cost = a[order], b[order], cost[order]
        # After the cells come MOST_SEATS more nodes, one a seat, each joined to its seat's cell by
        # one link whose length is the head start it lacks: those are changed in place per try.
        pointer = np.concatenate([[0], np.cumsum(np.bincount(a, minlength=n)), len(a) + np.arange(1, MOST_SEATS + 1)])
        self.graph = sparse.csr_matrix((np.concatenate([cost, np.full(MOST_SEATS, 1e12)]),
                                        np.concatenate([b, np.zeros(MOST_SEATS, dtype=b.dtype)]), pointer),
                                       shape=(n + MOST_SEATS, n + MOST_SEATS))
        self.mean_going = float(going.mean())
        if islands is not None and islands.any():
            _, (iy, ix) = ndimage.distance_transform_edt(~mask, return_indices=True)
            ys, xs = np.nonzero(islands)
            self.island_cell = self.index[iy[ys, xs], ix[ys, xs]]
            self.island_at = (ys, xs)
        else:
            self.island_cell = np.zeros(0, dtype=np.int64)
            self.island_at = (np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64))
        self.side = None
        lines = self.wet | ridge
        if to_sides and lines.any() and not lines.all():
            plain = mask.copy()
            plain[mask] = ~lines
            _, (iy, ix) = ndimage.distance_transform_edt(~plain, return_indices=True)
            self.side = self.index[iy[mask], ix[mask]]

    def cell_at(self, y, x):
        return int(self.index[int(y), int(x)])

    def claim(self, seats, head_starts):
        """Which seat each cell goes to (0, 1, 2 ...), given each seat's cell and head start."""
        count = len(seats)
        lack = float(np.max(head_starts)) + 1.0 - np.asarray(head_starts, dtype=np.float64)
        self.graph.indices[-MOST_SEATS:] = 0
        self.graph.data[-MOST_SEATS:] = 1e12
        self.graph.indices[len(self.graph.indices) - MOST_SEATS: len(self.graph.indices) - MOST_SEATS + count] = seats
        self.graph.data[len(self.graph.data) - MOST_SEATS: len(self.graph.data) - MOST_SEATS + count] = lack
        reach, _, source = csgraph.dijkstra(self.graph, directed=False, indices=np.arange(self.n, self.n + count),
                                            return_predecessors=True, min_only=True)
        owner = source[: self.n] - self.n
        # How far each cell is from its seat by the going, the head start taken off again.
        self.far = np.where(owner >= 0, reach[: self.n] - lack[np.maximum(owner, 0)], 0.0)
        if (owner < 0).any():                            # a scrap cut off from every seat goes to the nearest claim
            grid = self.on_grid(owner)
            _, (iy, ix) = ndimage.distance_transform_edt(grid < 0, return_indices=True)
            owner = grid[iy, ix][self.mask]
        if self.side is not None:
            owner = owner[self.side]
        return owner

    def claim_tidied(self, seats, head_starts):
        """The same, tidied as it will be drawn (tidy.py)."""
        owner = self.claim(seats, head_starts)
        return tidy(self.on_grid(owner), self.mask, len(seats))[self.mask].astype(np.int64)

    def on_grid(self, owner, fill=-1):
        grid = np.full(self.mask.shape, fill, dtype=np.int64)
        grid[self.mask] = owner
        return grid

    def sizes(self, owner, count):
        """Cells in each share, the islands counted with the share they lie off."""
        size = np.bincount(owner, minlength=count).astype(np.float64)
        if self.island_cell.size:
            size += np.bincount(owner[self.island_cell], minlength=count)
        return size

    def shared(self, owner, count):
        """Length, in cells, of the border between each pair of shares."""
        grid = self.on_grid(owner)
        h, w = grid.shape
        length = np.zeros((count, count))
        for dy, dx in ((0, 1), (1, 0)):
            a = grid[: h - dy, : w - dx]; b = grid[dy:, dx:]
            meet = (a != b) & (a >= 0) & (b >= 0)
            tally = np.bincount(a[meet] * count + b[meet], minlength=count * count).reshape(count, count)
            length += tally + tally.T
        return length

    def even_out(self, seats, head_starts=None, near_enough=0.03, tries=60, step=25.0, most=70.0, tidied=False):
        """Head starts that make the shares about the same size: within [near_enough] of each
        other's mean, no closer, so borders are left on the rivers and ridges that hold them.
        Returns the head starts, the shares and how far the worst is from the mean. [tidied]:
        the shares are measured, and given back, as they will be drawn."""
        count = len(seats)
        start = np.zeros(count) if head_starts is None else np.array(head_starts, dtype=np.float64)
        claim = self.claim_tidied if tidied else self.claim
        best = None
        for _ in range(tries):
            owner = claim(seats, start)
            size = self.sizes(owner, count)
            wanted = size.sum() / count
            off = float(np.abs(size - wanted).max() / wanted)
            if best is None or off < best[2]:
                best = (start.copy(), owner, off)
            if off < near_enough:
                break
            # A head start of one km moves a border about half a km of going; share it out as the
            # borders' lengths say (the same sum as for the kingdoms' weights).
            length = self.shared(owner, count)
            spread = np.diag(length.sum(axis=1)) - length
            push = 2.0 * np.linalg.pinv(spread) @ (wanted - size)
            push = np.clip(push * self.km * self.mean_going * max(0.2, 0.92 ** _), -step, step)
            start = start + push
            start -= start.mean()
            start = np.clip(start, -most, most)          # no seat is given so little that another swallows it
        return best

    def middle_of(self, owner, which):
        mine = owner == which
        return float(self.rows[mine].mean()), float(self.cols[mine].mean())

    def best_seat(self, owner, which, reach_km=32.0, pull_km=22.0):
        """The best place for a seat in share [which]: a good site, not far from the share's
        middle."""
        mine = np.flatnonzero(owner == which)
        my, mx = self.rows[mine].mean(), self.cols[mine].mean()
        away = np.hypot(self.rows[mine] - my, self.cols[mine] - mx) * self.km
        worth = self.seat_worth[mine] - away / pull_km - 50.0 * (away > max(reach_km, away.min() + 6.0))
        return int(mine[int(np.argmax(worth))])

    def nearest_dry(self, y, x):
        """The dry cell nearest a spot: where a seat goes that was set down on water or outside."""
        dry = np.flatnonzero(self.seat_worth > -50.0)
        if dry.size == 0:
            dry = np.arange(self.n)
        return int(dry[np.argmin(np.hypot(self.rows[dry] - y, self.cols[dry] - x))])

    def edges(self, owner):
        """Cells on the border between two shares."""
        grid = self.on_grid(owner)
        h, w = grid.shape
        edge = np.zeros((h, w), dtype=bool)
        for dy, dx in ((0, 1), (1, 0)):
            a = grid[: h - dy, : w - dx]; b = grid[dy:, dx:]
            edge[: h - dy, : w - dx] |= (a != b) & (a >= 0) & (b >= 0)
        return edge

    def on_features(self, owner):
        """The share of the borders between shares that lies on a river, a lake or a ridge."""
        edge = self.edges(owner)
        if not edge.any():
            return 0.0
        near = ndimage.binary_dilation(self.on_grid(self.feature.astype(np.int64), 0) > 0, iterations=2)
        return float((edge & near).sum()) / float(edge.sum())

    def sprawl(self, owner, count):
        """How spread out each share is: its cells' mean distance from its middle, over what
        that would be were it a disc. 1 for a disc, about 1.6 for a strip four times as long
        as wide."""
        size = np.maximum(np.bincount(owner, minlength=count).astype(np.float64), 1.0)
        my = np.bincount(owner, weights=self.rows, minlength=count) / size
        mx = np.bincount(owner, weights=self.cols, minlength=count) / size
        away = np.hypot(self.rows - my[owner], self.cols - mx[owner])
        return (np.bincount(owner, weights=away, minlength=count) / size) / ((2.0 / 3.0) * np.sqrt(size / np.pi))
