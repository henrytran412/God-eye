"""Run a COCO-pretrained YOLO over a dataset's camera images and cache the 2D boxes.

YOLO was trained on neither DAIR-V2X-I nor TUMTraf, which is the point: it is the
frozen foundation-model half of a gaussian4d-style label-free teacher, so its errors
do not inherit the source domain's bias. Caching separates the slow GPU pass from the
LiDAR fitting that gets iterated on.

Writes {frame_index: [[x1, y1, x2, y2, conf, coco_class], ...]} to --out as JSON,
keyed by the dataset's own frame order so it lines up with the prediction pickles.

  python3 cache_yolo.py <config> --weights yolo11m.pt --out yolo.json [--limit N]
"""
import argparse
import json
import os
import time
import warnings

import mmcv
from torchpack.utils.config import configs
from mmdet3d.datasets import build_dataset
from mmdet3d.utils import recursive_eval

warnings.filterwarnings("ignore")

VEHICLE = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}   # COCO ids worth keeping


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--weights", default="yolo11m.pt")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--conf", type=float, default=0.15)
    args = ap.parse_args()

    from ultralytics import YOLO
    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    ds = build_dataset(cfg.data.test)
    model = YOLO(args.weights)

    n = len(ds) if not args.limit else min(args.limit, len(ds))
    out, t0, boxes = {}, time.time(), 0
    for i in range(n):
        cam = ds.choose_cams()[0]
        img = os.path.join(ds.data_root, ds.infos[i]["cam_infos"][cam]["filename"])
        r = model.predict(img, conf=args.conf, classes=list(VEHICLE), verbose=False)[0]
        b = r.boxes
        rows = [[*map(float, xyxy), float(c), int(k)]
                for xyxy, c, k in zip(b.xyxy.cpu().numpy(), b.conf.cpu().numpy(),
                                      b.cls.cpu().numpy())]
        out[i] = rows
        boxes += len(rows)
        if i % 200 == 0:
            print(f"  {i}/{n}  {boxes} boxes so far  {(i+1)/(time.time()-t0):.1f} img/s",
                  flush=True)
    json.dump(out, open(args.out, "w"))
    print(f"wrote {args.out}: {n} frames, {boxes} vehicle boxes "
          f"({boxes/max(n,1):.1f}/frame), {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
