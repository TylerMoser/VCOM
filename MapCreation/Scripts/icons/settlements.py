"""The proposals for the four kinds of settlement: for each kind a list of (what it is, how it is drawn).

A proposal that names the pack is built from the pack's own icons (their black taken as it is,
moved and resized); the others are drawn afresh in the pack's manner.
"""
import kit
import parts as P


def pk(ic, name, x=0.0, scale=1.0, flip=False, y=0.0, join=None):
    """The black of one of the pack's icons, as an ink layer."""
    L = join if join is not None else ic.layer()
    L["given"].append(kit.pack_black(name, x, y, scale, flip))
    return L


def smoke(ic, x, y, join):
    for i, (dx, dy, r) in enumerate(((0, 0, 7), (9, 17, 9), (2, 38, 11))):
        join["add"].append(kit.oval(x + dx, y + dy, r, r * 0.9))


# == hamlets: a dwelling or two ================================================================================
def h01(ic): pk(ic, "Village", 0, 0.7)
def h02(ic): P.house(ic, 0, 104, 48, 58)
def h03(ic): P.house_side(ic, 0, 140, 44, 42, windows=1)
def h04(ic): P.hut(ic, 0, 84, 30, 70)
def h05(ic):
    P.hut(ic, 44, 64, 24, 54, y=14)
    P.hut(ic, -22, 84, 30, 68)
def h06(ic):
    P.house(ic, -22, 100, 46, 56, chimney=-1)
    P.haystack(ic, 62, 54, 44)
def h07(ic):
    ic.piece("Trees 1", 62, 0, 0.5)
    P.house(ic, -24, 100, 46, 56, chimney=-1)
def h08(ic): P.barn(ic, 0, 124, 42, 60)
def h09(ic): P.tent(ic, 0, 104, 82)
def h10(ic): P.longhouse(ic, 0, 180, 30, 48)
def h11(ic):
    P.house(ic, -34, 98, 46, 56, chimney=-1)
    P.well(ic, 58)
def h12(ic):
    P.house(ic, -8, 100, 46, 56)
    P.fence(ic, 38, 104, 32)
def h13(ic): P.windmill(ic, 0, 100, 54)
def h14(ic):
    P.house(ic, 40, 74, 36, 44, y=8, chimney=0)
    P.house(ic, -28, 92, 44, 52, chimney=-1)
def h15(ic):
    P.hut(ic, -10, 82, 30, 66)
    P.fence(ic, 30, 96, 30)
def h16(ic):
    P.barn(ic, 46, 96, 36, 48, y=6)
    P.house(ic, -40, 86, 42, 50, chimney=-1)
def h17(ic):
    pk(ic, "Village", 46, 0.5, True, 10)
    pk(ic, "Village", -26, 0.66)
def h18(ic):
    P.hut(ic, 0, 54, 20, 46, y=30)
    P.hut(ic, -44, 60, 22, 50)
    P.hut(ic, 44, 60, 22, 50)
def h19(ic):
    L = P.house(ic, 0, 104, 48, 58)
    smoke(ic, 34, 112, L)
def h20(ic):
    P.tent(ic, 44, 78, 62, y=8)
    P.tent(ic, -30, 96, 78)
def h21(ic):
    ic.piece("Trees 2", -64, 0, 0.5)
    pk(ic, "Village", 20, 0.66)
def h22(ic):
    P.house_side(ic, 0, 128, 40, 40, chimney=-1, windows=1)
    P.haystack(ic, 96, 46, 36)
    P.haystack(ic, -94, 40, 30)


# == villages: a handful of houses ============================================================================
def v01(ic): pk(ic, "Village", 0, 1.0)
def v02(ic):
    pk(ic, "Village", 66, 0.72, True, 12)
    pk(ic, "Village", -46, 0.92)
def v03(ic):
    pk(ic, "Village", 0, 0.66, False, 62)
    pk(ic, "Village", -76, 0.78)
    pk(ic, "Village", 76, 0.78, True)
