"""Outer silhouette of a bright part on a dark background, by radial scanning.

For each angle, the profile from an interior centre point outwards is sampled
and the silhouette edge is the first point beyond `r_min` where the next `win_px`
pixels are less than `frac` bright, so thin dark detail inside the part and thin
bright mat grid lines outside it are both ignored. The edge is
refined to sub-pixel at the half-way level between the local inside and outside
brightness. Returns an (N, 3) array of x, y, angle_deg.
"""
import math

import numpy as np
from PIL import Image

from mat import bil


def radial_edges(path, centre, r_max, thr=120, run=6, step=0.5, n_angles=720, r_min=0, win_px=20, frac=0.25):
    a = np.asarray(Image.open(path).convert("L")).astype(float)
    cx, cy = centre
    out = []
    for k in range(n_angles):
        th = 2 * math.pi * k / n_angles
        dx, dy = math.cos(th), math.sin(th)
        rs = np.arange(0, r_max, step)
        prof = np.array([bil(a, cx + r * dx, cy + r * dy) for r in rs])
        if np.isnan(prof).any():
            good = ~np.isnan(prof)
            rs, prof = rs[good], prof[good]
        bright = prof > thr
        need = int(run / step)
        win = int(win_px / step)
        # first position (after r_min) where the window ahead is mostly dark
        j = None
        i0 = int(r_min / step)
        for i in range(i0, len(bright) - win):
            if bright[i] and not bright[i + 1] and bright[i + 1:i + 1 + win].mean() < frac:
                j = i
                break
        if j is None:
            continue
        inside = np.median(prof[max(0, j - need):j + 1])
        outside = np.median(prof[j + 1:j + 1 + need]) if j + 1 < len(prof) else 0
        t = (inside + outside) / 2
        # find crossing near j
        r_edge = rs[j]
        for i in range(j, min(len(prof) - 1, j + need)):
            if prof[i] >= t > prof[i + 1]:
                r_edge = rs[i] + (prof[i] - t) / (prof[i] - prof[i + 1]) * step
                break
        out.append((cx + r_edge * dx, cy + r_edge * dy, math.degrees(th)))
    return np.array(out)
