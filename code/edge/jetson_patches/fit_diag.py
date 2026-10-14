"""Where does the LiDAR fitter go wrong? Pair every oracle fit with its source GT car.

With perfect 2D boxes the teacher reaches only 13.93 centre-distance AP although it
fits a box for 74% of cars, so most fitted boxes must land metres from the car they
were cut from. This follows each GT car through the pipeline and reports where the
evidence is lost:

  frustum   points projecting inside the 2D box
  kept      after removing ground and structure above 3 m
  cluster   the DBSCAN cluster the fitter chose
  and how far the cluster's centroid, and the final box, sit from the GT centre.

If the chosen cluster's centroid is already far from the GT centre, the fitter picked
the wrong object (background in the frustum); if the centroid is close but the box is
far, the rectangle or the extension step moved it.

  python3 fit_diag.py <config> [--n 120]
"""
import argparse
import os
import warnings

import mmcv
import numpy as np
from sklearn.cluster import DBSCAN
from torchpack.utils.config import configs
from mmdet3d.datasets import build_dataset
from mmdet3d.utils import recursive_eval

import label_free_teacher as lft

warnings.filterwarnings("ignore")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--n", type=int, default=120)
    args = ap.parse_args()
    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    ds = build_dataset(cfg.data.test)
    car = list(ds.classes).index("car")
    H, W = cfg.data.test["dataset"]["H"], cfg.data.test["dataset"]["W"]

    rows = []
    for i in range(0, len(ds), max(1, len(ds) // args.n)):
        info = ds.infos[i]
        lid = info["lidar_infos"]["LIDAR_TOP"]["filename"]
        o = ds.load_pcd(os.path.join(ds.data_root, lid))
        P = lft.as_np(o[0] if isinstance(o, tuple) else o)[:, :3].astype(np.float64)
        cam = ds.choose_cams()[0]
        K = np.asarray(info["cam_infos"][cam]["calibrated_sensor"]["camera_intrinsic"], float)
        l2c = np.asarray(lft.as_np(ds.load_lidar2camera_mat(lid, ds.data_root)), float).reshape(-1, 4, 4)[0]
        Pc = (l2c @ np.c_[P, np.ones(len(P))].T).T[:, :3]
        front = Pc[:, 2] > 0.5
        uv = np.full((len(P), 2), -1e9)
        uv[front] = (K @ Pc[front].T).T[:, :2] / Pc[front, 2:3]
        gmap = lft.ground_map(P)
        gfb = float(np.percentile(P[:, 2], 5))
        g, gl = ds.get_gt(info, ds.choose_cams())
        g, gl = lft.as_np(g), lft.as_np(gl)
        if not g.size:
            continue
        for b in g.reshape(-1, g.shape[-1])[gl == car]:
            cc = (l2c @ np.c_[lft.corners_gt(b), np.ones(8)].T).T[:, :3]
            if (cc[:, 2] <= 0.5).any():
                continue
            q = (K @ cc.T).T[:, :2] / cc[:, 2:3]
            x1, y1 = np.clip(q.min(0), 0, [W - 1, H - 1]); x2, y2 = np.clip(q.max(0), 0, [W - 1, H - 1])
            if x2 - x1 <= 4 or y2 - y1 <= 4:
                continue
            mx, my = 0.08 * (x2 - x1), 0.08 * (y2 - y1)
            sel = (uv[:, 0] >= x1 + mx) & (uv[:, 0] <= x2 - mx) & (uv[:, 1] >= y1 + my) & (uv[:, 1] <= y2 - my)
            F = P[sel]
            r = dict(frustum=len(F), kept=0, cluster=0, cdist=np.nan, bdist=np.nan,
                     gdist=float(np.linalg.norm(b[:2])), ingt=int(lft.in_box_bev(P, b).sum())
                     if hasattr(lft, "in_box_bev") else -1)
            if len(F) >= 5:
                gz = lft.ground_at(gmap, np.median(F[:, :2], axis=0), gfb)
                Fk = F[(F[:, 2] > gz + 0.25) & (F[:, 2] < gz + 3.0)]
                r["kept"] = len(Fk)
                if len(Fk) >= 5:
                    lab = DBSCAN(eps=0.9, min_samples=4).fit_predict(Fk[:, :3])
                    if (lab >= 0).any():
                        C = Fk[lab == np.bincount(lab[lab >= 0]).argmax()]
                        r["cluster"] = len(C)
                        r["cdist"] = float(np.linalg.norm(C[:, :2].mean(0) - b[:2]))
                        # how far is the frustum's nearest-to-camera cluster, as an alternative?
                        bx = lft.fit_box(F, gmap, gfb, 0.0)
                        if bx is not None:
                            r["bdist"] = float(np.linalg.norm(bx[:2] - b[:2]))
            rows.append(r)

    import collections
    k = lambda key: np.array([x[key] for x in rows], float)
    fr, ke, cl, cd, bd = k("frustum"), k("kept"), k("cluster"), k("cdist"), k("bdist")
    n = len(rows)
    print(f"GT cars traced: {n}")
    print(f"  frustum >=5 pts {100*(fr>=5).mean():5.1f}%   median frustum {np.median(fr):.0f} pts")
    print(f"  kept    >=5 pts {100*(ke>=5).mean():5.1f}%   median kept {np.median(ke):.0f} pts")
    print(f"  got a cluster   {100*(cl>=5).mean():5.1f}%   median cluster {np.median(cl[cl>0]) if (cl>0).any() else 0:.0f} pts")
    ok = ~np.isnan(cd)
    if ok.any():
        print(f"  cluster centroid -> GT centre: median {np.nanmedian(cd):.2f} m   "
              f"<2 m {100*(cd[ok]<2).mean():.1f}%   >4 m {100*(cd[ok]>4).mean():.1f}%")
    okb = ~np.isnan(bd)
    if okb.any():
        print(f"  fitted box     -> GT centre: median {np.nanmedian(bd):.2f} m   "
              f"<2 m {100*(bd[okb]<2).mean():.1f}%   >4 m {100*(bd[okb]>4).mean():.1f}%")
    print(f"  frustum-to-cluster ratio (how much of the frustum was background): "
          f"median {np.nanmedian(cl[cl>0]/fr[cl>0]):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
