# Which component actually fails — measured, 18 Sep 2026

The C.1 experiment from the proposal, run for real: substitute ground truth for
one predicted field at a time and re-score. The lift is the ceiling any repair
aimed at that component could reach.

**It does not support the proposal's current claim.** Heading degrades, but
fixing it recovers almost nothing: perfect yaw buys 0.06 AP on Car.

What the measurements converge on instead is that **no single component is
responsible**. Cars carry a 22.3° yaw spread, a 21% height under-prediction, a
10% width under-prediction and a 0.49 m elevation error *simultaneously*, and
Car is scored at IoU 0.5. Each error alone is survivable; together they put the
box the wrong side of the threshold. Recall is the largest single term — 84% of
the Car loss — but "the model stops detecting" overstates it, since the model
still emits 6.3 boxes per frame. The accurate statement is that several
components degrade moderately at once and a strict IoU threshold turns that into
a total loss.

Nine training-free repairs were then tried against that diagnosis. The best
moved Car from 1.83 to 2.30. The negative results, and the controls that produced
them, are the substance of this document.

## Harness validation

The in-domain baseline reproduces **69.70** Car 3D AP, matching the published
DAIR-V2X-I table exactly. Numbers below are trustworthy to that standard.

One bug was found and fixed first. Substituting GT centre drove 3D AP to zero
while BEV AP went *up* — the signature of a z-convention gap, since BEV ignores
height. `V2XDataset.get_gt` builds boxes from a nuScenes `Box`, whose centre is
geometric; the detection head predicts a bottom face. Confirmed by measurement
rather than assumption: after subtracting h/2 the pedestrian residual sits at
0.00 m. `gt_substitution.py` now converts. All numbers here are post-fix.

## Ceiling per component (moderate; Car @ IoU 0.5, Ped/Cyc @ IoU 0.25)

| substituted | Car in | Car cross | Ped in | Ped cross | Cyc in | Cyc cross |
|---|---|---|---|---|---|---|
| baseline | 69.70 | 0.79 | 48.87 | 28.50 | 57.63 | 36.43 |
| GT yaw | 69.83 | **0.85** | 48.98 | 28.76 | 60.66 | 36.80 |
| GT size | 69.36 | 2.61 | 48.39 | 49.10 | 55.70 | 43.01 |
| GT centre | 71.19 | 4.36 | 76.89 | 65.92 | 71.85 | 57.62 |
| all three | 71.74 | 14.10 | 80.11 | 68.47 | 78.14 | 61.37 |

Cross-domain lift from fixing one component alone:

| | yaw | size | centre |
|---|---|---|---|
| Car | **+0.06** | +1.82 | +3.57 |
| Pedestrian | +0.26 | +20.60 | +37.42 |
| Cyclist | +0.37 | +6.58 | +21.19 |

**Perfect heading buys 0.06 AP on Car — 0.09% of a 68.91 AP drop.**

## Why: the ceiling itself collapsed

"All three" is the ceiling with every matched box made perfect. It cannot exceed
what recall allows, because a GT object with no prediction near it can never be
scored. That ceiling falls from 71.74 to 14.10.

| | in-domain | cross-domain |
|---|---|---|
| predictions per frame (score ≥ 0.4) | 18.7 | 2.5 |
| GT objects with a prediction within 2.5 m | **76.5%** | **22.9%** |

Decomposing the Car drop of 68.91 AP:

| term | AP | share |
|---|---|---|
| ceiling collapse (detection / recall) | 57.64 | **84%** |
| box quality at fixed recall | 11.27 | 16% |

Pedestrian splits 57% / 43%, Cyclist 79% / 21%. Recall dominates everywhere, and
overwhelmingly for Car.

## The heading finding still reproduces — it is just not the bottleneck

Matched car pairs, score ≥ 0.4: yaw median −0.83°, **std 22.26°, only 35.0%
within ±5°**. Alongside it, car height is under-predicted by 21%
(pred/GT 0.786) and car z sits 0.49 m below truth. So orientation really does
degrade. It simply cannot move AP while 77% of objects go undetected.

## Repairs tried so far

Scored on a disjoint 1620-frame split. The 540-frame calibration set had to be
carved out by hand: `tumtraf_infos_train.pkl` came out of the converter **empty**,
so `default_tumtraf.yaml` pointed its train split at the val file, and
calibrating on that would have been transductive.

