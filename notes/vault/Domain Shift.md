---
title: Domain Shift
tags:
  - finding
  - domain-shift
---

# Domain Shift

V2XFusion trained on [[Datasets#DAIR-V2X-I|DAIR-V2X-I]] (Beijing), evaluated unchanged
on [[Datasets#TUMTraf Intersection|TUMTraf]] (Munich). Zero-shot, no recalibration.

| 3D AP, moderate | Source | Target | Retained |
|---|---|---|---|
| Car @ IoU 0.5 | 69.70 | **1.83** | 3% |
| Pedestrian @ IoU 0.25 | 48.87 | 43.11 | 88% |
| Cyclist @ IoU 0.25 | 57.63 | 43.13 | 75% |

> [!warning] The classes are not scored alike
> Car is judged at IoU 0.5, the other two at 0.25. That single difference drives most
> of the apparent class pattern — see [[Metrics]].

## It is not a metric artefact

Scored by nuScenes centre distance, the loosest standard metric, the target still
reads **6.45** against **95.51** in-domain. For each target GT car, the nearest
prediction within 2 m was:

- a car — 23.0%
- **nothing at all — 73.7%**
- some other class — ~3%

In-domain, 98.7% of cars get a car prediction. ==The detector does not see
three-quarters of the target cars.==

## Input differences, measured

|  | Source | Target |
|---|---|---|
| points inside `point_cloud_range` | 37,930/frame | 9,508/frame |
| GT cars with >=5 LiDAR points | 96.5% | 89.4% |
| median points on a car | 52 | 21 |
| camera focal length | 2183 | 1293 |
| median object depth | 68.3 m | 31.6 m |
| median detection score | 0.987 | 0.286 |

Sparser input is real but is **not** the cause — see the density control in
[[Repair Attempts]].

Next: [[Component Attribution]].
