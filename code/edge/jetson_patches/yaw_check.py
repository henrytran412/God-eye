"""Is the TUMTraf yaw error a constant offset (conversion bug) or spread (domain shift)?

A convention error gives a sharply peaked SIGNED error at some non-zero constant.
Genuine degradation gives a broad distribution centred near zero.
"""
import json, glob
import numpy as np, torch, mmcv

def gt(root, n):
    out = []
    for p in sorted(glob.glob(root + "/label/camera/*.json"))[:n]:
        b = [[float(o["3d_location"]["x"]), float(o["3d_location"]["y"]),
              float(o["rotation"])]
             for o in json.load(open(p)) if o["type"] in ("Car", "Van", "Truck")]
        out.append(np.array(b).reshape(-1, 3))
    return out

def pred(pkl, n):
    out = []
    for r in mmcv.load(pkl)[:n]:
        B = r["boxes_3d"].tensor.numpy()
        S = r["scores_3d"].numpy() if torch.is_tensor(r["scores_3d"]) else np.asarray(r["scores_3d"])
        L = r["labels_3d"].numpy() if torch.is_tensor(r["labels_3d"]) else np.asarray(r["labels_3d"])
        k = (S > 0.4) & np.isin(L, [0, 1, 3, 4])
        out.append(np.stack([B[k][:, 0], B[k][:, 1], B[k][:, 6]], axis=1) if k.any() else np.zeros((0, 3)))
    return out

def report(tag, gts, prs):
    errs = []
    for g, p in zip(gts, prs):
        if len(g) == 0 or len(p) == 0:
            continue
        d = np.linalg.norm(p[:, None, :2] - g[None, :, :2], axis=2)
        j = d.argmin(1)
        m = d[np.arange(len(p)), j] < 2.5        # tight match: same object
        if m.any():
            e = (p[m, 2] - g[j[m], 2] + np.pi) % (2 * np.pi) - np.pi
            errs.append(e)
    if not errs:
        print(f"  {tag}: no matches"); return
    e = np.concatenate(errs)
    ef = np.where(np.abs(e) > np.pi / 2, e - np.sign(e) * np.pi, e)   # fold 180 deg
    d = np.degrees(ef)
    print(f"  {tag}:  {len(d)} tight matches")
    print(f"    signed yaw err  median {np.median(d):+7.1f}  mean {d.mean():+7.1f}  std {d.std():6.1f} deg")
    print(f"    quartiles       25% {np.percentile(d,25):+7.1f}   75% {np.percentile(d,75):+7.1f} deg")
    h, edges = np.histogram(d, bins=[-90,-60,-30,-15,-5,5,15,30,60,90])
    print("    histogram " + "  ".join(f"[{int(edges[i])},{int(edges[i+1])}):{h[i]}" for i in range(len(h))))

N = 600
print("Signed yaw error, vehicles, tight (<2.5 m) matches")
report("TUMTraf INT8", gt("/home/sjsujetson/data/tumtraf-dair", N),
       pred("/home/sjsujetson/godeye/out/tumtraf/tumtraf_int8_outputs.pkl", N))
report("DAIR    INT8", gt("/home/sjsujetson/data/dair-v2x/single-infrastructure-side", N),
       pred("/home/sjsujetson/godeye/out/trackB/ptq_outputs.pkl", N))
