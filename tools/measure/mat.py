"""Calibrate a photo from the 1 cm grid of a cutting mat lying in the photo.

    from mat import calibrate
    cal = calibrate(img_path, seeds={(0, 27): (193, 222), (42, 27): (1749, 215),
                                     (0, 0): (34, 1265), (42, 0): (1896, 1258)},
                    xr=range(0, 43), yr=range(0, 28))

1. A rough homography (mat cm -> image px) is fitted to the seed points.
2. Every integer grid crossing is predicted and refined to sub-pixel: both lines
   through the crossing are located on short perpendicular intensity profiles
   (parabolic peak fit), fitted as lines and intersected. Crossings hidden by an
   object, or with weak or inconsistent line evidence, are rejected.
3. The homography is refitted to all accepted crossings, twice, with outliers
   beyond 3x the median residual removed.
4. The camera is recovered from the homography assuming square pixels and a
   centred principal point (single-view focal estimate), so rays can be
   intersected with planes above the mat (for parts that stand above it).

Returned dict: H (mm -> px), Hinv, rms_mm, n_points, f_px, R, t, K, points.
"""
from __future__ import annotations

import math

import cv2
import numpy as np
from PIL import Image


def gray(path):
    return np.asarray(Image.open(path).convert("L")).astype(float)


def bil(a, x, y):
    h, w = a.shape
    if not (0 <= x < w - 1 and 0 <= y < h - 1):
        return float("nan")
    x0, y0 = int(x), int(y)
    dx, dy = x - x0, y - y0
    return (a[y0, x0] * (1 - dx) * (1 - dy) + a[y0, x0 + 1] * dx * (1 - dy)
            + a[y0 + 1, x0] * (1 - dx) * dy + a[y0 + 1, x0 + 1] * dx * dy)


def apply(H, pts):
    pts = np.asarray(pts, float).reshape(-1, 2)
    p = np.c_[pts, np.ones(len(pts))] @ H.T
    return p[:, :2] / p[:, 2:3]


def line_points(a, c, d, half_len=9, half_w=6, step=0.25, min_contrast=25):
    """Find where a thin bright line with direction d crosses short profiles.

    Profiles are taken perpendicular to d at positions along d within
    +/- half_len px of c (skipping the central 3 px where the other line crosses).
    Returns list of (x, y) on the line.
    """
    d = np.asarray(d, float) / np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    pts = []
    for s in np.arange(-half_len, half_len + 0.01, 1.0):
        if abs(s) < 3:
            continue
        base = np.asarray(c) + s * d
        offs = np.arange(-half_w, half_w + 0.01, step)
        prof = np.array([bil(a, *(base + o * n)) for o in offs])
        if np.isnan(prof).any():
            continue
        i = int(np.argmax(prof))
        if prof[i] - np.median(prof) < min_contrast or i in (0, len(prof) - 1):
            continue
        y0, y1, y2 = prof[i - 1], prof[i], prof[i + 1]
        den = y0 - 2 * y1 + y2
        sub = i + (0.5 * (y0 - y2) / den if den else 0)
        pts.append(base + offs[0] * n + sub * step * n)
    return pts


def fit_line(pts):
    pts = np.asarray(pts)
    c = pts.mean(axis=0)
    u, s, vt = np.linalg.svd(pts - c)
    d = vt[0]
    resid = np.abs((pts - c) @ vt[1])
    return c, d, resid


def intersect(c1, d1, c2, d2):
    A = np.array([d1, -d2]).T
    t = np.linalg.solve(A, c2 - c1)
    return c1 + t[0] * d1


def refine(a, H, X, Y):
    """Refine the crossing of mat lines x=X cm and y=Y cm. Returns (x, y) or None."""
    c = apply(H, [(X * 10, Y * 10)])[0]
    dv = apply(H, [(X * 10, Y * 10 + 5)])[0] - c        # along the x=X line
    dh = apply(H, [(X * 10 + 5, Y * 10)])[0] - c        # along the y=Y line
    pv = line_points(a, c, dv)
    ph = line_points(a, c, dh)
    if len(pv) < 8 or len(ph) < 8:
        return None
    cv_, dv_, rv = fit_line(pv)
    ch_, dh_, rh = fit_line(ph)
    if np.median(rv) > 0.6 or np.median(rh) > 0.6:
        return None
    p = intersect(cv_, dv_, ch_, dh_)
    if np.linalg.norm(p - c) > 6:
        return None
    return p


