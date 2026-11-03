"""Render the whole-pack blueprint sheets (P1-P4) for the Hasbro 1984 Proton Pack.

Usage:  python tools/make_pack_drawings.py

Writes docs/drawings/p<N>_*.png and .svg, and docs/drawings/pack_blueprints.pdf
(US Letter landscape, print at 100%). All values come from tools/pack_data.py.

Colour code (same as the part sheets):
  white          measured (cutting-mat photo)
  light blue     estimated from Hasbro's product photos, scaled to the overall height
  grey, dashed   schematic (shape or position only, or hidden in the photos)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

import make_drawings as md  # noqa: E402
import pack_data as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "drawings"
VERSION = "0.6"
COL = {"measured": md.LINE, "estimated": md.DERIVED, "schematic": md.SCHEM}


class PackSheet(md.Sheet):
    def __init__(self, sid, title, scale, n, total, sources):
        self._sources = sources
        super().__init__(sid, title, scale, n, total, [])

    def title_block(self, sid, title, scale, n, total, posts):
        x0, y0, w, h = md.PAGE_W - 10 - 128, 10, 128, 44
        a = self.ax
        a.add_patch(Rectangle((x0, y0), w, h, fc=md.BG, ec=md.LINE, lw=0.8, zorder=6))
        for yy in (y0 + 30, y0 + 20, y0 + 10):
            self.line([x0, x0 + w], [yy, yy], lw=0.4, z=7)
        self.line([x0 + 96, x0 + 96], [y0 + 20, y0 + 30], lw=0.4, z=7)
        self.line([x0 + 64, x0 + 64], [y0, y0 + 10], lw=0.4, z=7)

        def t(xx, yy, s, **k):
            a.text(xx, yy, s, color=k.pop("color", md.LINE), zorder=8, **k)

        t(x0 + 2, y0 + 39.5, "HASBRO 1984 PROTON PACK · BLUEPRINT", fontsize=6.2, weight="bold", va="center")
        t(x0 + 2, y0 + 34, "GBFans.com community blueprint · Hasbro Pulse G19145L00", fontsize=4.8,
          va="center", color=md.SCHEM)
        t(x0 + 2, y0 + 25, title.upper(), fontsize=8.6, weight="bold", va="center")
        t(x0 + 98, y0 + 27.2, "SHEET", fontsize=4.5, color=md.SCHEM, va="center")
        t(x0 + 98, y0 + 23, f"{sid}  ({n} of {total})", fontsize=7, weight="bold", va="center")
        t(x0 + 2, y0 + 17, "MEASURED", fontsize=5.2, weight="bold", va="center")
        t(x0 + 24, y0 + 17, "ESTIMATED", fontsize=5.2, weight="bold", va="center", color=md.DERIVED,
          fontstyle="italic")
        t(x0 + 47, y0 + 17, "- - SCHEMATIC", fontsize=5.2, weight="bold", va="center", color=md.SCHEM)
        t(x0 + 76, y0 + 17, "estimates ±3% unless noted", fontsize=5.0, va="center", color=md.SCHEM)
        t(x0 + 2, y0 + 12.6, "Sources: " + self._sources, fontsize=4.6, va="center", color=md.SCHEM)
        t(x0 + 2, y0 + 6.5, f"SCALE  {scale}", fontsize=6, weight="bold", va="center")
        t(x0 + 2, y0 + 2.6, "Dimensions in mm", fontsize=4.6, va="center", color=md.SCHEM)
        t(x0 + 66, y0 + 6.5, f"v{VERSION} · {date(2026, 11, 3).isoformat()}", fontsize=5.4, va="center")
        t(x0 + 66, y0 + 2.6, "Drawn: ryan-brumback · not a Hasbro drawing", fontsize=4.6, va="center",
          color=md.SCHEM)
        self.text(12, 12.5, f"Overall height {pd.H:.0f} mm (range {pd.H_RANGE[0]}-{pd.H_RANGE[1]}). "
                  "Pixel readings: tools/pack_data.py · method: docs/METHOD.md", size=4.8, color=md.SCHEM)

    # ---- helpers in drawing space -------------------------------------------
    def dh(self, x1, x2, y, s, status="estimated", ext=None, below=False, size=6.2):
        c = COL[status]
        if ext:
            for x, y0 in zip((x1, x2), ext):
                self.line([x, x], [y0, y + (-1.2 if below else 1.2) * (1 if y > y0 else -1) * -1], color=c, lw=0.3)
        self.arrow(x1, y, x2, y, color=c, style="<|-|>", ms=4, lw=0.45)
        self.ax.text((x1 + x2) / 2, y + (-0.8 if below else 0.8), s, fontsize=size, color=c, ha="center",
                     va="top" if below else "bottom", fontstyle="italic" if status == "estimated" else "normal",
                     zorder=5)

    def dv(self, x, y1, y2, s, status="estimated", ext=None, left=False, size=6.2):
        c = COL[status]
        if ext:
            for y, x0 in zip((y1, y2), ext):
                self.line([x0, x], [y, y], color=c, lw=0.3)
        self.arrow(x, y1, x, y2, color=c, style="<|-|>", ms=4, lw=0.45)
        self.ax.text(x + (-0.9 if left else 0.9), (y1 + y2) / 2, s, fontsize=size, color=c, rotation=90,
                     ha="right" if left else "left", va="center",
                     fontstyle="italic" if status == "estimated" else "normal", zorder=5)


# ------------------------------------------------------------------ drawing primitives
def board_outline(S, ox, oy, sc, mirror=False, lw=0.9):
    """Draw the motherboard outline. (ox, oy) = page position of the board's top-left; sc = mm per mm."""
    pts = pd.BOARD

    def P(p):
        x, y = p
        if mirror:
            x = pd.UPPER_W - x
        return ox + x * sc, oy - y * sc

    n = len(pts)
    for i in range(n):
        (p1, h1), (p2, h2) = pts[i], pts[(i + 1) % n]
        hidden = h1 or h2
        a, b = P(p1), P(p2)
        S.line([a[0], b[0]], [a[1], b[1]], color=md.SCHEM if hidden else md.DERIVED, lw=lw * (0.7 if hidden else 1),
               ls=(0, (3, 2)) if hidden else "-")


