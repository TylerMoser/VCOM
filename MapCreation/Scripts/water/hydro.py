"""Water running downhill over a grid of land heights: where each cell drains, how much passes
through it, and what ponds on the way.

A cell drains to its lowest neighbour. Where it has none lower (the floor of a hollow) the water
ponds until it spills over the lowest pass, and the hollow drains that way. Both come out of one
construction: the minimum spanning tree of the grid, each link between neighbours weighted by
the higher of its two cells, rooted at the sea. A cell's link to its lowest neighbour is always
in that tree, and the tree's path from any cell to the sea is the one whose highest point is as
low as can be, which is the level a hollow fills to.

Heights are in metres, one number per land cell; cells are numbered in reading order.
"""
import numpy as np
from scipy import sparse
from scipy.sparse import csgraph

OFFSET = 10.0            # added to every link's weight: the solver reads a weight of nought as no link
LOWEST_FIRST = 1e-7      # weight given to a link's lower end, so the lowest neighbour is preferred


class Grid:
    """The land cells of a mask and the links between neighbouring ones."""

    def __init__(self, land):
        self.land = land
        self.shape = land.shape
        h, w = land.shape
        self.n = int(land.sum())
        self.index = -np.ones((h, w), dtype=np.int64)
        self.index[land] = np.arange(self.n)
        self.rows, self.cols = np.nonzero(land)
        a_parts, b_parts, len_parts = [], [], []
        for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
            if dx >= 0:
                a = self.index[: h - dy, : w - dx]; b = self.index[dy:, dx:]
            else:
                a = self.index[: h - dy, -dx:]; b = self.index[dy:, : w + dx]
            both = (a >= 0) & (b >= 0)
            a_parts.append(a[both]); b_parts.append(b[both])
            len_parts.append(np.full(int(both.sum()), np.hypot(dy, dx)))
        self.link_a = np.concatenate(a_parts)
        self.link_b = np.concatenate(b_parts)
        self.link_len = np.concatenate(len_parts)          # in cells: 1 or the diagonal
        # Cells with sea (or the picture's edge) beside them drain straight to it.
        padded = np.pad(land, 1, constant_values=False)
        beside_sea = np.zeros((h, w), dtype=bool)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy or dx:
                    beside_sea |= ~padded[1 + dy: 1 + dy + h, 1 + dx: 1 + dx + w]
        self.shore = self.index[land & beside_sea]
        self.sea = self.n                      # the one node standing for all the sea

    def flat(self, field):
        return np.asarray(field)[self.land]

    def full(self, values, fill=0.0, dtype=None):
        out = np.full(self.shape, fill, dtype=dtype or np.asarray(values).dtype)
        out[self.land] = values
        return out


def route(grid, z):
    """Where every cell drains: returns the cells ordered from the sea outward (each after the
    cell it drains to) and, for each cell, the cell it drains to ([grid.sea] for the sea)."""
    a, b = grid.link_a, grid.link_b
    za, zb = z[a], z[b]
    weight = np.maximum(za, zb) + LOWEST_FIRST * np.minimum(za, zb) + OFFSET
    rows = np.concatenate([a, grid.shore])
    cols = np.concatenate([b, np.full(grid.shore.size, grid.sea, dtype=np.int64)])
    data = np.concatenate([weight, z[grid.shore] + OFFSET])
    links = sparse.coo_matrix((data, (rows, cols)), shape=(grid.n + 1, grid.n + 1)).tocsr()
    tree = csgraph.minimum_spanning_tree(links)
    order, to = csgraph.breadth_first_order(tree, grid.sea, directed=False, return_predecessors=True)
    return order[1:], to[: grid.n]


def spill_levels(grid, z, order, to):
    """The level water stands at over each cell: its own height, or the pass its hollow spills
    over if that is higher."""
    level = z.tolist() + [0.0]
    heights = z.tolist()
    to_list = to.tolist()
    for i in order.tolist():
        below = level[to_list[i]]
        if below > heights[i]:
            level[i] = below
    return np.array(level[: grid.n])


def gather(grid, order, to, gain, pond=None, keep=None):
    """What flows out of each cell: what it gathers itself ([gain], which may be a loss) plus all
    that drains into it. Flow never goes negative on its way down, except between cells of the
    same pond ([pond], an id per cell, nought for none), so a pond that loses more to the sun
    than it takes in passes nothing on. [keep], if given, is the share of its flow each cell
    passes on (rivers dwindling across a desert)."""
    flow = np.asarray(gain, dtype=np.float64).tolist() + [0.0]
    to_list = to.tolist()
    pond_list = pond.tolist() + [0] if pond is not None else None
    keep_list = keep.tolist() if keep is not None else None
    for i in reversed(order.tolist()):
        value = flow[i]
        if keep_list is not None and value > 0:
            value *= keep_list[i]
            flow[i] = value
        j = to_list[i]
        if pond_list is not None and pond_list[i] and pond_list[i] == pond_list[j]:
            flow[j] += value
        elif value > 0:
            flow[j] += value
    return np.array(flow[: grid.n])


