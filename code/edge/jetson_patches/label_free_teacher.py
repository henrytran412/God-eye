"""A gaussian4d-style label-free teacher for 3D car detection on the target domain.

Prof. Liu's ngperception/gaussian4d builds occupancy targets with no human labels by
trusting raw LiDAR geometry and borrowing semantics from frozen 2D foundation models.
This applies the same recipe to detection. A COCO-pretrained YOLO — trained on neither
DAIR-V2X-I nor TUMTraf — says where the cars are in the image; the LiDAR points inside
each 2D box are clustered and a 3D box is fitted to them by geometry alone. Nothing is
trained and no target label is read.

It targets the two failures the attribution work measured on TUMTraf: 74% of cars
get no prediction within 2 m (recall), and the cars that are found carry yaw, height
and width errors at once (box quality). Modes:

  teacher   replace V2XFusion's car predictions with teacher boxes
  refine    keep V2XFusion's car boxes but refit each one's geometry from LiDAR
  union     keep V2XFusion's car boxes and add teacher boxes where it has none
  both      refine and union together

Non-car predictions pass through untouched, so Pedestrian and Cyclist stay as they
were and any change in the Car row is the teacher's doing.

--oracle2d swaps YOLO for GT boxes projected into the image: a perfect 2D detector.
That isolates the LiDAR fitting from the 2D detection, and because it writes boxes
in the convention the evaluator scores, it is also the check that the convention is
right — a wrong yaw convention shows up as collapsed BEV AP even with perfect 2D.

  python3 label_free_teacher.py <config> <preds.pkl> --start 540 \
      (--yolo yolo.json | --oracle2d) --mode both --out teacher.pkl [--eval]
"""
import argparse
import copy
import json
import os
import warnings

import mmcv
import numpy as np
import torch
from sklearn.cluster import DBSCAN
from torchpack.utils.config import configs
from mmdet3d.datasets import build_dataset
from mmdet3d.utils import recursive_eval

warnings.filterwarnings("ignore")

# Fallback size priors, used only when a run passes no --size file. They were first
# set near TUMTraf GT medians, which is a target-label leak; label-free runs pass
# --size, measured from unlabeled LiDAR by lidar_size_stats.py, and override them.
CAR_L, CAR_W = 4.3, 1.9
CAR_H = None                            # height floor; None keeps the measured height
L_RANGE, W_RANGE, H_RANGE = (3.6, 5.6), (1.6, 2.2), (1.35, 2.4)
CELL = 4.0                              # ground-map cell size, metres


def as_np(x):
    return x.numpy() if torch.is_tensor(x) else np.asarray(x)


def ground_map(P):
    """Per-cell low percentile of z: a local road height that tolerates slope."""
    ij = np.floor(P[:, :2] / CELL).astype(np.int64)
    key = ij[:, 0] * 100003 + ij[:, 1]
    order = np.argsort(key)
    key, z, ij = key[order], P[order, 2], ij[order]
    uniq, start = np.unique(key, return_index=True)
    out = {}
    for k, s, e in zip(uniq, start, np.r_[start[1:], len(key)]):
        if e - s >= 8:
            out[(ij[s, 0], ij[s, 1])] = np.percentile(z[s:e], 5)
    return out


def ground_at(gmap, xy, fallback):
    ci, cj = int(np.floor(xy[0] / CELL)), int(np.floor(xy[1] / CELL))
    vals = [gmap[(ci + a, cj + b)] for a in (-1, 0, 1) for b in (-1, 0, 1)
            if (ci + a, cj + b) in gmap]
    return float(np.median(vals)) if vals else fallback


def min_area_rect(xy):
    """Minimum-area rectangle by angle search. Returns centre, long-axis angle, L, W."""
    best = None
    for deg in range(0, 90):
        t = np.deg2rad(deg)
        c, s = np.cos(t), np.sin(t)
        u = xy[:, 0] * c + xy[:, 1] * s
        v = -xy[:, 0] * s + xy[:, 1] * c
        du, dv = u.max() - u.min(), v.max() - v.min()
        if best is None or du * dv < best[0]:
            best = (du * dv, t, du, dv, (u.max() + u.min()) / 2, (v.max() + v.min()) / 2)
    _, t, du, dv, uc, vc = best
    c, s = np.cos(t), np.sin(t)
    centre = np.array([uc * c - vc * s, uc * s + vc * c])
    if du >= dv:
        return centre, t, du, dv
    return centre, t + np.pi / 2, dv, du


