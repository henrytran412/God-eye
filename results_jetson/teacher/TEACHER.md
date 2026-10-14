# Raising target-domain Car AP with a label-free teacher — 14 Oct 2026

Prof. Liu's feedback was that Car AP looked too low, "usually around 30%", and he
pointed to `ngperception/` in his DeepDataMiningLearning repository. This round
measured why it is low, then applied the recipe of his `gaussian4d` module to
detection.

**Result.** With no target label and no training, the best configuration that
uses only source-domain priors raises target Car AP **4.2×** by nuScenes centre
distance (6.45 → **27.21**) and **4.8×** by BEV IoU 0.5 (3.69 → **17.87**). Strict
3D IoU 0.5 barely moves (1.83 → 1.95). That metric needs height, elevation and
footprint all near-exact at once, which ~13 LiDAR points per car cannot give.

## 1. The "30%" is not a metric artefact

Prof. Liu's TUTORIAL reports nuScenes centre-distance AP, where his own model
reads 0.467 by centre distance against 0.157 by IoU 0.5. Scoring ours his way
(`cd_ap.py`, the nuscenes-devkit formula):

| Car, centre-distance AP | value |
|---|---|
| source, in-domain | **95.51** |
| target, V2XFusion unchanged | **6.45** |

The target stays low under the loosest metric too. For each target GT car, the
nearest prediction within 2 m was a car for 23.0% of them, and nothing at all for
**73.7%**. Only 3% got called something else. In-domain, 98.7% of cars get a
car prediction. **The detector does not see three-quarters of the target cars.**

## 2. The method

`gaussian4d` builds occupancy targets without human labels. It trusts raw LiDAR
geometry and borrows semantics from frozen 2D foundation models. The same recipe
applied to detection (`label_free_teacher.py`):

1. **A COCO-pretrained YOLO**, trained on neither DAIR-V2X-I nor TUMTraf, finds
   cars in the target camera image.
2. **The LiDAR points inside each 2D box** are cut out, ground and structure
   are removed, they are clustered, and a minimum-area rectangle is fitted.
3. **2D-guided refinement.** The box is slid and rotated until its projection
   matches the 2D box, while staying on the LiDAR points.
4. **Ground-plane fallback** for boxes with too few points. The 2D box's bottom
   edge is projected onto the mapped road surface.

V2XFusion's car predictions are replaced. Its Pedestrian and Cyclist predictions
pass through unchanged, which is why those two columns never move below.

## 3. Results

Car moderate on the 1,620-frame evaluation split. Ped and Cyc are at IoU 0.25.

| run | Car 3D@0.5 | BEV@0.5 | 3D@0.25 | BEV@0.25 | CD-AP |
|---|---|---|---|---|---|
| V2XFusion, unchanged | 1.83 | 3.69 | 6.26 | 9.21 | 6.45 |
| teacher, LiDAR fit only (v1) | 1.42 | 9.22 | 11.87 | 24.02 | 14.71 |
| + 2D-guided refinement (v2) † | 0.97 | 14.19 | 24.25 | 36.79 | 24.10 |
| **source priors, refinement** (v4) | **2.00** | **18.16** | 27.02 | 36.51 | 24.75 |
| **+ ground-plane fallback** (v5) | 1.95 | 17.87 | **27.98** | **37.57** | **27.21** |
| + target height from LiDAR (v3) ‡ | 3.77 | 18.63 | 29.20 | 36.61 | 25.06 |
| perfect 2D boxes + refinement (oracle) † | 5.22 | 14.90 | 24.82 | 33.40 | 25.49 |

The v4 and v5 rows are **airtight**. Every prior comes from source labels, which
domain adaptation is allowed to use, and no decision was made by looking at
target labels. Report these.

† Uses size priors that were first set near TUMTraf GT medians, which is a label
leak, later replaced. The oracle also predates the height floor, so v4/v5 beat it.