def rect_mm(S, ox, oy, sc, x, y, w, h, color=md.DERIVED, ls="-", lw=0.6):
    S.rect(ox + x * sc, oy - (y + h) * sc, w * sc, h * sc, color=color, ls=ls, lw=lw)


def circ_mm(S, ox, oy, sc, cx, cy, d, color=md.DERIVED, ls="-", lw=0.6):
    S.circle(ox + cx * sc, oy - cy * sc, d / 2 * sc, color=color, ls=ls, lw=lw)


def front_view(S, ox, oy, sc, labels=True):
    board_outline(S, ox, oy, sc, mirror=True, lw=0.7)
    for name, (x, y, w, h) in pd.COMPONENTS.items():
        rect_mm(S, ox, oy, sc, x, y, w, h)
    for name, (cx, cy, d) in pd.ROUND.items():
        ls = (0, (3, 2)) if name == "Cyclotron housing" else "-"
        circ_mm(S, ox, oy, sc, cx, cy, d, ls=ls, color=md.SCHEM if name == "Cyclotron housing" else md.DERIVED)
    lc = pd.ROUND["Cyclotron lid"]
    for (px, py) in pd.LENSES_PX:
        circ_mm(S, ox, oy, sc, pd.fx(px), pd.fy(py), pd.LENS_D)


def back_view(S, ox, oy, sc, detail=False):
    board_outline(S, ox, oy, sc)
    x, y, w, h = pd.POWER_CELL_BACK
    rect_mm(S, ox, oy, sc, x, y, w, h, color=md.SCHEM, ls=(0, (3, 2)))
    x, y, w, h = pd.SIDE_TUBE_BACK
    rect_mm(S, ox, oy, sc, x, y, w, h, color=md.SCHEM, ls=(0, (3, 2)))
    for x, y, d in pd.HOLES:
        circ_mm(S, ox, oy, sc, x, y, max(d, 1.5 / sc if not detail else d), lw=0.45)
    for x, y, w, h in pd.SLOTS:
        rect_mm(S, ox, oy, sc, x, y, w, h, lw=0.45)