def project_boxes(X, Y, Z, yaw, w, l, h, K, l2c, W, H):
    """Image-space min/max of many candidate boxes at once.

    Bottom-face z, col4 = length along yaw, col3 = width across — the evaluator's layout.
    Projected corners are clipped to the image, which is how a truncated car looks to
    any 2D detector, so a box half off-screen is matched against the visible part.
    """
    c, s = np.cos(yaw), np.sin(yaw)
    # Measured, not assumed: a car's long axis lies ALONG yaw (85% of well-observed
    # TUMTraf cars, 76% DAIR), so column 4 (length) runs along yaw and column 3
    # (width) across it.
    du = np.array([-1, -1, -1, -1, 1, 1, 1, 1]) * (l / 2)
    dv = np.array([-1, -1, 1, 1, -1, -1, 1, 1]) * (w / 2)
    dz = np.array([0, 1, 0, 1, 0, 1, 0, 1]) * h
    cx = X[:, None] + du[None] * c[:, None] - dv[None] * s[:, None]
    cy = Y[:, None] + du[None] * s[:, None] + dv[None] * c[:, None]
    cz = np.broadcast_to(Z + dz[None], cx.shape)
    pts = np.stack([cx, cy, cz, np.ones_like(cx)], -1)            # (N, 8, 4)
    cam = pts @ l2c.T                                              # (N, 8, 4)
    z = np.maximum(cam[..., 2], 1e-3)
    u = (K[0, 0] * cam[..., 0] + K[0, 2] * cam[..., 2]) / z
    v = (K[1, 1] * cam[..., 1] + K[1, 2] * cam[..., 2]) / z
    u, v = np.clip(u, 0, W - 1), np.clip(v, 0, H - 1)
    return np.stack([u.min(1), v.min(1), u.max(1), v.max(1)], 1), (cam[..., 2] > 0.5).all(1)


