# Which component actually fails — measured, 18 Sep 2026

The C.1 experiment from the proposal, run for real: substitute ground truth for
one predicted field at a time and re-score. The lift is the ceiling any repair
aimed at that component could reach.

**It does not support the proposal's current claim.** Heading degrades, but
fixing it recovers almost nothing. The dominant term is detection — the model
stops emitting boxes at all.

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

| repair | Car 3d | Ped 3d | Cyc 3d |
|---|---|---|---|
| baseline (DAIR-calibrated INT8) | 1.83 | 43.11 | 43.13 |
| **Repair 1** — INT8 recalibrated on 540 unlabeled target frames | **0.15** | **47.34** | 42.15 |

Repair 1 **hurts Car** (−1.68) and helps Pedestrian (+4.23). Not the answer, and
a useful negative: the proposal lists it as the cheapest intervention.

A queue (`repair_queue.sh`) is working through score-threshold sweeps, lidar
intensity renormalisation and ground-plane z shifts — all aimed at recall, since
that is where the loss actually is.

## Caveats

- The cross-domain Car baseline reads 0.79 on all 2160 frames here, against the
  published 0.13. Same pickle, so this is a scoped-versus-unscoped evaluation
  difference that has not been run down. It does not change the picture — both
  are catastrophic against 69.70 — but it needs resolving before publication.
- Substituting centre by construction places a box on top of a GT object, which
  guarantees the positional part of the match. The centre column is therefore an
  upper bound on the localisation term, not a neutral estimate.
- Whether the converter itself drops or misplaces target objects has not been
  ruled out as a contributor to the 22.9% match rate.

## What this means for the proposal

The synopsis says *"detection and position largely survive while heading
estimation collapses."* Measurement contradicts both halves: detection does not
survive and is 84% of the loss, position is the largest box-quality term, and
heading contributes ~0.1%.

This is still a C.1 result, and arguably a better one — the protocol worked and
overturned the hypothesis it was built to test. But the proposal's framing has to
change before submission.
