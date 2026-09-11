# Cross-dataset result: DAIR-V2X-I → TUMTraf Intersection

Zero-shot. V2XFusion trained on DAIR-V2X-I (Beijing roadside), evaluated unchanged on
TUMTraf Intersection R2 (German roadside, 2160 frames). Jetson Orin Nano, 15 W. The INT8
model keeps its **DAIR** calibration on purpose — PTQ derives per-tensor ranges from a
source-domain set, and whether they still fit the target is the effect under test.

## 1. Domain shift is large and clean

3D AP, moderate difficulty, FP16:

| class | DAIR (source) | TUMTraf (target) | drop |
|---|---|---|---|
| Car @0.5 | 69.73 | **0.13** | **−99.8%** |
| Pedestrian @0.25 | 49.39 | **27.61** | **−44.1%** |
| Cyclist @0.25 | 57.90 | **37.76** | **−34.8%** |

Car is evaluated at a stricter IoU (0.7/0.5) than Pedestrian and Cyclist (0.5/0.25), so the
three numbers are not directly comparable to each other. At a **matched** IoU of 0.5, all
three collapse together: Car 0.12, Cyclist 0.024, Pedestrian 0.013.

## 2. The mechanism is orientation, not detection

The detector still finds objects — AP is 30–40 at IoU 0.25. What fails is the angle.
Signed yaw error against nearest-matched ground truth, vehicles, FP16:

| | DAIR | TUMTraf |
|---|---|---|
| median | −0.2° | −0.2° |
| **std** | **12.4°** | **24.0°** |
| **within ±5°** | **88%** (363/411) | **28%** (196/705) |

The median is −0.2° in **both** domains, which rules out a conversion or convention error:
a frame mismatch would appear as a constant offset. The TUMTraf error is also multi-modal,
clustering near **+15…30°** and **−30…−60°** — consistent with the model having learned
DAIR's intersection approach angles as an orientation prior.

This single mechanism explains the AP pattern. A ~20° yaw error on a 4.1 × 1.9 m box still
overlaps enough to pass IoU 0.25 but not IoU 0.5, which is exactly why Car (scored at 0.5
and 0.7) collapses while Pedestrian and Cyclist (scored at 0.25) survive.

**Testable prediction:** the error clusters should align with TUMTraf's lane headings.
Not yet checked.

## 3. Compression amplification is NOT demonstrated

Δ = FP16 − INT8 (positive means INT8 is worse), 3D AP moderate:

| class | Δ_in (DAIR) | Δ_out (TUMTraf) | ratio |
|---|---|---|---|
| Car @0.5 | +0.037 | **−0.654** | −17.9 |
| Pedestrian @0.25 | +0.518 | **−0.892** | −1.7 |
| Cyclist @0.25 | +0.263 | **+1.328** | +5.0 |

**The signs disagree.** Two of three classes show INT8 *better* than FP16 out-of-domain,
which is not physically meaningful and indicates the differences are at noise level. Only
Cyclist shows the predicted amplification (5×). The Car ratio is meaningless because both
absolute values are ~0.

On the mechanism the signal is cleaner but small — quantisation costs nothing in-domain and
a little out-of-domain:

| yaw error std | FP16 | INT8 | Δ |
|---|---|---|---|
| DAIR | 12.4° | 12.4° | **0.0°** |
| TUMTraf | 24.0° | 25.2° | **+1.2°** |

**Honest conclusion: this run measures a large domain shift and identifies its mechanism,
but it does not establish that compression amplifies domain fragility.** A single
calibration seed, one target dataset and one model cannot separate a 1.3 AP effect from
noise. Establishing or refuting amplification needs repeated calibration seeds, a second
target domain, and per-class confidence intervals — which is Phase 2 work, not a one-week
result.

## Method notes and known limitations

* **Camera scoping.** DAIR labels only camera-visible objects (0 of 14099 fail to project);
  TUMTraf labels the full 360° LiDAR scene. Objects that do not project into the image are
  dropped (16301 of 30483), leaving 14182 = Car 12495 / Pedestrian 1039 / Cyclist 648.
  Verified afterwards to change the AP table **not at all**: the evaluator's `clean_data`
  already ignored them as truncated. Kept for cleanliness, not because it mattered.
* **Ground alignment.** The Ouster sits 7.48 m above `s110_base`; a +5.23 m shift brings
  object centres to a median z of −1.32 against DAIR's −1.19. Object survival in
  `point_cloud_range` goes 5.6% → 92.2%, and the result is identical at +5.0/+5.23/+5.5.
* **Class balance differs between domains.** TUMTraf has no traffic cones (DAIR's largest
  class) and far fewer cyclists. Per-class AP is the honest unit; a single averaged mAP
  would silently mix this in.
* **Two bugs were found and fixed during this work**, both from assuming TUMTraf resembled
  DAIR: a config declaring `H: 1080` when TUMTraf images are 1920×1200 (≈10% vertical
  misalignment between pixels and calibration), and a missing custom `collate_fn`. The
  pre-fix numbers are kept in `UNSCOPED_*.txt` only as a record of the artefact.
