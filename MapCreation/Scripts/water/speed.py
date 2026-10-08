"""How long the drainage of a grid takes at each size, on a made-up bumpy surface."""
import sys, time
import numpy as np
from scipy import ndimage
sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
import hydro
out = sys.argv[1]
for factor in (4, 2):
    g = np.load(out + "/grid%d.npz" % factor)
    t = time.time(); grid = hydro.Grid(g["land"]); t_grid = time.time() - t
    rng = np.random.default_rng(1)
    d = ndimage.distance_transform_edt(g["land"])
    z = d * 5 + ndimage.gaussian_filter(rng.standard_normal(g["land"].shape), 6) * 400
    z = grid.flat(z - z.min() + 1.0) + rng.random(grid.n) * 1e-3
    t = time.time(); order, to = hydro.route(grid, z); t_route = time.time() - t
    t = time.time(); level = hydro.spill_levels(grid, z, order, to); t_level = time.time() - t
    t = time.time(); flow = hydro.gather(grid, order, to, np.ones(grid.n)); t_flow = time.time() - t
    lower = (z[np.where(to == grid.sea, 0, to)] < z) | (to == grid.sea)
    print("1/%d: %d cells; grid %.1fs, route %.1fs, levels %.1fs, gather %.1fs; ponded cells %.1f%%; biggest gathering %.0f; drains downhill %.1f%%" % (
        factor, grid.n, t_grid, t_route, t_level, t_flow, 100 * (level > z + 1e-9).mean(), flow.max(), 100 * lower.mean()))