def v04(ic):
    P.house(ic, 0, 96, 46, 56, y=44, chimney=0, door=False)
    P.house(ic, -78, 100, 46, 56, chimney=-1)
    P.house(ic, 80, 92, 44, 52)
def v05(ic):
    P.church(ic, 30, 110, 44, 40, 1, 40, 96, 62, y=22)
    P.house(ic, -86, 94, 44, 54, chimney=-1)
    P.house(ic, 96, 84, 40, 48)
def v06(ic):
    P.house(ic, -92, 96, 46, 56, chimney=-1)
    P.house(ic, 92, 96, 46, 56)
    P.well(ic, 0)
def v07(ic):
    P.barn(ic, 96, 112, 40, 56, y=8)
    P.house_side(ic, -40, 150, 44, 42, chimney=-1, windows=1, y=18)
    P.house(ic, -110, 84, 40, 48, chimney=0)
    P.house(ic, 20, 84, 40, 48)
def v08(ic):
    P.house_side(ic, -118, 110, 42, 40, chimney=0, windows=0)
    P.house_side(ic, 0, 116, 48, 46, chimney=1, windows=1)
    P.house_side(ic, 118, 110, 42, 40, chimney=0, windows=0)
def v09(ic):
    P.hut(ic, -38, 70, 26, 58, y=36)
    P.hut(ic, 44, 70, 26, 58, y=36)
    P.hut(ic, -88, 78, 28, 62)
    P.hut(ic, 0, 78, 28, 62)
    P.hut(ic, 88, 78, 28, 62)
def v10(ic):
    P.windmill(ic, 84, 108, 54, y=14)
    P.house(ic, -84, 96, 46, 56, chimney=-1)
    P.house(ic, 0, 88, 42, 50)
def v11(ic):
    P.longhouse(ic, 0, 190, 32, 50, y=26)
    P.hut(ic, -96, 70, 26, 56)
    P.hut(ic, 96, 70, 26, 56)
def v12(ic):
    P.church(ic, -30, 128, 48, 44, -1, 42, 104, 66)
    P.house(ic, 92, 92, 44, 52)
def v13(ic):
    pk(ic, "Tower", -70, 0.56)
    pk(ic, "Village", 18, 0.84, True)
    pk(ic, "Village", 110, 0.6, False)
def v14(ic):
    P.house(ic, -70, 98, 46, 56, chimney=-1, y=14)
    P.house(ic, 34, 90, 42, 52, y=14)
    P.haystack(ic, 116, 52, 42)
    P.fence(ic, -130, 70, 30)
def v15(ic):
    P.house(ic, -52, 86, 40, 50, y=56, chimney=0, door=False)
    P.house(ic, 52, 86, 40, 50, y=56, chimney=0, door=False)
    P.house(ic, -104, 92, 44, 52, chimney=-1)
    P.house(ic, 0, 92, 44, 52, chimney=0)
    P.house(ic, 104, 92, 44, 52)
def v16(ic):
    P.house(ic, -96, 98, 46, 56, chimney=-1)
    P.house(ic, 96, 98, 46, 56)
    ic.piece("Trees 2", 0, 0, 0.5)
def v17(ic):
    P.hall(ic, 0, 132, 54, 48, y=20)
    P.house(ic, -108, 84, 40, 48, chimney=-1)
    P.house(ic, 108, 84, 40, 48)
def v18(ic):
    P.windmill(ic, -104, 96, 50, y=18)
    P.barn(ic, 104, 104, 38, 52, y=10)
    P.house(ic, -30, 92, 44, 54, chimney=-1)
    P.house(ic, 44, 80, 38, 46, chimney=0)
def v19(ic):
    P.church(ic, 0, 104, 42, 38, 1, 38, 94, 60, y=34)
    pk(ic, "Village", -84, 0.72)
    pk(ic, "Village", 88, 0.66, True)
def v20(ic):
    P.house(ic, -58, 92, 44, 54, chimney=-1, y=24)
    P.house(ic, 52, 92, 44, 54, y=24)
    P.fence(ic, -128, 128, 34)
