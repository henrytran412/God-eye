"""Gate checks before building a LiDAR-geometry teacher on the target domain.

A label-free teacher (2D detector -> LiDAR frustum -> fitted 3D box) is only as good
as three assumptions, each checked here against GT before any teacher box is scored:

  1. Points, GT boxes and the camera calibration share one frame. Measured as the
     fraction of GT cars whose footprint contains LiDAR points, and the fraction whose
     points project inside the image.
  2. Where the ground actually is relative to the label frame. The lowest points
     under a GT car sit on the road; their height against the GT box bottom says
     whether points and labels disagree vertically.
  3. The box convention: which tensor column holds the long side of a car, so fitted
     boxes are written in the layout the evaluator already scores correctly.

  python3 teacher_probe.py <config> [--n 150]
"""
import argparse
import os
import warnings

import mmcv
import numpy as np
import torch
from torchpack.utils.config import configs
from mmdet3d.datasets import build_dataset
from mmdet3d.utils import recursive_eval

warnings.filterwarnings("ignore")


def as_np(x):
    return x.numpy() if torch.is_tensor(x) else np.asarray(x)


def in_box_bev(pts, box):
    """Points whose BEV position falls inside the rotated GT footprint."""
    c, s = np.cos(box[6]), np.sin(box[6])
    d = pts[:, :2] - box[:2]
    u = d[:, 0] * c + d[:, 1] * s
    v = -d[:, 0] * s + d[:, 1] * c
    # Measured, not assumed: a car's long axis lies ALONG yaw (85% of well-observed
    # TUMTraf cars, 76% DAIR), so column 4 (length) runs along yaw and column 3
    # (width) across it.
    return (np.abs(u) <= box[4] / 2) & (np.abs(v) <= box[3] / 2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--n", type=int, default=150)
    args = ap.parse_args()
    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    ds = build_dataset(cfg.data.test)
    car = list(ds.classes).index("car")
    H, W = cfg.data.test["dataset"]["H"], cfg.data.test["dataset"]["W"]

    n_gt = with_pts = on_img = 0
    pts_per, bottom_gap, col3, col4 = [], [], [], []
    shown = False
    for i in range(0, len(ds), max(1, len(ds) // args.n)):
        info = ds.infos[i]
        g, gl = ds.get_gt(info, ds.choose_cams())
        g, gl = as_np(g), as_np(gl)
        if not g.size:
            continue
        g = g.reshape(-1, g.shape[-1])[gl == car]
        lid = info["lidar_infos"]["LIDAR_TOP"]["filename"]
        o = ds.load_pcd(os.path.join(ds.data_root, lid))
        P = as_np(o[0] if isinstance(o, tuple) else o)
        cam = ds.choose_cams()[0]
        K = np.asarray(info["cam_infos"][cam]["calibrated_sensor"]["camera_intrinsic"], float)
        l2c = np.asarray(as_np(ds.load_lidar2camera_mat(lid, ds.data_root)), float).reshape(-1, 4, 4)[0]
        if not shown:
            print(f"  cloud {P.shape}, image {W}x{H}, image file key: "
                  f"{info['cam_infos'][cam].get('filename', '?')}")
            shown = True
        for b in g:
            n_gt += 1
            col3.append(b[3]); col4.append(b[4])
            m = in_box_bev(P, b)
            if m.sum() >= 5:
                with_pts += 1
                pts_per.append(int(m.sum()))
                gz = b[2] - b[5] / 2.0                       # GT bottom (geometric-centre z)
                bottom_gap.append(np.percentile(P[m, 2], 3) - gz)
            Cc = l2c @ np.r_[b[:3], 1.0]
            if Cc[2] > 0.1:
                u, v = (K @ Cc[:3])[:2] / (K @ Cc[:3])[2]
                on_img += int(0 <= u < W and 0 <= v < H)

    pts_per, gap = np.asarray(pts_per), np.asarray(bottom_gap)
    print(f"  GT cars sampled                   {n_gt}")
    print(f"  with >=5 LiDAR points in footprint {100*with_pts/max(n_gt,1):5.1f}%   "
          f"(median {int(np.median(pts_per)) if len(pts_per) else 0} points)")
    print(f"  centre projects onto the image     {100*on_img/max(n_gt,1):5.1f}%")
    print(f"  lowest points minus GT box bottom  median {np.median(gap):+.3f} m   "
          f"p25 {np.percentile(gap,25):+.3f}  p75 {np.percentile(gap,75):+.3f}")
    print("    (about 0 = points and labels agree vertically; negative = cloud sits lower)")
    print(f"  GT car tensor col3 median {np.median(col3):.2f} m, col4 median {np.median(col4):.2f} m"
          f"  -> long side is column {3 if np.median(col3) > np.median(col4) else 4}")
    try:
        import sklearn; print(f"  sklearn {sklearn.__version__} available")
    except ImportError:
        print("  sklearn not available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
