---
title: Label-Free Teacher
tags:
  - experiment
  - result
  - teacher
---

# Label-Free Teacher

Prof. Liu's [`ngperception/gaussian4d`](https://github.com/lkk688/DeepDataMiningLearning/tree/main/DeepDataMiningLearning/ngperception)
builds occupancy targets with **no human labels**: raw LiDAR geometry for structure,
frozen 2D foundation models for semantics. This applies the same recipe to detection.

## The pipeline

1. A **COCO-pretrained YOLO** — trained on neither dataset — finds cars in the target image.
2. The **LiDAR points inside each 2D box** are cut out, ground removed, clustered, and a
   minimum-area rectangle fitted.
3. **2D-guided refinement**: the box is slid and rotated until its projection matches the
   2D box, while staying on the points.
4. **Ground-plane lift** for boxes with too few points: the 2D box's bottom edge is
   projected onto the mapped road surface.

Nothing is trained. No target label is read. V2XFusion's Pedestrian and Cyclist
predictions pass through untouched, so any change in the Car row is the teacher's doing.

| Run | 3D@0.5 | BEV@0.5 | 3D@0.25 | BEV@0.25 | CD-AP | Note |
|---|---|---|---|---|---|---|
| Baseline | 1.83 | 3.69 | 6.26 | 9.21 | **6.45** | V2XFusion unchanged. |
| Teacher, LiDAR only | 1.42 | 9.22 | 11.87 | 24.02 | **14.71** | YOLO frustum + minimum-area rectangle. |
| + 2D refinement | 0.97 | 14.19 | 24.25 | 36.79 | **24.10** | Box slid until its projection matches the 2D box. Used leaked size priors. |
| Source priors | 2.00 | 18.16 | 27.02 | 36.51 | **24.75** | **Airtight.** Every prior from source labels. |
| + ground-plane lift | 1.95 | 17.87 | 27.98 | 37.57 | **27.21** | **Airtight, best.** Recovers boxes with too few points. |
| + LiDAR height floor | 3.77 | 18.63 | 29.20 | 36.61 | **25.06** | Upper reference only: the height estimate was trusted after a target-label check. |
| Oracle: perfect 2D | 5.22 | 14.90 | 24.82 | 33.40 | **25.49** | Ceiling of LiDAR fitting given a flawless 2D detector. |

> [!success] Best airtight result
> **CD-AP 6.45 -> 27.21** (4.2x), **BEV@0.5 3.69 -> 17.87** (4.8x), using only
> source-domain priors. At the 4 m threshold, CD-AP reaches **50.53**.

> [!warning] Strict 3D barely moves
> 1.83 -> 1.95. IoU 0.5 in 3D needs height, elevation and footprint near-exact at once,
> and ~21 points per car cannot pin that down. See [[Metrics]].

## What the refinement fixes

With perfect 2D boxes, a car's LiDAR cluster holds a median **13 points**, all on the
sensor-facing side, so its centroid sits **1.74 m** from the true centre. Matching the
projection to the 2D box roughly doubled every metric (oracle CD-AP 13.75 -> 25.49).

## Tried and rejected

| variant | effect |
|---|---|
| refine V2XFusion's own boxes | worse (CD-AP 6.19) — its scores are collapsed, so refined boxes rank badly |
| union with V2XFusion cars | ~ teacher alone |
| snap yaw to road directions | worse (BEV@0.5 18.63 -> 14.19) — three directions from noisy yaws are too coarse |
| add YOLO's `truck` class | best BEV@0.25 (41.09), worse elsewhere |

Next: [[Open Questions]].
