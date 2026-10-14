"""Car AP by BEV centre distance — the nuScenes metric, on any V2XDataset pickle.

The project scores Car by 3D IoU >= 0.5, the strictest standard metric, and so reads
1.83 AP cross-domain. Prof. Liu's ngperception TUTORIAL reports detection by nuScenes
centre distance instead, where the same model can read three times higher than by IoU
(car 0.467 by centre distance against 0.157 by IoU 0.5 on his full nuScenes run). This
scores our predictions his way so the two can be compared at all.

Matching follows nuscenes-devkit: predictions in descending score, each takes the
nearest still-unmatched GT of the class within the threshold; precision is sampled at
101 recall points, the region below recall 0.1 dropped, 0.1 subtracted from precision
and clipped, and the mean renormalised by 0.9. Thresholds 0.5 / 1 / 2 / 4 m, averaged.

Centre distance ignores height, size and heading entirely, so it is NOT a fix for the
IoU number. It answers a different question: does the detector put a car-labelled box
near each car?

  python3 cd_ap.py <config> <outputs.pkl> [--start N] [--cls car]
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

THRESHOLDS = (0.5, 1.0, 2.0, 4.0)
MIN_RECALL = MIN_PRECISION = 0.1


def as_np(x):
    return x.numpy() if torch.is_tensor(x) else np.asarray(x)


def nusc_ap(scores, frames, xy, gts, thr):
    """nuScenes accumulate + calc_ap for one class at one distance threshold."""
    npos = sum(len(g) for g in gts.values())
    if npos == 0 or len(scores) == 0:
        return 0.0
    taken = {f: np.zeros(len(g), bool) for f, g in gts.items()}
    tp = np.zeros(len(scores)); fp = np.zeros(len(scores))
    for k, i in enumerate(np.argsort(-scores, kind="stable")):
        g = gts.get(frames[i])
        if g is None or len(g) == 0:
            fp[k] = 1; continue
        d = np.linalg.norm(g - xy[i], axis=1)
        d[taken[frames[i]]] = np.inf
        j = int(np.argmin(d))
        if d[j] < thr:
            tp[k] = 1; taken[frames[i]][j] = True
        else:
            fp[k] = 1
    tp, fp = np.cumsum(tp), np.cumsum(fp)
    prec = tp / np.maximum(tp + fp, 1e-9)
    rec = tp / npos
    rec_i = np.linspace(0, 1, 101)
    prec_i = np.interp(rec_i, rec, prec, right=0)
    prec_i = prec_i[round(100 * MIN_RECALL) + 1:] - MIN_PRECISION
    prec_i[prec_i < 0] = 0
    return float(np.mean(prec_i)) / (1.0 - MIN_PRECISION)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("outputs")
    ap.add_argument("--start", type=int, default=0,
                    help="offset of the dataset's first frame inside the pickle")
    ap.add_argument("--cls", default="car",
                    help="class name, or a comma list merged into one class")
    ap.add_argument("--confusion", action="store_true",
                    help="for each GT object, the label of the nearest prediction within 2 m")
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    ds = build_dataset(cfg.data.test)
    outs = mmcv.load(args.outputs)[args.start:args.start + len(ds)]
    assert len(outs) == len(ds), f"{len(outs)} results vs {len(ds)} frames"
    pcr = cfg.point_cloud_range
    names = args.cls.split(",")
    cls_ids = [list(ds.classes).index(n) for n in names]
    conf = {}

    def in_range(a):
        return (a[:, 0] >= pcr[0]) & (a[:, 0] <= pcr[3]) & (a[:, 1] >= pcr[1]) & (a[:, 1] <= pcr[4])

    gts, S, F, XY = {}, [], [], []
    for i, r in enumerate(outs):
        g, gl = ds.get_gt(ds.infos[i], ds.choose_cams())
        g, gl = as_np(g), as_np(gl)
        g = g.reshape(-1, g.shape[-1])[np.isin(gl, cls_ids)] if g.size else np.zeros((0, 9))
        gts[i] = g[in_range(g)][:, :2] if len(g) else np.zeros((0, 2))
        b = as_np(r["boxes_3d"].tensor); s = as_np(r["scores_3d"]); l = as_np(r["labels_3d"])
        if args.confusion and len(g):
            for gx in g[in_range(g)][:, :2]:
                d = np.linalg.norm(b[:, :2] - gx, axis=1) if len(b) else np.array([])
                key = ds.classes[int(l[d.argmin()])] if len(d) and d.min() < 2.0 else "(nothing within 2 m)"
                conf[key] = conf.get(key, 0) + 1
        k = np.isin(l, cls_ids)
        b, s = b[k], s[k]
        if len(b):
            m = in_range(b); b, s = b[m], s[m]
        S.append(s); XY.append(b[:, :2] if len(b) else np.zeros((0, 2))); F += [i] * len(s)
    S, XY, F = np.concatenate(S), np.concatenate(XY), np.asarray(F)
    per = [nusc_ap(S, F, XY, gts, t) for t in THRESHOLDS]

    print(f"{args.label or args.outputs}  [{len(ds)} frames, "
          f"{sum(len(g) for g in gts.values())} GT {args.cls}, {len(S)} predictions]")
    print("  " + "  ".join(f"@{t:g}m {100*a:6.2f}" for t, a in zip(THRESHOLDS, per))
          + f"   | mean CD-AP {100*np.mean(per):6.2f}")
    if conf:
        tot = sum(conf.values())
        print(f"  nearest prediction to each GT {args.cls}:")
        for k_, v in sorted(conf.items(), key=lambda kv: -kv[1]):
            print(f"    {k_:<22} {v:6d}  {100*v/tot:5.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
