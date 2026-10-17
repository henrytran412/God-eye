---
title: Corrections
tags:
  - method
  - corrections
---

# Corrections

Claims this project made and then withdrew. Kept because each one changed a conclusion,
and because a reader of the older documents will otherwise trust them.

> [!bug] "Orientation is what breaks"
> The [[Proposal]] title, synopsis and four sections rest on it. Substituting perfect
> heading recovers **+0.06 AP**. Overturned by [[Component Attribution]].
> `docs/index.html` still carries this headline publicly.

> [!bug] "Only ~48% of target cars have LiDAR points"
> The correct figure is **89.4%** (median 21 points). The probe that produced 48% was
> testing footprints rotated 90 degrees. This matters: it means the fitter discards cars
> it could fit, which is a cheap remaining gain.

> [!bug] "Target cars are 1.70 m tall"
> Inferred from a ratio mid-session. Measured: **1.50 m** against the source's 1.40 m.
> So the height difference explains little of the 0.786x under-prediction.

> [!bug] "The point cloud ground sits ~1 m below the labels"
> Read off a z-histogram. Measured directly, points and labels agree vertically:
> **+0.01 m** on target, -0.10 m on source. The converter is not at fault.

> [!bug] "The 0.13 vs 0.79 gap is a scoping difference"
> It is precision: 0.13 is FP16, 0.79 is INT8, on the same frames. See [[Metrics]].

> [!bug] An oracle that scored *below* real YOLO
> The "perfect 2D box" oracle initially drew GT boxes rotated 90 degrees, so it looked
> worse than the real detector. A gate comparing both yaw conventions caught it
> (BEV@0.5 6.43 against 0.004).