def side_view(S, ox, oy, sc):
    """Schematic side view: board as a plate, depths of the front-most features."""
    t = 6  # board + lip, schematic
    S.rect(ox, oy - pd.H * sc, t * sc, pd.H * sc, color=md.SCHEM, ls=(0, (3, 2)), lw=0.6)
    feats = {
        "Gearbox front": (pd.COMPONENTS["Gearbox"][1], pd.COMPONENTS["Gearbox"][3]),
        "Cyclotron lid face": (pd.ROUND["Cyclotron lid"][1] - pd.ROUND["Cyclotron lid"][2] / 2,
                               pd.ROUND["Cyclotron lid"][2]),
        "Lower cap front": (pd.ROUND["Lower cap (DANGER label)"][1] - 33, 66),
        "Bumper knob tip": (pd.ROUND["Bumper knob (copper)"][1] - 16, 33),
    }
    for name, (y0, hgt) in feats.items():
        d = pd.DEPTH[name]
        S.rect(ox + t * sc, oy - (y0 + hgt) * sc, (d - t) * sc, hgt * sc, color=md.SCHEM, ls=(0, (3, 2)), lw=0.5)
    return feats


# ------------------------------------------------------------------ sheets
def p1_general(S: PackSheet):
    sc = 1 / 6
    top = 192
    # front
    ox = 22
    front_view(S, ox, top, sc)
    S.view_label(ox + pd.UPPER_W * sc / 2, top - pd.H * sc - 7, "FRONT", "1:6")
    S.dv(ox - 5, top, top - pd.H * sc, f"{pd.H:.0f} ({pd.H_RANGE[0]}–{pd.H_RANGE[1]})", ext=(ox, ox), left=True)
    # back
    ox2 = 95
    back_view(S, ox2, top, sc)
    S.view_label(ox2 + pd.UPPER_W * sc / 2, top - pd.H * sc - 7, "BACK", "1:6")
    S.dh(ox2, ox2 + pd.UPPER_W * sc, top + 2.5, f"{pd.UPPER_W:.0f}")
    S.dh(ox2 + 4.1 * sc, ox2 + (4.1 + pd.LOWER_W) * sc, top - 380 * sc, f"{pd.LOWER_W:.0f}", size=5.6)
    # side
    ox3 = 172
    side_view(S, ox3, top, sc)
    S.view_label(ox3 + 22, top - pd.H * sc - 7, "SIDE (SCHEMATIC)", "1:6")
    dmax = max(pd.DEPTH.values())
    S.dh(ox3, ox3 + dmax * sc, top + 2.5, f"~{dmax} to bumper knob", status="schematic")
    S.notes(14, 58, "General arrangement", [
        (f"Overall height {pd.H:.0f} mm, estimated (range {pd.H_RANGE[0]}–{pd.H_RANGE[1]}), from the ALICE frame "
         "on gbrich's pack. All other values scale with it.", "posts #68, #72"),
        ("Back view is square to the camera; front view is corrected for a vertical foreshortening of 0.88.",
         "Hasbro product photos"),
        ("Side depths are schematic (worn photo, yaw ~14°, about ±15%).", None),
        ("Dashed: hidden in the photos (behind straps, belt, power cell).", None),
    ], width=100, size=5.4)


