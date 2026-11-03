"""Whole-pack measurements of the Hasbro 1984 Proton Pack (G19145L00).

Every value is computed here from pixel readings on Hasbro's product photos and
gbrich's cutting-mat photos, so each number on a pack sheet can be traced and
re-measured. Pixel coordinates are in the original 2000 x 2000 px images:

  FRONT = https://cdn.media.amplience.net/i/hasbropulse/G19145L00_1.png
  BACK  = https://cdn.media.amplience.net/i/hasbropulse/G19145L00_9.png
  SIDE  = https://cdn.media.amplience.net/i/hasbropulse/G19145L00_3.png (worn)
  OPEN  = https://cdn.media.amplience.net/i/hasbropulse/G19145L00_7.png (lid off)

Scope: Hasbro 1984 pack evidence only. See data/measurements.json and docs/METHOD.md.

Statuses: "measured" (cutting-mat photo, gbrich), "estimated" (product photo,
scaled to the overall height), "schematic" (shape or position only).
"""
from __future__ import annotations

PHOTOS = {
    "FRONT": "https://cdn.media.amplience.net/i/hasbropulse/G19145L00_1.png",
    "BACK": "https://cdn.media.amplience.net/i/hasbropulse/G19145L00_9.png",
    "SIDE": "https://cdn.media.amplience.net/i/hasbropulse/G19145L00_3.png",
    "OPEN": "https://cdn.media.amplience.net/i/hasbropulse/G19145L00_7.png",
}

# ------------------------------------------------------------------ overall scale
H = 655.0                 # overall height, mm (estimated, 640-680; frame-based, see measurements.json)
H_RANGE = (640, 680)

# BACK photo: board square to the camera
BACK_TOP, BACK_BOTTOM = 175, 1912            # board top / bottom edge, px
SB = H / (BACK_BOTTOM - BACK_TOP)            # mm per px, 0.3771
BACK_LEFT = 494                              # board left edge at the top, px (x datum)

# FRONT photo: shot from above with the pack leaning back
FRONT_TOP, FRONT_BOTTOM = 131, 1835          # board top / bottom of lower cap, px
K = 0.88                                     # vertical foreshortening (lens 0.91, knob cap 0.85; lens square)
SV = H / (FRONT_BOTTOM - FRONT_TOP)          # mm per vertical px, 0.3844
SH = SV * K                                  # mm per horizontal px, 0.338
FRONT_RIGHT = 1400                           # board edge on the right of the front photo, px (x datum)


def bx(px):
    return (px - BACK_LEFT) * SB


def by(py):
    return (py - BACK_TOP) * SB


# ------------------------------------------------------------------ motherboard (BACK photo)
# Outline points in BACK px, clockwise from the top-left corner. Points flagged
# hidden=True are behind straps, belt or the power cell and are drawn dashed.
BOARD_PX = [
    ((494, 300), False), ((505, 245), False), ((528, 205), False), ((560, 185), False), ((600, 178), False),
    ((960, 178), False), ((985, 192), False), ((1000, 205), False), ((1340, 205), False), ((1352, 217), False),
    ((1352, 480), False),
    ((1293, 800), True),                     # step hidden behind the power cell
    ((1293, 1360), False),
    ((1270, 1500), True), ((1240, 1700), True), ((1180, 1840), True), ((1100, 1890), True),
    ((985, 1895), False), ((985, 1912), False), ((860, 1912), False), ((860, 1895), False),
    ((760, 1890), True), ((680, 1840), True), ((620, 1750), True), ((560, 1600), True), ((530, 1450), True),
    ((517, 1360), False),
]
BOARD = [((bx(x), by(y)), hid) for (x, y), hid in BOARD_PX]

UPPER_W = bx(1352)          # 323.6
LOWER_W = bx(1293) - bx(505)  # lower section, left edge drifts in slightly
STEP_HIDDEN_Y = (by(480), by(800))           # 115-236 mm, behind the power cell

# Holes visible in the BACK photo (centre px, apparent diameter px). Automatic
# dark-blob detection, checked by eye; diameters are approximate (+/-3 px).
HOLES_PX = [
    (560, 255, 12), (1125, 241, 14), (1312, 433, 14), (548, 600, 18),
    (849, 701, 12), (962, 703, 14), (924, 855, 12), (965, 1033, 18),
    (851, 1100, 16), (963, 1102, 13), (942, 1222, 12), (942, 1855, 12),
]
HOLES = [(bx(x), by(y), d * SB) for x, y, d in HOLES_PX]

# Rectangular strap slots (x0, y0, x1, y1 px)
SLOTS_PX = [(578, 333, 700, 348), (1115, 342, 1240, 357)]
SLOTS = [(bx(a), by(b), bx(c) - bx(a), by(d) - by(b)) for a, b, c, d in SLOTS_PX]

