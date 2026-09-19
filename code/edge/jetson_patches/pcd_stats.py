"""Compare the raw lidar input between the two domains.

PointPillars consumes (x, y, z, intensity) directly, so any of those four
channels landing on a different scale puts the pillar features off the manifold
the network was trained on -- a plausible cause of the detection collapse that
costs nothing to check. This reads clouds through the dataset's own loader, so
whatever normalisation the pipeline applies is included.

Run before spending GPU time on intensity or z-shift sweeps: if the channels
already agree, those experiments are not worth queueing.

  python3 pcd_stats.py <config> [--n 60]
"""
import argparse
import warnings

import mmcv
import numpy as np
import torch
from torchpack.utils.config import configs
from mmdet3d.datasets import build_dataset
from mmdet3d.utils import recursive_eval

warnings.filterwarnings("ignore")

PCTS = (1, 25, 50, 75, 99)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    ds = build_dataset(cfg.data.test)

    counts, chunks = [], []
    step = max(1, len(ds) // args.n)
    for i in range(0, len(ds), step):
        if len(counts) >= args.n:
            break
        info = ds.infos[i]
        try:
            out = ds.load_pcd(__import__("os").path.join(
                ds.data_root, info["lidar_infos"]["LIDAR_TOP"]["filename"]))
        except Exception as e:
            print("  load failed:", e)
            continue
        pts = out[0] if isinstance(out, tuple) else out
        a = np.asarray(pts.numpy() if torch.is_tensor(pts) else pts)
        if a.ndim != 2 or a.shape[1] < 4:
            continue
        counts.append(len(a))
        chunks.append(a[np.random.default_rng(0).choice(
            len(a), size=min(4000, len(a)), replace=False)])

    if not chunks:
        print("no clouds read")
        return 1
    A = np.concatenate(chunks)
    rng = np.linalg.norm(A[:, :2], axis=1)

    print(f"{args.label or args.config}")
    print(f"  frames sampled   {len(counts)}")
    print(f"  points per frame median {int(np.median(counts)):,}  "
          f"min {min(counts):,}  max {max(counts):,}")
    for name, v in (("x", A[:, 0]), ("y", A[:, 1]), ("z", A[:, 2]),
                    ("intensity", A[:, 3]), ("range", rng)):
        q = np.percentile(v, PCTS)
        print(f"  {name:<10}" + "  ".join(f"p{p}={x:8.3f}" for p, x in zip(PCTS, q)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
