import pickle, sys, time
import numpy as np
sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from kingdom_net import Network
from net_solve import solve
OUT = sys.argv[1]
with open(OUT + "/network.pickle", "rb") as handle:
    net = pickle.load(handle)
x0 = net.home_x()
drawn = net.areas(x0)
total = drawn.sum()
wanted = drawn + 0.1 * (total / 9.0 - drawn)
t = time.time()
x, rounds, miss = solve(net, x0.copy(), wanted, x0, 2e-5, 1.0, rounds=25, verbose=True)
print("rounds", rounds, "miss", miss, "%.1fs" % (time.time() - t))