# Parts that stand proud of the board edge in the BACK photo
POWER_CELL_BACK = (bx(1352), by(480), bx(1398) - bx(1352), by(790) - by(480))   # beyond the upper edge
SIDE_TUBE_BACK = (bx(1293), by(800), bx(1335) - bx(1293), by(1300) - by(800))   # vertical tube beyond lower edge


# ------------------------------------------------------------------ front components (FRONT photo)
def fx(px):
    """FRONT px -> mm from the board's left edge as seen from the front."""
    return UPPER_W - (FRONT_RIGHT - px) * SH


def fy(py):
    return (py - FRONT_TOP) * SV


# name: (x0, y0, x1, y1) FRONT px, read on a 50 px grid at full resolution (+/-10 px)
COMPONENTS_PX = {
    "Gearbox": (915, 150, 1235, 590),
    "Booster tube": (715, 115, 815, 800),
    "Gun mount": (510, 165, 700, 345),
    "Power cell": (365, 330, 610, 790),
    "Capacitor (DANGER label)": (865, 815, 955, 990),
    "Twin-lens block": (670, 855, 860, 1000),
    "Bumper": (590, 1440, 1335, 1560),
}
COMPONENTS = {k: (fx(a), fy(b), (c - a) * SH, (d - b) * SV) for k, (a, b, c, d) in COMPONENTS_PX.items()}

# Round parts: centre (px), diameter (horizontal px; horizontal is not foreshortened)
ROUND_PX = {
    "Crank generator": (1150, 1020, 240),
    "Cyclotron lid": (994, 1475, 708),
    "Cyclotron housing": (994, 1475, 790),
    "Bumper knob (copper)": (1006, 1543, 97),
    "Lower cap (DANGER label)": (1142, 1770, 195),
}
ROUND = {k: (fx(x), fy(y), d * SH) for k, (x, y, d) in ROUND_PX.items()}
# the lower cap's bottom is the front-height datum (FRONT_BOTTOM); place its centre so it sits on it
_c = ROUND["Lower cap (DANGER label)"]
ROUND["Lower cap (DANGER label)"] = (_c[0], H - _c[2] / 2, _c[2])

# Cyclotron lenses: centres (px). Upper pair fully visible; lower pair partly
# hidden by the bumper, centres from the visible part (biased low).
LENSES_PX = [(856, 1354), (1132, 1354), (879, 1592), (1110, 1598)]
LENS_D_PX = 93.3                    # unlit upper-left lens, ellipse major axis
LENS_SPACING_H = (1132 - 856) * SH  # 93.3 mm
LENS_SPACING_V = (1595 - 1354) * SV  # 92.6 mm (biased high)
LENS_D = LENS_D_PX * SH             # 31.5 mm

# ------------------------------------------------------------------ cyclotron (gbrich, cutting mat)
PANEL_OD = 262.0     # measured, 260-264, post #23
CAKE_TOP = 141.0     # measured, 138-144, post #23
CAKE_H = 46.0        # measured, 41-53, post #23

# Housing opening from the OPEN photo: ratio to the cake top (same view)
CAKE_TOP_PX_OPEN = 723.0      # mean of ellipse fits 707-736 px (major axis)
OPENING_PX_OPEN = 1140.0      # horizontal 1014 px / cake aspect 0.89
OPENING = CAKE_TOP * OPENING_PX_OPEN / CAKE_TOP_PX_OPEN   # ~222 mm; rim nearer the camera, so an upper bound

# ------------------------------------------------------------------ side view (SIDE photo, schematic)
# Depth from the back of the board, corrected for a ~14 deg yaw (lid aspect
# ~0.24) and the near-edge offset; worn photo, scale and perspective uncontrolled.
DEPTH = {
    "Gearbox front": 162,
    "Cyclotron lid face": 182,
    "Lower cap front": 212,
    "Bumper knob tip": 256,
}
DEPTH_NOTE = "schematic, about +/-15%"


if __name__ == "__main__":
    print(f"SB {SB:.4f}  SV {SV:.4f}  SH {SH:.4f}  upper width {UPPER_W:.1f}  lower width {LOWER_W:.1f}")
    for k, v in COMPONENTS.items():
        print(f"{k:28s} x {v[0]:6.1f}  y {v[1]:6.1f}  w {v[2]:5.1f}  h {v[3]:5.1f}")
    for k, v in ROUND.items():
        print(f"{k:28s} cx {v[0]:6.1f}  cy {v[1]:6.1f}  d {v[2]:5.1f}")
    print(f"lenses: spacing {LENS_SPACING_H:.1f} x {LENS_SPACING_V:.1f}, d {LENS_D:.1f}; opening {OPENING:.0f}")
    print("power cell beyond board edge (back):", round(POWER_CELL_BACK[2], 1), "mm")
    print("power cell outer face (front) from board left edge:", round(COMPONENTS['Power cell'][0], 1), "mm")
