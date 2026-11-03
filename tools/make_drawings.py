"""Render the blueprint sheets and their attribution page.

Usage:  python tools/make_drawings.py

Writes, for each sheet in drawing_data.SHEETS:
  docs/drawings/<stem>.png   (200 dpi, for the wiki)
  docs/drawings/<stem>.svg
and docs/drawings/blueprints.pdf (all sheets, US Letter landscape, print at 100%)
and docs/RENDERINGS.md (every dimension -> post, plus the forum photos of each part).

Every sheet is laid out in millimetres on a US Letter landscape page, so the PDF
prints at true size. Each sheet states its drawing scale.
"""
from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon, Rectangle  # noqa: E402

import drawing_data as dd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "drawings"
VERSION = "0.2"

PAGE_W, PAGE_H = 279.4, 215.9          # US Letter landscape, mm
MM = 1 / 25.4                           # inches per mm

BG = "#123a6b"
GRID_MINOR = "#18467e"
GRID_MAJOR = "#24578f"
LINE = "#ffffff"
DERIVED = "#8fd8ff"
SCHEM = "#b9cfe8"
REJECT = "#ffb4a2"
FONT = "DejaVu Sans"

plt.rcParams.update({"font.family": FONT, "svg.fonttype": "none"})


# ---------------------------------------------------------------- data helpers

def dim(key):
    return dd.DIMS[key]


def fmt(key, prefix=""):
    v, unit, posts, status, _ = dim(key)
    vs = f"{v:g}"
    unit_s = {"mm": "", "deg": "°", "pcs": "×", "teeth": "T"}.get(unit, unit)
    return f"{prefix}{vs}{unit_s}"


def refs(key):
    return "p" + ",".join(f"{p}" for p in dim(key)[2])


def color_for(key):
    return {"sourced": LINE, "derived": DERIVED, "schematic": SCHEM}[dim(key)[3]]


# -------------------------------------------------------------- page framework

