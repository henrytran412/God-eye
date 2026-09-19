"""How much AP would come back if ONE predicted quantity were perfect?

This is the monodle sub-task attribution protocol (CVPR 2021) applied across a
domain gap instead of in-domain. For each predicted box we find its nearest
ground-truth box and overwrite exactly one field -- yaw, or centre, or size --
with the true value, leaving every other field as the network produced it. Then
we re-score. The AP that comes back is the ceiling that fixing that one
component could ever reach, and so the budget available to any repair aimed at
that component.

Nothing here touches the network: no GPU, no training, no retraining. It reads
the pickles the eval scripts already wrote.

  python3 gt_substitution.py <config> <outputs.pkl> --fields yaw center size

GT comes from V2XDataset.get_gt(), which rebuilds boxes from the info file via a
quaternion. The prediction head uses its own yaw convention, and a 90 degree
offset between the two would silently turn this experiment into noise -- so
--check first reports the signed yaw error over matched pairs and refuses to
continue if the median is far from zero. yaw_check.py already established that
the honest value is about -0.2 degrees in both domains.

Note on yaw: rotated-box IoU is invariant under a 180 degree rotation (a
rectangle maps onto itself), so the ceiling measured for yaw is a ceiling on
*half-range* heading error. A repair that leaves front/back ambiguous therefore
costs nothing in AP -- which is what makes a geometric refit worth trying.
"""
import argparse
import copy
import warnings

import mmcv
import numpy as np
import torch
from torchpack.utils.config import configs
from mmdet3d.datasets import build_dataset
from mmdet3d.utils import recursive_eval

warnings.filterwarnings("ignore")

MATCH_RADIUS = 2.5      # metres in BEV; the tight criterion yaw_check.py uses
MAX_MEDIAN_DEG = 5.0    # refuse to substitute if conventions disagree by more


def gt_for(dataset, i):
    """(N, >=7) ground-truth boxes for frame i in the same frame as predictions."""
    try:
        boxes, _ = dataset.get_gt(dataset.infos[i], dataset.choose_cams())
    except Exception:
        return None
    g = boxes.numpy() if torch.is_tensor(boxes) else np.asarray(boxes)
    return g.reshape(-1, g.shape[-1]) if g.size else np.zeros((0, 9))


def match(pred, gt):
    """Nearest-GT assignment in BEV. Returns (mask over pred, index into gt)."""
    if gt is None or len(gt) == 0 or len(pred) == 0:
        return None, None
    d = np.linalg.norm(pred[:, None, :2] - gt[None, :, :2], axis=2)
    j = d.argmin(1)
    m = d[np.arange(len(pred)), j] < MATCH_RADIUS
    return (m, j) if m.any() else (None, None)


def convention_check(dataset, outputs):
    """Signed yaw error over matched pairs -- a sanity gate, not a result."""
    errs = []
    for i, r in enumerate(outputs):
        p = r["boxes_3d"].tensor.numpy()
        m, j = match(p, gt_for(dataset, i))
        if m is None:
            continue
        e = (p[m, 6] - gt_for(dataset, i)[j[m], 6] + np.pi) % (2 * np.pi) - np.pi
        errs.append(np.where(np.abs(e) > np.pi / 2, e - np.sign(e) * np.pi, e))
    if not errs:
        return None, 0
    d = np.degrees(np.concatenate(errs))
    return float(np.median(d)), len(d)


def substitute(pred, gt, fields):
    m, j = match(pred, gt)
    if m is None:
        return 0
    src = gt[j[m]]
    if "yaw" in fields:
        pred[m, 6] = src[:, 6]
    if "center" in fields:
        pred[m, 0:2] = src[:, 0:2]
        # V2XDataset.get_gt builds boxes from a nuScenes Box, whose centre is the
        # GEOMETRIC centre; the prediction head's z is the BOTTOM face. Copying z
        # across raises every box by h/2, which leaves BEV IoU untouched and
        # drives 3D IoU to zero -- measured, not assumed: match_stats.py puts the
        # pedestrian residual at 0.00 m once h/2 is removed.
        pred[m, 2] = src[:, 2] - src[:, 5] / 2.0
    if "size" in fields:
        pred[m, 3:6] = src[:, 3:6]
    return int(m.sum())


def run(dataset, outputs, fields):
    out = copy.deepcopy(outputs)
    total = 0
    for i, r in enumerate(out):
        t = r["boxes_3d"].tensor.numpy().copy()
        total += substitute(t, gt_for(dataset, i), fields)
        r["boxes_3d"].tensor = torch.from_numpy(t)
    return out, total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("outputs", help="pickle written by eval_crossdataset.py --out")
    ap.add_argument("--fields", nargs="+", default=["yaw", "center", "size"])
    ap.add_argument("--also-all", action="store_true",
                    help="additionally substitute every field at once")
    ap.add_argument("--limit", type=int, default=0,
                    help="use only the first N frames (smoke test)")
    ap.add_argument("--check-only", action="store_true",
                    help="run the convention gate and stop")
    args = ap.parse_args()

    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    dataset = build_dataset(cfg.data.test)
    outputs = mmcv.load(args.outputs)
    if args.limit:
        outputs = outputs[: args.limit]
    print(f"{len(dataset)} frames in dataset, {len(outputs)} results in use\n")

    g0 = gt_for(dataset, 0)
    if g0 is None:
        print("ERROR: dataset.get_gt() failed; cannot substitute.")
        return 1
    print(f"GT box width: {g0.shape[1]} columns (expect >=7: x y z dx dy dz yaw)")

    med, n = convention_check(dataset, outputs)
    if med is None:
        print("ERROR: no prediction matched a GT box. Frame ordering is probably "
              "misaligned between the pickle and dataset.infos.")
        return 1
    print(f"convention gate: median signed yaw error {med:+.2f} deg over {n} "
          f"matched pairs")
    if abs(med) > MAX_MEDIAN_DEG:
        print(f"ABORT: |median| > {MAX_MEDIAN_DEG} deg, so GT yaw and predicted yaw "
              f"do not share a convention. Substituting would measure the offset, "
              f"not the domain gap.")
        return 1
    print("gate passed: GT and predictions share a yaw convention.\n")
    if args.check_only:
        return 0

    print("=" * 62)
    print("baseline (nothing substituted)")
    print("=" * 62, flush=True)
    print(dataset.evaluate(outputs))

    runs = [[f] for f in args.fields]
    if args.also_all:
        runs.append(list(args.fields))
    for fields in runs:
        print("\n" + "=" * 62)
        print(f"ground truth substituted for: {', '.join(fields)}")
        print("=" * 62, flush=True)
        sub, k = run(dataset, outputs, fields)
        print(f"({k} predictions matched a GT box within {MATCH_RADIUS} m)")
        print(dataset.evaluate(sub))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