| repair | Car 3d | Ped 3d | Cyc 3d | verdict |
|---|---|---|---|---|
| baseline (DAIR-calibrated INT8) | 1.83 | 43.11 | 43.13 | — |
| **1.** INT8 recalibrated on 540 unlabeled target frames | **0.15** | 47.34 | 42.15 | hurts Car |
| **2.** detection head threshold 0.1 → 0.05 | 1.83 | 43.11 | 43.13 | no effect |
| **3.** evaluator operating point 0.45 → 0.20 | 2.30 | 43.25 | 43.97 | +0.47, then plateaus |

Repair 1 **hurts Car** (−1.68) while helping Pedestrian (+4.23). A useful
negative: the proposal lists it as the cheapest intervention.

Repair 2 moved nothing because `result2kitti.py:253` hardcodes
`detection_score > 0.45`, discarding predictions *before* AP is computed. The
head's own threshold is therefore irrelevant. That line is now
`KITTI_SCORE_THR`, defaulting to 0.45 so published numbers stay bit-identical.

### Confidence collapse is real but is not the cause

| | median score | predictions/frame | survive the 0.45 cut |
|---|---|---|---|
| DAIR (source) | **0.987** | 20.5 | 18.5 — loses 10% |
| TUMTraf (target) | **0.286** | 6.3 | 2.3 — **loses 64%** |

A fixed operating point chosen where the median is 0.987 throws away nearly
two-thirds of target predictions, which looked like free recall. It is not.
Sweeping the operating point on **both** domains:

| operating point | Car tgt | Ped tgt | Cyc tgt | Car src | Ped src | Cyc src |
|---|---|---|---|---|---|---|
| 0.45 | 1.83 | 43.11 | 43.13 | 69.70 | 48.87 | 57.63 |
| 0.20 | 2.30 | 43.25 | 43.97 | 69.65 | 49.97 | 58.86 |
| 0.10 | 2.20 | 43.25 | 44.60 | — | — | — |
| 0.01 | 2.20 | 43.25 | 44.60 | — | — | — |

**The source gains as much as the target** (Ped +1.10 source against +0.14
target; Cyc +1.23 against +0.84), so this is ordinary threshold tuning, not a
domain-shift repair. 0.10 and 0.01 are identical because the head stops emitting
below its own 0.1 floor.

The conclusion is the unwelcome one: the predictions hidden below 0.45 are
genuinely false positives, so the recall collapse is a **real detection
failure**, not a thresholding artifact. That strengthens the 84% figure rather
than explaining it away.

### Input-space hypotheses: intensity and density both exonerated

| repair | Car 3d | Ped 3d | Cyc 3d | verdict |
|---|---|---|---|---|
| **4.** intensity replaced by a constant | 0.23 | **19.03** | 43.28 | intensity is *informative* |

The two domains' intensity medians already agree (13 against 11), and blanking
the channel costs Pedestrian 43.11 → 19.03. Nothing to repair here.

Density looked far more promising. The target supplies **9,508** points inside
`point_cloud_range` per frame against the source's **37,930** — four times
sparser, after 54.5% of the TUMTraf cloud is cropped as structure above the +3 m
ceiling. The control is to thin the *source* to the target's density and score
**in-domain**:

| DAIR, scored in-domain | Car | Ped | Cyc |
|---|---|---|---|
| full density (37,930 points) | 69.70 | 48.87 | 57.63 |
| thinned to 9,508 points | 64.58 | 34.79 | 46.27 |
| cost of 4× sparser input | **−5.12** | −14.08 | −11.36 |

**Density explains 5.12 AP of Car's 67.87 AP loss — 7.5%.** Car is remarkably
robust to sparse input; it is the small classes that suffer, which is the
opposite of the cross-domain pattern. Density is not the answer.

## The failure is conjunctive

Matched car pairs (score ≥ 0.4) carry several modest errors at once:

| axis | measured |
|---|---|
| yaw | std 22.3°, 35% within ±5° |
| height | 0.786× true |
| width | 0.904× true |
| length | 0.996× (correct) |
| elevation | 0.49 m low |

A 22° yaw error on a 4.1 × 1.9 m box puts BEV IoU at roughly 0.47 — just under
the 0.5 threshold Car is scored at. Height under-prediction then drags 3D IoU to
about 0.37. Each axis alone is survivable; together they land the wrong side of
the line.