class Sheet:
    def __init__(self, sid, title, scale, n, total, posts):
        self.fig = plt.figure(figsize=(PAGE_W * MM, PAGE_H * MM))
        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, PAGE_W)
        ax.set_ylim(0, PAGE_H)
        ax.set_aspect("equal")
        ax.axis("off")
        self.ax = ax
        ax.add_patch(Rectangle((0, 0), PAGE_W, PAGE_H, color=BG, zorder=-10))
        for x in range(0, int(PAGE_W) + 1, 5):
            ax.plot([x, x], [0, PAGE_H], color=GRID_MAJOR if x % 25 == 0 else GRID_MINOR, lw=0.35, zorder=-9)
        for y in range(0, int(PAGE_H) + 1, 5):
            ax.plot([0, PAGE_W], [y, y], color=GRID_MAJOR if y % 25 == 0 else GRID_MINOR, lw=0.35, zorder=-9)
        ax.add_patch(Rectangle((8, 8), PAGE_W - 16, PAGE_H - 16, fill=False, ec=LINE, lw=1.2))
        ax.add_patch(Rectangle((10, 10), PAGE_W - 20, PAGE_H - 20, fill=False, ec=LINE, lw=0.4))
        self.title_block(sid, title, scale, n, total, posts)

    # basic drawing ----------------------------------------------------------
    def text(self, x, y, s, size=7, color=LINE, ha="left", va="baseline", **kw):
        self.ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, **kw)

    def line(self, xs, ys, color=LINE, lw=0.8, ls="-", z=2):
        self.ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="butt")

    def rect(self, x, y, w, h, hatch=None, color=LINE, lw=0.8, ls="-", fill=False, fc=None, z=2):
        self.ax.add_patch(Rectangle((x, y), w, h, fill=fill, fc=fc, ec=color, lw=lw, ls=ls,
                                    hatch=hatch, zorder=z))

    def circle(self, x, y, r, color=LINE, lw=0.8, ls="-", hatch=None, fill=False, fc=None, z=2):
        self.ax.add_patch(Circle((x, y), r, fill=fill, fc=fc, ec=color, lw=lw, ls=ls, hatch=hatch, zorder=z))

    def arrow(self, x1, y1, x2, y2, color=LINE, style="-|>", lw=0.7, ms=6, rad=0.0):
        self.ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=ms,
                                          color=color, lw=lw, connectionstyle=f"arc3,rad={rad}", zorder=4))

    def centerline(self, x1, y1, x2, y2):
        self.line([x1, x2], [y1, y2], lw=0.4, ls=(0, (8, 2, 1, 2)))

    # dimensions -------------------------------------------------------------
    def label(self, x, y, key, prefix="", ha="center", va="bottom", size=7, rot=0):
        c = color_for(key)
        style = "italic" if dim(key)[3] == "derived" else "normal"
        self.ax.text(x, y, fmt(key, prefix), fontsize=size, color=c, ha=ha, va=va, rotation=rot,
                     fontstyle=style, zorder=5)
        # source tag
        dx, dy = (0, -3.2) if rot == 0 else (3.2, 0)
        if va == "top":
            dy = -3.2 if rot == 0 else 0
        self.ax.text(x + dx, y + dy if va == "bottom" else y + dy, refs(key), fontsize=4.6, color=c,
                     ha=ha, va="top" if va == "bottom" else "top", rotation=rot, alpha=0.85, zorder=5)

    def dim_h(self, x1, x2, y, key, ext_from=None, prefix="", above=True):
        c = color_for(key)
        if ext_from is not None:
            for x, y0 in zip((x1, x2), ext_from):
                self.line([x, x], [y0, y + (1.5 if y > y0 else -1.5)], color=c, lw=0.35)
        self.arrow(x1, y, x2, y, color=c, style="<|-|>", ms=5, lw=0.5)
        ty = y + 0.8 if above else y - 0.8
        c2 = color_for(key)
        st = "italic" if dim(key)[3] == "derived" else "normal"
        self.ax.text((x1 + x2) / 2, ty, fmt(key, prefix), fontsize=7, color=c2, ha="center",
                     va="bottom" if above else "top", fontstyle=st, zorder=5)
        self.ax.text((x1 + x2) / 2, ty + (3.4 if above else -3.4), refs(key), fontsize=4.6, color=c2,
                     ha="center", va="bottom" if above else "top", alpha=0.85, zorder=5)

    def dim_v(self, x, y1, y2, key, ext_from=None, prefix="", right=True):
        c = color_for(key)
        if ext_from is not None:
            for y, x0 in zip((y1, y2), ext_from):
                self.line([x0, x + (1.5 if x > x0 else -1.5)], [y, y], color=c, lw=0.35)
        self.arrow(x, y1, x, y2, color=c, style="<|-|>", ms=5, lw=0.5)
        tx = x + 1.2 if right else x - 1.2
        st = "italic" if dim(key)[3] == "derived" else "normal"
        self.ax.text(tx, (y1 + y2) / 2, fmt(key, prefix), fontsize=7, color=c, rotation=90,
                     ha="left" if right else "right", va="center", fontstyle=st, zorder=5)
        self.ax.text(tx + (3.6 if right else -3.6), (y1 + y2) / 2, refs(key), fontsize=4.6, color=c,
                     rotation=90, ha="left" if right else "right", va="center", alpha=0.85, zorder=5)

    def callout(self, x, y, tx, ty, s, color=LINE, size=6.5, ha="left"):
        self.line([x, tx], [y, ty], color=color, lw=0.45)
        self.ax.add_patch(Circle((x, y), 0.5, color=color, zorder=4))
        self.text(tx + (1 if ha == "left" else -1), ty, s, size=size, color=color, ha=ha, va="center")

    def view_label(self, x, y, s, scale=None):
        self.text(x, y, s, size=8, weight="bold", ha="center")
        if scale:
            self.text(x, y - 3.6, scale, size=5.8, ha="center", color=SCHEM)

    def notes(self, x, y, heading, items, width=95, size=6.2):
        self.text(x, y, heading, size=7.5, weight="bold")
        y -= 5
        for i, (s, ref) in enumerate(items, 1):
            wrapped = wrap(f"{i}. {s}", width)
            for j, w in enumerate(wrapped):
                self.text(x + (0 if j == 0 else 3.2), y, w, size=size)
                y -= 3.3
            if ref:
                self.text(x + 3.2, y + 0.3, ref, size=4.8, color=SCHEM)
                y -= 3.0
            y -= 0.8
        return y

    def schematic_stamp(self, x, y, s="SCHEMATIC — NOT TO SCALE"):
        self.text(x, y, s, size=6.5, color=SCHEM, weight="bold")

    # title block --------------------------------------------------------------
    def title_block(self, sid, title, scale, n, total, posts):
        x0, y0, w, h = PAGE_W - 10 - 128, 10, 128, 44
        a = self.ax
        a.add_patch(Rectangle((x0, y0), w, h, fc=BG, ec=LINE, lw=0.8, zorder=6))
        for yy in (y0 + 30, y0 + 20, y0 + 10):
            self.line([x0, x0 + w], [yy, yy], lw=0.4, z=7)
        self.line([x0 + 96, x0 + 96], [y0 + 20, y0 + 30], lw=0.4, z=7)
        self.line([x0 + 64, x0 + 64], [y0, y0 + 10], lw=0.4, z=7)
        t = lambda xx, yy, s, **k: a.text(xx, yy, s, color=k.pop("color", LINE), zorder=8, **k)
        t(x0 + 2, y0 + 39.5, "HASBRO 1984 PROTON PACK MODDING", fontsize=6.2, weight="bold", va="center")
        t(x0 + 2, y0 + 34, "GBFans.com community guide · drawn from forum-reported measurements",
          fontsize=4.8, va="center", color=SCHEM)
        t(x0 + 2, y0 + 25, title.upper(), fontsize=8.6, weight="bold", va="center")
        t(x0 + 98, y0 + 27.2, "SHEET", fontsize=4.5, color=SCHEM, va="center")
        t(x0 + 98, y0 + 23, f"{sid}  ({n} of {total})", fontsize=7, weight="bold", va="center")
        # legend
        t(x0 + 2, y0 + 17, "SOURCED", fontsize=5.2, weight="bold", va="center")
        t(x0 + 22, y0 + 17, "DERIVED", fontsize=5.2, weight="bold", va="center", color=DERIVED,
          fontstyle="italic")
        t(x0 + 42, y0 + 17, "- - SCHEMATIC", fontsize=5.2, weight="bold", va="center", color=SCHEM)
        t(x0 + 70, y0 + 17, "pN = forum post number", fontsize=5.2, va="center", color=SCHEM)
        srcs = "Source: thread 219236, posts " + ", ".join(f"#{p}" for p in posts)
        t(x0 + 2, y0 + 12.6, srcs, fontsize=4.8, va="center", color=SCHEM)
        t(x0 + 2, y0 + 6.5, f"SCALE  {scale}", fontsize=6, weight="bold", va="center")
        t(x0 + 2, y0 + 2.6, "Dimensions in mm unless noted", fontsize=4.6, va="center", color=SCHEM)
        t(x0 + 66, y0 + 6.5, f"v{VERSION} · {date(2026, 11, 2).isoformat()}", fontsize=5.4, va="center")
        t(x0 + 66, y0 + 2.6, "Drawn: ryan-brumback · not a Hasbro drawing", fontsize=4.6, va="center",
          color=SCHEM)
        # footer disclaimer
        self.text(12, 12.5, "Builder-reported values from GBFans.com. Check against your own pack before "
                  "cutting or drilling. Attribution and forum photos: docs/RENDERINGS.md", size=4.8, color=SCHEM)


