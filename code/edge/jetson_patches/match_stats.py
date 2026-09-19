"""Are predictions and GT even comparable? Counts, z convention, size gap.

gt_substitution.py produced two things that need explaining before any of its
numbers mean anything:

  1. Substituting GT centre drove 3D AP to zero while BEV AP went UP. BEV ignores
     height, so that is the signature of a z-convention mismatch -- most likely
     nuScenes Box centre (geometric centre) versus mmdet3d LiDARInstance3DBoxes
     (bottom centre), which differ by h/2.
  2. Substituting GT yaw barely moved AP, which contradicts the yaw diagnosis.
     That could be real, or it could mean hardly any prediction matched a GT box
     in the first place, in which case substitution cannot reveal anything.

This measures both, plus the per-class size gap between the two domains, which
is the quantity ROS and SN both target.

  python3 match_stats.py <config> <outputs.pkl> [--limit N]
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

RADII = (1.0, 2.5, 5.0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("outputs")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--score", type=float, default=0.0,
                    help="drop predictions below this score first")
    args = ap.parse_args()

    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    dataset = build_dataset(cfg.data.test)
    outputs = mmcv.load(args.outputs)
    if args.limit:
        outputs = outputs[: args.limit]

    classes = list(dataset.classes)
    n_pred = n_gt = 0
    matched = {r: 0 for r in RADII}
    # accumulate per predicted-class so car statistics are not diluted by
    # pedestrians, which are a third the width and would drag every median down
    per = {}

    for i, r in enumerate(outputs):
        p = r["boxes_3d"].tensor.numpy()
        s = r["scores_3d"].numpy() if torch.is_tensor(r["scores_3d"]) \
            else np.asarray(r["scores_3d"])
        lab = r["labels_3d"].numpy() if torch.is_tensor(r["labels_3d"]) \
            else np.asarray(r["labels_3d"])
        if args.score > 0:
            keep = s >= args.score
            p, lab = p[keep], lab[keep]
        g, gl = dataset.get_gt(dataset.infos[i], dataset.choose_cams())
        g = g.numpy() if torch.is_tensor(g) else np.asarray(g)
        gl = gl.numpy() if torch.is_tensor(gl) else np.asarray(gl)
        g = g.reshape(-1, g.shape[-1]) if g.size else np.zeros((0, 9))
        n_pred += len(p)
        n_gt += len(g)
        if len(p) == 0 or len(g) == 0:
            continue
        d = np.linalg.norm(p[:, None, :2] - g[None, :, :2], axis=2)
        j = d.argmin(1)
        near = d[np.arange(len(p)), j]
        for rad in RADII:
            matched[rad] += int((near < rad).sum())
        m = near < 2.5
        if not m.any():
            continue
        src, sl = g[j[m]], gl[j[m]]
        e = (p[m, 6] - src[:, 6] + np.pi) % (2 * np.pi) - np.pi
        e = np.where(np.abs(e) > np.pi / 2, e - np.sign(e) * np.pi, e)
        for k, cls in enumerate(lab[m]):
            if cls != sl[k]:          # class disagrees: not a like-for-like pair
                continue
            b = per.setdefault(int(cls), {"dz": [], "dzh": [], "yaw": [],
                                          "p": [], "g": []})
            b["dz"].append(src[k, 2] - p[m][k, 2])
            # if GT z is a geometric centre and predictions are bottom
            # centre, this residual should sit at zero
            b.setdefault("dzc", []).append(
                (src[k, 2] - src[k, 5] / 2.0) - p[m][k, 2])
            b["dzh"].append((src[k, 2] - p[m][k, 2]) / max(src[k, 5], 1e-6))
            b["yaw"].append(e[k])
            b["p"].append(p[m][k, 3:6])
            b["g"].append(src[k, 3:6])

    print(f"frames            {len(outputs)}")
    print(f"predictions       {n_pred}   ({n_pred/len(outputs):.1f} per frame)")
    print(f"ground-truth objs {n_gt}   ({n_gt/len(outputs):.1f} per frame)")
    print()
    for rad in RADII:
        print(f"predictions within {rad:>4} m of a GT box: {matched[rad]:6d} "
              f"({100*matched[rad]/max(n_pred,1):5.1f}% of predictions, "
              f"{100*matched[rad]/max(n_gt,1):5.1f}% of GT)")

    if not per:
        print("\nno same-class matches -- nothing further to report")
        return 1

    print("\nper class, same-class pairs matched within 2.5 m")
    print(f"{'class':<14}{'n':>6}{'dz med':>9}{'dz/h':>7}"
          f"{'yaw med':>9}{'yaw std':>9}{'+-5deg':>8}"
          f"{'dx p/GT':>9}{'dy p/GT':>9}{'dz p/GT':>9}{'z-h/2 res':>10}")
    print("-" * 99)
    for cid in sorted(per):
        b = per[cid]
        dz = np.asarray(b["dz"])
        dy = np.degrees(np.asarray(b["yaw"]))
        P, G = np.asarray(b["p"]), np.asarray(b["g"])
        ratios = [np.median(P[:, k]) / max(np.median(G[:, k]), 1e-6) for k in range(3)]
        dzc = np.asarray(b["dzc"])
        print(f"{classes[cid][:14]:<14}{len(dz):>6}{np.median(dz):>+9.3f}"
              f"{np.median(b['dzh']):>+7.2f}{np.median(dy):>+9.2f}{dy.std():>9.2f}"
              f"{100*(np.abs(dy) < 5).mean():>7.1f}%"
              + "".join(f"{r:>9.3f}" for r in ratios)
              + f"{np.median(dzc):>+10.3f}")
    print("\ndz med  = GT z minus predicted z, metres. dz/h is that over GT height:")
    print("          about +0.5 would mean a bottom-centre vs geometric-centre")
    print("          convention gap; anything else is a real elevation error.")
    print("dx/dy/dz p/GT = predicted extent over true extent. 1.000 is correct;")
    print("          below 1 means the detector draws boxes too small.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
