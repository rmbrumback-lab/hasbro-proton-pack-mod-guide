"""Measure a feature's width in pixels from an intensity profile across it.

A line is sampled between two points that cross the feature. Edges are found as
gradient extrema, refined to sub-pixel by a parabola through the peak, and the
measurement is repeated on parallel lines offset along the feature so the
result has a spread, not just a single value.

    from profile import width
    w = width(img, (x1, y1), (x2, y2), channel="L", offsets=range(-6, 7, 2))
    -> dict(mean, sd, n, each=[...], edges=[(a, b), ...])

channel: "L" luminance, "R"/"G"/"B", or "sat" (saturation, good for red/blue hoses
on a dark background).
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image


def load(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(float)


def chan(img, channel):
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    if channel == "L":
        return 0.299 * r + 0.587 * g + 0.114 * b
    if channel == "sat":
        mx, mn = img.max(axis=2), img.min(axis=2)
        return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1) * 255, 0)
    return {"R": r, "G": g, "B": b}[channel]


def sample(a, x, y):
    """Bilinear sample of 2-D array a at float coords."""
    x0, y0 = int(math.floor(x)), int(math.floor(y))
    dx, dy = x - x0, y - y0
    h, w = a.shape
    x0, y0 = min(max(x0, 0), w - 2), min(max(y0, 0), h - 2)
    return (a[y0, x0] * (1 - dx) * (1 - dy) + a[y0, x0 + 1] * dx * (1 - dy)
            + a[y0 + 1, x0] * (1 - dx) * dy + a[y0 + 1, x0 + 1] * dx * dy)


def sub_peak(v, i):
    if 0 < i < len(v) - 1:
        a, b, c = v[i - 1], v[i], v[i + 1]
        den = a - 2 * b + c
        if den != 0:
            return i + 0.5 * (a - c) / den
    return float(i)


def halfmax(prof, step, close=6):
    """Outer edges of the region around the profile centre at half maximum.

    A running max over `close` px (a 1-D closing) bridges specular highlights or
    printed detail inside the feature before thresholding.
    """
    k = max(1, int(close / step))
    pad = np.pad(prof, k, mode="edge")
    dil = np.array([pad[i:i + 2 * k + 1].max() for i in range(len(prof))])
    pad2 = np.pad(dil, k, mode="edge")
    clo = np.array([pad2[i:i + 2 * k + 1].min() for i in range(len(prof))])
    lo, hi = np.percentile(clo, 5), np.percentile(clo, 95)
    t = lo + (hi - lo) / 2
    c = len(clo) // 2
    if clo[c] < t:
        return float("nan"), (float("nan"), float("nan"))
    i = c
    while i > 0 and clo[i - 1] >= t:
        i -= 1
    j = c
    while j < len(clo) - 1 and clo[j + 1] >= t:
        j += 1
    def interp(a, b):
        va, vb = prof[a], prof[b]
        return a + (t - va) / (vb - va) * (b - a) if vb != va else float(a)
    e1 = interp(i - 1, i) if i > 0 else 0.0
    e2 = interp(j, j + 1) if j < len(prof) - 1 else float(len(prof) - 1)
    return (e2 - e1) * step, (e1 * step, e2 * step)


def one(a, p1, p2, step=0.25, method="halfmax", close=6):
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1)
    n = int(L / step) + 1
    xs = np.linspace(x1, x2, n)
    ys = np.linspace(y1, y2, n)
    prof = np.array([sample(a, x, y) for x, y in zip(xs, ys)])
    prof = np.convolve(prof, np.ones(3) / 3, mode="same")
    if method == "halfmax":
        return halfmax(prof, step, close)
    g = np.gradient(prof)
    i_up, i_dn = int(np.argmax(g)), int(np.argmin(g))
    e1, e2 = sorted((sub_peak(g, i_up), sub_peak(-g, i_dn)))
    return (e2 - e1) * step, (e1 * step, e2 * step)


def width(img, p1, p2, channel="L", offsets=range(-6, 7, 2), method="halfmax", close=6, invert=False):
    a = chan(img, channel)
    if invert:
        a = 255 - a
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1)
    # unit vector along the feature (perpendicular to the sampling line)
    tx, ty = -(y2 - y1) / L, (x2 - x1) / L
    each, edges = [], []
    for o in offsets:
        w, e = one(a, (x1 + tx * o, y1 + ty * o), (x2 + tx * o, y2 + ty * o), method=method, close=close)
        each.append(w)
        edges.append(e)
    arr = np.array([x for x in each if not math.isnan(x)])
    return {"mean": float(arr.mean()), "sd": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
            "n": len(arr), "each": [round(x, 2) for x in each], "edges": edges}


if __name__ == "__main__":
    import json
    import sys
    path, x1, y1, x2, y2 = sys.argv[1], *map(float, sys.argv[2:6])
    ch = sys.argv[6] if len(sys.argv) > 6 else "L"
    print(json.dumps(width(load(path), (x1, y1), (x2, y2), ch), indent=1))