def wrap(s, width):
    words, out, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        out.append(cur)
    return out


def tag(posts):
    return "Source: " + ", ".join(f"post #{p} ({dd.AUTHORS.get(p, '')})" for p in posts)


# ---------------------------------------------------------------------- sheets

def s1_emitter(S: Sheet):
    k = 3.0                                    # drawing scale 3:1
    od, idd, L, ins = (dim(x)[0] for x in ("tube_od", "tube_id", "tube_len", "insert_len"))
    wall = (od - idd) / 2
    x0, y0 = 30, 125
    S.view_label(x0 + L * k / 2, 196, "SECTION A–A  ·  ASSEMBLED TUBE", "scale 3:1")
    # caps (schematic)
    capw = 4 * k
    for xc in (x0 - capw, x0 + L * k):
        S.rect(xc, y0 - 1.5, capw, od * k + 3, color=SCHEM, ls=(0, (3, 2)), lw=0.6)
    S.callout(x0 - capw / 2, y0 + od * k + 1.5, x0 - 14, y0 + od * k + 24, "Original cap, reused (not dimensioned)",
              color=SCHEM)
    # tube walls
    S.rect(x0, y0, L * k, wall * k, hatch="////", lw=0.7)
    S.rect(x0, y0 + (od - wall) * k, L * k, wall * k, hatch="////", lw=0.7)
    S.line([x0, x0 + L * k], [y0, y0], lw=1.0)
    S.line([x0, x0 + L * k], [y0 + od * k, y0 + od * k], lw=1.0)
    # insert
    S.rect(x0 + 0.0, y0 + wall * k, ins * k, idd * k, hatch="..", color=LINE, lw=0.6)
    S.callout(x0 + ins * k * 0.45, y0 + od * k / 2, x0 + 30, y0 - 17, "Original black insert, reused  (flexible, polyurethane-like)  p23")
    S.centerline(x0 - capw - 4, y0 + od * k / 2, x0 + L * k + capw + 4, y0 + od * k / 2)
    # glue beads
    for xg in (x0, x0 + L * k):
        for yg in (y0 + od * k, y0):
            S.ax.add_patch(Polygon([[xg - 1.6, yg], [xg + 1.6, yg], [xg, yg + (2.2 if yg > y0 else -2.2)]],
                                   color=DERIVED if False else LINE, zorder=5))
    S.callout(x0 + L * k, y0 + od * k + 2.2, x0 + L * k + 14, y0 + od * k + 24, "Superglue bead at each end  p32")
    # dims
    S.dim_h(x0, x0 + L * k, y0 + od * k + 12, "tube_len", ext_from=(y0 + od * k, y0 + od * k))
    S.dim_h(x0, x0 + ins * k, y0 - 9, "insert_len", ext_from=(y0, y0), above=False)
    S.dim_v(x0 + L * k + capw + 9, y0, y0 + od * k, "tube_od", ext_from=(x0 + L * k, x0 + L * k), prefix="Ø")
    S.dim_v(x0 - capw - 9, y0 + wall * k, y0 + (od - wall) * k, "tube_id", ext_from=(x0, x0), prefix="Ø",
            right=False)
    # play
    S.text(x0 + ins * k + 0.5, y0 + od * k / 2 + 2, fmt("tube_play"), size=6.2, color=DERIVED, fontstyle="italic")
    S.text(x0 + ins * k + 0.5, y0 + od * k / 2 - 2.6, "play", size=4.8, color=DERIVED)

    # end view, 3:1
    cx, cy = 168, 160
    S.view_label(cx, 196, "END VIEW · TUBE", "scale 3:1")
    S.circle(cx, cy, od * k / 2, lw=1.0)
    S.circle(cx, cy, idd * k / 2, lw=0.8)
    S.ax.add_patch(Circle((cx, cy), od * k / 2, fill=False, hatch="////", ec=LINE, lw=0, zorder=1))
    S.ax.add_patch(Circle((cx, cy), idd * k / 2, color=BG, zorder=1.5))
    S.centerline(cx - 26, cy, cx + 26, cy)
    S.centerline(cx, cy - 26, cx, cy + 26)
    S.callout(cx + od * k / 2 * 0.7, cy + od * k / 2 * 0.7, cx + 32, cy + 22, "")
    S.label(cx + 33, cy + 22.5, "tube_od", prefix="Ø", ha="left")
    S.callout(cx - idd * k / 2 * 0.7, cy - idd * k / 2 * 0.7, cx - 32, cy - 22, "", ha="right")
    S.label(cx - 33, cy - 21.5, "tube_id", prefix="Ø", ha="right")
    S.text(cx, cy - 31, "Clear acrylic tube", size=6.2, ha="center")

    # rejected sizes, drawn at 1.5:1 beside the size that worked
    kr = 1.5
    S.view_label(238, 196, "SIZES THAT DID NOT WORK", "scale 1.5:1 · dashed = size that worked")
    S.circle(222, 165, 11 * kr / 2, color=REJECT, lw=0.9)
    S.circle(222, 165, 12 * kr / 2, color=LINE, lw=0.5, ls=(0, (2, 1.5)))
    S.circle(254, 165, 15 * kr / 2, color=REJECT, lw=0.9)
    S.circle(254, 165, 14 * kr / 2, color=LINE, lw=0.5, ls=(0, (2, 1.5)))
    for (cx2, key, txt) in ((222, "tube_reject_id", "ID too small for\nthe inserts (need Ø12)"),
                            (254, "tube_reject_od", "OD too big for the\nlid housing (Ø14 fits)")):
        S.text(cx2, 150, f"Ø{dim(key)[0]:g} " + ("ID" if key.endswith("id") else "OD"),
               size=7, color=REJECT, ha="center", weight="bold")
        S.text(cx2, 146.5, refs(key), size=4.6, color=REJECT, ha="center")
        S.text(cx2, 143, txt, size=5.2, color=REJECT, ha="center", va="top", linespacing=1.2)

    # notes
    S.notes(18, 92, "PROCEDURE", [
        ("Free the caps: clamp the middle of each stock tube with locking pliers and squeeze it oval. "
         "The glue seal breaks and the caps pop off. The clear tubes are sacrificed; caps and inserts survive.",
         tag([23])),
        (f"Buy clear acrylic tube {fmt('tube_od', 'Ø')} OD × {fmt('tube_id', 'Ø')} ID. gbrich bought "
         f"{fmt('tube_stock')} mm, enough for the four tubes plus spares.", tag([23])),
        (f"Cut to {fmt('tube_len')} mm: the insert is {fmt('insert_len')} mm long without its nub, leaving "
         f"{fmt('tube_play')} mm of play. A {fmt('saw_blade')} fine-cut mitre saw gave square ends; a junior "
         "hacksaw struggled.", tag([23, 32])),
        ("Glue a cap to one end, slide the insert in from the other end, then glue that end into the lid. "
         "The rebuilt tubes no longer twist-lock.", tag([32])),
    ], width=78)
    S.notes(148, 92, "NOTES", [
        ("The black inserts and caps can be painted before assembly (gbrich: copper inserts, chrome caps).",
         tag([23, 32])),
        ("mcspain also rebuilt his tubes from acrylic and discarded about half of his cuts. Allow spare tube.",
         tag([81])),
        ("Cap geometry is not documented and is drawn schematically.", None),
    ], width=56)