def v21(ic):
    L = P.house(ic, 0, 96, 46, 58, y=30, chimney=0)
    P.pennant(ic, 0, 30 + 46 + 58 - 4, 40, 30, 20, join=L)
    P.house(ic, -84, 92, 44, 52, chimney=-1)
    P.house(ic, 84, 92, 44, 52)
def v22(ic):
    P.house_side(ic, 0, 150, 46, 44, windows=2, y=40, chimney=0)
    P.house(ic, -96, 90, 44, 52, chimney=-1)
    P.house(ic, 0, 80, 38, 46, chimney=0)
    P.house(ic, 96, 90, 44, 52)


# == towns: houses about a tower, a church or a gate ==========================================================
def t01(ic): pk(ic, "Town", 0, 1.0)
def t02(ic):
    pk(ic, "Town", -40, 1.0)
    pk(ic, "Village", 112, 0.7, True)
def t03(ic):
    pk(ic, "Town", 0, 0.96)
    pk(ic, "Village", -128, 0.66)
    pk(ic, "Village", 140, 0.6, True)
def t04(ic):
    P.tower(ic, 0, 56, 170, "cone", 84, y=20)
    P.house(ic, -104, 96, 46, 56, chimney=-1)
    P.house(ic, -22, 84, 40, 48, chimney=0)
    P.house(ic, 84, 100, 48, 58)
def t05(ic):
    P.church(ic, 0, 150, 56, 50, 1, 48, 130, 80, y=24)
    P.house(ic, -118, 92, 44, 54, chimney=-1)
    P.house(ic, -30, 80, 38, 46, chimney=0)
    P.house(ic, 118, 92, 44, 54)
def t06(ic):
    P.keep(ic, 0, 116, 132, y=22)
    P.house(ic, -112, 94, 44, 54, chimney=-1)
    P.house(ic, 112, 94, 44, 54)
def t07(ic):
    P.tower(ic, -60, 50, 150, "cone", 76, door=False, y=20)
    P.house(ic, 30, 100, 60, 56, y=30, chimney=1, door=False)
    P.house(ic, 110, 84, 52, 48, y=30, chimney=0, door=False)
    P.wall(ic, -150, 160, 54, gate=0)
def t08(ic):
    P.tower(ic, -112, 50, 150, "cone", 76)
    P.tower(ic, 112, 50, 150, "flat")
    P.hall(ic, 0, 150, 60, 52)
def t09(ic):
    P.house(ic, -60, 90, 70, 52, y=40, chimney=-1, door=False)
    P.house(ic, 62, 96, 76, 54, y=40, chimney=1, door=False)
    P.gatehouse(ic, 0, 110, 78, 40, 116)
    P.house(ic, -146, 86, 40, 48, chimney=0)
    P.house(ic, 146, 86, 40, 48, chimney=0)
def t10(ic):
    P.tower(ic, -124, 48, 150, "cone", 74, door=False, y=26)
    P.church(ic, 36, 140, 54, 48, 1, 46, 128, 78, y=26)
    P.house(ic, -150, 86, 40, 50, chimney=0)
    P.house(ic, -66, 96, 46, 56, chimney=-1)
    P.house(ic, 20, 84, 40, 48, chimney=0)
    P.house(ic, 132, 92, 44, 52)
def t11(ic):
    pk(ic, "Tower", 0, 0.8, False, 16)
    pk(ic, "Village", -92, 0.8)
    pk(ic, "Village", 96, 0.74, True)
def t12(ic):
    L = P.hall(ic, 0, 156, 62, 54, y=20)
    P.pennant(ic, 0, 20 + 62 + 54 + 44, 44, 34, 22, join=L)
    P.house(ic, -122, 88, 42, 50, chimney=-1)
    P.house(ic, 122, 88, 42, 50)
def t13(ic):
    L = P.tower(ic, 0, 64, 160, "flat", y=20)
    P.pennant(ic, 0, 20 + 160 + 30, 46, 36, 22, join=L)
    P.house(ic, -96, 96, 46, 56, chimney=-1)
    P.house(ic, 96, 96, 46, 56)
