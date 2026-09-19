"""Does the converted camera calibration actually project objects onto the image?

Blanking the camera takes every class to 0.00 AP, so the camera branch is
load-bearing. That makes its geometry worth auditing: the LSS view transform
splats image features into BEV using lidar2camera and the intrinsics, so if the
converter got either wrong, camera evidence lands in the wrong BEV cells and
poisons the fused feature map everywhere -- which would look exactly like the
conjunctive, catastrophic failure we measure.

The test needs no labels beyond the ones already there: take each GT box centre,
push it through the stored calibration, and ask what fraction lands inside the
image. On a correct calibration most in-front-of-camera objects land on the
sensor. On a broken one they scatter or fall behind the camera.

Run it against both domains; the source is the control.

  python3 calib_check.py <config> --label DAIR
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--label", default="")
    ap.add_argument("--n", type=int, default=120)
    args = ap.parse_args()

    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    ds = build_dataset(cfg.data.test)
    H = cfg.data.test["dataset"]["H"]
    W = cfg.data.test["dataset"]["W"]

    tot = infront = onimg = 0
    us, vs, ds_ = [], [], []
    shown = False

    step = max(1, len(ds) // args.n)
    for i in range(0, len(ds), step):
        if tot > 4000:
            break
        info = ds.infos[i]
        cams = ds.choose_cams()
        g, _ = ds.get_gt(info, cams)
        g = as_np(g)
        if g.size == 0:
            continue
        g = g.reshape(-1, g.shape[-1])

        cam = cams[0]
        ci = info["cam_infos"][cam]
        K = np.asarray(ci["calibrated_sensor"]["camera_intrinsic"], dtype=float)
        try:
            l2c = as_np(ds.load_lidar2camera_mat(
                info["lidar_infos"]["LIDAR_TOP"]["filename"], ds.data_root))
        except Exception as e:
            print("lidar2camera load failed:", e)
            return 1
        l2c = np.asarray(l2c, dtype=float).reshape(-1, 4, 4)[0]

        if not shown:
            print(f"  image {W}x{H}   fx={K[0,0]:.1f} fy={K[1,1]:.1f} "
                  f"cx={K[0,2]:.1f} cy={K[1,2]:.1f}")
            print(f"  lidar2camera translation {np.round(l2c[:3, 3], 2)}")
            shown = True

        P = np.concatenate([g[:, :3], np.ones((len(g), 1))], axis=1)
        C = (l2c @ P.T).T[:, :3]
        tot += len(C)
        z = C[:, 2]
        ok = z > 0.1
        infront += int(ok.sum())
        if not ok.any():
            continue
        uv = (K @ C[ok].T).T
        u, v = uv[:, 0] / uv[:, 2], uv[:, 1] / uv[:, 2]
        onimg += int(((u >= 0) & (u < W) & (v >= 0) & (v < H)).sum())
        us.append(u); vs.append(v); ds_.append(z[ok])

    print(f"{args.label or args.config}")
    print(f"  GT centres tested        {tot}")
    print(f"  in front of the camera   {100*infront/max(tot,1):5.1f}%")
    print(f"  landing on the image     {100*onimg/max(tot,1):5.1f}%   "
          f"(of those in front: {100*onimg/max(infront,1):5.1f}%)")
    if us:
        u = np.concatenate(us); v = np.concatenate(vs); d = np.concatenate(ds_)
        for nm, a, hi in (("u", u, W), ("v", v, H)):
            q = np.percentile(a, [1, 25, 50, 75, 99])
            print(f"  {nm} (0..{hi}): " + "  ".join(f"p{p}={x:8.1f}"
                                                    for p, x in zip([1, 25, 50, 75, 99], q)))
        print(f"  depth   : median {np.median(d):7.1f} m")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