def s2_spacer(S: Sheet):
    k = 3.0
    od, idd, t = (dim(x)[0] for x in ("sp_od", "sp_id", "sp_t"))
    cx, cy = 60, 150
    S.view_label(cx, 196, "PLAN VIEW", "scale 3:1")
    S.circle(cx, cy, od * k / 2, lw=1.0)
    S.circle(cx, cy, idd * k / 2, lw=0.9)
    S.centerline(cx - 38, cy, cx + 38, cy)
    S.centerline(cx, cy - 38, cx, cy + 38)
    S.dim_h(cx - od * k / 2, cx + od * k / 2, cy - od * k / 2 - 10, "sp_od", prefix="Ø",
            ext_from=(cy, cy), above=False)
    S.dim_h(cx - idd * k / 2, cx + idd * k / 2, cy + od * k / 2 + 6, "sp_id", prefix="Ø",
            ext_from=(cy, cy))

    sx, sy = 120, 145
    S.view_label(sx + od * k / 2, 196, "SECTION B–B", "scale 3:1")
    w_ring = (od - idd) / 2 * k
    S.rect(sx, sy, w_ring, t * k, hatch="////", lw=0.9)
    S.rect(sx + w_ring + idd * k, sy, w_ring, t * k, hatch="////", lw=0.9)
    S.line([sx + w_ring, sx + w_ring + idd * k], [sy, sy], color=SCHEM, lw=0.3, ls=(0, (2, 2)))
    S.line([sx + w_ring, sx + w_ring + idd * k], [sy + t * k, sy + t * k], color=SCHEM, lw=0.3, ls=(0, (2, 2)))
    S.centerline(sx + od * k / 2, sy - 8, sx + od * k / 2, sy + t * k + 8)
    S.dim_v(sx + od * k + 8, sy, sy + t * k, "sp_t", ext_from=(sx + od * k, sx + od * k))
    S.dim_h(sx, sx + od * k, sy - 10, "sp_od", prefix="Ø", ext_from=(sy, sy), above=False)
    S.text(sx, sy + t * k + 18, "Printed in PLA by gbrich; rubber washers or other spacers also work  p68",
           size=6.2)

    # stack-up schematic
    S.view_label(205, 122, "WHY IT'S NEEDED")
    S.schematic_stamp(178, 115)
    bx, by = 172, 80
    for (lbl, x) in (("BEFORE", bx), ("AFTER", bx + 52)):
        S.text(x + 10, by + 24, lbl, size=6.5, weight="bold", ha="center")
        S.rect(x, by, 20, 6, hatch="xx", color=SCHEM, lw=0.6)               # board/mount
        S.text(x + 22, by + 2, "board + mount", size=4.8, color=SCHEM)
        spacer = 3 if lbl == "AFTER" else 0
        S.rect(x + 3, by + 6, 14, 1.4, color=SCHEM, lw=0.6)                  # washer
        if spacer:
            S.rect(x + 3, by + 7.4, 14, 3, hatch="////", lw=0.7)
            S.text(x + 22, by + 8.4, "3 mm spacer", size=4.8)
        top = by + 7.4 + spacer
        S.rect(x + 7.5, by - 8, 5, top - by + 8 + (0 if spacer else 3), color=SCHEM, lw=0.6)  # bolt shank
        S.rect(x + 5, by - 11, 10, 3, color=SCHEM, lw=0.6)                   # head
        if not spacer:
            S.arrow(x + 15, top + 3, x + 15, top, color=REJECT, style="<|-|>", ms=4, lw=0.5)
            S.text(x + 16.5, top + 0.3, "~3 mm too long\nboard won't close", size=4.6, color=REJECT)
        else:
            S.text(x + 2, top + 2.2, "end sits flush", size=4.8)
    S.notes(18, 92, "NOTES", [
        ("With Redman's 1984 ALICE frame mounting kit, the bolts were about 3 mm too long for the "
         "aluminum motherboard to close flush.", tag([68])),
        ("gbrich considered grinding the bolt ends, reversing the bolts, or spacers. He printed these "
         "spacers and fitted them under the outer washers.", tag([68])),
        ("The stack-up diagram shows the principle only. Hardware shapes are not documented.", None),
    ], width=70)