def step_lengths(grid, to):
    """Distance, in cells, from each cell to the cell it drains to."""
    w = grid.shape[1]
    target = np.where(to == grid.sea, np.arange(grid.n), to)
    dy = grid.rows[target] - grid.rows
    dx = grid.cols[target] - grid.cols
    return np.maximum(np.hypot(dy, dx), 1.0)


def outlets(grid, order, to, closed=None):
    """For each cell, the cell where its water leaves the land: the shore cell it drains through,
    or, for water that ends in a pond with no outflow, that pond's lowest-order cell. [closed] marks
    the cells at which the water stops."""
    out = np.arange(grid.n).tolist()
    to_list = to.tolist()
    closed_list = closed.tolist() if closed is not None else None
    for i in order.tolist():
        j = to_list[i]
        if j == grid.sea or (closed_list is not None and closed_list[i]):
            continue
        out[i] = out[j]
    return np.array(out)


def settle(grid, wanted, order, to, drop=0.02):
    """[wanted] heights raised wherever they would leave a cell no higher than the cell it drains
    to: every cell ends at least [drop] metres above the next one down, so nothing ponds."""
    out = np.asarray(wanted, dtype=np.float64).tolist() + [-drop]
    to_list = to.tolist()
    for i in order.tolist():
        least = out[to_list[i]] + drop
        if out[i] < least:
            out[i] = least
    return np.array(out[: grid.n])


def incise(grid, surface, order, to, pull):
    """One round of rivers cutting down: each cell is drawn toward the height of the cell it
    drains to, by the share [pull] / (1 + pull) of the difference, working up from the sea so
    that a cut below is felt above in the same round. [pull] grows with the water passing, so
    big rivers flatten their beds quickly and trickles hardly move theirs. [surface] must have
    no hollows (use the spill levels)."""
    out = np.asarray(surface, dtype=np.float64).tolist() + [0.0]
    to_list = to.tolist()
    pull_list = np.asarray(pull, dtype=np.float64).tolist()
    for i in order.tolist():
        f = pull_list[i]
        out[i] = (out[i] + f * out[to_list[i]]) / (1.0 + f)
    return np.array(out[: grid.n])


def climb(grid, steepness, cell, sinks=()):
    """Heights and drainage together, from how steep the ground is meant to be.

    [steepness] is the rise wanted per unit of distance at each cell (metres per km, with [cell]
    the size of a cell in km). Each cell is given the least total climb of any way to it from the
    sea, and drains back along that way. Heights made so rise everywhere away from the sea with
    no hollows, steeply where the ground was meant steep; ways up share the easy ground, so they
    gather into rivers as they come down; and ridges fall where climbs from two shores meet.

    [sinks] are (cell, height) pairs: hollows the water may also end in, each at its own height,
    for land that drains to no sea. Returns the heights, the cell each drains to ([grid.sea] for
    the sea or its own sink), the cells in order of height, and a mark on each cell at which
    water stops in a sink."""
    a, b = grid.link_a, grid.link_b
    weight = 0.5 * (steepness[a] + steepness[b]) * grid.link_len * cell
    n = grid.n
    start = n + 1                                      # one node that everything is reached from
    rows = [a, grid.shore, np.array([grid.sea])]
    cols = [b, np.full(grid.shore.size, grid.sea, dtype=np.int64), np.array([start])]
    data = [weight, 0.5 * steepness[grid.shore] * cell, np.array([1e-9])]
    for sink, height in sinks:
        rows.append(np.array([sink])); cols.append(np.array([start])); data.append(np.array([float(height)]))
    links = sparse.coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(n + 2, n + 2)).tocsr()
    height, came_from = csgraph.dijkstra(links, directed=False, indices=start, return_predecessors=True)
    to = came_from[:n].astype(np.int64)
    closed = to == start
    to[closed] = grid.sea
    order = np.argsort(height[:n], kind="stable")
    return height[:n], to, order, closed


def upstream(grid, to):
    """For looking up the cells that drain straight into a cell: returns (starts, cells) such
    that cells[starts[i]:starts[i + 1]] drain into cell i."""
    inland = np.flatnonzero(to != grid.sea)
    by_target = inland[np.argsort(to[inland], kind="stable")]
    starts = np.searchsorted(to[by_target], np.arange(grid.n + 1))
    return starts, by_target
