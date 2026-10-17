---
title: Datasets
tags:
  - context
  - dataset
---

# Datasets

## DAIR-V2X-I

Beijing roadside infrastructure, the **source** domain. V2XFusion's training set.
2,016 validation frames. Dense: 37,930 in-range points per frame, median 52 points on a
car. Camera focal length 2183, median object depth 68.3 m.

## TUMTraf Intersection

Munich roadside gantry (R2), the **target** domain. 2,160 frames, split here into 540
calibration and 1,620 evaluation. Converted to DAIR layout by
`code/edge/jetson_patches/tumtraf_to_dair.py`.

Sparser and closer: 9,508 in-range points per frame, median 21 points on a car, focal
1293, median depth 31.6 m. 54.5% of its cloud sits above the +3 m ceiling and is cropped.

> [!note] Labels are sound
> 99.8% of TUMTraf GT sits inside `point_cloud_range`, better than DAIR's own 80.9%, and
> GT z matches (-1.00 vs -0.90). The conversion is not the problem — see [[Corrections]].

Both feed [[Domain Shift]].