def p2_motherboard(S: PackSheet):
    sc = 1 / 4
    ox, top = 30, 197
    back_view(S, ox, top, sc, detail=True)
    W = pd.UPPER_W
    S.dh(ox, ox + W * sc, top + 2.5, f"{W:.1f} upper section")
    S.dv(ox - 6, top, top - pd.H * sc, f"{pd.H:.0f} overall", ext=(ox, ox), left=True)
    lx = pd.bx(505)
    S.dh(ox + lx * sc, ox + (lx + pd.LOWER_W) * sc, top - 380 * sc, f"{pd.LOWER_W:.1f} lower section")
    y1, y2 = pd.STEP_HIDDEN_Y
    S.dv(ox + W * sc + 14, top - y1 * sc, top - y2 * sc, f"step {y1:.0f}–{y2:.0f} below top (hidden)",
         status="schematic", ext=(ox + W * sc, ox + W * sc))
    S.dv(ox + W * sc + 4, top, top - pd.by(205) * sc, f"{pd.by(205):.0f}", ext=(ox + W * sc, ox + W * sc))
    S.callout(ox + (pd.POWER_CELL_BACK[0] + 8) * sc, top - (pd.POWER_CELL_BACK[1] + 80) * sc,
              ox + W * sc + 22, top - 160 * sc, f"power cell, {pd.POWER_CELL_BACK[2]:.0f} beyond edge",
              color=md.SCHEM, size=5.6)
    S.callout(ox + (pd.SIDE_TUBE_BACK[0] + 5) * sc, top - 330 * sc, ox + W * sc + 22, top - 330 * sc,
              "vertical tube, beyond lower edge", color=md.SCHEM, size=5.6)
    S.callout(ox + 120 * sc, top - 600 * sc, ox + W * sc + 22, top - 560 * sc, "bottom taper hidden by belt",
              color=md.SCHEM, size=5.6)
    # hole table
    y = 196
    TX = 186
    S.text(TX, y, "Holes (centre from datum, mm)", size=7, weight="bold")
    y -= 4.5
    for i, (x, yy, d) in enumerate(pd.HOLES, 1):
        S.text(TX, y, f"H{i:<2d} x {x:4.0f}  y {yy:4.0f}  Ø~{d:.0f}", size=5.6, color=md.DERIVED,
               family="DejaVu Sans Mono")
        S.text(ox + x * sc + 1.2, top - yy * sc + 0.8, f"H{i}", size=4.2, color=md.DERIVED)
        y -= 3.5
    y -= 2
    for i, (x, yy, w, h) in enumerate(pd.SLOTS, 1):
        S.text(TX, y, f"Slot {i}: x {x:.0f}  y {yy:.0f}  {w:.0f} × {h:.0f}", size=5.6, color=md.DERIVED)
        y -= 3.5
    S.notes(TX, y - 4, "Notes", [
        ("Datum: top-left corner of the board's bounding box in the straight-on back photo (x right, y down).",
         None),
        ("Hole diameters are approximate (±1 mm); positions ±2 mm plus the ±3% scale.", None),
        ("Upper and lower widths differ by a step on the power-cell side, hidden behind the power cell.", None),
        ("The stock board's lip wraps the shell base; an aftermarket flat board does not.", "post #55"),
    ], width=44, size=5.2)


def p3_front(S: PackSheet):
    sc = 1 / 4
    ox, top = 22, 197
    front_view(S, ox, top, sc)
    W = pd.UPPER_W
    S.dh(ox, ox + W * sc, top + 2.5, f"{W:.0f} (board, upper)")
    # label components
    for name, (x, y, w, h) in pd.COMPONENTS.items():
        S.text(ox + (x + w / 2) * sc, top - (y + h / 2) * sc, str(list(pd.COMPONENTS).index(name) + 1), size=6,
               color=md.LINE, ha="center", va="center", weight="bold")
    for j, (name, (cx, cy, d)) in enumerate(pd.ROUND.items()):
        if name == "Cyclotron housing":
            continue
        S.text(ox + cx * sc + (d / 2) * sc * 0.7, top - cy * sc + (d / 2) * sc * 0.7, chr(65 + j), size=6,
               color=md.LINE, ha="center", va="center", weight="bold")
    y = 196
    S.text(118, y, "Components (mm; x from the board's left edge as seen from the front, y from the top)",
           size=6.6, weight="bold")
    y -= 5
    for i, (name, (x, yy, w, h)) in enumerate(pd.COMPONENTS.items(), 1):
        S.text(118, y, f"{i}  {name}", size=5.8)
        S.text(178, y, f"x {x:6.0f}  y {yy:5.0f}   {w:4.0f} wide × {h:4.0f} high", size=5.8, color=md.DERIVED,
               family="DejaVu Sans Mono")
        y -= 3.8
    y -= 1.5
    for j, (name, (cx, cy, d)) in enumerate(pd.ROUND.items()):
        st = md.SCHEM if name == "Cyclotron housing" else md.DERIVED
        S.text(118, y, f"{chr(65 + j)}  {name}", size=5.8)
        S.text(178, y, f"centre x {cx:5.0f}  y {cy:5.0f}   Ø {d:4.0f}", size=5.8, color=st, family="DejaVu Sans Mono")
        y -= 3.8
    S.notes(118, y - 3, "Notes", [
        ("Envelopes are the outer extents of each part as seen from the front, read at full resolution "
         "(±3 mm) and scaled with a horizontal 0.338 and a vertical 0.384 mm per pixel.", "Hasbro product photo 1"),
        ("Front-view horizontal values carry the foreshortening uncertainty (0.85–0.92), about ±5%.", None),
        ("Parts at different depths are drawn in one plane (no perspective correction for depth).", None),
        ("Check: the power cell overhangs the board by 27 in this view and 17 in the back view; the 10 mm "
         "difference is the size of the front-view horizontal uncertainty.", "Hasbro product photos 1 and 9"),
        ("Part names follow common GBFans usage.", None),
    ], width=66, size=5.4)


