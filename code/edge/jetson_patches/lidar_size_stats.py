"""Estimate a domain's typical car size from raw LiDAR — no labels.

Statistical Normalization fixes the size shift between datasets, but it needs the
target's object-size statistics, which come from target labels. Here the same
statistics are measured from unlabeled LiDAR instead. The detector's own
predictions on unlabeled frames seed where the cars are; only densely observed
clusters are kept, because a sparse cluster sees just a car's near side and reads
short.

Validate before trusting: run this on the SOURCE domain, where the labelled
medians are known, and use whichever statistic recovers them. --report-gt prints
the domain's labelled medians beside the estimate for that check. It is reporting
only and never feeds the estimate.

  python3 lidar_size_stats.py <config> <preds.pkl> [--split train] [--start 0]
      [--n 540] [--min-pts 40] [--report-gt] [--out size.json]
"""
import argparse
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

import label_free_teacher as lft

warnings.filterwarnings("ignore")


def A(x):
    return x.numpy() if torch.is_tensor(x) else np.asarray(x)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("preds")
    ap.add_argument("--split", choices=["train", "test"], default="test")
    ap.add_argument("--start", type=int, default=0, help="pickle index of the split's first frame")
    ap.add_argument("--n", type=int, default=540)
    ap.add_argument("--min-pts", type=int, default=40)
    ap.add_argument("--report-gt", action="store_true")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    ds = build_dataset(cfg.data.train if args.split == "train" else cfg.data.test)
    preds = mmcv.load(args.preds)
    car = list(ds.classes).index("car")
    n = min(args.n, len(ds))

    L, W, H = [], [], []
    for i in range(n):
        r = preds[args.start + i]
        b, s, lab = A(r["boxes_3d"].tensor), A(r["scores_3d"]), A(r["labels_3d"])
        seeds = b[(lab == car) & (s >= 0.3)]
        if not len(seeds):
            continue
        info = ds.infos[i]
        o = ds.load_pcd(os.path.join(ds.data_root, info["lidar_infos"]["LIDAR_TOP"]["filename"]))
        P = A(o[0] if isinstance(o, tuple) else o)[:, :3].astype(np.float64)
        gmap = lft.ground_map(P)
        gfb = float(np.percentile(P[:, 2], 5))
        for sd in seeds:
            near = np.linalg.norm(P[:, :2] - sd[:2], axis=1) < 3.0
            if near.sum() < args.min_pts:
                continue
            g = lft.ground_at(gmap, sd[:2], gfb)
            F = P[near & (P[:, 2] > g + 0.25) & (P[:, 2] < g + 3.0)]
            if len(F) < args.min_pts:
                continue
            lab_ = DBSCAN(eps=0.7, min_samples=5).fit_predict(F)
            if (lab_ >= 0).sum() == 0:
                continue
            C = F[lab_ == np.bincount(lab_[lab_ >= 0]).argmax()]
            if len(C) < args.min_pts:
                continue
            _, _, l_, w_ = lft.min_area_rect(C[:, :2])
            L.append(l_); W.append(w_); H.append(np.percentile(C[:, 2], 97) - g)

    L, W, H = map(np.asarray, (L, W, H))
    print(f"dense clusters (>= {args.min_pts} pts): {len(L)} from {n} frames")
    for name, v in (("length", L), ("width", W), ("height", H)):
        print(f"  {name:<7} median {np.median(v):.2f}   p75 {np.percentile(v,75):.2f}   p90 {np.percentile(v,90):.2f}")

    if args.report_gt:
        G = []
        for i in range(0, n, 2):
            g_, gl = ds.get_gt(ds.infos[i], ds.choose_cams())
            g_, gl = A(g_), A(gl)
            if g_.size:
                G.append(g_.reshape(-1, g_.shape[-1])[gl == car][:, 3:6])
        G = np.concatenate(G)
        print(f"  labelled medians (reporting only): length {np.median(G[:,1]):.2f}  "
              f"width {np.median(G[:,0]):.2f}  height {np.median(G[:,2]):.2f}")

    if args.out:
        json.dump(dict(n=len(L),
                       length=dict(median=float(np.median(L)), p75=float(np.percentile(L, 75)), p90=float(np.percentile(L, 90))),
                       width=dict(median=float(np.median(W)), p75=float(np.percentile(W, 75)), p90=float(np.percentile(W, 90))),
                       height=dict(median=float(np.median(H)), p75=float(np.percentile(H, 75)), p90=float(np.percentile(H, 90)))),
                  open(args.out, "w"), indent=2)
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
