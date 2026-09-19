"""Zero-shot cross-dataset evaluation with one training-free repair applied.

Same contract as eval_crossdataset.py -- a source-domain model, a target dataset,
no retraining and no target labels -- but with a switch for each intervention so
they can be swept from the queue runner without editing code.

The interventions target what the attribution experiment actually found. Recall
collapse is 84% of the Car drop (only 22.9% of target GT gets any prediction
within 2.5 m, against 76.5% in-domain), so the levers here mostly aim at getting
boxes emitted at all, not at polishing the boxes that already exist.

  --score-threshold X   the head discards proposals below 0.1 by default. If the
                        target's confidences are uniformly depressed, that floor
                        alone can erase most detections.
  --intensity-scale S   PointPillars feeds intensity in as a feature channel. The
                        Ouster on the TUMTraf mast and DAIR's sensor do not share
                        an intensity scale, so the pillar features land off the
                        training manifold.
  --intensity-const C   replace intensity with a constant, removing the channel's
                        domain dependence entirely.
  --z-shift Z           matched pairs put predicted car boxes 0.49 m below GT;
                        this shifts the input cloud instead of the output.

The model is a whole-module torch.save, so test-time thresholds are baked into
the pickled object rather than read from the config -- they are patched on the
loaded module here, and the patch is echoed so a log always states what ran.
"""
import argparse
import warnings
from functools import partial

import mmcv
import numpy as np
import torch
from mmcv.parallel import MMDataParallel
from torchpack.utils.config import configs
from mmdet3d.apis import single_gpu_test
from mmdet3d.datasets import build_dataloader, build_dataset
from mmdet3d.datasets.v2x_dataset import collate_fn
from mmdet3d.utils import recursive_eval

warnings.filterwarnings("ignore")


def patch_threshold(model, thr):
    """Lower the head's proposal floor on an already-pickled module."""
    hits = []
    root = model.module if hasattr(model, "module") else model
    for name, mod in root.named_modules():
        for attr in ("score_threshold",):
            if hasattr(mod, attr) and isinstance(getattr(mod, attr), (int, float)):
                hits.append(f"{name}.{attr}: {getattr(mod, attr)} -> {thr}")
                setattr(mod, attr, thr)
        bc = getattr(mod, "bbox_coder", None)
        if bc is not None and hasattr(bc, "score_threshold"):
            hits.append(f"{name}.bbox_coder.score_threshold: "
                        f"{bc.score_threshold} -> {thr}")
            bc.score_threshold = thr
        tc = getattr(mod, "test_cfg", None)
        if isinstance(tc, dict) and "score_threshold" in tc:
            hits.append(f"{name}.test_cfg[score_threshold]: "
                        f"{tc['score_threshold']} -> {thr}")
            tc["score_threshold"] = thr
    for h in hits:
        print("  patched", h)
    if not hits:
        print("  WARNING: no score_threshold found to patch")
    return len(hits)


def patch_blank_camera(dataset):
    """Replace every image with the training mean, deleting camera evidence.

    The two domains do not mount their cameras alike -- TUMTraf's south1 optical
    axis sits about 16 degrees further down than DAIR's -- so the camera branch
    may be feeding the fuser geometry it was never trained on and suppressing
    detections the lidar branch would otherwise make. Feeding a constant image
    is the cheapest way to ask that question: if AP rises when the camera says
    nothing, the camera was doing harm, and the repair is to gate it under shift.

    A mean-valued image is used rather than zeros because the pipeline
    normalises by (x - img_mean) / img_std, so the mean maps to exactly zero
    activation instead of a large negative one.
    """
    orig = dataset.get_image

    def wrapped(cam_infos, cams, *a, **k):
        out = orig(cam_infos, cams, *a, **k)
        items = list(out)
        imgs = items[0]
        t = imgs if torch.is_tensor(imgs) else torch.as_tensor(imgs)
        items[0] = torch.zeros_like(t)      # post-normalisation zero == the mean
        return tuple(items)

    dataset.get_image = wrapped
    print("  patched get_image: camera input blanked to the normalised mean")