def t14(ic):
    P.house(ic, -132, 66, 84, 50, chimney=0)
    P.house(ic, -66, 70, 116, 54, chimney=-1)
    P.house(ic, 4, 66, 92, 50, chimney=0)
    P.house(ic, 72, 70, 128, 56, chimney=1)
    P.house(ic, 140, 66, 78, 48, chimney=0)
def t15(ic):
    P.dome(ic, 0, 128, 62, 62, y=22)
    P.house(ic, -118, 90, 44, 52, chimney=-1)
    P.house(ic, 118, 90, 44, 52)
def t16(ic):
    P.house(ic, -70, 92, 76, 50, y=24, chimney=-1, door=False)
    P.house(ic, 14, 84, 96, 52, y=24, chimney=0, door=False)
    P.house(ic, 90, 88, 70, 48, y=24, chimney=1, door=False)
    L = P.wall(ic, -128, 128, 52, gate=0)
    P.tower(ic, -150, 46, 86, "flat", door=False, window=True, join=L)
    P.tower(ic, 150, 46, 86, "flat", door=False, window=True, join=L)
def t17(ic):
    P.church(ic, 70, 120, 48, 44, 1, 42, 112, 70, y=26)
    pk(ic, "Tower", -110, 0.66, False, 10)
    pk(ic, "Village", -30, 0.74)
    pk(ic, "Village", 112, 0.6, True)
def t18(ic):
    P.tower(ic, -110, 48, 132, "dome", 64, y=22)
    P.tower(ic, 0, 54, 176, "cone", 84, y=22)
    P.tower(ic, 110, 48, 140, "spire", 90, y=22)
    P.house(ic, -58, 88, 42, 50, chimney=0)
    P.house(ic, 58, 88, 42, 50, chimney=0)
def t19(ic):
    P.windmill(ic, -138, 100, 50, y=14)
    P.church(ic, 40, 132, 50, 46, 1, 44, 118, 72, y=24)
    P.house(ic, -56, 92, 44, 54, chimney=-1)
    P.house(ic, 34, 82, 40, 46, chimney=0)
    P.house(ic, 132, 88, 42, 50)
def t20(ic):
    L = P.tower(ic, 0, 66, 190, "flat", window=False, y=18)
    L["cut"].append(kit.oval(0, 18 + 190 * 0.8, 17, 17))
    P.house(ic, -108, 76, 80, 52, chimney=-1)
    P.house(ic, -40, 70, 60, 46, chimney=0)
    P.house(ic, 40, 70, 64, 46, chimney=0)
    P.house(ic, 108, 76, 84, 52)
def t21(ic):
    pk(ic, "Tower", 120, 0.72, False, 12)
    pk(ic, "Town", -30, 0.94, True)
def t22(ic):
    P.keep(ic, -70, 96, 120, windows=1, y=22)
    P.tower(ic, 70, 50, 150, "cone", 76, door=False, y=22)
    P.house(ic, -140, 84, 40, 48, chimney=0)
    P.house(ic, 0, 92, 44, 54, chimney=-1)
    P.house(ic, 100, 90, 44, 52)


# == cities: walls, many towers, a castle or a great church ===================================================
def c01(ic):
    pk(ic, "Castle", 0, 1.1, False, 34)
    pk(ic, "Town", -168, 0.8)
    pk(ic, "Town", 176, 0.76, True)
    pk(ic, "Village", -52, 0.6)
    pk(ic, "Village", 58, 0.56, True)
def c02(ic):
    pk(ic, "Tower", -196, 0.86)
    pk(ic, "Tower", 196, 0.86)
    pk(ic, "Castle", 0, 1.2)
    pk(ic, "Village", -112, 0.5)
    pk(ic, "Village", 114, 0.5, True)
def c03(ic):
    P.cathedral(ic, 0, 150, 84, 56, 44, 170, 96, y=40)
    P.tower(ic, -150, 46, 150, "cone", 74, door=False, y=40)
    P.tower(ic, 150, 46, 150, "cone", 74, door=False, y=40)
    L = P.wall(ic, -210, 210, 58, gate=0)
    P.tower(ic, -232, 50, 96, "flat", door=False, join=L)
    P.tower(ic, 232, 50, 96, "flat", door=False, join=L)