def s3_neck(S: Sheet):
    k = 1.0
    idd, wall, od, skin = (dim(x)[0] for x in ("np_id", "np_wall", "np_od", "np_skin"))
    cx, cy = 52, 145
    S.view_label(cx, 196, "SECTION · NECK PAD", "scale 1:1")
    S.circle(cx, cy, (od + 2 * skin) * k / 2, lw=1.0, fill=True, fc="#0e2f57")
    S.ax.add_patch(Circle((cx, cy), od * k / 2, fill=True, fc=BG, hatch="..", ec=LINE, lw=0.8, zorder=2.5))
    S.circle(cx, cy, idd * k / 2, lw=0.9, fill=True, fc=BG, z=3)
    S.centerline(cx - 34, cy, cx + 34, cy)
    S.centerline(cx, cy - 34, cx, cy + 34)
    S.dim_h(cx - idd * k / 2, cx + idd * k / 2, cy + 2, "np_id", prefix="Ø")
    S.dim_h(cx - od * k / 2, cx + od * k / 2, cy - od * k / 2 - 14, "np_od", prefix="Ø",
            ext_from=(cy - 2, cy - 2), above=False)
    S.dim_h(cx - (od + 2 * skin) * k / 2, cx + (od + 2 * skin) * k / 2, cy + (od + 2 * skin) * k / 2 + 6,
            "np_od_total", prefix="Ø", ext_from=(cy + 2, cy + 2))
    S.dim_v(cx + od * k / 2 + 12, cy + idd * k / 2, cy + od * k / 2, "np_wall",
            ext_from=(cx + 4, cx + od * k / 2 * 0.5))
    S.callout(cx + (od + skin) * k / 2 * 0.71, cy + (od + skin) * k / 2 * 0.71, cx + 30, cy + 40,
              f"{fmt('np_skin')} mm adhesive neoprene / foam sheet  p73")
    S.callout(cx + od * k / 2 * 0.6, cy - od * k / 2 * 0.6, cx + 30, cy - 40, "Grey pipe insulation  p73")

    # flat pattern, 1:1
    fx, fy, fw, fh = 102, 128, dim("np_circ")[0], 40
    S.view_label(fx + fw / 2, 196, "COVERING · FLAT PATTERN", "scale 1:1 (print at 100%)")
    S.rect(fx, fy, fw, fh, lw=1.0)
    for xx in (fx + fw * 0.33, fx + fw * 0.66):
        S.line([xx - 2, xx + 2], [fy + fh + 2, fy - 2], color=SCHEM, lw=0.4)
    S.dim_h(fx, fx + fw, fy + fh + 7, "np_circ", ext_from=(fy + fh, fy + fh))
    S.text(fx + fw / 2, fy + fh / 2, "LENGTH: TO SUIT YOUR FRAME (not documented)", size=6.2, ha="center",
           va="center", color=SCHEM)
    S.text(fx, fy - 6, "Width = π × (48 + 3) = 160.2 mm, measured at the sheet's mid-thickness. "
           "Add a small overlap if you butt-join with adhesive.", size=5.6, color=DERIVED, fontstyle="italic")
    S.text(fx, fy - 10.5, "gbrich shared his own measurement template for any tube diameter (see RENDERINGS.md).",
           size=5.6, color=SCHEM)
    S.notes(18, 92, "NOTES", [
        ("Core: grey pipe insulation, 22 mm ID, 13 mm wall (48 mm OD). Covering: 3 mm black adhesive "
         "neoprene/foam sheet cut to fit.", tag([73])),
        ("After a full day at MCM Comic Con London the top nut of the ALICE frame still dug in through "
         "two layers of 3 mm padding. Plan for more.", tag([88])),
        ("On gbrich's pack stand, 3 mm neoprene pads took indents from the pack (the pack was unmarked); he may switch to 3 mm felt.", tag([91])),
    ], width=70)