‡ The height floor of 1.45 m is estimated from unlabeled target LiDAR, so it is
label-free in itself. But the choice to trust the LiDAR height estimate and not
its width estimate was made after comparing both against target labels. Treat
this row as an upper reference, not a reportable number. It also shows how
sensitive strict 3D@0.5 is: 5 cm of box height nearly doubles it.

Centre-distance AP of v5 by threshold: 0.5 m 2.07, 1 m 21.91, 2 m 34.35,
**4 m 50.53**.

## 4. What was tried and did not help

| variant | effect | why |
|---|---|---|
| refine V2XFusion's own car boxes with teacher geometry | worse (CD-AP 6.19) | its scores are collapsed (median 0.286), so the refined boxes rank badly |
| keep V2XFusion cars and add teacher boxes (union) | ≈ teacher alone | adds nothing the teacher does not already find |
| snap yaw to road directions from unlabeled V2XFusion yaws | worse (BEV@0.5 18.63 → 14.19) | three directions from noisy yaws are too coarse; 86% of boxes were forced onto them |
| add YOLO's `truck` class | best BEV@0.25 (41.09), worse elsewhere | finds more vehicles and more false positives |

## 5. Measured along the way

- **Where the fitter lost accuracy.** With perfect 2D boxes, the LiDAR cluster
  for a car holds a median **13 points**, all on the side facing the sensor, so
  its centroid sits **1.74 m** from the true centre. Matching the projection to
  the 2D box roughly doubled every metric (oracle CD-AP 13.75 → 25.49).
- **Box convention, measured.** A car's long axis lies along yaw for 85% of
  well-observed TUMTraf cars and 76% of DAIR cars, and predicted z is the box
  bottom. An earlier oracle drew GT boxes rotated 90°. A gate comparing both yaw
  offsets caught it (BEV@0.5 6.43 against 0.004).
- **Points and labels agree vertically**: +0.01 m on target, −0.10 m on source.
  An earlier reading of a "1 m ground offset" from a z-histogram was wrong.
- **LiDAR coverage.** **89.4%** of target GT cars hold ≥5 points (median 21),
  against **96.5%** in-domain (median 52). The target cloud is about 2.5× sparser
  per car, but it is not empty. An earlier figure of ~48% came from a footprint
  test still drawn 90° rotated, and is withdrawn. So the 47% of YOLO boxes the
  LiDAR fitter could not fit are mostly lost *inside the pipeline* (the 8%
  frustum shrink, ground removal, the 5-point cluster minimum), not for lack of
  points. The ground-plane fallback recovers them coarsely. A fitter that keeps
  more of that evidence should recover them better, and is the cheapest next gain.
- **Car size from unlabeled LiDAR** (`lidar_size_stats.py`, validated on source
  first). Height is recovered in both domains (target 1.45 against 1.50
  labelled). Width is not: target 1.06 against 1.90, because from a mast the
  sparse points mostly trace a car's long side.
- **Correction to an earlier claim.** Target cars are 1.50 m tall, not the
  1.70 m inferred from a ratio during the session. So the source/target height
  difference (1.40 vs 1.50) explains little of V2XFusion's 0.786× height
  under-prediction.

## 6. Next step: teacher → student

Everything above runs alongside an unchanged V2XFusion. The step that changes
the detector itself is the one gaussian4d is built for: use these teacher boxes
as **pseudo-labels to fine-tune V2XFusion's detection head** on unlabeled target
frames, with the backbone frozen. That is the first experiment here that trains
weights. It is feasible on the Orin Nano for the head alone, but slow, and it
is the obvious use of the 540-frame calibration split, which no result above
has touched.

## Files

`RESULTS.txt` is every run's row. `RUNS.status` is the run log with box counts.
`cd_logs/` has centre-distance AP per threshold. `priors.json` holds the road
directions. `size_*.json` hold the LiDAR size estimates. Code is in
`code/edge/jetson_patches/`.
