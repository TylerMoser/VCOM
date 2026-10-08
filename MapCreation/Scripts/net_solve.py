"""Placing a border network's points so its regions enclose given areas.

Shared by the scripts that try different ideas of what should be kept: how little the lines
stretch (strain), how near each point stays to somewhere (an anchor), or both.
"""
import numpy as np

PENALTY = 0.05           # the least a pixel of area still owed counts for beside the cost


def slopes(function, x, step=1.0):
    base = function(x)
    out = np.zeros((base.size, x.size))
    for k in range(x.size):
        up = x.copy(); up[k] += step
        down = x.copy(); down[k] -= step
        out[:, k] = (function(up) - function(down)) / (2 * step)
    return out


def residuals(net, x, anchor, anchor_weight, strain_weight):
    """What is made small, as a list whose squares are summed: for each border the difference
    between its two ends' shifts over the root of its length, and each variable's distance from
    its anchor."""
    where, _ = net.unpack(x)
    out = []
    if strain_weight > 0:
        for key, names in net.ends.items():
            a = where[names[0]] - net.home[names[0]]
            b = where[names[1]] - net.home[names[1]]
            out.extend((np.sqrt(strain_weight / net.length[key]) * (b - a)).tolist())
    out.extend((np.sqrt(anchor_weight) * (x - anchor)).tolist())
    return np.array(out)


def solve(net, x, wanted, anchor, anchor_weight, strain_weight=1.0, furthest=40.0, rounds=80, verbose=False):
    """Newton steps on the cost and the areas together, no variable moving more than [furthest]
    in one, and each step cut back until it is worth taking: the coast turns sharp corners, where
    a full step would only overshoot and come back. [anchor_weight] may be one number or one per
    variable. Returns the variables, the rounds taken and how far the worst area still is from
    [wanted]."""
    anchor_weight = np.broadcast_to(np.asarray(anchor_weight, dtype=np.float64), x.shape)
    cost = lambda x: residuals(net, x, anchor, anchor_weight, strain_weight)
    gap = lambda x: (net.areas(x) - wanted)[:-1]            # the last area follows from the rest
    # A pixel of area owed has to count for more than it would cost to supply, or a step that
    # trades area for cost looks worth taking: the price is raised to stay ahead of that.
    price = PENALTY
    worth = lambda x: float((cost(x) ** 2).sum()) + price * float(np.abs(gap(x)).sum())
    reach = furthest
    for count in range(rounds):
        r = cost(x); J = slopes(cost, x)
        g = gap(x); A = slopes(gap, x)
        n, m = x.size, g.size
        system = np.block([[J.T @ J, A.T], [A, np.zeros((m, m))]])
        answer = np.linalg.lstsq(system, np.concatenate([-J.T @ r, -g]), rcond=None)[0]
        step = answer[:n]
        price = max(price, 4.0 * float(np.abs(answer[n:]).max()))
        biggest = float(np.abs(step).max())
        if biggest > reach:
            step = step * (reach / biggest)
        before = worth(x)
        share = 1.0
        for _ in range(8):
            if worth(x + share * step) < before:
                break
            share *= 0.5
        else:
            reach = max(reach * 0.5, 0.5)
            share = 0.0
        if verbose:
            print("    round %2d: cost %9.3f  worst gap %8.0f  step %7.2f x %.3f" % (
                count, float(r @ r), np.abs(g).max(), min(biggest, reach), share))
        x = x + share * step
        if share > 0 and biggest * share < 0.02:
            break
        if share == 0.0 and reach <= 0.5:
            break
    return x, count + 1, float(np.abs(gap(x)).max())