def s4_bnc(S: Sheet):
    S.view_label(80, 196, "CABLE END · BEFORE AND AFTER")
    S.schematic_stamp(46, 186)
    y = 150
    # before
    S.text(30, y + 24, "STOCK", size=6.5, weight="bold")
    S.rect(30, y, 60, 12, color=SCHEM, ls=(0, (3, 2)), fill=True, fc="#0e2f57")
    S.rect(90, y - 1, 10, 14, color=SCHEM, ls=(0, (3, 2)))
    S.text(91, y + 15, "molded end", size=5.2, color=SCHEM)
    S.line([90, 90], [y - 4, y + 16], color=REJECT, lw=0.9, ls=(0, (4, 2)))
    S.text(88, y - 7, "slice off here", size=5.2, color=REJECT, ha="right")
    # after
    y2 = 105
    S.text(30, y2 + 24, "MODIFIED", size=6.5, weight="bold")
    S.rect(30, y2, 60, 12, color=SCHEM, ls=(0, (3, 2)), fill=True, fc="#0e2f57")
    S.rect(72, y2 + 3.25, 18, 5.5, hatch="////", lw=0.7)
    S.text(70, y2 + 6, "bore", size=5.2, ha="right", va="center")
    S.rect(84, y2 + 3.5, 24, 5, color=LINE, lw=0.8)
    S.rect(108, y2 + 1, 10, 10, color=LINE, lw=0.8)
    S.text(110, y2 + 15, "metal BNC connector", size=5.2)
    S.dim_v(124, y2 + 3.25, y2 + 8.75, "bnc_bore", prefix="Ø", ext_from=(108, 108))
    S.notes(150, 175, "OPTIONS", [
        (f"Drill {fmt('bnc_bore', 'Ø')} into the cable stub: the connector pushes in and holds by friction, "
         "no glue needed.", tag([12])),
        (f"Drill {fmt('bnc_bore_alt', 'Ø')} if that's the bit you have, and glue the connector in.", tag([12])),
        ("Slice the molded ends off with a scalpel blade first. gbrich bought a pack of 10 connectors "
         "for about £5.", tag([12])),
        ("Bore depth, cable diameter and connector sizes are not documented: proportions here are illustrative.",
         None),
    ], width=60)


def s5_ion_arm(S: Sheet):
    S.view_label(90, 196, "ION ARM END CAP · SIDE VIEW")
    S.schematic_stamp(55, 186)
    x0, y0 = 40, 120
    S.rect(x0, y0, 90, 26, color=SCHEM, ls=(0, (3, 2)), lw=0.7)     # ion arm body
    S.text(x0 + 30, y0 + 11, "ion arm (stock plastic)", size=5.6, color=SCHEM)
    S.rect(x0 + 90, y0 - 2, 22, 30, lw=0.9)                          # end cap
    S.text(x0 + 101, y0 + 32, "end cap\n(push fit, can fall off)", size=5.4, ha="center", linespacing=1.2)
    for yy in (y0 + 6, y0 + 20):
        S.circle(x0 + 101, yy, 2.4, color=SCHEM, lw=0.6)               # molded fake bolt heads
    # bolts drawn going into the arm, horizontally
    for yy in (y0 + 6, y0 + 20):
        S.rect(x0 + 101 - 22, yy - 0.9, 22, 1.8, hatch="////", lw=0.6)
        S.rect(x0 + 101, yy - 1.8, 2.2, 3.6, lw=0.6, fill=True, fc=BG)
    S.dim_h(x0 + 79, x0 + 103.2, y0 - 12, "ia_bolt_len", ext_from=(y0 + 5, y0 + 5), above=False)
    S.callout(x0 + 101, y0 + 20, x0 + 140, y0 + 40, f"Ø{dim('ia_hole')[0]:g} hole through the center of each "
              "molded fake bolt, into the arm  p73")
    S.callout(x0 + 88, y0 + 24, x0 + 140, y0 + 50, "Remove the top rear silver screw: it blocks the hole  p73")
    S.notes(18, 85, "PROCEDURE", [
        (f"Drill two {fmt('ia_hole', 'Ø')} mm holes through the centers of the two molded fake bolts on the end "
         "cap, into the ion arm.", tag([73])),
        (f"Fit two M3 × {fmt('ia_bolt_len')} mm bolts. Remove the top rear silver screw first.", tag([73])),
        ("Alternative: an aluminum ion arm (GBFans shop).", tag([73])),
        ("Positions and proportions are illustrative; only the hole and bolt sizes are documented.", None),
    ], width=80)


