---
title: Head threshold
tags:
  - experiment
verdict: no effect
car_3d_05: 1.83
---

# Head threshold

> [!question] Why it was tried
> The detection head discards proposals below 0.1, which might be erasing real detections.

**Result — no effect.** Two more boxes per frame, not one digit of movement. `result2kitti.py:253` cuts at 0.45 *before* AP is computed, so the head's floor never reaches the metric.

Part of [[Repair Attempts]]. Diagnosis in [[Component Attribution]].
