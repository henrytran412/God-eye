---
title: Open Questions
tags:
  - next
---

# Open Questions

## 1. Teacher -> student

Everything in [[Label-Free Teacher]] runs *alongside* an unchanged V2XFusion. The step
`gaussian4d` is actually built for is to use the teacher boxes as **pseudo-labels to
fine-tune the detection head** on unlabeled target frames, backbone frozen.

- First experiment here that trains weights
- Feasible on the [[Jetson]] for the head alone, but slow
- The obvious use of the 540-frame calibration split, which no result has touched

## 2. Recover the cars the fitter drops

[[Corrections]] showed 89.4% of target cars have LiDAR points, yet the fitter converts
only 53% of YOLO's boxes. The losses are inside the pipeline — the 8% frustum shrink,
ground removal, the 5-point cluster minimum — not for lack of evidence. ==Cheapest
remaining gain.==

## 3. Recall before box quality

Perfect boxes on everything currently detected reach only 14.10, because 77% of objects
are never found. Until detection improves, box-refinement is capped at a fifth of source
performance. This orders the whole programme.

## 4. Things the measurements cannot yet separate

- **Sensor vs geography.** One source and one target cannot tell them apart. A second
  target pair turns a case study into an attribution.
- **The 1.69x focal gap** feeding a camera branch the model cannot run without
  ([[Domain Shift]]). Measured, untested as a cause.
- **A supervised oracle** would let every repair be reported as a fraction of the
  recoverable gap, the convention the adaptation literature uses.

## 5. The proposal needs rewriting

Title, synopsis, A.2, A.3, all of B, and two of C.3's four repairs rest on the
orientation claim. See [[Proposal]].
