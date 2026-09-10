# Track B — in-domain compression cost on DAIR-V2X-I

Jetson Orin Nano, 15 W. NVIDIA pretrained `v2xfusion_sparsity.pth`, full 2016-frame
validation split. FP16 = same model and evaluator with quantisation disabled; INT8 =
PTQ calibrated on 10 batches. 3D AP, easy / moderate / hard.

| class | FP16 | INT8 | **Δ_in (cost of INT8)** |
|---|---|---|---|
| Car @0.5 | 82.12 / 69.73 / 69.79 | 82.08 / 69.70 / 69.75 | **0.041 / 0.037 / 0.040** |
| Pedestrian @0.25 | 51.78 / 49.39 / 49.78 | 51.17 / 48.87 / 49.22 | **0.604 / 0.518 / 0.557** |
| Cyclist @0.25 | 59.36 / 57.90 / 58.50 | 59.08 / 57.63 / 58.22 | **0.278 / 0.263 / 0.281** |
| Overall | 32.62 / 27.55 / 27.80 | 32.10 / 27.32 / 27.55 | 0.519 / 0.231 / 0.246 |

**In-domain, INT8 is close to free.** Cars lose 0.04 AP. The largest per-class cost is
Pedestrian at ~0.6. This matches the pattern in NVIDIA's published table — small objects
are the most quantisation-sensitive — and it is measured here rather than quoted:

| class | our Δ_in | NVIDIA published Δ |
|---|---|---|
| Car | 0.04 / 0.04 / 0.04 | 0.02 / 0.00 / 0.01 |
| Pedestrian | 0.60 / 0.52 / 0.56 | 0.38 / 0.29 / 0.32 |
| Cyclist | 0.28 / 0.26 / 0.28 | 0.26 / 0.26 / 0.22 |

Same magnitude throughout; ours runs slightly higher on Pedestrian.

## This is the left column of the experiment

|  | DAIR-V2X-I (source) | TUMTraf (target) |
|---|---|---|
| FP16 | 69.73 (Car mod) | pending |
| INT8 | 69.70 | pending |
| Δ | **0.037** | pending = Δ_out |

The question the project asks is whether Δ_out is larger than Δ_in — whether compression
that is nearly free at home becomes expensive off-distribution.

## Correction: the Cyclist-easy anomaly is NOT calibration noise

Against NVIDIA's published FP16 row our FP16 run gives:

| class | our FP16 − published FP16 |
|---|---|
| Car | +0.04 / +0.03 / +0.03 |
| Pedestrian | +0.27 / +0.24 / +0.24 |
| Cyclist | **−1.85** / −0.17 / −0.15 |

Earlier, seeing the same ~1.9 gap in the INT8 run, the working hypothesis was PTQ
calibration sampling. **That is now ruled out**: the FP16 run performs no calibration at
all and shows the same −1.85. The cause is systematic, not stochastic, and it is confined
to the single easy-Cyclist cell while every other cell agrees to within 0.3.

Candidates not yet distinguished: the difficulty assignment for easy cyclists (a
truncation/occlusion threshold), a label-conversion detail in `dair2kitti.py`, or an edge
case in the CPU rotated-IoU replacement that only bites on the sparsest category. This
must be resolved before the Cyclist row is quoted; Car and Pedestrian are unaffected.
