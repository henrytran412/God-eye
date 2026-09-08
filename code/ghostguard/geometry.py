"""BEV geometry: rotated-box IoU with a cheap center-distance prefilter.

Everything is 2D bird's-eye-view. Boxes are (x, y, l, w, yaw) with l along the
heading. Height is dropped on purpose: none of the questions this sandbox is
built to answer (message admission, duplicate collapse, ghost suppression)
depend on the z extent, and dropping it keeps the counterfactual reruns cheap.
"""
import numpy as np


def corners(box):
    x, y, l, w, yaw = box[0], box[1], box[2], box[3], box[4]
    c, s = np.cos(yaw), np.sin(yaw)
    dx = np.array([l / 2, l / 2, -l / 2, -l / 2])
    dy = np.array([w / 2, -w / 2, -w / 2, w / 2])
    return np.stack([x + c * dx - s * dy, y + s * dx + c * dy], axis=1)


def _clip(subject, clipper):
    """Sutherland-Hodgman convex polygon clip (both inputs CCW convex quads)."""
    out = subject
    n = len(clipper)
    for i in range(n):
        if not out:
            return []
        a = clipper[i]
        b = clipper[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        inside = lambda p: ex * (p[1] - a[1]) - ey * (p[0] - a[0]) >= 0
        new = []
        m = len(out)
        for j in range(m):
            p = out[j]
            q = out[(j + 1) % m]
            pi, qi = inside(p), inside(q)
            if pi:
                new.append(p)
            if pi != qi:
                dx, dy = q[0] - p[0], q[1] - p[1]
                den = ex * dy - ey * dx
                if abs(den) > 1e-12:
                    t = (ey * (p[0] - a[0]) - ex * (p[1] - a[1])) / den
                    new.append((p[0] + t * dx, p[1] + t * dy))
        out = new
    return out


def _area(poly):
    if len(poly) < 3:
        return 0.0
    a = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def _ccw(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return list(pts) if a >= 0 else list(pts[::-1])


def iou(box_a, box_b):
    """Rotated BEV IoU. Prefiltered by center distance vs half-diagonals."""
    d = np.hypot(box_a[0] - box_b[0], box_a[1] - box_b[1])
    ra = 0.5 * np.hypot(box_a[2], box_a[3])
    rb = 0.5 * np.hypot(box_b[2], box_b[3])
    if d > ra + rb:
        return 0.0
    pa = _ccw([tuple(p) for p in corners(box_a)])
    pb = _ccw([tuple(p) for p in corners(box_b)])
    inter = _area(_clip(pa, pb))
    if inter <= 0.0:
        return 0.0
    aa = box_a[2] * box_a[3]
    ab = box_b[2] * box_b[3]
    return float(inter / (aa + ab - inter))


def iou_matrix(boxes_a, boxes_b):
    A, B = len(boxes_a), len(boxes_b)
    M = np.zeros((A, B))
    for i in range(A):
        for j in range(B):
            M[i, j] = iou(boxes_a[i], boxes_b[j])
    return M
