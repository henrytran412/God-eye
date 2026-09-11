"""Zero-shot cross-dataset evaluation: a model saved on the source domain, run on a target.

This deliberately does NOT re-quantise or re-calibrate on the target. ptq.pth was
calibrated on DAIR-V2X-I, and that is the whole point of the experiment: PTQ picks
per-tensor dynamic ranges from a calibration set drawn from the SOURCE domain, so
under domain shift the target's activations can fall outside those ranges and
saturate. Recalibrating on the target would erase the very effect being measured.

  python3 eval_crossdataset.py <config> <model.pth> --out results.pkl

<model.pth> is a whole-model torch.save (what ptq_v2xfusion.py writes at line 250),
so the architecture comes from the checkpoint and the config supplies only the
dataset. Dataset and evaluator are identical to the in-domain run, so any
difference in the numbers comes from the data rather than the code path.
"""
import argparse
import warnings
from functools import partial

import mmcv
import torch
from mmcv.parallel import MMDataParallel
from torchpack.utils.config import configs
from mmdet3d.apis import single_gpu_test
from mmdet3d.datasets import build_dataloader, build_dataset
from mmdet3d.datasets.v2x_dataset import collate_fn
from mmdet3d.utils import recursive_eval

warnings.filterwarnings("ignore")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("checkpoint", help="whole-model .pth saved by ptq/fp16 script")
    ap.add_argument("--out", default="", help="pickle the raw outputs before evaluating")
    ap.add_argument("--skip-eval", action="store_true",
                    help="write outputs only; score them offline")
    args = ap.parse_args()

    configs.load(args.config, recursive=True)
    cfg = mmcv.Config(recursive_eval(configs), filename=args.config)
    torch.backends.cudnn.benchmark = cfg.get("cudnn_benchmark", False)

    dataset = build_dataset(cfg.data.test)
    data_loader = build_dataloader(
        dataset,
        samples_per_gpu=1,
        workers_per_gpu=cfg.data.get("workers_per_gpu", 4),
        dist=False,
        shuffle=False,
    )
    # This repo's samples are a 15-element list, not a dict; mmcv's default collate
    # cannot batch them. Use the same collate the in-domain eval uses
    # (eval_fp16_v2xfusion.py:210) so both runs share one code path.
    data_loader.collate_fn = partial(collate_fn, is_return_depth=False)
    print(f"target dataset: {len(dataset)} frames")

    # Whole-model load. weights_only=False is required because the checkpoint is a
    # pickled nn.Module, not a state_dict; it is a file we produced ourselves.
    model = torch.load(args.checkpoint, map_location="cuda", weights_only=False)
    model = model.cuda().eval()
    if not isinstance(model, MMDataParallel):
        model = MMDataParallel(model, device_ids=[0])
    if not hasattr(model, "CLASSES"):
        model.CLASSES = dataset.classes

    outputs = single_gpu_test(model, data_loader)

    if args.out:
        print(f"writing raw outputs to {args.out}")
        mmcv.dump(outputs, args.out)

    if not args.skip_eval:
        print(dataset.evaluate(outputs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