That resolves what first looked like a contradiction. Substituting one field
recovers almost nothing (+0.06 for yaw) because the others still fail the
threshold, while substituting all three recovers +13.31. And it explains the
class pattern directly: Pedestrian and Cyclist are scored at IoU 0.25 and retain
88% and 75%, while Car at IoU 0.5 retains 3%.

**The honest headline is neither "orientation is the fragile component" nor
"it is all recall". It is that several components degrade moderately and Car's
strict IoU threshold converts that into a total loss.**

## The camera branch is load-bearing, and its calibration is sound

| repair | Car 3d | Ped 3d | Cyc 3d |
|---|---|---|---|
| baseline | 1.83 | 43.11 | 43.13 |
| **5.** camera input blanked | **0.00** | **0.00** | **0.00** |

Feeding a constant image takes every class to exactly zero and cuts output to
2.1 boxes per frame. The camera is not poisoning the fuser; the model cannot run
without it. Gating the camera under shift is therefore not an available repair.

One caveat on the strength of that claim: a constant image is not the same as a
lidar-only architecture. The fuser still receives a well-formed but
information-free feature map, which may be worse than a proper camera-free path.
The honest reading is *the model cannot tolerate a constant image*.

`calib_check.py` then audited the geometry by projecting GT centres through
`lidar2camera` and the intrinsics. Both domains are sound — 100% of centres in
front of the camera, 96.5% landing on the image for DAIR and 84.2% for TUMTraf —
so the converter did not break the calibration. It did quantify a domain gap the
proposal never mentioned: **TUMTraf's lens is 1.69× wider** (fx 1293 against
2183), with objects at 31.6 m median depth against 68.3 m. The branch the model
depends on is seeing objects at an apparent scale it never trained on, and no
input patch reaches that.

## The converter's z handling is NOT at fault

If points and labels were genuinely ~0.5 m apart, shifting the input cloud up by
that much should produce a maximum. Sweeping z on 400 frames, with z = 0 as a
control:

| z shift | Car 3d | Ped 3d | Cyc 3d | preds/frame |
|---|---|---|---|---|
| −1.00 | 1.01 | 29.21 | 14.19 | 11.0 |
| **−0.50** | **2.08** | 34.77 | 28.91 | 9.6 |
| 0 (control) | 1.73 | **51.66** | 36.92 | 7.6 |
| +0.30 | 1.39 | 45.81 | 42.15 | 6.9 |
| +0.50 | 1.29 | 42.25 | **44.50** | 6.5 |
| +0.70 | 1.07 | 34.86 | 44.00 | 6.1 |
| +1.00 | 0.80 | 22.69 | 42.55 | 5.9 |
| +1.50 | 0.40 | 16.76 | 32.58 | 6.1 |

**There is no peak at +0.5.** Car and Pedestrian decline monotonically as the
cloud rises, Cyclist peaks at +0.5 and follows. What the curve tracks is the
range crop — every metre up costs points off a cloud that already loses 54.5% to
the +3 m ceiling — not label alignment.

So the 0.49 m gap between predicted and true box centres is the model genuinely
mislocating objects in an unfamiliar domain. **The cross-dataset numbers stand as
a real domain-shift measurement, not an artifact of our pipeline.** That was the
outcome worth having, even though it removes the last repair candidate.

The −0.50 point does lift Car to 2.08 against the 1.73 control, but Pedestrian
falls 51.66 → 34.77 and Cyclist 36.92 → 28.91 at the same time, and by −1.00 Car
is back under the control at 1.01. A narrow +0.35 bump, at absolute values near
1–2 AP where 400 frames carry real noise, with the small classes paying for it.
A full-split rerun and a source-domain control are queued; the operating-point
sweep already showed how readily an apparent repair turns out to help both
domains equally.

### Still open

- Whether the converter drops or misplaces target objects has not been ruled out
  as a contributor to the 22.9% match rate, though the calibration audit and the
  z sweep both came back clean.
- The camera-scale gap (1.69× focal length, 2.2× median object depth) is
  measured but untested as a cause; testing it needs a resized-input experiment
  or retraining.

## What this means for the proposal

The synopsis says *"detection and position largely survive while heading
estimation collapses."* Measurement contradicts both halves: detection does not
survive and is 84% of the loss, position is the largest box-quality term, and
heading contributes ~0.1%.

This is still a C.1 result, and arguably a better one — the protocol worked and
overturned the hypothesis it was built to test. But the proposal's framing has to
change before submission.