def p4_cyclotron(S: PackSheet):
    sc = 1 / 2
    cx, cy = 80, 128
    hous = pd.ROUND["Cyclotron housing"][2]
    lid = pd.ROUND["Cyclotron lid"][2]
    S.circle(cx, cy, hous / 2 * sc, color=md.SCHEM, ls=(0, (3, 2)), lw=0.6)
    S.circle(cx, cy, lid / 2 * sc, color=md.DERIVED, lw=0.9)
    S.circle(cx, cy, pd.PANEL_OD / 2 * sc, color=md.LINE, lw=0.6, ls=(0, (6, 2)))
    S.circle(cx, cy, pd.CAKE_TOP / 2 * sc, color=md.LINE, lw=0.8)
    S.circle(cx, cy, pd.OPENING / 2 * sc, color=md.SCHEM, ls=(0, (1, 1.5)), lw=0.5)
    a = pd.LENS_SPACING_H / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            S.circle(cx + sx * a * sc, cy + sy * a * sc, pd.LENS_D / 2 * sc, color=md.DERIVED, lw=0.7)
    S.centerline(cx - hous / 2 * sc - 4, cy, cx + hous / 2 * sc + 4, cy)
    S.centerline(cx, cy - hous / 2 * sc - 4, cx, cy + hous / 2 * sc + 4)
    S.dh(cx - lid / 2 * sc, cx + lid / 2 * sc, cy + hous / 2 * sc + 3, f"Ø{lid:.0f} lid")
    S.dh(cx - a * sc, cx + a * sc, cy - 6, f"{pd.LENS_SPACING_H:.0f} lens pitch", size=5.6)
    S.dv(cx + a * sc + 9, cy + a * sc, cy - a * sc, f"{pd.LENS_SPACING_V:.0f}", size=5.6)
    TX = 152
    S.callout(cx + a * sc + pd.LENS_D / 2 * sc * 0.7, cy + a * sc + pd.LENS_D / 2 * sc * 0.7,
              TX, 146, f"lens Ø{pd.LENS_D:.0f} (4×), estimated", color=md.DERIVED, size=5.8)
    S.callout(cx + pd.CAKE_TOP / 2 * sc * 0.707, cy + pd.CAKE_TOP / 2 * sc * 0.707 - 6, TX, 140,
              f"cake top Ø{pd.CAKE_TOP:.0f} (138–144), measured", color=md.LINE, size=5.8)
    S.callout(cx + pd.OPENING / 2 * sc * 0.97, cy + pd.OPENING / 2 * sc * 0.25, TX, 134,
              f"opening Ø~{pd.OPENING:.0f} (lid off), upper bound", color=md.SCHEM, size=5.8)
    S.callout(cx + pd.PANEL_OD / 2 * sc, cy, TX, 128,
              f"rear panel Ø{pd.PANEL_OD:.0f} (260–264), measured", color=md.LINE, size=5.8)
    S.callout(cx + hous / 2 * sc * 0.97, cy - hous / 2 * sc * 0.25, TX, 122,
              f"housing Ø~{hous:.0f}, schematic", color=md.SCHEM, size=5.8)
    S.view_label(cx, 52, "CYCLOTRON, FRONT (LID ON, INNER PARTS DASHED)", "1:2")
    # cake section
    x0, yb = 175, 176
    S.rect(x0, yb, pd.PANEL_OD * 0.25, 2, color=md.LINE, lw=0.6)
    cw = pd.CAKE_TOP * 0.25
    S.rect(x0 + (pd.PANEL_OD * 0.25 - cw) / 2, yb + 2, cw, pd.CAKE_H * 0.25, color=md.LINE, lw=0.7)
    S.dv(x0 + pd.PANEL_OD * 0.25 + 4, yb + 2, yb + 2 + pd.CAKE_H * 0.25, f"{pd.CAKE_H:.0f} (41–53)", status="measured",
         ext=(x0 + (pd.PANEL_OD * 0.25 + cw) / 2, x0 + (pd.PANEL_OD * 0.25 + cw) / 2))
    S.dh(x0, x0 + pd.PANEL_OD * 0.25, yb - 3, f"{pd.PANEL_OD:.0f}", status="measured", below=True)
    S.view_label(x0 + pd.PANEL_OD * 0.125, yb - 12, "CAKE ON REAR PANEL, SIDE", "1:4 (panel thickness schematic)")
    S.notes(152, 113, "Notes", [
        ("Rear panel and cake measured by gbrich's photos on a 1 cm cutting mat (camera calibrated from the grid).",
         "post #23"),
        ("Lid and lenses estimated on Hasbro's front photo. The four lenses form a square (93 × 93 mm), which "
         "checks the foreshortening correction.", "Hasbro product photo 1"),
        ("The housing (Ø~267) clears the 262 mm panel; the lid (Ø~240) covers the ~222 mm opening.",
         "Hasbro product photos 1 and 7"),
    ], width=62, size=5.4)