def c04(ic):
    P.cathedral(ic, -96, 140, 72, 52, 42, 150, 90, y=24)
    P.keep(ic, 110, 120, 140, y=24)
    P.house(ic, -216, 86, 40, 50, chimney=-1)
    P.house(ic, -10, 92, 44, 54, chimney=0)
    P.house(ic, 70, 84, 40, 48, chimney=0)
    P.house(ic, 214, 88, 42, 50)
def c05(ic):
    P.tower(ic, -190, 46, 140, "spire", 86, door=False, y=30)
    P.tower(ic, -110, 52, 190, "cone", 84, door=False, y=30)
    P.tower(ic, -30, 48, 150, "dome", 66, door=False, y=30)
    P.tower(ic, 54, 54, 210, "spire", 100, door=False, y=30)
    P.tower(ic, 136, 50, 160, "flat", door=False, y=30)
    P.tower(ic, 208, 44, 130, "cone", 70, door=False, y=30)
    for i, x in enumerate((-226, -150, -74, 2, 78, 154, 228)):
        P.house(ic, x, 72, 40, 46, chimney=(1 if i % 3 == 0 else 0))
def c06(ic):
    P.tower(ic, -120, 44, 130, "spire", 84, door=False, y=44)
    P.tower(ic, 30, 48, 150, "dome", 64, door=False, y=44)
    P.tower(ic, 140, 44, 120, "cone", 70, door=False, y=44)
    P.house(ic, -180, 86, 60, 50, y=40, chimney=0, door=False)
    P.house(ic, -50, 96, 70, 54, y=40, chimney=-1, door=False)
    P.house(ic, 86, 90, 64, 52, y=40, chimney=0, door=False)
    P.house(ic, 196, 82, 58, 48, y=40, chimney=0, door=False)
    L = P.wall(ic, -236, 236, 56, gate=0)
    for x in (-250, -84, 84, 250):
        P.tower(ic, x, 46, 92, "flat", door=False, join=L)
def c07(ic):
    P.keep(ic, 0, 150, 176, windows=2, y=30)
    P.tower(ic, -110, 52, 150, "cone", 76, door=False, y=30)
    P.tower(ic, 110, 52, 150, "cone", 76, door=False, y=30)
    P.house(ic, -206, 90, 44, 52, chimney=-1)
    P.house(ic, -118, 84, 40, 48, chimney=0)
    P.house(ic, 118, 84, 40, 48, chimney=0)
    P.house(ic, 206, 90, 44, 52)
def c08(ic):
    P.tower(ic, -150, 44, 150, "spire", 90, door=False, y=40)
    P.tower(ic, 150, 44, 150, "spire", 90, door=False, y=40)
    P.house(ic, -84, 100, 78, 58, y=40, chimney=-1, door=False)
    P.house(ic, 84, 100, 78, 58, y=40, chimney=1, door=False)
    L = P.wall(ic, -230, 230, 54)
    P.gatehouse(ic, 0, 116, 84, 44, 130, join=None)
    P.tower(ic, -246, 46, 90, "flat", door=False, join=L)
    P.tower(ic, 246, 46, 90, "flat", door=False, join=L)
def c09(ic):
    P.dome(ic, 0, 170, 80, 84, y=30)
    P.tower(ic, -140, 46, 170, "spire", 96, door=False, y=30)
    P.tower(ic, 140, 46, 170, "spire", 96, door=False, y=30)
    P.house(ic, -210, 88, 42, 50, chimney=-1)
    P.house(ic, -124, 80, 38, 46, chimney=0)
    P.house(ic, 124, 80, 38, 46, chimney=0)
    P.house(ic, 210, 88, 42, 50)
def c10(ic):
    P.cathedral(ic, 0, 160, 96, 60, 46, 190, 100, y=44)
    P.tower(ic, -170, 50, 140, "cone", 74, door=False, y=44)
    P.tower(ic, 170, 50, 140, "cone", 74, door=False, y=44)
    P.wall(ic, -220, 220, 60, gate=0)
