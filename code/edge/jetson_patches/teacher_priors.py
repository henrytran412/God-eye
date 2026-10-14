"""Priors for the label-free teacher, drawn only from what adaptation may use.

  * Car size: from the SOURCE domain's labels (DAIR-V2X-I). Source labels are
    legitimately available in domain adaptation; target labels are not. The first
    teacher took its size priors from TUMTraf GT medians, which was a leak.
  * Road directions: from the TARGET domain, but only from V2XFusion's unlabeled
    predictions on the 540 calibration frames, which are disjoint from the 1620
    frames that get scored. V2XFusion's target yaw is noisy (std ~22 deg) yet
    centred on the truth, so its histogram peaks where the roads run.

  python3 teacher_priors.py <source_config> <target_preds.pkl> [--calib 540]
"""
import argparse
import json
import warnings

import mmcv
import numpy as np
import torch
from torchpack.utils.config import configs
from mmdet3d.datasets import build_dataset
from mmdet3d.utils import recursive_eval

warnings.filterwarnings("ignore")


def A(x):
    return x.numpy() if torch.is_tensor(x) else np.asarray(x)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_config")
    ap.add_argument("target_preds")
    ap.add_argument("--calib", type=int, default=540)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    configs.load(args.source_config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.source_config)
    ds = build_dataset(cfg.data.test)
    car = list(ds.classes).index("car")
    S = []
    for i in range(0, len(ds), 4):
        g, gl = ds.get_gt(ds.infos[i], ds.choose_cams())
        g, gl = A(g), A(gl)
        if g.size:
            S.append(g.reshape(-1, g.shape[-1])[gl == car][:, 3:6])
    S = np.concatenate(S)
    w, l, h = np.median(S, 0)
    print(f"SOURCE car medians  width {w:.2f}  length {l:.2f}  height {h:.2f}   (n={len(S)})")
    print(f"SOURCE car height   p25 {np.percentile(S[:,2],25):.2f}  p75 {np.percentile(S[:,2],75):.2f}")

    Y = []
    for r in mmcv.load(args.target_preds)[: args.calib]:
        b, s, lab = A(r["boxes_3d"].tensor), A(r["scores_3d"]), A(r["labels_3d"])
        k = (lab == car) & (s >= 0.4)
        Y.append(b[k, 6])
    Y = np.degrees(np.concatenate(Y)) % 180.0
    hist, edges = np.histogram(Y, bins=36, range=(0, 180))
    print(f"TARGET calib-split car yaws (unlabeled V2XFusion predictions): n={len(Y)}")
    for k in range(36):
        if hist[k] >= 0.25 * hist.max():
            print(f"  {edges[k]:5.0f}-{edges[k+1]:3.0f} deg  {hist[k]:4d}  {'#' * int(40 * hist[k] / hist.max())}")

    # peaks: local maxima of a circularly smoothed histogram, at least 30 deg apart
    sm = np.convolve(np.r_[hist[-2:], hist, hist[:2]], np.ones(5) / 5, mode="valid")
    order = np.argsort(-sm)
    peaks = []
    for k in order:
        c = (edges[k] + edges[k + 1]) / 2
        if sm[k] < 0.3 * sm.max():
            break
        if all(min(abs(c - p), 180 - abs(c - p)) >= 30 for p in peaks):
            peaks.append(float(c))
    print(f"road directions (deg, mod 180): {[round(p, 1) for p in peaks]}")
    if args.out:
        json.dump(dict(car_w=float(w), car_l=float(l), car_h=float(h), roads_deg=peaks),
                  open(args.out, "w"), indent=2)
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
