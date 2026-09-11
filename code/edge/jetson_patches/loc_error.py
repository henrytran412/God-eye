"""Decompose localisation error: match each prediction to its nearest GT and
report systematic centre offset, size ratio and yaw difference, per domain.

A uniform bias (e.g. a residual z offset or a yaw convention mismatch) shows up
as a non-zero median here, and would explain AP that survives IoU 0.25 but dies
at IoU 0.5 without the detector actually being blind.
"""
import json, glob, sys
import numpy as np, torch, mmcv

def gt_boxes(root, n):
    out = []
    for p in sorted(glob.glob(root + "/label/camera/*.json"))[:n]:
        b = []
        for o in json.load(open(p)):
            if o["type"] not in ("Car", "Van", "Truck"):
                continue
            d, L = o["3d_dimensions"], o["3d_location"]
            b.append([float(L["x"]), float(L["y"]), float(L["z"]),
                      float(d["l"]), float(d["w"]), float(d["h"]), float(o["rotation"])])
        out.append(np.array(b).reshape(-1, 7))
    return out

def pred_boxes(pkl, n):
    o = mmcv.load(pkl)[:n]
    out = []
    for r in o:
        B = r["boxes_3d"].tensor.numpy()
        S = r["scores_3d"].numpy() if torch.is_tensor(r["scores_3d"]) else np.asarray(r["scores_3d"])
        L = r["labels_3d"].numpy() if torch.is_tensor(r["labels_3d"]) else np.asarray(r["labels_3d"])
        k = (S > 0.3) & np.isin(L, [0, 1, 3, 4])      # car/truck/bus/trailer
        out.append(B[k])
    return out

def report(tag, gts, prs):
    dx = dy = dz = []
    D, Sz, Yw = [], [], []
    for g, p in zip(gts, prs):
        if len(g) == 0 or len(p) == 0:
            continue
        # nearest GT in BEV for each prediction
        d = np.linalg.norm(p[:, None, :2] - g[None, :, :2], axis=2)
        j = d.argmin(1)
        m = d[np.arange(len(p)), j] < 4.0          # plausible matches only
        if not m.any():
            continue
        pp, gg = p[m], g[j[m]]
        D.append(pp[:, :3] - gg[:, :3])
        Sz.append(pp[:, 3:6] / np.maximum(gg[:, 3:6], 1e-6))
        dyaw = (pp[:, 6] - gg[:, 6] + np.pi) % (2 * np.pi) - np.pi
        Yw.append(np.minimum(np.abs(dyaw), np.abs(np.abs(dyaw) - np.pi)))  # 180-deg agnostic
    if not D:
        print(f"  {tag}: no matches"); return
    D = np.concatenate(D); Sz = np.concatenate(Sz); Yw = np.concatenate(Yw)
    print(f"  {tag}:  {len(D)} matched pairs")
    print(f"    centre offset median  dx {np.median(D[:,0]):+.2f}  dy {np.median(D[:,1]):+.2f}  dz {np.median(D[:,2]):+.2f} m")
    print(f"    |offset| median       {np.median(np.linalg.norm(D,axis=1)):.2f} m   BEV {np.median(np.linalg.norm(D[:,:2],axis=1)):.2f} m")
    print(f"    size ratio median     l {np.median(Sz[:,0]):.2f}  w {np.median(Sz[:,1]):.2f}  h {np.median(Sz[:,2]):.2f}")
    print(f"    |yaw err| median      {np.degrees(np.median(Yw)):.1f} deg")

N = 600
print("Vehicle-class localisation error, predictions vs nearest GT")
report("TUMTraf", gt_boxes("/home/sjsujetson/data/tumtraf-dair", N),
       pred_boxes("/home/sjsujetson/godeye/out/tumtraf/tumtraf_fp16_outputs.pkl", N))
report("DAIR   ", gt_boxes("/home/sjsujetson/data/dair-v2x/single-infrastructure-side", N),
       pred_boxes("/home/sjsujetson/godeye/out/trackB/fp16_outputs.pkl", N))