def s6_hga(S: Sheet):
    S.view_label(130, 196, "HGA REMOVAL · nomake-wan's non-destructive method")
    S.schematic_stamp(100, 186)
    panels = [(20, "1  Remove the 2 bracket screws"),
              (82, "2  Blade under bracket, sharp edge up"),
              (144, "3  Draw blade up the curve; lift bracket"),
              (206, "4  Rotate 30°, slide out")]
    cy = 140
    for i, (x, cap) in enumerate(panels, 1):
        S.rect(x, 100, 56, 78, color=SCHEM, lw=0.5)
        S.text(x + 3, 172, cap, size=5.6, weight="bold")
        hx = x + 28
        # HGA body: rounded cylinder seen end-on as circle with bracket arc
        S.circle(hx, cy, 13, lw=0.9)
        S.circle(hx, cy, 4, color=SCHEM, lw=0.5)
        if i < 4:
            S.ax.add_patch(Arc((hx, cy), 31, 31, theta1=20, theta2=160, ec=LINE, lw=2.2, zorder=3))  # bracket
            for ang in (20, 160):
                a = math.radians(ang)
                S.circle(hx + 15.5 * math.cos(a), cy + 15.5 * math.sin(a), 1.4,
                         color=REJECT if i == 1 else LINE, lw=0.7, fill=i != 1, fc=LINE)
        if i == 1:
            for ang in (20, 160):
                a = math.radians(ang)
                S.arrow(hx + 15.5 * math.cos(a), cy + 15.5 * math.sin(a) + 9, hx + 15.5 * math.cos(a),
                        cy + 15.5 * math.sin(a) + 2, color=REJECT, ms=5)
            S.text(hx, 112, "screws out", size=5.2, color=REJECT, ha="center")
        if i == 2:
            S.line([hx - 24, hx - 6], [cy + 9, cy + 13.5], color=REJECT, lw=1.4)
            S.arrow(hx - 24, cy + 9, hx - 9, cy + 12.7, color=REJECT, ms=6)
            S.text(hx, 112, "push until it bottoms out", size=5.2, color=REJECT, ha="center")
        if i == 3:
            S.ax.add_patch(Arc((hx, cy), 29, 29, theta1=110, theta2=165, ec=REJECT, lw=1.2, zorder=4))
            S.arrow(hx - 9.3, cy + 11.1, hx - 3, cy + 14.2, color=REJECT, ms=6)
            S.arrow(hx, cy + 19, hx, cy + 27, color=LINE, ms=6)
            S.text(hx, 112, "cuts the superglue (expect pops)", size=5.2, color=REJECT, ha="center")
        if i == 4:
            for ang in (0, 120, 240):
                a = math.radians(ang)
                S.rect(hx + 13 * math.cos(a) - 1.5, cy + 13 * math.sin(a) - 1.5, 3, 3, lw=0.6, fill=True, fc=LINE)
            S.ax.add_patch(Arc((hx, cy), 40, 40, theta1=0, theta2=30, ec=REJECT, lw=1.0, zorder=4))
            S.arrow(hx + 19.3, cy + 5.2, hx + 17.3, cy + 10, color=REJECT, ms=6)
            S.label(hx + 23, cy + 9, "hga_rot", ha="left")
            S.text(hx, 112, "tabs line up with the slots", size=5.2, color=REJECT, ha="center")
    S.notes(18, 88, "NOTES", [
        ("Use a thin safety blade (nomake-wan used the one from a Tamiya basic tool set). Worked on both a HasLab "
         "and a 1984 pack with no damage to the HGA or bracket.", tag([27])),
        ("Once unscrewed, a pry tool can also pop the glue off the band around the HGA.", tag([21])),
        ("Remove the HGA before cutting off the fake bolts: the cut is much cleaner.", tag([29])),
        ("mcspain found the twist lock holds the HGA firmly even without the bracket.", tag([81])),
        ("The HGA, bracket and tab positions are drawn schematically. See nomake-wan's photos for the blade position.",
         None),
    ], width=96)


def s7_drill(S: Sheet):
    S.view_label(120, 196, "HOLE SIZES AT TRUE SIZE", "scale 1:1 — print at 100% and check the 50 mm bar")
    # scale bar
    S.rect(20, 18.5, 50, 2, fill=True, fc=LINE, lw=0.5)
    for i in range(0, 51, 10):
        S.line([20 + i, 20 + i], [17, 22], lw=0.5)
    S.text(45, 23.5, "50 mm check bar", size=5.2, ha="center")
    holes = [
        ("cake_screw", "M2.5 screws: cake lid window", "screw"),
        ("clamp_holes", "C&A ribbon cable clamp: 2 new holes", "hole"),
        ("ia_hole", "Ion arm end cap: 2 holes for M3 × 20", "hole"),
        ("rivet_bolt", "M3 bolts + nuts in place of rivets", "screw"),
        ("banjo_hole", "Wand wing, Mack's banjo screw (4–4.5)", "hole"),
        ("speaker_holes", "Aluminum board over speaker: 7 holes", "hole"),
        ("bnc_bore", "BNC into cable stub: friction fit", "hole"),
        ("bnc_bore_alt", "BNC into cable stub: with glue", "hole"),
        ("bolt_m6", "Real bolts on the HGA (originals 1/4-20)", "screw"),
        ("toggle_holes", "Dummy toggle switches in cyclotron", "hole"),
        ("redman_shell", "Redman shell bolts, per instructions (5/16\")", "hole"),
        ("legris_hole", "Brass elbows / Legris (stepped from 8)", "hole"),
    ]
    cols = [(22, 172), (110, 172), (198, 172)]
    for i, (key, what, kind) in enumerate(holes):
        c = i // 4
        r = i % 4
        x, ytop = cols[c]
        y = ytop - r * 34
        d = dim(key)[0]
        cx = x + 8
        S.circle(cx, y, d / 2, lw=0.7, hatch=None)
        S.centerline(cx - d / 2 - 3, y, cx + d / 2 + 3, y)
        S.centerline(cx, y - d / 2 - 3, cx, y + d / 2 + 3)
        lab = (f"M{d:g}" if kind == "screw" else f"Ø{d:g} mm")
        if key == "redman_shell":
            lab = "Ø7.94 mm (5/16\")"
        S.text(x + 18, y + 4, lab, size=8, weight="bold")
        for j, w in enumerate(wrap(what, 34)):
            S.text(x + 18, y - 0.5 - j * 3.4, w, size=5.6)
        S.text(x + 18, y - 4.5 - (len(wrap(what, 34)) - 1) * 3.4,
               ", ".join(f"post #{p}" for p in dim(key)[2]), size=4.8, color=SCHEM)
    yy = 44
    for para in ("Pilot holes for the M6 bolts: slightly smaller than the bolt shank so the bolt threads into the "
                 "plastic (exact bit not recorded, post #22).",
                 "Cosmetic Redman shell bolts: start small and enlarge until the bolt threads in snugly; only one "
                 "bolt per bracket is structural (post #68)."):
        for w in wrap(para, 92):
            S.text(22, yy, w, size=5.6)
            yy -= 3.4
        yy -= 1.5


