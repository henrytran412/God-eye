---
title: Intensity neutralised
tags:
  - experiment
verdict: much worse
car_3d_05: 0.23
---

# Intensity neutralised

> [!question] Why it was tried
> PointPillars consumes intensity as a feature and two lidars report it differently.

**Result — much worse.** The medians already agree (13 vs 11). Blanking it cost Pedestrian 43.11 -> 19.03, so the channel carries signal.

Part of [[Repair Attempts]]. Diagnosis in [[Component Attribution]].