def c11(ic):
    P.cathedral(ic, 0, 150, 96, 60, 46, 170, 100, y=150)
    P.house(ic, -190, 90, 44, 52, chimney=-1)
    P.house(ic, 190, 90, 44, 52)
    pk(ic, "Castle", 0, 1.45)
def c12(ic):
    pk(ic, "Town", -150, 0.95, False, 20)
    pk(ic, "Town", 150, 0.95, True, 20)
    pk(ic, "Castle", 0, 1.05)
def c13(ic):
    P.tower(ic, -130, 50, 190, "cone", 84, door=False, y=70)
    P.tower(ic, 0, 54, 220, "spire", 104, door=False, y=70)
    P.tower(ic, 130, 50, 190, "dome", 70, door=False, y=70)
    for x in (-190, -112, -36, 40, 116, 192):
        P.house(ic, x, 74, 40, 46, y=74, chimney=0, door=False)
    for x in (-152, -74, 2, 78, 154):
        P.house(ic, x, 76, 40, 48, y=36, chimney=0, door=False)
    for i, x in enumerate((-196, -118, -40, 38, 116, 194)):
        P.house(ic, x, 76, 42, 48, chimney=(-1 if i == 0 else 1 if i == 5 else 0))
def c14(ic):
    L = P.keep(ic, 0, 140, 190, windows=2, y=30)
    P.pennant(ic, 0, 30 + 190 + 30, 50, 40, 24, join=L)
    for x in (-128, 128):
        P.tower(ic, x, 54, 150, "flat", door=False, y=30)
    L2 = P.wall(ic, -196, 196, 60, gate=0)
    for x in (-214, 214):
        P.tower(ic, x, 50, 100, "flat", door=False, join=L2)
def c15(ic):
    for x, h, r in ((-170, 130, "cone"), (-84, 170, "flat"), (0, 210, "cone"), (84, 170, "flat"), (170, 130, "cone")):
        L = P.tower(ic, x, 52, h, r, 78, door=False, y=34)
        P.pennant(ic, x, 34 + h + (72 if r == "cone" else 30), 40, 30, 18, join=L)
    P.wall(ic, -222, 222, 58, gate=0)
def c16(ic):
    P.keep(ic, -96, 124, 170, windows=2, y=26)
    P.keep(ic, 96, 124, 140, windows=2, y=26)
    P.tower(ic, 0, 50, 200, "spire", 100, door=False, y=26)
    for x in (-196, -8, 196):
        P.house(ic, x, 88, 42, 50, chimney=0)
def c17(ic):
    for x, h, rh in ((-168, 120, 110), (-84, 160, 130), (0, 200, 150), (84, 160, 130), (168, 120, 110)):
        P.tower(ic, x, 50, h, "spire", rh, door=False, y=30)
    for x in (-210, -126, -42, 42, 126, 210):
        P.house(ic, x, 76, 42, 48, chimney=0)
def c18(ic):
    P.dome(ic, 70, 130, 70, 70, y=52)
    P.keep(ic, -84, 110, 150, windows=2, y=52)
    L = P.wall(ic, -200, 200, 62, gate=0)
    for x in (-218, 218):
        P.tower(ic, x, 50, 104, "flat", door=False, join=L)
def c19(ic):
    for x, h in ((-216, 130), (216, 130), (-50, 250), (50, 250)):
        P.tower(ic, x, 46, h, "spire", 100, door=(abs(x) > 100), y=0)
    pk(ic, "Castle", 0, 1.3)
def c20(ic):
    P.cathedral(ic, -110, 124, 80, 52, 40, 170, 92, y=56)
    P.dome(ic, 110, 130, 76, 72, y=56)
    P.keep(ic, 0, 96, 190, windows=1, y=56)
    for x in (-150, -50, 50, 150):
        P.house(ic, x, 80, 50, 48, y=40, chimney=0, door=False)
    L = P.wall(ic, -232, 232, 56, gate=0)
    for x in (-250, 250):
        P.tower(ic, x, 46, 94, "flat", door=False, join=L)