def focal_from_H(H, w, h):
    """Single-view focal length (px) from a plane homography, square pixels,
    principal point at the image centre."""
    T = np.array([[1, 0, -w / 2], [0, 1, -h / 2], [0, 0, 1]])
    Hc = T @ H
    h1, h2 = Hc[:, 0], Hc[:, 1]
    num1 = -(h1[0] * h2[0] + h1[1] * h2[1])
    den1 = h1[2] * h2[2]
    num2 = -((h1[0] ** 2 + h1[1] ** 2) - (h2[0] ** 2 + h2[1] ** 2))
    den2 = h1[2] ** 2 - h2[2] ** 2
    est = []
    for num, den in ((num1, den1), (num2, den2)):
        if den != 0 and num / den > 0:
            est.append(math.sqrt(num / den))
    return est


def pose(H, f, w, h):
    K = np.array([[f, 0, w / 2], [0, f, h / 2], [0, 0, 1.0]])
    M = np.linalg.inv(K) @ H
    lam = 1 / np.linalg.norm(M[:, 0])
    r1, r2, t = M[:, 0] * lam, M[:, 1] * lam, M[:, 2] * lam
    if t[2] < 0:
        r1, r2, t = -r1, -r2, -t
    R = np.c_[r1, r2, np.cross(r1, r2)]
    U, _, Vt = np.linalg.svd(R)
    R = U @ Vt
    return K, R, t


def to_plane(cal, px, z_mm=0.0):
    """Image px -> mat-frame (x, y) mm on the plane z = z_mm above the mat.

    The mat frame has z pointing towards the camera when the camera is above it.
    """
    K, R, t = cal["K"], cal["R"], cal["t"]
    C = -R.T @ t                                   # camera centre in mat frame
    sign = 1.0 if C[2] > 0 else -1.0
    out = []
    for u, v in np.asarray(px, float).reshape(-1, 2):
        ray = R.T @ np.linalg.inv(K) @ np.array([u, v, 1.0])
        s = (sign * z_mm - C[2]) / ray[2]
        P = C + s * ray
        out.append(P[:2])
    return np.array(out)


def calibrate(path, seeds, xr, yr, exclude=None):
    a = gray(path)
    h, w = a.shape
    src = np.array([(X * 10, Y * 10) for (X, Y) in seeds], float)
    dst = np.array(list(seeds.values()), float)
    H, _ = cv2.findHomography(src, dst, 0)
    pts = {}
    for _ in range(2):
        pts = {}
        for X in xr:
            for Y in yr:
                if exclude and exclude(X, Y):
                    continue
                p = refine(a, H, X, Y)
                if p is not None:
                    pts[(X, Y)] = p
        src = np.array([(X * 10, Y * 10) for (X, Y) in pts], float)
        dst = np.array(list(pts.values()), float)
        H, _ = cv2.findHomography(src, dst, 0)
        # outlier removal
        Hinv = np.linalg.inv(H)
        back = apply(Hinv, dst)
        res = np.linalg.norm(back - src, axis=1)
        keep = res < max(3 * np.median(res), 0.15)
        src, dst = src[keep], dst[keep]
        pts = {k: v for k, v, ok in zip(list(pts), list(pts.values()), keep) if ok}
        H, _ = cv2.findHomography(src, dst, 0)
    Hinv = np.linalg.inv(H)
    res = np.linalg.norm(apply(Hinv, dst) - src, axis=1)
    fs = focal_from_H(H, w, h)
    f = float(np.mean(fs)) if fs else float("nan")
    K, R, t = pose(H, f, w, h) if fs else (None, None, None)
    return {"H": H, "Hinv": Hinv, "rms_mm": float(np.sqrt((res ** 2).mean())),
            "max_mm": float(res.max()), "n_points": len(src), "f_px": f, "f_est": fs,
            "K": K, "R": R, "t": t, "points": pts, "size": (w, h),
            "cam_height_mm": float((-R.T @ t)[2]) if R is not None else float("nan")}