def patch_points(dataset, scale=None, const=None, zshift=None, keep=None):
    """Wrap load_pcd so the input cloud is transformed before it reaches the net.

    `keep` randomly thins the cloud to that many points. It exists for the
    decisive control: TUMTraf supplies 9,508 points inside point_cloud_range
    per frame against DAIR's 37,930, so thinning DAIR to TUMTraf's density
    and re-scoring in-domain says how much of the cross-dataset collapse is
    simply sparser input rather than anything about the domain.
    """
    orig = dataset.load_pcd
    rng = np.random.default_rng(0)

    def wrapped(*a, **k):
        out = orig(*a, **k)
        pts, rest = (out[0], out[1:]) if isinstance(out, tuple) else (out, ())
        arr = pts.numpy() if torch.is_tensor(pts) else pts
        arr = np.asarray(arr)
        if arr.ndim == 2 and arr.shape[1] >= 4:
            if zshift is not None:
                arr[:, 2] += zshift
            if const is not None:
                arr[:, 3] = const
            elif scale is not None:
                arr[:, 3] *= scale
            if keep is not None and len(arr) > keep:
                arr = arr[rng.choice(len(arr), size=keep, replace=False)]
        pts = torch.from_numpy(arr) if torch.is_tensor(pts) else arr
        return (pts,) + rest if rest else pts

    dataset.load_pcd = wrapped
    print(f"  patched load_pcd (scale={scale} const={const} zshift={zshift} "
          f"keep={keep})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("checkpoint")
    ap.add_argument("--out", default="")
    ap.add_argument("--score-threshold", type=float, default=None)
    ap.add_argument("--intensity-scale", type=float, default=None)
    ap.add_argument("--intensity-const", type=float, default=None)
    ap.add_argument("--z-shift", type=float, default=None)
    ap.add_argument("--keep-points", type=int, default=None,
                    help="thin the cloud to N points (density control)")
    ap.add_argument("--blank-camera", action="store_true",
                    help="feed a constant image: is the camera branch harmful?")
    ap.add_argument("--skip-eval", action="store_true")
    args = ap.parse_args()

    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    torch.backends.cudnn.benchmark = cfg.get("cudnn_benchmark", False)

    dataset = build_dataset(cfg.data.test)
    if args.blank_camera:
        patch_blank_camera(dataset)
    if any(x is not None for x in (args.intensity_scale, args.intensity_const,
                                   args.z_shift, args.keep_points)):
        patch_points(dataset, args.intensity_scale, args.intensity_const,
                     args.z_shift, args.keep_points)

    data_loader = build_dataloader(
        dataset, samples_per_gpu=1,
        workers_per_gpu=0 if (args.intensity_scale or args.intensity_const
                              or args.z_shift or args.blank_camera
                              or args.keep_points)
        else cfg.data.get("workers_per_gpu", 4),
        dist=False, shuffle=False,
    )
    # this repo's samples are a 15-element list, not a dict; mmcv's default
    # collate cannot batch them
    data_loader.collate_fn = partial(collate_fn, is_return_depth=False)
    print(f"target dataset: {len(dataset)} frames")

    model = torch.load(args.checkpoint, map_location="cuda", weights_only=False)
    model = model.cuda().eval()
    if not isinstance(model, MMDataParallel):
        model = MMDataParallel(model, device_ids=[0])
    if not hasattr(model, "CLASSES"):
        model.CLASSES = dataset.classes
    if args.score_threshold is not None:
        patch_threshold(model, args.score_threshold)

    outputs = single_gpu_test(model, data_loader)
    n = sum(len(o["scores_3d"]) for o in outputs)
    print(f"predictions emitted: {n} ({n/max(len(outputs),1):.1f} per frame)")

    if args.out:
        mmcv.dump(outputs, args.out)
        print(f"wrote {args.out}")
    if not args.skip_eval:
        print(dataset.evaluate(outputs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