SHEETS = [
    ("P1", "p1_general_arrangement", "General arrangement", "1:6", p1_general,
     "Hasbro photos 1, 3, 9; posts #68, #72"),
    ("P2", "p2_motherboard", "Motherboard", "1:4", p2_motherboard, "Hasbro photo 9; post #55"),
    ("P3", "p3_front_layout", "Front layout", "1:4", p3_front, "Hasbro photo 1"),
    ("P4", "p4_cyclotron", "Cyclotron", "1:2", p4_cyclotron, "Hasbro photos 1, 7; post #23"),
]


RENDER_SECTION = """
## Whole-pack sheets P1–P4

Generated by `tools/make_pack_drawings.py` (run it after `tools/make_drawings.py`, which rewrites this file) from the pixel readings in `tools/pack_data.py`. Every value traces to one of these photos (linked, not copied):

- [Hasbro product photo 1, front](https://cdn.media.amplience.net/i/hasbropulse/G19145L00_1.png): front layout (P1, P3), lid and lenses (P4).
- [Hasbro product photo 9, back](https://cdn.media.amplience.net/i/hasbropulse/G19145L00_9.png): motherboard outline, holes and slots (P1, P2).
- [Hasbro product photo 3, worn side](https://cdn.media.amplience.net/i/hasbropulse/G19145L00_3.png): schematic depths (P1).
- [Hasbro product photo 7, lid off](https://cdn.media.amplience.net/i/hasbropulse/G19145L00_7.png): cyclotron opening (P4).
- gbrich, [post #23](https://forum.gbfans.com/t/hasbro-1984-proton-pack-big-overhaul-and-customisation/219236/23): rear panel and cake on a cutting mat (P4).
- gbrich, [post #68](https://forum.gbfans.com/t/hasbro-1984-proton-pack-big-overhaul-and-customisation/219236/68) and [post #72](https://forum.gbfans.com/t/hasbro-1984-proton-pack-big-overhaul-and-customisation/219236/72): Rothco ALICE frame on the pack, which sets the overall height (all sheets).
"""


def write_render_section():
    p = ROOT / "docs" / "RENDERINGS.md"
    t = p.read_text(encoding="utf-8")
    if "## Whole-pack sheets P1" in t:
        t = t[:t.index("\n## Whole-pack sheets P1")]
    p.write_text(t.rstrip("\n") + "\n" + RENDER_SECTION, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with PdfPages(OUT / "pack_blueprints.pdf") as pdf:
        for n, (sid, stem, title, scale, func, src) in enumerate(SHEETS, 1):
            S = PackSheet(sid, title, scale, n, len(SHEETS), src)
            func(S)
            S.fig.savefig(OUT / f"{stem}.png", dpi=200, facecolor=md.BG)
            S.fig.savefig(OUT / f"{stem}.svg", facecolor=md.BG)
            pdf.savefig(S.fig, facecolor=md.BG)
            plt.close(S.fig)
            print(sid, stem)
    write_render_section()


if __name__ == "__main__":
    main()
