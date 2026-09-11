# Jetson artifacts (kept locally, gitignored — too large for git)

Pulled off the Orin Nano before it was unplugged. Nothing here is in version control;
this file records what exists and what it would cost to recreate.

| path | size | cost to recreate |
|---|---|---|
| `wheels/mmcv_full-1.7.2-cp312-cp312-linux_aarch64.whl` | 29 MB | **~25 min compile** on the Jetson |
| `models/ptq.pth` | 145 MB | ~22 min (PTQ calibrate + eval) |
| `models/fp16_ref.pth` | 145 MB | ~22 min |
| `detections/fp16_outputs.pkl` | 5.2 MB | ~11 min (DAIR FP16 inference) |
| `detections/ptq_outputs.pkl` | 5.2 MB | ~23 min (DAIR INT8 inference) |
| `detections/tumtraf_fp16_outputs.pkl` | 3.7 MB | ~11 min |
| `detections/tumtraf_int8_outputs.pkl` | 3.8 MB | ~23 min |
| `out/` | 32 MB | run logs; the AP tables are committed separately |

The **wheel is the single most valuable item**: mmcv-full 1.7.2 compiled against torch 2.6
on aarch64/JetPack 7. That build is not available anywhere publicly and took 291 source
files to compile.

The **detection pickles matter more than the models** for analysis: any re-scoring
(different IoU thresholds, per-weather breakdown, the lane-heading check against the yaw
error clusters) runs on these in seconds, with no Jetson needed.

Datasets are deliberately not kept: TUMTraf 9.1 GB, converted 2.2 GB, KITTI 3.3 GB,
DAIR 7.2 GB. All regenerate from `raw/dataset/` via
`code/edge/jetson_patches/tumtraf_to_dair.py`.
