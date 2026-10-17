---
title: Metrics
tags:
  - method
  - metrics
---

# Metrics

> [!important] Say which metric, every time
> "Car AP" is ambiguous here by a factor of fourteen. The same predictions read
> **1.95** or **27.21** depending only on the rule.

## The three in use

| metric | what it demands | baseline | best achieved |
|---|---|---|---|
| **3D AP @ IoU 0.5** | height, elevation, footprint, heading all near-exact | 1.83 | 1.95 |
| **BEV AP @ IoU 0.5** | footprint and heading; ignores height | 3.69 | **17.87** |
| **Centre distance (nuScenes)** | a box within 0.5–4 m; ignores size and heading entirely | 6.45 | **27.21** |

Prof. Liu's `ngperception` TUTORIAL reports centre distance, where his own model reads
0.467 by centre distance against 0.157 by IoU 0.5. The "usually around 30%" expectation
is a centre-distance number.

## Why Car looks so much worse than Pedestrian

Car is scored at IoU 0.5; Pedestrian and Cyclist at 0.25. A 22 deg heading error on a
4.1 x 1.9 m box gives BEV IoU ~0.47 — fails 0.5, passes 0.25 comfortably. The classes
were never compared at a matched threshold.

`KITTI_CAR_LOOSE=1` adds a Car-at-0.25 column to the evaluator; unset, results are
bit-identical to before.

## Three baseline numbers, all correct

| value | what it is |
|---|---|
| 0.13 | FP16, all 2160 frames — the published headline |
| 0.79 | INT8, all 2160 frames |
| **1.83** | INT8, 1620-frame eval split — the baseline for every repair |

Earlier I guessed this was a scoping difference. It is precision: the delta table gives
Car -0.654 with INT8 better, and 0.13 + 0.654 = 0.78. See [[Corrections]].
