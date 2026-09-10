# Track B — V2XFusion INT8-PTQ on DAIR-V2X-I (in-domain baseline)

Jetson Orin Nano, 15 W. NVIDIA pretrained `v2xfusion_sparsity.pth`, PTQ calibrated on
10 batches, evaluated on the full **2016-frame** DAIR-V2X-I validation split.

## Reproduction of NVIDIA's published numbers

3D AP, easy / moderate / hard:

| class | NVIDIA published | this run | diff |
|---|---|---|---|
| Car @0.5 | 82.06 / 69.70 / 69.75 | **82.08 / 69.70 / 69.75** | +0.02 / −0.00 / +0.00 |
| Pedestrian @0.25 | 51.13 / 48.86 / 49.22 | **51.17 / 48.87 / 49.22** | +0.04 / +0.01 / −0.00 |
| Cyclist @0.25 | 60.95 / 57.81 / 58.43 | **59.08 / 57.63 / 58.22** | **−1.87** / −0.18 / −0.21 |

Car and Pedestrian agree to within 0.04 AP. The pipeline reproduces the published
result, which is what makes every later number from it trustworthy.

**The Cyclist-easy gap of 1.87 is ~30x the other deltas and is not dismissed here.**
The most likely cause is PTQ calibration sampling: calibration uses only 10 batches
and "easy cyclist" is the sparsest cell in the table, so it has the highest variance.
This should be re-run with a different calibration seed before the number is quoted.

## Full result

| metric | easy | moderate | hard |
|---|---|---|---|
| Overall bbox AP | 75.92 | 69.83 | 70.66 |
| Overall BEV AP | 38.86 | 33.65 | 33.93 |
| Overall 3D AP | 32.10 | 27.32 | 27.55 |
| Overall AOS | 73.05 | 67.06 | 67.86 |

Per-class detail in `eval_int8_dair.txt`.

## What this is for

This is the **source domain**. The cross-dataset experiment evaluates these same frozen
weights on TUMTraf Intersection (a German roadside dataset the model never saw) and
measures the drop. The published-number agreement above is what licenses attributing
that drop to domain shift rather than to a broken pipeline.

## Caveats

* These are **INT8-PTQ (fake-quantised)** numbers. The FP16 reference still needs a run
  with quantisation disabled, which is required before any compression-cost claim.
* Raw detections are saved as `ptq_outputs.pkl`, so re-scoring costs seconds rather than
  another 22-minute inference pass.
* Rotated-box IoU is computed by a CPU replacement (`code/edge/jetson_patches/`) because
  numba's CUDA backend segfaults on this board. The agreement with published numbers is
  independent evidence that the replacement is correct.