def c21(ic):
    pk(ic, "Tower", -206, 0.74, False, 8)
    pk(ic, "Castle", 30, 1.15, False, 26)
    pk(ic, "Town", -96, 0.84)
    pk(ic, "Village", 150, 0.72, True)
    pk(ic, "Village", 36, 0.56)
def c22(ic):
    P.tower(ic, -60, 50, 190, "cone", 84, door=False, y=46)
    P.tower(ic, 60, 50, 170, "dome", 70, door=False, y=46)
    P.house(ic, -150, 90, 64, 52, y=44, chimney=-1, door=False)
    P.house(ic, 150, 90, 64, 52, y=44, chimney=1, door=False)
    L = P.wall(ic, -120, 120, 58)
    P.gatehouse(ic, 0, 96, 78, 40, 112)
    for x in (-200, 200):
        P.house(ic, x, 86, 42, 50, chimney=0)


def _numbered(prefix, count, scope):
    return [scope["%s%02d" % (prefix, i)] for i in range(1, count + 1)]


WHAT = {
    "Hamlet": ["the pack's house, small", "a cottage", "a cottage seen from the side", "a round hut", "two round huts", "a cottage and a haystack",
               "a cottage by the pack's trees", "a barn", "a tent", "a longhouse", "a cottage and a well", "a cottage and a fence", "a windmill",
               "two small cottages", "a hut and a fence", "a cottage and a barn", "two of the pack's houses, small", "three small huts",
               "a cottage with smoke", "two tents", "the pack's house by its trees", "a farmhouse between haystacks"],
    "Village": ["the pack's Village", "two of the pack's houses", "three of the pack's houses", "three cottages", "cottages and a chapel",
                "two cottages and a well", "a farm village: houses and a barn", "a row of three houses", "five round huts", "cottages and a windmill",
                "a longhouse and two huts", "a church and a cottage", "the pack's tower and houses, small", "cottages, a haystack and a fence",
                "five cottages in two rows", "two cottages about the pack's trees", "a hall between two cottages", "a windmill, a barn and cottages",
                "the pack's houses and a chapel", "two cottages behind a fence", "three cottages, one flying a flag", "three cottages before a long house"],
    "Town": ["the pack's Town", "the pack's Town and house", "the pack's Town between two houses", "a tower and three houses", "a church and houses",
             "a keep between two houses", "a wall and gate, roofs and a tower behind", "a hall between two towers", "a gatehouse, houses behind and beside",
             "a church, a tower and houses", "the pack's tower between two houses", "a market hall with a flag", "a watch tower with a flag, two houses",
             "a row of tall town houses", "a domed hall between two houses", "a walled town: wall, corner towers, roofs", "a church with the pack's tower and houses",
             "three towers and two houses", "a windmill, a church and houses", "a clock tower over town houses", "the pack's Town and tower",
             "a keep, a tower and houses"],
    "City": ["the pack's Castle, Towns and houses", "the pack's Castle between its towers", "a great church behind a towered wall", "a great church, a keep and houses",
             "a skyline of six towers over a row of houses", "a walled city: four wall towers, roofs and spires", "a great keep, two towers and houses",
             "a gatehouse in a long wall, spires behind", "a great dome between two spires", "a great church and towers behind a wall",
             "the pack's Castle before a great church", "the pack's Castle between two of its Towns", "three rows of houses under three towers",
             "a citadel: a keep with a flag, towers and a wall", "five flagged towers behind a wall", "two keeps and a spire", "five spires over a row of houses",
             "a keep and a dome behind a wall", "the pack's Castle among four spires", "a great church, a keep and a dome behind a wall",
             "the pack's Castle, Town, tower and houses", "a gatehouse and wall, two towers and houses"],
}
SETS = {
    "Hamlet": _numbered("h", 22, globals()),
    "Village": _numbered("v", 22, globals()),
    "Town": _numbered("t", 22, globals()),
    "City": _numbered("c", 22, globals()),
}
