---
title: INT8 recalibration
tags:
  - experiment
verdict: worse
car_3d_05: 0.15
---

# INT8 recalibration

> [!question] Why it was tried
> PTQ picks activation ranges from the source domain; if the target's activations fall outside them, everything saturates.

**Result — worse.** Calibrated on 540 unlabeled target frames. Car fell to 0.15, Pedestrian rose to 47.34.

Part of [[Repair Attempts]]. Diagnosis in [[Component Attribution]].
