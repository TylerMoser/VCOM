"""Lines that run together, drawn so that neither hides the other.

A border, a river and a road are each a line with a width. Where one crosses another the upper
one passes over and that is all. Where a river or a road runs *along* a border, the border is
not left under it: it is drawn along both sides of it, half its width on each, so the river or
road shows down the middle with the border's colour on either hand.

Water is of two kinds for this. Broad water is the body of a lake: wherever the lake is at
least 9 px across and part of open water at least 17 px across. It is drawn under the borders,
so a border across a lake is a line across the lake with water showing on both sides of it. All
other water is narrow and is drawn over the borders: every river, the thin arms of lakes, and
lakes too small for a line to cross without hiding them.
"""
import numpy as np
from scipy import ndimage
from skimage.morphology import skeletonize

SEA, WHITE = (181, 235, 255), (255, 255, 255)
PINK, PURPLE, GREY = (233, 0, 255), (110, 30, 180), (128, 128, 128)
BLUE, RED, UMBER = (28, 112, 224), (200, 40, 30), (60, 35, 15)
# A rank's name, colour, and how far its colour reaches from the edge of a line it runs along:
# half its own width. Painted in this order, the greater over the lesser.
RANKS = (("county", GREY, 1.0), ("duchy", PURPLE, 1.5), ("kingdom", PINK, 2.5))
FOLLOW = 12              # px of a border's middle under a line before the line is said to run along it...
FOLLOW_WIDTHS = 1.5      # ...or this many times the line's width, if that is more (a border crossing a lake's arm)
BODY = 4.0               # radius, px: broad water is at least 9 px across...
CORE = 8.0               # ...and joined to open water a disc of this radius fits in (17 px across)
WIDEST_WATER = 17        # px: narrow water is nowhere as wide as this
WIDEST_ROAD = 5          # px: a highway's bridge
CLEAR = 2.0              # px of white kept round every dot
EIGHT = np.ones((3, 3), dtype=bool)


def is_colour(picture, colour):
    return (picture[..., 0] == colour[0]) & (picture[..., 1] == colour[1]) & (picture[..., 2] == colour[2])


def disc(radius):
    r = int(np.floor(radius))
    y, x = np.ogrid[-r: r + 1, -r: r + 1]
    return x * x + y * y <= radius * radius


def broad_water(lake):
    """The bodies of the lakes: where a disc of radius BODY fits, joined to where one of radius CORE fits."""
    body = ndimage.binary_opening(lake, structure=disc(BODY))
    core = ndimage.binary_opening(lake, structure=disc(CORE)) & body
    return ndimage.binary_propagation(core, structure=EIGHT, mask=body)


def middle_of(lines):
    """A line's middle, one pixel wide."""
    return skeletonize(lines)


class Cover:
    """A set of lines that lie over the borders (the roads, or the narrow water), with what is
    needed to find the stretch of them a border runs under."""

    def __init__(self, mask, widest):
        self.mask = mask
        self.reach = int(np.ceil(widest / 2.0)) + 1
        self.inside = ndimage.distance_transform_edt(mask)                       # how far in from the line's edge
        self.half = ndimage.maximum_filter(self.inside, size=2 * self.reach + 1)  # half the line's width hereabouts

    def runs_along(self, middle):
        """The parts of a border's middle that lie under the cover far enough on end for the cover
        to be running along the border and not across it: (mask, how many)."""
        under = middle & self.mask
        labels, n = ndimage.label(under, structure=EIGHT)
        if n == 0:
            return under, 0
        index = np.arange(1, n + 1)
        sizes = ndimage.sum_labels(under, labels, index=index)
        widths = 2.0 * ndimage.maximum(self.half, labels, index=index) - 1.0
        along = sizes >= np.maximum(FOLLOW, FOLLOW_WIDTHS * widths)
        return np.concatenate([[False], along])[labels], int(along.sum())

    def stretch(self, run):
        """The cover from side to side wherever [run], a border's middle, lies under it."""
        if not run.any():
            return run
        near, (iy, ix) = ndimage.distance_transform_edt(~run, return_indices=True)
        grown = ndimage.binary_dilation(run, structure=EIGHT, iterations=2 * self.reach, mask=self.mask)
        # From the run to the far edge of the line is the line's width less how far in the run lies.
        return grown & (near <= 2.0 * self.half - self.inside[iy, ix] + 0.5)

    def both_sides(self, run, margin):
        """Pixels off the cover within [margin] of the stretch [run] lies under."""
        stretch = self.stretch(run)
        if not stretch.any():
            return stretch
        return (ndimage.distance_transform_edt(~stretch) <= margin) & ~self.mask


def border_lines(picture, dots, near_land):
    """Each rank's border lines in a picture that has borders and dots: {name: mask}."""
    return {name: is_colour(picture, colour) & ~dots & near_land for name, colour, _ in RANKS}


def clear_of(dots):
    return ndimage.distance_transform_edt(~dots) > CLEAR


def deepest_hidden(middle, shown):
    """How far the furthest hidden pixel of a border's middle is from any pixel of its colour that
    shows: (px, (x, y)). 0 if none is hidden."""
    hidden = middle & ~shown
    if not hidden.any():
        return 0.0, None
    away = ndimage.distance_transform_edt(~shown)
    worst = np.where(hidden, away, 0.0)
    y, x = np.unravel_index(int(np.argmax(worst)), worst.shape)
    return float(worst[y, x]), (int(x), int(y))


def longest_hidden(middle, shown):
    """The longest run of a border's middle of which nothing shows: (px, (x, y))."""
    hidden = middle & ~shown
    labels, n = ndimage.label(hidden, structure=EIGHT)
    if n == 0:
        return 0, None
    sizes = ndimage.sum_labels(hidden, labels, index=np.arange(1, n + 1))
    i = int(np.argmax(sizes))
    y, x = ndimage.center_of_mass(labels == i + 1)
    return int(sizes[i]), (int(x), int(y))
