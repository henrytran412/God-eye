---
title: Component Attribution
tags:
  - finding
  - attribution
---

# Component Attribution

The C.1 protocol from the [[Proposal]], run for real: substitute ground truth for one
predicted field, re-score, read off the ceiling that fixing that component could reach.

> [!success] Harness validated
> The in-domain baseline reproduces **69.70** exactly, matching the published table.

| GT substituted for | In-domain | Cross-domain |
|---|---|---|
| nothing (baseline) | 69.70 | **0.79** |
| heading (yaw) | 69.83 | **0.85** |
| size | 69.36 | **2.61** |
| centre | 71.19 | **4.36** |
| all three at once | 71.74 | **14.10** |

> [!danger] The hypothesis was wrong
> Perfect heading buys **+0.06 AP** on Car — 0.09% of a 68.91 AP drop. The
> [[Proposal]] was built on orientation being the fragile component. It is not.

## The failure is conjunctive

Matched cars carry several moderate errors *at once*:

| Axis | Measured | Effect on a 4.1 x 1.9 m box |
|---|---|---|
| Heading | std 22.3 deg | BEV IoU falls to ~0.47 |
| Height | 0.786x | 3D IoU falls to ~0.37 |
| Width | 0.904x | compounds both |
| Elevation | 0.49 m low | compounds vertical overlap |
| Length | 0.996x | correct |

Each error alone is survivable. Together they put the box the wrong side of IoU 0.5,
while Pedestrian and Cyclist at IoU 0.25 stay on the right side of theirs. That is the
whole class pattern in [[Domain Shift]], explained.

This also resolves the apparent contradiction: one field substituted recovers almost
nothing, three recover +13.31.

## The recall ceiling

Even with every matched box made perfect, cross-domain AP reaches only **14.10**,
because just **22.9%** of target objects get any prediction within 2.5 m against
**76.5%** in-domain. Box quality cannot be repaired on objects never found.

Decomposing the 68.91 AP Car drop: ~84% ceiling collapse (detection), ~16% box quality.

Next: [[Repair Attempts]].
