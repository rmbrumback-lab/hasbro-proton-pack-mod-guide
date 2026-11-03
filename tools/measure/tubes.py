"""Measure the width of coloured tubes (hoses) along their length.

The tube is segmented by colour, skeletonised, and at every skeleton point on a
locally straight run its width is measured on an intensity profile perpendicular
to the local direction (half-maximum edges on the saturation channel, see
profile.py). Returns per-point widths with positions, so straight, unobscured
runs can be selected and averaged.

    from tubes import tube_widths
    rows = tube_widths(img_path, colour="red", roi=(x0, y0, x1, y1))
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image
from skimage.morphology import skeletonize, remove_small_objects

from profile import chan, one


def colour_mask(rgb, colour):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(axis=2)
    sat = (mx - rgb.min(axis=2)) / np.maximum(mx, 1)
    if colour == "red":
        return (r > 90) & (r > 1.8 * g) & (r > 1.8 * b) & (sat > 0.45)
    if colour == "blue":
        return (b > 70) & (b > 1.4 * r) & (b > 1.2 * g) & (sat > 0.4)
    raise ValueError(colour)


def tube_widths(path, colour, roi, spacing=4, straight_px=14, max_bend_deg=8, half=None):
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(float)
    x0, y0, x1, y1 = roi
    m = np.zeros(rgb.shape[:2], bool)
    m[y0:y1, x0:x1] = colour_mask(rgb[y0:y1, x0:x1], colour)
    m = remove_small_objects(m, 200)
    sk = skeletonize(m)
    ys, xs = np.nonzero(sk)
    pts = np.c_[xs, ys].astype(float)
    a = chan(rgb, "sat")
    out = []
    used = np.zeros(len(pts), bool)
    for i in range(0, len(pts), 1):
        if used[i]:
            continue
        p = pts[i]
        d2 = ((pts - p) ** 2).sum(1)
        near = pts[d2 < straight_px ** 2]
        used[d2 < spacing ** 2] = True
        if len(near) < straight_px:          # end of tube or junction
            continue
        c = near.mean(0)
        u, s, vt = np.linalg.svd(near - c)
        if s[1] / max(s[0], 1e-6) > math.tan(math.radians(max_bend_deg)):
            continue                          # not straight here
        d = vt[0]
        n = np.array([-d[1], d[0]])
        hw = half or 40
        w, e = one(a, tuple(c - hw * n), tuple(c + hw * n), close=6)
        if not math.isnan(w):
            out.append((c[0], c[1], w, math.degrees(math.atan2(d[1], d[0]))))
    return np.array(out)