SHEET_FUNCS = {"S1": (s1_emitter, "3:1"), "S2": (s2_spacer, "3:1"), "S3": (s3_neck, "1:1"),
               "S4": (s4_bnc, "NOT TO SCALE"), "S5": (s5_ion_arm, "NOT TO SCALE"),
               "S6": (s6_hga, "NOT TO SCALE"), "S7": (s7_drill, "1:1")}


# ----------------------------------------------------------------- attribution

def write_renderings_md(files):
    L = [
        "# Renderings and attribution",
        "",
        "Generated by `tools/make_drawings.py` from [`tools/drawing_data.py`](../tools/drawing_data.py). "
        "Every value on every sheet is listed here with the post it comes from, and each sheet links to the "
        "forum photos that show the same part, so you can compare the drawing with the real thing.",
        "",
        "**Rules:** a value is drawn only if a post states it (**sourced**) or it is calculated from sourced "
        "values (**derived**, shown in light blue italics with the calculation). Shapes and positions that "
        "nobody documented are drawn dashed and stamped **schematic — not to scale**. Forum photos are "
        "linked, not copied, and remain the property of the members who posted them.",
        "",
        "**Printing:** [`drawings/blueprints.pdf`](drawings/blueprints.pdf) is US Letter landscape. Print at "
        "100% (no fit-to-page). Sheet S7 has a 50 mm check bar.",
        "",
    ]
    for (sid, stem, title, photo_posts, keys), n in zip(dd.SHEETS, range(1, len(dd.SHEETS) + 1)):
        scale = SHEET_FUNCS[sid][1]
        L += [f"## {sid}. {title}", "", f"![{title}](drawings/{stem}.png)", "",
              f"Scale: {scale}. Files: [PNG](drawings/{stem}.png) · [SVG](drawings/{stem}.svg)", "",
              "| Value | Status | Source | Note |", "|---|---|---|---|"]
        for key in keys:
            v, unit, posts, status, note = dim(key)
            src = ", ".join(f"[post #{p}]({dd.post_url(p)}) ({dd.AUTHORS.get(p, '')})" for p in posts)
            u = {"mm": " mm", "deg": "°", "pcs": "", "teeth": "-tooth"}.get(unit, unit)
            L.append(f"| {v:g}{u} | {status} | {src} | {note} |")
        L += ["", "**Compare with the forum photos:**", ""]
        any_photo = False
        for p in sorted(dd.PHOTOS):
            for url, cap, sheet in dd.PHOTOS[p]:
                if sheet != sid:
                    continue
                L.append(f"- [{cap}]({url}) — [post #{p}]({dd.post_url(p)}), {dd.AUTHORS.get(p, '')}")
                any_photo = True
        if not any_photo:
            L.append("- No photos of this step were posted.")
        L.append("")
    (ROOT / "docs" / "RENDERINGS.md").write_text("\n".join(L), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = len(dd.SHEETS)
    files = []
    with PdfPages(OUT / "blueprints.pdf") as pdf:
        for n, (sid, stem, title, photo_posts, keys) in enumerate(dd.SHEETS, 1):
            func, scale = SHEET_FUNCS[sid]
            posts = sorted({p for k in keys for p in dim(k)[2]} | set(photo_posts))
            S = Sheet(sid, title, scale, n, total, posts)
            func(S)
            S.fig.savefig(OUT / f"{stem}.png", dpi=200, facecolor=BG)
            S.fig.savefig(OUT / f"{stem}.svg", facecolor=BG)
            pdf.savefig(S.fig, facecolor=BG)
            plt.close(S.fig)
            files.append(stem)
            print(f"{sid} {stem}")
    write_renderings_md(files)
    print("wrote docs/RENDERINGS.md and docs/drawings/blueprints.pdf")


if __name__ == "__main__":
    main()