def refine_with_2d(bx, box2d, C, K, l2c, W, H, yaw_span_deg=12, allow_perp=True,
                   yaw_grid=None, span_m=3.0):
    """Move a LiDAR-fitted box so its projection matches the 2D box.

    The sparse LiDAR cluster sees only a car's near side, which drags its centroid
    ~1.7 m toward the sensor. The 2D box bounds the whole car precisely, so search
    position and yaw for the box (prior-sized, resting on the ground) whose projected
    extent best matches it, while a second term keeps the LiDAR points inside the
    footprint so depth stays anchored. Coarse 0.25 m grid over +-3 m, then a 0.05 m pass.
    """
    x1, y1, x2, y2 = box2d
    bw, bh = max(x2 - x1, 1.0), max(y2 - y1, 1.0)
    target = np.array([x1, y1, x2, y2])
    w, l, h, z = bx[3], bx[4], bx[5], bx[2]
    pts = C[:, :2] if len(C) else np.zeros((0, 2))

    def score(X, Y, Yaw):
        img, ok = project_boxes(X, Y, z, Yaw, w, l, h, K, l2c, W, H)
        e2d = (np.abs(img[:, [0, 2]] - target[[0, 2]]).sum(1) / bw
               + np.abs(img[:, [1, 3]] - target[[1, 3]]).sum(1) / bh)
        c, s = np.cos(Yaw), np.sin(Yaw)
        d = pts[None] - np.stack([X, Y], 1)[:, None]
        uu = np.abs(d[..., 0] * c[:, None] + d[..., 1] * s[:, None]) - l / 2 - 0.2
        vv = np.abs(-d[..., 0] * s[:, None] + d[..., 1] * c[:, None]) - w / 2 - 0.2
        outside = np.mean((uu > 0) | (vv > 0), axis=1) if len(pts) else np.zeros(len(X))
        return np.where(ok, e2d + 1.0 * outside, np.inf)

    best = (np.inf, bx[0], bx[1], bx[6])
    coarse_step = max(2, yaw_span_deg // 2)
    for (span, step, ydeg, ystep) in ((span_m, 0.25, yaw_span_deg, coarse_step), (0.3, 0.05, 4, 2)):
        g = np.arange(-span, span + 1e-6, step)
        yaws = [best[3]] if span < 1 else ([bx[6], bx[6] + np.pi / 2] if allow_perp else [bx[6]])
        if span >= 1 and yaw_grid is not None:
            ylist = np.asarray(yaw_grid, float)
        else:
            ylist = np.concatenate([y0 + np.deg2rad(np.arange(-ydeg, ydeg + 1e-6, ystep)) for y0 in yaws])
        GX, GY, GYAW = np.meshgrid(best[1] + g, best[2] + g, ylist, indexing="ij")
        X, Y, Yaw = GX.ravel(), GY.ravel(), GYAW.ravel()
        sc = score(X, Y, Yaw)
        k = int(np.argmin(sc))
        if sc[k] < best[0]:
            best = (sc[k], X[k], Y[k], Yaw[k])
    out = bx.copy()
    out[0], out[1], out[6] = best[1], best[2], best[3]
    return out


def mono_box(box2d, K, l2c, gmap, g_fallback, W, H):
    """A car box from the 2D box alone, for cars the LiDAR barely touches.

    The bottom edge of a car's 2D box is where it meets the road. The camera is
    calibrated and the road height is mapped, so the ray through that pixel meets
    the ground at the car's near edge. Position and yaw are then searched against
    the 2D box exactly as for LiDAR fits, with every yaw open since no points
    constrain it.
    """
    x1, y1, x2, y2 = box2d
    c2l = np.linalg.inv(l2c)
    o = c2l[:3, 3]
    d = c2l[:3, :3] @ (np.linalg.inv(K) @ np.array([(x1 + x2) / 2, y2, 1.0]))
    if d[2] >= -1e-6:                       # ray never descends to the road
        return None
    g = g_fallback
    for _ in range(2):                      # intersect, then re-read local ground there
        t = (g - o[2]) / d[2]
        p = o + t * d
        g = ground_at(gmap, p[:2], g_fallback)
    if t <= 0 or np.linalg.norm(p[:2] - o[:2]) > 120:
        return None
    hd = d[:2] / max(np.linalg.norm(d[:2]), 1e-6)
    c = p[:2] + hd * (CAR_W / 2 + 0.3)      # the box centre lies beyond its near edge
    h = CAR_H if CAR_H is not None else 1.5
    bx = np.array([c[0], c[1], g, CAR_W, CAR_L, h, np.arctan2(hd[1], hd[0]), 0, 0], np.float32)
    return refine_with_2d(bx, box2d, np.zeros((0, 3)), K, l2c, W, H,
                          yaw_grid=np.deg2rad(np.arange(0, 180, 15)), span_m=4.0)


def fit_box(F, gmap, g_fallback, yaw_offset, return_cluster=False):
    """Fit one car box to frustum points F (N, >=3). None when the evidence is too thin."""
    g = ground_at(gmap, np.median(F[:, :2], axis=0), g_fallback)
    F = F[(F[:, 2] > g + 0.25) & (F[:, 2] < g + 3.0)]
    if len(F) < 5:
        return None
    lab = DBSCAN(eps=0.9, min_samples=4).fit_predict(F[:, :3])
    if (lab >= 0).sum() == 0:
        return None
    C = F[lab == np.bincount(lab[lab >= 0]).argmax()]
    if len(C) < 5:
        return None
    centre, phi, L, W = min_area_rect(C[:, :2])
    a = np.array([np.cos(phi), np.sin(phi)])          # long axis
    b = np.array([-a[1], a[0]])                       # short axis
    l = L if L >= L_RANGE[0] else CAR_L
    w = W if W >= 1.5 else CAR_W
    l, w = np.clip(l, *L_RANGE), np.clip(w, *W_RANGE)
    # the unseen part of a car is always its far side, so grow away from the sensor
    centre = centre + np.sign(centre @ a or 1.0) * (l - L) / 2 * a \
                    + np.sign(centre @ b or 1.0) * (w - W) / 2 * b
    h = np.percentile(C[:, 2], 97) - g
    # a sparse cluster seen from a mast rarely samples the roof, so measured height
    # runs short; a domain height estimated from dense clusters acts as a floor
    if CAR_H is not None:
        h = max(h, CAR_H)
    h = np.clip(h, *H_RANGE)
    yaw = phi + yaw_offset
    # tensor layout the evaluator scores: col3 = width, col4 = length along yaw, z = bottom
    box = np.array([centre[0], centre[1], g, w, l, h, yaw, 0.0, 0.0], dtype=np.float32)
    return (box, C) if return_cluster else box


def corners_gt(b):
    """8 corners of a GT box (geometric-centre z; col4 = length along yaw, col3 across)."""
    c, s = np.cos(b[6]), np.sin(b[6])
    out = []
    for du in (-1, 1):
        for dv in (-1, 1):
            for dz in (-1, 1):
                u, v = du * b[4] / 2, dv * b[3] / 2
                out.append([b[0] + u * c - v * s, b[1] + u * s + v * c, b[2] + dz * b[5] / 2])
    return np.array(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("preds")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--yolo", default="")
    ap.add_argument("--oracle2d", action="store_true")
    ap.add_argument("--coco", default="2", help="COCO class ids to treat as car, e.g. 2,7")
    ap.add_argument("--min-conf", type=float, default=0.3)
    ap.add_argument("--mode", choices=["teacher", "refine", "union", "both"], default="both")
    ap.add_argument("--yaw-offset-deg", type=float, default=-90.0)
    ap.add_argument("--match", type=float, default=2.0, help="BEV metres for refine/union pairing")
    ap.add_argument("--size", default="", help="JSON from lidar_size_stats.py")
    ap.add_argument("--size-stat", default="median", choices=["median", "p75", "p90"])
    ap.add_argument("--roads", default="", help="JSON with roads_deg (teacher_priors.py)")
    ap.add_argument("--snap-deg", type=float, default=25.0,
                    help="snap yaw to a road direction within this many degrees")
    ap.add_argument("--mono", action="store_true",
                    help="lift 2D boxes with too few LiDAR points via the ground plane")
    ap.add_argument("--mono-weight", type=float, default=0.6,
                    help="score multiplier for mono boxes, ranking them below LiDAR fits")
    ap.add_argument("--fit2d", action="store_true",
                    help="move each LiDAR fit so its projection matches its 2D box")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--eval", action="store_true")
    args = ap.parse_args()

    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    ds = build_dataset(cfg.data.test)
    preds = mmcv.load(args.preds)
    car = list(ds.classes).index("car")
    H, W = cfg.data.test["dataset"]["H"], cfg.data.test["dataset"]["W"]
    yolo = json.load(open(args.yolo)) if args.yolo else {}
    coco = {int(c) for c in args.coco.split(",")}
    yoff = np.deg2rad(args.yaw_offset_deg)
    global CAR_L, CAR_W, CAR_H
    if args.size:
        sz = json.load(open(args.size))
        CAR_L, CAR_W, CAR_H = (sz[k][args.size_stat] for k in ("length", "width", "height"))
        print(f"  size priors from {os.path.basename(args.size)} ({args.size_stat}): l={CAR_L:.2f} w={CAR_W:.2f} h={CAR_H:.2f}")
    roads = np.deg2rad(json.load(open(args.roads))["roads_deg"]) if args.roads else None
    if roads is not None:
        print(f"  road directions: {np.round(np.rad2deg(roads), 1).tolist()} (snap within {args.snap_deg} deg)")
    stats_snap = [0, 0]
    n = len(ds) if not args.limit else args.limit

    outs, stats = [], dict(boxes2d=0, fitted=0, refined=0, added=0)
    for i in range(n):
        info = ds.infos[i]
        r = copy.deepcopy(preds[args.start + i])
        lid = info["lidar_infos"]["LIDAR_TOP"]["filename"]
        o = ds.load_pcd(os.path.join(ds.data_root, lid))
        P = as_np(o[0] if isinstance(o, tuple) else o)[:, :3].astype(np.float64)
        cam = ds.choose_cams()[0]
        K = np.asarray(info["cam_infos"][cam]["calibrated_sensor"]["camera_intrinsic"], float)
        l2c = np.asarray(as_np(ds.load_lidar2camera_mat(lid, ds.data_root)), float).reshape(-1, 4, 4)[0]
        Pc = (l2c @ np.c_[P, np.ones(len(P))].T).T[:, :3]
        front = Pc[:, 2] > 0.5
        uv = np.full((len(P), 2), -1e9)
        uv[front] = (K @ Pc[front].T).T[:, :2] / Pc[front, 2:3]
        gmap = ground_map(P)
        g_fallback = float(np.percentile(P[:, 2], 5))

        if args.oracle2d:
            g, gl = ds.get_gt(info, ds.choose_cams())
            g, gl = as_np(g), as_np(gl)
            boxes2d = []
            for b in (g.reshape(-1, g.shape[-1])[gl == car] if g.size else []):
                cc = (l2c @ np.c_[corners_gt(b), np.ones(8)].T).T[:, :3]
                if (cc[:, 2] <= 0.5).any():
                    continue
                q = (K @ cc.T).T[:, :2] / cc[:, 2:3]
                x1, y1 = np.clip(q.min(0), 0, [W - 1, H - 1]); x2, y2 = np.clip(q.max(0), 0, [W - 1, H - 1])
                if x2 - x1 > 4 and y2 - y1 > 4:
                    boxes2d.append([x1, y1, x2, y2, 1.0])
        else:
            boxes2d = [row[:5] for row in yolo.get(str(i), [])
                       if int(row[5]) in coco and row[4] >= args.min_conf]
        stats["boxes2d"] += len(boxes2d)

        fitted, fscore = [], []
        for x1, y1, x2, y2, conf in boxes2d:
            mx, my = 0.08 * (x2 - x1), 0.08 * (y2 - y1)
            sel = (uv[:, 0] >= x1 + mx) & (uv[:, 0] <= x2 - mx) & (uv[:, 1] >= y1 + my) & (uv[:, 1] <= y2 - my)
            res = (fit_box(P[sel], gmap, g_fallback, yoff, return_cluster=args.fit2d)
                   if sel.sum() >= 5 else None)
            if res is None:
                if args.mono:
                    mb = mono_box((x1, y1, x2, y2), K, l2c, gmap, g_fallback, W, H)
                    if mb is not None:
                        fitted.append(mb); fscore.append(conf * args.mono_weight)
                        stats["mono"] = stats.get("mono", 0) + 1
                continue
            if args.fit2d:
                bx, C = res
                span, perp = 12, True
                if roads is not None:
                    # the long axis is ambiguous by 180 deg, so compare modulo pi
                    d = (bx[6] - roads + np.pi / 2) % np.pi - np.pi / 2
                    k = int(np.argmin(np.abs(d)))
                    stats_snap[1] += 1
                    if abs(d[k]) < np.deg2rad(args.snap_deg):
                        bx[6] = roads[k]; span, perp = 4, False; stats_snap[0] += 1
                bx = refine_with_2d(bx, (x1, y1, x2, y2), C, K, l2c, W, H,
                                    yaw_span_deg=span, allow_perp=perp)
            else:
                bx = res
            fitted.append(bx); fscore.append(conf)
        stats["fitted"] += len(fitted)
        fitted = np.asarray(fitted, np.float32).reshape(-1, 9)
        fscore = np.asarray(fscore, np.float32)

        B = as_np(r["boxes_3d"].tensor).astype(np.float32)
        S = as_np(r["scores_3d"]).astype(np.float32)
        L = as_np(r["labels_3d"])
        iscar = L == car
        if args.mode == "teacher":
            keep = ~iscar
            B, S, L = B[keep], S[keep], L[keep]
            B = np.r_[B, fitted]; S = np.r_[S, fscore]; L = np.r_[L, np.full(len(fitted), car)]
        else:
            used = np.zeros(len(fitted), bool)
            if args.mode in ("refine", "both") and len(fitted):
                for k in np.where(iscar)[0]:
                    d = np.linalg.norm(fitted[:, :2] - B[k, :2], axis=1)
                    d[used] = np.inf
                    j = int(np.argmin(d))
                    if d[j] < args.match:
                        B[k] = fitted[j]; used[j] = True; stats["refined"] += 1
            if args.mode in ("union", "both") and len(fitted):
                cars = B[L == car][:, :2]
                for j in np.where(~used)[0]:
                    if len(cars) == 0 or np.linalg.norm(cars - fitted[j, :2], axis=1).min() >= args.match:
                        B = np.r_[B, fitted[j:j + 1]]; S = np.r_[S, fscore[j:j + 1]]
                        L = np.r_[L, [car]]; stats["added"] += 1
        r["boxes_3d"].tensor = torch.from_numpy(B.reshape(-1, 9))
        r["scores_3d"] = torch.from_numpy(S)
        r["labels_3d"] = torch.from_numpy(L.astype(np.int64))
        outs.append(r)
        if i % 200 == 0:
            print(f"  {i}/{n}  {stats}", flush=True)

    mmcv.dump(outs, args.out)
    if roads is not None:
        print(f"  yaw snapped to a road direction: {stats_snap[0]}/{stats_snap[1]}")
    print(f"wrote {args.out}  {stats}")
    if args.eval:
        print(ds.evaluate(outs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
